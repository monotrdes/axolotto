import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session

from app.database import get_session
from app.core.auth import get_verified_user_id, require_admin
from app.services.admin_service import (
    SimRunParams,
    check_admin_status,
    get_overview,
    get_players,
    get_player_detail,
    get_economy_charts,
    get_simulation_report,
    get_simulation_status,
    run_simulation,
    get_card_distribution,
)

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
    return run_simulation(params, background_tasks)


@router.get("/cards/distribution")
def admin_card_distribution(
    _: str = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return get_card_distribution(session)
