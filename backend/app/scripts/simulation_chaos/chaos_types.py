"""
chaos_types.py — Types and configuration for the Chaos & Security Simulator v2.

Supports up to 500 concurrent bots + 6 attack agents as a PostgreSQL stress test.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import random

# ── RNG — SystemRandom exclusively (critical rule #5) ──────────────────────────
_rng = random.SystemRandom()


class IncidentSeverity(str, Enum):
    CRITICAL = "CRITICAL"   # 🔴 Immediate action required — vulnerability found
    WARNING = "WARNING"     # 🟡 Review and optimize — degraded, retry needed
    INFO = "INFO"           # 🟢 Correct behavior — attack blocked, normal flow


@dataclass
class SecurityIncident:
    """A single security-relevant event recorded during the simulation."""
    severity: IncidentSeverity
    category: str           # e.g. "replay_attack", "race_condition", "bot_500"
    description: str
    status_code: int
    detail: str
    timestamp: str          # ISO format
    thread_id: str          # which bot/agent recorded this


@dataclass
class ChaosConfig:
    """Configuration for a chaos simulation run.

    total_players bots are distributed: 20% whale, 30% collector, 50% free2play.
    """
    total_players: int = 100
    duration_seconds: int = 120
    skip_reset: bool = False
    db_url: Optional[str] = None

    # Attack agent toggles
    enable_replay_attack: bool = True
    enable_id_spoofing: bool = True
    enable_race_condition: bool = True        # Double Spend via race
    enable_double_booking: bool = True        # Multiplayer lobby abuse
    enable_boundary_injection: bool = True    # Negative amounts, overflow, null bytes
    enable_cooldown_bypass: bool = True       # Daily rewards, sleep time manipulation

    @property
    def whale_count(self) -> int:
        return max(1, int(self.total_players * 0.20))

    @property
    def collector_count(self) -> int:
        return max(1, int(self.total_players * 0.30))

    @property
    def free2play_count(self) -> int:
        return max(1, self.total_players - self.whale_count - self.collector_count)

    @property
    def total_bots(self) -> int:
        return self.whale_count + self.collector_count + self.free2play_count


# ── Chaos Bot Personalities ──────────────────────────────────────────────────
# Each personality defines action weights and think-time ranges.
# Think-times are more aggressive than original sim to generate dense traffic.

CHAOS_PERSONALITY_MAP = {
    "whale": {
        "name": "whale",
        "min_wait": 0.05,
        "max_wait": 0.3,
        "shop_weight": 0.35,
        "game_weight": 0.40,
        "care_weight": 0.10,
        "decor_weight": 0.15,
        "vip_tier": "axolite",
        "play_style": "champion",
    },
    "collector": {
        "name": "collector",
        "min_wait": 0.2,
        "max_wait": 0.8,
        "shop_weight": 0.50,
        "game_weight": 0.10,
        "care_weight": 0.20,
        "decor_weight": 0.20,
        "vip_tier": "dorado",
        "play_style": "rookie",
    },
    "free2play": {
        "name": "free2play",
        "min_wait": 0.5,
        "max_wait": 2.0,
        "shop_weight": 0.10,
        "game_weight": 0.60,
        "care_weight": 0.20,
        "decor_weight": 0.10,
        "vip_tier": None,
        "play_style": "rookie",
    },
}

# Build a list for random.choice() — N copies of each personality type
def build_personality_list(whales: int, collectors: int, free2play: int) -> list[dict]:
    """Return a flat list of personality dicts for all bots."""
    result = []
    for _ in range(whales):
        result.append(dict(CHAOS_PERSONALITY_MAP["whale"]))
    for _ in range(collectors):
        result.append(dict(CHAOS_PERSONALITY_MAP["collector"]))
    for _ in range(free2play):
        result.append(dict(CHAOS_PERSONALITY_MAP["free2play"]))
    _rng.shuffle(result)
    return result


# ── Action categories for weighted selection ──────────────────────────────────

ACTION_CATEGORIES = ["shop", "game", "care", "decor"]

# Specific actions within each category (resolved at runtime by bot_state_machine)
# These are just labels — actual functions are in bot_actions.py
