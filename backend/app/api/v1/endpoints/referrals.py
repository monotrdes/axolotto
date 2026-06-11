"""Referral API endpoints — codes, claiming, dashboard, milestones.

Phase 2 (task-1780974969-59).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional

from sqlmodel import Session, select

from app.database import get_session
from app.core.auth import get_verified_user_id
from app.services.referral_service import ReferralService

router = APIRouter()


# ── Request Schemas ─────────────────────────────────────────────────────────

class ClaimReferralRequest(BaseModel):
    code: str


class MilestoneRequest(BaseModel):
    milestone: str  # "tutorial_done" | "first_game" | "d7_retained" | "converted" | "vip_coral"


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/code")
def get_my_code(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Get (or lazily generate) your unique referral code."""
    code = ReferralService.get_or_create_referral_code(session, verified_user_id)
    return {
        "code": code.code,
        "total_uses": code.total_uses,
        "active_referrals": code.active_referrals,
        "share_link": f"https://axolot.to/join/{code.code}",
    }


@router.post("/claim")
def claim_referral(
    req: ClaimReferralRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Claim a referral code after registration. Grants rewards + auto-friends."""
    return ReferralService.claim_referral(session, req.code, verified_user_id)


@router.post("/milestone")
def report_milestone(
    req: MilestoneRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Report a milestone reached (tutorial done, first game, D7, purchase, VIP).

    Called by the frontend when the user completes tutorial, plays first game, etc.
    Also callable by backend cron jobs.
    """
    valid = {"tutorial_done", "first_game", "d7_retained", "converted", "vip_coral"}
    if req.milestone not in valid:
        raise HTTPException(status_code=400, detail=f"Hito inválido. Válidos: {valid}")
    return ReferralService.process_milestone(session, verified_user_id, req.milestone)


@router.get("/dashboard")
def referral_dashboard(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Get your referral dashboard: code, stats, list of referred users."""
    return ReferralService.get_referral_dashboard(session, verified_user_id)


@router.get("/reward-history")
def reward_history(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Get history of referral rewards earned."""
    from app.models.economy import TransactionLedger, TransactionType
    txs = session.exec(
        select(TransactionLedger).where(
            TransactionLedger.user_id == verified_user_id,
            TransactionLedger.description.ilike("reward_referral_%"),
        ).order_by(TransactionLedger.created_at.desc()).limit(50)
    ).all()
    return [
        {
            "id": tx.id,
            "description": tx.description,
            "amount": tx.amount,
            "currency": tx.currency.value if tx.currency else None,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in txs
    ]
