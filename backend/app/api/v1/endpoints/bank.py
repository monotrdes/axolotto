from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlmodel import Session
from pydantic import BaseModel
from typing import Any, Optional

from app.models.economy import CurrencyType
from app.services.bank_service import BankService
from app.database import get_session
from app.core.auth import get_verified_user_id, require_admin, verify_no_active_game
from app.core.config import settings, axf_to_internal, frj_to_internal, axf_to_display, frj_to_display
from app.core.economy_types import AxfAmount, FrjAmount
from app.core.limiter import limiter

router = APIRouter()

# --- ESQUEMAS DE DATOS ---

class DepositRequest(BaseModel):
    user_id: str
    amount: float  # humano-legible, endpoint convierte según currency
    currency: CurrencyType
    description: str = "Depósito manual"

class TransferRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float  # humano-legible, endpoint convierte según currency
    currency: CurrencyType

# --- ESQUEMAS DE RESPUESTA (VULN-06: tipos con serializer automático) ---

class WalletResponse(BaseModel):
    user_id: str
    axofichas: float  # serializado desde int por el endpoint
    frijolitos: float
    fragmentos: dict

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
        "axofichas": axf_to_display(wallet.axofichas),
        "frijolitos": frj_to_display(wallet.frijolitos),
        "tickets_reciclon": wallet.tickets_reciclon,
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
    # VULN-06: convertir monto humano → unidad mínima entera
    if req.currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA):
        amount_int = axf_to_internal(req.amount)
    elif req.currency in (CurrencyType.GEMA_ALGA, CurrencyType.FRIJOLITO):
        amount_int = frj_to_internal(req.amount)
    else:
        amount_int = int(req.amount)  # fragmentos ya son enteros
    resultado = BankService.admin_deposit(
        session=session,
        user_id=req.user_id,
        amount=amount_int,
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
    verified_user_id: str = Depends(verify_no_active_game)
) -> Any:
    """Transfiere fondos a un amigo cobrando la comisión de la casa."""
    if req.sender_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No puedes transferir fondos de otro usuario.")
    # VULN-06: convertir monto humano → unidad mínima entera
    if req.currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA):
        amount_int = axf_to_internal(req.amount)
    elif req.currency in (CurrencyType.GEMA_ALGA, CurrencyType.FRIJOLITO):
        amount_int = frj_to_internal(req.amount)
    else:
        amount_int = int(req.amount)
    resultado = BankService.transfer_p2p(
        session=session,
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        amount=amount_int,
        currency=req.currency
    )
    return resultado