"""Per-account capability decisions for age, consent and commerce.

Global product flags and account eligibility must both allow an operation.
Unknown or incomplete age data always produces the least privileged result.
"""

from typing import Any

from fastapi import HTTPException

from app.core.config import settings


def account_capabilities(user: Any) -> dict[str, bool]:
    """Return public, fail-closed capabilities for one authenticated account."""
    # The legacy simulator is accepted only on a local chain by Settings.
    # It exists to exercise historical economy tests and is never a public
    # product policy, so age/KYC fixtures are intentionally bypassed there.
    if settings.PRODUCT_MODE == "legacy_simulation":
        commerce_enabled = (
            settings.ENABLE_FIAT_PAYMENTS or settings.ENABLE_CRYPTO_CHECKOUT
        )
        marketplace_enabled = settings.ENABLE_PLAYER_MARKETPLACE
        return {
            "can_play": True,
            "age_assured": True,
            "legal_consents_current": True,
            "guardian_consent_required": False,
            "can_use_embedded_wallet": True,
            "can_purchase": commerce_enabled,
            "can_use_marketplace": marketplace_enabled,
            "can_publish_for_sale": marketplace_enabled,
            "can_receive_payouts": settings.ENABLE_CREATOR_PAYOUTS,
        }

    age_band = getattr(user, "age_band", "unknown") or "unknown"
    commerce_status = getattr(user, "commerce_status", "disabled") or "disabled"
    creator_status = getattr(user, "creator_status", "ineligible") or "ineligible"
    kyc_status = getattr(user, "kyc_status", "not_started") or "not_started"
    age_assured_at = getattr(user, "age_assured_at", None)
    guardian_consented = bool(getattr(user, "guardian_consent_at", None))
    terms_version = settings.TERMS_VERSION.strip()
    privacy_version = settings.PRIVACY_NOTICE_VERSION.strip()
    legal_consents_current = bool(terms_version and privacy_version) and (
        getattr(user, "terms_accepted_version", None) == terms_version
        and getattr(user, "privacy_accepted_version", None) == privacy_version
    )

    is_adult = age_band == "adult_18_plus" and bool(age_assured_at)
    is_teen_with_consent = (
        age_band == "teen_13_17"
        and bool(age_assured_at)
        and guardian_consented
    )
    age_assured = bool(age_assured_at) and (
        is_adult or is_teen_with_consent or age_band == "under_13"
    )

    can_purchase = (
        (settings.ENABLE_FIAT_PAYMENTS or settings.ENABLE_CRYPTO_CHECKOUT)
        and settings.REQUIRE_ADULT_FOR_COMMERCE
        and is_adult
        and legal_consents_current
        and commerce_status == "eligible"
    )
    can_use_marketplace = (
        settings.ENABLE_PLAYER_MARKETPLACE
        and is_adult
        and legal_consents_current
        and commerce_status == "eligible"
    )
    can_publish_for_sale = (
        can_use_marketplace
        and creator_status == "approved"
        and kyc_status == "verified"
    )
    can_receive_payouts = can_publish_for_sale and settings.ENABLE_CREATOR_PAYOUTS

    return {
        "can_play": True,
        "age_assured": age_assured,
        "legal_consents_current": legal_consents_current,
        "guardian_consent_required": age_band in {"under_13", "teen_13_17"},
        # Public wallet linking is disabled until the server verifies a signed
        # address challenge and records wallet provenance. Privy/client payloads
        # alone are not proof of address control.
        "can_use_embedded_wallet": False,
        "can_purchase": can_purchase,
        "can_use_marketplace": can_use_marketplace,
        "can_publish_for_sale": can_publish_for_sale,
        "can_receive_payouts": can_receive_payouts,
    }


def require_account_capability(user: Any, capability: str) -> None:
    """Reject an account operation unless its server-derived policy allows it."""
    capabilities = account_capabilities(user)
    if not capabilities.get(capability, False):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCOUNT_CAPABILITY_REQUIRED",
                "capability": capability,
            },
        )
