import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session

from app.database import get_session
from app.core.auth import get_verified_user_id, require_admin
from app.core.config import settings
from app.core.product_policy import require_feature, require_legacy_local
from app.services.admin_service import (
    SimRunParams,
    ChaosRunParams,
    check_admin_status,
    get_overview,
    get_players,
    get_player_detail,
    get_economy_charts,
    get_simulation_report,
    get_simulation_status,
    run_simulation,
    get_chaos_simulation_report,
    get_chaos_simulation_status,
    run_chaos_simulation,
    get_card_distribution,
    adjust_player_balance,
    require_admin_balance_policy,
    grant_player_vip,
    override_player_tutorial,
    toggle_player_status,
    get_promo_batches,
    PromoBatchCreate,
    create_promo_batch,
    export_promo_batch_csv,
)
from pydantic import BaseModel

logger = logging.getLogger("admin")
router = APIRouter()


@router.get("/me")
def admin_me(user_id: str = Depends(get_verified_user_id)):
    return check_admin_status(user_id)


@router.get("/overview")
def admin_overview(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_overview(session)


@router.get("/players")
def admin_players(
    search: Optional[str] = None,
    sort: str = "created_at_desc",
    page: int = 1,
    limit: int = 50,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_players(session, search=search, sort=sort, page=page, limit=limit)


@router.get("/players/{player_did}")
def admin_player_detail(
    player_did: str,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_player_detail(session, player_did)


@router.get("/economy/charts")
def admin_economy_charts(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_economy_charts(session)


@router.get("/simulation/report")
def admin_simulation_report(_: str = Depends(require_admin)):
    return get_simulation_report()


@router.get("/simulation/status")
def admin_simulation_status(_: str = Depends(require_admin)):
    return get_simulation_status()


@router.post("/simulation/run")
def admin_run_simulation(
    params: SimRunParams,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_admin),
):
    require_legacy_local("admin_simulation")
    return run_simulation(params, background_tasks)


# ── Chaos & Security Simulator v2 routes ────────────────────────────────────

@router.get("/simulation/chaos/report")
def admin_chaos_simulation_report(_: str = Depends(require_admin)):
    return get_chaos_simulation_report()


@router.get("/simulation/chaos/status")
def admin_chaos_simulation_status(_: str = Depends(require_admin)):
    return get_chaos_simulation_status()


@router.post("/simulation/chaos/run")
def admin_run_chaos_simulation(
    params: ChaosRunParams,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_admin),
):
    require_legacy_local("admin_chaos_simulation")
    return run_chaos_simulation(params, background_tasks)


@router.get("/cards/distribution")
def admin_card_distribution(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_card_distribution(session)


class AdjustBalanceRequest(BaseModel):
    currency: str
    amount: float
    reason: str


class GrantVipRequest(BaseModel):
    tier: str
    duration_days: int


class TutorialOverrideRequest(BaseModel):
    action: str


class ToggleStatusRequest(BaseModel):
    is_active: bool


@router.post("/players/{player_did}/adjust-balance")
def admin_adjust_balance(
    player_did: str,
    payload: AdjustBalanceRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    require_admin_balance_policy(payload.currency, payload.amount)
    return adjust_player_balance(session, player_did, payload.currency, payload.amount, payload.reason)


@router.post("/players/{player_did}/grant-vip")
def admin_grant_vip(
    player_did: str,
    payload: GrantVipRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    if payload.tier != "none":
        require_feature(settings.ENABLE_VIP_SALES, "vip_sales")
    return grant_player_vip(session, player_did, payload.tier, payload.duration_days)


@router.post("/players/{player_did}/tutorial-override")
def admin_tutorial_override(
    player_did: str,
    payload: TutorialOverrideRequest,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    require_feature(
        settings.ENABLE_GAMEPLAY_TOKEN_REWARDS,
        "gameplay_token_rewards",
    )
    require_feature(settings.ENABLE_HATCHING, "hatching")
    require_feature(
        settings.ENABLE_BOARD_ASSET_MUTATIONS,
        "board_asset_mutations",
    )
    return override_player_tutorial(session, player_did, payload.action)


@router.post("/players/{player_did}/toggle-status")
def admin_toggle_status(
    player_did: str,
    payload: ToggleStatusRequest,
    _: str = Depends(require_admin),
):
    return toggle_player_status(player_did, payload.is_active)


@router.get("/promo/batches")
def admin_get_promo_batches(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_promo_batches(session)


@router.post("/promo/batches")
def admin_create_promo_batch(
    payload: PromoBatchCreate,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    require_feature(
        settings.ENABLE_PROMOTIONAL_TOKEN_REWARDS,
        "promotional_token_rewards",
    )
    return create_promo_batch(session, payload)


@router.get("/promo/batches/{batch_name}/export")
def admin_export_promo_batch(
    batch_name: str,
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return export_promo_batch_csv(session, batch_name)
