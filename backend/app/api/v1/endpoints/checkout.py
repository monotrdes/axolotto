"""
checkout.py — Endpoints para compra de AXG con cripto.

Rutas:
  GET  /bank/checkout/packs                    → catálogo de packs con oferta flash
  POST /bank/checkout/crypto                   → crear orden de compra
  GET  /bank/checkout/crypto/{order_id}        → estado de la orden
  POST /bank/checkout/crypto/{order_id}/confirm → confirmar pago (tx_hash)
  GET  /bank/exchange-rate                     → tipo de cambio USD/MXN
"""
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.services.checkout_service import CheckoutService
from app.core.limiter import limiter

router = APIRouter()

# ── Modelos de request ────────────────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    pack_id: str

class ConfirmPaymentRequest(BaseModel):
    tx_hash: str = Field(..., pattern=r"^(0x[0-9a-fA-F]{64}|0x_mock.*)$")

# ── Exchange rate con TTL simple ──────────────────────────────────────────────

_rate_cache: dict = {"rate": 17.5, "updated_at": None}

async def _fetch_usd_mxn() -> float:
    """Obtiene el tipo de cambio USD→MXN. Fallback a 17.5 si falla."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                "https://api.exchangerate-api.com/v4/latest/USD"
            )
            data = res.json()
            return float(data["rates"]["MXN"])
    except Exception:
        return 17.5


def _get_cached_rate() -> float:
    now = datetime.utcnow()
    last = _rate_cache.get("updated_at")
    if last is None or (now - last).total_seconds() > 3600:
        # No podemos await aquí (sync route), devolvemos el último conocido
        return _rate_cache["rate"]
    return _rate_cache["rate"]


# ── Rutas ─────────────────────────────────────────────────────────────────────

@router.get("/packs")
def get_packs() -> Any:
    """Catálogo de packs con precios USD/MXN y oferta flash del día."""
    rate = _get_cached_rate()
    return {
        "packs": CheckoutService.get_packs_info(usd_mxn=rate),
        "usd_mxn": rate,
    }


@router.get("/exchange-rate")
async def get_exchange_rate() -> Any:
    """Tipo de cambio USD→MXN actualizado."""
    rate = await _fetch_usd_mxn()
    _rate_cache["rate"] = rate
    _rate_cache["updated_at"] = datetime.utcnow()
    return {"usd_mxn": rate, "updated_at": datetime.utcnow().isoformat()}


@router.post("/crypto")
@limiter.limit("10/minute")
def create_order(
    request: Request,
    req: CreateOrderRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> Any:
    """Crea una orden de compra. Devuelve la dirección treasury y monto USDC."""
    order = CheckoutService.create_order(
        session=session,
        user_id=verified_user_id,
        pack_id=req.pack_id,
    )
    return {
        "order_id":         order.id,
        "pack_id":          order.pack_id,
        "pay_to":           order.treasury_address,
        "usdc_amount":      order.usdc_amount,
        "axg_amount":       order.axg_amount,
        "bonus_pct":        order.bonus_pct,
        "bonus_applied":    order.bonus_applied,
        "expires_at":       order.expires_at.isoformat(),
        "status":           order.status,
    }


@router.get("/crypto/{order_id}")
def get_order_status(
    order_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> Any:
    """Estado actual de la orden."""
    order = CheckoutService.get_order(session, order_id, verified_user_id)
    return {
        "order_id":       order.id,
        "status":         order.status,
        "pack_id":        order.pack_id,
        "axg_amount":     order.axg_amount,
        "bonus_pct":      order.bonus_pct,
        "tx_hash_payment": order.tx_hash_payment,
        "tx_hash_mint":   order.tx_hash_mint,
        "expires_at":     order.expires_at.isoformat(),
        "completed_at":   order.completed_at.isoformat() if order.completed_at else None,
    }


@router.post("/crypto/{order_id}/confirm")
@limiter.limit("5/minute")
def confirm_payment(
    request: Request,
    order_id: str,
    req: ConfirmPaymentRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> Any:
    """
    El frontend informa el tx_hash después de enviar USDC.
    El backend verifica on-chain y mintea AXG si todo es correcto.
    """
    order = CheckoutService.confirm_payment(
        session=session,
        order_id=order_id,
        user_id=verified_user_id,
        tx_hash=req.tx_hash,
    )
    return {
        "status":       order.status,
        "axg_amount":   order.axg_amount,
        "bonus_pct":    order.bonus_pct,
        "tx_hash_mint": order.tx_hash_mint,
        "polygon_scan": f"https://amoy.polygonscan.com/tx/{order.tx_hash_payment}" if order.tx_hash_payment else None,
    }
