"""Wallet linking must be server-authorized, never trusted from sync body."""

from datetime import datetime

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services.user_service import sync_user
from tests.conftest import make_user


@pytest.fixture(autouse=True)
def safe_account_policy(monkeypatch):
    monkeypatch.setattr(settings, "PRODUCT_MODE", "non_gambling")
    monkeypatch.setattr(settings, "TERMS_VERSION", "2026-07")
    monkeypatch.setattr(settings, "PRIVACY_NOTICE_VERSION", "2026-07")


def test_unknown_account_cannot_link_wallet_from_sync_body(session):
    user = make_user(
        session,
        privy_did="did:privy:wallet_unknown",
        wallet_address=None,
    )

    with pytest.raises(HTTPException) as exc:
        sync_user(
            session,
            user.privy_did,
            user.email,
            "0x0000000000000000000000000000000000000001",
            user.privy_did,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail["capability"] == "can_use_embedded_wallet"
    session.refresh(user)
    assert user.wallet_address is None


def test_assured_adult_still_needs_signed_wallet_link_flow(session):
    user = make_user(
        session,
        privy_did="did:privy:wallet_adult",
        wallet_address=None,
    )
    user.age_band = "adult_18_plus"
    user.age_assured_at = datetime.utcnow()
    user.terms_accepted_version = "2026-07"
    user.privacy_accepted_version = "2026-07"
    session.add(user)
    session.commit()

    address = "0x0000000000000000000000000000000000000002"
    with pytest.raises(HTTPException) as exc:
        sync_user(
            session,
            user.privy_did,
            user.email,
            address,
            user.privy_did,
        )

    session.refresh(user)
    assert exc.value.status_code == 403
    assert exc.value.detail["capability"] == "can_use_embedded_wallet"
    assert user.wallet_address is None
