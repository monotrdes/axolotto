from __future__ import annotations
import asyncio
import json
import random
from datetime import datetime

# Generador criptográficamente seguro para el sorteo — impide predecir el orden de cartas.
# random.SystemRandom usa /dev/urandom, a diferencia del Mersenne Twister del módulo random.
_rng = random.SystemRandom()
from sqlmodel import Session, select

from app.core.config import VIP_CONFIG, settings
from app.core.prices import MULTIPLAYER_ROOMS
from app.services.sal_service import sal_slip_chance, room_entropy
from app.database import engine
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import CurrencyType, TransactionType, TransactionLedger
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
        if user_id:
            for reg in regs:
                reg_axo = session.get(Axolotito, reg.axolotito_id)
                if reg_axo:
                    if reg_axo.user_id == user_id:
                        already_registered = True
                        break
                    if wallet_address:
                        reg_owner = session.exec(select(User).where(User.privy_did == reg_axo.user_id)).first()
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
    fee_val = fee.get("fee", 10.0) if isinstance(fee, dict) else 10.0

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
        """Busca salas en estado 'waiting' y evalúa si deben comenzar por tiempo o capacidad."""
        with Session(engine) as session:
            rooms = session.exec(select(GameRoom).where(GameRoom.status == "waiting")).all()
            for room in rooms:
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
                should_start = should_start_room(total_tables, elapsed_seconds)
                
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
            
            for reg in registrations:
                axo = session.get(Axolotito, reg.axolotito_id)
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
                # Axolite VIP paga -15% de cuota de entrada
                owner = session.exec(select(User).where(User.privy_did == axo.user_id)).first()
                entry_discount = VIP_CONFIG.get(getattr(owner, "vip_tier", "") or "", {}).get("multiplayer_discount", 0.0) if (owner and owner.is_vip) else 0.0
                effective_fee = round(room.entry_fee_gal * (1 - entry_discount), 2)
                entry_fee_total = len(b_ids) * effective_fee
                axo.escrow_balance_gal = max(0.0, axo.escrow_balance_gal - entry_fee_total)
                
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
                owner_for_wallet = session.exec(select(User).where(User.privy_did == uid)).first()
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
                    "axo_focus": 50.0,
                    "axo_luck": 10.0
                })
                
            # --- 4. CÁLCULO Y REPARTO DE LA BOLSA (POTS) ---
            # La bolsa total se calcula en base a los buy-ins pagados por humanos
            total_collected_gal = human_boards_count * room.entry_fee_gal
            
            # Reparto de comisiones
            treasury_share = total_collected_gal * 0.05
            jackpot_share = total_collected_gal * 0.05

            # Host commission: 5% del pozo va al anfitrión (si es sala hosted)
            host_share = 0.0
            if room.host_id and room.room_type == "player_hosted":
                host_share = total_collected_gal * 0.05
                host_user = session.exec(select(User).where(User.privy_did == room.host_id)).first()
                if host_user:
                    host_wallet = session.exec(select(Wallet).where(Wallet.user_id == room.host_id)).first()
                    if not host_wallet:
                        host_wallet = Wallet(user_id=room.host_id, frijolitos=0.0, axofichas=0.0, gemas_alga=0.0)
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
                    reputation_gain = 1 + (5 if human_boards_count >= max_players * 0.8 else 0)
                    room.host_reputation_earned = (room.host_reputation_earned or 0) + reputation_gain

            # Acumular a Tesorería
            treasury = session.exec(select(TreasuryVault)).first()
            if not treasury:
                treasury = TreasuryVault(balance=0.0)
                session.add(treasury)
            treasury.balance += treasury_share
            treasury.updated_at = datetime.utcnow()

            # Acumular a Jackpot
            jackpot = session.exec(select(JackpotVault)).first()
            if not jackpot:
                jackpot = JackpotVault(current_amount=1000.0, seed_amount=1000.0)
                session.add(jackpot)
            jackpot.current_amount += jackpot_share
            jackpot.updated_at = datetime.utcnow()

            # Bolsas netas de juego (reducidas si hay host commission)
            # Total comisiones: 5% Tesorería + 5% Jackpot + (5% Anfitrión si aplica)
            # Suma total de distribución siempre es 100%.
            premio_1_pool = total_collected_gal * 0.30 if host_share > 0 else total_collected_gal * 0.35
            premio_2_pool = total_collected_gal * 0.55 if host_share > 0 else total_collected_gal * 0.55
            
            # --- 5. SIMULACIÓN DEL SORTEO (CARTAS CANTADAS) ---
            # Leer patrones de victoria configurados en la sala
            room_cfg = json.loads(room.room_config or "{}")
            active_win_patterns = room_cfg.get("win_patterns", ["line", "cuadrito"])
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
                        
                        # Comprobar si se cumple condición de Jackpot (turnos 4, 5 o 6 y jugadores reales)
                        if 4 <= turns <= 6 and jackpot_eligible:
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
                
            # Tracking para game logs de notificación
            axo_prize_won = {axo_id: 0.0 for axo_id in axo_registrations_map}
            axo_xp_gained = {axo_id: 0 for axo_id in axo_registrations_map}
            axo_prize_breakdown = {axo_id: [] for axo_id in axo_registrations_map}

            # --- 6. ENTREGAR RECOMPENSAS E HISTORIAL ---
            
            # 6.1 Entrega Premio 1 (Línea o Cuadrito)
            share_p1 = premio_1_pool / len(premio_1_winners)
            for w in premio_1_winners:
                if not w["is_bot"]:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    luck_bonus = (w["axo_luck"] / 1000.0) * share_p1
                    # +5% jackpot bonus para Axolite VIP
                    winner_user = session.exec(select(User).where(User.privy_did == w["user_id"])).first()
                    vip_bonus = share_p1 * VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) if (winner_user and winner_user.is_vip) else 0.0
                    axo_obj.escrow_balance_gal += (share_p1 + luck_bonus + vip_bonus)
                    axo_prize_won[w["axo_id"]] += (share_p1 + luck_bonus + vip_bonus)
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "premio_1",
                        "label": "Primer Patrón",
                        "gross_gal": round(share_p1, 2),
                        "luck_bonus": round(luck_bonus, 2),
                        "vip_bonus": round(vip_bonus, 2),
                    })

                    # Sumar XP al Axolotito y Tabla
                    axo_obj.experience += 20
                    axo_xp_gained[w["axo_id"]] += 20
                    board_obj = session.get(PlayerBoard, w["board_id"])
                    if board_obj:
                        board_obj.xp += 15
                        board_obj.games_played += 1
                        board_obj.games_won += 1
                        
            # 6.2 Entrega Premio 2 (Tabla Llena)
            share_p2 = premio_2_pool / len(premio_2_winners)
            for w in premio_2_winners:
                if not w["is_bot"]:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    luck_bonus = (w["axo_luck"] / 1000.0) * share_p2
                    winner_user = session.exec(select(User).where(User.privy_did == w["user_id"])).first()
                    vip_bonus = share_p2 * VIP_CONFIG.get(getattr(winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) if (winner_user and winner_user.is_vip) else 0.0
                    axo_obj.escrow_balance_gal += (share_p2 + luck_bonus + vip_bonus)
                    axo_prize_won[w["axo_id"]] += (share_p2 + luck_bonus + vip_bonus)
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "premio_2",
                        "label": "Tabla Llena",
                        "gross_gal": round(share_p2, 2),
                        "luck_bonus": round(luck_bonus, 2),
                        "vip_bonus": round(vip_bonus, 2),
                    })

                    axo_obj.experience += 50
                    axo_xp_gained[w["axo_id"]] += 50
                    board_obj = session.get(PlayerBoard, w["board_id"])
                    if board_obj:
                        board_obj.xp += 40
                        board_obj.games_played += 1
                        board_obj.games_won += 1
                        
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
                        
            # 6.3 Entrega de Jackpot de Oro si aplica
            if jackpot_winners:
                total_jackpot = jackpot.current_amount
                winner_jackpot_payout = total_jackpot * 0.90
                share_jackpot = winner_jackpot_payout / len(jackpot_winners)
                
                for w in jackpot_winners:
                    axo_obj, _ = axo_registrations_map[w["axo_id"]]
                    jackpot_winner_user = session.exec(select(User).where(User.privy_did == w["user_id"])).first()
                    vip_jackpot_bonus = share_jackpot * VIP_CONFIG.get(getattr(jackpot_winner_user, "vip_tier", "") or "", {}).get("jackpot_bonus", 0.0) if (jackpot_winner_user and jackpot_winner_user.is_vip) else 0.0
                    payout = share_jackpot + vip_jackpot_bonus
                    axo_obj.escrow_balance_gal += payout
                    axo_prize_won[w["axo_id"]] += payout
                    axo_prize_breakdown[w["axo_id"]].append({
                        "prize_type": "jackpot",
                        "label": "Jackpot Global",
                        "gross_gal": round(share_jackpot, 2),
                        "luck_bonus": 0.0,
                        "vip_bonus": round(vip_jackpot_bonus, 2),
                    })

                    # Registrar victoria del Jackpot
                    win_record = JackpotWin(
                        axo_id=w["axo_id"],
                        user_id=w["user_id"],
                        amount_won=share_jackpot,
                        cards_drawn_count=turns
                    )
                    session.add(win_record)
                    
                    # Ledger record
                    ledger_jackpot = TransactionLedger(
                        user_id=w["user_id"],
                        amount=share_jackpot,
                        currency=CurrencyType.FRIJOLITO,
                        tx_type=TransactionType.REWARD,
                        description=f"🎉 GANADOR DEL JACKPOT GLOBAL FRJ! Axo: {axo_obj.name} | Sorteo #{turns}"
                    )
                    session.add(ledger_jackpot)
                    
                # Re-sembrado (Reset)
                remaining_pool = total_jackpot * 0.10
                if remaining_pool < 1000.0:
                    diff_needed = 1000.0 - remaining_pool
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
                print(f"💰 [Multiplayer Service] ¡Jackpot de {total_jackpot} GAL ganado por {len(jackpot_winners)} Axo(s)!")

            # --- 6.4 CREAR REGISTROS DE PARTIDA PARA NOTIFICACIONES ---
            p1_winner_axo_ids = {w["axo_id"] for w in premio_1_winners if not w["is_bot"]}
            p2_winner_axo_ids = {w["axo_id"] for w in premio_2_winners if not w["is_bot"]}

            for axo_id, (axo_obj, b_ids) in axo_registrations_map.items():
                entry_cost = len(b_ids) * room.entry_fee_gal
                prize_won = axo_prize_won.get(axo_id, 0.0)
                net_gal = round(prize_won - entry_cost, 2)
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
                    entry_fee_paid=round(entry_cost, 2),
                    gross_prize_gal=round(prize_won, 2),
                    notified=False,
                )
                session.add(game_log)

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
                no_funds = axo_obj.escrow_balance_gal < (len(b_ids) * room.entry_fee_gal)
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
