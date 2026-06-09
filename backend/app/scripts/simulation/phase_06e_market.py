from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.models.axolotito import Axolotito
from app.services.bank_service import BankService
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
                print(f"  🤝 {user_id}: listó sobre '{item.name if item else 'Booster'}' en P2P a {price} GAL")
            except HTTPException as e:
                errors.append(f"p2p_list {user_id}: {e.detail}")

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
            if wallet.frijolitos < price:
                wallet.frijolitos += price + 100.0
                session.add(wallet)
                session.commit()

            try:
                res = buy_inventory_listing(listing_id=listing_id, session=session, verified_user_id=user_id)
                stats["p2p_purchases"] = stats.get("p2p_purchases", 0) + 1
                print(f"  🤝 {user_id}: compró sobre en P2P por {price} GAL del vendedor {seller_id}")
                bought_count += 1
            except HTTPException as e:
                errors.append(f"p2p_buy {user_id}: {e.detail}")

    # ── Axolotito Marketplace: listar axolotitos para venta ──────────────
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
                progress(f"  🦎 {user_id}: '{axo_to_sell.name}' listado en venta a {price:.0f} GAL")
            except HTTPException as e:
                errors.append(f"axo_sale_list {user_id}: {e.detail}")

    progress(f"  ✅ P2P: {stats.get('p2p_listings', 0)} listados, "
             f"{stats.get('p2p_purchases', 0)} compras, "
             f"{stats.get('axos_listed_sale', 0)} axos en venta.")
    return {}
