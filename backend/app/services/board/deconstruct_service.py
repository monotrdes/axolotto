"""Board rental and sale market operations."""
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.models.board import PlayerBoard
from app.models.user import User
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.lobby_models import TreasuryVault
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.services.board.staking_service import get_board_csr
from app.core.config import FRJ_DECIMALS_BACKEND, frj_to_internal, settings
from app.core.product_policy import require_feature
from app.core.account_policy import require_account_capability


# ─── Rental market ───────────────────────────────────────────────────────

def _build_rental_board_response(
    board: PlayerBoard, session: Session
) -> dict:
    """Construye el dict de respuesta para una tabla en el mercado de rentas."""
    csr = get_board_csr(board)
    if csr >= 35.0:
        suerte_tag = "\U0001f340 Muy Suertuda"
    elif csr <= 15.0:
        suerte_tag = "\U0001f9c2 Salada"
    else:
        suerte_tag = "⚙️ Normal"

    win_rate = (
        (board.games_won / board.games_played * 100)
        if board.games_played > 0
        else 0.0
    )

    owner = session.exec(
        select(User).where(User.privy_did == board.user_id)
    ).first()
    owner_vip_tier = owner.vip_tier if (owner and owner.is_vip) else None

    return {
        "id": board.id,
        "owner_id": board.user_id,
        "owner_vip_tier": owner_vip_tier,
        "name": board.name,
        "card_ids": board.card_ids,
        "games_played": board.games_played,
        "games_won": board.games_won,
        "win_rate": round(win_rate, 1),
        "level": board.level,
        "xp": board.xp,
        "csr": round(csr, 1),
        "suerte_tag": suerte_tag,
        "rent_fee_gal": board.rent_fee_gal,
        "rent_share_owner_pct": board.rent_share_owner_pct,
    }


def get_rental_market_data(skip: int, limit: int, session: Session) -> list:
    """Obtiene el listado de tablas publicadas en el mercado que están listas para ser rentadas."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    now = datetime.utcnow()

    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.is_listed_for_rent == True)
        .where(PlayerBoard.is_dead == False)
        .where(PlayerBoard.is_frozen_by_vip == False)
        .where(
            (PlayerBoard.is_rented == False)
            | (PlayerBoard.rent_expires_at == None)
            | (PlayerBoard.rent_expires_at <= now)
        )
        .offset(skip)
        .limit(limit)
    ).all()

    return [_build_rental_board_response(b, session) for b in boards]


def list_board_for_rent_operation(
    board_id: int,
    user_id: str,
    rent_fee_gal: float,
    rent_share_owner_pct: int,
    session: Session,
) -> dict:
    """Lista un tablero en el mercado de rentas fijando fee y win split."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    require_account_capability(user, "can_use_marketplace")
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No eres el dueño de esta tabla."
        )
    if board.is_tutorial:
        raise HTTPException(
            status_code=400, detail="La Tabla Tutorial no se puede rentar."
        )
    if board.is_dead:
        raise HTTPException(
            status_code=400, detail="Esta tabla está desarmada (muerta)."
        )
    if board.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Esta tabla está congelada. Renueva tu VIP para desbloquearla.",
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400, detail="Esta tabla ya está bajo una renta activa."
        )
    if rent_share_owner_pct < 0 or rent_share_owner_pct > 100:
        raise HTTPException(
            status_code=400,
            detail="El porcentaje de win split debe ser de 0 a 100.",
        )

    board.is_listed_for_rent = True
    board.rent_fee_gal = rent_fee_gal
    board.rent_share_owner_pct = rent_share_owner_pct

    session.add(board)
    session.commit()

    return {
        "mensaje": f"Tabla '{board.name}' listada con éxito en el mercado de rentas.",
        "rent_fee_gal": board.rent_fee_gal,
        "rent_share_owner_pct": board.rent_share_owner_pct,
    }


def cancel_rent_listing_operation(
    board_id: int, user_id: str, session: Session
) -> dict:
    """Retira un tablero del mercado de rentas."""
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No eres el dueño de esta tabla."
        )
    if board.is_dead:
        raise HTTPException(
            status_code=400, detail="Esta tabla está desarmada (muerta)."
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="No puedes cancelar el listado si la tabla ya está rentada.",
        )

    board.is_listed_for_rent = False

    session.add(board)
    session.commit()

    return {
        "mensaje": f"Tabla '{board.name}' retirada del mercado de rentas."
    }


def rent_board_operation(
    board_id: int, user_id: str, session: Session
) -> dict:
    """Alquila una tabla del mercado de rentas por 24 horas pagando la fee de GAL por adelantado."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    require_account_capability(user, "can_use_marketplace")
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Esta tabla está congelada. Renueva tu VIP para desbloquearla.",
        )
    if board.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="No puedes rentar tu propia tabla."
        )
    if board.is_dead:
        raise HTTPException(
            status_code=400, detail="Esta tabla está desarmada (muerta)."
        )
    if not board.is_listed_for_rent:
        raise HTTPException(
            status_code=400, detail="Esta tabla no está disponible para renta."
        )

    now = datetime.utcnow()
    if board.is_rented and board.rent_expires_at and board.rent_expires_at <= now:
        board.is_rented = False
        board.renter_id = None

    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="Esta tabla ya está ocupada por otro inquilino.",
        )

    renter_wallet = BankService.get_or_create_wallet(
        session, user_id, for_update=True
    )
    owner_wallet = BankService.get_or_create_wallet(
        session, board.user_id, for_update=True
    )

    fee_internal = frj_to_internal(board.rent_fee_gal)
    if renter_wallet.frijolitos < fee_internal:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo de FRJ insuficiente para rentar esta tabla (requieres {board.rent_fee_gal} FRJ, tienes {frj_to_internal(renter_wallet.frijolitos):.1f} FRJ).",
        )

    burn_amount = int(round(fee_internal * 0.05))
    net_owner_amount = fee_internal - burn_amount

    renter_wallet.frijolitos -= fee_internal
    owner_wallet.frijolitos += net_owner_amount

    ledger_renter = TransactionLedger(
        user_id=user_id,
        amount=fee_internal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Renta de tabla #{board.id} a propietario {board.user_id}",
    )
    ledger_owner = TransactionLedger(
        user_id=board.user_id,
        amount=net_owner_amount,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD,
        description=f"Ingreso de renta recibida por tabla #{board.id} de arrendatario {user_id}",
    )
    ledger_burn = TransactionLedger(
        user_id=board.user_id,
        amount=burn_amount,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.BURN,
        description=f"Comisión de plataforma (5%) por renta de tabla #{board.id}",
    )

    board.is_rented = True
    board.renter_id = user_id
    board.rent_expires_at = now + timedelta(hours=24)

    session.add(renter_wallet)
    session.add(owner_wallet)
    session.add(ledger_renter)
    session.add(ledger_owner)
    session.add(ledger_burn)
    session.add(board)
    session.commit()

    return {
        "mensaje": f"¡Has rentado la tabla '{board.name}' con éxito por 24 horas!",
        "board_id": board.id,
        "rent_expires_at": board.rent_expires_at.isoformat() + "Z",
    }


# ─── Sale market ─────────────────────────────────────────────────────────

def _build_sale_board_response(
    board: PlayerBoard, session: Session
) -> dict:
    """Construye el dict de respuesta para una tabla en el mercado de venta."""
    csr = get_board_csr(board)
    if csr >= 35.0:
        suerte_tag = "\U0001f340 Muy Suertuda"
    elif csr <= 15.0:
        suerte_tag = "\U0001f9c2 Salada"
    else:
        suerte_tag = "⚙️ Normal"

    win_rate = (
        (board.games_won / board.games_played * 100)
        if board.games_played > 0
        else 0.0
    )

    owner = session.exec(
        select(User).where(User.privy_did == board.user_id)
    ).first()
    owner_vip_tier = owner.vip_tier if (owner and owner.is_vip) else None

    return {
        "id": board.id,
        "owner_id": board.user_id,
        "owner_vip_tier": owner_vip_tier,
        "name": board.name,
        "card_ids": board.card_ids,
        "games_played": board.games_played,
        "games_won": board.games_won,
        "win_rate": round(win_rate, 1),
        "level": board.level,
        "xp": board.xp,
        "csr": round(csr, 1),
        "suerte_tag": suerte_tag,
        "sale_price_gal": board.sale_price_gal,
    }


def get_sale_market_data(skip: int, limit: int, session: Session) -> list:
    """Obtiene el listado de tablas publicadas en el mercado que están en venta."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.is_listed_for_sale == True)
        .where(PlayerBoard.is_dead == False)
        .where(PlayerBoard.is_frozen_by_vip == False)
        .offset(skip)
        .limit(limit)
    ).all()

    return [_build_sale_board_response(b, session) for b in boards]


def list_board_for_sale_operation(
    board_id: int,
    user_id: str,
    sale_price_gal: float,
    session: Session,
) -> dict:
    """Publica un tablero en el mercado de venta definitiva."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    require_account_capability(user, "can_publish_for_sale")
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No eres el dueño de esta tabla."
        )
    if board.is_tutorial:
        raise HTTPException(
            status_code=400, detail="La Tabla Tutorial no se puede vender."
        )
    if board.is_dead:
        raise HTTPException(status_code=400, detail="Esta tabla está desarmada.")
    if board.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Esta tabla está congelada. Renueva tu VIP para desbloquearla.",
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400, detail="No puedes vender una tabla que está rentada."
        )
    if board.is_listed_for_rent:
        raise HTTPException(
            status_code=400,
            detail="No puedes vender una tabla publicada en el mercado de rentas. Retírala primero.",
        )
    if sale_price_gal <= 0:
        raise HTTPException(
            status_code=400, detail="El precio de venta debe ser mayor a 0 FRJ."
        )

    board.is_listed_for_sale = True
    board.sale_price_gal = sale_price_gal

    session.add(board)
    session.commit()

    return {
        "mensaje": f"Tabla '{board.name}' publicada en venta por {board.sale_price_gal} FRJ.",
        "sale_price_gal": board.sale_price_gal,
    }


def cancel_sale_operation(
    board_id: int, user_id: str, session: Session
) -> dict:
    """Cancela la publicación de venta de un tablero."""
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No eres el dueño de esta tabla."
        )
    if not board.is_listed_for_sale:
        raise HTTPException(
            status_code=400, detail="Esta tabla no está en venta."
        )

    board.is_listed_for_sale = False
    session.add(board)
    session.commit()
    return {
        "mensaje": f"Publicación de venta para '{board.name}' cancelada con éxito."
    }


def buy_board_operation(
    board_id: int, user_id: str, session: Session
) -> dict:
    """Compra un tablero en venta definitiva, realizando la transferencia de GAL y el NFT on-chain."""
    require_feature(settings.ENABLE_PLAYER_MARKETPLACE, "player_marketplace")
    buyer = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    require_account_capability(buyer, "can_use_marketplace")
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Esta tabla está congelada. Renueva tu VIP para desbloquearla.",
        )
    if board.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="No puedes comprar tu propio tablero."
        )
    if not board.is_listed_for_sale:
        raise HTTPException(
            status_code=400, detail="Esta tabla no está disponible para venta."
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="Esta tabla está bajo un arriendo activo y no se puede transferir.",
        )

    buyer_wallet = BankService.get_or_create_wallet(
        session, user_id, for_update=True
    )
    seller_wallet = BankService.get_or_create_wallet(
        session, board.user_id, for_update=True
    )

    price = board.sale_price_gal
    price_internal = frj_to_internal(price)
    if buyer_wallet.frijolitos < price_internal:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo de FRJ insuficiente para comprar esta tabla (cuesta {price} FRJ, tienes {frj_to_internal(buyer_wallet.frijolitos):.1f} FRJ).",
        )

    buyer_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    from app.core.auth import require_tutorial
    if buyer_record: require_tutorial(buyer_record)
    max_slots = (
        buyer_record.unlocked_board_slots
        if (buyer_record and buyer_record.unlocked_board_slots is not None)
        else 3
    )
    current_boards_count = session.exec(
        select(func.count(PlayerBoard.id))
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).one()
    if current_boards_count >= max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de tableros alcanzado. Tienes {current_boards_count}/{max_slots} tableros activos. Desbloquea un nuevo slot para poder adquirir más.",
        )

    commission = int(round(price_internal * 0.05))
    seller_net = price_internal - commission

    buyer_wallet.frijolitos -= price_internal
    seller_wallet.frijolitos += seller_net

    treasury = session.exec(select(TreasuryVault)).first()
    if not treasury:
        treasury = TreasuryVault(balance=0)
        session.add(treasury)
    treasury.balance += commission

    ledger_buyer = TransactionLedger(
        user_id=user_id,
        amount=price_internal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Compra de tabla #{board.id} al propietario {board.user_id}",
    )
    ledger_seller = TransactionLedger(
        user_id=board.user_id,
        amount=seller_net,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD,
        description=f"Venta de tabla #{board.id} al comprador {user_id}",
    )
    ledger_commission = TransactionLedger(
        user_id=board.user_id,
        amount=commission,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.BURN,
        description=f"Comisión de plataforma (5%) por venta de tabla #{board.id}",
    )

    tx_hash = ""
    if board.blockchain_token_id:
        buyer_user = session.exec(
            select(User).where(User.privy_did == user_id)
        ).first()
        seller_user = session.exec(
            select(User).where(User.privy_did == board.user_id)
        ).first()
        if (
            buyer_user
            and buyer_user.wallet_address
            and seller_user
            and seller_user.wallet_address
        ):
            try:
                tx_hash = Web3Service.transfer_board_onchain(
                    seller_user.wallet_address,
                    buyer_user.wallet_address,
                    board.blockchain_token_id,
                )
            except Exception as e:
                print(
                    f"⚠️ Error al transferir tabla on-chain: {e}"
                )

    old_owner_id = board.user_id
    board.user_id = user_id
    board.is_listed_for_sale = False
    board.sale_price_gal = 0.0

    session.add(buyer_wallet)
    session.add(seller_wallet)
    session.add(ledger_buyer)
    session.add(ledger_seller)
    session.add(board)
    session.commit()

    return {
        "mensaje": f"¡Has comprado la tabla '{board.name}' con éxito!",
        "board_id": board.id,
        "new_owner": board.user_id,
        "old_owner": old_owner_id,
        "tx_blockchain": tx_hash,
    }
