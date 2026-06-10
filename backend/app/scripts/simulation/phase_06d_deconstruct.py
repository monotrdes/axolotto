from sqlmodel import Session
from fastapi import HTTPException

from app.services.bank_service import BankService
from app.api.v1.endpoints.board import delete_board
from app.core.prices import CONSUMABLE_PRICES


def phase_board_deconstruction(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    boards_by_user: dict = state["boards_by_user"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    solvente_cost = CONSUMABLE_PRICES["solvente"]  # 1 AXF

    progress("  🧴 Simulando desarme seguro con Solvente de Pegamento (1 AXF)...")

    for p in players:
        user_id = p["user_id"]
        if p["personality"]["name"] not in ("casual", "aggressive"):
            continue

        user_boards = boards_by_user.get(user_id, [])
        if len(user_boards) < 2:
            continue

        board_id = user_boards.pop()
        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.axofichas < solvente_cost:
            wallet.axofichas += solvente_cost * 2
            session.add(wallet)
            session.commit()

        try:
            res = delete_board(board_id=board_id, session=session, verified_user_id=user_id)
            stats["boards_deconstructed"] = stats.get("boards_deconstructed", 0) + 1
            preserved = res.get("preserved_xp", 0)
            print(f"  🧴 {user_id}: desarmó la tabla #{board_id} (1 AXF). 16 cartas devueltas. XP preservado en slot: {preserved}.")
        except HTTPException as e:
            errors.append(f"deconstruct {user_id} board #{board_id}: {e.detail}")

    return {}
