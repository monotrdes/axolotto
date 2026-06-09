"""
admin_events.py — CRUD de eventos de modo manual para admins.

Endpoints:
  POST   /api/v1/admin/events          — crear evento
  GET    /api/v1/admin/events          — listar eventos
  PATCH  /api/v1/admin/events/{id}     — editar evento
  DELETE /api/v1/admin/events/{id}     — cancelar evento
  POST   /api/v1/admin/events/{id}/broadcast — enviar convocatoria
  GET    /api/v1/admin/events/{id}/stats     — stats del evento
"""
from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import require_admin
from app.database import get_session
from app.models.manual_mode_event import ManualModeEvent

router = APIRouter()


# --- Schemas ---

class EventCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    daily_open_time: Optional[time] = None
    daily_close_time: Optional[time] = None
    timezone: str = "America/Mexico_City"
    tabla_cost_gal: float = 10.0
    max_tablas_per_player: int = 3
    prize_pool_pct: float = 0.80
    platform_fee_pct: float = 0.10
    jackpot_contribution_pct: float = 0.10
    bonus_gal_on_win: float = 0.0
    drop_multiplier: float = 1.0
    xp_bonus_pct: float = 0.0
    griton_delay_ms: int = 2000
    griton_repeats: bool = True
    win_condition: str = "tabla_llena"  # línea_h|línea_v|esquinas|tabla_llena|cruz|l_invertida
    max_game_duration_s: Optional[int] = None
    tie_behavior: str = "split"         # split|replay
    allowed_modes: str = "both"         # manual|bot|both
    max_players_per_room: int = 10
    min_players_to_start: int = 2
    room_wait_timeout_s: int = 90
    vip_only: bool = False
    min_axo_level: Optional[int] = None
    first_time_only: bool = False
    broadcast_message: Optional[str] = None
    auto_reminder: bool = True
    notify_room_start: bool = True
    post_event_summary: bool = True


class EventPatch(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    daily_open_time: Optional[time] = None
    daily_close_time: Optional[time] = None
    is_active: Optional[bool] = None
    broadcast_message: Optional[str] = None
    bonus_gal_on_win: Optional[float] = None
    drop_multiplier: Optional[float] = None
    griton_delay_ms: Optional[int] = None
    max_players_per_room: Optional[int] = None


# --- Endpoints ---

@router.post("")
def create_event(
    payload: EventCreate,
    session: Session = Depends(get_session),
    admin_id: str = Depends(require_admin),
):
    """Crea un nuevo evento de modo manual."""
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date debe ser >= start_date.")
    if payload.prize_pool_pct + payload.platform_fee_pct + payload.jackpot_contribution_pct > 1.01:
        raise HTTPException(status_code=400, detail="La suma de porcentajes no puede superar 100%.")

    event = ManualModeEvent(created_by=admin_id, **payload.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("")
def list_events(
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Lista todos los eventos ordenados por fecha de inicio descendente."""
    events = session.exec(
        select(ManualModeEvent).order_by(ManualModeEvent.start_date.desc())
    ).all()
    now_date = datetime.utcnow().date()

    def status(e: ManualModeEvent) -> str:
        if not e.is_active:
            return "cancelled"
        if e.end_date < now_date:
            return "past"
        if e.start_date > now_date:
            return "upcoming"
        return "active"

    return [{"event": e, "status": status(e)} for e in events]


@router.patch("/{event_id}")
def patch_event(
    event_id: int,
    payload: EventPatch,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Actualiza campos de un evento. Solo si no ha terminado."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    if event.end_date < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="No se puede editar un evento terminado.")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(event, field, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
def cancel_event(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Desactiva (cancela) un evento."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    event.is_active = False
    session.add(event)
    session.commit()
    return {"mensaje": f"Evento '{event.name}' cancelado."}


@router.post("/{event_id}/broadcast")
def send_broadcast(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Marca el evento como 'convocatoria enviada'. Notificacion real: futuro."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    if not event.broadcast_message:
        raise HTTPException(status_code=400, detail="El evento no tiene mensaje de convocatoria.")

    event.broadcast_sent = True
    event.broadcast_sent_at = datetime.utcnow()
    session.add(event)
    session.commit()

    return {
        "mensaje": f"Convocatoria marcada como enviada para '{event.name}'.",
        "sent_at": event.broadcast_sent_at.isoformat(),
    }


@router.get("/{event_id}/stats")
def event_stats(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Stats del evento (placeholder — se expande con logs de partidas)."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    return {
        "event_id": event_id,
        "name": event.name,
        "broadcast_sent": event.broadcast_sent,
        "start_date": event.start_date.isoformat(),
        "end_date": event.end_date.isoformat(),
    }
