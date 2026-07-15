from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional, Dict, Any

# ── VIP_CONFIG: montos monetarios en unidad mínima entera (VULN-06) ─────
# price_axg, welcome_gal → enteros. Descuentos/comisiones → basis points (0-10000).
# Rediseño §1 del plan económico (docs/plan_economia_devex_fintech.md):
# valor de conveniencia y estatus — sin bonos que multipliquen ganancias
# ni pozos de azar (jackpot_bonus_bps=0 en todos los niveles, cortafuegos legal).
VIP_CONFIG: Dict[str, Any] = {
    "coral": {
        "price_axg": 50 * (10 ** 6),          # 50 AXF (~$100 MXN/mes)
        "gal_daily": 20 * (10 ** 4),          # 20 FRJ/día
        "discount_bps": 500,                  # 5.00% descuento tienda
        "capsulas_mensuales": {"bronce": 2},
        "table_bonus_slots": 0,
        "axolotito_bonus_slots": 0,
        "p2p_commission_bps": 400,            # 4.00%
        "jackpot_bonus_bps": 0,               # 0% — prohibido multiplicar pozos de azar
        "multiplayer_discount_bps": 0,        # 0% — prohibido multiplicar ganancias
        "welcome_gal": 200 * (10 ** 4),       # 200 FRJ bienvenida
        "welcome_boosters": [],
        "popular": False,
    },
    "dorado": {
        "price_axg": 120 * (10 ** 6),         # 120 AXF (~$240 MXN/mes)
        "gal_daily": 50 * (10 ** 4),          # 50 FRJ/día
        "discount_bps": 1200,                 # 12.00% descuento tienda
        "capsulas_mensuales": {"bronce": 2, "plata": 1},
        "table_bonus_slots": 1,
        "axolotito_bonus_slots": 0,
        "p2p_commission_bps": 300,            # 3.00%
        "jackpot_bonus_bps": 0,               # 0% — prohibido multiplicar pozos de azar
        "multiplayer_discount_bps": 0,        # 0% — prohibido multiplicar ganancias
        "welcome_gal": 500 * (10 ** 4),       # 500 FRJ bienvenida
        "welcome_boosters": ["normal"],
        "popular": True,
    },
    "axolite": {
        "price_axg": 300 * (10 ** 6),         # 300 AXF (~$600 MXN/mes)
        "gal_daily": 130 * (10 ** 4),         # 130 FRJ/día
        "discount_bps": 2000,                 # 20.00% descuento tienda
        "capsulas_mensuales": {"bronce": 3, "plata": 2, "oro": 1},
        "table_bonus_slots": 2,
        "axolotito_bonus_slots": 1,
        "p2p_commission_bps": 200,            # 2.00%
        "jackpot_bonus_bps": 0,               # 0% — prohibido multiplicar pozos de azar
        "multiplayer_discount_bps": 0,        # 0% — prohibido multiplicar ganancias
        "welcome_gal": 1000 * (10 ** 4),      # 1000 FRJ bienvenida
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

# ── Ley económica (§1 del plan): 1 AXF = $2.00 MXN fijo ───────────────────
# Relación lineal estricta para evitar arbitrajes. En centavos MXN.
AXF_MXN_CENTS: int = 200

# Factores de conversión: multiplicar una cantidad en unidad mínima de backend
# por este factor para obtener wei (18 decimales) on-chain.
#   backend → wei:  amount * 10**(18 - DECIMALS)
#   wei → backend:  wei_amount // 10**(18 - DECIMALS)
AXF_BACKEND_TO_WEI_FACTOR: int = 10 ** (18 - 6)   # 10^12
FRJ_BACKEND_TO_WEI_FACTOR: int = 10 ** (18 - 4)   # 10^14


class Settings(BaseSettings):
    IS_MOCK_WEB3: bool = False
    DATABASE_URL: str

    # ── Product policy: non-gambling by default ──────────────────────────
    # `legacy_simulation` exists only so local balance/test tooling can inspect
    # the previous economy. It is rejected outside BLOCKCHAIN_MODE=local.
    PRODUCT_MODE: str = "non_gambling"  # non_gambling | legacy_simulation

    # Every value-bearing feature is fail-closed. Enabling commerce later also
    # requires legal identity, versioned terms/privacy and adult gating.
    ENABLE_FIAT_PAYMENTS: bool = False
    ENABLE_CRYPTO_CHECKOUT: bool = False
    ENABLE_PLAYER_MARKETPLACE: bool = False
    ENABLE_CREATOR_PAYOUTS: bool = False
    ENABLE_VIP_SALES: bool = False
    ENABLE_FREE_GAMEPLAY: bool = True
    ENABLE_PAID_GAMEPLAY: bool = False
    ENABLE_GAMEPLAY_TOKEN_REWARDS: bool = False
    ENABLE_JACKPOT: bool = False
    ENABLE_PURCHASED_RANDOM_REWARDS: bool = False
    ENABLE_TOKEN_CASHOUT: bool = False
    ENABLE_PLAYER_TOKEN_TRANSFERS: bool = False
    ENABLE_CLIENT_REPORTED_REWARDS: bool = False
    ENABLE_PROMOTIONAL_TOKEN_REWARDS: bool = False
    ENABLE_ADMIN_TOKEN_MINTS: bool = False
    ENABLE_ADMIN_BALANCE_ADJUSTMENTS: bool = False
    ENABLE_PASSIVE_TOKEN_REWARDS: bool = False
    ENABLE_LEGACY_ASSET_CLAIMS: bool = False
    ENABLE_FIXED_ITEM_SHOP: bool = False
    ENABLE_FIXED_GAMEPLAY_SPENDING: bool = False
    ENABLE_CARD_CRAFTING: bool = False
    ENABLE_BOARD_ASSET_MUTATIONS: bool = False
    ENABLE_HATCHING: bool = False
    ENABLE_RECICLON: bool = False

    REQUIRE_ADULT_FOR_COMMERCE: bool = True
    CHAIN_ECONOMY_AUTHORITATIVE: bool = True

    PAYMENT_GATEWAY_PROVIDER: str = "mock"
    KYC_PROVIDER: str = ""
    LEGAL_ENTITY_NAME: str = ""
    TERMS_VERSION: str = ""
    PRIVACY_NOTICE_VERSION: str = ""

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

    # ── Tianguis P2P fiat (docs/plan_economia_devex_fintech.md) ──────────────
    MARKET_ESCROW_ADDRESS: str = ""          # contrato MarketEscrow.sol
    PAYMENT_WEBHOOK_SECRET: str = "axolotto_dev_webhook_secret"  # HMAC webhooks pasarela
    P2P_QUARANTINE_HOURS: int = 72           # cuarentena AXF_Earned (§4 AML)

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
    CHAOS_SIMULATION_REPORT_PATH: str = "/app/chaos_simulation_report.txt"
    CHAOS_SIMULATION_PROGRESS_PATH: str = "/app/chaos_simulation_progress.log"

    # ── El Reciclón — economía de reciclaje de cartas ─────────────────────────
    # Tickets obtenidos al reciclar 1 carta duplicada (según rareza).
    # Ratio 5:1 — reciclar 5 de una rareza da justo para comprar 1 de esa misma.
    RECYCLE_TICKETS_COMMON: int = 3
    RECYCLE_TICKETS_RARE: int = 9
    RECYCLE_TICKETS_EPIC: int = 30
    RECYCLE_TICKETS_LEGENDARY: int = 100
    # Costo en tickets para canjear 1 carta específica del catálogo.
    REDEEM_COST_COMMON: int = 15
    REDEEM_COST_RARE: int = 45
    REDEEM_COST_EPIC: int = 150
    REDEEM_COST_LEGENDARY: int = 500
    # Dirección del ReciclonVault — contrato de custodia para cartas recicladas.
    # Si está vacío, las cartas recicladas solo se borran de la DB (sin on-chain).
    RECICLON_VAULT_ADDRESS: str = ""
    # Feature flag: activa operaciones on-chain en El Reciclón (transferCard al vault).
    # False = solo DB (default). True = enqueua ChainOutbox para transferir cartas al vault.
    RECICLON_ONCHAIN_ENABLED: bool = False

    # ── Dev Corcholata Auto-Reward ────────────────────────────────────────────
    # Movido a backend/app/api/v1/endpoints/dev.py como constantes del módulo.
    # Importar desde ahí si se necesita en modo local:
    #   from app.api.v1.endpoints.dev import DEV_AUTO_REWARD_AXF, DEV_AUTO_REWARD_FRJ

    @model_validator(mode="after")
    def _enforce_product_policy(self) -> 'Settings':
        mode = self.PRODUCT_MODE.strip().lower()
        if mode not in {"non_gambling", "legacy_simulation"}:
            raise ValueError(
                "PRODUCT_MODE debe ser 'non_gambling' o 'legacy_simulation'."
            )
        self.PRODUCT_MODE = mode

        if self.ALLOW_DEV_PAYMENTS and not (
            mode == "legacy_simulation" and self.BLOCKCHAIN_MODE == "local"
        ):
            raise ValueError(
                "ALLOW_DEV_PAYMENTS=True requiere "
                "PRODUCT_MODE=legacy_simulation y BLOCKCHAIN_MODE=local."
            )

        if mode == "legacy_simulation":
            if self.BLOCKCHAIN_MODE != "local":
                raise ValueError(
                    "PRODUCT_MODE=legacy_simulation está prohibido fuera de local."
                )
            return self

        prohibited = {
            "ENABLE_PAID_GAMEPLAY": self.ENABLE_PAID_GAMEPLAY,
            "ENABLE_JACKPOT": self.ENABLE_JACKPOT,
            "ENABLE_PURCHASED_RANDOM_REWARDS": self.ENABLE_PURCHASED_RANDOM_REWARDS,
            "ENABLE_TOKEN_CASHOUT": self.ENABLE_TOKEN_CASHOUT,
            "ENABLE_PLAYER_TOKEN_TRANSFERS": self.ENABLE_PLAYER_TOKEN_TRANSFERS,
            "ENABLE_CLIENT_REPORTED_REWARDS": self.ENABLE_CLIENT_REPORTED_REWARDS,
            "ENABLE_ADMIN_TOKEN_MINTS": self.ENABLE_ADMIN_TOKEN_MINTS,
            "ENABLE_ADMIN_BALANCE_ADJUSTMENTS": self.ENABLE_ADMIN_BALANCE_ADJUSTMENTS,
            "ENABLE_PASSIVE_TOKEN_REWARDS": self.ENABLE_PASSIVE_TOKEN_REWARDS,
            "ENABLE_LEGACY_ASSET_CLAIMS": self.ENABLE_LEGACY_ASSET_CLAIMS,
            "ENABLE_FIXED_ITEM_SHOP": self.ENABLE_FIXED_ITEM_SHOP,
            "ENABLE_FIXED_GAMEPLAY_SPENDING": self.ENABLE_FIXED_GAMEPLAY_SPENDING,
            "ENABLE_CARD_CRAFTING": self.ENABLE_CARD_CRAFTING,
            # Current marketplace routes exchange player inventory for FRJ and
            # are not the future MXN creator-sales ledger.
            "ENABLE_PLAYER_MARKETPLACE": self.ENABLE_PLAYER_MARKETPLACE,
            "ENABLE_CREATOR_PAYOUTS": self.ENABLE_CREATOR_PAYOUTS,
            # Current VIP accrues token yield and jackpot advantages.
            "ENABLE_VIP_SALES": self.ENABLE_VIP_SALES,
            # These contracts still rely on controller-forced approvals or
            # delivery authority. Keep public writes off until user-signed
            # intents and finalized-event projections replace those paths.
            "ENABLE_BOARD_ASSET_MUTATIONS": self.ENABLE_BOARD_ASSET_MUTATIONS,
            "ENABLE_HATCHING": self.ENABLE_HATCHING,
            # The current backend credits tickets before final chain receipt.
            # Keep this impossible in the public mode until the projection is
            # driven by finalized vault events and user-signed transfers.
            "ENABLE_RECICLON": self.ENABLE_RECICLON,
        }
        enabled_prohibited = [name for name, enabled in prohibited.items() if enabled]
        if enabled_prohibited:
            raise ValueError(
                "PRODUCT_MODE=non_gambling prohíbe: "
                + ", ".join(enabled_prohibited)
            )

        if self.ENABLE_GAMEPLAY_TOKEN_REWARDS and (
            self.ENABLE_TOKEN_CASHOUT or self.ENABLE_PLAYER_TOKEN_TRANSFERS
        ):
            raise ValueError(
                "Las recompensas de juego no pueden ser transferibles o canjeables."
            )

        commercial_features = {
            "ENABLE_FIAT_PAYMENTS": self.ENABLE_FIAT_PAYMENTS,
            "ENABLE_CRYPTO_CHECKOUT": self.ENABLE_CRYPTO_CHECKOUT,
            "ENABLE_PLAYER_MARKETPLACE": self.ENABLE_PLAYER_MARKETPLACE,
            "ENABLE_CREATOR_PAYOUTS": self.ENABLE_CREATOR_PAYOUTS,
            "ENABLE_VIP_SALES": self.ENABLE_VIP_SALES,
        }
        enabled_commerce = [name for name, enabled in commercial_features.items() if enabled]
        if enabled_commerce:
            missing = []
            if not self.REQUIRE_ADULT_FOR_COMMERCE:
                missing.append("REQUIRE_ADULT_FOR_COMMERCE")
            if not self.LEGAL_ENTITY_NAME.strip():
                missing.append("LEGAL_ENTITY_NAME")
            if not self.TERMS_VERSION.strip():
                missing.append("TERMS_VERSION")
            if not self.PRIVACY_NOTICE_VERSION.strip():
                missing.append("PRIVACY_NOTICE_VERSION")
            if missing:
                raise ValueError(
                    "No se puede habilitar comercio sin: " + ", ".join(missing)
                )

        if self.ENABLE_FIAT_PAYMENTS and self.PAYMENT_GATEWAY_PROVIDER.lower() == "mock":
            raise ValueError(
                "ENABLE_FIAT_PAYMENTS requiere una pasarela real, no mock."
            )

        if self.ENABLE_CREATOR_PAYOUTS:
            if not self.ENABLE_PLAYER_MARKETPLACE:
                raise ValueError(
                    "Creator payouts requieren ENABLE_PLAYER_MARKETPLACE."
                )
            if not self.KYC_PROVIDER.strip():
                raise ValueError("Creator payouts requieren KYC_PROVIDER.")

        if (
            self.CHAIN_ECONOMY_AUTHORITATIVE
            and self.BLOCKCHAIN_MODE != "local"
            and self.IS_MOCK_WEB3
        ):
            raise ValueError(
                "La economía chain-authoritative no permite IS_MOCK_WEB3 fuera de local."
            )

        return self

    @model_validator(mode="after")
    def validate_usdc_address(self) -> 'Settings':
        if (
            self.BLOCKCHAIN_MODE != "local"
            and self.ENABLE_CRYPTO_CHECKOUT
            and not self.USDC_ADDRESS
        ):
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
        if (
            self.BLOCKCHAIN_MODE != "local"
            and self.ENABLE_FIAT_PAYMENTS
            and self.PAYMENT_WEBHOOK_SECRET == "axolotto_dev_webhook_secret"
        ):
            raise ValueError(
                "PAYMENT_WEBHOOK_SECRET debe configurarse con un valor propio "
                "fuera de modo local (firma HMAC de webhooks de pago)."
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
