"""
game_service.py — CPU-mode game logic and Axolotito lifecycle management.

Contains:
  - play_match: Full Lotería simulation (player vs NPC bots)
  - feed_axolotito / sleep_axolotito / wake_axolotito: Energy management
"""
from datetime import datetime, timedelta
import json
import logging
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings, FRJ_DECIMALS_BACKEND, frj_to_internal, frj_to_display
from app.core.prices import CONSUMABLE_PRICES
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger, ChainOutbox
from app.models.items import ItemCatalog, ItemType
from app.models.user import User
from app.services.bank_service import BankService
from app.services.incubation_service import _apply_imprinting_if_needed
from app.services.npc_service import _ensure_npc_pool, _spawn_npc_replacement

logger = logging.getLogger("game_service")
from app.services.game_logic import (
    _rng,
    _lucky_save,
    _miss_chance,
    check_loterica_line,
    get_winning_line,
    ROOM_CONFIG,
    MAX_WIN_MULTIPLIER_BPS,
    WINNING_LINES,
)
from app.services.sal_service import apply_sal_bias
from app.services.pila_service import recovery_multiplier
from app.services.web3_service import Web3Service


def _enqueue_chain_op(session: Session, user_id: str, operation: str, payload: dict):
    """Escribe una intención on-chain en la tabla ChainOutbox dentro de la misma
    transacción DB. El worker chain_outbox la procesará con reintentos.

    Reemplaza el patrón roto:  wallet.frijolitos -= X; session.commit();
                               try: Web3Service.burn_frj(...)
                               except: print(...)  # error tragado
    """
    entry = ChainOutbox(
        user_id=user_id,
        operation=operation,
        payload_json=json.dumps(payload),
        status="pending",
    )
    session.add(entry)
    return entry


def _flush_outbox(session: Session, max_batch: int = 10):
    """Procesa la outbox de forma síncrona (best-effort) después del commit DB.
    Si falla, las entradas quedan 'pending' y el worker las reintentará."""
    try:
        from app.services.chain_outbox_worker import process_outbox_sync
        process_outbox_sync(session, max_batch=max_batch)
    except Exception:
        pass  # El worker asíncrono se encargará


class GameService:

    @staticmethod
    def play_match(
        axolotito_id: int,
        room_name: str,
        multiplier: int,
        bot_enabled: bool,
        bot_budget_gal: float,
        bot_loss_limit_pct: float,
        bot_profit_limit_pct: float,
        session: Session,
        verified_user_id: str,
    ) -> dict:
        """Simulates a Lotería match, consuming Axolotito energy and charging entry fee."""
        # 1. Fetch Axolotito and validate ownership
        axo = session.get(Axolotito, axolotito_id)
        if not axo:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axo.user_id != verified_user_id:
            raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")

        # 1b. Verificar tutorial completado
        from app.core.auth import require_tutorial
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user: require_tutorial(user)

        # 2. Check Axolotito status and energy
        if axo.status == "sleeping" and axo.sleep_expires_at and axo.sleep_expires_at > datetime.utcnow():
            raise HTTPException(status_code=400, detail="Este Axolotito está durmiendo. Despiértalo primero.")
        if axo.energy_current < 10:
            raise HTTPException(status_code=400, detail="Energía insuficiente. Tu Axolotito necesita comer o dormir (mínimo 10 energía).")

        # 3. Check assigned board
        if not axo.assigned_board_id:
            raise HTTPException(status_code=400, detail="Este Axolotito no tiene ninguna tabla asignada para jugar.")

        board = session.get(PlayerBoard, axo.assigned_board_id)
        if not board or board.is_dead:
            raise HTTPException(status_code=400, detail="La tabla asignada no existe o está desarmada.")

        # 4. Set Room details from centralised ROOM_CONFIG and apply multiplier
        if room_name not in ROOM_CONFIG:
            raise HTTPException(status_code=400, detail="Sala de juego no válida.")
        if multiplier not in (1, 2, 5, 10):
            raise HTTPException(status_code=400, detail="Multiplicador no soportado. Valores válidos: 1, 2, 5, 10.")

        room = ROOM_CONFIG[room_name]
        # VULN-06: ROOM_CONFIG almacena montos en FRJ human-readable.
        # Convertir a unidad mínima entera para operar contra wallet (que usa internal).
        entry_fee        = frj_to_internal(room["fee"] * multiplier)
        win_prize        = frj_to_internal(room["prize"] * multiplier)
        loss_consolation = frj_to_internal(room["consolation"] * multiplier)
        difficulty_label = room["difficulty_label"]
        
        # Sub-linear XP scaling (using square root) to prevent excessive level-ups at high stakes
        import math
        xp_multiplier = math.sqrt(multiplier)
        win_xp_board    = int(room["win_xp_board"] * xp_multiplier)
        win_xp_axo      = int(room["win_xp_axo"] * xp_multiplier)
        loss_xp_board   = int(room["loss_xp_board"] * xp_multiplier)
        loss_xp_axo     = int(room["loss_xp_axo"] * xp_multiplier)
        room_title      = room["title"]
        bot_count       = room["bot_count"]
        bot_focus       = room["bot_focus"]

        # 5. Check user wallet balance
        wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
        if wallet.frijolitos < entry_fee:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Entrar a {room_title} ({multiplier}x) cuesta {frj_to_display(entry_fee):.1f} FRJ."
            )

        # --- DEDUCT COST AND ENERGY ---
        wallet.frijolitos -= entry_fee
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user and user.wallet_address and settings.GEMA_ALGA_ADDRESS:
            _enqueue_chain_op(session, verified_user_id, "burn_frj", {
                "from_address": user.wallet_address,
                "amount": entry_fee,
            })

        axo.energy_current -= 10
        axo.status = "playing"

        ledger_fee = TransactionLedger(
            user_id=verified_user_id,
            amount=entry_fee,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.MARKET_BUY,
            description=f"Entrada a sala {room_title} con Axolotito {axo.name} ({multiplier}x)"
        )
        session.add(ledger_fee)

        # --- SIMULATION ---
        # Retrieve player cards
        player_card_ids = board.card_ids
        # Resolve card details for UX logging
        all_cards = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)).all()
        card_map = {c.id: c.name for c in all_cards}
        num_map = {c.id: (c.item_metadata or {}).get("numero_loteria", 0) for c in all_cards}
        zero_count = sum(1 for v in num_map.values() if v == 0)
        if zero_count > len(num_map) * 0.5:
            print(f"[WARNING] {zero_count}/{len(num_map)} cards have no numero_loteria in metadata. "
                  f"Run seed_cards.py to populate item_metadata.")

        # Fetch NPC boards from DB for this room
        all_card_ids = list(card_map.keys())
        npc_room_key = "rookie" if room_name == "rookie" else "champion"
        npc_boards_db = session.exec(
            select(PlayerBoard)
            .where(PlayerBoard.is_npc_pool == True)
            .where(PlayerBoard.npc_room == npc_room_key)
            .where(PlayerBoard.npc_retired == False)
        ).all()

        if len(npc_boards_db) == 0:
            _ensure_npc_pool(session, npc_room_key, all_card_ids, _rng)
            npc_boards_db = session.exec(
                select(PlayerBoard)
                .where(PlayerBoard.is_npc_pool == True)
                .where(PlayerBoard.npc_room == npc_room_key)
                .where(PlayerBoard.npc_retired == False)
            ).all()

        if len(npc_boards_db) >= bot_count:
            chosen_npc = _rng.sample(list(npc_boards_db), bot_count)
        else:
            # Fallback: use whatever NPC boards exist + fill rest with random (marked as None)
            chosen_npc = list(npc_boards_db)
            needed = bot_count - len(chosen_npc)
            chosen_npc += [None] * needed

        opponents_boards = [
            b.card_ids if b else _rng.sample(all_card_ids, 16)
            for b in chosen_npc
        ]
        chosen_npc_ids = [b.id if b else None for b in chosen_npc]

        # Play state
        player_marked    = set()
        opponents_marked = [set() for _ in range(bot_count)]

        deck = list(card_map.keys())
        _rng.shuffle(deck)
        # SAL: deck bias — empuja las cartas del tablero del jugador al fondo del mazo
        apply_sal_bias(deck, player_card_ids, axo.stat_salinity, _rng)

        turns = 0
        winner_name = None
        winner_bot_index: Optional[int] = None
        winning_line: Optional[list] = None
        drawn_cards_history = []
        player_misses = []
        lucky_save_used: bool = False
        lucky_save_turn: Optional[int] = None

        # Focus logic: chance to miss a card (same formula for player and bots)
        player_miss_chance = _miss_chance(axo.stat_focus)
        bot_miss_chance    = _miss_chance(bot_focus)

        for card_drawn in deck:
            turns += 1
            card_name = card_map.get(card_drawn, f"Carta #{card_drawn}")
            drawn_cards_history.append(card_name)

            # 1. Update Bots (with their own miss chance)
            for idx, opp_board in enumerate(opponents_boards):
                if card_drawn in opp_board:
                    opp_index = opp_board.index(card_drawn)
                    if _rng.random() >= bot_miss_chance:
                        opponents_marked[idx].add(opp_index)

            # 2. Update Player (Focus miss check)
            if card_drawn in player_card_ids:
                player_index = player_card_ids.index(card_drawn)
                if _rng.random() < player_miss_chance:
                    player_misses.append(card_name)
                else:
                    player_marked.add(player_index)

            # 3. Check Winners (player first — tie goes to player)
            player_won    = check_loterica_line(player_marked)
            opponents_won = [check_loterica_line(om) for om in opponents_marked]

            if player_won or any(opponents_won):
                if player_won:
                    winner_name = "player"
                    winning_line = sorted(list(get_winning_line(player_marked) or []))
                    break
                else:
                    if _lucky_save(axo.stat_luck, lucky_save_used):
                        lucky_save_used = True
                        lucky_save_turn = turns
                        # Lucky Save activated — bot victory annulled this turn; continue
                    else:
                        win_idx = opponents_won.index(True)
                        winner_name = f"opponent_{win_idx + 1}"
                        winner_bot_index = win_idx
                        winning_line = sorted(list(get_winning_line(opponents_marked[win_idx]) or []))
                        break

        # Fallback: deck exhausted without a winner (extremely rare)
        if not winner_name:
            best_idx = 0
            best_marks = 0
            best_threat = 0
            for i, om in enumerate(opponents_marked):
                n_marks = len(om)
                threat = max((len(line & om) for line in WINNING_LINES), default=0)
                if n_marks > best_marks or (n_marks == best_marks and threat > best_threat):
                    best_idx = i
                    best_marks = n_marks
                    best_threat = threat
            winner_name = f"opponent_{best_idx + 1}"
            winner_bot_index = best_idx
            best_line = max(
                WINNING_LINES,
                key=lambda line: len(line & opponents_marked[best_idx]),
                default=set()
            )
            winning_line = sorted(list(best_line)) if best_line else []

        # --- REWARDS & STATS UPDATE ---
        is_win = winner_name == "player"
        prize_awarded = 0
        streak = axo.cpu_win_streak   # streak BEFORE this game
        streak_bonus_pct = 0          # will be set in win block if applicable
        streak_broken    = False      # will be set in loss block if applicable

        if is_win:
            # Win: Prize scaled slightly by Luck stat (+0% to +10% max)
            # luck_bonus = (stat_luck / 1000) * win_prize → integer (VULN-06)
            luck_bonus = axo.stat_luck * win_prize // 1000
            prize_awarded = win_prize + luck_bonus

            # Win Streak bonus: +15% per previous consecutive win, capped at +50%
            if streak >= 1:
                streak_bonus_pct = min(50, streak * 15)
                prize_awarded = prize_awarded * (100 + streak_bonus_pct) // 100
            # Hard cap: luck + streak combined cannot exceed MAX_WIN_MULTIPLIER of base prize
            prize_awarded = min(prize_awarded, win_prize * MAX_WIN_MULTIPLIER_BPS // 100)
            streak_broken         = False
            axo.cpu_win_streak    = streak + 1

            # Add prize to wallet
            wallet.frijolitos += prize_awarded

            # Ledger entry for win
            streak_note = f" (🔥 racha x{streak}, +{streak_bonus_pct}%)" if streak_bonus_pct > 0 else ""
            from app.core.config import FRJ_DECIMALS_BACKEND
            _prize_display = prize_awarded / (10 ** FRJ_DECIMALS_BACKEND)
            ledger_win = TransactionLedger(
                user_id=verified_user_id,
                amount=prize_awarded,
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.REWARD,
                description=f"🏆 ¡Victoria en sala {room_title}! Premio: {_prize_display:.2f} FRJ{streak_note}"
            )
            session.add(ledger_win)

            # Accrue XP and levels
            board.xp += win_xp_board
            axo.experience += win_xp_axo
            board.games_won += 1
        else:
            # Loss: reset streak
            streak_broken      = streak >= 1
            axo.cpu_win_streak = 0
            # Loss: consolation prize
            prize_awarded = loss_consolation
            wallet.frijolitos += prize_awarded

            from app.core.config import FRJ_DECIMALS_BACKEND
            _prize_display = prize_awarded / (10 ** FRJ_DECIMALS_BACKEND)
            ledger_loss = TransactionLedger(
                user_id=verified_user_id,
                amount=prize_awarded,
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.REWARD,
                description=f"Consolación en sala {room_title}. Premio: {_prize_display:.2f} FRJ"
            )
            session.add(ledger_loss)

            board.xp += loss_xp_board
            axo.experience += loss_xp_axo

        # Update Board games_played and Level
        board.games_played += 1
        # Simple level up threshold: level * 100 XP
        while board.xp >= (board.level * 100):
            board.xp -= (board.level * 100)
            board.level += 1

        # Update Axolotito level
        while axo.experience >= (axo.level * 100):
            axo.experience -= (axo.level * 100)
            axo.level += 1

        # Reset status back to idle
        axo.status = "idle"

        # Save bot config preferences in the Axolotito if configured
        if bot_enabled:
            axo.bot_enabled = bot_enabled
            axo.bot_budget_axg = bot_budget_gal
            axo.bot_loss_limit_axg = bot_loss_limit_pct
            axo.bot_profit_limit_axg = bot_profit_limit_pct

        # --- UPDATE DAILY PLAY STREAK ---
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user:
            from datetime import datetime as dt_module
            now = dt_module.utcnow()
            today = now.date()
            if user.last_play_date:
                last_date = user.last_play_date.date()
                diff = (today - last_date).days
                if diff == 1:
                    user.daily_play_streak += 1
                elif diff > 1:
                    user.daily_play_streak = 1
            else:
                user.daily_play_streak = 1
            user.last_play_date = now
            session.add(user)

        # --- ON-CHAIN REWARDS & STATS UPDATE ---
        if user and user.wallet_address and settings.GEMA_ALGA_ADDRESS:
            _enqueue_chain_op(session, verified_user_id, "mint_frj", {
                "to_address": user.wallet_address,
                "amount": prize_awarded,
            })

        if board.blockchain_token_id is not None:
            xp_gained = win_xp_board if is_win else loss_xp_board
            _enqueue_chain_op(session, verified_user_id, "update_board_stats", {
                "board_token_id": board.blockchain_token_id,
                "won": is_win,
                "xp_gained": xp_gained,
            })

        # --- NPC BOARD XP UPDATE ---
        npc_win_xp  = win_xp_board
        npc_loss_xp = loss_xp_board

        for bot_idx, npc_b in enumerate(chosen_npc):
            if npc_b is None:
                continue
            npc_won = (winner_name == f"opponent_{bot_idx + 1}")
            npc_b.xp += npc_win_xp if npc_won else npc_loss_xp
            npc_b.games_played += 1
            if npc_won:
                npc_b.games_won += 1
            # Level up
            while npc_b.xp >= npc_b.level * 100:
                npc_b.xp -= npc_b.level * 100
                npc_b.level += 1
            # Graduation: level 10 → retire to gashapon pool
            if npc_b.level >= 10 and not npc_b.npc_retired:
                csr = round(npc_b.games_won / max(1, npc_b.games_played) * 100)
                npc_b.npc_retired = True
                npc_b.name = f"Tabla Forjada Nv.{npc_b.level} — {npc_b.games_played} batallas"
                npc_b.origin_story = (
                    f"Forjada en {npc_b.games_played} batallas. "
                    f"Ganó {csr}% de sus partidas. Nunca se rindió."
                )
                session.add(npc_b)
                # Spawn replacement NPC board
                _spawn_npc_replacement(session, npc_b.npc_room, all_card_ids, _rng)
            else:
                session.add(npc_b)

        # Build bot_board_nums for frontend display
        bot_board_nums = []
        for b in chosen_npc:
            if b:
                nums = [num_map.get(cid, 0) for cid in b.card_ids]
            else:
                nums = [0] * 16
            bot_board_nums.append(nums)

        # --- IMPRINTING: aplicar si este axo es padrino de un Webito ---
        _miss_rate = _miss_chance(axo.stat_focus)
        _mark_accuracy = max(0.0, 1.0 - _miss_rate)
        try:
            _imprinting_info = _apply_imprinting_if_needed(
                axo=axo,
                is_win=is_win,
                had_jackpot=prize_awarded > win_prize * 1.5,
                mark_accuracy=_mark_accuracy,
                session=session,
            )
        except Exception as exc:
            print(f"⚠️ [imprinting] error no-fatal al aplicar deltas: {exc}")
            _imprinting_info = None

        session.add(wallet)
        session.add(board)
        session.add(axo)
        session.commit()
        _flush_outbox(session)  # best-effort: procesa outbox inline, el worker reintenta si falla
        session.refresh(axo)
        session.refresh(board)

        # Response details
        winner_label = "Tú" if is_win else f"Bot {winner_name.split('_')[1]}"
        return {
            "resultado": "victoria" if is_win else "derrota",
            "room_title": room_title,
            "winner": winner_label,
            "turns": turns,
            "prize_gal": frj_to_display(prize_awarded),
            "board_xp_gained": win_xp_board if is_win else loss_xp_board,
            "board_level_current": board.level,
            "axo_xp_gained": win_xp_axo if is_win else loss_xp_axo,
            "axo_level_current": axo.level,
            "energy_remaining": axo.energy_current,
            "drawn_cards_sample": drawn_cards_history[:turns],
            "player_missed_cards": player_misses,
            "bot_count": bot_count,
            "bot_focus": bot_focus,
            "player_miss_chance_pct": round(player_miss_chance * 100, 1),
            "lucky_save_occurred": lucky_save_used,
            "lucky_save_turn": lucky_save_turn,
            "win_streak_after":  axo.cpu_win_streak,
            "streak_bonus_pct":  streak_bonus_pct,
            "streak_broken":     streak_broken,
            "bot_board_nums":    bot_board_nums,
            "bot_board_ids":     chosen_npc_ids,
            "bot_marked_indices": [list(om) for om in opponents_marked],
            "winning_line":      winning_line,
            "winner_bot_index":  winner_bot_index,
            "imprinting": _imprinting_info,
        }

    @staticmethod
    def feed_axolotito(
        axo_id: int,
        food_type: str,
        session: Session,
        verified_user_id: str,
    ) -> dict:
        """Feeds an Axolotito, deducting GAL from wallet and restoring energy."""
        axo = session.get(Axolotito, axo_id)
        if not axo:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axo.user_id != verified_user_id:
            raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")

        # Verificar tutorial completado
        from app.core.auth import require_tutorial
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user: require_tutorial(user)

        if axo.status == "sleeping":
            raise HTTPException(status_code=400, detail="No puedes alimentar a un Axolotito que está durmiendo.")

        # Cap max energy
        max_energy = axo.stat_stamina if axo.stat_stamina else 100
        if axo.energy_current >= max_energy:
            raise HTTPException(status_code=400, detail="Este Axolotito ya tiene su energía al máximo.")

        if food_type == "pellet":
            cost = CONSUMABLE_PRICES["alimento_comun"]
            energy_restore = 15
            food_name = "Algae Pellet"
        elif food_type == "shrimp":
            cost = CONSUMABLE_PRICES["alimento_premium"]
            energy_restore = 60
            food_name = "Premium Brine Shrimp"
        else:
            raise HTTPException(status_code=400, detail="Tipo de alimento no válido.")

        wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
        if wallet.frijolitos < cost:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Comprar {food_name} cuesta {frj_to_display(cost):.0f} FRJ.")

        # Deduct cost and add energy
        wallet.frijolitos -= cost
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user and user.wallet_address and settings.GEMA_ALGA_ADDRESS:
            _enqueue_chain_op(session, verified_user_id, "burn_frj", {
                "from_address": user.wallet_address,
                "amount": cost,
            })

        final_restore = energy_restore
        if axo.nature == "glutton":
            final_restore = energy_restore * 130 // 100  # +30% (VULN-06: integer)
        axo.energy_current = min(max_energy, axo.energy_current + final_restore)

        ledger = TransactionLedger(
            user_id=verified_user_id,
            amount=cost,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.MARKET_BUY,
            description=f"Alimentar a {axo.name} con {food_name}"
        )
        session.add(ledger)
        session.add(wallet)
        session.add(axo)
        session.commit()
        _flush_outbox(session)  # best-effort: procesa burn_frj outbox
        session.refresh(axo)

        return {
            "mensaje": f"Has alimentado a {axo.name} con {food_name}. Restaurados {energy_restore} de energía.",
            "energy_current": axo.energy_current,
            "max_energy": max_energy,
            "cost_gal": cost
        }

    @staticmethod
    def sleep_axolotito(
        axo_id: int,
        session: Session,
        verified_user_id: str,
    ) -> dict:
        """Puts an Axolotito to sleep to restore full energy for free after a short cooldown."""
        axo = session.get(Axolotito, axo_id)
        if not axo:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axo.user_id != verified_user_id:
            raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")

        # Verificar tutorial completado
        from app.core.auth import require_tutorial
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user: require_tutorial(user)

        if axo.status == "sleeping":
            raise HTTPException(status_code=400, detail="Este Axolotito ya está durmiendo.")

        max_energy = axo.stat_stamina if axo.stat_stamina else 100
        if axo.energy_current >= max_energy:
            raise HTTPException(status_code=400, detail="Este Axolotito ya está con energía al máximo.")

        axo.status = "sleeping"
        # Sleep duration: 1 minute for quick gameplay testing, reduced by PILA (stamina)
        base_recovery_minutes = 1.0
        recovery_minutes = base_recovery_minutes * recovery_multiplier(axo.stat_stamina)
        if axo.nature == "hyperactive":
            recovery_minutes *= 0.75  # 25% faster recovery
        axo.sleep_expires_at = datetime.utcnow() + timedelta(minutes=recovery_minutes)

        session.add(axo)
        session.commit()
        session.refresh(axo)

        return {
            "mensaje": f"{axo.name} se ha ido a dormir. Estará listo en 60 segundos.",
            "status": axo.status,
            "sleep_expires_at": axo.sleep_expires_at.isoformat() + "Z"
        }

    @staticmethod
    def wake_axolotito(
        axo_id: int,
        session: Session,
        verified_user_id: str,
    ) -> dict:
        """Wakes up an Axolotito from sleep, restoring full energy if cooldown expired."""
        axo = session.get(Axolotito, axo_id)
        if not axo:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axo.user_id != verified_user_id:
            raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")

        # Verificar tutorial completado
        from app.core.auth import require_tutorial
        user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
        if user: require_tutorial(user)

        if axo.status != "sleeping":
            raise HTTPException(status_code=400, detail="Este Axolotito no está durmiendo.")

        now = datetime.utcnow()
        if axo.sleep_expires_at and axo.sleep_expires_at > now:
            time_left = int((axo.sleep_expires_at - now).total_seconds())
            raise HTTPException(
                status_code=400,
                detail=f"Aún durmiendo... faltan {time_left} segundos para despertar."
            )

        # Wake up and restore energy
        max_energy = axo.stat_stamina if axo.stat_stamina else 100
        axo.status = "idle"
        axo.energy_current = max_energy
        axo.sleep_expires_at = None

        session.add(axo)
        session.commit()
        session.refresh(axo)

        return {
            "mensaje": f"¡{axo.name} se ha despertado y está con energía completa (100%)!",
            "status": axo.status,
            "energy_current": axo.energy_current
        }
