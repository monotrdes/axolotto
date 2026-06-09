## English

Axolotto offers **five distinct game modes** so every type of player can find their place — from the casual competitor wanting a quick match against bots to the F2P collector just starting out who wants to earn their first rewards without owning an axolotito. Here is each one in detail.

---

## 1. CPU Mode (Solo vs Bots)

The primary PvE mode. You face system-controlled bots in quick Lotería matches. Perfect for practicing, farming Frijolitos, and leveling up your axolotitos without the pressure of playing against humans.

### Available Rooms

| Room | Name | Bots | Difficulty | Entry Fee | Win Prize | Consolation |
|------|------|------|------------|-----------|-----------|-------------|
| Rookies | Charco de Novatos | 1 easy bot | Focus 40 (~18% miss rate) | 25 FRJ | 85 FRJ | 8 FRJ |
| Champions | Fosa del Campeón | 5 hard bots | Focus 80 (~6% miss rate) | 100 FRJ | 400 FRJ | 20 FRJ |

### Multipliers

You can multiply your bet and winnings with these options:

| Multiplier | Rookies Entry | Rookies Prize | Champions Entry | Champions Prize |
|------------|---------------|---------------|-----------------|-----------------|
| 1× | 25 FRJ | 85 FRJ | 100 FRJ | 400 FRJ |
| 2× | 50 FRJ | 170 FRJ | 200 FRJ | 800 FRJ |
| 5× | 125 FRJ | 425 FRJ | 500 FRJ | 2,000 FRJ |
| 10× | 250 FRJ | 850 FRJ | 1,000 FRJ | 4,000 FRJ |

### Experience (axo XP)

- **Rookies**: 25–35 axo XP on win, 8 axo XP on loss
- **Champions**: 60–75 axo XP on win, 15 axo XP on loss

### Win Streak

Each consecutive win adds a **+15%** bonus on the base prize, capped at **+50%** (4 straight wins). Losing resets the streak.

### Energy Cost

Always **10 energy** per match, regardless of multiplier or room.

### How to Play

1. Select your active axolotito from your inventory
2. Pick a Lotería board (or create a new one in the Board Editor)
3. Choose a room: Charco de Novatos or Fosa del Campeón
4. Select your multiplier
5. Press Play! The result resolves in seconds

---

## 2. Multiplayer Mode (Auto-AFK)

The main competitive mode. Real-time matches with up to **30 human players** per room. Your axolotito plays automatically — you set the strategy and it handles the rest.

### Multiplayer Rooms

| Room | Entry Fee | Base Prize |
|------|-----------|------------|
| Rookies (Charco de Novatos) | 10 FRJ | Varies by participants |
| Champions (Fosa del Campeón) | 50 FRJ | Varies by participants |

### Auto-AFK: Set Your Strategy

- **Budget (stop-loss)**: maximum FRJ you are willing to lose. When reached, your axolotito stops playing.
- **Take-profit**: profit target. When reached, your winnings are automatically withdrawn.
- **Auto-reinscription**: your axolotito automatically re-enters new matches until limits are hit or energy runs out.

### Settlement

After playing, you manually claim:
- Accumulated winnings held in escrow
- Loyalty Points for each completed match

### Room Filling

If fewer than **4 human players** are in a room, the system fills it with bots to ensure the match runs. Multiplayer bots use the same logic as CPU mode but with randomized names.

### Start Times

| Registered Boards | Wait Time |
|-------------------|-----------|
| 30+ boards | Instant start |
| 15–29 boards | 15 seconds |
| 5–14 boards | 30 seconds |
| 1–4 boards | 60 seconds |

### Energy Cost

Formula: **10 + (salinity × 0.2)** per round, capped at **30 energy** per match. High-salinity axolotitos burn more energy in multiplayer — another strategic factor to consider.

---

## 3. Manual PvP Mode (Interactive)

The most intense and competitive mode. It is NOT permanently open — only activated during **special events** created by administrators.

### Key Differences from Other Modes

- **Manual marking**: you click cards on your board yourself. No auto-marking.
- **Agility stat**: card-marking speed depends on your Agility stat. Marking delay ranges from **800 ms** (high agility) to **2,500 ms** (low agility).
- **Manual "¡Lotería!"**: you can shout "¡Lotería!" to claim victory at the exact right moment. Shouting without the full pattern costs you points.
- **Real-time WebSocket**: direct server connection for minimal latency.
- **El Gritón calls cards**: an automated caller (El Gritón) announces cards on an admin-configurable timer.

### Player-Hosted Rooms (Cuevita Host)

A player with enough Frijolitos can create their own private PvP room:
- Configure the Gritón timer
- Invite specific friends
- Set custom entry fees and prizes
- Choose whether to apply special rules (like Saladito)

### XP Multipliers

During Manual PvP events, XP multipliers are **higher** than in any other mode, making these events the fastest way to level rare axolotitos.

---

## 4. Saladito Mode (Inverse Lotería)

The most fun and chaotic twist on traditional Lotería. The rules are **inverted**: the player who ends with the **fewest marked cards** on their board wins.

### When Is It Available?

- **Automatic**: every night from **3:00 to 4:00 AM** server time (Mexico City, GMT-6)
- **Manual**: in private player-hosted rooms (Cuevita Host) at any time

### Inverted Rules

- El Gritón calls cards as usual
- Your axolotito tries NOT to mark cards
- Whoever has the **fewest marked cards** at the end of the round wins
- On a tie, the one with the highest SAL wins

### SAL Becomes a Benefit

In normal mode, high SAL is bad because it causes cards to "slip" and fail to mark. But in Saladito mode, **this is exactly what you want**. A high-SAL axolotito has a higher chance of cards slipping off — which is GOOD in Saladito because you want few marked cards.

This creates a fun meta where axolotitos that would normally be "bad" (high salinity) suddenly become valuable during Saladito hour.

### Special Rewards

- FRJ prizes equivalent to CPU Champions mode
- Chance to obtain **Webitos with Saladito traits** (special traits only obtainable in this mode)
- Temporary "Rey del Saladito" badge for winning 3 consecutive matches in one night

---

## 5. Spectator Mode (F2P / El Espejo del Cenote)

The free mode designed for players who **do not own axolotitos**. You can watch live matches and earn micro-rewards by participating as a spectator.

### How It Works

- Enter the **Espejo del Cenote** (Cenote Mirror), the spectator lobby
- Pick an active match to watch
- You receive a **Mirror Board** (Tablero Espejo): an exact copy of a real player's board in that match
- Watch the match in real time from that player's perspective

### Spectator Rewards

| Action | Reward |
|--------|--------|
| Mirror board wins the match | Up to 10 FRJ/day |
| "Back" (cheer for) an axolotito | Fragmentos Astrales de Webito |
| Tap interactive bubbles | Send floating bubbles to the real player |

### Fragmentos Astrales de Webito

- Earned by backing axolotitos and watching full matches
- **100 fragments = 1 free Common Webito**
- Daily cap: **10 fragments**

### Daily Caps

| Resource | Daily Limit |
|----------|-------------|
| FRJ | 10 FRJ |
| Fragmentos Astrales | 10 fragments |

### Interactive Tap

As a spectator, you can tap the screen to send **floating bubbles** to the player you are watching. The real player sees these bubbles appear on their screen — a fun way to show support without affecting the match.

---

## Comparison Table

| Feature | CPU | Multiplayer | Manual PvP | Saladito | Spectator |
|---------|-----|-------------|------------|----------|-----------|
| **Type** | PvE vs Bots | PvP Auto-AFK | PvP Interactive | Inverse Lotería | Watch only |
| **Entry Fee** | 25–250 FRJ | 10–50 FRJ | Variable (event) | 25–100 FRJ | Free |
| **Max Prize** | 850 FRJ (10×) | Variable | Variable (high) | 400 FRJ | 10 FRJ/day |
| **Players** | 1 human + bots | Up to 30 humans | 2–8 humans | 1 human + bots | Unlimited |
| **Interaction** | None (auto) | Strategy (config) | Manual clicking | None (auto) | Bubble taps |
| **Availability** | 24/7 | 24/7 | Events only | 3–4 AM + private | 24/7 |
| **Energy** | 10 fixed | 10–30 variable | 15 fixed | 10 fixed | 0 (free) |
| **Requires axolotito?** | Yes | Yes | Yes | Yes | No |
| **XP** | 8–75 axo XP | Similar to CPU | Boosted (event) | Similar to CPU | 0 XP |
| **Streak** | +15%/win | +10%/win | +20%/win | N/A | N/A |

---

## Quick Reference / Referencia Rápida

| Concept / Concepto | Value / Valor |
|---|---|
| Total game modes | 5 (CPU, Multiplayer, Manual PvP, Saladito, Spectator) |
| CPU rooms | Rookies (easy) and Champions (hard) |
| CPU entry fees | 25–1,000 FRJ depending on multiplier |
| Multiplayer max players | 30 per room |
| Multiplayer energy cost | 10 + (salinity × 0.2), max 30 |
| Auto-AFK budget options | Stop-loss and take-profit limits |
| Manual PvP availability | Special events only (admin-created) |
| Manual PvP marking delay | 800 ms – 2,500 ms based on Agility |
| Saladito schedule | 3:00–4:00 AM Mexico City time (GMT-6) |
| Saladito rule | Fewest marked cards wins (inverted) |
| Spectator cost | Free (no axolotito required) |
| Spectator daily cap | 10 FRJ + 10 Fragmentos Astrales |
| Fragmentos → Webito | 100 fragments = 1 free Common Webito |
| Win streak bonus | +15% per CPU win, +10% per MP win, +20% per PvP win |
| Max streak bonus | +50% (CPU), capped per mode |

---

→ See also / Ver también: [[06-como-jugar-loteria]] · [[23-salas-y-multijugador]] · [[24-saladito-y-modos-especiales]] · [[25-f2p-guia-gratis]] · [[00-INDEX]]
