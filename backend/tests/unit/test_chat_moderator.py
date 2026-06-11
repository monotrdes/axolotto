"""
test_chat_moderator.py — Unit tests for the chat moderation service.

Covers: sanitization, rate limiting, megaphone validation, enrichment.
"""

import time
import pytest
from app.services.chat_moderator import (
    ChatModerator,
    ModerationResult,
    MEGAPHONE_COST_FRJ,
    RATE_LIMIT_WINDOW_SEC,
)


class TestSanitization:
    """Message sanitization tests."""

    def setup_method(self):
        self.moderator = ChatModerator()

    def test_empty_message_blocked(self):
        result = self.moderator.sanitize("   ", is_public_room=True)
        assert not result.allowed
        assert "vacío" in result.reason.lower()

    def test_message_too_long_blocked(self):
        long_text = "A" * 300
        result = self.moderator.sanitize(long_text, is_public_room=True)
        assert not result.allowed
        assert "largo" in result.reason.lower()

    def test_clean_message_passes(self):
        result = self.moderator.sanitize("¡Hola a todos!", is_public_room=True)
        assert result.allowed
        assert result.sanitized_text == "¡Hola a todos!"

    def test_external_url_blocked_public(self):
        result = self.moderator.sanitize("Check this: https://scam.com/fake", is_public_room=True)
        assert not result.allowed
        assert "enlaces" in result.reason.lower() or "externos" in result.reason.lower()

    def test_axolotto_url_allowed(self):
        result = self.moderator.sanitize("Join at https://axolot.to/game", is_public_room=True)
        assert result.allowed

    def test_hex_address_blocked_public(self):
        result = self.moderator.sanitize(
            "Send to 0x1234567890abcdef1234567890abcdef12345678 please",
            is_public_room=True,
        )
        assert not result.allowed
        assert "wallet" in result.reason.lower() or "dirección" in result.reason.lower()

    def test_scam_keywords_blocked(self):
        result = self.moderator.sanitize("FREE AIRDROP claim now!!!", is_public_room=True)
        assert not result.allowed
        assert "scam" in result.reason.lower() or "seguridad" in result.reason.lower()

    def test_profanity_censored(self):
        result = self.moderator.sanitize("¡Qué mierda es esto!", is_public_room=True)
        assert result.allowed
        assert "mierda" not in result.sanitized_text
        assert "******" in result.sanitized_text

    def test_private_room_skips_url_block(self):
        """Private rooms allow URLs and hex addresses."""
        result = self.moderator.sanitize(
            "Check https://example.com and 0x1234567890abcdef1234567890abcdef12345678",
            is_public_room=False,
        )
        assert result.allowed
        # URLs and hex addresses should pass through in private rooms
        assert "https://example.com" in result.sanitized_text

    def test_private_room_still_censors_profanity(self):
        """Even private rooms get profanity censored."""
        result = self.moderator.sanitize("This is shit content", is_public_room=False)
        assert result.allowed
        assert "shit" not in result.sanitized_text.lower()

    def test_sticker_validation(self):
        result = self.moderator.sanitize_sticker("")
        assert not result.allowed

        result = self.moderator.sanitize_sticker("sticker_hello")
        # Without populated VALID_STICKER_IDS, any non-empty sticker passes
        assert result.allowed
        assert result.sticker_id == "sticker_hello"


class TestRateLimiting:
    """Rate limiting tests."""

    def setup_method(self):
        self.moderator = ChatModerator()

    def test_first_message_allowed(self):
        result = self.moderator.check_rate_limit("user-1")
        assert result.allowed

    def test_rapid_fire_blocked(self):
        """Two messages within the same window should be blocked."""
        user_id = "user-2"
        # First message passes
        r1 = self.moderator.check_rate_limit(user_id)
        assert r1.allowed

        # Immediate second message fails (within same window)
        r2 = self.moderator.check_rate_limit(user_id)
        assert not r2.allowed

    def test_reactions_have_more_lenient_limit(self):
        """Reactions allow more messages per window."""
        user_id = "user-3"
        for i in range(3):
            result = self.moderator.check_rate_limit(user_id, is_reaction=True)
            assert result.allowed, f"Reaction {i+1} should be allowed"

        # 4th reaction should still be blocked
        r4 = self.moderator.check_rate_limit(user_id, is_reaction=True)
        # Should be blocked (effective_max = 1 * 3 = 3)
        assert not r4.allowed

    def test_rate_limit_resets_after_window(self):
        """After the window passes, user can send again."""
        user_id = "user-4"
        # Send first message
        self.moderator.check_rate_limit(user_id)
        # Manually advance the window by modifying state
        state = self.moderator._rate_limits[user_id]
        state.window_start = time.time() - RATE_LIMIT_WINDOW_SEC - 0.1
        state.message_count = 1

        # Next message should reset window and pass
        result = self.moderator.check_rate_limit(user_id)
        assert result.allowed

    def test_auto_mute_blocks_all_messages(self):
        user_id = "user-5"
        self.moderator.apply_auto_mute(user_id, duration_seconds=60)
        result = self.moderator.check_rate_limit(user_id)
        assert not result.allowed
        assert "silenciado" in result.reason.lower()

    def test_clear_mute_restores(self):
        user_id = "user-6"
        self.moderator.apply_auto_mute(user_id, duration_seconds=60)
        self.moderator.clear_mute(user_id)
        result = self.moderator.check_rate_limit(user_id)
        assert result.allowed


class TestMegaphoneValidation:
    """Megaphone FRJ cost validation tests."""

    def test_sufficient_balance_passes(self):
        result = ChatModerator.validate_megaphone(
            wallet_frj_balance=100_000,  # 1000 FRJ in backend units (assuming decimals=2)
            frj_decimals=2,
        )
        assert result.allowed
        assert result.is_megaphone
        assert result.megaphone_cost_frj == MEGAPHONE_COST_FRJ

    def test_insufficient_balance_blocks(self):
        result = ChatModerator.validate_megaphone(
            wallet_frj_balance=500,  # 5 FRJ — not enough
            frj_decimals=2,
        )
        assert not result.allowed
        assert not result.is_megaphone

    def test_exact_balance_passes(self):
        exact_cost = MEGAPHONE_COST_FRJ * 100  # 10 FRJ * 10^2 = 1000 backend units
        result = ChatModerator.validate_megaphone(
            wallet_frj_balance=exact_cost,
            frj_decimals=2,
        )
        assert result.allowed


class TestEnrichment:
    """Message enrichment for broadcast tests."""

    def test_basic_enrichment(self):
        msg = ChatModerator.enrich_for_broadcast(
            user_id="usr-123",
            username="AxoPro",
            text="¡Hola!",
            vip_tier="dorado",
            nature="hyperactive",
        )
        assert msg["player_id"] == "usr-123"
        assert msg["username"] == "AxoPro"
        assert msg["text"] == "¡Hola!"
        assert msg["vip_tier"] == "dorado"
        assert msg["nature"] == "hyperactive"
        assert msg["megaphone"] is False
        assert msg["sticker_id"] is None
        assert isinstance(msg["timestamp"], int)

    def test_default_values_for_none(self):
        msg = ChatModerator.enrich_for_broadcast(
            user_id="usr-456",
            username="Newbie",
            text="hey",
            vip_tier=None,
            nature=None,
        )
        assert msg["vip_tier"] == "none"
        assert msg["nature"] == "curious"

    def test_megaphone_enrichment(self):
        msg = ChatModerator.enrich_for_broadcast(
            user_id="usr-789",
            username="RichAxo",
            text="BIG ANNOUNCEMENT",
            vip_tier="axolite",
            nature="showoff",
            sticker_id=None,
            megaphone=True,
        )
        assert msg["megaphone"] is True

    def test_sticker_enrichment(self):
        msg = ChatModerator.enrich_for_broadcast(
            user_id="usr-012",
            username="StickerFan",
            text="",
            vip_tier="coral",
            nature="shy",
            sticker_id="sticker_gg",
        )
        assert msg["sticker_id"] == "sticker_gg"
