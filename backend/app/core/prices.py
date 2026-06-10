# 🃏 Centralized Price and Token Conversions Config for Axolotto
#
# ⚠️ VULN-06 Remediation: Todos los montos monetarios se almacenan como enteros
# en la unidad más pequeña. Ver core/config.py para los factores de conversión.
#
#   AXF: multiplicar por 10**6  (AXF_DECIMALS_BACKEND = 6)
#   FRJ: multiplicar por 10**4  (FRJ_DECIMALS_BACKEND = 4)
#
# Los montos NO monetarios (porcentajes, ratios, XP) se mantienen sin cambios.

from app.core.config import AXF_DECIMALS_BACKEND, FRJ_DECIMALS_BACKEND

_AXF = 10 ** AXF_DECIMALS_BACKEND   # 1_000_000
_FRJ = 10 ** FRJ_DECIMALS_BACKEND   #    10_000

# --- TIPO DE CAMBIO NOMINAL (Para fallback/referencias) ---
# Paquete más barato: 200 FRJ = $35 MXN → 1 FRJ ≈ $0.175 MXN
NOMINAL_AXF_PRICE_MXN = 2.00  # 1 AXF = $2 MXN nominal
DEVEX_RATE_70_GROSS = 1.40   # 70% del bruto ($1.40 MXN payout)
DEVEX_RATE_70_NET = 1.14     # 70% del neto ($1.14 MXN payout)
DEVEX_RATE_50_GROSS = 1.00   # 50% del bruto ($1.00 MXN payout)

# --- WEBITOS (EGG CATALOG) — precios en AXF ---
WEBITO_PRICES = {
    1: 400 * _AXF,     # Fase 1 (Génesis)
    2: 800 * _AXF,     # Fase 2 (Expansión)
    3: 1200 * _AXF,    # Fase 3 (Retail)
    "astral": 3000 * _AXF,  # Astral
}

# --- BOOSTERS CATALOG ---
# Cada entrada: {"axg": precio_premium (AXF), "gal": precio_earned (FRJ)}
BOOSTER_PRICES = {
    # Fase 1 (First Edition)
    1: {
        "fiesta": {"axg": 10 * _AXF, "gal": 100 * _FRJ},
        "nido":   {"axg": 10 * _AXF, "gal": 100 * _FRJ},
        "cosmos": {"axg": 10 * _AXF, "gal": 100 * _FRJ},
        "pure":   {"axg":  6 * _AXF, "gal":  60 * _FRJ},
    },
    # Fase 2 (Unlimited)
    2: {
        "fiesta": {"axg": 15 * _AXF, "gal": 150 * _FRJ},
        "nido":   {"axg": 15 * _AXF, "gal": 150 * _FRJ},
        "cosmos": {"axg": 15 * _AXF, "gal": 150 * _FRJ},
        "pure":   {"axg": 10 * _AXF, "gal": 100 * _FRJ},
    },
    # Fase 3 (Retail / Standard)
    3: {
        "fiesta": {"axg": 20 * _AXF, "gal": 200 * _FRJ},
        "nido":   {"axg": 20 * _AXF, "gal": 200 * _FRJ},
        "cosmos": {"axg": 20 * _AXF, "gal": 200 * _FRJ},
        "pure":   {"axg": 15 * _AXF, "gal": 150 * _FRJ},
    },
    "foil": {"axg": 80 * _AXF, "gal": 800 * _FRJ},  # Booster Brillante
}

# --- GASHAPON COSTS (FRJ) ---
GASHAPON_TIER_COSTS = {
    "bronce": 1500 * _FRJ,
    "plata": 5000 * _FRJ,
    "oro": 20000 * _FRJ,
    "triple": 22500 * _FRJ,
}

# --- CONSUMIBLES ---
# Convención de nombres en claves:
#   Las que contienen "vip_" o "lampara" o "upgrade" → AXF (multiplicar por _AXF)
#   Las demás → FRJ (multiplicar por _FRJ)
CONSUMABLE_PRICES = {
    "gotas": 200 * _FRJ,                # Gotas Anti-Escarcha (FRJ)
    "lampara": 200 * _AXF,              # Lámpara Infrarroja Pro (AXF)
    "vip_coral": 400 * _AXF,            # Pase Coral VIP 30 días (AXF)
    "vip_dorado": 600 * _AXF,           # Pase Dorado VIP 30 días (AXF)
    "vip_axolite": 1800 * _AXF,         # Pase Axolite VIP 30 días (AXF)
    "alimento_comun": 30 * _FRJ,        # Algae Pellet (FRJ)
    "alimento_premium": 150 * _FRJ,     # Brine Shrimp (FRJ)
    "solvente": 120 * _FRJ,             # Solvente de Pegamento (FRJ)
    "upgrade_board_slots": 300 * _AXF,  # Upgrade Board Slots (AXF)
}

# --- TABLAS DE JUEGO (BOARD) ---
BOARD_PRICES = {
    "clasica": {"axg": 10 * _AXF, "gal": 130 * _FRJ},
    "suerte":  {"axg": 50 * _AXF, "gal": 520 * _FRJ},
    "plasma":  {"axg": 150 * _AXF, "gal": 1560 * _FRJ},
    "cosmica": {"axg": 200 * _AXF, "gal": 0},
}

# --- BOARD SLOTS DESBLOQUEOS (FRJ) ---
BOARD_SLOT_COSTS = {
    4: 500 * _FRJ,
    5: 1000 * _FRJ,
    6: 2000 * _FRJ,
    7: 4000 * _FRJ,
    8: 8000 * _FRJ,
    9: 15000 * _FRJ,
}

# --- MULTIPLAYER FEES (FRJ) ---
# Solo 2 salas públicas oficiales (rookie_pool y champion_abyss).
# Basado en: paquete más barato = 200 FRJ por $35 MXN.
#   → Rookie:  25 FRJ ($4.38 MXN) — 8 juegos por paquete
#   → Champion: 100 FRJ ($17.50 MXN) — 2 juegos por paquete
# Player-hosted (cave) rooms usan buy_in_frj configurable.
MULTIPLAYER_FEES = {
    "rookie_pool": 25 * _FRJ,
    "champion_abyss": 100 * _FRJ,
    # Legacy keys — mantener para compatibilidad con datos existentes
    "rookie": 25 * _FRJ,
    "champion": 100 * _FRJ,
}

# --- MULTIPLAYER ROOMS CONFIG ---
# fee, prize, consolation en FRJ (multiplicar por _FRJ)
# XP se mantiene como entero (no es monto monetario)
MULTIPLAYER_ROOMS = {
    "rookie_pool": {
        "title": "Charco de Novatos",
        "difficulty_label": "Fácil",
        "fee": 25 * _FRJ,
        "prize": 85 * _FRJ,
        "consolation": 8 * _FRJ,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion_abyss": {
        "title": "Fosa del Campeón",
        "difficulty_label": "Difícil",
        "fee": 100 * _FRJ,
        "prize": 400 * _FRJ,
        "consolation": 20 * _FRJ,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
    # Legacy keys — mantener para compatibilidad
    "rookie": {
        "fee": 25 * _FRJ,
        "prize": 85 * _FRJ,
        "consolation": 8 * _FRJ,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion": {
        "fee": 100 * _FRJ,
        "prize": 400 * _FRJ,
        "consolation": 20 * _FRJ,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
}
