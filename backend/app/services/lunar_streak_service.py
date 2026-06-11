"""lunar_streak_service.py — Ciclo Lunar unified F2P reward system.

Replaces two separate mechanics (DailyRewardService + capsule daily claim)
with a single 3-loop system:
  Loop 1 (daily): Days 1-6 give FRJ. Day 7 gives capsule(s) based on Luna.
  Loop 2 (weekly): Completing 7 days advances the Luna (1→2→...→6).
  Loop 3 (cycle): Completing Luna 6 closes a cycle, resets to Luna 1.

Inactivity rule: if lunar_last_claim_at is >7 calendar days ago (MX time),
reset lunar_week to 1 and lunar_streak_day to 0 before processing.

Miss-a-day rule: gap of >1 day (but ≤7) resets lunar_streak_day to 0
(restarts the current week) WITHOUT resetting lunar_week.
"""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session

from app.models.economy import CurrencyType, TransactionLedger, TransactionType, Wallet
from app.models.user import User
from app.services.bank_service import BankService
from app.services.capsule_service import _roll_capsule

MX_TZ = timezone(timedelta(hours=-6))

DAILY_FRJ: list[float] = [50, 65, 80, 95, 110, 130]  # index 0=day1 ... 5=day6

LUNA_REWARDS: dict[int, list[dict]] = {
    1: [{"tier": "bronce", "qty": 1}],
    2: [{"tier": "bronce", "qty": 2}],
    3: [{"tier": "plata",  "qty": 1}],
    4: [{"tier": "plata",  "qty": 1}, {"tier": "bronce", "qty": 1}],
    5: [{"tier": "plata",  "qty": 2}],
    6: [{"tier": "oro",    "qty": 1}],
}

LUNA_REWARD_LABELS: dict[int, str] = {
    1: "1× Bronce",
    2: "2× Bronce",
    3: "1× Plata",
    4: "Plata + Bronce",
    5: "2× Plata",
    6: "1× Oro ✨",
}

INACTIVITY_RESET_DAYS = 7


def _apply_inactivity_reset(user: User) -> None:
    if user.lunar_last_claim_at is None:
        return

    last_claim_aware = (
        user.lunar_last_claim_at.replace(tzinfo=timezone.utc)
        if user.lunar_last_claim_at.tzinfo is None
        else user.lunar_last_claim_at
    )
    last_claim_date = last_claim_aware.astimezone(MX_TZ).date()
    today_date = datetime.now(timezone.utc).astimezone(MX_TZ).date()
    days_gap = (today_date - last_claim_date).days

    if days_gap > INACTIVITY_RESET_DAYS:
        user.lunar_week = 1
        user.lunar_streak_day = 0
    elif days_gap > 1:
        user.lunar_streak_day = 0


def _can_claim_today(user: User) -> bool:
    if user.lunar_last_claim_at is None:
        return True

    last_claim_aware = (
        user.lunar_last_claim_at.replace(tzinfo=timezone.utc)
        if user.lunar_last_claim_at.tzinfo is None
        else user.lunar_last_claim_at
    )
    last_claim_date = last_claim_aware.astimezone(MX_TZ).date()
    today_date = datetime.now(timezone.utc).astimezone(MX_TZ).date()
    return last_claim_date != today_date


def get_status(user: User) -> dict:
    # Compute effective state for display — read-only, no mutation
    effective_day = user.lunar_streak_day
    effective_week = user.lunar_week
    last = user.lunar_last_claim_at
    if last is not None:
        last_utc = last.replace(tzinfo=timezone.utc) if last.tzinfo is None else last
        last_mx = last_utc.astimezone(MX_TZ)
        today_mx = datetime.now(timezone.utc).astimezone(MX_TZ)
        gap = (today_mx.date() - last_mx.date()).days
        if gap > INACTIVITY_RESET_DAYS:
            effective_week = 1
            effective_day = 0
        elif gap > 1:
            effective_day = 0

    can_claim = _can_claim_today(user)
    next_day = effective_day + 1

    if next_day <= 6:
        today_reward = {
            "type": "frj",
            "amount": DAILY_FRJ[next_day - 1],
            "capsules": None,
        }
    else:
        today_reward = {
            "type": "capsule",
            "amount": None,
            "capsules": LUNA_REWARDS[effective_week],
        }

    next_claim_at = None
    if not can_claim and user.lunar_last_claim_at is not None:
        last_claim_aware = (
            user.lunar_last_claim_at.replace(tzinfo=timezone.utc)
            if user.lunar_last_claim_at.tzinfo is None
            else user.lunar_last_claim_at
        )
        last_claim_mx = last_claim_aware.astimezone(MX_TZ)
        next_day_mx = last_claim_mx.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        next_claim_at = next_day_mx.astimezone(timezone.utc).isoformat()

    luna_track = [
        {
            "luna": i,
            "completed": i < effective_week,
            "is_current": i == effective_week,
            "reward_label": LUNA_REWARD_LABELS[i],
        }
        for i in range(1, 7)
    ]

    return {
        "lunar_week": effective_week,
        "streak_day": effective_day,
        "can_claim": can_claim,
        "today_reward": today_reward,
        "day7_reward": {
            "capsules": LUNA_REWARDS[effective_week],
            "label": LUNA_REWARD_LABELS[effective_week],
        },
        "next_claim_at": next_claim_at,
        "luna_track": luna_track,
        "cycles_completed": user.lunar_cycles_completed,
    }


def claim(db: Session, user: User) -> dict:
    from app.core.auth import require_tutorial
    require_tutorial(user)

    _apply_inactivity_reset(user)

    if not _can_claim_today(user):
        raise HTTPException(status_code=429, detail="Ya reclamaste hoy tu recompensa del Ciclo Lunar.")

    next_day = user.lunar_streak_day + 1

    if next_day <= 6:
        amount = DAILY_FRJ[next_day - 1]
        wallet = BankService.get_or_create_wallet(db, user.privy_did, for_update=True)
        wallet.frijolitos += amount
        db.add(wallet)

        db.add(TransactionLedger(
            user_id=user.privy_did,
            amount=amount,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.F2P_REWARD,
            description=f"Ciclo Lunar Día {next_day}: {amount:.0f} FRJ",
        ))

        user.lunar_streak_day = next_day
        user.lunar_last_claim_at = datetime.utcnow()
        db.add(user)
        db.commit()

        return {
            "type": "frj",
            "amount": amount,
            "streak_day": user.lunar_streak_day,
            "lunar_week": user.lunar_week,
            "cycles_completed": user.lunar_cycles_completed,
        }

    # next_day == 7: capsule day
    BankService.get_or_create_wallet(db, user.privy_did, for_update=True)
    current_luna = user.lunar_week
    reward_entries = LUNA_REWARDS[current_luna]
    rolls = []
    for entry in reward_entries:
        for _ in range(entry["qty"]):
            result = _roll_capsule(entry["tier"], user.privy_did, db)
            rolls.append(result)

    db.add(TransactionLedger(
        user_id=user.privy_did,
        amount=0,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.F2P_REWARD,
        description=f"Día 7 — Luna {current_luna}: {LUNA_REWARD_LABELS[current_luna]}",
    ))

    user.lunar_streak_day = 0

    was_cycle_complete = current_luna == 6
    if current_luna < 6:
        user.lunar_week = current_luna + 1
    else:
        user.lunar_week = 1
        user.lunar_cycles_completed += 1

    user.lunar_last_claim_at = datetime.utcnow()
    db.add(user)
    db.commit()

    return {
        "type": "capsule",
        "rolls": rolls,
        "streak_day": user.lunar_streak_day,
        "lunar_week": user.lunar_week,
        "cycles_completed": user.lunar_cycles_completed,
        "cycle_complete": was_cycle_complete,
    }
