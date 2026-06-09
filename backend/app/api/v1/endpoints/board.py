import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from app.database import get_session
from app.core.auth import get_verified_user_id
from app.services.board_service import (
    get_user_boards_data,
    create_random_board_operation,
    create_manual_board_operation,
    edit_board_operation,
    delete_board_operation,
    claim_staking_operation,
    claim_all_staking_operation,
    get_rental_market_data,
    list_board_for_rent_operation,
    cancel_rent_listing_operation,
    rent_board_operation,
    get_slot_status_data,
    unlock_slot_operation,
    get_sale_market_data,
    list_board_for_sale_operation,
    cancel_sale_operation,
    buy_board_operation,
)

router = APIRouter()
_rng = random.SystemRandom()

# --- MODELOS DE ENTRADA ---

class CreateManualBoardRequest(BaseModel):
    name: str
    card_ids: List[int]
    card_first_editions: Optional[List[bool]] = None

class EditBoardRequest(BaseModel):
    name: Optional[str] = None
    card_ids: Optional[List[int]] = None

class ListRentRequest(BaseModel):
    rent_fee_gal: float
    rent_share_owner_pct: int

class ListSaleRequest(BaseModel):
    sale_price_gal: float


# --- ENDPOINTS ---

@router.get("/user/{user_id}")
def get_user_boards(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Devuelve las tablas que posee el usuario y las que tiene rentadas actualmente."""
    if user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No autorizado.")
    return get_user_boards_data(user_id, session)


@router.post("/create/random")
def create_random_board(
    payload: CreateManualBoardRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Crea un tablero de Lotería al azar cobrando 25 GAL de comisión."""
    return create_random_board_operation(verified_user_id, payload.name, session)


@router.post("/create/manual")
def create_manual_board(
    payload: CreateManualBoardRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Crea un tablero de Lotería manualmente validando las cartas y cobrando 50 GAL."""
    card_first_editions = payload.card_first_editions
    if not card_first_editions:
        card_first_editions = [False] * 16
    return create_manual_board_operation(
        verified_user_id,
        payload.name,
        payload.card_ids,
        card_first_editions,
        session,
    )


@router.put("/{board_id}/edit")
def edit_board(
    board_id: int,
    payload: EditBoardRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Reconfigura una tabla existente permitiendo SOLO cambiar el nombre de forma gratuita."""
    if payload.card_ids is not None:
        raise HTTPException(
            status_code=400,
            detail="No se pueden cambiar las cartas de una tabla una vez creada para no perder la suerte acumulada.",
        )
    return edit_board_operation(board_id, verified_user_id, payload.name, session)


@router.delete("/{board_id}")
def delete_board(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Desarma y marca como inactiva (dead) la tabla, perdiendo una carta al azar, liberando las otras 15 y cobrando el staking."""
    return delete_board_operation(board_id, verified_user_id, session)


@router.post("/{board_id}/claim-staking")
def claim_board_staking(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Reclama las Gemas Alga acumuladas por el staking de las cartas de esta tabla."""
    return claim_staking_operation(board_id, verified_user_id, session)


@router.post("/claim-staking/all")
def claim_all_boards_staking(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Reclama las Gemas Alga acumuladas por el staking de TODAS las tablas del usuario a la vez."""
    return claim_all_staking_operation(verified_user_id, session)


# --- RENTAS Y MERCADO ---

@router.get("/rent/market")
def get_rental_market_boards(
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Obtiene el listado de tablas publicadas en el mercado que están listas para ser rentadas."""
    return get_rental_market_data(skip, limit, session)


@router.post("/{board_id}/list-rent")
def list_board_for_rent(
    board_id: int,
    payload: ListRentRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Lista un tablero en el mercado de rentas fijando fee y win split."""
    return list_board_for_rent_operation(
        board_id,
        verified_user_id,
        payload.rent_fee_gal,
        payload.rent_share_owner_pct,
        session,
    )


@router.post("/{board_id}/cancel-rent")
def cancel_board_listing(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Retira un tablero del mercado de rentas."""
    return cancel_rent_listing_operation(board_id, verified_user_id, session)


@router.post("/{board_id}/rent")
def rent_board(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Alquila una tabla del mercado de rentas por 24 horas pagando la fee de GAL por adelantado."""
    return rent_board_operation(board_id, verified_user_id, session)


@router.get("/slots/status")
def get_board_slots_status(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Obtiene el estado de slots del usuario (desbloqueados, usados, estadísticas de desbloqueo)."""
    return get_slot_status_data(verified_user_id, session)


@router.post("/slots/unlock")
def unlock_board_slot(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Desbloquea el siguiente slot de tabla cobrando los GAL correspondientes y validando requisitos."""
    return unlock_slot_operation(verified_user_id, session)


# --- VENTAS Y COMPRA P2P ---

@router.get("/sale/market")
def get_sale_market_boards(
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Obtiene el listado de tablas publicadas en el mercado que están en venta."""
    return get_sale_market_data(skip, limit, session)


@router.post("/{board_id}/list-sale")
def list_board_for_sale(
    board_id: int,
    payload: ListSaleRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Publica un tablero en el mercado de venta definitiva."""
    return list_board_for_sale_operation(
        board_id, verified_user_id, payload.sale_price_gal, session
    )


@router.post("/{board_id}/cancel-sale")
def cancel_board_sale(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Cancela la publicación de venta de un tablero."""
    return cancel_sale_operation(board_id, verified_user_id, session)


@router.post("/{board_id}/buy")
def buy_board(
    board_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """Compra un tablero en venta definitiva, realizando la transferencia de GAL y el NFT on-chain."""
    return buy_board_operation(board_id, verified_user_id, session)
