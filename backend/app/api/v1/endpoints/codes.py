from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.core.auth import get_verified_user_id
from app.core.config import settings
from app.core.product_policy import require_feature
from app.services.promo_service import redeem_promo_code

router = APIRouter()


class RedeemRequest(BaseModel):
    code: str
    email: str


@router.post("/redeem")
def redeem_code(
    request: RedeemRequest,
    verified_user_id: str = Depends(get_verified_user_id),
    session: Session = Depends(get_session),
):
    require_feature(
        settings.ENABLE_PROMOTIONAL_TOKEN_REWARDS,
        "promotional_token_rewards",
    )
    return redeem_promo_code(
        session=session,
        user_id=verified_user_id,
        code=request.code,
        email=request.email,
    )
