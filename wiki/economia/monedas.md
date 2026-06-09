---
tags: [economia, monedas]
description: "AXF y FRJ: diferencias, aliases, cómo obtenerlas, restricciones de uso"
last_modified: "2026-06-07"
source_files: ["backend/app/core/config.py", "backend/app/core/prices.py"]
---

# Monedas del Juego

---

## Tabla Comparativa

| Característica | AXF (Axofichas) | FRJ (Frijolitos) |
|---------------|----------------|-----------------|
| Nombre completo | Axofichas | Frijolitos |
| Nombre anterior | AXG / Axogemas | GAL / Gemas Alga |
| Alias en código (Wallet) | `axg`, `axofichas`, `axf` | `gal`, `frijolitos`, `frj` |
| Contrato Solidity | `Axogema.sol` / `AXOGEMA_ADDRESS` | `GemaAlga.sol` / `GEMA_ALGA_ADDRESS` |
| Tipo | Moneda premium | Moneda de gameplay |
| Cómo obtener | Compra real (MoonPay / USDC onramp) | Jugar, staking de boards, FRJ VIP diarios, P2P, premios multijugador |
| Valor nominal | $2.00 MXN por AXF | Sin valor en dinero real ($0.175 MXN de referencia) |
| Usos principales | VIP, Webitos, Boosters, Boards, Lámpara Infrarroja, Upgrade Slots | Salas multijugador, Cápsulas Gashapon, Alimentos, Solvente, Slots de cueva |
| ¿Usable en multijugador? | **PROHIBIDO en escrow/lobby** | **UNICA moneda permitida** |
| ¿Tiene DevEx? | Sí (70% bruto = $1.40 MXN / 70% neto = $1.14 MXN) | No |

---

## Aliases en el Código

```python
# Wallet model: estos pares acceden al MISMO campo en la DB
wallet.axg         # alias legacy — no usar en código nuevo
wallet.axofichas   # nombre correcto — SIEMPRE usar este en código nuevo

wallet.gal         # alias legacy — no usar en código nuevo
wallet.frijolitos  # nombre correcto — SIEMPRE usar este en código nuevo
```

Los aliases `axg` y `gal` existen para compatibilidad con endpoints y scripts legacy que aún usan los nombres anteriores. El código nuevo debe usar `axofichas` y `frijolitos`.

---

## Restricción de Multijugador

Fuente: `config.py` — `MULTIPLAYER_CURRENCY: str = "frijolito"`

> Por compliance legal, el juego multijugador **SOLO** acepta Frijolitos (FRJ).
> Axofichas (AXF) está prohibido en cualquier operación de lobby, salas o escrow.

Esta restricción está hardcodeada como constante de módulo en `config.py`. Ningún endpoint de lobby/multiplayer debe aceptar o procesar AXF. El servicio de multiplayer (`multiplayer_service.py`) valida esto en el registro de sala.

---

## Cómo Obtener AXF

1. **Compra con USDC** vía MoonPay widget (onramp fiat → USDC → AXF)
2. **Checkout crypto** directo — `POST /api/v1/checkout/create-order` (Polygon Amoy)
3. **Modo local/dev** — todo usuario nuevo recibe `DEV_AUTO_REWARD_AXF = 50 000 AXF` automáticamente

## Cómo Obtener FRJ

1. **Ganar partidas individuales** — pago en FRJ por victoria (campo `GAL obtenidas` en simulación)
2. **Staking de boards** — emisión pasiva por hora según rareza de cartas en la tabla (ver [[economia_general]])
3. **FRJ VIP diarios** — 40/100/200 FRJ por día según tier (ver [[vip_tiers]])
4. **Premios multijugador** — el ganador recibe el premio de la sala en FRJ
5. **P2P marketplace** — vender cartas, boards o Axolotitos a otros jugadores
6. **Modo local/dev** — todo usuario nuevo recibe `DEV_AUTO_REWARD_FRJ = 500 000 FRJ` automáticamente

---

## Historia del Renombre (2026-06)

- **AXG (Axogemas) → AXF (Axofichas)**: renombre para simplificar y estandarizar la identidad de marca
- **GAL (Gemas Alga) → FRJ (Frijolitos)**: renombre temático alineado al universo acuático mexicano
- Los aliases `axg` / `gal` se mantienen en el modelo `Wallet` para compatibilidad con código legacy, clientes existentes y datos en DB
- Los contratos Solidity mantienen sus nombres originales (`Axogema.sol`, `GemaAlga.sol`) — el renombre es solo en capa de producto/UI

---

→ Ver todos los precios en [[tablas_precios]] · VIP y FRJ diarios en [[vip_tiers]]
