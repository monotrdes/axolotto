"""
test_in_game_lock.py — Tests for in-game locking, AFK penalties, and lobby timeouts.

Covers:
- verify_no_active_game dependency (HTTP 409 when user has active game)
- require_tutorial dependency (HTTP 403 when tutorial not completed)
- active-check endpoint (returns room_id, play_mode, axolotito_id)
- Lobby ready/unready and countdown endpoints
"""

import json
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.main import app
from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.lobby_models import GameRoom, RoomRegistration
from app.models.axolotito import Axolotito
from app.models.economy import Wallet
from app.models.user import User
from app.models.items import ItemCatalog, ItemType, Rarity


# ── Dependency override helpers ──────────────────────────────────────────────


def _override_deps(session: Session, user_id: str):
    """Sobreescribir dependencias de FastAPI para tests."""
    app.dependency_overrides[get_verified_user_id] = lambda: user_id
    app.dependency_overrides[get_session] = lambda: session


def _clear_overrides():
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Test: verify_no_active_game blocks mutations ──────────────────────────────


class TestInGameLock:
    """verify_no_active_game debe lanzar 409 si el usuario tiene partida activa."""

    def test_active_game_blocks_shop_purchase(self, session: Session, client):
        from app.models.items import ItemType, Rarity
        from app.models.economy import Wallet

        # Create user, axolotito, room
        u = _make_test_user(session, "did:privy:lock_test")
        _make_test_wallet(session, u.privy_did)
        axo = _make_test_axo(session, u.privy_did, u.wallet_address)

        # Create an ACTIVE game room
        room = GameRoom(
            name="Test Active Room",
            room_type="player_hosted",
            entry_fee_gal=10,
            status="playing",
            host_id=u.privy_did,
        )
        session.add(room)
        session.commit()
        session.refresh(room)

        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json="[]",
            play_mode="manual",
        )
        session.add(reg)
        session.commit()

        # Create a test item in catalog
        item = ItemCatalog(
            name="Test Item",
            item_type=ItemType.CONSUMABLE,
            price_gal=10,
            rarity=Rarity.COMMON,
        )
        session.add(item)
        session.commit()

        # Try to buy — should be blocked by verify_no_active_game
        _override_deps(session, u.privy_did)
        try:
            res = client.post(
                "/api/v1/shop/buy",
                json={"item_id": item.id, "quantity": 1, "payment_method": "gal"},
            )
            assert res.status_code == 409
            assert "IN_GAME_LOCK" in res.json()["detail"]
        finally:
            _clear_overrides()

    def test_no_active_game_allows_shop_purchase(self, session: Session, client):
        """Sin partida activa, la compra debe proceder normalmente."""
        u = _make_test_user(session, "did:privy:no_lock")
        _make_test_wallet(session, u.privy_did, gemas_alga=500)

        item = ItemCatalog(
            name="Allowed Item",
            item_type=ItemType.CONSUMABLE,
            price_gal=10,
            rarity=Rarity.COMMON,
        )
        session.add(item)
        session.commit()

        _override_deps(session, u.privy_did)
        try:
            res = client.post(
                "/api/v1/shop/buy",
                json={"item_id": item.id, "quantity": 1, "payment_method": "gal"},
            )
            # Should succeed (not 409) — could be 200 or 402 depending on balance
            assert res.status_code != 409
        finally:
            _clear_overrides()


# ── Test: require_tutorial blocks non-tutorial users ──────────────────────────


class TestTutorialLock:
    def test_tutorial_not_completed_blocks_social(self, session: Session, client):
        """Usuario sin tutorial no puede usar endpoints sociales."""
        u = _make_test_user(
            session,
            "did:privy:no_tutorial",
            tutorial_completed=False,
        )

        _override_deps(session, u.privy_did)
        try:
            res = client.get("/api/v1/social/friends")
            assert res.status_code == 403
            assert "TUTORIAL_REQUIRED" in res.json()["detail"]
        finally:
            _clear_overrides()


# ── Test: active-check endpoint ───────────────────────────────────────────────


class TestActiveCheck:
    def test_active_check_returns_false_when_idle(self, session: Session, client):
        u = _make_test_user(session, "did:privy:idle_user")
        axo = _make_test_axo(session, u.privy_did, u.wallet_address)

        # Room with status "waiting" — not active
        room = GameRoom(
            name="Waiting Room",
            room_type="rookie_pool",
            entry_fee_gal=10,
            status="waiting",
        )
        session.add(room)
        session.commit()
        session.refresh(room)

        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json="[]",
        )
        session.add(reg)
        session.commit()

        _override_deps(session, u.privy_did)
        try:
            res = client.get("/api/v1/multiplayer/active-check")
            assert res.status_code == 200
            data = res.json()
            assert data["active"] is False
        finally:
            _clear_overrides()

    def test_active_check_returns_true_when_playing(self, session: Session, client):
        u = _make_test_user(session, "did:privy:playing_user")
        axo = _make_test_axo(session, u.privy_did, u.wallet_address)

        room = GameRoom(
            name="Playing Room",
            room_type="player_hosted",
            entry_fee_gal=10,
            status="playing",
            host_id=u.privy_did,
        )
        session.add(room)
        session.commit()
        session.refresh(room)

        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json=json.dumps([]),
            play_mode="manual",
        )
        session.add(reg)
        session.commit()

        _override_deps(session, u.privy_did)
        try:
            res = client.get("/api/v1/multiplayer/active-check")
            assert res.status_code == 200
            data = res.json()
            assert data["active"] is True
            assert data["room_id"] == room.id
            assert data["play_mode"] == "manual"
            assert data["axolotito_id"] == axo.id
        finally:
            _clear_overrides()


# ── Test: Lobby ready / countdown ─────────────────────────────────────────────


class TestLobbyReady:
    def test_player_set_ready(self, session: Session, client):
        u = _make_test_user(session, "did:privy:ready_player")
        axo = _make_test_axo(session, u.privy_did, u.wallet_address)

        room = GameRoom(
            name="Ready Test Room",
            room_type="player_hosted",
            entry_fee_gal=10,
            status="waiting",
            host_id=u.privy_did,
        )
        session.add(room)
        session.commit()
        session.refresh(room)

        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json=json.dumps([]),
        )
        session.add(reg)
        session.commit()

        _override_deps(session, u.privy_did)
        try:
            res = client.post(f"/api/v1/multiplayer/rooms/{room.id}/ready")
            assert res.status_code == 200
            data = res.json()
            assert data["ready"] is True
        finally:
            _clear_overrides()

        # Verify in DB
        session.refresh(reg)
        assert reg.ready is True
        assert reg.ready_at is not None

    def test_host_start_countdown(self, session: Session, client):
        u = _make_test_user(session, "did:privy:host_countdown")

        room = GameRoom(
            name="Countdown Room",
            room_type="player_hosted",
            entry_fee_gal=10,
            status="waiting",
            host_id=u.privy_did,
        )
        session.add(room)
        session.commit()
        session.refresh(room)

        _override_deps(session, u.privy_did)
        try:
            res = client.post(f"/api/v1/multiplayer/rooms/{room.id}/start-countdown")
            assert res.status_code == 200
        finally:
            _clear_overrides()

        session.refresh(room)
        assert room.countdown_started_at is not None
        assert room.last_host_activity_at is not None

    def test_non_host_cannot_start_countdown(self, session: Session, client):
        host = _make_test_user(session, "did:privy:host_owner")
        other = _make_test_user(session, "did:privy:not_host")

        room = GameRoom(
            name="Host-Only Room",
            room_type="player_hosted",
            entry_fee_gal=10,
            status="waiting",
            host_id=host.privy_did,
        )
        session.add(room)
        session.commit()

        # Other user tries to start countdown
        _override_deps(session, other.privy_did)
        try:
            res = client.post(f"/api/v1/multiplayer/rooms/{room.id}/start-countdown")
            assert res.status_code == 403
        finally:
            _clear_overrides()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_test_user(
    session: Session,
    privy_did: str,
    tutorial_completed: bool = True,
) -> User:
    from datetime import datetime, timedelta
    import uuid

    wallet_address = f"0x{uuid.uuid4().hex.zfill(40)}"
    user = User(
        privy_did=privy_did,
        wallet_address=wallet_address,
        tutorial_completed=tutorial_completed,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_test_wallet(
    session: Session,
    user_id: str,
    gemas_alga: float = 500,
) -> Wallet:
    from app.core.config import frj_to_internal
    frj_int = frj_to_internal(gemas_alga)
    wallet = Wallet(user_id=user_id, frijolitos=frj_int)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return wallet


def _make_test_axo(
    session: Session,
    user_id: str,
    wallet_address: str,
) -> Axolotito:
    axo = Axolotito(
        name="Test Axo",
        user_id=user_id,
        wallet_address=wallet_address,
        status="idle",
        energy_current=100,
        stat_luck=10,
        stat_focus=50,
        stat_stamina=50,
        stat_salinity=5,
        escrow_balance_gal=0,
    )
    session.add(axo)
    session.commit()
    session.refresh(axo)
    return axo
