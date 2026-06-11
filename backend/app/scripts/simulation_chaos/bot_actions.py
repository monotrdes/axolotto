"""
bot_actions.py — Atomic single-step actions for chaos simulator bots.

Each action opens its own Session(engine), calls the underlying service,
handles errors, and returns a standardized result dict: {"ok": bool, ...}.

All actions are thread-safe — they acquire the DB semaphore before opening
a session and release it after.
"""
import random as _stdlib_random
from typing import Optional, Any
from sqlmodel import Session, select
from fastapi import HTTPException

from app.database import engine
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.items import ItemCatalog, PlayerInventory, ItemType
from app.models.user import User
from app.services.game_service import GameService
from app.services.shop_service import ShopService
from app.services.bank_service import BankService
from app.services.lunar_streak_service import claim as lunar_claim
from app.models.economy import CurrencyType

from chaos_types import SecurityIncident, IncidentSeverity, _rng
from runtime_state import record_incident, increment_counter, increment_stat, get_db_semaphore


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _action(fn, category: str = "bot_action") -> dict:
    """Wrapper: acquire semaphore, open session, execute fn(session), handle errors."""
    sem = get_db_semaphore()
    acquired = False
    if sem:
        sem.acquire()
        acquired = True
    try:
        with Session(engine) as session:
            try:
                result = fn(session)
                # Many services commit internally; explicit commit is a no-op if already done
                try:
                    session.commit()
                except Exception:
                    pass
                return {"ok": True, "detail": result}
            except HTTPException as e:
                try:
                    session.rollback()
                except Exception:
                    pass
                return {"ok": False, "error_code": e.status_code, "detail": str(e.detail)[:200]}
            except Exception as e:
                try:
                    session.rollback()
                except Exception:
                    pass
                record_incident(SecurityIncident(
                    severity=IncidentSeverity.WARNING,
                    category=category,
                    description=f"Unexpected error: {type(e).__name__}",
                    status_code=500,
                    detail=str(e)[:200],
                    timestamp="",
                    thread_id=category,
                ))
                return {"ok": False, "error_code": 500, "detail": str(e)[:200]}
    finally:
        if acquired and sem:
            sem.release()


def _get_random_item_of_type(session: Session, item_type: ItemType) -> Optional[ItemCatalog]:
    """Get a random active item of the given type."""
    items = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == item_type,
            ItemCatalog.is_active == True,
        )
    ).all()
    if not items:
        return None
    return _rng.choice(items)


def _get_player_axolotitos(session: Session, user_id: str) -> list[int]:
    """Get all axolotito IDs owned by a user."""
    axos = session.exec(
        select(Axolotito.id).where(Axolotito.user_id == user_id)
    ).all()
    return list(axos)


def _get_player_boards(session: Session, user_id: str) -> list[int]:
    """Get all non-dead board IDs owned by a user."""
    boards = session.exec(
        select(PlayerBoard.id).where(
            PlayerBoard.user_id == user_id,
            PlayerBoard.is_dead == False,
        )
    ).all()
    return list(boards)


def _get_player_sealed_boosters(session: Session, user_id: str) -> list[int]:
    """Get all sealed booster inventory IDs for a user (boosters in inventory)."""
    rows = session.exec(
        select(PlayerInventory.id)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(
            PlayerInventory.user_id == user_id,
            ItemCatalog.item_type == ItemType.BOOSTER,
            PlayerInventory.quantity > 0,
        )
    ).all()
    return list(rows)


def _get_player_user(session: Session, user_id: str) -> Optional[User]:
    """Get the User object for a player."""
    return session.exec(select(User).where(User.privy_did == user_id)).first()


# ═══════════════════════════════════════════════════════════════════════════════
# Data fetch (not an action — used by bot init)
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_player_state(user_id: str) -> dict:
    """Fetch a player's current state: axolotitos, boards, sealed boosters.

    Returns a dict with keys: axolotito_ids, board_ids, booster_inv_ids.
    Returns empty lists if user not found or has no items.
    """
    def _fetch(session: Session) -> dict:
        return {
            "axolotito_ids": _get_player_axolotitos(session, user_id),
            "board_ids": _get_player_boards(session, user_id),
            "booster_inv_ids": _get_player_sealed_boosters(session, user_id),
        }
    result = _action(_fetch, "fetch_state")
    if result.get("ok") and isinstance(result.get("detail"), dict):
        return result["detail"]
    return {"axolotito_ids": [], "board_ids": [], "booster_inv_ids": []}


# ═══════════════════════════════════════════════════════════════════════════════
# Shop Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_buy_random_booster(user_id: str) -> dict:
    """Buy a random active booster from the shop."""
    def _fn(session: Session) -> Any:
        booster = _get_random_item_of_type(session, ItemType.BOOSTER)
        if not booster:
            raise HTTPException(status_code=404, detail="No boosters available in catalog")
        return ShopService.buy_item(session, user_id, booster.id, CurrencyType.AXOGEMA)

    result = _action(_fn, "buy_booster")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
        if result.get("error_code") == 500:
            increment_stat("bot_500s")
    return result


def action_open_booster(user_id: str, inventory_item_id: int) -> dict:
    """Open a specific sealed booster from inventory."""
    def _fn(session: Session) -> Any:
        return ShopService.open_booster(session, user_id, inventory_item_id)

    result = _action(_fn, "open_booster")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
        if result.get("error_code") == 500:
            increment_stat("bot_500s")
    return result


def action_buy_vip(user_id: str, tier: str) -> dict:
    """Buy a VIP subscription tier (coral, dorado, axolite)."""
    # Map tier to item name in catalog
    tier_to_item = {
        "coral": "VIP Coral",
        "dorado": "VIP Dorado",
        "axolite": "VIP Axolite",
    }
    item_name = tier_to_item.get(tier, "VIP Coral")

    def _fn(session: Session) -> Any:
        item = session.exec(
            select(ItemCatalog).where(ItemCatalog.name == item_name)
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"VIP item '{item_name}' not found")
        return ShopService.buy_item(session, user_id, item.id, CurrencyType.AXOGEMA)

    result = _action(_fn, "buy_vip")
    increment_stat("bot_actions")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Game Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_play_match(
    axolotito_id: int,
    user_id: str,
    room_name: str = "rookie",
    multiplier: int = 1,
    bot_enabled: bool = False,
    bot_budget_gal: float = 0.0,
    bot_loss_limit_pct: float = 30.0,
    bot_profit_limit_pct: float = 50.0,
) -> dict:
    """Play a solo lottery match with the given axolotito."""
    def _fn(session: Session) -> Any:
        return GameService.play_match(
            axolotito_id=axolotito_id,
            room_name=room_name,
            multiplier=multiplier,
            bot_enabled=bot_enabled,
            bot_budget_gal=bot_budget_gal,
            bot_loss_limit_pct=bot_loss_limit_pct,
            bot_profit_limit_pct=bot_profit_limit_pct,
            session=session,
            verified_user_id=user_id,
        )

    result = _action(_fn, "play_match")
    increment_stat("bot_actions")
    if result.get("ok"):
        increment_stat("games_played")
    else:
        increment_stat("bot_errors")
        if result.get("error_code") == 500:
            increment_stat("bot_500s")
    return result


def action_feed_axolotito(axo_id: int, user_id: str, food_type: str = "pellet") -> dict:
    """Feed an axolotito to restore energy."""
    def _fn(session: Session) -> Any:
        return GameService.feed_axolotito(
            axo_id=axo_id,
            food_type=food_type,
            session=session,
            verified_user_id=user_id,
        )

    result = _action(_fn, "feed")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_sleep_axolotito(axo_id: int, user_id: str) -> dict:
    """Put an axolotito to sleep."""
    def _fn(session: Session) -> Any:
        return GameService.sleep_axolotito(
            axo_id=axo_id,
            session=session,
            verified_user_id=user_id,
        )

    result = _action(_fn, "sleep")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_wake_axolotito(axo_id: int, user_id: str) -> dict:
    """Wake a sleeping axolotito."""
    def _fn(session: Session) -> Any:
        return GameService.wake_axolotito(
            axo_id=axo_id,
            session=session,
            verified_user_id=user_id,
        )

    result = _action(_fn, "wake")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Daily / VIP / Economy Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_claim_daily_reward(user_id: str) -> dict:
    """Claim the daily lunar cycle reward."""
    def _fn(session: Session) -> Any:
        user = _get_player_user(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return lunar_claim(session, user)

    result = _action(_fn, "claim_daily")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_claim_vip_frj(user_id: str) -> dict:
    """Claim pending VIP FRJ rewards."""
    from app.services.user_service import claim_vip_frj

    def _fn(session: Session) -> Any:
        return claim_vip_frj(session, user_id)

    result = _action(_fn, "claim_vip_frj")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Cave / Decor Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_equip_cave_item(axo_id: int, user_id: str) -> dict:
    """Equip a random cave item on an axolotito."""
    def _fn(session: Session) -> Any:
        # Get a random CAVE_ITEM from catalog
        cave_item = _get_random_item_of_type(session, ItemType.CAVE_ITEM)
        if not cave_item:
            raise HTTPException(status_code=404, detail="No cave items available")

        # Check if player owns this item in inventory
        inv = session.exec(
            select(PlayerInventory).where(
                PlayerInventory.user_id == user_id,
                PlayerInventory.item_id == cave_item.id,
                PlayerInventory.quantity > 0,
            )
        ).first()
        if not inv:
            raise HTTPException(status_code=400, detail="Player doesn't own this cave item")

        from app.services.cave_service import equip_cave_item
        return equip_cave_item(axo_id, cave_item.id, session, user_id)

    result = _action(_fn, "equip_cave")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Multiplayer Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_register_multiplayer(
    axolotito_id: int,
    user_id: str,
    board_ids: list[int],
    room_type: str = "rookie",
    budget_gal: float = 50.0,
    loss_limit_pct: float = 30.0,
    profit_limit_pct: float = 50.0,
) -> dict:
    """Register an axolotito for a multiplayer room."""
    from app.api.v1.endpoints.multiplayer import RegisterRequest, register_axolotito

    def _fn(session: Session) -> Any:
        req = RegisterRequest(
            axolotito_id=axolotito_id,
            room_type=room_type,
            boards=board_ids[:3],  # max 3 boards
            budget_gal=budget_gal,
            loss_limit_pct=loss_limit_pct,
            profit_limit_pct=profit_limit_pct,
            play_mode="auto",
        )
        return register_axolotito(req=req, session=session, verified_user_id=user_id)

    result = _action(_fn, "register_multi")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
        if result.get("error_code") == 500:
            increment_stat("bot_500s")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Gashapon Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_roll_gashapon(user_id: str, tier: str = "common") -> dict:
    """Roll the gashapon machine (common or premium tier, paying with FRJ)."""
    def _fn(session: Session) -> Any:
        from app.api.v1.endpoints.shop import roll_gashapon, GashaponRollRequest
        roll_type = "premium" if tier == "premium" else "common"
        req = GashaponRollRequest(roll_type=roll_type)
        return roll_gashapon(request=req, session=session, verified_user_id=user_id)

    result = _action(_fn, "roll_gashapon")
    increment_stat("bot_actions")
    if result.get("ok"):
        increment_stat("gashapon_rolls")
    else:
        increment_stat("bot_errors")
    return result


def action_roll_gashapon_ticket(user_id: str, tier: str = "common") -> dict:
    """Attempt a gashapon roll — ticket-based rolls use the same endpoint.
    If the player has a ticket, the endpoint handles it automatically.
    Falls back to FRJ payment if no ticket."""
    # The gashapon endpoint in shop.py currently only supports FRJ payment.
    # For now, this is the same as action_roll_gashapon but counted separately.
    return action_roll_gashapon(user_id, tier)


# ═══════════════════════════════════════════════════════════════════════════════
# Cave Expansion Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_expand_cave(user_id: str) -> dict:
    """Start or accelerate a cave expansion."""
    def _fn(session: Session) -> Any:
        from app.api.v1.endpoints.cave_expansion import start_expansion, accelerate_expansion
        # Try accelerating first (if an expansion is in progress)
        try:
            return accelerate_expansion(session=session, verified_user_id=user_id)
        except HTTPException:
            pass
        # Otherwise start a new expansion
        return start_expansion(session=session, verified_user_id=user_id)

    result = _action(_fn, "expand_cave")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Card Forge / Melter Action
# ═══════════════════════════════════════════════════════════════════════════════

def action_melt_random_card(user_id: str) -> dict:
    """Melt a random duplicate card into fragments via the Card Melter."""
    def _fn(session: Session) -> Any:
        from app.services.forge_service import melt_card
        from app.models.items import ItemCatalog as _IC, ItemType as _IT
        # Find player's cards (not boosters, not eggs)
        cards = session.exec(
            select(PlayerInventory)
            .join(_IC, PlayerInventory.item_id == _IC.id)
            .where(PlayerInventory.user_id == user_id)
            .where(_IC.item_type == ItemType.CARD)
            .where(PlayerInventory.quantity > 0)
        ).all()
        if not cards:
            raise HTTPException(status_code=400, detail="No cards to melt")
        card = _rng.choice(cards)
        return melt_card(
            session=session,
            user_id=user_id,
            card_id=card.item_id,
            is_first_edition=bool(card.is_first_edition),
        )

    result = _action(_fn, "melt_card")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Market P2P Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_list_board_for_sale(user_id: str) -> dict:
    """List a random board for sale on the P2P market."""
    def _fn(session: Session) -> Any:
        from app.api.v1.endpoints.market import list_board_for_sale, ListBoardRequest
        boards = _get_player_boards(session, user_id)
        if not boards:
            raise HTTPException(status_code=400, detail="No boards to sell")
        board_id = _rng.choice(boards)
        price = _rng.randint(50, 500)
        req = ListBoardRequest(board_id=board_id, price_gal=price)
        return list_board_for_sale(req=req, session=session, verified_user_id=user_id)

    result = _action(_fn, "list_board")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_buy_random_market_board(user_id: str) -> dict:
    """Buy a random board from the P2P market."""
    def _fn(session: Session) -> Any:
        from app.api.v1.endpoints.market import buy_listed_board
        from app.models.market import InventoryMarketListing
        listings = session.exec(
            select(InventoryMarketListing).where(
                InventoryMarketListing.seller_id != user_id,
                InventoryMarketListing.status == "active",
            )
        ).all()
        if not listings:
            raise HTTPException(status_code=404, detail="No market listings available")
        listing = _rng.choice(listings)
        return buy_listed_board(
            listing_id=listing.id,
            session=session,
            verified_user_id=user_id,
        )

    result = _action(_fn, "buy_market_board")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Bulk data refresh for bot state
# ═══════════════════════════════════════════════════════════════════════════════

def refresh_bot_state(user_id: str) -> dict:
    """Refresh a bot's state (axolotitos, boards, boosters).

    Called periodically by the bot loop to pick up new items/axolotitos
    created by previous actions or by other bots (market, breeding, etc.).
    """
    return fetch_player_state(user_id)
