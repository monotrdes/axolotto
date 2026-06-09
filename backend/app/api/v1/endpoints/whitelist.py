from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.core.auth import get_verified_user_id
from app.models.items import WhitelistEntry

router = APIRouter()


class WhitelistRegisterRequest(BaseModel):
    email: str


@router.post("/register")
def register_whitelist(
    request: WhitelistRegisterRequest,
    verified_user_id: str = Depends(get_verified_user_id),
    session: Session = Depends(get_session),
):
    """Registra al usuario autenticado en la whitelist de Fase 1."""
    existing = session.exec(
        select(WhitelistEntry).where(WhitelistEntry.user_id == verified_user_id)
    ).first()
    if existing:
        return {"message": "Ya estás registrado en la whitelist", "entry": existing}

    entry = WhitelistEntry(
        user_id=verified_user_id,
        email=request.email,
        source="microsite",
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return {"message": "Registrado exitosamente en la whitelist de Fase 1", "entry": entry}
