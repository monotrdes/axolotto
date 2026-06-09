"""
imprinting_service.py — Logica de imprinting para Webitos.

El ADN incompleto del Webito se moldea por las partidas del padrino.
Los deltas se acumulan en WebitoIncubation.bonus_* fields.
Al completar N partidas (segun rareza), el ADN se sella y eclosa.

Puro: sin imports de DB ni FastAPI para facilitar testing.
"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.axolotito import Axolotito

from app.models.items import Rarity

_rng = random.SystemRandom()

_REQUIRED_GAMES: dict[str, int] = {
    "common":    3,
    "rare":      5,
    "epic":      7,
    "legendary": 7,
}

_BASE_RANGES: dict[str, tuple[float, float]] = {
    "luck":     (20.0, 50.0),
    "focus":    (25.0, 55.0),
    "stamina":  (70.0, 110.0),
    "salinity": (10.0, 30.0),
}


@dataclass
class ImprintingGameResult:
    """Datos de una partida que alimentan el imprinting del Webito."""
    won: bool
    had_jackpot_bonus: bool
    mark_accuracy: float          # 0.0-1.0
    session_game_count: int       # imprinting_games_played + 1
    padrino_energy_pct: float     # energy_current / stat_stamina (0.0-1.0)
    padrino_sal: float            # stat_salinity del padrino (0-100)


@dataclass
class StatDeltas:
    """Cambios a aplicar a los stats del Webito tras una partida."""
    luck_delta: float = 0.0
    focus_delta: float = 0.0
    stamina_delta: float = 0.0
    salinity_delta: float = 0.0


def required_games_for_rarity(rarity: Rarity) -> int:
    """Partidas de imprinting requeridas segun rareza del huevo."""
    return _REQUIRED_GAMES.get(rarity.value, 3)


def initial_base_stats(padrino: Optional[Axolotito] = None) -> dict[str, float]:
    """
    Genera los stats base iniciales del Webito al iniciar el imprinting.
    Llamar UNA SOLA VEZ y almacenar en WebitoIncubation.base_stat_*.
    """
    luck = _rng.uniform(*_BASE_RANGES["luck"])
    focus = _rng.uniform(*_BASE_RANGES["focus"])
    stamina = _rng.uniform(*_BASE_RANGES["stamina"])
    salinity = _rng.uniform(*_BASE_RANGES["salinity"])

    if padrino is not None:
        factor = 0.15 if padrino.level > 20 else 0.10
        luck += padrino.stat_luck * factor
        focus += padrino.stat_focus * factor
        stamina += padrino.stat_stamina * factor
        salinity += padrino.stat_salinity * factor

    return {
        "base_stat_luck":     luck,
        "base_stat_focus":    focus,
        "base_stat_stamina":  stamina,
        "base_stat_salinity": salinity,
    }


def compute_deltas(result: ImprintingGameResult, padrino_nature: Optional[str] = None) -> StatDeltas:
    """
    Calcula los deltas de stats para el Webito a partir del resultado de una partida.
    Puro, sin efectos secundarios - testeable en aislamiento.
    """
    d = StatDeltas()

    # --- SUERTE ---
    if result.had_jackpot_bonus:
        d.luck_delta = 20.0
    elif result.won:
        d.luck_delta = _rng.uniform(8.0, 15.0)
    else:
        d.luck_delta = -_rng.uniform(8.0, 12.0)

    # --- OJO (Focus) ---
    if result.mark_accuracy >= 0.80:
        d.focus_delta = _rng.uniform(10.0, 18.0)
    elif result.mark_accuracy <= 0.50:
        d.focus_delta = -_rng.uniform(8.0, 14.0)
    if result.padrino_energy_pct > 0.80:
        d.focus_delta += 5.0

    # --- PILA (Stamina) ---
    if result.session_game_count >= 3:
        d.stamina_delta = _rng.uniform(10.0, 15.0)
    elif result.session_game_count == 1:
        d.stamina_delta = -5.0
    if result.padrino_energy_pct > 0.80:
        d.stamina_delta += 8.0

    # --- SAL (Salinity) ---
    if result.padrino_sal < 20.0:
        d.salinity_delta = -_rng.uniform(6.0, 10.0)
    elif result.padrino_sal > 50.0:
        d.salinity_delta = _rng.uniform(8.0, 12.0)
    if result.mark_accuracy < 0.40:
        d.salinity_delta += 5.0

    # Apply nature modifiers
    if padrino_nature:
        nature_lower = padrino_nature.lower()
        if nature_lower == "lucky" and d.luck_delta > 0:
            d.luck_delta *= 1.25
        elif nature_lower == "methodical" and d.focus_delta > 0:
            d.focus_delta *= 1.25
        elif nature_lower == "hyperactive" and d.stamina_delta > 0:
            d.stamina_delta *= 1.25
        elif nature_lower == "glutton" and not result.won:
            if d.luck_delta < 0:
                d.luck_delta *= 0.80
            if d.focus_delta < 0:
                d.focus_delta *= 0.80
            if d.stamina_delta < 0:
                d.stamina_delta *= 0.80
            if d.salinity_delta < 0:
                d.salinity_delta *= 0.80

    return d


def apply_deltas_to_incubation(incubation, deltas: StatDeltas) -> None:
    """
    Aplica los deltas al WebitoIncubation en memoria.
    El caller hace session.add(incubation) y session.commit().
    """
    incubation.bonus_luck         = _clamp(incubation.bonus_luck + deltas.luck_delta,         -50.0, 50.0)
    incubation.bonus_focus        = _clamp(incubation.bonus_focus + deltas.focus_delta,        -50.0, 50.0)
    incubation.bonus_stamina      = _clamp(incubation.bonus_stamina + deltas.stamina_delta,    -60.0, 60.0)
    incubation.bonus_salinity_adj = _clamp(
        incubation.bonus_salinity_adj + deltas.salinity_delta, -50.0, 50.0
    )
    incubation.imprinting_games_played += 1


def final_stats(incubation) -> dict:
    """
    Calcula los stats finales del Axolotito al eclosionar.
    base_stat_* + bonus_* clampeados a rangos validos.

    En el tutorial base_stat_* = 0 y los bonus_* (sembrados desde user_id) son el
    valor completo del stat. En huevos reales la ruta de imprinting setea base_stat_*
    antes de eclosionar.
    """
    base_luck     = incubation.base_stat_luck
    base_focus    = incubation.base_stat_focus
    base_stamina  = incubation.base_stat_stamina
    base_salinity = incubation.base_stat_salinity

    luck     = _clamp(base_luck + incubation.bonus_luck,                   0.0, 100.0)
    focus    = _clamp(base_focus + incubation.bonus_focus,                 0.0, 100.0)
    stamina  = int(_clamp(base_stamina + incubation.bonus_stamina,         50.0, 200.0))
    salinity = _clamp(base_salinity + incubation.bonus_salinity_adj,       0.0, 100.0)
    return {
        "stat_luck":     luck,
        "stat_focus":    focus,
        "stat_stamina":  stamina,
        "stat_salinity": salinity,
        "stat_agility":  focus,    # OJO = Focus = Agility per 4-stats design
        "stat_charisma": 0.0,
        "stat_wisdom":   0.0,
        "stat_strength": 0.0,
    }


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
