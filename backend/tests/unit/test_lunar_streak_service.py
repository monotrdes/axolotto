"""test_lunar_streak_service.py — Unit tests for LunarStreakService.

DB and external service calls are mocked. Required env vars are injected
before any app import so the config module initialises without an .env file.
"""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("TREASURY_PRIVATE_KEY", "0x" + "a" * 64)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import unittest                                      # noqa: E402

from datetime import datetime, timedelta, timezone  # noqa: E402
from types import SimpleNamespace                   # noqa: E402
from unittest.mock import MagicMock, patch          # noqa: E402

from fastapi import HTTPException                   # noqa: E402

from app.services.lunar_streak_service import (     # noqa: E402
    DAILY_FRJ,
    LUNA_REWARDS,
    LUNA_REWARD_LABELS,
    _apply_inactivity_reset,
    _can_claim_today,
    claim,
    get_status,
)
from app.models.economy import TransactionLedger    # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(**kwargs) -> SimpleNamespace:
    """
    Returns a plain namespace that mimics User fields used by lunar_streak_service.
    Using SimpleNamespace avoids SQLAlchemy instrumentation which requires a session.
    """
    defaults = dict(
        privy_did="did:privy:test",
        lunar_streak_day=0,
        lunar_week=1,
        lunar_last_claim_at=None,
        lunar_cycles_completed=0,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _yesterday_utc() -> datetime:
    return datetime.utcnow() - timedelta(days=1, seconds=1)


def _days_ago_utc(n: int) -> datetime:
    return datetime.utcnow() - timedelta(days=n, seconds=1)


def _make_mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    return db


def _make_mock_wallet(frijolitos: float = 0.0):
    wallet = MagicMock()
    wallet.frijolitos = frijolitos
    return wallet


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

class TestGetStatusFreshUser:

    def test_get_status_fresh_user(self):
        user = _make_user()
        status = get_status(user)

        assert status["can_claim"] is True
        assert status["streak_day"] == 0
        assert status["lunar_week"] == 1
        assert status["today_reward"]["type"] == "frj"
        assert status["today_reward"]["amount"] == DAILY_FRJ[0]  # 50
        assert status["cycles_completed"] == 0
        assert len(status["luna_track"]) == 6


class TestGetStatusMidWeek:

    def test_get_status_mid_week(self):
        """streak_day=4 → next day is 5, reward is DAILY_FRJ[4] = 110."""
        user = _make_user(
            lunar_streak_day=4,
            lunar_last_claim_at=_yesterday_utc(),
        )
        status = get_status(user)

        assert status["can_claim"] is True
        assert status["streak_day"] == 4
        assert status["today_reward"]["type"] == "frj"
        assert status["today_reward"]["amount"] == DAILY_FRJ[4]  # 110


class TestGetStatusAlreadyClaimedToday:

    def test_get_status_already_claimed_today(self):
        now = datetime.now(timezone.utc)
        user = _make_user(lunar_last_claim_at=now)
        status = get_status(user)

        assert status["can_claim"] is False
        assert status["next_claim_at"] is not None


# ---------------------------------------------------------------------------
# claim — FRJ days
# ---------------------------------------------------------------------------

class TestClaimDay1:

    def test_claim_day1(self):
        user = _make_user(
            lunar_streak_day=0,
            lunar_last_claim_at=_yesterday_utc(),
        )
        mock_wallet = _make_mock_wallet(frijolitos=0.0)
        db = _make_mock_db()

        with patch(
            "app.services.lunar_streak_service.BankService.get_or_create_wallet",
            return_value=mock_wallet,
        ):
            result = claim(db, user)

        assert result["type"] == "frj"
        assert result["amount"] == 50.0
        assert result["streak_day"] == 1
        assert mock_wallet.frijolitos == 50.0
        db.commit.assert_called_once()


class TestClaimDay6:

    def test_claim_day6(self):
        user = _make_user(
            lunar_streak_day=5,
            lunar_last_claim_at=_yesterday_utc(),
        )
        mock_wallet = _make_mock_wallet(frijolitos=0.0)
        db = _make_mock_db()

        with patch(
            "app.services.lunar_streak_service.BankService.get_or_create_wallet",
            return_value=mock_wallet,
        ):
            result = claim(db, user)

        assert result["type"] == "frj"
        assert result["amount"] == 130.0
        assert result["streak_day"] == 6
        assert mock_wallet.frijolitos == 130.0


# ---------------------------------------------------------------------------
# claim — Day 7 (capsule)
# ---------------------------------------------------------------------------

class TestClaimDay7Luna1:

    def test_claim_day7_luna1(self):
        user = _make_user(
            lunar_streak_day=6,
            lunar_week=1,
            lunar_last_claim_at=_yesterday_utc(),
        )
        mock_roll_result = {"tier": "bronce", "outcome_type": "gal"}
        db = _make_mock_db()

        with patch(
            "app.services.lunar_streak_service.BankService.get_or_create_wallet",
            return_value=_make_mock_wallet(),
        ):
            with patch(
                "app.services.lunar_streak_service._roll_capsule",
                return_value=mock_roll_result,
            ) as mock_roll:
                result = claim(db, user)

        assert result["type"] == "capsule"
        mock_roll.assert_called_once_with("bronce", user.privy_did, db)
        assert len(result["rolls"]) == 1
        assert result["streak_day"] == 0
        assert result["lunar_week"] == 2
        assert result["cycle_complete"] is False


class TestClaimDay7Luna6CompletesCycle:

    def test_claim_day7_luna6_completes_cycle(self):
        user = _make_user(
            lunar_streak_day=6,
            lunar_week=6,
            lunar_last_claim_at=_yesterday_utc(),
            lunar_cycles_completed=0,
        )
        mock_roll_result = {"tier": "oro", "outcome_type": "axolotito"}
        db = _make_mock_db()

        with patch(
            "app.services.lunar_streak_service.BankService.get_or_create_wallet",
            return_value=_make_mock_wallet(),
        ):
            with patch(
                "app.services.lunar_streak_service._roll_capsule",
                return_value=mock_roll_result,
            ):
                result = claim(db, user)

        assert result["type"] == "capsule"
        assert result["cycle_complete"] is True
        assert result["lunar_week"] == 1
        assert result["cycles_completed"] == 1
        assert user.lunar_week == 1
        assert user.lunar_cycles_completed == 1


# ---------------------------------------------------------------------------
# _apply_inactivity_reset
# ---------------------------------------------------------------------------

class TestInactivityReset:

    def test_inactivity_resets_luna(self):
        """8 days of inactivity resets both lunar_week and streak_day."""
        user = _make_user(
            lunar_week=4,
            lunar_streak_day=5,
            lunar_last_claim_at=_days_ago_utc(8),
        )
        _apply_inactivity_reset(user)

        assert user.lunar_week == 1
        assert user.lunar_streak_day == 0

    def test_miss_a_day_resets_streak_not_luna(self):
        """2-day gap resets streak_day but preserves lunar_week."""
        user = _make_user(
            lunar_week=3,
            lunar_streak_day=4,
            lunar_last_claim_at=_days_ago_utc(2),
        )
        _apply_inactivity_reset(user)

        assert user.lunar_streak_day == 0
        assert user.lunar_week == 3


# ---------------------------------------------------------------------------
# _can_claim_today
# ---------------------------------------------------------------------------

class TestCanClaimToday:

    def test_no_last_claim_returns_true(self):
        user = _make_user()
        assert _can_claim_today(user) is True

    def test_claimed_today_returns_false(self):
        now = datetime.now(timezone.utc)
        user = _make_user(lunar_last_claim_at=now)
        assert _can_claim_today(user) is False

    def test_claimed_yesterday_returns_true(self):
        yesterday = _yesterday_utc()
        user = _make_user(lunar_last_claim_at=yesterday)
        assert _can_claim_today(user) is True


# Alias used by TestDoubleClaimRejection (matches the spec naming)
make_user = _make_user


# ---------------------------------------------------------------------------
# double-claim rejection
# ---------------------------------------------------------------------------

class TestDoubleClaimRejection(unittest.TestCase):
    def test_claim_twice_same_day_raises_429(self):
        """Second claim on same MX calendar day must be rejected."""
        user = make_user(lunar_streak_day=1, lunar_week=1,
                         lunar_last_claim_at=datetime.utcnow())
        mock_db = MagicMock()
        mock_wallet = MagicMock()
        mock_wallet.frijolitos = 0.0
        with patch("app.services.lunar_streak_service.BankService.get_or_create_wallet",
                   return_value=mock_wallet):
            with self.assertRaises(HTTPException) as ctx:
                claim(mock_db, user)
        self.assertEqual(ctx.exception.status_code, 429)
