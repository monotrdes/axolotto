"""
phase_07e_cave_expansion.py — Expansión del Cenote (niveles 2-8).

Simula el crecimiento completo del Cenote:
  - Verifica el estado actual de la cueva (/cave/status)
  - Inyecta logros/stats necesarios para cada nivel (daily_play_streak, jackpots, etc.)
  - Inicia la excavación con FRJ (con descuento VIP 50% si aplica)
  - Acelera la excavación con AXF para completarla instantáneamente
  - Registra el nivel alcanzado y el huevo de recompensa

VIP tier shortcuts:
  - Nivel 6: VIP Coral+ salta el logro
  - Nivel 7: VIP Dorado+ salta el logro
  - Nivel 8: VIP Axolite salta el logro
"""
import random
from datetime import datetime, timedelta

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.user import User
from app.models.economy import Wallet, CurrencyType, TransactionLedger, TransactionType
from app.models.axolotito import Axolotito
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.api.v1.endpoints.cave_expansion import (
    get_cave_status,
    start_expansion,
    accelerate_expansion,
    CAVE_LEVEL_DEFINITIONS,
    MAX_CAVE_LEVEL,
    _get_user_stats,
)

_rng = random.SystemRandom()


def _ensure_board_stats(
    session: Session,
    user_id: str,
    min_games: int = 0,
    min_wins: int = 0,
) -> None:
    """
    Asegura que al menos un PlayerBoard del usuario tenga >= min_games
    y >= min_wins. Si no hay tableros, crea uno dummy para la simulación.
    _get_user_stats() solo cuenta desde PlayerBoard, no desde TransactionLedger.
    """
    from app.models.board import PlayerBoard
    boards = session.exec(
        select(PlayerBoard).where(
            PlayerBoard.user_id == user_id,
            PlayerBoard.is_dead == False,
        )
    ).all()

    if not boards:
        # Crear un tablero dummy para satisfacer los checks de stats
        board = PlayerBoard(
            user_id=user_id,
            name="[SIM] Tablero de expansión",
            is_dead=False,
            games_played=max(min_games, 1),
            games_won=min_wins,
        )
        session.add(board)
        session.commit()
        print(f"    🎴 Tablero dummy creado: {min_games} partidas, {min_wins} victorias")
        return

    total_games = sum(b.games_played or 0 for b in boards)
    total_wins = sum(b.games_won or 0 for b in boards)

    needs_update = False
    if min_games > 0 and total_games < min_games:
        boards[0].games_played = (boards[0].games_played or 0) + (min_games - total_games)
        needs_update = True
        print(f"    🎮 Partidas forzadas: {total_games} → {min_games}")
    if min_wins > 0 and total_wins < min_wins:
        boards[0].games_won = (boards[0].games_won or 0) + (min_wins - total_wins)
        needs_update = True
        print(f"    ⚔️  Victorias forzadas: {total_wins} → {min_wins}")

    if needs_update:
        session.add(boards[0])
        session.commit()


def _ensure_achievements_for_level(
    session: Session,
    user_id: str,
    target_level: int,
    user: User,
) -> None:
    """
    Manipula la DB para asegurar que el usuario cumple los logros
    requeridos para expandir al `target_level`.
    Los VIPs saltan automáticamente niveles 6+ según su tier.
    """
    vip_tier = user.vip_tier if user.is_vip else None

    if target_level == 2:
        # Requiere total_games >= 10 y main_axo_level >= 3
        main_axo = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .order_by(Axolotito.created_at)
        ).first()
        if main_axo and (main_axo.level or 1) < 3:
            main_axo.level = 3
            main_axo.experience = 500
            session.add(main_axo)
            session.commit()
            print(f"    📈 {main_axo.name} subido a nivel 3 para nivel 2")

        _ensure_board_stats(session, user_id, min_games=10)

    elif target_level == 3:
        # Requiere total_wins >= 3 y daily_play_streak >= 3
        if (user.daily_play_streak or 0) < 3:
            user.daily_play_streak = 3
            user.last_play_date = datetime.utcnow()
            session.add(user)
            session.commit()
            print(f"    📈 daily_play_streak forzado a 3 para nivel 3")

        _ensure_board_stats(session, user_id, min_wins=3)

    elif target_level == 4:
        # Requiere al menos 1 jackpot ganado
        jackpots = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id == user_id,
                TransactionLedger.description.ilike("%jackpot%"),
            )
        ).all()
        if len(jackpots) == 0:
            session.add(TransactionLedger(
                user_id=user_id,
                amount=500.0,
                currency=CurrencyType.GEMA_ALGA,
                tx_type=TransactionType.REWARD,
                description="[SIM] Jackpot ganado en partida multijugador",
            ))
            session.commit()
            print(f"    🎰 Jackpot simulado inyectado para nivel 4")

    elif target_level == 5:
        # Requiere main_axo_level >= 15
        main_axo = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .order_by(Axolotito.created_at)
        ).first()
        if main_axo:
            if (main_axo.level or 1) < 15:
                main_axo.level = 15
                main_axo.experience = 5000
                session.add(main_axo)
                session.commit()
                print(f"    📈 {main_axo.name} subido a nivel 15 para nivel 5")
        else:
            # Sin Axolotito: crear uno dummy nivel 15
            dummy_axo = Axolotito(
                user_id=user_id,
                name="[SIM] Axolote ancestral",
                level=15,
                experience=5000,
                skin_color="common",
            )
            session.add(dummy_axo)
            session.commit()
            print(f"    🦎 Axolotito dummy nivel 15 creado para nivel 5")

    elif target_level == 6:
        # Requiere (games>=50 + feeds>=100) O VIP Coral+
        if vip_tier in ("coral", "dorado", "axolite"):
            print(f"    👑 VIP {vip_tier} salta logro de nivel 6")
            return
        # Inyectar feeds (contados desde TransactionLedger con "alimentar")
        feed_count = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id == user_id,
                TransactionLedger.description.ilike("%alimentar%"),
            )
        ).all()
        shortfall = 100 - len(feed_count)
        if shortfall > 0:
            for _ in range(shortfall):
                session.add(TransactionLedger(
                    user_id=user_id,
                    amount=0,
                    currency=CurrencyType.GEMA_ALGA,
                    tx_type=TransactionType.MARKET_BUY,
                    description="[SIM] Alimentar a Axolotito",
                ))
            session.commit()
            print(f"    🍽️  {shortfall} feeds simulados para nivel 6 (total: 100)")

        # Asegurar games >= 50 en tableros
        _ensure_board_stats(session, user_id, min_games=50)

    elif target_level == 7:
        # Requiere (games>=100 + wins>=15) O VIP Dorado+
        if vip_tier in ("dorado", "axolite"):
            print(f"    👑 VIP {vip_tier} salta logro de nivel 7")
            return
        _ensure_board_stats(session, user_id, min_games=100, min_wins=15)

    elif target_level == 8:
        # Requiere (games>=200 + epic/legendary axo) O VIP Axolite
        if vip_tier == "axolite":
            print(f"    👑 VIP Axolite salta logro de nivel 8")
            return
        # Dar skin premium a un axolotito
        main_axo = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .order_by(Axolotito.created_at)
        ).first()
        if main_axo:
            main_axo.skin_color = "astral"
            session.add(main_axo)
            session.commit()
            print(f"    ✨ {main_axo.name} convertido a skin astral para nivel 8")

        _ensure_board_stats(session, user_id, min_games=200)


def _cleanup_stuck_expansion(session: Session, user_id: str, target_level: int) -> None:
    """
    Si start_expansion commiteó pero accelerate_expansion falló, el usuario queda
    con cave_expansion_target_level y cave_expansion_started_at seteados, y FRJ
    ya descontados. Esta función revierte ese estado para que el usuario no quede
    atrapado en una excavación que nunca se completará.
    """
    from app.models.user import User as UserModel
    user = session.exec(
        select(UserModel).where(UserModel.privy_did == user_id).with_for_update()
    ).first()
    if not user:
        return

    # Solo limpiar si realmente hay una expansión stuck (target_level coincide)
    if user.cave_expansion_target_level != target_level:
        return

    level_def = CAVE_LEVEL_DEFINITIONS.get(target_level, {})
    frj_cost = level_def.get("cost_frj", 0)
    # Reembolsar con descuento VIP si aplica
    is_vip = user.is_vip
    frj_refund = int(frj_cost * 0.5) if is_vip else frj_cost

    # Reembolsar FRJ
    wallet = session.exec(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    ).first()
    if wallet:
        wallet.frijolitos = (wallet.frijolitos or 0) + frj_refund
        session.add(wallet)

    # Limpiar estado de expansión
    user.cave_expansion_target_level = None
    user.cave_expansion_started_at = None
    session.add(user)
    session.commit()
    print(f"  🧹 {user_id}: Estado de excavación nivel {target_level} limpiado, "
          f"{frj_refund} FRJ reembolsados")


def phase_cave_expansion(engine, config, **state) -> dict:
    """Simula la expansión del Cenote de nivel 1 a 8 para todos los bots."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  ⛏️  Fase de expansión del Cenote...")

    # ── Solo el admin llega a nivel máximo (8) ──
    from app.core.config import settings
    admin_did = getattr(settings, "ADMIN_PRIVY_DID", None)
    # Fallback del .env si no está en settings
    if not admin_did:
        import os
        admin_did = os.getenv("ADMIN_PRIVY_DID", "did:privy:cmpl1jf3t01cc0ck4gqt004l5")

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        p_name = personality.get("name", "casual")
        vip_tier = personality.get("vip_tier")

        user = session.exec(
            select(User).where(User.privy_did == user_id).with_for_update()
        ).first()
        if not user:
            errors.append(f"cave_exp: user {user_id} not found")
            continue

        # ── Determinar nivel objetivo ──
        is_admin = (user_id == admin_did)
        if is_admin:
            target_max = 8  # Admin llega al máximo
            print(f"  👑 {user_id} ({p_name}): ADMIN — target nivel 8")
        elif p_name == "whale":
            target_max = 6  # Whale normal llega a 6 (VIP Coral/Dorado)
        elif p_name in ("aggressive", "collector"):
            target_max = 5  # Comprometidos llegan a 5
        elif p_name == "casual":
            target_max = 4
        else:  # free2play
            target_max = 3

        current_level = user.cave_level or 1
        if current_level >= target_max:
            print(f"  ⛏️  {user_id} ({p_name}): ya en nivel {current_level}, "
                  f"target {target_max}. Saltando.")
            continue

        # Asegurar fondos para todas las expansiones
        wallet = session.exec(
            select(Wallet).where(Wallet.user_id == user_id).with_for_update()
        ).first()
        if wallet:
            wallet.frijolitos = max(wallet.frijolitos or 0, 200_000)
            wallet.axofichas = max(wallet.axofichas or 0, 5_000)
            session.add(wallet)
            session.commit()

        expansions_done = 0
        axf_spent_total = 0.0
        eggs_received = 0

        for target_level in range(current_level + 1, target_max + 1):
            try:
                # ── Asegurar logros para este nivel ──
                session.refresh(user)
                _ensure_achievements_for_level(
                    session=session,
                    user_id=user_id,
                    target_level=target_level,
                    user=user,
                )

                # ── Verificar estado actual ──
                try:
                    cave_status = get_cave_status(
                        session=session,
                        verified_user_id=user_id,
                    )
                    print(f"  🏠 {user_id}: Cenote nivel {cave_status['current']['level']} "
                          f"— siguiente: {cave_status.get('next_level', {}).get('name', 'N/A')}")
                except Exception as e:
                    errors.append(f"cave_status {user_id}: {e}")
                    continue

                # ── Iniciar expansión ──
                level_def = CAVE_LEVEL_DEFINITIONS.get(target_level, {})
                level_name = level_def.get("name", f"Nivel {target_level}")

                try:
                    res = start_expansion(
                        session=session,
                        verified_user_id=user_id,
                    )
                    print(f"  ⛏️  {user_id}: Excavación iniciada → {level_name} "
                          f"({res.get('frj_spent', 0)} FRJ)")
                    stats["cave_expansions_total"] = stats.get("cave_expansions_total", 0) + 1
                except HTTPException as e:
                    session.rollback()
                    errors.append(f"cave_expand {user_id} → {target_level}: {e.detail}")
                    break

                # ── Acelerar excavación ──
                try:
                    accel_res = accelerate_expansion(
                        session=session,
                        verified_user_id=user_id,
                    )
                    axf_spent = accel_res.get("axf_spent", 0)
                    axf_spent_total += axf_spent
                    expansions_done += 1

                    reward = accel_res.get("reward_egg")
                    if reward:
                        eggs_received += 1
                        print(f"  🥚 {user_id}: Huevo de recompensa recibido: {reward.get('name', '?')}")

                    new_level = accel_res.get("current_level", target_level)
                    print(f"  ✅ {user_id}: {level_name} completada (nivel {new_level}) "
                          f"— {axf_spent} AXF aceleración")

                except HTTPException as e:
                    # ⚠️ start_expansion ya commiteó → limpiar estado de expansión + reembolsar FRJ
                    session.rollback()
                    errors.append(f"cave_accelerate {user_id} → {target_level}: {e.detail}")
                    _cleanup_stuck_expansion(session, user_id, target_level)
                    break

            except Exception as e:
                # ⚠️ Si start_expansion commiteó antes de fallar, limpiar estado
                session.rollback()
                errors.append(f"cave_expansion_loop {user_id} lvl {target_level}: {e}")
                _cleanup_stuck_expansion(session, user_id, target_level)
                break

        # Refresh para ver nivel final
        session.refresh(user)
        final_level = user.cave_level
        print(f"  🏆 {user_id} ({p_name}): Cenote nivel {final_level}, "
              f"{expansions_done} expansiones, {axf_spent_total:.0f} AXF gastados, "
              f"{eggs_received} huevos recibidos")

        stats["cave_expansion_axf_spent"] = (
            stats.get("cave_expansion_axf_spent", 0) + axf_spent_total
        )
        stats["max_cave_level_reached"] = max(
            stats.get("max_cave_level_reached", 1), final_level
        )

    progress(
        f"  ✅ Cenotes expandidos: máx nivel {stats.get('max_cave_level_reached', 1)}, "
        f"{stats.get('cave_expansions_total', 0)} expansiones totales, "
        f"{stats.get('cave_expansion_axf_spent', 0):.0f} AXF gastados"
    )
    return {}
