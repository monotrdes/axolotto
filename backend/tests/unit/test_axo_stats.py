import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models.axolotito import Axolotito
from app.models.user import User
from app.models.items import ItemCatalog, WebitoIncubation, ItemType, Rarity
from app.models.lobby_models import GameRoom, RoomRegistration
from app.services.multiplayer_service import MultiplayerService
from app.api.v1.endpoints.game import sleep_axolotito
from app.api.v1.endpoints.multiplayer import settle_axolotito_escrow
from unittest.mock import patch

def test_salinity_energy_loss(session: Session):
    # Setup user and Axolotito
    user = User(privy_did="user_salinity", wallet_address="0x123", email="salinity@test.com")
    axo = Axolotito(
        id=101,
        user_id=user.privy_did,
        name="Salinity Axo",
        stat_salinity=50.0,  # 50.0 salinity -> extra_energy_loss = round(50.0 * 0.2) = 10
        energy_current=100,
        stat_stamina=100
    )
    session.add_all([user, axo])
    session.commit()

    # Create rookie room
    room = GameRoom(
        name="Rookie Room",
        room_type="rookie",
        entry_fee_gal=10.0,
        status="waiting"
    )
    session.add(room)
    session.commit()

    # Registration with 1 board (represented as list of IDs [1])
    reg = RoomRegistration(
        room_id=room.id,
        axolotito_id=axo.id,
        boards_json="[1]"
    )
    session.add(reg)
    session.commit()

    # Stub ItemCatalog cards (we need at least 16 cards for the bot sample)
    for i in range(1, 20):
        card = ItemCatalog(id=i, name=f"Card {i}", item_type=ItemType.CARD, rarity=Rarity.COMMON)
        session.add(card)
    session.commit()

    # Simulate match
    MultiplayerService.simulate_multiplayer_match(room.id)

    # Refresh Axo
    session.refresh(axo)

    # Base energy loss = 10
    # Extra salinity energy loss = round(50.0 * 0.2) = 10
    # Total expected loss = 20
    # Expected remaining energy = 100 - 20 = 80
    assert axo.energy_current == 80

def test_stamina_sleep_duration(session: Session):
    user = User(privy_did="user_stamina", wallet_address="0x456", email="stamina@test.com")
    axo = Axolotito(
        id=202,
        user_id=user.privy_did,
        name="Stamina Axo",
        energy_current=20,
        stat_stamina=200,  # 200 stamina -> raw multiplier = 1.0 - (150/300) = 0.5 (maximum mitigation)
        status="idle"
    )
    session.add_all([user, axo])
    session.commit()

    # Test sleep in game endpoint
    with patch("app.api.v1.endpoints.game.get_session", return_value=session), \
         patch("app.api.v1.endpoints.game.get_verified_user_id", return_value=user.privy_did):
        res = sleep_axolotito(axo_id=axo.id, session=session, verified_user_id=user.privy_did)
        session.refresh(axo)
        
        # Expected duration = 1 minute * 0.5 = 30 seconds
        time_diff = (axo.sleep_expires_at - datetime.utcnow()).total_seconds()
        assert 25 <= time_diff <= 35
        assert axo.status == "sleeping"

# NOTA: el mecanismo de calor/congelado/clima del criadero fue retirado.
# El test de mitigación de pérdida de calor por fuerza ya no aplica.
