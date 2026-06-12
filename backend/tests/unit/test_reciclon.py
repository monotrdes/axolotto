import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlmodel import select

from app.models.economy import CurrencyType, TransactionLedger, Wallet
from app.models.items import ItemCatalog, ItemType, PlayerInventory, Rarity
from app.api.v1.endpoints.shop import (
    recycle_cards_endpoint as recycle_cards,
    redeem_tickets_endpoint as redeem_tickets,
    RecycleCardsRequest, RecycleItem, RedeemTicketsRequest,
)
from tests.conftest import make_user, make_wallet, make_item


@pytest.fixture(autouse=True)
def mock_web3(monkeypatch):
    """Mock Web3Service to prevent real blockchain calls during tests."""
    monkeypatch.setattr(
        "app.services.web3_service.Web3Service.burn_frj",
        MagicMock(return_value=None),
    )


def test_recycle_batch_success(session):
    """Recycle several cards of different rarities in a single batch call."""
    user = make_user(session, privy_did="did:privy:reciclon_user")
    make_wallet(session, user.privy_did, gemas_alga=0.0)

    common_card = make_item(session, "El Gallo", ItemType.CARD, rarity=Rarity.COMMON)
    rare_card = make_item(session, "La Sirena", ItemType.CARD, rarity=Rarity.RARE)

    # Seed inventory: 3 commons, 2 rares
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=3,
        is_first_edition=False, is_shiny=False
    ))
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=rare_card.id, quantity=2,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    # Recycle 2 commons + 1 rare
    req = RecycleCardsRequest(items=[
        RecycleItem(card_id=common_card.id, quantity=2),
        RecycleItem(card_id=rare_card.id, quantity=1),
    ])
    res = recycle_cards(request=req, session=session, verified_user_id=user.privy_did)

    assert res["success"] is True
    # 2 commons × 3 = 6 + 1 rare × 9 = 9 → 15 total
    assert res["tickets_earned"] == 15
    assert res["total_tickets"] == 15
    assert res["cards_recycled"] == 3
    assert len(res["details"]) == 2

    # Verify inventory
    inv_common = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv_common.quantity == 1  # 3 → 1 left

    inv_rare = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == rare_card.id)
    ).first()
    assert inv_rare.quantity == 1  # 2 → 1 left

    # Verify wallet
    wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
    assert wallet.tickets_reciclon == 15

    # Verify ledgers
    ledgers = session.exec(
        select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
    ).all()
    assert len(ledgers) == 2
    assert all(lg.tx_type.value == "reciclon_recycle" for lg in ledgers)
    assert all(lg.currency == CurrencyType.TICKET_RECICLON for lg in ledgers)


def test_recycle_clears_inventory_when_all_consumed(session):
    """When all copies are recycled, the inventory row should be deleted."""
    user = make_user(session, privy_did="did:privy:reciclon_clear")
    make_wallet(session, user.privy_did)

    common_card = make_item(session, "El Tambor", ItemType.CARD, rarity=Rarity.COMMON)
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=5,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    # Recycle all 5
    req = RecycleCardsRequest(items=[
        RecycleItem(card_id=common_card.id, quantity=5),
    ])
    res = recycle_cards(request=req, session=session, verified_user_id=user.privy_did)

    assert res["tickets_earned"] == 15  # 5 × 3
    assert res["total_tickets"] == 15

    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv is None  # Row deleted


def test_recycle_insufficient_copies(session):
    """Reject when trying to recycle more copies than owned."""
    user = make_user(session, privy_did="did:privy:reciclon_low")
    make_wallet(session, user.privy_did)

    common_card = make_item(session, "El Catrin", ItemType.CARD, rarity=Rarity.COMMON)
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=2,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    req = RecycleCardsRequest(items=[
        RecycleItem(card_id=common_card.id, quantity=5),
    ])
    with pytest.raises(HTTPException) as exc:
        recycle_cards(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "Copias insuficientes" in exc.value.detail


def test_recycle_empty_items(session):
    """Reject empty items list."""
    user = make_user(session, privy_did="did:privy:reciclon_empty")
    make_wallet(session, user.privy_did)
    session.commit()

    req = RecycleCardsRequest(items=[])
    with pytest.raises(HTTPException) as exc:
        recycle_cards(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "al menos una carta" in exc.value.detail.lower()


def test_redeem_success(session):
    """Redeem tickets for a specific card."""
    user = make_user(session, privy_did="did:privy:redeem_user")
    wallet = make_wallet(session, user.privy_did)
    wallet.tickets_reciclon = 15
    session.add(wallet)

    common_card = make_item(session, "El Sol", ItemType.CARD, rarity=Rarity.COMMON)
    session.commit()

    req = RedeemTicketsRequest(target_card_id=common_card.id)
    res = redeem_tickets(request=req, session=session, verified_user_id=user.privy_did)

    assert res["success"] is True
    assert res["redeemed_card"]["id"] == common_card.id
    assert res["tickets_spent"] == 15
    assert res["total_tickets"] == 0

    # Verify inventory
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv is not None
    assert inv.quantity == 1

    # Verify ledger
    ledger = session.exec(
        select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
    ).first()
    assert ledger is not None
    assert ledger.amount == -15  # negative → spent
    assert ledger.currency == CurrencyType.TICKET_RECICLON
    assert ledger.tx_type.value == "reciclon_redeem"


def test_redeem_insufficient_tickets(session):
    """Reject when not enough tickets."""
    user = make_user(session, privy_did="did:privy:redeem_low")
    wallet = make_wallet(session, user.privy_did)
    wallet.tickets_reciclon = 10
    session.add(wallet)

    rare_card = make_item(session, "La Rosa", ItemType.CARD, rarity=Rarity.RARE)
    session.commit()

    req = RedeemTicketsRequest(target_card_id=rare_card.id)
    with pytest.raises(HTTPException) as exc:
        redeem_tickets(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "Tickets insuficientes" in exc.value.detail


def test_redeem_stacks_existing_inventory(session):
    """When redeeming a card the user already owns, stack it."""
    user = make_user(session, privy_did="did:privy:redeem_stack")
    wallet = make_wallet(session, user.privy_did)
    wallet.tickets_reciclon = 30
    session.add(wallet)

    common_card = make_item(session, "La Luna", ItemType.CARD, rarity=Rarity.COMMON)
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=1,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    req = RedeemTicketsRequest(target_card_id=common_card.id)
    res = redeem_tickets(request=req, session=session, verified_user_id=user.privy_did)

    assert res["success"] is True
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv.quantity == 2  # Stacked


def test_full_cycle_recycle_and_redeem(session):
    """End-to-end: recycle cards → earn tickets → redeem a specific card."""
    user = make_user(session, privy_did="did:privy:fullcycle")
    make_wallet(session, user.privy_did)

    # Create 5 commons and 1 rare (target to redeem)
    common_card = make_item(session, "El Mundo", ItemType.CARD, rarity=Rarity.COMMON)
    rare_card = make_item(session, "El Apache", ItemType.CARD, rarity=Rarity.RARE)

    # Seed 5 common duplicates
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=5,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    # 1. Recycle all 5 commons → 15 tickets
    req_recycle = RecycleCardsRequest(items=[
        RecycleItem(card_id=common_card.id, quantity=5),
    ])
    res_recycle = recycle_cards(
        request=req_recycle, session=session, verified_user_id=user.privy_did
    )
    assert res_recycle["tickets_earned"] == 15
    assert res_recycle["total_tickets"] == 15

    # 2. Redeem rare card (cost 45) — should FAIL with only 15 tickets
    req_redeem_fail = RedeemTicketsRequest(target_card_id=rare_card.id)
    with pytest.raises(HTTPException) as exc:
        redeem_tickets(
            request=req_redeem_fail, session=session,
            verified_user_id=user.privy_did
        )
    assert exc.value.status_code == 400
    assert "Tickets insuficientes" in exc.value.detail

    # 3. Redeem common card (cost 15) — should SUCCEED
    req_redeem_ok = RedeemTicketsRequest(target_card_id=common_card.id)
    res_redeem = redeem_tickets(
        request=req_redeem_ok, session=session,
        verified_user_id=user.privy_did
    )
    assert res_redeem["success"] is True
    assert res_redeem["total_tickets"] == 0

    # 4. Verify final inventory: 1 copy of common_card (we just redeemed it)
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv is not None
    assert inv.quantity == 1


def test_fragments_untouched_by_reciclon(session):
    """Old fragment fields are not modified by recycle or redeem operations."""
    user = make_user(session, privy_did="did:privy:frags_untouched")
    wallet = make_wallet(session, user.privy_did)
    wallet.frag_comun = 42
    wallet.frag_raro = 7
    session.add(wallet)

    common_card = make_item(session, "El Pescado", ItemType.CARD, rarity=Rarity.COMMON)
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=5,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    # Recycle
    req = RecycleCardsRequest(items=[
        RecycleItem(card_id=common_card.id, quantity=5),
    ])
    recycle_cards(request=req, session=session, verified_user_id=user.privy_did)

    wallet_after = session.exec(
        select(Wallet).where(Wallet.user_id == user.privy_did)
    ).first()
    assert wallet_after.frag_comun == 42  # Untouched
    assert wallet_after.frag_raro == 7    # Untouched
    assert wallet_after.tickets_reciclon == 15

    # Redeem
    wallet_after.tickets_reciclon = 15
    session.add(wallet_after)
    session.commit()

    req2 = RedeemTicketsRequest(target_card_id=common_card.id)
    redeem_tickets(request=req2, session=session, verified_user_id=user.privy_did)

    wallet_final = session.exec(
        select(Wallet).where(Wallet.user_id == user.privy_did)
    ).first()
    assert wallet_final.frag_comun == 42  # Still untouched
    assert wallet_final.frag_raro == 7    # Still untouched
