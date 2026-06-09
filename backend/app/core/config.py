from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional, Dict, Any

VIP_CONFIG: Dict[str, Any] = {
    "coral": {
        "price_axg": 400,
        "gal_daily": 40,
        "discount": 0.05,
        "capsulas_mensuales": {"bronce": 2},
        "table_bonus_slots": 0,
        "axolotito_bonus_slots": 0,
        "p2p_commission": 0.04,
        "jackpot_bonus": 0.0,
        "multiplayer_discount": 0.0,
        "welcome_gal": 200,
        "welcome_boosters": [],
        "popular": False,
    },
    "dorado": {
        "price_axg": 600,
        "gal_daily": 100,
        "discount": 0.12,
        "capsulas_mensuales": {"bronce": 2, "plata": 1},
        "table_bonus_slots": 1,
        "axolotito_bonus_slots": 0,
        "p2p_commission": 0.03,
        "jackpot_bonus": 0.0,
        "multiplayer_discount": 0.0,
        "welcome_gal": 500,
        "welcome_boosters": ["normal"],
        "popular": True,
    },
    "axolite": {
        "price_axg": 1800,
        "gal_daily": 200,
        "discount": 0.20,
        "capsulas_mensuales": {"bronce": 3, "plata": 2, "oro": 1},
        "table_bonus_slots": 2,
        "axolotito_bonus_slots": 1,
        "p2p_commission": 0.015,
        "jackpot_bonus": 0.05,
        "multiplayer_discount": 0.15,
        "welcome_gal": 1000,
        "welcome_boosters": ["foil"],
        "popular": False,
    },
}

# ── Moneda exclusiva para multijugador ────────────────────────────────────
# Por compliance legal, el juego multijugador SOLO acepta Frijolitos (FRJ).
# Axofichas (AXF) está prohibido en cualquier operación de lobby/salas/escrow.
MULTIPLAYER_CURRENCY: str = "frijolito"


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
    # En modo local, todo nuevo usuario recibe automáticamente este premio.
    DEV_AUTO_REWARD_AXF: float = 50000.0
    DEV_AUTO_REWARD_FRJ: float = 500000.0

    @model_validator(mode="after")
    def validate_usdc_address(self) -> 'Settings':
        if self.BLOCKCHAIN_MODE != "local" and not self.USDC_ADDRESS:
            raise ValueError("USDC_ADDRESS must be set in non-local environments")
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