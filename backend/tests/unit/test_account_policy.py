"""Age and commerce capability regression tests."""

from datetime import datetime
from types import SimpleNamespace

import pytest

from app.core.account_policy import account_capabilities
from app.core.config import settings


@pytest.fixture(autouse=True)
def non_gambling_mode(monkeypatch):
    monkeypatch.setattr(settings, "PRODUCT_MODE", "non_gambling")
    monkeypatch.setattr(settings, "TERMS_VERSION", "2026-07")
    monkeypatch.setattr(settings, "PRIVACY_NOTICE_VERSION", "2026-07")


def _user(**overrides):
    values = {
        "age_band": "unknown",
        "age_assured_at": None,
        "guardian_consent_at": None,
        "terms_accepted_version": None,
        "privacy_accepted_version": None,
        "commerce_status": "disabled",
        "creator_status": "ineligible",
        "kyc_status": "not_started",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_unknown_age_is_fail_closed(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIAT_PAYMENTS", True)
    monkeypatch.setattr(settings, "ENABLE_PLAYER_MARKETPLACE", True)
    monkeypatch.setattr(settings, "ENABLE_CREATOR_PAYOUTS", True)

    capabilities = account_capabilities(_user())

    assert capabilities["can_play"] is True
    assert capabilities["age_assured"] is False
    assert capabilities["can_use_embedded_wallet"] is False
    assert capabilities["can_purchase"] is False
    assert capabilities["can_use_marketplace"] is False
    assert capabilities["can_receive_payouts"] is False


def test_teen_with_guardian_consent_still_cannot_trade(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIAT_PAYMENTS", True)
    monkeypatch.setattr(settings, "ENABLE_PLAYER_MARKETPLACE", True)

    capabilities = account_capabilities(
        _user(
            age_band="teen_13_17",
            age_assured_at=datetime.utcnow(),
            guardian_consent_at=datetime.utcnow(),
            terms_accepted_version="2026-07",
            privacy_accepted_version="2026-07",
            commerce_status="eligible",
        )
    )

    assert capabilities["age_assured"] is True
    assert capabilities["can_use_embedded_wallet"] is False
    assert capabilities["can_purchase"] is False
    assert capabilities["can_use_marketplace"] is False


def test_adult_creator_requires_status_and_kyc(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIAT_PAYMENTS", True)
    monkeypatch.setattr(settings, "ENABLE_PLAYER_MARKETPLACE", True)
    monkeypatch.setattr(settings, "ENABLE_CREATOR_PAYOUTS", True)
    monkeypatch.setattr(settings, "REQUIRE_ADULT_FOR_COMMERCE", True)

    capabilities = account_capabilities(
        _user(
            age_band="adult_18_plus",
            age_assured_at=datetime.utcnow(),
            terms_accepted_version="2026-07",
            privacy_accepted_version="2026-07",
            commerce_status="eligible",
            creator_status="approved",
            kyc_status="verified",
        )
    )

    assert capabilities["can_purchase"] is True
    assert capabilities["can_publish_for_sale"] is True
    assert capabilities["can_receive_payouts"] is True


def test_adult_without_assurance_timestamp_is_fail_closed(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIAT_PAYMENTS", True)

    capabilities = account_capabilities(
        _user(
            age_band="adult_18_plus",
            commerce_status="eligible",
            terms_accepted_version="2026-07",
            privacy_accepted_version="2026-07",
        )
    )

    assert capabilities["age_assured"] is False
    assert capabilities["can_use_embedded_wallet"] is False
    assert capabilities["can_purchase"] is False


def test_stale_legal_consent_blocks_wallet_and_commerce(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIAT_PAYMENTS", True)

    capabilities = account_capabilities(
        _user(
            age_band="adult_18_plus",
            age_assured_at=datetime.utcnow(),
            commerce_status="eligible",
            terms_accepted_version="2026-06",
            privacy_accepted_version="2026-07",
        )
    )

    assert capabilities["legal_consents_current"] is False
    assert capabilities["can_use_embedded_wallet"] is False
    assert capabilities["can_purchase"] is False
