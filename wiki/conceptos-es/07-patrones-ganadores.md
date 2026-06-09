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

