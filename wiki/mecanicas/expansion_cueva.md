---
tags: [mecanicas, cueva, progresion]
description: "Los 8 niveles de expansión de cueva con costos, beneficios y requisitos exactos"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/cave_expansion.py"]
---

# Expansión de Cueva (Cenote) — 8 Niveles

El jugador tiene una sola cueva (Cenote) que se expande progresivamente hasta 8 niveles. Cada expansión requiere cumplir un logro de desbloq y pagar en FRJ. Los miembros VIP reciben un 50 % de descuento en FRJ y un 50 % menos de tiempo de excavación.

Aceleración de excavación: **4 AXF por hora restante** (redondeado arriba, mínimo 1 AXF).

---

## Tabla Completa de Niveles

| Nivel | Nombre | Spots Axo | Slots Decor | Mesa | Asientos | Excav. (h) | Costo FRJ | Huevo recompensa |
|-------|--------|-----------|-------------|------|----------|------------|-----------|-----------------|
| 1 | El Nicho | 1 | 2 | No | — | — | Gratis (tutorial) | — |
| 2 | La Gruta | 2 | 4 | No | — | 2.0 | 500 | fase1 |
| 3 | La Caverna | 3 | 6 | Sí | 2 | 6.0 | 1,500 | fase1_plus |
| 4 | El Salón | 4 | 8 | Sí | 4 | 12.0 | 4,000 | fase2 |
| 5 | El Santuario | 5 | 10 | Sí | 6 | 24.0 | 8,000 | fase2_nature |
| 6 | El Abismo | 6 | 12 | Sí | 8 | 36.0 | 15,000 | fase2_nature |
| 7 | El Templo | 7 | 14 | Sí | 8 | 48.0 | 30,000 | astral |
| 8 | Palacio Astral | 8 | 16 | Sí | 8 | 72.0 | 60,000 | astral |

**Nota VIP**: costo FRJ efectivo = `costo × 0.5`; tiempo excavación efectivo = `horas × 0.5`.

---

## Requisitos de Logro por Nivel

### Nivel 2 — La Gruta
- **Requisito**: 10 partidas jugadas (total) AND Axolotito principal nivel ≥ 3.

### Nivel 3 — La Caverna
- **Requisito**: 3 victorias totales AND racha de 3 días consecutivos jugando.

### Nivel 4 — El Salón
- **Requisito**: al menos 1 Jackpot ganado.

### Nivel 5 — El Santuario
- **Requisito**: Axolotito principal nivel ≥ 15.

### Nivel 6 — El Abismo
- **Requisito**: (50 partidas totales AND 100 alimentaciones a Axolotitos) OR ser VIP Coral, Dorado o Axolite.

### Nivel 7 — El Templo
- **Requisito**: (100 partidas totales AND 15 victorias totales) OR ser VIP Dorado o Axolite.

### Nivel 8 — Palacio Astral
- **Requisito**: (200 partidas totales AND poseer al menos un Axolotito con skin `gold` o `astral`) OR ser VIP Axolite.

---

## Descripción de Bonus Pasivos (`CAVE_PASSIVE_BONUSES`)

Los bonos son acumulativos: al llegar al nivel N se activan todos los bonos de los niveles anteriores.

| Nivel desbloqueado | Bonus pasivo | Descripción |
|-------------------|-------------|-------------|
| 1 | (ninguno) | Cueva inicial sin bonos |
| 2 | `gal_multiplier: 1.02` | +2 % sobre ganancias de FRJ (Frijolitos) |
| 3 | `extra_starting_card: True` | +1 carta en la mano inicial al comenzar partida |
| 4 | `booster_chance_bonus: 0.05` | +5 % de probabilidad de obtener booster como drop |
| 5 | `global_incubation_slot: 1` | +1 slot global de incubación de Webitos |
| 6 | `p2p_fee_reduction: 0.05` | -5 % de comisión en transacciones del mercado P2P |
| 7 | `monthly_foil_booster: 1` | 1 booster foil por mes |
| 8 | `axg_multiplier: 1.10` | +10 % de AXF en el ecosistema |

Los bonos multiplicativos (`gal_multiplier`, `axg_multiplier`) se multiplican entre sí si se acumulan; los aditivos (`booster_chance_bonus`, `p2p_fee_reduction`) se suman.

---

## Mecánica de Excavación

1. El jugador llama a `POST /api/v1/cave/expand` si cumple el logro y tiene FRJ suficientes.
2. Se descuenta el FRJ y se registra `cave_expansion_started_at` (timestamp de inicio) y `cave_expansion_target_level`.
3. La cueva no sube de nivel inmediatamente: hay un timer de excavación de 2 a 72 horas según el nivel.
4. Al hacer `GET /api/v1/cave/status`, el backend auto-verifica si el timer ya expiró y sube el nivel automáticamente, entregando el huevo de recompensa.
5. El jugador puede acelerar pagando AXF vía `POST /api/v1/cave/expand/accelerate` (ratio: 4 AXF/hora restante, ceil, mínimo 1 AXF).

### Truco de timestamp VIP
Para el descuento de tiempo VIP, el backend desplaza `cave_expansion_started_at` hacia el pasado en `(total_hours - effective_hours)` horas, de modo que el check de auto-completado (que siempre usa `total_hours` como referencia) se satisface antes.

---

## Slots de Staking derivados

La cantidad de Axolotitos que pueden hacer staking simultáneamente es `cave_level + 1` (ver [[staking]]).

---

## Tipos de Huevo de Recompensa

| Tipo | Descripción |
|------|-------------|
| `fase1` | Huevo estándar de fase 1 |
| `fase1_plus` | Huevo de fase 1 con rareza rara/épica/legendaria |
| `fase2` | Huevo de fase 2 (item_metadata `fase: 2`) |
| `fase2_nature` | Huevo de fase 2 (se usa la misma búsqueda que `fase2`) |
| `astral` | Huevo con `is_astral: true` en metadata, o nombre con "astral" |

Ver también: [[staking]], [[incubacion_imprinting]], [[estadisticas_axolotito]]
