"""Product-policy regression tests for the non-gambling baseline."""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import Settings
from app.core.config import settings
from app.core.product_policy import public_product_policy, require_feature


BASE_ENV = {
    "DATABASE_URL": "sqlite://",
    "TREASURY_PRIVATE_KEY": "0x" + "11" * 32,
}

SAFE_POLICY = {
    "PRODUCT_MODE": "non_gambling",
    "ALLOW_DEV_PAYMENTS": False,
    "ENABLE_FIAT_PAYMENTS": False,
    "ENABLE_CRYPTO_CHECKOUT": False,
    "ENABLE_PLAYER_MARKETPLACE": False,
    "ENABLE_CREATOR_PAYOUTS": False,
    "ENABLE_VIP_SALES": False,
    "ENABLE_PAID_GAMEPLAY": False,
    "ENABLE_GAMEPLAY_TOKEN_REWARDS": False,
    "ENABLE_JACKPOT": False,
    "ENABLE_PURCHASED_RANDOM_REWARDS": False,
    "ENABLE_TOKEN_CASHOUT": False,
    "ENABLE_PLAYER_TOKEN_TRANSFERS": False,
    "ENABLE_CLIENT_REPORTED_REWARDS": False,
    "ENABLE_PROMOTIONAL_TOKEN_REWARDS": False,
    "ENABLE_ADMIN_TOKEN_MINTS": False,
    "ENABLE_ADMIN_BALANCE_ADJUSTMENTS": False,
    "ENABLE_PASSIVE_TOKEN_REWARDS": False,
    "ENABLE_LEGACY_ASSET_CLAIMS": False,
    "ENABLE_FIXED_ITEM_SHOP": False,
    "ENABLE_FIXED_GAMEPLAY_SPENDING": False,
    "ENABLE_CARD_CRAFTING": False,
    "ENABLE_BOARD_ASSET_MUTATIONS": False,
    "ENABLE_HATCHING": False,
    "ENABLE_RECICLON": False,
}


def build_settings(**overrides) -> Settings:
    values = {**BASE_ENV, **SAFE_POLICY, **overrides}
    return Settings(_env_file=None, **values)


def test_non_gambling_defaults_are_fail_closed():
    cfg = build_settings()

    assert cfg.PRODUCT_MODE == "non_gambling"
    assert cfg.CHAIN_ECONOMY_AUTHORITATIVE is True
    assert cfg.ENABLE_FREE_GAMEPLAY is True
    assert cfg.ENABLE_PAID_GAMEPLAY is False
    assert cfg.ENABLE_JACKPOT is False
    assert cfg.ENABLE_FIAT_PAYMENTS is False
    assert cfg.ENABLE_CRYPTO_CHECKOUT is False
    assert cfg.ENABLE_PLAYER_MARKETPLACE is False
    assert cfg.ENABLE_CREATOR_PAYOUTS is False
    assert cfg.ENABLE_PURCHASED_RANDOM_REWARDS is False
    assert cfg.ENABLE_TOKEN_CASHOUT is False
    assert cfg.ENABLE_PLAYER_TOKEN_TRANSFERS is False
    assert cfg.ENABLE_ADMIN_BALANCE_ADJUSTMENTS is False
    assert cfg.ENABLE_PASSIVE_TOKEN_REWARDS is False
    assert cfg.ENABLE_LEGACY_ASSET_CLAIMS is False
    assert cfg.ENABLE_FIXED_ITEM_SHOP is False
    assert cfg.ENABLE_FIXED_GAMEPLAY_SPENDING is False
    assert cfg.ENABLE_CARD_CRAFTING is False
    assert cfg.ENABLE_BOARD_ASSET_MUTATIONS is False
    assert cfg.ENABLE_HATCHING is False
    assert cfg.ENABLE_RECICLON is False


@pytest.mark.parametrize(
    "flag",
    [
        "ENABLE_PAID_GAMEPLAY",
        "ENABLE_JACKPOT",
        "ENABLE_PURCHASED_RANDOM_REWARDS",
        "ENABLE_TOKEN_CASHOUT",
        "ENABLE_PLAYER_TOKEN_TRANSFERS",
        "ENABLE_CLIENT_REPORTED_REWARDS",
        "ENABLE_ADMIN_TOKEN_MINTS",
        "ENABLE_ADMIN_BALANCE_ADJUSTMENTS",
        "ENABLE_PASSIVE_TOKEN_REWARDS",
        "ENABLE_LEGACY_ASSET_CLAIMS",
        "ENABLE_FIXED_ITEM_SHOP",
        "ENABLE_FIXED_GAMEPLAY_SPENDING",
        "ENABLE_CARD_CRAFTING",
        "ENABLE_PLAYER_MARKETPLACE",
        "ENABLE_CREATOR_PAYOUTS",
        "ENABLE_VIP_SALES",
        "ENABLE_BOARD_ASSET_MUTATIONS",
        "ENABLE_HATCHING",
        "ENABLE_RECICLON",
    ],
)
def test_non_gambling_rejects_prohibited_features(flag):
    with pytest.raises(ValidationError, match=flag):
        build_settings(**{flag: True})


def test_legacy_simulation_is_local_only():
    local = build_settings(
        PRODUCT_MODE="legacy_simulation",
        ENABLE_PAID_GAMEPLAY=True,
        ENABLE_JACKPOT=True,
    )
    assert local.BLOCKCHAIN_MODE == "local"

    with pytest.raises(ValidationError, match="legacy_simulation"):
        build_settings(
            PRODUCT_MODE="legacy_simulation",
            BLOCKCHAIN_MODE="polygon_amoy",
            PRIVY_APP_ID="privy-app",
        )


def test_dev_payments_require_explicit_legacy_local_sandbox():
    with pytest.raises(ValidationError, match="ALLOW_DEV_PAYMENTS"):
        build_settings(ALLOW_DEV_PAYMENTS=True)

    local = build_settings(
        PRODUCT_MODE="legacy_simulation",
        ALLOW_DEV_PAYMENTS=True,
    )
    assert local.ALLOW_DEV_PAYMENTS is True


def test_commerce_requires_legal_surfaces_and_adult_gate():
    with pytest.raises(ValidationError, match="LEGAL_ENTITY_NAME"):
        build_settings(ENABLE_CRYPTO_CHECKOUT=True)

    with pytest.raises(ValidationError, match="REQUIRE_ADULT_FOR_COMMERCE"):
        build_settings(
            ENABLE_CRYPTO_CHECKOUT=True,
            REQUIRE_ADULT_FOR_COMMERCE=False,
            LEGAL_ENTITY_NAME="Axolotto Test",
            TERMS_VERSION="2026-07",
            PRIVACY_NOTICE_VERSION="2026-07",
        )


def test_fiat_payments_reject_mock_gateway():
    with pytest.raises(ValidationError, match="pasarela real"):
        build_settings(
            ENABLE_FIAT_PAYMENTS=True,
            LEGAL_ENTITY_NAME="Axolotto Test",
            TERMS_VERSION="2026-07",
            PRIVACY_NOTICE_VERSION="2026-07",
        )


def test_disabled_feature_uses_stable_503_error():
    with pytest.raises(HTTPException) as exc:
        require_feature(False, "paid_gameplay")

    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "FEATURE_DISABLED_BY_PRODUCT_POLICY"
    assert exc.value.detail["feature"] == "paid_gameplay"


def test_public_policy_exposes_new_fail_closed_capabilities(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FREE_GAMEPLAY", True)
    monkeypatch.setattr(settings, "ENABLE_PASSIVE_TOKEN_REWARDS", False)
    monkeypatch.setattr(settings, "ENABLE_FIXED_ITEM_SHOP", False)
    monkeypatch.setattr(settings, "ENABLE_FIXED_GAMEPLAY_SPENDING", False)
    monkeypatch.setattr(settings, "ENABLE_CARD_CRAFTING", False)

    policy = public_product_policy()

    assert policy["economy_authority"] == "chain"
    assert policy["economy_authority_status"] == "target_not_enforced"
    assert policy["gameplay"]["free_play"] is True
    assert policy["gameplay"]["passive_token_rewards"] is False
    assert policy["gameplay"]["fixed_spending"] is False
    assert policy["commerce"]["fixed_item_shop"] is False
    assert policy["assets"]["card_crafting"] is False
