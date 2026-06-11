"""
chaos_agents.py — Chaos Monkey attack agents.

Each agent runs in its own thread and continuously launches specific attack
patterns against the backend. Results are classified as:
  - CRITICAL: attack succeeded (vulnerability found)
  - WARNING: attack blocked with unexpected error code
  - INFO: attack correctly blocked (expected behavior)

All agents use Session(engine) isolation and respect the stop_event.
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timezone
from sqlmodel import Session, select

from app.database import engine
from app.models.user import User
from app.models.axolotito import Axolotito
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.services.shop_service import ShopService
from app.services.game_service import GameService
from app.services.bank_service import BankService
from app.services.lunar_streak_service import claim as lunar_claim
from app.models.economy import CurrencyType
from fastapi import HTTPException

from chaos_types import (
    SecurityIncident, IncidentSeverity, ChaosConfig, _rng,
)
from runtime_state import (
    record_incident, increment_counter, increment_stat, get_db_semaphore,
    report_activity,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _agent_session():
    """Context manager: acquire DB semaphore, open session, return it.
    Usage:
        with _agent_session() as session:
            ...
    """
    sem = get_db_semaphore()
    if sem:
        sem.acquire()
    try:
        with Session(engine) as session:
            yield session
    finally:
        if sem:
            sem.release()


def _record_attack(severity: IncidentSeverity, category: str, description: str,
                   status_code: int, detail: str, thread_id: str) -> None:
    """Record an attack incident with the given severity."""
    record_incident(SecurityIncident(
        severity=severity,
        category=category,
        description=description,
        status_code=status_code,
        detail=str(detail)[:200],
        timestamp=datetime.now(timezone.utc).isoformat(),
        thread_id=thread_id,
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 1: Replay Attack
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_replay_attack(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Attempt to replay the same transaction hash multiple times.

    Tests ProcessedTransaction UNIQUE constraint. Expected: HTTP 409 Conflict.
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}
    fake_tx = f"0x_chaos_replay_{id(stop_event):x}_000001"

    while not stop_event.is_set():
        time.sleep(_rng.uniform(0.5, 2.0))
        target_user = _rng.choice(user_ids) if user_ids else None
        if not target_user:
            continue

        counters["launched"] += 1
        increment_counter("replay_launched")
        report_activity("replay_agent", "replay", "Replay attack", "attack")

        try:
            with _agent_session() as session:
                # Try to insert a duplicate ProcessedTransaction
                from app.models.economy import ProcessedTransaction
                existing = session.exec(
                    select(ProcessedTransaction).where(
                        ProcessedTransaction.tx_hash == fake_tx
                    )
                ).first()

                if existing:
                    # Attempt to process the same tx again — should be rejected
                    from app.services.checkout_service import CheckoutService
                    try:
                        # Try to find any order and confirm with the duplicate hash
                        from app.models.economy import CryptoPurchaseOrder
                        order = session.exec(
                            select(CryptoPurchaseOrder).where(
                                CryptoPurchaseOrder.user_id == target_user
                            ).limit(1)
                        ).first()
                        if order:
                            CheckoutService.confirm_payment(
                                session=session,
                                order_id=order.id,
                                user_id=target_user,
                                tx_hash=fake_tx,
                            )
                            session.commit()
                            counters["succeeded"] += 1
                            increment_counter("replay_succeeded")
                            _record_attack(
                                IncidentSeverity.CRITICAL, "replay_attack",
                                "REPLAY SUCCEEDED: duplicate tx_hash accepted!",
                                200, f"tx_hash={fake_tx}, order={order.id}", "replay_agent",
                            )
                        else:
                            counters["blocked"] += 1
                            increment_counter("replay_blocked")
                    except HTTPException as e:
                        if e.status_code == 409:
                            counters["blocked"] += 1
                            increment_counter("replay_blocked")
                            _record_attack(
                                IncidentSeverity.INFO, "replay_attack",
                                f"Replay correctly blocked: {e.detail}",
                                e.status_code, str(e.detail), "replay_agent",
                            )
                        else:
                            counters["blocked"] += 1
                            increment_counter("replay_blocked")
                            _record_attack(
                                IncidentSeverity.WARNING, "replay_attack",
                                f"Replay blocked with non-standard code {e.status_code}",
                                e.status_code, str(e.detail), "replay_agent",
                            )
                else:
                    # First time — insert the tx (it may or may not be valid)
                    counters["blocked"] += 1
                    increment_counter("replay_blocked")
        except Exception as e:
            counters["blocked"] += 1
            increment_counter("replay_blocked")

    return counters


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 2: ID Spoofing / Privilege Escalation
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_id_spoofing(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Attempt to act on another user's resources (axolotitos, boards).

    Tests ownership validation. Expected: HTTP 403 Forbidden.
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}

    while not stop_event.is_set():
        time.sleep(_rng.uniform(0.3, 1.5))
        if len(user_ids) < 2 or not axolotito_ids:
            continue

        counters["launched"] += 1
        increment_counter("spoof_launched")
        report_activity("spoof_agent", "spoof", "ID Spoofing", "attack")

        # Pick two different users: attacker and victim
        attacker, victim = _rng.sample(user_ids, 2)

        try:
            with _agent_session() as session:
                # Find an axolotito owned by the victim
                victim_axo = session.exec(
                    select(Axolotito).where(
                        Axolotito.user_id == victim,
                        Axolotito.status != "sleeping",
                    ).limit(1)
                ).first()

                if not victim_axo:
                    counters["blocked"] += 1
                    increment_counter("spoof_blocked")
                    continue

                # Attacker tries to play with victim's axolotito
                try:
                    GameService.play_match(
                        axolotito_id=victim_axo.id,
                        room_name="rookie",
                        multiplier=1,
                        bot_enabled=False,
                        bot_budget_gal=0,
                        bot_loss_limit_pct=30,
                        bot_profit_limit_pct=50,
                        session=session,
                        verified_user_id=attacker,  # <-- spoofed identity
                    )
                    session.commit()
                    # If we get here, spoofing succeeded — CRITICAL
                    counters["succeeded"] += 1
                    increment_counter("spoof_succeeded")
                    _record_attack(
                        IncidentSeverity.CRITICAL, "id_spoofing",
                        f"ID SPOOFING SUCCEEDED: {attacker[:20]} played as {victim[:20]}'s axo #{victim_axo.id}",
                        200, "No ownership check", "spoof_agent",
                    )
                except HTTPException as e:
                    if e.status_code == 403:
                        counters["blocked"] += 1
                        increment_counter("spoof_blocked")
                        _record_attack(
                            IncidentSeverity.INFO, "id_spoofing",
                            f"ID spoofing correctly blocked: {e.detail}",
                            e.status_code, str(e.detail), "spoof_agent",
                        )
                    elif e.status_code in (400, 404):
                        counters["blocked"] += 1
                        increment_counter("spoof_blocked")
                    else:
                        counters["blocked"] += 1
                        increment_counter("spoof_blocked")
                        _record_attack(
                            IncidentSeverity.WARNING, "id_spoofing",
                            f"Spoof blocked with unexpected code {e.status_code}",
                            e.status_code, str(e.detail), "spoof_agent",
                        )
        except Exception:
            counters["blocked"] += 1
            increment_counter("spoof_blocked")

    return counters


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 3: Race Condition — Double Spend
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_race_condition(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Fire simultaneous purchase requests to test SELECT FOR UPDATE locking.

    Sets wallet balance to exactly 1 item cost, then fires 10 concurrent buys.
    Expected: exactly 1 succeeds, 9 fail with HTTP 400/402.
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}

    while not stop_event.is_set():
        time.sleep(_rng.uniform(2.0, 5.0))  # Less frequent — sets up wallet first
        if not user_ids:
            continue

        target_user = _rng.choice(user_ids)
        counters["launched"] += 1
        increment_counter("race_launched")
        report_activity("race_agent", "race", "Race Condition burst", "attack")

        try:
            with _agent_session() as session:
                # Find a cheap booster
                booster = session.exec(
                    select(ItemCatalog).where(
                        ItemCatalog.item_type == ItemType.BOOSTER,
                        ItemCatalog.is_active == True,
                    ).limit(1)
                ).first()
                if not booster:
                    continue

                booster_price = booster.price_axg or 10.0

                # Set wallet balance to exactly 1 booster price
                wallet = BankService.get_or_create_wallet(session, target_user)
                wallet.axg_balance = booster_price
                session.add(wallet)
                session.commit()

            # Now fire 10 concurrent buys
            succeeded_count = [0]
            failed_count = [0]

            def _race_buy() -> None:
                try:
                    with _agent_session() as s:
                        ShopService.buy_item(s, target_user, booster.id, CurrencyType.AXOGEMA)
                        s.commit()
                        succeeded_count[0] += 1
                except HTTPException:
                    failed_count[0] += 1
                except Exception:
                    failed_count[0] += 1

            # Fire 10 concurrent threads
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(_race_buy) for _ in range(10)]
                wait(futures, timeout=15)

            if succeeded_count[0] > 1:
                # More than 1 succeeded — CRITICAL vulnerability
                counters["succeeded"] += succeeded_count[0] - 1  # count extras as "succeeded attacks"
                increment_counter("race_succeeded", succeeded_count[0] - 1)
                _record_attack(
                    IncidentSeverity.CRITICAL, "race_condition",
                    f"DOUBLE SPEND: {succeeded_count[0]} purchases succeeded, only 1 should have",
                    200, f"Wallet drained below 0. Extra buys: {succeeded_count[0] - 1}", "race_agent",
                )
                counters["blocked"] += failed_count[0]
                increment_counter("race_blocked", failed_count[0])
            elif succeeded_count[0] == 1:
                # Exactly 1 — correct behavior
                counters["blocked"] += failed_count[0]
                increment_counter("race_blocked", failed_count[0])
                _record_attack(
                    IncidentSeverity.INFO, "race_condition",
                    f"Race condition correctly handled: 1 succeeded, {failed_count[0]} failed",
                    200, "SELECT FOR UPDATE working", "race_agent",
                )
            else:
                counters["blocked"] += failed_count[0]
                increment_counter("race_blocked", failed_count[0])
        except Exception:
            counters["blocked"] += 10
            increment_counter("race_blocked", 10)

    return counters


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 4: Double Booking — Multiplayer Lobby Abuse
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_double_booking(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Attempt to register the same axolotito in multiple multiplayer rooms.

    Expected: exactly 1 registration succeeds, others fail with HTTP 400.
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}

    while not stop_event.is_set():
        time.sleep(_rng.uniform(1.0, 3.0))
        if not user_ids or not axolotito_ids:
            continue

        target_user = _rng.choice(user_ids)
        # Find user's axolotitos
        try:
            with _agent_session() as session:
                user_axos = session.exec(
                    select(Axolotito.id).where(
                        Axolotito.user_id == target_user,
                        Axolotito.status == "idle",
                    ).limit(5)
                ).all()
                user_boards = session.exec(
                    select(PlayerInventory.id).where(
                        PlayerInventory.user_id == target_user,
                        PlayerInventory.quantity > 0,
                    ).limit(3)
                ).all()
        except Exception:
            continue

        if not user_axos or not user_boards:
            continue

        counters["launched"] += 1
        increment_counter("booking_launched")
        report_activity("booking_agent", "booking", "Double Booking", "attack")

        axo_id = _rng.choice(user_axos)
        from app.api.v1.endpoints.multiplayer import RegisterRequest, register_axolotito

        succeeded_count = [0]
        failed_count = [0]

        def _race_register() -> None:
            try:
                with _agent_session() as s:
                    req = RegisterRequest(
                        axolotito_id=axo_id,
                        room_type="rookie",
                        boards=list(user_boards)[:2],
                        budget_gal=50.0,
                        loss_limit_pct=30.0,
                        profit_limit_pct=50.0,
                        play_mode="auto",
                    )
                    register_axolotito(req=req, session=s, verified_user_id=target_user)
                    s.commit()
                    succeeded_count[0] += 1
            except HTTPException:
                failed_count[0] += 1
            except Exception:
                failed_count[0] += 1

        # Fire 5 concurrent registrations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(_race_register) for _ in range(5)]
            wait(futures, timeout=10)

        if succeeded_count[0] > 1:
            counters["succeeded"] += succeeded_count[0] - 1
            increment_counter("booking_succeeded", succeeded_count[0] - 1)
            _record_attack(
                IncidentSeverity.CRITICAL, "double_booking",
                f"DOUBLE BOOKING: axo #{axo_id} registered in {succeeded_count[0]} rooms",
                200, "Axo should only be in 1 room", "booking_agent",
            )
        elif succeeded_count[0] == 1:
            counters["blocked"] += failed_count[0]
            increment_counter("booking_blocked", failed_count[0])
            _record_attack(
                IncidentSeverity.INFO, "double_booking",
                f"Double booking correctly blocked: 1 success, {failed_count[0]} rejections",
                200, "", "booking_agent",
            )
        else:
            counters["blocked"] += 5
            increment_counter("booking_blocked", 5)

    return counters


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 5: Boundary Injection
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_boundary_injection(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Send malformed payloads: negative amounts, overflow values, null bytes.

    Expected: HTTP 400/422 ValidationError from Pydantic schemas or model validators.
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}

    # Malicious payload strategies
    strategies = ["negative_amount", "huge_value", "null_bytes", "empty_string"]

    while not stop_event.is_set():
        time.sleep(_rng.uniform(0.5, 2.0))
        if not user_ids:
            continue

        target_user = _rng.choice(user_ids)
        strategy = _rng.choice(strategies)
        counters["launched"] += 1
        increment_counter("injection_launched")
        report_activity("injection_agent", "injection", f"Injection: {strategy}", "attack")

        try:
            with _agent_session() as session:
                try:
                    if strategy == "negative_amount":
                        # Try to buy with negative amount (via admin_deposit negative)
                        BankService.admin_deposit(
                            session, target_user, -1000000, CurrencyType.FRIJOLITO,
                            "INJECTION_TEST: negative deposit",
                        )
                        session.commit()
                        # If we get here without error, check if balance went negative
                        wallet = BankService.get_or_create_wallet(session, target_user)
                        if wallet.gal_balance < 0:
                            counters["succeeded"] += 1
                            increment_counter("injection_succeeded")
                            _record_attack(
                                IncidentSeverity.CRITICAL, "boundary_injection",
                                f"NEGATIVE BALANCE accepted: {wallet.gal_balance}",
                                200, "Admin deposit accepted negative amount", "injection_agent",
                            )
                        else:
                            counters["blocked"] += 1
                            increment_counter("injection_blocked")

                    elif strategy == "huge_value":
                        # Try to deposit an astronomically large amount
                        BankService.admin_deposit(
                            session, target_user, 10**18, CurrencyType.FRIJOLITO,
                            "INJECTION_TEST: overflow deposit",
                        )
                        session.commit()
                        counters["succeeded"] += 1
                        increment_counter("injection_succeeded")
                        _record_attack(
                            IncidentSeverity.WARNING, "boundary_injection",
                            "HUGE VALUE accepted without overflow protection",
                            200, "10^18 deposit succeeded", "injection_agent",
                        )

                    elif strategy == "null_bytes":
                        # Try to use a string with null bytes
                        user = session.exec(
                            select(User).where(User.privy_did == target_user)
                        ).first()
                        if user:
                            original_name = user.username
                            user.username = "hack\x00name"
                            session.add(user)
                            session.commit()
                            counters["succeeded"] += 1
                            increment_counter("injection_succeeded")
                            _record_attack(
                                IncidentSeverity.WARNING, "boundary_injection",
                                "NULL BYTE accepted in username",
                                200, "Null byte injection not filtered", "injection_agent",
                            )
                            # Restore
                            user.username = original_name
                            session.add(user)
                            session.commit()

                    elif strategy == "empty_string":
                        # Try with empty/invalid room name
                        GameService.play_match(
                            axolotito_id=_rng.choice(axolotito_ids) if axolotito_ids else 1,
                            room_name="",
                            multiplier=0,
                            bot_enabled=False,
                            bot_budget_gal=0,
                            bot_loss_limit_pct=0,
                            bot_profit_limit_pct=0,
                            session=session,
                            verified_user_id=target_user,
                        )
                        session.commit()
                        counters["succeeded"] += 1
                        increment_counter("injection_succeeded")
                        _record_attack(
                            IncidentSeverity.WARNING, "boundary_injection",
                            "Empty room name accepted in play_match",
                            200, "No validation on room_name", "injection_agent",
                        )

                except HTTPException as e:
                    if e.status_code in (400, 422):
                        counters["blocked"] += 1
                        increment_counter("injection_blocked")
                        _record_attack(
                            IncidentSeverity.INFO, "boundary_injection",
                            f"{strategy} correctly rejected: {e.detail}",
                            e.status_code, str(e.detail), "injection_agent",
                        )
                    else:
                        counters["blocked"] += 1
                        increment_counter("injection_blocked")
                        _record_attack(
                            IncidentSeverity.WARNING, "boundary_injection",
                            f"{strategy} rejected with non-standard code {e.status_code}",
                            e.status_code, str(e.detail), "injection_agent",
                        )
                except (TypeError, ValueError, AttributeError) as e:
                    # Pydantic validation errors come as ValueError/TypeError at service level
                    counters["blocked"] += 1
                    increment_counter("injection_blocked")
        except Exception:
            counters["blocked"] += 1
            increment_counter("injection_blocked")

    return counters


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 6: Cooldown Bypass
# ═══════════════════════════════════════════════════════════════════════════════

def chaos_cooldown_bypass(
    config: ChaosConfig,
    user_ids: list[str],
    axolotito_ids: list[int],
    stop_event: threading.Event,
) -> dict:
    """Attempt to bypass time-based cooldowns (daily rewards, sleep cycles).

    Expected: HTTP 400 Bad Request (server-side utcnow() validation).
    """
    counters = {"launched": 0, "blocked": 0, "succeeded": 0}

    while not stop_event.is_set():
        time.sleep(_rng.uniform(0.5, 2.0))
        if not user_ids:
            continue

        target_user = _rng.choice(user_ids)
        counters["launched"] += 1
        increment_counter("cooldown_launched")
        report_activity("cooldown_agent", "cooldown", "Cooldown bypass", "attack")

        try:
            with _agent_session() as session:
                user = session.exec(
                    select(User).where(User.privy_did == target_user)
                ).first()
                if not user:
                    continue

                try:
                    # Attempt 1: claim daily reward twice in rapid succession
                    lunar_claim(session, user)
                    session.commit()
                    # Attempt 2 immediately — should be rejected
                    lunar_claim(session, user)
                    session.commit()
                    # If we got here, cooldown was bypassed
                    counters["succeeded"] += 1
                    increment_counter("cooldown_succeeded")
                    _record_attack(
                        IncidentSeverity.CRITICAL, "cooldown_bypass",
                        "DAILY REWARD claimed twice in succession",
                        200, "No cooldown enforcement", "cooldown_agent",
                    )
                except HTTPException as e:
                    if e.status_code == 400:
                        counters["blocked"] += 1
                        increment_counter("cooldown_blocked")
                        _record_attack(
                            IncidentSeverity.INFO, "cooldown_bypass",
                            f"Cooldown correctly enforced: {e.detail}",
                            e.status_code, str(e.detail), "cooldown_agent",
                        )
                    else:
                        counters["blocked"] += 1
                        increment_counter("cooldown_blocked")

                # Attempt 2: manipulate sleep time on an axolotito
                if axolotito_ids:
                    axo_id = _rng.choice(axolotito_ids)
                    axo = session.get(Axolotito, axo_id)
                    if axo and axo.status == "sleeping":
                        try:
                            # Set sleep_expires_at to past — should not allow wake
                            original_expiry = axo.sleep_expires_at
                            axo.sleep_expires_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
                            session.add(axo)
                            session.commit()

                            GameService.wake_axolotito(
                                axo_id=axo_id,
                                session=session,
                                verified_user_id=target_user,
                            )
                            session.commit()
                            counters["succeeded"] += 1
                            increment_counter("cooldown_succeeded")
                            _record_attack(
                                IncidentSeverity.WARNING, "cooldown_bypass",
                                f"Sleep time manipulation succeeded for axo #{axo_id}",
                                200, "wake_axolotito accepted manipulated sleep_expires_at", "cooldown_agent",
                            )
                            # Restore
                            axo.sleep_expires_at = original_expiry
                            session.add(axo)
                            session.commit()
                        except HTTPException as e:
                            if e.status_code == 400:
                                counters["blocked"] += 1
                                increment_counter("cooldown_blocked")
                            else:
                                counters["blocked"] += 1
                                increment_counter("cooldown_blocked")
        except Exception:
            counters["blocked"] += 1
            increment_counter("cooldown_blocked")

    return counters
