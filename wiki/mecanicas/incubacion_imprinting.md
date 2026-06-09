---
tags: [mecanicas, incubacion, crianza]
description: "Sistema de incubación de huevos Webito e imprinting con Axolotitos padrinos"
last_modified: "2026-06-07"
source_files: ["backend/app/models/items.py:WebitoIncubation", "backend/app/services/incubation_service.py", "backend/app/services/imprinting_service.py"]
---

# Incubación e Imprinting

Los Webitos son huevos que se incuban mediante calor (clicks) y cuidados. El sistema de imprinting permite que un Axolotito padrino moldee los stats del Axolotito que nacerá.

---

## Modelo WebitoIncubation — Campos Completos

### Sistema Térmico del Huevo

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `calor_actual` | float | 0.0 | Temperatura del huevo, rango 0–100 %. Sube con clicks. |
| `clicks_hoy` | int | 0 | Clicks recibidos en el día actual. |
| `clicks_totales` | int | 0 | Total histórico de clicks. |
| `is_frozen` | bool | False | Si el huevo está congelado (pierde calor en lugar de ganarlo). |
| `frozen_clicks_left` | int | 0 | Clicks restantes en estado congelado antes de volver a la normalidad. |
| `protected_until` | datetime | null | Timestamp hasta el que el huevo no puede ser dañado. |
| `genetic_purity` | float | 100.0 | Pureza genética del huevo. Decrece con eventos negativos durante la incubación. |
| `fecha_inicio` | datetime | utcnow | Fecha de inicio de la incubación. |
| `fecha_eclosion_estimada` | datetime | requerido | Fecha estimada de eclosión. |
| `ultimo_click` | datetime | utcnow | Timestamp del último click recibido. |

### Sistema de Cuidados (Cariñitos)

Tres tipos de cuidado con cooldowns distintos. Los bonos se acumulan en los campos `bonus_*` y se aplican al nacer.

| Tipo de cuidado | Campo timestamp | Cooldown | Stat bonificado |
|----------------|----------------|----------|----------------|
| Acariciar (petting) | `last_petting` | 4 horas | `bonus_strength` y `bonus_agility` |
| Cantarle (singing) | `last_singing` | 8 horas | `bonus_wisdom` y `bonus_focus` |
| Alimentar (feeding) | `last_feeding` | 12 horas | `bonus_stamina` y `bonus_luck` |

Los cooldowns **no están definidos en `items.py`** con constantes explícitas; el valor "4h / 8h / 12h" proviene del comentario en el campo del modelo. Verificar en el endpoint de incubación si difieren.

### Campos de Bonus Acumulados (cuidados)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `bonus_strength` | 0.0 | Acumulado por acariciar |
| `bonus_agility` | 0.0 | Acumulado por acariciar |
| `bonus_wisdom` | 0.0 | Acumulado por cantarle |
| `bonus_focus` | 0.0 | Acumulado por cantarle (también afectado por imprinting) |
| `bonus_stamina` | 0.0 | Acumulado por alimentar (también afectado por imprinting) |
| `bonus_luck` | 0.0 | Acumulado por alimentar (también afectado por imprinting) |

---

## Sistema de Imprinting con Padrino Axolotito

El imprinting reemplaza al sistema de cooldown de cuidados: en lugar de clicks, es el padrino quien juega partidas y su desempeño moldea los stats del Webito.

### Juegos Requeridos por Rareza del Huevo

Definido en `imprinting_service.py`, constante `_REQUIRED_GAMES`:

| Rareza del huevo | Juegos de imprinting requeridos |
|-----------------|--------------------------------|
| common | 3 |
| rare | 5 |
| epic | 7 |
| legendary | 7 |

Cuando `imprinting_games_played >= required`, el campo `imprinting_complete` se pone en `True` y el ADN queda sellado.

### Campos de Imprinting en WebitoIncubation

| Campo | Default | Descripción |
|-------|---------|-------------|
| `imprinting_games_played` | 0 | Partidas completadas con el padrino. |
| `imprinting_padrino_id` | null | ID del Axolotito que actúa como padrino. |
| `base_stat_luck` | 0.0 | Stat base de suerte (asignado al iniciar imprinting). |
| `base_stat_focus` | 0.0 | Stat base de concentración. |
| `base_stat_stamina` | 0.0 | Stat base de stamina. |
| `base_stat_salinity` | 0.0 | Stat base de salinidad. |
| `bonus_salinity_adj` | 0.0 | Ajuste de salinidad acumulado durante imprinting. |
| `imprinting_complete` | False | True cuando el ADN está sellado y listo para eclosionar. |

---

## Herencia Genética

Los stats base se generan al iniciar el imprinting (`imprinting_service.py → initial_base_stats`):

```
base_luck    = random(20.0, 50.0) + padrino.stat_luck    × factor
base_focus   = random(25.0, 55.0) + padrino.stat_focus   × factor
base_stamina = random(70.0, 110.0) + padrino.stat_stamina × factor
base_salinity = random(10.0, 30.0) + padrino.stat_salinity × factor
```

- `factor = 0.10` si `padrino.level <= 20`
- `factor = 0.15` si `padrino.level > 20`

### Deltas por Partida (imprinting_service.py → compute_deltas)

Los deltas se acumulan en `bonus_luck`, `bonus_focus`, `bonus_stamina`, `bonus_salinity_adj`.

**Suerte (luck_delta)**

| Condición | Delta |
|-----------|-------|
| Padrino tuvo jackpot | +20.0 (fijo) |
| Padrino ganó | +random(8.0, 15.0) |
| Padrino perdió | -random(8.0, 12.0) |

**Concentración (focus_delta)**

| Condición | Delta base |
|-----------|-----------|
| mark_accuracy ≥ 0.80 | +random(10.0, 18.0) |
| mark_accuracy ≤ 0.50 | -random(8.0, 14.0) |
| padrino_energy_pct > 0.80 | +5.0 adicional |

**Stamina (stamina_delta)**

| Condición | Delta |
|-----------|-------|
| session_game_count ≥ 3 | +random(10.0, 15.0) |
| session_game_count == 1 | -5.0 |
| padrino_energy_pct > 0.80 | +8.0 adicional |

**Salinidad (salinity_delta)**

| Condición | Delta |
|-----------|-------|
| padrino_sal < 20.0 | -random(6.0, 10.0) |
| padrino_sal > 50.0 | +random(8.0, 12.0) |
| mark_accuracy < 0.40 | +5.0 adicional |

### Clamps de bonus acumulados

| Bonus | Rango permitido |
|-------|----------------|
| `bonus_luck` | -50.0 – +50.0 |
| `bonus_focus` | -50.0 – +50.0 |
| `bonus_stamina` | -60.0 – +60.0 |
| `bonus_salinity_adj` | -50.0 – +50.0 |

### Genetic Purity

El campo `genetic_purity` (default 100.0) existe en el modelo. Su lógica de reducción no está definida en `imprinting_service.py` ni `incubation_service.py` — (dato no encontrado en código — verificar manualmente en el endpoint de incubación).

---

## Tutorial de Incubación

Campos del tutorial en `WebitoIncubation`:

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `tutorial_phase` | int | 0 | Fase activa: 0 = sin tutorial, 1–3 = activo, 4 = karma, 5 = completo |
| `tutorial_act_index` | int | 0 | Acto exacto del script del tutorial (0–11) |
| `tutorial_karma` | str | null | Karma resultante: `"lucky"` o `"salty"` |
| `tutorial_board_card_ids` | list | null | 16 card IDs determinísticos para el tablero del tutorial |

Las fases 0–5 definen el progreso del tutorial de incubación:

| Fase | Descripción |
|------|-------------|
| 0 | Sin tutorial activo (huevo real o no iniciado) |
| 1–3 | Tutorial activo — el jugador recibe instrucciones guiadas |
| 4 | Fase de karma — se determina si el Axolotito nacerá con karma `lucky` o `salty` |
| 5 | Tutorial completo — el Axolotito nació |

La lógica detallada de cada acto (0–11) del script del tutorial no está en `incubation_service.py` — (dato no encontrado en código — verificar en `tutorial_service.py`).

---

## Stats Finales al Eclosionar

```
stat_luck     = clamp(base_stat_luck + bonus_luck, 0.0, 100.0)
stat_focus    = clamp(base_stat_focus + bonus_focus, 0.0, 100.0)
stat_stamina  = int(clamp(base_stat_stamina + bonus_stamina, 50.0, 200.0))
stat_salinity = clamp(base_stat_salinity + bonus_salinity_adj, 0.0, 100.0)
stat_agility  = stat_focus  (alias)
stat_charisma = 0.0
stat_wisdom   = 0.0
stat_strength = 0.0
```

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]], [[gashapon]]
