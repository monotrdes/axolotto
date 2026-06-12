from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    privy_did: str = Field(index=True, unique=True) # El ID de Privy
    nickname: Optional[str] = None
    email: Optional[str] = None
    wallet_address: Optional[str] = Field(default=None, index=True, unique=True)
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    puntos: int = Field(default=0)
    unlocked_board_slots: int = Field(default=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    first_crypto_purchase_at: Optional[datetime] = None  # para bonus +10% primera compra
    promo_code_attempts: int = Field(default=0)  # intentos fallidos de canjear corcholatas (máx 3)

    # --- Tutorial & F2P ---
    tutorial_completed: bool = Field(default=False)
    cave_level: int = Field(default=1)                                 # Nivel de expansión del Cenote (1-8). Reemplaza webito_slots_unlocked.
    cave_name: Optional[str] = Field(default=None)                     # Nombre personalizado de la cueva
    cave_decorations: Optional[str] = Field(default="{}")              # JSON: {decorId: {pos, rot, scale}} por cueva
    cave_expansion_started_at: Optional[datetime] = Field(default=None) # Timer de excavación en curso
    cave_expansion_target_level: Optional[int] = Field(default=None)   # Nivel que se está excavando
    last_play_date: Optional[datetime] = Field(default=None)
    daily_play_streak: int = Field(default=0)
    f2p_astral_fragments: int = Field(default=0)
    f2p_daily_gal_earned: int = Field(default=0)  # VULN-06: FRJ en unidad mínima
    f2p_daily_gal_reset_at: Optional[datetime] = Field(default=None)
    f2p_daily_frags_earned: int = Field(default=0)
    last_f2p_daily_claim_at: Optional[datetime] = Field(default=None)
    f2p_daily_claim_streak: int = Field(default=0)

    # Ciclo Lunar — unified F2P reward track
    lunar_streak_day: int = Field(default=0)        # days completed in current week (0=none, 1-7)
    lunar_week: int = Field(default=1)              # current Luna (1-6)
    lunar_last_claim_at: Optional[datetime] = Field(default=None)
    lunar_cycles_completed: int = Field(default=0)  # full 6-Luna cycles completed

    # --- VIP Club ---
    vip_tier: Optional[str] = Field(default=None)                    # "coral" | "dorado" | "axolite"
    vip_expires_at: Optional[datetime] = Field(default=None)
    vip_streak_months: int = Field(default=0)
    vip_streak_last_renewed: Optional[datetime] = Field(default=None)
    vip_pending_gal: int = Field(default=0)                          # VULN-06: FRJ en unidad mínima
    vip_pending_gal_expires_at: Optional[datetime] = Field(default=None)  # expiración del lote más antiguo
    vip_last_daily_gal_at: Optional[datetime] = Field(default=None)       # último momento en que se generó GAL diario (Xochimilco)
    vip_tiers_activated: Optional[str] = Field(default="[]")         # JSON array: ["coral", "dorado"]
    vip_auto_renew: bool = Field(default=False)                       # cobra automáticamente ~3 días antes de vencer

    @property
    def is_vip(self) -> bool:
        return self.vip_expires_at is not None and self.vip_expires_at > datetime.utcnow()

    @property
    def vip_bonus_table_slots(self) -> int:
        if not self.is_vip or not self.vip_tier:
            return 0
        return {"coral": 0, "dorado": 1, "axolite": 2}.get(self.vip_tier, 0)

    @property
    def vip_bonus_axolotito_slots(self) -> int:
        return 1 if self.is_vip and self.vip_tier == "axolite" else 0

    # DEPRECATED: Replaced by cave_level. Read-only legacy. No longer written to.
    webito_slots_unlocked: int = Field(default=1)