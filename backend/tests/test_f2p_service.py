"""
test_f2p_service.py — Tests para F2PService.

Cubre:
  - egg_reaction_stage por tramo de fragmentos
  - get_dream_bubble (devuelve string no vacío en etapas 1-5)
  - under_daily_cap
  - watch_game_reward (ganó / no ganó)
"""

import pytest
from app.services.f2p_service import F2PService


@pytest.fixture
def svc() -> F2PService:
    return F2PService()


# ---------------------------------------------------------------------------
# egg_reaction_stage
# ---------------------------------------------------------------------------

class TestEggReactionStage:
    @pytest.mark.parametrize("fragments,expected_stage", [
        (0,   0),
        (1,   0),
        (19,  0),
        (20,  1),
        (39,  1),
        (40,  2),
        (59,  2),
        (60,  3),
        (79,  3),
        (80,  4),
        (99,  4),
        (100, 5),
        (150, 5),
        (999, 5),
    ])
    def test_stage_boundaries(self, svc, fragments, expected_stage):
        assert svc.egg_reaction_stage(fragments) == expected_stage, (
            f"fragments={fragments} → expected stage {expected_stage}"
        )


# ---------------------------------------------------------------------------
# get_dream_bubble
# ---------------------------------------------------------------------------

class TestGetDreamBubble:
    def test_stage_0_returns_empty_string(self, svc):
        # Etapa 0: sin burbuja
        for frags in [0, 10, 19]:
            bubble = svc.get_dream_bubble(frags)
            assert bubble == "", f"fragments={frags} debe devolver ''"

    def test_stage_1_returns_nonempty_string(self, svc):
        bubble = svc.get_dream_bubble(20)
        assert isinstance(bubble, str) and len(bubble) > 0

    def test_stage_2_returns_nonempty_string(self, svc):
        bubble = svc.get_dream_bubble(40)
        assert isinstance(bubble, str) and len(bubble) > 0

    def test_stage_3_returns_nonempty_string(self, svc):
        bubble = svc.get_dream_bubble(60)
        assert isinstance(bubble, str) and len(bubble) > 0

    def test_stage_4_returns_nonempty_string(self, svc):
        bubble = svc.get_dream_bubble(80)
        assert isinstance(bubble, str) and len(bubble) > 0

    def test_stage_5_returns_nonempty_string(self, svc):
        bubble = svc.get_dream_bubble(100)
        assert isinstance(bubble, str) and len(bubble) > 0

    def test_stage_5_phrases_are_specific(self, svc):
        # Las frases de etapa 5 son fijas y conocidas
        expected = {"¡Despierto pronto!", "¡El Cenote me está llamando!"}
        # Muestrear suficientes veces para que salgan ambas (probabilístico)
        results = {svc.get_dream_bubble(100) for _ in range(50)}
        assert results.issubset(expected)
        assert len(results) >= 1  # al menos una salió


# ---------------------------------------------------------------------------
# under_daily_cap
# ---------------------------------------------------------------------------

class TestUnderDailyCap:
    def test_zero_earned_is_under_cap(self, svc):
        assert svc.under_daily_cap(0.0) is True

    def test_just_below_cap_is_under(self, svc):
        assert svc.under_daily_cap(9.99) is True

    def test_exactly_at_cap_is_not_under(self, svc):
        assert svc.under_daily_cap(10.0) is False

    def test_above_cap_is_not_under(self, svc):
        assert svc.under_daily_cap(15.0) is False


# ---------------------------------------------------------------------------
# watch_game_reward
# ---------------------------------------------------------------------------

class TestWatchGameReward:
    def test_win_gives_3_gal_and_2_frags(self, svc):
        reward = svc.watch_game_reward(won=True)
        assert reward["gal"] == 3.0
        assert reward["fragments"] == 2

    def test_loss_gives_01_gal_and_1_frag(self, svc):
        reward = svc.watch_game_reward(won=False)
        assert abs(reward["gal"] - 0.1) < 1e-9
        assert reward["fragments"] == 1

    def test_reward_keys_present(self, svc):
        for won in [True, False]:
            reward = svc.watch_game_reward(won=won)
            assert "gal" in reward
            assert "fragments" in reward

    def test_gal_is_positive(self, svc):
        for won in [True, False]:
            assert svc.watch_game_reward(won=won)["gal"] > 0

    def test_fragments_is_positive_int(self, svc):
        for won in [True, False]:
            frags = svc.watch_game_reward(won=won)["fragments"]
            assert isinstance(frags, int) and frags > 0
