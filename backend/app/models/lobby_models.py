from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class MultiplayerGameLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    axolotito_id: int = Field(foreign_key="axolotito.id", index=True)
    axo_name: str
    room_name: str
    outcome: str       # "Victoria", "Derrota"
    net_gal: int                           # VULN-06: unidad mínima entera
    xp_gained: int
    # Prize breakdown (2026-06 — multiplayer prize clarity)
    prize_breakdown_json: Optional[str] = Field(default=None)  # JSON: [{prize_type, label, gross_gal, luck_bonus, vip_bonus}]
    won_premio_1: bool = Field(default=False)
    won_premio_2: bool = Field(default=False)
    won_jackpot: bool = Field(default=False)
    entry_fee_paid: int = Field(default=0)  # VULN-06: unidad mínima entera
    gross_prize_gal: int = Field(default=0) # VULN-06: unidad mínima entera
    notified: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TreasuryVault(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    balance: int = Field(default=0)  # VULN-06: unidad mínima entera
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class JackpotVault(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    current_amount: int = Field(default=10_000_000)  # VULN-06: 1000 FRJ en unidad mínima
    seed_amount: int = Field(default=10_000_000)     # VULN-06: 1000 FRJ en unidad mínima
    last_won_at: Optional[datetime] = None
    last_winner_axo_id: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class JackpotWin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    axo_id: int = Field(foreign_key="axolotito.id")
    user_id: str = Field(foreign_key="user.privy_did")
    amount_won: int                        # VULN-06: unidad mínima entera
    cards_drawn_count: int
    won_at: datetime = Field(default_factory=datetime.utcnow)

class GameRoom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str # e.g. "Charco de Novatos #1"
    room_type: str # "rookie" o "champion" o "player_hosted"
    entry_fee_gal: int                     # FRJ human-readable (convertir con frj_to_internal al usarse en escrow)
    status: str = Field(default="waiting") # waiting, playing, finished
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Player-hosted rooms (cave table)
    host_id: Optional[str] = Field(default=None, foreign_key="user.privy_did", index=True)
    room_config: Optional[str] = Field(default=None)  # JSON: {buy_in_frj, max_players, visibility, speed, win_patterns, password_hash, game_type}
    visibility: str = Field(default="public")  # "public" | "friends" | "private"
    password_hash: Optional[str] = Field(default=None)
    host_reputation_earned: int = Field(default=0)  # reputación ganada en esta sala
    # Lobby timeout / AFK tracking
    countdown_started_at: Optional[datetime] = Field(default=None)  # cuando el host inicia la cuenta regresiva
    last_host_activity_at: Optional[datetime] = Field(default=None)  # última actividad del host en el lobby

class RoomRegistration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="gameroom.id", index=True)
    axolotito_id: int = Field(foreign_key="axolotito.id", index=True)
    boards_json: str # JSON list of board IDs registered e.g. "[1, 2]"
    play_mode: str = Field(default="auto")  # "auto" (AFK) o "manual" (tiempo real)
    ready: bool = Field(default=False)  # jugador listo para comenzar la partida
    ready_at: Optional[datetime] = Field(default=None)  # cuando marcó ready
    registered_at: datetime = Field(default_factory=datetime.utcnow)


class ActiveGameState(SQLModel, table=True):
    """Estado en vivo de una partida en curso. El backend escribe aquí cada tick
    para que el frontend pueda leer el estado mediante polling (modo auto)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="gameroom.id", unique=True, index=True)
    phase: str = Field(default="playing")  # "playing" | "finished"
    cards_drawn_json: str = Field(default="[]")  # JSON array de card_ids cantados
    player_states_json: str = Field(default="{}")  # JSON: {axo_id: {board_id, marked, missed}}
    turns_played: int = Field(default=0)
    current_card_id: Optional[int] = Field(default=None)  # carta actual siendo cantada
    tension_level: str = Field(default="low")  # "low" | "medium" | "high" | "critical"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
