---
tags: [mecanicas, juego, patrones]
description: "Los patrones ganadores del juego con grids ASCII y índices exactos de cada celda"
last_modified: "2026-06-07"
source_files: ["backend/app/services/game_logic.py"]
---

# Patrones Ganadores

El tablero de Lotería es una grilla 4×4 con índices 0–15 en orden row-major:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

`X` = celda requerida, `.` = celda libre.

---

## Patrón: `line` — Línea recta (10 variantes)

Cualquiera de las 10 líneas de la constante `WINNING_LINES` en `game_logic.py`.

### Filas (4 variantes)

**Fila 0**
```
X X X X
. . . .
. . . .
. . . .
```
Índices: `{0, 1, 2, 3}`

**Fila 1**
```
. . . .
X X X X
. . . .
. . . .
```
Índices: `{4, 5, 6, 7}`

**Fila 2**
```
. . . .
. . . .
X X X X
. . . .
```
Índices: `{8, 9, 10, 11}`

**Fila 3**
```
. . . .
. . . .
. . . .
X X X X
```
Índices: `{12, 13, 14, 15}`

### Columnas (4 variantes)

**Columna 0**
```
X . . .
X . . .
X . . .
X . . .
```
Índices: `{0, 4, 8, 12}`

**Columna 1**
```
. X . .
. X . .
. X . .
. X . .
```
Índices: `{1, 5, 9, 13}`

**Columna 2**
```
. . X .
. . X .
. . X .
. . X .
```
Índices: `{2, 6, 10, 14}`

**Columna 3**
```
. . . X
. . . X
. . . X
. . . X
```
Índices: `{3, 7, 11, 15}`

### Diagonales (2 variantes)

**Diagonal principal (↘)**
```
X . . .
. X . .
. . X .
. . . X
```
Índices: `{0, 5, 10, 15}`

**Diagonal anti-principal (↙)**
```
. . . X
. . X .
. X . .
X . . .
```
Índices: `{3, 6, 9, 12}`

**Total variantes `line`: 10**

---

## Patrón: `cuadrito` — Cuadrado 2×2 (9 variantes)

Definido en `WINNING_CUADRITOS`. Cualquiera de los nueve cuadrados 2×2 posibles.

**Cuadrito (0,1,4,5) — superior izquierdo**
```
X X . .
X X . .
. . . .
. . . .
```
Índices: `{0, 1, 4, 5}`

**Cuadrito (1,2,5,6)**
```
. X X .
. X X .
. . . .
. . . .
```
Índices: `{1, 2, 5, 6}`

**Cuadrito (2,3,6,7) — superior derecho**
```
. . X X
. . X X
. . . .
. . . .
```
Índices: `{2, 3, 6, 7}`

**Cuadrito (4,5,8,9)**
```
. . . .
X X . .
X X . .
. . . .
```
Índices: `{4, 5, 8, 9}`

**Cuadrito (5,6,9,10) — centro**
```
. . . .
. X X .
. X X .
. . . .
```
Índices: `{5, 6, 9, 10}`

**Cuadrito (6,7,10,11)**
```
. . . .
. . X X
. . X X
. . . .
```
Índices: `{6, 7, 10, 11}`

**Cuadrito (8,9,12,13)**
```
. . . .
. . . .
X X . .
X X . .
```
Índices: `{8, 9, 12, 13}`

**Cuadrito (9,10,13,14)**
```
. . . .
. . . .
. X X .
. X X .
```
Índices: `{9, 10, 13, 14}`

**Cuadrito (10,11,14,15) — inferior derecho**
```
. . . .
. . . .
. . X X
. . X X
```
Índices: `{10, 11, 14, 15}`

**Total variantes `cuadrito`: 9**

---

## Patrón: `pocito` — Centro 2×2 (1 variante)

Definido en `WINNING_POCITO = frozenset({5, 6, 9, 10})`.

```
. . . .
. X X .
. X X .
. . . .
```
Índices: `{5, 6, 9, 10}`

**Total variantes `pocito`: 1**

---

## Patrón: `esquinas` — 4 Esquinas (1 variante)

Definido en `WINNING_ESQUINAS = frozenset({0, 3, 12, 15})`.

```
X . . X
. . . .
. . . .
X . . X
```
Índices: `{0, 3, 12, 15}`

**Total variantes `esquinas`: 1**

---

## Patrón: `cruz` — Cruz recta (función `check_cruz_recta`)

Cualquier fila completa + cualquier columna completa simultáneas. 4 filas × 4 columnas = **16 variantes** posibles. Las celdas de intersección solo se requieren una vez.

Ejemplo (fila 0 + columna 0):
```
X X X X
X . . .
X . . .
X . . .
```
Índices variables según la fila y columna elegidas.

**Total variantes `cruz`: 16**

---

## Patrón: `cruz_diagonal` — La X (1 variante)

Definido en `WINNING_CRUZ_DIAGONAL = frozenset({0, 3, 5, 6, 9, 10, 12, 15})`.

```
X . . X
. X X .
. X X .
X . . X
```
Índices: `{0, 3, 5, 6, 9, 10, 12, 15}`

**Total variantes `cruz_diagonal`: 1**

---

## Patrón: `l_shape` — Forma L (4 variantes)

Definido en `WINNING_L_SHAPES`. Una esquina + su fila completa + su columna completa.

**L top-left**
```
X X X X
X . . .
X . . .
X . . .
```
Índices: `{0, 1, 2, 3, 4, 8, 12}`

**L top-right**
```
X X X X
. . . X
. . . X
. . . X
```
Índices: `{0, 1, 2, 3, 7, 11, 15}`

**L bottom-left**
```
X . . .
X . . .
X . . .
X X X X
```
Índices: `{0, 4, 8, 12, 13, 14, 15}`

**L bottom-right**
```
. . . X
. . . X
. . . X
X X X X
```
Índices: `{3, 7, 11, 12, 13, 14, 15}`

**Total variantes `l_shape`: 4**

---

## Patrón: `z_shape` — Forma Z/S (2 variantes)

Definido en `WINNING_Z_SHAPES`. Fila superior + 2 celdas diagonales medias + fila inferior.

**Z**
```
X X X X
. . X .
. X . .
X X X X
```
Índices: `{0, 1, 2, 3, 6, 9, 12, 13, 14, 15}`

**S (Z espejo)**
```
X X X X
. X . .
. . X .
X X X X
```
Índices: `{0, 1, 2, 3, 5, 10, 12, 13, 14, 15}`

**Total variantes `z_shape`: 2**

---

## Patrón: `full_board` — Tablero lleno (1 variante)

Verificado en `check_full_board`: `len(marked) == 16`. Todas las 16 celdas marcadas.

```
X X X X
X X X X
X X X X
X X X X
```
Índices: `{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}`

**Total variantes `full_board`: 1**

---

## Patrones activos por sala

| Sala | Modo | Patrones habilitados |
|------|------|----------------------|
| `rookie_pool` / `rookie` | Fácil | `line`, `cuadrito` |
| `champion_abyss` / `champion` | Difícil | `line`, `cuadrito`, `pocito`, `esquinas` |

Los patrones `cruz`, `cruz_diagonal`, `l_shape`, `z_shape`, `full_board` existen en el código (`PATTERN_CHECKERS`) pero no están asignados a ninguna sala en `ROOM_CONFIG`. Se usan en `validate_win` para validación de backend.

---

## Resumen de totales

| Patrón | Variantes |
|--------|-----------|
| `line` | 10 |
| `cuadrito` | 9 |
| `pocito` | 1 |
| `esquinas` | 1 |
| `cruz` | 16 |
| `cruz_diagonal` | 1 |
| `l_shape` | 4 |
| `z_shape` | 2 |
| `full_board` | 1 |
| **Total** | **45** |

---

## Sistema de Tensión

`check_tension_status` en `game_logic.py` evalúa los tableros de todos los jugadores y devuelve un nivel de tensión:

| Nivel | Condición |
|-------|-----------|
| `low` | Ninguna hot_line activa |
| `medium` | Al menos 1 hot_line (≤2 celdas faltantes en cualquier patrón) |
| `high` | Al menos 2 jugadores a ≤2 celdas de ganar |
| `critical` | Al menos 1 jugador a ≤1 celda de ganar |

Una "hot_line" se activa cuando un jugador tiene ≤2 celdas faltantes para completar una `line` o un `cuadrito`.

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]]
