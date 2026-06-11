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
    "vip_coral": 50 * _AXF,             # Pase Coral VIP 30 días ($100 MXN)
    "vip_dorado": 120 * _AXF,           # Pase Dorado VIP 30 días ($240 MXN)
    "vip_axolite": 300 * _AXF,          # Pase Axolite VIP 30 días ($600 MXN)
    "alimento_comun": 30 * _FRJ,        # Algae Pellet (FRJ)
    "alimento_premium": 150 * _FRJ,     # Brine Shrimp (FRJ)
    "solvente": 1 * _AXF,               # 1 AXF (era 120 FRJ)
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

# --- MULTIPLAYER FEES (FRJ, human-readable) ---
# Se aplica frj_to_internal() al guardar en DB. Aquí en unidades legibles.
# Basado en: booster pure = 60 FRJ, gashapon bronce = 1500 FRJ.
#   → Rookie:  10 FRJ (~$1.75 MXN) — accesible, ~20 juegos por booster
#   → Champion: 50 FRJ (~$8.75 MXN) — riesgo moderado, ~4 juegos por booster
MULTIPLAYER_FEES = {
    "rookie_pool": 10,
    "champion_abyss": 50,
    # Legacy keys — mantener para compatibilidad
    "rookie": 10,
    "champion": 50,
}

# --- MULTIPLAYER ROOMS CONFIG ---
# fee, prize, consolation en FRJ human-readable
# XP se mantiene como entero (no es monto monetario)
MULTIPLAYER_ROOMS = {
    "rookie_pool": {
        "title": "Charco de Novatos",
        "difficulty_label": "Fácil",
        "fee": 10,
        "prize": 40,
        "consolation": 5,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion_abyss": {
        "title": "Fosa del Campeón",
        "difficulty_label": "Difícil",
        "fee": 50,
        "prize": 200,
        "consolation": 10,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
    # Legacy keys — mantener para compatibilidad
    "rookie": {
        "fee": 10,
        "prize": 40,
        "consolation": 5,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion": {
        "fee": 50,
        "prize": 200,
        "consolation": 10,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
}
