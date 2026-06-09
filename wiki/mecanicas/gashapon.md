---
tags: [mecanicas, gashapon, capsulas]
description: "Sistema de cápsulas Gashapon: pity, probabilidades, recompensas del Ciclo Lunar"
last_modified: "2026-06-07"
source_files: ["backend/app/services/capsule_service.py", "backend/app/services/lunar_streak_service.py", "backend/app/services/daily_reward_service.py"]
---

# Cápsulas Gashapon

---

## Tiers de Cápsulas

| Tier | Costo FRJ | Pity (rolls sin Axolotito → garantía) |
|------|----------|--------------------------------------|
| Bronce | 1,500 | 10 |
| Plata | 5,000 | 5 |
| Oro | 20,000 | 3 |
| Triple Suerte | 22,500 | (aplica el pity de cada tier incluido) |

La Triple Suerte (`TRIPLE_COST = 22500.0`) incluye los tres tiers en un solo paquete. El costo base sumado sería 26,500 FRJ; los 22,500 representan un descuento aproximado del 15 %.

---

## Tabla de Probabilidades — Pool Normal (`TIER_POOLS`)

Los breakpoints son **acumulados** (se compara contra un único roll `_rng.random()`):

### Bronce (1,500 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.45 | FRJ | 45 % |
| 0.45 – 0.75 | Carta | 30 % |
| 0.75 – 0.85 | Accesorio | 10 % |
| 0.85 – 0.95 | Sobre (booster) | 10 % |
| 0.95 – 1.00 | Axolotito (huevo) | 5 % |

### Plata (5,000 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.20 | FRJ | 20 % |
| 0.20 – 0.65 | Carta | 45 % |
| 0.65 – 0.80 | Accesorio | 15 % |
| 0.80 – 0.90 | Sobre (booster) | 10 % |
| 0.90 – 1.00 | Axolotito (huevo) | 10 % |

### Oro (20,000 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.05 | FRJ | 5 % |
| 0.05 – 0.45 | Carta | 40 % |
| 0.45 – 0.65 | Accesorio | 20 % |
| 0.65 – 0.75 | Sobre (booster) | 10 % |
| 0.75 – 1.00 | Axolotito (huevo) | 25 % |

---

## Rangos de FRJ al obtener outcome "gal" (`FRJ_RANGES`)

| Tier | FRJ mínimo | FRJ máximo |
|------|-----------|-----------|
| Bronce | 50 | 150 |
| Plata | 200 | 600 |
| Oro | 500 | 3,000 |

Los valores son `_rng.uniform(lo, hi)`, redondeados a 1 decimal.

---

## Rareza mínima de cartas y accesorios por tier

### Cartas (`TIER_CARD_RARITIES`)

| Tier | Rarezas posibles |
|------|----------------|
| Bronce | COMMON, RARE |
| Plata | RARE, EPIC |
| Oro | EPIC, LEGENDARY |

### Accesorios (`TIER_ACC_RARITIES`)

| Tier | Rarezas posibles |
|------|----------------|
| Bronce | COMMON |
| Plata | RARE |
| Oro | EPIC, LEGENDARY |

---

## Probabilidad de Booster Foil cuando sale "Sobre" (`FOIL_FROM_SOBRE`)

Dentro del outcome "sobre", hay un check secundario de que el booster sea FOIL:

| Tier | Probabilidad de Foil |
|------|---------------------|
| Bronce | 5 % |
| Plata | 12 % |
| Oro | 22 % |

---

## Drops Legendarios Pre-check (`CAPSULE_LEGENDARY_PROBS`)

Antes del pool normal, se evalúan drops especiales. Si sale, el pity se reinicia a 0 y no cuenta como roll normal:

| Tier | Booster Foil (pre-check) |
|------|------------------------|
| Bronce | 0.2 % |
| Plata | 0.5 % |
| Oro | 1.0 % |

Nota: el Webito Astral **ya no** se obtiene por cápsula directamente. Ahora se obtiene como recompensa al desbloquear el nivel 7 u 8 de la Cueva (ver [[expansion_cueva]]).

---

## Sistema Pity (`CapsulaPity`)

El modelo `CapsulaPity` en `backend/app/models/items.py` tiene tres contadores:

| Campo en BD | Tier al que corresponde | Threshold |
|------------|------------------------|-----------|
| `pity_cobre` | Bronce | 10 rolls sin Axolotito → garantía |
| `pity_plata` | Plata | 5 rolls sin Axolotito → garantía |
| `pity_oro` | Oro | 3 rolls sin Axolotito → garantía |

Nota histórica: el campo se llama `pity_cobre` (no `pity_bronce`) porque el tier se llamaba "Cobre" en una versión anterior. El mapeo actual en `capsule_service.py` es `PITY_FIELD_MAP = {"bronce": "pity_cobre", "plata": "pity_plata", "oro": "pity_oro"}`.

El pity se **reinicia a 0** cuando:
- Sale un Axolotito por el pool normal.
- Sale un drop legendario pre-check (Booster Foil).
- Sale una Tabla Forjada.

El pity **aumenta en 1** para todos los demás outcomes.

---

## Sistema de Ciclo Lunar (Recompensas Diarias)

El Ciclo Lunar reemplaza y unifica el sistema de cápsula diaria gratuita y las recompensas de racha. Se reclama una vez por día calendario (zona horaria Mexico City, UTC-6).

### Estructura del Ciclo

- **Loop 1 (días 1–6)**: cada día otorga FRJ según `DAILY_FRJ`.
- **Loop 2 (día 7)**: en lugar de FRJ, se otorgan cápsulas según la Luna activa (`LUNA_REWARDS`).
- **Loop 3 (ciclo completo)**: completar Luna 6 reinicia el ciclo a Luna 1 y suma 1 a `lunar_cycles_completed`.

### Recompensas FRJ diarias (`DAILY_FRJ`)

| Día | FRJ |
|-----|-----|
| 1 | 50 |
| 2 | 65 |
| 3 | 80 |
| 4 | 95 |
| 5 | 110 |
| 6 | 130 |
| 7 | Cápsulas según Luna activa |

### Recompensas del Día 7 por Luna (`LUNA_REWARDS`)

| Luna | Recompensa |
|------|-----------|
| 1 | 1× Cápsula Bronce |
| 2 | 2× Cápsulas Bronce |
| 3 | 1× Cápsula Plata |
| 4 | 1× Cápsula Plata + 1× Cápsula Bronce |
| 5 | 2× Cápsulas Plata |
| 6 | 1× Cápsula Oro |

### Reglas de Racha

| Condición | Efecto |
|-----------|--------|
| Gap ≤ 1 día | La racha continúa normalmente |
| Gap > 1 día y ≤ 7 días | `lunar_streak_day` se reinicia a 0, pero la Luna (semana) no cambia |
| Gap > 7 días | `lunar_streak_day` se reinicia a 0 Y `lunar_week` vuelve a Luna 1 |

### Recompensas Diarias Legacy (`DailyRewardService`)

El archivo `daily_reward_service.py` contiene un sistema anterior más simple, aún presente en el código:

| Día de racha | FRJ | Fórmula |
|-------------|-----|---------|
| 1 | 15 | base |
| 2 | 20 | base + 1×5 |
| 3 | 25 | base + 2×5 |
| 4 | 30 | base + 3×5 |
| 5 | 35 | base + 4×5 |
| 6 | 40 | base + 5×5 |
| 7 | 45 | base + 6×5 (máximo) |

- `BASE_REWARD = 15.0 FRJ`
- `STREAK_BONUS = 5.0 FRJ por día consecutivo`
- `MAX_STREAK = 7 días`

Este servicio legacy puede estar activo en paralelo o reemplazado por el Ciclo Lunar — (verificar manualmente qué endpoint lo usa actualmente).

---

## Relacion Costo-Beneficio

Basándose en los datos del código:

- **Bronce**: mayor probabilidad de FRJ (45 %), bueno para acumular capsulas baratas. Pity en 10 asegura huevo cada 10 rolls como máximo.
- **Plata**: mejor balance carta/accesorio, pity en 5 rolls.
- **Oro**: 25 % base de huevo sin depender del pity, drops legendarios 5× más frecuentes que Bronce. La mayoría de FRJ posible (500–3,000 por drop de FRJ). Pity garantizado en solo 3 rolls.

El Ciclo Lunar (día 7 en Luna 6) entrega 1 Cápsula Oro gratis, equivalente a 20,000 FRJ de valor nominal, cada 6 semanas de juego consistente.

Ver también: [[incubacion_imprinting]], [[expansion_cueva]], [[estadisticas_axolotito]]
