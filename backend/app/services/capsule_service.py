from __future__ import annotations
"""
Capsule Service — logica de capsulas sorpresa (roll + daily claim + pity).

Contiene las constantes de tier, pools, pity, y las funciones _roll_capsule
y _daily_can_claim que antes vivian en shop.py.
"""
import random
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, func
from app.models.items import (
    ItemCatalog, PlayerInventory, ItemType, Rarity,
    CapsulaDailyFree, CapsulaPity,
)
from app.models.economy import TransactionLedger, TransactionType, CurrencyType, Wallet
from app.services.bank_service import BankService
from app.services.drop_service import (
    _try_legendary_drop,
    _try_tabla_forjada_drop,
    _get_foil_booster,
    _add_to_inventory,
)

_rng = random.SystemRandom()

# ── Constantes de capsulas ────────────────────────────────────────────────────

TIER_COSTS = {"bronce": 1500.0, "plata": 5000.0, "oro": 20000.0}
TRIPLE_COST = 22500.0  # (1500+5000+20000)*0.85 = 22525, redondeado a 22500 FRJ

# Cápsulas — solo Booster Foil como premio legendario (Webito Astral ahora se obtiene desbloqueando la Cueva 6)
CAPSULE_LEGENDARY_PROBS: dict[str, dict[str, float]] = {
    "bronce": {"booster_foil": 0.002},
    "plata":  {"booster_foil": 0.005},
    "oro":    {"booster_foil": 0.010},
}

# Cuando el pool normal da "sobre" en una cápsula, hay una probabilidad
# secundaria de que ese sobre sea FOIL en lugar de un booster normal:
FOIL_FROM_SOBRE: dict[str, float] = {
    "bronce": 0.05,  # 5%
    "plata":  0.12,  # 12%
    "oro":    0.22,  # 22%
}

# ── Breakpoints acumulados de cápsulas: (umbral, outcome_type) ────────────────
# ⚠️  SIN WEBITOS — Los huevos (EGG) se compran en tienda o se obtienen expandiendo la Cueva.
#     El Webito Astral se obtiene desbloqueando la Cueva nivel 6.
TIER_POOLS: dict = {
    "bronce": [(0.45, "gal"), (0.80, "carta"), (0.92, "accesorio"), (0.97, "sobre"), (1.0, "carta_rara")],
    "plata":  [(0.20, "gal"), (0.68, "carta"), (0.85, "accesorio"), (0.93, "sobre"), (1.0, "carta_rara")],
    "oro":    [(0.05, "gal"), (0.55, "carta"), (0.75, "accesorio"), (0.85, "sobre"), (1.0, "carta_rara")],
}
FRJ_RANGES = {"bronce": (50, 150), "plata": (200, 600), "oro": (500, 3000)}
PITY_LIMITS = {"bronce": 10, "plata": 5, "oro": 3}

# Rareza mínima de carta/accesorio según tier
TIER_CARD_RARITIES: dict = {
    "bronce": [Rarity.COMMON, Rarity.RARE],
    "plata":  [Rarity.RARE, Rarity.EPIC],
    "oro":    [Rarity.EPIC, Rarity.LEGENDARY],
}
TIER_ACC_RARITIES: dict = {
    "bronce": [Rarity.COMMON],
    "plata":  [Rarity.RARE],
    "oro":    [Rarity.EPIC, Rarity.LEGENDARY],
}

# Mapa de campo pity en BD (los nombres de columna usan "cobre" históricamente)
PITY_FIELD_MAP = {"bronce": "pity_cobre", "plata": "pity_plata", "oro": "pity_oro"}


# ── Roll de cápsula ────────────────────────────────────────────────────────────

def _roll_capsule(tier: str, user_id: str, session: Session) -> dict:
    """
    Helper central: ejecuta un roll de cápsula y devuelve el resultado sin commit.

    Flujo:
      1. Pre-check legendario (Booster Foil / Tabla Forjada) — si sale, retorna inmediato.
      2. Pity check — si se alcanzó el límite, fuerza axolotito.
      3. Pool normal según tier.
      4. Para outcome "sobre": check secundario de Foil.
    """
    pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user_id)).first()
    if not pity:
        pity = CapsulaPity(user_id=user_id)
        session.add(pity)

    pity_field = PITY_FIELD_MAP[tier]
    pity_count = getattr(pity, pity_field, 0)

    # ── 2. Pity / Pool normal ─────────────────────────────────────────────────
    if pity_count >= PITY_LIMITS.get(tier, 999):
        outcome_type = "carta_rara"
    else:
        # ── 1. Pre-check drops legendarios ────────────────────────────────────────
        leg_probs = CAPSULE_LEGENDARY_PROBS.get(tier, {})
        legendary = _try_legendary_drop(
            session, user_id,
            p_foil=leg_probs.get("booster_foil", 0.0),
        )
        if legendary:
            setattr(pity, pity_field, 0)
            session.add(pity)
            session.add(TransactionLedger(
                user_id=user_id,
                amount=TIER_COSTS.get(tier, 0),
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.MARKET_BUY,
                description=(
                    f"Cápsula {tier.capitalize()} ★LEGENDARIO★: "
                    f"{legendary['item']['name']}"
                ),
                item_id=legendary['item']['id']
            ))
            return {
                **legendary,
                "tier": tier,
                "outcome_type": legendary["legendary_type"],
                "pity_after": 0,
            }
        tabla = _try_tabla_forjada_drop(session, user_id, tier)
        if tabla:
            setattr(pity, pity_field, 0)
            session.add(pity)
            session.add(TransactionLedger(
                user_id=user_id,
                amount=TIER_COSTS.get(tier, 0),
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.MARKET_BUY,
                description=f"Cápsula {tier.capitalize()} ★TABLA FORJADA★: {tabla['board']['name']}",
            ))
            return {
                **tabla,
                "tier": tier,
                "outcome_type": "tabla_forjada",
                "pity_after": 0,
            }
        rand = _rng.random()
        outcome_type = "carta_rara"  # fallback (último tier en el pool)
        for threshold, otype in TIER_POOLS[tier]:
            if rand < threshold:
                outcome_type = otype
                break

    item = None
    gal_rewarded = None
    is_foil_sobre = False

    if outcome_type == "gal":
        lo, hi = FRJ_RANGES[tier]
        gal_rewarded = round(_rng.uniform(lo, hi), 1)
        wallet = BankService.get_or_create_wallet(session, user_id)
        wallet.frijolitos += gal_rewarded
        session.add(wallet)
        outcome_text = f"{gal_rewarded} FRJ"

    elif outcome_type == "carta":
        rarities = TIER_CARD_RARITIES[tier]
        cards = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.CARD)
            .where(ItemCatalog.rarity.in_(rarities))
        ).all()
        if not cards:
            cards = session.exec(
                select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
            ).all()
        item = _rng.choice(cards) if cards else None
        if item:
            _add_to_inventory(session, user_id, item.id)
        outcome_text = item.name if item else "Carta"

    elif outcome_type == "accesorio":
        rarities = TIER_ACC_RARITIES[tier]
        accs = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.ACCESSORY)
            .where(ItemCatalog.rarity.in_(rarities))
        ).all()
        if not accs:
            accs = session.exec(
                select(ItemCatalog).where(ItemCatalog.item_type == ItemType.ACCESSORY)
            ).all()
        item = _rng.choice(accs) if accs else None
        if item:
            _add_to_inventory(session, user_id, item.id)
        outcome_text = item.name if item else "Accesorio"

    elif outcome_type == "sobre":
        foil_chance = FOIL_FROM_SOBRE.get(tier, 0.0)
        if _rng.random() < foil_chance:
            item = _get_foil_booster(session)
            is_foil_sobre = item is not None and (item.item_metadata or {}).get("is_foil", False)
        if not item:
            all_boosters = session.exec(
                select(ItemCatalog)
                .where(ItemCatalog.item_type == ItemType.BOOSTER)
                .where(ItemCatalog.is_active == True)
            ).all()
            normal_boosters = [
                b for b in all_boosters
                if not (b.item_metadata or {}).get("is_foil")
            ]
            pool = normal_boosters if normal_boosters else all_boosters
            item = _rng.choice(pool) if pool else None
        if item:
            _add_to_inventory(session, user_id, item.id)
        outcome_text = (
            f"Booster Foil ✨ {item.name}" if is_foil_sobre and item
            else (item.name if item else "Sobre")
        )

    elif outcome_type == "carta_rara":  # Carta de rareza elevada (reemplaza a Webitos)
        rarities = {
            "bronce": [Rarity.RARE, Rarity.EPIC],
            "plata":  [Rarity.EPIC, Rarity.LEGENDARY],
            "oro":    [Rarity.EPIC, Rarity.LEGENDARY],
        }.get(tier, [Rarity.RARE])
        rare_cards = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.CARD)
            .where(ItemCatalog.rarity.in_(rarities))
        ).all()
        if not rare_cards:
            rare_cards = session.exec(
                select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
            ).all()
        item = _rng.choice(rare_cards) if rare_cards else None
        if item:
            _add_to_inventory(session, user_id, item.id)
        outcome_text = f"Carta {item.rarity.value.upper() if item else 'Rara'}: {item.name if item else '?'}"
        setattr(pity, pity_field, 0)
        session.add(pity)

    else:
        # Fallback genérico — no debería llegar aquí, pero por si acaso
        outcome_text = "Premio misterioso"

    if outcome_type != "carta_rara":
        setattr(pity, pity_field, pity_count + 1)
        session.add(pity)

    session.add(TransactionLedger(
        user_id=user_id,
        amount=TIER_COSTS.get(tier, 0),
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Cápsula {tier.capitalize()}: {outcome_text}",
        item_id=item.id if item else None
    ))

    return {
        "is_legendary": False,
        "legendary_type": None,
        "tier": tier,
        "outcome_type": outcome_type,
        "item": item.model_dump() if item else None,
        "gal_rewarded": gal_rewarded,
        "is_foil_sobre": is_foil_sobre,
        "mensaje": f"¡Abriste una Cápsula {tier.capitalize()} y obtuviste {outcome_text}!",
        "pity_after": getattr(pity, pity_field, 0),
    }


def _daily_can_claim(user_id: str, session: Session) -> tuple[bool, int, datetime | None]:
    """Devuelve (can_claim, consecutive_days, next_claim_at_utc)."""
    mx_tz = timezone(timedelta(hours=-6))
    now_mx = datetime.now(timezone.utc).astimezone(mx_tz)
    today_mx = now_mx.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_mx = today_mx - timedelta(days=1)

    last = session.exec(
        select(CapsulaDailyFree)
        .where(CapsulaDailyFree.user_id == user_id)
        .order_by(CapsulaDailyFree.claimed_at.desc())
    ).first()

    if last is None:
        return True, 0, None

    claimed_utc = last.claimed_at.replace(tzinfo=timezone.utc) if last.claimed_at.tzinfo is None else last.claimed_at
    claimed_mx = claimed_utc.astimezone(mx_tz)
    claimed_day = claimed_mx.replace(hour=0, minute=0, second=0, microsecond=0)

    if claimed_day >= today_mx:
        next_claim_mx = today_mx + timedelta(days=1)
        next_claim_utc = next_claim_mx.astimezone(timezone.utc).replace(tzinfo=None)
        return False, last.consecutive_days, next_claim_utc

    if claimed_day == yesterday_mx:
        streak = last.consecutive_days + 1
    else:
        streak = 1

    return True, streak, None
