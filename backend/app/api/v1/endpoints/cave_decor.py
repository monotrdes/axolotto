from __future__ import annotations
"""
cave_decor.py — Decoraciones y minijuegos del Cenote.

Rutas — Decoración:
  GET  /api/v1/cave/decorations           — Estado actual de decoraciones
  GET  /api/v1/cave/decorations/inventory — Inventario de CAVE_ITEM del usuario
  POST /api/v1/cave/decorations/update    — Colocar/quitar decoraciones

Rutas — Minijuegos:
  POST /api/v1/cave/minigames/wishing-well
  POST /api/v1/cave/minigames/arcade/play
  GET  /api/v1/cave/minigames/arcade/leaderboard
"""

import json
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from sqlmodel import Session, select, func

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.axolotito import Axolotito
from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
    Wallet,
)
from app.models.items import (
    ArcadeLeaderboard,
    ItemCatalog,
    ItemType,
    PlayerInventory,
    Rarity,
)
from app.models.user import User
from app.services.bank_service import BankService
from app.services.drop_service import _add_to_inventory
from app.api.v1.endpoints.cave_expansion import CAVE_LEVEL_DEFINITIONS

router = APIRouter()
_rng = random.SystemRandom()

# ── Slot naming: {subcategory}_{index}  e.g. "FLOOR_0", "WALL_1" ──────
VALID_SUBCATEGORIES = {"FLOOR", "WALL", "WATER", "SPECIAL"}

WISHING_WELL_COST_FRJ = 20
ARCADE_PLAY_COST_AXF = 1


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

    placed_decorations = {k: v for k, v in decorations.items() if v is not None}
    used_slots = len(placed_decorations)
    max_slots = _get_decor_slots(user.cave_level)

    focus_total = 0.0
    staking_total = 0.0
    incubation_total = 0.0

    for slot_id, item_id in placed_decorations.items():
        catalog = session.get(ItemCatalog, item_id)
        if not catalog:
            continue
        meta = catalog.item_metadata or {}
        focus_total += float(meta.get("focus_bonus", 0.0))
        staking_total += float(meta.get("staking_bonus", 0.0))
        incubation_total += float(meta.get("incubation_boost", 0.0))

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
    (FLOOR, WALL, WATER, SPECIAL).
    """
    results = session.exec(
        select(PlayerInventory, ItemCatalog)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.quantity > 0)
        .where(ItemCatalog.item_type == ItemType.CAVE_ITEM)
    ).all()

    items_by_category: Dict[str, list] = {
        "FLOOR": [],
        "WALL": [],
        "WATER": [],
        "SPECIAL": [],
    }

    for inv, cat in results:
        meta = cat.item_metadata or {}
        subcat = meta.get("cave_subcategory", "SPECIAL")
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

    Body: { "decorations": { "FLOOR_0": 123, "WALL_0": null, ... } }
      - item_id = int: colocar ese item en el slot
      - item_id = null: remover el item del slot

    Validaciones:
      - Prefijo del slot (FLOOR/WALL/WATER/SPECIAL) debe coincidir con cave_subcategory del item
      - Item debe ser CAVE_ITEM y existir en el inventario del usuario
      - Total items colocados <= decor_slots del nivel actual

    Usa SELECT FOR UPDATE en inventario para prevenir condiciones de carrera.
    """
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id).with_for_update()
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    new_decorations = body.decorations or {}

    # ── 1. Validar límite de slots ──
    max_slots = _get_decor_slots(user.cave_level)
    placed_count = sum(1 for v in new_decorations.values() if v is not None)
    if placed_count > max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de {max_slots} decoraciones excedido. Tienes {placed_count} items colocados.",
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

    for slot_id, new_item_id in new_decorations.items():
        slot_prefix = _subcategory_from_slot(slot_id)
        if not slot_prefix:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de slot inválido: '{slot_id}'. Debe ser 'SUBCATEGORIA_INDICE'.",
            )
        if slot_prefix not in VALID_SUBCATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Prefijo de slot inválido: '{slot_prefix}'. Debe ser FLOOR, WALL, WATER o SPECIAL.",
            )

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

    # ── 6. Guardar nuevo estado ──
    user.cave_decorations = json.dumps(new_decorations)
    session.add(user)
    session.commit()
    session.refresh(user)

    return _build_decorations_response(user, session)


# ═══════════════════════════════════════════════════════════════════════
# MINIJUEGOS (existente)
# ═══════════════════════════════════════════════════════════════════════


# ── POST /minigames/wishing-well ──────────────────────────────────────────────

@router.post("/minigames/wishing-well")
def play_wishing_well(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Lanza una moneda al pozo de los deseos.

    Cuesta 20 FRJ.
    Resultados:
      - perfect (5%):   recuperas 30 FRJ + un CAVE_ITEM común aleatorio
      - good    (15%):  recuperas 15 FRJ
      - okay    (30%):  recuperas  5 FRJ
      - miss    (50%):  nada
    """
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    if wallet.frijolitos < WISHING_WELL_COST_FRJ:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Saldo insuficiente. El pozo de los deseos cuesta "
                f"{WISHING_WELL_COST_FRJ} FRJ y tienes {int(wallet.frijolitos)} FRJ."
            ),
        )

    # Deducir coste
    wallet.frijolitos -= WISHING_WELL_COST_FRJ
    session.add(wallet)

    # Determinar resultado
    roll = _rng.random()
    if roll < 0.05:
        outcome = "perfect"
        frj_won = 30
    elif roll < 0.20:
        outcome = "good"
        frj_won = 15
    elif roll < 0.50:
        outcome = "okay"
        frj_won = 5
    else:
        outcome = "miss"
        frj_won = 0

    # Creditar FRJ ganados
    item_won = None
    if frj_won > 0:
        wallet.frijolitos += frj_won

    # Si es perfect: otorgar un CAVE_ITEM común aleatorio
    if outcome == "perfect":
        cave_items = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.CAVE_ITEM)
            .where(ItemCatalog.rarity == Rarity.COMMON)
            .where(ItemCatalog.is_active == True)
        ).all()
        if cave_items:
            chosen_item = _rng.choice(cave_items)
            _add_to_inventory(session, verified_user_id, chosen_item.id)
            item_won = {
                "id": chosen_item.id,
                "name": chosen_item.name,
                "rarity": chosen_item.rarity,
                "description": chosen_item.description,
            }

    # Registrar en TransactionLedger
    session.add(TransactionLedger(
        user_id=verified_user_id,
        amount=float(WISHING_WELL_COST_FRJ),
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.WISHING_WELL,
        description=(
            f"Pozo de los deseos — resultado: {outcome}, "
            f"FRJ gastados: {WISHING_WELL_COST_FRJ}, FRJ ganados: {frj_won}"
            + (f", item: {item_won['name']}" if item_won else "")
        ),
        item_id=item_won["id"] if item_won else None,
    ))

    session.commit()

    return {
        "outcome": outcome,
        "frj_spent": WISHING_WELL_COST_FRJ,
        "frj_won": frj_won,
        "item_won": item_won,
        "net_frj": frj_won - WISHING_WELL_COST_FRJ,
    }


# ── POST /minigames/arcade/play ───────────────────────────────────────────────

@router.post("/minigames/arcade/play")
def play_arcade(
    body: dict,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Juega una partida de arcade en el Cenote.

    Cuesta 1 AXF.  El jugador envía su puntuación `score`.
    Se registra en el leaderboard global de arcade y se devuelve
    el ranking actual.
    """
    score = body.get("score", 0)
    if not isinstance(score, int) or score < 0:
        raise HTTPException(status_code=400, detail="El campo 'score' debe ser un entero >= 0.")

    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    if wallet.axofichas < ARCADE_PLAY_COST_AXF:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Saldo insuficiente. Jugar al arcade cuesta "
                f"{ARCADE_PLAY_COST_AXF} AXF y tienes {wallet.axofichas} AXF."
            ),
        )

    # Deducir coste
    wallet.axofichas -= ARCADE_PLAY_COST_AXF
    session.add(wallet)

    # Obtener cave_name del usuario
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()

    # Insertar nuevo registro en el leaderboard
    leaderboard_entry = ArcadeLeaderboard(
        user_id=verified_user_id,
        cave_name=user.cave_name if user else None,
        score=score,
        played_at=datetime.utcnow(),
    )
    session.add(leaderboard_entry)

    # Personal best: max score del usuario
    personal_best = session.exec(
        select(func.max(ArcadeLeaderboard.score))
        .where(ArcadeLeaderboard.user_id == verified_user_id)
    ).one_or_none() or 0
    if personal_best is None:
        personal_best = score

    # Total de jugadores únicos
    total_players = session.exec(
        select(func.count(func.distinct(ArcadeLeaderboard.user_id)))
    ).one_or_none() or 0

    # Rank global: cuántos jugadores tienen score ESTRICTAMENTE mayor
    higher_count = session.exec(
        select(func.count(func.distinct(ArcadeLeaderboard.user_id)))
        .where(ArcadeLeaderboard.score > score)
    ).one_or_none() or 0
    rank = higher_count + 1

    # Registrar ledger
    session.add(TransactionLedger(
        user_id=verified_user_id,
        amount=float(ARCADE_PLAY_COST_AXF),
        currency=CurrencyType.AXOGEMA,
        tx_type=TransactionType.ARCADE_PLAY,
        description=(
            f"Arcade del Cenote — score: {score}, "
            f"personal_best: {personal_best}, rank: {rank}"
        ),
    ))

    session.commit()

    return {
        "score": score,
        "axf_spent": ARCADE_PLAY_COST_AXF,
        "personal_best": int(personal_best) if personal_best else score,
        "rank": rank,
        "total_players": int(total_players) if total_players else 1,
    }


# ── GET /minigames/arcade/leaderboard ─────────────────────────────────────────

@router.get("/minigames/arcade/leaderboard")
def get_arcade_leaderboard(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Devuelve el top 20 global del arcade del Cenote, más el mejor score
    del usuario autenticado (incluso si no está en el top 20).
    """
    # Top 20: scored best score per user, ordered by highest score DESC, then by earliest played_at for ties
    # Subquery: max score per user
    top_scores_query = (
        select(
            ArcadeLeaderboard.user_id,
            ArcadeLeaderboard.cave_name,
            func.max(ArcadeLeaderboard.score).label("max_score"),
            func.min(ArcadeLeaderboard.played_at).label("first_played"),
        )
        .group_by(ArcadeLeaderboard.user_id, ArcadeLeaderboard.cave_name)
        .order_by(func.max(ArcadeLeaderboard.score).desc(), func.min(ArcadeLeaderboard.played_at).asc())
        .limit(20)
    )
    top_results = session.exec(top_scores_query).all()

    leaderboard = []
    for i, row in enumerate(top_results):
        leaderboard.append({
            "rank": i + 1,
            "user_id": row.user_id,
            "cave_name": row.cave_name,
            "score": int(row.max_score),
            "played_at": row.first_played.isoformat() if row.first_played else None,
        })

    # My best score
    my_best = session.exec(
        select(func.max(ArcadeLeaderboard.score))
        .where(ArcadeLeaderboard.user_id == verified_user_id)
    ).one_or_none() or 0

    my_best_obj = None
    if my_best and int(my_best) > 0:
        my_best_obj = {
            "user_id": verified_user_id,
            "score": int(my_best),
        }

    return {
        "leaderboard": leaderboard,
        "my_best": my_best_obj,
    }
