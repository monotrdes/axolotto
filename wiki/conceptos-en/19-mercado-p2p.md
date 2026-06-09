## English

# P2P Marketplace — Player-to-Player Trading

The **Axolotto P2P Market** is a player-driven bazaar where YOU set the prices. Buy and sell individual cards, complete boards, Axolotitos, and accessories. Everything is traded in **FRJ**, the in-game currency. It is the heart of Axolotto's circular economy: players create value and other players buy it.

---

## What Can You Sell?

The marketplace accepts five item types:

| Item Type | On-chain NFT? | Notes |
|---|---|---|
| **Individual cards** | No (off-chain) | From your personal collection. Foil cards are worth 5-50x more |
| **Complete boards** | Yes (ERC-721) | On-chain NFT transfer — [[10-tablas]] |
| **Axolotitos** | Yes (ERC-721) | Only sell duplicates — you need at least 1 to play! |
| **Accessories & cosmetics** | No (off-chain) | Frames, skins, cave decorations |
| **Sealed boosters** | No (off-chain) | Unopened sobres — attractive for buyers seeking the unboxing thrill |

---

## Listing an Item

Listing an item is free with no penalty for cancelling.

### Listing process

1. Open your **Inventory**
2. Select the item you want to sell
3. Click **"Publicar en Mercado"** (Publish to Market)
4. Configure the sale parameters (varies by item type)

### Parameters by item type

**Individual cards:**
- Sale price in FRJ
- The card gets locked (cannot be used on boards while listed)

**Complete boards:**
- Sale price in FRJ
- Rental options (see Board Rental section below)
- The board is removed from your active slots upon listing
- Active staking is automatically paused

**Axolotitos:**
- Sale price in FRJ
- The Axolotito must have at least a **24-hour cooldown** since its last match
- You cannot sell your last Axolotito (at least 1 required to play)
- Stats, nature, and visual traits are shown on the listing

**Sealed boosters:**
- Sale price in FRJ
- The booster must not be opened (obviously)

### Managing listings

- Your item stays listed **until sold or cancelled**
- Cancel anytime with zero cost or penalty
- Upon cancellation, the item returns to your inventory immediately
- You can modify a listing's price without cancelling and re-publishing

---

## Market Fees (Commission)

The market charges a small commission on each sale to keep the economy healthy. The commission is **paid by the seller** (deducted from the sale price).

### Commission Table by VIP Status

| VIP Status | Sale Commission | Rental Commission | Sale Destination | Rental Destination |
|---|---|---|---|---|
| No VIP | 5% | 5% | TreasuryVault | Burned (BURN) |
| Coral | 4% | 4% | TreasuryVault | Burned (BURN) |
| Dorado | 3% | 3% | TreasuryVault | Burned (BURN) |
| Axolite | 1.5% | 1.5% | TreasuryVault | Burned (BURN) |
| Cave Lvl 6+ | Additional -5% | Additional -5% | — | — |

### Understanding the fees

- **Sale commission:** Goes to the **TreasuryVault** (game treasury). These FRJ are reinvested into jackpot prizes, special events, and community rewards. They do not disappear — they circulate back into the ecosystem.
- **Rental commission:** Is **BURNED** (permanently destroyed). This reduces the total FRJ supply in circulation and helps control inflation. Burned FRJ vanish from the ecosystem forever.
- **Cave Level 6+ Bonus:** Players with Cave level 6 or higher receive an additional 5 percentage point reduction on both commissions. This bonus **stacks** with the VIP discount.

### Calculation example

You sell a Legendary Foil card for **10,000 FRJ**:

| Your level | Commission | You receive |
|---|---|---|
| No VIP | 5% = 500 FRJ | 9,500 FRJ |
| Coral | 4% = 400 FRJ | 9,600 FRJ |
| Dorado | 3% = 300 FRJ | 9,700 FRJ |
| Axolite | 1.5% = 150 FRJ | 9,850 FRJ |
| Axolite + Cave 6+ | -3.5% → 0% (minimum) | 10,000 FRJ |

> **Important:** The effective commission never drops below 0%. There are no "negative" commissions — the market does not pay you to sell.

---

## Board Rental (Scholarship)

The board rental system is one of the most innovative and popular mechanics in the P2P Market. It allows board owners to generate passive income and players without good boards to access high-level equipment.

### How it works

1. **Owner configures the rental:**
   - Rental price in **FRJ per 24 hours**
   - Percentage of winnings the owner receives if the renter wins matches (**owner share %**)
2. **Renter pays the price** and receives the board for 24 hours
3. **If the renter wins matches** with that board, the owner gets their percentage of the winnings
4. After 24 hours, the board automatically returns to the owner

### Rental example

- Owner lists the board "Stellar Destroyer" (CSR 78%):
  - Rental price: **200 FRJ / 24h**
  - Owner share: **15%**
- Renter pays 200 FRJ and plays for 24 hours
- Renter wins 3 Champion matches: 3 x 400 = **1,200 FRJ** in prizes
- Owner receives 15% of 1,200 = **180 FRJ** additional
- **Owner earns:** 200 + 180 = 380 FRJ | **Renter earns:** 1,200 - 200 - 180 = 820 FRJ net

### Win-win for both

- **Owner:** Passive income without playing. The more the renter wins, the more the owner earns — aligned incentives.
- **Renter:** Access to premium boards they couldn't build yet. Ideal for new players or testing builds before buying.

### Rent from Rankings

You can rent boards directly from the **leaderboard (Rankings)**. Boards with high CSR (win rate) and good staking history are featured. This keeps the market transparent — the best boards are visible to everyone.

---

## Buying Items

The purchase process is designed to be simple yet secure.

### Purchase flow

1. **Browse the market** — infinite scroll list, filterable by:
   - Item type (cards, boards, Axolotitos, accessories, boosters)
   - Rarity (Common, Rare, Epic, Legendary)
   - Foil status (normal, foil)
   - FRJ price range
   - Sort by: price (asc/desc), rarity, publication date
2. **Find your item** and review its details
3. **Hold-to-confirm** — prevents accidental purchases
4. **FRJ deducted from your wallet**
5. Item appears in your **inventory** immediately
6. If it's an NFT (board, Axolotito), the **on-chain transfer** happens automatically

### NFT transfer requirements

To buy or sell NFT items (boards, Axolotitos), **both buyer and seller** must have a wallet linked to their account. If either party lacks a wallet, the transaction is rejected with an explanatory message.

---

## Market Safety

The P2P Market is designed with multiple layers of protection so all transactions are secure:

- **Server escrow:** All transactions are mediated by the game server. No direct wallet-to-wallet transfers — the game acts as a trusted intermediary.
- **Items locked when listed:** A listed item cannot be used in matches, staking, or other mechanics while for sale. This prevents conflicts and duplication.
- **Atomic transfers:** On-chain transfers are all-or-nothing. If any step fails, the entire transaction is reverted. There is no intermediate state where "the buyer paid but didn't receive the NFT."
- **No scam risk:** Since the game mediates everything, there is no way for a seller to "take the money and not deliver" or for a buyer to "receive the item and not pay."

---

## P2P Market Tips

### For sellers

- **Check market prices before melting cards.** A duplicate card may be worth far more on the market than the materials from melting it. Always compare.
- **Rare foil cards sell for 5 to 50 times more** than their common counterparts. Don't melt them by accident.
- **Boards with high CSR (win rate)** command premium rental prices. A 60%+ CSR is already attractive to renters.
- **The best time to sell is during special events**, when demand spikes due to excitement and limited rewards.
- **Include a good description** in your listing. Buyers trust sellers who detail what they offer.

### For buyers

- **The best time to buy is during off-peak hours** (late night or weekdays), when there is less competition and sellers lower prices.
- **Use the filters.** With hundreds or thousands of listings, filters are your best friend for finding exactly what you need.
- **Rent before buying.** If you are considering an expensive board, rent a similar one first to see if it fits your playstyle.
- **Compare prices.** The same card type can have very different prices between sellers. Take your time.

### Golden rule

**Never sell your last Axolotito.** You need at least 1 Axolotito to play. If you sell your last one, you will be unable to participate in matches until you incubate a new one or buy another.

---

## Quick Reference / Referencia Rápida

| Concept / Concepto | Value / Valor |
|---|---|
| Market currency / Moneda del mercado | FRJ (Frijolitos) |
| Base sale commission / Comisión base de venta | 5% → TreasuryVault |
| Base rental commission / Comisión base de renta | 5% → Burned (quemado) |
| Coral commission / Comisión Coral | 4% venta, 4% renta |
| Dorado commission / Comisión Dorado | 3% venta, 3% renta |
| Axolite commission / Comisión Axolite | 1.5% venta, 1.5% renta |
| Cave Lvl 6+ bonus / Bonus Cueva Nvl 6+ | -5% adicional (se acumula con VIP) |
| Minimum commission / Comisión mínima | 0% (nunca negativa) |
| Listing fee / Costo de publicar | Gratis (sin costo) |
| Cancellation penalty / Penalización por cancelar | Ninguna |
| Rental duration / Duración de renta | 24 horas |
| Axolotito sell cooldown / Enfriamiento para venta | 24 horas desde última partida |
| Purchase confirmation / Confirmación de compra | Hold-to-confirm (mantener presionado) |
| NFT transfer requirement / Requisito transferencia NFT | Ambas partes necesitan wallet vinculada |
| Best time to sell / Mejor momento para vender | Durante eventos especiales |
| Best time to buy / Mejor momento para comprar | Horas valle (madrugada / entre semana) |
| Sale commission destination / Destino comisión venta | TreasuryVault (tesorería) |
| Rental commission destination / Destino comisión renta | Burned / Quemado (anti-inflación) |

---

→ See also / Ver también: [[09-cartas]] · [[10-tablas]] · [[12-economia-dual]] · [[15-vip-club]] · [[20-staking-ingresos-pasivos]] · [[22-jackpot]] · [[00-INDEX]]
