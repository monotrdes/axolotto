---
tags: [mecanicas, staking, economia]
description: "Sistema de staking: multiplicadores por rareza de skin y partes, tasa de emisión FRJ/hora"
last_modified: "2026-06-07"
source_files: ["backend/app/services/staking_service.py"]
---

# Staking — Ganancias Pasivas de FRJ

Los Axolotitos generan FRJ (Frijolitos) pasivamente mientras su dueño siga jugando al menos 1 partida cada 24 horas (regla Play-to-Stake).

---

## Multiplicadores por Color de Skin

El color de skin determina la rareza, y la rareza determina el multiplicador base por hora.

### Mapeo skin_color → rareza (`SKIN_RARITY_MAP`)

| skin_color | Rareza |
|-----------|--------|
| `pink` | comun |
| `gray` | comun |
| `gray_light` | comun |
| `gray_dark` | comun |
| `cyan` | rara |
| `purple` | rara |
| `neon` | epica |
| `coral` | epica |
| `gold` | legendaria |
| `astral` | astral |

Cualquier color no listado se trata como `comun`.

### Multiplicador base por rareza (`SKIN_MULTIPLIER`, FRJ/hora)

| Rareza | FRJ/hora (skin base) |
|--------|---------------------|
| comun | 0.05 |
| rara | 0.15 |
| epica | 0.40 |
| legendaria | 1.00 |
| astral | 2.50 |

---

## Bonus por Rareza de Partes

Cada una de las 6 partes corporales contribuye con un bonus adicional de FRJ/hora según su rareza. Si un valor de trait no está mapeado, se trata como `comun` (0.01 FRJ/hora).

### `PARTS_BONUS_BY_RARITY`

| Rareza de parte | Bonus FRJ/hora |
|----------------|---------------|
| comun | 0.01 |
| rara | 0.03 |
| epica | 0.08 |
| legendaria | 0.20 |

### Rareza de cada trait (`_TRAIT_RARITY`)

**gill_type (branquias)**

| Valor | Rareza |
|-------|--------|
| `short` | comun |
| `normal` | comun |
| `feathery` | rara |
| `crown` | epica |
| `phoenix` | legendaria |

**eye_type (ojos)**

| Valor | Rareza |
|-------|--------|
| `cute` | comun |
| `derp` | comun |
| `dreamer` | rara |
| `cool` | epica |
| `zen` | legendaria |

**mouth_type (boca)**

| Valor | Rareza |
|-------|--------|
| `flat` | comun |
| `smile` | comun |
| `fang` | rara |
| `rockstar` | epica |
| `divine` | legendaria |

**tail_type (cola)**

| Valor | Rareza |
|-------|--------|
| `standard` | comun |
| `wavy` | comun |
| `betta` | rara |
| `plasma` | epica |

**forehead_type (frente)**

| Valor | Rareza |
|-------|--------|
| `none` | comun |
| `stripes` | comun |
| `gem` | rara |
| `halo` | epica |

**limb_type (extremidades)**

| Valor | Rareza |
|-------|--------|
| `soft` | comun |
| `claws` | comun |
| `scales` | rara |
| `coral` | epica |

Nota: `tail_type`, `forehead_type` y `limb_type` no tienen variantes `legendaria` en la tabla actual.

---

## Fórmula Completa de Tasa Horaria

Definida en `StakingService.calculate_axolotito_hourly_rate`:

```
hourly_rate = SkinMultiplier × (1 + 0.1 × level) + SUM(PartsBonus)
```

- **SkinMultiplier**: valor de `SKIN_MULTIPLIER` según rareza del `skin_color`.
- **level**: campo `level` del Axolotito (comienza en 1).
- **SUM(PartsBonus)**: suma de los bonus de las 6 partes (`gill_type`, `eye_type`, `mouth_type`, `tail_type`, `forehead_type`, `limb_type`).

### Ejemplos de cálculo

**Axolotito mínimo** (skin pink, nivel 1, todas las partes comun):
```
0.05 × (1 + 0.1×1) + (0.01×6) = 0.05 × 1.1 + 0.06 = 0.055 + 0.06 = 0.115 FRJ/hora
```

**Axolotito máximo teórico** (skin astral, nivel con partes legendarias):
```
2.50 × (1 + 0.1×nivel) + (0.20×3 + 0.08×3)  [3 legendarias + 3 épicas, aproximación]
```

---

## Regla Play-to-Stake

- **Condición**: el jugador debe haber completado al menos 1 partida en las últimas 24 horas.
- **Campo evaluado**: `user.last_play_date` comparado contra `datetime.utcnow() - timedelta(hours=24)`.
- **Si inactivo**: `calculate_accrued_frj` retorna `0.0` y no se acumula nada.
- **Constante**: `PLAY_TO_STAKE_HOURS = 24`

---

## Cap de Acumulación

- **Máximo de acumulación**: `MAX_ACCUMULATION_HOURS = 12` horas.
- El Axolotito nunca acumula más de `12 × hourly_rate` FRJ sin reclamar, incluso si pasan más de 12 horas.
- Al reclamar por primera vez (`last_staking_claim is None`), se otorga directamente el equivalente a 12 horas.

---

## Slots de Staking

La cantidad de Axolotitos que pueden generar staking simultáneamente depende del nivel de cueva del usuario:

```
staking_slots = user.cave_level + 1
```

| Nivel de cueva | Slots de staking |
|---------------|-----------------|
| 1 (El Nicho) | 2 |
| 2 (La Gruta) | 3 |
| 3 (La Caverna) | 4 |
| 4 (El Salón) | 5 |
| 5 (El Santuario) | 6 |
| 6 (El Abismo) | 7 |
| 7 (El Templo) | 8 |
| 8 (Palacio Astral) | 9 |

Para aumentar slots se debe expandir la cueva (ver [[expansion_cueva]]).

---

## Cómo Calcular Tu Ganancia Estimada

```
ganancia_estimada = hourly_rate × horas_activas
```

Donde `horas_activas` es el tiempo transcurrido desde el último claim, con tope en `MAX_ACCUMULATION_HOURS = 12`.

Si tienes múltiples Axolotitos, la ganancia total es la suma de cada uno hasta sus respectivos caps individuales.

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]]
