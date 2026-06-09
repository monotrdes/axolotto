import pytest
import json
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet, CurrencyType, TransactionLedger
from app.models.lobby_models import GameRoom, RoomRegistration, TreasuryVault, JackpotVault, JackpotWin
from app.models.items import ItemType, Rarity
from app.api.v1.endpoints.multiplayer import register_axolotito, RegisterRequest, recall_axolotito, settle_axolotito_escrow
from app.services.multiplayer_service import get_or_create_waiting_room, MultiplayerService

from tests.conftest import make_user, make_wallet, make_card_pool

def setup_escrow_entities(session: Session):
    # 1. Crear usuarios y wallets
    user_a = make_user(session, privy_did="user_a", wallet_address="0x111")
    user_b = make_user(session, privy_did="user_b", wallet_address="0x222")
    make_wallet(session, user_id="user_a", gemas_alga=1000.0)
    make_wallet(session, user_id="user_b", gemas_alga=1000.0)

    # 2. Crear Axolotitos
    axo_a = Axolotito(
        name="Axolotito A",
        user_id="user_a",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=60,
        stat_luck=0,
    )
    axo_b = Axolotito(
        name="Axolotito B",
        user_id="user_b",
        status="idle",
        energy_current=100,
        energy_max=100,
        stat_focus=60,
        stat_luck=0,
    )
    session.add(axo_a)
    session.add(axo_b)
    session.commit()

    # 3. Seed de cartas para las tablas
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]

    # 4. Crear tableros para user_a y user_b con las cartas seeded
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

def test_escrow_retained_on_registration(session):
    user_a, _, axo_a, _, boards_a, _ = setup_escrow_entities(session)
    wallet = session.exec(select(Wallet).where(Wallet.user_id == "user_a")).one()
    initial_balance = wallet.gemas_alga

    # Registrar el axolotito con presupuesto de 100.0 GAL
    req = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[boards_a[0].id],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    res = register_axolotito(req, session, verified_user_id="user_a")
    
    session.refresh(axo_a)
    session.refresh(wallet)

    # El escrow debe ser retenido del saldo del usuario y asignado al axolotito
    assert wallet.gemas_alga == initial_balance - 100.0
    assert axo_a.escrow_balance_gal == 100.0
    assert axo_a.status == "playing"

    # Verificar que existe la registración de la sala
    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    assert reg is not None
    assert json.loads(reg.boards_json) == [boards_a[0].id]

def test_recall_during_game_in_progress(session):
    user_a, _, axo_a, _, boards_a, _ = setup_escrow_entities(session)

    # Registrar el axolotito
    req = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[boards_a[0].id],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req, session, verified_user_id="user_a")
    session.refresh(axo_a)

    # Obtener la sala asignada y cambiar su estado a "in_progress"
    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    room = session.get(GameRoom, reg.room_id)
    room.status = "in_progress"
    session.add(room)
    session.commit()

    # Intentar retirar (recall) mientras la partida está en progreso
    # Debe encolarse (wants_to_stop = True) pero no retirarlo de inmediato (immediate = False)
    res = recall_axolotito(axolotito_id=axo_a.id, session=session, verified_user_id="user_a")
    assert res["immediate"] is False
    
    session.refresh(axo_a)
    assert axo_a.wants_to_stop is True
    assert axo_a.status == "playing"

    # Intentar liquidar (settle) mientras la partida está activa debe fallar con HTTP 400
    with pytest.raises(HTTPException) as exc:
        settle_axolotito_escrow(axolotito_id=axo_a.id, session=session, verified_user_id="user_a")
    assert exc.value.status_code == 400
    assert "no está listo para liquidación" in exc.value.detail

def test_cancel_room_refund(session):
    user_a, _, axo_a, _, boards_a, _ = setup_escrow_entities(session)
    wallet = session.exec(select(Wallet).where(Wallet.user_id == "user_a")).one()
    initial_balance = wallet.gemas_alga

    # Registrar
    req = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[boards_a[0].id],
        budget_gal=100.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req, session, verified_user_id="user_a")
    session.refresh(axo_a)

    # Simular cancelación: eliminar RoomRegistration y colocar estado waiting_settlement
    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    session.delete(reg)
    axo_a.status = "waiting_settlement"
    session.add(axo_a)
    session.commit()

    # Liquidar fondos del escrow
    res = settle_axolotito_escrow(axolotito_id=axo_a.id, session=session, verified_user_id="user_a")
    assert res["refunded_gal"] == 100.0

    session.refresh(axo_a)
    session.refresh(wallet)

    assert wallet.gemas_alga == initial_balance  # Reembolso total
    assert axo_a.escrow_balance_gal == 0.0
    assert axo_a.status == "sleeping"

def test_win_escrow_settlement(session):
    # Setup 2 jugadores (user_a con 3 tablas, user_b con 2 tablas) -> 5 tablas totales -> Elegible para Jackpot
    user_a, user_b, axo_a, axo_b, boards_a, boards_b = setup_escrow_entities(session)
    
    wallet_a = session.exec(select(Wallet).where(Wallet.user_id == "user_a")).one()
    wallet_b = session.exec(select(Wallet).where(Wallet.user_id == "user_b")).one()
    
    initial_balance_a = wallet_a.gemas_alga
    initial_balance_b = wallet_b.gemas_alga

    # Crear vaults de prueba
    treasury = TreasuryVault(balance=100.0)
    jackpot = JackpotVault(current_amount=2000.0, seed_amount=1000.0)
    session.add_all([treasury, jackpot])
    session.commit()

    # Registrar ambos
    req_a = RegisterRequest(
        axolotito_id=axo_a.id,
        room_type="rookie",
        boards=[b.id for b in boards_a],
        budget_gal=300.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req_a, session, verified_user_id="user_a")

    req_b = RegisterRequest(
        axolotito_id=axo_b.id,
        room_type="rookie",
        boards=[b.id for b in boards_b],
        budget_gal=200.0,
        loss_limit_pct=30.0,
        profit_limit_pct=50.0
    )
    register_axolotito(req_b, session, verified_user_id="user_b")

    # Obtener sala creada
    reg = session.exec(select(RoomRegistration).where(RoomRegistration.axolotito_id == axo_a.id)).first()
    room_id = reg.room_id

    # Establecer wants_to_stop = True para que salgan del loop tras la partida
    axo_a.wants_to_stop = True
    axo_b.wants_to_stop = True
    session.add_all([axo_a, axo_b])
    session.commit()

    # Simular la partida
    MultiplayerService.simulate_multiplayer_match(room_id)

    # Verificar que la sala está terminada
    room = session.get(GameRoom, room_id)
    assert room.status == "finished"

    session.refresh(axo_a)
    session.refresh(axo_b)

    # Ambos axolotitos deben haber salido del juego ya que la partida terminó y wants_to_stop se cumplió por defecto tras match, 
    # o porque sus fondos cambiaron y se les marcó para liquidación
    assert axo_a.status == "waiting_settlement"
    assert axo_b.status == "waiting_settlement"

    # Liquidar fondos del escrow de ambos
    settle_axolotito_escrow(axolotito_id=axo_a.id, session=session, verified_user_id="user_a")
    settle_axolotito_escrow(axolotito_id=axo_b.id, session=session, verified_user_id="user_b")

    session.refresh(wallet_a)
    session.refresh(wallet_b)
    session.refresh(axo_a)
    session.refresh(axo_b)

    # Verificar que el dinero en escrow regresó a las wallets de los usuarios (con ganancias o pérdidas)
    assert axo_a.escrow_balance_gal == 0.0
    assert axo_b.escrow_balance_gal == 0.0

    # La suma total de gemas de ambos usuarios + tesorería + jackpot debe conservarse
    # (Conservación de energía del ecosistema: total_gal inicial = total_gal final)
    total_initial = initial_balance_a + initial_balance_b + 100.0 + 2000.0
    
    session.refresh(treasury)
    session.refresh(jackpot)
    
    total_final = wallet_a.gemas_alga + wallet_b.gemas_alga + treasury.balance + jackpot.current_amount
    assert round(total_initial, 2) == round(total_final, 2)
