"""
reconciliation_service.py — Algoritmo de conciliación webhook fiat ↔ escrow on-chain.

Implementa E3 del plan (docs/plan_economia_devex_fintech.md):
  1. Autenticidad (HMAC en tiempo constante)
  2. Idempotencia (ProcessedTransaction, regla crítica #4)
  3. Matching DB (SELECT FOR UPDATE: monto, ítem y split exactos)
  4. Matching on-chain (la pasarela NO es fuente de verdad del activo)
  5. Ejecución atómica (outbox + cuarentena 72h + ledger)
  6. Liberación post-commit por el worker de ChainOutbox

Propiedad clave: dinero (3) y activo (4) se validan de forma independiente
y la liberación solo ocurre si ambos concilian con el mismo listing_id.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.models.economy import (
    ChainOutbox, CurrencyType, ProcessedTransaction, TransactionLedger, TransactionType,
)
from app.models.market_escrow import (
    EarnedBalanceLock, EscrowListing, EscrowListingStatus, FiatIntentStatus, FiatPaymentIntent,
)
from app.models.user import User
from app.services.payment_gateway import get_gateway

logger = logging.getLogger("reconciliation")


class ReconciliationService:

    @staticmethod
    def reconcile(session: Session, raw_body: bytes, signature: str) -> dict:
        # ── 1. Autenticidad ──────────────────────────────────────────────
        gateway = get_gateway()
        if not signature or not gateway.verify_webhook(raw_body, signature):
            logger.warning("reconcile: firma de webhook inválida")
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Payload inválido.")

        gateway_ref = payload.get("ref", "")
        if not gateway_ref:
            raise HTTPException(status_code=400, detail="Webhook sin ref.")

        # ── Capa 1: check rápido de idempotencia para replays del success event ──
        already_processed = session.exec(
            select(ProcessedTransaction).where(ProcessedTransaction.tx_hash == f"webhook:{gateway_ref}")
        ).first()
        if already_processed:
            logger.info("reconcile: replay benigno (Capa 1) ref=%s", gateway_ref)
            return {"status": "already_processed", "ref": gateway_ref}

        # ── 3a. Cargar intent + listing bajo lock (regla crítica #3) ─────
        intent = session.exec(
            select(FiatPaymentIntent)
            .where(FiatPaymentIntent.gateway_ref == gateway_ref)
            .with_for_update()
        ).first()
        if not intent:
            logger.error("reconcile: webhook para ref desconocido %s", gateway_ref)
            raise HTTPException(status_code=404, detail="Pago desconocido.")

        # Si ya se procesó con éxito en otro thread, retornar temprano
        if intent.status == FiatIntentStatus.SUCCEEDED:
            logger.info("reconcile: intent ya completado ref=%s", gateway_ref)
            return {"status": "already_processed", "ref": gateway_ref}

        listing = session.exec(
            select(EscrowListing)
            .where(EscrowListing.id == intent.listing_id)
            .with_for_update()
        ).first()

        # Evento de pago fallido: no liberar, regresar a la venta.
        # No registramos ProcessedTransaction para fallos para permitir reintentos futuros del success event.
        if payload.get("event") == "payment.failed":
            intent.status = FiatIntentStatus.FAILED
            if listing and listing.status == EscrowListingStatus.PENDING_PAYMENT:
                listing.status = EscrowListingStatus.ESCROWED
                listing.updated_at = datetime.utcnow()
                session.add(listing)
            session.add(intent)
            session.commit()
            return {"status": "payment_failed", "ref": gateway_ref}

        # ── 2. Idempotencia para evento de éxito (regla crítica #4) ──────
        session.add(ProcessedTransaction(
            tx_hash=f"webhook:{gateway_ref}",
            user_id=intent.buyer_id,
            purpose="p2p_fiat_payment",
        ))
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            logger.info("reconcile: replay benigno ref=%s", gateway_ref)
            return {"status": "already_processed", "ref": gateway_ref}

        # ── 3b. Matching DB: monto, ítem y split exactos ─────────────────
        reject_reason = ReconciliationService._match_db(payload, intent, listing)
        if reject_reason:
            intent.status = FiatIntentStatus.FAILED
            session.add(intent)
            session.commit()
            logger.error("reconcile: RECHAZADO ref=%s motivo=%s", gateway_ref, reject_reason)
            return {"status": "rejected", "ref": gateway_ref, "reason": reject_reason}

        # ── 4. Matching on-chain: custodia real del activo ───────────────
        if not ReconciliationService._verify_onchain_custody(listing):
            intent.status = FiatIntentStatus.FAILED
            listing.status = EscrowListingStatus.MISMATCH
            listing.updated_at = datetime.utcnow()
            session.add(intent)
            session.add(listing)
            session.commit()
            logger.critical(
                "reconcile: MISMATCH pago recibido pero custodia inconsistente "
                "listing=%s ref=%s — requiere reembolso manual", listing.id, gateway_ref,
            )
            return {"status": "reconciliation_mismatch", "ref": gateway_ref}

        # ── 5. Ejecución atómica ─────────────────────────────────────────
        now = datetime.utcnow()
        intent.status = FiatIntentStatus.SUCCEEDED
        listing.status = EscrowListingStatus.PAID
        listing.buyer_id = intent.buyer_id
        listing.updated_at = now
        session.add(intent)
        session.add(listing)

        buyer = session.exec(select(User).where(User.privy_did == intent.buyer_id)).first()
        buyer_wallet = buyer.wallet_address if buyer else None
        session.add(ChainOutbox(
            user_id=listing.seller_id,
            operation="escrow_release",
            payload_json=json.dumps({
                "listing_id": listing.id,
                "buyer_address": buyer_wallet,
                "payment_ref": gateway_ref,
            }),
            status="pending",
        ))

        # Cuarentena 72h del AXF_Earned (neto de comisión, §4 del plan)
        fee_axf = listing.price_axf * listing.fee_bps // 10_000
        net_axf = listing.price_axf - fee_axf
        session.add(EarnedBalanceLock(
            seller_id=listing.seller_id,
            listing_id=listing.id,
            axf_amount=net_axf,
            unlocks_at=now + timedelta(hours=settings.P2P_QUARANTINE_HOURS),
        ))

        session.add(TransactionLedger(
            user_id=listing.seller_id, amount=net_axf, currency=CurrencyType.AXOFICHA,
            tx_type=TransactionType.MARKET_SELL, related_user_id=intent.buyer_id,
            fee_applied=fee_axf,
            description=f"Venta Tianguis P2P {listing.asset_type.value} #{listing.asset_id} (fiat ref {gateway_ref})",
        ))
        session.add(TransactionLedger(
            user_id=intent.buyer_id, amount=listing.price_axf, currency=CurrencyType.AXOFICHA,
            tx_type=TransactionType.MARKET_BUY, related_user_id=listing.seller_id,
            description=f"Compra Tianguis P2P {listing.asset_type.value} #{listing.asset_id} (fiat ref {gateway_ref})",
        ))

        session.commit()
        logger.info("reconcile: OK listing=%s ref=%s buyer=%s", listing.id, gateway_ref, intent.buyer_id)

        # ── 6. Post-commit: procesar outbox best-effort (worker reintenta) ─
        try:
            from app.services.chain_outbox_worker import process_outbox_sync
            from app.services.escrow_market_service import EscrowMarketService
            process_outbox_sync(session, max_batch=5)
            EscrowMarketService.finalize_confirmed_escrow_ops(session)
        except Exception:
            logger.exception("reconcile: outbox inline falló, el worker reintentará")

        return {"status": "ok", "ref": gateway_ref, "listing_id": listing.id}

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _match_db(payload: dict, intent: FiatPaymentIntent, listing: EscrowListing | None) -> str | None:
        """Devuelve el motivo de rechazo, o None si todo concilia (pasos a-e de E3)."""
        if intent.status != FiatIntentStatus.CREATED:
            return f"intent_status:{intent.status}"
        if intent.expires_at <= datetime.utcnow():
            return "intent_expired"
        if not listing:
            return "listing_missing"
        if listing.status not in (EscrowListingStatus.ESCROWED, EscrowListingStatus.PENDING_PAYMENT):
            return f"listing_status:{listing.status}"
        if payload.get("amount_mxn_cents") != intent.amount_mxn_cents:
            return "amount_mismatch"
        meta = payload.get("metadata") or {}
        if meta.get("listing_id") != listing.id:
            return "listing_mismatch"
        split = payload.get("split") or {}
        if (split.get("fee_cents"), split.get("seller_cents")) != (intent.split_fee_cents, intent.split_seller_cents):
            return "split_mismatch"
        return None

    @staticmethod
    def _verify_onchain_custody(listing: EscrowListing) -> bool:
        """Paso 4 de E3: la custodia del NFT debe ser real antes de liberar.

        En modo mock no hay chain: la custodia simulada es el depósito
        confirmado vía outbox (escrow_tx_hash presente).
        """
        if settings.IS_MOCK_WEB3 or not settings.MARKET_ESCROW_ADDRESS:
            return listing.escrow_tx_hash is not None
        from app.services.web3_service import Web3Service
        return Web3Service.verify_escrow_custody(
            listing.id, listing.nft_contract, listing.token_id or 0
        )
