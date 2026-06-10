from enum import Enum
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime, timedelta

class ItemType(str, Enum):
    EGG = "EGG"
    BOOSTER = "BOOSTER"
    CARD = "CARD"
    ACCESSORY = "ACCESSORY"
    BOARD = "BOARD"
    CONSUMABLE = "CONSUMABLE"
    CURRENCY_PACK = "CURRENCY_PACK"
    CAVE_ITEM = "CAVE_ITEM"

class Rarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ItemCatalog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    item_type: ItemType
    rarity: Rarity = Field(default=Rarity.COMMON)
    
    # --- NUEVA ECONOMÍA (VULN-06: montos en unidad mínima entera) ---
    price_axg: Optional[int] = Field(default=None) # Precio en AXF (6 decimales)
    price_gal: Optional[int] = Field(default=None) # Precio en FRJ (4 decimales)
    is_active: bool = Field(default=True)            # Para ocultar ítems agotados de la tienda visual
    # -----------------------------------------------------------------
    
    is_sellable: bool = Field(default=True)
    max_supply: Optional[int] = None # Aquí es donde pondremos los límites (420, 1260, etc.)
    max_per_user: Optional[int] = None  # límite de compra por wallet por ítem
    
    item_metadata: Optional[Dict] = Field(default={}, sa_type=JSON)

class PlayerInventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    item_id: int = Field(foreign_key="itemcatalog.id")
    quantity: int = Field(default=1)
    is_first_edition: bool = Field(default=False)
    is_shiny: bool = Field(default=False)

class WebitoIncubation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    item_id: int # El ID del Webito en el catálogo
    clicks_hoy: int = Field(default=0)
    clicks_totales: int = Field(default=0)
    calor_actual: float = Field(default=0.0) # Porcentaje 0 a 100
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow)
    fecha_eclosion_estimada: datetime
    ultimo_click: datetime = Field(default_factory=datetime.utcnow)
    is_frozen: bool = Field(default=False)
    frozen_clicks_left: int = Field(default=0)
    protected_until: Optional[datetime] = Field(default=None)
    genetic_purity: float = Field(default=100.0)

    # --- SISTEMA DE CARIÑITOS (Hatchery 2.0) ---
    # Timestamps del último cuidado (para cooldowns)
    last_petting: Optional[datetime] = Field(default=None)   # Acariciar - cooldown 4h
    last_singing: Optional[datetime] = Field(default=None)   # Cantarle   - cooldown 8h
    last_feeding: Optional[datetime] = Field(default=None)   # Alimentar  - cooldown 12h

    # Bonos de estadísticas acumuladas por cuidado (se aplican al nacer)
    bonus_strength: float = Field(default=0.0)  # Acariciar -> Fuerza / Agilidad
    bonus_agility: float = Field(default=0.0)   # Acariciar -> Fuerza / Agilidad
    bonus_wisdom: float = Field(default=0.0)    # Cantarle  -> Sabiduría / Concentración
    bonus_focus: float = Field(default=0.0)     # Cantarle  -> Sabiduría / Concentración
    bonus_stamina: float = Field(default=0.0)   # Alimentar -> Energía / Suerte
    bonus_luck: float = Field(default=0.0)      # Alimentar -> Energía / Suerte

    # --- TUTORIAL ---
    tutorial_phase: int = Field(default=0)          # 0=sin tutorial, 1-3=fase activa, 4=karma, 5=completo
    tutorial_act_index: int = Field(default=0)      # Acto exacto del script del tutorial (0-11)
    tutorial_karma: Optional[str] = Field(default=None)  # "lucky" | "salty"
    tutorial_board_card_ids: Optional[list] = Field(default=None, sa_type=JSON)  # 16 card IDs determinísticos

    # --- SISTEMA DE IMPRINTING (reemplaza cooldown care) ---
    imprinting_games_played: int = Field(default=0)
    imprinting_padrino_id: Optional[int] = Field(
        default=None, nullable=True, foreign_key="axolotito.id"
    )
    # Stats base al inicio del imprinting (se setean al llamar start_imprinting)
    base_stat_luck: float = Field(default=0.0)
    base_stat_focus: float = Field(default=0.0)
    base_stat_stamina: float = Field(default=0.0)
    base_stat_salinity: float = Field(default=0.0)
    # bonus_salinity acumulado durante imprinting (nuevo — los otros bonus_* ya existen)
    bonus_salinity_adj: float = Field(default=0.0)
    # imprinting completado (ADN sellado, listo para eclosión)
    imprinting_complete: bool = Field(default=False)

class CapsulaDailyFree(SQLModel, table=True):
    """Registro de cada cápsula diaria gratuita reclamada por usuario."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    claimed_at: datetime = Field(default_factory=datetime.utcnow)
    consecutive_days: int = Field(default=1)

class CapsulaPity(SQLModel, table=True):
    """Contadores pity por tier por usuario (garantía después de N rolls sin axolotito)."""
    user_id: str = Field(primary_key=True)
    pity_cobre: int = Field(default=0)
    pity_plata: int = Field(default=0)
    pity_oro: int = Field(default=0)

class LegacyBacker(SQLModel, table=True):
    """
    Tabla de inversores originales del proyecto (2021).
    Permite reclamar Webitos Fundadores gratis al sincronizarse con Privy.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email_or_wallet: str = Field(index=True, unique=True)  # Email o dirección de wallet
    eggs_owed: int = Field(default=1)       # Webitos prometidos
    eggs_claimed: int = Field(default=0)    # Webitos ya reclamados
    notes: Optional[str] = Field(default=None)  # Nombre o referencia del backer


class InventoryMarketListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(foreign_key="user.privy_did", index=True)
    item_id: int = Field(foreign_key="itemcatalog.id")
    quantity: int = Field(default=1)
    is_first_edition: bool = Field(default=False)
    is_shiny: bool = Field(default=False)
    price_gal: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)



class WhitelistEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True, unique=True)
    email: str = Field(index=True)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    phase_access: int = Field(default=1)
    source: str = Field(default="microsite")  # "microsite", "legacy", "vip"