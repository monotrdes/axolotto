"""
test_escrow_market.py — Tianguis P2P con escrow: listings, checkout y cuarentena.

Cubre el ciclo de vida de EscrowListing (Parte II E1.3 del plan económico)
con la pasarela fiat simulada y la blockchain en modo mock.
"""
import json
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings, AXF_MXN_CENTS
from app.models.axolotito import Axolotito
from app.models.economy import ChainOutbox
from app.models.market_escrow import (
    EarnedBalanceLock, EarnedLockStatus, EscrowAssetType,
    EscrowListing, EscrowListingStatus, FiatIntentStatus, FiatPaymentIntent,
)
from app.services.chain_outbox_worker import process_outbox_sync
from app.services.escrow_market_service import EscrowMarketService, AXOLOTITO_LISTED_STATUS
from tests.conftest import make_user, make_wallet

PRICE_500_AXF = 500 * (10 ** 6)


@pytest.fixture(autouse=True)
def _mock_web3(monkeypatch):
    monkeypatch.setattr(settings, "IS_MOCK_WEB3", True)


def _make_seller_with_axolotito(session: Session, did="seller_1", token_id=77):
    seller = make_user(session, privy_did=did, wallet_address=f"0xSELLER_{did}")
    make_wallet(session, user_id=did)
    axo = Axolotito(
        name="Épico", user_id=did, status="idle",
        energy_current=100, energy_max=100,
        stat_focus=50, stat_luck=50,
        blockchain_token_id=token_id,
    )
    session.add(axo)
    session.commit()
    session.refresh(axo)
    return seller, axo


def _confirm_deposit(session: Session, listing_id: str) -> EscrowListing:
    """Simula el worker confirmando el depósito on-chain."""
    process_outbox_sync(session, max_batch=10)
    EscrowMarketService.finalize_confirmed_escrow_ops(session)
    return session.get(EscrowListing, listing_id)


# ── Publicación ──────────────────────────────────────────────────────────

def test_create_listing_freezes_asset_and_enqueues_deposit(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )

    assert listing.status == EscrowListingStatus.DRAFT
    # Ley económica: 500 AXF = $1,000 MXN = 100,000 centavos
    assert listing.price_mxn_cents == PRICE_500_AXF * AXF_MXN_CENTS // 10 ** 6 == 100_000
    assert listing.fee_bps == 500  # sin VIP

    session.refresh(axo)
    assert axo.status == AXOLOTITO_LISTED_STATUS

    outbox = session.exec(
        select(ChainOutbox).where(ChainOutbox.operation == "escrow_deposit")
    ).one()
    payload = json.loads(outbox.payload_json)
    assert payload["listing_id"] == listing.id
    assert payload["token_id"] == 77


def test_create_listing_vip_fee_from_config(session):
    seller = make_user(
        session, privy_did="seller_vip", wallet_address="0xVIP",
        is_vip=True, vip_tier="axolite",
    )
    make_wallet(session, user_id="seller_vip")
    axo = Axolotito(
        name="Épico", user_id="seller_vip", status="idle",
        energy_current=100, energy_max=100, stat_focus=50, stat_luck=50,
        blockchain_token_id=99,
    )
    session.add(axo)
    session.commit()
    session.refresh(axo)

    listing = EscrowMarketService.create_listing(
        session, "seller_vip", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    assert listing.fee_bps == 200  # Axolite: 2% especial (§1 del plan)


def test_create_listing_rejects_duplicates_and_busy_assets(session):
    _, axo = _make_seller_with_axolotito(session)
    EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.create_listing(
            session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
        )
    # ya listado: el activo quedó congelado (no idle) → 400, o 409 si sigue idle
    assert exc.value.status_code in (400, 409)


def test_create_listing_rejects_foreign_asset(session):
    _, axo = _make_seller_with_axolotito(session)
    make_user(session, privy_did="otro", wallet_address="0xOTRO")
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.create_listing(
            session, "otro", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
        )
    assert exc.value.status_code == 404


def test_create_listing_rejects_nonpositive_price(session):
    _, axo = _make_seller_with_axolotito(session)
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.create_listing(
            session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, 0,
        )
    assert exc.value.status_code == 400


def test_deposit_confirmation_moves_to_escrowed(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    listing = _confirm_deposit(session, listing.id)
    assert listing.status == EscrowListingStatus.ESCROWED
    assert listing.escrow_tx_hash is not None


# ── Cancelación ──────────────────────────────────────────────────────────

def test_cancel_escrowed_listing_enqueues_refund_and_unfreezes(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    _confirm_deposit(session, listing.id)

    listing = EscrowMarketService.cancel_listing(session, "seller_1", listing.id)
    assert listing.status == EscrowListingStatus.REFUNDED

    refund = session.exec(
        select(ChainOutbox).where(ChainOutbox.operation == "escrow_refund")
    ).first()
    assert refund is not None

    session.refresh(axo)
    assert axo.status == "idle"


def test_cancel_foreign_listing_rejected(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    make_user(session, privy_did="intruso", wallet_address="0xMAL")
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.cancel_listing(session, "intruso", listing.id)
    assert exc.value.status_code == 404


# ── Checkout fiat ────────────────────────────────────────────────────────

def test_checkout_creates_intent_with_split(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    _confirm_deposit(session, listing.id)
    make_user(session, privy_did="buyer_1", wallet_address="0xBUYER")

    result = EscrowMarketService.create_checkout(session, "buyer_1", listing.id)
    assert result["gateway"] == "mock"
    assert result["amount_mxn_cents"] == 100_000

    intent = session.exec(select(FiatPaymentIntent)).one()
    # Split: 5% casa ($50 MXN), 95% vendedor ($950 MXN)
    assert intent.split_fee_cents == 5_000
    assert intent.split_seller_cents == 95_000
    assert intent.status == FiatIntentStatus.CREATED

    listing = session.get(EscrowListing, listing.id)
    assert listing.status == EscrowListingStatus.PENDING_PAYMENT


def test_checkout_rejects_self_purchase_and_unescrowed(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    # aún en DRAFT (sin custodia) → no comprable
    make_user(session, privy_did="buyer_1", wallet_address="0xBUYER")
    with pytest.raises(HTTPException):
        EscrowMarketService.create_checkout(session, "buyer_1", listing.id)

    _confirm_deposit(session, listing.id)
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.create_checkout(session, "seller_1", listing.id)
    assert exc.value.status_code == 400


def test_checkout_rejects_concurrent_intent(session):
    _, axo = _make_seller_with_axolotito(session)
    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    _confirm_deposit(session, listing.id)
    make_user(session, privy_did="buyer_1", wallet_address="0xBUYER")
    make_user(session, privy_did="buyer_2", wallet_address="0xBUYER2")

    EscrowMarketService.create_checkout(session, "buyer_1", listing.id)
    with pytest.raises(HTTPException) as exc:
        EscrowMarketService.create_checkout(session, "buyer_2", listing.id)
    # pending_payment bloquea (400) o intent activo (409)
    assert exc.value.status_code in (400, 409)


# ── Cuarentena AXF_Earned (§4) ───────────────────────────────────────────

def test_earned_balance_matures_after_quarantine(session):
    make_user(session, privy_did="vendedor", wallet_address="0xV")
    _, axo = _make_seller_with_axolotito(session, did="s2", token_id=88)
    listing = EscrowMarketService.create_listing(
        session, "s2", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )

    session.add(EarnedBalanceLock(
        seller_id="vendedor", listing_id=listing.id,
        axf_amount=100 * 10 ** 6,
        unlocks_at=datetime.utcnow() + timedelta(hours=72),
    ))
    session.add(EarnedBalanceLock(
        seller_id="vendedor", listing_id=listing.id,
        axf_amount=50 * 10 ** 6,
        unlocks_at=datetime.utcnow() - timedelta(minutes=1),  # ya maduró
    ))
    session.commit()

    balance = EscrowMarketService.earned_balance(session, "vendedor")
    assert balance["axf_earned_locked"] == 100 * 10 ** 6
    assert balance["axf_earned_available"] == 50 * 10 ** 6
    assert balance["quarantine_hours"] == 72
