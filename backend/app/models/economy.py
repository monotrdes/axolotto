from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint, Column, BigInteger
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
    # Tickets de El Reciclón
    TICKET_RECICLON = "ticket_reciclon"

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
    RECICLON_RECYCLE = "reciclon_recycle"  # Recicló cartas duplicadas → tickets
    RECICLON_REDEEM = "reciclon_redeem"    # Canjeó tickets → carta específica
    BURN = "burn"                # Quema de tokens (comisiones de plataforma)
    VIP_GAL_EXPIRED = "vip_gal_expired"  # GAL VIP que expiró sin reclamar
    F2P_REWARD = "f2p_reward"            # Micro-recompensa por ver partidas (jugador F2P)
    TUTORIAL_BONUS = "tutorial_bonus"    # Bonus otorgado al completar el tutorial
    WEBITO_UNLOCK = "webito_unlock"      # Desbloqueo de slot de Webito
    PROMO_REWARD = "promo_reward"        # Tokens obsequiados por corcholata/código promo
    STAKING_REWARD = "staking_reward"    # Recompensa pasiva por tener Axolotitos en staking

class Wallet(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("axofichas >= 0", name="axofichas_non_negative"),
        CheckConstraint("frijolitos >= 0", name="frijolitos_non_negative"),
        CheckConstraint("tickets_reciclon >= 0", name="tickets_reciclon_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", unique=True)

    # Saldos actuales en unidad mínima entera (VULN-06: sin float)
    # 1 AXF = 10**6 unidades mínimas, 1 FRJ = 10**4 unidades mínimas
    axofichas: int = Field(default=0, sa_column=Column(BigInteger, default=0, nullable=False))
    frijolitos: int = Field(default=0, sa_column=Column(BigInteger, default=0, nullable=False))

    @property
    def axogemas(self) -> float:
        from app.core.config import axf_to_display
        return axf_to_display(self.axofichas)

    @axogemas.setter
    def axogemas(self, value: float) -> None:
        from app.core.config import axf_to_internal
        self.axofichas = axf_to_internal(value)

    @property
    def gemas_alga(self) -> float:
        from app.core.config import frj_to_display
        return frj_to_display(self.frijolitos)

    @gemas_alga.setter
    def gemas_alga(self, value: float) -> None:
        from app.core.config import frj_to_internal
        self.frijolitos = frj_to_internal(value)

    def __init__(self, **data):
        from app.core.config import axf_to_internal, frj_to_internal
        if "axogemas" in data:
            val = data.pop("axogemas")
            data["axofichas"] = val if isinstance(val, int) and not isinstance(val, bool) else axf_to_internal(val)
        if "gemas_alga" in data:
            val = data.pop("gemas_alga")
            data["frijolitos"] = val if isinstance(val, int) and not isinstance(val, bool) else frj_to_internal(val)
        super().__init__(**data)
    
    # Fragmentos (Se guardan como enteros porque no hay "medio fragmento")
    # DEPRECATED: El Reciclón reemplaza fragmentos por tickets_reciclon.
    frag_comun: int = Field(default=0)
    frag_raro: int = Field(default=0)
    frag_epico: int = Field(default=0)
    frag_legendario: int = Field(default=0)

    # Tickets de El Reciclón — moneda única cross-rarity para reciclaje de cartas
    tickets_reciclon: int = Field(default=0)

    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TransactionLedger(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    
    amount: int = Field(sa_column=Column(BigInteger, nullable=False))
    currency: CurrencyType
    tx_type: TransactionType

    # Para rastrear P2P (quién mandó a quién)
    related_user_id: Optional[str] = None

    # Para vincular transacciones con ítems del catálogo
    item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", index=True)

    # Para auditoría: ¿cuánta comisión se quedó la casa? (unidad mínima)
    fee_applied: int = Field(default=0, sa_column=Column(BigInteger, default=0, nullable=False))
    
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
    """Orden de compra de AXF con cripto. Cada orden corresponde a un pack."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    pack_id: str                          # "huevito" | "axolotito" | "cenote" | "jackpot"
    usd_amount: float                     # USD fiat (referencia, 2 decimales)
    usdc_amount: int = Field(sa_column=Column(BigInteger, nullable=False))                      # USDC en unidad mínima (6 decimales)
    axg_amount: int = Field(sa_column=Column(BigInteger, nullable=False))                       # AXF en unidad mínima (6 decimales)
    payment_token: str = "USDC"
    treasury_address: str                 # dirección donde el jugador debe enviar
    tx_hash_payment: Optional[str] = Field(default=None, unique=True)  # anti double-mint
    tx_hash_mint: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.AWAITING_PAYMENT)
    bonus_applied: Optional[str] = None  # "first_purchase" | "flash_sale"
    bonus_pct: float = Field(default=0.0)  # porcentaje (0.0-1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime                  # created_at + 30 min
    completed_at: Optional[datetime] = None

    def __init__(self, **data):
        if "axf_amount" in data:
            data["axg_amount"] = data.pop("axf_amount")
        super().__init__(**data)

    @property
    def axf_amount(self) -> int:
        return self.axg_amount

    @axf_amount.setter
    def axf_amount(self, value: int) -> None:
        self.axg_amount = value


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


class ChainOutbox(SQLModel, table=True):
    """Outbox transaccional para operaciones on-chain.

    Patrón: la intención on-chain se persiste en la misma transacción DB que la
    mutación de estado. Un worker externo procesa las entradas con reintentos y
    backoff, garantizando eventual consistencia entre DB y blockchain.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    operation: str          # "mint_frj" | "burn_frj" | "mint_axf" | "transfer_card" | "transfer_board" | "update_board_stats"
    payload_json: str       # argumentos serializados en JSON
    status: str = Field(default="pending")  # pending | processing | confirmed | failed
    tx_hash: Optional[str] = Field(default=None, index=True)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=5)
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AxfPurchaseRecord(SQLModel, table=True):
    """Registro de compras de AXF con pesos (MXN)."""
    __tablename__: str = "axf_purchase_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    axf_amount: int = Field(sa_column=Column(BigInteger, nullable=False))                       # AXF en unidad mínima (6 decimales)
    mxn_amount: float                     # MXN fiat (referencia)
    pack_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        if "axg_amount" in data:
            data["axf_amount"] = data.pop("axg_amount")
        super().__init__(**data)

    @property
    def axg_amount(self) -> int:
        return self.axf_amount

    @axg_amount.setter
    def axg_amount(self, value: int) -> None:
        self.axf_amount = value

AxgPurchaseRecord = AxfPurchaseRecord