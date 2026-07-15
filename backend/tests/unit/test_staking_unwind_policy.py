"""Feature shutdown must release staked assets without minting yield."""

from datetime import datetime

from fastapi import Request
from sqlmodel import Session, select

from app.api.v1.endpoints.staking import unstake_axolotito
from app.core.config import settings
from app.models.axolotito import Axolotito
from app.models.economy import TransactionLedger, Wallet
from tests.conftest import make_user


def test_disabled_staking_unstake_is_immediate_unwind_without_yield(
    session: Session,
    monkeypatch,
):
    request = Request(
        scope={"type": "http", "method": "POST", "path": "/", "headers": []},
    )
    user = make_user(
        session,
        privy_did="did:privy:staking_unwind",
        wallet_address=None,
    )
    axolotito = Axolotito(
        user_id=user.privy_did,
        name="Unwind",
        status="studying",
        last_staking_claim=datetime.utcnow(),
        accrued_unclaimed=42.0,
    )
    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    monkeypatch.setattr(settings, "ENABLE_PASSIVE_TOKEN_REWARDS", False)
    result = unstake_axolotito(
        request,
        axolotito.id,
        session,
        user.privy_did,
    )

    session.refresh(axolotito)
    assert result["claimed_frj"] == 0.0
    assert result["rewards_enabled"] is False
    assert axolotito.status == "idle"
    assert axolotito.accrued_unclaimed == 0
    assert axolotito.last_staking_claim is None
    assert session.exec(
        select(Wallet).where(Wallet.user_id == user.privy_did)
    ).first() is None
    assert session.exec(
        select(TransactionLedger).where(
            TransactionLedger.user_id == user.privy_did,
        )
    ).all() == []
