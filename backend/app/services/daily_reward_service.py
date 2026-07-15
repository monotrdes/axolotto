"""
daily_reward_service.py — Daily F2P reward with streak bonus.

F2P players can claim a daily reward of Frijolitos (FRJ) once per calendar day
in America/Mexico_City timezone (UTC-6). The reward increases with consecutive
daily claims, up to a maximum streak of 7 days.

Streak schedule:
  Day 1: 15 FRJ (base)
  Day 2: 20 FRJ (base + 1 * 5)
  Day 3: 25 FRJ (base + 2 * 5)
  ...
  Day 7: 45 FRJ (base + 6 * 5)  <-- max
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.core.product_policy import require_feature
from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
    Wallet,
)
from app.models.user import User
from app.services.bank_service import BankService

# Timezone for streak calculations (Xochimilco / America/Mexico_City = UTC-6)
MX_TZ = timezone(timedelta(hours=-6))


class DailyRewardService:
    """Service for F2P daily reward claims with streak logic."""

    BASE_REWARD: float = 15.0       # Base FRJ per claim
    STREAK_BONUS: float = 5.0       # Extra FRJ per consecutive day
    MAX_STREAK: int = 7             # Max days for streak bonus

    def calculate_daily_reward(self, user: User) -> dict:
        """
        Calculate the daily reward amount based on the user's claim streak.

        Evaluates the user's `last_f2p_daily_claim_at` against the current
        date in America/Mexico_City to determine whether the streak continues,
        resets, or raises a 429 if already claimed today.

        Args:
            user: The User model instance.

        Returns:
            dict with keys:
                amount (float)    — FRJ to award
                streak (int)      — current streak day (1-7)
                is_streak_max (bool)

        Raises:
            HTTPException 429 if already claimed today (Mexico City time).
        """
        now_mx = datetime.now(timezone.utc).astimezone(MX_TZ)
        today_mx = now_mx.date()

        last_claim = user.last_f2p_daily_claim_at

        if last_claim is not None:
            # Normalize to MX timezone for date comparison
            if last_claim.tzinfo is None:
                last_claim_mx = last_claim.replace(
                    tzinfo=timezone.utc
                ).astimezone(MX_TZ)
            else:
                last_claim_mx = last_claim.astimezone(MX_TZ)

            last_claim_date = last_claim_mx.date()

            if last_claim_date == today_mx:
                raise HTTPException(
                    status_code=429,
                    detail="Ya reclamaste tus Frijolitos diarios hoy.",
                )

            if last_claim_date == today_mx - timedelta(days=1):
                # Consecutive day — increment streak
                streak = user.f2p_daily_claim_streak + 1
            else:
                # Gap of more than 1 day — reset streak to 1
                streak = 1
        else:
            # First ever claim
            streak = 1

        # Cap streak at MAX_STREAK
        streak = min(streak, self.MAX_STREAK)

        # Calculate reward
        bonus = (streak - 1) * self.STREAK_BONUS
        amount = self.BASE_REWARD + bonus

        return {
            "amount": amount,
            "streak": streak,
            "is_streak_max": streak >= self.MAX_STREAK,
        }

    def claim_daily_reward(self, db: Session, user: User) -> dict:
        """
        Claim the daily F2P reward.

        Adds FRJ to the user's wallet, records a TransactionLedger entry with
        type F2P_REWARD, and updates the user's claim tracking fields.

        Args:
            db: SQLModel session.
            user: The User model instance.

        Returns:
            dict with keys: amount, streak, is_streak_max
        """
        require_feature(
            settings.ENABLE_GAMEPLAY_TOKEN_REWARDS,
            "gameplay_token_rewards",
        )

        # Calculate reward (may raise 429 if already claimed today)
        reward = self.calculate_daily_reward(user)

        # Lock wallet for mutation (pessimistic lock)
        wallet = BankService.get_or_create_wallet(
            db, user.privy_did, for_update=True
        )

        # Credit FRJ using canonical field name
        wallet.frijolitos += reward["amount"]
        wallet.last_updated = datetime.utcnow()
        db.add(wallet)

        # Record in TransactionLedger
        ledger_entry = TransactionLedger(
            user_id=user.privy_did,
            amount=reward["amount"],
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.F2P_REWARD,
            description=(
                f"Recompensa diaria F2P: {reward['amount']:.0f} FRJ "
                f"(racha de {reward['streak']} "
                f"{'día' if reward['streak'] == 1 else 'días'})"
            ),
        )
        db.add(ledger_entry)

        # Update user's claim tracking fields
        user.last_f2p_daily_claim_at = datetime.utcnow()
        user.f2p_daily_claim_streak = reward["streak"]
        db.add(user)

        db.commit()

        return reward
