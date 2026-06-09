from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint
import uuid

class CurrencyType(str, Enum):
    # Monedas canónicas (nuevas)
    AXOFICHA = "axoficha"          # Moneda Premium (SPEI)
    FRIJOLITO = "frijolito"        # Moneda de Juego
    # Legacy — DB tiene registros con estos nombres (NO BORRAR)
    AXOGEMA = "axogema"            # Nombre antiguo para premium
    GEMA_ALGA = "gema_alga"        # Nombre antiguo para juego
    # Fragmentos
    FRAGMENTO_COMUN = "frag_c"     # Fragmentos para crafteo
    FRAGMENTO_RARO = "frag_r"
    FRAGMENTO_EPICO = "frag_e"
    FRAGMENTO_LEGENDARIO = "frag_l"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"          # Carga de saldo (Admin/SPEI)
    WITHDRAW = "withdraw"        # Retiro
    P2P_SEND = "p2p_send"        # Envío a amigo
    P2P_RECEIVE = "p2p_receive"  # Recepción de amigo
    MARKET_BUY = "market_buy"    # Compra en el mercado
    MARKET_SELL = "market_sell"  # Venta en el mercado
    REWARD = "reward"            # Premio por jugar/retos
    BOOSTER_PURCHASE = "booster" # Compra de sobres
    CRAFTING = "crafting"        # Gasto de fragmentos para crear carta
    BURN = "burn"                # Quema de tokens (comisiones de plataforma)
    VIP_GAL_EXPIRED = "vip_gal_expired"  # GAL VIP que expiró sin reclamar
    F2P_REWARD = "f2p_reward"            # Micro-recompensa por ver partidas (jugador F2P)
    TUTORIAL_BONUS = "tutorial_bonus"    # Bonus otorgado al completar el tutorial
    WEBITO_UNLOCK = "webito_unlock"      # Desbloqueo de slot de Webito
    PROMO_REWARD = "promo_reward"        # Tokens obsequiados por corcholata/código promo
    STAKING_REWARD = "staking_reward"    # Recompensa pasiva por tener Axolotitos en staking
    ARCADE_PLAY = "arcade_play"          # Minijuego Arcade del Cenote

class Wallet(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("axofichas >= 0", name="axofichas_non_negative"),
        CheckConstraint("frijolitos >= 0", name="frijolitos_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", unique=True)
    
    # Saldos actuales (Caché rápida)
    axofichas: float = Field(default=0.0)
    frijolitos: float = Field(default=0.0)

    @property
    def axogemas(self) -> float:
        return self.axofichas

    @axogemas.setter
    def axogemas(self, value: float) -> None:
        self.axofichas = value

    @property
    def gemas_alga(self) -> float:
        return self.frijolitos

    @gemas_alga.setter
    def gemas_alga(self, value: float) -> None:
        self.frijolitos = value

    def __init__(self, **data):
        if "axogemas" in data:
            data["axofichas"] = data.pop("axogemas")
        if "gemas_alga" in data:
            data["frijolitos"] = data.pop("gemas_alga")
        super().__init__(**data)
    
    # Fragmentos (Se guardan como enteros porque no hay "medio fragmento")
    frag_comun: int = Field(default=0)
    frag_raro: int = Field(default=0)
    frag_epico: int = Field(default=0)
    frag_legendario: int = Field(default=0)

    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TransactionLedger(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    
    amount: float
    currency: CurrencyType
    tx_type: TransactionType
    
    # Para rastrear P2P (quién mandó a quién)
    related_user_id: Optional[str] = None 
    
    # Para vincular transacciones con ítems del catálogo
    item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", index=True)
    
    # Para auditoría: ¿cuánta comisión se quedó la casa?
    fee_applied: float = Field(default=0.0)
    
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Hash de seguridad opcional para detectar alteraciones
    # tx_hash: Optional[str] = None


class OrderStatus(str, Enum):
    AWAITING_PAYMENT = "awaiting_payment"
    CONFIRMING       = "confirming"
    COMPLETED        = "completed"
    EXPIRED          = "expired"
    FAILED           = "failed"


class CryptoPurchaseOrder(SQLModel, table=True):
    """Orden de compra de AXG con cripto. Cada orden corresponde a un pack."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    pack_id: str                          # "huevito" | "axolotito" | "cenote" | "jackpot"
    usd_amount: float
    usdc_amount: float                    # usd_amount + 1% buffer para slippage
    axg_amount: float                     # AXG a mintear (base + bonus ya calculado)
    payment_token: str = "USDC"
    treasury_address: str                 # dirección donde el jugador debe enviar
    tx_hash_payment: Optional[str] = Field(default=None, unique=True)  # anti double-mint
    tx_hash_mint: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.AWAITING_PAYMENT)
    bonus_applied: Optional[str] = None  # "first_purchase" | "flash_sale"
    bonus_pct: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime                  # created_at + 30 min
    completed_at: Optional[datetime] = None


class ProcessedTransaction(SQLModel, table=True):
    """Registro de transacciones blockchain procesadas. Previene ataques de replay."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tx_hash: str = Field(unique=True, index=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    purpose: str  # "checkout_usdc" | futuras fuentes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CryptoPaymentAttempt(SQLModel, table=True):
    """Log de todos los intentos de verificación de pagos crypto (audit trail)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(foreign_key="cryptopurchaseorder.id", index=True)
    tx_hash: str = Field(index=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    status: str  # "success" | "failed"
    error_detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AxfPurchaseRecord(SQLModel, table=True):
    """Registro de compras de AXF con pesos (MXN)."""
    __tablename__: str = "axf_purchase_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    axf_amount: float
    mxn_amount: float
    pack_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        if "axg_amount" in data:
            data["axf_amount"] = data.pop("axg_amount")
        super().__init__(**data)

    @property
    def axg_amount(self) -> float:
        return self.axf_amount

    @axg_amount.setter
    def axg_amount(self, value: float) -> None:
        self.axf_amount = value

AxgPurchaseRecord = AxfPurchaseRecord