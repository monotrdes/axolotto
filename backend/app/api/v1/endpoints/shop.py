import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_session
from app.models.economy import CurrencyType, TransactionType
from app.services.shop_service import ShopService
from app.services.bank_service import BankService
from app.services.drop_service import (
    _try_legendary_drop,
    _add_to_inventory,
    PROB_BOOSTER_FOIL_GASHAPON,
)
from app.services.capsule_service import (
    _roll_capsule,
    TIER_COSTS,
    TRIPLE_COST,
)
from app.services.forge_service import melt_card, forge_card
from app.services.vip_service import (
    get_vip_tiers as _get_vip_tiers,
    get_vip_stats as _get_vip_stats,
    get_vip_upgrade_preview as _get_vip_upgrade_preview,
)
from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity, CapsulaPity
from app.models.economy import TransactionLedger, Wallet
from app.models.user import User
from app.models.axolotito import Axolotito
from app.core.auth import get_verified_user_id

router = APIRouter()
_rng = random.SystemRandom()

# ── Pool del Gashapón (umbrales acumulados por rareza de accesorio) ────────────
GASHAPON_COMMON_THRESHOLDS = [
    (0.70, Rarity.COMMON),
    (0.95, Rarity.RARE),
    (1.00, Rarity.EPIC),
]
GASHAPON_PREMIUM_THRESHOLDS = [
    (0.45, Rarity.RARE),
    (0.90, Rarity.EPIC),
    (1.00, Rarity.LEGENDARY),
]


class BuyRequest(BaseModel):
    item_id: int
    payment_currency: CurrencyType


@router.get("/items")
def get_store_items(user_id: Optional[str] = None, session: Session = Depends(get_session)):
    """Muestra los ítems activos y calcula su stock vendido en tiempo real."""
    items = session.exec(select(ItemCatalog).where(ItemCatalog.is_active == True)).all()

    # Pre-compute nido status once for all egg items (avoids repeated queries)
    nido_status: dict | None = None
    if user_id:
        egg_inv_count = session.exec(
            select(func.sum(PlayerInventory.quantity))
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(PlayerInventory.user_id == user_id)
            .where(ItemCatalog.item_type == ItemType.EGG)
        ).one_or_none() or 0

        user_data = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user_data:
            from app.api.v1.endpoints.cave_expansion import CAVE_PASSIVE_BONUSES, _get_next_level_info
            bonus_slots = sum(
                CAVE_PASSIVE_BONUSES.get(lvl, {}).get("global_incubation_slot", 0)
                for lvl in range(1, user_data.cave_level + 1)
            )
            max_slots = user_data.cave_level + bonus_slots
            egg_inv_count = int(egg_inv_count)
            sin_nidos = egg_inv_count >= max_slots
            nido_status = {
                "sin_nidos": sin_nidos,
                "total_huevos": egg_inv_count,
                "max_nidos": max_slots,
                "nidos_libres": max(0, max_slots - egg_inv_count),
            }
            if sin_nidos:
                nido_status["next_level"] = _get_next_level_info(user_data.cave_level)

    resultado = []
    for item in items:
        if (item.item_type == ItemType.BOOSTER) or item.item_type == ItemType.EGG:
            total_sold = session.exec(
                select(func.count(TransactionLedger.id))
                .where(TransactionLedger.item_id == item.id)
            ).one_or_none() or 0
        else:
            total_sold = session.exec(
                select(func.sum(PlayerInventory.quantity)).where(PlayerInventory.item_id == item.id)
            ).one_or_none() or 0

        user_owned = 0
        if user_id:
            if item.item_type == ItemType.BOOSTER:
                user_owned = session.exec(
                    select(func.count(TransactionLedger.id))
                    .where(TransactionLedger.user_id == user_id)
                    .where(TransactionLedger.tx_type == TransactionType.BOOSTER_PURCHASE)
                ).one_or_none() or 0
            elif item.item_type == ItemType.EGG:
                total_eggs = session.exec(
                    select(func.sum(PlayerInventory.quantity))
                    .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                    .where(PlayerInventory.user_id == user_id)
                    .where(ItemCatalog.item_type == ItemType.EGG)
                ).one_or_none() or 0
                total_axolotitos = session.exec(
                    select(func.count(Axolotito.id))
                    .where(Axolotito.user_id == user_id)
                ).one_or_none() or 0
                user_owned = total_eggs + total_axolotitos
            else:
                user_owned = session.exec(
                    select(func.sum(PlayerInventory.quantity))
                    .where(PlayerInventory.user_id == user_id)
                    .where(PlayerInventory.item_id == item.id)
                ).one_or_none() or 0

        item_dict = item.model_dump()
        if item.name == "Booster Brillante (Foil)":
            now = datetime.utcnow()
            start_of_month = datetime(now.year, now.month, 1)
            monthly_sold = session.exec(
                select(func.count(TransactionLedger.id))
                .where(TransactionLedger.item_id == item.id)
                .where(TransactionLedger.created_at >= start_of_month)
            ).one_or_none() or 0
            total_sold = monthly_sold
            item_dict["max_supply"] = 100

        item_dict["total_sold"] = total_sold
        item_dict["user_owned"] = user_owned

        # Attach nido availability for egg items so the frontend can block purchase upfront
        if item.item_type == ItemType.EGG and nido_status is not None:
            item_dict["sin_nidos"] = nido_status["sin_nidos"]
            item_dict["max_nidos"] = nido_status["max_nidos"]
            item_dict["nidos_libres"] = nido_status["nidos_libres"]
            item_dict["total_huevos"] = nido_status["total_huevos"]
            if nido_status.get("next_level") is not None:
                item_dict["cave_next_level"] = nido_status["next_level"]

        resultado.append(item_dict)

    return resultado


@router.post("/buy")
def buy_item(
    request: BuyRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Compra un ítem usando Gemas de Alga o Axogemas."""
    return ShopService.buy_item(
        session=session,
        user_id=verified_user_id,
        item_id=request.item_id,
        payment_currency=request.payment_currency
    )


@router.get("/activity")
def get_recent_shop_activity(session: Session = Depends(get_session)):
    """Retorna las últimas 15 compras globales en la tienda hechas por cualquier usuario."""
    ledgers = session.exec(
        select(TransactionLedger)
        .where(
            (TransactionLedger.tx_type == TransactionType.BOOSTER_PURCHASE) |
            (
                (TransactionLedger.tx_type == TransactionType.MARKET_BUY) &
                (
                    TransactionLedger.description.contains("Huevo") |
                    TransactionLedger.description.contains("Webito") |
                    TransactionLedger.description.contains("Fase")
                )
            )
        )
        .order_by(TransactionLedger.created_at.desc())
        .limit(15)
    ).all()

    activity = []
    for ledger in ledgers:
        user = session.exec(select(User).where(User.privy_did == ledger.user_id)).first()
        activity.append({
            "id": ledger.id,
            "nickname": user.nickname if user and user.nickname else "Jugador Axolotto",
            "description": ledger.description or "Compra en Tienda",
            "amount": ledger.amount,
            "currency": ledger.currency,
            "created_at": ledger.created_at
        })
    return activity


@router.get("/cards")
def get_all_cards(session: Session = Depends(get_session)):
    """Devuelve el catálogo maestro de las 54 cartas de la Lotería para dibujar el álbum."""
    cards = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.CARD)
        .order_by(ItemCatalog.id)
    ).all()

    from app.services.rarity_service import get_card_dynamic_rarities
    dynamic_rarities = get_card_dynamic_rarities(session)

    response_cards = []
    for card in cards:
        card_data = card.model_dump()
        rarity_info = dynamic_rarities.get(card.id, {"dynamic_rarity": "Común", "circulation": 0})
        card_data["dynamic_rarity"] = rarity_info["dynamic_rarity"]
        card_data["circulation"] = rarity_info["circulation"]
        response_cards.append(card_data)

    return response_cards


class GashaponRollRequest(BaseModel):
    roll_type: str = "common"


@router.post("/gashapon/roll")
def roll_gashapon(
    request: GashaponRollRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Lanza el Gashapón de Axolotto consumiendo FRJ para obtener un accesorio o comida premium."""
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)

    cost = 1000.0 if request.roll_type == "common" else 2500.0
    if wallet.frijolitos < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo de FRJ insuficiente para lanzar el Gashapón (cuesta {cost} FRJ, tienes {wallet.frijolitos} FRJ)."
        )

    # ── 1. Pre-check drop legendario (Booster Foil) ────────────────────────────
    legendary = _try_legendary_drop(
        session, verified_user_id,
        p_foil=PROB_BOOSTER_FOIL_GASHAPON,
    )
    if legendary:
        wallet.frijolitos -= cost
        session.add(wallet)
        session.add(TransactionLedger(
            user_id=verified_user_id,
            amount=cost,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.MARKET_BUY,
            description=(
                f"Gashapón ({request.roll_type.upper()}) "
                f"★LEGENDARIO★: {legendary['item']['name']}"
            ),
        ))
        session.commit()
        return {
            **legendary,
            "roll_type": request.roll_type,
            "cost_frj": cost,
        }

    # ── 2. Roll normal: accesorio por rareza ──────────────────────────────────
    rand = _rng.random()
    thresholds = (
        GASHAPON_COMMON_THRESHOLDS
        if request.roll_type == "common"
        else GASHAPON_PREMIUM_THRESHOLDS
    )
    chosen_rarity = thresholds[-1][1]
    for threshold, rarity in thresholds:
        if rand < threshold:
            chosen_rarity = rarity
            break

    accessories = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.ACCESSORY)
        .where(ItemCatalog.rarity == chosen_rarity)
    ).all()
    if not accessories:
        accessories = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.ACCESSORY)
        ).all()
    if not accessories:
        raise HTTPException(
            status_code=404,
            detail="No hay accesorios sembrados en el catálogo de la tienda."
        )

    drop_item = _rng.choice(accessories)

    # ── 3. Cobrar FRJ y añadir al inventario ──────────────────────────────────
    wallet.frijolitos -= cost
    _add_to_inventory(session, verified_user_id, drop_item.id)

    session.add(wallet)
    session.add(TransactionLedger(
        user_id=verified_user_id,
        amount=cost,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=(
            f"Gashapón ({request.roll_type.upper()}) "
            f"usando FRJ: "
            f"{drop_item.name} [{chosen_rarity.value}]"
        ),
    ))
    session.commit()

    return {
        "is_legendary": False,
        "legendary_type": None,
        "mensaje": f"¡Lanzaste el Gashapón y obtuviste '{drop_item.name}'!",
        "item": drop_item,
        "rarity": chosen_rarity.value,
        "roll_type": request.roll_type,
        "cost_frj": cost,
    }


# ───────────────────────────────────────────────────────────────────────────────
#  SISTEMA DE CÁPSULAS SORPRESA (3 Tiers + Diaria + Triple)
# ───────────────────────────────────────────────────────────────────────────────

class CapsuleRollRequest(BaseModel):
    tier: str
    use_capsule: bool = False


class TripleSuerteRequest(BaseModel):
    pass


@router.get("/capsule/pity")
def get_capsule_pity(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Retorna los contadores de karma/pity por tier del Gashapón."""
    pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == verified_user_id)).first()
    return {
        "pity": {
            "bronce": pity.pity_cobre if pity else 0,
            "plata": pity.pity_plata if pity else 0,
            "oro": pity.pity_oro if pity else 0,
        },
    }


@router.get("/capsule/daily-status")
def get_daily_status(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    raise HTTPException(status_code=410, detail="Usa GET /api/v1/rewards/lunar/status")


@router.post("/capsule/daily-claim")
def claim_daily_capsule(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    raise HTTPException(status_code=410, detail="Usa POST /api/v1/rewards/lunar/claim")


@router.post("/capsule/roll")
def roll_capsule(
    request: CapsuleRollRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    tier = request.tier.lower()
    if tier not in TIER_COSTS:
        raise HTTPException(status_code=400, detail=f"Tier inválido. Usa: {list(TIER_COSTS.keys())}")

    cost = TIER_COSTS[tier]
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)

    if request.use_capsule:
        all_consumables = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CONSUMABLE)
        ).all()
        capsule_item = next(
            (c for c in all_consumables if (c.item_metadata or {}).get("capsule_tier") == tier),
            None
        )
        if not capsule_item:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró el ítem Cápsula {tier.capitalize()} en el catálogo."
            )
        inv_item = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == verified_user_id)
            .where(PlayerInventory.item_id == capsule_item.id)
            .with_for_update()
        ).first()
        if not inv_item or inv_item.quantity < 1:
            raise HTTPException(
                status_code=400,
                detail=f"No tienes Cápsula {tier.capitalize()} en tu inventario."
            )
        inv_item.quantity -= 1
        if inv_item.quantity <= 0:
            session.delete(inv_item)
        else:
            session.add(inv_item)
        cost = 0.0
    else:
        if wallet.frijolitos < cost:
            raise HTTPException(
                status_code=400,
                detail=f"FRJ insuficientes. Necesitas {cost} FRJ, tienes {wallet.frijolitos:.1f} FRJ.",
            )
        wallet.frijolitos -= cost
        session.add(wallet)

    result = _roll_capsule(tier, verified_user_id, session)
    session.commit()
    result["balance_after"] = wallet.frijolitos
    return result


@router.post("/capsule/triple-suerte")
def roll_triple_suerte(
    request: TripleSuerteRequest = TripleSuerteRequest(),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)

    if wallet.frijolitos < TRIPLE_COST:
        raise HTTPException(
            status_code=400,
            detail=f"FRJ insuficientes para Triple Suerte. Necesitas {TRIPLE_COST} FRJ, tienes {wallet.frijolitos:.1f} FRJ.",
        )
    wallet.frijolitos -= TRIPLE_COST
    session.add(wallet)

    results = [_roll_capsule(t, verified_user_id, session) for t in ("bronce", "plata", "oro")]
    session.commit()

    return {
        "results": results,
        "total_cost": TRIPLE_COST,
        "saved": 400,
        "balance_after": wallet.frijolitos,
    }


@router.get("/capsule/feed")
def get_capsule_feed(session: Session = Depends(get_session)):
    """Últimos 15 rolls globales de cápsulas — La Suertuda."""
    ledgers = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.description.startswith("Cápsula "))
        .order_by(TransactionLedger.created_at.desc())
        .limit(15)
    ).all()

    feed = []
    for ledger in ledgers:
        user = session.exec(select(User).where(User.privy_did == ledger.user_id)).first()
        nickname = (user.nickname if user and user.nickname else None) or (
            ledger.user_id[:8] + "..." if ledger.user_id else "Jugador"
        )
        desc = ledger.description or ""
        parts = desc.split(": ", 1)
        tier_label = parts[0].replace("Cápsula ", "").lower() if parts else "?"
        outcome_text = parts[1] if len(parts) > 1 else desc
        feed.append({
            "nickname": nickname,
            "outcome_text": outcome_text,
            "tier": tier_label,
            "created_at": ledger.created_at,
        })
    return feed


# ─── VIP TIERS (público, sin auth) ───────────────────────────────────────────

@router.get("/vip/tiers")
def get_vip_tiers():
    """
    Devuelve la lista de tiers VIP con los valores económicos canónicos.
    Público — no requiere autenticación. Fuente única: VIP_CONFIG en config.py.
    """
    return _get_vip_tiers()


# ─── VIP STATS (público, sin auth) ───────────────────────────────────────────

@router.get("/vip/stats")
def get_vip_stats(session: Session = Depends(get_session)):
    """
    Devuelve el número de usuarios con membresía VIP activa (vip_expires_at > now()).
    Público — no requiere autenticación.
    """
    return _get_vip_stats(session)


# ─── VIP UPGRADE PREVIEW ──────────────────────────────────────────────────────

@router.get("/vip/upgrade-preview")
def vip_upgrade_preview(
    target_tier: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Calcula el precio de upgrade VIP con crédito proporcional, sin cobrar nada."""
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return _get_vip_upgrade_preview(session, user, target_tier)


class OpenBoosterRequest(BaseModel):
    item_id: int


@router.post("/booster/open")
def open_booster(
    request: OpenBoosterRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Abre un sobre sellado de manera diferida en la mochila del usuario."""
    return ShopService.open_booster(session, verified_user_id, request.item_id)


class MeltCardRequest(BaseModel):
    card_id: int
    is_first_edition: bool = False


class ForgeCardRequest(BaseModel):
    target_card_id: int


@router.post("/melter/melt")
def melt_card_endpoint(
    request: MeltCardRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Fundir 5 copias de una carta de rareza común, rara o épica para obtener fragmentos y una carta aleatoria superior."""
    return melt_card(session, verified_user_id, request.card_id, request.is_first_edition)


@router.post("/melter/forge")
def forge_card_endpoint(
    request: ForgeCardRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Forjar una carta específica consumiendo fragmentos de su rareza y GAL."""
    return forge_card(session, verified_user_id, request.target_card_id)
