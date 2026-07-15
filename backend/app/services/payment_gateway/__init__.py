from app.services.payment_gateway.base import PaymentGateway, CheckoutIntent
from app.services.payment_gateway.mock_gateway import MockPaymentGateway
from app.core.config import settings


def _mock_gateway_allowed() -> bool:
    return (
        settings.PRODUCT_MODE == "legacy_simulation"
        and settings.BLOCKCHAIN_MODE == "local"
        and settings.ALLOW_DEV_PAYMENTS
    )


def get_gateway() -> PaymentGateway:
    """Return an explicitly configured gateway; never silently select mock."""
    if not settings.ENABLE_FIAT_PAYMENTS:
        raise RuntimeError("Fiat payments are disabled by product policy.")

    provider = settings.PAYMENT_GATEWAY_PROVIDER.strip().lower()
    if provider == "mock":
        if not _mock_gateway_allowed():
            raise RuntimeError(
                "MockPaymentGateway requires local legacy_simulation and "
                "ALLOW_DEV_PAYMENTS=true."
            )
        return MockPaymentGateway()

    raise RuntimeError(
        f"Payment gateway provider '{provider}' is not implemented/configured."
    )
