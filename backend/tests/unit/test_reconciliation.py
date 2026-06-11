"""
test_reconciliation.py — Algoritmo de conciliación webhook fiat ↔ escrow (E3).

Verifica los 6 pasos: firma HMAC, idempotencia anti-replay, matching DB
(monto/ítem/split exactos), matching on-chain, ejecución atómica
(cuarentena 72h + ledger) y liberación vía outbox.
"""
import json
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.models.axolotito import Axolotito
from app.models.economy import (
    ChainOutbox, ProcessedTransaction, TransactionLedger, TransactionType,
)
from app.models.market_escrow import (
    EarnedBalanceLock, EarnedLockStatus, EscrowAssetType,
    EscrowListing, EscrowListingStatus, FiatIntentStatus, FiatPaymentIntent,
)
from app.services.chain_outbox_worker import process_outbox_sync
from app.services.escrow_market_service import EscrowMarketService
from app.services.payment_gateway.mock_gateway import MockPaymentGateway
from app.services.reconciliation_service import ReconciliationService
from tests.conftest import make_user, make_wallet

PRICE_500_AXF = 500 * (10 ** 6)


@pytest.fixture(autouse=True)
def _mock_web3(monkeypatch):
    monkeypatch.setattr(settings, "IS_MOCK_WEB3", True)


def _setup_paid_flow(session: Session):
    """Listing en custodia + checkout abierto. Devuelve (listing, intent, axo)."""
    make_user(session, privy_did="seller_1", wallet_address="0xSELLER")
    make_wallet(session, user_id="seller_1")
    make_user(session, privy_did="buyer_1", wallet_address="0xBUYER")
    make_wallet(session, user_id="buyer_1")

    axo = Axolotito(
        name="Épico", user_id="seller_1", status="idle",
        energy_current=100, energy_max=100, stat_focus=50, stat_luck=50,
        blockchain_token_id=42,
    )
    session.add(axo)
    session.commit()
    session.refresh(axo)

    listing = EscrowMarketService.create_listing(
        session, "seller_1", EscrowAssetType.AXOLOTITO, axo.id, PRICE_500_AXF,
    )
    process_outbox_sync(session, max_batch=10)
    EscrowMarketService.finalize_confirmed_escrow_ops(session)

    EscrowMarketService.create_checkout(session, "buyer_1", listing.id)
    intent = session.exec(select(FiatPaymentIntent)).one()
    listing = session.get(EscrowListing, listing.id)
    return listing, intent, axo


# ── Paso 1: autenticidad ─────────────────────────────────────────────────

def test_invalid_signature_rejected_401(session):
    _, intent, _ = _setup_paid_flow(session)
    raw_body, _ = MockPaymentGateway.build_webhook(intent, "success")
    with pytest.raises(HTTPException) as exc:
        ReconciliationService.reconcile(session, raw_body, "firma_falsa")
    assert exc.value.status_code == 401


def test_tampered_body_rejected_401(session):
    _, intent, _ = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "success")
    tampered = raw_body.replace(b'"amount_mxn_cents":100000', b'"amount_mxn_cents":1')
    with pytest.raises(HTTPException) as exc:
        ReconciliationService.reconcile(session, tampered, signature)
    assert exc.value.status_code == 401


# ── Camino feliz (pasos 3-6) ─────────────────────────────────────────────

def test_happy_path_releases_nft_and_quarantines_earnings(session):
    listing, intent, axo = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "success")

    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "ok"

    session.expire_all()
    intent = session.get(FiatPaymentIntent, intent.id)
    assert intent.status == FiatIntentStatus.SUCCEEDED

    # Liberación procesada inline (mock): NFT entregado y listing released
    listing = session.get(EscrowListing, listing.id)
    assert listing.status == EscrowListingStatus.RELEASED
    assert listing.buyer_id == "buyer_1"
    assert listing.release_tx_hash is not None

    # El activo cambió de dueño en DB
    axo = session.get(Axolotito, axo.id)
    assert axo.user_id == "buyer_1"
    assert axo.status == "idle"

    # Cuarentena 72h del AXF_Earned neto (500 AXF - 5% = 475 AXF)
    lock = session.exec(select(EarnedBalanceLock)).one()
    assert lock.seller_id == "seller_1"
    assert lock.status == EarnedLockStatus.LOCKED
    assert lock.axf_amount == 475 * 10 ** 6
    assert lock.unlocks_at > datetime.utcnow() + timedelta(hours=71)

    # Ledger doble: venta (con fee) y compra
    sale = session.exec(
        select(TransactionLedger).where(TransactionLedger.tx_type == TransactionType.MARKET_SELL)
    ).one()
    assert sale.user_id == "seller_1"
    assert sale.amount == 475 * 10 ** 6
    assert sale.fee_applied == 25 * 10 ** 6
    buy = session.exec(
        select(TransactionLedger).where(TransactionLedger.tx_type == TransactionType.MARKET_BUY)
    ).one()
    assert buy.user_id == "buyer_1"
    assert buy.amount == PRICE_500_AXF

    # El paymentRef quedó en el payload de liberación (auditoría on-chain)
    release_op = session.exec(
        select(ChainOutbox).where(ChainOutbox.operation == "escrow_release")
    ).one()
    payload = json.loads(release_op.payload_json)
    assert payload["payment_ref"] == intent.gateway_ref
    assert release_op.status == "confirmed"


# ── Paso 2: idempotencia / anti-replay (regla crítica #4) ────────────────

def test_replay_webhook_is_benign_noop(session):
    listing, intent, _ = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "success")

    first = ReconciliationService.reconcile(session, raw_body, signature)
    assert first["status"] == "ok"

    replay = ReconciliationService.reconcile(session, raw_body, signature)
    assert replay["status"] == "already_processed"

    # Sin dobles efectos: un solo lock y un solo par de asientos
    locks = session.exec(select(EarnedBalanceLock)).all()
    assert len(locks) == 1
    processed = session.exec(
        select(ProcessedTransaction).where(ProcessedTransaction.purpose == "p2p_fiat_payment")
    ).all()
    assert len(processed) == 1


# ── Paso 3: matching DB ──────────────────────────────────────────────────

def test_wrong_amount_rejected_without_release(session):
    listing, intent, axo = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "wrong_amount")

    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "rejected"
    assert result["reason"] == "amount_mismatch"

    session.expire_all()
    assert session.get(FiatPaymentIntent, intent.id).status == FiatIntentStatus.FAILED
    # El NFT jamás se libera
    assert session.exec(
        select(ChainOutbox).where(ChainOutbox.operation == "escrow_release")
    ).first() is None
    assert session.get(Axolotito, axo.id).user_id == "seller_1"


def test_wrong_listing_rejected(session):
    _, intent, _ = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "wrong_listing")
    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "rejected"
    assert result["reason"] == "listing_mismatch"


def test_payment_failed_returns_listing_to_sale(session):
    listing, intent, _ = _setup_paid_flow(session)
    raw_body, signature = MockPaymentGateway.build_webhook(intent, "failed")

    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "payment_failed"

    session.expire_all()
    assert session.get(FiatPaymentIntent, intent.id).status == FiatIntentStatus.FAILED
    assert session.get(EscrowListing, listing.id).status == EscrowListingStatus.ESCROWED


def test_expired_intent_rejected(session):
    listing, intent, _ = _setup_paid_flow(session)
    intent.expires_at = datetime.utcnow() - timedelta(minutes=1)
    session.add(intent)
    session.commit()

    raw_body, signature = MockPaymentGateway.build_webhook(intent, "success")
    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "rejected"
    assert result["reason"] == "intent_expired"


# ── Paso 4: matching on-chain ────────────────────────────────────────────

def test_custody_mismatch_blocks_release_and_flags_listing(session, monkeypatch):
    listing, intent, axo = _setup_paid_flow(session)
    monkeypatch.setattr(
        ReconciliationService, "_verify_onchain_custody", staticmethod(lambda _l: False)
    )

    raw_body, signature = MockPaymentGateway.build_webhook(intent, "success")
    result = ReconciliationService.reconcile(session, raw_body, signature)
    assert result["status"] == "reconciliation_mismatch"

    session.expire_all()
    assert session.get(EscrowListing, listing.id).status == EscrowListingStatus.MISMATCH
    assert session.get(Axolotito, axo.id).user_id == "seller_1"
    assert session.exec(
        select(ChainOutbox).where(ChainOutbox.operation == "escrow_release")
    ).first() is None
