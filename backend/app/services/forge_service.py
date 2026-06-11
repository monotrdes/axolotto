"""
Forge Service — logica de fundicion (melt) y forja (forge) de cartas.

Contiene la logica de negocio de los endpoints /melter/melt y /melter/forge
que antes vivia directamente en shop.py.
"""
import random
import logging
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.items import ItemCatalog, ItemType, Rarity, PlayerInventory
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.user import User

logger = logging.getLogger("forge_service")
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.core.config import settings, frj_to_internal, frj_to_display

_rng = random.SystemRandom()


def melt_card(session: Session, user_id: str, card_id: int, is_first_edition: bool = False) -> dict:
    """Fundir 5 copias de una carta de rareza común, rara o épica para obtener fragmentos y una carta aleatoria superior."""
    # 1. Obtener la carta
    card = session.get(ItemCatalog, card_id)
    if not card or card.item_type != ItemType.CARD:
        raise HTTPException(status_code=404, detail="La carta no existe en el catálogo.")

    rarity = card.rarity
    if rarity not in [Rarity.COMMON, Rarity.RARE, Rarity.EPIC]:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden fundir cartas comunes, raras o épicas."
        )

    # 2. Verificar inventario
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == card_id)
        .where(PlayerInventory.is_first_edition == is_first_edition)
        .where(PlayerInventory.is_shiny == False)
        .with_for_update()
    ).first()

    if not inv or inv.quantity < 5:
        raise HTTPException(
            status_code=400,
            detail=f"No tienes suficientes copias (necesitas al menos 5, tienes {inv.quantity if inv else 0})."
        )

    # 3. Costo y wallet
    price = 0.0
    frag_field = ""
    next_rarity = None

    if rarity == Rarity.COMMON:
        price = 100.0
        frag_field = "frag_comun"
        next_rarity = Rarity.RARE
    elif rarity == Rarity.RARE:
        price = 250.0
        frag_field = "frag_raro"
        next_rarity = Rarity.EPIC
    elif rarity == Rarity.EPIC:
        price = 1500.0
        frag_field = "frag_epico"
        next_rarity = Rarity.LEGENDARY

    price_internal = frj_to_internal(price)
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < price_internal:
        raise HTTPException(
            status_code=400,
            detail=f"Frijolitos insuficientes. Cuesta {price} FRJ, tienes {frj_to_display(wallet.frijolitos):.1f} FRJ."
        )

    # 4. Obtener cartas de la rareza superior
    next_cards = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.CARD)
        .where(ItemCatalog.rarity == next_rarity)
        .where(ItemCatalog.is_active == True)
    ).all()

    if not next_cards:
        raise HTTPException(
            status_code=400,
            detail=f"No hay cartas disponibles de la rareza superior ({next_rarity.value})."
        )

    # 5. Ejecutar cobro y deducción
    wallet.frijolitos -= price_internal

    current_frags = getattr(wallet, frag_field) + 10
    setattr(wallet, frag_field, current_frags)

    inv.quantity -= 5
    if inv.quantity <= 0:
        session.delete(inv)
    else:
        session.add(inv)

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if user and user.wallet_address and settings.GEMA_ALGA_ADDRESS:
        try:
            Web3Service.burn_frj(user.wallet_address, price_internal)
        except Exception as e:
            logger.error("Error al quemar GAL on-chain en fundición: %s", e)

    # 6. Elegir carta superior aleatoria
    chosen_card = _rng.choice(next_cards)

    new_inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == chosen_card.id)
        .where(PlayerInventory.is_first_edition == False)
        .where(PlayerInventory.is_shiny == False)
    ).first()

    if new_inv:
        new_inv.quantity += 1
    else:
        new_inv = PlayerInventory(
            user_id=user_id,
            item_id=chosen_card.id,
            quantity=1,
            is_first_edition=False,
            is_shiny=False
        )
    session.add(new_inv)

    ledger = TransactionLedger(
        user_id=user_id,
        amount=price_internal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.CRAFTING,
        description=f"Fundición de 5 cartas id={card_id} -> Carta superior id={chosen_card.id}",
        item_id=chosen_card.id
    )
    session.add(ledger)
    session.add(wallet)
    session.commit()

    return {
        "success": True,
        "new_card": {
            "id": chosen_card.id,
            "name": chosen_card.name,
            "rarity": chosen_card.rarity.value,
        },
        "balance_gal": frj_to_display(wallet.frijolitos),
        "fragments": {
            "frag_comun": wallet.frag_comun,
            "frag_raro": wallet.frag_raro,
            "frag_epico": wallet.frag_epico,
            "frag_legendario": wallet.frag_legendario
        }
    }


def forge_card(session: Session, user_id: str, target_card_id: int) -> dict:
    """Forjar una carta específica consumiendo fragmentos de su rareza y GAL."""
    card = session.get(ItemCatalog, target_card_id)
    if not card or card.item_type != ItemType.CARD:
        raise HTTPException(status_code=404, detail="La carta no existe en el catálogo.")

    rarity = card.rarity
    frag_cost = 0
    gal_cost = 0.0
    frag_field = ""

    if rarity == Rarity.COMMON:
        frag_cost = 50
        gal_cost = 100.0
        frag_field = "frag_comun"
    elif rarity == Rarity.RARE:
        frag_cost = 100
        gal_cost = 500.0
        frag_field = "frag_raro"
    elif rarity == Rarity.EPIC:
        frag_cost = 250
        gal_cost = 1000.0
        frag_field = "frag_epico"
    elif rarity == Rarity.LEGENDARY:
        frag_cost = 500
        gal_cost = 3000.0
        frag_field = "frag_legendario"

    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)

    user_frags = getattr(wallet, frag_field)
    if user_frags < frag_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Fragmentos insuficientes. Cuesta {frag_cost} fragmentos ({rarity.value}), tienes {user_frags}."
        )

    gal_cost_internal = frj_to_internal(gal_cost)
    if wallet.frijolitos < gal_cost_internal:
        raise HTTPException(
            status_code=400,
            detail=f"Frijolitos insuficientes. Cuesta {gal_cost} FRJ, tienes {frj_to_display(wallet.frijolitos):.1f} FRJ."
        )

    setattr(wallet, frag_field, user_frags - frag_cost)
    wallet.frijolitos -= gal_cost_internal

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if user and user.wallet_address and settings.GEMA_ALGA_ADDRESS:
        try:
            Web3Service.burn_frj(user.wallet_address, gal_cost_internal)
        except Exception as e:
            print(f"⚠️ Error al quemar FRJ on-chain en forja: {e}")

    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == target_card_id)
        .where(PlayerInventory.is_first_edition == False)
        .where(PlayerInventory.is_shiny == False)
    ).first()

    if inv:
        inv.quantity += 1
    else:
        inv = PlayerInventory(
            user_id=user_id,
            item_id=target_card_id,
            quantity=1,
            is_first_edition=False,
            is_shiny=False
        )
    session.add(inv)

    ledger = TransactionLedger(
        user_id=user_id,
        amount=gal_cost_internal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.CRAFTING,
        description=f"Forja de carta id={target_card_id} (Rarity: {rarity.value}) usando {frag_cost} fragmentos",
        item_id=target_card_id
    )
    session.add(ledger)
    session.add(wallet)
    session.commit()

    return {
        "success": True,
        "forged_card": {
            "id": card.id,
            "name": card.name,
            "rarity": card.rarity.value,
        },
        "balance_gal": frj_to_display(wallet.frijolitos),
        "fragments": {
            "frag_comun": wallet.frag_comun,
            "frag_raro": wallet.frag_raro,
            "frag_epico": wallet.frag_epico,
            "frag_legendario": wallet.frag_legendario
        }
    }
