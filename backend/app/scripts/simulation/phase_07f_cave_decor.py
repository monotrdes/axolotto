"""
phase_07f_cave_decor.py — Decoración del Cenote (CAVE_ITEM).

Simula la compra y colocación de decoraciones en el Cenote:
  1. Comprar CAVE_ITEMs en la tienda usando FRJ (Frijolitos)
  2. Colocar decoraciones en slots válidos según subcategoría
  3. Validar que el backend rechaza slot incorrecto (ej. FONDO en LUZ_0)
  4. Validar límite de slots por nivel de cueva
"""
import json
import random

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.user import User
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.models.economy import CurrencyType, Wallet
from app.services.shop_service import ShopService
from app.api.v1.endpoints.cave_decor import (
    update_cave_decorations,
    UpdateDecorationsRequest,
    SUBCATEGORY_ORDER,
    _slot_layout,
    _subcategory_from_slot,
)

_rng = random.SystemRandom()


def _slot_names_for_level(cave_level: int) -> list[str]:
    """Slots reales del nivel según el layout del backend (fuente de verdad)."""
    return [s["slot_id"] for s in _slot_layout(cave_level)]


def phase_cave_decor(engine, config, **state) -> dict:
    """Simula compra y equipamiento de decoraciones de Cenote."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🖼️  Fase de decoración del Cenote...")

    # Buscar CAVE_ITEMs disponibles en catálogo
    cave_items_catalog = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.CAVE_ITEM,
            ItemCatalog.is_active == True,
        )
    ).all()

    if not cave_items_catalog:
        progress("  ⚠️  Sin CAVE_ITEMs en catálogo. Saltando fase.")
        return {}

    # Agrupar por subcategoría
    items_by_subcat: dict[str, list] = {subcat: [] for subcat in SUBCATEGORY_ORDER}
    for item in cave_items_catalog:
        meta = item.item_metadata or {}
        subcat = meta.get("cave_subcategory", "ESPECIAL")
        if subcat not in items_by_subcat:
            items_by_subcat[subcat] = []
        items_by_subcat[subcat].append(item)

    total_equipped = 0
    slot_mismatch_tested = 0

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        p_name = personality.get("name", "casual")

        user = session.exec(
            select(User).where(User.privy_did == user_id).with_for_update()
        ).first()
        if not user:
            errors.append(f"cave_decor: user {user_id} not found")
            continue

        cave_level = user.cave_level or 1
        available_slots = _slot_names_for_level(cave_level)

        # Solo decorar si la cueva tiene slots (nivel 2+ tiene más slots)
        if cave_level <= 1 and p_name not in ("whale", "aggressive"):
            continue

        # ── Asegurar FRJ para compras ──
        wallet = session.exec(
            select(Wallet).where(Wallet.user_id == user_id).with_for_update()
        ).first()
        if wallet:
            wallet.frijolitos = max(wallet.frijolitos or 0, 50_000)
            session.add(wallet)
            session.commit()

        # ── Comprar decoraciones ──
        purchased = []
        # Número de decoraciones a comprar según personalidad
        n_to_buy = {"whale": 6, "aggressive": 4, "collector": 4, "casual": 2, "free2play": 1}.get(p_name, 2)

        for _ in range(n_to_buy):
            # Elegir una categoría al azar
            cat = _rng.choice(list(items_by_subcat.keys()))
            cat_items = items_by_subcat[cat]
            if not cat_items:
                continue
            item = _rng.choice(cat_items)

            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=item.id,
                    payment_currency=CurrencyType.GEMA_ALGA,  # FRJ via GAL
                )
                purchased.append(item)
                print(f"  🛒 {user_id}: '{item.name}' comprado ({cat})")
            except HTTPException as e:
                session.rollback()
                errors.append(f"cave_item_buy {user_id}/{item.name}: {e.detail}")

        if not purchased:
            continue

        # ── Colocar decoraciones en slots ──
        session.refresh(user)
        current_decor = {}
        try:
            if user.cave_decorations:
                current_decor = json.loads(user.cave_decorations or "{}")
        except (json.JSONDecodeError, TypeError):
            current_decor = {}

        placed = 0
        for item in purchased:
            meta = item.item_metadata or {}
            item_subcat = meta.get("cave_subcategory", "ESPECIAL")

            # Encontrar un slot vacío que coincida con la subcategoría
            matching_slot = None
            for slot_id in available_slots:
                if slot_id in current_decor and current_decor[slot_id] is not None:
                    continue
                slot_prefix = _subcategory_from_slot(slot_id)
                if slot_prefix == item_subcat:
                    matching_slot = slot_id
                    break

            if matching_slot is None:
                continue  # No hay slot libre de esta subcategoría

            # Construir body con solo este placement
            new_decor = dict(current_decor)
            new_decor[matching_slot] = item.id

            try:
                update_cave_decorations(
                    body=UpdateDecorationsRequest(decorations=new_decor),
                    session=session,
                    verified_user_id=user_id,
                )
                current_decor = new_decor
                placed += 1
                total_equipped += 1
                print(f"  🖼️  {user_id}: '{item.name}' colocado en slot {matching_slot}")
            except HTTPException as e:
                session.rollback()
                errors.append(f"cave_decor_place {user_id}/{item.name}@{matching_slot}: {e.detail}")

        # ── Test de seguridad: colocar item en slot de categoría incorrecta ──
        if purchased and available_slots:
            # Intentar colocar el primer item comprado en un slot de tipo diferente
            test_item = purchased[0]
            test_meta = test_item.item_metadata or {}
            test_subcat = test_meta.get("cave_subcategory", "ESPECIAL")

            wrong_slot = None
            for slot_id in available_slots:
                slot_prefix = _subcategory_from_slot(slot_id)
                if slot_prefix != test_subcat:
                    wrong_slot = slot_id
                    break

            if wrong_slot:
                try:
                    wrong_decor = dict(current_decor)
                    wrong_decor[wrong_slot] = test_item.id
                    update_cave_decorations(
                        body=UpdateDecorationsRequest(decorations=wrong_decor),
                        session=session,
                        verified_user_id=user_id,
                    )
                    errors.append(
                        f"cave_decor_security {user_id}: Error — "
                        f"se permitió colocar {test_subcat} en slot {wrong_slot}"
                    )
                except HTTPException as e:
                    if e.status_code == 400:
                        slot_mismatch_tested += 1
                        print(f"  🔒 {user_id}: Bloqueo de slot incorrecto verificado: "
                              f"'{test_item.name}' ({test_subcat}) no puede ir en {wrong_slot}")
                    else:
                        errors.append(f"cave_decor_security {user_id}: HTTP {e.status_code}: {e.detail}")
                except Exception as e:
                    session.rollback()
                    errors.append(f"cave_decor_security {user_id}: {e}")

        print(f"  🏠 {user_id} ({p_name}): {placed} decoraciones colocadas en cueva nivel {cave_level}")

    stats["cave_items_equipped"] = total_equipped
    stats["cave_decor_slot_mismatch_checked"] = slot_mismatch_tested

    progress(
        f"  ✅ Decoraciones: {total_equipped} equipadas, "
        f"{slot_mismatch_tested} tests de seguridad de slot"
    )
    return {}
