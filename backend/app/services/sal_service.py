"""
sal_service.py — Mecanica del stat SAL (salinity).

SAL es el anti-stat: a mayor valor, peor desempeno del Axolotito.

  - Solo/Bot:   deck bias  -> empuja las cartas del tablero al final del mazo.
  - Multi:      slip       -> carta cantada puede "escaparse" sin marcarse.
  - Multi:      entropia   -> SAL promedio de la sala = nivel de caos.

Todas las funciones son puras y reciben rng inyectado para testabilidad.
"""
import random
from typing import List


def apply_sal_bias(
    deck: List[int],
    board_card_ids: List[int],
    sal: float,
    rng: random.Random,
) -> List[int]:
    """
    Empuja las cartas del tablero en la primera mitad del mazo hacia la segunda,
    con probabilidad sal/200 por carta. Modifica y retorna deck. sal=0 -> sin cambios.
    """
    if sal <= 0:
        return deck
    prob = min(0.5, sal / 200.0)
    half = len(deck) // 2
    board_set = set(board_card_ids)
    for i in range(half):
        if deck[i] in board_set and rng.random() < prob:
            j = rng.randint(half, len(deck) - 1)
            deck[i], deck[j] = deck[j], deck[i]
    return deck


def sal_slip_chance(sal: float) -> float:
    """
    Probabilidad de que una carta cantada se "escape" en multijugador.
    sal/300, maximo 33.33%.
    """
    return max(0.0, min(0.3333, sal / 300.0))


def room_entropy(sal_values: List[float]) -> float:
    """
    Nivel de caos de una sala: SAL promedio / 100, en [0, 1]. Sala vacia -> 0.
    """
    if not sal_values:
        return 0.0
    return min(1.0, (sum(sal_values) / len(sal_values)) / 100.0)
