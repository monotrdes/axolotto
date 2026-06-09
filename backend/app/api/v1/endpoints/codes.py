from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.core.auth import get_verified_user_id
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
    return redeem_promo_code(
        session=session,
        user_id=verified_user_id,
        code=request.code,
        email=request.email,
    )
