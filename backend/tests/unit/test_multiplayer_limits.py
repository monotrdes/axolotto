import pytest
import json
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet
from app.models.lobby_models import GameRoom, RoomRegistration
from app.models.user import User
from app.api.v1.endpoints.multiplayer import register_axolotito, RegisterRequest
from app.services.multiplayer_service import get_or_create_waiting_room, MultiplayerService

from tests.conftest import make_user, make_wallet

def setup_test_entities(session: Session):
    # Crear usuarios
    user_a = make_user(session, privy_did="user_a", wallet_address="0x111")
    user_b = make_user(session, privy_did="user_b", wallet_address="0x222")
    user_c = make_user(session, privy_did="user_c", wallet_address="0x333") # Distinta wallet para evitar IntegrityError en BD

    # Crear wallets con fondos
    make_wallet(session, user_id="user_a", gemas_alga=1000.0)
    make_wallet(session, user_id="user_b", gemas_alga=1000.0)
    make_wallet(session, user_id="user_c", gemas_alga=1000.0)

    # Crear Axolotitos
    axo_a = Axolotito(
        name="Axo A",
        user_id="user_a",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=50,
        stat_luck=10,
    )
    axo_b = Axolotito(
        name="Axo B",
        user_id="user_b",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=50,
        stat_luck=10,
    )
    axo_c = Axolotito(
        name="Axo C",
        user_id="user_c",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=50,
        stat_luck=10,
    )
    session.add(axo_a)
    session.add(axo_b)
    session.add(axo_c)
    session.commit()

    # Crear Tablas (PlayerBoard)
    for i in range(1, 4):
        session.add(PlayerBoard(id=i, user_id="user_a", is_dead=False))
        session.add(PlayerBoard(id=i+3, user_id="user_b", is_dead=False))
        session.add(PlayerBoard(id=i+6, user_id="user_c", is_dead=False))
    session.commit()

    return user_a, user_b, user_c, axo_a, axo_b, axo_c


def test_user_registration_limit(session):
    user_a, _, _, axo_a, _, _ = setup_test_entities(session)

    # Inscribir primer Axolotito
    req1 = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[1],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req1, session, verified_user_id="user_a")

    # Intentar inscribir de nuevo con el mismo usuario (mientras el primero está en espera)
    # Creamos un segundo axolotito para user_a para intentar registrarlo
    axo_a2 = Axolotito(
        name="Axo A2",
        user_id="user_a",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=50,
        stat_luck=10,
    )
    session.add(axo_a2)
    session.commit()

    req2 = RegisterRequest(
        axolotito_id=axo_a2.id,
        room_type="rookie",
        boards=[3],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    with pytest.raises(HTTPException) as exc:
        register_axolotito(req2, session, verified_user_id="user_a")
    assert exc.value.status_code == 400
    assert "Ya tienes un Axolotito en sala de espera" in exc.value.detail


def test_wallet_registration_limit(session):
    user_a, _, user_c, axo_a, _, axo_c = setup_test_entities(session)

    # Inscribir user_a (wallet 0x111)
    req1 = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[1],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req1, session, verified_user_id="user_a")

    # Intentar inscribir user_c (mismo wallet 0x111)
    user_c.__dict__["wallet_address"] = "0x111"
    req2 = RegisterRequest(
        axolotito_id=axo_c.id,
        room_type="rookie",
        boards=[7],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    with pytest.raises(HTTPException) as exc:
        register_axolotito(req2, session, verified_user_id="user_c")
    assert exc.value.status_code == 400
    assert "vinculado a tu dirección de billetera (0x111)" in exc.value.detail


def test_boards_limit_per_room(session):
    user_a, _, user_c, axo_a, _, axo_c = setup_test_entities(session)

    # Para probar el límite de 5 tablas por wallet en la misma sala,
    # primero creamos manualmente una sala en espera y registramos a user_a con 3 tablas
    room = GameRoom(name="Sala Test", room_type="rookie", entry_fee_gal=10.0, status="waiting")
    session.add(room)
    session.commit()

    reg_a = RoomRegistration(
        room_id=room.id,
        axolotito_id=axo_a.id,
        boards_json=json.dumps([1, 2, 3]) # 3 tablas
    )
    session.add(reg_a)
    axo_a.status = "playing"
    session.add(axo_a)
    session.commit()

    # Ahora intentamos registrar a user_c (mismo wallet) con 3 tablas en esa misma sala.
    # El total acumulado sería 3 + 3 = 6, superando el límite de 5.
    # Nota: para forzar que caiga en la misma sala a nivel de get_or_create_waiting_room,
    # temporalmente llamamos al registro normal.
    # Pero get_or_create_waiting_room debería segregar las wallets y tirarlo a otra sala!
    # Validamos que get_or_create_waiting_room nos mande a OTRA sala
    user_c.__dict__["wallet_address"] = "0x111"
    new_room = get_or_create_waiting_room(session, "rookie", 3, user_id="user_c")
    assert new_room.id != room.id

    # Si por alguna razón forzamos la misma sala (bypass de get_or_create_waiting_room)
    # y llamamos la lógica de verificación de register_axolotito directamente:
    # Vamos a probar que si intentamos registrar más de 5 en total en la misma sala, se bloquea.
    # Para simular esto, mockeamos get_or_create_waiting_room para que devuelva la misma sala 'room'
    # y envolvemos session.exec para que ignore los checks de registro existente/billetera.
    from unittest.mock import patch, MagicMock
    original_exec = session.exec
    def mock_exec(statement, *args, **kwargs):
        stmt_str = str(statement).lower()
        if "join" in stmt_str and "roomregistration" in stmt_str:
            mock_result = MagicMock()
            mock_result.first.return_value = None
            return mock_result
        return original_exec(statement, *args, **kwargs)

    user_c.__dict__["wallet_address"] = "0x111"
    with patch("app.api.v1.endpoints.multiplayer.get_or_create_waiting_room", return_value=room):
        with patch.object(session, "exec", side_effect=mock_exec):
            req_c = RegisterRequest(
                axolotito_id=axo_c.id,
                room_type="rookie",
                boards=[7, 8, 9], # 3 tablas
                budget_gal=300.0,
                loss_limit_pct=30.0,
                profit_limit_pct=50.0
            )
            with pytest.raises(HTTPException) as exc:
                register_axolotito(req_c, session, verified_user_id="user_c")
            assert exc.value.status_code == 400
            assert "superaría el límite de 5 tablas" in exc.value.detail


def test_get_or_create_waiting_room_segregation(session):
    user_a, _, user_c, axo_a, _, _ = setup_test_entities(session)

    # 1. Crear una sala y meter a user_a
    room_1 = get_or_create_waiting_room(session, "rookie", 2, user_id="user_a")
    reg_a = RoomRegistration(
        room_id=room_1.id,
        axolotito_id=axo_a.id,
        boards_json=json.dumps([1, 2])
    )
    session.add(reg_a)
    session.commit()

    # 2. Intentar buscar/crear sala para user_c (mismo wallet)
    # Debería crear una sala nueva (room_2) en lugar de retornar room_1,
    # ya que user_a (mismo wallet) ya está en room_1.
    user_c.__dict__["wallet_address"] = "0x111"
    room_2 = get_or_create_waiting_room(session, "rookie", 1, user_id="user_c")
    assert room_2.id != room_1.id


def test_randomness_properties():
    # Comprobar que MultiplayerService usa SystemRandom para la mezcla
    from app.services.multiplayer_service import _rng
    import random
    assert isinstance(_rng, random.SystemRandom)

    # Comprobar que no hay predicción basada en semillas estándar (no-seeding)
    # Generar 5 barajas de 50 elementos y verificar que la probabilidad de que
    # todas sean idénticas es extremadamente baja (indicando aleatoriedad CSPRNG)
    deck_base = list(range(50))
    decks = []
    for _ in range(5):
        d = deck_base.copy()
        _rng.shuffle(d)
        decks.append(d)

    # Verificar que no son todas idénticas
    all_equal = True
    for i in range(1, 5):
        if decks[i] != decks[0]:
            all_equal = False
            break
    assert not all_equal
