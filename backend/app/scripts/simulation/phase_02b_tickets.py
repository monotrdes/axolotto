from sqlmodel import Session, select

from app.models.items import ItemCatalog, ItemType, PlayerInventory


def phase_seed_tickets(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  📦 Sembrando Cápsulas iniciales para los jugadores...")

    # Buscar las 3 cápsulas en el catálogo
    all_consumables = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CONSUMABLE)
    ).all()
    capsula_items = {}
    for tier in ("bronce", "plata", "oro"):
        capsula_items[tier] = next(
            (c for c in all_consumables if (c.item_metadata or {}).get("capsule_tier") == tier),
            None
        )

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        # whale/collector get more capsules
        tiers_qty = {"bronce": 3, "plata": 2, "oro": 1}
        if personality.get("name") in ("whale", "collector"):
            tiers_qty = {"bronce": 5, "plata": 3, "oro": 2}

        for tier, qty in tiers_qty.items():
            item = capsula_items.get(tier)
            if not item:
                continue
            inv_item = session.exec(
                select(PlayerInventory)
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == item.id)
            ).first()
            if inv_item:
                inv_item.quantity += qty
            else:
                inv_item = PlayerInventory(
                    user_id=user_id,
                    item_id=item.id,
                    quantity=qty,
                    is_first_edition=False,
                    is_shiny=False
                )
            session.add(inv_item)
            print(f"  📦 {user_id}: +{qty} Cápsula {tier.capitalize()} en inventario")
    session.commit()
    return {}
