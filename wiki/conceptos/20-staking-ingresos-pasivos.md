---
tags: [conceptos, economia, staking]
description: "Staking en Axolotto — genera FRJ pasivo con tus tablas y Axolotitos | Staking in Axolotto — earn passive FRJ with your boards and Axolotitos"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Staking — Ingresos Pasivos de FRJ

El staking es la fuente de ingresos pasivos mas estable de Axolotto. Mientras tus tablas no estan jugando y tus Axolotitos estan inactivos, generan Frijolitos (FRJ) automaticamente. No hay riesgo: no importa si ganas o pierdes partidas, el staking produce FRJ igual. Es la base economica que permite a los jugadores financiar su gameplay diario — entradas a partidas, comida para Axolotitos, capsulas — sin depender exclusivamente de los premios de cada ronda.

Hay dos tipos de staking que funcionan simultaneamente: **Staking de Tablas** y **Staking de Axolotitos**. Ambos se acumulan. Un jugador con buenas tablas y una coleccion de Axolotitos fuertes puede generar cientos de FRJ al dia sin mover un dedo... bueno, casi. Porque hay una regla importante: la regla **Play-to-Stake**.

## Staking de Tablas

Cualquier tabla que NO este jugando una partida activa puede ponerse en staking. La tasa de generacion depende de dos factores: la rareza de sus 16 cartas y el nivel de la tabla. El nivel de la tabla multiplica la tasa base: el multiplicador es `1 + 0.1 x nivel`. Una tabla nivel 20 genera el triple que una tabla nivel 1. Ademas, cada carta foil en la tabla otorga un **+5% de rendimiento adicional**, acumulable hasta un maximo de +80% si las 16 cartas son foil. Una tabla completamente foil de nivel alto es una maquina de imprimir FRJ.

Para cobrar, ve a tu inventario y haz clic en "Cobrar" sobre la tabla, o usa "Cobrar Todo" para reclamar todas las tablas de una vez. Hay un limite de acumulacion de **24 horas**: si no reclamas en ese plazo, el FRJ excedente se pierde. No lo dejes pasar.

**Regla Play-to-Stake para Tablas**: debes haber jugado al menos 1 partida en cualquier modo en las ultimas 24 horas. Si no, el staking se pausa hasta que vuelvas a jugar. Esto asegura que el staking sea una recompensa por participar activamente en el ecosistema, no un mecanismo de "farm and forget".

## Staking de Axolotitos

Los Axolotitos que no estan jugando ni durmiendo pueden asignarse a los espacios de staking dentro de tu cueva (el Cenote). La cantidad de espacios disponibles depende del nivel de tu cueva: `nivel_cueva + 1` espacios. Una cueva nivel 8 te da 9 espacios para stakear Axolotitos simultaneamente.

La tasa de generacion de cada Axolotito se calcula a partir de **dos factores combinados**: la rareza de su skin (cuerpo base) y la rareza de sus 6 partes individuales (ojos, branquias, cresta, cola, aletas, patron). La skin define la tasa base por hora, y cada parte anade un bonus adicional.

### Multiplicadores de Skin (tasa base por hora)

| Rareza de Skin | FRJ/hora |
|----------------|----------|
| Comun (rosa, gris) | 0.05 |
| Rara (cyan, morado) | 0.15 |
| Epica (neon, coral) | 0.40 |
| Legendaria (oro) | 1.00 |
| Astral | 2.50 |

### Bonos por Parte (cada una de las 6 partes suma)

| Rareza de Parte | FRJ/hora por parte |
|-----------------|---------------------|
| Rasgo Comun | 0.01 |
| Rasgo Raro | 0.03 |
| Rasgo Epico | 0.08 |
| Rasgo Legendario | 0.20 |

### Como se calcula la tasa horaria

Se parte de la tasa base de la skin y se suman los bonos de las 6 partes. Luego, el nivel del Axolotito aplica un multiplicador: `1 + 0.1 x nivel`. Cada nivel aumenta el rendimiento un 10%.

**Ejemplo con un Axolotito Epico nivel 15**:
- Skin Epica (neon): 0.40 FRJ/h base
- Partes: 3 raras + 2 epicas + 1 legendaria = 3x0.03 + 2x0.08 + 1x0.20 = 0.09 + 0.16 + 0.20 = 0.45 FRJ/h en bonos
- Base total: 0.40 + 0.45 = 0.85 FRJ/h
- Con nivel 15: 0.85 x (1 + 0.1 x 15) = 0.85 x 2.5 = 2.125 FRJ/h
- Por dia: 2.125 x 24 = **51 FRJ/dia**
- Con 8 Axolotitos similares stakedos: aproximadamente **400 FRJ/dia**

**Ejemplo Legendario Completo (mejor caso realista)**:
- Skin Legendaria Oro: 1.00 FRJ/h
- 6 partes Legendarias: 6 x 0.20 = 1.20 FRJ/h
- Base total: 2.20 FRJ/h
- Nivel 30: 2.20 x (1 + 0.1 x 30) = 2.20 x 4.0 = 8.8 FRJ/h
- Por dia: 8.8 x 24 = **211 FRJ/dia por Axolotito**
- Con 9 stakedos: aproximadamente **1,900 FRJ/dia** — ahora si estamos hablando en serio

**Ejemplo Astral (maximo absoluto)**:
- Skin Astral: 2.50 FRJ/h
- 6 partes Legendarias: 1.20 FRJ/h
- Base total: 3.70 FRJ/h
- Nivel 30: 3.70 x 4.0 = 14.8 FRJ/h
- Por dia: **355 FRJ/dia por Axolotito**

## Regla Play-to-Stake

Esta regla aplica a AMBOS tipos de staking. Debes jugar al menos **1 partida en cualquier modo** en las ultimas 24 horas. Si no juegas, el staking se pausa completamente hasta que vuelvas a participar. Esto no es un castigo — es un recordatorio de que Axolotto es un juego de habilidad y competencia, no una inversion pasiva. El staking recompensa a quienes participan activamente.

## Limites de Acumulacion

| Tipo de Staking | Limite de acumulacion | Frecuencia optima de cobro |
|-----------------|-----------------------|----------------------------|
| Tablas | 24 horas | 1 vez al dia |
| Axolotitos | 12 horas | 2 veces al dia |

El FRJ no reclamado que exceda el limite se **PIERDE**. Si dejas un Axolotito Legendario 30 sin cobrar por 24 horas, solo recibiras 12 horas de FRJ — el resto desaparece. Pon una alarma o entra a cobrar en la manana y en la noche.

## Como Maximizar tus Ingresos Pasivos

- **Expande tu cueva**: mas espacios de staking = mas Axolotitos generando FRJ simultaneamente. Una cueva nivel 8 te da 9 espacios.
- **Cria por rasgos raros**: skins Astrales y Legendarias, y partes Legendarias, multiplican dramaticamente las tasas. Cada cruza es una inversion a largo plazo.
- **Sube de nivel a tus Axolotitos**: cada nivel es +10% de rendimiento. Un nivel 30 cuadruplica la tasa base.
- **Construye tablas foil**: cada carta foil en la tabla suma +5% al rendimiento. Una tabla 100% foil rinde +80%.
- **Juega a diario**: manten activa la regla Play-to-Stake. Una partida rapida es suficiente.
- **Cobra regularmente**: no dejes que los limites de acumulacion desperdicien tu FRJ.
- **El VIP ayuda indirectamente**: mas espacios de tablas, mas espacios de Axolotitos, expansion de cueva mas rapida.

## Por Que Stakeear?

El staking es el ingreso de FRJ mas estable del juego. No depende de ganar partidas, no tiene riesgo de perder, y escala con todo lo que haces en Axolotto: jugar, criar, mejorar tu coleccion. Los jugadores de endgame pueden financiar todo su gameplay — entradas, comida, capsulas, crianza — unicamente con staking. Y lo mejor: funciona en segundo plano mientras tu te diviertes jugando.

---

## English

Staking is Axolotto's most stable source of passive income. It works in two simultaneous layers: **Board Staking** and **Axolotito Staking**. Both generate Frijolitos (FRJ) automatically while your assets sit idle. There is zero risk — staking yields FRJ regardless of match outcomes. Active players can fund their entire daily gameplay (entry fees, food, capsules, breeding) from staking alone.

**Board Staking** kicks in for any board not currently in an active game. The rate depends on the rarity of its 16 cards plus the board's level, which applies a multiplier of `1 + 0.1 x level` — a level 20 board generates 3x the base rate of a level 1 board. Foil cards each add +5% yield, stacking up to +80% with all 16 foil. The accumulation cap is 24 hours; claim via "Cobrar" on the board or "Cobrar Todo" for all at once.

**Axolotito Staking** assigns idle axolotitos to cave slots (cave_level + 1 slots, up to 9 at level 8). The hourly rate combines the Skin multiplier (Common: 0.05, Rare: 0.15, Epic: 0.40, Legendary: 1.00, Astral: 2.50 FRJ/h) with bonuses from each of the 6 body parts (Common: 0.01, Rare: 0.03, Epic: 0.08, Legendary: 0.20 FRJ/h per part). The axolotito's level then multiplies the total by `1 + 0.1 x level`. A full Legendary level 30 yields 211 FRJ/day; a full Astral reaches 355 FRJ/day. Stack 8-9 of these in a high-level cave for thousands of FRJ daily. The accumulation cap is 12 hours — claim twice daily for optimal yield.

The **Play-to-Stake rule** applies to both types: you must play at least 1 game in any mode within the last 24 hours, or staking pauses. This keeps staking tied to active participation — Axolotto rewards players, not idle farmers. Unclaimed FRJ beyond the accumulation cap is lost, so set reminders and claim regularly.

Maximize your passive income by expanding your cave for more staking slots, breeding for Astral/Legendary skins and parts, leveling up your axolotitos (+10% yield per level), building foil-heavy boards (+5% per foil card), playing daily to keep Play-to-Stake active, and claiming before caps expire. VIP status helps indirectly through more board slots, more axo slots, and faster cave expansion.

## Quick Reference / Referencia Rapida

| Concept / Concepto | Value / Valor |
|---|---|
| Tipos de staking | Tablas + Axolotitos (simultaneos) |
| Staking types | Boards + Axolotitos (simultaneous) |
| Multiplicador por nivel (tablas y axos) | 1 + 0.1 x nivel |
| Level multiplier (boards and axos) | 1 + 0.1 x level |
| Bonus por carta foil en tabla | +5% cada una (max +80%) |
| Foil card bonus per board | +5% each (max +80%) |
| Limite acumulacion tablas | 24 horas |
| Board accumulation cap | 24 hours |
| Limite acumulacion Axolotitos | 12 horas |
| Axolotito accumulation cap | 12 hours |
| Skin Astral (tasa base) | 2.50 FRJ/h |
| Astral Skin (base rate) | 2.50 FRJ/h |
| Skin Legendaria (tasa base) | 1.00 FRJ/h |
| Legendary Skin (base rate) | 1.00 FRJ/h |
| Skin Epica (tasa base) | 0.40 FRJ/h |
| Epic Skin (base rate) | 0.40 FRJ/h |
| Skin Rara (tasa base) | 0.15 FRJ/h |
| Rare Skin (base rate) | 0.15 FRJ/h |
| Skin Comun (tasa base) | 0.05 FRJ/h |
| Common Skin (base rate) | 0.05 FRJ/h |
| Parte Legendaria (bonus) | 0.20 FRJ/h cada una |
| Legendary Part (bonus) | 0.20 FRJ/h each |
| Parte Epica (bonus) | 0.08 FRJ/h cada una |
| Epic Part (bonus) | 0.08 FRJ/h each |
| Parte Rara (bonus) | 0.03 FRJ/h cada una |
| Rare Part (bonus) | 0.03 FRJ/h each |
| Parte Comun (bonus) | 0.01 FRJ/h cada una |
| Common Part (bonus) | 0.01 FRJ/h each |
| Espacios de staking en cueva | nivel_cueva + 1 |
| Cave staking slots | cave_level + 1 |
| Regla Play-to-Stake | 1 partida cada 24h |
| Play-to-Stake rule | 1 game every 24h |
| Mejor Axolotito realista (Legendario 30) | ~211 FRJ/dia |
| Best realistic Axolotito (Legendary 30) | ~211 FRJ/day |
| Mejor Axolotito absoluto (Astral 30) | ~355 FRJ/dia |
| Absolute best Axolotito (Astral 30) | ~355 FRJ/day |
| FRJ no reclamado excedente | Se PIERDE |
| Excess unclaimed FRJ | LOST |

---

→ See also / Ver tambien: [[10-tablas]] · [[02-axolotitos]] · [[05-rasgos-visuales-y-rareza]] · [[16-el-cenote-cueva]] · [[00-INDEX]]
