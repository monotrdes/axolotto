"""
game_logic.py — Pure utility functions for Lotería game logic.

No database dependencies. All functions are deterministic or use injected SystemRandom.
"""
from __future__ import annotations
import random
from typing import Dict, Any

from app.core.prices import MULTIPLAYER_ROOMS

_rng = random.SystemRandom()

# Champion: max payout = win_prize * 1.65 (luck +10%, streak +50% → combined x1.65)
# Basis points: 165 = x1.65. Division by 100 after multiplication.
MAX_WIN_MULTIPLIER: float = 1.65  # legacy float — usar MAX_WIN_MULTIPLIER_BPS
MAX_WIN_MULTIPLIER_BPS: int = 165  # 1.65x en basis points (VULN-06)

# ---------------------------------------------------------------------------
# ROOM_CONFIG — centralised balance constants.
# Changing a number here touches every calculation automatically.
#
# bot_focus: 0–100. Translates to bot miss_chance via the same formula as
#   the player:  miss = max(0, min(0.3, (100 - focus) * 0.003))
#   focus=40  → 18 % miss  (Rookie bots: careless)
#   focus=80  →  6 % miss  (Champion bots: sharp but not perfect)
#
# Simulation results (50 000 games, scripts/sim_cpu_balance.py):
#
#   ROOKIE (1 bot, focus=40, fee=10, prize=16, consolation=2):
#     focus= 0 → win 35.9 %  house edge +29.7 % ✅
#     focus=30 → win 47.7 %  house edge +13.2 % ✅
#     focus=50 → win 55.4 %  house edge  +2.4 % ✅  ← typical player
#     focus=70 → win 62.1 %  house edge  -6.9 % ⚠️  (veteran advantage)
#     focus=100→ win 71.0 %  house edge -19.4 % ⚠️  (expert reward)
#
#   CHAMPION (5 bots, focus=80, fee=50, prize=290, consolation=5):
#     focus= 0 → win  6.5 %  house edge +53.1 % ✅
#     focus=30 → win 10.0 %  house edge +33.1 % ✅
#     focus=50 → win 12.9 %  house edge +16.6 % ✅  ← typical player
#     focus=70 → win 16.0 %  house edge  -1.4 % ⚠️  (veteran advantage)
#     focus=100→ win 21.8 %  house edge -34.2 % ⚠️  (expert reward)
#
# Design intent:
#   Negative house-edge at high focus IS intentional — it rewards axolotito
#   progression investment (AXG spent on stat upgrades). Exploitation is
#   capped by the energy system (10 games per sleep cycle) and the low
#   absolute COR values at Rookie level.
# ---------------------------------------------------------------------------
ROOM_CONFIG: Dict[str, Any] = {
    "rookie_pool": {
        "title":            "Charco de Novatos",
        "difficulty_label": "Fácil",
        "bot_count":        1,
        "bot_focus":        40,    # miss ≈ 18 %
        "fee":              MULTIPLAYER_ROOMS["rookie_pool"]["fee"],
        "prize":            MULTIPLAYER_ROOMS["rookie_pool"]["prize"],
        "consolation":      MULTIPLAYER_ROOMS["rookie_pool"]["consolation"],
        "win_xp_board":     MULTIPLAYER_ROOMS["rookie_pool"]["win_xp_board"],
        "win_xp_axo":       MULTIPLAYER_ROOMS["rookie_pool"]["win_xp_axo"],
        "loss_xp_board":    MULTIPLAYER_ROOMS["rookie_pool"]["loss_xp_board"],
        "loss_xp_axo":      MULTIPLAYER_ROOMS["rookie_pool"]["loss_xp_axo"],
        "win_patterns":     ["line", "cuadrito"],
    },
    "champion_abyss": {
        "title":            "Fosa del Campeón",
        "difficulty_label": "Difícil",
        "bot_count":        5,
        "bot_focus":        80,    # miss ≈ 6 %
        "fee":              MULTIPLAYER_ROOMS["champion_abyss"]["fee"],
        "prize":            MULTIPLAYER_ROOMS["champion_abyss"]["prize"],
        "consolation":      MULTIPLAYER_ROOMS["champion_abyss"]["consolation"],
        "win_xp_board":     MULTIPLAYER_ROOMS["champion_abyss"]["win_xp_board"],
        "win_xp_axo":       MULTIPLAYER_ROOMS["champion_abyss"]["win_xp_axo"],
        "loss_xp_board":    MULTIPLAYER_ROOMS["champion_abyss"]["loss_xp_board"],
        "loss_xp_axo":      MULTIPLAYER_ROOMS["champion_abyss"]["loss_xp_axo"],
        "win_patterns":     ["line", "cuadrito", "pocito", "esquinas"],
    },
    # Legacy keys para compatibilidad con código que aún use "rookie"/"champion"
    "rookie": {
        "title":            "Charco de Novatos",
        "difficulty_label": "Fácil",
        "bot_count":        1,
        "bot_focus":        40,
        "fee":              MULTIPLAYER_ROOMS["rookie"]["fee"],
        "prize":            MULTIPLAYER_ROOMS["rookie"]["prize"],
        "consolation":      MULTIPLAYER_ROOMS["rookie"]["consolation"],
        "win_xp_board":     MULTIPLAYER_ROOMS["rookie"]["win_xp_board"],
        "win_xp_axo":       MULTIPLAYER_ROOMS["rookie"]["win_xp_axo"],
        "loss_xp_board":    MULTIPLAYER_ROOMS["rookie"]["loss_xp_board"],
        "loss_xp_axo":      MULTIPLAYER_ROOMS["rookie"]["loss_xp_axo"],
        "win_patterns":     ["line", "cuadrito"],
    },
    "champion": {
        "title":            "Fosa del Campeón",
        "difficulty_label": "Difícil",
        "bot_count":        5,
        "bot_focus":        80,
        "fee":              MULTIPLAYER_ROOMS["champion"]["fee"],
        "prize":            MULTIPLAYER_ROOMS["champion"]["prize"],
        "consolation":      MULTIPLAYER_ROOMS["champion"]["consolation"],
        "win_xp_board":     MULTIPLAYER_ROOMS["champion"]["win_xp_board"],
        "win_xp_axo":       MULTIPLAYER_ROOMS["champion"]["win_xp_axo"],
        "loss_xp_board":    MULTIPLAYER_ROOMS["champion"]["loss_xp_board"],
        "loss_xp_axo":      MULTIPLAYER_ROOMS["champion"]["loss_xp_axo"],
        "win_patterns":     ["line", "cuadrito", "pocito", "esquinas"],
    },
}

# --- WINNING LINES DEFINITIONS (4x4 Grid indices 0 to 15) ---
WINNING_LINES = [
    # Rows
    {0, 1, 2, 3}, {4, 5, 6, 7}, {8, 9, 10, 11}, {12, 13, 14, 15},
    # Columns
    {0, 4, 8, 12}, {1, 5, 9, 13}, {2, 6, 10, 14}, {3, 7, 11, 15},
    # Diagonals
    {0, 5, 10, 15}, {3, 6, 9, 12},
]


def check_loterica_line(marked_indices: set) -> bool:
    """Returns True if any winning line is fully marked."""
    for line in WINNING_LINES:
        if line.issubset(marked_indices):
            return True
    return False


def get_winning_line(marked_indices: set) -> set | None:
    """Returns the first completed winning line set, or None."""
    for line in WINNING_LINES:
        if line.issubset(marked_indices):
            return line
    return None


def _lucky_save(axo_luck: float, already_used: bool) -> bool:
    """
    Returns True if the Lucky Save activates.
    Triggers at most once per game (already_used guard).
    Chance = (axo_luck / 1000.0) * 0.5  ->  max 5% at luck=100.
    """
    if already_used:
        return False
    chance = (axo_luck / 1000.0) * 0.5
    return _rng.random() < chance


def _miss_chance(focus: float) -> float:
    """
    Chance to miss marking a card on your board.
    Focus 100 → 0 % miss. Focus 50 → 15 % miss. Focus 0 → 30 % miss.
    """
    return max(0.0, min(0.3, (100.0 - focus) * 0.003))


# --- 2×2 SQUARE DEFINITIONS ---
WINNING_CUADRITOS = [
    {0, 1, 4, 5}, {1, 2, 5, 6}, {2, 3, 6, 7},        # Top
    {4, 5, 8, 9}, {5, 6, 9, 10}, {6, 7, 10, 11},     # Mid
    {8, 9, 12, 13}, {9, 10, 13, 14}, {10, 11, 14, 15} # Bottom
]

# --- EXPANDED PATTERN DEFINITIONS ---
WINNING_POCITO: frozenset = frozenset({5, 6, 9, 10})          # Centro 2×2
WINNING_ESQUINAS: frozenset = frozenset({0, 3, 12, 15})       # 4 Esquinas
WINNING_CRUZ_DIAGONAL: frozenset = frozenset({0, 3, 5, 6, 9, 10, 12, 15})  # La X

# L-shapes: una esquina + su fila + su columna (4 variantes)
WINNING_L_SHAPES: list = [
    frozenset({0, 1, 2, 3, 4, 8, 12}),    # top-left
    frozenset({0, 1, 2, 3, 7, 11, 15}),   # top-right
    frozenset({0, 4, 8, 12, 13, 14, 15}), # bottom-left
    frozenset({3, 7, 11, 12, 13, 14, 15}), # bottom-right
]

# Z-shapes: fila superior + 2 celdas diagonales medias + fila inferior
WINNING_Z_SHAPES: list = [
    frozenset({0, 1, 2, 3, 6, 9, 12, 13, 14, 15}),  # Z
    frozenset({0, 1, 2, 3, 5, 10, 12, 13, 14, 15}),  # S (Z espejo)
]

# Filas y columnas para check_cruz_recta
_ROWS: list = [{0,1,2,3}, {4,5,6,7}, {8,9,10,11}, {12,13,14,15}]
_COLS: list = [{0,4,8,12}, {1,5,9,13}, {2,6,10,14}, {3,7,11,15}]


def check_pocito(marked: set) -> bool:
    return WINNING_POCITO.issubset(marked)


def check_esquinas_pattern(marked: set) -> bool:
    return WINNING_ESQUINAS.issubset(marked)


def check_cruz_recta(marked: set) -> bool:
    """Cualquier fila completa + cualquier columna completa (cruz)."""
    for row in _ROWS:
        if row.issubset(marked):
            for col in _COLS:
                if col.issubset(marked):
                    return True
    return False


def check_cruz_diagonal(marked: set) -> bool:
    return WINNING_CRUZ_DIAGONAL.issubset(marked)


def check_l_shape(marked: set) -> bool:
    return any(l.issubset(marked) for l in WINNING_L_SHAPES)


def check_z_shape(marked: set) -> bool:
    return any(z.issubset(marked) for z in WINNING_Z_SHAPES)


def check_full_board(marked: set) -> bool:
    return len(marked) == 16


PATTERN_CHECKERS: dict = {
    "line": check_loterica_line,
    "cuadrito": lambda m: any(sq.issubset(m) for sq in WINNING_CUADRITOS),
    "pocito": check_pocito,
    "esquinas": check_esquinas_pattern,
    "cruz": check_cruz_recta,
    "cruz_diagonal": check_cruz_diagonal,
    "l_shape": check_l_shape,
    "z_shape": check_z_shape,
    "full_board": check_full_board,
}


def check_any_pattern(marked: set, patterns: list) -> tuple:
    """Returns (True, pattern_name) if any of the given patterns is completed."""
    for p in patterns:
        checker = PATTERN_CHECKERS.get(p)
        if checker and checker(marked):
            return True, p
    return False, None


# --- TENSION STATUS ---

from dataclasses import dataclass, field as dc_field


@dataclass
class TensionStatus:
    """Estado de tensión de una partida de Lotería en curso.

    Evalúa cuán cerca están los jugadores de completar una línea o cuadrito.
    Útil para: modular velocidad de animación (auto), alertar al jugador (manual).
    """
    level: str  # "low" | "medium" | "high" | "critical"
    near_win_players: list[int] = dc_field(default_factory=list)  # axo IDs a 1 celda de ganar
    hot_lines: list[dict] = dc_field(default_factory=list)  # [{player_axo_id, line_indices, missing_cell, cells_matched}]


def check_tension_status(
    boards: list[dict],
    *,
    tension_thresholds: dict | None = None,
) -> TensionStatus:
    """
    Evalúa el nivel de tensión de la sala a partir del estado de todos los tableros.

    Args:
        boards: Lista de dicts, cada uno con:
            - axo_id: int (ID del Axolotito, None para bots)
            - marked_indices: set[int] (celdas ya marcadas, índices 0–15)
        tension_thresholds: Opcional. Override de umbrales.
            Default: medium≥1 hot_line, high≥2 jugadores near-win, critical=alguien a 1 celda.

    Returns:
        TensionStatus con level, lista de jugadores near-win, y hot_lines activas.
    """
    if tension_thresholds is None:
        tension_thresholds = {
            "medium_min_hot": 1,     # al menos 1 hot_line → medium
            "high_min_players": 2,   # al menos 2 jugadores near-win → high
            "critical_cells_left": 1, # 1 celda faltante → critical
        }

    all_hot_lines: list[dict] = []
    near_win_players: list[int] = []
    critical_players: list[int] = []

    for board in boards:
        axo_id = board.get("axo_id")
        marked = set(board.get("marked_indices", []))

        # Revisar cada línea de victoria
        for line in WINNING_LINES:
            matched = line & marked
            cells_matched = len(matched)
            missing = line - marked
            cells_left = 4 - cells_matched

            if cells_left == 0:
                continue  # ya ganó — no contribuye a tensión
            if cells_left <= 2:
                all_hot_lines.append({
                    "player_axo_id": axo_id,
                    "line_indices": list(line),
                    "missing_cells": list(missing),
                    "cells_matched": cells_matched,
                })

        # Revisar cuadritos
        for sq in WINNING_CUADRITOS:
            matched = sq & marked
            cells_matched = len(matched)
            missing = sq - marked
            cells_left = 4 - cells_matched

            if cells_left == 0:
                continue
            if cells_left <= 2:
                all_hot_lines.append({
                    "player_axo_id": axo_id,
                    "line_indices": list(sq),
                    "missing_cells": list(missing),
                    "cells_matched": cells_matched,
                })

        # Determinar si este jugador está a 1 celda de ganar
        nearest = 4  # peor caso: 0 celdas marcadas
        for line in WINNING_LINES:
            cells_left = 4 - len(line & marked)
            if cells_left < nearest:
                nearest = cells_left
        for sq in WINNING_CUADRITOS:
            cells_left = 4 - len(sq & marked)
            if cells_left < nearest:
                nearest = cells_left

        if nearest <= 1 and axo_id is not None:
            critical_players.append(axo_id)
        if nearest <= 2 and axo_id is not None:
            near_win_players.append(axo_id)

    # Determinar nivel
    if critical_players:
        level = "critical"
    elif len(near_win_players) >= tension_thresholds["high_min_players"]:
        level = "high"
    elif len(all_hot_lines) >= tension_thresholds["medium_min_hot"]:
        level = "medium"
    else:
        level = "low"

    return TensionStatus(
        level=level,
        near_win_players=near_win_players,
        hot_lines=all_hot_lines,
    )


def validate_win(
    marked_indices: set[int],
    called_card_ids: set[int],
    board_card_ids: list[int],
) -> tuple[bool, str | None, set[int] | None]:
    """
    Valida si un jugador realmente completó una línea/cuadrito con cartas que YA fueron cantadas.

    Args:
        marked_indices: Celdas que el jugador marcó (índices 0–15).
        called_card_ids: Conjunto de card_ids que ya han sido cantadas por el Gritón.
        board_card_ids: Lista de 16 card_ids que componen el tablero del jugador.

    Returns:
        (is_valid, win_type, winning_cells)
        - is_valid: True si el jugador ganó legítimamente.
        - win_type: "line" | "cuadrito" | None
        - winning_cells: Set de índices de la línea/cuadrito ganadora, o None.
    """
    # Verificar que TODAS las celdas marcadas correspondan a cartas cantadas
    for idx in marked_indices:
        if idx < 0 or idx >= 16:
            return False, None, None
        card_id = board_card_ids[idx]
        if card_id not in called_card_ids:
            return False, None, None

    # Verificar líneas
    for line in WINNING_LINES:
        if line.issubset(marked_indices):
            return True, "line", line

    # Verificar cuadritos
    for sq in WINNING_CUADRITOS:
        if sq.issubset(marked_indices):
            return True, "cuadrito", sq

    # Verificar esquinas
    if WINNING_ESQUINAS.issubset(marked_indices):
        return True, "esquinas", set(WINNING_ESQUINAS)

    # Verificar pocito
    if WINNING_POCITO.issubset(marked_indices):
        return True, "pocito", set(WINNING_POCITO)

    # Verificar tablero lleno
    if len(marked_indices) == 16:
        return True, "full_board", set(range(16))

    return False, None, None
