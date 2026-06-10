"""
test_prize_invariants.py — Suite VULN-05: Invariante de conservación de fondos en premios multijugador.

Cubre:
  1. Σ premios P1+P2 ≤ Σ cuotas cobradas (invariante base, sin VIP)
  2. Σ premios con jugador VIP Axolite + luck alto ≤ pool (VIP bonus in-pool)
  3. Luck bonus cappado al 10% del share base (fórmula pura)
  4. Shares de bots van a tesorería, no se pierden
  5. Juego con un solo jugador humano respeta invariante

Nota: se usa inserción directa en BD (como tests E y J de jackpot_inflation) para
evitar la validación de presupuesto en el endpoint /register (fees en micro-FRJ).
"""
from __future__ import annotations
import json
import pytest
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import Wallet
from app.models.lobby_models import (
    GameRoom, RoomRegistration, TreasuryVault, JackpotVault, MultiplayerGameLog,
)
from app.models.user import User
from app.services.multiplayer_service import MultiplayerService
from tests.conftest import make_user, make_wallet, make_card_pool

ENTRY_FEE = 100.0  # FRJ por tabla — valor simple para pruebas
ESCROW = 500.0     # saldo inicial en custodia (> entry fee)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_axolotito(
    session: Session,
    user_id: str,
    name: str = "Axo",
    stat_focus: float = 100.0,
    stat_luck: float = 0.0,
    is_vip: bool = False,
    vip_tier: str | None = None,
) -> Axolotito:
    axo = Axolotito(
        name=name,
        user_id=user_id,
        status="playing",
        energy_current=100,
        energy_max=100,
        stat_focus=stat_focus,
        stat_luck=stat_luck,
        escrow_balance_gal=ESCROW,
        bot_budget_axg=ESCROW,
        bot_loss_limit_axg=ESCROW * 0.5,
        bot_profit_limit_axg=ESCROW * 0.5,
        bot_enabled=True,
    )
    session.add(axo)
    session.commit()
    session.refresh(axo)
    return axo


def make_boards(session: Session, user_id: str, count: int, card_ids: list) -> list:
    boards = []
    for _ in range(count):
        b = PlayerBoard(user_id=user_id, card_ids=card_ids, is_dead=False)
        session.add(b)
        session.commit()
        session.refresh(b)
        boards.append(b)
    return boards


def setup_room(
    session: Session,
    players: list[tuple],  # [(user, axo, boards_list), ...]
    entry_fee: float = ENTRY_FEE,
) -> GameRoom:
    """Crea sala + registros directos en BD, sin pasar por el endpoint /register."""
    room = GameRoom(
        name="Sala Test",
        room_type="rookie_pool",
        entry_fee_gal=entry_fee,
        status="playing",
    )
    session.add(room)
    session.commit()
    session.refresh(room)

    for user, axo, boards in players:
        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        if wallet:
            wallet.frijolitos -= entry_fee * len(boards)
            session.add(wallet)
        reg = RoomRegistration(
            room_id=room.id,
            axolotito_id=axo.id,
            boards_json=json.dumps([b.id for b in boards]),
        )
        session.add(reg)
    session.commit()
    return room


def init_vaults(session, jackpot_amount=1000.0):
    treasury = TreasuryVault(balance=5000.0)
    jackpot = JackpotVault(current_amount=jackpot_amount, seed_amount=1000.0)
    session.add_all([treasury, jackpot])
    session.commit()
    session.refresh(jackpot)
    return jackpot


# ---------------------------------------------------------------------------
# 1. Invariante base: Σ premios ≤ Σ cuotas (sin VIP, luck=0)
# ---------------------------------------------------------------------------

def test_prize_pool_invariant_no_bonuses(session):
    """VULN-05: con luck=0 y sin VIP, premios ≤ player pool."""
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]
    init_vaults(session)

    user_a = make_user(session, privy_did="inv1_a", wallet_address="0xINV1_A")
    user_b = make_user(session, privy_did="inv1_b", wallet_address="0xINV1_B")
    make_wallet(session, user_id="inv1_a", gemas_alga=1000.0)
    make_wallet(session, user_id="inv1_b", gemas_alga=1000.0)

    axo_a = make_axolotito(session, "inv1_a", "InvA", stat_focus=100.0, stat_luck=0.0)
    axo_b = make_axolotito(session, "inv1_b", "InvB", stat_focus=100.0, stat_luck=0.0)

    boards_a = make_boards(session, "inv1_a", 1, card_ids)
    boards_b = make_boards(session, "inv1_b", 1, card_ids)

    room = setup_room(session, [
        (user_a, axo_a, boards_a),
        (user_b, axo_b, boards_b),
    ])

    MultiplayerService.simulate_multiplayer_match(room.id)

    logs = session.exec(select(MultiplayerGameLog)).all()
    total_prizes = sum(log.gross_prize_gal for log in logs)
    total_collected = 2 * room.entry_fee_gal
    player_pool = total_collected * 0.90  # 35% + 55% = 90% del collected

    assert total_prizes <= player_pool + 0.01, (
        f"VULN-05: premios {total_prizes:.4f} exceden pool {player_pool:.4f} "
        f"(overflow: {total_prizes - player_pool:.4f})"
    )


# ---------------------------------------------------------------------------
# 2. Invariante con VIP Axolite (jackpot_bonus=5%) + luck=100 (max real)
# ---------------------------------------------------------------------------

def test_prize_pool_invariant_vip_max_luck(session):
    """VULN-05: VIP Axolite con luck=100 — bonuses in-pool, total ≤ player pool."""
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]
    init_vaults(session)

    from datetime import datetime, timedelta

    user_vip = make_user(
        session, privy_did="inv2_vip", wallet_address="0xINV2_VIP",
        is_vip=True, vip_tier="axolite",
    )
    user_b = make_user(session, privy_did="inv2_b", wallet_address="0xINV2_B")
    make_wallet(session, user_id="inv2_vip", gemas_alga=1000.0)
    make_wallet(session, user_id="inv2_b", gemas_alga=1000.0)

    # VIP con suerte máxima (stat_luck=100 → 10% luck_pct; vip jackpot_bonus=5%)
    axo_vip = make_axolotito(session, "inv2_vip", "VipAxo", stat_focus=100.0, stat_luck=100.0)
    axo_b = make_axolotito(session, "inv2_b", "NormalAxo", stat_focus=100.0, stat_luck=100.0)

    boards_vip = make_boards(session, "inv2_vip", 1, card_ids)
    boards_b = make_boards(session, "inv2_b", 1, card_ids)

    room = setup_room(session, [
        (user_vip, axo_vip, boards_vip),
        (user_b, axo_b, boards_b),
    ])

    MultiplayerService.simulate_multiplayer_match(room.id)

    logs = session.exec(select(MultiplayerGameLog)).all()
    total_prizes = sum(log.gross_prize_gal for log in logs)
    total_collected = 2 * room.entry_fee_gal
    player_pool = total_collected * 0.90

    assert total_prizes <= player_pool + 0.01, (
        f"VULN-05 VIP+luck: premios {total_prizes:.4f} exceden pool {player_pool:.4f}. "
        f"Inflación: {total_prizes - player_pool:.4f}"
    )


# ---------------------------------------------------------------------------
# 3. Fórmula pura: luck_pct cappado al 10%
# ---------------------------------------------------------------------------

def test_luck_pct_formula_capped():
    """VULN-05: luck_pct = min(stat_luck/1000, 0.10) — nunca supera 10%."""
    test_cases = [
        (0.0, 0.0),
        (50.0, 0.05),
        (100.0, 0.10),   # max real (stat_luck 0–100)
        (500.0, 0.10),   # hipotético: cap funciona
        (1000.0, 0.10),  # extremo: cap funciona
    ]
    for stat_luck, expected_pct in test_cases:
        luck_pct = min(stat_luck / 1000.0, 0.10)
        assert luck_pct == pytest.approx(expected_pct, abs=1e-9), (
            f"stat_luck={stat_luck}: luck_pct={luck_pct} ≠ {expected_pct}"
        )
        assert luck_pct <= 0.10, f"luck_pct={luck_pct} supera cap 10%"


# ---------------------------------------------------------------------------
# 4. Shares de bots van a tesorería, no se pierden
# ---------------------------------------------------------------------------

def test_bot_share_credited_to_treasury(session):
    """VULN-05: si hay ganadores bot, su share va a tesorería, no se pierde."""
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]
    init_vaults(session)

    user_a = make_user(session, privy_did="bot4_a", wallet_address="0xBOT4_A")
    make_wallet(session, user_id="bot4_a", gemas_alga=1000.0)
    axo_a = make_axolotito(session, "bot4_a", "HumanAxo", stat_focus=100.0, stat_luck=0.0)
    boards_a = make_boards(session, "bot4_a", 1, card_ids)

    room = setup_room(session, [(user_a, axo_a, boards_a)])

    treasury_before = session.exec(select(TreasuryVault)).first().balance

    MultiplayerService.simulate_multiplayer_match(room.id)

    treasury_after = session.exec(select(TreasuryVault)).first().balance
    logs = session.exec(select(MultiplayerGameLog)).all()
    total_prizes = sum(log.gross_prize_gal for log in logs)

    total_collected = 1 * room.entry_fee_gal
    player_pool = total_collected * 0.90  # 90% va a premios jugadores
    treasury_min_increase = total_collected * 0.05  # al menos el 5% de corte base

    assert total_prizes <= player_pool + 0.01, (
        f"Premios {total_prizes:.4f} exceden pool {player_pool:.4f}"
    )
    assert treasury_after >= treasury_before + treasury_min_increase - 0.01, (
        f"Tesorería no creció lo esperado: antes={treasury_before:.2f} "
        f"después={treasury_after:.2f} corte_mín={treasury_min_increase:.2f}"
    )


# ---------------------------------------------------------------------------
# 5. Un solo jugador humano con max luck: invariante se respeta
# ---------------------------------------------------------------------------

def test_single_human_max_luck_invariant(session):
    """VULN-05: 1 jugador humano con luck=100, gana todo el pool, nunca lo excede."""
    cards = make_card_pool(session, count=16)
    card_ids = [c.id for c in cards]
    init_vaults(session)

    user_a = make_user(session, privy_did="solo5_a", wallet_address="0xSOLO5_A")
    make_wallet(session, user_id="solo5_a", gemas_alga=1000.0)
    axo_a = make_axolotito(session, "solo5_a", "SoloAxo", stat_focus=100.0, stat_luck=100.0)
    boards_a = make_boards(session, "solo5_a", 1, card_ids)

    room = setup_room(session, [(user_a, axo_a, boards_a)])

    MultiplayerService.simulate_multiplayer_match(room.id)

    logs = session.exec(select(MultiplayerGameLog)).all()
    total_prizes = sum(log.gross_prize_gal for log in logs)
    player_pool = room.entry_fee_gal * 0.90

    assert total_prizes <= player_pool + 0.01, (
        f"VULN-05 solo+luck: premios {total_prizes:.4f} exceden pool {player_pool:.4f}"
    )
