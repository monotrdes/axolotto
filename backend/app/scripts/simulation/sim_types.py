from dataclasses import dataclass
from typing import Optional

import random

# ── RNG — use SystemRandom everywhere (critical rule #3) ─────────────────────
_rng = random.SystemRandom()


@dataclass
class SimConfig:
    players: int = 4
    incubation: int = 45
    games: int = 5
    multi_wait: int = 35
    skip_reset: bool = False
    max_boosters: Optional[int] = None
    max_boards: Optional[int] = None
    max_webitos: Optional[int] = None
    include_user: Optional[str] = None
    db_url: Optional[str] = None
    skip_imprinting: bool = False     # si True, salta simulación de partidas de imprinting (más rápido)
    create_test_event: bool = False   # si True, crea un ManualModeEvent de prueba durante la simulación
    initial_axf: float = 0.0          # AXF inicial por jugador (0 = auto-calcular según personalidad)
    initial_frj: float = 0.0          # FRJ inicial por jugador (0 = auto-calcular según personalidad)


# ── Personalidades de jugador ─────────────────────────────────────────────────
PERSONALITY_POOL = [
    {
        # Máximo gastador: abre todo inmediatamente, VIP máximo, juega en champion
        "name": "whale",
        "boosters_normal": 35,
        "boosters_foil": 12,
        "eggs": 4,
        "boards_random": 4,
        "solo_games": 8,
        "auto_budget": 1000.0,
        "vip_tier": "axolite",
        "gashapon_rolls": 6,
        "play_style": "champion",
        "does_triple_suerte": True,
    },
    {
        # Coleccionista: acumula boosters/huevos/tableros, VIP por descuento, casi no juega
        "name": "collector",
        "boosters_normal": 28,
        "boosters_foil": 10,
        "eggs": 4,
        "boards_random": 5,
        "solo_games": 1,
        "auto_budget": 0.0,
        "vip_tier": "dorado",
        "gashapon_rolls": 5,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
    {
        # Jugador competitivo: muchas partidas, gasta en ítems, vende en P2P
        "name": "aggressive",
        "boosters_normal": 20,
        "boosters_foil": 5,
        "eggs": 2,
        "boards_random": 3,
        "solo_games": 10,
        "auto_budget": 700.0,
        "vip_tier": "dorado",
        "gashapon_rolls": 3,
        "play_style": "champion",
        "does_triple_suerte": True,
    },
    {
        # Jugador casual: gasto mínimo, pocas partidas, VIP básico
        "name": "casual",
        "boosters_normal": 6,
        "boosters_foil": 1,
        "eggs": 1,
        "boards_random": 2,
        "solo_games": 3,
        "auto_budget": 100.0,
        "vip_tier": "coral",
        "gashapon_rolls": 1,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
    {
        # Free-to-play: casi sin gasto real, juega mucho para ganar GAL, sin VIP
        "name": "free2play",
        "boosters_normal": 2,
        "boosters_foil": 0,
        "eggs": 0,
        "boards_random": 2,
        "solo_games": 15,
        "auto_budget": 400.0,
        "vip_tier": None,
        "gashapon_rolls": 2,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
]

PRO_USER_DID = "did:privy:cmnn1tv0o02au0ckzho9ugkb2"

# Estrategia de apertura por personalidad:
#   "immediate"  → abre todo en cuanto compra
#   "selective"  → abre solo foils ahora, guarda normales para después
#   "hoarder"    → guarda todos; los abre mucho después (o nunca)
#   "random"     → decide aleatoriamente cuáles abrir
BOOSTER_OPEN_STRATEGY: dict[str, str] = {
    "whale":      "immediate",   # Ballena: abre todo de una vez
    "aggressive": "selective",   # Agresivo: abre la mayoría en post-incubación, conserva un poco
    "casual":     "hoarder",     # Casual: abre la mayoría al final, conserva un poco
    "collector":  "random",      # Coleccionista: abre la mayoría, conserva un poco
    "free2play":  "hoarder",     # F2P: guarda los pocos que tiene, los abre al final
}
