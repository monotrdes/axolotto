## English

# Rooms and Multiplayer

Multiplayer is the competitive heart of Axolotto. It is not an extra mode or an afterthought — it is where the game comes alive, where strategies collide, and where the real prizes are won. Here is absolutely everything you need to know about rooms, from the lobby to final settlement.

---

## Room Types

Axolotto has two main categories of multiplayer rooms: Official Rooms (run by the system) and Host Rooms (created and managed by players like you).

### Official Rooms

These rooms are always open, always have traffic, and are the natural entry point for any player.

| Room | Entry (buy-in) | Max Players | Difficulty |
|------|-------------------|---------------|------------|
| **Charco de Novatos (Rookies)** | 10 FRJ | 30 | Casual — ideal for learning, testing new Boards, or playing stress-free |
| **Fosa del Campeón (Champions)** | 50 FRJ | 30 | Competitive — where serious players go to prove their stats and strategies |

**Official room features:**
- The Gritón is server-controlled, with fixed speed (normal mode, 1.0×)
- No host commission — the entire pot goes to players (minus 5% treasury and 5% Jackpot)
- Automatic bots fill the room if there are fewer than 4 human Boards
- Open 24/7, no password, visible to everyone

### Host Rooms (Player-Hosted)

Want total control? Create your own room. Host rooms are the space where the community builds its own rules, private tournaments, and custom experiences.

**Configurable parameters for the host:**

| Parameter | Options | Notes |
|-----------|---------|-------|
| **Buy-in** | 10 – 1,000 FRJ | The host sets the entry fee. Higher buy-in = bigger pot... and bigger risk |
| **Players** | 2 – 8 | Smaller, more strategic rooms. No bots |
| **Speed** | Normal (1.0×) · Fast (0.6×) · Turbo (0.3×) | Affects the delay between Gritón cards. Turbo is pure adrenaline |
| **Visibility** | Public · Friends · Private (password) | Total control over who enters |
| **Win patterns** | Configurable | The host decides which patterns count for Premio 1 in their room |

**Host commission:** the room creator receives **5% of the total pot** from every match. This means hosting popular rooms is a legitimate business within Axolotto. A host with an 8-player room at 1,000 FRJ each moves 8,000 FRJ per match and earns 400 FRJ in commission alone.

> 🏠 **Host tip:** Fast rooms (fast or turbo) generate more matches per hour. Even if the buy-in tends to be lower, volume makes up for it. A 50 FRJ turbo room with 8 players can generate more commissions per hour than a 200 FRJ normal room.

---

## Cuevita as Host

Every Axolotito has its Cuevita — its personal sanctuary in Xochimilco. And every Cuevita can host games.

**Decoration quality = lobby visibility.** The more decorated your Cuevita (more objects, higher rarity, completed expansions), the higher your room appears in the lobby listing. This is not cosmetic — it is strategic positioning. A premium Cuevita attracts more players, generating more commissions, which pays for the decoration.

**Benefits of hosting from your Cuevita:**
- Your room displays your Axolotito's name and image
- Players can visit your Cuevita from the lobby (spectator mode)
- Cuevita expansions unlock additional room slots (maximum 3 simultaneous rooms per Cuevita)
- Rare decorations give a special border to your lobby listing

---

## Registration Flow (How to Enter a Room)

Entering a multiplayer room is not just clicking a button. There is a registration process that protects your economy and prepares your Axolotito for the session.

### Registration Step by Step

1. **Select your Axolotito** — it will play for you. Its stats matter: OJO for marking, SUERTE for prizes and saves, SAL for deck position.

2. **Choose 1 to 3 Boards** — you can register up to 3 Boards simultaneously in the same room. Each Board plays independently (like 3 separate bingo cards). More Boards = more chances to win, but also more cost.

3. **Budget (FRJ) moves to escrow on your Axolotito** — upon registering, the FRJ you will use are not immediately deducted, but set aside in an escrow tied to your Axolotito. This guarantees you always have funds to cover your matches.

4. **Minimum budget** = `fee_per_board × number_of_boards`. If you register 3 Boards in Fosa del Campeón (50 FRJ each), you need at least 150 FRJ in escrow.

5. **Set your risk limits:**
   - **Stop-loss:** maximum loss you tolerate. When your escrow balance drops to this level, your Axolotito stops auto-reinscribing. Example: you enter with 300 FRJ, set stop-loss at 100 FRJ. If you lose 200 FRJ, you withdraw.
   - **Take-profit:** target gain. When your escrow balance reaches this level, your Axolotito stops auto-reinscribing and secures profits. Example: you enter with 300 FRJ, set take-profit at 600 FRJ. If you double up, you withdraw with profit.

6. **System limits:**
   - Maximum **1 registration per user** per room type (you cannot be in two Rookie rooms simultaneously)
   - Maximum **1 registration per wallet address** per room type (anti-multi-account)
   - Maximum **5 total Boards** across all your active registrations
   - You can be in one official room AND one host room simultaneously (they are different types)

---

## Matchmaking: How Matches Start

Axolotto's matchmaking system runs as a backend loop every **10 seconds**, evaluating all active rooms. Its goal is simple: start matches as quickly as possible without sacrificing match quality.

### Wait Times by Number of Boards

| Registered Boards | Wait Time | Description |
|-------------------|-----------|-------------|
| **30+** | **Instant** | Full room. Match starts immediately |
| **21 – 29** | 15 seconds | High demand. Minimal wait to catch any late arrivals |
| **11 – 20** | 20 seconds | Good size. A breather to reach better matchmaking |
| **6 – 10** | 25 seconds | Medium room. Reasonable time to attract more players |
| **3 – 5** | 35 seconds | Small room. A bit more patience |
| **1 – 2** | 60 seconds | Minimal room. Maximum wait to avoid playing alone |

### Bot Rule

If at the end of the wait time there are **fewer than 4 human Boards** registered, the system fills the room with **bots** up to a minimum of 4 participants. This guarantees you never play completely alone and that there is always a reasonable pot in play.

Bots have randomized balanced stats — they are not free wins, but they are not unbeatable either. They are designed to provide a fair experience while more humans arrive.

> 🎯 **Important note:** Host rooms NEVER use bots. If the human minimum is not met, the room simply waits. Part of the art of hosting is knowing when to open a room to guarantee it fills up.

---

## Match Flow

Once matchmaking triggers the start, here is what happens in order:

### 1. Entry Fee Charged

The buy-in is deducted from each registered Axolotito's escrow. If you are **VIP Axolite**, you receive a **15% discount** on the buy-in. This discount is automatic and applies to both official and host rooms.

### 2. Energy Deduction

Each match consumes energy from your Axolotito:

- **Base cost:** 10 energy per match
- **Extra cost for salinity:** `round(SAL × 0.2)` additional
- **Total range:** 10 to 30 energy per match

An Axolotito with low SAL (0-10) pays 10-12 energy per match. One with high SAL (80-100) pays 26-30. Keeping salinity low not only improves your deck position — it also lets you play more matches per session.

### 3. Max Energy Decay

In addition to the per-match cost, your **max energy** decays by **3 points per match**. This simulates your Axolotito's accumulated fatigue. After several consecutive matches, your total energy capacity shrinks, eventually forcing you to rest.

### 4. The Gritón Calls

The 54-card deck is shuffled with cryptographic randomness (`SystemRandom`). The Gritón begins announcing cards one by one. The speed between cards depends on the room type:

| Room Type | Delay Between Cards | Vibe |
|-----------|---------------------|------|
| **Official** | Normal (fixed) | Classic Lotería rhythm |
| **Host Normal** | ~3-4 seconds | Relaxed, social |
| **Host Fast (0.6×)** | ~2 seconds | Brisk, keeps your attention |
| **Host Turbo (0.3×)** | ~1 second | Frenetic, pure adrenaline |

### 5. Two Prize Pools Per Match

Every multiplayer match has **two independent prize pools**, plus automatic contributions:

| Destination | Percentage of Pot | Notes |
|-------------|-------------------|-------|
| **Treasury (house)** | 5% | System fee, keeps the servers running |
| **Jackpot** | 5% | Accumulates in the global pool |
| **Host commission** | 5% | Only in host rooms. 0% in official rooms |
| **Premio 1** | 35% (30% with host) | First pattern completed |
| **Premio 2** | 55% | Full board — ¡Lotería! |

---

## Prize Distribution

### Premio 1 — First Pattern

**Condition:** be the first Board to complete **any of the winning patterns configured** for that room.

In official rooms, patterns include: horizontal line, vertical line, diagonal line, 4 corners, and central square (2×2). In host rooms, the host can choose exactly which patterns apply — it can be as restrictive ("diagonal only") or as generous ("all classic patterns") as they want.

**Distribution:** if multiple Boards complete the same winning pattern on the exact same card, the Premio 1 pool is split **equally** among all of them. If one Board completes a pattern on card 12 and another on card 15, the first one wins.

### Premio 2 — ¡Lotería! (Full Board)

**Condition:** be the first Board to fill **all 16 cells** (full board). This is classic Lotería — the shout of "¡Buenas!" that every player dreams of giving.

The Premio 2 pool is always **55%** of the total pot, regardless of whether there is a host or not. It is the big prize of every match.

**Can the same player win both prizes?** Yes! The Double Winner Rule allows it. If you complete a winning pattern first (Premio 1) AND are also the first to fill your entire board (Premio 2), you take both pools. It is rare, but when it happens... the entire room celebrates.

### Luck Bonus

All prizes (Premio 1, Premio 2, and Jackpot) receive a **SUERTE (Luck) bonus:**

```
final_share = base_share × (1 + axo_luck / 1000)
```

An Axolotito with 100 SUERTE receives a 10% bonus on its prize share. One with 200 SUERTE receives 20% extra. Luck does not make you win more often — but when you win, you win bigger.

---

## The Jackpot in Multiplayer

The Jackpot is the global accumulated pool that grows with every multiplayer match. For full details, see [[22-jackpot]], but here is the summary from a room perspective:

### Eligibility Requirements

- **Minimum 5 human Boards** registered in the room
- **Minimum 2 distinct wallets** among participants (anti-sybil: prevents a single person with multiple accounts from manipulating the system)

### Jackpot Trigger

The Jackpot activates only when **Premio 1 is won on cards 4, 5, or 6**. That is, someone completes a winning pattern extremely early in the match, when only the first few Gritón cards have been drawn. This requires a brutal combination of:
- A Board perfectly optimized for the pattern
- Extremely high OJO to avoid misses
- SUERTE for your cards to come out early
- Low SAL so you are not pushed to the end of the deck

### Jackpot Payout

- **90%** of the accumulated pool goes to the winner (or is split among simultaneous winners)
- **10%** is re-seeded for the next round
- If after re-seeding the Jackpot drops below **1,000 FRJ**, the game treasury automatically fills the gap
- **VIP Axolite** players receive a **+5% bonus** on their Jackpot winnings

> 🌟 Winning the Jackpot is the most epic achievement in Axolotto. Not just for the prize — but because it requires absolutely everything to go perfectly: your Board, your stats, and just the right moment of luck.

---

## Auto-Reinscription: Your Axolotito Never Sleeps

One of the most powerful multiplayer mechanics: you do not need to be glued to the screen. Once registered, your Axolotito can keep playing match after match automatically.

### Conditions for Auto-Reinscription

After each match, the system evaluates whether your Axolotito should automatically re-register for the next one. Conditions are:

1. **Stop-loss not hit** — your escrow balance is still above the loss limit you set
2. **Take-profit not hit** — your escrow balance has not reached the target gain
3. **Current energy >= 10** — enough energy for at least one more match
4. **Funds available for entry fee** — escrow covers the next match's buy-in
5. **Not manually recalled** — you did not press "Dejar de Jugar" (Stop Playing)

If all conditions are met, your Axolotito automatically re-registers and keeps playing. You can go to sleep, work, or whatever — your Axolotito stays there, marking cards, winning prizes.

### How to Exit: Dejar de Jugar (Stop Playing)

When you want to stop, click the **"Dejar de Jugar"** button. This does NOT pull your Axolotito out immediately — it finishes the current match and then stops. It is a graceful exit, not a rage-quit.

### Settlement

When your Axolotito ends its session (whether through stop-loss, take-profit, depleted energy, or manual withdrawal), it enters Settlement:

1. **Escrow balance returned to your wallet** — the FRJ you did not spend comes back to you
2. **Loyalty points awarded:**
   - **5 base points** for participating in the session
   - **+1 extra point per 10 FRJ of net profit**
   - Example: you finished with 150 FRJ net profit = 5 + 15 = 20 loyalty points
3. **Your Axolotito enters SLEEPING state** — it needs rest. During sleep, it recovers energy and reduces salinity. See [[02-axolotitos]] for the full sleep system.

---

## The Gritón (The Caller)

The Gritón is the soul of every match. It is the voice (system-generated) that announces cards one by one, setting the rhythm of the game.

### In Official Rooms

- Fully server-controlled
- Fixed speed (normal mode)
- No human intervention possible
- Same voice, same rhythm, for everyone

### In Host Rooms

The host configures the Gritón's speed when creating the room:

| Mode | Multiplier | Vibe |
|------|---------------|------|
| **Normal** | 1.0× | Classic. ~3-4 seconds between cards. Ideal for social rooms |
| **Fast** | 0.6× | ~2 seconds. Good pace without being overwhelming |
| **Turbo** | 0.3× | ~1 second. For those who want pure action |

### Manual Mode (Advanced)

In host rooms, there is a manual mode where the host can:
- Repeat the last announced card (to give extra time)
- Configure tie-breaking behavior (simultaneous first pattern)
- Briefly pause between cards to build tension

Manual mode is for advanced hosts who want to create a more theatrical, streamer-style experience.

---

## Host Reputation

Hosting does not only pay in FRJ — it also builds your reputation in the community.

### Reputation System

| Action | Reputation Earned |
|--------|-------------------|
| Host a completed match | +1 |
| Room filled at 80%+ capacity | +5 extra (total +6 for that match) |

**Practical example:** you have an 8-player room. If 7 or 8 slots fill (80%+), you earn +6 reputation per match. In one hour of a full turbo room, you can easily rack up +60 reputation.

### Benefits of High Reputation

- **Better lobby visibility:** host rooms with high reputation appear higher in listings
- **Host badge:** visual insignias showing your host level (Bronze, Silver, Gold, Axolite)
- **Community trust:** players prefer rooms from hosts with good reputation — they know the experience will be fair and fun
- **More traffic = more commissions:** it is a virtuous circle

---

## Multiplayer Strategy

A few quick tips to dominate the rooms:

### For Players

- **Register 3 Boards whenever possible** — you triple your chances of winning Premio 1. The extra cost is worth every FRJ.
- **Set stop-loss and take-profit thoughtfully** — a stop-loss that is too tight pulls you out early. A take-profit that is too ambitious never gets hit. Find your balance.
- **SAL matters more in multiplayer** — in CPU mode you can compensate low SAL with volume. In multiplayer, where everyone shares the same Gritón, low SAL is a real competitive advantage.
- **Choose the room speed that fits your style** — if you have good OJO but slow reflexes, play normal. If you trust your Board and want volume, go turbo.
- **Auto-reinscription is your friend** — set your limits, register, and let your Axolotito work. Check in every hour to adjust.

### For Hosts

- **Open rooms during peak hours** — less competition for visibility, more players looking for a match
- **Turbo with low buy-in attracts volume** — many players prefer 10 quick matches at 20 FRJ over one slow match at 200 FRJ
- **Decorate your Cuevita** — every decorative object is an investment in lobby visibility. It pays for itself with commissions
- **Be consistent** — a host who opens rooms regularly builds community. Players return to familiar rooms
- **Choose interesting patterns** — if you only accept diagonal as Premio 1, matches will be longer and tenser. If you accept all patterns, they will be faster and more chaotic. Find your niche.

---

## Quick Reference / Referencia Rápida

| Concept / Concepto | Value / Valor |
|---|---|
| Official rooms / Salas oficiales | Charco de Novatos (10 FRJ) · Fosa del Campeón (50 FRJ) |
| Max players official / Máx jugadores oficial | 30 |
| Host room buy-in range / Rango buy-in anfitrión | 10 – 1,000 FRJ |
| Host room players / Jugadores sala anfitrión | 2 – 8 |
| Speed modes / Modos de velocidad | Normal (1.0×) · Rápido (0.6×) · Turbo (0.3×) |
| Visibility options / Opciones de visibilidad | Pública · Amigos · Privada (contraseña) |
| Host commission / Comisión anfitrión | 5% del pozo / of pot |
| Max boards per player / Máx Tablas por jugador | 3 per room / por sala |
| Max total boards / Máx Tablas totales | 5 across all rooms / entre todas las salas |
| Matchmaking loop / Loop de matchmaking | 10 seconds / segundos |
| Instant start threshold / Arranque instantáneo | 30+ boards / Tablas |
| Bot fill threshold / Umbral de bots | < 4 human boards / Tablas humanas |
| Entry fee cost / Costo de entrada | Buy-in − 15% if VIP Axolite |
| Energy cost per match / Costo energía por partida | 10 + round(SAL × 0.2) → range 10-30 |
| Max energy decay / Decaimiento energía máx | −3 per match / por partida |
| Treasury fee / Comisión tesorería | 5% |
| Jackpot contribution / Contribución Jackpot | 5% |
| Premio 1 share / Porcentaje Premio 1 | 35% (30% with host / con host) |
| Premio 2 share / Porcentaje Premio 2 | 55% |
| Jackpot eligibility / Elegibilidad Jackpot | 5+ human boards + 2+ wallets · Premio 1 on cards 4-6 |
| Jackpot payout / Pago Jackpot | 90% winner · 10% reseed · min 1,000 FRJ floor |
| VIP Axolite Jackpot bonus | +5% on winnings / sobre ganancias |
| Luck bonus formula / Fórmula bonus suerte | base_share × (1 + luck / 1000) |
| Auto-reinscription check / Chequeo auto-reinscripción | Every match end / cada fin de partida |
| Auto-reinscription conditions / Condiciones | ¬stop-loss · ¬take-profit · energy ≥ 10 · funds ≥ entry · ¬recalled |
| Settlement loyalty / Lealtad settlement | 5 base + 1 per 10 FRJ net profit / ganancia neta |
| Post-session state / Estado post-sesión | SLEEPING |
| Host reputation base / Reputación base anfitrión | +1 per match / partida |
| Host reputation full room / Reputación sala llena | +5 extra (80%+ capacity / capacidad) |

---

→ See also / Ver también: [[06-como-jugar-loteria]] · [[08-modos-de-juego]] · [[07-patrones-ganadores]] · [[22-jackpot]] · [[02-axolotitos]] · [[00-INDEX]]
