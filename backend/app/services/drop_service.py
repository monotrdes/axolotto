from __future__ import annotations
"""
Drop Service — legendario / foil / tabla forjada / helpers de catálogo.

Contiene la lógica de "pre-check" de drops legendarios que se evalúa
ANTES del pool normal en Gashapón y Cápsulas.
"""
import random
from sqlmodel import Session, select, func
from app.models.items import ItemCatalog, PlayerInventory, ItemType
from app.models.board import PlayerBoard
from app.models.user import User

_rng = random.SystemRandom()

# ── Probabilidades de premios legendarios ─────────────────────────────────────

# Gashapón (ambas variantes, misma prob — solo Booster Foil):
PROB_BOOSTER_FOIL_GASHAPON = 0.005   # 0.50 %

PROB_TABLA_FORJADA_ORO = 0.03   # 3% chance in bola de oro capsule


# ── Helpers de inventario ─────────────────────────────────────────────────────

def _add_to_inventory(session: Session, user_id: str, item_id: int) -> None:
    """Adds one unit of `item_id` to the user's inventory (creates row if missing)."""
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == item_id)
    ).first()
    if inv:
        inv.quantity += 1
        session.add(inv)
    else:
        session.add(PlayerInventory(user_id=user_id, item_id=item_id, quantity=1))


def _get_astral_egg(session: Session) -> ItemCatalog | None:
    """
    Busca el Webito Astral en el catálogo.
    Orden: nombre contiene 'astral' → metadata is_astral=True → cualquier huevo activo.
    """
    astral = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.EGG)
        .where(ItemCatalog.name.ilike("%astral%"))
        .where(ItemCatalog.is_active == True)
    ).first()
    if astral:
        return astral
    eggs = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.EGG)
        .where(ItemCatalog.is_active == True)
    ).all()
    for egg in eggs:
        if (egg.item_metadata or {}).get("is_astral"):
            return egg
    return eggs[0] if eggs else None


def _get_foil_booster(session: Session) -> ItemCatalog | None:
    """
    Busca el Booster Foil activo en el catálogo.
    Orden: metadata is_foil=True → nombre contiene 'foil' / 'brillante' → cualquier booster activo.
    """
    boosters = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.BOOSTER)
        .where(ItemCatalog.is_active == True)
    ).all()
    for b in boosters:
        if (b.item_metadata or {}).get("is_foil"):
            return b
    for b in boosters:
        if any(kw in b.name.lower() for kw in ("foil", "brillante", "shiny")):
            return b
    return boosters[0] if boosters else None


# ── Drops legendarios ─────────────────────────────────────────────────────────

def _try_legendary_drop(
    session: Session,
    user_id: str,
    p_foil: float,
) -> dict | None:
    """
    Pre-check de drop legendario: Booster Foil.
    Si ocurre un drop, añade el ítem SELLADO al inventario y retorna un dict de
    resultado con `is_legendary=True` y `legendary_type`.
    Retorna None si no hubo drop legendario (continúa con pool normal).
    """
    rand = _rng.random()

    if rand < p_foil:
        item = _get_foil_booster(session)
        if item:
            _add_to_inventory(session, user_id, item.id)
            return {
                "is_legendary": True,
                "legendary_type": "booster_foil",
                "item": item.model_dump(),
                "gal_rewarded": None,
                "mensaje": (
                    "✨ ¡¡BOOSTER BRILLANTE!! Un sobre Foil se materializó en tu mochila. "
                    "Ábrelo cuando quieras. (0.5 % de probabilidad)"
                ),
            }

    return None   # sin drop legendario


def _try_tabla_forjada_drop(session: Session, user_id: str, tier: str) -> dict | None:
    """Attempt to award a Tabla Forjada from the retired NPC pool. Only for 'oro' tier."""
    if tier != "oro":
        return None
    if _rng.random() >= PROB_TABLA_FORJADA_ORO:
        return None
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        return None
    max_slots = user.unlocked_board_slots + user.vip_bonus_table_slots
    current_boards = session.exec(
        select(func.count(PlayerBoard.id))
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).one()
    if current_boards >= max_slots:
        return None
    board = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.is_npc_pool == True)
        .where(PlayerBoard.npc_retired == True)
        .order_by(PlayerBoard.created_at)
        .with_for_update(skip_locked=True)
    ).first()
    if not board:
        return None
    board.user_id = user_id
    board.is_npc_pool = False
    board.npc_retired = False
    session.add(board)
    return {
        "is_legendary": True,
        "legendary_type": "tabla_forjada",
        "board": {
            "id": board.id,
            "name": board.name,
            "level": board.level,
            "xp": board.xp,
            "games_played": board.games_played,
            "games_won": board.games_won,
            "origin_story": board.origin_story,
            "card_ids": board.card_ids,
        },
        "gal_rewarded": None,
        "mensaje": (
            f"TABLA FORJADA!! Has recibido '{board.name}'. "
            f"{board.origin_story or ''} Solo obtenible con bola de oro."
        ),
    }
