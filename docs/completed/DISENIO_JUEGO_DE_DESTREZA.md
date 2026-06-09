# Rediseño Legal y de Producto: Axolotto como Juego de Destreza (Skill Contest)

> [!IMPORTANT]
> **DIAGNÓSTICO LEGAL CRÍTICO:**
> Las partidas competitivas donde los jugadores pagan una entrada en **AXF (Axofichas)**, juegan a una dinámica basada en el azar (lotería/lotto) y el ganador se lleva el acumulado (jackpot) en AXF, constituyen **apuestas y juego de azar en línea no autorizado**. 
>
> Bajo las leyes de México (SEGOB) y Estados Unidos (UIGEA / Leyes Estatales), este flujo es clasificado como casino ilegal. Se debe reestructurar la mecánica del juego o el flujo transaccional de inmediato.
>
> **Documentos Relacionados:**
> - [AUDITORIA_LEGAL_FINANCIERA.md](file:///home/monotr/axolotto/docs/AUDITORIA_LEGAL_FINANCIERA.md)
> - [AXOLOTTO_BIBLE.md](file:///home/monotr/axolotto/docs/completed/AXOLOTTO_BIBLE.md)

---

## 1. ¿Por qué las Partidas Competitivas en AXF son Ilegales?

En el derecho penal y regulatorio, una apuesta se define por la concurrencia de tres factores: **Pago por participar (Entry Fee) + Mecánica de Azar (Chance) + Premio de Valor Real (Prize)**. 

El diseño actual de las partidas en AXF reúne los tres factores:
1. **Pago:** Los jugadores aportan AXF (moneda comprada con fíat/USDC).
2. **Azar:** Aunque se elijan Axolotitos con estadísticas, la extracción de los números del lotto es aleatoria. Un mal jugador con suerte puede ganarle a un experto si sus números salen primero.
3. **Premio:** El ganador se lleva el AXF acumulado y puede cambiarlo por dólares o pesos.

Para operar este flujo de forma legal, se requiere una **Licencia de Operación de Juegos y Sorteos** de la SEGOB (México) o cumplir con licencias estatales de juego interactivo en EE. UU., lo cual cuesta millones de dólares, requiere fianzas bancarias masivas y restringe la plataforma geográficamente.

---

## 2. Tres Caminos para que Axolotto sea un Concurso de Destreza (Skill)

Para eliminar la clasificación de casino sin requerir licencias de apuestas, debemos **eliminar el Azar como factor determinante en el resultado**. El juego debe estructurarse de tal manera que un jugador experto gane consistentemente al menos el **80% de las veces** contra un jugador novato.

A continuación se presentan tres propuestas de rediseño de producto:

```
                            ┌──────────────────────────────────┐
                            │    RED DISEÑO DE AXOLOTTO        │
                            └────────────────┬─────────────────┘
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         ▼                                   ▼                                   ▼
┌──────────────────┐               ┌──────────────────┐               ┌──────────────────┐
│ Opción A: Lobbies │               │ Opción B: Speed  │               │ Opción C: Auto-  │
│ Simétricos       │               │ Dabbing (E-sport)│               │ Battler / CCG    │
└──────────────────┘               └──────────────────┘               └──────────────────┘
```

### Opción A: Lobbies Simétricos (Duplicate Board Solitaire) - *La más fácil de implementar*
Esta mecánica se inspira en el bridge competitivo y el ajedrez por correspondencia. Consiste en eliminar la asimetría de la suerte entre los jugadores.

* **Cómo funciona:**
  1. Ambos jugadores entran al lobby y se les asigna exactamente el **mismo tablero de cartas** (o tableros con la misma distribución de probabilidades).
  2. La secuencia de números que se extrae del lotto es **idéntica para ambos jugadores**.
  3. No se trata de quién llena el tablero primero por suerte, sino de **quién optimiza mejor los recursos**.
  4. Los jugadores tienen una barra de energía y cartas de "habilidades" (activadas por sus Axolotitos) que les permiten:
     * Duplicar puntos de una celda.
     * Intercambiar posiciones de números.
     * Ralentizar el tiempo del oponente.
* **Factor de Habilidad:** Al tener las mismas variables de partida (mismo tablero, mismos números llamados), la suerte se reduce a cero. El ganador se define puramente por su velocidad de reacción, estrategia en el uso de habilidades y gestión de la energía.

---

### Opción B: Speed Dabbing / Tablero de Reflejos (E-sports de Reacción)
Transforma el lotto pasivo en un juego de habilidad mental, reflejos visuales y coordinación ojo-mano.

* **Cómo funciona:**
  1. Cuando un número es llamado (ej. "¡Axolote Dorado - 24!"), el número no se marca automáticamente.
  2. Aparece en pantalla y los jugadores deben buscarlo en sus tableros y presionarlo manualmente.
  3. **Mecánica de Multiplicador de Velocidad:** Si presionas el número en los primeros 0.5 segundos, obtienes 3x puntos; entre 0.5 y 1.5 segundos, 1.5x puntos; después, 1x puntos. Si presionas un número equivocado, sufres una penalización de puntaje y un bloqueo temporal de 2 segundos.
  4. La partida no termina necesariamente al completar una línea, sino que dura un tiempo fijo (ej. 2 minutos) y gana el jugador con más puntos acumulados por velocidad y precisión.
* **Factor de Habilidad:** El juego premia la agudeza visual, los reflejos físicos y el autocontrol bajo presión. Es la misma base legal que permite operar plataformas como *Skillz* (donde los jugadores apuestan dinero real en juegos como Solitaire Cube o Bubble Shooter).

---

### Opción C: Rediseño Estratégico a Auto-Battler / CCG (Combate Táctico de Cartas)
Si se desea retirar por completo la temática de lotería para eliminar la palabra "Lotto" (que es un imán de reguladores), el juego se puede transformar en un juego de estrategia de cartas coleccionables de Axolotes.

* **Cómo funciona:**
  1. El tablero de 4x4 o 5x5 ya no es un cartón de bingo, sino un **campo de batalla táctico**.
  2. Los jugadores arman un mazo con sus cartas de Axolotitos e ítems.
  3. En cada turno, roban cartas de su mazo y las colocan en el tablero para atacar las posiciones del oponente, curar aliados o capturar nodos de energía.
  4. La sinergia de elementos (Agua, Fuego, Planta) y las estadísticas de crianza del Axolotito determinan el daño y la victoria.
* **Factor de Habilidad:** Se clasifica como juego de destreza mental pura (estrategia, construcción de mazos, anticipación y matemáticas de combate), similar a Hearthstone o Magic: The Gathering.

---

## 3. Reestructuración Legal del Flujo de Transacciones

Incluso si el juego es 100% de habilidad, para blindarse legalmente ante las leyes de lavado de dinero y juego de azar, se deben implementar las siguientes estructuras de procesamiento financiero:

### A. La Regla del Premio Fijo vs. Pozo Acumulado (Legality Wrapper)
En muchas jurisdicciones (especialmente en EE. UU.), si las entradas de los jugadores forman directamente el premio del ganador (Jackpot), se considera una apuesta deportiva/apuesta P2P.
* **La Solución:** La plataforma (Tridyland) debe actuar como **patrocinador** del torneo. 
* El premio de la sala debe ser **fijo y garantizado de antemano por Tridyland** (ej. "Torneo del Cenote: Premio de 90 AXF garantizados"), independientemente de cuántos jugadores se registren. 
* Tridyland cobra una tarifa de inscripción (Entry Fee) para cubrir los costos y generar su margen, pero el pozo no fluctúa según el número de participantes de última hora. Esto lo encuadra legalmente como un **concurso de cuota de entrada** y no como un pozo de apuestas.

### B. Prohibición de Lobbies Directos en AXF (Modelo de Aislamiento)
La forma más segura de operar comercialmente sin riesgos de clausura es la siguiente:

```
[Dinero Fíat / USDC] ──> Compras AXF (Tienda) ──> Adquieres Activos (Webitos/Cartas)
                                                       │
                                                       ▼ (Marketplace P2P)
[Retiro / DevEx] <── Vendes Activos por AXF <──  Obtienes Activos Jugando Lobbies
                                                       ▲
                                                       │ (Gameplay Seguro)
                              Solo se juega con FRJ (Moneda blanda del juego)
```

1. **El Gameplay es 100% F2P / FRJ:** Los lobbies competitivos se juegan únicamente con **FRJ (Frijolitos)** o entradas gratuitas diarias. Los jugadores no arriesgan dinero real en las partidas competitivas.
2. **Recompensas de Habilidad:** Al ganar las partidas de habilidad en FRJ o torneos gratuitos, los jugadores ganan **recompensas en especie** (cartas raras de tableros, fragmentos de Axolotitos, webitos cosméticos).
3. **Monetización en el Marketplace:** Los jugadores venden estas recompensas ganadas con su esfuerzo y habilidad a otros jugadores en el Marketplace P2P a cambio de **AXF**.
4. **DevEx:** Quienes vendan artículos y acumulen AXF pueden retirarlas.
* **Por qué es 100% Legal:** Se rompe el vínculo directo entre apostar dinero y ganar dinero en un juego. El dinero real (AXF) solo se mueve en el comercio de activos digitales (Marketplace), lo cual es comercio electrónico ordinario (bienes digitales). El juego es solo el medio para producir esos bienes digitales mediante destreza.

---

## 4. Matriz de Decisión de Rediseño para los Fundadores

| Opción de Diseño | Complejidad de Código | Nivel de Riesgo Legal | Impacto en Retención de Jugadores | Recomendación |
| :--- | :--- | :--- | :--- | :--- |
| **Lotto Tradicional en AXF (Actual)** | Muy Baja | **CRÍTICO / ILEGAL** | Alto (Adicción a apuestas) | **NO OPERAR** |
| **A: Lobbies Simétricos (Duplicate Lotto)** | Media | **Bajo** | Medio | Recomendado como transición rápida en el código actual. |
| **B: Speed Dabbing (Reflejos)** | Media-Alta | **Muy Bajo** (Clasificación e-sports) | Muy Alto (Competitivo activo) | **Altamente Recomendado** para la versión móvil. |
| **C: Auto-Battler de Cartas (Táctico)** | Alta | **Nulo** | Extremadamente Alto | Excelente para Fase 3 (Lanzamiento retail). |
| **D: Aislamiento Económico (Lobbies en FRJ / Ventas P2P en AXF)** | Baja | **Nulo** (El modelo Roblox) | Alto (Economía sana de mercado) | **Debe ser la Regla de Oro del Ecosistema.** |
