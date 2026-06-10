"""
escrow_market_service.py — Tianguis P2P: listings con escrow on-chain + checkout fiat.

Flujo (Parte II E1.3 del plan):
  create_listing()  → valida activo artesanal, lo congela y encola escrow_deposit
  create_checkout() → abre intent fiat con split según VIP del vendedor
  cancel_listing()  → encola escrow_refund y libera el activo
  (la liberación al comprador la dispara reconciliation_service vía webhook)

Solo NFTs artesanales (cortafuegos legal §2): Axolotitos y Tablas. Los precios
son en AXF anclado a fiat (1 AXF = $2.00 MXN, config.AXF_MXN_CENTS).
"""
import json
import logging
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings, VIP_CONFIG, AXF_MXN_CENTS, AXF_DECIMALS_BACKEND
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import ChainOutbox
from app.models.market_escrow import (
    EarnedBalanceLock, EarnedLockStatus, EscrowAssetType, EscrowListing,
    EscrowListingStatus, FiatIntentStatus, FiatPaymentIntent,
)
from app.models.user import User
from app.services.payment_gateway import get_gateway

logger = logging.getLogger("escrow_market")

DEFAULT_FEE_BPS = 500          # 5% sin VIP (mismo default que el mercado de inventario)
AXOLOTITO_LISTED_STATUS = "listed_market"

ACTIVE_LISTING_STATUSES = [
    EscrowListingStatus.DRAFT,
    EscrowListingStatus.ESCROWED,
    EscrowListingStatus.PENDING_PAYMENT,
    EscrowListingStatus.PAID,
]


def _seller_fee_bps(session: Session, seller: User) -> int:
    if seller.is_vip and seller.vip_tier:
        return VIP_CONFIG.get(seller.vip_tier, {}).get("p2p_commission_bps", DEFAULT_FEE_BPS)
    return DEFAULT_FEE_BPS


def _nft_contract_for(asset_type: EscrowAssetType) -> str:
    if asset_type == EscrowAssetType.AXOLOTITO:
        return settings.AXOLOTITOS_ADDRESS or ""
    return settings.TABLAS_ADDRESS or ""


class EscrowMarketService:

    @staticmethod
    def create_listing(
        session: Session,
        seller_id: str,
        asset_type: EscrowAssetType,
        asset_id: int,
        price_axf: int,
    ) -> EscrowListing:
        if price_axf <= 0:
            raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0 AXF.")

        seller = session.exec(select(User).where(User.privy_did == seller_id)).first()
        if not seller or not seller.wallet_address:
            raise HTTPException(status_code=400, detail="Necesitas una wallet vinculada para vender en el Tianguis.")

        # Validar propiedad y disponibilidad del activo artesanal
        if asset_type == EscrowAssetType.AXOLOTITO:
            asset = session.exec(
                select(Axolotito)
                .where(Axolotito.id == asset_id, Axolotito.user_id == seller_id)
                .with_for_update()
            ).first()
            if not asset:
                raise HTTPException(status_code=404, detail="Axolotito no encontrado o no es tuyo.")
            if asset.status != "idle":
                raise HTTPException(status_code=400, detail="El Axolotito debe estar en reposo (idle) para listarse.")
            token_id = asset.blockchain_token_id
        else:
            asset = session.exec(
                select(PlayerBoard)
                .where(PlayerBoard.id == asset_id, PlayerBoard.user_id == seller_id)
                .with_for_update()
            ).first()
            if not asset or asset.is_dead:
                raise HTTPException(status_code=404, detail="Tabla no encontrada, muerta o no es tuya.")
            token_id = asset.blockchain_token_id

        existing = session.exec(
            select(EscrowListing).where(
                EscrowListing.asset_type == asset_type,
                EscrowListing.asset_id == asset_id,
                EscrowListing.status.in_(ACTIVE_LISTING_STATUSES),  # type: ignore[attr-defined]
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Este activo ya está listado en el Tianguis.")

        fee_bps = _seller_fee_bps(session, seller)
        listing = EscrowListing(
            seller_id=seller_id,
            asset_type=asset_type,
            asset_id=asset_id,
            nft_contract=_nft_contract_for(asset_type),
            token_id=token_id,
            price_axf=price_axf,
            price_mxn_cents=price_axf * AXF_MXN_CENTS // (10 ** AXF_DECIMALS_BACKEND),
            fee_bps=fee_bps,
            status=EscrowListingStatus.DRAFT,
        )
        session.add(listing)

        # Congelar el activo en el juego mientras está listado
        if asset_type == EscrowAssetType.AXOLOTITO:
            asset.status = AXOLOTITO_LISTED_STATUS
            session.add(asset)

        # Depósito al contrato vía outbox (misma transacción DB — atomicidad)
        session.add(ChainOutbox(
            user_id=seller_id,
            operation="escrow_deposit",
            payload_json=json.dumps({
                "listing_id": listing.id,
                "seller_address": seller.wallet_address,
                "nft_contract": listing.nft_contract,
                "token_id": token_id,
                "price_axf": price_axf,
            }),
            status="pending",
        ))
        session.commit()
        session.refresh(listing)
        return listing

    @staticmethod
    def cancel_listing(session: Session, seller_id: str, listing_id: str) -> EscrowListing:
        listing = session.exec(
            select(EscrowListing)
            .where(EscrowListing.id == listing_id, EscrowListing.seller_id == seller_id)
            .with_for_update()
        ).first()
        if not listing:
            raise HTTPException(status_code=404, detail="Publicación no encontrada.")
        if listing.status not in (EscrowListingStatus.DRAFT, EscrowListingStatus.ESCROWED,
                                  EscrowListingStatus.PENDING_PAYMENT):
            raise HTTPException(status_code=400, detail="La publicación ya no puede cancelarse.")

        # Invalidar intents de pago activos
        intents = session.exec(
            select(FiatPaymentIntent).where(
                FiatPaymentIntent.listing_id == listing.id,
                FiatPaymentIntent.status == FiatIntentStatus.CREATED,
            )
        ).all()
        for intent in intents:
            intent.status = FiatIntentStatus.EXPIRED
            session.add(intent)

        was_escrowed = listing.status in (EscrowListingStatus.ESCROWED, EscrowListingStatus.PENDING_PAYMENT)
        listing.status = EscrowListingStatus.CANCELLED if not was_escrowed else EscrowListingStatus.REFUNDED
        listing.updated_at = datetime.utcnow()
        session.add(listing)

        if was_escrowed:
            session.add(ChainOutbox(
                user_id=seller_id,
                operation="escrow_refund",
                payload_json=json.dumps({"listing_id": listing.id}),
                status="pending",
            ))

        EscrowMarketService._unfreeze_asset(session, listing)
        session.commit()
        session.refresh(listing)
        return listing

    @staticmethod
    def create_checkout(session: Session, buyer_id: str, listing_id: str) -> dict:
        listing = session.exec(
            select(EscrowListing).where(EscrowListing.id == listing_id).with_for_update()
        ).first()
        if not listing:
            raise HTTPException(status_code=404, detail="Publicación no encontrada.")
        if listing.seller_id == buyer_id:
            raise HTTPException(status_code=400, detail="No puedes comprar tu propia publicación.")
        if listing.status != EscrowListingStatus.ESCROWED:
            raise HTTPException(status_code=400, detail="La publicación no está disponible para compra.")

        active_intent = session.exec(
            select(FiatPaymentIntent).where(
                FiatPaymentIntent.listing_id == listing.id,
                FiatPaymentIntent.status == FiatIntentStatus.CREATED,
                FiatPaymentIntent.expires_at > datetime.utcnow(),
            )
        ).first()
        if active_intent:
            raise HTTPException(status_code=409, detail="Hay un pago en curso para esta publicación.")

        amount = listing.price_mxn_cents
        fee = amount * listing.fee_bps // 10_000
        seller_share = amount - fee

        gateway = get_gateway()
        checkout = gateway.create_checkout(
            amount_mxn_cents=amount,
            split_fee_cents=fee,
            split_seller_cents=seller_share,
            metadata={"listing_id": listing.id, "buyer_id": buyer_id},
        )

        intent = FiatPaymentIntent(
            listing_id=listing.id,
            buyer_id=buyer_id,
            gateway=gateway.name,
            gateway_ref=checkout.gateway_ref,
            amount_mxn_cents=amount,
            split_fee_cents=fee,
            split_seller_cents=seller_share,
            expires_at=checkout.expires_at,
        )
        session.add(intent)
        listing.status = EscrowListingStatus.PENDING_PAYMENT
        listing.updated_at = datetime.utcnow()
        session.add(listing)
        session.commit()

        return {
            "intent_id": intent.id,
            "gateway": gateway.name,
            "gateway_ref": checkout.gateway_ref,
            "checkout_url": checkout.checkout_url,
            "amount_mxn_cents": amount,
            "expires_at": checkout.expires_at.isoformat(),
        }

    # ── Saldos AXF_Earned (cuarentena §4) ────────────────────────────────

    @staticmethod
    def earned_balance(session: Session, user_id: str) -> dict:
        """Madura locks vencidos y devuelve el desglose AXF_Earned."""
        now = datetime.utcnow()
        locks = session.exec(
            select(EarnedBalanceLock)
            .where(EarnedBalanceLock.seller_id == user_id)
            .with_for_update()
        ).all()

        locked = available = 0
        for lock in locks:
            if lock.status == EarnedLockStatus.LOCKED and lock.unlocks_at <= now:
                lock.status = EarnedLockStatus.AVAILABLE
                session.add(lock)
            if lock.status == EarnedLockStatus.LOCKED:
                locked += lock.axf_amount
            elif lock.status == EarnedLockStatus.AVAILABLE:
                available += lock.axf_amount
        session.commit()

        return {
            "axf_earned_locked": locked,
            "axf_earned_available": available,
            "quarantine_hours": settings.P2P_QUARANTINE_HOURS,
        }

    # ── Sincronización DB ↔ outbox confirmada ────────────────────────────

    @staticmethod
    def finalize_confirmed_escrow_ops(session: Session) -> int:
        """Refleja en EscrowListing las operaciones de escrow confirmadas
        por el worker de ChainOutbox. Idempotente."""
        entries = session.exec(
            select(ChainOutbox).where(
                ChainOutbox.operation.in_(["escrow_deposit", "escrow_release", "escrow_refund"]),  # type: ignore[attr-defined]
                ChainOutbox.status == "confirmed",
            )
        ).all()

        updated = 0
        for entry in entries:
            payload = json.loads(entry.payload_json)
            listing = session.get(EscrowListing, payload.get("listing_id"))
            if not listing:
                continue
            if entry.operation == "escrow_deposit" and listing.status == EscrowListingStatus.DRAFT:
                listing.status = EscrowListingStatus.ESCROWED
                listing.escrow_tx_hash = entry.tx_hash
            elif entry.operation == "escrow_release" and listing.status == EscrowListingStatus.PAID:
                listing.status = EscrowListingStatus.RELEASED
                listing.release_tx_hash = entry.tx_hash
                EscrowMarketService._transfer_asset_ownership(session, listing)
            elif entry.operation == "escrow_refund" and listing.status == EscrowListingStatus.REFUNDED:
                if not listing.release_tx_hash:
                    listing.release_tx_hash = entry.tx_hash
            else:
                continue
            listing.updated_at = datetime.utcnow()
            session.add(listing)
            updated += 1

        if updated:
            session.commit()
        return updated

    # ── Helpers internos ─────────────────────────────────────────────────

    @staticmethod
    def _unfreeze_asset(session: Session, listing: EscrowListing) -> None:
        if listing.asset_type == EscrowAssetType.AXOLOTITO:
            asset = session.get(Axolotito, listing.asset_id)
            if asset and asset.status == AXOLOTITO_LISTED_STATUS:
                asset.status = "idle"
                session.add(asset)

    @staticmethod
    def _transfer_asset_ownership(session: Session, listing: EscrowListing) -> None:
        """Reasigna el activo en DB al comprador tras la liberación on-chain."""
        if not listing.buyer_id:
            return
        if listing.asset_type == EscrowAssetType.AXOLOTITO:
            asset = session.get(Axolotito, listing.asset_id)
            if asset:
                asset.user_id = listing.buyer_id
                asset.status = "idle"
                session.add(asset)
        else:
            asset = session.get(PlayerBoard, listing.asset_id)
            if asset:
                asset.user_id = listing.buyer_id
                session.add(asset)
