from sqlmodel import SQLModel, Field, JSON
from typing import Optional, List
from datetime import datetime

class Axolotito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    name: str = Field(default="Axolotito Bebé")
    
    # --- Mapeo de Identificadores Visuales (Rápido) ---
    skin_color: str = Field(default="pink")        # pink, gray_light, gray_dark, gold, astral, etc.
    gill_type: str = Field(default="normal")        # short, normal, feathery, crown, phoenix
    eye_type: str = Field(default="cute")          # cute, derp, dreamer, cool, zen
    mouth_type: str = Field(default="smile")       # flat, smile, fang, rockstar, divine
    tail_type: str = Field(default="standard")     # standard, wavy, betta, plasma
    forehead_type: str = Field(default="none")     # none, stripes, gem, halo
    limb_type: str = Field(default="soft")         # soft, claws, scales, coral
    
    # --- Estadísticas Reales ---
    level: int = Field(default=1)
    experience: int = Field(default=0)
    
    stat_salinity: float = Field(default=5.0)      # 0.0 a 100.0 (Mala suerte)
    stat_luck: float = Field(default=10.0)          # 0.0 a 100.0 (Drops)
    stat_focus: float = Field(default=50.0)         # 0.0 a 100.0 (Concentración)
    stat_stamina: int = Field(default=100)          # 50 a 200 (Energía Máxima)
    stat_charisma: float = Field(default=10.0)      # 0.0 a 100.0 (Carisma)
    stat_agility: float = Field(default=10.0)       # 0.0 a 100.0 (Agilidad)
    stat_wisdom: float = Field(default=10.0)        # 0.0 a 100.0 (Sabiduría)
    stat_strength: float = Field(default=10.0)      # 0.0 a 100.0 (Fuerza)
    
    # --- Estado Actual del Juego ---
    status: str = Field(default="idle")             # idle, expedition, resting, studying, playing, sleeping, waiting_settlement
    energy_current: int = Field(default=100)        # Energía restante
    sleep_expires_at: Optional[datetime] = Field(default=None, nullable=True)
    last_staking_claim: Optional[datetime] = Field(default=None)
    accrued_unclaimed: int = Field(default=0)          # VULN-06: FRJ en unidad mínima
    escrow_balance_gal: int = Field(default=0)         # VULN-06: FRJ en unidad mínima
    loyalty_points: int = Field(default=0)          # Puntos de afecto / lealtad acumulados
    cpu_win_streak: int = Field(default=0)          # consecutive CPU wins (resets on loss)
    wants_to_stop: bool = Field(default=False)       # Señal del jugador para retirar al final de la partida actual

    # --- Configuración del Bot (Autojuego) ---
    # serialization_alias → frontend recibe nombres AXF (commit rename AXG→AXF)
    bot_enabled: bool = Field(default=False)
    bot_budget_axg: int = Field(default=0, serialization_alias='bot_budget_axf')      # VULN-06: FRJ unidad mínima
    bot_loss_limit_axg: int = Field(default=0, serialization_alias='bot_loss_limit_axf')  # VULN-06
    bot_profit_limit_axg: int = Field(default=0, serialization_alias='bot_profit_limit_axf')  # VULN-06
    assigned_board_id: Optional[int] = Field(default=None, foreign_key="playerboard.id")

    # --- Renta y Venta (P2P Market) ---
    is_listed_for_sale: bool = Field(default=False)
    sale_price_gal: int = Field(default=0)             # VULN-06: FRJ en unidad mínima
    is_listed_for_rent: bool = Field(default=False)
    rent_fee_gal: int = Field(default=0)               # VULN-06: FRJ en unidad mínima
    rent_share_owner_pct: int = Field(default=0)
    is_rented: bool = Field(default=False)
    renter_id: Optional[str] = Field(default=None, foreign_key="user.privy_did", nullable=True)
    rent_expires_at: Optional[datetime] = Field(default=None, nullable=True)
    
    # --- Equipamiento (Accesorios) ---
    equipped_head_item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", nullable=True)
    equipped_eyes_item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", nullable=True)
    equipped_body_item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", nullable=True)
    
    # --- Cueva (Cave Equipment) ---
    cave_items: List[int] = Field(default=[], sa_type=JSON)
    # List of up to 3 ItemCatalog IDs currently equipped in this axolotito's cave

    nature: Optional[str] = Field(default=None, nullable=True)
    mentorship_count: int = Field(default=0)
    tutored_by_id: Optional[int] = Field(default=None)

    # --- Web3 Mapping ---
    blockchain_token_id: Optional[int] = Field(default=None, unique=True)
    dna_sequence: Optional[str] = Field(default=None) # Representación string de uint256

    # VIP — congelado si el dueño pierde la membresía Axolite que le otorgaba el slot extra
    is_frozen_by_vip: bool = Field(default=False)
    is_main: bool = Field(default=False)
    is_tutorial: bool = Field(default=False, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
