"""
market_escrow.py — Endpoints del Tianguis P2P con escrow on-chain y pago fiat.

Montado en /api/v1/market/escrow. Ver docs/plan_economia_devex_fintech.md (Parte II).
"""
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id
from app.core.config import axf_to_internal
from app.database import get_session
from app.models.market_escrow import EscrowAssetType, EscrowListing, EscrowListingStatus
from app.services.escrow_market_service import EscrowMarketService

router = APIRouter()


class CreateEscrowListingRequest(BaseModel):
    asset_type: EscrowAssetType
    asset_id: int
    price_axf: float          # AXF legible; se convierte a unidad mínima


@router.post("/list")
def create_escrow_listing(
    request: CreateEscrowListingRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Publica un NFT artesanal (Axolotito/Tabla) en el Tianguis P2P.

    El NFT pasa a custodia del contrato MarketEscrow vía outbox.
    """
    listing = EscrowMarketService.create_listing(
        session,
        seller_id=verified_user_id,
        asset_type=request.asset_type,
        asset_id=request.asset_id,
        price_axf=axf_to_internal(request.price_axf),
    )
    return {
        "mensaje": "Publicación creada. El NFT pasa a custodia del escrow.",
        "listing_id": listing.id,
        "status": listing.status,
        "price_mxn_cents": listing.price_mxn_cents,
    }


@router.post("/{listing_id}/cancel")
def cancel_escrow_listing(
    listing_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Cancela una publicación propia; el NFT regresa de la custodia al vendedor."""
    listing = EscrowMarketService.cancel_listing(session, verified_user_id, listing_id)
    return {"mensaje": "Publicación cancelada.", "status": listing.status}


@router.post("/{listing_id}/checkout")
def checkout_escrow_listing(
    listing_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Abre el checkout fiat (pasarela con split payout) para comprar el listing."""
    return EscrowMarketService.create_checkout(session, verified_user_id, listing_id)


@router.get("/listings")
def get_escrow_listings(
    asset_type: Optional[EscrowAssetType] = None,
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    """Publicaciones activas (en custodia) del Tianguis P2P."""
    statement = (
        select(EscrowListing)
        .where(EscrowListing.status == EscrowListingStatus.ESCROWED)
        .order_by(EscrowListing.created_at.desc())
    )
    if asset_type:
        statement = statement.where(EscrowListing.asset_type == asset_type)
    listings = session.exec(statement.offset(skip).limit(limit)).all()
    return [l.model_dump() for l in listings]


@router.get("/earned-balance")
def get_earned_balance(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Saldo AXF_Earned (elegible a retiro DevEx) con desglose de cuarentena 72h."""
    return EscrowMarketService.earned_balance(session, verified_user_id)
