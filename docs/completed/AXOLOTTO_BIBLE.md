# AXOLOTTO — Biblia del Juego

> **Documento maestro de referencia.** Cubre: concepto, mundo, personajes, mecánicas, economía, legalidad, arquitectura técnica y visión de producto. Todo miembro del equipo, colaborador o socio debe leer este documento antes de contribuir al proyecto.
>
> **Última actualización:** 2026-05-28
> **Ver también:** `GDD.md` (roadmap de fases), `monetizacion_tokenomics.md` (modelo financiero), `vip_club_design.md` (sistema VIP), `legal_y_liquidez.md` (marco legal), `nido_design.md` (diseño del cenote), `design_critique_report.md` (análisis de UX)

---

## Tabla de Contenidos

1. [Concepto y Visión](#1-concepto-y-visión)
2. [El Mundo: Xochimilco Digital](#2-el-mundo-xochimilco-digital)
3. [Los Axolotitos — Tus Personajes](#3-los-axolotitos--tus-personajes)
4. [Los Webitos — Huevos Coleccionables](#4-los-webitos--huevos-coleccionables)
5. [El Nido — Tu Cenote Personal](#5-el-nido--tu-cenote-personal)
6. [Las Cartas de Lotería](#6-las-cartas-de-lotería)
7. [Los Tableros — Tu Herramienta de Juego](#7-los-tableros--tu-herramienta-de-juego)
8. [El Juego: Lotería en Tiempo Real](#8-el-juego-lotería-en-tiempo-real)
9. [La Economía Dual: AXG y COR](#9-la-economía-dual-axg-y-cor)
10. [La Tienda y el Mercado P2P](#10-la-tienda-y-el-mercado-p2p)
11. [El Gashapón](#11-el-gashapón)
12. [El Club VIP](#12-el-club-vip)
13. [Los Rankings](#13-los-rankings)
14. [Por Qué es Legal](#14-por-qué-es-legal)
15. [Cómo Entrar al Juego](#15-cómo-entrar-al-juego)
16. [Arquitectura Técnica](#16-arquitectura-técnica)
17. [Hoja de Ruta y Visión Futura](#17-hoja-de-ruta-y-visión-futura)

---

## 1. Concepto y Visión

### ¿Qué es Axolotto?

Axolotto es un **juego de colección, crianza y lotería** ambientado en los cenotes de Xochimilco, México. Los jugadores crían Axolotitos — criaturas digitales únicas basadas en el ajolote mexicano (*Ambystoma mexicanum*) — los personalizan, construyen tableros de lotería con cartas coleccionables, y los envían a competir automáticamente en salas de juego en tiempo real.

Es un juego **Web3** construido sobre blockchain, lo que significa que los activos del jugador (Axolotitos, cartas, tableros) son NFTs que el jugador posee de verdad y puede vender, rentar o intercambiar en el mercado P2P. Sin embargo, no es necesario entender blockchain para jugar — el juego abstrae toda la complejidad técnica.

### Los Tres Pilares

```
COLECCIONAR          CRIAR               JUGAR
───────────          ─────               ─────
54 cartas de    →   Incubar huevos  →   Enviar Axolotitos
lotería             criar Axolotitos     a salas de lotería
únicas              con genes únicos     automáticas
```

### Propuesta de Valor Única

1. **Lotería mexicana digitalizada** — El juego más tradicional de México, reimaginado como un juego de estrategia con economía real.
2. **Tu mascota juega por ti** — No tienes que estar presente. El Axolotito juega solo mientras tú haces otra cosa; tú revisas el resultado cuando quieras.
3. **Activos que son tuyos de verdad** — A diferencia de otros juegos donde los ítems "desaparecen" si el juego cierra, tus NFTs viven en la blockchain.
4. **Economía sostenible** — Diseñada desde cero para no repetir los errores de Axie Infinity o STEPN. El modelo econímico prioriza la diversión y el coleccionismo sobre la especulación.
5. **Identidad cultural** — El ajolote es un símbolo de México en peligro de extinción. Axolotto lo convierte en protagonista digital, celebrando su existencia.

### Para Quién es Axolotto

| Tipo de Jugador | Qué obtiene |
|---|---|
| **El coleccionista** | 54 cartas únicas, Axolotitos con genes irrepetibles, variantes Brillante/Holográficas |
| **El estratega** | Optimizar tableros, combinar stats de Axolotitos con tipos de sala, gestión de economía |
| **El pasivo** | El Axolotito juega solo; el jugador revisa ganancias/pérdidas cuando quiere |
| **El social** | Mercado P2P, rentas de tableros, rankings globales, salas multijugador |
| **El inversor casual** | Sistema de renta pasiva de tableros; VIP con ROI positivo garantizado |

---

## 2. El Mundo: Xochimilco Digital

### El Escenario

El mundo de Axolotto está inspirado en **Xochimilco** — la zona lacustre de Ciudad de México, Patrimonio de la Humanidad, hogar natural del ajolote. Cada rincón del juego refleja este ecosistema:

- **Los cenotes** son el hábitat del Nido: agua azul-verdosa, rayos de luz filtrándose desde la superficie, burbujas de aire subiendo, paredes de roca oscura.
- **El clima** refleja las condiciones reales de Xochimilco: madrugadas frías, tardes cálidas, noches con neblina. Este clima afecta directamente la incubación de los huevos.
- **Las cartas de lotería** son las 54 figuras tradicionales de La Lotería mexicana, con arte original.

### Filosofía de Diseño Visual

El juego utiliza una estética **dark neon** — fondos casi negros con brillos de neón en rosa, teal, dorado y violeta. Cada sección del juego tiene su propio color dominante para facilitar la orientación:

| Sección | Color |
|---|---|
| Tienda | Rosa hot `#E4007C` |
| Cartas | Índigo `#818CF8` |
| Tableros | Esmeralda `#34D399` |
| El Nido | Teal `#2DD4BF` |
| Rankings | Ámbar `#FBBF24` |
| Gashapón | Violeta `#A855F7` |

### La Visión 2.5D

El estado actual del juego es 2D. La visión a futuro es convertir cada sección en un **entorno 2.5D habitable** — el jugador "camina" por el mundo de Xochimilco, moviéndose físicamente de zona en zona:

```
[Mercado]  ←──→  [El Cenote/Nido]  ←──→  [Sala de Lotería]
    ↕                    ↕                        ↕
[Gashapón]  ←──→  [Galería/Inventario]  ←──→  [Arena/Rankings]
                         ↕
                    [Club VIP]
```

El **Nido** ya implementa esta visión de referencia: una escena con capas de profundidad CSS, axolotitos animados nadando libremente, cuevas con estados visuales dinámicos, y clima en tiempo real.

---

## 3. Los Axolotitos — Tus Personajes

Los Axolotitos son las **mascotas-jugadores** de Axolotto. Son NFTs únicos que el jugador cría, personaliza y entrena para jugar mejor.

### ¿Qué hace especial a cada Axolotito?

Cada Axolotito tiene **genes únicos** codificados en la blockchain como un número `uint256` (DNA). Estos genes determinan su apariencia y sus estadísticas base.

#### Rasgos Físicos (Genes)

| Gen | Opciones |
|---|---|
| **Piel** | Color base del cuerpo |
| **Branquias** | Tipo y tamaño de las branquias externas |
| **Ojos** | Forma y expresión de los ojos |
| **Expresión** | Boca y actitud facial |
| **Cola** | Forma de la aleta caudal |
| **Frente** | Marcas o rasgos en la cabeza |
| **Extremidades** | Tipo de patas y aletas |

La combinación de estos genes produce una criatura visualmente única. Dos Axolotitos nunca son exactamente iguales.

#### Estadísticas Funcionales (Stats)

Los stats determinan el **rendimiento real en el juego**:

| Stat | Efecto en el Juego |
|---|---|
| **Suerte** (Luck) | Aumenta el multiplicador de premios críticos y la probabilidad de drops raros |
| **Enfoque** (Focus) | Reduce la probabilidad de que el Axolotito "falle" una carta cantada (error de marcado) |
| **Energía** (Stamina) | Capacidad máxima de partidas antes de necesitar dormir |
| **Salinidad** (Salinity) | Factor de mala suerte — a mayor salinidad, mayor probabilidad de resultados negativos |
| **Carisma** (Charisma) | Descuentos en la tienda del criadero |
| **Agilidad** | Resistencia ante inclemencias climáticas en salas avanzadas |
| **Sabiduría** | Mejor manejo de situaciones adversas en partidas |
| **Fuerza** | Resistencia ante eventos negativos en salas de alta dificultad |

#### Personalidades (Character Natures)

Al nacer, cada Axolotito recibe una personalidad que modifica su comportamiento:

| Personalidad | Efecto positivo | Efecto negativo |
|---|---|---|
| **Metódico** | +15% Enfoque | +10% consumo de energía |
| **Suertudo** | +15% Suerte | -5% Agilidad |
| **Hiperactivo** | Recupera energía 20% más rápido | 10% de probabilidad extra de fallar cartas |

### Estados del Axolotito

En todo momento, tu Axolotito se encuentra en uno de cuatro estados:

```
   IDLE          PLAYING        SLEEPING      WAITING_SETTLEMENT
(Disponible)  (En partida)    (Durmiendo)    (Listo para reporte)
     ●              ●               ●               ●
  Puede           Jugando        Recuperando    Sesión terminada,
  jugar,          solo en        energía        esperando que el
  comer o         segundo        sin poder      jugador haga el
  dormir          plano          interactuar    "corte de caja"
```

### El Sistema de Reporte (Settlement)

Cuando el Axolotito termina su sesión de juego — ya sea por alcanzar el límite de pérdidas, el límite de ganancias, o quedarse sin energía — entra en modo `WAITING_SETTLEMENT`.

El jugador ve una **boleta de rendimiento** con:
- COR ganadas/perdidas netas
- XP ganada
- Número de partidas jugadas
- Victorias y derrotas

Al confirmar con "¡Gracias por el esfuerzo! ❤️":
- Los COR acumulados se transfieren a la cartera del jugador
- El Axolotito recibe Puntos de Lealtad
- El Axolotito se va a dormir para recuperar energía al 100%

### Equipamiento y Cosméticos

Los Axolotitos pueden equipar **accesorios** obtenidos en el Gashapón o el mercado:
- **Cabeza:** Gorros, coronas, cascos
- **Ojos:** Lentes, gafas, anteojos
- **Cuerpo:** Ropa, capas, armaduras

Los accesorios son puramente cosméticos y no afectan el rendimiento de juego. Su valor es de colección y personalización.

### Límite de Axolotitos

| Estado VIP | Slots de Axolotito |
|---|---|
| Sin VIP | 6 slots |
| VIP Axolite | 7 slots |

---

## 4. Los Webitos — Huevos Coleccionables

Los Axolotitos nacen de **Webitos** — huevos NFT que el jugador adquiere en la tienda oficial. Son el punto de entrada al sistema de crianza.

### Tipos de Webitos

| Tipo | Descripción | Rareza |
|---|---|---|
| **Webito Normal** | Huevo estándar de Axolotto | Común |
| **Webito Génesis** | Primera generación — aura dorada | Especial |
| **Webito Fundador** | Emisión limitada de los primeros jugadores — aura violeta | Rarísimo |

### El Proceso de Incubación

Una vez colocado en un slot del Nido, el huevo inicia un período de incubación de **7 días** que puede acelerarse o sufrir retrasos según el clima y los cuidados.

**Variables que afectan la incubación:**

| Variable | Efecto |
|---|---|
| **Temperatura (Calor %)** | Progreso de incubación — se pierde calor cada hora según el clima |
| **Clima de Xochimilco** | El clima del servidor (4 períodos: Madrugada, Mañana, Tarde, Noche) afecta la pérdida de calor por hora |
| **Congelamiento** | Si el calor cae a 0%, el huevo se congela y la incubación se pausa |
| **Escudo** | Un consumible que protege el huevo de las pérdidas de calor por un tiempo fijo |

**Acciones del jugador durante la incubación:**
- **Calentar:** Gastar COR para subir la temperatura y acelerar el proceso
- **Poner escudo:** Comprar protección temporal contra el frío
- **Ver progreso:** La barra de calor y el badge de estado son visibles en la escena del Nido

### Eclosión

Cuando las horas restantes llegan a 0, el huevo entra en estado "Listo" (el emoji cambia a 🐣 y el nido pulsa en rosa). Al hacer tap, el Axolotito eclosiona con sus genes y stats únicos determinados por la incubación.

---

## 5. El Nido — Tu Cenote Personal

El Nido es el **hogar digital de tus Axolotitos y Webitos**. Es la vista más inmersiva del juego — una escena 2.5D de un cenote mexicano donde todo está vivo.

### La Escena

```
┌─────────────────────────────────────────────────────┐  ← superficie
│  ≈≈≈ rayos de luz bailando (teal transparente) ≈≈≈  │  capa 1
│  ○    ○    burbujas subiendo    ○    ○    ○          │  capa 3
│                                                     │
│    🦎(pequeño, profundo)   🦎(mediano)              │  capa axolotitos
│          🦎(grande, cerca)                          │
│                                                     │
│  [cueva] 🥚 [cueva] 🥚 [cueva] 🥚                  │  fila trasera
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        │  piedras profundas
│  🥚  [cueva] 🥚 [cueva] 🥚  [cueva] 🥚             │  fila frontal
│▓▓▓▓▓▓▓▓▓▓▓▓ FONDO DE PIEDRA ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     │  suelo
└─────────────────────────────────────────────────────┘
```

### Los Nidos de Incubación (Cuevas)

Hay **7 slots de nido** — 3 en la fila trasera (más pequeños, más al fondo) y 4 en la fila frontal (más grandes, más cerca). Cada slot puede contener un Webito en incubación o estar vacío.

Las cuevas tienen un sistema de colores que indica su estado de un vistazo:

| Color | Estado |
|---|---|
| Naranja cálido | Incubando con buena temperatura |
| Rosa pulsante | ¡Listo para eclosionar! |
| Cyan/azul | Congelado o con riesgo de congelamiento |
| Dorado suave | Protegido por escudo |
| Casi invisible | Vacío |

### El Clima en Tiempo Real

El chip de clima (arriba de la escena) muestra las condiciones actuales de Xochimilco:

| Dato | Significado |
|---|---|
| ❄️ `X%/h` | Pérdida de calor por hora — cuánto frío hace |
| 🔥 `Xx` | Multiplicador de efectividad del calentamiento |
| 🧬 `Xx` | Bonus de stats al nacer con este clima |
| 🌊 `X%` | Probabilidad de congelamiento repentino |

### Los Axolotitos en el Cenote

Los Axolotitos ya eclosionados nadan libremente en la escena. Cada uno tiene una posición y animación de nado única generada aleatoriamente — algunos nadan cerca, otros lejos (más pequeños por la perspectiva). Al tapear un Axolotito, se abre su ficha con stats y opciones.

### Límite de Slots

| Estado VIP | Slots de Nido (Webitos simultáneos) |
|---|---|
| Sin VIP | 7 slots (estándar) |
| VIP activo | Los slots no cambian — el VIP afecta tableros y Axolotitos, no nidos |

---

## 6. Las Cartas de Lotería

Las cartas son el **activo base** del sistema de juego. Son NFTs del estándar ERC-1155 (múltiples copias del mismo ítem posibles).

### El Catálogo

Existen **54 cartas únicas**, basadas en las figuras clásicas de La Lotería mexicana: El Gallo, La Dama, La Luna, El Sol, La Mano, etc. Cada carta tiene:

- **Arte original** con estética Axolotto
- **Nombre y número** (1-54)
- **Rareza** que determina su valor y efectos visuales

### Sistema de Rareza

| Rareza | Descripción | Visual |
|---|---|---|
| **Común** | La mayoría de las cartas | Borde gris sutil |
| **Poco Común** | Moderadamente difícil de obtener | Borde teal |
| **Rara** | Difícil de obtener | Borde cyan brillante |
| **Épica** | Muy difícil, gran valor | Borde violeta |
| **Legendaria** | Rarísima, máximo valor | Borde dorado con glow |

### Variantes Especiales

- **Brillante / Holográfica (Foil):** Una versión especial de cualquier carta con un efecto de gradiente arcoíris animado. Probabilidad ~3% al abrir sobres Foil. Los tableros con cartas brillantes reciben un bonus de rendimiento de COR (+5% por carta brillante, hasta +80%).
- **Primera Edición:** Marcadas con ⭐ — son las primeras copias acuñadas de cada carta. Su valor en el mercado P2P suele ser mayor.

### Cómo se Obtienen las Cartas

1. **Paquetes (Boosters) en la Tienda:** La fuente principal. Hay 4 tipos con diferentes probabilidades.
2. **Gashapón:** La máquina gacha del juego — 3 tiers de rolls.
3. **Mercado P2P:** Comprar directamente a otros jugadores.
4. **Crafteo (Card Melter):** Quemar cartas duplicadas + COR para obtener una carta de mayor rareza (5 Comunes + 20 COR → 1 Rara aleatoria).

---

## 7. Los Tableros — Tu Herramienta de Juego

Los tableros son NFTs del estándar ERC-721. Son cuadrículas de **4×4 (16 cartas)** armadas por el jugador con cartas de su inventario.

### Crear un Tablero

| Método | Costo | Descripción |
|---|---|---|
| **Aleatoria** | 25 COR | El sistema selecciona 16 cartas al azar de tu inventario |
| **Manual** | 50 COR | Elige y posiciona cada carta a tu gusto (editor drag-and-drop) |

La construcción manual permite **estrategia**: posicionar cartas de alta rareza para maximizar las probabilidades de completar patrones ganadores primero.

### Staking Pasivo

Un tablero que no está jugando puede ponerse en **staking** para generar COR/hora de forma pasiva. La tasa de retorno escala con el nivel del tablero (XP ganada en partidas). Es la fuente de ingresos más estable y predecible del juego.

### Desmontar un Tablero

Si ya no quieres un tablero, puedes **desmontarlo** (50 COR). Esto:
- Destruye aleatoriamente 1 de las 16 cartas
- Regresa las 15 cartas restantes a tu inventario

### Límite de Tableros

| Estado VIP | Slots de Tablero |
|---|---|
| Sin VIP | 3 slots |
| VIP Coral | 3 slots |
| VIP Dorado | 4 slots (+1) |
| VIP Axolite | 5 slots (+2) |

### El Mercado de Rentas (Scholarships)

Puedes **rentar tus tableros** a otros jugadores que no tienen suficientes tableros para jugar. Tú defines:
- **Precio en COR** por 24 horas de renta
- **% de ganancias** que recibes cuando el tablero rentado gana una partida

El mercado de rentas es una fuente de **ingresos pasivos sin riesgo** — si el rentante pierde, tú igual cobras la cuota.

---

## 8. El Juego: Lotería en Tiempo Real

### El Bucle de Juego

```
1. Seleccionar Axolotito
       ↓
2. Seleccionar Tablero (propio o rentado)
       ↓
3. Configurar Presupuesto
   (apuesta máxima + límite de pérdida + límite de ganancia)
       ↓
4. Elegir Sala (Rookies o Campeones)
       ↓
5. El Axolotito juega automáticamente en segundo plano
       ↓
6. Notificación cuando termina → Cobrar resultados
```

El jugador configura las reglas una vez y el Axolotito ejecuta las partidas solo, hasta que:
- Alcanza el límite de pérdida configurado
- Alcanza el límite de ganancia configurado
- Se queda sin energía o fondos

### La Mecánica de la Lotería

Cada partida simula una partida de lotería tradicional mexicana:

1. **El Cantador** llama cartas al azar del mazo de 54
2. Si la carta está en el tablero del jugador, se marca automáticamente
3. El primero en completar un **Hito** gana

### Hitos y Premios

| Hito | Condición | Premio |
|---|---|---|
| **Hito 1** (Línea o Cuadrito) | Primera línea de 4 cartas (horizontal, vertical, diagonal) O un cuadro de 2×2 | **35%** de la bolsa total |
| **Hito 2** (Tabla Llena / "¡Lotería!") | Primero en marcar las 16 cartas | **55%** de la bolsa total |
| **Jackpot de Oro** | Completar Hito 1 entre las primeras 4, 5 o 6 cartas cantadas | **90%** del pozo acumulado global |

El **5%** de cada bolsa va al Jackpot de Oro y el **5%** restante a la tesorería del juego.

### Las Salas

| Sala | Descripción | Perfil |
|---|---|---|
| **Rookies** | Cuotas bajas, jugadores nuevos y bots de relleno | Bajo riesgo, baja recompensa |
| **Campeones** | Cuotas más altas, jugadores veteranos | Mayor riesgo, mayor recompensa |

Cada sala tiene un cupo máximo de **30 tableros**. Si hay menos de 4 inscritos cuando el temporizador de 30 segundos expira, el sistema completa con bots de relleno para que la partida siempre empiece.

### El Jackpot de Oro

El pozo acumulado global comienza con **1,000 COR** de semilla. Crece cada partida con el 5% de cada bolsa.

**Para ganarlo:** Un jugador humano debe completar el Hito 1 en tiempo récord — antes de que se canten la 5ta o 6ta carta. Es improbable, pero cuando sucede, es el evento más importante del juego.

**Restricciones anti-trampa:**
- Solo jugadores humanos pueden ganarlo (no bots)
- La sala debe tener mínimo 5 tableros humanos de al menos 2 jugadores diferentes
- El ganador recibe el 90% del pozo; el 10% queda como semilla del siguiente

**VIP Axolite:** +5% sobre el Jackpot ganado.

### Modo Multijugador Real

Además de salas automáticas, hay un **lobby multijugador** donde jugadores reales se inscriben, ven quién más está en la sala (con sus Axolotitos y marcos VIP visibles), y compiten en tiempo real con actualizaciones de estado instantáneas.

---

## 9. La Economía Dual: AXG y COR

Axolotto usa **dos monedas** con funciones completamente distintas. Este diseño es fundamental para la sostenibilidad económica del juego.

### AXG — Axogemas (Moneda Premium)

```
¿Qué es?    Token ERC-20 en blockchain (Plasma Chain)
¿De dónde?  Solo se obtiene comprando con dinero real (fiat o crypto)
¿Para qué?  Comprar activos permanentes: Webitos, sobres premium, VIP, slots extra
¿Se gana?   NUNCA como recompensa de juego — solo se compra
```

**AXG es la moneda de valor real.** Cada AXG emitida está respaldada por dinero real en la reserva del juego. Por eso el juego puede ofrecer un programa de retiro (DevEx) donde los jugadores que venden activos en el P2P pueden convertir sus AXG en pesos reales.

**Precio de referencia:** ~$10 MXN por AXG (o $0.50 USD).

### COR — Corcholatas (Moneda de Juego)

```
¿Qué es?    Moneda soft, NO está en blockchain pública
¿De dónde?  Jugando partidas, ganando jackpots, rentas, staking, VIP diario
¿Para qué?  Pagar buy-ins, crear tableros, consumibles, Gashapón, P2P entre jugadores
¿Se retira? NO — no tiene conversión directa a dinero real
```

**COR es el combustible del juego.** Se gana jugando y se gasta jugando. Es inflacionaria por diseño — el juego tiene suficientes "sumideros" (gastos necesarios de COR) para equilibrar su emisión.

> **Por qué no se puede retirar COR:** Si los jugadores pudieran convertir COR en pesos, el sistema colapsaría en inflación (como le pasó a Axie Infinity con SLP). COR existe solo dentro del ecosistema.

### Paquetes de Conversión (Banco de Algas)

Los jugadores que quieren más COR sin esperar pueden comprarlos con AXG:

| Paquete | Costo AXG | COR obtenidas | Bonus |
|---|---|---|---|
| Alga Común | 10 AXG | 100 COR | — |
| Alga Abundante | 50 AXG | 600 COR | +20% gratis |
| Alga Imperial | 100 AXG | 1,500 COR | +50% gratis |
| Súper Carga | 250 AXG | 4,000 COR | +60% gratis |

### El Modelo de Reserva 80/20

Por cada AXG vendida, el dinero se divide:

```
$10 MXN (precio de 1 AXG)
    │
    ├── IVA 16% → $1.38 MXN al SAT
    ├── Comisión procesador (4.5%) → $0.45 MXN
    └── Neto: $8.17 MXN
           │
           ├── 80% ($6.54) → Reserva de respaldo (intocable)
           └── 20% ($1.63) → Tesorería operativa (gastos, marketing, desarrollo)
```

La reserva garantiza que si todos los jugadores quisieran retirar sus AXG simultáneamente, el juego podría pagar a todos — es **matemáticamente solvente** ante un bank run total.

### Cómo Ganar Dinero Real (DevEx)

El camino legítimo para convertir tiempo de juego en dinero real:

```
Jugar partidas → ganar COR → comprar/crear activos valiosos
→ vender activos en Mercado P2P → recibir AXG
→ solicitar DevEx → recibir pesos/USDT
```

**Condiciones del retiro:**
- Solo AXG obtenidas vendiendo en el P2P (no por compra directa — eso sería solo devolver lo que pagaste)
- Período de retención de 14 días (anti-fraude)
- KYC obligatorio (identificación oficial)
- Tasa de recompra: ~70% del precio de compra (el spread del 30% es el "impuesto de retiro")
- Retención fiscal automática (~7% según régimen de premios)

---

## 10. La Tienda y el Mercado P2P

### La Tienda Oficial

La tienda tiene cuatro secciones:

#### 1. Paquetes de Cartas (Boosters)

| Paquete | Precio | Contenido |
|---|---|---|
| **Fiesta** | AXG | Cartas Comunes y Poco Comunes |
| **Nido** | AXG | Mayor probabilidad de Raras |
| **Cosmos** | AXG | Probabilidad de Épicas |
| **Brillante** | AXG | Incluye probabilidad de cartas Foil/Holográficas |

> Todas las probabilidades de rareza están publicadas antes de la compra.

#### 2. Banco de Algas (Conversión AXG → COR)

Los 4 paquetes de conversión descritos en la sección de economía.

#### 3. Cápsulas Sorpresa

Cápsulas individuales de contenido aleatorio — accesorios, cartas, consumibles. Menor costo que un booster completo.

#### 4. Racha Diaria (Daily Streak)

Una recompensa gratuita que crece día a día mientras mantengas la racha de login. Perder un día reinicia la racha.

### El Mercado P2P

El mercado entre jugadores funciona dentro del juego. Los jugadores pueden:

**Vender o rentar:**
- Cartas de lotería individuales
- Tableros completos (venta o renta 24h)
- Axolotitos
- Accesorios

**Comisiones del Mercado:**

| Tipo de transacción | Fee estándar | Fee VIP Coral | Fee VIP Dorado | Fee VIP Axolite |
|---|---|---|---|---|
| Venta (en AXG) | 5% → Tesorería | 4% | 3% | 1.5% |
| Renta (en COR) | 5% → Quema | 4% | 3% | 1.5% |

Las comisiones de renta en COR se **queman** — salen de circulación para controlar la inflación.

---

## 11. El Gashapón

El Gashapón es la **máquina gacha** del juego. Tres tiers de probabilidades y premios:

| Tier | Costo por roll | Contenido | Pity (garantía) |
|---|---|---|---|
| **Cobre** | 150 COR | Accesorios comunes, cartas básicas | 10 rolls |
| **Plata** | 500 COR | Accesorios raros, cartas Raras | 5 rolls |
| **Oro** | 2,000 COR | Accesorios Épicos/Legendarios, cartas Épicas | 3 rolls |

**Sistema de Pity:** Si no obtienes la rareza máxima del tier después de N rolls, el siguiente es garantizado. El contador se muestra en todo momento.

**Triple Roll:** Disponible en todos los tiers — obtén 3 resultados con un leve descuento vs. 3 rolls individuales.

**Celebración de Legendaria:** Cuando sale un ítem Legendario, la interfaz entra en modo celebración con partículas y efectos especiales.

---

## 12. El Club VIP

El Club VIP es el sistema de **membresía mensual** de Axolotto. Es la herramienta principal de retención y la principal fuente de ingresos recurrente.

### Los Tres Niveles

#### 🪸 Pase Coral — 100 AXG/mes

| Beneficio | Detalle |
|---|---|
| +40 COR/día | Hasta 1,200 COR/mes si reclamas todos los días |
| 5% descuento en tienda | Todos los ítems AXG excepto Webitos |
| 1 roll de Gashapón/mes | Al activar o renovar |
| Bono de bienvenida | +200 COR al activar por primera vez |
| Marco Coral | Borde turquesa animado en todos tus Axolotitos |

**ROI positivo garantizado:** 1,200 COR/mes ≈ 120 AXG de valor. Pagas 100 AXG, recibes 120 AXG en COR. La membresía se paga sola con el daily.

#### ✨ Pase Dorado — 250 AXG/mes ⭐ Más Popular

| Beneficio | Detalle |
|---|---|
| +100 COR/día | Hasta 3,000 COR/mes |
| 12% descuento en tienda | |
| 3 rolls de Gashapón/mes | |
| +1 slot de tablero | Renta ese tablero extra → el pase se paga solo |
| Caja mensual | 1 Booster aleatorio al activar/renovar |
| Bono de bienvenida | +500 COR + 1 Booster extra |
| Comisión P2P reducida | 3% (vs 5% estándar) |
| Acceso anticipado 24h | A nuevas fases de contenido |
| Marco Dorado + corona | Borde dorado con shimmer en tus Axolotitos |

#### 🌟 Pase Axolite — 500 AXG/mes

| Beneficio | Detalle |
|---|---|
| +200 COR/día | Hasta 6,000 COR/mes |
| 20% descuento en tienda | |
| 5 rolls de Gashapón/mes | |
| +2 slots de tablero | |
| +1 slot de Axolotito | Límite 6 → 7 |
| Caja premium mensual | 1 Booster Foil + 1 Booster normal |
| Bono de bienvenida | +1,000 COR + 1 Booster Foil extra |
| Comisión P2P | 1.5% |
| Entrada multijugador | -15% en buy-ins |
| Bonus Jackpot | +5% sobre jackpots ganados |
| Marco Axolite animado | Gradiente oro→rosa→violeta con partículas |
| Nombre dorado | En rankings y leaderboards |

### La Mecánica del Claim Diario

El COR diario no se acredita automáticamente — el jugador debe abrirlo activamente. Esto crea un **hábito de login diario** sin que se sienta como obligación:

- El COR pendiente se acumula máximo **2 días**
- Al día 3 sin reclamar, el lote más antiguo expira
- Al reclamar: animación de monedas volando al contador de COR

### El Marco VIP en los Axolotitos

El estatus VIP se expresa visualmente en **todos los Axolotitos del jugador**. No existe un "Axolotito Principal" — si eres VIP, todos lo muestran. Esto hace el estatus visible en:
- El lobby de multijugador
- Los rankings/leaderboards
- El mercado P2P
- El header del modal VIP

### Sistema de Racha

La racha no se rompe al cambiar de tier. Las recompensas de racha son **permanentes** (se quedan aunque el VIP expire):

| Racha | Recompensa permanente |
|---|---|
| 3 meses | Badge "Constante 🔥" |
| 6 meses | Marco "Veterano" cosmético exclusivo |
| 12 meses | Título "Axolotto Original" + 1 Webito Astral gratis |
| 24 meses | Marco "Leyenda del Nido" — el más raro del juego |

---

## 13. Los Rankings

La sección de Rankings es el **salón de la fama** de Axolotto. Tres tablas de líderes:

### Ranking de Axolotitos

Los Axolotitos más poderosos del juego, ordenables por:
- Nivel (XP acumulada)
- Victorias totales
- Estadísticas específicas

### Ranking de Tableros

Los tableros con mejor rendimiento histórico, ordenables por:
- Victorias totales
- Odds promedio (eficiencia)

Los tableros del ranking pueden **rentarse directamente** desde la lista — perfecta para jugadores que aún no tienen un tablero competitivo.

### Ranking de Tableros Forjados

Una categoría especial para los tableros "legendarios" del juego — los que han alcanzado niveles extremos de XP y rendimiento.

---

## 14. Por Qué es Legal

La legalidad de Axolotto se sostiene en tres pilares: clasificación correcta de los activos, separación de flujos de dinero, y cumplimiento fiscal.

### 1. AXG es un Utility Token, no un Valor Financiero

La diferencia entre un token ilegal y uno legal en México y EEUU es si promete **ganancias de la inversión ajena**. AXG no es un instrumento de inversión:

- **No promete rendimientos:** El precio de AXG no fluctúa — su valor está fijado por la reserva
- **Tiene utilidad concreta:** Solo sirve para comprar cosas en el juego
- **No genera dividendos:** Tener AXG no te da derechos sobre las ganancias de la empresa
- **Los Términos de Servicio** dejan explícito que AXG es una moneda de entretenimiento digital, no un depósito bancario ni un instrumento financiero

### 2. El Modelo DevEx (Roblox) es el Más Seguro del Mundo

El retiro de dinero real (DevEx) es legal porque:

- **No hay libre convertibilidad directa:** Un jugador NO puede comprar AXG y retirarlas al día siguiente. Solo puede retirar AXG obtenidas **vendiendo activos** en el P2P — demostrando que aportó valor al ecosistema
- **KYC obligatorio:** Todo retiro requiere verificación de identidad (INE/Pasaporte), cumpliendo con la Ley Anti-Lavado de Dinero (PLD/AML)
- **Período de retención:** 14 días naturales de bloqueo en AXG del P2P para detectar fraudes con tarjetas clonadas
- **Retención fiscal automática:** ~7% retenido en cada DevEx, emitido como CFDI por la empresa

### 3. Xochimilco es un Concurso de Destreza, no un Casino

La distinción legal crítica en México (Ley Federal de Juegos y Sorteos) entre un casino y un concurso de destreza:

| Casino | Concurso de Destreza |
|---|---|
| El resultado depende 100% del azar | El resultado depende de habilidad del participante |
| No se puede influir el resultado | El jugador puede mejorar con práctica y estrategia |
| Requiere licencia de casinos | No requiere licencia de casino |

En Axolotto, **la destreza importa**:
- Elegir el Axolotito correcto (stats) para cada tipo de sala
- Construir tableros optimizados (posición de cartas)
- Gestionar el presupuesto (límites de pérdida/ganancia)
- Elegir el momento correcto para jugar (clima, tipo de sala, competencia)

Un jugador experto consistentemente rinde mejor que uno nuevo. Esto lo clasifica como concurso de destreza.

### 4. Cumplimiento Fiscal en México

La operación de Axolotto requiere y contempla:

- **Persona Moral constituida** (Tridyland S.A.P.I. de C.V. o S.A. de C.V.)
- **IVA 16%** deslosado en cada compra de AXG como "servicio digital de entretenimiento"
- **ISR corporativo** calculado sobre el margen real (ingresos − reserva − costos operativos)
- **CFDI automatizados** para compras (global diario con RFC genérico; nominativo si el jugador lo solicita)
- **Retenciones por premios** (DevEx) bajo el régimen de Premios y Sorteos: ~7% retenido por la plataforma
- **Separación de cuentas** — cuenta operativa (20%) separada de la cuenta de reserva (80%)

---

## 15. Cómo Entrar al Juego

### Requisitos

- Un dispositivo con navegador web moderno (Chrome, Firefox, Safari) — móvil o desktop
- Una dirección de correo electrónico, cuenta de Google, o cuenta de Discord
- Opcionalmente: una wallet de crypto (MetaMask, etc.) para usar el riel Web3

### Proceso de Registro

1. **Visitar axolot.to**
2. **Crear cuenta** con Privy — el sistema de autenticación maneja todo. Puedes usar:
   - Email + código de verificación (no necesitas password)
   - Google SSO
   - Discord SSO
   - Wallet de crypto (para usuarios Web3 avanzados)
3. **Wallet automática:** Privy crea una wallet de blockchain automáticamente — no necesitas MetaMask ni entender crypto para empezar
4. **Tutorial de onboarding:** La primera vez, un guía te explica el Nido, las cartas y cómo jugar tu primera partida

### Cómo Empezar a Jugar (Flujo del Jugador Nuevo)

**Día 1 — Sin gastar nada:**
- Recibir el Webito de bienvenida
- Colocarlo en el Nido para incubar
- Usar las cartas de bienvenida para armar un primer tablero
- Jugar la primera partida en sala Rookies con COR de bienvenida

**Semana 1 — Explorar:**
- Eclosionar el primer Axolotito
- Entender sus stats y cómo mejorarlos
- Obtener más cartas con la Racha Diaria
- Explorar el Gashapón Cobre

**Mes 1 — Compromiso:**
- Optimizar tableros con las cartas acumuladas
- Evaluar si el VIP Coral vale la pena (ROI positivo desde el primer día)
- Participar en multijugador
- Rentar el tablero para ingresos pasivos

### Métodos de Pago para Comprar AXG

| Método | Región | Proceso |
|---|---|---|
| **Tarjeta de crédito/débito** | México y LatAm | MoonPay / Mercado Pago — pago en MXN |
| **SPEI** | México | Transferencia bancaria vía Mercado Pago |
| **OXXO** | México | Pago en efectivo vía Mercado Pago |
| **USDT/USDC** | Global | Smart contract directo — 5-10% de descuento |
| **ETH/MATIC** | Global | Smart contract directo |

---

## 16. Arquitectura Técnica

### Stack

| Capa | Tecnología |
|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4 |
| **Autenticación** | Privy (email, social, wallet) |
| **Interacción blockchain** | Viem + Privy embedded wallets |
| **Backend** | FastAPI (Python), PostgreSQL, SQLModel |
| **Blockchain** | Plasma Chain (EVM-compatible), Foundry para contratos |
| **Tiempo real** | Polling con backoff exponencial (4s-30s) → WebSocket en roadmap |
| **Infraestructura** | Docker Compose, PM2, reiniciar.sh |
| **Fiat onramp** | MoonPay / Mercado Pago |

### Smart Contracts

| Contrato | Estándar | Función |
|---|---|---|
| `GemaAlga.sol` | ERC-20 | Token COR (moneda soft) |
| `Axogema.sol` | ERC-20 | Token AXG (moneda premium) |
| `Webitos.sol` | ERC-721 | Huevos coleccionables con metadatos de fase |
| `Axolotitos.sol` | ERC-721 | Mascotas con DNA de rasgos y stats on-chain |
| `CartasLoteria.sol` | ERC-1155 | Las 54 cartas (múltiples copias) |
| `TablasLoteria.sol` | ERC-721 | Tableros con layout de 16 cartas en escrow |
| `Consumables.sol` | ERC-1155 | Comida, lámparas y consumibles del criadero |
| `GameController.sol` | — | Orquestador con permisos de mint/burn sobre todos los contratos |

### Separación On-Chain vs Off-Chain

La arquitectura híbrida es deliberada para balancear seguridad, velocidad y costo:

**On-chain (en la blockchain):**
- Propiedad de NFTs (Webitos, Axolotitos, Cartas, Tableros)
- Saldo de AXG
- Transferencias de activos en el P2P

**Off-chain (en la base de datos):**
- Saldo de COR (no en blockchain pública)
- Estado del juego en tiempo real (partidas, lobbies)
- Incubación y clima
- Logs de partidas y resultados
- Perfil y preferencias del usuario

Esta separación permite que el juego sea rápido (acciones de COR son instantáneas, no esperan confirmaciones de blockchain) y barato (no se pagan gas fees por cada acción de juego).

---

## 17. Hoja de Ruta y Visión Futura

### Estado Actual (v1.0)

| Módulo | Estado |
|---|---|
| Sistema de autenticación (Privy) | ✅ Completo |
| Nido 2.5D con clima en tiempo real | ✅ Completo |
| Incubación de Webitos | ✅ Completo |
| Crianza y stats de Axolotitos | ✅ Completo |
| Sistema de cartas (54 cartas + rareza) | ✅ Completo |
| Tableros (creación, staking, desmontar) | ✅ Completo |
| Juego de lotería CPU (simulado) | ✅ Completo |
| Lobby multijugador | ✅ Completo |
| Sistema de Jackpot de Oro | ✅ Completo |
| Tienda oficial (boosters, cápsulas, daily) | ✅ Completo |
| Gashapón (3 tiers + pity) | ✅ Completo |
| Mercado P2P (cartas, tableros, axolotitos) | ✅ Completo |
| Mercado de rentas (scholarships) | ✅ Completo |
| Sistema VIP (3 tiers + daily claim) | ✅ Completo |
| Rankings (Axolotitos, Tableros, Forjados) | ✅ Completo |
| Smart contracts (Foundry + Plasma Chain) | ✅ Completo |
| Integración blockchain completa (mint/burn/transfer) | ✅ Completo |
| Sistema de accesorios del Axolotito | ✅ Completo |

### Próximas Fases

#### Fase 6 — Confirmación Blockchain Completa
- Verificación on-chain de transferencias NFT en ventas P2P
- Auditoría de seguridad de smart contracts

#### Fase 7 — Pulido de Onboarding y UX
- Tutorial interactivo para nuevos jugadores
- Pantalla de resumen antes de iniciar partida
- Dot badges de notificación en tabs de navegación
- SVG/sprites para Axolotitos (reemplazar emojis)
- Posición del jugador en Rankings

#### Fase 8 — Misiones Diarias y Crafteo
- Tablero de misiones diarias (Daily Bounties)
- Card Melter — crafteo de cartas
- Personalidades avanzadas de Axolotitos

#### Fase 9 — La Visión 2.5D Completa
- Convertir todas las vistas en entornos habitables
- Transiciones de cámara entre zonas
- Assets visuales de alta calidad para el mundo
- Personalización del cenote (decoraciones comprables)
- Vendor NPCs en la tienda

#### Fase 10 — Ecosistema y Comunidad
- Torneos VIP mensuales
- Sistema de referidos
- Card para redes sociales (compartir rango)
- VIP Shop exclusivo con items rotativos
- Integración con Discord para notificaciones

---

*Desarrollado por Tridyland. El ajolote mexicano (*Ambystoma mexicanum*) es una especie en peligro crítico de extinción. Axolotto existe también para celebrar y visibilizar esta criatura única en el mundo. 🦎🌿*
