from __future__ import annotations
import asyncio
import json
import random
from datetime import datetime

# Generador criptográficamente seguro para el sorteo — impide predecir el orden de cartas.
# random.SystemRandom usa /dev/urandom, a diferencia del Mersenne Twister del módulo random.
_rng = random.SystemRandom()
from sqlmodel import Session, select

from app.core.config import VIP_CONFIG, settings, FRJ_DECIMALS_BACKEND, frj_to_internal
from app.core.prices import MULTIPLAYER_ROOMS
from app.services.sal_service import sal_slip_chance, room_entropy
from app.database import engine
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import CurrencyType, TransactionType, TransactionLedger, Wallet
from app.models.items import ItemCatalog, ItemType
from app.models.lobby_models import TreasuryVault, JackpotVault, JackpotWin, GameRoom, RoomRegistration, MultiplayerGameLog, ActiveGameState
from app.models.user import User
from app.services.incubation_service import _apply_imprinting_if_needed

from app.services.game_logic import (
    WINNING_LINES,
    WINNING_CUADRITOS,
    check_loterica_line as check_line,
    PATTERN_CHECKERS,
    check_any_pattern,
)

def _max_wait_seconds(total_boards: int) -> int:
    """How long to wait before forcing room start (stepped by occupancy)."""
    if total_boards >= 30: return 0
    if total_boards >= 21: return 15
    if total_boards >= 11: return 20
    if total_boards >=  6: return 25
    if total_boards >=  3: return 35
    return 60  # 1–2 boards: wait up to 1 minute


def should_start_room(total_boards: int, elapsed_seconds: float) -> bool:
    """
    True when the room should start.
    Full room (≥30 boards) → immediate start.
    Otherwise, start after the board-count-scaled wait period.
    """
    if total_boards >= 30:
        return True
    if total_boards < 1:
        return False
    return elapsed_seconds >= _max_wait_seconds(total_boards)


def _entry_fee_internal(room: GameRoom) -> int:
    """Devuelve entry_fee_gal en unidades mínimas internas, manejando DB legacy.

    Salas nuevas + player-hosted: human-readable (ej. 10 = 10 FRJ, max 1000).
    Salas viejas oficiales: internal (ej. 100000 = 10 FRJ en unidad mínima).
    Umbral: >= 50000 → legacy internal; < 50000 → human-readable.
    """
    val = room.entry_fee_gal
    if val >= 50000:
        return int(val)  # ya está en unidades mínimas (legacy)
    return frj_to_internal(val)


def check_cuadrito(marked: set) -> bool:
    return any(sq.issubset(marked) for sq in WINNING_CUADRITOS)

def get_or_create_waiting_room(
    session: Session,
    room_type: str,
    boards_count: int,
    user_id: str | None = None
) -> GameRoom:
    """
    Obtiene o crea una sala de espera. Hard-cap: máximo 1 sala waiting por tipo oficial.
    Las salas oficiales se reutilizan siempre (sin números incrementales).
    Player-hosted rooms pueden tener múltiples instancias.
    """
    # Normalizar room_type: aceptar legacy keys
    _room_type = room_type
    if room_type == "rookie":
        _room_type = "rookie_pool"
    elif room_type == "champion":
        _room_type = "champion_abyss"

    # Obtener la dirección de billetera del usuario si se proporciona user_id
    wallet_address = None
    if user_id:
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user:
            wallet_address = user.wallet_address

    # Bloquear las salas de espera activas para evitar race conditions en registros simultáneos
    rooms = session.exec(
        select(GameRoom)
        .where(GameRoom.room_type == _room_type, GameRoom.status == "waiting")
        .with_for_update()
    ).all()

    # Para salas oficiales: hard-cap a 1 sala. Reutilizar la existente.
    is_official = _room_type in ("rookie_pool", "champion_abyss")

    for r in rooms:
        regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == r.id)).all()

        # Omitir salas donde el usuario o su wallet ya estén registrados
        already_registered = False
        if user_id and regs:
            # Precargar axolotitos y usuarios en batch para evitar N+1 (VULN-12)
            _axo_ids = [reg.axolotito_id for reg in regs]
            _axos_loaded = session.exec(select(Axolotito).where(Axolotito.id.in_(_axo_ids))).all()
            _axos_map = {a.id: a for a in _axos_loaded}

            _uids = set(a.user_id for a in _axos_loaded if a.user_id != user_id)
            _users_map: dict[str, User] = {}
            if wallet_address and _uids:
                _users_loaded = session.exec(select(User).where(User.privy_did.in_(_uids))).all()
                _users_map = {u.privy_did: u for u in _users_loaded}

            for reg in regs:
                reg_axo = _axos_map.get(reg.axolotito_id)
                if reg_axo:
                    if reg_axo.user_id == user_id:
                        already_registered = True
                        break
                    if wallet_address:
                        reg_owner = _users_map.get(reg_axo.user_id)
                        if reg_owner and reg_owner.wallet_address == wallet_address:
                            already_registered = True
                            break

        if already_registered:
            continue

        current_tables = sum(len(json.loads(reg.boards_json)) for reg in regs)
        if current_tables + boards_count <= 30:
            return r

    # Si llegamos aquí, necesitamos crear una nueva sala
    fee = MULTIPLAYER_ROOMS.get(_room_type, MULTIPLAYER_ROOMS.get(room_type, {}))
    _DEFAULT_FEE = 10  # FRJ human-readable
    fee_val = fee.get("fee", _DEFAULT_FEE) if isinstance(fee, dict) else _DEFAULT_FEE
    # entry_fee_gal stays human-readable; converted via frj_to_internal() at escrow time

    if _room_type == "rookie_pool":
        name = "Charco de Novatos"
    elif _room_type == "champion_abyss":
        name = "Fosa del Campeón"
    else:
        # Player-hosted rooms
        total_rooms_of_type = len(session.exec(
            select(GameRoom).where(GameRoom.room_type == room_type)
        ).all())
        index = total_rooms_of_type + 1
        name = f"Sala de {room_type} #{index}"

    new_room = GameRoom(
        name=name,
        room_type=_room_type if is_official else room_type,
        entry_fee_gal=fee_val,
        status="waiting",
    )
    session.add(new_room)
    session.flush()
    return new_room


class MultiplayerService:

    @staticmethod
    def update_host_activity(room_id: int) -> None:
        """Actualiza el timestamp de última actividad del host en el lobby.
        Evita la disolución automática por inactividad de 5 minutos."""
        with Session(engine) as session:
            room = session.get(GameRoom, room_id)
            if room and room.status == "waiting":
                room.last_host_activity_at = datetime.utcnow()
                session.add(room)
                session.commit()

    @staticmethod
    async def start_scheduler_loop():
        """Bucle asíncrono periódico que corre en segundo plano procesando los lobbies en espera."""
        print("🚀 [Multiplayer Scheduler] Iniciando bucle de matchmaking...")
        while True:
            try:
                await asyncio.sleep(10) # Ejecutar cada 10 segundos
                await MultiplayerService.process_waiting_rooms()
            except Exception as e:
                print(f"❌ [Multiplayer Scheduler] Error crítico en scheduler: {e}")

    @staticmethod
    async def process_waiting_rooms():
        """Busca salas en estado 'waiting' y evalúa si deben comenzar por tiempo o capacidad.
        También gestiona timeouts del lobby: ready-check de 2 min y disolución por host AFK de 5 min."""
        with Session(engine) as session:
            rooms = session.exec(select(GameRoom).where(GameRoom.status == "waiting")).all()
            for room in rooms:
                regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == room.id)).all()

                # ── Lobby Timeout: Disolución por Host AFK (5 min) ──
                if room.room_type == "player_hosted" and room.host_id:
                    if room.last_host_activity_at:
                        host_idle_seconds = (datetime.utcnow() - room.last_host_activity_at).total_seconds()
                    else:
                        host_idle_seconds = (datetime.utcnow() - room.created_at).total_seconds()

                    if host_idle_seconds > 300:  # 5 minutos
                        print(f"⏰ [Lobby Timeout] Disolviendo sala '{room.name}' por inactividad del host ({host_idle_seconds:.0f}s).")
                        # Devolver tablas y fondos del escrow a los jugadores
                        for reg in regs:
                            axo = session.get(Axolotito, reg.axolotito_id)
                            if axo:
                                b_ids = json.loads(reg.boards_json)
                                entry_fee = len(b_ids) * _entry_fee_internal(room)
                                axo.escrow_balance_gal += entry_fee
                                session.add(axo)
                            session.delete(reg)
                        room.status = "finished"
                        session.add(room)
                        session.commit()
                        continue

                # ── Lobby Timeout: Ready-Check (2 min desde countdown) ──
                if room.room_type == "player_hosted" and room.countdown_started_at:
                    countdown_elapsed = (datetime.utcnow() - room.countdown_started_at).total_seconds()
                    if countdown_elapsed > 120:  # 2 minutos
                        non_ready_regs = [r for r in regs if not r.ready]
                        if non_ready_regs:
                            print(f"⏰ [Lobby Timeout] Expulsando {len(non_ready_regs)} jugadores no listos de '{room.name}' (countdown: {countdown_elapsed:.0f}s).")
                            for reg in non_ready_regs:
                                axo = session.get(Axolotito, reg.axolotito_id)
                                if axo:
                                    b_ids = json.loads(reg.boards_json)
                                    entry_fee = len(b_ids) * _entry_fee_internal(room)
                                    axo.escrow_balance_gal += entry_fee
                                    session.add(axo)
                                session.delete(reg)
                            session.commit()
                            # Recargar registros después de la limpieza
                            regs = session.exec(select(RoomRegistration).where(RoomRegistration.room_id == room.id)).all()

                # Contar número total de tablas inscritas
                total_tables = 0
                for reg in regs:
                    b_list = json.loads(reg.boards_json)
                    total_tables += len(b_list)

                elapsed_seconds = (datetime.utcnow() - room.created_at).total_seconds()

                # En modo local: si la sala contiene SOLO jugadores mock, no iniciar.
                # La sala espera indefinidamente hasta que el dev real se una.
                if settings.BLOCKCHAIN_MODE == "local" and regs:
                    def _is_mock(reg: RoomRegistration) -> bool:
                        axo = session.get(Axolotito, reg.axolotito_id)
                        return axo is not None and axo.user_id.startswith("did:privy:dev_mock_")
                    if all(_is_mock(r) for r in regs):
                        continue

                # Condiciones para iniciar la partida:
                # 1. Capacidad máxima alcanzada (30 tablas)
                # 2. Timeout (30 segundos) con al menos 1 tabla (permite juego en solitario)
                # 3. Player-hosted: si todos los jugadores están ready después del countdown
                should_start = should_start_room(total_tables, elapsed_seconds)

                # Para salas player-hosted: iniciar si todos están ready y hay countdown activo
                if room.room_type == "player_hosted" and room.countdown_started_at and regs:
                    all_ready = all(r.ready for r in regs)
                    if all_ready and len(regs) >= 1:
                        should_start = True

                if should_start:
                    print(f"🎮 [Multiplayer Scheduler] Iniciando partida en la sala '{room.name}' ({total_tables} tablas)...")
                    # Bloquear sala inmediatamente cambiándole el estado
                    room.status = "playing"
                    session.add(room)
                    session.commit()

                    # Ejecutar simulación en thread para no bloquear el event loop
                    try:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(
                            None,
                            MultiplayerService.simulate_multiplayer_match,
                            room.id
                        )
                    except Exception as match_err:
                        print(f"❌ [Multiplayer Scheduler] Error simulando partida en sala {room.name}: {match_err}")

    @staticmethod
    def simulate_multiplayer_match(room_id: int):
        """Simula una partida de Lotería completa para una sala específica."""
        with Session(engine) as session:
            room = session.get(GameRoom, room_id)
            if not room:
                return
                
            registrations = session.exec(
                select(RoomRegistration).where(RoomRegistration.room_id == room.id)
            ).all()

            # --- 1. RECOPILAR JUGADORES HUMANOS ---
            participating_boards = []
            human_players = set()
            human_boards_count = 0

            # Para re-encolar a los Axolotitos después de procesar
            axo_registrations_map = {} # axo_id -> (axolotito, board_ids_list)

            # Precargar axolotitos y usuarios en batch para evitar N+1 (VULN-12)
            _all_axo_ids = [reg.axolotito_id for reg in registrations]
            _axos_by_id: dict[int, Axolotito] = {}
            if _all_axo_ids:
                _axos_loaded = session.exec(
                    select(Axolotito).where(Axolotito.id.in_(_all_axo_ids))
                ).all()
                _axos_by_id = {a.id: a for a in _axos_loaded}

            _users_by_did: dict[str, User] = {}
            _user_ids_to_load = set(a.user_id for a in _axos_by_id.values())
            if room.host_id:
                _user_ids_to_load.add(room.host_id)
            if _user_ids_to_load:
                _users_loaded = session.exec(
                    select(User).where(User.privy_did.in_(_user_ids_to_load))
                ).all()
                _users_by_did = {u.privy_did: u for u in _users_loaded}

            for reg in registrations:
                axo = _axos_by_id.get(reg.axolotito_id)
                if not axo:
                    continue
                
                b_ids = json.loads(reg.boards_json)
                axo_registrations_map[axo.id] = (axo, b_ids)
                
                # Descontar energía fija al Axolotito por participar (10 de energía)
                axo.energy_current = max(0, axo.energy_current - 10)
                
                # Pérdida extra de energía al finalizar partida basada en salinity
                extra_energy_loss = round(axo.stat_salinity * 0.2)  # 0-20 puntos según salinity
                axo.energy_current = max(0, axo.energy_current - extra_energy_loss)
                
                # Descontar Buy-in del depósito en custodia (escrow) por cada tabla registrada
                # Axolite VIP paga -15% de cuota de entrada (VULN-06: aritmética entera)
                owner = _users_by_did.get(axo.user_id)
                entry_discount_bps = VIP_CONFIG.get(getattr(owner, "vip_tier", "") or "", {}).get("multiplayer_discount_bps", 0) if (owner and owner.is_vip) else 0
                fee_int = _entry_fee_internal(room)
                effective_fee = fee_int * (10000 - entry_discount_bps) // 10000
                entry_fee_total = len(b_ids) * effective_fee
                axo.escrow_balance_gal = max(0, axo.escrow_balance_gal - entry_fee_total)
                
                for board_id in b_ids:
                    board = session.get(PlayerBoard, board_id)
                    if board:
                        participating_boards.append({
                            "board_id": board.id,
                            "axo_id": axo.id,
                            "user_id": axo.user_id,
                            "card_ids": board.card_ids,
                            "is_bot": False,
                            "marked_indices": set(),
                            "axo_focus": axo.stat_focus,
                            "axo_luck": axo.stat_luck,
                            "axo_salinity": axo.stat_salinity,
                        })
                        human_players.add(axo.user_id)
                        human_boards_count += 1
            
            # --- 2. EVALUAR ELEGIBILIDAD DEL JACKPOT (anti-sybil) ---
            # Requiere: >= 5 tablas humanas Y >= 2 wallet_address ÚNICAS.
            # Contar wallets distintas (no solo user_ids) impide que un atacante con N
            # cuentas que comparten la misma billetera controle la elegibilidad del jackpot
            # y acapare el premio. El check de registro ya bloquea la misma wallet en la
            # sala, pero este check doble garantiza la invariante incluso ante futuros
            # cambios en el flujo de registro.
            human_wallets: set[str] = set()
            for uid in human_players:
                owner_for_wallet = _users_by_did.get(uid)
                if owner_for_wallet and owner_for_wallet.wallet_address:
                    human_wallets.add(owner_for_wallet.wallet_address.lower())
            jackpot_eligible = (human_boards_count >= 5) and (len(human_wallets) >= 2)
            
            # --- 3. RELLENAR CON BOTS SI ES NECESARIO ---
            # Si el cupo mínimo total es menor a 4, autocompletamos con bots virtuales
            all_cards = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)).all()
            all_card_ids = [c.id for c in all_cards]
            card_map = {c.id: c.name for c in all_cards}
            
            bot_count_needed = max(0, 4 - len(participating_boards))
            for i in range(bot_count_needed):
                bot_cards = _rng.sample(all_card_ids, 16)
                participating_boards.append({
                    "board_id": -i - 1, # ID negativo para identificar bot
                    "axo_id": None,
                    "user_id": f"bot_{i}",
                    "card_ids": bot_cards,
                    "is_bot": True,
                    "marked_indices": set(),
                    "axo_focus": 50,
                    "axo_luck": 10
                })
                
            # --- 4. CÁLCULO Y REPARTO DE LA BOLSA (POTS) ---
            # La bolsa total se calcula en base a los buy-ins pagados por humanos
            total_collected_gal = human_boards_count * _entry_fee_internal(room)

            # Reparto de comisiones (VULN-06: aritmética entera, 5% = 5/100)
            treasury_share = total_collected_gal * 5 // 100
            jackpot_share = total_collected_gal * 5 // 100

            # Host commission: 5% del pozo va al anfitrión (si es sala hosted)
            host_share = 0
            if room.host_id and room.room_type == "player_hosted":
                host_share = total_collected_gal * 5 // 100
                host_user = _users_by_did.get(room.host_id)
                if host_user:
                    host_wallet = session.exec(select(Wallet).where(Wallet.user_id == room.host_id)).first()
                    if not host_wallet:
                        host_wallet = Wallet(user_id=room.host_id, frijolitos=0, axofichas=0, gemas_alga=0)
                        session.add(host_wallet)
                    host_wallet.frijolitos += host_share
                    session.add(host_wallet)
                    session.add(TransactionLedger(
                        user_id=room.host_id,
                        amount=host_share,
                        currency=CurrencyType.FRIJOLITO,
                        tx_type=TransactionType.REWARD,
                        description=f"Comision de anfitrion FRJ — sala '{room.name}'",
                    ))
                    # Reputación: +1 por partida, +5 extra si sala llena (>=80% capacidad)
                    config = json.loads(room.room_config or "{}")
                    max_players = config.get("max_players", 4)
                    reputation_gain = 1 + (5 if human_boards_count >= max_players * 80 // 100 else 0)
                    room.host_reputation_earned = (room.host_reputation_earned or 0) + reputation_gain

            # Acumular a Tesorería
            treasury = session.exec(select(TreasuryVault)).first()
            if not treasury:
                treasury = TreasuryVault(balance=0)
                session.add(treasury)
            treasury.balance += treasury_share
            treasury.updated_at = datetime.utcnow()

            # Acumular a Jackpot
            from app.core.config import FRJ_DECIMALS_BACKEND
            _FRJ = 10 ** FRJ_DECIMALS_BACKEND
            jackpot = session.exec(select(JackpotVault)).first()
            if not jackpot:
                jackpot = JackpotVault(current_amount=1000 * _FRJ, seed_amount=1000 * _FRJ)
                session.add(jackpot)
            jackpot.current_amount += jackpot_share
            jackpot.updated_at = datetime.utcnow()

            # Bolsas netas de juego (reducidas si hay host commission)
            # Total comisiones: 5% Tesorería + 5% Jackpot + (5% Anfitrión si aplica)
            # Suma total de distribución siempre es 100%.
            premio_1_pool = total_collected_gal * 30 // 100 if host_share > 0 else total_collected_gal * 35 // 100
            premio_2_pool = total_collected_gal * 55 // 100 if host_share > 0 else total_collected_gal * 55 // 100
            
            # --- 5. SIMULACIÓN DEL SORTEO (CARTAS CANTADAS) ---
            # Leer patrones de victoria configurados en la sala
            room_cfg = json.loads(room.room_config or "{}")
            active_win_patterns = room_cfg.get("win_patterns", ["line", "cuadrito"])

            # Ajuste dinámico y balanceado del Jackpot (Punto 1.A)
            PATTERN_SIZES = {
                "line": 4,
                "cuadrito": 4,
                "pocito": 4,
                "esquinas": 4,
                "cruz": 7,
                "l_shape": 7,
                "cruz_diagonal": 8,
                "z_shape": 10,
                "full_board": 16
            }
            min_pattern_size = min([PATTERN_SIZES.get(p, 4) for p in active_win_patterns]) if active_win_patterns else 4
            jackpot_min_turn = min_pattern_size
            # Ventana de 5 turnos equilibrada (ej. 4 a 8 para patrones de 4 celdas)
            jackpot_max_turn = min_pattern_size + 4

            # Premio 2 siempre es tabla llena (independiente de patrones de Premio 1)
            p2_patterns = ["full_board"]

            deck = all_card_ids.copy()
            _rng.shuffle(deck)

            # Crear registro de estado en vivo para el visor del frontend (modo auto)
            game_state = ActiveGameState(
                room_id=room.id,
                phase="playing",
                cards_drawn_json="[]",
                player_states_json="{}",
                turns_played=0,
                tension_level="low",
            )
            session.add(game_state)
            session.flush()

            # Entropia de sala: nivel de caos segun SAL promedio de humanos
            human_sal = [pb["axo_salinity"] for pb in participating_boards if not pb.get("is_bot")]
            sala_entropy = room_entropy(human_sal)
            if sala_entropy > 0.3:
                print(f"[Multiplayer Service] Sala entropia SAL alta: {sala_entropy:.2f}")

            turns = 0
            premio_1_winners = []
            premio_2_winners = []
            jackpot_winners = []
            premio_1_awarded = False
            drawn_cards_history = []

            for card_drawn in deck:
                turns += 1
                drawn_cards_history.append(card_drawn)
                
                # 5.1 Actualizar marcas en cada tablero
                for pb in participating_boards:
                    if card_drawn in pb["card_ids"]:
                        idx = pb["card_ids"].index(card_drawn)
                        if pb["is_bot"]:
                            pb["marked_indices"].add(idx)
                        else:
                            # Logica de Concentracion (Focus): chance de fallar marcar la carta
                            miss_chance = max(0.0, min(0.3, (100.0 - pb["axo_focus"]) * 0.003))
                            if _rng.random() < miss_chance:
                                continue  # OJO miss: la carta no se marca
                            # SAL slip: roll independiente — la carta "se escapa"
                            slip = sal_slip_chance(pb.get("axo_salinity", 0.0))
                            if _rng.random() < slip:
                                continue  # la carta se escapa por SAL
                            pb["marked_indices"].add(idx)
                                
                # 5.1b Escribir estado en vivo cada 3 turnos (ActiveGameState para polling)
                if turns % 3 == 0:
                    from app.services.game_logic import check_tension_status
                    tension = check_tension_status([
                        {"axo_id": pb.get("axo_id"), "marked_indices": list(pb.get("marked_indices", set()))}
                        for pb in participating_boards
                    ])
                    player_states_dict = {}
                    for pb in participating_boards:
                        key = str(pb["board_id"])
                        player_states_dict[key] = {
                            "marked": list(pb.get("marked_indices", set())),
                            "missed": [],  # bots no generan missed
                        }
                    game_state.cards_drawn_json = json.dumps(drawn_cards_history)
                    game_state.player_states_json = json.dumps(player_states_dict)
                    game_state.turns_played = turns
                    game_state.current_card_id = card_drawn
                    game_state.tension_level = tension.level
                    game_state.updated_at = datetime.utcnow()
                    session.add(game_state)
                    session.flush()

                # 5.2 Comprobar Premio 1 usando patrones configurados en la sala
                if not premio_1_awarded:
                    round_winners_p1 = []
                    for pb in participating_boards:
                        won, _ = check_any_pattern(pb["marked_indices"], active_win_patterns)
                        if won:
                            round_winners_p1.append(pb)
                            
                    if round_winners_p1:
                        premio_1_winners = round_winners_p1
                        premio_1_awarded = True
                        
                        # Comprobar si se cumple condición de Jackpot (rango dinámico y equilibrado)
                        if jackpot_min_turn <= turns <= jackpot_max_turn and jackpot_eligible:
                            human_winners = [w for w in round_winners_p1 if not w["is_bot"]]
                            if human_winners:
                                jackpot_winners = human_winners
                                
                # 5.3 Comprobar Premio 2 (Tabla Llena)
                round_winners_p2 = []
                for pb in participating_boards:
                    if len(pb["marked_indices"]) == 16:
                        round_winners_p2.append(pb)
                        
                if round_winners_p2:
                    premio_2_winners = round_winners_p2
                    break # Fin de la partida
                    
            # Si el deck se termina sin ganador de Tabla Llena (extremadamente raro), elegimos el de mayor puntaje
            if not premio_2_winners:
                participating_boards.sort(key=lambda x: len(x["marked_indices"]), reverse=True)
                premio_2_winners = [participating_boards[0]]
                
            # Si nadie hizo Premio 1 en todo el juego (teóricamente imposible antes de tabla llena, pero preventivo)
            if not premio_1_winners:
                premio_1_winners = premio_2_winners
                
            # Tracking para game logs de notificación (VULN-06: enteros)
            axo_prize_won = {axo_id: 0 for axo_id in axo_registrations_map}
            axo_xp_gained = {axo_id: 0 for axo_id in axo_registrations_map}
            axo_prize_breakdown = {axo_id: [] for axo_id in axo_registrations_map}

            # --- 6. ENTREGAR RECOMPENSAS E HISTORIAL ---

            # 6.1 Entrega Premio 1 — VULN-05/06: in-pool bonuses con aritmética entera
            share_p1 = premio_1_pool // len(premio_1_winners)
            _p1_raw: list = []  # (w, raw_prize, luck_b, vip_b)

            for w in premio_1_winners:
                if w["is_bot"]:
                    continue
                luck_bps = min(int(w["axo_luck"] * 100), 1000)  # cap 10% = 1000 bps
                winner_user = _users_by_did.get(w["user_id"])
                vip_bps = (
                    int(VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                    if (winner_user and winner_user.is_vip) else 0
                )
                raw = share_p1 * (10000 + luck_bps + vip_bps) // 10000
                luck_b = share_p1 * luck_bps // 10000
                vip_b = share_p1 * vip_bps // 10000
                _p1_raw.append((w, raw, luck_b, vip_b))

            # Normalizar: Σ prizes ≤ pool — ningún centavo se crea fuera del pool
            _total_raw_p1 = sum(r[1] for r in _p1_raw)
            _total_raw_p1 = max(_total_raw_p1, 1)  # evitar div/0
            _total_p1_paid = 0

            for w, raw, luck_b, vip_b in _p1_raw:
                axo_obj, _ = axo_registrations_map[w["axo_id"]]
                final_p1 = raw * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else raw
                luck_final = luck_b * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else luck_b
                vip_final = vip_b * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else vip_b
                _total_p1_paid += final_p1
                axo_obj.escrow_balance_gal += final_p1
                axo_prize_won[w["axo_id"]] += final_p1
                axo_prize_breakdown[w["axo_id"]].append({
                    "prize_type": "premio_1",
                    "label": "Primer Patrón",
                    "gross_gal": share_p1 * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else share_p1,
                    "luck_bonus": luck_final,
                    "vip_bonus": vip_final,
                })
                axo_obj.experience += 20
                axo_xp_gained[w["axo_id"]] += 20
                board_obj = session.get(PlayerBoard, w["board_id"])
                if board_obj:
                    board_obj.xp += 15
                    board_obj.games_played += 1
                    board_obj.games_won += 1

            # Shares de bots + sobrante de normalización → tesorería
            _p1_remainder = premio_1_pool - _total_p1_paid
            if _p1_remainder > 0:
                treasury.balance += _p1_remainder
                treasury.updated_at = datetime.utcnow()

            # 6.2 Entrega Premio 2 (Tabla Llena) — VULN-05/06: mismo patrón in-pool entero
            share_p2 = premio_2_pool // len(premio_2_winners)
            _p2_raw: list = []

            for w in premio_2_winners:
                if w["is_bot"]:
                    continue
                luck_bps = min(int(w["axo_luck"] * 100), 1000)
                winner_user = _users_by_did.get(w["user_id"])
                vip_bps = (
                    int(VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                    if (winner_user and winner_user.is_vip) else 0
                )
                raw = share_p2 * (10000 + luck_bps + vip_bps) // 10000
                luck_b = share_p2 * luck_bps // 10000
                vip_b = share_p2 * vip_bps // 10000
                _p2_raw.append((w, raw, luck_b, vip_b))

            _total_raw_p2 = sum(r[1] for r in _p2_raw)
            _total_raw_p2 = max(_total_raw_p2, 1)
            _total_p2_paid = 0

            for w, raw, luck_b, vip_b in _p2_raw:
                axo_obj, _ = axo_registrations_map[w["axo_id"]]
                final_p2 = raw * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else raw
                luck_final = luck_b * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else luck_b
                vip_final = vip_b * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else vip_b
                _total_p2_paid += final_p2
                axo_obj.escrow_balance_gal += final_p2
                axo_prize_won[w["axo_id"]] += final_p2
                axo_prize_breakdown[w["axo_id"]].append({
                    "prize_type": "premio_2",
                    "label": "Tabla Llena",
                    "gross_gal": share_p2 * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else share_p2,
                    "luck_bonus": luck_final,
                    "vip_bonus": vip_final,
                })
                axo_obj.experience += 50
                axo_xp_gained[w["axo_id"]] += 50
                board_obj = session.get(PlayerBoard, w["board_id"])
                if board_obj:
                    board_obj.xp += 40
                    board_obj.games_played += 1
                    board_obj.games_won += 1

            _p2_remainder = premio_2_pool - _total_p2_paid
            if _p2_remainder > 0:
                treasury.balance += _p2_remainder
                treasury.updated_at = datetime.utcnow()
                        
            # Consolación XP para los que no ganaron nada
            winner_board_ids = {w["board_id"] for w in premio_1_winners + premio_2_winners}
            for pb in participating_boards:
                if not pb["is_bot"] and pb["board_id"] not in winner_board_ids:
                    axo_obj, _ = axo_registrations_map[pb["axo_id"]]
                    axo_obj.experience += 5
                    axo_xp_gained[pb["axo_id"]] += 5
                    board_obj = session.get(PlayerBoard, pb["board_id"])
                    if board_obj:
                        board_obj.xp += 5
                        board_obj.games_played += 1
                        
            # 6.3 Entrega de Jackpot de Oro si aplica (VULN-06: aritmética entera)
            if jackpot_winners:
                total_jackpot = jackpot.current_amount
                winner_jackpot_payout = total_jackpot * 90 // 100
                share_jackpot = winner_jackpot_payout // len(jackpot_winners)

                # VULN-05/06: VIP bonus normalizado dentro del 90% del vault (no phantom funds)
                _jp_raw: list = []
                for w in jackpot_winners:
                    jackpot_winner_user = _users_by_did.get(w["user_id"])
                    vip_jp_bps = (
                        int(VIP_CONFIG.get(getattr(jackpot_winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                        if (jackpot_winner_user and jackpot_winner_user.is_vip) else 0
                    )
                    raw_jp = share_jackpot * (10000 + vip_jp_bps) // 10000
                    vip_jp_b = share_jackpot * vip_jp_bps // 10000
                    _jp_raw.append((w, raw_jp, vip_jp_b))

                _total_raw_jp = sum(r[1] for r in _jp_raw)
                _total_raw_jp = max(_total_raw_jp, 1)

                for w, raw_jp, vip_jp_b in _jp_raw:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    payout = raw_jp * winner_jackpot_payout // _total_raw_jp if _total_raw_jp > winner_jackpot_payout else raw_jp
                    vip_bonus_final = vip_jp_b * winner_jackpot_payout // _total_raw_jp if _total_raw_jp > winner_jackpot_payout else vip_jp_b
                    axo_obj.escrow_balance_gal += payout
                    axo_prize_won[w["axo_id"]] += payout
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "jackpot",
                        "label": "Jackpot Global",
                        "gross_gal": payout - vip_bonus_final,
                        "luck_bonus": 0,
                        "vip_bonus": vip_bonus_final,
                    })

                    # Registrar victoria del Jackpot
                    win_record = JackpotWin(
                        axo_id=w["axo_id"],
                        user_id=w["user_id"],
                        amount_won=payout,
                        cards_drawn_count=turns
                    )
                    session.add(win_record)

                    # Ledger record
                    ledger_jackpot = TransactionLedger(
                        user_id=w["user_id"],
                        amount=payout,
                        currency=CurrencyType.FRIJOLITO,
                        tx_type=TransactionType.REWARD,
                        description=f"🎉 GANADOR DEL JACKPOT GLOBAL FRJ! Axo: {axo_obj.name} | Sorteo #{turns}"
                    )
                    session.add(ledger_jackpot)

                # Re-sembrado (Reset)
                remaining_pool = total_jackpot * 10 // 100
                _SEED_AMOUNT = 1000 * (10 ** FRJ_DECIMALS_BACKEND)
                if remaining_pool < _SEED_AMOUNT:
                    diff_needed = _SEED_AMOUNT - remaining_pool
                    # Tomar lo que se pueda de la tesorería
                    amount_from_treasury = min(diff_needed, treasury.balance)
                    treasury.balance -= amount_from_treasury
                    jackpot.current_amount = remaining_pool + amount_from_treasury
                else:
                    jackpot.current_amount = remaining_pool

                jackpot.last_won_at = datetime.utcnow()
                jackpot.last_winner_axo_id = jackpot_winners[0]["axo_id"]
                session.add(jackpot)
                session.add(treasury)
                print(f"💰 [Multiplayer Service] ¡Jackpot de {total_jackpot} FRJ-units ganado por {len(jackpot_winners)} Axo(s)!")

            # --- 6.4 CREAR REGISTROS DE PARTIDA PARA NOTIFICACIONES ---
            p1_winner_axo_ids = {w["axo_id"] for w in premio_1_winners if not w["is_bot"]}
            p2_winner_axo_ids = {w["axo_id"] for w in premio_2_winners if not w["is_bot"]}

            for axo_id, (axo_obj, b_ids) in axo_registrations_map.items():
                entry_cost = len(b_ids) * _entry_fee_internal(room)
                prize_won = axo_prize_won.get(axo_id, 0)
                net_gal = prize_won - entry_cost
                xp_total = axo_xp_gained.get(axo_id, 0)
                is_winner = axo_id in p1_winner_axo_ids or axo_id in p2_winner_axo_ids
                outcome = "Victoria" if is_winner else "Derrota"

                # Calculate mark_accuracy
                total_marked = 0
                total_called_matching = 0
                for pb in participating_boards:
                    if pb["axo_id"] == axo_id:
                        total_marked += len(pb["marked_indices"])
                        total_called_matching += sum(1 for cid in pb["card_ids"] if cid in drawn_cards_history)

                if total_called_matching == 0:
                    mark_accuracy = 1.0
                else:
                    mark_accuracy = total_marked / total_called_matching

                # Apply imprinting if needed
                try:
                    _apply_imprinting_if_needed(
                        axo=axo_obj,
                        is_win=is_winner,
                        had_jackpot=any(w["axo_id"] == axo_id for w in jackpot_winners),
                        mark_accuracy=mark_accuracy,
                        session=session,
                    )
                except Exception as exc:
                    print(f"⚠️ [imprinting] error no-fatal in multiplayer: {exc}")

                player_breakdown = axo_prize_breakdown.get(axo_id, [])
                won_p1 = axo_id in p1_winner_axo_ids
                won_p2 = axo_id in p2_winner_axo_ids
                won_jp = any(w["axo_id"] == axo_id for w in jackpot_winners)

                game_log = MultiplayerGameLog(
                    user_id=axo_obj.user_id,
                    axolotito_id=axo_obj.id,
                    axo_name=axo_obj.name,
                    room_name=room.name,
                    outcome=outcome,
                    net_gal=net_gal,
                    xp_gained=xp_total,
                    prize_breakdown_json=json.dumps(player_breakdown) if player_breakdown else None,
                    won_premio_1=won_p1,
                    won_premio_2=won_p2,
                    won_jackpot=won_jp,
                    entry_fee_paid=entry_cost,
                    gross_prize_gal=prize_won,
                    notified=False,
                )
                session.add(game_log)

            # VULN-05/06: Log de invariante — Σ pagos de juego ≤ Σ bolsas de juego
            _game_prizes_total = _total_p1_paid + _total_p2_paid
            _player_pool = premio_1_pool + premio_2_pool
            if _game_prizes_total > _player_pool:
                print(f"⚠️ [VULN-05 INVARIANT] VIOLATED room_id={room_id}: "
                      f"player_pool={_player_pool} paid={_game_prizes_total} "
                      f"overflow={_game_prizes_total - _player_pool}")
            else:
                print(f"✅ [VULN-05] room_id={room_id} invariant OK: "
                      f"collected={total_collected_gal} "
                      f"player_pool={_player_pool} paid={_game_prizes_total}")

            # --- 7. REVOLVER LÍMITES Y AUTO-REINSCRIBIR ---
            for axo_id, (axo_obj, b_ids) in axo_registrations_map.items():
                session.refresh(axo_obj)
                # Nivelar tablas
                for board_id in b_ids:
                    board_obj = session.get(PlayerBoard, board_id)
                    if board_obj:
                        while board_obj.xp >= (board_obj.level * 100):
                            board_obj.xp -= (board_obj.level * 100)
                            board_obj.level += 1
                        session.add(board_obj)
                        
                # Nivelar Axolotito
                while axo_obj.experience >= (axo_obj.level * 100):
                    axo_obj.experience -= (axo_obj.level * 100)
                    axo_obj.level += 1
                    
                # Evaluar límites de parada
                # Pérdida acumulada: presupuesto inicial - balance actual en escrow
                loss_limit_val = axo_obj.bot_loss_limit_axg
                profit_limit_val = axo_obj.bot_profit_limit_axg

                # Límites de salida
                triggered_stop_loss = (axo_obj.escrow_balance_gal <= (axo_obj.bot_budget_axg - loss_limit_val))
                triggered_take_profit = (axo_obj.escrow_balance_gal >= (axo_obj.bot_budget_axg + profit_limit_val))
                no_energy = axo_obj.energy_current < 10
                no_funds = axo_obj.escrow_balance_gal < (len(b_ids) * _entry_fee_internal(room))
                wants_to_stop = axo_obj.wants_to_stop

                if triggered_stop_loss or triggered_take_profit or no_energy or no_funds or wants_to_stop:
                    axo_obj.status = "waiting_settlement"
                    axo_obj.wants_to_stop = False  # reset para la siguiente sesión
                    print(f"🛑 [Multiplayer Service] Axolotito {axo_obj.name} salió del juego (SL={triggered_stop_loss}, TP={triggered_take_profit}, Sin Energía={no_energy}, Sin Fondos={no_funds}, Recall={wants_to_stop}).")
                else:
                    # AUTO-REINSCRIBIR en la siguiente sala activa en espera
                    new_room = get_or_create_waiting_room(session, room.room_type, len(b_ids), user_id=axo_obj.user_id)
                    new_reg = RoomRegistration(
                        room_id=new_room.id,
                        axolotito_id=axo_obj.id,
                        boards_json=json.dumps(b_ids)
                    )
                    session.add(new_reg)
                    print(f"🔄 [Multiplayer Service] Axolotito {axo_obj.name} se re-inscribió en {new_room.name}.")
                    
                session.add(axo_obj)
                
            # Establecer sala como terminada
            room.status = "finished"
            session.add(room)

            # Marcar ActiveGameState como finished
            game_state.phase = "finished"
            game_state.cards_drawn_json = json.dumps(drawn_cards_history)
            game_state.turns_played = turns
            game_state.updated_at = datetime.utcnow()
            session.add(game_state)
            
            # Borrar los registros de inscripción de la sala terminada
            for reg in registrations:
                session.delete(reg)
                
            session.commit()
            print(f"✅ [Multiplayer Service] Simulación de la sala {room.name} terminada en {turns} cartas.")

    @staticmethod
    def resolve_multiplayer_match(
        room_id: int,
        winner_axo_id: Optional[int],
        turns: int,
        player_marked_data: dict[int, list[int]],
        drawn_cards_history: list[int]
    ) -> None:
        """
        Finaliza una partida multijugador jugada manualmente (vía WebSocket).
        Calcula las recompensas reales usando las marcas reales, cobra entradas,
        actualiza la base de datos y marca la sala como finalizada.
        """
        import json
        from sqlmodel import Session, select
        from app.database import engine
        from app.models.lobby_models import (
            GameRoom, RoomRegistration, TreasuryVault, JackpotVault, 
            JackpotWin, MultiplayerGameLog, ActiveGameState
        )
        from app.models.axolotito import Axolotito
        from app.models.user import User
        from app.models.board import PlayerBoard, Wallet, TransactionLedger
        from app.models.items import ItemCatalog, ItemType
        from app.core.config import VIP_CONFIG, FRJ_DECIMALS_BACKEND, CurrencyType, TransactionType
        from app.services.bank import BankService
        from app.services.incubation_service import _apply_imprinting_if_needed
        import random

        _rng = random.SystemRandom()

        with Session(engine) as session:
            room = session.get(GameRoom, room_id)
            if not room or room.status == "finished":
                return

            registrations = session.exec(
                select(RoomRegistration).where(RoomRegistration.room_id == room.id)
            ).all()

            # --- 1. RECOPILAR JUGADORES HUMANOS ---
            participating_boards = []
            human_players = set()
            human_boards_count = 0
            axo_registrations_map = {}

            _all_axo_ids = [reg.axolotito_id for reg in registrations]
            _axos_by_id = {}
            if _all_axo_ids:
                _axos_loaded = session.exec(
                    select(Axolotito).where(Axolotito.id.in_(_all_axo_ids))
                ).all()
                _axos_by_id = {a.id: a for a in _axos_loaded}

            _user_ids_to_load = set(a.user_id for a in _axos_by_id.values())
            if room.host_id:
                _user_ids_to_load.add(room.host_id)
            _users_by_did = {}
            if _user_ids_to_load:
                _users_loaded = session.exec(
                    select(User).where(User.privy_did.in_(_user_ids_to_load))
                ).all()
                _users_by_did = {u.privy_did: u for u in _users_loaded}

            for reg in registrations:
                axo = _axos_by_id.get(reg.axolotito_id)
                if not axo:
                    continue
                
                b_ids = json.loads(reg.boards_json)
                axo_registrations_map[axo.id] = (axo, b_ids)
                
                # Descontar energía fija al Axolotito por participar (10 de energía)
                axo.energy_current = max(0, axo.energy_current - 10)
                
                # Pérdida extra de energía al finalizar partida basada en salinity
                extra_energy_loss = round(axo.stat_salinity * 0.2)
                axo.energy_current = max(0, axo.energy_current - extra_energy_loss)
                
                # Descontar Buy-in del depósito en custodia (escrow)
                owner = _users_by_did.get(axo.user_id)
                entry_discount_bps = VIP_CONFIG.get(getattr(owner, "vip_tier", "") or "", {}).get("multiplayer_discount_bps", 0) if (owner and owner.is_vip) else 0
                fee_int = _entry_fee_internal(room)
                effective_fee = fee_int * (10000 - entry_discount_bps) // 10000
                entry_fee_total = len(b_ids) * effective_fee
                axo.escrow_balance_gal = max(0, axo.escrow_balance_gal - entry_fee_total)
                
                for board_id in b_ids:
                    board = session.get(PlayerBoard, board_id)
                    if board:
                        marked = player_marked_data.get(axo.id, [])
                        participating_boards.append({
                            "board_id": board.id,
                            "axo_id": axo.id,
                            "user_id": axo.user_id,
                            "card_ids": board.card_ids,
                            "is_bot": False,
                            "marked_indices": set(marked),
                            "axo_focus": axo.stat_focus,
                            "axo_luck": axo.stat_luck,
                            "axo_salinity": axo.stat_salinity,
                        })
                        human_players.add(axo.user_id)
                        human_boards_count += 1

            # --- 2. EVALUAR ELEGIBILIDAD DEL JACKPOT ---
            human_wallets = set()
            for uid in human_players:
                owner_for_wallet = _users_by_did.get(uid)
                if owner_for_wallet and owner_for_wallet.wallet_address:
                    human_wallets.add(owner_for_wallet.wallet_address.lower())
            jackpot_eligible = (human_boards_count >= 5) and (len(human_wallets) >= 2)

            # --- 3. RELLENAR CON BOTS SI ES NECESARIO ---
            all_cards = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)).all()
            all_card_ids = [c.id for c in all_cards]
            
            bot_count_needed = max(0, 4 - len(participating_boards))
            for i in range(bot_count_needed):
                bot_cards = _rng.sample(all_card_ids, 16)
                participating_boards.append({
                    "board_id": -i - 1,
                    "axo_id": None,
                    "user_id": f"bot_{i}",
                    "card_ids": bot_cards,
                    "is_bot": True,
                    "marked_indices": set(),
                    "axo_focus": 50,
                    "axo_luck": 10
                })

            # --- 4. CÁLCULO Y REPARTO DE LA BOLSA ---
            total_collected_gal = human_boards_count * _entry_fee_internal(room)
            treasury_share = total_collected_gal * 5 // 100
            jackpot_share = total_collected_gal * 5 // 100

            host_share = 0
            if room.host_id and room.room_type == "player_hosted":
                host_share = total_collected_gal * 5 // 100
                host_user = _users_by_did.get(room.host_id)
                if host_user:
                    host_wallet = session.exec(select(Wallet).where(Wallet.user_id == room.host_id)).first()
                    if not host_wallet:
                        host_wallet = Wallet(user_id=room.host_id, frijolitos=0, axofichas=0, gemas_alga=0)
                        session.add(host_wallet)
                    host_wallet.frijolitos += host_share
                    session.add(host_wallet)
                    session.add(TransactionLedger(
                        user_id=room.host_id,
                        amount=host_share,
                        currency=CurrencyType.FRIJOLITO,
                        tx_type=TransactionType.REWARD,
                        description=f"Comision de anfitrion FRJ — sala '{room.name}'",
                    ))
                    config = json.loads(room.room_config or "{}")
                    max_players = config.get("max_players", 4)
                    reputation_gain = 1 + (5 if human_boards_count >= max_players * 80 // 100 else 0)
                    room.host_reputation_earned = (room.host_reputation_earned or 0) + reputation_gain

            # Acumular a Tesorería
            treasury = session.exec(select(TreasuryVault)).first()
            if not treasury:
                treasury = TreasuryVault(balance=0)
                session.add(treasury)
            treasury.balance += treasury_share
            treasury.updated_at = datetime.utcnow()

            # Acumular a Jackpot
            _FRJ = 10 ** FRJ_DECIMALS_BACKEND
            jackpot = session.exec(select(JackpotVault)).first()
            if not jackpot:
                jackpot = JackpotVault(current_amount=1000 * _FRJ, seed_amount=1000 * _FRJ)
                session.add(jackpot)
            jackpot.current_amount += jackpot_share
            jackpot.updated_at = datetime.utcnow()

            # Bolsas netas de juego
            premio_1_pool = total_collected_gal * 30 // 100 if host_share > 0 else total_collected_gal * 35 // 100
            premio_2_pool = total_collected_gal * 55 // 100 if host_share > 0 else total_collected_gal * 55 // 100

            # --- 5. DETERMINAR GANADORES ---
            premio_1_winners = []
            premio_2_winners = []
            jackpot_winners = []

            if winner_axo_id is not None:
                # El ganador real
                winner_board = next((pb for pb in participating_boards if pb["axo_id"] == winner_axo_id), None)
                if winner_board:
                    premio_1_winners = [winner_board]
                    premio_2_winners = [winner_board]
                    if jackpot_eligible:
                        jackpot_winners = [winner_board]
            else:
                # Si no hay ganador explícito, determinar por marcas (fallback)
                participating_boards.sort(key=lambda x: len(x["marked_indices"]), reverse=True)
                if participating_boards:
                    premio_2_winners = [participating_boards[0]]
                    premio_1_winners = [participating_boards[0]]

            # --- 6. ENTREGAR RECOMPENSAS E HISTORIAL ---
            axo_prize_won = {axo_id: 0 for axo_id in axo_registrations_map}
            axo_xp_gained = {axo_id: 0 for axo_id in axo_registrations_map}
            axo_prize_breakdown = {axo_id: [] for axo_id in axo_registrations_map}

            # 6.1 Entrega Premio 1
            if premio_1_winners:
                share_p1 = premio_1_pool // len(premio_1_winners)
                _p1_raw = []
                for w in premio_1_winners:
                    if w["is_bot"]:
                        continue
                    luck_bps = min(int(w["axo_luck"] * 100), 1000)
                    winner_user = _users_by_did.get(w["user_id"])
                    vip_bps = (
                        int(VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                        if (winner_user and winner_user.is_vip) else 0
                    )
                    raw = share_p1 * (10000 + luck_bps + vip_bps) // 10000
                    luck_b = share_p1 * luck_bps // 10000
                    vip_b = share_p1 * vip_bps // 10000
                    _p1_raw.append((w, raw, luck_b, vip_b))

                _total_raw_p1 = sum(r[1] for r in _p1_raw)
                _total_raw_p1 = max(_total_raw_p1, 1)
                _total_p1_paid = 0

                for w, raw, luck_b, vip_b in _p1_raw:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    final_p1 = raw * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else raw
                    luck_final = luck_b * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else luck_b
                    vip_final = vip_b * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else vip_b
                    _total_p1_paid += final_p1
                    axo_obj.escrow_balance_gal += final_p1
                    axo_prize_won[w["axo_id"]] += final_p1
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "premio_1",
                        "label": "Primer Patrón",
                        "gross_gal": share_p1 * premio_1_pool // _total_raw_p1 if _total_raw_p1 > premio_1_pool else share_p1,
                        "luck_bonus": luck_final,
                        "vip_bonus": vip_final,
                    })
                    axo_obj.experience += 20
                    axo_xp_gained[w["axo_id"]] += 20
                    board_obj = session.get(PlayerBoard, w["board_id"])
                    if board_obj:
                        board_obj.xp += 15
                        board_obj.games_played += 1
                        board_obj.games_won += 1

            # 6.2 Entrega Premio 2
            if premio_2_winners:
                share_p2 = premio_2_pool // len(premio_2_winners)
                _p2_raw = []
                for w in premio_2_winners:
                    if w["is_bot"]:
                        continue
                    luck_bps = min(int(w["axo_luck"] * 100), 1000)
                    winner_user = _users_by_did.get(w["user_id"])
                    vip_bps = (
                        int(VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                        if (winner_user and winner_user.is_vip) else 0
                    )
                    raw = share_p2 * (10000 + luck_bps + vip_bps) // 10000
                    luck_b = share_p2 * luck_bps // 10000
                    vip_b = share_p2 * vip_bps // 10000
                    _p2_raw.append((w, raw, luck_b, vip_b))

                _total_raw_p2 = sum(r[1] for r in _p2_raw)
                _total_raw_p2 = max(_total_raw_p2, 1)
                _total_p2_paid = 0

                for w, raw, luck_b, vip_b in _p2_raw:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    final_p2 = raw * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else raw
                    luck_final = luck_b * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else luck_b
                    vip_final = vip_b * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else vip_b
                    _total_p2_paid += final_p2
                    axo_obj.escrow_balance_gal += final_p2
                    axo_prize_won[w["axo_id"]] += final_p2
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "premio_2",
                        "label": "Tabla Llena",
                        "gross_gal": share_p2 * premio_2_pool // _total_raw_p2 if _total_raw_p2 > premio_2_pool else share_p2,
                        "luck_bonus": luck_final,
                        "vip_bonus": vip_final,
                    })
                    axo_obj.experience += 30
                    axo_xp_gained[w["axo_id"]] += 30
                    board_obj = session.get(PlayerBoard, w["board_id"])
                    if board_obj:
                        board_obj.xp += 20
                        board_obj.games_played += 1
                        board_obj.games_won += 1

            # Consolar a los que no ganaron
            for pb in participating_boards:
                if not pb["is_bot"] and pb["board_id"] not in [w["board_id"] for w in premio_1_winners + premio_2_winners]:
                    axo_obj, _ = axo_registrations_map[pb["axo_id"]]
                    axo_obj.experience += 5
                    axo_xp_gained[pb["axo_id"]] += 5
                    board_obj = session.get(PlayerBoard, pb["board_id"])
                    if board_obj:
                        board_obj.xp += 5
                        board_obj.games_played += 1

            # 6.3 Entrega de Jackpot
            if jackpot_winners:
                total_jackpot = jackpot.current_amount
                winner_jackpot_payout = total_jackpot * 90 // 100
                share_jackpot = winner_jackpot_payout // len(jackpot_winners)
                _jp_raw = []
                for w in jackpot_winners:
                    jackpot_winner_user = _users_by_did.get(w["user_id"])
                    vip_jp_bps = (
                        int(VIP_CONFIG.get(getattr(jackpot_winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) * 10000)
                        if (jackpot_winner_user and jackpot_winner_user.is_vip) else 0
                    )
                    raw_jp = share_jackpot * (10000 + vip_jp_bps) // 10000
                    vip_jp_b = share_jackpot * vip_jp_bps // 10000
                    _jp_raw.append((w, raw_jp, vip_jp_b))

                _total_raw_jp = sum(r[1] for r in _jp_raw)
                _total_raw_jp = max(_total_raw_jp, 1)

                for w, raw_jp, vip_jp_b in _jp_raw:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    payout = raw_jp * winner_jackpot_payout // _total_raw_jp if _total_raw_jp > winner_jackpot_payout else raw_jp
                    vip_bonus_final = vip_jp_b * winner_jackpot_payout // _total_raw_jp if _total_raw_jp > winner_jackpot_payout else vip_jp_b
                    axo_obj.escrow_balance_gal += payout
                    axo_prize_won[w["axo_id"]] += payout
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "jackpot",
                        "label": "Jackpot Global",
                        "gross_gal": payout - vip_bonus_final,
                        "luck_bonus": 0,
                        "vip_bonus": vip_bonus_final,
                    })

                    win_record = JackpotWin(
                        axo_id=w["axo_id"],
                        user_id=w["user_id"],
                        amount_won=payout,
                        cards_drawn_count=turns
                    )
                    session.add(win_record)

                    ledger_jackpot = TransactionLedger(
                        user_id=w["user_id"],
                        amount=payout,
                        currency=CurrencyType.FRIJOLITO,
                        tx_type=TransactionType.REWARD,
                        description=f"🎉 GANADOR DEL JACKPOT GLOBAL FRJ! Axo: {axo_obj.name} | Sorteo #{turns}"
                    )
                    session.add(ledger_jackpot)

                remaining_pool = total_jackpot * 10 // 100
                _SEED_AMOUNT = 1000 * (10 ** FRJ_DECIMALS_BACKEND)
                if remaining_pool < _SEED_AMOUNT:
                    diff_needed = _SEED_AMOUNT - remaining_pool
                    amount_from_treasury = min(diff_needed, treasury.balance)
                    treasury.balance -= amount_from_treasury
                    jackpot.current_amount = remaining_pool + amount_from_treasury
                else:
                    jackpot.current_amount = remaining_pool

                jackpot.last_won_at = datetime.utcnow()
                jackpot.last_winner_axo_id = jackpot_winners[0]["axo_id"]
                session.add(jackpot)
                session.add(treasury)

            # 6.4 CREAR REGISTROS DE PARTIDA PARA NOTIFICACIONES ---
            p1_winner_axo_ids = {w["axo_id"] for w in premio_1_winners if not w["is_bot"]}
            p2_winner_axo_ids = {w["axo_id"] for w in premio_2_winners if not w["is_bot"]}

            for axo_id, (axo_obj, b_ids) in axo_registrations_map.items():
                entry_cost = len(b_ids) * _entry_fee_internal(room)
                prize_won = axo_prize_won.get(axo_id, 0)

                # --- AFK / Disconnect penalty (-30% reward penalty if they went auto/AFK) ---
                reg_obj = next((r for r in registrations if r.axolotito_id == axo_id), None)
                was_afk = reg_obj is not None and reg_obj.play_mode == "auto"
                
                # Apply AFK penalty if they were auto
                if was_afk:
                    prize_won = prize_won * 70 // 100
                    axo_obj.loyalty_points = max(0, axo_obj.loyalty_points - 5)
                    reward_reduction = axo_prize_won.get(axo_id, 0) - prize_won
                    if reward_reduction > 0:
                        axo_obj.escrow_balance_gal = max(0, axo_obj.escrow_balance_gal - reward_reduction)
                
                net_gal = prize_won - entry_cost
                xp_total = axo_xp_gained.get(axo_id, 0)
                is_winner = axo_id in p1_winner_axo_ids or axo_id in p2_winner_axo_ids
                outcome = "Victoria" if is_winner else "Derrota"

                if was_afk:
                    outcome += " (AFK Penalty)"

                total_marked = 0
                total_called_matching = 0
                for pb in participating_boards:
                    if pb["axo_id"] == axo_id:
                        total_marked += len(pb["marked_indices"])
                        total_called_matching += sum(1 for cid in pb["card_ids"] if cid in drawn_cards_history)

                if total_called_matching == 0:
                    mark_accuracy = 1.0
                else:
                    mark_accuracy = total_marked / total_called_matching

                try:
                    _apply_imprinting_if_needed(
                        axo=axo_obj,
                        is_win=is_winner,
                        had_jackpot=any(w["axo_id"] == axo_id for w in jackpot_winners),
                        mark_accuracy=mark_accuracy,
                        session=session,
                    )
                except Exception as exc:
                    print(f"⚠️ [imprinting] error no-fatal: {exc}")

                player_breakdown = axo_prize_breakdown.get(axo_id, [])
                won_p1 = axo_id in p1_winner_axo_ids
                won_p2 = axo_id in p2_winner_axo_ids
                won_jp = any(w["axo_id"] == axo_id for w in jackpot_winners)

                game_log = MultiplayerGameLog(
                    user_id=axo_obj.user_id,
                    axolotito_id=axo_obj.id,
                    axo_name=axo_obj.name,
                    room_name=room.name,
                    outcome=outcome,
                    net_gal=net_gal,
                    xp_gained=xp_total,
                    prize_breakdown_json=json.dumps(player_breakdown) if player_breakdown else None,
                    won_premio_1=won_p1,
                    won_premio_2=won_p2,
                    won_jackpot=won_jp,
                    entry_fee_paid=entry_cost,
                    gross_prize_gal=prize_won,
                    notified=False,
                )
                session.add(game_log)

            # --- 7. ACTUALIZAR ESTADOS Y LIMPIAR ---
            for axo_id, (axo_obj, b_ids) in axo_registrations_map.items():
                session.refresh(axo_obj)
                for board_id in b_ids:
                    board_obj = session.get(PlayerBoard, board_id)
                    if board_obj:
                        while board_obj.xp >= (board_obj.level * 100):
                            board_obj.xp -= (board_obj.level * 100)
                            board_obj.level += 1
                        session.add(board_obj)
                        
                while axo_obj.experience >= (axo_obj.level * 100):
                    axo_obj.experience -= (axo_obj.level * 100)
                    axo_obj.level += 1
                    
                axo_obj.status = "waiting_settlement"
                axo_obj.wants_to_stop = False
                session.add(axo_obj)

            room.status = "finished"
            session.add(room)

            # Marcar ActiveGameState como finished
            game_state = session.exec(select(ActiveGameState).where(ActiveGameState.room_id == room.id)).first()
            if not game_state:
                game_state = ActiveGameState(
                    room_id=room.id,
                    phase="finished",
                    cards_drawn_json=json.dumps(drawn_cards_history),
                    turns_played=turns,
                )
            else:
                game_state.phase = "finished"
                game_state.cards_drawn_json = json.dumps(drawn_cards_history)
                game_state.turns_played = turns
                game_state.updated_at = datetime.utcnow()
            session.add(game_state)
            
            for reg in registrations:
                session.delete(reg)
                
            session.commit()
            print(f"✅ [Multiplayer Service] Partida manual de la sala {room.name} resuelta exitosamente.")
