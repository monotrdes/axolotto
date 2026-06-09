from __future__ import annotations
from datetime import date, datetime, time
from typing import Optional
from sqlmodel import Field, SQLModel


class ManualModeEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                                      # "Noche de Lotería #1 🌙"
    start_date: date
    end_date: date
    daily_open_time: Optional[time] = Field(default=None, nullable=True)   # None = todo el día
    daily_close_time: Optional[time] = Field(default=None, nullable=True)
    timezone: str = Field(default="America/Mexico_City")

    # Economía
    tabla_cost_gal: float = Field(default=10.0)
    max_tablas_per_player: int = Field(default=3)
    prize_pool_pct: float = Field(default=0.80)
    platform_fee_pct: float = Field(default=0.10)
    jackpot_contribution_pct: float = Field(default=0.10)
    bonus_gal_on_win: float = Field(default=0.0)
    drop_multiplier: float = Field(default=1.0)
    xp_bonus_pct: float = Field(default=0.0)

    # Mecánicas
    griton_delay_ms: int = Field(default=2000)
    griton_repeats: bool = Field(default=True)
    win_condition: str = Field(default="tabla_llena")  # línea_h|línea_v|esquinas|tabla_llena|cruz|l_invertida
    max_game_duration_s: Optional[int] = Field(default=None, nullable=True)
    tie_behavior: str = Field(default="split")     # split|replay
    allowed_modes: str = Field(default="both")     # manual|bot|both

    # Jugadores
    max_players_per_room: int = Field(default=10)
    min_players_to_start: int = Field(default=2)
    room_wait_timeout_s: int = Field(default=90)
    vip_only: bool = Field(default=False)
    min_axo_level: Optional[int] = Field(default=None, nullable=True)
    first_time_only: bool = Field(default=False)

    # Comunicación
    broadcast_message: Optional[str] = Field(default=None, nullable=True)
    broadcast_sent: bool = Field(default=False)
    broadcast_sent_at: Optional[datetime] = Field(default=None, nullable=True)
    auto_reminder: bool = Field(default=True)
    notify_room_start: bool = Field(default=True)
    post_event_summary: bool = Field(default=True)

    # Meta
    is_active: bool = Field(default=True)
    created_by: str = Field(foreign_key="user.privy_did")  # privy_did del admin que creó el evento
    created_at: datetime = Field(default_factory=datetime.utcnow)
