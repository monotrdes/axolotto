"""Board CRUD operations — creation, editing, deletion, slot management, and validation."""
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.models.board import PlayerBoard, PlayerBoardSlot
from app.models.items import ItemCatalog, PlayerInventory, ItemType
from app.models.user import User
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.axolotito import Axolotito
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.services.board.staking_service import (
    get_board_hourly_rate,
    get_accrued_staking,
    get_board_csr,
    deduct_staked_cards,
    return_staked_cards,
    _total_board_xp,
    _apply_preserved_xp_to_board,
    _level_from_total_xp,
)
from app.core.config import FRJ_DECIMALS_BACKEND, frj_to_internal, frj_to_display, settings
from app.core.product_policy import require_feature
from app.core.prices import BOARD_SLOT_COSTS, CONSUMABLE_PRICES

logger = logging.getLogger("board_service")
import random
_rng = random.SystemRandom()


# ─── Board response builders ─────────────────────────────────────────────

def _build_board_response(
    board: PlayerBoard,
    session: Session,
    user_id: str,
) -> dict:
    """Construye el dict de respuesta para un tablero."""
    accrued = (
        get_accrued_staking(board, session) if board.user_id == user_id else 0.0
    )
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

    return {
        "id": board.id,
        "user_id": board.user_id,
        "name": board.name,
        "card_ids": board.card_ids,
        "games_played": board.games_played,
        "games_won": board.games_won,
        "win_rate": round(win_rate, 1),
        "level": board.level,
        "xp": board.xp,
        "csr": round(csr, 1),
        "suerte_tag": suerte_tag,
        "accrued_staking_gal": round(accrued, 2),
        "hourly_yield_gal": round(get_board_hourly_rate(board, session), 3),
        "is_listed_for_rent": board.is_listed_for_rent,
        "is_rented": board.is_rented,
        "renter_id": board.renter_id,
        "rent_fee_gal": board.rent_fee_gal,
        "rent_share_owner_pct": board.rent_share_owner_pct,
        "rent_expires_at": board.rent_expires_at.isoformat() + "Z"
        if board.rent_expires_at
        else None,
        "is_tutorial": board.is_tutorial,
        "slot_index": board.slot_index,
        "slot_generation": board.slot_generation,
        "created_at": board.created_at.isoformat() + "Z"
        if board.created_at
        else None,
    }


def get_user_boards_data(user_id: str, session: Session) -> list:
    """Devuelve las tablas que posee el usuario y las que tiene rentadas actualmente."""
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    now = datetime.utcnow()

    owned_boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).all()

    rented_boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.renter_id == user_id)
        .where(PlayerBoard.is_rented == True)
        .where(PlayerBoard.is_dead == False)
        .where(PlayerBoard.rent_expires_at > now)
    ).all()

    resultado = []
    for board in owned_boards + rented_boards:
        resultado.append(_build_board_response(board, session, user_id))

    return resultado


# ─── Slot assignment ─────────────────────────────────────────────────────

def _assign_slot_index(user_id: str, session: Session) -> int:
    """Devuelve el slot_index más bajo disponible (sin tabla activa) para el usuario."""
    used_slots = set(
        session.exec(
            select(PlayerBoard.slot_index)
            .where(PlayerBoard.user_id == user_id)
            .where(PlayerBoard.is_dead == False)
            .where(PlayerBoard.slot_index.is_not(None))
        ).all()
    )
    slot = 1
    while slot in used_slots:
        slot += 1
    return slot


# ─── Board creation ──────────────────────────────────────────────────────

def create_random_board_operation(
    user_id: str, name: str, session: Session
) -> dict:
    """Crea un tablero de Lotería al azar cobrando 25 GAL de comisión."""
    require_feature(settings.ENABLE_BOARD_ASSET_MUTATIONS, "board_asset_mutations")
    require_feature(
        settings.ENABLE_PURCHASED_RANDOM_REWARDS,
        "purchased_random_rewards",
    )
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    if (
        settings.PRODUCT_MODE != "legacy_simulation"
        and (not user_record or not user_record.wallet_address)
    ):
        raise HTTPException(
            status_code=409,
            detail="Se requiere una wallet verificada para crear una tabla on-chain.",
        )
    from app.core.auth import require_tutorial
    if user_record: require_tutorial(user_record)
    max_slots = (
        user_record.unlocked_board_slots
        if (user_record and user_record.unlocked_board_slots is not None)
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
            detail=f"Límite de tableros alcanzado. Tienes {current_boards_count}/{max_slots} tableros creados. Desbloquea un nuevo espacio para poder crear más.",
        )

    _cost_random = 25 * (10 ** FRJ_DECIMALS_BACKEND)
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < _cost_random:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Crear un tablero aleatorio cuesta 25 FRJ (tienes {frj_to_display(wallet.frijolitos):.1f} FRJ).",
        )

    inventory = session.exec(
        select(PlayerInventory)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.quantity > 0)
        .where(ItemCatalog.item_type == ItemType.CARD)
    ).all()

    inventory_map = {}
    for item in inventory:
        key = (item.item_id, getattr(item, "is_first_edition", False))
        inventory_map[key] = inventory_map.get(key, 0) + item.quantity

    card_total_available = {}
    for (cid, is_fe), qty in inventory_map.items():
        if qty > 0:
            card_total_available[cid] = card_total_available.get(cid, 0) + qty

    available_cids = [cid for cid, qty in card_total_available.items() if qty > 0]

    if len(available_cids) < 16:
        raise HTTPException(
            status_code=400,
            detail=f"No tienes suficientes cartas libres en tu mochila. Requieres 16 únicas libres, tienes {len(available_cids)}.",
        )

    chosen_cids = _rng.sample(available_cids, 16)

    chosen_first_editions = []
    for cid in chosen_cids:
        if inventory_map.get((cid, True), 0) > 0:
            chosen_first_editions.append(True)
            inventory_map[(cid, True)] -= 1
        else:
            chosen_first_editions.append(False)
            inventory_map[(cid, False)] -= 1

    wallet.frijolitos -= _cost_random
    ledger = TransactionLedger(
        user_id=user_id,
        amount=_cost_random,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Creación aleatoria de tabla: {name}",
    )

    tx_blockchain = ""
    blockchain_token_id = None
    if user_record and user_record.wallet_address:
        try:
            Web3Service.approve_tablas_for_player(user_record.wallet_address)
            tx_blockchain = Web3Service.create_board_onchain(
                user_record.wallet_address, chosen_cids
            )
            blockchain_token_id = Web3Service.get_token_id_from_tx(tx_blockchain)
        except Exception as e:
            logger.error("Error al crear tabla en Blockchain (random): %s", e)
            if settings.PRODUCT_MODE != "legacy_simulation":
                raise HTTPException(
                    status_code=503,
                    detail="La cadena no confirmó la tabla; no se guardó estado local.",
                ) from e
            import secrets
            tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

    if settings.PRODUCT_MODE != "legacy_simulation" and blockchain_token_id is None:
        raise HTTPException(
            status_code=503,
            detail="No se obtuvo un tokenId confirmado para la tabla.",
        )

    new_board = PlayerBoard(
        user_id=user_id,
        name=name or "Tabla Aleatoria",
        card_ids=chosen_cids,
        card_first_editions=chosen_first_editions,
        blockchain_token_id=blockchain_token_id,
    )

    new_board.slot_index = _assign_slot_index(user_id, session)
    _slot_rec = session.exec(
        select(PlayerBoardSlot).where(
            PlayerBoardSlot.user_id == user_id,
            PlayerBoardSlot.slot_index == new_board.slot_index,
        )
    ).first()
    if _slot_rec:
        if _slot_rec.preserved_xp > 0:
            _apply_preserved_xp_to_board(new_board, _slot_rec.preserved_xp)
            _slot_rec.preserved_xp = 0
        _slot_rec.boards_created += 1
        new_board.slot_generation = _slot_rec.boards_created
        session.add(_slot_rec)
    else:
        new_board.slot_generation = 1
        session.add(PlayerBoardSlot(
            user_id=user_id,
            slot_index=new_board.slot_index,
            preserved_xp=0,
            boards_created=1,
        ))

    deduct_staked_cards(user_id, chosen_cids, chosen_first_editions, session)

    session.add(wallet)
    session.add(ledger)
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return {
        "mensaje": f"¡Tabla aleatoria '{new_board.name}' creada con éxito!",
        "board_id": new_board.id,
        "card_ids": new_board.card_ids,
        "tx_blockchain": tx_blockchain,
        "slot_index": new_board.slot_index,
        "slot_generation": new_board.slot_generation,
        "inherited_level": new_board.level,
    }


def create_manual_board_operation(
    user_id: str,
    name: str,
    card_ids: list[int],
    card_first_editions: list[bool],
    session: Session,
) -> dict:
    """Crea un tablero de Lotería manualmente validando las cartas y cobrando 50 GAL."""
    require_feature(settings.ENABLE_BOARD_ASSET_MUTATIONS, "board_asset_mutations")
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    if (
        settings.PRODUCT_MODE != "legacy_simulation"
        and (not user_record or not user_record.wallet_address)
    ):
        raise HTTPException(
            status_code=409,
            detail="Se requiere una wallet verificada para crear una tabla on-chain.",
        )
    from app.core.auth import require_tutorial
    if user_record: require_tutorial(user_record)
    max_slots = (
        user_record.unlocked_board_slots
        if (user_record and user_record.unlocked_board_slots is not None)
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
            detail=f"Límite de tableros alcanzado. Tienes {current_boards_count}/{max_slots} tableros creados. Desbloquea un nuevo espacio para poder crear más.",
        )

    _cost_manual = 50 * (10 ** FRJ_DECIMALS_BACKEND)
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < _cost_manual:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Crear un tablero manual cuesta 50 FRJ (tienes {frj_to_display(wallet.frijolitos):.1f} FRJ).",
        )

    fe_flags = card_first_editions if card_first_editions else [False] * 16

    validate_card_availability(user_id, card_ids, fe_flags, None, session)

    wallet.frijolitos -= _cost_manual
    ledger = TransactionLedger(
        user_id=user_id,
        amount=_cost_manual,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Creación manual de tabla: {name}",
    )

    tx_blockchain = ""
    blockchain_token_id = None
    if user_record and user_record.wallet_address:
        try:
            Web3Service.approve_tablas_for_player(user_record.wallet_address)
            tx_blockchain = Web3Service.create_board_onchain(
                user_record.wallet_address, card_ids
            )
            blockchain_token_id = Web3Service.get_token_id_from_tx(tx_blockchain)
        except Exception as e:
            logger.error("Error al crear tabla en Blockchain (manual): %s", e)
            if settings.PRODUCT_MODE != "legacy_simulation":
                raise HTTPException(
                    status_code=503,
                    detail="La cadena no confirmó la tabla; no se guardó estado local.",
                ) from e
            import secrets
            tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

    if settings.PRODUCT_MODE != "legacy_simulation" and blockchain_token_id is None:
        raise HTTPException(
            status_code=503,
            detail="No se obtuvo un tokenId confirmado para la tabla.",
        )

    new_board = PlayerBoard(
        user_id=user_id,
        name=name or "Mi Tabla Personalizada",
        card_ids=card_ids,
        card_first_editions=fe_flags,
        blockchain_token_id=blockchain_token_id,
    )

    new_board.slot_index = _assign_slot_index(user_id, session)
    _slot_rec = session.exec(
        select(PlayerBoardSlot).where(
            PlayerBoardSlot.user_id == user_id,
            PlayerBoardSlot.slot_index == new_board.slot_index,
        )
    ).first()
    if _slot_rec:
        if _slot_rec.preserved_xp > 0:
            _apply_preserved_xp_to_board(new_board, _slot_rec.preserved_xp)
            _slot_rec.preserved_xp = 0
        _slot_rec.boards_created += 1
        new_board.slot_generation = _slot_rec.boards_created
        session.add(_slot_rec)
    else:
        new_board.slot_generation = 1
        session.add(PlayerBoardSlot(
            user_id=user_id,
            slot_index=new_board.slot_index,
            preserved_xp=0,
            boards_created=1,
        ))

    deduct_staked_cards(user_id, card_ids, fe_flags, session)

    session.add(wallet)
    session.add(ledger)
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return {
        "mensaje": f"¡Tabla '{new_board.name}' guardada con éxito!",
        "board_id": new_board.id,
        "tx_blockchain": tx_blockchain,
        "slot_index": new_board.slot_index,
        "slot_generation": new_board.slot_generation,
        "inherited_level": new_board.level,
    }


# ─── Board editing / deletion ─────────────────────────────────────────────

def edit_board_operation(
    board_id: int, user_id: str, name: Optional[str], session: Session
) -> dict:
    """Reconfigura una tabla existente permitiendo SOLO cambiar el nombre de forma gratuita."""
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(status_code=403, detail="No eres dueño de esta tabla.")
    if board.is_dead:
        raise HTTPException(
            status_code=400,
            detail="No puedes editar una tabla que está desarmada (muerta).",
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="No puedes editar una tabla que está rentada.",
        )

    if name is not None:
        board.name = name

    session.add(board)
    session.commit()
    session.refresh(board)

    return {
        "mensaje": f"Nombre de la tabla #{board_id} actualizado correctamente.",
        "board_id": board.id,
    }


def delete_board_operation(board_id: int, user_id: str, session: Session) -> dict:
    """Desarma la tabla: devuelve las 16 cartas, cobra 1 AXF y preserva 80% del XP en el slot."""
    require_feature(settings.ENABLE_BOARD_ASSET_MUTATIONS, "board_asset_mutations")
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para desarmar esta tabla."
        )
    if board.is_tutorial:
        raise HTTPException(
            status_code=400, detail="La Tabla Tutorial no se puede desarmar."
        )
    if board.is_dead:
        raise HTTPException(
            status_code=400,
            detail="Esta tabla ya está desarmada (muerta).",
        )
    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="No puedes desarmar una tabla que está rentada.",
        )
    if (
        settings.PRODUCT_MODE != "legacy_simulation"
        and board.blockchain_token_id is None
    ):
        raise HTTPException(
            status_code=409,
            detail="La tabla no tiene identidad on-chain confirmada y no puede mutarse.",
        )
    if board.is_listed_for_rent:
        raise HTTPException(
            status_code=400,
            detail="No puedes desarmar una tabla publicada en el mercado de rentas. Retírala primero.",
        )

    axo_assigned = session.exec(
        select(Axolotito).where(Axolotito.assigned_board_id == board_id)
    ).first()
    if axo_assigned:
        raise HTTPException(
            status_code=400,
            detail=f"No puedes desarmar una tabla asignada al Axolotito '{axo_assigned.name}'. Desasígnala primero.",
        )
    if board.origin_story is not None and settings.PRODUCT_MODE != "legacy_simulation":
        raise HTTPException(
            status_code=409,
            detail="Las tablas forjadas requieren una ruta de disolución on-chain antes de mutarse.",
        )

    cost = CONSUMABLE_PRICES["solvente"]
    wallet = BankService.get_or_create_wallet(session, user_id)
    if wallet.axofichas < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Desarmar cuesta 1 AXF (Solvente de Pegamento).",
        )

    wallet.axofichas -= cost
    ledger_delete = TransactionLedger(
        user_id=user_id,
        amount=cost,
        currency=CurrencyType.AXOFICHA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Solvente de Pegamento para desarmar tabla #{board_id}",
    )
    session.add(ledger_delete)

    accrued = get_accrued_staking(board, session)
    if accrued > 0:
        wallet.frijolitos += accrued
        ledger_stake = TransactionLedger(
            user_id=user_id,
            amount=accrued,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.REWARD,
            description=f"Cobro final de staking por desarmar tabla #{board_id}",
        )
        session.add(ledger_stake)
    session.add(wallet)

    tx_blockchain = ""
    if board.origin_story is not None:
        board.is_dead = True
        board.is_listed_for_rent = False
        board.is_rented = False
        session.add(board)
        session.commit()
        return {
            "mensaje": "Tabla Forjada desarmada con éxito. Al ser un tablero forjado en batalla, sus cartas no regresan al inventario.",
            "lost_card": None,
            "tx_blockchain": "",
        }
    if board.card_ids:
        if board.blockchain_token_id is not None:
            try:
                tx_blockchain = Web3Service.dissolve_board_safe_onchain(
                    board.blockchain_token_id
                )
            except Exception as e:
                print(
                    f"⚠️ Error al disolver tabla en Blockchain de forma segura: {e}"
                )
                if settings.PRODUCT_MODE != "legacy_simulation":
                    raise HTTPException(
                        status_code=503,
                        detail="La cadena no confirmó la disolución; no se modificó la tabla local.",
                    ) from e
                import secrets
                tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

        card_first_editions_list = getattr(board, "card_first_editions", None) or [
            False
        ] * len(board.card_ids)

        return_staked_cards(
            user_id,
            board.card_ids,
            card_first_editions_list,
            session,
            skip_index=None,
        )

    preserved_xp_out = 0
    if board.slot_index is not None:
        total_xp = _total_board_xp(board)
        preserved = int(total_xp * 0.8)
        preserved_xp_out = preserved
        slot_record = session.exec(
            select(PlayerBoardSlot).where(
                PlayerBoardSlot.user_id == user_id,
                PlayerBoardSlot.slot_index == board.slot_index,
            )
        ).first()
        if slot_record:
            slot_record.preserved_xp = preserved
            session.add(slot_record)
        else:
            session.add(PlayerBoardSlot(
                user_id=user_id,
                slot_index=board.slot_index,
                preserved_xp=preserved,
                boards_created=1,
            ))

    board.is_dead = True
    board.is_listed_for_rent = False
    board.is_rented = False

    session.add(board)
    session.commit()

    return {
        "mensaje": "Tabla desarmada. Las 16 cartas han vuelto a tu inventario. El 80% del XP queda guardado en el slot.",
        "lost_card": None,
        "preserved_xp": preserved_xp_out,
        "tx_blockchain": tx_blockchain,
    }


# ─── Card validation ─────────────────────────────────────────────────────

def validate_card_availability(
    user_id: str,
    new_card_ids: list[int],
    card_first_editions: list[bool],
    board_id_to_exclude: Optional[int],
    session: Session,
):
    """Valida que el usuario tenga las cartas disponibles en inventario (no stakeadas en otra tabla)."""
    if len(new_card_ids) != 16:
        raise HTTPException(
            status_code=400,
            detail="Un tablero de Lotería debe consistir en exactamente 16 cartas.",
        )
    if len(set(new_card_ids)) != 16:
        raise HTTPException(
            status_code=400,
            detail="Un tablero de Lotería no puede contener cartas duplicadas.",
        )
    if len(card_first_editions) != 16:
        raise HTTPException(
            status_code=400,
            detail="Un tablero de Lotería debe tener exactamente 16 flags de Primera Edición.",
        )

    inventory = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.quantity > 0)
    ).all()
    inventory_map = {}
    for item in inventory:
        key = (item.item_id, getattr(item, "is_first_edition", False))
        inventory_map[key] = inventory_map.get(key, 0) + item.quantity

    catalogo_cartas = session.exec(
        select(ItemCatalog).where(ItemCatalog.id.in_(new_card_ids))
    ).all()
    catalogo_ids = {c.id for c in catalogo_cartas if c.item_type == ItemType.CARD}
    for cid in new_card_ids:
        if cid not in catalogo_ids:
            raise HTTPException(
                status_code=400,
                detail=f"La carta con ID {cid} no existe o no es de tipo CARD en el catálogo.",
            )

    for idx, cid in enumerate(new_card_ids):
        is_fe = card_first_editions[idx]
        owned = inventory_map.get((cid, is_fe), 0)
        if owned < 1:
            fe_label = "Primera Edición" if is_fe else "Normal"
            raise HTTPException(
                status_code=400,
                detail=f"No tienes la carta ID {cid} ({fe_label}) disponible en tu mochila (ya está en una tabla o no la posees).",
            )


# ─── Slot requirements ───────────────────────────────────────────────────

def get_slot_requirements(current_unlocked: int):
    """Calcula los requisitos para desbloquear el siguiente slot de tabla."""
    next_slot = current_unlocked + 1
    if next_slot in BOARD_SLOT_COSTS:
        cost = BOARD_SLOT_COSTS[next_slot]
    else:
        multiplier = next_slot - 8
        cost = BOARD_SLOT_COSTS[9] * multiplier

    if next_slot == 4:
        return {"cost_gal": cost, "games_played": 0, "games_won": 0}
    elif next_slot == 5:
        return {"cost_gal": cost, "games_played": 10, "games_won": 0}
    elif next_slot == 6:
        return {"cost_gal": cost, "games_played": 25, "games_won": 0}
    elif next_slot == 7:
        return {"cost_gal": cost, "games_played": 50, "games_won": 5}
    elif next_slot == 8:
        return {"cost_gal": cost, "games_played": 100, "games_won": 15}
    else:
        multiplier = next_slot - 8
        return {
            "cost_gal": cost,
            "games_played": 200 + (multiplier * 50),
            "games_won": 30 + (multiplier * 10),
        }


# ─── Slot status / unlock ─────────────────────────────────────────────────

def get_slot_status_data(user_id: str, session: Session) -> dict:
    """Obtiene el estado de slots del usuario (desbloqueados, usados, estadísticas de desbloqueo)."""
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    from app.core.auth import require_tutorial
    if user_record: require_tutorial(user_record)
    unlocked_slots = (
        user_record.unlocked_board_slots
        if (user_record and user_record.unlocked_board_slots is not None)
        else 3
    )

    used_slots = session.exec(
        select(func.count(PlayerBoard.id))
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).one()

    total_games_played = (
        session.exec(
            select(func.sum(PlayerBoard.games_played)).where(
                PlayerBoard.user_id == user_id
            )
        ).one()
        or 0
    )
    total_games_won = (
        session.exec(
            select(func.sum(PlayerBoard.games_won)).where(
                PlayerBoard.user_id == user_id
            )
        ).one()
        or 0
    )

    reqs = get_slot_requirements(unlocked_slots)

    can_unlock = True
    reasons = []

    wallet = BankService.get_or_create_wallet(session, user_id)
    if wallet.frijolitos < reqs["cost_gal"]:
        can_unlock = False
        reasons.append(
            f"Faltan {frj_to_display(reqs['cost_gal'] - wallet.frijolitos):.1f} FRJ"
        )

    if total_games_played < reqs["games_played"]:
        can_unlock = False
        reasons.append(
            f"Se requieren {reqs['games_played']} partidas jugadas (tienes {total_games_played})"
        )

    if total_games_won < reqs["games_won"]:
        can_unlock = False
        reasons.append(
            f"Se requieren {reqs['games_won']} partidas ganadas (tienes {total_games_won})"
        )

    slot_records = session.exec(
        select(PlayerBoardSlot).where(PlayerBoardSlot.user_id == user_id)
    ).all()
    slots_xp = {
        rec.slot_index: {
            "preserved_xp": rec.preserved_xp,
            "preserved_level": _level_from_total_xp(rec.preserved_xp),
        }
        for rec in slot_records
        if rec.preserved_xp > 0
    }

    return {
        "unlocked_slots": unlocked_slots,
        "used_slots": used_slots,
        "total_games_played": total_games_played,
        "total_games_won": total_games_won,
        "current_gal": wallet.frijolitos,
        "next_slot_requirements": {
            "slot_number": unlocked_slots + 1,
            "cost_gal": reqs["cost_gal"],
            "games_played_required": reqs["games_played"],
            "games_won_required": reqs["games_won"],
            "can_unlock": can_unlock,
            "reasons": reasons,
        },
        "slots_xp": slots_xp,
    }


def unlock_slot_operation(user_id: str, session: Session) -> dict:
    """Desbloquea el siguiente slot de tabla cobrando los GAL correspondientes y validando requisitos."""
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    from app.core.auth import require_tutorial
    require_tutorial(user_record)

    unlocked_slots = (
        user_record.unlocked_board_slots
        if user_record.unlocked_board_slots is not None
        else 3
    )

    reqs = get_slot_requirements(unlocked_slots)

    total_games_played = (
        session.exec(
            select(func.sum(PlayerBoard.games_played)).where(
                PlayerBoard.user_id == user_id
            )
        ).one()
        or 0
    )
    total_games_won = (
        session.exec(
            select(func.sum(PlayerBoard.games_won)).where(
                PlayerBoard.user_id == user_id
            )
        ).one()
        or 0
    )

    if (
        total_games_played < reqs["games_played"]
        or total_games_won < reqs["games_won"]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Requisitos no cumplidos. Requiere {reqs['games_played']} partidas jugadas y {reqs['games_won']} ganadas.",
        )

    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < reqs["cost_gal"]:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Desbloquear el slot {unlocked_slots + 1} cuesta {frj_to_display(reqs['cost_gal']):.0f} FRJ.",
        )

    wallet.frijolitos -= reqs["cost_gal"]
    user_record.unlocked_board_slots = unlocked_slots + 1

    ledger = TransactionLedger(
        user_id=user_id,
        amount=reqs["cost_gal"],
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Desbloqueo de slot de tabla #{unlocked_slots + 1}",
    )

    session.add(wallet)
    session.add(user_record)
    session.add(ledger)
    session.commit()
    session.refresh(user_record)

    return {
        "mensaje": f"¡Slot {user_record.unlocked_board_slots} desbloqueado con éxito!",
        "unlocked_slots": user_record.unlocked_board_slots,
    }
