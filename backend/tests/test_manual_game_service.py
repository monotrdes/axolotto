"""
test_manual_game_service.py — Tests para ManualGameService.

Cubre los casos clave de los parámetros de entorno en modo manual:
  - Límites de focus (highlight_window_ms)
  - Límites de agility (griton_delay_ms)
  - Límites de stamina (visual_hints)
  - Probabilidad de crítico según luck y marked_in_window
  - Crit window = 30% de highlight_window_ms
  - Interpolación de valores intermedios
"""

import pytest
from app.services.manual_game_service import ManualGameService, ManualEnvParams


@pytest.fixture
def svc() -> ManualGameService:
    return ManualGameService()


# ---------------------------------------------------------------------------
# highlight_window_ms — stat_focus
# ---------------------------------------------------------------------------

class TestFocus:
    def test_focus_0_yields_min_window(self, svc):
        params = svc.get_env_params(focus=0, agility=50, stamina=100)
        assert params.highlight_window_ms == 1000

    def test_focus_100_yields_max_window(self, svc):
        params = svc.get_env_params(focus=100, agility=50, stamina=100)
        assert params.highlight_window_ms == 4000

    def test_focus_50_midpoint(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=100)
        # Esperamos 2500 ms (punto medio entre 1000 y 4000)
        assert params.highlight_window_ms == 2500

    def test_focus_clamped_below_zero(self, svc):
        params = svc.get_env_params(focus=-10, agility=50, stamina=100)
        assert params.highlight_window_ms == 1000

    def test_focus_clamped_above_max(self, svc):
        params = svc.get_env_params(focus=150, agility=50, stamina=100)
        assert params.highlight_window_ms == 4000


# ---------------------------------------------------------------------------
# griton_delay_ms — stat_agility
# ---------------------------------------------------------------------------

class TestAgility:
    def test_agility_0_yields_min_delay(self, svc):
        params = svc.get_env_params(focus=50, agility=0, stamina=100)
        assert params.griton_delay_ms == 800

    def test_agility_100_yields_max_delay(self, svc):
        params = svc.get_env_params(focus=50, agility=100, stamina=100)
        assert params.griton_delay_ms == 2500

    def test_agility_50_midpoint(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=100)
        # Punto medio entre 800 y 2500 = 1650 ms
        assert params.griton_delay_ms == 1650

    def test_agility_clamped_below_zero(self, svc):
        params = svc.get_env_params(focus=50, agility=-5, stamina=100)
        assert params.griton_delay_ms == 800

    def test_agility_clamped_above_max(self, svc):
        params = svc.get_env_params(focus=50, agility=200, stamina=100)
        assert params.griton_delay_ms == 2500


# ---------------------------------------------------------------------------
# visual_hints — stat_stamina
# ---------------------------------------------------------------------------

class TestStamina:
    def test_stamina_50_yields_1_hint(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=50)
        assert params.visual_hints == 1

    def test_stamina_200_yields_8_hints(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=200)
        assert params.visual_hints == 8

    def test_stamina_125_midpoint(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=125)
        # Punto medio entre 1 y 8 = 4.5 → round → 4 o 5 dependiendo del round
        # _lerp(125, 50, 200, 1, 8) = 1 + (75/150)*7 = 1 + 3.5 = 4.5 → round → 4
        assert params.visual_hints in (4, 5)

    def test_stamina_clamped_below_min(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=0)
        assert params.visual_hints == 1

    def test_stamina_clamped_above_max(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=300)
        assert params.visual_hints == 8


# ---------------------------------------------------------------------------
# crit_window_ms — 30% de highlight_window_ms
# ---------------------------------------------------------------------------

class TestCritWindow:
    def test_crit_window_is_30_pct_of_highlight_window(self, svc):
        params = svc.get_env_params(focus=0, agility=50, stamina=100)
        # highlight_window = 1000 ms → crit_window = 300 ms
        assert params.crit_window_ms == 300

    def test_crit_window_at_max_focus(self, svc):
        params = svc.get_env_params(focus=100, agility=50, stamina=100)
        # highlight_window = 4000 ms → crit_window = 1200 ms
        assert params.crit_window_ms == 1200


# ---------------------------------------------------------------------------
# crit_probability — stat_luck
# ---------------------------------------------------------------------------

class TestCritProbability:
    def test_luck_0_in_window_returns_min_prob(self, svc):
        prob = svc.crit_probability(luck=0, marked_in_window=True)
        assert abs(prob - 0.03) < 1e-9

    def test_luck_100_in_window_returns_max_prob(self, svc):
        prob = svc.crit_probability(luck=100, marked_in_window=True)
        assert abs(prob - 0.50) < 1e-9

    def test_any_luck_not_in_window_returns_zero(self, svc):
        for luck in [0, 25, 50, 75, 100]:
            prob = svc.crit_probability(luck=luck, marked_in_window=False)
            assert prob == 0.0, f"Esperado 0.0 para luck={luck} fuera de ventana"

    def test_luck_50_midpoint_in_window(self, svc):
        prob = svc.crit_probability(luck=50, marked_in_window=True)
        # _lerp(50, 0, 100, 0.03, 0.50) = 0.03 + 0.5 * (0.50 - 0.03) = 0.03 + 0.235 = 0.265
        assert abs(prob - 0.265) < 1e-9

    def test_luck_clamped_below_zero(self, svc):
        prob = svc.crit_probability(luck=-10, marked_in_window=True)
        assert abs(prob - 0.03) < 1e-9

    def test_luck_clamped_above_max(self, svc):
        prob = svc.crit_probability(luck=200, marked_in_window=True)
        assert abs(prob - 0.50) < 1e-9


# ---------------------------------------------------------------------------
# to_dict — serialización
# ---------------------------------------------------------------------------

class TestToDict:
    def test_to_dict_returns_all_keys(self, svc):
        params = svc.get_env_params(focus=50, agility=50, stamina=100)
        d = svc.to_dict(params)
        assert set(d.keys()) == {
            "highlight_window_ms",
            "griton_delay_ms",
            "visual_hints",
            "crit_window_ms",
        }

    def test_to_dict_values_match_dataclass(self, svc):
        params = svc.get_env_params(focus=0, agility=0, stamina=50)
        d = svc.to_dict(params)
        assert d["highlight_window_ms"] == params.highlight_window_ms
        assert d["griton_delay_ms"] == params.griton_delay_ms
        assert d["visual_hints"] == params.visual_hints
        assert d["crit_window_ms"] == params.crit_window_ms
