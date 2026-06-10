"""
base.py — Interfaz abstracta de pasarela de pagos fiat con split payout.

El resto del backend solo conoce esta interfaz; cambiar de mock a
Mercado Pago / Stripe Connect es implementar otra subclase y ajustar
el factory get_gateway() (ver __init__.py).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CheckoutIntent:
    gateway_ref: str            # id del checkout en la pasarela
    checkout_url: str           # URL/deeplink que abre el frontend
    amount_mxn_cents: int
    split_fee_cents: int        # comisión casa
    split_seller_cents: int     # payout al vendedor
    expires_at: datetime


class PaymentGateway(ABC):
    name: str

    @abstractmethod
    def create_checkout(
        self,
        amount_mxn_cents: int,
        split_fee_cents: int,
        split_seller_cents: int,
        metadata: dict,
    ) -> CheckoutIntent:
        """Crea un checkout con split payout. metadata DEBE incluir
        listing_id y buyer_id (clave de conciliación, E3 del plan)."""

    @abstractmethod
    def verify_webhook(self, raw_body: bytes, signature: str) -> bool:
        """Valida la firma del webhook en tiempo constante."""

    # ── Reservados para la fase de pasarela real (KYC / §4 del plan) ──────

    def create_seller_account(self, user_id: str) -> str:
        """Crea la sub-cuenta fiduciaria del vendedor (Stripe Express / MP)."""
        raise NotImplementedError("Disponible al integrar la pasarela real.")

    def get_kyc_status(self, user_id: str) -> str:
        """Estado KYC del vendedor (bloqueo > $500 USD/año sin verificar)."""
        raise NotImplementedError("Disponible al integrar la pasarela real.")
