from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.models.user import User
from app.models.board import PlayerBoard
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.api.v1.endpoints.board import (
    create_random_board, create_manual_board,
    CreateManualBoardRequest,
    list_board_for_sale, list_board_for_rent, rent_board, unlock_board_slot,
    ListSaleRequest, ListRentRequest,
)
from app.services.bank_service import BankService
from app.core.config import frj_to_internal

from sim_types import _rng


def phase_boards(engine, config, **state) -> dict:
    """Compra slots si hacen falta; crea tableros aleatorios y 1 manual. Retorna boards_by_user en state."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  📋 Creando tableros (aleatorios + manual)...")
    boards_by_user: dict[str, list[int]] = {}

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        user        = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            continue

        n_random = personality.get("boards_random", 2)
        ids: list[int] = []

        # Verificar si necesita más slots
        current_boards = session.exec(
            select(func.count(PlayerBoard.id))
            .where(PlayerBoard.user_id == user_id, PlayerBoard.is_dead == False)
        ).one()
        needed = n_random + 1  # +1 para el manual
        if (user.unlocked_board_slots or 3) < needed:
            user.unlocked_board_slots = needed + 1
            session.add(user)
            session.commit()
            print(f"  🔓 {user_id}: slots ampliados a {user.unlocked_board_slots}")

        # Tableros aleatorios
        for b_i in range(n_random):
            try:
                res = create_random_board(
                    payload=CreateManualBoardRequest(
                        name=f"Tabla {personality['name'].title()} #{b_i+1}",
                        card_ids=[],
                    ),
                    session=session,
                    verified_user_id=user_id,
                )
                bid = res.get("board_id")
                if bid:
                    ids.append(bid)
                    stats["boards_created"] = stats.get("boards_created", 0) + 1
                    print(f"  📋 {user_id}: tabla aleatoria #{bid} ({len(res.get('card_ids',[]))} cartas)")
            except HTTPException as e:
                errors.append(f"board_random {user_id}: {e.detail}")

        # Tablero manual (con las cartas del inventario)
        inv_cards = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.CARD,
                PlayerInventory.quantity > 0,
            )
        ).all()

        # Obtener IDs de cartas ya usadas en tableros existentes (no disponibles)
        existing_boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.user_id == user_id,
                PlayerBoard.is_dead == False,
            )
        ).all()
        used_card_ids: set[int] = set()
        for b in existing_boards:
            if b.card_ids:
                used_card_ids.update(b.card_ids)

        # Deduplicar por item_id y filtrar cartas ya usadas en otros tableros
        unique_available: dict[int, PlayerInventory] = {}
        for inv in inv_cards:
            if inv.item_id not in used_card_ids and inv.item_id not in unique_available:
                unique_available[inv.item_id] = inv

        if len(unique_available) >= 16:
            available_list = list(unique_available.values())
            selected = _rng.sample(available_list, 16)
            card_ids = [inv.item_id for inv in selected]
            try:
                res = create_manual_board(
                    payload=CreateManualBoardRequest(
                        name=f"Tabla Manual {personality['name'].title()}",
                        card_ids=card_ids,
                    ),
                    session=session,
                    verified_user_id=user_id,
                )
                bid = res.get("board_id")
                if bid:
                    ids.append(bid)
                    stats["boards_created"] = stats.get("boards_created", 0) + 1
                    stats["manual_boards"]   = stats.get("manual_boards", 0) + 1
                    print(f"  🖊️  {user_id}: tabla MANUAL #{bid} con {len(card_ids)} cartas únicas")
            except HTTPException as e:
                errors.append(f"board_manual {user_id}: {e.detail}")
        else:
            print(f"  ℹ️  {user_id}: solo {len(unique_available)} cartas únicas disponibles para tabla manual (se necesitan 16)")

        boards_by_user[user_id] = ids

    # ── Board Marketplace: listar tableros para venta ─────────────────────
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        if personality["name"] not in ("whale", "aggressive"):
            continue

        user_boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.user_id == user_id,
                PlayerBoard.is_dead == False,
                PlayerBoard.is_frozen_by_vip == False,
                PlayerBoard.is_listed_for_sale == False,
                PlayerBoard.is_listed_for_rent == False,
                PlayerBoard.is_rented == False,
            )
        ).all()
        if len(user_boards) >= 2:
            board_to_sell = _rng.choice(user_boards)
            price = _rng.uniform(500, 3000)
            try:
                list_board_for_sale(
                    board_id=board_to_sell.id,
                    payload=ListSaleRequest(sale_price_gal=round(price, 2)),
                    session=session,
                    verified_user_id=user_id,
                )
                stats["boards_listed_sale"] = stats.get("boards_listed_sale", 0) + 1
                progress(f"  🏪 {user_id}: tablero #{board_to_sell.id} listado en venta a {price:.0f} FRJ")
            except HTTPException as e:
                errors.append(f"board_sale_list {user_id}: {e.detail}")

    # ── Board Rental: listar tableros para renta ──────────────────────────
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        if personality["name"] not in ("aggressive", "casual"):
            continue

        user_boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.user_id == user_id,
                PlayerBoard.is_dead == False,
                PlayerBoard.is_frozen_by_vip == False,
                PlayerBoard.is_listed_for_sale == False,
                PlayerBoard.is_listed_for_rent == False,
                PlayerBoard.is_rented == False,
            )
        ).all()
        for board in user_boards[:1]:
            fee = _rng.uniform(50, 300)
            try:
                list_board_for_rent(
                    board_id=board.id,
                    payload=ListRentRequest(rent_fee_gal=round(fee, 2), rent_share_owner_pct=30),
                    session=session,
                    verified_user_id=user_id,
                )
                stats["boards_listed_rent"] = stats.get("boards_listed_rent", 0) + 1
                progress(f"  🏠 {user_id}: tablero #{board.id} listado en renta a {fee:.0f} FRJ/día")
            except HTTPException as e:
                errors.append(f"board_rent_list {user_id}: {e.detail}")

    # ── Board Slot Upgrades: desbloquear slots extra ─────────────────────
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        if personality["name"] not in ("whale", "aggressive"):
            continue

        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            continue
        current_slots = user.unlocked_board_slots or 3
        if current_slots >= 6:
            continue

        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.frijolitos < frj_to_internal(500):
            wallet.frijolitos += frj_to_internal(1000)
            session.add(wallet)
            session.commit()

        try:
            unlock_board_slot(session=session, verified_user_id=user_id)
            session.refresh(user)
            stats["slot_upgrades"] = stats.get("slot_upgrades", 0) + 1
            progress(f"  🔓 {user_id}: slot desbloqueado ({current_slots} → {user.unlocked_board_slots})")
        except HTTPException as e:
            errors.append(f"slot_upgrade {user_id}: {e.detail}")

    progress(f"  ✅ {stats.get('boards_created', 0)} tableros creados "
             f"({stats.get('manual_boards', 0)} manuales), "
             f"{stats.get('boards_listed_sale', 0)} en venta, "
             f"{stats.get('boards_listed_rent', 0)} en renta, "
             f"{stats.get('slot_upgrades', 0)} slots desbloqueados.")
    return {"boards_by_user": boards_by_user}
