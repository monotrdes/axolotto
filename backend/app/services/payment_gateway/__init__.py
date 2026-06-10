from app.services.payment_gateway.base import PaymentGateway, CheckoutIntent
from app.services.payment_gateway.mock_gateway import MockPaymentGateway


def get_gateway() -> PaymentGateway:
    """Factory del gateway activo. Fase actual: solo mock.

    Cuando se integre Mercado Pago / Stripe, seleccionar aquí según
    settings (p.ej. settings.PAYMENT_GATEWAY).
    """
    return MockPaymentGateway()
