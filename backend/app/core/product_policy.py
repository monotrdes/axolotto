"""Fail-closed product feature gates for the non-gambling model."""

from fastapi import HTTPException, status

from app.core.config import settings


def require_feature(enabled: bool, feature: str) -> None:
    """Reject a disabled value-bearing feature with a stable API error."""
    if enabled:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "FEATURE_DISABLED_BY_PRODUCT_POLICY",
            "feature": feature,
            "product_mode": settings.PRODUCT_MODE,
        },
    )


def is_legacy_local() -> bool:
    """Return whether the process is the explicit, non-public legacy sandbox."""
    return (
        settings.PRODUCT_MODE == "legacy_simulation"
        and settings.BLOCKCHAIN_MODE == "local"
    )


def require_legacy_local(feature: str) -> None:
    """Reject simulation-only operations outside the explicit local sandbox."""
    require_feature(is_legacy_local(), feature)


def dev_payments_allowed() -> bool:
    """Synthetic payment receipts require both the sandbox and its opt-in."""
    return is_legacy_local() and settings.ALLOW_DEV_PAYMENTS


def public_product_policy() -> dict:
    """Return only policy values that clients need to hide unsafe flows."""
    return {
        "product_mode": settings.PRODUCT_MODE,
        "economy_authority": (
            "chain" if settings.CHAIN_ECONOMY_AUTHORITATIVE else "database"
        ),
        # The desired authority is public, but the current outbox still lacks
        # receipt finality/indexer reconciliation. Do not imply it is enforced.
        "economy_authority_status": (
            "target_not_enforced"
            if settings.CHAIN_ECONOMY_AUTHORITATIVE
            else "database_legacy"
        ),
        "gameplay": {
            "free_play": settings.ENABLE_FREE_GAMEPLAY,
            "paid_entries": settings.ENABLE_PAID_GAMEPLAY,
            "token_rewards": settings.ENABLE_GAMEPLAY_TOKEN_REWARDS,
            "passive_token_rewards": settings.ENABLE_PASSIVE_TOKEN_REWARDS,
            "fixed_spending": settings.ENABLE_FIXED_GAMEPLAY_SPENDING,
            "jackpot": settings.ENABLE_JACKPOT,
        },
        "commerce": {
            "fiat_payments": settings.ENABLE_FIAT_PAYMENTS,
            "crypto_checkout": settings.ENABLE_CRYPTO_CHECKOUT,
            "player_marketplace": settings.ENABLE_PLAYER_MARKETPLACE,
            "creator_payouts": settings.ENABLE_CREATOR_PAYOUTS,
            "vip_sales": settings.ENABLE_VIP_SALES,
            "purchased_random_rewards": settings.ENABLE_PURCHASED_RANDOM_REWARDS,
            "fixed_item_shop": settings.ENABLE_FIXED_ITEM_SHOP,
        },
        "tokens": {
            "player_transfers": settings.ENABLE_PLAYER_TOKEN_TRANSFERS,
            "cashout": settings.ENABLE_TOKEN_CASHOUT,
        },
        "assets": {
            "board_mutations": settings.ENABLE_BOARD_ASSET_MUTATIONS,
            "hatching": settings.ENABLE_HATCHING,
            "card_crafting": settings.ENABLE_CARD_CRAFTING,
            "legacy_asset_claims": settings.ENABLE_LEGACY_ASSET_CLAIMS,
            "reciclon": settings.ENABLE_RECICLON,
        },
        "safety": {
            "adult_required_for_commerce": settings.REQUIRE_ADULT_FOR_COMMERCE,
            "client_reported_rewards": settings.ENABLE_CLIENT_REPORTED_REWARDS,
            "promotional_token_rewards": settings.ENABLE_PROMOTIONAL_TOKEN_REWARDS,
        },
    }
