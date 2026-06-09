"""
cave_service.py — Cave (Cueva) management for Axolotitos.

Handles equipping, unequipping, and listing cave items for an axolotito.
"""
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.items import ItemCatalog, ItemType, PlayerInventory


def _cave_max_slots(axo_level: int) -> int:
    """Returns cave slot count: 1 base + 1 per 5 levels, capped at 3."""
    return min(3, 1 + (axo_level // 5))


def get_cave(axo_id: int, session: Session, verified_user_id: str) -> dict:
    """Returns current cave items and slot capacity for an axolotito."""
    axo = _get_axo_or_403(axo_id, session, verified_user_id)
    max_slots = _cave_max_slots(axo.level)
    items = []
    for item_id in (axo.cave_items or []):
        catalog = session.get(ItemCatalog, item_id)
        if catalog:
            items.append({
                "id": catalog.id,
                "name": catalog.name,
                "rarity": catalog.rarity,
                "item_metadata": catalog.item_metadata,
            })
    return {"axo_id": axo_id, "cave_items": items, "max_slots": max_slots}


def equip_cave_item(axo_id: int, item_id: int, session: Session, verified_user_id: str) -> dict:
    """Equips a cave item from the player's inventory into the axolotito's cave."""
    axo = _get_axo_or_403(axo_id, session, verified_user_id)

    max_slots = _cave_max_slots(axo.level)
    cave = list(axo.cave_items or [])

    if len(cave) >= max_slots:
        raise HTTPException(status_code=400, detail="No hay slots disponibles en esta cueva.")
    if item_id in cave:
        raise HTTPException(status_code=400, detail="Este item ya está equipado.")

    # Verify item type is CAVE_ITEM
    catalog = session.get(ItemCatalog, item_id)
    if not catalog or catalog.item_type != ItemType.CAVE_ITEM:
        raise HTTPException(status_code=400, detail="Este item no es un accesorio de cueva.")

    # Verify player has item in inventory (pessimistic lock)
    inv = session.exec(
        select(PlayerInventory)
        .where(
            PlayerInventory.user_id == verified_user_id,
            PlayerInventory.item_id == item_id,
        )
        .order_by(PlayerInventory.is_shiny, PlayerInventory.is_first_edition)
        .with_for_update()
    ).first()
    if not inv or inv.quantity < 1:
        raise HTTPException(status_code=400, detail="No tienes este item en tu inventario.")

    # Deduct from inventory
    inv.quantity -= 1
    if inv.quantity == 0:
        session.delete(inv)
    else:
        session.add(inv)

    # Equip
    cave.append(item_id)
    axo.cave_items = cave
    session.add(axo)
    session.commit()

    return {
        "mensaje": f"Item equipado en la cueva de {axo.name}.",
        "cave_items": cave,
    }


def unequip_cave_item(axo_id: int, item_id: int, session: Session, verified_user_id: str) -> dict:
    """Removes a cave item from the axolotito's cave and returns it to the player's inventory."""
    axo = _get_axo_or_403(axo_id, session, verified_user_id)

    cave = list(axo.cave_items or [])
    if item_id not in cave:
        raise HTTPException(status_code=400, detail="Este item no está equipado.")

    cave.remove(item_id)
    axo.cave_items = cave
    session.add(axo)

    # Return item to inventory (pessimistic lock on existing row if present)
    inv = session.exec(
        select(PlayerInventory)
        .where(
            PlayerInventory.user_id == verified_user_id,
            PlayerInventory.item_id == item_id,
        )
        .with_for_update()
    ).first()
    if inv:
        inv.quantity += 1
        session.add(inv)
    else:
        session.add(PlayerInventory(user_id=verified_user_id, item_id=item_id, quantity=1))

    session.commit()

    return {"mensaje": "Item desequipado.", "cave_items": cave}


def _get_axo_or_403(axo_id: int, session: Session, verified_user_id: str) -> Axolotito:
    """Helper to fetch an Axolotito and validate ownership."""
    axo = session.get(Axolotito, axo_id)
    if not axo:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axo.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de este Axolotito.")
    return axo
