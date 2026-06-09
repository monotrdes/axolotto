from __future__ import annotations
"""
incubation_service.py — DB-dependent wrapper for Webito imprinting during gameplay.

Contains the session-aware function that applies imprinting deltas from a match
result. Calls into the pure imprinting_service for computation.
"""
from sqlmodel import Session, select

from app.models.items import WebitoIncubation, ItemCatalog
from app.services.imprinting_service import (
    ImprintingGameResult,
    compute_deltas,
    apply_deltas_to_incubation,
    required_games_for_rarity,
)


def _apply_imprinting_if_needed(
    axo,
    is_win: bool,
    had_jackpot: bool,
    mark_accuracy: float,
    session: Session,
) -> dict | None:
    """
    Si el Axolotito es padrino de un Webito en imprinting activo, aplica los deltas.
    Devuelve info del imprinting si ocurrió, None si no.
    No hace commit — el caller commitea todo junto.
    """
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.imprinting_padrino_id == axo.id)
        .where(WebitoIncubation.imprinting_complete == False)
    ).first()
    if not incubation:
        return None

    energy_pct = (axo.energy_current / axo.stat_stamina) if axo.stat_stamina > 0 else 0.0

    result = ImprintingGameResult(
        won=is_win,
        had_jackpot_bonus=had_jackpot,
        mark_accuracy=mark_accuracy,
        session_game_count=incubation.imprinting_games_played + 1,
        padrino_energy_pct=min(1.0, energy_pct),
        padrino_sal=axo.stat_salinity,
    )
    padrino_nature = axo.nature
    deltas = compute_deltas(result, padrino_nature=padrino_nature)
    apply_deltas_to_incubation(incubation, deltas)

    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    if incubation.imprinting_games_played >= required:
        incubation.imprinting_complete = True

    session.add(incubation)

    return {
        "imprinting_game": incubation.imprinting_games_played,
        "required": required,
        "complete": incubation.imprinting_complete,
        "deltas": {
            "suerte": round(deltas.luck_delta, 1),
            "ojo":    round(deltas.focus_delta, 1),
            "pila":   round(deltas.stamina_delta, 1),
            "sal":    round(deltas.salinity_delta, 1),
        },
    }
