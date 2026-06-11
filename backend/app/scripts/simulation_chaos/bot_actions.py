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


def _get_player_axolotitos_info(session: Session, user_id: str) -> list[dict]:
    """Get all axolotito IDs and statuses owned by a user."""
    axos = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_id)
    ).all()
    return [{"id": axo.id, "status": axo.status} for axo in axos]


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
    """Fetch a player's current state: axolotitos, boards, sealed boosters, tutorial status.

    Returns a dict with keys: axolotito_ids, board_ids, booster_inv_ids, tutorial_completed.
    Returns empty/default values if user not found or has no items.
    """
    def _fetch(session: Session) -> dict:
        user = _get_player_user(session, user_id)
        axos_info = _get_player_axolotitos_info(session, user_id)
        return {
            "axolotito_ids": [axo["id"] for axo in axos_info],
            "axolotitos": axos_info,
            "board_ids": _get_player_boards(session, user_id),
            "booster_inv_ids": _get_player_sealed_boosters(session, user_id),
            "tutorial_completed": user.tutorial_completed if user else False,
        }
    result = _action(_fetch, "fetch_state")
    if result.get("ok") and isinstance(result.get("detail"), dict):
        return result["detail"]
    return {"axolotito_ids": [], "axolotitos": [], "board_ids": [], "booster_inv_ids": [], "tutorial_completed": False}


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
        from app.api.v1.endpoints.board import list_board_for_sale, ListSaleRequest
        boards = _get_player_boards(session, user_id)
        if not boards:
            raise HTTPException(status_code=400, detail="No boards to sell")
        board_id = _rng.choice(boards)
        price = _rng.randint(50, 500)
        req = ListSaleRequest(sale_price_gal=float(price))
        return list_board_for_sale(board_id=board_id, payload=req, session=session, verified_user_id=user_id)

    result = _action(_fn, "list_board")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_buy_random_market_board(user_id: str) -> dict:
    """Buy a random listing (booster/card) from the P2P market."""
    def _fn(session: Session) -> Any:
        from app.api.v1.endpoints.market import buy_inventory_listing
        from app.models.items import InventoryMarketListing
        listings = session.exec(
            select(InventoryMarketListing).where(
                InventoryMarketListing.seller_id != user_id,
                InventoryMarketListing.is_active == True,
            )
        ).all()
        if not listings:
            raise HTTPException(status_code=404, detail="No market listings available")
        listing = _rng.choice(listings)
        return buy_inventory_listing(
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


def action_progress_tutorial(user_id: str) -> dict:
    """Simulates the step-by-step progress of the tutorial for a bot user.

    Fills the database state deterministically for the onboarding egg,
    then executes start_tutorial, advances phases (1 to 4) using play_tutorial_game + tutorial_next_step,
    and completes the tutorial using complete_tutorial (which hatches the axolotito).
    """
    from datetime import datetime, timedelta
    from app.models.items import WebitoIncubation, ItemCatalog, ItemType, PlayerInventory
    from app.services.tutorial_service import TutorialService
    from app.api.v1.endpoints.tutorial import (
        play_tutorial_game,
        tutorial_next_step,
        complete_tutorial as complete_tutorial_endpoint,
        NextStepBody,
        _board_from_user_id,
        _stats_from_user_id,
    )

    def _fn(session: Session) -> Any:
        # Check if user has already completed the tutorial
        user = _get_player_user(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        if user.tutorial_completed:
            return {"completed": True, "tutorial_phase": 5}

        # Find tutorial incubation
        inc = session.exec(
            select(WebitoIncubation)
            .where(WebitoIncubation.user_id == user_id)
            .where(WebitoIncubation.tutorial_phase < 5)
        ).first()

        if not inc:
            # 1. No incubation: grant onboarding egg and create tutorial incubation
            egg = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.EGG,
                    ItemCatalog.is_active == True,
                )
            ).first()
            if not egg:
                raise HTTPException(status_code=404, detail="No eggs active in catalog")

            # Check if user has egg in inventory
            inv = session.exec(
                select(PlayerInventory)
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == egg.id)
            ).first()
            if not inv:
                inv = PlayerInventory(user_id=user_id, item_id=egg.id, quantity=1)
                session.add(inv)
                session.flush()

            # Create incubation (phase 0)
            seed_stats = _stats_from_user_id(user_id)
            inc = WebitoIncubation(
                user_id=user_id,
                item_id=egg.id,
                fecha_eclosion_estimada=datetime.utcnow() - timedelta(seconds=10),
                bonus_focus=seed_stats["bonus_focus"],
                bonus_luck=seed_stats["bonus_luck"],
                bonus_stamina=seed_stats["bonus_stamina"],
                bonus_agility=seed_stats["bonus_agility"],
                bonus_salinity_adj=seed_stats["bonus_salinity_adj"],
                tutorial_phase=0,
                tutorial_act_index=0,
            )
            inc.tutorial_board_card_ids = _board_from_user_id(user_id, session)
            session.add(inc)
            session.commit()
            return {"completed": False, "tutorial_phase": 0}

        # 2. Existing incubation
        phase = inc.tutorial_phase
        if phase == 0:
            # Phase 0 -> 1: Start tutorial
            TutorialService.start_tutorial(session=session, user_id=user_id, incubation=inc)
            session.commit()
            return {"completed": False, "tutorial_phase": 1}
        elif 1 <= phase <= 3:
            # Phase 1->2->3->4: Play tutorial game + next step
            won = None
            try:
                game_res = play_tutorial_game(session=session, verified_user_id=user_id)
                won = (game_res.get("resultado") == "victoria")
            except HTTPException:
                won = None
            
            tutorial_next_step(
                incubation_id=inc.id,
                body=NextStepBody(won=won),
                session=session,
                verified_user_id=user_id,
            )
            session.commit()
            return {"completed": False, "tutorial_phase": phase + 1}
        elif phase == 4:
            # Phase 4 -> 5: Complete tutorial
            inc.tutorial_karma = _rng.choice(["lucky", "salty"])
            session.add(inc)
            session.flush()
            complete_tutorial_endpoint(
                incubation_id=inc.id,
                session=session,
                verified_user_id=user_id,
            )
            session.commit()
            return {"completed": True, "tutorial_phase": 5}
        else:
            # tutorial_phase >= 5, but user.tutorial_completed was somehow False
            user.tutorial_completed = True
            session.add(user)
            session.commit()
            return {"completed": True, "tutorial_phase": 5}

    result = _action(_fn, "progress_tutorial")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Staking Actions
# ═══════════════════════════════════════════════════════════════════════════════

def action_stake_axolotito(axo_id: int, user_id: str, status: str = "studying") -> dict:
    """Put an axolotito into staking (studying or resting)."""
    from app.services.staking_service import StakingService
    from datetime import datetime

    def _fn(session: Session) -> Any:
        user = _get_player_user(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        axolotito = session.exec(select(Axolotito).where(Axolotito.id == axo_id)).first()
        if not axolotito:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axolotito.user_id != user_id:
            raise HTTPException(status_code=403, detail="Este Axolotito no te pertenece.")
        if axolotito.status in ["studying", "resting"]:
            raise HTTPException(status_code=400, detail=f"Axolotito ya está en staking ({axolotito.status}).")
        if axolotito.status != "idle":
            raise HTTPException(status_code=400, detail=f"Axolotito no está ocioso ({axolotito.status}).")

        staked_count = len(session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .where(Axolotito.status.in_(["studying", "resting"]))
        ).all())

        max_slots = StakingService.get_staking_slots(user)
        if staked_count >= max_slots:
            raise HTTPException(status_code=400, detail="Límite de slots de staking alcanzado.")

        axolotito.status = status
        axolotito.last_staking_claim = datetime.utcnow()
        axolotito.accrued_unclaimed = 0
        session.add(axolotito)
        session.commit()
        
        # Track staking count
        increment_stat("axolotitos_staked")
        
        return {"id": axo_id, "status": status}

    result = _action(_fn, "stake")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result


def action_unstake_axolotito(axo_id: int, user_id: str) -> dict:
    """Take an axolotito out of staking and claim accrued rewards."""
    from app.services.staking_service import StakingService

    def _fn(session: Session) -> Any:
        user = _get_player_user(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        axolotito = session.exec(select(Axolotito).where(Axolotito.id == axo_id)).first()
        if not axolotito:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axolotito.user_id != user_id:
            raise HTTPException(status_code=403, detail="Este Axolotito no te pertenece.")
        if axolotito.status not in ["studying", "resting"]:
            raise HTTPException(status_code=400, detail="Axolotito no está en staking.")

        claim_result = StakingService.claim_staking_reward(session, axo_id, user)
        axolotito.status = "idle"
        session.add(axolotito)
        session.commit()
        
        # Track unstaking count
        increment_stat("axolotitos_unstaked")
        
        return {"id": axo_id, "status": "idle", "claimed_frj": claim_result.get("claimed_frj", 0.0)}

    result = _action(_fn, "unstake")
    increment_stat("bot_actions")
    if not result.get("ok"):
        increment_stat("bot_errors")
    return result
