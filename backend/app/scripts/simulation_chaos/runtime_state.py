"""
Runtime shared state for the chaos simulator — thread-safe incident collector,
counters, and simulation stats. Imported by all chaos modules.
"""
import time
import threading
from typing import Optional
from chaos_types import SecurityIncident


# ── Incident collector ────────────────────────────────────────────────────────
_incidents: list[SecurityIncident] = []
_incidents_lock = threading.Lock()


def record_incident(incident: SecurityIncident) -> None:
    """Thread-safe incident recording."""
    with _incidents_lock:
        _incidents.append(incident)


def get_incidents() -> list[SecurityIncident]:
    """Return a copy of all recorded incidents."""
    with _incidents_lock:
        return list(_incidents)


def clear_incidents() -> None:
    """Reset the incident log."""
    with _incidents_lock:
        _incidents.clear()


# ── Shared counters (atomic via lock) ─────────────────────────────────────────
_counters: dict = {}
_counters_lock = threading.Lock()


def increment_counter(key: str, delta: int = 1) -> None:
    """Thread-safe counter increment."""
    with _counters_lock:
        _counters[key] = _counters.get(key, 0) + delta


def get_counters() -> dict:
    """Return a copy of all counters."""
    with _counters_lock:
        return dict(_counters)


def clear_counters() -> None:
    """Reset all counters."""
    with _counters_lock:
        _counters.clear()


# ── Simulation stats ──────────────────────────────────────────────────────────
_stats: dict = {}
_stats_lock = threading.Lock()


def update_stat(key: str, value) -> None:
    """Thread-safe stat increment (int/float) or set."""
    with _stats_lock:
        if key in _stats and isinstance(_stats[key], (int, float)) and isinstance(value, (int, float)):
            _stats[key] += value
        else:
            _stats[key] = value


def increment_stat(key: str, delta: int = 1) -> None:
    """Shorthand for numeric increment."""
    update_stat(key, delta)


def get_stats() -> dict:
    """Return a copy of all stats."""
    with _stats_lock:
        return dict(_stats)


def clear_stats() -> None:
    """Reset all stats."""
    with _stats_lock:
        _stats.clear()


# ── DB session semaphore (prevents connection pool exhaustion) ────────────────
_db_semaphore: Optional[threading.BoundedSemaphore] = None


def init_db_semaphore(max_connections: int = 100) -> None:
    """Initialize the DB connection semaphore. Called once at runner startup."""
    global _db_semaphore
    _db_semaphore = threading.BoundedSemaphore(max_connections)


def get_db_semaphore() -> Optional[threading.BoundedSemaphore]:
    """Get the DB semaphore (None if not initialized)."""
    return _db_semaphore


# ── Live activity tracking (for visual dashboard) ────────────────────────────
# Maps thread_id -> {"action": str, "zone": str, "timestamp": float, "color": str, "type": "bot"|"attack"}
_live_activities: dict = {}
_live_activities_lock = threading.Lock()

# Zone definitions for the visual dashboard
ZONES = {
    "shop":        {"name": "Tienda",       "emoji": "🛒", "css_class": "zone-shop"},
    "tutorial":    {"name": "Tutorial",     "emoji": "📖", "css_class": "zone-tutorial"},
    "incubation":  {"name": "Incubación",   "emoji": "🥚", "css_class": "zone-incubation"},
    "solo_game":   {"name": "Partida Solo", "emoji": "🎮", "css_class": "zone-solo"},
    "multiplayer": {"name": "Multiplayer",  "emoji": "⚔️", "css_class": "zone-multi"},
    "gashapon":    {"name": "Gashapon",     "emoji": "🎰", "css_class": "zone-gasha"},
    "cave":        {"name": "Cueva",        "emoji": "🏠", "css_class": "zone-cave"},
    "daily":       {"name": "Daily Rewards","emoji": "🌙", "css_class": "zone-daily"},
    "care":        {"name": "Cuidado",      "emoji": "💤", "css_class": "zone-care"},
    "staking":     {"name": "Staking",      "emoji": "🎓", "css_class": "zone-staking"},
    "idle":        {"name": "Idle",         "emoji": "⏳", "css_class": "zone-idle"},
    "replay":      {"name": "Replay Atk",   "emoji": "🔄", "css_class": "zone-attack"},
    "spoof":       {"name": "ID Spoof",     "emoji": "👤", "css_class": "zone-attack"},
    "race":        {"name": "Race Cond",    "emoji": "⚡", "css_class": "zone-attack"},
    "booking":     {"name": "Double Book",  "emoji": "🎯", "css_class": "zone-attack"},
    "injection":   {"name": "Injection",    "emoji": "💉", "css_class": "zone-attack"},
    "cooldown":    {"name": "Cooldown Byp", "emoji": "⏱️", "css_class": "zone-attack"},
}

# Color palette for bot personalities (tailwind-compatible)
BOT_COLORS = {
    "whale":     "#6366F1",  # indigo
    "collector": "#10B981",  # emerald
    "free2play": "#9CA3AF",  # gray-400
}
ATTACK_COLOR = "#EF4444"  # red-500


def report_activity(thread_id: str, zone: str, action: str,
                    bot_type: str = "bot", personality: str = "free2play") -> None:
    """Report what a bot/agent is currently doing. Called before each action."""
    color = BOT_COLORS.get(personality, BOT_COLORS["free2play"])
    if bot_type == "attack":
        color = ATTACK_COLOR
    with _live_activities_lock:
        _live_activities[thread_id] = {
            "action": action,
            "zone": zone,
            "timestamp": time.monotonic(),
            "color": color,
            "type": bot_type,
            "personality": personality,
            "thread_id": thread_id,
        }


def get_live_activities() -> dict:
    """Return a snapshot of current activities (for API polling)."""
    with _live_activities_lock:
        return dict(_live_activities)


def clear_activities() -> None:
    """Clear all live activities."""
    with _live_activities_lock:
        _live_activities.clear()


def remove_activity(thread_id: str) -> None:
    """Remove a single bot/agent from live activities (called on bot finish)."""
    with _live_activities_lock:
        _live_activities.pop(thread_id, None)


# ── Reset all state ───────────────────────────────────────────────────────────
def reset_all_state() -> None:
    """Clear all shared state. Called at the start of a new simulation."""
    clear_incidents()
    clear_counters()
    clear_stats()
    clear_activities()
    global _db_semaphore
    _db_semaphore = None
