from __future__ import annotations
"""
cave_decor.py — Decoraciones del Cenote.

Rutas — Decoración:
  GET  /api/v1/cave/decorations           — Estado actual de decoraciones
  GET  /api/v1/cave/decorations/inventory — Inventario de CAVE_ITEM del usuario
  POST /api/v1/cave/decorations/update    — Colocar/quitar decoraciones

"""

import json
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from sqlmodel import Session, select, func

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.axolotito import Axolotito
from app.models.items import (
    ItemCatalog,
    ItemType,
    PlayerInventory,
    Rarity,
)
from app.models.user import User
from app.api.v1.endpoints.cave_expansion import CAVE_LEVEL_DEFINITIONS

router = APIRouter()
_rng = random.SystemRandom()

# ── Slot naming: {subcategory}_{index}  e.g. "AMBIENTE_0", "FONDO_2" ──────
# Taxonomía del diorama (plan task-84): la zona central de la cueva tiene
# slots tipados — ambiente/color, iluminación, mesa de juego, mantel,
# sillas, decoración de fondo e items especiales (rocola, vasijas...).
VALID_SUBCATEGORIES = {"AMBIENTE", "LUZ", "MESA", "MANTEL", "SILLAS", "FONDO", "ESPECIAL"}

# Orden canónico de render/listado.
SUBCATEGORY_ORDER = ("AMBIENTE", "LUZ", "MESA", "MANTEL", "SILLAS", "FONDO", "ESPECIAL")


# ── Request / Response schemas ─────────────────────────────────────────

class UpdateDecorationsRequest(BaseModel):
    decorations: Dict[str, Optional[int]]  # slot_id -> item_id (null = remove)


# ── Helpers para decoración ────────────────────────────────────────────

def _get_decor_slots(cave_level: int) -> int:
    """Obtiene la cantidad de slots de decoración para un nivel de cueva dado."""
    if cave_level <= 1:
        return 2
    level_def = CAVE_LEVEL_DEFINITIONS.get(cave_level, {})
    return level_def.get("decor_slots", 2)


def _slot_layout(cave_level: int) -> list[dict]:
    """
    Layout de slots de decoración por nivel de cueva — fuente de verdad para
    backend y diorama. Los slots únicos (AMBIENTE/LUZ/MESA/MANTEL/SILLAS) son
    skins intercambiables; FONDO y ESPECIAL crecen con el nivel. La suma por
    nivel cuadra exactamente con `decor_slots` de CAVE_LEVEL_DEFINITIONS.

    MESA/SILLAS requieren mesa de juego (has_table, nivel 3+); MANTEL además
    requiere nivel 4+ (y una MESA equipada, validado en /decorations/update).
    """
    level = max(1, min(cave_level, max(CAVE_LEVEL_DEFINITIONS)))
    has_table = level > 1 and CAVE_LEVEL_DEFINITIONS.get(level, {}).get("has_table", False)
    counts = {
        "AMBIENTE": 1,
        "LUZ": 1 if level >= 2 else 0,
        "MESA": 1 if has_table else 0,
        "MANTEL": 1 if has_table and level >= 4 else 0,
        "SILLAS": 1 if has_table else 0,
        "FONDO": 1 if level == 1 else (2 if level <= 4 else level - 2),
        "ESPECIAL": max(0, level - 3),
    }
    return [
        {"slot_id": f"{subcat}_{i}", "subcategory": subcat}
        for subcat in SUBCATEGORY_ORDER
        for i in range(counts[subcat])
    ]


def _subcategory_from_slot(slot_id: str) -> str:
    """Extrae la subcategoría del slot_id, e.g. 'FLOOR_0' -> 'FLOOR'."""
    if "_" not in slot_id:
        return ""
    return slot_id.split("_")[0].upper()


def _return_item_to_inventory(session, user_id: str, item_id: int) -> None:
    """Devuelve 1 unidad de un item al inventario del usuario (SELECT FOR UPDATE)."""
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == item_id)
        .with_for_update()
    ).first()
    if inv:
        inv.quantity += 1
        session.add(inv)
    else:
        session.add(PlayerInventory(user_id=user_id, item_id=item_id, quantity=1))


def _build_decorations_response(user: User, session) -> dict:
    """
    Construye la respuesta completa de estado de decoraciones.
    Retorna decorations, max_slots, used_slots, bonuses calculados con topes.
    """
    decorations_raw = user.cave_decorations or "{}"
    try:
        decorations = json.loads(decorations_raw)
    except (json.JSONDecodeError, TypeError):
        decorations = {}
    if not isinstance(decorations, dict):
        decorations = {}

    layout = _slot_layout(user.cave_level)
    valid_slot_ids = {s["slot_id"] for s in layout}
    # Descartar en lectura slots con prefijo viejo/desconocido (migración de
    # la taxonomía FLOOR/WALL/WATER/SPECIAL — no había catálogo sembrado).
    decorations = {k: v for k, v in decorations.items() if k in valid_slot_ids}

    placed_decorations = {k: v for k, v in decorations.items() if v is not None}
    used_slots = len(placed_decorations)
    max_slots = len(layout)

    focus_total = 0.0
    staking_total = 0.0
    incubation_total = 0.0
    items_detail: Dict[str, dict] = {}

    for slot_id, item_id in placed_decorations.items():
        catalog = session.get(ItemCatalog, item_id)
        if not catalog:
            continue
        meta = catalog.item_metadata or {}
        focus_total += float(meta.get("focus_bonus", 0.0))
        staking_total += float(meta.get("staking_bonus", 0.0))
        incubation_total += float(meta.get("incubation_boost", 0.0))
        # Detalle para que el diorama pueda dibujar el item equipado.
        items_detail[str(item_id)] = {
            "id": catalog.id,
            "name": catalog.name,
            "rarity": catalog.rarity,
            "subcategory": meta.get("cave_subcategory", ""),
            "emoji": meta.get("emoji", "🏺"),
            "color": meta.get("color"),
            "focus_bonus": float(meta.get("focus_bonus", 0.0)),
            "staking_bonus": float(meta.get("staking_bonus", 0.0)),
            "incubation_boost": float(meta.get("incubation_boost", 0.0)),
        }

    # Contar axolotitos para el cap de staking
    active_axolotitos = session.exec(
        select(func.count(Axolotito.id))
        .where(Axolotito.user_id == user.privy_did)
    ).one_or_none() or 0

    # Topes variables
    focus_cap = min(0.50, 0.10 + user.cave_level * 0.05)
    staking_cap = min(0.28, active_axolotitos * 0.035)

    return {
        "decorations": decorations,
        "slots": layout,
        "items": items_detail,
        "max_slots": max_slots,
        "used_slots": used_slots,
        "bonuses": {
            "focus_recovery_boost": round(min(focus_total, focus_cap), 4),
            "frj_staking_multiplier": round(min(staking_total, staking_cap), 4),
            "incubation_boost_total": round(incubation_total, 4),
        },
        "caps": {
            "focus_cap": round(focus_cap, 4),
            "staking_cap": round(staking_cap, 4),
            "active_axolotitos": active_axolotitos,
        },
    }


# ── GET /decorations ───────────────────────────────────────────────────

@router.get("/decorations")
def get_cave_decorations(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Devuelve el estado actual de las decoraciones del Cenote.

    Incluye el mapa de decoraciones (slot_id -> item_id), slots usados/máximos,
    y los bonos activos calculados con sus topes aplicados según el nivel de
    la cueva y la cantidad de axolotitos del usuario.
    """
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return _build_decorations_response(user, session)


# ── GET /decorations/inventory ─────────────────────────────────────────

@router.get("/decorations/inventory")
def get_cave_decorations_inventory(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Devuelve el inventario de CAVE_ITEM del usuario, agrupado por subcategoría
    (AMBIENTE, LUZ, MESA, MANTEL, SILLAS, FONDO, ESPECIAL).
    """
    results = session.exec(
        select(PlayerInventory, ItemCatalog)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.quantity > 0)
        .where(ItemCatalog.item_type == ItemType.CAVE_ITEM)
    ).all()

    items_by_category: Dict[str, list] = {subcat: [] for subcat in SUBCATEGORY_ORDER}

    for inv, cat in results:
        meta = cat.item_metadata or {}
        subcat = meta.get("cave_subcategory", "ESPECIAL")
        if subcat not in items_by_category:
            items_by_category[subcat] = []
        items_by_category[subcat].append({
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "rarity": cat.rarity,
            "quantity": inv.quantity,
            "price_gal": cat.price_gal,
            "item_metadata": meta,
        })

    # Ordenar por rarity (legendary primero) y luego por nombre
    rarity_order = {"legendary": 0, "epic": 1, "rare": 2, "common": 3}
    for subcat in items_by_category:
        items_by_category[subcat].sort(
            key=lambda x: (rarity_order.get(x["rarity"], 99), x["name"])
        )

    return {"items_by_category": items_by_category}


# ── POST /decorations/update ───────────────────────────────────────────

@router.post("/decorations/update")
def update_cave_decorations(
    body: UpdateDecorationsRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Actualiza las decoraciones del Cenote.

    Body: { "decorations": { "AMBIENTE_0": 123, "FONDO_0": null, ... } }
      — es el ESTADO DESEADO COMPLETO: los slots ausentes del body se tratan
        como removidos (el item vuelve al inventario).
      - item_id = int: colocar ese item en el slot
      - item_id = null: remover el item del slot

    Validaciones:
      - slot_id debe existir en el layout del nivel actual (_slot_layout)
      - Subcategoría del slot debe coincidir con cave_subcategory del item
      - Item debe ser CAVE_ITEM y existir en el inventario del usuario
      - MANTEL requiere una MESA equipada en el estado resultante

    Usa SELECT FOR UPDATE en inventario para prevenir condiciones de carrera.
    """
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id).with_for_update()
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    new_decorations = body.decorations or {}

    # ── 1. Validar slots contra el layout del nivel ──
    layout = _slot_layout(user.cave_level)
    valid_slot_ids = {s["slot_id"] for s in layout}
    for slot_id in new_decorations:
        if slot_id not in valid_slot_ids:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Slot '{slot_id}' no disponible en tu cueva (nivel {user.cave_level}). "
                    f"Expande la cueva para desbloquear más slots."
                ),
            )

    # Estado resultante (solo colocaciones efectivas).
    final_state = {k: v for k, v in new_decorations.items() if v is not None}

    # MANTEL solo tiene sentido sobre una mesa equipada.
    mantel_placed = any(_subcategory_from_slot(s) == "MANTEL" for s in final_state)
    mesa_placed = any(_subcategory_from_slot(s) == "MESA" for s in final_state)
    if mantel_placed and not mesa_placed:
        raise HTTPException(
            status_code=400,
            detail="Necesitas una mesa equipada para ponerle mantel.",
        )

    # ── 2. Cargar estado actual ──
    try:
        current_decorations = json.loads(user.cave_decorations or "{}")
    except (json.JSONDecodeError, TypeError):
        current_decorations = {}
    if not isinstance(current_decorations, dict):
        current_decorations = {}

    # ── 3. Clasificar operaciones ──
    removals: list[int] = []
    placements: list[tuple[str, int]] = []

    # Slots equipados hoy que el body ya no menciona → devolver al inventario
    # (antes se perdían silenciosamente al sobreescribir el JSON).
    for slot_id, old_item_id in current_decorations.items():
        if old_item_id is not None and slot_id not in new_decorations:
            removals.append(old_item_id)

    for slot_id, new_item_id in new_decorations.items():
        slot_prefix = _subcategory_from_slot(slot_id)
        old_item_id = current_decorations.get(slot_id)

        if new_item_id == old_item_id:
            continue

        if old_item_id is not None:
            removals.append(old_item_id)

        if new_item_id is not None:
            catalog = session.get(ItemCatalog, new_item_id)
            if not catalog:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item con id {new_item_id} no encontrado en el catálogo.",
                )
            if catalog.item_type != ItemType.CAVE_ITEM:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{catalog.name}' no es un artículo de decoración (CAVE_ITEM).",
                )

            meta = catalog.item_metadata or {}
            item_subcat = meta.get("cave_subcategory", "")
            if slot_prefix != item_subcat:
                raise HTTPException(
                    status_code=400,
                    detail=f"Slot '{slot_id}' requiere tipo {slot_prefix}, pero '{catalog.name}' es {item_subcat}.",
                )

            placements.append((slot_id, new_item_id))

    # ── 4. Ejecutar removals (devolver al inventario) ──
    for item_id in removals:
        _return_item_to_inventory(session, verified_user_id, item_id)

    # ── 5. Ejecutar placements (ordenado por item_id para evitar deadlocks) ──
    placements.sort(key=lambda x: x[1])

    for slot_id, item_id in placements:
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == verified_user_id)
            .where(PlayerInventory.item_id == item_id)
            .with_for_update()
        ).first()
        if not inv or inv.quantity < 1:
            catalog = session.get(ItemCatalog, item_id)
            item_name = catalog.name if catalog else f"#{item_id}"
            raise HTTPException(
                status_code=400,
                detail=f"No tienes '{item_name}' en tu inventario.",
            )
        inv.quantity -= 1
        if inv.quantity > 0:
            session.add(inv)
        else:
            session.delete(inv)

    # ── 6. Guardar nuevo estado (solo slots ocupados) ──
    user.cave_decorations = json.dumps(final_state)
    session.add(user)
    session.commit()
    session.refresh(user)

    return _build_decorations_response(user, session)

