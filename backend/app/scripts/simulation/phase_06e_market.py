from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.services.bank_service import BankService
from app.core.config import frj_to_internal
from app.api.v1.endpoints.market import (
    list_inventory_item, buy_inventory_listing, get_inventory_listings,
    ListInventoryItemRequest,
)
from app.api.v1.endpoints.user import (
    list_axolotito_for_sale, ListAxoSaleRequest,
)

from sim_types import _rng


def phase_p2p_market(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🤝 Simulando Mercado Secundario P2P (Listado y Venta)...")

    # 1. Listar sobres
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] == "whale":
            continue

        sealed_boosters = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0
            )
        ).all()

        for inv in sealed_boosters:
            item = session.get(ItemCatalog, inv.item_id)
            is_foil = (item.item_metadata or {}).get("is_foil", False) if item else False
            price = 500.0 if is_foil else 200.0

            try:
                res = list_inventory_item(
                    request=ListInventoryItemRequest(inventory_id=inv.id, quantity=1, price_gal=price),
                    session=session,
                    verified_user_id=user_id
                )
                stats["p2p_listings"] = stats.get("p2p_listings", 0) + 1
                print(f"  🤝 {user_id}: listó sobre '{item.name if item else 'Booster'}' en P2P a {price} FRJ")
            except HTTPException as e:
                errors.append(f"p2p_list {user_id}: {e.detail}")

    # 2. Comprar sobres listados
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] not in ("whale", "collector"):
            continue

        listings = get_inventory_listings(item_type=ItemType.BOOSTER, session=session)
        if not listings:
            break

        bought_count = 0
        for listing in listings:
            if bought_count >= 2:
                break

            listing_id = listing["id"]
            seller_id = listing["seller_id"]
            price = listing["price_gal"]

            if seller_id == user_id:
                continue

            wallet = BankService.get_or_create_wallet(session, user_id)
            if wallet.frijolitos < frj_to_internal(price):
                wallet.frijolitos += frj_to_internal(price + 100.0)
                session.add(wallet)
                session.commit()

            try:
                res = buy_inventory_listing(listing_id=listing_id, session=session, verified_user_id=user_id)
                stats["p2p_purchases"] = stats.get("p2p_purchases", 0) + 1
                print(f"  🤝 {user_id}: compró sobre en P2P por {price} FRJ del vendedor {seller_id}")
                bought_count += 1
            except HTTPException as e:
                errors.append(f"p2p_buy {user_id}: {e.detail}")

    # 3. Listar Axolotitos para venta
    progress("  🦎 Mercado de Axolotitos: listando para venta...")
    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        if personality["name"] == "free2play":
            continue

        axos = session.exec(
            select(Axolotito).where(
                Axolotito.user_id == user_id,
                Axolotito.status == "idle",
                Axolotito.is_frozen_by_vip == False,
                Axolotito.is_listed_for_sale == False,
            )
        ).all()
        if len(axos) >= 2 and _rng.random() < 0.4:
            axo_to_sell = _rng.choice(axos)
            price = _rng.uniform(1000, 5000)
            try:
                list_axolotito_for_sale(
                    axolotito_id=axo_to_sell.id,
                    payload=ListAxoSaleRequest(sale_price_gal=round(price, 2)),
                    session=session,
                    verified_user_id=user_id,
                )
                stats["axos_listed_sale"] = stats.get("axos_listed_sale", 0) + 1
                progress(f"  🦎 {user_id}: '{axo_to_sell.name}' listado en venta a {price:.0f} FRJ")
            except HTTPException as e:
                errors.append(f"axo_sale_list {user_id}: {e.detail}")

    # 4. Comprar Axolotitos listados
    progress("  🦎 Mercado de Axolotitos: procesando compras P2P...")
    axos_on_sale = session.exec(
        select(Axolotito).where(
            Axolotito.is_listed_for_sale == True,
        )
    ).all()

    for axo in axos_on_sale:
        eligible_buyers = [p["user_id"] for p in players if p["user_id"] != axo.user_id]
        if not eligible_buyers:
            continue
        buyer_id = _rng.choice(eligible_buyers)
        price = axo.sale_price_gal or 2000.0

        wallet = BankService.get_or_create_wallet(session, buyer_id)
        if wallet.frijolitos < frj_to_internal(price):
            wallet.frijolitos = max(wallet.frijolitos or 0, frj_to_internal(price + 1000.0))
            session.add(wallet)
            session.commit()

        try:
            from app.api.v1.endpoints.user import buy_axolotito
            buy_axolotito(axolotito_id=axo.id, session=session, verified_user_id=buyer_id)
            stats["axos_bought_p2p"] = stats.get("axos_bought_p2p", 0) + 1
            print(f"  🦎 {buyer_id}: compró Axolotito '{axo.name}' (#{axo.id}) en P2P por {price:.0f} FRJ")
        except HTTPException as e:
            errors.append(f"axo_buy_p2p {buyer_id} axo #{axo.id}: {e.detail}")
        except Exception as e:
            errors.append(f"axo_buy_p2p_unexpected {buyer_id}: {e}")
            session.rollback()

    # 5. Comprar tableros en venta
    progress("  📋 Mercado de Tableros: procesando compras P2P...")
    boards_on_sale = session.exec(
        select(PlayerBoard).where(
            PlayerBoard.is_listed_for_sale == True,
            PlayerBoard.is_dead == False,
        )
    ).all()

    for board in boards_on_sale:
        eligible_buyers = [p["user_id"] for p in players if p["user_id"] != board.user_id]
        if not eligible_buyers:
            continue
        buyer_id = _rng.choice(eligible_buyers)
        price = board.sale_price_gal or 1000.0

        wallet = BankService.get_or_create_wallet(session, buyer_id)
        if wallet.frijolitos < frj_to_internal(price):
            wallet.frijolitos = max(wallet.frijolitos or 0, frj_to_internal(price + 500.0))
            session.add(wallet)
            session.commit()

        try:
            from app.api.v1.endpoints.board import buy_board
            buy_board(board_id=board.id, session=session, verified_user_id=buyer_id)
            stats["boards_bought_p2p"] = stats.get("boards_bought_p2p", 0) + 1
            print(f"  📋 {buyer_id}: compró tablero #{board.id} en P2P por {price:.0f} FRJ")
        except HTTPException as e:
            errors.append(f"board_buy_p2p {buyer_id} board #{board.id}: {e.detail}")
        except Exception as e:
            errors.append(f"board_buy_p2p_unexpected {buyer_id}: {e}")
            session.rollback()

    # 6. Rentar tableros en renta
    progress("  🏠 Mercado de Rentas: procesando rentas P2P...")
    boards_on_rent = session.exec(
        select(PlayerBoard).where(
            PlayerBoard.is_listed_for_rent == True,
            PlayerBoard.is_dead == False,
            PlayerBoard.is_rented == False,
        )
    ).all()

    for board in boards_on_rent:
        eligible_renters = [p["user_id"] for p in players if p["user_id"] != board.user_id]
        if not eligible_renters:
            continue
        renter_id = _rng.choice(eligible_renters)
        fee = board.rent_fee_gal or 100.0

        wallet = BankService.get_or_create_wallet(session, renter_id)
        if wallet.frijolitos < frj_to_internal(fee):
            wallet.frijolitos = max(wallet.frijolitos or 0, frj_to_internal(fee + 100.0))
            session.add(wallet)
            session.commit()

        try:
            from app.api.v1.endpoints.board import rent_board
            rent_board(board_id=board.id, session=session, verified_user_id=renter_id)
            stats["boards_rented_p2p"] = stats.get("boards_rented_p2p", 0) + 1
            print(f"  🏠 {renter_id}: rentó tablero #{board.id} en P2P por {fee:.0f} FRJ/día")
        except HTTPException as e:
            errors.append(f"board_rent_p2p {renter_id} board #{board.id}: {e.detail}")
        except Exception as e:
            errors.append(f"board_rent_p2p_unexpected {renter_id}: {e}")
            session.rollback()

    # Rebuild boards_by_user mapping in state to reflect new ownership after transactions
    new_boards_by_user = {}
    for p in players:
        user_id = p["user_id"]
        db_boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.user_id == user_id,
                PlayerBoard.is_dead == False,
            )
        ).all()
        new_boards_by_user[user_id] = [b.id for b in db_boards]
    state["boards_by_user"].update(new_boards_by_user)

    progress(f"  ✅ P2P: {stats.get('p2p_listings', 0)} listados, "
             f"{stats.get('p2p_purchases', 0)} compras sobre, "
             f"{stats.get('axos_listed_sale', 0)} axos listados, "
             f"{stats.get('axos_bought_p2p', 0)} axos comprados P2P, "
             f"{stats.get('boards_bought_p2p', 0)} tableros comprados P2P, "
             f"{stats.get('boards_rented_p2p', 0)} tableros rentados P2P.")
    return {}
