# 🃏 Centralized Price and Token Conversions Config for Axolotto

# --- TIPO DE CAMBIO NOMINAL (Para fallback/referencias) ---
# Paquete más barato: 200 FRJ = $35 MXN → 1 FRJ ≈ $0.175 MXN
NOMINAL_AXF_PRICE_MXN = 2.00  # 1 AXF = $2 MXN nominal
DEVEX_RATE_70_GROSS = 1.40   # 70% del bruto ($1.40 MXN payout)
DEVEX_RATE_70_NET = 1.14     # 70% del neto ($1.14 MXN payout)
DEVEX_RATE_50_GROSS = 1.00   # 50% del bruto ($1.00 MXN payout)

# --- WEBITOS (EGG CATALOG) ---
WEBITO_PRICES = {
    1: 400.0,    # Fase 1 (Génesis)
    2: 800.0,    # Fase 2 (Expansión)
    3: 1200.0,   # Fase 3 (Retail)
    "astral": 3000.0  # Astral
}

# --- BOOSTERS CATALOG ---
# Cada entrada: {"axg": precio_premium, "gal": precio_earned}
BOOSTER_PRICES = {
    # Fase 1 (First Edition)
    1: {
        "fiesta": {"axg": 10.0, "gal": 100.0},
        "nido":   {"axg": 10.0, "gal": 100.0},
        "cosmos": {"axg": 10.0, "gal": 100.0},
        "pure":   {"axg":  6.0, "gal":  60.0},
    },
    # Fase 2 (Unlimited)
    2: {
        "fiesta": {"axg": 15.0, "gal": 150.0},
        "nido":   {"axg": 15.0, "gal": 150.0},
        "cosmos": {"axg": 15.0, "gal": 150.0},
        "pure":   {"axg": 10.0, "gal": 100.0},
    },
    # Fase 3 (Retail / Standard)
    3: {
        "fiesta": {"axg": 20.0, "gal": 200.0},
        "nido":   {"axg": 20.0, "gal": 200.0},
        "cosmos": {"axg": 20.0, "gal": 200.0},
        "pure":   {"axg": 15.0, "gal": 150.0},
    },
    "foil": {"axg": 80.0, "gal": 800.0},  # Booster Brillante
}

# --- GASHAPON COSTS (GAL) ---
GASHAPON_TIER_COSTS = {
    "bronce": 1500.0,
    "plata": 5000.0,
    "oro": 20000.0,
    "triple": 22500.0
}

# --- CONSUMIBLES (AXG / GAL) ---
CONSUMABLE_PRICES = {
    "gotas": 200.0,      # Gotas Anti-Escarcha (GAL)
    "lampara": 200.0,    # Lámpara Infrarroja Pro (AXG)
    "vip_coral": 400.0,    # Pase Coral VIP 30 días (AXG)
    "vip_dorado": 600.0,   # Pase Dorado VIP 30 días (AXG)
    "vip_axolite": 1800.0, # Pase Axolite VIP 30 días (AXG)
    "alimento_comun": 30.0,    # Algae Pellet (GAL)
    "alimento_premium": 150.0, # Brine Shrimp (GAL)
    "solvente": 120.0,          # Solvente de Pegamento (GAL)
    "upgrade_board_slots": 300.0 # Upgrade Board Slots (AXG)
}

# --- TABLAS DE JUEGO (BOARD) ---
BOARD_PRICES = {
    "clasica": {"axg": 10.0, "gal": 130.0},
    "suerte": {"axg": 50.0, "gal": 520.0},
    "plasma": {"axg": 150.0, "gal": 1560.0},
    "cosmica": {"axg": 200.0, "gal": 0.0}
}

# --- BOARD SLOTS DESBLOQUEOS (GAL) ---
BOARD_SLOT_COSTS = {
    4: 500.0,
    5: 1000.0,
    6: 2000.0,
    7: 4000.0,
    8: 8000.0,
    9: 15000.0
}

# --- MULTIPLAYER FEES (FRJ) ---
# Solo 2 salas públicas oficiales (rookie_pool y champion_abyss).
# Basado en: paquete más barato = 200 FRJ por $35 MXN.
#   → Rookie:  25 FRJ ($4.38 MXN) — 8 juegos por paquete
#   → Champion: 100 FRJ ($17.50 MXN) — 2 juegos por paquete
# Player-hosted (cave) rooms usan buy_in_frj configurable.
MULTIPLAYER_FEES = {
    "rookie_pool": 25.0,
    "champion_abyss": 100.0,
    # Legacy keys — mantener para compatibilidad con datos existentes
    "rookie": 25.0,
    "champion": 100.0,
}

# --- MULTIPLAYER ROOMS CONFIG ---
MULTIPLAYER_ROOMS = {
    "rookie_pool": {
        "title": "Charco de Novatos",
        "difficulty_label": "Fácil",
        "fee": 25.0,
        "prize": 85.0,
        "consolation": 8.0,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion_abyss": {
        "title": "Fosa del Campeón",
        "difficulty_label": "Difícil",
        "fee": 100.0,
        "prize": 400.0,
        "consolation": 20.0,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
    # Legacy keys — mantener para compatibilidad
    "rookie": {
        "fee": 25.0,
        "prize": 85.0,
        "consolation": 8.0,
        "win_xp_board": 25,
        "win_xp_axo": 35,
        "loss_xp_board": 8,
        "loss_xp_axo": 8,
    },
    "champion": {
        "fee": 100.0,
        "prize": 400.0,
        "consolation": 20.0,
        "win_xp_board": 60,
        "win_xp_axo": 75,
        "loss_xp_board": 15,
        "loss_xp_axo": 15,
    },
}
