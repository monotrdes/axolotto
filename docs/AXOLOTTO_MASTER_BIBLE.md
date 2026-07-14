# 🦎 AXOLOTTO — BIBLIA MAESTRA Y DOCUMENTO DE DISEÑO DE JUEGO (GDD)

Este documento consolidado y unificado representa la referencia definitiva sobre el concepto, lore, mecánicas, estadísticas, economía y arquitectura del proyecto **Axolotto** (un metaverso de lotería mexicana y crianza Web3). 

Está diseñado específicamente para ser importado en **NotebookLM** u otros modelos de lenguaje a fin de permitir discusiones profundas sobre balance, jugabilidad, estrategias y futuras adiciones.

---

## 1. Identidad y Concepto del Proyecto

### ¿Qué es Axolotto?
Axolotto es un juego de colección, crianza y lotería mexicana multijugador en tiempo real ambientado en los canales digitales de Xochimilco, México. Los jugadores crían **Axolotitos** (criaturas digitales únicas con genes on-chain en formato de NFT), construyen tableros de lotería (grillas de 4×4 cartas) y los envían a competir de forma automatizada (bot-play en segundo plano) o en lobbies multijugador activos para ganar premios en una economía de doble token.

### Los Tres Pilares de Jugabilidad
1. **Coleccionar:** Reunir las 54 cartas de la lotería tradicional mexicana en distintas rarezas y variantes holográficas (Foil).
2. **Criar:** Incubar Webitos (huevos) controlando la temperatura y el clima, y realizar el proceso de *Imprinting* (apadrinamiento) para heredar y mejorar las estadísticas.
3. **Competir:** Participar con tableros optimizados en salas de juego en tiempo real (Rookies o Campeones) para llevarse la bolsa de premios y el Jackpot de Oro.

---

## 2. El Lore y Escenario: Xochimilco Digital

### El Escenario
El metaverso transcurre en **Xochimilco**, el mítico sistema de canales y lagos de la Ciudad de México. Cada sección visual recrea este ecosistema:
- **Los Cenotes y Nidos:** Agua turquesa iluminada por haces de luz que se filtran desde la superficie, cuevas rocosas oscuras y burbujas ascendentes.
- **El Clima Dinámico:** Refleja las condiciones climáticas del servidor en tiempo real con cuatro fases diarias (Madrugada fría, Mañana fresca, Tarde cálida, Noche con neblina). Esto afecta directamente la tasa de pérdida de calor en la incubación y los bonos genéticos al nacer.
- **La Tradición de la Lotería:** El juego celebra el folclor mexicano de la lotería. Las cartas están ilustradas con arte neo-oscuro y los cantos son entonados por **El Gritón**, la voz misteriosa del cenote.

---

## 3. Los Axolotitos (Personajes)

Los Axolotitos son las mascotas coleccionables del jugador (NFTs ERC-721 en el contrato [Axolotitos.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/Axolotitos.sol)). Sus rasgos visuales y estadísticas iniciales se codifican en la blockchain mediante un número `uint256` (DNA).

### Los 4 Estados del Axolotito
- `idle` (Disponible): Listo para jugar, ser alimentado con consumibles o mandado a dormir.
- `playing` (En Partida): Compitiendo activamente en una sala de lotería o en la cola del lobby.
- `sleeping` (Durmiendo): Recuperando energía en un cooldown de sueño.
- `waiting_settlement` (Listo para Reporte): La sesión de juego ha concluido (por stop-loss, take-profit o falta de energía) y el Axolotito espera a que el jugador haga el "corte de caja".

### El Sistema de Reporte (Settlement)
Cuando el Axolotito entra en `waiting_settlement`, el jugador debe confirmar y agradecer su esfuerzo:
1. Se despliega una boleta con las victorias, derrotas, FRJ ganados/perdidos netos y XP obtenida.
2. Al hacer clic en **"¡Gracias por el esfuerzo! ❤️"**, los FRJ en custodia se transfieren a la cartera del jugador.
3. El Axolotito recibe **Puntos de Lealtad (Loyalty Points)** (5 puntos base + 1 punto por cada 10 FRJ netos ganados).
4. El Axolotito pasa al estado `sleeping` para restaurar su energía al 100%.

### Las 8 Estadísticas (Stats)
Definidas en el modelo [axolotito.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/axolotito.py):

| Stat | Campo de Código | Rango | Efecto en Juego |
| :--- | :--- | :--- | :--- |
| **Suerte (Luck)** | `stat_luck` | `0.0 – 100.0` | Aumenta el multiplicador de premios críticos y la probabilidad de un *Lucky Save*. |
| **Concentración (Focus)**| `stat_focus` | `0.0 – 100.0` | Reduce la probabilidad de que el Axolotito falle al marcar una carta cantada. |
| **Energía (Stamina)** | `stat_stamina` | `50 – 200` | Determina el límite de energía máxima (`energy_current`). |
| **Salinidad (Salinity)** | `stat_salinity` | `0.0 – 100.0` | Factor de mala suerte hereditaria; influye negativamente en la cría. |
| **Agilidad** | `stat_agility` | `0.0 – 100.0` | Vinculada directamente al Focus (`agility = focus`) en crianza. |
| **Carisma** | `stat_charisma` | `0.0 – 100.0` | Fijo en `0.0` al nacer. Diseñado para descuentos en tiendas (futuro). |
| **Sabiduría** | `stat_wisdom` | `0.0 – 100.0` | Fijo en `0.0` al nacer. Diseñado para mitigar eventos climáticos (futuro). |
| **Fuerza** | `stat_strength` | `0.0 – 100.0` | Fijo en `0.0` al nacer. Diseñado para resistencia ante eventos negativos (futuro). |

> [!NOTE]
> Actualmente, las estadísticas operativas principales son **Luck, Focus, Stamina y Salinity**. Las estadísticas secundarias (*Agility, Charisma, Wisdom, Strength*) están preparadas en el modelo de base de datos para futuras expansiones de juego de destreza.

### Fórmulas Matemáticas de Juego
Definidas en el motor lógico [game_logic.py](file:///d:/Axolotto_2026/axolotto/backend/app/services/game_logic.py):

#### 1. Probabilidad de Fallo de Marcado (Miss Chance)
Determina la tasa a la que el Axolotito "olvida" marcar una carta cantada en su tablero:
$$\text{miss\_chance} = \max\left(0.0, \min\left(0.3, (100.0 - \text{focus}) \times 0.003\right)\right)$$
- **Focus 100:** Miss Chance = 0.0% (Marcado perfecto).
- **Focus 80 (Bot Campeón):** Miss Chance = 6.0%.
- **Focus 50 (Jugador promedio):** Miss Chance = 15.0%.
- **Focus 40 (Bot Novato):** Miss Chance = 18.0%.
- **Focus 0:** Miss Chance = 30.0% (Límite máximo).

#### 2. Salvada Afortunada (Lucky Save)
Probabilidad única por partida de anular un evento de juego desfavorable:
$$\text{lucky\_save\_chance} = \left(\frac{\text{luck}}{1000.0}\right) \times 0.5$$
- **Luck 100 (Máximo):** 5.0% de probabilidad.
- **Luck 50:** 2.5% de probabilidad.
- **Luck 0:** 0.0% de probabilidad.

### Personalidades (Natures)
Al eclosionar, cada Axolotito recibe una de las siguientes naturalezas en [imprinting_service.py](file:///d:/Axolotto_2026/axolotto/backend/app/services/imprinting_service.py):
- **Metódico (`methodical`):** Multiplica por $1.25$ los incrementos de Focus durante el Imprinting. Consume 10% más energía por partida.
- **Suertudo (`lucky`):** Multiplica por $1.25$ los incrementos de Luck en la cría. -5% de Agilidad base.
- **Hiperactivo (`hyperactive`):** Multiplica por $1.25$ los incrementos de Stamina. Recupera energía 20% más rápido al dormir, pero tiene 10% de probabilidad extra de fallar cartas en partida (penalización a Focus).
- **Glotón (`glutton`):** Mitiga pérdidas genéticas; si el padrino pierde la partida, los deltas de imprinting negativos se reducen al 80%.

---

## 4. Los Webitos y el Sistema de Crianza (Imprinting)

Los Axolotitos nacen de Webitos (NFTs ERC-721 en [Webitos.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/Webitos.sol)). Su ciclo se divide en incubación básica y apadrinamiento genético.

### El Proceso de Incubación
En la base de datos se modela a través de `WebitoIncubation` (en [items.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/items.py)):
- **Incubación Básica (Cariñitos):** El jugador puede interactuar con el huevo bajo tres acciones con cooldowns específicos para acumular bonos al nacer:
  - **Acariciar (Petting):** Cooldown de 4 horas. Otorga `bonus_strength` y `bonus_agility`.
  - **Cantarle (Singing):** Cooldown de 8 horas. Otorga `bonus_wisdom` y `bonus_focus`.
  - **Alimentar (Feeding):** Cooldown de 12 horas. Otorga `bonus_stamina` y `bonus_luck`.
- **Temperatura y Clima:** El huevo inicia con 100% de calor. Pierde calor cada hora según las inclemencias del clima de Xochimilco. Si el calor cae a 0%, el Webito entra en estado congelado (`is_frozen = True`), pausando su incubación. Los jugadores pueden calentar el huevo usando FRJ o equipando consumibles como el *Escudo Anti-Escarcha*.
- **Eclosión:** Una vez transcurrido el tiempo (normalmente 7 días), el huevo pulsa en rosa y eclosiona al tapearlo, generando el nuevo Axolotito.

### El Sistema de Apadrinamiento (Imprinting)
Consiste en asignar un Axolotito adulto como padrino (`imprinting_padrino_id`). El padrino juega partidas mientras tutela al Webito, transmitiéndole estadísticas base y deltas dinámicos basados en su propio rendimiento.

#### 1. Cantidad de Partidas Requeridas por Rareza del Webito
- **Común (Common):** 3 partidas.
- **Raro (Rare):** 5 partidas.
- **Épico (Epic) / Legendario (Legendary):** 7 partidas.

#### 2. Herencia Genética Base
Al iniciar el apadrinamiento, el Webito recibe estadísticas aleatorias sumadas a un porcentaje de las estadísticas del padrino:
$$\text{Webito Stat Base} = \text{Random\_Range} + \left(\text{Padrino Stat} \times \text{Factor}\right)$$

| Stat | Rango Aleatorio | Factor (Padrino Nivel $\le$ 20) | Factor (Padrino Nivel $>$ 20) |
| :--- | :--- | :--- | :--- |
| **Luck** | `20.0 – 50.0` | $0.10$ | $0.15$ |
| **Focus** | `25.0 – 55.0` | $0.10$ | $0.15$ |
| **Stamina** | `70.0 – 110.0` | $0.10$ | $0.15$ |
| **Salinity** | `10.0 – 30.0` | $0.10$ | $0.15$ |

> [!TIP]
> Entrenar y subir de nivel al Axolotito padrino por encima del nivel 20 incrementa la herencia del 10% al 15%, asegurando crías sustancialmente más fuertes.

#### 3. Deltas Acumulativos por Partida del Padrino
Cada partida jugada por el padrino modifica el ADN del Webito en desarrollo antes de sellarse:
- **Suerte (`luck_delta`):**
  - Si el padrino gana la partida: $+[8.0 \dots 15.0]$
  - Si el padrino pierde: $-[8.0 \dots 12.0]$
  - Si el padrino se lleva el Jackpot: $+20.0$ fijo.
- **Concentración (`focus_delta`):**
  - Si la precisión de marcado (Accuracy) del padrino es $\ge 80\%$: $+[10.0 \dots 18.0]$
  - Si es $\le 50\%$: $-[8.0 \dots 14.0]$
  - Si la energía del padrino está por encima de $80\%$: $+5.0$ extra.
- **Energía (`stamina_delta`):**
  - Si la sesión de juego del padrino fue $\ge 3$ partidas: $+[10.0 \dots 15.0]$
  - Si solo fue 1 partida (sesión corta): $-5.0$
  - Si la energía del padrino está por encima de $80\%$: $+8.0$ extra.
- **Salinidad (`salinity_delta`):**
  - Si la salinidad del padrino es baja ($< 20.0$): $-[6.0 \dots 10.0]$ (reduce salinidad, lo cual es positivo).
  - Si la salinidad es alta ($> 50.0$): $+[8.0 \dots 12.0]$
  - Si la precisión del padrino es pésima ($< 40\%$): $+5.0$ extra.

> [!IMPORTANT]
> Todos los deltas acumulados tienen límites estrictos de control de balance (*clamps*): la suerte, concentración y salinidad no pueden modificarse más de $\pm 50.0$, mientras que la estamina está limitada a $\pm 60.0$.

---

## 5. El Nido: Tu Cenote Habitado

El Nido es la interfaz inmersiva 2.5D construida con capas de profundidad CSS y físicas dinámicas.
- **Nidos de Incubación:** Cuenta con **7 slots de cuevas** (3 traseras y 4 delanteras en perspectiva). Los colores de las cuevas indican de forma inmediata el estatus del huevo (naranja = cálido; azul = congelado/frío; dorado = protegido con escudo; rosa pulsante = listo para eclosión).
- **Mascotas Libres:** Los Axolotitos eclosionados nadan de fondo a frente en un bucle orgánico con posiciones y tamaños aleatorios calculados dinámicamente. Al hacer tap en cualquiera, se accede a su ficha técnica.

---

## 6. Cartas y Tableros de Lotería

### Las Cartas de Lotería
Existen **54 cartas maestras** de la Lotería Mexicana (NFTs ERC-1155 en [CartasLoteria.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/CartasLoteria.sol)), divididas en rarezas: *Común (Common)*, *Poco Común (Uncommon)*, *Rara (Rare)*, *Épica (Epic)* y *Legendaria (Legendary)*.
- **Variante Brillante (Foil):** Cartas holográficas con efectos visuales de arcoíris. Los tableros equipados con cartas Foil incrementan permanentemente el yield del staking de FRJ ($+5\%$ por carta foil, acumulable hasta $+80\%$).

### Los Tableros (Tablas)
Un Tablero es una grilla de 4×4 cartas (NFT ERC-721 en [TablasLoteria.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/TablasLoteria.sol)) que se puede crear de dos formas:
1. **Aleatorio:** Cuesta **130 FRJ** (25 GAL históricos). Selecciona 16 cartas al azar del inventario.
2. **Manual (Editor):** Cuesta **520 FRJ** (50 GAL históricos). Permite colocar y posicionar estratégicamente las cartas.

#### Otras Operaciones de Tableros:
- **Card Melter (Forja):** Permite fundir 5 cartas del mismo nivel y rareza más un pago en FRJ para forjar 1 carta de rareza superior, actuando como el principal sumidero inflacionario de cartas duplicadas.
- **Desarmar Tablero (Dissolve):** Cuesta **50 FRJ**. Destruye de forma aleatoria 1 de las 16 cartas del tablero; las otras 15 vuelven al inventario del usuario.
- **Rentas de Tableros (Scholarships):** Los propietarios pueden rentar sus tableros por periodos de 24 horas en el mercado P2P. Establecen una tarifa fija en FRJ y un porcentaje (%) de compartición de ganancias en las partidas de lotería que el arrendatario gane.

---

## 7. Mecánicas de Juego y Multijugador

El núcleo competitivo es la Lotería Mexicana en tiempo real. La grilla del tablero se lee en formato row-major (índices 0 a 15):
```
 0   1   2   3
 4   5   6   7
 8   9  10  11
12  13  14  15
```

### Hitos y Condiciones de Victoria
1. **Premio 1 (Hito 1 - Línea o Cuadrito):** Se lleva el **35% de la bolsa total** de la sala. Se otorga al primero en completar una línea recta de 4 celdas (filas, columnas o diagonales) o un cuadrito de 2×2 adyacente (9 variantes).
2. **Premio 2 (Hito 2 - Tabla Llena o "¡Lotería!"):** Se lleva el **55% de la bolsa total**. Se entrega al primer tablero en marcar las 16 celdas de su cuadrícula. Esto finaliza la partida.
3. **El Jackpot de Oro:** Se lleva el **90% del pozo acumulado global**. Es un jackpot acumulativo global que inicia con una semilla mínima de 1,000 FRJ. 
   - **Condición de Activación:** Se debe completar el Hito 1 en un tiempo récord: **dentro de las primeras 4, 5 o 6 cartas cantadas**.
   - **Medidas Anti-Sybil:** Para evitar abusos en salas privadas, la partida debe tener al menos **5 tableros controlados por humanos** pertenecientes a mínimo **2 carteras únicas**. Los bots no son elegibles para activar el Jackpot.

### Estructura de Lobbies y Matchmaking
- **Matchmaking Timeout:** El temporizador de inicio es de 30 segundos una vez inscrito el primer participante.
- **Cupo de Sala:** Límite máximo de **30 tableros** por sala para mantener la distribución matemática de probabilidades.
- **Relleno de Bots:** Si al expirar los 30 segundos hay menos de 4 jugadores inscritos, la sala se completa con bots virtuales para iniciar la partida inmediatamente.

### Las Salas Oficiales

| Sala | Dificultad | Cuota de Entrada (Buy-in) | Recompensa Ganador | Patrones Activos | XP (Win / Loss) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Charco de Novatos (`rookie_pool`)** | Fácil | 25 FRJ | 85 FRJ (+8 de consolación) | Líneas y Cuadritos | 35 / 8 (Axo) · 25 / 8 (Board) |
| **Fosa del Campeón (`champion_abyss`)**| Difícil | 100 FRJ | 400 FRJ (+20 de consolación)| Líneas, Cuadritos, Pocito, Esquinas | 75 / 15 (Axo) · 60 / 15 (Board) |

---

## 8. Economía Dual y Tokenomics

El metaverso de Axolotto se rige por un sistema balanceado de dos divisas, protegiendo al ecosistema de la hiperinflación.

```
                  ┌──────────────────────────────┐
                  │ DINERO FIAT / CRYPTO ON-RAMP │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  AXF (Axofichas)      │ ◄───[ Retiro P2P (DevEx) ]
                     │  Hard Currency - EVM  │
                     └───────────┬───────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ ACTIVOS PERMANENTES ]         [ COMPRA DE PAQUETES ]
    Webitos, VIP, Sobrecitos Foil           Banco de Algas
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │  FRJ (Frijolitos)     │
                                     │  Soft Utility Token   │
                                     └───────────┬───────────┘
                                                 │
                 ┌─────────────────────────┼─────────────────────────┐
                 ▼                         ▼                         ▼
         [ JUEGO ACTIVO ]         [ SUMIDEROS DE FRJ ]       [ STAKING PASIVO ]
      Buy-ins, Multijugador     Cueva, Gashapon, Alimento    Emisión de tableros
```

### 1. Axofichas (AXF) — Moneda Premium "Hard"
- **Naturaleza:** Token ERC-20 implementado en la Plasma Chain (cadena de pruebas EVM, chain ID 9746). 
- **Adquisición:** Exclusivamente mediante SPEI, pago en OXXO, tarjeta de crédito o criptomonedas directas (USDC/USDT/ETH).
- **Usos:** Compra de Webitos, pases de membresía VIP, boosters foil premium y paquetes de conversión de Frijolitos.

### 2. Frijolitos (FRJ) — Moneda de Utilidad "Soft"
- **Naturaleza:** Token de utilidad para el bucle activo de juego (buy-ins, consumibles del criadero, rolls de Gashapón y comisiones de mercado).
- **Adquisición:** Se obtiene ganando partidas de lotería, mediante el staking pasivo de tableros en reposo o comprando paquetes en el banco utilizando AXF.

#### Conversión del Banco de Algas (AXF $\to$ FRJ):
- **Alga Común:** 10 AXF $\to$ 100 FRJ
- **Alga Abundante:** 50 AXF $\to$ 600 FRJ (+$20\%$ gratis)
- **Alga Imperial:** 100 AXF $\to$ 1,500 FRJ (+$50\%$ gratis)
- **Súper Carga:** 250 AXF $\to$ 4,000 FRJ (+$60\%$ gratis)

### Modelo de Reserva 80/20
Toda compra de AXF se respalda financieramente de la siguiente manera:
- **16%:** Impuesto (IVA) en México.
- **4.5%:** Comisión de pasarela de pago.
- **79.5% Neto Restante:** Se divide bajo una regla estricta:
  - **80%:** Cuenta de Reserva de Garantía (fondos bloqueados para respaldar retiros reales de jugadores, evitando insolvencia).
  - **20%:** Cuenta de Tesorería Operativa (costos de servidores, marketing y mantenimiento).

### El Sistema de Retiros (DevEx)
Los jugadores que vendan activos en el mercado P2P por AXF pueden retirar ganancias reales (pesos o stablecoins):
- **KYC Obligatorio** y filtros PLD/AML para cumplimiento legal.
- **Período de retención (Hold):** 14 días naturales anti-fraude para validar transacciones secundarias.
- **Spread de Retiro:** La tasa de recompra se establece al 70% del valor de venta (el 30% restante actúa como amortización de liquidez del pool y retención fiscal aproximada del 7% en México).

### Staking Pasivo de Tableros
Los tableros que no están participando en partidas generan FRJ/hora basándose en la rareza de sus cartas y su nivel:
$$\text{hourly\_rate\_frj} = \left(\sum \text{rarity\_bonus\_cards}\right) \times \left(1.0 + \frac{\text{board.level}}{10.0}\right)$$

- **Bonos por Rareza de Carta:**
  - *Común (Common) / Poco Común (Uncommon):* 0.05 FRJ/h.
  - *Rara (Rare):* 0.15 FRJ/h.
  - *Épica (Epic):* 0.40 FRJ/h.
  - *Legendaria (Legendary):* 1.00 FRJ/h.
- **Play-to-Stake:** El propietario debe haber jugado al menos **1 partida en las últimas 24 horas** (evaluado con `user.last_play_date`). Si el usuario está inactivo, el yield acumulado cae a 0.
- **Límite de Acumulación (Cap):** El reclamo tiene un tope máximo de **12 horas acumuladas** (`MAX_ACCUMULATION_HOURS`). El jugador debe cobrar periódicamente para no pausar su generación.
- **Slots Disponibles:** La capacidad de tableros simultáneos en staking está determinada por el nivel del Cenote: $\text{Slots} = \text{Cave\_Level} + 1$.

---

## 9. Tianguis (Tienda) y Máquina Gashapón

### Catálogo del Tianguis
Ofrece boosters de cartas en tres fases cronológicas del metaverso:
- **Fase 1 (First Edition):** Fiesta/Nido/Cosmos = 10 AXF o 100 FRJ. Pure = 6 AXF o 60 FRJ.
- **Fase 2 (Unlimited):** Fiesta/Nido/Cosmos = 15 AXF o 150 FRJ. Pure = 10 AXF o 100 FRJ.
- **Fase 3 (Standard):** Fiesta/Nido/Cosmos = 20 AXF o 200 FRJ. Pure = 15 AXF o 150 FRJ.
- **Booster Brillante (Foil):** 80 AXF o 800 FRJ.
- **Consumibles:** Gotas Anti-Escarcha (200 FRJ), Lámpara Infrarroja (200 AXF), Algae Pellet (30 FRJ), Brine Shrimp (150 FRJ), Solvente (120 FRJ), Upgrade de Slots (300 AXF).

### La Máquina Gashapón
Funciona a través de `capsule_service.py` ([capsule_service.py](file:///d:/Axolotto_2026/axolotto/backend/app/services/capsule_service.py)). El sistema cuenta con breakpoints de roll acumulados:

| Tier de Cápsula | Costo (FRJ) | Pity (Garantía Huevo) | Drop Pool (FRJ / Carta / Acc / Booster / Huevo) |
| :--- | :--- | :--- | :--- |
| **Bronce** | 1,500 | 10 rolls | $45\% \ / \ 30\% \ / \ 10\% \ / \ 10\% \ / \ 5\%$ |
| **Plata** | 5,000 | 5 rolls | $20\% \ / \ 45\% \ / \ 15\% \ / \ 10\% \ / \ 10\%$ |
| **Oro** | 20,000 | 3 rolls | $5\% \ / \ 40\% \ / \ 20\% \ / \ 10\% \ / \ 25\%$ |

- **Descuento Triple Suerte:** El triple roll de Gashapón cuesta **22,500 FRJ** (descuento del 15% comparado con la compra individual de los tres tiers).
- **Rango de FRJ Otorgados:** Bronce = $[50 \dots 150]$; Plata = $[200 \dots 600]$; Oro = $[500 \dots 3,000]$.
- **Pity Reset:** El contador de pity vuelve a 0 al obtener un Webito, una Tabla Forjada o un Booster Foil del pre-check legendario.
- **Pre-check Legendario:** Probabilidad marginal por tirada de evadir el pool estándar y entregar un Booster Foil directo (Bronce = $0.2\%$, Plata = $0.5\%$, Oro = $1.0\%$).

---

## 10. Expansión de la Cueva (El Cenote)

La progresión de la cueva aumenta la capacidad de la granja del jugador (slots de staking, decoración y mesas).

| Nivel | Nombre | Spots Axo (Staking) | Mesa / Asientos | Excavación (Horas) | Costo (FRJ) | Huevo Recompensa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | El Nicho | 1 (2 slots) | No / 0 | — | Gratis | — |
| **2** | La Gruta | 2 (3 slots) | No / 0 | 2.0 h | 500 | Fase 1 |
| **3** | La Caverna | 3 (4 slots) | Sí / 2 | 6.0 h | 1,500 | Fase 1 Plus (Raro/Épico) |
| **4** | El Salón | 4 (5 slots) | Sí / 4 | 12.0 h | 4,000 | Fase 2 |
| **5** | El Santuario | 5 (6 slots) | Sí / 6 | 24.0 h | 8,000 | Fase 2 Nature |
| **6** | El Abismo | 6 (7 slots) | Sí / 8 | 36.0 h | 15,000 | Fase 2 Nature |
| **7** | El Templo | 7 (8 slots) | Sí / 8 | 48.0 h | 30,000 | Astral |
| **8** | Palacio Astral | 8 (9 slots) | Sí / 8 | 72.0 h | 60,000 | Astral |

> [!TIP]
> Los jugadores con membresía VIP activa reciben un **50% de descuento en el costo de FRJ** y un **50% de reducción en el tiempo** de excavación.

### Requisitos de Logros para Expandir:
- **Nivel 2:** 10 partidas jugadas totales y Axolotito principal $\ge$ nivel 3.
- **Nivel 3:** 3 victorias totales y racha de 3 días consecutivos jugando.
- **Nivel 4:** Al menos 1 Jackpot ganado.
- **Nivel 5:** Axolotito principal $\ge$ nivel 15.
- **Nivel 6:** (50 partidas totales y 100 alimentaciones) O ser VIP (Coral, Dorado o Axolite).
- **Nivel 7:** (100 partidas totales y 15 victorias) O ser VIP (Dorado o Axolite).
- **Nivel 8:** (200 partidas totales y poseer un Axolotito con skin `gold` o `astral`) O ser VIP (Axolite).

### Bonus Pasivos Acumulativos:
- **Nivel 2:** `gal_multiplier: 1.02` (+2% de Frijolitos ganados en salas).
- **Nivel 3:** `extra_starting_card: True` (+1 carta en la mano inicial).
- **Nivel 4:** `booster_chance_bonus: 0.05` (+5% de drop de boosters tras partidas).
- **Nivel 5:** `global_incubation_slot: 1` (+1 ranura de incubación de Webitos).
- **Nivel 6:** `p2p_fee_reduction: 0.05` (-5% de comisión en compras del marketplace).
- **Nivel 7:** `monthly_foil_booster: 1` (1 booster foil gratis al mes).
- **Nivel 8:** `axg_multiplier: 1.10` (+10% de ganancia de AXF en eventos/drops).

---

## 11. Membresías VIP (El Club VIP)

Las membresías duran 30 días y se gestionan en [config.py](file:///d:/Axolotto_2026/axolotto/backend/app/core/config.py):

| Beneficio | Pase Coral | Pase Dorado | Pase Axolite |
| :--- | :--- | :--- | :--- |
| **Costo (AXF)** | 400 AXF | 600 AXF | 1,800 AXF |
| **FRJ Reclamables Diarios**| +40 FRJ / día | +100 FRJ / día | +200 FRJ / día |
| **Descuento en Tienda** | 5% | 12% | 20% |
| **Slots de Tablero Extras** | 0 | +1 slot | +2 slots |
| **Slots de Axolotitos Extras**| 0 | 0 | +1 slot (Límite a 7) |
| **Comisión del Mercado P2P**| 4% (vs 5% normal) | 3% | 1.5% |
| **Descuento en Match Fees**| 0% | 0% | 15% |
| **Bono de Jackpot** | 0% | 0% | +5% adicional |
| **FRJ de Entrada (Welcome)**| +200 FRJ | +500 FRJ | +1,000 FRJ |
| **Cajas y Boosters** | 2x Cápsulas Bronce | 2x Bronce, 1x Plata, 1x Booster Normal | 3x Bronce, 2x Plata, 1x Oro, 1x Booster Foil |
| **Visuales** | Marco Coral turquesa | Marco Dorado con corona | Marco Axolite rotativo con partículas |

- **Expiración VIP:** Si el VIP caduca, las tablas o Axolotitos extra en slots bonus quedan **congelados** (`is_frozen_by_vip = True`). El jugador no pierde sus NFTs, pero no puede enviarlos a jugar ni en staking hasta renovar la suscripción.
- **Rachas de Membresía:** Se recompensa la lealtad acumulada sin resetearse al cambiar de tier (3 meses: insignia "Constante"; 6 meses: marco exclusivo "Veterano"; 12 meses: título "Axolotto Original" + 1 Webito Astral gratis; 24 meses: marco legendario "Leyenda del Nido").

---

## 12. Ciclo Lunar (Racha Diaria)

El Ciclo Lunar regula el reclamo diario de recompensas para fomentar la retención:
- **Días 1 a 6:** Entrega cantidades incrementales de soft currency: $50 \to 65 \to 80 \to 95 \to 110 \to 130$ FRJ.
- **Día 7:** Entrega una cápsula de Gashapón basada en la Luna (semana) activa del usuario:
  - *Luna 1:* 1x Cápsula Bronce.
  - *Luna 2:* 2x Cápsulas Bronce.
  - *Luna 3:* 1x Cápsula Plata.
  - *Luna 4:* 1x Plata + 1x Bronce.
  - *Luna 5:* 2x Cápsulas Plata.
  - *Luna 6:* 1x Cápsula Oro.
- **Reglas de Racha:** 
  - Retraso de 1 día: La racha continúa.
  - Retraso de 2 a 7 días: El día de la racha vuelve a 0, pero conserva la semana lunar actual.
  - Retraso mayor a 7 días: El ciclo se reinicia por completo a la semana Luna 1 y el día 0.

---

## 13. Balance, Estrategias y Retos (Para Discutir con el LLM)

Esta sección recopila los problemas de balance y dinámicas de juego identificados en el código y simulaciones, esenciales para la discusión estratégica en el Notebook:

### A. Balance de Estadísticas y Meta de Juego
- **La Salinidad:** Actualmente, la salinidad actúa como una estadística de mala suerte que incrementa los eventos negativos o deltas negativos en el apadrinamiento. Sin embargo, no hay consumibles comunes para reducirla (el *Solvente de Pegamento* limpia accesorios, no salinidad). Esto hace que Axolotitos con alta salinidad queden obsoletos rápidamente. **Discusión:** ¿Debería introducirse un método para "purificar" la salinidad mediante la quema de FRJ o un ritual en el Cenote?
- **Desuso de Stats Secundarios:** Las estadísticas de *Carisma, Sabiduría y Fuerza* existen en los modelos de base de datos pero se fijan en `0.0` en la eclosión, y no se usan en las fórmulas principales de victoria. **Discusión:** ¿Cómo diseñar mecánicas de eventos dinámicos en las salas de juego avanzadas para darles uso (ej: Fuerza reduce el daño por fango, Sabiduría reduce la tensión crítica)?

### B. La Inflación de Frijolitos (FRJ)
- **Staking vs. Juego Activo:** Un tablero con cartas legendarias en nivel alto genera una cantidad masiva de FRJ/hora pasivos, limitados solo por la regla de jugar 1 partida cada 24 horas. Si la tasa de generación de FRJ supera con creces la velocidad de quema (consumo de comida, desmontaje de tableros, rolls de Gashapón), el mercado P2P sufrirá hiperinflación de soft currency. **Discusión:** ¿Cuáles son los sumideros de FRJ most effective que se pueden añadir sin alienar a los jugadores F2P? (Ej. Forjar decoraciones estéticas para el cenote, torneos especiales en salas con buy-ins hiper-elevados).

### C. Estrategia de Scholarships (Alquiler de Tablas)
- Dado que los dueños de tableros definen libremente la cuota fija en FRJ y el porcentaje de ganancias, hay riesgo de que jugadores veteranos monopolicen el mercado de becas ofreciendo tarifas sumamente bajas que destruyan el incentivo para que los nuevos jugadores compren sus propias cartas. **Discusión:** ¿Debe el orquestador fijar límites dinámicos (pisos/techos) a las rentas basados en el promedio móvil de victorias del tablero?

### D. Explotación de Bots en Salas Rookie
- Las salas Rookie tienen fees muy bajos (25 FRJ) y se rellenan con bots si faltan jugadores reales. Un jugador malintencionado podría desplegar múltiples cuentas F2P con Axolotitos de baja concentración que aprovechen el autojuego masivo en salas Rookie para farmear FRJ de forma pasiva a coste casi cero. **Discusión:** ¿Cómo optimizar el filtro de detección y limitar las recompensas en salas Rookie cuando hay un exceso de tableros virtuales/bots en la partida?

### E. Flujo Corcholata (Onboarding de Landing Page)
- El kit de bienvenida del flujo físico entrega **139 AXF** y **1,000 FRJ**. El 139 es intencional: tras jugar 13 partidas clásicas (130 AXF), al jugador le quedan 9 AXF, quedándose a solo 1 AXF de poder jugar otra partida, lo que incentiva la primera microtransacción o la interacción con el banco de conversión. **Discusión:** ¿Cómo asegurar que este enganche inicial se traduzca en una conversión a largo plazo (VIP o compra de Webitos) sin generar frustración?

---

## 14. Referencia de Modelos e Infraestructura Técnica

### Estructura de la Base de Datos
- **Usuarios ([user.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/user.py)):** Almacena saldos de `axf_balance` y `frj_balance`, nivel de cueva (`cave_level`), estado VIP (`vip_tier`, `vip_expires_at`) e historial de logins (`last_play_date`).
- **Axolotitos ([axolotito.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/axolotito.py)):** Registra el ADN (`dna_sequence`), nivel, XP, estados de juego, energía y estadísticas funcionales.
- **Incubación de Webitos ([items.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/items.py)):** Controla el estado térmico (`calor_actual`), clicks de cariño, progreso de apadrinamiento genético (`imprinting_games_played`, `imprinting_complete`) y el ID del padrino tutor.
- **Tableros (PlayerBoard en [board.py](file:///d:/Axolotto_2026/axolotto/backend/app/models/board.py)):** Registra el mapeo de 16 cartas, nivel del tablero, XP, estado de venta/renta y variables de staking.

### Arquitectura Blockchain (Plasma Chain)
El juego realiza llamadas on-chain a contratos Solidity desplegados localmente sobre Anvil/Plasma (puerto 8545):
- [Axolotitos.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/Axolotitos.sol) realiza el acuñamiento (minting) al eclosionar y almacena los metadatos de ADN.
- [GameController.sol](file:///d:/Axolotto_2026/axolotto/contracts/src/GameController.sol) valida las firmas y orquesta las transferencias de activos en el mercado P2P y las quemas/emisiones de divisas resultantes de la compra de boosters.
- La comunicación off-chain/on-chain es manejada por el servicio web3 de FastAPI en `web3_service.py` ([web3_service.py](file:///d:/Axolotto_2026/axolotto/backend/app/services/web3_service.py)).
