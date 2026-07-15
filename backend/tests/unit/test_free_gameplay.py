"""Regression tests for CPU play without any economic consideration or prize."""

from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlmodel import select

from app.core.config import settings
from app.api.v1.endpoints.cave_expansion import (
    accelerate_expansion,
    start_expansion,
)
from app.api.v1.endpoints.tutorial import start_tutorial
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import ChainOutbox, TransactionLedger, Wallet
from app.models.items import ItemCatalog, ItemType, WebitoIncubation
from app.models.user import User
from app.services.game_service import GameService
from app.services.tutorial_service import TutorialService


def _play_args(session=None, user_id="did:privy:free_play", **overrides):
    values = {
        "axolotito_id": 1,
        "room_name": "rookie",
        "multiplier": 1,
        "bot_enabled": False,
        "bot_budget_gal": 0,
        "bot_loss_limit_pct": 0,
        "bot_profit_limit_pct": 0,
        "session": session,
        "verified_user_id": user_id,
    }
    values.update(overrides)
    return values


def test_cpu_play_is_rejected_when_all_play_modes_are_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", False)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)

    with pytest.raises(HTTPException) as exc:
        GameService.play_match(**_play_args())

    assert exc.value.status_code == 503
    assert exc.value.detail["feature"] == "cpu_gameplay"


def test_fixed_gameplay_spending_routes_fail_before_database_access(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FIXED_GAMEPLAY_SPENDING", False)

    guarded_calls = [
        lambda: GameService.feed_axolotito(
            axo_id=1,
            food_type="pellet",
            session=None,
            verified_user_id="did:privy:test",
        ),
        lambda: start_expansion(
            session=None,
            verified_user_id="did:privy:test",
        ),
        lambda: accelerate_expansion(
            session=None,
            verified_user_id="did:privy:test",
        ),
    ]

    for guarded_call in guarded_calls:
        with pytest.raises(HTTPException) as exc:
            guarded_call()
        assert exc.value.status_code == 503
        assert exc.value.detail["feature"] == "fixed_gameplay_spending"


@pytest.mark.parametrize(
    "override",
    [
        {"multiplier": 2},
        {"bot_enabled": True},
        {"bot_budget_gal": 1},
        {"bot_loss_limit_pct": 1},
        {"bot_profit_limit_pct": 1},
    ],
)
def test_free_cpu_play_rejects_economic_parameters(monkeypatch, override):
    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)

    with pytest.raises(HTTPException) as exc:
        GameService.play_match(**_play_args(**override))

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "FREE_PLAY_ECONOMIC_PARAMETERS_FORBIDDEN"


def test_free_cpu_play_progresses_without_wallet_ledger_or_chain_value(
    session, monkeypatch
):
    user_id = "did:privy:free_play"
    user = User(
        privy_did=user_id,
        wallet_address=None,
        tutorial_completed=True,
    )
    wallet = Wallet(user_id=user_id, frijolitos=0)
    session.add(user)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)

    cards = []
    for number in range(1, 55):
        card = ItemCatalog(
            name=f"Carta {number}",
            item_type=ItemType.CARD,
            item_metadata={"numero_loteria": number},
        )
        session.add(card)
        cards.append(card)
    session.commit()
    for card in cards:
        session.refresh(card)

    board = PlayerBoard(
        user_id=user_id,
        name="Tabla gratuita",
        card_ids=[card.id for card in cards[:16]],
        card_first_editions=[False] * 16,
        is_tutorial=True,
    )
    session.add(board)
    session.commit()
    session.refresh(board)

    axolotito = Axolotito(
        user_id=user_id,
        name="Axo gratuito",
        assigned_board_id=board.id,
        energy_current=100,
        is_tutorial=True,
        cpu_win_streak=3,
    )
    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_BOARD_ASSET_MUTATIONS", False)
    monkeypatch.setattr(settings, "ENABLE_HATCHING", False)

    result = GameService.play_match(
        **_play_args(
            session=session,
            user_id=user_id,
            axolotito_id=axolotito.id,
        )
    )

    session.refresh(wallet)
    session.refresh(board)
    session.refresh(axolotito)

    assert result["play_mode"] == "free"
    assert result["economic_reward"] is False
    assert result["entry_fee_gal"] == 0
    assert result["prize_gal"] == 0
    assert wallet.frijolitos == 0
    assert board.games_played == 1
    assert axolotito.energy_current == 90
    assert axolotito.cpu_win_streak == 3
    assert result["win_streak_after"] == 0
    assert session.exec(
        select(TransactionLedger).where(TransactionLedger.user_id == user_id)
    ).all() == []
    assert session.exec(
        select(ChainOutbox).where(ChainOutbox.user_id == user_id)
    ).all() == []
    assert session.exec(select(Wallet).where(Wallet.user_id == user_id)).one().frijolitos == 0


def test_free_onboarding_creates_only_offchain_practice_starters(
    session, monkeypatch
):
    user_id = "did:privy:free_onboarding"
    user = User(privy_did=user_id, wallet_address=None, tutorial_completed=False)
    session.add(user)
    for number in range(1, 55):
        session.add(ItemCatalog(
            name=f"Tutorial Carta {number}",
            item_type=ItemType.CARD,
            item_metadata={"numero_loteria": number},
        ))
    session.commit()

    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_HATCHING", False)
    monkeypatch.setattr(settings, "ENABLE_BOARD_ASSET_MUTATIONS", False)

    started = start_tutorial(session=session, verified_user_id=user_id)
    incubation = session.get(WebitoIncubation, started["id"])
    assert incubation is not None

    for _ in range(3):
        TutorialService.advance_phase(
            session=session,
            user_id=user_id,
            incubation=incubation,
            won=True,
        )
        session.refresh(incubation)
    assert incubation.tutorial_phase == 4

    result = TutorialService.complete_tutorial(
        session=session,
        user_id=user_id,
        incubation=incubation,
    )

    session.refresh(user)
    starter = session.get(Axolotito, result["axolotito_id"])
    board = session.get(PlayerBoard, starter.assigned_board_id)

    assert user.tutorial_completed is True
    assert result["bonus"] == {"type": "none", "amount": 0, "currency": None}
    assert result["axolotito"]["asset_scope"] == "offchain_non_transferable_practice"
    assert starter.blockchain_token_id is None
    assert starter.is_tutorial is True
    assert board.is_tutorial is True
    assert len(board.card_ids) == 16
    assert session.exec(select(Wallet).where(Wallet.user_id == user_id)).first() is None
    assert session.exec(
        select(TransactionLedger).where(TransactionLedger.user_id == user_id)
    ).all() == []
    assert session.exec(
        select(ChainOutbox).where(ChainOutbox.user_id == user_id)
    ).all() == []


def test_free_play_never_mutates_tokenized_assets(session, monkeypatch):
    user_id = "did:privy:tokenized_free_reject"
    session.add(User(privy_did=user_id, tutorial_completed=True))
    cards = []
    for number in range(1, 17):
        card = ItemCatalog(
            name=f"Tokenized Carta {number}",
            item_type=ItemType.CARD,
            item_metadata={"numero_loteria": number},
        )
        session.add(card)
        cards.append(card)
    session.commit()
    for card in cards:
        session.refresh(card)

    board = PlayerBoard(
        user_id=user_id,
        card_ids=[card.id for card in cards],
        card_first_editions=[False] * 16,
        blockchain_token_id=101,
    )
    session.add(board)
    session.commit()
    session.refresh(board)
    axolotito = Axolotito(
        user_id=user_id,
        assigned_board_id=board.id,
        blockchain_token_id=202,
        energy_current=100,
    )
    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)

    with pytest.raises(HTTPException) as exc:
        GameService.play_match(
            **_play_args(
                session=session,
                user_id=user_id,
                axolotito_id=axolotito.id,
            )
        )

    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "FREE_PLAY_REQUIRES_PRACTICE_ASSETS"
    session.refresh(axolotito)
    session.refresh(board)
    assert axolotito.energy_current == 100
    assert board.games_played == 0


def test_free_tutorial_does_not_adopt_a_real_incubation(session, monkeypatch):
    user_id = "did:privy:real_egg_isolated"
    session.add(User(privy_did=user_id, tutorial_completed=False))
    egg = ItemCatalog(name="Huevo real", item_type=ItemType.EGG)
    session.add(egg)
    for number in range(1, 55):
        session.add(ItemCatalog(
            name=f"Isolation Carta {number}",
            item_type=ItemType.CARD,
            item_metadata={"numero_loteria": number},
        ))
    session.commit()
    session.refresh(egg)
    real_incubation = WebitoIncubation(
        user_id=user_id,
        item_id=egg.id,
        fecha_eclosion_estimada=datetime.utcnow(),
    )
    session.add(real_incubation)
    session.commit()
    session.refresh(real_incubation)

    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_HATCHING", False)
    monkeypatch.setattr(settings, "ENABLE_BOARD_ASSET_MUTATIONS", False)

    started = start_tutorial(session=session, verified_user_id=user_id)
    practice_incubation = session.get(WebitoIncubation, started["id"])

    assert practice_incubation.item_id == 0
    assert practice_incubation.id != real_incubation.id
    assert session.get(WebitoIncubation, real_incubation.id) is not None


def test_free_completion_does_not_reuse_a_tokenized_tutorial_axolotito(
    session, monkeypatch
):
    user_id = "did:privy:legacy_tutorial_asset"
    user = User(privy_did=user_id, tutorial_completed=False)
    session.add(user)
    cards = []
    for number in range(1, 17):
        card = ItemCatalog(
            name=f"Legacy Isolation Carta {number}",
            item_type=ItemType.CARD,
            item_metadata={"numero_loteria": number},
        )
        session.add(card)
        cards.append(card)
    session.commit()
    for card in cards:
        session.refresh(card)

    legacy_board = PlayerBoard(
        user_id=user_id,
        card_ids=[card.id for card in cards],
        card_first_editions=[False] * 16,
        is_tutorial=True,
        blockchain_token_id=301,
    )
    session.add(legacy_board)
    session.commit()
    session.refresh(legacy_board)
    legacy_axolotito = Axolotito(
        user_id=user_id,
        assigned_board_id=legacy_board.id,
        is_tutorial=True,
        blockchain_token_id=302,
    )
    session.add(legacy_axolotito)
    incubation = WebitoIncubation(
        user_id=user_id,
        item_id=0,
        fecha_eclosion_estimada=datetime.utcnow(),
        tutorial_phase=4,
        tutorial_karma="lucky",
        tutorial_board_card_ids=[card.id for card in cards],
    )
    session.add(incubation)
    session.commit()
    session.refresh(legacy_axolotito)
    session.refresh(incubation)

    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PAID_GAMEPLAY", False)
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_HATCHING", False)
    monkeypatch.setattr(settings, "ENABLE_BOARD_ASSET_MUTATIONS", False)

    result = TutorialService.complete_tutorial(
        session=session,
        user_id=user_id,
        incubation=incubation,
    )
    practice = session.get(Axolotito, result["axolotito_id"])
    practice_board = session.get(PlayerBoard, practice.assigned_board_id)

    assert practice.id != legacy_axolotito.id
    assert practice.blockchain_token_id is None
    assert practice_board.blockchain_token_id is None
    assert session.get(Axolotito, legacy_axolotito.id).blockchain_token_id == 302
