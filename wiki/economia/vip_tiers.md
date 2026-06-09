---
tags: [economia, vip]
description: "Comparativa completa de tiers VIP con todos los beneficios — fuente: config.py:VIP_CONFIG"
last_modified: "2026-06-07"
source_files: ["backend/app/core/config.py:VIP_CONFIG", "backend/app/core/prices.py:CONSUMABLE_PRICES"]
---

# Membresía VIP — Comparativa de Tiers

> Duración: 30 días. Renovación automática configurable desde el perfil del jugador.
>
> Fuente autoritativa: `VIP_CONFIG` en `backend/app/core/config.py`.

---

## Tabla de Beneficios

| Beneficio | Sin VIP | Coral | Dorado | Axolite |
|-----------|---------|-------|--------|---------|
| **Precio AXF** | — | 400 | 600 | 1 800 |
| **FRJ diarios** | 0 | 40 | 100 | 200 |
| **Descuento tienda** | 0% | 5% | 12% | 20% |
| **Slots de tabla extra** | 0 | 0 | +1 | +2 |
| **Slots de Axolotito extra** | 0 | 0 | 0 | +1 |
| **Comisión P2P** | 5% | 4% | 3% | 1.5% |
| **Bonus jackpot** | 0% | 0% | 0% | +5% |
| **Descuento multijugador** | 0% | 0% | 0% | 15% |
| **FRJ al activar** | — | 200 | 500 | 1 000 |
| **Boosters al activar** | — | Ninguno | 1x Normal | 1x Foil |
| **Cápsulas mensuales** | — | 2x Bronce | 2x Bronce + 1x Plata | 3x Bronce + 2x Plata + 1x Oro |
| **Popular** | — | No | Sí | No |

---

## Descripción de los Beneficios de Bienvenida

Al activar el VIP por primera vez (o al renovar), el sistema acredita inmediatamente:

| Tier | Bienvenida |
|------|-----------|
| Coral | 200 FRJ en cuenta |
| Dorado | 500 FRJ + 1 Booster Normal |
| Axolite | 1 000 FRJ + 1 Booster Foil |

---

## Cápsulas Gashapon Mensuales

Las cápsulas se acumulan en cuenta y son reclamables con `POST /api/v1/rewards/lunar/claim`.

| Tier | Bronce | Plata | Oro |
|------|--------|-------|-----|
| Coral | 2 | — | — |
| Dorado | 2 | 1 | — |
| Axolite | 3 | 2 | 1 |

---

## Notas Importantes

- **Caducidad**: si el VIP caduca, los Axolotitos extra que ocupaban el slot bonus quedan **CONGELADOS** hasta renovar. No se borran, pero no son jugables ni rentables.
- **FRJ diarios**: se acumulan en la cuenta Xochimilco. Son reclamables manualmente desde la UI. No se transfieren automáticamente a la wallet activa.
- **Auto-renovación**: configurable desde el perfil del jugador. Si está activa y la wallet tiene saldo, la renovación se ejecuta al expirar el período de 30 días.
- **Bonus jackpot Axolite**: el +5% aplica sobre el share individual del jugador en Premio 1, Premio 2 y Jackpot de Oro. Se aplica en `multiplayer_service.py` durante el settlement de la sala.
- **Descuento multijugador Axolite**: 15% sobre el entry fee de la sala. Solo aplica en salas públicas (`rookie_pool`, `champion_abyss`).

---

## Análisis de Valor: Recuperación por FRJ Diarios

Cuántos días de FRJ diarios se necesitan para recuperar el costo del VIP, asumiendo que los FRJ valen $0.175 MXN cada uno y el AXF $2.00 MXN.

| Tier | Costo AXF | Costo MXN equiv. | FRJ/día | FRJ/día en MXN | Días para recuperar |
|------|-----------|-----------------|---------|----------------|---------------------|
| Coral | 400 AXF | $800 MXN | 40 FRJ | $7.00 MXN | ~114 días |
| Dorado | 600 AXF | $1 200 MXN | 100 FRJ | $17.50 MXN | ~69 días |
| Axolite | 1 800 AXF | $3 600 MXN | 200 FRJ | $35.00 MXN | ~103 días |

> Nota: estos cálculos usan los precios nominales de `prices.py`. La rentabilidad real depende de cómo se usen los FRJ obtenidos (competir, comprar cápsulas, etc.). El descuento de tienda del 20% (Axolite) y los boosters de bienvenida mejoran sustancialmente el valor efectivo.

---

→ Ver precios de membresía en [[tablas_precios]] · Historial de cambios: [[../CHANGELOG]]
