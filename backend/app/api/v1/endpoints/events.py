from __future__ import annotations
"""
events.py — Endpoint público para consultar el estado del modo manual.

GET /api/v1/events/manual-mode
→ { active_event: {...} | null, next_event: {...} | null }

No requiere autenticación — el frontend puede llamarlo sin token.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.manual_mode_event import ManualModeEvent

router = APIRouter()


def _event_is_active_now(event: ManualModeEvent) -> bool:
    """
    True si el evento está activo ahora mismo.
    NOTA: Se compara en UTC. El campo `timezone` del evento es informativo
    pero no afecta la comparación aún. TODO: convertir a timezone del evento.
    """
    now = datetime.utcnow()
    today = now.date()
    current_time = now.time()

    if not event.is_active:
        return False
    if event.start_date > today or event.end_date < today:
        return False
    if event.daily_open_time is None or event.daily_close_time is None:
        return True  # todo el día (o configuración incompleta — se trata como todo el día)
    # No se soportan ventanas que cruzan medianoche (ej. 22:00–02:00 fallará)
    if event.daily_close_time < event.daily_open_time:
        return False
    return event.daily_open_time <= current_time <= event.daily_close_time


def _event_is_upcoming(event: ManualModeEvent) -> bool:
    today = datetime.utcnow().date()
    return event.is_active and event.start_date > today


def _serialize_event(e: ManualModeEvent | None) -> dict | None:
    if e is None:
        return None
    return {
        "id": e.id,
        "name": e.name,
        "start_date": e.start_date.isoformat(),
        "end_date": e.end_date.isoformat(),
        "daily_open_time": e.daily_open_time.isoformat() if e.daily_open_time else None,
        "daily_close_time": e.daily_close_time.isoformat() if e.daily_close_time else None,
        "bonus_gal_on_win": e.bonus_gal_on_win,
        "drop_multiplier": e.drop_multiplier,
        "xp_bonus_pct": e.xp_bonus_pct,
        "griton_delay_ms": e.griton_delay_ms,
        "win_condition": e.win_condition,
        "allowed_modes": e.allowed_modes,
        "max_players_per_room": e.max_players_per_room,
    }


@router.get("/manual-mode")
def manual_mode_status(session: Session = Depends(get_session)):
    """
    Devuelve el evento activo ahora y el próximo evento programado.
    Usado por el frontend para mostrar/deshabilitar el botón de modo manual.
    """
    all_events = session.exec(
        select(ManualModeEvent)
        .where(ManualModeEvent.is_active == True)
        .order_by(ManualModeEvent.start_date.asc())
    ).all()

    active = next((e for e in all_events if _event_is_active_now(e)), None)
    upcoming = next((e for e in all_events if _event_is_upcoming(e)), None)

    return {
        "active_event": _serialize_event(active),
        "next_event": _serialize_event(upcoming) if active is None else None,
    }
