#!/usr/bin/env python3
from __future__ import annotations
"""Thread-safe API rate limit tracker for AI providers.

Tracks per-provider request counts locally since Anthropic and DeepSeek
don't expose standard rate-limit headers. Gemini headers parsed when available.
"""

import time
from datetime import datetime, timezone
from threading import Lock


class RateLimitTracker:
    """Track API rate limits across all providers. Thread-safe."""

    # Approximate rate limits per provider (requests per minute)
    _RPM_LIMITS = {
        "claude": 100,         # Anthropic tier 1
        "deepclaude": 500,     # DeepSeek via claude CLI
    }

    def __init__(self):
        self._lock = Lock()
        self._limits = {}
        for provider in self._RPM_LIMITS:
            self._limits[provider] = self._default_state(provider)

    def _default_state(self, provider: str) -> dict:
        return {
            "remaining": self._RPM_LIMITS.get(provider, 100),
            "limit": self._RPM_LIMITS.get(provider, 100),
            "reset_at": None,
            "last_checked": None,
            "available": True,
            "requests_this_minute": 0,
            "minute_start": time.time(),
            "total_calls": 0,
            "total_errors": 0,
            "cooldown_until": 0,
        }

    def record_call(self, provider: str, response_headers: dict | None = None):
        """Update tracking after a successful API call."""
        with self._lock:
            state = self._limits.get(provider)
            if not state:
                return

            now = time.time()
            # Reset per-minute counter if window elapsed
            if now - state["minute_start"] > 60:
                state["requests_this_minute"] = 0
                state["minute_start"] = now
                state["available"] = True  # reset on new window

            state["requests_this_minute"] += 1
            state["total_calls"] += 1
            state["last_checked"] = datetime.now(timezone.utc).isoformat()

            # Update remaining
            limit = state["limit"]
            rpm = state["requests_this_minute"]
            state["remaining"] = max(0, limit - rpm)

            # Parse Gemini/Google rate-limit headers if present
            if response_headers:
                if "X-RateLimit-Remaining" in response_headers:
                    state["remaining"] = int(response_headers["X-RateLimit-Remaining"])
                if "X-RateLimit-Limit" in response_headers:
                    state["limit"] = int(response_headers["X-RateLimit-Limit"])
                if "X-RateLimit-Reset" in response_headers:
                    state["reset_at"] = response_headers["X-RateLimit-Reset"]

    def record_error(self, provider: str, status_code: int, cooldown_seconds: int = 30):
        """Record an API error. 429 triggers cooldown. Pass cooldown_seconds for custom duration."""
        with self._lock:
            state = self._limits.get(provider)
            if not state:
                return

            now = time.time()
            state["total_errors"] += 1
            state["last_checked"] = datetime.now(timezone.utc).isoformat()

            if status_code == 429:
                state["available"] = False
                state["remaining"] = 0
                state["cooldown_until"] = now + cooldown_seconds
            # 401/403 logged but don't disable

    def get_status(self, provider: str | None = None) -> dict:
        """Get rate limit status. Returns all providers if provider is None."""
        with self._lock:
            if provider:
                s = self._limits.get(provider)
                return dict(s) if s else {}
            return {k: dict(v) for k, v in self._limits.items()}

    def is_available(self, provider: str) -> bool:
        """Check if a provider is currently available. Auto-recovers from cooldown."""
        with self._lock:
            state = self._limits.get(provider)
            if not state:
                return False
            # Auto-recover from cooldown if time has passed
            if not state["available"] and state.get("cooldown_until", 0) > 0:
                if time.time() >= state["cooldown_until"]:
                    state["available"] = True
                    state["remaining"] = state["limit"]  # Reset remaining
                    state["cooldown_until"] = 0
            return state["available"]
