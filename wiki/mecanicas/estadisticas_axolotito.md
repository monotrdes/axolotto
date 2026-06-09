---
tags: [mecanicas, axolotito, stats]
description: "Las 8 estadísticas del Axolotito con rangos exactos, fórmulas y efectos en juego"
last_modified: "2026-06-07"
source_files: ["backend/app/models/axolotito.py", "backend/app/services/game_logic.py", "backend/app/services/imprinting_service.py"]
---

# Estadísticas del Axolotito

## Tabla de Stats

| Stat | Campo en código | Tipo | Default | Rango | Efecto en juego |
|------|----------------|------|---------|-------|-----------------|
| Suerte | `stat_luck` | float | 10.0 | 0.0 – 100.0 | Probabilidad de Lucky Save (ver fórmula abajo) |
| Concentración | `stat_focus` | float | 50.0 | 0.0 – 100.0 | Probabilidad de miss al marcar carta (ver fórmula abajo) |
| Energía Máxima | `stat_stamina` | int | 100 | 50 – 200 | Tope máximo de `energy_current`; afecta recuperación |
| Salinidad | `stat_salinity` | float | 5.0 | 0.0 – 100.0 | Mala suerte; afecta deltas de imprinting en Webitos |
| Carisma | `stat_charisma` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |
| Agilidad | `stat_agility` | float | 10.0 | 0.0 – 100.0 | Igual a Focus en el sistema de imprinting (`stat_agility = focus`) |
| Sabiduría | `stat_wisdom` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |
| Fuerza | `stat_strength` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |

Nota: `stat_charisma`, `stat_wisdom` y `stat_strength` existen en el modelo pero `imprinting_service.py` los fija en `0.0` al eclosionar un Webito. El diseño 4-stats activo es: **Luck, Focus, Stamina, Salinity**.

---

## Fórmula: Miss Chance

Definida en `game_logic.py`, función `_miss_chance(focus)`:

```
miss_chance = max(0.0, min(0.3, (100.0 - focus) * 0.003))
```

| `stat_focus` | Miss Chance | Descripción |
|-------------|-------------|-------------|
| 100 | 0.0 % | Sin fallos |
| 80 | 6.0 % | Bot Campeón (`bot_focus=80`) |
| 50 | 15.0 % | Jugador típico |
| 40 | 18.0 % | Bot Novato (`bot_focus=40`) |
| 0 | 30.0 % | Máximo posible (techo en 30 %) |

El techo es 30 % (`min(0.3, ...)`). El piso es 0 % (`max(0.0, ...)`). La fórmula es lineal entre focus 0 y focus 100.

---

## Fórmula: Lucky Save

Definida en `game_logic.py`, función `_lucky_save(axo_luck, already_used)`:

```
chance = (axo_luck / 1000.0) * 0.5
```

- Se activa **como máximo una vez por partida** (`already_used` guard).
- Cuando se activa, cancela un evento negativo para el jugador.

| `stat_luck` | Probabilidad Lucky Save |
|------------|------------------------|
| 0 | 0.0 % |
| 10 | 0.5 % |
| 50 | 2.5 % |
| 100 | 5.0 % (máximo) |

---

## Energía y Recuperación

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `energy_current` | int | 100 | Energía restante. Se consume por partida. Se recupera al dormir. |
| `stat_stamina` | int | 50–200 | Energía máxima del Axolotito. Default 100. |
| `sleep_expires_at` | datetime | null | Timestamp en que termina el sueño y se restaura la energía. |
| `status` | str | `"idle"` | Estados posibles: `idle`, `expedition`, `resting`, `studying`, `playing`, `sleeping`, `waiting_settlement` |

El diseño indica 10 partidas por ciclo de sueño (energy_current se consume y se recupera con `sleep_expires_at`). Los bots no consumen energía.

---

## Sistema de Imprinting

Campos en el modelo `Axolotito` que afectan a los Webitos que este Axolotito apadrina:

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `nature` | str (opcional) | `null` | Naturaleza del Axolotito. Modifica los deltas de imprinting. |
| `mentorship_count` | int | 0 | Número de Webitos que este Axolotito ha apadrinado. |
| `tutored_by_id` | int (opcional) | `null` | ID del Axolotito que apadrinó a este cuando era Webito. |

### Natures disponibles y sus efectos

Definidas en `imprinting_service.py`, función `compute_deltas`:

| Nature | Efecto |
|--------|--------|
| `lucky` | Si `luck_delta > 0`, se multiplica por 1.25 |
| `methodical` | Si `focus_delta > 0`, se multiplica por 1.25 |
| `hyperactive` | Si `stamina_delta > 0`, se multiplica por 1.25 |
| `glutton` | Si el padrino pierde, todos los deltas negativos se reducen al 80 % de su magnitud (amortiguador de pérdida) |

### Herencia genética del padrino al Webito

Al iniciar el imprinting (`initial_base_stats` en `imprinting_service.py`), los stats base del Webito se calculan con rangos aleatorios más un bonus del padrino:

| Stat | Rango base aleatorio | Factor herencia (nivel ≤20) | Factor herencia (nivel >20) |
|------|---------------------|----------------------------|----------------------------|
| `luck` | 20.0 – 50.0 | `padrino.stat_luck × 0.10` | `padrino.stat_luck × 0.15` |
| `focus` | 25.0 – 55.0 | `padrino.stat_focus × 0.10` | `padrino.stat_focus × 0.15` |
| `stamina` | 70.0 – 110.0 | `padrino.stat_stamina × 0.10` | `padrino.stat_stamina × 0.15` |
| `salinity` | 10.0 – 30.0 | `padrino.stat_salinity × 0.10` | `padrino.stat_salinity × 0.15` |

El factor sube de 10 % a 15 % cuando el padrino supera el nivel 20.

---

## Stats finales al eclosionar (imprinting_service.py → `final_stats`)

| Stat final | Fórmula | Clamp |
|-----------|---------|-------|
| `stat_luck` | `base_stat_luck + bonus_luck` | 0.0 – 100.0 |
| `stat_focus` | `base_stat_focus + bonus_focus` | 0.0 – 100.0 |
| `stat_stamina` | `base_stat_stamina + bonus_stamina` | 50.0 – 200.0 (int) |
| `stat_salinity` | `base_stat_salinity + bonus_salinity_adj` | 0.0 – 100.0 |
| `stat_agility` | igual a `stat_focus` | — |
| `stat_charisma` | `0.0` (fijo al eclosionar) | — |
| `stat_wisdom` | `0.0` (fijo al eclosionar) | — |
| `stat_strength` | `0.0` (fijo al eclosionar) | — |

Los bonus acumulados en `WebitoIncubation` están limitados a ±50 (luck, focus, salinity) y ±60 (stamina) mediante `_clamp`.

---

## Campos adicionales relevantes

| Campo | Descripción |
|-------|-------------|
| `cpu_win_streak` | Racha consecutiva de victorias vs CPU. Se reinicia al perder. |
| `loyalty_points` | Puntos de afecto/lealtad acumulados (sistema de progresión pendiente). |
| `escrow_balance_gal` | FRJ en custodia del Axolotito (escrow interno). |
| `is_frozen_by_vip` | `True` si el dueño bajó de tier VIP y el slot extra fue revocado. |
| `is_main` | Marca al Axolotito principal del jugador. |
| `is_tutorial` | `True` si es el Axolotito creado durante el tutorial. |
| `blockchain_token_id` | Token ID en el contrato `Axolotitos.sol` (único en la cadena). |
| `dna_sequence` | Representación string del uint256 de ADN en cadena. |

Ver también: [[staking]], [[incubacion_imprinting]], [[patrones_ganadores]]
