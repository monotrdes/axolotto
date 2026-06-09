---
tags: [conceptos, economia, mercado, p2p]
description: "Mercado P2P de Axolotto — compra y venta entre jugadores, subasta de cartas, tablas y Axolotitos, sistema de comisiones VIP y renta de tablas | Axolotto P2P Marketplace — player-to-player trading, card & board auctions, VIP commission system and board rentals"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Mercado P2P — Compra y Venta Entre Jugadores

El **Mercado P2P de Axolotto** es un bazar impulsado por los jugadores donde TÚ pones los precios. Compra y vende cartas individuales, tableros completos, Axolotitos y accesorios. Todo se comercia en **FRJ**, la moneda de juego. Es el corazón de la economía circular de Axolotto: los jugadores crean valor y otros jugadores lo compran.

---

## ¿Qué Puedes Vender?

El mercado acepta cinco tipos de artículos:

| Tipo de artículo | ¿Es NFT on-chain? | Notas |
|---|---|---|
| **Cartas individuales** | No (off-chain) | De tu colección personal. Las cartas foil valen 5-50x más |
| **Tableros completos** | Sí (ERC-721) | Transferencia on-chain del NFT [[10-tablas]] |
| **Axolotitos** | Sí (ERC-721) | Solo se recomienda vender duplicados — ¡necesitas al menos 1 para jugar! |
| **Accesorios y cosméticos** | No (off-chain) | Marcos, skins, decoraciones de cueva |
| **Sobrecitos sellados** | No (off-chain) | Boosters sin abrir — atractivos para compradores que buscan la emoción del unboxing |

---

## Publicar un Artículo

Publicar un artículo en el mercado es gratis y sin penalización por cancelar.

### Proceso de publicación

1. Abre tu **Inventario**
2. Selecciona el artículo que quieres vender
3. Pulsa **"Publicar en Mercado"**
4. Configura los parámetros de venta (varían según el tipo)

### Parámetros por tipo de artículo

**Cartas individuales:**
- Precio de venta en FRJ
- La carta queda bloqueada (no se puede usar en tableros mientras esté listada)

**Tableros completos:**
- Precio de venta en FRJ
- Opciones de renta (ver sección Renta de Tableros más abajo)
- El tablero se retira de tus slots activos al listarlo
- Si el tablero tiene staking activo, el staking se pausa automáticamente

**Axolotitos:**
- Precio de venta en FRJ
- El Axolotito debe tener al menos **24 horas de enfriamiento** desde su última partida
- No puedes vender tu último Axolotito (necesitas al menos 1 para jugar)
- Las stats, naturaleza y rasgos visuales se muestran en el listing

**Sobrecitos sellados:**
- Precio de venta en FRJ
- El sobrecito no puede estar abierto (obviamente)

### Gestión de listings

- Tu artículo permanece listado **hasta que se venda o lo canceles**
- Puedes cancelar un listing en cualquier momento sin costo ni penalización
- Al cancelar, el artículo vuelve inmediatamente a tu inventario
- Puedes modificar el precio de un listing activo sin necesidad de cancelarlo y volverlo a publicar

---

## Comisiones del Mercado (Commission)

El mercado cobra una pequeña comisión sobre cada venta para mantener la economía saludable. La comisión **la paga el vendedor** (se descuenta del precio de venta).

### Tabla de Comisiones por Nivel VIP

| Estatus VIP | Comisión de Venta | Comisión de Renta | Destino Venta | Destino Renta |
|---|---|---|---|---|
| Sin VIP | 5% | 5% | TreasuryVault | Quemado (BURN) |
| Coral | 4% | 4% | TreasuryVault | Quemado (BURN) |
| Dorado | 3% | 3% | TreasuryVault | Quemado (BURN) |
| Axolite | 1.5% | 1.5% | TreasuryVault | Quemado (BURN) |
| Cueva Nivel 6+ | -5% adicional | -5% adicional | — | — |

### Entendiendo las comisiones

- **Comisión de venta:** Va al **TreasuryVault** (la tesorería del juego). Estos FRJ se reinvierten en premios de jackpot, eventos especiales y recompensas comunitarias. No desaparecen — circulan de vuelta al ecosistema.
- **Comisión de renta:** Se **QUEMA** (se destruye permanentemente). Esto reduce la oferta total de FRJ en circulación y ayuda a controlar la inflación. Los FRJ quemados desaparecen para siempre del ecosistema.
- **Bonus de Cueva Nivel 6+:** Los jugadores con Cueva nivel 6 o superior reciben una reducción adicional de 5 puntos porcentuales en ambas comisiones. Este bonus se **acumula** con el descuento VIP.

### Ejemplo de cálculo

Vendes una carta Legendaria Foil por **10,000 FRJ**:

| Tu nivel | Comisión | Recibes |
|---|---|---|
| Sin VIP | 5% = 500 FRJ | 9,500 FRJ |
| Coral | 4% = 400 FRJ | 9,600 FRJ |
| Dorado | 3% = 300 FRJ | 9,700 FRJ |
| Axolite | 1.5% = 150 FRJ | 9,850 FRJ |
| Axolite + Cueva 6+ | -3.5% → 0% (mínimo) | 10,000 FRJ |

> **Importante:** La comisión efectiva nunca baja de 0%. No hay comisiones "negativas" — el mercado no te paga por vender.

---

## Renta de Tableros (Scholarship)

El sistema de renta de tableros es una de las mecánicas más innovadoras y populares del Mercado P2P. Permite a dueños de tableros generar ingresos pasivos y a jugadores sin buenos tableros acceder a equipo de alto nivel.

### Cómo funciona

1. **El dueño configura la renta:**
   - Precio de renta en **FRJ por 24 horas**
   - Porcentaje de ganancias que recibe el dueño si el rentador gana partidas (**owner share %**)
2. **El rentador paga el precio** y recibe el tablero por 24 horas
3. **Si el rentador gana partidas** con ese tablero, el dueño recibe su porcentaje de las ganancias
4. Al terminar las 24 horas, el tablero vuelve automáticamente al dueño

### Ejemplo de renta

- Dueño lista el tablero "Destructor Estelar" (CSR 78%):
  - Precio de renta: **200 FRJ / 24h**
  - Owner share: **15%**
- Rentador paga 200 FRJ y juega durante 24 horas
- El rentador gana 3 partidas Champions: 3 x 400 = **1,200 FRJ** en premios
- El dueño recibe 15% de 1,200 = **180 FRJ** adicionales
- **Dueño gana:** 200 + 180 = 380 FRJ | **Rentador gana:** 1,200 - 200 - 180 = 820 FRJ netos

### Win-win para ambos

- **Dueño:** Ingreso pasivo sin jugar. Mientras más gane el rentador, más gana el dueño — incentivo alineado.
- **Rentador:** Acceso a tableros premium que no podría construir todavía. Ideal para nuevos jugadores o para probar builds antes de comprar.

### Rentar desde el Ranking

Puedes rentar tableros directamente desde la **tabla de clasificaciones (Rankings)**. Los tableros con alto CSR (win rate) y buen historial de staking aparecen destacados. Esto hace que el mercado sea transparente — los mejores tableros son visibles para todos.

---

## Comprar Artículos

El proceso de compra está diseñado para ser simple pero seguro.

### Flujo de compra

1. **Explora el mercado** — lista infinita con scroll, filtrable por:
   - Tipo de artículo (cartas, tableros, Axolotitos, accesorios, sobres)
   - Rareza (Común, Rara, Épica, Legendaria)
   - Estado foil (normal, foil)
   - Rango de precio en FRJ
   - Ordenar por: precio (asc/desc), rareza, fecha de publicación
2. **Encuentra tu artículo** y revisa sus detalles
3. **Mantén presionado para confirmar** (hold-to-confirm) — evita compras accidentales
4. Los **FRJ se descuentan de tu wallet**
5. El artículo aparece en tu **inventario** inmediatamente
6. Si es un NFT (tablero, Axolotito), la **transferencia on-chain** se ejecuta automáticamente

### Requisitos para transferencias NFT

Para comprar o vender artículos que son NFTs (tableros, Axolotitos), **tanto el comprador como el vendedor** deben tener una wallet vinculada a su cuenta. Si alguna de las partes no tiene wallet, la transacción se rechaza con un mensaje explicativo.

---

## Seguridad del Mercado

El Mercado P2P está diseñado con múltiples capas de protección para que todas las transacciones sean seguras:

- **Escrow del servidor:** Todas las transacciones son mediadas por el servidor del juego. No hay transferencias directas wallet-a-wallet — el juego actúa como intermediario de confianza.
- **Artículos bloqueados al listar:** Un artículo listado en el mercado no puede usarse en partidas, staking ni otras mecánicas mientras esté a la venta. Esto evita conflictos y duplicaciones.
- **Transferencias atómicas:** Las transferencias on-chain son todo-o-nada. Si algún paso falla, la transacción completa se revierte. No existe el estado intermedio donde "el comprador pagó pero no recibió el NFT".
- **Sin riesgo de estafa:** Como el juego media todo, no hay forma de que un vendedor "se lleve el dinero y no entregue el artículo" ni de que un comprador "reciba el artículo y no pague".

---

## Tips Para el Mercado P2P

### Para vendedores

- **Revisa los precios del mercado antes de fundir cartas.** Una carta duplicada puede valer mucho más en el mercado que los materiales que obtendrías al fundirla. Compara siempre.
- **Las cartas foil raras se venden por 5 a 50 veces más** que su contraparte común. No las fundas por accidente.
- **Los tableros con alto CSR (win rate)** pueden cobrar precios premium en renta. Un CSR de 60%+ ya es atractivo para rentadores.
- **El mejor momento para vender es durante eventos especiales**, cuando la demanda sube por la emoción y las recompensas limitadas.
- **Incluye una buena descripción** en tu listing. Los compradores confían más en vendedores que detallan lo que ofrecen.

### Para compradores

- **El mejor momento para comprar es en horas valle** (madrugada o días entre semana), cuando hay menos competencia y los vendedores bajan precios.
- **Usa los filtros.** Con cientos o miles de listings, los filtros son tu mejor amigo para encontrar exactamente lo que buscas.
- **Renta antes de comprar.** Si estás considerando comprar un tablero caro, renta uno similar primero para ver si se adapta a tu estilo de juego.
- **Compara precios.** El mismo tipo de carta puede tener precios muy distintos entre vendedores. Tómate tu tiempo.

### Regla de oro

**Nunca vendas tu último Axolotito.** Necesitas al menos 1 Axolotito para jugar. Si vendes tu último, te quedarás sin poder participar en partidas hasta que incube uno nuevo o compre otro.

---

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
