"""rewards.py — Endpoints para reclamar premios.

- POST /claim                 — Reclamar premio Corcholata post-tutorial
- GET  /daily-claim/status    — Estado de la recompensa diaria F2P
- POST /daily-claim           — Reclamar recompensa diaria F2P (Frijolitos + racha)
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.economy import CurrencyType, TransactionLedger, TransactionType
from app.models.promo import PendingReward
from app.models.user import User
from app.services.bank_service import BankService
from app.core.limiter import limiter
from app.core.config import axf_to_internal, frj_to_internal, axf_to_display, frj_to_display, settings
from app.core.product_policy import require_feature

router = APIRouter()


@router.post("/claim")
@limiter.limit("5/minute")
def claim_pending_reward(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Reclama el premio Corcholata pendiente después del tutorial."""
    require_feature(
        settings.ENABLE_PROMOTIONAL_TOKEN_REWARDS,
        "promotional_token_rewards",
    )

    pending = session.exec(
        select(PendingReward).where(
            PendingReward.user_id == verified_user_id,
            PendingReward.claimed == False,
        ).with_for_update()
    ).first()

    if not pending:
        raise HTTPException(status_code=404, detail="No tienes premios pendientes")

    if pending.expires_at and pending.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Tu premio ha expirado")

    # ENTREGAR
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)

    reward_axf_int = axf_to_internal(pending.reward_axf)
    reward_frj_int = frj_to_internal(pending.reward_frj)

    wallet.axofichas = (wallet.axofichas or 0) + reward_axf_int
    wallet.frijolitos = (wallet.frijolitos or 0) + reward_frj_int
    wallet.last_updated = datetime.utcnow()
    session.add(wallet)

    # Entregar item si existe
    if pending.reward_item_id is not None:
        from app.models.items import PlayerInventory
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == verified_user_id)
            .where(PlayerInventory.item_id == pending.reward_item_id)
        ).first()
        if inv:
            inv.quantity += 1
        else:
            inv = PlayerInventory(user_id=verified_user_id, item_id=pending.reward_item_id, quantity=1)
        session.add(inv)

    # Registrar en ledger para trazabilidad y métricas de admin
    if reward_axf_int > 0:
        session.add(TransactionLedger(
            user_id=verified_user_id,
            amount=reward_axf_int,
            currency=CurrencyType.AXOFICHA,
            tx_type=TransactionType.PROMO_REWARD,
            description=f"Corcholata reclamada (promo_id={pending.promo_code_id})",
        ))
    if reward_frj_int > 0:
        session.add(TransactionLedger(
            user_id=verified_user_id,
            amount=reward_frj_int,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.PROMO_REWARD,
            description=f"Corcholata reclamada (promo_id={pending.promo_code_id})",
        ))

    # Marcar como reclamado
    pending.claimed = True
    pending.claimed_at = datetime.utcnow()
    session.add(pending)

    session.commit()

    return {
        "status": "claimed",
        "reward": {
            "axofichas": pending.reward_axf,
            "frijolitos": pending.reward_frj,
            "item_id": pending.reward_item_id,
        },
        "wallet": {
            "axofichas": axf_to_display(wallet.axofichas),
            "frijolitos": frj_to_display(wallet.frijolitos),
        },
    }


# ---------------------------------------------------------------------------
# GET /daily-claim/status
# ---------------------------------------------------------------------------

@router.get("/daily-claim/status")
@limiter.limit("30/minute")
def get_daily_claim_status(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    raise HTTPException(status_code=410, detail="Usa GET /api/v1/rewards/lunar/status")


# ---------------------------------------------------------------------------
# POST /daily-claim
# ---------------------------------------------------------------------------

@router.post("/daily-claim")
@limiter.limit("10/minute")
def claim_daily_reward(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    raise HTTPException(status_code=410, detail="Usa POST /api/v1/rewards/lunar/claim")


# ---------------------------------------------------------------------------
# GET /lunar/status  — Ciclo Lunar state
# ---------------------------------------------------------------------------

@router.get("/lunar/status")
@limiter.limit("30/minute")
def get_lunar_status(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    require_feature(
        settings.ENABLE_GAMEPLAY_TOKEN_REWARDS,
        "gameplay_token_rewards",
    )
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    from app.services.lunar_streak_service import get_status
    return get_status(user)


# ---------------------------------------------------------------------------
# POST /lunar/claim  — Reclamar día del Ciclo Lunar
# ---------------------------------------------------------------------------

@router.post("/lunar/claim")
@limiter.limit("10/minute")
def claim_lunar_day(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    require_feature(
        settings.ENABLE_GAMEPLAY_TOKEN_REWARDS,
        "gameplay_token_rewards",
    )
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    from app.services.lunar_streak_service import claim
    return claim(session, user)
