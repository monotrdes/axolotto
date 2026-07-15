from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.core.auth import get_verified_user_id, verify_no_active_game
from app.core.config import frj_to_internal, settings
from app.core.product_policy import require_feature
from app.services.game_service import GameService
from app.services.cave_service import get_cave, equip_cave_item, unequip_cave_item

router = APIRouter()

# --- INPUT SCHEMAS ---
class PlayRequest(BaseModel):
    axolotito_id: int
    room_name: str  # "rookie" or "champion"
    bot_enabled: bool = False
    bot_budget_gal: float = 0.0
    bot_loss_limit_pct: float = 0.0
    bot_profit_limit_pct: float = 0.0
    multiplier: int = 1

class FeedRequest(BaseModel):
    food_type: str  # "pellet" or "shrimp"

class CaveEquipRequest(BaseModel):
    item_id: int

class CaveUnequipRequest(BaseModel):
    item_id: int


@router.post("/play")
def play_match(
    req: PlayRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game)
):
    """Simulates a CPU match under the active free or legacy paid policy."""
    require_feature(
        settings.ENABLE_FREE_GAMEPLAY or settings.ENABLE_PAID_GAMEPLAY,
        "cpu_gameplay",
    )
    return GameService.play_match(
        axolotito_id=req.axolotito_id,
        room_name=req.room_name,
        multiplier=req.multiplier,
        bot_enabled=req.bot_enabled,
        bot_budget_gal=frj_to_internal(req.bot_budget_gal),
        bot_loss_limit_pct=int(req.bot_loss_limit_pct),   # porcentaje, NO monetario
        bot_profit_limit_pct=int(req.bot_profit_limit_pct),  # porcentaje, NO monetario
        session=session,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axo_id}/feed")
def feed_axolotito(
    axo_id: int,
    req: FeedRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game)
):
    """Feeds an Axolotito, deducting FRJ from wallet and restoring energy."""
    return GameService.feed_axolotito(
        axo_id=axo_id,
        food_type=req.food_type,
        session=session,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axo_id}/sleep")
def sleep_axolotito(
    axo_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game)
):
    """Puts an Axolotito to sleep to restore full energy for free after a short cooldown."""
    return GameService.sleep_axolotito(
        axo_id=axo_id,
        session=session,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axo_id}/wake")
def wake_axolotito(
    axo_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game)
):
    """Wakes up an Axolotito from sleep, restoring full energy if cooldown expired."""
    return GameService.wake_axolotito(
        axo_id=axo_id,
        session=session,
        verified_user_id=verified_user_id,
    )


# ---------------------------------------------------------------------------
# CAVE (CUEVA) ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/axolotitos/{axo_id}/cave")
def get_cave_endpoint(
    axo_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Returns current cave items and slot capacity for an axolotito."""
    return get_cave(axo_id, session, verified_user_id)


@router.post("/axolotitos/{axo_id}/cave/equip")
def equip_cave_item_endpoint(
    axo_id: int,
    req: CaveEquipRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Equips a cave item from the player's inventory into the axolotito's cave."""
    return equip_cave_item(axo_id, req.item_id, session, verified_user_id)


@router.post("/axolotitos/{axo_id}/cave/unequip")
def unequip_cave_item_endpoint(
    axo_id: int,
    req: CaveUnequipRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Removes a cave item from the axolotito's cave and returns it to the player's inventory."""
    return unequip_cave_item(axo_id, req.item_id, session, verified_user_id)
