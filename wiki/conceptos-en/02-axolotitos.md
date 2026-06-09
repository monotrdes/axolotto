## English

> **Axolotitos are the heart of Axolotto.** They are your digital pets, your star players, your amphibian friends who compete for you in Mexican Loteria. This page explains absolutely EVERYTHING about them: how they work, how to care for them, how to level them up, and how to gear them up.

---

### What is an Axolotito?

An **Axolotito** is a unique digital creature inspired by the Mexican axolotl (*Ambystoma mexicanum*). It is far more than a virtual pet — it is your player-character in the Axolotto universe.

**In technical terms**, each Axolotito is an **ERC-721 NFT** with 256-bit DNA (`uint256`) recorded on the blockchain. This DNA determines its visual appearance (skin color, gill type, eye shape, tail, etc.) and its base stats. No two Axolotitos are identical — each one is one of a kind.

**In gameplay terms**, your Axolotito is the one who actually **plays Loteria for you**. You pick the board, set the budget, configure win/loss limits... and the Axolotito runs the matches. You just check the results whenever you feel like it.

> **Fun fact:** The real axolotl is an endemic species from Xochimilco, Mexico City, critically endangered. Axolotto makes it the digital protagonist to celebrate its existence and raise awareness.

---

### The 4 Core Stats

Every Axolotito is born with 4 fundamental stats that determine its in-game performance. These are the ones you care about day to day.

#### SUERTE (Luck) 🍀 — The Success Stat

| Property | Value |
|----------|-------|
| Range | 0 to 100 |
| Starting value | 10 |
| What it does | Boosts prizes and saves you from losing |

**Luck** is your best friend. Every point of Luck improves your odds in several ways:

- **Prize bonus:** On a win, Luck applies an extra multiplier on top of the base prize. With high Luck, big wins become huge.
- **Lucky Save:** Up to a **5% chance** to prevent a bot from winning when you are about to lose. It is that "I can't believe it" moment that saves your wallet.
- **Better Gashapon drops:** Axolotitos with high Luck tend to get better capsule results. Luck is factored in at drop time.

> **Tip:** If you love Gashapon or play hard-mode rooms, prioritize high-Luck Axolotitos.

---

#### OJO (Focus) 👁️ — The Precision Stat

| Property | Value |
|----------|-------|
| Range | 0 to 100 |
| Starting value | 50 |
| What it does | Reduces the chance of missing called cards |

When the Caller (Griton) announces a card, your Axolotito must **mark it on the board**. If the card is on the board but the Axolotito fails to mark it... that is a **miss**. And misses cost games.

**OJO** (Focus) determines how likely that miss is:

| OJO | Miss Chance |
|-----|------------|
| 0 | ~30% — nearly one in three cards slips by |
| 25 | ~22% |
| 50 | ~15% — starting value, balanced |
| 75 | ~7% |
| 100 | 0% — NEVER misses |

> **Tip:** For competitive multiplayer, OJO is arguably the most important stat. An Axolotito with OJO 100 never loses to a slip-up.

---

#### PILA (Stamina) 🔋 — The Endurance Stat

| Property | Value |
|----------|-------|
| Range | 50 to 200 |
| Starting value | 100 |
| What it does | Determines how many games you can play and how fast you rest |

**PILA** (Stamina) is your maximum energy pool. It defines your play rhythm:

- **Higher energy max:** At 50 PILA your max energy is 50 — few games. At 200 PILA you have double the normal maximum. More games before needing sleep.
- **Faster recovery:** While sleeping, a high-PILA Axolotito recovers faster. At PILA 200, sleep is up to **65% faster** than at PILA 50.
- **Every match costs 10 energy.** At PILA 100, you get ~10 games. At PILA 200, ~20 games before running dry.

> **Tip:** If you plan long play sessions ("leave the bot on all night"), look for high PILA.

---

#### SAL (Salinity) 🧂 — The Anti-Stat

| Property | Value |
|----------|-------|
| Range | 0 to 100 |
| Starting value | 5 |
| What it does | Drags performance down — the lower, the better |

**SAL** (Salinity) is the stat you **do NOT want**. It is a deadweight, a bad-luck factor that hurts performance:

- **Card slippage:** In CPU mode, SAL pushes your cards to the back of the deck, delaying when they appear. The more SAL, the further back your cards go.
- **In multiplayer, SAL is dangerous.** At SAL = 100, you have up to a **33% chance that a called card is NOT marked** on your board (a "slip"). In other words: OJO and SAL oppose each other — but SAL applies AFTER, so even OJO 100 cannot fully save you.
- **Think of it this way:** SUERTE, OJO, and PILA pull you up. SAL pulls you down. An Axolotito with decent stats but high SAL performs worse than one with low stats and zero SAL.

> **Crucial tip:** When shopping for an Axolotito on the P2P market, check SAL before anything else. An Axolotito with SAL above 30 is already problematic. Above 60 it is nearly unplayable in multiplayer.

---

### The Energy System

Energy is the resource that limits how many games you can play before resting. Understanding the energy system is key to optimizing your play.

#### Key Concepts

| Concept | Explanation |
|---------|-------------|
| **energy_current** | Your current energy. Starts at 100. Costs 10 per match (CPU or multiplayer). |
| **energy_max_current** | Your effective max energy. Starts at 100. Decays with use. |
| **Decay** | Each game played reduces `energy_max_current` by **3 points**. Cumulative. |
| **Floor** | `energy_max_current` never drops below **10**. You can always play at least 1-2 games. |
| **Sleep** | Restores `energy_current` and resets `energy_max_current` to its original value (your PILA). |
| **Sleep threshold** | You can only sleep when current energy is below **85%** of current max. |

#### Example Play Session

```
Start: energy_current = 100, energy_max_current = 100
Game 1: current 90, max 97
Game 2: current 80, max 94
Game 3: current 70, max 91
Game 4: current 60, max 88
Game 5: current 50, max 85
...
Game 10: current 0, max 70  ← out of energy, must sleep
Sleep (~1 min) → current 100, max 100 again
```

> **Important:** You cannot chain games forever. The max-decay system ensures you eventually need a break. It is designed to be healthy — the bot stops, your Axolotito rests, you breathe too.

#### Food: Recover Energy Without Sleeping

If you do not want to wait for sleep, you can feed your Axolotito:

| Food | Cost | Energy Restored |
|------|------|----------------|
| **Algae Pellet** | 30 FRJ | +15 energy |
| **Brine Shrimp** | 150 FRJ | +60 energy |

Food restores `energy_current` but does **NOT** reset `energy_max_current`. Decay is only cured by sleep.

#### Sleep

- Sleep takes approximately **1 minute**.
- Axolotitos with high PILA sleep faster — up to **65% faster** at PILA 200.
- The sleep button only appears when your energy is below 85% of current max.
- On waking: `energy_current` and `energy_max_current` are fully restored.
- When energy hits **0**, the Axolotito **must sleep**. Cannot play until rested.

---

### The 4 States

At any moment, your Axolotito is in one of these four states:

#### IDLE — Available 😊

Default state. Your Axolotito is awake, has energy, ready for anything:
- Can play (CPU or multiplayer)
- Can eat
- You can equip accessories
- You can review its stats

#### PLAYING — In a Match 🎮

The Axolotito is playing Loteria. During this state:
- Cannot modify equipment
- Cannot change assigned board
- Match progress updates in real time (or on refresh)
- In CPU auto-bot mode, the Axolotito keeps playing on its own until limits are met or energy runs out

#### SLEEPING — Resting 😴

The Axolotito is recovering energy:
- Cannot play or do anything
- The sleep bar shows progress (~1 minute)
- On waking: energy fully restored
- `energy_max_current` resets to PILA value (clearing accumulated decay)

#### WAITING_SETTLEMENT — Waiting for Report 📋

The play session ended and the Axolotito is waiting for you to review the results. This is the "cash-out" step:
- You see a **performance slip** with: net gains/losses, XP earned, games played, wins and losses
- On confirming with a tap, gains are transferred to your wallet and the Axolotito earns Loyalty Points
- After settlement, the Axolotito usually goes to sleep

---

### Leveling: How to Level Up

Axolotitos earn **experience (XP)** by playing matches. Enough XP levels them up, improving their stats.

#### Level-Up Threshold

The formula is simple:

> **XP needed to level up = current level x 100**

For example: level 1 to 2 requires 100 XP. Level 5 to 6 requires 500 XP. Level 10 to 11 requires 1,000 XP.

#### XP Earned Per Match

**CPU Mode:**

| Result | Axolotito XP |
|--------|-------------|
| Win (easy) | +35 XP |
| Win (hard) | +75 XP |
| Loss (easy) | +8 XP |
| Loss (hard) | +15 XP |

**Multiplayer Mode:**

| Result | Axolotito XP |
|--------|-------------|
| Premio 1 (1st place) | +50 XP |
| Premio 2 (2nd place) | +20 XP |
| Consolation | +5 XP |

#### What Improves on Level Up?

On level up, all core stats (SUERTE, OJO, PILA) receive a gradual improvement. SAL does not change on level up — it only changes through breeding and genes.

Higher levels also unlock:
- Access to higher-difficulty rooms
- Better staking rates
- Greater visibility on leaderboards

---

### Equipment and Accessories

You can dress your Axolotito with accessories. Equipment is **purely cosmetic** — it does not affect gameplay stats. Its value is in collection, personalization, and status.

#### The 3 Equipment Slots

| Slot | What Goes There | Examples |
|------|----------------|----------|
| **Head** 🎩 | Hats, crowns, helmets | Mariachi hat, Lily crown, Diving helmet, Astral tiara |
| **Eyes** 👓 | Glasses, goggles, masks | Sunglasses, Golden monocle, Dive goggles, Wrestler mask |
| **Body** 👘 | Clothing, capes, armor | Xochimilco poncho, Champion cape, Tactical vest, Obsidian armor |

#### How to Get Accessories

- **Gashapon:** The main source. Silver and Gold capsules have good odds for rare accessories.
- **P2P Market:** Buy from other players — sometimes you find pieces no longer in rotation.
- **Special events:** Some accessories are seasonal exclusives (Day of the Dead, Christmas, anniversary).

> **Note:** Accessories do NOT affect stats. An Axolotito wearing the most epic helmet in the game performs exactly the same as one with nothing on. Fashion is for the soul, not for SUERTE.

---

### Slot Limits

You cannot have infinite Axolotitos. The game limits how many active Axolotitos you can keep.

| Membership Tier | Axolotito Slots |
|-----------------|-----------------|
| No VIP | 6 slots |
| VIP Coral | 6 slots |
| VIP Dorado | 6 slots |
| VIP Axolite | 7 slots |

#### What Happens If My VIP Axolite Expires?

If you have 7 Axolotitos and your VIP Axolite expires, the 7th Axolotito (the newest one) enters **frozen** status:
- Cannot play, eat, sleep, or be sold
- Attempting to use it returns an **HTTP 423 (Locked)** error
- It still occupies a slot — it does not disappear, it just goes inactive
- **Solution:** Renew VIP Axolite to unfreeze it, or release (burn) an Axolotito to drop to 6 and restore normal access

> **Tip:** If you are on VIP Axolite and know it is about to expire, plan ahead — decide which Axolotito to release, or sell one on the P2P market before expiration.

---

### Power Formula (Rankings)

**POWER** is a global metric that summarizes how strong your Axolotito is. It is used for rankings and quick comparisons:

> **POWER = SUERTE + OJO + PILA + (100 - SAL)**

In other words: sum your three positive stats, and add the "inverse" of SAL (since low SAL = good). Maximum theoretical value is **500**:

| Stat | Max | Contribution |
|------|-----|-------------|
| SUERTE | 100 | +100 |
| OJO | 100 | +100 |
| PILA | 200 | +200 |
| (100 - SAL) | 100 (when SAL=0) | +100 |
| **TOTAL max** | | **500** |

This makes PILA the heaviest stat in the ranking (since it goes to 200), followed by SUERTE and OJO (cap at 100). A high-PILA Axolotito will naturally have more POWER than a high-SUERTE one, though both may be equally valuable depending on your play style.

---

### How to Get an Axolotito

There are three paths to obtaining your first (or next) Axolotito:

#### 1. Tutorial — Your First Free Axolotito 🎁

Complete the game tutorial and receive your first Axolotito completely free. It is a basic Axolotito with starting stats (SUERTE 10, OJO 50, PILA 100, SAL 5) and no special traits, but it is 100% functional and lets you start playing immediately.

#### 2. Hatch from a Webito 🥚

The main method for obtaining Axolotitos with unique genes:

1. **Buy a Webito** (egg) from the Shop. Prices range from 400 to 3,000 FRJ depending on type (Genesis, Expansion, Retail, Astral).
2. **Place it in an incubation slot** in your Cenote.
3. **Incubate for 7 days.** During this period you manage temperature and protect the egg from cold with shields. Xochimilco's weather affects progress.
4. **Imprint the Webito:** During incubation, you can feed the egg items that modify the future Axolotito's stats (e.g., lower SAL, boost SUERTE).
5. **Hatch:** After the 7 days, the egg hatches and your Axolotito is born with stats and traits determined by incubation and imprinting.

> See the full guide at: [[11-webitos-y-crianza]]

#### 3. P2P Market 🛒

Buy an existing Axolotito from another player:
- You can check its stats BEFORE buying
- Prices vary by stats, trait rarity, level, and equipment
- Axolotitos with low SAL and high SUERTE/OJO tend to be the most expensive
- See details at: [[19-mercado-p2p]]

---

### Beginner's Summary

If you are new to Axolotto and just want the essentials:

1. Your first Axolotito is **free** by completing the tutorial.
2. The 4 key stats are **SUERTE** (win bigger), **OJO** (don't miss), **PILA** (play longer), and **SAL** (lower is better).
3. Each game costs **10 energy**. No energy means sleep (~1 min).
4. **Don't obsess over perfect stats at the start.** Learn to play with what you have. The difference between a "good" Axolotito and a "perfect" one only matters at high levels of play.
5. **SAL is sneaky.** If you are buying on the P2P market, check SAL before price.
6. Accessories are **purely cosmetic** — dress your Axolotito however you want, it does not affect gameplay.
7. **The auto-bot is your friend.** Set a budget, loss/profit limits, and let your Axolotito play on its own. Check results whenever you feel like it.

---

## Quick Reference / Referencia Rapida

| Concept / Concepto | Value / Valor |
|---|---|
| Starting Axolotito slots / Slots iniciales | 6 |
| Max slots with VIP Axolite / Max slots con VIP Axolite | 7 |
| Frozen slot HTTP code / Codigo HTTP de slot congelado | 423 |
| SUERTE (Luck) default / Valor inicial | 10 (range/rango 0-100) |
| OJO (Focus) default / Valor inicial | 50 (range/rango 0-100) |
| OJO 50 miss chance / Probabilidad de fallo | ~15% |
| OJO 100 miss chance / Probabilidad de fallo | 0% |
| OJO 0 miss chance / Probabilidad de fallo | ~30% |
| PILA (Stamina) default / Valor inicial | 100 (range/rango 50-200) |
| SAL (Salinity) default / Valor inicial | 5 (range/rango 0-100) |
| Max SAL slip chance (multiplayer) / Max probabilidad de slip | 33% |
| Energy per match / Energia por partida | 10 |
| Energy max decay per match / Decaimiento de max por partida | 3 |
| Energy max minimum (floor) / Piso de energia maxima | 10 |
| Sleep threshold / Umbral de sueno | < 85% of energy_max_current |
| Sleep duration / Duracion del sueno | ~1 min |
| Max sleep speedup (PILA 200) / Max aceleracion de sueno | 65% faster |
| Lucky Save max chance / Max probabilidad de Salvada Milagrosa | 5% |
| Algae Pellet cost / Costo | 30 FRJ (+15 energy / energia) |
| Brine Shrimp cost / Costo | 150 FRJ (+60 energy / energia) |
| Level-up threshold / Umbral de subida de nivel | level x 100 XP |
| CPU win XP (easy) / XP por victoria CPU (facil) | +35 XP |
| CPU win XP (hard) / XP por victoria CPU (dificil) | +75 XP |
| CPU loss XP (easy) / XP por derrota CPU (facil) | +8 XP |
| CPU loss XP (hard) / XP por derrota CPU (dificil) | +15 XP |
| Multiplayer Premio 1 XP | +50 XP |
| Multiplayer Premio 2 XP | +20 XP |
| Multiplayer consolation XP / XP de consolacion | +5 XP |
| Equipment slots / Slots de equipamiento | 3 (Head/Cabeza, Eyes/Ojos, Body/Cuerpo) |
| Equipment stat effect / Efecto en stats del equipamiento | None / Ninguno (cosmetic only / solo cosmetico) |
| Power formula / Formula de Poder | SUERTE + OJO + PILA + (100 - SAL) |
| Max theoretical Power / Poder maximo teorico | 500 |
| DNA type / Tipo de ADN | uint256 (on-chain, unique / unico) |
| Axolotito NFT standard / Estandar NFT | ERC-721 |

---

→ See also / Ver tambien: [[03-estadisticas-de-axolotito]] · [[04-naturalezas-y-personalidad]] · [[05-rasgos-visuales-y-rareza]] · [[11-webitos-y-crianza]] · [[00-INDEX]]
