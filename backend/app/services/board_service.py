import random
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlmodel import Session, select, func

logger = logging.getLogger("board_service")

from app.core.prices import BOARD_SLOT_COSTS, CONSUMABLE_PRICES
from app.models.board import PlayerBoard
from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity
from app.models.axolotito import Axolotito
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.lobby_models import TreasuryVault
from app.models.user import User
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service

_rng = random.SystemRandom()


# ─── Pure helper functions ───────────────────────────────────────────────

def get_board_hourly_rate(board: PlayerBoard, session: Session) -> float:
    """Calcula la recompensa de GAL por hora de una tabla en base a sus cartas y nivel."""
    if not board.card_ids:
        return 0.0

    cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.id.in_(board.card_ids))
    ).all()

    rarity_bonuses = {
        Rarity.COMMON: 0.05,
        Rarity.RARE: 0.15,
        Rarity.EPIC: 0.40,
        Rarity.LEGENDARY: 1.00
    }

    total_bonus = 0.0
    for card in cards:
        total_bonus += rarity_bonuses.get(card.rarity, 0.05)

    level_multiplier = 1.0 + (board.level / 10.0)

    return total_bonus * level_multiplier


def get_accrued_staking(board: PlayerBoard, session: Session) -> float:
    """Calcula las GAL acumuladas desde el último reclamo de staking, con cap de 24h y play-to-stake."""
    now = datetime.utcnow()
    
    # Play-to-Stake check
    user = session.exec(select(User).where(User.privy_did == board.user_id)).first()
    if not user or not user.last_play_date:
        return 0.0
    
    cutoff = now - timedelta(hours=24)
    if user.last_play_date < cutoff:
        return 0.0

    hours_elapsed = (now - board.last_staking_claim).total_seconds() / 3600.0
    if hours_elapsed <= 0:
        return 0.0
    
    # Cap at 24 hours
    hours_elapsed = min(hours_elapsed, 24.0)
    
    return hours_elapsed * get_board_hourly_rate(board, session)


def get_board_csr(board: PlayerBoard) -> float:
    """Calcula el Coeficiente de Suerte Real (CSR) en base a estadísticas y racha."""
    if board.games_played == 0:
        return 25.0  # Desempeño promedio estándar (25%)

    win_rate = (board.games_won / board.games_played) * 100.0

    # Racha: victorias en los últimos 5 juegos otorgan bono, derrotas restan
    streak_bonus = 0.0
    if board.recent_games_results:
        # Contar victorias recientes
        recent_wins = sum(1 for res in board.recent_games_results if res)
        # 5 victorias = +10% de CSR, 0 victorias = -10% de CSR
        streak_bonus = (recent_wins - 2.5) * 4.0

    # Retornar el CSR acotado entre 0 y 100
    return max(0.0, min(100.0, win_rate + streak_bonus))


def deduct_staked_cards(
    user_id: str,
    card_ids: List[int],
    card_first_editions: List[bool],
    session: Session,
):
    """Descuenta las cartas stakeadas del inventario disponible del jugador."""
    for idx, cid in enumerate(card_ids):
        is_fe = card_first_editions[idx] if idx < len(card_first_editions) else False
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == cid)
            .where(PlayerInventory.is_first_edition == is_fe)
            .with_for_update()
        ).first()
        if inv:
            inv.quantity -= 1
            if inv.quantity <= 0:
                session.delete(inv)
            else:
                session.add(inv)


def return_staked_cards(
    user_id: str,
    card_ids: List[int],
    card_first_editions: List[bool],
    session: Session,
    skip_index: Optional[int] = None,
):
    """Devuelve las cartas al inventario del jugador (al desarmar una tabla). skip_index = carta destruída."""
    for idx, cid in enumerate(card_ids):
        if idx == skip_index:
            continue
        is_fe = card_first_editions[idx] if idx < len(card_first_editions) else False
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == cid)
            .where(PlayerInventory.is_first_edition == is_fe)
        ).first()
        if inv:
            inv.quantity += 1
            session.add(inv)
        else:
            session.add(
                PlayerInventory(
                    user_id=user_id,
                    item_id=cid,
                    quantity=1,
                    is_first_edition=is_fe,
                    is_shiny=False,
                )
            )


def validate_card_availability(
    user_id: str,
    new_card_ids: List[int],
    card_first_editions: List[bool],
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

    # Inventario disponible (ya refleja el stake real — quantity baja al stakear)
    inventory = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.quantity > 0)
    ).all()
    inventory_map = {}
    for item in inventory:
        key = (item.item_id, getattr(item, "is_first_edition", False))
        inventory_map[key] = inventory_map.get(key, 0) + item.quantity

    # Validar existencia en catálogo
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

    # Validar disponibilidad en inventario (inventory_map ya tiene staked cards descontadas)
    for idx, cid in enumerate(new_card_ids):
        is_fe = card_first_editions[idx]
        owned = inventory_map.get((cid, is_fe), 0)
        if owned < 1:
            fe_label = "Primera Edición" if is_fe else "Normal"
            raise HTTPException(
                status_code=400,
                detail=f"No tienes la carta ID {cid} ({fe_label}) disponible en tu mochila (ya está en una tabla o no la posees).",
            )


def get_slot_requirements(current_unlocked: int):
    """Calcula los requisitos para desbloquear el siguiente slot de tabla."""
    next_slot = current_unlocked + 1
    if next_slot in BOARD_SLOT_COSTS:
        cost = BOARD_SLOT_COSTS[next_slot]
    else:
        # A partir del slot 9 en adelante
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


# ─── Service methods (business logic extracted from endpoint handlers) ──

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

    # Clasificar la suerte
    if csr >= 35.0:
        suerte_tag = "\U0001f340 Muy Suertuda"
    elif csr <= 15.0:
        suerte_tag = "\U0001f9c2 Salada"
    else:
        suerte_tag = "⚙️ Normal"

    # Calcular win rate
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
        "created_at": board.created_at.isoformat() + "Z"
        if board.created_at
        else None,
    }


def get_user_boards_data(user_id: str, session: Session) -> list:
    """Devuelve las tablas que posee el usuario y las que tiene rentadas actualmente."""
    now = datetime.utcnow()

    # 1. Tablas propias del usuario (solo activas)
    owned_boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).all()

    # 2. Tablas rentadas por el usuario actualmente activas
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


def create_random_board_operation(
    user_id: str, name: str, session: Session
) -> dict:
    """Crea un tablero de Lotería al azar cobrando 25 GAL de comisión."""
    # 0. Validar límite de tableros
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    max_slots = (
        user_record.unlocked_board_slots
        if (user_record and user_record.unlocked_board_slots is not None)
        else 3
    )

    current_boards_count = session.exec(
        select(func.count(PlayerBoard.id)).where(PlayerBoard.user_id == user_id)
    ).one()

    if current_boards_count >= max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de tableros alcanzado. Tienes {current_boards_count}/{max_slots} tableros creados. Desbloquea un nuevo espacio para poder crear más.",
        )

    # 1. Validar que el usuario posea al menos 25 GAL
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < 25.0:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente. Crear un tablero aleatorio cuesta 25 GAL.",
        )

    # 2. Buscar todas las cartas del usuario que no estén en stake total
    inventory = session.exec(
        select(PlayerInventory)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.quantity > 0)
        .where(ItemCatalog.item_type == ItemType.CARD)
    ).all()

    # Inventario disponible
    inventory_map = {}
    for item in inventory:
        key = (item.item_id, getattr(item, "is_first_edition", False))
        inventory_map[key] = inventory_map.get(key, 0) + item.quantity

    # Obtener el stock total disponible de cada carta
    card_total_available = {}
    for (cid, is_fe), qty in inventory_map.items():
        if qty > 0:
            card_total_available[cid] = card_total_available.get(cid, 0) + qty

    # Quedarnos con las cartas que tengan stock > 0
    available_cids = [cid for cid, qty in card_total_available.items() if qty > 0]

    # 3. Validar que tengamos al menos 16 cartas únicas disponibles
    if len(available_cids) < 16:
        raise HTTPException(
            status_code=400,
            detail=f"No tienes suficientes cartas libres en tu mochila. Requieres 16 únicas libres, tienes {len(available_cids)}.",
        )

    # Elegir 16 cartas únicas al azar
    chosen_cids = _rng.sample(available_cids, 16)

    # Determinar si cada carta elegida se asigna como Primera Edición
    chosen_first_editions = []
    for cid in chosen_cids:
        if inventory_map.get((cid, True), 0) > 0:
            chosen_first_editions.append(True)
            inventory_map[(cid, True)] -= 1
        else:
            chosen_first_editions.append(False)
            inventory_map[(cid, False)] -= 1

    # Cobrar
    wallet.frijolitos -= 25.0
    ledger = TransactionLedger(
        user_id=user_id,
        amount=25.0,
        currency=CurrencyType.GEMA_ALGA,
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
            import secrets

            tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

    new_board = PlayerBoard(
        user_id=user_id,
        name=name or "Tabla Aleatoria",
        card_ids=chosen_cids,
        card_first_editions=chosen_first_editions,
        blockchain_token_id=blockchain_token_id,
    )

    # Stakear las cartas
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
    }


def create_manual_board_operation(
    user_id: str,
    name: str,
    card_ids: List[int],
    card_first_editions: List[bool],
    session: Session,
) -> dict:
    """Crea un tablero de Lotería manualmente validando las cartas y cobrando 50 GAL."""
    # 0. Validar límite de tableros
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    max_slots = (
        user_record.unlocked_board_slots
        if (user_record and user_record.unlocked_board_slots is not None)
        else 3
    )

    current_boards_count = session.exec(
        select(func.count(PlayerBoard.id)).where(PlayerBoard.user_id == user_id)
    ).one()

    if current_boards_count >= max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de tableros alcanzado. Tienes {current_boards_count}/{max_slots} tableros creados. Desbloquea un nuevo espacio para poder crear más.",
        )

    # 1. Validar que el usuario posea al menos 50 GAL
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < 50.0:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente. Crear un tablero manual cuesta 50 GAL.",
        )

    # 2. Validar propiedad y disponibilidad de cartas
    fe_flags = card_first_editions if card_first_editions else [False] * 16

    validate_card_availability(user_id, card_ids, fe_flags, None, session)

    # 3. Cobrar y guardar
    wallet.frijolitos -= 50.0
    ledger = TransactionLedger(
        user_id=user_id,
        amount=50.0,
        currency=CurrencyType.GEMA_ALGA,
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
            import secrets

            tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

    new_board = PlayerBoard(
        user_id=user_id,
        name=name or "Mi Tabla Personalizada",
        card_ids=card_ids,
        card_first_editions=fe_flags,
        blockchain_token_id=blockchain_token_id,
    )

    # Stakear las cartas
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
    }


def edit_board_operation(
    board_id: int, user_id: str, name: Optional[str], session: Session
) -> dict:
    """Reconfigura una tabla existente permitiendo SOLO cambiar el nombre de forma gratuita."""
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
    """Desarma y marca como inactiva (dead) la tabla, perdiendo una carta al azar, liberando las otras 15 y cobrando el staking."""
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
    if board.is_listed_for_rent:
        raise HTTPException(
            status_code=400,
            detail="No puedes desarmar una tabla publicada en el mercado de rentas. Retírala primero.",
        )

    # Verificar si está asignada a algún Axolotito
    axo_assigned = session.exec(
        select(Axolotito).where(Axolotito.assigned_board_id == board_id)
    ).first()
    if axo_assigned:
        raise HTTPException(
            status_code=400,
            detail=f"No puedes desarmar una tabla asignada al Axolotito '{axo_assigned.name}'. Desasígnala primero.",
        )

    # 1. Validar y cobrar costo de desarmado (Solvente)
    cost = CONSUMABLE_PRICES["solvente"]
    wallet = BankService.get_or_create_wallet(session, user_id)
    if wallet.frijolitos < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Desarmar una tabla cuesta {cost} GAL para el Solvente de Pegamento.",
        )

    wallet.frijolitos -= cost
    ledger_delete = TransactionLedger(
        user_id=user_id,
        amount=cost,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Costo por desarmar tabla #{board_id} (Solvente de Pegamento)",
    )
    session.add(ledger_delete)

    # 2. Reclamar staking acumulado antes de marcar como muerta
    accrued = get_accrued_staking(board, session)
    if accrued > 0:
        wallet.frijolitos += accrued
        ledger_stake = TransactionLedger(
            user_id=user_id,
            amount=accrued,
            currency=CurrencyType.GEMA_ALGA,
            tx_type=TransactionType.REWARD,
            description=f"Cobro final de staking por desarmar tabla #{board_id}",
        )
        session.add(ledger_stake)
    session.add(wallet)

    # NPC-origin boards (won via gashapon): cards were never in any user inventory
    tx_blockchain = ""
    if board.origin_story is not None:
        # NPC board: mark dead, skip card operations
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
        # Llamar a disolver en la blockchain si corresponde
        if board.blockchain_token_id is not None:
            try:
                tx_blockchain = Web3Service.dissolve_board_safe_onchain(
                    board.blockchain_token_id
                )
            except Exception as e:
                print(
                    f"⚠️ Error al disolver tabla en Blockchain de forma segura: {e}"
                )
                import secrets

                tx_blockchain = f"0x_error_fallback_{secrets.token_hex(32)}"

        card_first_editions_list = getattr(board, "card_first_editions", None) or [
            False
        ] * len(board.card_ids)

        # Devolver las 16 cartas sobrevivientes al inventario
        return_staked_cards(
            user_id,
            board.card_ids,
            card_first_editions_list,
            session,
            skip_index=None,
        )

    # 3. Marcar tabla como muerta y limpiar estados activos de renta
    board.is_dead = True
    board.is_listed_for_rent = False
    board.is_rented = False

    session.add(board)
    session.commit()

    return {
        "mensaje": "Tabla desarmada con éxito usando Solvente de Pegamento. Las 16 cartas han vuelto a tu inventario intactas.",
        "lost_card": None,
        "tx_blockchain": tx_blockchain,
    }


def claim_staking_operation(board_id: int, user_id: str, session: Session) -> dict:
    """Reclama las Gemas Alga acumuladas por el staking de las cartas de esta tabla."""
    board = session.get(PlayerBoard, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Tabla no encontrada.")
    if board.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta tabla.")
    if board.is_dead:
        raise HTTPException(
            status_code=400, detail="Esta tabla está desarmada (muerta)."
        )

    accrued = get_accrued_staking(board, session)
    if accrued <= 0:
        return {
            "mensaje": "No tienes recompensas acumuladas aún.",
            "claimed_amount": 0.0,
        }

    wallet = BankService.get_or_create_wallet(session, user_id)
    wallet.frijolitos += accrued

    board.last_staking_claim = datetime.utcnow()

    ledger = TransactionLedger(
        user_id=user_id,
        amount=accrued,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Reclamo de Staking de cartas en tabla #{board_id}",
    )

    session.add(wallet)
    session.add(board)
    session.add(ledger)
    session.commit()

    return {
        "mensaje": f"¡Has reclamado {round(accrued, 2)} GAL exitosamente!",
        "claimed_amount": round(accrued, 2),
    }


def claim_all_staking_operation(user_id: str, session: Session) -> dict:
    """Reclama las Gemas Alga acumuladas por el staking de TODAS las tablas del usuario a la vez."""
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user_id)
        .where(PlayerBoard.is_dead == False)
    ).all()

    total_accrued = 0.0
    claimed_boards = []

    for board in boards:
        accrued = get_accrued_staking(board, session)
        if accrued > 0:
            total_accrued += accrued
            board.last_staking_claim = datetime.utcnow()
            session.add(board)
            claimed_boards.append(board.id)

    if total_accrued <= 0:
        return {
            "mensaje": "No tienes recompensas acumuladas en ninguna de tus tablas.",
            "claimed_amount": 0.0,
            "claimed_boards": [],
        }

    wallet = BankService.get_or_create_wallet(session, user_id)
    wallet.frijolitos += total_accrued

    ledger = TransactionLedger(
        user_id=user_id,
        amount=total_accrued,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Reclamo masivo de Staking para tablas: {claimed_boards}",
    )

    session.add(wallet)
    session.add(ledger)
    session.commit()

    return {
        "mensaje": f"¡Has reclamado {round(total_accrued, 2)} GAL exitosamente de {len(claimed_boards)} tablas!",
        "claimed_amount": round(total_accrued, 2),
        "claimed_boards": claimed_boards,
    }


# ─── Rental market helpers ─────────────────────────────────────────────

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

    # Obtener el tier de VIP del dueño
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
    # Si estaba rentada pero ya expiró, liberarla antes de procesar
    if board.is_rented and board.rent_expires_at and board.rent_expires_at <= now:
        board.is_rented = False
        board.renter_id = None

    if board.is_rented:
        raise HTTPException(
            status_code=400,
            detail="Esta tabla ya está ocupada por otro inquilino.",
        )

    # Cobrar fee fija de GAL al arrendatario (renter) y dárselo al dueño (owner)
    renter_wallet = BankService.get_or_create_wallet(
        session, user_id, for_update=True
    )
    owner_wallet = BankService.get_or_create_wallet(
        session, board.user_id, for_update=True
    )

    fee = board.rent_fee_gal
    if renter_wallet.frijolitos < fee:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo de GAL insuficiente para rentar esta tabla (requieres {fee} GAL, tienes {renter_wallet.frijolitos} GAL).",
        )

    # Transferencia de saldo con 5% de burn
    burn_amount = fee * 0.05
    net_owner_amount = fee - burn_amount

    renter_wallet.frijolitos -= fee
    owner_wallet.frijolitos += net_owner_amount

    # Ledger para el arrendatario
    ledger_renter = TransactionLedger(
        user_id=user_id,
        amount=fee,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Renta de tabla #{board.id} a propietario {board.user_id}",
    )
    # Ledger para el propietario
    ledger_owner = TransactionLedger(
        user_id=board.user_id,
        amount=net_owner_amount,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Ingreso de renta recibida por tabla #{board.id} de arrendatario {user_id}",
    )
    # Ledger de burn
    ledger_burn = TransactionLedger(
        user_id=board.user_id,
        amount=burn_amount,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.BURN,
        description=f"Comisión de plataforma (5%) por renta de tabla #{board.id}",
    )

    # Registrar contrato
    board.is_rented = True
    board.renter_id = user_id
    board.rent_expires_at = now + timedelta(
        hours=24
    )  # Contrato clásico de 24 horas

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


# ─── Slot management ───────────────────────────────────────────────────

def get_slot_status_data(user_id: str, session: Session) -> dict:
    """Obtiene el estado de slots del usuario (desbloqueados, usados, estadísticas de desbloqueo)."""
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
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

    # Obtener estadísticas de juegos
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

    # Calcular requerimientos del siguiente slot
    reqs = get_slot_requirements(unlocked_slots)

    can_unlock = True
    reasons = []

    # Validar monedas
    wallet = BankService.get_or_create_wallet(session, user_id)
    if wallet.frijolitos < reqs["cost_gal"]:
        can_unlock = False
        reasons.append(
            f"Faltan {reqs['cost_gal'] - wallet.frijolitos:.1f} GAL"
        )

    # Validar partidas jugadas
    if total_games_played < reqs["games_played"]:
        can_unlock = False
        reasons.append(
            f"Se requieren {reqs['games_played']} partidas jugadas (tienes {total_games_played})"
        )

    # Validar partidas ganadas
    if total_games_won < reqs["games_won"]:
        can_unlock = False
        reasons.append(
            f"Se requieren {reqs['games_won']} partidas ganadas (tienes {total_games_won})"
        )

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
    }


def unlock_slot_operation(user_id: str, session: Session) -> dict:
    """Desbloquea el siguiente slot de tabla cobrando los GAL correspondientes y validando requisitos."""
    user_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    unlocked_slots = (
        user_record.unlocked_board_slots
        if user_record.unlocked_board_slots is not None
        else 3
    )

    # Calcular requerimientos
    reqs = get_slot_requirements(unlocked_slots)

    # 1. Validar estadísticas de juegos
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

    # 2. Validar saldo GAL
    wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
    if wallet.frijolitos < reqs["cost_gal"]:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Desbloquear el slot {unlocked_slots + 1} cuesta {reqs['cost_gal']} GAL.",
        )

    # 3. Cobrar y actualizar
    wallet.frijolitos -= reqs["cost_gal"]
    user_record.unlocked_board_slots = unlocked_slots + 1

    ledger = TransactionLedger(
        user_id=user_id,
        amount=reqs["cost_gal"],
        currency=CurrencyType.GEMA_ALGA,
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


# ─── Sale market helpers ───────────────────────────────────────────────

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

    # Obtener el tier de VIP del dueño
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
            status_code=400, detail="El precio de venta debe ser mayor a 0 GAL."
        )

    board.is_listed_for_sale = True
    board.sale_price_gal = sale_price_gal

    session.add(board)
    session.commit()

    return {
        "mensaje": f"Tabla '{board.name}' publicada en venta por {board.sale_price_gal} GAL.",
        "sale_price_gal": board.sale_price_gal,
    }


def cancel_sale_operation(
    board_id: int, user_id: str, session: Session
) -> dict:
    """Cancela la publicación de venta de un tablero."""
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
    if buyer_wallet.frijolitos < price:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo de GAL insuficiente para comprar esta tabla (cuesta {price} GAL, tienes {buyer_wallet.frijolitos} GAL).",
        )

    # --- Validar slots disponibles para el comprador ---
    buyer_record = session.exec(
        select(User).where(User.privy_did == user_id)
    ).first()
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

    # 1. Transferencia económica con 5% de comisión (burn)
    commission = price * 0.05
    seller_net = price - commission

    buyer_wallet.frijolitos -= price
    seller_wallet.frijolitos += seller_net

    # 2. Registrar comisión en el tesoro (AXG)
    treasury = session.exec(select(TreasuryVault)).first()
    if not treasury:
        treasury = TreasuryVault(balance=0.0)
        session.add(treasury)
    treasury.balance += commission

    # Ledgers
    ledger_buyer = TransactionLedger(
        user_id=user_id,
        amount=price,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Compra de tabla #{board.id} al propietario {board.user_id}",
    )
    ledger_seller = TransactionLedger(
        user_id=board.user_id,
        amount=seller_net,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Venta de tabla #{board.id} al comprador {user_id}",
    )
    ledger_commission = TransactionLedger(
        user_id=board.user_id,
        amount=commission,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.BURN,
        description=f"Comisión de plataforma (5%) por venta de tabla #{board.id}",
    )

    # 2. Transferencia on-chain del NFT de la tabla si existe token_id
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

    # 3. Reasignar propiedad y resetear banderas de venta
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
