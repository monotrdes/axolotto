from sqlmodel import Session
from fastapi import HTTPException

from app.services.bank_service import BankService
from app.api.v1.endpoints.board import delete_board


def phase_board_deconstruction(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    boards_by_user: dict = state["boards_by_user"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🧴 Simulando desarme seguro con Solvente de Pegamento...")

    for p in players:
        user_id = p["user_id"]
        if p["personality"]["name"] not in ("casual", "aggressive"):
            continue

        user_boards = boards_by_user.get(user_id, [])
        if len(user_boards) < 2:
            continue

        board_id = user_boards.pop()
        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.frijolitos < 120.0:
            wallet.frijolitos += 150.0
            session.add(wallet)
            session.commit()

        try:
            res = delete_board(board_id=board_id, session=session, verified_user_id=user_id)
            stats["boards_deconstructed"] = stats.get("boards_deconstructed", 0) + 1
            print(f"  🧴 {user_id}: desarmó la tabla #{board_id} usando Solvente de Pegamento (120 GAL). 16 cartas devueltas.")
        except HTTPException as e:
            errors.append(f"deconstruct {user_id} board #{board_id}: {e.detail}")

    return {}
