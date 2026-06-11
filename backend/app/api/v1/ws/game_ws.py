"""
game_ws.py — WebSocket endpoint para el modo manual interactivo.

Ruta: WS /api/v1/ws/game/{room_id}?token=<jwt>

Ciclo de vida:
  1. Handshake JWT — validar token, verificar pertenencia a la sala
  2. Fase Lobby — broadcast player_joined/player_left
  3. Fase Countdown — 3..2..1..YA!
  4. Fase Juego — ciclo de cartas (Griton), taps del jugador, validacion
  5. Fase Resultado — broadcast game_end, premios
"""

import json
import jwt
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.core.config import settings
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.lobby_models import GameRoom, RoomRegistration
from app.models.items import ItemCatalog, ItemType
from app.models.user import User
from app.services.ws_manager import ws_manager

logger = logging.getLogger("ws.game")
router = APIRouter()


def _verify_token_local(token: str) -> str:
    """
    Valida el JWT de Privy y retorna el privy_did (claim 'sub').

    Modo produccion: verifica firma ES256 con JWKS de Privy.
    Modo desarrollo (local, sin PRIVY_APP_ID): decodifica sin verificar firma.
    """
    if not settings.PRIVY_APP_ID:
        # Modo desarrollo — decodificar sin verificar firma
        if settings.BLOCKCHAIN_MODE != "local":
            raise ValueError("PRIVY_APP_ID no configurado en entorno no-local.")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token sin campo 'sub'.")
            return user_id
        except Exception as e:
            raise ValueError(f"Error decodificando token: {e}")

    # Modo produccion — verificar firma con Privy JWKS
    try:
        from app.core.auth import get_jwks_client
        jwks_client = get_jwks_client()
        if not jwks_client:
            raise ValueError("Error configurando JWKS de Privy.")

        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience=settings.PRIVY_APP_ID,
            issuer="privy.io",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token sin campo 'sub'.")
        return user_id

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado.")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Token invalido: {e}")


@router.websocket("/game/{room_id}")
async def manual_game_ws(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
    session: Session = Depends(get_session),
):
    """
    WebSocket para el modo manual de Loteria Multijugador.

    Query params:
        token: JWT de Privy (X-Privy-Token)

    Mensajes del cliente:
        {"type": "mark_cell", "cell_index": 7}
        {"type": "shout_loteria"}
        {"type": "use_hint"}

    Mensajes del servidor:
        {"type": "card_called", "card_id": 12, "turn": 5, "window_ms": 2000, ...}
        {"type": "loteria_validated", "player_axo_id": 42, "win_type": "line", ...}
        {"type": "tension_update", "level": "high", "near_win": [...]}
        {"type": "game_start", ...}
        {"type": "game_end", ...}
    """
    # 1. Handshake — validar token
    try:
        user_id = _verify_token_local(token)
    except ValueError as e:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close(code=4001, reason="Token invalido.")
        return

    # 2. Verificar que el usuario tiene un Axolotito registrado en esta sala
    reg = session.exec(
        select(RoomRegistration)
        .join(Axolotito, RoomRegistration.axolotito_id == Axolotito.id)
        .where(RoomRegistration.room_id == room_id)
        .where(Axolotito.user_id == user_id)
    ).first()

    if not reg:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": "No tienes un Axolotito registrado en esta sala."
        })
        await websocket.close(code=4002, reason="No registrado.")
        return

    axo = session.get(Axolotito, reg.axolotito_id)
    if not axo:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Axolotito no encontrado."})
        await websocket.close(code=4003, reason="Axolotito no encontrado.")
        return

    # 3. Obtener las tablas registradas y sus cartas
    board_ids = json.loads(reg.boards_json)
    board_card_ids: dict[int, list[int]] = {}
    for bid in board_ids:
        board = session.get(PlayerBoard, bid)
        if board:
            board_card_ids[bid] = board.card_ids[:16] if board.card_ids else []

    # 4. Registrar conexion (intentar reconectarse si ya está registrado en la sesión activa)
    session_obj = ws_manager.get_session(room_id)
    reconnected = False
    if session_obj and user_id in session_obj.players:
        reconnected = await ws_manager.reconnect(room_id, user_id, websocket, play_mode=reg.play_mode)

    if not reconnected:
        # Look up user VIP tier for chat enrichment
        user_obj = session.exec(
            select(User).where(User.privy_did == user_id)
        ).first()
        await ws_manager.connect(
            room_id=room_id,
            user_id=user_id,
            ws=websocket,
            axolotito_id=axo.id,
            axo_name=axo.name,
            board_ids=board_ids,
            board_card_ids=board_card_ids,
            play_mode=reg.play_mode,
            vip_tier=user_obj.vip_tier if user_obj else None,
            nature=axo.nature,
        )

    # 6. Si la sala esta en lobby y hay suficientes jugadores, iniciar
    room = session.get(GameRoom, room_id)
    session_obj = ws_manager.get_session(room_id)

    if room and room.status == "waiting" and session_obj:
        player_count = ws_manager.get_player_count(room_id)
        if player_count >= 2:
            all_cards = session.exec(
                select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
            ).all()
            all_card_ids = [c.id for c in all_cards]

            room.status = "playing"
            session.add(room)
            session.commit()

            await ws_manager.start_game(room_id, all_card_ids)

    # 6. Loop de mensajes del cliente
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "mark_cell":
                cell_index = data.get("cell_index", -1)
                await ws_manager.handle_mark_cell(room_id, user_id, int(cell_index))

            elif msg_type == "shout_loteria":
                await ws_manager.handle_shout_loteria(room_id, user_id)

            elif msg_type == "use_hint":
                await ws_manager.handle_use_hint(room_id, user_id)

            elif msg_type == "chat_message":
                data_payload = data.get("data", {})
                await ws_manager.handle_chat_message(
                    room_id=room_id,
                    user_id=user_id,
                    text=data_payload.get("text", ""),
                    is_reaction=data_payload.get("is_reaction", False),
                    sticker_id=data_payload.get("sticker_id"),
                    megaphone=data_payload.get("megaphone", False),
                )

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Tipo de mensaje desconocido: {msg_type}"
                })

    except WebSocketDisconnect:
        await ws_manager.disconnect(room_id, user_id, websocket)
    except Exception as e:
        logger.warning(f"WebSocket error en room {room_id}, user {user_id}: {e}")
        await ws_manager.disconnect(room_id, user_id, websocket)
