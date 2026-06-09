---
tags: [conceptos, gameplay, patrones]
description: "Todos los patrones ganadores de Lotería — líneas, cuadritos, cruz, esquinas y más | All winning Lotería patterns — lines, squares, cross, corners and more"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Patrones Ganadores

En Axolotto, ganar una ronda de Lotería significa marcar en tu Tabla un **patrón específico** de celdas antes que los demás jugadores. El patrón requerido depende del modo de juego y de la sala donde estés jugando. No todas las salas usan los mismos patrones: las salas Rookies mantienen las cosas simples, mientras que las salas de Campeones y las salas alojadas por jugadores desbloquean patrones más difíciles (y más gratificantes).

---

## El Tablero (4×4)

Todas las Tablas de Lotería en Axolotto son cuadrículas de 4 filas × 4 columnas, con posiciones numeradas del 0 al 15:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

Cada celda contiene una carta del mazo tradicional de Lotería Mexicana (El Gallo, La Dama, El Corazón, etc.). El dealer saca cartas una por una, y tú marcas las celdas que coinciden.

---

## 1. Línea (Line)

Una línea completa es **4 celdas consecutivas en cualquier dirección**: fila, columna o diagonal.

**Total de variantes: 10**

### Filas (4 variantes)

```
Fila 0:               Fila 1:               Fila 2:               Fila 3:
 ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■
 Celdas: {0,1,2,3}    Celdas: {4,5,6,7}    Celdas: {8,9,10,11}  Celdas: {12,13,14,15}
```

### Columnas (4 variantes)

```
Col 0:                Col 1:                Col 2:                Col 3:
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 Celdas: {0,4,8,12}   Celdas: {1,5,9,13}   Celdas: {2,6,10,14}  Celdas: {3,7,11,15}
```

### Diagonales (2 variantes)

```
Diagonal ↘            Diagonal ↙
 ■  ·  ·  ·           ·  ·  ·  ■
 ·  ■  ·  ·           ·  ·  ■  ·
 ·  ·  ■  ·           ·  ■  ·  ·
 ·  ·  ·  ■           ■  ·  ·  ·
 Celdas: {0,5,10,15}  Celdas: {3,6,9,12}
```

**Dificultad**: Fácil (4 celdas)

**Disponible en**: TODAS las salas — Rookies, Champions y salas alojadas por jugadores.

**Premio**: Premio 1 (el premio base por patrón). Es el patrón más común y el primero que todo jugador aprende a buscar.

**Estrategia**: Revisa siempre las 10 líneas posibles cada vez que marques una celda. Las esquinas (0, 3, 12, 15) aparecen en más líneas que las celdas del borde medio, y las celdas del centro (5, 6, 9, 10) aparecen en aún más patrones. Prioriza tablas que ya tengan varias celdas en una misma línea.

---

## 2. Cuadrito (2×2 Block)

Un bloque de **2 filas × 2 columnas** contiguas. Cualquier grupo de 4 celdas que formen un cuadrado.

**Total de variantes: 9**

```
Top-Izquierda         Top-Centro            Top-Derecha
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Celdas: {0,1,4,5}    Celdas: {1,2,5,6}    Celdas: {2,3,6,7}

Mid-Izquierda         Centro                Mid-Derecha
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Celdas: {4,5,8,9}    Celdas: {5,6,9,10}   Celdas: {6,7,10,11}

Bottom-Izquierda      Bottom-Centro         Bottom-Derecha
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 Celdas: {8,9,12,13}  Celdas: {9,10,13,14} Celdas: {10,11,14,15}
```

**Dificultad**: Media (4 celdas, pero contiguas en 2D)

**Disponible en**: TODAS las salas — Rookies, Champions y salas alojadas por jugadores.

**Estrategia**: El cuadrito recompensa tener celdas agrupadas en una misma zona del tablero. Si tu tabla tiene un "cluster" natural de cartas marcadas en una esquina, enfócate en completar ese cuadrito. Las celdas centrales (5, 6, 9, 10) pertenecen a 4 cuadritos distintos — son las más valiosas para este patrón.

---

## 3. Pocito (Center)

Exactamente el **bloque central de 2×2**. A diferencia del Cuadrito general, el Pocito es un patrón fijo: solo hay una ubicación posible.

```
Pocito
 ·  ·  ·  ·
 ·  ■  ■  ·
 ·  ■  ■  ·
 ·  ·  ·  ·
 Celdas: {5, 6, 9, 10}
```

**Dificultad**: Media (4 celdas, pero ubicación fija)

**Disponible en**: Sala Champions + salas alojadas por jugadores. **No disponible en Rookies.**

**Estrategia**: Como el Pocito siempre está en el centro, vale la pena priorizar las cartas centrales (posiciones 5, 6, 9, 10) desde el inicio si estás en una sala donde este patrón está activo. Estas mismas celdas también te ayudan con Línea y Cuadrito, así que nunca son una mala inversión.

---

## 4. Esquinas (4 Corners)

Las **4 esquinas** del tablero. Otro patrón fijo de una sola ubicación.

```
Esquinas
 ■  ·  ·  ■
 ·  ·  ·  ·
 ·  ·  ·  ·
 ■  ·  ·  ■
 Celdas: {0, 3, 12, 15}
```

**Dificultad**: Media (4 celdas, dispersas)

**Disponible en**: Sala Champions + salas alojadas por jugadores. **No disponible en Rookies.**

**Estrategia**: Las esquinas son celdas de alto valor porque también participan en Líneas (son extremos de filas, columnas y una diagonal). Marcar esquinas temprano te acerca a múltiples patrones simultáneamente. Si ya tienes 2 o 3 esquinas marcadas y estás en Champions, cambia tu prioridad a conseguir la cuarta.

---

## 5. Cruz (Cross)

Una **fila completa + una columna completa** que se intersectan. El resultado es una cruz en el tablero.

**Total de variantes: 16** (4 filas × 4 columnas)

**Ejemplo — Fila 0 + Columna 2:**

```
Cruz (Fila 0, Col 2)
 ■  ■  ■  ■
 ·  ·  ■  ·
 ·  ·  ■  ·
 ·  ·  ■  ·
 Celdas: {0,1,2,3, 6,10,14}
```

```
Cruz (Fila 1, Col 0)        Cruz (Fila 2, Col 3)        Cruz (Fila 0, Col 0)
 ■  ·  ·  ·                  ·  ·  ·  ■                  ■  ■  ■  ■
 ■  ■  ■  ■                  ·  ·  ·  ■                  ■  ·  ·  ·
 ■  ·  ·  ·                  ■  ■  ■  ■                  ■  ·  ·  ·
 ■  ·  ·  ·                  ·  ·  ·  ■                  ■  ·  ·  ·
 Celdas: {0,4,5,6,7,8,12}    Celdas: {3,7,8,9,10,11,15}  Celdas: {0,1,2,3,4,8,12}
```

**Dificultad**: Difícil (7 celdas — 4 de la fila + 4 de la columna, menos 1 de la intersección)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: Con 7 celdas requeridas, la Cruz es un patrón de media partida. Necesitas que el dealer saque cartas de una fila y una columna específicas. Busca intersecciones donde ya tengas varias celdas marcadas en ambas direcciones. La celda de intersección cuenta una sola vez, así que si ya la tienes, solo necesitas 6 celdas adicionales.

---

## 6. Cruz Diagonal (X Shape)

**Ambas diagonales** simultáneamente, formando una X completa en el tablero.

```
Cruz Diagonal (X)
 ■  ·  ·  ■
 ·  ■  ■  ·
 ·  ■  ■  ·
 ■  ·  ·  ■
 Celdas: {0, 3, 5, 6, 9, 10, 12, 15}
```

**Dificultad**: Muy Difícil (8 celdas — las 4 de cada diagonal; las celdas centrales 5,6,9,10 NO se intersectan con las diagonales principales, por lo que el patrón completo abarca 8 celdas distintas)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Nota importante**: Las dos diagonales del tablero 4×4 son:
- Diagonal ↘: {0, 5, 10, 15}
- Diagonal ↙: {3, 6, 9, 12}

Estas 8 celdas NO comparten ninguna posición entre sí, por lo que la Cruz Diagonal requiere marcar exactamente 8 celdas. Sin embargo, 4 de ellas son esquinas (0, 3, 12, 15), que son celdas de alto valor estratégico.

**Estrategia**: Este patrón combina perfectamente con Esquinas (4 esquinas + 4 celdas internas de las diagonales). Si el host activa ambos patrones, prioriza las esquinas y las celdas {5, 6, 9, 10} para maximizar tu progreso hacia ambos patrones.

---

## 7. L-Shape

Una **L** que abarca un borde completo del tablero: una fila completa + una columna completa que nacen de una misma esquina.

**Total de variantes: 4** (una por cada esquina)

```
L Noroeste (NW)        L Noreste (NE)         L Suroeste (SW)        L Sureste (SE)
 ■  ■  ■  ■            ■  ■  ■  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ■  ■  ■            ■  ■  ■  ■
 Celdas:                Celdas:                Celdas:                Celdas:
 {0,1,2,3, 4,8,12}     {0,1,2,3, 7,11,15}    {12,13,14,15, 0,4,8}  {12,13,14,15, 3,7,11}
 7 celdas               7 celdas               7 celdas               7 celdas
```

**Dificultad**: Difícil (7 celdas en NW y SW; 6 celdas en NE y SE porque la esquina se comparte — pero en NW y SW la esquina de intersección 0 o 12 ya pertenece a la fila, así que son 7 celdas en los 4 casos: 4 de fila + 3 de columna adicionales, ya que la celda esquina pertenece a ambas)

Nota: En los 4 casos, la celda de la esquina se comparte entre la fila y la columna. Son 4 celdas de la fila + 4 celdas de la columna − 1 compartida = 7 celdas.

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: Si tu tabla tiene una esquina marcada y varias celdas en la fila y columna adyacentes, una L-Shape puede ser tu camino más rápido a la victoria. Las L-Shapes NW y SW comparten la columna izquierda; las NE y SE comparten la columna derecha.

---

## 8. Z-Shape

Un patrón en zigzag que recorre el tablero. Dos variantes: **Z normal** y **S (Z invertida)**.

**Total de variantes: 2**

```
Z-Shape (normal)                          S-Shape (Z invertida)
 ■  ■  ■  ■                               ·  ·  ·  ■
 ·  ·  ·  ■                               ·  ·  ■  ·
 ·  ■  ·  ·                               ·  ■  ·  ·
 ■  ■  ■  ■                               ■  ■  ■  ■
 Celdas:                                   Celdas:
 Fila 0 + celda 7 + celda 9 + Fila 3      Celda 3 + celda 6 + celda 9 + Fila 3
 = {0,1,2,3, 7, 9, 12,13,14,15}          = {3, 6, 9, 12,13,14,15}
 10 celdas                                 7 celdas

Nota: La Z-Shape requiere:
- Z normal: Fila 0 entera + Fila 3 entera + celda 7 (conecta fila 0 con fila 2) + celda 9 (conecta fila 2 con fila 3)
           = {0,1,2,3, 7, 9, 12,13,14,15} → 10 celdas
- S invertida: celda 3 (fila 0) + celda 6 (fila 1) + celda 9 (fila 2) + Fila 3 entera
             = {3, 6, 9, 12,13,14,15} → 7 celdas
```

**Dificultad**: Muy Difícil (10 celdas para Z normal; 7 celdas para S invertida)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: La Z-Shape normal es el patrón más grande después de Tabla Llena (10 de 16 celdas). Requiere paciencia y una tabla favorable. La S-Shape es más accesible con 7 celdas. En ambos casos, necesitas que el mazo coopere sacando cartas de zonas muy específicas del tablero.

---

## 9. Tabla Llena (Full Board) — ¡Lotería!

Las **16 celdas** marcadas. El patrón definitivo. Cuando gritas "¡Lotería!" con la tabla llena, has ganado el premio máximo de la ronda.

```
Tabla Llena
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 Celdas: {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}
```

**Dificultad**: Extrema (las 16 celdas — requiere que el dealer saque prácticamente todo el mazo)

**Disponible en**: **TODAS las salas** — Rookies, Champions y salas alojadas por jugadores.

**Premio**: Siempre es **Premio 2** (el premio mayor). En salas Rookies y Champions, Tabla Llena paga más que cualquier otro patrón. En salas alojadas, el host puede configurar la escala de premios.

**Estrategia**: Tabla Llena no se "busca" activamente — simplemente sucede si nadie gana con los patrones más pequeños y el dealer sigue sacando cartas. Si llegas a 12+ celdas marcadas sin que nadie haya ganado, empieza a prestar mucha atención: estás cerca. La tensión en este punto es máxima.

---

## Resumen de Patrones

| # | Patrón | Celdas | Dificultad | Rookies | Champions | Player-Hosted |
|---|--------|--------|------------|---------|-----------|---------------|
| 1 | Línea | 4 | Fácil | ✅ | ✅ | ✅ |
| 2 | Cuadrito | 4 | Media | ✅ | ✅ | ✅ |
| 3 | Pocito | 4 | Media | ❌ | ✅ | ✅ |
| 4 | Esquinas | 4 | Media | ❌ | ✅ | ✅ |
| 5 | Cruz | 7 | Difícil | ❌ | ❌ | ✅ |
| 6 | Cruz Diagonal | 8 | Muy Difícil | ❌ | ❌ | ✅ |
| 7 | L-Shape | 7 | Difícil | ❌ | ❌ | ✅ |
| 8 | Z-Shape | 7-10 | Muy Difícil | ❌ | ❌ | ✅ |
| 9 | Tabla Llena | 16 | Extrema | ✅ | ✅ | ✅ |

---

## El Sistema de Tensión (Tension System)

A medida que los jugadores se acercan a completar un patrón, el sistema de tensión de Axolotto ajusta la experiencia de juego. La barra de tensión indica qué tan cerca está **alguien** (tú u otro jugador) de ganar. No es un valor por jugador — es un estado global de la sala que todos pueden ver.

**Niveles de Tensión:**

| Nivel | Significado | Efecto |
|-------|-------------|--------|
| **Baja (Low)** | Nadie tiene más de 2 celdas en ningún patrón activo. El juego apenas comienza. | Ritmo normal. Sin presión. |
| **Media (Medium)** | Al menos un jugador tiene 3 celdas en un patrón activo (a 1 de ganar en Línea/Cuadrito/Pocito/Esquinas). | La música se intensifica ligeramente. Los jugadores empiezan a prestar más atención a las cartas que salen. |
| **Alta (High)** | Al menos un jugador está a **1 celda** de completar un patrón — o varios jugadores tienen 3 celdas en patrones distintos. | Efectos visuales en la UI (bordes del tablero pulsan). El dealer saca cartas más rápido. La adrenalina sube. |
| **Crítica (Critical)** | Múltiples jugadores están a 1 celda de ganar, o alguien está a 1 celda de Tabla Llena (15/16). | Efectos visuales máximos. La sala entera sabe que el próximo turno puede ser el último. |

**Cómo usar el Sistema de Tensión a tu favor:**

- Si la tensión está **Baja**, juega relajado. Prioriza marcar celdas que te sirvan para múltiples patrones.
- Si la tensión está **Media**, enfócate en el patrón donde estás más cerca. No te disperses.
- Si la tensión está **Alta**, revisa el tablero rápido: ¿quién está a punto de ganar? Si eres tú, aguanta la respiración. Si es otro, prepárate para la derrota.
- Si la tensión está **Crítica**, todo puede terminar en la próxima carta. Es el momento de mayor emoción en Axolotto.

---

## Configuración en Salas Alojadas por Jugadores

Cuando un jugador crea una sala (Player-Hosted Room), puede elegir qué patrones están activos. Esto permite modos de juego personalizados:

- **Modo Clásico**: Solo Línea + Cuadrito + Tabla Llena (como Rookies).
- **Modo Avanzado**: Línea + Cuadrito + Pocito + Esquinas + Tabla Llena (como Champions).
- **Modo Caótico**: Todos los patrones activos. Hasta 9 formas distintas de ganar en una sola ronda.
- **Modo Personalizado**: El host elige manualmente qué patrones activar. ¿Solo Cruz y Cruz Diagonal? ¿Solo L-Shapes? La decisión es tuya.

El host también puede configurar:
- **Premios por patrón**: Cuánto paga cada patrón en AXF y FRJ.
- **Límite de tiempo por ronda**: Tiempo máximo antes de que la ronda termine automáticamente.
- **Número máximo de ganadores**: ¿Gana el primero o pueden ganar varios?

---

## Consejos Generales para Todos los Patrones

1. **Las celdas centrales (5, 6, 9, 10) son las más valiosas**: Participan en 2 diagonales + 2 filas + 2 columnas + 4 cuadritos + 1 Pocito. Son las celdas más conectadas del tablero.

2. **Las esquinas (0, 3, 12, 15) son el segundo mejor grupo**: Cada esquina participa en 1 fila + 1 columna + 1 diagonal + 1 cuadrito + Esquinas + L-Shape + Cruz Diagonal.

3. **Las celdas del borde medio (1, 2, 4, 7, 8, 11, 13, 14) son las menos conectadas**: Solo participan en 1 fila + 1 columna (las de la mitad de borde) o 1 diagonal (si están en la diagonal). Planifica con cuidado.

4. **No te cases con un solo patrón**: La mejor estrategia es mantener abiertas varias rutas hacia la victoria. Marcar una celda debe acercarte a al menos 2 patrones simultáneamente.

5. **Observa a tus rivales**: En multijugador, si ves que alguien está a punto de completar un patrón, considera si puedes ganar antes con otro patrón diferente.

---

## English

# Winning Patterns

In Axolotto, winning a Lotería round means marking a **specific pattern** of cells on your Board before the other players. The required pattern depends on the game mode and the room you are playing in. Not all rooms use the same patterns: Rookies rooms keep things simple, while Champions rooms and player-hosted rooms unlock harder (and more rewarding) patterns.

---

## The Board (4x4)

All Lotería Boards in Axolotto are 4-row x 4-column grids, with positions numbered 0 through 15:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

Each cell contains a card from the traditional Mexican Lotería deck (El Gallo, La Dama, El Corazón, etc.). The dealer draws cards one by one, and you mark the matching cells.

---

## 1. Línea (Line)

A complete line is **4 consecutive cells in any direction**: row, column, or diagonal.

**Total variants: 10**

### Rows (4 variants)

```
Row 0:                Row 1:                Row 2:                Row 3:
 ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■
 Cells: {0,1,2,3}     Cells: {4,5,6,7}     Cells: {8,9,10,11}   Cells: {12,13,14,15}
```

### Columns (4 variants)

```
Col 0:                Col 1:                Col 2:                Col 3:
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 Cells: {0,4,8,12}    Cells: {1,5,9,13}    Cells: {2,6,10,14}   Cells: {3,7,11,15}
```

### Diagonals (2 variants)

```
Diagonal ↘            Diagonal ↙
 ■  ·  ·  ·           ·  ·  ·  ■
 ·  ■  ·  ·           ·  ·  ■  ·
 ·  ·  ■  ·           ·  ■  ·  ·
 ·  ·  ·  ■           ■  ·  ·  ·
 Cells: {0,5,10,15}   Cells: {3,6,9,12}
```

**Difficulty**: Easy (4 cells)

**Available in**: ALL rooms — Rookies, Champions, and player-hosted rooms.

**Prize**: Prize 1 (the base pattern prize). This is the most common pattern and the first one every player learns to look for.

**Strategy**: Always check all 10 possible lines every time you mark a cell. Corners (0, 3, 12, 15) appear in more lines than mid-edge cells, and center cells (5, 6, 9, 10) appear in even more patterns. Prioritize boards that already have several cells in the same line.

---

## 2. Cuadrito (2x2 Block)

A block of **2 rows x 2 columns** contiguous cells. Any group of 4 cells forming a square.

**Total variants: 9**

```
Top-Left              Top-Center            Top-Right
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Cells: {0,1,4,5}     Cells: {1,2,5,6}     Cells: {2,3,6,7}

Mid-Left              Center                Mid-Right
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Cells: {4,5,8,9}     Cells: {5,6,9,10}    Cells: {6,7,10,11}

Bottom-Left           Bottom-Center         Bottom-Right
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 Cells: {8,9,12,13}   Cells: {9,10,13,14}  Cells: {10,11,14,15}
```

**Difficulty**: Medium (4 cells, but contiguous in 2D)

**Available in**: ALL rooms — Rookies, Champions, and player-hosted rooms.

**Strategy**: Cuadrito rewards having cells grouped together in the same area of the board. If your board has a natural cluster of marked cards in one corner, focus on completing that cuadrito. The center cells (5, 6, 9, 10) belong to 4 different cuadritos — they are the most valuable for this pattern.

---

## 3. Pocito (Center)

Exactly the **central 2x2 block**. Unlike the general Cuadrito, Pocito is a fixed pattern: only one possible location.

```
Pocito
 ·  ·  ·  ·
 ·  ■  ■  ·
 ·  ■  ■  ·
 ·  ·  ·  ·
 Cells: {5, 6, 9, 10}
```

**Difficulty**: Medium (4 cells, but fixed location)

**Available in**: Champions rooms + player-hosted rooms. **Not available in Rookies.**

**Strategy**: Since Pocito is always in the center, it is worth prioritizing center cards (positions 5, 6, 9, 10) from the start if you are in a room where this pattern is active. These same cells also help with Línea and Cuadrito, so they are never a bad investment.

---

## 4. Esquinas (4 Corners)

The **4 corners** of the board. Another fixed single-location pattern.

```
Corners
 ■  ·  ·  ■
 ·  ·  ·  ·
 ·  ·  ·  ·
 ■  ·  ·  ■
 Cells: {0, 3, 12, 15}
```

**Difficulty**: Medium (4 cells, scattered)

**Available in**: Champions rooms + player-hosted rooms. **Not available in Rookies.**

**Strategy**: Corners are high-value cells because they also participate in Lines (they are ends of rows, columns, and one diagonal). Marking corners early brings you closer to multiple patterns simultaneously. If you already have 2 or 3 corners marked and you are in Champions, shift your priority to getting the fourth.

---

## 5. Cruz (Cross)

A **complete row + a complete column** that intersect. The result is a cross on the board.

**Total variants: 16** (4 rows x 4 columns)

**Example — Row 0 + Column 2:**

```
Cross (Row 0, Col 2)
 ■  ■  ■  ■
 ·  ·  ■  ·
 ·  ·  ■  ·
 ·  ·  ■  ·
 Cells: {0,1,2,3, 6,10,14}
```

```
Cross (Row 1, Col 0)      Cross (Row 2, Col 3)      Cross (Row 0, Col 0)
 ■  ·  ·  ·                ·  ·  ·  ■                ■  ■  ■  ■
 ■  ■  ■  ■                ·  ·  ·  ■                ■  ·  ·  ·
 ■  ·  ·  ·                ■  ■  ■  ■                ■  ·  ·  ·
 ■  ·  ·  ·                ·  ·  ·  ■                ■  ·  ·  ·
 Cells: {0,4,5,6,7,8,12}   Cells: {3,7,8,9,10,11,15} Cells: {0,1,2,3,4,8,12}
```

**Difficulty**: Hard (7 cells — 4 from the row + 4 from the column, minus 1 at the intersection)

**Available in**: **Player-hosted rooms only**. Not available in Rookies or Champions.

**Strategy**: With 7 required cells, Cruz is a mid-game pattern. You need the dealer to draw cards from a specific row and column. Look for intersections where you already have several marked cells in both directions. The intersection cell counts only once, so if you already have it, you only need 6 additional cells.

---

## 6. Cruz Diagonal (X Shape)

**Both diagonals** simultaneously, forming a complete X on the board.

```
Diagonal Cross (X)
 ■  ·  ·  ■
 ·  ■  ■  ·
 ·  ■  ■  ·
 ■  ·  ·  ■
 Cells: {0, 3, 5, 6, 9, 10, 12, 15}
```

**Difficulty**: Very Hard (8 cells — the 4 from each diagonal; the center cells 5,6,9,10 do NOT intersect with the main diagonals, so the complete pattern covers 8 distinct cells)

**Available in**: **Player-hosted rooms only**. Not available in Rookies or Champions.

**Important note**: The two diagonals of the 4x4 board are:
- Diagonal ↘: {0, 5, 10, 15}
- Diagonal ↙: {3, 6, 9, 12}

These 8 cells do NOT share any positions with each other, so Cruz Diagonal requires marking exactly 8 cells. However, 4 of them are corners (0, 3, 12, 15), which are high-strategic-value cells.

**Strategy**: This pattern combines perfectly with Esquinas (4 corners + 4 inner diagonal cells). If the host activates both patterns, prioritize corners and cells {5, 6, 9, 10} to maximize your progress toward both.

---

## 7. L-Shape

An **L** that spans a complete edge of the board: a full row + a full column originating from the same corner.

**Total variants: 4** (one per corner)

```
L Northwest (NW)       L Northeast (NE)       L Southwest (SW)       L Southeast (SE)
 ■  ■  ■  ■            ■  ■  ■  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ■  ■  ■            ■  ■  ■  ■
 Cells:                 Cells:                 Cells:                 Cells:
 {0,1,2,3, 4,8,12}     {0,1,2,3, 7,11,15}    {12,13,14,15, 0,4,8}  {12,13,14,15, 3,7,11}
 7 cells                7 cells                7 cells                7 cells
```

Note: In all 4 cases, the corner cell is shared between the row and the column. 4 row cells + 4 column cells - 1 shared = 7 cells.

**Difficulty**: Hard (7 cells)

**Available in**: **Player-hosted rooms only**. Not available in Rookies or Champions.

**Strategy**: If your board has a corner marked and several cells in the adjacent row and column, an L-Shape may be your fastest path to victory. NW and SW L-Shapes share the left column; NE and SE share the right column.

---

## 8. Z-Shape

A zigzag pattern that traverses the board. Two variants: **normal Z** and **S (inverted Z)**.

**Total variants: 2**

```
Z-Shape (normal)                          S-Shape (inverted Z)
 ■  ■  ■  ■                               ·  ·  ·  ■
 ·  ·  ·  ■                               ·  ·  ■  ·
 ·  ■  ·  ·                               ·  ■  ·  ·
 ■  ■  ■  ■                               ■  ·  ·  ·
 Cells:                                    Cells:
 Row 0 + cell 7 + cell 9 + Row 3          Cell 3 + cell 6 + cell 9 + Row 3
 = {0,1,2,3, 7, 9, 12,13,14,15}          = {3, 6, 9, 12,13,14,15}
 10 cells                                  7 cells
```

**Difficulty**: Very Hard (10 cells for normal Z; 7 cells for inverted S)

**Available in**: **Player-hosted rooms only**. Not available in Rookies or Champions.

**Strategy**: The normal Z-Shape is the largest pattern after Full Board (10 of 16 cells). It requires patience and a favorable board. The S-Shape is more accessible with 7 cells. In both cases, you need the deck to cooperate by drawing cards from very specific areas of the board.

---

## 9. Tabla Llena (Full Board) — Lotería!

All **16 cells** marked. The ultimate pattern. When you shout "Lotería!" with a full board, you have won the round's maximum prize.

```
Full Board
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 Cells: {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}
```

**Difficulty**: Extreme (all 16 cells — requires the dealer to draw nearly the entire deck)

**Available in**: **ALL rooms** — Rookies, Champions, and player-hosted rooms.

**Prize**: Always **Prize 2** (the major prize). In Rookies and Champions rooms, Full Board pays more than any other pattern. In player-hosted rooms, the host can configure the prize scale.

**Strategy**: Full Board is not actively "pursued" — it simply happens if no one wins with smaller patterns and the dealer keeps drawing cards. If you reach 12+ marked cells without anyone having won, start paying close attention: you are close. Tension at this point is at its maximum.

---

## Pattern Summary

| # | Pattern | Cells | Difficulty | Rookies | Champions | Player-Hosted |
|---|---------|-------|------------|---------|-----------|---------------|
| 1 | Línea | 4 | Easy | ✅ | ✅ | ✅ |
| 2 | Cuadrito | 4 | Medium | ✅ | ✅ | ✅ |
| 3 | Pocito | 4 | Medium | ❌ | ✅ | ✅ |
| 4 | Esquinas | 4 | Medium | ❌ | ✅ | ✅ |
| 5 | Cruz | 7 | Hard | ❌ | ❌ | ✅ |
| 6 | Cruz Diagonal | 8 | Very Hard | ❌ | ❌ | ✅ |
| 7 | L-Shape | 7 | Hard | ❌ | ❌ | ✅ |
| 8 | Z-Shape | 7-10 | Very Hard | ❌ | ❌ | ✅ |
| 9 | Full Board | 16 | Extreme | ✅ | ✅ | ✅ |

---

## The Tension System

As players get closer to completing a pattern, Axolotto's tension system adjusts the gameplay experience. The tension bar indicates how close **someone** (you or another player) is to winning. It is not a per-player value — it is a global room state that everyone can see.

**Tension Levels:**

| Level | Meaning | Effect |
|-------|---------|--------|
| **Low** | No one has more than 2 cells in any active pattern. The game is just getting started. | Normal pace. No pressure. |
| **Medium** | At least one player has 3 cells in an active pattern (1 away from winning on Línea/Cuadrito/Pocito/Esquinas). | Music intensifies slightly. Players start paying more attention to the cards being drawn. |
| **High** | At least one player is **1 cell away** from completing a pattern — or several players have 3 cells in different patterns. | Visual effects in the UI (board borders pulse). The dealer draws cards faster. Adrenaline rises. |
| **Critical** | Multiple players are 1 cell away from winning, or someone is 1 cell away from Full Board (15/16). | Maximum visual effects. The entire room knows the next turn could be the last. |

**How to use the Tension System to your advantage:**

- If tension is **Low**, play relaxed. Prioritize marking cells that serve multiple patterns.
- If tension is **Medium**, focus on the pattern where you are closest. Don't spread yourself thin.
- If tension is **High**, scan the board quickly: who is about to win? If it is you, hold your breath. If it is someone else, prepare for defeat.
- If tension is **Critical**, everything can end on the next card. This is the most exciting moment in Axolotto.

---

## Player-Hosted Room Configuration

When a player creates a room (Player-Hosted Room), they can choose which patterns are active. This enables custom game modes:

- **Classic Mode**: Only Línea + Cuadrito + Full Board (like Rookies).
- **Advanced Mode**: Línea + Cuadrito + Pocito + Esquinas + Full Board (like Champions).
- **Chaos Mode**: All patterns active. Up to 9 different ways to win in a single round.
- **Custom Mode**: The host manually selects which patterns to activate. Only Cruz and Cruz Diagonal? Only L-Shapes? The choice is yours.

The host can also configure:
- **Pattern prizes**: How much each pattern pays in AXF and FRJ.
- **Round time limit**: Maximum time before the round ends automatically.
- **Maximum winners**: Does the first player win, or can multiple players win?

---

## General Tips for All Patterns

1. **Center cells (5, 6, 9, 10) are the most valuable**: They participate in 2 diagonals + 2 rows + 2 columns + 4 cuadritos + 1 Pocito. They are the most connected cells on the board.

2. **Corners (0, 3, 12, 15) are the second best group**: Each corner participates in 1 row + 1 column + 1 diagonal + 1 cuadrito + Esquinas + L-Shape + Cruz Diagonal.

3. **Mid-edge cells (1, 2, 4, 7, 8, 11, 13, 14) are the least connected**: They only participate in 1 row + 1 column (mid-edges) or 1 diagonal (if on a diagonal). Plan carefully.

4. **Don't marry a single pattern**: The best strategy is to keep multiple paths to victory open. Marking a cell should bring you closer to at least 2 patterns simultaneously.

5. **Watch your opponents**: In multiplayer, if you see someone is about to complete a pattern, consider whether you can win first with a different pattern.

---

## Quick Reference / Referencia Rápida

| Concept / Concepto | Value / Valor |
|---|---|
| Board size / Tamaño del tablero | 4×4 (16 cells / celdas) |
| Easiest pattern / Patrón más fácil | Línea (4 cells) |
| Hardest non-full pattern / Patrón más difícil (no lleno) | Z-Shape (10 cells) |
| Ultimate pattern / Patrón definitivo | Tabla Llena (16 cells) |
| Total Línea variants / Variantes de Línea | 10 (4 rows + 4 cols + 2 diags) |
| Total Cuadrito variants / Variantes de Cuadrito | 9 |
| Total Cruz variants / Variantes de Cruz | 16 (4 rows x 4 cols) |
| Total L-Shape variants / Variantes de L | 4 |
| Total Z-Shape variants / Variantes de Z | 2 |
| Patterns in Rookies / Patrones en Rookies | 3 (Línea, Cuadrito, Tabla Llena) |
| Patterns in Champions / Patrones en Champions | 5 (+ Pocito, Esquinas) |
| Patterns in Player-Hosted / Patrones en Salas | Up to / Hasta 9 |
| Tension levels / Niveles de tensión | 4 (Low, Medium, High, Critical) |

---

→ See also / Ver también: [[06-como-jugar-loteria]] · [[08-modos-de-juego]] · [[10-tablas]] · [[23-salas-y-multijugador]] · [[00-INDEX]]
