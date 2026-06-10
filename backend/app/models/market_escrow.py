"""
market_escrow.py — Modelos del Tianguis P2P con escrow on-chain y pago fiat.

Ver docs/plan_economia_devex_fintech.md (Parte II, E1.2).

Saldos duales (§3 del plan): NO se parte Wallet.axofichas en dos columnas.
AXF_Earned disponible = SUM(EarnedBalanceLock.axf_amount WHERE status='available');
todo lo demás es AXF_Purchased. El elegible a retiro DevEx se deriva del ledger.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from sqlmodel import SQLModel, Field


class EscrowListingStatus(str, Enum):
    DRAFT           = "draft"             # creado en DB, depósito on-chain pendiente
    ESCROWED        = "escrowed"          # NFT en custodia del MarketEscrow
    PENDING_PAYMENT = "pending_payment"   # checkout fiat activo
    PAID            = "paid"              # webhook conciliado, liberación en outbox
    RELEASED        = "released"          # NFT entregado al comprador
    CANCELLED       = "cancelled"         # cancelado antes del depósito
    REFUNDED        = "refunded"          # NFT devuelto al vendedor
    MISMATCH        = "reconciliation_mismatch"  # pago recibido pero custodia inconsistente


class EscrowAssetType(str, Enum):
    AXOLOTITO = "axolotito"   # ERC-721 Axolotitos.sol
    TABLA     = "tabla"       # ERC-721 TablasLoteria.sol


class FiatIntentStatus(str, Enum):
    CREATED   = "created"
    SUCCEEDED = "succeeded"
    FAILED    = "failed"
    EXPIRED   = "expired"


class EarnedLockStatus(str, Enum):
    LOCKED      = "locked"       # cuarentena 72h (§4 del plan)
    AVAILABLE   = "available"    # elegible para retiro DevEx
    CLAWED_BACK = "clawed_back"  # revertido por fraude/contracargo


class EscrowListing(SQLModel, table=True):
    """Publicación P2P de un NFT artesanal con custodia on-chain.

    El id (uuid) se usa también como listingId on-chain: bytes32 = keccak(id).
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    seller_id: str = Field(foreign_key="user.privy_did", index=True)

    asset_type: EscrowAssetType
    asset_id: int                              # id en DB (Axolotito.id / PlayerBoard.id)
    nft_contract: str = ""                     # dirección desde settings (nunca hardcode)
    token_id: Optional[int] = None             # blockchain_token_id del activo

    price_axf: int                             # unidad mínima 10**6 (1 AXF = $2.00 MXN fijo)
    price_mxn_cents: int                       # derivado vía AXF_MXN_CENTS
    fee_bps: int                               # comisión según VIP del vendedor

    status: EscrowListingStatus = Field(default=EscrowListingStatus.DRAFT, index=True)
    buyer_id: Optional[str] = Field(default=None, foreign_key="user.privy_did")

    escrow_tx_hash: Optional[str] = None       # tx del depósito al contrato
    release_tx_hash: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FiatPaymentIntent(SQLModel, table=True):
    """Intento de pago fiat (checkout) contra un EscrowListing."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    listing_id: str = Field(foreign_key="escrowlisting.id", index=True)
    buyer_id: str = Field(foreign_key="user.privy_did", index=True)

    gateway: str                               # "mock" | "mercadopago" | "stripe"
    gateway_ref: str = Field(unique=True, index=True)

    amount_mxn_cents: int
    split_fee_cents: int                       # comisión casa
    split_seller_cents: int                    # resto al vendedor

    status: FiatIntentStatus = Field(default=FiatIntentStatus.CREATED, index=True)
    expires_at: datetime                       # TTL (mismo patrón que CryptoPurchaseOrder)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EarnedBalanceLock(SQLModel, table=True):
    """Cuarentena 72h del AXF_Earned tras una venta P2P (§4 del plan)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(foreign_key="user.privy_did", index=True)
    listing_id: str = Field(foreign_key="escrowlisting.id")

    axf_amount: int                            # unidad mínima (neto de comisión)
    unlocks_at: datetime
    status: EarnedLockStatus = Field(default=EarnedLockStatus.LOCKED, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
