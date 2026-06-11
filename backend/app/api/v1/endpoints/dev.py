"""
dev.py — Endpoints de desarrollo. Solo activos en BLOCKCHAIN_MODE=local.

Rutas:
  POST /api/v1/dev/reset-tutorial          — Resetea el tutorial del usuario autenticado
  POST /api/v1/dev/fill-multiplayer-rooms  — Llena una sala con jugadores mock para testing

Seguridad:
  - El router entero solo se monta si BLOCKCHAIN_MODE == "local" (main.py).
  - Dependency de router: _check_dev_mode_dep (404 si no es local, no revela existencia).
  - Todos los endpoints requieren autenticación de admin (require_admin).
"""

import json
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.core.auth import get_verified_user_id, require_admin
from app.core.config import settings
from app.core.prices import MULTIPLAYER_FEES
from app.database import get_session
from app.models.items import WebitoIncubation, ItemCatalog, ItemType
from app.models.promo import PendingReward, PromoCode
from app.models.user import User
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet
from app.models.lobby_models import GameRoom, RoomRegistration
from app.services.multiplayer_service import get_or_create_waiting_room

_rng = random.SystemRandom()

# ── Dev Auto-Reward ────────────────────────────────────────────────────
# Valores modestos para testing local. Fuente de verdad para user_service y simulación.
DEV_AUTO_REWARD_AXF: float = 1000.0
DEV_AUTO_REWARD_FRJ: float = 5000.0


def _check_dev_mode_dep():
    """Dependency del router: bloquea con 404 si no es modo local.
    Usa 404 en vez de 403 para no revelar la existencia de estos endpoints en producción."""
    if settings.BLOCKCHAIN_MODE != "local":
        raise HTTPException(status_code=404)


router = APIRouter(dependencies=[Depends(_check_dev_mode_dep)])


@router.post("/reset-tutorial")
def reset_tutorial(
    delete_axolotito: bool = False,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
    _admin: str = Depends(require_admin),
):
    """
    Resetea completamente el estado del tutorial del usuario autenticado:
    - WebitoIncubation: tutorial_phase=0, tutorial_karma=None, imprinting_complete=False
    - User: tutorial_completed=False, is_new_user tratado como False (no se toca)
    - Opcional: elimina el Axolotito nacido del tutorial si delete_axolotito=True

    Requiere autenticación de admin. Solo disponible con BLOCKCHAIN_MODE=local.
    """

    actions = []

    # 1. Reset todas las incubaciones del usuario (normalmente solo hay una tutorial)
    incubations = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
    ).all()

    for inc in incubations:
        inc.tutorial_phase = 0
        inc.tutorial_act_index = 0
        inc.tutorial_karma = None
        inc.imprinting_complete = False
        session.add(inc)
        actions.append(f"incubación #{inc.id} reseteada (phase=0)")

    # 2. Reset tutorial_completed en el User
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if user:
        user.tutorial_completed = False
        session.add(user)
        actions.append("User.tutorial_completed = False")

    # 2b. Reset VIP subscription
    if user:
        user.vip_tier = None
        user.vip_expires_at = None
        user.vip_streak_months = 0
        user.vip_streak_last_renewed = None
        user.vip_pending_gal = 0
        user.vip_pending_gal_expires_at = None
        user.vip_last_daily_gal_at = None
        user.vip_tiers_activated = "[]"
        user.vip_auto_renew = False
        session.add(user)
        actions.append("VIP subscription reseteada")

    # 2c. Asegurar PendingReward: resetear claimed si existe, crear si no existe
    pending = session.exec(
        select(PendingReward).where(PendingReward.user_id == user_id)
    ).first()
    if pending:
        if pending.claimed:
            pending.claimed = False
            pending.claimed_at = None
            session.add(pending)
            actions.append(f"PendingReward #{pending.id} reseteada (claimed=False)")
        else:
            actions.append(f"PendingReward #{pending.id} ya estaba pendiente")
    else:
        # Create if missing — dev auto-reward
        dev_code = session.exec(
            select(PromoCode).where(PromoCode.code == "DEV_AUTO")
        ).first()
        if not dev_code:
            dev_code = PromoCode(
                code="DEV_AUTO",
                batch="dev",
                reward_type="booster_pack",
                reward_axofichas=DEV_AUTO_REWARD_AXF,
                reward_frijolitos=DEV_AUTO_REWARD_FRJ,
            )
            session.add(dev_code)
            session.flush()
        pending = PendingReward(
            user_id=user_id,
            promo_code_id=dev_code.id,
            reward_axf=DEV_AUTO_REWARD_AXF,
            reward_frj=DEV_AUTO_REWARD_FRJ,
            expires_at=datetime.utcnow() + timedelta(days=365),
        )
        session.add(pending)
        actions.append(f"PendingReward creada: {DEV_AUTO_REWARD_AXF:.0f} AXF + {DEV_AUTO_REWARD_FRJ:.0f} FRJ")

    # 3. Opcional: eliminar Axolotito nacido
    if delete_axolotito:
        axos = session.exec(
            select(Axolotito).where(Axolotito.user_id == user_id)
        ).all()
        for axo in axos:
            session.delete(axo)
            actions.append(f"Axolotito #{axo.id} '{axo.name}' eliminado")

    session.commit()

    return {
        "ok": True,
        "message": f"Tutorial reseteado. Acciones: {len(actions)}",
        "actions": actions,
        "user_id": user_id,
    }


@router.post("/skip-tutorial")
def skip_tutorial(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
    _admin: str = Depends(require_admin),
):
    """
    Brinca el tutorial del usuario de inmediato:
    - Asegura que exista una incubación tutorial (si no, la crea).
    - Fuerza phase = 4 y completa el tutorial (lo que hace nacer el axolotito y crea la tabla).
    - Asigna un número aleatorio de victorias y derrotas en la tabla creada.
    - Devuelve el resultado de la eclosión.
    """
    from app.services.tutorial_service import TutorialService
    from app.api.v1.endpoints.tutorial import _board_from_user_id

    # 1. Obtener o crear incubación de tutorial
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.user_id == user_id)
        .where(WebitoIncubation.tutorial_phase < 5)
    ).first()

    if not incubation:
        # Buscar primer huevo del catálogo para crear incubación
        egg_item = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.EGG)
        ).first()
        if not egg_item:
            raise HTTPException(
                status_code=500,
                detail="No hay huevos en el catálogo para iniciar tutorial.",
            )
        incubation = WebitoIncubation(
            user_id=user_id,
            item_id=egg_item.id,
            fecha_eclosion_estimada=datetime.utcnow(),
            bonus_focus=20.0,
            bonus_luck=20.0,
            bonus_agility=20.0,
            bonus_stamina=100,
            bonus_salinity_adj=5.0,
            tutorial_phase=0,
            tutorial_act_index=0,
        )
        session.add(incubation)
        session.flush()

    # Asegurar que tenga card ids asignados
    if not incubation.tutorial_board_card_ids:
        incubation.tutorial_board_card_ids = _board_from_user_id(user_id, session)

    # 2. Forzar phase = 4 y karma aleatorio
    incubation.tutorial_phase = 4
    incubation.tutorial_karma = _rng.choice(["lucky", "salty"])
    session.add(incubation)
    session.flush()

    # 3. Completar tutorial (eclosiona + crea tabla tutorial)
    result = TutorialService.complete_tutorial(session, user_id, incubation)

    # 4. Asignar victorias y derrotas aleatorias al tablero creado
    # El tablero creado por complete_tutorial tiene is_tutorial=True y pertenece al usuario
    board = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_tutorial == True)
    ).first()

    if board:
        # Generar victorias/derrotas aleatorias
        games_played = _rng.randint(5, 30)
        games_won = _rng.randint(0, games_played)
        
        board.games_played = games_played
        board.games_won = games_won
        
        # Llenar recent_games_results
        recent_len = min(5, games_played)
        recent_results = []
        for _ in range(recent_len):
            if games_played > 0 and (_rng.random() < (games_won / games_played)):
                recent_results.append(True)
            else:
                recent_results.append(False)
        board.recent_games_results = recent_results
        
        session.add(board)
        session.commit()

    return {
        "ok": True,
        "message": "Tutorial brincado con éxito. Se asignaron estadísticas aleatorias a tu tabla.",
        "tutorial_result": result,
    }




@router.post("/fill-multiplayer-rooms")
def fill_multiplayer_rooms(
    room_type: str = Query(default="rookie_pool", description="rookie_pool o champion_abyss"),
    count: int = Query(default=3, ge=1, le=5, description="Número de jugadores mock (1-5)"),
    axf_amount: float = Query(default=0.0, ge=0.0, description="Cantidad de AXF (axofichas) por jugador mock"),
    frj_amount: float = Query(default=10000.0, ge=0.0, description="Cantidad de FRJ (frijolitos) por jugador mock"),
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
    _admin: str = Depends(require_admin),
):
    """
    Crea jugadores mock (did:privy:dev_mock_1..N) con Axolotitos y tablas,
    les da AXF y FRJ y los inscribe en la sala de espera indicada.

    Las salas pobladas SOLO con mocks no inician automáticamente en modo local —
    permanecen en 'waiting' hasta que el desarrollador se une.

    Requiere autenticación de admin. Solo disponible con BLOCKCHAIN_MODE=local.
    """
    _room_type = room_type
    if _room_type == "rookie":
        _room_type = "rookie_pool"
    elif _room_type == "champion":
        _room_type = "champion_abyss"

    if _room_type not in ("rookie_pool", "champion_abyss"):
        raise HTTPException(status_code=400, detail="room_type debe ser 'rookie_pool' o 'champion_abyss'.")

    fee = MULTIPLAYER_FEES[_room_type]
    budget_per_mock = fee * 10  # 10 partidas de presupuesto para testing holgado

    # Obtener cartas disponibles para armar tablas
    all_cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
    ).all()
    if len(all_cards) < 16:
        raise HTTPException(
            status_code=500,
            detail=f"No hay suficientes cartas en la DB para crear tablas ({len(all_cards)} < 16)."
        )
    all_card_ids = [c.id for c in all_cards]

    actions = []

    for i in range(1, count + 1):
        mock_did = f"did:privy:dev_mock_{i}"
        mock_name = f"Mockito {i}"

        # --- 1. Usuario mock ---
        user = session.exec(select(User).where(User.privy_did == mock_did)).first()
        if not user:
            user = User(
                privy_did=mock_did,
                nickname=mock_name,
                tutorial_completed=True,
            )
            session.add(user)
            session.flush()
            actions.append(f"Usuario {mock_did} creado")
        else:
            actions.append(f"Usuario {mock_did} ya existe")

        # --- 2. Wallet con AXF/FRJ según lo especificado ---
        wallet = session.exec(select(Wallet).where(Wallet.user_id == mock_did)).first()
        if not wallet:
            wallet = Wallet(user_id=mock_did, frijolitos=frj_amount, axofichas=axf_amount)
            session.add(wallet)
            session.flush()
            actions.append(f"Wallet creada con {frj_amount:,.0f} FRJ + {axf_amount:,.0f} AXF para {mock_did}")
        elif wallet.frijolitos < budget_per_mock or wallet.axofichas < axf_amount:
            wallet.frijolitos = max(wallet.frijolitos, frj_amount)
            wallet.axofichas = max(wallet.axofichas, axf_amount)
            session.add(wallet)
            actions.append(f"Wallet recargada a {wallet.frijolitos:,.0f} FRJ + {wallet.axofichas:,.0f} AXF para {mock_did}")

        # --- 3. Axolotito mock ---
        axo = session.exec(select(Axolotito).where(Axolotito.user_id == mock_did)).first()
        if not axo:
            axo = Axolotito(
                user_id=mock_did,
                name=mock_name,
                status="idle",
                energy_current=100,
                stat_focus=60.0,
                stat_luck=15.0,
                stat_salinity=5.0,
                is_main=True,
            )
            session.add(axo)
            session.flush()
            actions.append(f"Axolotito '{mock_name}' creado (id={axo.id})")
        else:
            if axo.status == "playing":
                actions.append(f"Axolotito '{axo.name}' ya está jugando — omitido")
                continue
            axo.status = "idle"
            axo.energy_current = max(axo.energy_current, 10)
            session.add(axo)
            actions.append(f"Axolotito '{axo.name}' existente (id={axo.id})")

        # --- 4. PlayerBoard mock (1 tabla de 16 cartas random) ---
        board = session.exec(select(PlayerBoard).where(PlayerBoard.user_id == mock_did)).first()
        if not board:
            board_cards = _rng.sample(all_card_ids, 16)
            board = PlayerBoard(
                user_id=mock_did,
                name=f"Tabla de {mock_name}",
                card_ids=board_cards,
                card_first_editions=[False] * 16,
            )
            session.add(board)
            session.flush()
            actions.append(f"PlayerBoard creado para {mock_did} (id={board.id})")
        else:
            actions.append(f"PlayerBoard existente para {mock_did} (id={board.id})")

        # --- 5. Verificar que el mock no esté ya registrado en esta sala ---
        already_in_room = session.exec(
            select(RoomRegistration)
            .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
            .where(GameRoom.room_type == _room_type)
            .where(GameRoom.status == "waiting")
            .where(RoomRegistration.axolotito_id == axo.id)
        ).first()

        if already_in_room:
            actions.append(f"Mock {i} ya está registrado en sala {_room_type} — omitido")
            continue

        # --- 6. Registrar en sala ---
        room = get_or_create_waiting_room(session, _room_type, 1, user_id=mock_did)

        wallet.frijolitos -= budget_per_mock
        axo.escrow_balance_gal = budget_per_mock
        axo.bot_budget_axg = budget_per_mock
        axo.bot_loss_limit_axg = budget_per_mock * 0.8
        axo.bot_profit_limit_axg = budget_per_mock * 2.0
        axo.bot_enabled = True
        axo.status = "playing"
        session.add(axo)
        session.add(wallet)

        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json=json.dumps([board.id]),
        )
        session.add(reg)
        actions.append(f"Mock {i} inscrito en sala '{room.name}' (id={room.id})")

    session.commit()

    return {
        "ok": True,
        "room_type": _room_type,
        "mocks_requested": count,
        "message": f"{len([a for a in actions if 'inscrito' in a])} mock(s) inscritos en sala de espera.",
        "actions": actions,
    }
