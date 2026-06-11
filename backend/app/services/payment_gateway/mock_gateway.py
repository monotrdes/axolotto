"""
mock_gateway.py — Pasarela fiat simulada (fase sin Mercado Pago / Stripe).

Replica el contrato de una pasarela real: checkout con split, y webhook
`payment.completed` firmado con HMAC-SHA256 — el mismo esquema de firma
que usará la pasarela real, de modo que el flujo de conciliación (E3)
se ejercita completo desde hoy.

El "pago" se dispara con el endpoint dev POST /payments/mock/{ref}/pay,
que admite outcomes de fallo para tests: failed | wrong_amount |
wrong_listing (replay se prueba reenviando el mismo webhook).
"""
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta

from app.core.config import settings
from app.services.payment_gateway.base import CheckoutIntent, PaymentGateway

CHECKOUT_TTL_MINUTES = 30


class MockPaymentGateway(PaymentGateway):
    name = "mock"

    def create_checkout(
        self,
        amount_mxn_cents: int,
        split_fee_cents: int,
        split_seller_cents: int,
        metadata: dict,
    ) -> CheckoutIntent:
        ref = f"mock_{uuid.uuid4().hex}"
        return CheckoutIntent(
            gateway_ref=ref,
            checkout_url=f"/dev/mock-checkout/{ref}",
            amount_mxn_cents=amount_mxn_cents,
            split_fee_cents=split_fee_cents,
            split_seller_cents=split_seller_cents,
            expires_at=datetime.utcnow() + timedelta(minutes=CHECKOUT_TTL_MINUTES),
        )

    # ── Firma HMAC (mismo esquema que la pasarela real) ──────────────────

    @staticmethod
    def sign(raw_body: bytes) -> str:
        return hmac.new(
            settings.PAYMENT_WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

    def verify_webhook(self, raw_body: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(raw_body), signature)

    # ── Construcción del webhook simulado ────────────────────────────────

    @staticmethod
    def build_webhook(intent, outcome: str = "success") -> tuple[bytes, str]:
        """Construye (raw_body, signature) del webhook que la pasarela real
        enviaría a POST /api/v1/payments/webhook.

        outcomes: success | failed | wrong_amount | wrong_listing
        (cubren los pasos 1-4 del algoritmo de conciliación E3).
        """
        payload = {
            "event": "payment.failed" if outcome == "failed" else "payment.completed",
            "gateway": "mock",
            "ref": intent.gateway_ref,
            "amount_mxn_cents": intent.amount_mxn_cents,
            "split": {
                "fee_cents": intent.split_fee_cents,
                "seller_cents": intent.split_seller_cents,
            },
            "metadata": {
                "listing_id": intent.listing_id,
                "buyer_id": intent.buyer_id,
            },
            "created_at": datetime.utcnow().isoformat(),
        }
        if outcome == "wrong_amount":
            payload["amount_mxn_cents"] = intent.amount_mxn_cents + 1
        elif outcome == "wrong_listing":
            payload["metadata"]["listing_id"] = str(uuid.uuid4())

        raw = json.dumps(payload, separators=(",", ":")).encode()
        return raw, MockPaymentGateway.sign(raw)
