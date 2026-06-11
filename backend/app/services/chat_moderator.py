"""
chat_moderator.py — Chat message sanitization, rate limiting, and enrichment.

Handles:
- Profanity / spam filtering via regex
- URL/hex address blocking (anti-phishing for Web3)
- Rate limiting per user (cooldown)
- VIP tier and Nature enrichment for broadcast
- Megaphone FRJ cost validation
"""

from __future__ import annotations
import re
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("chat.moderator")

# ---------------------------------------------------------------------------
# Compiled regex patterns — compiled once at import time
# ---------------------------------------------------------------------------

# Block external URLs (only axolot.to domain allowed)
URL_PATTERN = re.compile(
    r'https?://(?!(?:[\w.-]*\.)?axolot\.to(?:\/|$|\s))[^\s]+',
    re.IGNORECASE,
)

# Block hexadecimal addresses (Ethereum-style 0x...)
HEX_ADDRESS_PATTERN = re.compile(r'\b0x[a-fA-F0-9]{40}\b')

# Block common crypto scam keywords
SCAM_KEYWORDS = re.compile(
    r'\b(airdrop|giveaway|free\s*token|send\s*eth|claim\s*now|verify\s*wallet|'
    r'connect\s*wallet|mint\s*now|whitelist|presale|double\s*your)\b',
    re.IGNORECASE,
)

# Profanity / offensive words (basic list — expand as needed)
PROFANITY_PATTERN = re.compile(
    r'\b(fuck|shit|ass|bitch|bastard|damn|puto|mierda|cabr[oó]n|pendejo|'
    r'chinga|verga|hdp|joder|coño|carajo|gilipollas)\b',
    re.IGNORECASE,
)

# Max message length
MAX_MESSAGE_LENGTH = 280

# Rate limit: messages per user per cooldown window
RATE_LIMIT_WINDOW_SEC = 1.5
RATE_LIMIT_MAX_MESSAGES = 1  # 1 message per 1.5s per user

# Megaphone cost in FRJ (aligned with plan: 10 FRJ)
MEGAPHONE_COST_FRJ = 10

# Allowed sticker IDs (populated from DB or config)
VALID_STICKER_IDS: set[str] = set()  # Fase 4 will populate this


@dataclass
class ModerationResult:
    """Result of moderating a chat message."""
    allowed: bool
    sanitized_text: str = ""
    reason: str = ""
    is_megaphone: bool = False
    megaphone_cost_frj: int = 0
    sticker_id: str | None = None


@dataclass
class RateLimitState:
    """Per-user rate limit tracking."""
    last_message_at: float = 0.0
    message_count: int = 0
    window_start: float = 0.0
    muted_until: float = 0.0  # auto-mute expiration (epoch seconds)


# ---------------------------------------------------------------------------
# Chat Moderator
# ---------------------------------------------------------------------------


class ChatModerator:
    """
    Sanitizes, rate-limits, and enriches chat messages for WebSocket broadcast.

    Thread-safe for asyncio (single-threaded event loop).
    """

    def __init__(self) -> None:
        self._rate_limits: dict[str, RateLimitState] = {}

    # ------------------------------------------------------------------
    # Sanitization
    # ------------------------------------------------------------------

    def sanitize(self, text: str, is_public_room: bool = True) -> ModerationResult:
        """
        Validate and sanitize a chat message.

        Args:
            text: Raw message text from the client.
            is_public_room: If True, apply strict public-room filters (anti-scam, profanity, URL blocking).

        Returns:
            ModerationResult with allowed flag and sanitized text.
        """
        # 1. Length check
        if len(text) > MAX_MESSAGE_LENGTH:
            return ModerationResult(
                allowed=False,
                reason=f"Mensaje demasiado largo (máx {MAX_MESSAGE_LENGTH} caracteres).",
            )

        sanitized = text.strip()

        # 2. Empty check
        if not sanitized:
            return ModerationResult(
                allowed=False,
                reason="Mensaje vacío.",
            )

        if is_public_room:
            # 3. URL blocking (only axolot.to allowed)
            if URL_PATTERN.search(sanitized):
                return ModerationResult(
                    allowed=False,
                    reason="No se permiten enlaces externos en salas públicas.",
                )

            # 4. Hex address blocking (anti-phishing)
            if HEX_ADDRESS_PATTERN.search(sanitized):
                return ModerationResult(
                    allowed=False,
                    reason="No se permiten direcciones de wallet en el chat público.",
                )

            # 5. Scam keyword detection
            if SCAM_KEYWORDS.search(sanitized):
                return ModerationResult(
                    allowed=False,
                    reason="Mensaje bloqueado por seguridad (posible scam).",
                )

        # 6. Profanity filter
        match = PROFANITY_PATTERN.search(sanitized)
        if match:
            # Replace profanity with asterisks
            sanitized = PROFANITY_PATTERN.sub(
                lambda m: '*' * len(m.group()), sanitized
            )

        return ModerationResult(
            allowed=True,
            sanitized_text=sanitized,
        )

    def sanitize_sticker(self, sticker_id: str) -> ModerationResult:
        """Validate a sticker message."""
        if not sticker_id:
            return ModerationResult(allowed=False, reason="Sticker ID vacío.")

        if VALID_STICKER_IDS and sticker_id not in VALID_STICKER_IDS:
            return ModerationResult(
                allowed=False,
                reason=f"Sticker no válido: {sticker_id}",
            )

        return ModerationResult(
            allowed=True,
            sanitized_text="",
            sticker_id=sticker_id,
        )

    # ------------------------------------------------------------------
    # Rate limiting
    # ------------------------------------------------------------------

    def check_rate_limit(self, user_id: str, is_reaction: bool = False) -> ModerationResult:
        """
        Check if user is within rate limits.

        Quick reactions have a shorter visual cooldown (handled client-side),
        but server still enforces a soft limit.
        """
        now = time.time()
        state = self._rate_limits.get(user_id)

        if state is None:
            state = RateLimitState()
            self._rate_limits[user_id] = state

        # Check auto-mute
        if state.muted_until > now:
            remaining = int(state.muted_until - now)
            return ModerationResult(
                allowed=False,
                reason=f"Has sido silenciado temporalmente. Intenta de nuevo en {remaining}s.",
            )

        # Reset window if needed
        if now - state.window_start > RATE_LIMIT_WINDOW_SEC:
            state.window_start = now
            state.message_count = 0

        # Reactions have a more permissive limit
        effective_max = RATE_LIMIT_MAX_MESSAGES * 3 if is_reaction else RATE_LIMIT_MAX_MESSAGES

        if state.message_count >= effective_max:
            return ModerationResult(
                allowed=False,
                reason="Demasiados mensajes. Espera un momento.",
            )

        state.message_count += 1
        state.last_message_at = now

        return ModerationResult(allowed=True)

    def apply_auto_mute(self, user_id: str, duration_seconds: int = 300) -> None:
        """
        Apply an automatic mute (5 min default) for repeated offenses.

        Called when a user triggers multiple moderation blocks in a short window.
        """
        state = self._rate_limits.get(user_id)
        if state is None:
            state = RateLimitState()
            self._rate_limits[user_id] = state

        state.muted_until = time.time() + duration_seconds
        logger.info(f"User {user_id} auto-muted for {duration_seconds}s")

    def clear_mute(self, user_id: str) -> None:
        """Manually clear a user's mute (admin action)."""
        state = self._rate_limits.get(user_id)
        if state:
            state.muted_until = 0.0

    # ------------------------------------------------------------------
    # Message enrichment for broadcast
    # ------------------------------------------------------------------

    @staticmethod
    def enrich_for_broadcast(
        user_id: str,
        username: str,
        text: str,
        vip_tier: str | None,
        nature: str | None,
        sticker_id: str | None = None,
        megaphone: bool = False,
    ) -> dict[str, Any]:
        """
        Build the broadcast-ready message payload with VIP and Nature metadata.

        This is called AFTER sanitization and rate-limit checks pass.
        """
        return {
            "player_id": user_id,
            "username": username,
            "vip_tier": vip_tier or "none",
            "nature": nature or "curious",
            "text": text,
            "sticker_id": sticker_id,
            "megaphone": megaphone,
            "timestamp": int(time.time()),
        }

    # ------------------------------------------------------------------
    # Megaphone cost validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_megaphone(
        wallet_frj_balance: int,
        frj_decimals: int = 2,
    ) -> ModerationResult:
        """
        Validate that the user can afford the megaphone cost.

        Called BEFORE broadcasting. If insufficient balance, the message
        is still sent but without megaphone highlight.

        Args:
            wallet_frj_balance: User's FRJ balance in backend units (int).
            frj_decimals: 10^decimals for conversion.
        """
        cost_units = MEGAPHONE_COST_FRJ * (10 ** frj_decimals)

        if wallet_frj_balance < cost_units:
            return ModerationResult(
                allowed=False,
                reason=f"Saldo insuficiente para megáfono. Necesitas {MEGAPHONE_COST_FRJ} FRJ.",
                is_megaphone=False,
            )

        return ModerationResult(
            allowed=True,
            is_megaphone=True,
            megaphone_cost_frj=MEGAPHONE_COST_FRJ,
        )


# Singleton instance
chat_moderator = ChatModerator()
