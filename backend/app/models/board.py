from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime

class PlayerBoard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    name: str = Field(default="Mi Tabla Lotería")
    is_dead: bool = Field(default=False)
    
    # Lista de 16 IDs de cartas (posiciones 0 a 15)
    card_ids: List[int] = Field(default=[], sa_type=JSON)
    # Lista de 16 booleanos indicando si la carta en esa posición es Primera Edición
    card_first_editions: List[bool] = Field(default=[], sa_type=JSON)
    
    # Stats
    games_played: int = Field(default=0)
    games_won: int = Field(default=0)
    level: int = Field(default=1)
    xp: int = Field(default=0)
    
    # Historial de los últimos 5 juegos (ej: [True, False, ...]) para racha y CSR
    recent_games_results: List[bool] = Field(default=[], sa_type=JSON)
    
    # Staking
    last_staking_claim: datetime = Field(default_factory=datetime.utcnow)
    
    # Renta (Scholarship)
    is_listed_for_rent: bool = Field(default=False)
    is_rented: bool = Field(default=False)
    renter_id: Optional[str] = Field(default=None, foreign_key="user.privy_did", nullable=True)
    rent_fee_gal: float = Field(default=0.0)
    rent_share_owner_pct: int = Field(default=0)
    rent_expires_at: Optional[datetime] = Field(default=None, nullable=True)
    
    # Venta (P2P Sale)
    is_listed_for_sale: bool = Field(default=False)
    sale_price_gal: float = Field(default=0.0)
    
    # Web3 Mapping
    blockchain_token_id: Optional[int] = Field(default=None, unique=True)

    # VIP — congelada si el dueño pierde la membresía que le otorgaba este slot
    is_frozen_by_vip: bool = Field(default=False)
    is_tutorial: bool = Field(default=False, index=True)

    # NPC Bot Pool
    is_npc_pool: bool          = Field(default=False)
    npc_room: Optional[str]    = Field(default=None)   # "rookie" | "champion"
    npc_retired: bool          = Field(default=False)  # graduated → gashapon pool
    origin_story: Optional[str] = Field(default=None)  # set when graduated

    created_at: datetime = Field(default_factory=datetime.utcnow)
