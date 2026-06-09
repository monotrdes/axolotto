"""
test_simulation_modules.py — Unit tests for the modular simulation package.

Tests cover sim_types.py, utils.py, and all phase_XX.py files without hitting
a real database. App modules are mocked before any phase import.
"""
import sys
import os
import importlib
import importlib.util
from unittest.mock import MagicMock

# ── sys.path setup (mirror runner.py) ────────────────────────────────────────
_this_dir    = os.path.dirname(os.path.abspath(__file__))
_sim_dir     = os.path.abspath(os.path.join(_this_dir, "../../app/scripts/simulation"))
_backend_dir = os.path.abspath(os.path.join(_this_dir, "../../"))
_REPO_ROOT   = os.path.abspath(os.path.join(_this_dir, "../../.."))

# Insert at position 0 so simulation-local imports (sim_types, phase_XX) resolve
# before any installed package with the same name.
if _sim_dir not in sys.path:
    sys.path.insert(0, _sim_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# ── Mock the entire app module tree before any phase/utils import ─────────────
# Phase files do top-level "from app.X import Y" which would try to connect to a
# database or load heavy FastAPI state. We stub out every sub-module they touch.
_APP_MOCKS = [
    "app",
    "app.database",
    "app.core",
    "app.core.config",
    "app.models",
    "app.models.user",
    "app.models.economy",
    "app.models.items",
    "app.models.axolotito",
    "app.models.board",
    "app.models.lobby_models",
    "app.services",
    "app.services.bank_service",
    "app.services.shop_service",
    "app.services.multiplayer_service",
    "app.services.web3_service",
    "app.api",
    "app.api.v1",
    "app.api.v1.endpoints",
    "app.api.v1.endpoints.incubation",
    "app.api.v1.endpoints.board",
    "app.api.v1.endpoints.game",
    "app.api.v1.endpoints.shop",
    "app.api.v1.endpoints.user",
    "app.api.v1.endpoints.market",
    "app.api.v1.endpoints.multiplayer",
    "app.scripts",
    "app.scripts.seed_cards",
    "app.scripts.seed_catalog",
]

import pytest

@pytest.fixture(scope="module", autouse=True)
def mock_app_tree():
    _original_sys_modules = {}
    for _mod_name in _APP_MOCKS:
        if _mod_name in sys.modules:
            _original_sys_modules[_mod_name] = sys.modules[_mod_name]
        else:
            _original_sys_modules[_mod_name] = None
            sys.modules[_mod_name] = MagicMock()

    yield

    for _mod_name, _original_val in _original_sys_modules.items():
        if _original_val is None:
            sys.modules.pop(_mod_name, None)
        else:
            sys.modules[_mod_name] = _original_val

# sim_types and utils have no circular deps between each other
from sim_types import SimConfig, PERSONALITY_POOL, BOOSTER_OPEN_STRATEGY  # noqa: E402


# =============================================================================
# 1. SimConfig — dataclass defaults and overrides
# =============================================================================

class TestSimConfigDefaults:
    def test_defaults(self):
        config = SimConfig()
        assert config.players == 4
        assert config.incubation == 45
        assert config.games == 5
        assert config.skip_reset is False

    def test_multi_wait_default(self):
        config = SimConfig()
        assert config.multi_wait == 35

    def test_optional_fields_default_to_none(self):
        config = SimConfig()
        assert config.max_boosters is None
        assert config.max_boards is None
        assert config.max_webitos is None
        assert config.include_user is None
        assert config.db_url is None


class TestSimConfigOverrides:
    def test_players_override(self):
        config = SimConfig(players=10)
        assert config.players == 10
        assert config.incubation == 45  # unchanged

    def test_max_boosters_override(self):
        config = SimConfig(max_boosters=5)
        assert config.max_boosters == 5
        assert config.players == 4     # unchanged

    def test_skip_reset_override(self):
        config = SimConfig(skip_reset=True)
        assert config.skip_reset is True

    def test_combined_override(self):
        config = SimConfig(players=10, max_boosters=5)
        assert config.players == 10
        assert config.max_boosters == 5
        assert config.incubation == 45  # unchanged

    def test_include_user_override(self):
        did = "did:privy:test123"
        config = SimConfig(include_user=did)
        assert config.include_user == did

    def test_db_url_override(self):
        url = "postgresql://user:pass@localhost/axolotto"
        config = SimConfig(db_url=url)
        assert config.db_url == url

    def test_games_override(self):
        config = SimConfig(games=20)
        assert config.games == 20

    def test_incubation_override(self):
        config = SimConfig(incubation=120)
        assert config.incubation == 120


# =============================================================================
# 2. PERSONALITY_POOL — structure validation
# =============================================================================

class TestPersonalityPool:
    def test_has_exactly_5_entries(self):
        assert len(PERSONALITY_POOL) == 5

    def test_required_fields_present(self):
        required = {"name", "vip_tier", "play_style"}
        for p in PERSONALITY_POOL:
            for field in required:
                assert field in p, f"Missing '{field}' in personality {p.get('name')!r}"

    def test_numeric_fields_present(self):
        numeric_fields = {"boosters_normal", "boosters_foil", "eggs", "boards_random", "solo_games"}
        for p in PERSONALITY_POOL:
            for field in numeric_fields:
                assert field in p, f"Missing '{field}' in personality {p.get('name')!r}"
                assert isinstance(p[field], (int, float)), (
                    f"Field '{field}' in personality {p.get('name')!r} must be numeric"
                )

    def test_all_names_are_unique(self):
        names = [p["name"] for p in PERSONALITY_POOL]
        assert len(names) == len(set(names)), "Personality names must be unique"

    def test_known_personality_names(self):
        names = {p["name"] for p in PERSONALITY_POOL}
        expected = {"whale", "collector", "aggressive", "casual", "free2play"}
        assert names == expected

    def test_play_style_values_are_valid(self):
        valid_styles = {"rookie", "champion"}
        for p in PERSONALITY_POOL:
            assert p["play_style"] in valid_styles, (
                f"Personality {p['name']!r} has invalid play_style {p['play_style']!r}"
            )

    def test_does_triple_suerte_is_bool(self):
        for p in PERSONALITY_POOL:
            assert isinstance(p["does_triple_suerte"], bool), (
                f"Personality {p['name']!r}: does_triple_suerte must be bool"
            )

    def test_auto_budget_is_non_negative(self):
        for p in PERSONALITY_POOL:
            assert p["auto_budget"] >= 0, (
                f"Personality {p['name']!r}: auto_budget must be >= 0"
            )


# =============================================================================
# 3. BOOSTER_OPEN_STRATEGY — completeness and validity
# =============================================================================

class TestBoosterOpenStrategy:
    def test_all_personalities_covered(self):
        """Every personality name must have an entry in BOOSTER_OPEN_STRATEGY."""
        for p in PERSONALITY_POOL:
            assert p["name"] in BOOSTER_OPEN_STRATEGY, (
                f"Personality {p['name']!r} missing from BOOSTER_OPEN_STRATEGY"
            )

    def test_strategy_values_are_valid(self):
        valid_strategies = {"immediate", "selective", "hoarder", "random"}
        for name, strategy in BOOSTER_OPEN_STRATEGY.items():
            assert strategy in valid_strategies, (
                f"BOOSTER_OPEN_STRATEGY[{name!r}] = {strategy!r} is not a valid strategy"
            )

    def test_whale_uses_immediate_strategy(self):
        assert BOOSTER_OPEN_STRATEGY["whale"] == "immediate"

    def test_no_extra_keys(self):
        """BOOSTER_OPEN_STRATEGY should not reference personalities that don't exist."""
        personality_names = {p["name"] for p in PERSONALITY_POOL}
        for key in BOOSTER_OPEN_STRATEGY:
            assert key in personality_names, (
                f"BOOSTER_OPEN_STRATEGY has key {key!r} not found in PERSONALITY_POOL"
            )

    def test_has_exactly_5_entries(self):
        assert len(BOOSTER_OPEN_STRATEGY) == 5


# =============================================================================
# 4. _make_bar utility — from utils.py
# =============================================================================

class TestMakeBar:
    """
    utils.py imports app modules at module level. We import _make_bar by loading
    only that function via exec on the source, extracting just what we need.

    Alternatively: because app modules are already mocked in sys.modules, a plain
    import of utils should succeed without DB connection.
    """

    @pytest.fixture(autouse=True, scope="class")
    def import_make_bar(self, request):
        """Import _make_bar once for the whole class."""
        # utils.py module-level imports will resolve against our MagicMock stubs
        import utils as _utils_mod
        request.cls._make_bar = staticmethod(_utils_mod._make_bar)

    def test_full_bar(self):
        bar = self._make_bar(100, width=10)
        assert bar == "█" * 10
        assert "░" not in bar

    def test_empty_bar(self):
        bar = self._make_bar(0, width=10)
        assert bar == "░" * 10
        assert "█" not in bar

    def test_half_bar(self):
        bar = self._make_bar(50, width=10)
        assert bar == "█" * 5 + "░" * 5
        assert len(bar) == 10

    def test_returns_string(self):
        bar = self._make_bar(42, width=22)
        assert isinstance(bar, str)

    def test_width_respected(self):
        for w in (5, 10, 20, 40):
            bar = self._make_bar(50, width=w)
            assert len(bar) == w, f"Expected bar of width {w}, got {len(bar)}"

    def test_over_100_pct_clamped(self):
        """Values > 100 should produce a full bar (clamped by min(pct, 100))."""
        bar_over = self._make_bar(200, width=10)
        bar_full  = self._make_bar(100, width=10)
        assert bar_over == bar_full

    def test_default_width_is_22(self):
        bar = self._make_bar(100)
        assert len(bar) == 22

    def test_fractional_pct(self):
        """33.3% of width=9 -> int(9 * 0.333) = 3 filled."""
        bar = self._make_bar(33.3, width=9)
        assert len(bar) == 9
        assert bar.startswith("█")


# =============================================================================
# 5. runner.py — argparse via subprocess
# =============================================================================

class TestRunnerArgparse:
    def test_help_flag_exits_zero(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        # argparse always exits 0 for --help
        assert result.returncode == 0

    def test_help_contains_players_flag(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert "--players" in result.stdout

    def test_help_contains_incubation_flag(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert "--incubation" in result.stdout

    def test_help_contains_include_user_flag(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert "--include-user" in result.stdout

    def test_help_contains_games_flag(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert "--games" in result.stdout

    def test_help_contains_skip_reset_flag(self):
        import subprocess
        result = subprocess.run(
            [sys.executable,
             os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
             "--help"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert "--skip-reset" in result.stdout

    def test_runner_module_has_spec(self):
        """runner.py must be discoverable by importlib (module-level code is safe)."""
        spec = importlib.util.spec_from_file_location(
            "runner",
            os.path.join(_REPO_ROOT, "backend/app/scripts/simulation/runner.py"),
        )
        assert spec is not None
        assert spec.loader is not None


# =============================================================================
# 6. Phase module import tests
# =============================================================================

PHASE_FILES = [
    "phase_00_reset",
    "phase_01_users",
    "phase_02_wallets",
    "phase_02b_tickets",
    "phase_03_boosters",
    "phase_04_incubation",
    "phase_05_gashapon",
    "phase_06_boards",
    "phase_06c_crafting",
    "phase_06d_deconstruct",
    "phase_06e_market",
    "phase_07_vip",
    "phase_08_solo",
    "phase_09_multi",
    "phase_10_errors",
]


class TestPhaseImports:
    """
    Verify that each phase module can be imported without raising an exception.
    Because all app.* stubs are installed in sys.modules, no DB connection is made.
    """

    @pytest.mark.parametrize("module_name", PHASE_FILES)
    def test_phase_importable(self, module_name):
        mod = importlib.import_module(module_name)
        assert mod is not None

    @pytest.mark.parametrize("module_name", PHASE_FILES)
    def test_phase_has_callable(self, module_name):
        """Each phase module must expose at least one callable (its phase function)."""
        mod = importlib.import_module(module_name)
        callables = [v for v in vars(mod).values() if callable(v) and not isinstance(v, MagicMock)]
        assert len(callables) > 0, f"{module_name} exposes no callables"

    def test_phase_reset_exposes_phase_reset(self):
        mod = importlib.import_module("phase_00_reset")
        assert hasattr(mod, "phase_reset")
        assert callable(mod.phase_reset)

    def test_phase_reset_exposes_phase_migrations(self):
        mod = importlib.import_module("phase_00_reset")
        assert hasattr(mod, "phase_migrations")
        assert callable(mod.phase_migrations)

    def test_phase_users_exposes_phase_create_users(self):
        mod = importlib.import_module("phase_01_users")
        assert hasattr(mod, "phase_create_users")
        assert callable(mod.phase_create_users)

    def test_phase_wallets_exposes_phase_fund_wallets(self):
        mod = importlib.import_module("phase_02_wallets")
        assert hasattr(mod, "phase_fund_wallets")
        assert callable(mod.phase_fund_wallets)

    def test_phase_boosters_exposes_buy_and_open(self):
        mod = importlib.import_module("phase_03_boosters")
        assert hasattr(mod, "phase_buy_boosters")
        assert hasattr(mod, "phase_open_boosters")

    def test_phase_incubation_exposes_phase_incubation(self):
        mod = importlib.import_module("phase_04_incubation")
        assert hasattr(mod, "phase_incubation")

    def test_phase_solo_exposes_phase_individual_play(self):
        mod = importlib.import_module("phase_08_solo")
        assert hasattr(mod, "phase_individual_play")

    def test_phase_multi_exposes_phase_multiplayer(self):
        mod = importlib.import_module("phase_09_multi")
        assert hasattr(mod, "phase_multiplayer")

    def test_phase_errors_exposes_phase_error_tests(self):
        mod = importlib.import_module("phase_10_errors")
        assert hasattr(mod, "phase_error_tests")


# =============================================================================
# 7. sim_types — RNG source
# =============================================================================

class TestSimRNG:
    def test_rng_is_system_random(self):
        """Critical rule #3: must use SystemRandom, never random.random()."""
        import random
        from sim_types import _rng
        assert isinstance(_rng, random.SystemRandom)

    def test_rng_produces_floats_in_range(self):
        from sim_types import _rng
        for _ in range(20):
            val = _rng.random()
            assert 0.0 <= val < 1.0

    def test_rng_choice_works_on_personality_pool(self):
        from sim_types import _rng
        chosen = _rng.choice(PERSONALITY_POOL)
        assert chosen in PERSONALITY_POOL
