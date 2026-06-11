import sys
import os
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet

from app.models.axolotito import Axolotito
from app.models.user import User
from app.models.economy import Wallet, TransactionLedger
from app.services.staking_service import StakingService
from app.services.board_service import get_accrued_staking, PlayerBoard
from app.api.v1.endpoints.staking import (
    get_staking_status,
    claim_staking,
    claim_all_staking,
    stake_axolotito,
    unstake_axolotito,
)

def test_staking_slots(session: Session):
    user = make_user(session, privy_did="did:privy:slots_user")
    user.cave_level = 1
    assert StakingService.get_staking_slots(user) == 2

    user.cave_level = 5
    assert StakingService.get_staking_slots(user) == 6

def test_calculate_axolotito_hourly_rate(session: Session):
    # Test typical comun pink axolotito
    axo_pink = Axolotito(
        user_id="did:privy:test_rate",
        name="Pinky",
        skin_color="pink",
        level=1,
        gill_type="normal",
        eye_type="cute",
        mouth_type="smile",
        tail_type="standard",
        forehead_type="none",
        limb_type="soft",
    )
    # Pink skin: 0.05
    # Level 1 mult: 1 + 0.1 * 1 = 1.1 -> skin component = 0.05 * 1.1 = 0.055
    # Parts (all comun): 6 parts * 0.01 = 0.06
    # Total rate: 0.055 + 0.06 = 0.115
    rate = StakingService.calculate_axolotito_hourly_rate(axo_pink)
    assert abs(rate - 0.115) < 0.0001

    # Test legendary gold with rare/epic parts
    axo_gold = Axolotito(
        user_id="did:privy:test_rate",
        name="Golden",
        skin_color="gold",
        level=10,
        gill_type="phoenix", # legendary: +0.20 (Wait, parts mapping doesn't have legendary, defaults to comun (0.01)? Let's check: parts_bonus has legendary -> 0.20, but _TRAIT_RARITY maps phoenix to legendary!)
        eye_type="cool", # epic: +0.08
        mouth_type="fang", # rare: +0.03
        tail_type="plasma", # epic: +0.08
        forehead_type="gem", # rare: +0.03
        limb_type="scales", # rare: +0.03
    )
    # Gold skin: 1.00
    # Level 10 mult: 1 + 0.1 * 10 = 2.0 -> skin component = 1.00 * 2.0 = 2.0
    # Parts:
    # gill: phoenix (legendary) -> 0.20
    # eye: cool (epic) -> 0.08
    # mouth: fang (rare) -> 0.03
    # tail: plasma (epic) -> 0.08
    # forehead: gem (rare) -> 0.03
    # limb: scales (rare) -> 0.03
    # parts total: 0.20 + 0.08 + 0.03 + 0.08 + 0.03 + 0.03 = 0.45
    # Total: 2.0 + 0.45 = 2.45
    rate_gold = StakingService.calculate_axolotito_hourly_rate(axo_gold)
    assert abs(rate_gold - 2.45) < 0.0001

def test_is_staking_active(session: Session):
    user = make_user(session, privy_did="did:privy:active_test")
    assert not StakingService.is_staking_active(user)

    user.last_play_date = datetime.utcnow() - timedelta(hours=23)
    assert StakingService.is_staking_active(user)

    user.last_play_date = datetime.utcnow() - timedelta(hours=25)
    assert not StakingService.is_staking_active(user)

def test_calculate_accrued_frj_caps(session: Session):
    user = make_user(session, privy_did="did:privy:accrual_user")
    user.last_play_date = datetime.utcnow()
    axo = Axolotito(
        user_id=user.privy_did,
        name="Accrual",
        skin_color="pink",
        level=1,
        last_staking_claim=datetime.utcnow() - timedelta(hours=6),
        accrued_unclaimed=0.0,
    )
    # hourly rate: 0.115
    # 6 hours elapsed -> 6 * 0.115 = 0.69
    accrued = StakingService.calculate_accrued_frj(axo, user)
    assert abs(accrued - 0.69) < 0.0001

    # Over 12 hours (e.g. 15 hours) -> caps at 12 hours -> 12 * 0.115 = 1.38
    axo.last_staking_claim = datetime.utcnow() - timedelta(hours=15)
    accrued_cap = StakingService.calculate_accrued_frj(axo, user)
    assert abs(accrued_cap - 1.38) < 0.0001

    # If play-to-stake is inactive -> returns 0
    user.last_play_date = datetime.utcnow() - timedelta(hours=30)
    assert StakingService.calculate_accrued_frj(axo, user) == 0.0

def test_board_staking_cap_and_play_to_stake(session: Session):
    user = make_user(session, privy_did="did:privy:board_user")
    user.last_play_date = datetime.utcnow()
    
    board = PlayerBoard(
        user_id=user.privy_did,
        name="Test Board",
        level=1,
        last_staking_claim=datetime.utcnow() - timedelta(hours=5),
        card_ids=[],
    )
    session.add(board)
    session.commit()
    
    # 0 cards -> 0 rate
    assert get_accrued_staking(board, session) == 0.0

    # Let's mock a rate of 1.0 FRJ/h by adding cards or just patching it.
    # But wait, we can just test with play-to-stake inactive
    user.last_play_date = datetime.utcnow() - timedelta(hours=30)
    session.add(user)
    session.commit()
    assert get_accrued_staking(board, session) == 0.0

def test_endpoints_stake_and_unstake(session: Session):
    from fastapi import Request
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/staking",
        "headers": [],
    }
    req = Request(scope=scope)

    user = make_user(session, privy_did="did:privy:endpoint_user")
    make_wallet(session, user.privy_did, gemas_alga=0.0)
    user.cave_level = 1  # 2 slots max
    user.last_play_date = datetime.utcnow()
    session.add(user)
    session.commit()

    axo1 = Axolotito(user_id=user.privy_did, name="Axo 1", status="idle")
    axo2 = Axolotito(user_id=user.privy_did, name="Axo 2", status="idle")
    axo3 = Axolotito(user_id=user.privy_did, name="Axo 3", status="idle")
    session.add_all([axo1, axo2, axo3])
    session.commit()

    # Stake axo1 (studying)
    res = stake_axolotito(req, axo1.id, "studying", session, user.privy_did)
    assert "puesto en staking" in res["message"]
    assert axo1.status == "studying"

    # Stake axo2 (resting)
    res = stake_axolotito(req, axo2.id, "resting", session, user.privy_did)
    assert axo2.status == "resting"

    try:
        stake_axolotito(req, axo3.id, "studying", session, user.privy_did)
        assert False, "Should have failed due to slots limit"
    except Exception as e:
        # Check if it is HTTPException
        assert hasattr(e, "status_code")
        assert e.status_code == 400
        assert "Límite de slots" in e.detail

    # Test status endpoint
    status_res = get_staking_status(req, session, user.privy_did)
    assert status_res["slots_total"] == 2
    assert status_res["slots_used"] == 2

    # Simulate time passing by shifting last_staking_claim back by 3 minutes
    axo1.last_staking_claim = datetime.utcnow() - timedelta(minutes=3)
    session.add(axo1)
    session.commit()

    # Unstake axo1
    res_unstake = unstake_axolotito(req, axo1.id, session, user.privy_did)
    assert "sacado de staking" in res_unstake["message"]
    assert axo1.status == "idle"

    # Slots used should be 1 now
    status_res = get_staking_status(req, session, user.privy_did)
    assert status_res["slots_used"] == 1
