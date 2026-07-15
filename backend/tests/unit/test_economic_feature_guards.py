"""Fast fail-closed checks: guards must run before any DB dependency."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.legacy import claim_legacy_egg
from app.core.config import settings
from app.models.economy import CurrencyType
from app.services.admin_service import (
    PromoBatchCreate,
    adjust_player_balance,
    create_promo_batch,
    grant_player_vip,
    override_player_tutorial,
    run_simulation,
)
from app.services.daily_reward_service import DailyRewardService
from app.services.forge_service import forge_card, melt_card
from app.services.lunar_streak_service import claim as claim_lunar
from app.services.promo_service import redeem_promo_code
from app.services.shop_service import ShopService
from app.services.staking_service import StakingService
from app.services.tutorial_service import TutorialService


def _assert_disabled(call, feature: str) -> None:
    with pytest.raises(HTTPException) as exc:
        call()
    assert exc.value.status_code == 503
    assert exc.value.detail["feature"] == feature


def test_token_reward_services_fail_before_db(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_PASSIVE_TOKEN_REWARDS", False)
    user = SimpleNamespace(privy_did="did:privy:guard")

    _assert_disabled(lambda: claim_lunar(None, user), "gameplay_token_rewards")
    _assert_disabled(
        lambda: DailyRewardService().claim_daily_reward(None, user),
        "gameplay_token_rewards",
    )
    _assert_disabled(
        lambda: StakingService.claim_staking_reward(None, 1, user),
        "passive_token_rewards",
    )


def test_tutorial_preflight_fails_before_incubation_mutation(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)
    _assert_disabled(
        lambda: TutorialService.start_tutorial(None, "did:privy:guard", object()),
        "gameplay_token_rewards",
    )


def test_asset_and_shop_services_fail_before_db(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_LEGACY_ASSET_CLAIMS", False)
    monkeypatch.setattr(settings, "ENABLE_FIXED_ITEM_SHOP", False)
    monkeypatch.setattr(settings, "ENABLE_CARD_CRAFTING", False)

    _assert_disabled(
        lambda: claim_legacy_egg("u", session=None, verified_user_id="u"),
        "legacy_asset_claims",
    )
    _assert_disabled(
        lambda: ShopService.buy_item(None, "u", 1, CurrencyType.FRIJOLITO),
        "fixed_item_shop",
    )
    _assert_disabled(lambda: melt_card(None, "u", 1), "card_crafting")
    _assert_disabled(lambda: forge_card(None, "u", 1), "card_crafting")


def test_melt_also_requires_random_reward_flag(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_CARD_CRAFTING", True)
    monkeypatch.setattr(settings, "ENABLE_PURCHASED_RANDOM_REWARDS", False)
    _assert_disabled(
        lambda: melt_card(None, "u", 1),
        "purchased_random_rewards",
    )


def test_admin_and_promo_services_fail_before_db(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_ADMIN_TOKEN_MINTS", False)
    monkeypatch.setattr(settings, "ENABLE_ADMIN_BALANCE_ADJUSTMENTS", False)
    monkeypatch.setattr(settings, "ENABLE_VIP_SALES", False)
    monkeypatch.setattr(settings, "ENABLE_PROMOTIONAL_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)

    _assert_disabled(
        lambda: adjust_player_balance(None, "u", "frj", 1, "test"),
        "admin_token_mints",
    )
    _assert_disabled(
        lambda: adjust_player_balance(None, "u", "frj", -1, "test"),
        "admin_balance_adjustments",
    )
    _assert_disabled(
        lambda: grant_player_vip(None, "u", "coral", 30),
        "vip_sales",
    )
    _assert_disabled(
        lambda: override_player_tutorial(None, "u", "skip"),
        "gameplay_token_rewards",
    )
    _assert_disabled(
        lambda: redeem_promo_code(None, "u", "CODE"),
        "promotional_token_rewards",
    )
    _assert_disabled(
        lambda: create_promo_batch(
            None,
            PromoBatchCreate(
                name="guarded",
                quantity=1,
                axf_amount=1,
                frj_amount=1,
            ),
        ),
        "promotional_token_rewards",
    )


def test_admin_simulation_requires_legacy_local(monkeypatch):
    monkeypatch.setattr(settings, "PRODUCT_MODE", "non_gambling")
    monkeypatch.setattr(settings, "BLOCKCHAIN_MODE", "local")
    _assert_disabled(lambda: run_simulation(None, None), "admin_simulation")
