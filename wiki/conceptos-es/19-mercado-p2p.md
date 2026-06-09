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

