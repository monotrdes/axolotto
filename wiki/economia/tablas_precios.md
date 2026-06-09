---
tags: [economia, precios]
description: "Tablas completas de precios de todos los items — fuente: backend/app/core/prices.py"
last_modified: "2026-06-07"
source_files: ["backend/app/core/prices.py", "backend/app/core/config.py"]
---

# Tablas de Precios — Axolotto

> Si un precio cambia en el código, actualizar esta tabla Y añadir entrada en [[../CHANGELOG]].
>
> Moneda: **AXF** = Axofichas (premium). **FRJ** = Frijolitos (gameplay).
> Los alias en el código son `axg`/`gal` — ver [[monedas]] para el detalle completo.

---

## Webitos (Huevos NFT)

Precio en AXF. Fuente: `WEBITO_PRICES` en `prices.py`.

| Fase | Nombre | Precio AXF |
|------|--------|-----------|
| 1 | Génesis | 400 |
| 2 | Expansión | 800 |
| 3 | Retail | 1 200 |
| Especial | Astral | 3 000 |

---

## Boosters (Packs de 7 Cartas)

Fuente: `BOOSTER_PRICES` en `prices.py`. Cada tipo se puede comprar con AXF (premium) o FRJ (earned).

### Fase 1 — First Edition

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 10 | 100 |
| Nido | 10 | 100 |
| Cosmos | 10 | 100 |
| Pure (solo 1 carta) | 6 | 60 |

### Fase 2 — Unlimited

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 15 | 150 |
| Nido | 15 | 150 |
| Cosmos | 15 | 150 |
| Pure | 10 | 100 |

### Fase 3 — Retail / Standard

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 20 | 200 |
| Nido | 20 | 200 |
| Cosmos | 20 | 200 |
| Pure | 15 | 150 |

### Especial — Booster Brillante (Foil)

| Tipo | AXF | FRJ |
|------|-----|-----|
| Foil | 80 | 800 |

---

## Cápsulas Gashapon

Fuente: `GASHAPON_TIER_COSTS` en `prices.py`. Precio en FRJ.

| Tier | Costo FRJ |
|------|-----------|
| Bronce | 1 500 |
| Plata | 5 000 |
| Oro | 20 000 |
| Triple (pack 3) | 22 500 |

---

## Tablas de Juego (Boards)

Fuente: `BOARD_PRICES` en `prices.py`.

| Tipo de Tabla | AXF | FRJ |
|---------------|-----|-----|
| Clásica | 10 | 130 |
| Suerte | 50 | 520 |
| Plasma | 150 | 1 560 |
| Cósmica | 200 | 0 |

> La tabla Cósmica solo acepta pago en AXF; el campo FRJ está en 0 en el código.

---

## Slots de Cueva (Desbloqueo de Boards adicionales)

Fuente: `BOARD_SLOT_COSTS` en `prices.py`. Precio en FRJ. Los primeros 3 slots están incluidos por defecto; estos son los desbloqueos adicionales.

| Slot # | Costo FRJ |
|--------|-----------|
| 4 | 500 |
| 5 | 1 000 |
| 6 | 2 000 |
| 7 | 4 000 |
| 8 | 8 000 |
| 9 | 15 000 |

---

## Multijugador (siempre en FRJ)

Fuente: `MULTIPLAYER_ROOMS` en `prices.py`. Solo FRJ por mandato legal (`MULTIPLAYER_CURRENCY = "frijolito"` en `config.py`).

| Sala | Entry Fee FRJ | Premio 1er lugar FRJ | Consolación FRJ | XP Ganador (Board/Axo) | XP Perdedor (Board/Axo) |
|------|--------------|---------------------|----------------|------------------------|-------------------------|
| Charco de Novatos (`rookie_pool`) | 25 | 85 | 8 | 25 / 35 | 8 / 8 |
| Fosa del Campeón (`champion_abyss`) | 100 | 400 | 20 | 60 / 75 | 15 / 15 |

> Salas cave (player-hosted) usan `buy_in_frj` configurable por el anfitrión.

---

## Consumibles

Fuente: `CONSUMABLE_PRICES` en `prices.py`.

| Item | Precio | Moneda |
|------|--------|--------|
| Gotas Anti-Escarcha | 200 | FRJ |
| Lámpara Infrarroja Pro | 200 | AXF |
| Alimento Común — Algae Pellet | 30 | FRJ |
| Alimento Premium — Brine Shrimp | 150 | FRJ |
| Solvente de Pegamento | 120 | FRJ |
| Upgrade Board Slots | 300 | AXF |

---

## VIP (Membresía 30 días)

Fuente: `CONSUMABLE_PRICES` en `prices.py` y `VIP_CONFIG` en `config.py`.

| Tier | Precio AXF |
|------|-----------|
| Coral | 400 |
| Dorado | 600 |
| Axolite | 1 800 |

> Desglose completo de beneficios en [[vip_tiers]].

---

## Valor Nominal

Fuente: `prices.py` líneas 4-8.

| Concepto | Valor |
|----------|-------|
| 1 AXF en MXN (nominal) | $2.00 MXN |
| Paquete de referencia (FRJ) | 200 FRJ = $35 MXN |
| 1 FRJ en MXN (aproximado) | $0.175 MXN |
| DevEx 70% bruto | $1.40 MXN por AXF |
| DevEx 70% neto | $1.14 MXN por AXF |
| DevEx 50% bruto | $1.00 MXN por AXF |

---

→ Ver estructura de beneficios VIP en [[vip_tiers]] · Modelo económico en [[economia_general]] · Diferencias entre monedas en [[monedas]]
