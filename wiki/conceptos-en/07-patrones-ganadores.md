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
