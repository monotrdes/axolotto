"""
Reciclon Service — logica de reciclaje de cartas duplicadas
y canje de tickets por cartas especificas.

Reemplaza el antiguo sistema de fundicion (melt) y forja (forge).
Sin costo de FRJ/AXF. Sin fragmentos. Sin aleatoriedad.
"""
import json
import logging
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, ItemType, Rarity, PlayerInventory
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger, ChainOutbox
from app.models.user import User
from app.core.config import settings
from app.core.product_policy import require_feature
from app.services.bank_service import BankService

logger = logging.getLogger("reciclon_service")

# Ticket values: 5:1 ratio (recycle 5 of rarity X → buy 1 of same rarity)
# Configurable via settings / env vars.
RECYCLE_TICKETS = {
    Rarity.COMMON: settings.RECYCLE_TICKETS_COMMON,
    Rarity.RARE: settings.RECYCLE_TICKETS_RARE,
    Rarity.EPIC: settings.RECYCLE_TICKETS_EPIC,
    Rarity.LEGENDARY: settings.RECYCLE_TICKETS_LEGENDARY,
}

REDEEM_COST = {
    Rarity.COMMON: settings.REDEEM_COST_COMMON,
    Rarity.RARE: settings.REDEEM_COST_RARE,
    Rarity.EPIC: settings.REDEEM_COST_EPIC,
    Rarity.LEGENDARY: settings.REDEEM_COST_LEGENDARY,
}


def recycle_cards(session: Session, user_id: str, items: list[dict]) -> dict:
    """Reciclar cartas duplicadas para obtener Tickets de Reciclon.

    Args:
        session: DB session
        user_id: Privy DID del jugador
        items: [{"card_id": int, "quantity": int, "is_first_edition": bool}, ...]

    Returns:
        {"success": True, "tickets_earned": int, "total_tickets": int,
         "cards_recycled": int, "details": [...]}
    """
    require_feature(settings.ENABLE_RECICLON, "reciclon")
    # 0. Verificar tutorial completado
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if user:
        from app.core.auth import require_tutorial
        require_tutorial(user)

    if not items:
        raise HTTPException(status_code=400, detail="Debes seleccionar al menos una carta para reciclar.")

    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    total_tickets_earned = 0
    total_cards_recycled = 0
    details = []

    for item in items:
        card_id = item["card_id"]
        quantity = item.get("quantity", 1)
        is_first_edition = item.get("is_first_edition", False)

        if quantity <= 0:
            continue

        # 1. Validar carta
        card = session.get(ItemCatalog, card_id)
        if not card or card.item_type != ItemType.CARD:
            raise HTTPException(
                status_code=404,
                detail=f"La carta id={card_id} no existe en el catalogo."
            )

        rarity = card.rarity
        if rarity not in RECYCLE_TICKETS:
            raise HTTPException(
                status_code=400,
                detail=f"La rareza {rarity.value} no es reciclable."
            )

        # 2. Verificar inventario con lock
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == card_id)
            .where(PlayerInventory.is_first_edition == is_first_edition)
            .where(PlayerInventory.is_shiny == False)
            .with_for_update()
        ).first()

        if not inv or inv.quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Copias insuficientes de '{card.name}' — "
                    f"necesitas {quantity}, tienes {inv.quantity if inv else 0}."
                )
            )

        # 3. Calcular tickets
        tickets_per_card = RECYCLE_TICKETS[rarity]
        tickets_earned = tickets_per_card * quantity

        # 4. Deducir inventario
        inv.quantity -= quantity
        if inv.quantity <= 0:
            session.delete(inv)
        else:
            session.add(inv)

        # 5. Sumar tickets
        wallet.tickets_reciclon += tickets_earned
        total_tickets_earned += tickets_earned
        total_cards_recycled += quantity

        # 6. Ledger
        ledger = TransactionLedger(
            user_id=user_id,
            amount=tickets_earned,
            currency=CurrencyType.TICKET_RECICLON,
            tx_type=TransactionType.RECICLON_RECYCLE,
            description=(
                f"Reciclaje de {quantity}x {card.name} (id={card_id}, "
                f"{rarity.value}, 1raEd={is_first_edition}) → +{tickets_earned} tickets"
            ),
            item_id=card_id
        )
        session.add(ledger)

        details.append({
            "card_id": card_id,
            "card_name": card.name,
            "rarity": rarity.value,
            "quantity": quantity,
            "tickets_earned": tickets_earned,
        })

    # On-chain: encolar transferencia al vault (feature-flagged, async)
    if settings.RECICLON_ONCHAIN_ENABLED and settings.RECICLON_VAULT_ADDRESS:
        player_wallet = user.wallet_address if user else None
        if player_wallet:
            for item in items:
                session.add(ChainOutbox(
                    user_id=user_id,
                    operation="transfer_card_to_vault",
                    payload_json=json.dumps({
                        "from_address": player_wallet,
                        "card_id": item["card_id"],
                        "quantity": item.get("quantity", 1),
                    }),
                ))

    session.add(wallet)
    session.commit()

    return {
        "success": True,
        "tickets_earned": total_tickets_earned,
        "total_tickets": wallet.tickets_reciclon,
        "cards_recycled": total_cards_recycled,
        "details": details,
    }


def redeem_ticket(session: Session, user_id: str, target_card_id: int) -> dict:
    """Canjear Tickets de Reciclon por una carta especifica del catalogo.

    Args:
        session: DB session
        user_id: Privy DID del jugador
        target_card_id: ID de la carta a canjear

    Returns:
        {"success": True, "redeemed_card": {...}, "tickets_spent": int,
         "total_tickets": int}
    """
    require_feature(settings.ENABLE_RECICLON, "reciclon")
    # 0. Verificar tutorial completado
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if user:
        from app.core.auth import require_tutorial
        require_tutorial(user)

    # 1. Validar carta
    card = session.get(ItemCatalog, target_card_id)
    if not card or card.item_type != ItemType.CARD:
        raise HTTPException(
            status_code=404,
            detail="La carta no existe en el catalogo."
        )

    rarity = card.rarity
    if rarity not in REDEEM_COST:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede canjear una carta de rareza {rarity.value}."
        )

    ticket_cost = REDEEM_COST[rarity]

    # 2. Verificar tickets con lock
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.tickets_reciclon < ticket_cost:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tickets insuficientes. Cuesta {ticket_cost} tickets "
                f"({rarity.value}), tienes {wallet.tickets_reciclon}."
            )
        )

    # 3. Deducir tickets
    wallet.tickets_reciclon -= ticket_cost

    # 4. Añadir carta al inventario
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == target_card_id)
        .where(PlayerInventory.is_first_edition == False)
        .where(PlayerInventory.is_shiny == False)
    ).first()

    if inv:
        inv.quantity += 1
        session.add(inv)
    else:
        inv = PlayerInventory(
            user_id=user_id,
            item_id=target_card_id,
            quantity=1,
            is_first_edition=False,
            is_shiny=False
        )
        session.add(inv)

    # 5. Ledger
    ledger = TransactionLedger(
        user_id=user_id,
        amount=-ticket_cost,
        currency=CurrencyType.TICKET_RECICLON,
        tx_type=TransactionType.RECICLON_REDEEM,
        description=(
            f"Canje de carta id={target_card_id} "
            f"({card.name}, {rarity.value}) → -{ticket_cost} tickets"
        ),
        item_id=target_card_id
    )
    session.add(ledger)

    # On-chain: mintear la carta canjeada (feature-flagged, async)
    if settings.RECICLON_ONCHAIN_ENABLED and settings.RECICLON_VAULT_ADDRESS:
        player_wallet = user.wallet_address if user else None
        if player_wallet:
            session.add(ChainOutbox(
                user_id=user_id,
                operation="mint_cards",
                payload_json=json.dumps({
                    "to_address": player_wallet,
                    "card_ids": [target_card_id],
                    "amounts": [1],
                }),
            ))

    session.add(wallet)
    session.commit()

    return {
        "success": True,
        "redeemed_card": {
            "id": card.id,
            "name": card.name,
            "rarity": card.rarity.value,
        },
        "tickets_spent": ticket_cost,
        "total_tickets": wallet.tickets_reciclon,
    }
