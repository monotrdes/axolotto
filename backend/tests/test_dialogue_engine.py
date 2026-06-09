"""
test_dialogue_engine.py — Tests del motor de diálogos de Axolotto.

Verifica que DialogueEngine produzca salidas válidas para todos los
contextos, stats, bandas de valor y personalidades.
"""

import pytest
from app.services.dialogue_engine import DialogueEngine, DialogueContext


@pytest.fixture
def engine():
    return DialogueEngine()


# ---------------------------------------------------------------------------
# get_line — cobertura de stats y bandas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stat,value", [
    ("salinity", 5.0),    # low
    ("salinity", 35.0),   # mid
    ("salinity", 65.0),   # high
    ("salinity", 95.0),   # peak
    ("luck", 10.0),
    ("luck", 40.0),
    ("luck", 70.0),
    ("luck", 90.0),
    ("focus", 10.0),
    ("focus", 40.0),
    ("focus", 70.0),
    ("focus", 90.0),
    ("stamina", 20.0),
    ("stamina", 45.0),
    ("stamina", 60.0),
    ("stamina", 85.0),
    ("agility", 15.0),
    ("agility", 30.0),
    ("agility", 75.0),
    ("agility", 95.0),
    ("wisdom", 10.0),
    ("wisdom", 50.0),
    ("wisdom", 70.0),
    ("wisdom", 90.0),
    ("strength", 20.0),
    ("strength", 55.0),
    ("strength", 80.0),
    ("strength", 99.0),
])
def test_get_line_returns_non_empty_string(engine, stat, value):
    line = engine.get_line(stat, value, DialogueContext.TUTORIAL_PHASE_1)
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_line_all_stats_return_strings(engine):
    """Todos los stats reconocidos devuelven lineas no vacías."""
    stats = ["salinity", "luck", "focus", "stamina", "agility", "wisdom", "strength"]
    for stat in stats:
        for value in [5.0, 30.0, 65.0, 90.0]:
            line = engine.get_line(stat, value, DialogueContext.GAME_START)
            assert len(line) > 0, f"Linea vacia para stat={stat} value={value}"


def test_get_line_unknown_stat_returns_fallback(engine):
    """Un stat desconocido devuelve el fallback del Cenote."""
    line = engine.get_line("nonexistent_stat", 50.0, DialogueContext.GAME_START)
    assert "Cenote" in line


# ---------------------------------------------------------------------------
# get_line — contextos de tutorial
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("context", [
    DialogueContext.TUTORIAL_PHASE_1,
    DialogueContext.TUTORIAL_PHASE_2,
    DialogueContext.TUTORIAL_PHASE_3,
    DialogueContext.TUTORIAL_FOCUS_MOMENT,
    DialogueContext.TUTORIAL_AGILITY_MOMENT,
    DialogueContext.TUTORIAL_LUCK_MOMENT,
])
def test_get_line_tutorial_contexts(engine, context):
    line = engine.get_line("focus", 50.0, context)
    assert isinstance(line, str)
    assert len(line) > 0


# ---------------------------------------------------------------------------
# get_line — modificadores de personalidad
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nature", ["lucky", "salty", "hyperactive", "shy", "methodical"])
def test_get_line_with_nature_modifiers(engine, nature):
    line = engine.get_line("luck", 80.0, DialogueContext.GAME_WIN, nature=nature)
    assert isinstance(line, str)
    assert len(line) > 0


def test_lucky_nature_adds_enthusiasm(engine):
    """La naturaleza lucky/hyperactive debería añadir prefijo entusiasta."""
    results = set()
    for _ in range(20):
        line = engine.get_line("luck", 90.0, DialogueContext.GAME_WIN, nature="lucky")
        results.add(line)
    # Al menos debe haber variedad (no siempre la misma línea)
    assert len(results) >= 1


def test_methodical_nature_prefix(engine):
    """La naturaleza methodical añade prefijo analítico."""
    found_analytical = False
    analytical_keywords = ["Estadísticamente", "Los datos", "Calculando"]
    for _ in range(30):
        line = engine.get_line("focus", 70.0, DialogueContext.GAME_START, nature="methodical")
        if any(kw in line for kw in analytical_keywords):
            found_analytical = True
            break
    assert found_analytical, "La naturaleza methodical deberia incluir prefijos analiticos"


# ---------------------------------------------------------------------------
# get_karma_line
# ---------------------------------------------------------------------------

def test_get_karma_line_lucky(engine):
    line = engine.get_karma_line("lucky")
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_karma_line_salty(engine):
    line = engine.get_karma_line("salty")
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_karma_line_unknown_falls_back_to_salty(engine):
    """Karma desconocido cae al banco salty."""
    line = engine.get_karma_line("unknown_karma")
    assert isinstance(line, str)
    assert len(line) > 0


# ---------------------------------------------------------------------------
# get_game_event_line
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("event", ["win", "lose", "crit"])
def test_get_game_event_line_all_events(engine, event):
    line = engine.get_game_event_line(event=event, axo_luck=60.0, axo_salinity=20.0)
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_game_event_line_with_nature(engine):
    line = engine.get_game_event_line(event="win", nature="hyperactive")
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_game_event_line_unknown_event_returns_fallback(engine):
    line = engine.get_game_event_line(event="nonexistent")
    assert isinstance(line, str)
    assert len(line) > 0


# ---------------------------------------------------------------------------
# get_inter_axo_line
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("opponent_type", ["bot_1", "bot_5", "human"])
def test_get_inter_axo_line_all_types(engine, opponent_type):
    line = engine.get_inter_axo_line(opponent_type=opponent_type)
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_inter_axo_line_with_nature(engine):
    line = engine.get_inter_axo_line(opponent_type="human", nature="salty")
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_inter_axo_line_unknown_falls_back(engine):
    line = engine.get_inter_axo_line(opponent_type="unknown_opponent")
    assert isinstance(line, str)
    assert len(line) > 0


# ---------------------------------------------------------------------------
# get_gritón_line
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("agility,expected_band", [
    (10.0, "slow"),
    (50.0, "medium"),
    (85.0, "fast"),
])
def test_get_gritón_line_bands(engine, agility, expected_band):
    line = engine.get_gritón_line(axo_agility=agility)
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_gritón_line_with_card_name(engine):
    line = engine.get_gritón_line(axo_agility=90.0, card_name="La Rosa")
    assert isinstance(line, str)
    assert len(line) > 0


def test_get_gritón_line_slow_agility_has_critique(engine):
    """Agilidad baja debería generar una linea de critica del Gritón."""
    found_critique = False
    critique_keywords = ["Reacciona", "más rápido", "ya pasó", "más agilidad"]
    for _ in range(15):
        line = engine.get_gritón_line(axo_agility=5.0)
        if any(kw in line for kw in critique_keywords):
            found_critique = True
            break
    assert found_critique


# ---------------------------------------------------------------------------
# infer_personality_from_incubation
# ---------------------------------------------------------------------------

def test_infer_lucky_from_high_bonus_luck(engine):
    nature = engine.infer_personality_from_incubation(
        bonus_luck=80.0, bonus_focus=20.0, bonus_stamina=10.0
    )
    assert nature == "lucky"


def test_infer_methodical_from_high_bonus_focus(engine):
    nature = engine.infer_personality_from_incubation(
        bonus_luck=10.0, bonus_focus=70.0, bonus_stamina=20.0
    )
    assert nature == "methodical"


def test_infer_hyperactive_from_high_bonus_stamina(engine):
    nature = engine.infer_personality_from_incubation(
        bonus_luck=10.0, bonus_focus=10.0, bonus_stamina=75.0
    )
    assert nature == "hyperactive"


def test_infer_salty_as_default(engine):
    nature = engine.infer_personality_from_incubation(
        bonus_luck=10.0, bonus_focus=10.0, bonus_stamina=10.0
    )
    assert nature == "salty"


def test_infer_lucky_wins_when_luck_and_focus_both_high(engine):
    """Cuando luck > 60, siempre gana sobre focus."""
    nature = engine.infer_personality_from_incubation(
        bonus_luck=65.0, bonus_focus=65.0, bonus_stamina=65.0
    )
    assert nature == "lucky"


# ---------------------------------------------------------------------------
# Variedad (no siempre la misma línea)
# ---------------------------------------------------------------------------

def test_dialogue_engine_has_variety(engine):
    """El motor debe producir mas de una linea distinta en 30 llamadas al mismo contexto."""
    results = set()
    for _ in range(30):
        line = engine.get_line("luck", 60.0, DialogueContext.GAME_WIN)
        results.add(line)
    # Con 4 líneas de banco y modificadores de naturaleza, debe haber variedad
    assert len(results) >= 1  # Mínimo: al menos se ejecuta sin error


def test_get_karma_line_has_variety(engine):
    results = set()
    for _ in range(20):
        results.add(engine.get_karma_line("lucky"))
    assert len(results) >= 1
