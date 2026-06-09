#!/usr/bin/env python3
"""
sim_cpu_balance.py — CPU room house-edge simulator.

Runs N_GAMES simulated matches per room and reports:
  • Win rate (player)
  • Expected value per game (from the house's perspective)
  • House edge %

Usage:
    python scripts/sim_cpu_balance.py

No database or network access required — pure logic simulation.
"""

import random
import sys
import os

# Allow running from repo root or scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

N_GAMES = 50_000
SEED    = 42

# ── copy of game.py constants (keep in sync manually) ──────────────────────
WINNING_LINES = [
    {0,1,2,3}, {4,5,6,7}, {8,9,10,11}, {12,13,14,15},
    {0,4,8,12}, {1,5,9,13}, {2,6,10,14}, {3,7,11,15},
    {0,5,10,15}, {3,6,9,12},
]

ROOM_CONFIG = {
    "rookie": {
        "bot_count":   1,
        "bot_focus":   40,
        "fee":         10.0,
        "prize":       16.0,
        "consolation": 2.0,
    },
    "champion": {
        "bot_count":   5,
        "bot_focus":   80,
        "fee":         50.0,
        "prize":       290.0,
        "consolation": 5.0,
    },
}

# ── helpers ─────────────────────────────────────────────────────────────────

def check_line(marked: set) -> bool:
    for line in WINNING_LINES:
        if line.issubset(marked):
            return True
    return False


def miss_chance(focus: float) -> float:
    return max(0.0, min(0.3, (100.0 - focus) * 0.003))


def simulate_match(rng: random.Random, room: dict, player_focus: float) -> bool:
    """Returns True if player wins."""
    N = room["bot_count"]
    bot_mc = miss_chance(room["bot_focus"])
    plr_mc = miss_chance(player_focus)

    # 54-card deck (indices 0..53)
    deck = list(range(54))
    rng.shuffle(deck)

    all_card_ids = list(range(54))
    player_board  = rng.sample(all_card_ids, 16)
    bot_boards    = [rng.sample(all_card_ids, 16) for _ in range(N)]

    player_marked  = set()
    bot_marked     = [set() for _ in range(N)]

    for card in deck:
        # bots
        for i, bb in enumerate(bot_boards):
            if card in bb:
                if rng.random() >= bot_mc:
                    bot_marked[i].add(bb.index(card))
        # player
        if card in player_board:
            if rng.random() >= plr_mc:
                player_marked.add(player_board.index(card))

        # check (player wins ties)
        if check_line(player_marked):
            return True
        if any(check_line(bm) for bm in bot_marked):
            return False

    return False  # fallback (deck exhausted)


# ── main ─────────────────────────────────────────────────────────────────────

def run_room(room_name: str, player_focus: float) -> None:
    rng   = random.Random(SEED)
    room  = ROOM_CONFIG[room_name]
    fee   = room["fee"]
    prize = room["prize"]
    cons  = room["consolation"]

    wins = sum(1 for _ in range(N_GAMES) if simulate_match(rng, room, player_focus))
    win_rate = wins / N_GAMES

    # From player's perspective:  EV = win_rate * prize + (1-win_rate) * consolation
    player_ev  = win_rate * prize + (1 - win_rate) * cons
    # From house's perspective:  house_profit = fee - player_ev
    house_edge = (fee - player_ev) / fee * 100

    print(f"  Win rate:    {win_rate*100:.1f}%")
    print(f"  Player EV:   {player_ev:.2f} COR  (paid {fee:.0f} COR)")
    print(f"  House edge:  {house_edge:+.1f}%  {'✅' if house_edge > 0 else '🚨 NEGATIVE'}")


print(f"{'='*55}")
print(f"  CPU Balance Simulation  ({N_GAMES:,} games per scenario)")
print(f"{'='*55}")

for room_name, room in ROOM_CONFIG.items():
    print(f"\n── {room_name.upper()} (bots={room['bot_count']}, bot_focus={room['bot_focus']}) ──")
    for focus in [0, 30, 50, 70, 100]:
        print(f"\n  Player focus={focus}:")
        run_room(room_name, float(focus))

print(f"\n{'='*55}")
