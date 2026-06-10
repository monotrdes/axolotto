"""staking.py — Endpoints para Staking de Axolotitos.

Permite consultar el estado de staking pasivo, reclamar recompensas
individuales o en lote.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id
from app.core.limiter import limiter
from app.database import get_session
from app.models.axolotito import Axolotito
from app.models.user import User
from app.services.staking_service import StakingService

from datetime import datetime

router = APIRouter()


@router.get("/status")
@limiter.limit("30/minute")
def get_staking_status(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Return staking status for all of the authenticated user's Axolotitos."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    axolotitos = session.exec(
        select(Axolotito).where(Axolotito.user_id == verified_user_id)
    ).all()

    if not axolotitos:
        return {
            "user_id": verified_user_id,
            "staking_active": False,
            "slots_total": StakingService.get_staking_slots(user),
            "slots_used": 0,
            "axolotitos": [],
            "message": "No tienes Axolotitos para staking.",
        }

    return StakingService.get_staking_status(user, list(axolotitos))


@router.post("/claim/{axolotito_id}")
@limiter.limit("10/minute")
def claim_staking(
    request: Request,
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Claim staking reward for a single Axolotito."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return StakingService.claim_staking_reward(session, axolotito_id, user)


@router.post("/claim-all")
@limiter.limit("5/minute")
def claim_all_staking(
    request: Request,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Claim staking rewards for ALL of the user's Axolotitos at once."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return StakingService.claim_all_staking(session, user)


@router.post("/stake/{axolotito_id}")
@limiter.limit("10/minute")
def stake_axolotito(
    request: Request,
    axolotito_id: int,
    status: str = "studying",
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Pone a un Axolotito en staking (studying o resting)."""
    if status not in ["studying", "resting"]:
        raise HTTPException(
            status_code=400,
            detail="Status de staking inválido. Debe ser 'studying' o 'resting'."
        )

    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    axolotito = session.exec(
        select(Axolotito).where(Axolotito.id == axolotito_id)
    ).first()
    if not axolotito:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axolotito.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="Este Axolotito no te pertenece.")

    if axolotito.status in ["studying", "resting"]:
        raise HTTPException(
            status_code=400,
            detail=f"Este Axolotito ya está en staking ({axolotito.status})."
        )
    if axolotito.status != "idle":
        raise HTTPException(
            status_code=400,
            detail=f"El Axolotito no está ocioso (status actual: {axolotito.status})."
        )

    # Check slots
    staked_count = len(session.exec(
        select(Axolotito)
        .where(Axolotito.user_id == verified_user_id)
        .where(Axolotito.status.in_(["studying", "resting"]))
    ).all())

    max_slots = StakingService.get_staking_slots(user)
    if staked_count >= max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de slots de staking alcanzado ({staked_count}/{max_slots}). Mejora tu cueva para desbloquear más."
        )

    axolotito.status = status
    axolotito.last_staking_claim = datetime.utcnow()
    axolotito.accrued_unclaimed = 0

    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    return {
        "message": f"Axolotito #{axolotito_id} puesto en staking ({status}).",
        "axolotito": {
            "id": axolotito.id,
            "name": axolotito.name,
            "status": axolotito.status,
            "last_staking_claim": axolotito.last_staking_claim.isoformat() if axolotito.last_staking_claim else None,
        }
    }


@router.post("/unstake/{axolotito_id}")
@limiter.limit("10/minute")
def unstake_axolotito(
    request: Request,
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Saca a un Axolotito de staking tras cobrar las recompensas acumuladas."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    axolotito = session.exec(
        select(Axolotito).where(Axolotito.id == axolotito_id)
    ).first()
    if not axolotito:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
    if axolotito.user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="Este Axolotito no te pertenece.")

    if axolotito.status not in ["studying", "resting"]:
        raise HTTPException(
            status_code=400,
            detail="Este Axolotito no está en staking."
        )

    # Claim rewards first (this locks wallet, adds FRJ, resets timers)
    claim_result = StakingService.claim_staking_reward(session, axolotito_id, user)

    # Reload / update status to idle
    axolotito.status = "idle"
    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    return {
        "message": f"Axolotito #{axolotito_id} sacado de staking.",
        "claimed_frj": claim_result.get("claimed_frj", 0.0),
        "axolotito": {
            "id": axolotito.id,
            "name": axolotito.name,
            "status": axolotito.status,
        }
    }
