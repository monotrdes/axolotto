# backend/tests/unit/test_imprinting_service.py
"""Tests del servicio de imprinting. Sin DB — lógica pura."""
import pytest
from app.services.imprinting_service import (
    ImprintingGameResult,
    StatDeltas,
    apply_deltas_to_incubation,
    compute_deltas,
    final_stats,
    initial_base_stats,
    required_games_for_rarity,
    _clamp,
)
from app.models.items import Rarity


def test_required_games_common():
    assert required_games_for_rarity(Rarity.COMMON) == 3

def test_required_games_rare():
    assert required_games_for_rarity(Rarity.RARE) == 5

def test_required_games_legendary():
    assert required_games_for_rarity(Rarity.LEGENDARY) == 7

def test_required_games_epic_same_as_legendary():
    assert required_games_for_rarity(Rarity.EPIC) == 7

def test_suerte_jackpot_gives_20():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=True,
        mark_accuracy=0.9, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.luck_delta == 20.0

def test_suerte_win_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.9, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert 8.0 <= d.luck_delta <= 15.0

def test_suerte_loss_negative():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.5, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert -12.0 <= d.luck_delta <= -8.0

def test_ojo_high_accuracy_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.85, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.focus_delta >= 10.0

def test_ojo_low_accuracy_negative():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.40, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.focus_delta <= -8.0

def test_ojo_padrino_energy_bonus():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.85, session_game_count=1,
        padrino_energy_pct=0.85, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.focus_delta >= 15.0

def test_pila_long_session_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=3,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert 10.0 <= d.stamina_delta <= 15.0

def test_pila_single_short_game_negative():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.stamina_delta == -5.0

def test_pila_padrino_high_energy_bonus():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=3,
        padrino_energy_pct=0.85, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.stamina_delta >= 18.0

def test_sal_clean_game_negative():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert -10.0 <= d.salinity_delta <= -6.0

def test_sal_high_padrino_sal_increases():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=60.0,
    )
    d = compute_deltas(result)
    assert 8.0 <= d.salinity_delta <= 12.0

def test_sal_many_misses_adds():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.35, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=25.0,
    )
    d = compute_deltas(result)
    assert d.salinity_delta >= 5.0

class FakeIncubation:
    base_stat_luck = 35.0
    base_stat_focus = 40.0
    base_stat_stamina = 90.0
    base_stat_salinity = 20.0
    bonus_luck = 15.0
    bonus_focus = -5.0
    bonus_stamina = 12.0
    bonus_salinity_adj = -8.0

def test_final_stats_computes_correctly():
    inc = FakeIncubation()
    stats = final_stats(inc)
    assert stats["stat_luck"] == pytest.approx(50.0)
    assert stats["stat_focus"] == pytest.approx(35.0)
    assert stats["stat_stamina"] == 102
    assert stats["stat_salinity"] == pytest.approx(12.0)
    assert stats["stat_agility"] == pytest.approx(35.0)
    assert stats["stat_charisma"] == 0.0
    assert stats["stat_wisdom"] == 0.0
    assert stats["stat_strength"] == 0.0

def test_final_stats_clamped():
    inc = FakeIncubation()
    inc.bonus_luck = 200.0
    stats = final_stats(inc)
    assert stats["stat_luck"] == 100.0

def test_final_stats_stamina_min():
    inc = FakeIncubation()
    inc.bonus_stamina = -200.0
    stats = final_stats(inc)
    assert stats["stat_stamina"] == 50

def test_clamp_within():
    assert _clamp(50.0, 0.0, 100.0) == 50.0

def test_clamp_below():
    assert _clamp(-5.0, 0.0, 100.0) == 0.0

def test_clamp_above():
    assert _clamp(150.0, 0.0, 100.0) == 100.0


# ---------------------------------------------------------------------------
# initial_base_stats
# ---------------------------------------------------------------------------

def test_initial_base_stats_returns_four_keys():
    stats = initial_base_stats()
    assert set(stats.keys()) == {
        "base_stat_luck", "base_stat_focus", "base_stat_stamina", "base_stat_salinity"
    }

def test_initial_base_stats_luck_in_range():
    for _ in range(20):
        stats = initial_base_stats()
        assert 20.0 <= stats["base_stat_luck"] <= 50.0

def test_initial_base_stats_focus_in_range():
    for _ in range(20):
        stats = initial_base_stats()
        assert 25.0 <= stats["base_stat_focus"] <= 55.0

def test_initial_base_stats_stamina_in_range():
    for _ in range(20):
        stats = initial_base_stats()
        assert 70.0 <= stats["base_stat_stamina"] <= 110.0

def test_initial_base_stats_salinity_in_range():
    for _ in range(20):
        stats = initial_base_stats()
        assert 10.0 <= stats["base_stat_salinity"] <= 30.0


# ---------------------------------------------------------------------------
# apply_deltas_to_incubation
# ---------------------------------------------------------------------------

import types

def _make_incubation(**kwargs):
    """Helper: creates a simple namespace simulating WebitoIncubation fields."""
    defaults = dict(
        bonus_luck=0.0, bonus_focus=0.0, bonus_stamina=0.0,
        bonus_salinity_adj=0.0, imprinting_games_played=0,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)

def test_apply_deltas_increments_games_played():
    inc = _make_incubation()
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=5.0))
    assert inc.imprinting_games_played == 1

def test_apply_deltas_accumulates_luck():
    inc = _make_incubation(bonus_luck=10.0)
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=8.0))
    assert inc.bonus_luck == pytest.approx(18.0)

def test_apply_deltas_clamps_luck_max():
    inc = _make_incubation(bonus_luck=45.0)
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=20.0))
    assert inc.bonus_luck == 50.0  # clamped at +50

def test_apply_deltas_clamps_luck_min():
    inc = _make_incubation(bonus_luck=-40.0)
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=-20.0))
    assert inc.bonus_luck == -50.0  # clamped at -50

def test_apply_deltas_clamps_stamina_max():
    inc = _make_incubation(bonus_stamina=55.0)
    apply_deltas_to_incubation(inc, StatDeltas(stamina_delta=15.0))
    assert inc.bonus_stamina == 60.0  # clamped at +60

def test_apply_deltas_accumulates_salinity_adj():
    inc = _make_incubation(bonus_salinity_adj=-5.0)
    apply_deltas_to_incubation(inc, StatDeltas(salinity_delta=-8.0))
    assert inc.bonus_salinity_adj == pytest.approx(-13.0)

def test_apply_deltas_multiple_calls_accumulate():
    inc = _make_incubation()
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=10.0))
    apply_deltas_to_incubation(inc, StatDeltas(luck_delta=10.0))
    assert inc.bonus_luck == pytest.approx(20.0)
    assert inc.imprinting_games_played == 2


# ---------------------------------------------------------------------------
# New Imprinting System Tests (Inheritance, Natures, Hatch Rewards, Limits)
# ---------------------------------------------------------------------------
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.axolotito import Axolotito
from app.models.items import WebitoIncubation, ItemType, Rarity
from app.api.v1.endpoints.incubation import _perform_hatch, start_imprinting, StartImprintingPayload
from conftest import make_user, make_item

def test_base_stat_inheritance_low_level():
    padrino_low = Axolotito(
        user_id="user_test",
        level=10,
        stat_luck=50.0,
        stat_focus=40.0,
        stat_stamina=100,
        stat_salinity=10.0,
    )
    # Factor is 0.10 for level <= 20
    stats = initial_base_stats(padrino_low)
    # base luck is random in (20.0, 50.0) -> luck with padrino is luck_base + 50.0 * 0.10 = luck_base + 5.0
    assert 25.0 <= stats["base_stat_luck"] <= 55.0
    assert 29.0 <= stats["base_stat_focus"] <= 59.0
    assert 80.0 <= stats["base_stat_stamina"] <= 120.0
    assert 11.0 <= stats["base_stat_salinity"] <= 31.0

def test_base_stat_inheritance_high_level():
    padrino_high = Axolotito(
        user_id="user_test",
        level=25,
        stat_luck=50.0,
        stat_focus=40.0,
        stat_stamina=100,
        stat_salinity=10.0,
    )
    # Factor is 0.15 for level > 20
    stats = initial_base_stats(padrino_high)
    assert 27.5 <= stats["base_stat_luck"] <= 57.5
    assert 31.0 <= stats["base_stat_focus"] <= 61.0
    assert 85.0 <= stats["base_stat_stamina"] <= 125.0
    assert 11.5 <= stats["base_stat_salinity"] <= 31.5

def test_nature_archetype_modifiers_lucky():
    # Won is True, had_jackpot_bonus is True -> luck_delta = 20.0
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=True,
        mark_accuracy=0.9, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    # Lucky nature multiplies positive luck_delta by 1.25 -> 20.0 * 1.25 = 25.0
    d = compute_deltas(result, padrino_nature="lucky")
    assert d.luck_delta == 25.0

    # Lucky nature does not affect negative luck_delta
    result_loss = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.5, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d_loss = compute_deltas(result_loss, padrino_nature="lucky")
    assert -12.0 <= d_loss.luck_delta <= -8.0

def test_nature_archetype_modifiers_methodical():
    import app.services.imprinting_service as imp_serv
    orig_uniform = imp_serv._rng.uniform
    imp_serv._rng.uniform = lambda a, b: 10.0
    try:
        # high mark_accuracy -> focus_delta = 10.0
        result = ImprintingGameResult(
            won=True, had_jackpot_bonus=False,
            mark_accuracy=0.9, session_game_count=1,
            padrino_energy_pct=0.5, padrino_sal=10.0,
        )
        d = compute_deltas(result, padrino_nature="methodical")
        # focus_delta should be 10.0 * 1.25 = 12.5
        assert d.focus_delta == 12.5
    finally:
        imp_serv._rng.uniform = orig_uniform

def test_nature_archetype_modifiers_hyperactive():
    import app.services.imprinting_service as imp_serv
    orig_uniform = imp_serv._rng.uniform
    imp_serv._rng.uniform = lambda a, b: 10.0
    try:
        # session_game_count >= 3 -> stamina_delta = 10.0
        result = ImprintingGameResult(
            won=True, had_jackpot_bonus=False,
            mark_accuracy=0.7, session_game_count=3,
            padrino_energy_pct=0.5, padrino_sal=10.0,
        )
        d = compute_deltas(result, padrino_nature="hyperactive")
        # stamina_delta should be 10.0 * 1.25 = 12.5
        assert d.stamina_delta == 12.5
    finally:
        imp_serv._rng.uniform = orig_uniform

def test_nature_archetype_modifiers_glutton():
    import app.services.imprinting_service as imp_serv
    orig_uniform = imp_serv._rng.uniform
    imp_serv._rng.uniform = lambda a, b: 10.0
    try:
        # Won is False -> negative deltas reduced by 20% (multiplied by 0.80)
        # luck_delta = -10.0
        # focus_delta = -10.0 (if mark_accuracy <= 0.50)
        # stamina_delta = -5.0 (if session_game_count == 1)
        # salinity_delta = -10.0 (if padrino_sal < 20.0)
        result = ImprintingGameResult(
            won=False, had_jackpot_bonus=False,
            mark_accuracy=0.4, session_game_count=1,
            padrino_energy_pct=0.5, padrino_sal=10.0,
        )
        d = compute_deltas(result, padrino_nature="glutton")
        # luck_delta = -10 * 0.8 = -8
        # focus_delta = -10 * 0.8 = -8
        # stamina_delta = -5 * 0.8 = -4
        # salinity_delta = -10 * 0.8 = -8
        assert d.luck_delta == -8.0
        assert d.focus_delta == -8.0
        assert d.stamina_delta == -4.0
        assert d.salinity_delta == -8.0
    finally:
        imp_serv._rng.uniform = orig_uniform

def test_permanent_stats_boost_on_hatch(session):
    user = make_user(session, privy_did="did:privy:padrino_test_hatch")
    padrino = Axolotito(
        user_id=user.privy_did,
        name="Padrino Test",
        level=1,
        experience=50,
        stat_luck=10.0,
        stat_focus=10.0,
        stat_stamina=100,
        stat_salinity=10.0,
        mentorship_count=0
    )
    session.add(padrino)
    session.commit()
    session.refresh(padrino)

    egg = make_item(session, name="Huevo Comun", item_type=ItemType.EGG)
    
    # Create WebitoIncubation
    incubation = WebitoIncubation(
        user_id=user.privy_did,
        item_id=egg.id,
        fecha_eclosion_estimada=datetime.utcnow() - timedelta(minutes=1),
        imprinting_padrino_id=padrino.id,
        imprinting_complete=True,
        bonus_luck=5.0,
        bonus_focus=20.0, # Focus is the highest bonus
        bonus_stamina=10.0,
        bonus_salinity_adj=-2.0
    )
    session.add(incubation)
    session.commit()
    session.refresh(incubation)

    # Hatch egg
    res = _perform_hatch(incubation, user, session, is_astral=False)
    session.commit()
    session.refresh(padrino)

    # Highest delta was focus (20.0), so padrino.stat_focus should be 12.0 (+2)
    assert padrino.stat_focus == 12.0
    assert padrino.mentorship_count == 1
    # XP should increase by +150 (50 + 150 = 200). Since level=1, threshold is 100 XP.
    # Level up: level becomes 2, remaining XP: 200 - 100 = 100.
    # Level 2 threshold is 200 XP. So 100 XP remains, level is 2.
    assert padrino.level == 2
    assert padrino.experience == 100

    # Baby's tutored_by_id should be padrino.id
    baby_id = res["axolotito"]["id"]
    baby = session.get(Axolotito, baby_id)
    assert baby.tutored_by_id == padrino.id

def test_mentorship_limit_of_3(session):
    user = make_user(session, privy_did="did:privy:padrino_test_limit")
    padrino = Axolotito(
        user_id=user.privy_did,
        name="Padrino Limit",
        level=1,
        experience=50,
        stat_luck=10.0,
        stat_focus=10.0,
        stat_stamina=100,
        stat_salinity=10.0,
        mentorship_count=3 # Already 3
    )
    session.add(padrino)
    session.commit()
    session.refresh(padrino)

    egg = make_item(session, name="Huevo Raro", item_type=ItemType.EGG)
    incubation = WebitoIncubation(
        user_id=user.privy_did,
        item_id=egg.id,
        fecha_eclosion_estimada=datetime.utcnow() + timedelta(days=1),
    )
    session.add(incubation)
    session.commit()
    session.refresh(incubation)

    payload = StartImprintingPayload(
        incubation_id=incubation.id,
        padrino_axolotito_id=padrino.id
    )

    with pytest.raises(HTTPException) as exc_info:
        start_imprinting(payload, session, verified_user_id=user.privy_did)
    
    assert exc_info.value.status_code == 400
    assert "ya ha apadrinado 3 huevos" in exc_info.value.detail
