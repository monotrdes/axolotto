"""Staking calculations — passive GAL generation, XP preservation, and card management."""
import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.models.board import PlayerBoard
from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity
from app.models.user import User
from app.core.config import settings
from app.core.product_policy import require_feature

logger = logging.getLogger("board_service")


# ─── Slot XP helpers ─────────────────────────────────────────────────────

def _total_board_xp(board: PlayerBoard) -> int:
    """XP total acumulado = XP gastado en nivel-ups (curva triangular) + XP actual."""
    return (board.level * (board.level - 1) // 2) * 100 + board.xp


def _apply_preserved_xp_to_board(board: PlayerBoard, preserved_xp: int) -> None:
    """Aplica XP preservado a un tablero nuevo calculando el nivel resultante."""
    board.level = 1
    board.xp = preserved_xp
    while board.xp >= (board.level * 100):
        board.xp -= board.level * 100
        board.level += 1


def _level_from_total_xp(total_xp: int) -> int:
    """Nivel que resultaría de tener total_xp acumulado."""
    level, xp = 1, total_xp
    while xp >= (level * 100):
        xp -= level * 100
        level += 1
    return level


# ─── Passive staking helpers ─────────────────────────────────────────────

def get_board_hourly_rate(board: PlayerBoard, session: Session) -> float:
    """Calcula la recompensa de GAL por hora de una tabla en base a sus cartas y nivel."""
    if not board.card_ids:
        return 0.0

    cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.id.in_(board.card_ids))
    ).all()

    rarity_bonuses = {
        Rarity.COMMON: 0.05,
        Rarity.RARE: 0.15,
        Rarity.EPIC: 0.40,
        Rarity.LEGENDARY: 1.00
    }

    total_bonus = 0.0
    for card in cards:
        total_bonus += rarity_bonuses.get(card.rarity, 0.05)

    level_multiplier = 1.0 + (board.level / 10.0)

    return total_bonus * level_multiplier


def get_accrued_staking(board: PlayerBoard, session: Session) -> float:
    """Calcula las GAL acumuladas desde el último reclamo de staking, con cap de 24h y play-to-stake."""
    now = datetime.utcnow()

    # Play-to-Stake check
    user = session.exec(select(User).where(User.privy_did == board.user_id)).first()
    if not user or not user.last_play_date:
        return 0.0

    cutoff = now - timedelta(hours=24)
    if user.last_play_date < cutoff:
        return 0.0

    hours_elapsed = (now - board.last_staking_claim).total_seconds() / 3600.0
    if hours_elapsed <= 0:
        return 0.0

    # Cap at 24 hours
    hours_elapsed = min(hours_elapsed, 24.0)

    return hours_elapsed * get_board_hourly_rate(board, session)


def get_board_csr(board: PlayerBoard) -> float:
    """Calcula el Coeficiente de Suerte Real (CSR) en base a estadísticas y racha."""
    if board.games_played == 0:
        return 25.0  # Desempeño promedio estándar (25%)

    win_rate = (board.games_won / board.games_played) * 100.0

    # Racha: victorias en los últimos 5 juegos otorgan bono, derrotas restan
    streak_bonus = 0.0
    if board.recent_games_results:
        recent_wins = sum(1 for res in board.recent_games_results if res)
        streak_bonus = (recent_wins - 2.5) * 4.0

    return max(0.0, min(100.0, win_rate + streak_bonus))


# ─── Card staking operations ─────────────────────────────────────────────

def deduct_staked_cards(
    user_id: str,
    card_ids: list[int],
    card_first_editions: list[bool],
    session: Session,
):
    """Descuenta las cartas stakeadas del inventario disponible del jugador."""
    for idx, cid in enumerate(card_ids):
        is_fe = card_first_editions[idx] if idx < len(card_first_editions) else False
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == cid)
            .where(PlayerInventory.is_first_edition == is_fe)
            .with_for_update()
        ).first()
        if inv:
            inv.quantity -= 1
            if inv.quantity <= 0:
                session.delete(inv)
            else:
                session.add(inv)


def return_staked_cards(
    user_id: str,
    card_ids: list[int],
    card_first_editions: list[bool],
    session: Session,
    skip_index: int | None = None,
):
    """Devuelve las cartas al inventario del jugador (al desarmar una tabla). skip_index = carta destruída."""
    for idx, cid in enumerate(card_ids):
        if idx == skip_index:
            continue
        is_fe = card_first_editions[idx] if idx < len(card_first_editions) else False
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == cid)
            .where(PlayerInventory.is_first_edition == is_fe)
        ).first()
        if inv:
            inv.quantity += 1
            session.add(inv)
        else:
            session.add(
                PlayerInventory(
                    user_id=user_id,
                    item_id=cid,
                    quantity=1,
                    is_first_edition=is_fe,
                    is_shiny=False,
                )
            )


# ─── Staking claim operations ────────────────────────────────────────────

def claim_staking_operation(board_id: int, user_id: str, session: Session) -> dict:
    """Reclama las Gemas Alga acumuladas por el staking de las cartas de esta tabla."""
    require_feature(settings.ENABLE_GAMEPLAY_TOKEN_REWARDS, "gameplay_token_rewards")
    from fastapi import HTTPException
    from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
    from app.services.bank_service import BankService
    from app.core.config import frj_to_display

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta tabla.")
    if board.is_dead:
        raise HTTPException(
            status_code=400, detail="Esta tabla está desarmada (muerta)."
        )

    accrued = get_accrued_staking(board, session)
    if accrued <= 0:
        return {
            "mensaje": "No tienes recompensas acumuladas aún.",
            "claimed_amount": 0.0,
        }

    wallet = BankService.get_or_create_wallet(session, user_id)
    wallet.frijolitos += accrued

    board.last_staking_claim = datetime.utcnow()

    ledger = TransactionLedger(
        user_id=user_id,
        amount=accrued,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD,
        description=f"Reclamo de Staking de cartas en tabla #{board_id}",
    )

    session.add(wallet)
    session.add(board)
    session.add(ledger)
    session.commit()

    return {
        "mensaje": f"¡Has reclamado {frj_to_display(accrued):.2f} FRJ exitosamente!",
        "claimed_amount": frj_to_display(accrued),
    }


def claim_all_staking_operation(user_id: str, session: Session) -> dict:
    """Reclama las Gemas Alga acumuladas por el staking de TODAS las tablas del usuario a la vez."""
    require_feature(settings.ENABLE_GAMEPLAY_TOKEN_REWARDS, "gameplay_token_rewards")
    from fastapi import HTTPException
    from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
    from app.services.bank_service import BankService
    from app.core.config import frj_to_display

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).all()

    total_accrued = 0.0
    claimed_boards = []

    for board in boards:
        accrued = get_accrued_staking(board, session)
        if accrued > 0:
            total_accrued += accrued
            board.last_staking_claim = datetime.utcnow()
            session.add(board)
            claimed_boards.append(board.id)

    if total_accrued <= 0:
        return {
            "mensaje": "No tienes recompensas acumuladas en ninguna de tus tablas.",
            "claimed_amount": 0.0,
            "claimed_boards": [],
        }

    wallet = BankService.get_or_create_wallet(session, user_id)
    wallet.frijolitos += total_accrued

    ledger = TransactionLedger(
        user_id=user_id,
        amount=total_accrued,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD,
        description=f"Reclamo masivo de Staking para tablas: {claimed_boards}",
    )

    session.add(wallet)
    session.add(ledger)
    session.commit()

    return {
        "mensaje": f"¡Has reclamado {frj_to_display(total_accrued):.2f} FRJ exitosamente de {len(claimed_boards)} tablas!",
        "claimed_amount": frj_to_display(total_accrued),
        "claimed_boards": claimed_boards,
    }
