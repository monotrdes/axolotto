from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlmodel import Session
from pydantic import BaseModel
from typing import Any, Optional

# Importamos tu servicio y modelos
from app.models.economy import CurrencyType
from app.services.bank_service import BankService
from app.database import get_session
from app.core.auth import get_verified_user_id, require_admin
from app.core.config import settings
from app.core.limiter import limiter

router = APIRouter()

# --- ESQUEMAS DE DATOS (Lo que esperamos recibir en la petición) ---
class DepositRequest(BaseModel):
    user_id: str
    amount: float
    currency: CurrencyType
    description: str = "Depósito manual"

class TransferRequest(BaseModel):
    sender_id: str # (Nota: En el futuro esto lo sacaremos automáticamente del Token de Privy)
    receiver_id: str
    amount: float
    currency: CurrencyType

# --- ENDPOINTS (Las Ventanillas) ---

@router.get("/wallet/{user_id}")
def get_my_wallet(
    user_id: str, 
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
) -> Any:
    """Consulta el saldo de un jugador."""
    if user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a los recursos de este usuario.")
    wallet = BankService.get_or_create_wallet(session, user_id)
    return {
        "user_id": wallet.user_id,
        "axofichas": wallet.axofichas,
        "frijolitos": wallet.frijolitos,
        # backward compat — frontend legacy
        "axogemas": wallet.axofichas,
        "gemas_alga": wallet.frijolitos,
        "fragmentos": {
            "comunes": wallet.frag_comun,
            "raros": wallet.frag_raro,
            "epicos": wallet.frag_epico,
            "legendarios": wallet.frag_legendario
        }
    }

@router.post("/admin/deposit")
def admin_deposit_funds(
    req: DepositRequest, 
    session: Session = Depends(get_session),
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    _: str = Depends(require_admin)
) -> Any:
    """Ventanilla oculta: Deposita dinero de la nada (Para pruebas y recargas SPEI)."""
    if not settings.TRIDY_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="La llave administrativa no está configurada en el servidor."
        )
    if x_admin_token != settings.TRIDY_API_KEY:
        raise HTTPException(status_code=403, detail="Llave administrativa inválida.")
    resultado = BankService.admin_deposit(
        session=session,
        user_id=req.user_id,
        amount=req.amount,
        currency=req.currency,
        description=req.description
    )
    return resultado

@router.post("/transfer")
@limiter.limit("5/minute")
def transfer_funds(
    request: Request,
    req: TransferRequest, 
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
) -> Any:
    """Transfiere fondos a un amigo cobrando la comisión de la casa."""
    if req.sender_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No puedes transferir fondos de otro usuario.")
    resultado = BankService.transfer_p2p(
        session=session,
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        amount=req.amount,
        currency=req.currency
    )
    return resultado