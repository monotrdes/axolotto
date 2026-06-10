import hashlib
import json
import secrets as secrets_mod
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.core.prices import MULTIPLAYER_FEES
from app.core.auth import get_verified_user_id
from app.core.config import frj_to_internal, frj_to_display, FRJ_DECIMALS_BACKEND
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.lobby_models import TreasuryVault, JackpotVault, JackpotWin, GameRoom, RoomRegistration, MultiplayerGameLog, ActiveGameState
from app.models.user import User
from app.services.bank_service import BankService, assert_multijugador_currency
from app.services.multiplayer_service import get_or_create_waiting_room, _max_wait_seconds
from app.services.manual_game_service import ManualGameService
from app.services.pila_service import recovery_multiplier
from app.core.config import MULTIPLAYER_CURRENCY

router = APIRouter()

# --- INPUT SCHEMAS ---
class RegisterRequest(BaseModel):
    axolotito_id: int
    room_type: str # "rookie" o "champion"
    boards: List[int] # List of 1 to 3 board IDs
    budget_gal: float
    loss_limit_pct: float
    profit_limit_pct: float

class CreateRoomRequest(BaseModel):
    name: str                                    # Nombre de la sala
    game_type: str = "lotería_clásica"           # "lotería_clásica" | "lotería_rápida"
    buy_in_frj: float                            # Buy-in en FRJ (10-1000)
    max_players: int = 4                         # 2-8 según nivel de mesa
    visibility: str = "public"                   # "public" | "friends" | "private"
    speed: str = "normal"                        # "normal" | "rápido" | "turbo"
    win_patterns: List[str] = ["line", "cuadrito"]
    password: Optional[str] = None               # Contraseña opcional

class JoinRoomRequest(BaseModel):
    axolotito_id: int
    boards: List[int]
    budget_gal: float
    loss_limit_pct: float
    profit_limit_pct: float
    password: Optional[str] = None

def _hash_password(pw: str) -> str:
    return hashlib.sha256(f"axolotto_salt_{pw}".encode()).hexdigest()

# --- ENDPOINTS ---

@router.get("/unread-logs")
def get_unread_game_logs(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Devuelve los resultados de partidas no leídos para el usuario y los marca como notificados."""
    logs = session.exec(
        select(MultiplayerGameLog)
        .where(MultiplayerGameLog.user_id == verified_user_id)
        .where(MultiplayerGameLog.notified == False)  # noqa: E712
        .order_by(MultiplayerGameLog.created_at.asc())
    ).all()

    # Capturar datos ANTES del commit: después del commit los objetos SQLAlchemy
    # quedan "expirados" y su serialización con Pydantic v2 puede devolver 0/null.
    import json
    results = [
        {
            "id": log.id,
            "outcome": log.outcome,
            "axo_name": log.axo_name,
            "room_name": log.room_name,
            "net_gal": log.net_gal,
            "xp_gained": log.xp_gained,
            # Prize breakdown (2026-06)
            "prize_breakdown": json.loads(log.prize_breakdown_json) if log.prize_breakdown_json else [],
            "won_premio_1": log.won_premio_1,
            "won_premio_2": log.won_premio_2,
            "won_jackpot": log.won_jackpot,
            "entry_fee_paid": log.entry_fee_paid,
            "gross_prize_gal": log.gross_prize_gal,
        }
        for log in logs
    ]

    for log in logs:
        log.notified = True
        session.add(log)
    session.commit()

    return results


@router.post("/register")
def register_axolotito(
    req: RegisterRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Inscribe a un Axolotito y sus tablas en una sala de espera, reteniendo su presupuesto en escrow."""
    # 0. Obtener el objeto User
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 0.1 Normalizar room_type: aceptar legacy keys (rookie/champion)
    _room_type = req.room_type
    if _room_type == "rookie":
        _room_type = "rookie_pool"
    elif _room_type == "champion":
        _room_type = "champion_abyss"

    # 1. Validar Axolotito y pertenencia
    axo = session.get(Axolotito, req.axolotito_id)
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
        
    # 2. Validar estado y energía
    if axo.status != "idle":
        raise HTTPException(
            status_code=400, 
            detail=f"Tu Axolotito está ocupado (estado: {axo.status}). Debe estar Disponible."
        )
    if axo.energy_current < 10:
        raise HTTPException(
            status_code=400, 
            detail="Energía insuficiente. Tu Axolotito necesita mínimo 10 de energía para jugar."
        )
        
    # 3. Validar número de tablas (1 a 3)
    if not (1 <= len(req.boards) <= 3):
        raise HTTPException(status_code=400, detail="Debes registrar entre 1 y 3 tablas.")
        
    # 4. Validar pertenencia e integridad de las tablas
    for board_id in req.boards:
        board = session.get(PlayerBoard, board_id)
        if not board:
            raise HTTPException(status_code=400, detail=f"La tabla #{board_id} no existe.")
        if board.is_dead:
            raise HTTPException(status_code=400, detail=f"La tabla #{board_id} está desarmada.")
            
        # Validar pertenencia
        is_owner = board.user_id == verified_user_id
        is_active_renter = (
            board.renter_id == verified_user_id and 
            board.is_rented and 
            board.rent_expires_at and 
            board.rent_expires_at > datetime.utcnow()
        )
        if not (is_owner or is_active_renter):
            raise HTTPException(
                status_code=400, 
                detail=f"No tienes permiso de propiedad o arriendo activo sobre la tabla #{board_id}."
            )
            
    # 5. Validar que el presupuesto cubra al menos una entrada para cada tabla inscrita
    fee_per_board = MULTIPLAYER_FEES[_room_type]
    min_budget = fee_per_board * len(req.boards)
    if req.budget_gal < min_budget:
        raise HTTPException(
            status_code=400,
            detail=f"Presupuesto insuficiente. Requieres al menos {min_budget} GAL para jugar {len(req.boards)} tablas."
        )
        
    # 6. Validar balance de cartera del usuario (bloquear cartera de forma pesimista)
    # MULTIPLAYER CURRENCY: Solo Frijolitos (FRJ). Axofichas (AXF) prohibido por compliance.
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    assert_multijugador_currency(wallet, req.budget_gal)

    # --- TRANSACCIÓN ECONÓMICA A CUSTODIA (ESCROW) ---
    wallet.frijolitos -= req.budget_gal
    _budget_int = frj_to_internal(req.budget_gal)
    axo.escrow_balance_gal = _budget_int
    axo.bot_budget_axg = _budget_int
    axo.bot_loss_limit_axg = _budget_int * int(req.loss_limit_pct) // 100
    axo.bot_profit_limit_axg = _budget_int * int(req.profit_limit_pct) // 100
    axo.bot_enabled = True
    axo.status = "playing"
    
    # Crear registro contable (FRJ — moneda de juego)
    ledger_entry = TransactionLedger(
        user_id=verified_user_id,
        amount=req.budget_gal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Escrow FRJ para Axolotito {axo.name} en salas multijugador"
    )
    session.add(ledger_entry)
    
    # --- LÍMITE: 1 REGISTRO ACTIVO POR USUARIO POR TIPO DE SALA ---
    # Previene que un usuario llene una sala con múltiples Axolotitos suyos,
    # controlando el inicio de la partida y el tamaño de la bolsa.
    existing_reg = session.exec(
        select(RoomRegistration)
        .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
        .join(Axolotito, RoomRegistration.axolotito_id == Axolotito.id)
        .where(GameRoom.room_type == _room_type)
        .where(GameRoom.status == "waiting")
        .where(Axolotito.user_id == verified_user_id)
    ).first()
    if existing_reg:
        raise HTTPException(
            status_code=400,
            detail=f"Ya tienes un Axolotito en sala de espera '{req.room_type}'. "
                   "Espera a que termine la partida o retíralo antes de registrar otro."
        )

    # --- LÍMITE DE BILLETERA: 1 REGISTRO POR DIRECCIÓN DE BILLETERA POR TIPO DE SALA ---
    # Previene que un usuario con múltiples cuentas y la misma billetera llene la sala.
    if user.wallet_address:
        existing_wallet_reg = session.exec(
            select(RoomRegistration)
            .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
            .join(Axolotito, RoomRegistration.axolotito_id == Axolotito.id)
            .join(User, Axolotito.user_id == User.privy_did)
            .where(GameRoom.room_type == _room_type)
            .where(GameRoom.status == "waiting")
            .where(User.wallet_address == user.wallet_address)
        ).first()
        if existing_wallet_reg:
            raise HTTPException(
                status_code=400,
                detail=f"Ya hay un registro activo en la sala de espera '{req.room_type}' vinculado a tu dirección de billetera ({user.wallet_address})."
            )

    # --- ASIGNACIÓN DE SALA EN ESPERA ---
    room = get_or_create_waiting_room(session, req.room_type, len(req.boards), user_id=verified_user_id)
    
    # --- LÍMITE: MÁXIMO 5 TABLAS POR USUARIO/BILLETERA EN LA SALA ---
    # Previene que se acumulen más de 5 tablas del mismo usuario/billetera en la sala elegida.
    room_regs = session.exec(
        select(RoomRegistration)
        .where(RoomRegistration.room_id == room.id)
    ).all()
    user_boards_in_room = 0
    for r_reg in room_regs:
        reg_axo = session.get(Axolotito, r_reg.axolotito_id)
        if reg_axo:
            is_same_user = reg_axo.user_id == verified_user_id
            is_same_wallet = False
            if user.wallet_address:
                reg_owner = session.exec(select(User).where(User.privy_did == reg_axo.user_id)).first()
                if reg_owner and reg_owner.wallet_address == user.wallet_address:
                    is_same_wallet = True
            if is_same_user or is_same_wallet:
                user_boards_in_room += len(json.loads(r_reg.boards_json))
                
    if user_boards_in_room + len(req.boards) > 5:
        raise HTTPException(
            status_code=400,
            detail=f"Registrar estas tablas superaría el límite de 5 tablas por usuario/billetera en la sala '{room.name}'."
        )
    
    registration = RoomRegistration(
        room_id=room.id,
        axolotito_id=axo.id,
        boards_json=json.dumps(req.boards)
    )
    session.add(registration)
    session.add(axo)
    session.add(wallet)
    session.commit()
    
    return {
        "mensaje": f"Axolotito registrado con éxito en la sala '{room.name}'",
        "room_name": room.name,
        "entry_fee_gal": room.entry_fee_gal,
        "escrow_balance_gal": frj_to_display(axo.escrow_balance_gal)
    }

@router.get("/lobby")
def get_lobby_status(session: Session = Depends(get_session)):
    """Retorna las salas en espera con detalles de los Axolotitos y tablas registradas."""
    rooms = session.exec(select(GameRoom).where(GameRoom.status == "waiting")).all()
    room_details = []
    
    for r in rooms:
        regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == r.id)).all()
        registered_axolotitos = []
        total_boards = 0
        for reg in regs:
            axo = session.get(Axolotito, reg.axolotito_id)
            if axo:
                b_list = json.loads(reg.boards_json)
                total_boards += len(b_list)
                registered_axolotitos.append({
                    "id": axo.id,
                    "name": axo.name,
                    "skin_color": axo.skin_color,
                    "gill_type": axo.gill_type,
                    "eye_type": axo.eye_type,
                    "mouth_type": axo.mouth_type,
                    "tail_type": axo.tail_type,
                    "forehead_type": axo.forehead_type,
                    "limb_type": axo.limb_type,
                    "boards_count": len(b_list),
                    "owner_id": axo.user_id
                })
        elapsed = (datetime.utcnow() - r.created_at).total_seconds()
        max_wait = _max_wait_seconds(total_boards)
        secs_until_start = max(0, int(max_wait - elapsed))
        room_details.append({
            "id": r.id,
            "name": r.name,
            "room_type": r.room_type,
            "entry_fee_gal": r.entry_fee_gal,
            "total_boards": total_boards,
            "axolotitos": registered_axolotitos,
            "created_at": r.created_at,
            "seconds_until_start": secs_until_start,
        })
        
    return {
        "salas_espera": room_details
    }

@router.get("/jackpot")
def get_jackpot_status(session: Session = Depends(get_session)):
    """Retorna el acumulado del Jackpot de Oro e historial de ganadores recientes."""
    jackpot = session.exec(select(JackpotVault)).first()
    if not jackpot:
        _jp_seed = 1000 * (10 ** FRJ_DECIMALS_BACKEND)
        jackpot = JackpotVault(current_amount=_jp_seed, seed_amount=_jp_seed)
        session.add(jackpot)
        session.commit()
        session.refresh(jackpot)
        
    # Obtener últimas 10 victorias del Jackpot
    wins = session.exec(
        select(JackpotWin).order_by(JackpotWin.won_at.desc()).limit(10)
    ).all()
    
    history = []
    for w in wins:
        axo = session.get(Axolotito, w.axo_id)
        user = session.exec(select(User).where(User.privy_did == w.user_id)).first()
        history.append({
            "id": w.id,
            "axo_name": axo.name if axo else f"Axolotito #{w.axo_id}",
            "user_nickname": user.nickname if user and user.nickname else "Jugador Axolotto",
            "amount_won": w.amount_won,
            "cards_drawn_count": w.cards_drawn_count,
            "won_at": w.won_at
        })
        
    return {
        "current_amount": round(jackpot.current_amount, 2),
        "seed_amount": jackpot.seed_amount,
        "history": history
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER-HOSTED ROOMS (Cave Table)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/create-room")
def create_player_room(
    req: CreateRoomRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Crea una sala hosted por un jugador desde su mesa de la cueva.
    La sala aparece en el lobby bajo "Salas de Jugadores".
    """
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Validar buy-in
    if req.buy_in_frj < 10 or req.buy_in_frj > 1000:
        raise HTTPException(status_code=400, detail="El buy-in debe ser entre 10 y 1000 FRJ.")

    # Validar jugadores
    if req.max_players < 2 or req.max_players > 8:
        raise HTTPException(status_code=400, detail="Número de jugadores debe ser entre 2 y 8.")

    # Validar patrones de victoria
    valid_patterns = {"line", "cuadrito", "pocito", "esquinas", "cruz", "cruz_diagonal", "l_shape", "z_shape", "full_board"}
    if not req.win_patterns or not all(p in valid_patterns for p in req.win_patterns):
        raise HTTPException(status_code=400, detail=f"Patrones inválidos. Válidos: {sorted(valid_patterns)}")

    # Validar velocidad — afecta el timer
    speed_multipliers = {"normal": 1.0, "rápido": 0.6, "turbo": 0.3}

    # Validar nombre de sala
    if not req.name or len(req.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre de la sala debe tener al menos 2 caracteres.")

    # Convertir buy-in FRJ a GAL para consistencia con el sistema
    entry_fee_gal = req.buy_in_frj  # FRJ y GAL tienen paridad 1:1 en este contexto

    # Hash password si existe
    password_hash = _hash_password(req.password) if req.password else None

    room_config = {
        "game_type": req.game_type,
        "buy_in_frj": req.buy_in_frj,
        "max_players": req.max_players,
        "speed": req.speed,
        "speed_multiplier": speed_multipliers.get(req.speed, 1.0),
        "win_patterns": req.win_patterns,
        "created_by": verified_user_id,
    }

    room = GameRoom(
        name=req.name.strip(),
        room_type="player_hosted",
        entry_fee_gal=entry_fee_gal,
        status="waiting",
        host_id=verified_user_id,
        room_config=json.dumps(room_config),
        visibility=req.visibility,
        password_hash=password_hash,
    )
    session.add(room)
    session.commit()
    session.refresh(room)

    return {
        "room_id": room.id,
        "name": room.name,
        "room_type": room.room_type,
        "entry_fee_gal": room.entry_fee_gal,
        "visibility": room.visibility,
        "has_password": password_hash is not None,
        "config": room_config,
        "message": f"¡Sala '{room.name}' creada! Esperando jugadores.",
    }


@router.get("/player-rooms")
def get_player_rooms(
    search: Optional[str] = Query(default=None, description="Buscar por nombre de sala o host"),
    session: Session = Depends(get_session),
):
    """
    Lista las salas hosted por jugadores (visibles públicamente).
    Filtrable por nombre de sala o nickname del host.
    """
    rooms = session.exec(
        select(GameRoom)
        .where(GameRoom.room_type == "player_hosted")
        .where(GameRoom.status == "waiting")
        .where(GameRoom.visibility == "public")  # Solo públicas en este endpoint
    ).all()

    result = []
    for room in rooms:
        config = json.loads(room.room_config or "{}")
        host = session.exec(select(User).where(User.privy_did == room.host_id)).first()
        host_name = host.nickname if host and host.nickname else "Anfitrión"

        # Filtro de búsqueda
        if search:
            search_lower = search.lower()
            if search_lower not in room.name.lower() and search_lower not in host_name.lower():
                continue

        # Contar jugadores registrados
        regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == room.id)).all()
        player_count = len(regs)

        result.append({
            "id": room.id,
            "name": room.name,
            "host_name": host_name,
            "host_vip_tier": host.vip_tier if host and host.is_vip else None,
            "buy_in_frj": config.get("buy_in_frj", room.entry_fee_gal),
            "max_players": config.get("max_players", 4),
            "current_players": player_count,
            "speed": config.get("speed", "normal"),
            "win_patterns": config.get("win_patterns", ["line"]),
            "game_type": config.get("game_type", "lotería_clásica"),
            "has_password": room.password_hash is not None,
            "seconds_until_start": 0,  # Player rooms start when host decides or full
        })

    return {"rooms": result}


@router.post("/join-room/{room_id}")
def join_player_room(
    room_id: int,
    req: JoinRoomRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Unirse a una sala hosted por un jugador.
    Valida contraseña si la sala tiene una.
    """
    room = session.get(GameRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala no encontrada.")
    if room.room_type != "player_hosted":
        raise HTTPException(status_code=400, detail="Usa /register para salas oficiales.")
    if room.status != "waiting":
        raise HTTPException(status_code=400, detail="Esta sala ya no acepta jugadores.")

    # Validar contraseña
    if room.password_hash:
        if not req.password:
            raise HTTPException(status_code=403, detail="Esta sala requiere contraseña.")
        if _hash_password(req.password) != room.password_hash:
            raise HTTPException(status_code=403, detail="Contraseña incorrecta.")

    # Validar capacidad
    config = json.loads(room.room_config or "{}")
    max_players = config.get("max_players", 4)
    regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == room_id)).all()
    if len(regs) >= max_players:
        raise HTTPException(status_code=400, detail=f"La sala está llena ({max_players} jugadores máximo).")

    # Validar que el usuario no tenga ya un registro en esta sala
    user_regs = [
        r for r in regs
        if session.get(Axolotito, r.axolotito_id) and session.get(Axolotito, r.axolotito_id).user_id == verified_user_id
    ]
    if user_regs:
        raise HTTPException(status_code=400, detail="Ya tienes un Axolotito registrado en esta sala.")

    # Validar axolotito
    axo = session.get(Axolotito, req.axolotito_id)
    if not axo or axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
    if axo.status != "idle":
        raise HTTPException(status_code=400, detail=f"Axolotito ocupado (estado: {axo.status}).")
    if axo.energy_current < 10:
        raise HTTPException(status_code=400, detail="Energía insuficiente (mínimo 10).")

    # Validar tablas
    if not (1 <= len(req.boards) <= 3):
        raise HTTPException(status_code=400, detail="Debes registrar entre 1 y 3 tablas.")
    for board_id in req.boards:
        board = session.get(PlayerBoard, board_id)
        if not board or board.is_dead:
            raise HTTPException(status_code=400, detail=f"Tabla #{board_id} inválida.")
        is_owner = board.user_id == verified_user_id
        is_renter = (board.renter_id == verified_user_id and board.is_rented
                     and board.rent_expires_at and board.rent_expires_at > datetime.utcnow())
        if not (is_owner or is_renter):
            raise HTTPException(status_code=400, detail=f"No tienes permiso sobre la tabla #{board_id}.")

    # Validar presupuesto
    fee = room.entry_fee_gal * len(req.boards)
    if req.budget_gal < fee:
        raise HTTPException(status_code=400, detail=f"Presupuesto insuficiente. Necesitas al menos {fee} GAL.")
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    assert_multijugador_currency(wallet, req.budget_gal)

    # Mover fondos a escrow (FRJ)
    wallet.frijolitos -= req.budget_gal
    _budget_int = frj_to_internal(req.budget_gal)
    axo.escrow_balance_gal = _budget_int
    axo.bot_budget_axg = _budget_int
    axo.bot_loss_limit_axg = _budget_int * int(req.loss_limit_pct) // 100
    axo.bot_profit_limit_axg = _budget_int * int(req.profit_limit_pct) // 100
    axo.bot_enabled = True
    axo.status = "playing"

    session.add(TransactionLedger(
        user_id=verified_user_id,
        amount=req.budget_gal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Escrow FRJ para sala hosted '{room.name}' — Axo {axo.name}",
    ))

    registration = RoomRegistration(
        room_id=room.id,
        axolotito_id=axo.id,
        boards_json=json.dumps(req.boards),
    )
    session.add(registration)
    session.add(axo)
    session.add(wallet)
    session.commit()

    return {
        "joined": True,
        "room_name": room.name,
        "host_name": session.exec(select(User).where(User.privy_did == room.host_id)).first().nickname or "Anfitrión",
        "message": f"¡Te uniste a '{room.name}'! La partida comenzará pronto.",
    }


@router.post("/recall")
def recall_axolotito(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Retira al Axolotito inmediatamente de la sala de espera o lo marca para salir al terminar la partida actual."""
    axo = session.get(Axolotito, axolotito_id)
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
    if axo.status != "playing":
        raise HTTPException(
            status_code=400,
            detail=f"El Axolotito no está en partida activa ni en sala de espera (estado: {axo.status})."
        )

    # 1. Comprobar si el Axolotito está en una sala que aún está en espera ("waiting")
    reg = session.exec(
        select(RoomRegistration)
        .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
        .where(RoomRegistration.axolotito_id == axolotito_id)
        .where(GameRoom.status == "waiting")
    ).first()

    if reg:
        # Si la sala aún está en espera (no ha empezado la partida), lo removemos de inmediato
        session.delete(reg)
        axo.status = "waiting_settlement"  # Listo para corte de caja inmediato
        axo.wants_to_stop = False
        session.add(axo)
        session.commit()
        return {
            "mensaje": f"¡{axo.name} ha sido retirado de la sala de espera con éxito! Realiza el corte de caja (/settle) para recuperar tus fondos.",
            "immediate": True
        }

    # 2. Si ya está jugando (partida iniciada), se encola la salida segura al terminar el juego
    axo.wants_to_stop = True
    session.add(axo)
    session.commit()
    return {
        "mensaje": f"{axo.name} está jugando una partida activa. Terminará al finalizar este juego y regresará contigo.",
        "immediate": False
    }


@router.post("/settle")
def settle_axolotito_escrow(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    axo = session.exec(
        select(Axolotito)
        .where(Axolotito.id == axolotito_id)
        .with_for_update()
    ).first()
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
    if axo.status != "waiting_settlement":
        raise HTTPException(
            status_code=400, 
            detail="Este Axolotito no está listo para liquidación. Su estado debe ser 'waiting_settlement'."
        )
        
    # Calcular balance
    returned_amount = axo.escrow_balance_gal
    net_performance = returned_amount - axo.bot_budget_axg
    
    # Otorgar Bono de Afecto (Flat 5 puntos + 1 extra por cada 10 GAL de ganancia neta si aplica)
    loyalty_gained = 5
    if net_performance > 0:
        loyalty_gained += net_performance // 10
        
    # Devolver fondos a la billetera del usuario (FRJ)
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    wallet.frijolitos += returned_amount

    # Crear registro ledger (FRJ)
    ledger_entry = TransactionLedger(
        user_id=verified_user_id,
        amount=returned_amount,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD if net_performance >= 0 else TransactionType.WITHDRAW,
        description=f"Liquidacion de Escrow FRJ para {axo.name}: {returned_amount:.2f} FRJ devueltos (Neto: {net_performance:+.2f} FRJ)"
    )
    session.add(ledger_entry)
    
    # Actualizar Axolotito
    axo.escrow_balance_gal = 0
    axo.loyalty_points += loyalty_gained
    axo.status = "sleeping"
    # Sleep duration: 1 minute for quick gameplay testing, reduced by PILA (stamina)
    base_recovery_minutes = 1.0
    recovery_minutes = base_recovery_minutes * recovery_multiplier(axo.stat_stamina)
    if axo.nature == "hyperactive":
        recovery_minutes *= 0.75  # 25% faster recovery
    axo.sleep_expires_at = datetime.utcnow() + timedelta(minutes=recovery_minutes)
    
    session.add(axo)
    session.add(wallet)
    session.commit()
    session.refresh(axo)
    
    return {
        "mensaje": f"¡Corte de caja exitoso para {axo.name}! Recibes tu reporte.",
        "refunded_gal": round(returned_amount, 2),
        "net_performance": round(net_performance, 2),
        "loyalty_points_gained": loyalty_gained,
        "total_loyalty_points": axo.loyalty_points,
        "sleep_expires_at": axo.sleep_expires_at
    }


_manual_svc = ManualGameService()


@router.get("/game-state/{axolotito_id}")
def get_game_state(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Devuelve el estado en vivo de la partida en curso para el visor de modo auto.

    El frontend hace polling cada 2s para animar el tablero tick-por-tick
    mientras el Axolotito juega en background (AFK / espectador).
    """
    axo = session.get(Axolotito, axolotito_id)
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
    if axo.status != "playing":
        raise HTTPException(
            status_code=400,
            detail=f"El Axolotito no está en partida activa (estado: {axo.status})."
        )

    # Buscar la sala activa donde está registrado este Axolotito
    reg = session.exec(
        select(RoomRegistration)
        .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
        .where(RoomRegistration.axolotito_id == axolotito_id)
        .where(GameRoom.status == "playing")
    ).first()

    if not reg:
        raise HTTPException(
            status_code=404,
            detail="No se encontró partida activa para este Axolotito."
        )

    # Buscar el ActiveGameState de la sala
    game_state = session.exec(
        select(ActiveGameState)
        .where(ActiveGameState.room_id == reg.room_id)
    ).first()

    if not game_state:
        # La partida inició pero aún no hay estado registrado (primeros ticks)
        return {
            "phase": "playing",
            "room_name": "Sala de Juego",
            "turns_played": 0,
            "cards_drawn": [],
            "player_boards": [],
            "bot_boards": [],
            "tension_level": "low",
            "escrow_balance": frj_to_display(axo.escrow_balance_gal),
            "current_card": None,
        }

    import json
    cards_drawn = json.loads(game_state.cards_drawn_json) if game_state.cards_drawn_json else []
    player_states = json.loads(game_state.player_states_json) if game_state.player_states_json else {}

    # Construir respuesta para el jugador
    player_boards = []
    bot_boards = []
    b_ids = json.loads(reg.boards_json)

    for board_id in b_ids:
        key = str(board_id)
        state = player_states.get(key, {})
        player_boards.append({
            "board_id": board_id,
            "marked_indices": state.get("marked", []),
            "missed_indices": state.get("missed", []),
        })

    # Tableros de bots (otros participantes no-humanos)
    for key, state in player_states.items():
        if key.startswith("bot_"):
            bot_boards.append({
                "board_id": key,
                "marked_count": len(state.get("marked", [])),
            })

    # Obtener info de la carta actual
    current_card = None
    if game_state.current_card_id:
        from app.models.items import ItemCatalog, ItemType
        card = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.id == game_state.current_card_id,
                ItemCatalog.item_type == ItemType.CARD,
            )
        ).first()
        if card:
            meta = card.item_metadata or {}
            current_card = {
                "card_id": card.id,
                "numero": meta.get("numero_loteria"),
                "name": card.name,
            }

    room = session.get(GameRoom, reg.room_id)

    return {
        "phase": game_state.phase,
        "room_name": room.name if room else "Sala de Juego",
        "turns_played": game_state.turns_played,
        "cards_drawn": cards_drawn,
        "player_boards": player_boards,
        "bot_boards": bot_boards,
        "tension_level": game_state.tension_level,
        "escrow_balance": frj_to_display(axo.escrow_balance_gal),
        "current_card": current_card,
    }


@router.get("/manual-env/{axolotito_id}")
def get_manual_env(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Devuelve los parámetros de entorno para modo manual dado un Axolotito.

    El frontend llama a este endpoint antes de iniciar una partida manual para
    conocer la ventana de tiempo, el delay del gritón, las pistas visuales y
    la ventana crítica — todos modulados por los stats del Axolotito.

    El Axolotito debe pertenecer al usuario autenticado.
    """
    axo = session.get(Axolotito, axolotito_id)
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")

    # Modo manual: parámetros fijos estándar (el jugador ES el axolotito).
    # En modo manual NO se aplican modificadores de stat (spec §5).
    params = ManualGameService.fixed_params()

    return {
        "axolotito_id": axolotito_id,
        "axolotito_name": axo.name,
        "stats": {
            "suerte": axo.stat_luck,
            "ojo":    axo.stat_focus,
            "pila":   axo.stat_stamina,
            "sal":    axo.stat_salinity,
        },
        "env": _manual_svc.to_dict(params),
        "crit_probability_at_100_luck": _manual_svc.crit_probability(
            luck=axo.stat_luck, marked_in_window=True
        ),
    }
