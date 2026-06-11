"""
ws_manager.py — Game WebSocket Connection Manager.

Gestiona conexiones WebSocket para el modo manual (tiempo real interactivo).
Cada sala tiene un GameSession que orquesta el ciclo de cartas (el "Gritón"),
recibe taps de los jugadores y valida gritos de ¡Lotería! en tiempo real.

Patrón: singleton a nivel de módulo. La instancia se comparte entre el
endpoint WebSocket y el scheduler de salas.
"""

from __future__ import annotations
import asyncio
import json
import logging
import random
import secrets
import time
from dataclasses import dataclass, field as dc_field
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("ws.manager")

# Generador criptográficamente seguro para barajar el mazo
_rng = random.SystemRandom()

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PlayerState:
    """Estado de un jugador dentro de una sesión de juego manual."""
    user_id: str
    axolotito_id: int
    axo_name: str
    board_ids: list[int]                # IDs de tablas registradas
    board_card_ids: dict[int, list[int]]  # board_id -> lista de 16 card_ids
    marked_indices: dict[int, set[int]] = dc_field(default_factory=dict)   # board_id -> set de índices marcados
    hints_remaining: int = 3
    play_mode: str = "manual"
    missed_turns_count: int = 0
    ws: WebSocket | None = None
    connected: bool = True
    joined_at: float = dc_field(default_factory=time.time)


@dataclass
class GameSession:
    """Sesión activa de juego manual en una sala."""
    room_id: int
    room_name: str
    phase: str = "lobby"            # lobby | countdown | playing | finished
    players: dict[str, PlayerState] = dc_field(default_factory=dict)
    deck: list[int] = dc_field(default_factory=list)
    cards_called: set[int] = dc_field(default_factory=set)  # card_ids ya cantados
    cards_history: list[dict] = dc_field(default_factory=list)
    current_card_id: int | None = None
    turns_played: int = 0
    griton_delay_ms: int = 2000     # ms entre cartas (modulado por Agility)
    highlight_window_ms: int = 2000 # ms de ventana activa (modulado por Focus)
    winner_axo_id: int | None = None
    win_type: str | None = None
    started_at: float | None = None
    card_task: asyncio.Task | None = None  # tarea asyncio del ciclo de cartas


# ---------------------------------------------------------------------------
# Connection Manager
# ---------------------------------------------------------------------------


class GameWSManager:
    """
    Gestor central de conexiones WebSocket para el modo manual.

    Uso:
        manager = GameWSManager()
        await manager.connect(room_id, user_id, ws, player_info)
        await manager.start_game(room_id)
        # ... el ciclo de cartas corre en background ...
        await manager.disconnect(room_id, user_id)
    """

    def __init__(self) -> None:
        self.sessions: dict[int, GameSession] = {}       # room_id → GameSession
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(
        self,
        room_id: int,
        user_id: str,
        ws: WebSocket,
        axolotito_id: int,
        axo_name: str,
        board_ids: list[int],
        board_card_ids: dict[int, list[int]],
        play_mode: str = "manual",
    ) -> None:
        """Acepta la conexión WebSocket y registra al jugador en la sesión."""
        # 1. Si ya existe una conexión para este usuario en esta sala, desplazarla
        session_obj = self.sessions.get(room_id)
        if session_obj:
            existing_player = session_obj.players.get(user_id)
            if existing_player and existing_player.ws and existing_player.ws != ws:
                try:
                    await existing_player.ws.send_json({
                        "type": "session_replaced",
                        "message": "Se ha iniciado sesión en otra pestaña. Esta sesión ha sido desconectada."
                    })
                    await existing_player.ws.close(code=4008, reason="session_replaced")
                except Exception as ws_err:
                    logger.debug(f"Error cerrando WebSocket desplazado en connect para {user_id}: {ws_err}")

        await ws.accept()

        async with self._lock:
            if room_id not in self.sessions:
                self.sessions[room_id] = GameSession(room_id=room_id, room_name=f"Sala #{room_id}")

            session = self.sessions[room_id]
            player = PlayerState(
                user_id=user_id,
                axolotito_id=axolotito_id,
                axo_name=axo_name,
                board_ids=board_ids,
                board_card_ids=board_card_ids,
                play_mode=play_mode,
                ws=ws,
            )
            session.players[user_id] = player

        # Notificar a los demás
        await self.broadcast(room_id, {
            "type": "player_joined",
            "axolotito_id": axolotito_id,
            "axo_name": axo_name,
            "player_count": len(session.players),
        }, exclude=user_id)

    async def disconnect(self, room_id: int, user_id: str, ws: WebSocket) -> None:
        """Maneja la desconexión de un jugador. Mantiene el estado 15s para reconnect."""
        session = self.sessions.get(room_id)
        if not session:
            return
        player = session.players.get(user_id)
        if player:
            # Validar que la desconexión proviene del WebSocket activo actualmente
            if player.ws != ws:
                logger.info(f"Desconexión obsoleta ignorada para el usuario {user_id} en sala {room_id}")
                return
            
            player.connected = False
            player.ws = None

        await self.broadcast(room_id, {
            "type": "player_left",
            "axo_name": player.axo_name if player else "???",
            "player_count": sum(1 for p in session.players.values() if p.connected),
        })

        if player and player.play_mode == "manual":
            asyncio.create_task(self._disconnect_grace_period(room_id, user_id))

    async def _disconnect_grace_period(self, room_id: int, user_id: str) -> None:
        """Espera 15 segundos de gracia y, si no se ha reconectado, cambia a modo auto-play."""
        await asyncio.sleep(15)
        session = self.sessions.get(room_id)
        if not session or session.phase == "finished":
            return
        player = session.players.get(user_id)
        if player and not player.connected and player.play_mode == "manual":
            player.play_mode = "auto"
            try:
                from app.database import engine
                from sqlmodel import Session as DBSession, select
                from app.models.lobby_models import RoomRegistration
                with DBSession(engine) as db_session:
                    db_reg = db_session.exec(
                        select(RoomRegistration)
                        .where(RoomRegistration.room_id == room_id)
                        .where(RoomRegistration.axolotito_id == player.axolotito_id)
                    ).first()
                    if db_reg:
                        db_reg.play_mode = "auto"
                        db_session.add(db_reg)
                        db_session.commit()
            except Exception as db_err:
                logger.warning(f"Error actualizando play_mode a auto tras desconexión en DB para room {room_id}, axo {player.axolotito_id}: {db_err}")

            await self.broadcast(room_id, {
                "type": "player_afk",
                "axo_name": player.axo_name,
                "message": f"{player.axo_name} no reconectó en 15 segundos. El bot asume el control."
            })

    async def reconnect(
        self, room_id: int, user_id: str, ws: WebSocket, play_mode: str = "manual"
    ) -> bool:
        """Intenta reconectar a un jugador. Retorna True si exitoso."""
        session = self.sessions.get(room_id)
        if not session:
            return False
        player = session.players.get(user_id)
        if not player:
            return False

        # Si ya hay un WebSocket diferente conectado, notificar y desplazar
        if player.ws and player.ws != ws:
            try:
                await player.ws.send_json({
                    "type": "session_replaced",
                    "message": "Se ha iniciado sesión en otra pestaña. Esta sesión ha sido desconectada."
                })
                await player.ws.close(code=4008, reason="session_replaced")
            except Exception as ws_err:
                logger.debug(f"Error cerrando WebSocket desplazado en reconnect para {user_id}: {ws_err}")

        await ws.accept()
        player.ws = ws
        player.connected = True
        player.play_mode = play_mode
        player.missed_turns_count = 0

        # Enviar estado actual para que el frontend se sincronice
        await ws.send_json({
            "type": "game_state_sync",
            "phase": session.phase,
            "play_mode": player.play_mode,
            "cards_history": session.cards_history,
            "current_card_id": session.current_card_id,
            "player_marked": {str(bid): list(s) for bid, s in player.marked_indices.items()},
            "turns_played": session.turns_played,
            "griton_delay_ms": session.griton_delay_ms,
            "highlight_window_ms": session.highlight_window_ms,
            "opponents": [
                {"axo_name": p.axo_name, "marked_count": sum(len(s) for s in p.marked_indices.values())}
                for uid, p in session.players.items() if uid != user_id
            ],
        })
        return True

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    async def start_game(self, room_id: int, all_card_ids: list[int]) -> None:
        """Inicia la partida: countdown → barajar → ciclo de cartas."""
        session = self.sessions.get(room_id)
        if not session:
            return

        session.phase = "countdown"
        session.started_at = time.time()

        # Countdown 3..2..1..YA
        for i in range(3, 0, -1):
            await self.broadcast(room_id, {"type": "countdown", "seconds": i})
            await asyncio.sleep(1)
        await self.broadcast(room_id, {"type": "countdown", "seconds": 0, "message": "YA!"})

        # Barajar mazo
        deck = all_card_ids.copy()
        _rng.shuffle(deck)
        session.deck = deck
        session.phase = "playing"
        session.cards_called = set()

        await self.broadcast(room_id, {
            "type": "game_start",
            "room_id": room_id,
            "players": [
                {"axolotito_id": p.axolotito_id, "axo_name": p.axo_name}
                for p in session.players.values()
            ],
            "total_cards": len(deck),
            "griton_delay_ms": session.griton_delay_ms,
            "highlight_window_ms": session.highlight_window_ms,
        })

        # Lanzar ciclo de cartas en background
        session.card_task = asyncio.create_task(self._card_cycle(room_id))

    async def _card_cycle(self, room_id: int) -> None:
        """El Gritón: itera el mazo cantando una carta cada griton_delay_ms."""
        session = self.sessions.get(room_id)
        if not session or not session.deck:
            return

        # Importación local para evitar circular imports
        from app.services.game_logic import check_tension_status

        for card_id in session.deck:
            if session.phase == "finished":
                break

            session.current_card_id = card_id
            session.cards_called.add(card_id)
            session.turns_played += 1
            session.cards_history.append({
                "card_id": card_id,
                "turn": session.turns_played,
                "timestamp_ms": int(time.time() * 1000),
            })

            # Broadcast de la carta cantada
            await self.broadcast(room_id, {
                "type": "card_called",
                "card_id": card_id,
                "turn": session.turns_played,
                "window_ms": session.highlight_window_ms,
                "timestamp_ms": int(time.time() * 1000),
            })

            # Esperar la ventana de highlight
            await asyncio.sleep(session.highlight_window_ms / 1000.0)

            # AFK Detection: check if any manual player missed marking this card
            for p in list(session.players.values()):
                if p.play_mode == "manual":
                    primary_board = p.board_ids[0] if p.board_ids else None
                    if primary_board:
                        board_cards = p.board_card_ids.get(primary_board, [])
                        if card_id in board_cards:
                            idx = board_cards.index(card_id)
                            marked_set = p.marked_indices.get(primary_board, set())
                            if idx not in marked_set:
                                p.missed_turns_count += 1
                                if p.missed_turns_count >= 3:
                                    p.play_mode = "auto"
                                    try:
                                        from app.database import engine
                                        from sqlmodel import Session as DBSession, select
                                        from app.models.lobby_models import RoomRegistration
                                        with DBSession(engine) as db_session:
                                            db_reg = db_session.exec(
                                                select(RoomRegistration)
                                                .where(RoomRegistration.room_id == room_id)
                                                .where(RoomRegistration.axolotito_id == p.axolotito_id)
                                            ).first()
                                            if db_reg:
                                                db_reg.play_mode = "auto"
                                                db_session.add(db_reg)
                                                db_session.commit()
                                    except Exception as db_err:
                                        logger.warning(f"Error actualizando play_mode a auto en DB para room {room_id}, axo {p.axolotito_id}: {db_err}")

                                    # Warn player
                                    if p.ws and p.connected:
                                        try:
                                            await p.ws.send_json({
                                                "type": "afk_warning",
                                                "message": "El bot de tu Axolotito ha asumido el control debido a inactividad prolongada (+3 turnos perdidos). Estás en modo espectador."
                                            })
                                        except Exception:
                                            pass
                                    # Broadcast AFK event
                                    await self.broadcast(room_id, {
                                        "type": "player_afk",
                                        "axo_name": p.axo_name,
                                        "message": f"{p.axo_name} se ha quedado AFK. El bot asume el control."
                                    })

            # Evaluar tensión entre cartas
            tension = check_tension_status([
                {
                    "axo_id": p.axolotito_id,
                    "marked_indices": list(
                        p.marked_indices.get(p.board_ids[0], set())
                        if p.board_ids else set()
                    ),
                }
                for p in session.players.values()
            ])
            await self.broadcast(room_id, {
                "type": "tension_update",
                "level": tension.level,
                "near_win": tension.near_win_players,
            })

            # Esperar el delay entre cartas (menos la ventana ya transcurrida)
            remaining_delay = max(0, session.griton_delay_ms - session.highlight_window_ms)
            await asyncio.sleep(remaining_delay / 1000.0)

        # Si se acaba el mazo sin ganador
        if session.phase == "playing":
            await self._end_game(room_id, winner_axo_id=None)

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    async def handle_mark_cell(self, room_id: int, user_id: str, cell_index: int) -> None:
        """El jugador marca una celda en su tablero."""
        session = self.sessions.get(room_id)
        if not session or session.phase != "playing":
            return
        player = session.players.get(user_id)
        if not player or not player.connected:
            return

        if player.play_mode == "auto":
            await self._send_error(player, "El bot de tu Axolotito ha asumido el control debido a inactividad prolongada (+3 turnos perdidos). Estás en modo espectador.")
            return

        # Validar que la celda sea válida (0-15)
        if not (0 <= cell_index <= 15):
            await self._send_error(player, "Celda inválida.")
            return

        # Validar que la carta actual esté en el tablero del jugador
        if session.current_card_id is None:
            await self._send_error(player, "No hay carta activa para marcar.")
            return

        # Marcar en el primer board (modo manual: 1 tablero a la vez)
        primary_board = player.board_ids[0] if player.board_ids else None
        if not primary_board:
            return
        if primary_board not in player.marked_indices:
            player.marked_indices[primary_board] = set()

        board_cards = player.board_card_ids.get(primary_board, [])
        if cell_index >= len(board_cards):
            await self._send_error(player, "Índice de celda fuera del tablero.")
            return

        # Verificar que la carta en esa celda ya fue cantada
        card_at_cell = board_cards[cell_index]
        if card_at_cell not in session.cards_called:
            await self._send_error(player, "Esa carta aún no ha sido cantada.")
            return

        # Verificar que no esté ya marcada
        if cell_index in player.marked_indices[primary_board]:
            return  # ya marcada, ignorar silenciosamente

        player.marked_indices[primary_board].add(cell_index)
        player.missed_turns_count = 0

        # Confirmar al jugador
        if player.ws:
            await player.ws.send_json({
                "type": "cell_marked",
                "cell_index": cell_index,
                "board_id": primary_board,
            })

    async def handle_shout_loteria(self, room_id: int, user_id: str) -> None:
        """El jugador grita ¡Lotería! — validar si realmente ganó."""
        session = self.sessions.get(room_id)
        if not session or session.phase != "playing":
            return
        player = session.players.get(user_id)
        if not player or not player.connected:
            return

        if player.play_mode == "auto":
            await self._send_error(player, "El bot de tu Axolotito ha asumido el control debido a inactividad prolongada (+3 turnos perdidos). Estás en modo espectador.")
            return

        # Validar cada board del jugador
        from app.services.game_logic import validate_win

        for board_id in player.board_ids:
            marked = player.marked_indices.get(board_id, set())
            board_cards = player.board_card_ids.get(board_id, [])

            is_valid, win_type, winning_cells = validate_win(
                marked_indices=marked,
                called_card_ids=session.cards_called,
                board_card_ids=board_cards,
            )

            if is_valid:
                # ¡GANADOR!
                session.phase = "finished"
                session.winner_axo_id = player.axolotito_id
                session.win_type = win_type

                await self.broadcast(room_id, {
                    "type": "loteria_validated",
                    "player_axo_id": player.axolotito_id,
                    "player_name": player.axo_name,
                    "win_type": win_type,
                    "cells": list(winning_cells) if winning_cells else [],
                    "board_id": board_id,
                })

                # Cancelar el ciclo de cartas
                if session.card_task and not session.card_task.done():
                    session.card_task.cancel()

                # Breve pausa dramática y terminar
                await asyncio.sleep(2)
                await self._end_game(room_id, winner_axo_id=player.axolotito_id)
                return

        # Grito inválido — penalización
        await self._send_error(player, "¡Lotería inválida! No has completado una línea o cuadrito. Penalización: -5 FRJ.")

    async def handle_use_hint(self, room_id: int, user_id: str) -> None:
        """El jugador usa una pista visual (Focus stat)."""
        session = self.sessions.get(room_id)
        if not session or session.phase != "playing":
            return
        player = session.players.get(user_id)
        if not player or not player.connected:
            return

        if player.play_mode == "auto":
            await self._send_error(player, "El bot de tu Axolotito ha asumido el control debido a inactividad prolongada (+3 turnos perdidos). Estás en modo espectador.")
            return

        if player.hints_remaining <= 0:
            await self._send_error(player, "No te quedan pistas disponibles.")
            return

        if session.current_card_id is None:
            return

        player.hints_remaining -= 1

        # Encontrar en qué celdas del tablero del jugador está la carta actual
        primary_board = player.board_ids[0] if player.board_ids else None
        if not primary_board:
            return
        board_cards = player.board_card_ids.get(primary_board, [])
        hint_cells = [
            idx for idx, cid in enumerate(board_cards)
            if cid == session.current_card_id and idx not in player.marked_indices.get(primary_board, set())
        ]

        if player.ws:
            await player.ws.send_json({
                "type": "hint_activated",
                "cell_indices": hint_cells,
                "hints_remaining": player.hints_remaining,
            })

    # ------------------------------------------------------------------
    # Game end
    # ------------------------------------------------------------------

    async def _end_game(self, room_id: int, winner_axo_id: int | None) -> None:
        """Finaliza la partida y notifica a todos los jugadores."""
        session = self.sessions.get(room_id)
        if not session:
            return
        session.phase = "finished"

        # Resolve the match in the database using the actual marks and turns
        try:
            from app.services.multiplayer_service import MultiplayerService
            player_marked_data = {}
            for p in list(session.players.values()):
                primary_board = p.board_ids[0] if p.board_ids else None
                if primary_board:
                    player_marked_data[p.axolotito_id] = list(p.marked_indices.get(primary_board, set()))
                else:
                    player_marked_data[p.axolotito_id] = []

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                MultiplayerService.resolve_multiplayer_match,
                room_id,
                winner_axo_id,
                session.turns_played,
                player_marked_data,
                list(session.cards_called)
            )
        except Exception as e:
            logger.error(f"Error resolving manual match in DB for room {room_id}: {e}", exc_info=True)

        await self.broadcast(room_id, {
            "type": "game_end",
            "winner_axo_id": winner_axo_id,
            "turns_played": session.turns_played,
            "message": f"¡Partida terminada en {session.turns_played} turnos!",
        })

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    async def broadcast(
        self, room_id: int, message: dict[str, Any], exclude: str | None = None
    ) -> None:
        """Envía un mensaje JSON a todos los jugadores conectados en la sala."""
        session = self.sessions.get(room_id)
        if not session:
            return

        disconnected: list[str] = []
        for user_id, player in session.players.items():
            if exclude and user_id == exclude:
                continue
            if player.ws and player.connected:
                try:
                    await player.ws.send_json(message)
                except Exception:
                    disconnected.append(user_id)

        # Limpiar conexiones muertas
        for uid in disconnected:
            session.players[uid].connected = False
            session.players[uid].ws = None

    async def _send_error(self, player: PlayerState, message: str) -> None:
        """Envía un mensaje de error a un jugador específico."""
        if player.ws and player.connected:
            try:
                await player.ws.send_json({"type": "error", "message": message})
            except Exception:
                player.connected = False
                player.ws = None

    def get_player_count(self, room_id: int) -> int:
        """Número de jugadores conectados en la sala."""
        session = self.sessions.get(room_id)
        if not session:
            return 0
        return sum(1 for p in session.players.values() if p.connected)

    def get_session(self, room_id: int) -> GameSession | None:
        """Retorna la sesión de juego de la sala, o None."""
        return self.sessions.get(room_id)


# Instancia singleton — compartida entre el endpoint WebSocket y el scheduler
ws_manager = GameWSManager()
