from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional, Dict, Any

# ── VIP_CONFIG: montos monetarios en unidad mínima entera (VULN-06) ─────
# price_axg, welcome_gal → enteros. Descuentos/comisiones → basis points (0-10000).
VIP_CONFIG: Dict[str, Any] = {
    "coral": {
        "price_axg": 400 * (10 ** 6),        # 400 AXF
        "gal_daily": 40 * (10 ** 4),          # 40 FRJ/día
        "discount_bps": 500,                  # 5.00% (basis points)
        "capsulas_mensuales": {"bronce": 2},
        "table_bonus_slots": 0,
        "axolotito_bonus_slots": 0,
        "p2p_commission_bps": 400,            # 4.00%
        "jackpot_bonus_bps": 0,               # 0%
        "multiplayer_discount_bps": 0,        # 0%
        "welcome_gal": 200 * (10 ** 4),       # 200 FRJ
        "welcome_boosters": [],
        "popular": False,
        # legacy accessors kept for backward compat (set via __init__ below)
    },
    "dorado": {
        "price_axg": 600 * (10 ** 6),         # 600 AXF
        "gal_daily": 100 * (10 ** 4),         # 100 FRJ/día
        "discount_bps": 1200,                 # 12.00%
        "capsulas_mensuales": {"bronce": 2, "plata": 1},
        "table_bonus_slots": 1,
        "axolotito_bonus_slots": 0,
        "p2p_commission_bps": 300,            # 3.00%
        "jackpot_bonus_bps": 0,               # 0%
        "multiplayer_discount_bps": 0,        # 0%
        "welcome_gal": 500 * (10 ** 4),       # 500 FRJ
        "welcome_boosters": ["normal"],
        "popular": True,
    },
    "axolite": {
        "price_axg": 1800 * (10 ** 6),        # 1800 AXF
        "gal_daily": 200 * (10 ** 4),         # 200 FRJ/día
        "discount_bps": 2000,                 # 20.00%
        "capsulas_mensuales": {"bronce": 3, "plata": 2, "oro": 1},
        "table_bonus_slots": 2,
        "axolotito_bonus_slots": 1,
        "p2p_commission_bps": 150,            # 1.50%
        "jackpot_bonus_bps": 500,             # 5.00%
        "multiplayer_discount_bps": 1500,     # 15.00%
        "welcome_gal": 1000 * (10 ** 4),      # 1000 FRJ
        "welcome_boosters": ["foil"],
        "popular": False,
    },
}

# Backward-compat aliases: permitir acceso vía .get("discount") → devuelve float
for _tier, _cfg in VIP_CONFIG.items():
    _cfg.setdefault("discount", _cfg.get("discount_bps", 0) / 10000.0)
    _cfg.setdefault("p2p_commission", _cfg.get("p2p_commission_bps", 0) / 10000.0)
    _cfg.setdefault("jackpot_bonus", _cfg.get("jackpot_bonus_bps", 0) / 10000.0)
    _cfg.setdefault("multiplayer_discount", _cfg.get("multiplayer_discount_bps", 0) / 10000.0)

# ── Helpers de conversión frontend ↔ backend (VULN-06) ───────────────────
# El frontend envía/recibe montos en unidades humanas (float/string).
# El backend almacena en unidad mínima entera.
# Estas funciones convierten en ambas direcciones.

def axf_to_internal(human_amount: float) -> int:
    """Convierte AXF legible (ej. 250.5) a unidad mínima entera."""
    return int(round(human_amount * (10 ** AXF_DECIMALS_BACKEND)))

def frj_to_internal(human_amount: float) -> int:
    """Convierte FRJ legible (ej. 25.0) a unidad mínima entera."""
    return int(round(human_amount * (10 ** FRJ_DECIMALS_BACKEND)))

def axf_to_display(internal_amount: int) -> float:
    """Convierte AXF unidad mínima → legible (float con 6 decimales)."""
    return internal_amount / (10 ** AXF_DECIMALS_BACKEND)

def frj_to_display(internal_amount: int) -> float:
    """Convierte FRJ unidad mínima → legible (float con 4 decimales)."""
    return internal_amount / (10 ** FRJ_DECIMALS_BACKEND)


# ── Moneda exclusiva para multijugador ────────────────────────────────────
# Por compliance legal, el juego multijugador SOLO acepta Frijolitos (FRJ).
# Axofichas (AXF) está prohibido en cualquier operación de lobby/salas/escrow.
MULTIPLAYER_CURRENCY: str = "frijolito"

# ── Precisión de saldos monetarios (unidad mínima entera) ──────────────────
# Todos los saldos y montos se almacenan como enteros en la unidad más pequeña.
# Esto elimina errores de redondeo IEEE-754 (VULN-06: "dust farming").
#
# 1 AXF = 1_000_000 unidades mínimas (6 decimales)
# 1 FRJ =    10_000 unidades mínimas (4 decimales)
#
# Para mostrar al usuario:  display = amount / DECIMALS
# Para recibir del usuario:  internal = int(input * DECIMALS)
AXF_DECIMALS_BACKEND: int = 6
FRJ_DECIMALS_BACKEND: int = 4

# Factores de conversión: multiplicar una cantidad en unidad mínima de backend
# por este factor para obtener wei (18 decimales) on-chain.
#   backend → wei:  amount * 10**(18 - DECIMALS)
#   wei → backend:  wei_amount // 10**(18 - DECIMALS)
AXF_BACKEND_TO_WEI_FACTOR: int = 10 ** (18 - 6)   # 10^12
FRJ_BACKEND_TO_WEI_FACTOR: int = 10 ** (18 - 4)   # 10^14


class Settings(BaseSettings):
    IS_MOCK_WEB3: bool = False
    DATABASE_URL: str

    # ── Modo de Blockchain ────────────────────────────────────────────────────
    # "local"        = Anvil local (simulaciones / desarrollo)
    # "polygon_amoy" = Polygon Amoy Testnet (staging / pre-producción)
    BLOCKCHAIN_MODE: str = "local"

    # Polygon Amoy Testnet (staging)
    POLYGON_AMOY_RPC_URL: str = "https://rpc-amoy.polygon.technology"

    # Anvil local (desarrollo)
    ANVIL_RPC_URL: str = "http://127.0.0.1:8545"

    # ── Treasury (Admin Wallet) ───────────────────────────────────────────────
    TREASURY_PRIVATE_KEY: str

    # ── Direcciones de Contratos ──────────────────────────────────────────────
    # ERC-20
    AXOGEMA_ADDRESS: str = ""
    GEMA_ALGA_ADDRESS: str = ""

    # ERC-721
    WEBITOS_ADDRESS: str = ""
    AXOLOTITOS_ADDRESS: Optional[str] = None
    TABLAS_ADDRESS: Optional[str] = None

    # ERC-1155
    CARDS_ADDRESS: str = ""
    BOOSTERS_ADDRESS: str = ""
    CONSUMABLES_ADDRESS: Optional[str] = None

    # Orquestador
    GAME_CONTROLLER_ADDRESS: Optional[str] = None
    
    # ── NPC System Wallet ────────────────────────────────────────────────────
    # Wallet that receives minted NPC boards on-chain.
    # Defaults to Anvil account[9] for local dev.
    NPC_WALLET_ADDRESS: str = "0xa0Ee7A142d267C1f36714E4a8F75612F20a79720"

    # ── Checkout / Cripto ────────────────────────────────────────────────────
    USDC_ADDRESS: str = ""   # Contrato USDC en Polygon Amoy (ERC-20, 6 decimales)

    # ── Auth & Admin ──────────────────────────────────────────────────────────
    # Privy App ID for JWT Verification
    PRIVY_APP_ID: Optional[str] = None

    # Dev-only auth bypass — gates X-Dev-User header and unverified JWT decoding.
    # NEVER set to True in production.
    ALLOW_DEV_AUTH: bool = False

    # Dev-only payment bypass — makes verify_usdc_payment return True for mock hashes.
    # Decoupled from BLOCKCHAIN_MODE so a local-mode deploy cannot silently skip payment checks.
    # NEVER set to True in production.
    ALLOW_DEV_PAYMENTS: bool = False

    # Admin API Key
    TRIDY_API_KEY: Optional[str] = None

    ADMIN_PRIVY_DID: Optional[str] = None   # legacy: single admin DID (backward compat)
    ADMIN_PRIVY_DIDS: str = ""              # comma-separated admin DIDs (takes precedence)

    @property
    def admin_dids(self) -> list[str]:
        """Return list of admin Privy DIDs combining ADMIN_PRIVY_DIDS + ADMIN_PRIVY_DID fallback."""
        dids: list[str] = []
        if self.ADMIN_PRIVY_DIDS:
            dids.extend(d.strip() for d in self.ADMIN_PRIVY_DIDS.split(",") if d.strip())
        if self.ADMIN_PRIVY_DID and self.ADMIN_PRIVY_DID not in dids:
            dids.append(self.ADMIN_PRIVY_DID)
        return dids
    SIMULATION_REPORT_PATH: str = "/app/simulation_report.txt"

    # ── Dev Corcholata Auto-Reward ────────────────────────────────────────────
    # Movido a backend/app/api/v1/endpoints/dev.py como constantes del módulo.
    # Importar desde ahí si se necesita en modo local:
    #   from app.api.v1.endpoints.dev import DEV_AUTO_REWARD_AXF, DEV_AUTO_REWARD_FRJ

    @model_validator(mode="after")
    def validate_usdc_address(self) -> 'Settings':
        if self.BLOCKCHAIN_MODE != "local" and not self.USDC_ADDRESS:
            raise ValueError("USDC_ADDRESS must be set in non-local environments")
        return self

    @model_validator(mode="after")
    def _enforce_auth(self) -> 'Settings':
        if self.BLOCKCHAIN_MODE != "local" and not self.PRIVY_APP_ID:
            raise ValueError(
                "PRIVY_APP_ID es obligatorio cuando BLOCKCHAIN_MODE != 'local'. "
                "Configura PRIVY_APP_ID en el .env antes de arrancar."
            )
        if self.ALLOW_DEV_AUTH and self.BLOCKCHAIN_MODE != "local":
            raise ValueError(
                "ALLOW_DEV_AUTH=True está prohibido fuera de modo local. "
                "Elimínalo del .env de producción."
            )
        return self

    @property
    def rpc_url(self) -> str:
        """Devuelve la URL RPC correcta según el modo de blockchain."""
        if self.BLOCKCHAIN_MODE == "local":
            return self.ANVIL_RPC_URL
        return self.POLYGON_AMOY_RPC_URL

    @property
    def chain_id(self) -> int:
        """Chain ID según el modo: 31337=Anvil local, 80002=Polygon Amoy."""
        if self.BLOCKCHAIN_MODE == "local":
            return 31337
        return 80002

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()