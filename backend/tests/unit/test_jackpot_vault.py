import pytest
import json
from datetime import datetime
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet
from app.models.lobby_models import GameRoom, RoomRegistration, TreasuryVault, JackpotVault, JackpotWin
from app.api.v1.endpoints.multiplayer import register_axolotito, RegisterRequest
from app.services.multiplayer_service import MultiplayerService

from tests.conftest import make_user, make_wallet, make_card_pool

def setup_jackpot_entities(session: Session):
    # Crear usuarios
    user_a = make_user(session, privy_did="user_a", wallet_address="0x111")
    user_b = make_user(session, privy_did="user_b", wallet_address="0x222")
    make_wallet(session, user_id="user_a", gemas_alga=1000.0)
    make_wallet(session, user_id="user_b", gemas_alga=1000.0)

    # Crear Axolotitos
    axo_a = Axolotito(
        name="Axo A",
        user_id="user_a",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=100, # Max focus para que no falle marcas
        stat_luck=0,
    )
    axo_b = Axolotito(
        name="Axo B",
        user_id="user_b",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=100,
        stat_luck=0,
    )
    session.add(axo_a)
    session.add(axo_b)
    session.commit()

    # Crear cartas y tableros
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]

    boards_a = []
    for i in range(3):
        b = PlayerBoard(user_id="user_a", card_ids=card_ids, is_dead=False)
        session.add(b)
        session.commit()
        boards_a.append(b)

    boards_b = []
    for i in range(2):
        b = PlayerBoard(user_id="user_b", card_ids=card_ids, is_dead=False)
        session.add(b)
        session.commit()
        boards_b.append(b)

    return user_a, user_b, axo_a, axo_b, boards_a, boards_b

def test_jackpot_accumulation(session):
    # Setup: 2 users, but let's register only 3 boards total (not jackpot eligible, so it won't be won)
    user_a, user_b, axo_a, axo_b, boards_a, boards_b = setup_jackpot_entities(session)

    # Inicializar vaults
    treasury = TreasuryVault(balance=100.0)
    jackpot = JackpotVault(current_amount=2000.0, seed_amount=1000.0)
    session.add_all([treasury, jackpot])
    session.commit()

    # Registrar axo_a con 2 tablas y axo_b con 1 tabla -> 3 tablas totales
    req_a = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[boards_a[0].id, boards_a[1].id],
        budget_gal=300.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req_a, session, verified_user_id="user_a")

    req_b = RegisterRequest(
        axolotito_id=axo_b.id,
        room_type="rookie",
        boards=[boards_b[0].id],
        budget_gal=200.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req_b, session, verified_user_id="user_b")

    # Conseguir sala
    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    room_id = reg.room_id
    room = session.get(GameRoom, room_id)

    # Calcular comisión teórica del jackpot (5% del total recaudado)
    total_entry_fee = 3 * room.entry_fee_gal # 3 tablas
    expected_jackpot_fee = total_entry_fee * 0.05

    # Simular partida
    MultiplayerService.simulate_multiplayer_match(room_id)

    # Comprobar que el jackpot se incrementó exactamente por la comisión y no se reinició
    session.refresh(jackpot)
    assert jackpot.current_amount == 2000.0 + expected_jackpot_fee

def test_jackpot_no_reset_between_matches(session):
    # Verificar que el jackpot acumula consecutivamente a lo largo de varias partidas
    user_a, user_b, axo_a, axo_b, boards_a, boards_b = setup_jackpot_entities(session)

    # Inicializar vaults
    treasury = TreasuryVault(balance=100.0)
    jackpot = JackpotVault(current_amount=2000.0, seed_amount=1000.0)
    session.add_all([treasury, jackpot])
    session.commit()

    # Primera partida (2 tablas de user_a)
    req1 = RegisterRequest(
        axolotito_id=axo_a.id, room_type="rookie", boards=[boards_a[0].id, boards_a[1].id],
        budget_gal=200.0, loss_limit_pct=30.0, profit_limit_pct=50.0
    )
    register_axolotito(req1, session, verified_user_id="user_a")
    
    session.refresh(axo_a)
    axo_a.wants_to_stop = True
    session.add(axo_a)
    session.commit()

    reg1 = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    room1_id = reg1.room_id
    room1 = session.get(GameRoom, room1_id)
    MultiplayerService.simulate_multiplayer_match(room1_id)

    session.refresh(jackpot)
    amount_after_match1 = jackpot.current_amount
    expected_fee1 = (2 * room1.entry_fee_gal) * 0.05
    assert amount_after_match1 == 2000.0 + expected_fee1

    # Segunda partida (1 tabla de user_b)
    # Debemos resetear el estado de axo_a/b para poder registrar de nuevo (o crear otro axolotito)
    axo_b.status = "idle"
    session.add(axo_b)
    session.commit()
    req2 = RegisterRequest(
        axolotito_id=axo_b.id, room_type="rookie", boards=[boards_b[0].id],
        budget_gal=200.0, loss_limit_pct=30.0, profit_limit_pct=50.0
    )
    register_axolotito(req2, session, verified_user_id="user_b")
    reg2 = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_b.id)).first()
    room2_id = reg2.room_id
    room2 = session.get(GameRoom, room2_id)
    MultiplayerService.simulate_multiplayer_match(room2_id)

    session.refresh(jackpot)
    expected_fee2 = (1 * room2.entry_fee_gal) * 0.05
    assert jackpot.current_amount == amount_after_match1 + expected_fee2

def test_jackpot_payout_distribution(session):
    # Para probar el pago del jackpot, simulamos una partida elegible para jackpot
    # (5 tablas totales de humanos de 2 usuarios distintos)
    user_a, user_b, axo_a, axo_b, boards_a, boards_b = setup_jackpot_entities(session)

    # Inicializar vaults
    treasury = TreasuryVault(balance=100.0)
    jackpot = JackpotVault(current_amount=2000.0, seed_amount=1000.0)
    session.add_all([treasury, jackpot])
    session.commit()

    # Registrar 3 tablas de user_a y 2 tablas de user_b
    req_a = RegisterRequest(
        axolotito_id=axo_a.id, room_type="rookie", boards=[b.id for b in boards_a],
        budget_gal=300.0, loss_limit_pct=30.0, profit_limit_pct=50.0
    )
    register_axolotito(req_a, session, verified_user_id="user_a")

    req_b = RegisterRequest(
        axolotito_id=axo_b.id, room_type="rookie", boards=[b.id for b in boards_b],
        budget_gal=200.0, loss_limit_pct=30.0, profit_limit_pct=50.0
    )
    register_axolotito(req_b, session, verified_user_id="user_b")

    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    room_id = reg.room_id

    # Forzar ganadores de jackpot manipulando el random.random() de turnos de jackpot (4 a 6)
    # o simplemente mockear/parchear el generador aleatorio para que el primer premio (línea) ocurra en turno 4, 5 o 6.
    # En simulate_multiplayer_match, la mezcla de cartas decide el orden.
    # Para forzar un jackpot de manera deterministic, podemos monkeypatch _rng en multiplayer_service.py
    import random
    from unittest.mock import MagicMock
    
    # Creamos un mazo donde las primeras 4 cartas cantadas completen exactamente una línea en todos los tableros.
    # Nuestras tablas tienen card_ids = [c.id for c in cards]. Todas tienen la misma lista.
    # Si la lista es de 16 cartas, cantar las primeras 4 cartas completará la primera fila (0, 1, 2, 3) 
    # de todos los tableros!
    cards_in_db = session.exec(select(PlayerBoard).limit(1)).first().card_ids
    # Poner las primeras 4 cartas al inicio del mazo
    mocked_deck = cards_in_db.copy()
    
    # Parchear _rng.shuffle para que mantenga nuestro mazo predecible
    def mock_shuffle(d):
        d.clear()
        d.extend(mocked_deck)
    
    # Parchear _rng.random para evitar fallos de focus
    def mock_random():
        return 0.99
    
    import app.services.multiplayer_service
    original_shuffle = app.services.multiplayer_service._rng.shuffle
    original_random = app.services.multiplayer_service._rng.random
    
    app.services.multiplayer_service._rng.shuffle = mock_shuffle
    app.services.multiplayer_service._rng.random = mock_random
    
    try:
        MultiplayerService.simulate_multiplayer_match(room_id)
    finally:
        app.services.multiplayer_service._rng.shuffle = original_shuffle
        app.services.multiplayer_service._rng.random = original_random

    # Al completarse en el turno 4 (las primeras 4 cartas del mazo completan la fila), 
    # se cumple 4 <= turns <= 6 y jackpot_eligible (5 tablas y 2 users).
    # Por lo tanto, el jackpot debió haberse ganado!
    # El monto total acumulado del jackpot antes de ganar era 2000.0 + 5% fees = 2000 + (5 * 10) * 0.05 = 2002.50 GAL.
    # El payout es el 90% = 1802.25 GAL.
    # Dado que ambos usuarios completaron la línea en el mismo turno, ambos son ganadores.
    # El premio se divide en 2 partes: 901.125 GAL cada uno.
    session.refresh(jackpot)
    
    # Verificar que el record de ganancia de jackpot fue insertado
    wins = session.exec(select(JackpotWin)).all()
    assert len(wins) == 5
    
    # El jackpot debe haber sido reseteado al pool restante del 10% (aprox 200 GAL)
    # y rellenado a 1000.0 GAL usando fondos de la tesorería (si hay suficiente tesorería)
    # o mantener el saldo correspondiente
    assert jackpot.current_amount >= 200.25
    assert jackpot.last_winner_axo_id is not None
