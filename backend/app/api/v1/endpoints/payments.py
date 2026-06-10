"""
payments.py — Receptor de webhooks de la pasarela fiat + simulador dev.

Montado en /api/v1/payments. El webhook es el ÚNICO disparador de la
liberación de NFTs en escrow (algoritmo de conciliación E3 del plan).

En la fase actual la pasarela es simulada: POST /mock/{ref}/pay construye
y firma el mismo webhook que enviaría Mercado Pago / Stripe.
"""
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session, select

from app.core.config import settings
from app.database import get_session
from app.models.market_escrow import FiatPaymentIntent
from app.services.payment_gateway.mock_gateway import MockPaymentGateway
from app.services.reconciliation_service import ReconciliationService

logger = logging.getLogger("payments")

router = APIRouter()

MOCK_PAY_OUTCOMES = {"success", "failed", "wrong_amount", "wrong_listing"}


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_webhook_signature: str = Header(default=""),
    session: Session = Depends(get_session),
):
    """Webhook `payment.completed` / `payment.failed` de la pasarela fiat.

    La firma HMAC-SHA256 viaja en X-Webhook-Signature sobre el body crudo.
    """
    raw_body = await request.body()
    return ReconciliationService.reconcile(session, raw_body, x_webhook_signature)


@router.post("/mock/{gateway_ref}/pay")
def mock_pay(
    gateway_ref: str,
    outcome: str = "success",
    session: Session = Depends(get_session),
):
    """[DEV] Simula que el comprador pagó en la pasarela.

    Construye el webhook firmado y lo concilia — mismo código que la
    pasarela real ejercitaría. outcome: success|failed|wrong_amount|wrong_listing.
    """
    if settings.BLOCKCHAIN_MODE != "local" and not settings.ALLOW_DEV_PAYMENTS:
        raise HTTPException(status_code=403, detail="Solo disponible en modo local/dev.")
    if outcome not in MOCK_PAY_OUTCOMES:
        raise HTTPException(status_code=400, detail=f"outcome inválido: {outcome}")

    intent = session.exec(
        select(FiatPaymentIntent).where(FiatPaymentIntent.gateway_ref == gateway_ref)
    ).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent de pago no encontrado.")

    raw_body, signature = MockPaymentGateway.build_webhook(intent, outcome)
    return ReconciliationService.reconcile(session, raw_body, signature)
