from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_session
from app.core.auth import get_verified_user_id
from app.core.limiter import limiter

from app.services.user_service import (
    sync_user as _sync_user,
    get_user_inventory as _get_user_inventory,
    get_user_axolotitos as _get_user_axolotitos,
    update_axolotito_bot_config as _update_bot_config,
    get_sale_market_axolotitos as _get_sale_market,
    get_rent_market_axolotitos as _get_rent_market,
    list_axolotito_for_sale as _list_for_sale,
    cancel_axolotito_sale as _cancel_sale,
    list_axolotito_for_rent as _list_for_rent,
    cancel_axolotito_rent as _cancel_rent,
    get_vip_status as _get_vip_status,
    claim_vip_frj as _claim_vip_frj,
    set_vip_auto_renew as _set_vip_auto_renew,
    rent_axolotito as _rent_axolotito,
    buy_axolotito as _buy_axolotito,
    equip_accessory as _equip_accessory,
    unequip_accessory as _unequip_accessory,
    set_main_axolotito as _set_main,
)

router = APIRouter()


# ─── ESQUEMAS DE DATOS ───────────────────────────────────────────────────────

class SyncUserRequest(BaseModel):
    privy_did: str
    email: Optional[str] = None
    wallet_address: Optional[str] = None


class BotConfigRequest(BaseModel):
    user_id: str
    bot_enabled: bool
    bot_budget_axf: float
    bot_loss_limit_axf: float
    bot_profit_limit_axf: float
    assigned_board_id: Optional[int] = None


class ListAxoSaleRequest(BaseModel):
    sale_price_gal: float


class ListAxoRentRequest(BaseModel):
    rent_fee_gal: float
    rent_share_owner_pct: int


class EquipRequest(BaseModel):
    item_id: int
    slot: str  # "head", "eyes", "body"


class UnequipRequest(BaseModel):
    slot: str  # "head", "eyes", "body"


class AutoRenewRequest(BaseModel):
    enabled: bool


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/sync")
@limiter.limit("10/minute")
def sync_user(
    request: Request,
    req: SyncUserRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _sync_user(
        session,
        privy_did=req.privy_did,
        email=req.email,
        wallet_address=req.wallet_address,
        verified_user_id=verified_user_id,
    )


@router.get("/inventory/{user_id}")
def get_user_inventory(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _get_user_inventory(session, user_id, verified_user_id)


@router.get("/axolotitos/{user_id}")
def get_user_axolotitos(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _get_user_axolotitos(session, user_id, verified_user_id)


@router.post("/axolotitos/{axolotito_id}/bot-config")
def update_axolotito_bot_config(
    axolotito_id: int,
    req: BotConfigRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _update_bot_config(
        session,
        axolotito_id=axolotito_id,
        bot_enabled=req.bot_enabled,
        bot_budget_axf=req.bot_budget_axf,
        bot_loss_limit_axf=req.bot_loss_limit_axf,
        bot_profit_limit_axf=req.bot_profit_limit_axf,
        assigned_board_id=req.assigned_board_id,
        verified_user_id=verified_user_id,
        user_id_from_body=req.user_id,
    )


@router.get("/axolotitos/market/sale")
def get_sale_market_axolotitos(
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    return _get_sale_market(session, skip=skip, limit=limit)


@router.get("/axolotitos/market/rent")
def get_rent_market_axolotitos(
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    return _get_rent_market(session, skip=skip, limit=limit)


@router.post("/axolotitos/{axolotito_id}/list-sale")
def list_axolotito_for_sale(
    axolotito_id: int,
    payload: ListAxoSaleRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _list_for_sale(
        session,
        axolotito_id=axolotito_id,
        sale_price_gal=payload.sale_price_gal,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axolotito_id}/cancel-sale")
def cancel_axolotito_sale(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _cancel_sale(session, axolotito_id=axolotito_id, verified_user_id=verified_user_id)


@router.post("/axolotitos/{axolotito_id}/list-rent")
def list_axolotito_for_rent(
    axolotito_id: int,
    payload: ListAxoRentRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _list_for_rent(
        session,
        axolotito_id=axolotito_id,
        rent_fee_gal=payload.rent_fee_gal,
        rent_share_owner_pct=payload.rent_share_owner_pct,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axolotito_id}/cancel-rent")
def cancel_axolotito_rent(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _cancel_rent(session, axolotito_id=axolotito_id, verified_user_id=verified_user_id)


@router.get("/vip-status")
def get_vip_status(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _get_vip_status(session, verified_user_id)


@router.post("/vip/claim-daily-frj")
def claim_vip_frj(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _claim_vip_frj(session, verified_user_id)


@router.post("/vip/auto-renew")
def set_vip_auto_renew(
    req: AutoRenewRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _set_vip_auto_renew(session, enabled=req.enabled, verified_user_id=verified_user_id)


@router.post("/axolotitos/{axolotito_id}/rent")
def rent_axolotito(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _rent_axolotito(session, axolotito_id=axolotito_id, verified_user_id=verified_user_id)


@router.post("/axolotitos/{axolotito_id}/buy")
def buy_axolotito(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _buy_axolotito(session, axolotito_id=axolotito_id, verified_user_id=verified_user_id)


@router.post("/axolotitos/{axolotito_id}/equip")
def equip_accessory(
    axolotito_id: int,
    req: EquipRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _equip_accessory(
        session,
        axolotito_id=axolotito_id,
        item_id=req.item_id,
        slot=req.slot,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axolotito_id}/unequip")
def unequip_accessory(
    axolotito_id: int,
    req: UnequipRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _unequip_accessory(
        session,
        axolotito_id=axolotito_id,
        slot=req.slot,
        verified_user_id=verified_user_id,
    )


@router.post("/axolotitos/{axolotito_id}/set-main")
def set_axolotito_as_main(
    axolotito_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    return _set_main(session, axolotito_id=axolotito_id, verified_user_id=verified_user_id)
