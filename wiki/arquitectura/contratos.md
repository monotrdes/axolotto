---
tags: [arquitectura, contratos, solidity, web3]
description: "Suite de 12 contratos Solidity: tipos, propósitos y relaciones"
last_modified: "2026-06-07"
source_files: ["contracts/src/*.sol"]
---

# Contratos Solidity — Suite Axolotto

## Tabla de Contratos

| Contrato | Tipo | Token/Symbol | Propósito | Caller autorizado |
|----------|------|-------------|-----------|------------------|
| `Axoficha.sol` | ERC-20 | AXF (Axoficha) | Moneda premium actual — adquirida con dinero real (SPEI/cripto) | GameController |
| `Axogema.sol` | ERC-20 | AXG (Axogema) | Moneda premium legacy — nombre anterior de AXF, misma mecánica | GameController |
| `GemaAlga.sol` | ERC-20 | GAL (Gema Alga) | Moneda de juego legacy (nombre anterior de FRJ), gana jugando | GameController |
| `Frijolito.sol` | ERC-20 | FRJ (Frijolito) | Moneda de juego actual — se gana jugando, paga entradas, tienda | GameController |
| `Webitos.sol` | ERC-721 | WEBITO | Huevos NFT únicos — incuban en Axolotitos con cariñitos | GameController |
| `Axolotitos.sol` | ERC-721 | — | Mascotas NFT con DNA y stats (8 stats) almacenados on-chain | GameController |
| `CartasLoteria.sol` | ERC-1155 | — | 54 cartas de Lotería semi-fungibles (token IDs 1-54) | GameController |
| `Boosters.sol` | ERC-1155 | — | Sobres sellados de 7 cartas; 3 fases (420/1260/2520 por fase) | GameController |
| `TablasLoteria.sol` | ERC-721 + ERC-1155Holder | — | Tableros 4x4 NFT; las 16 cartas quedan en escrow on-chain | GameController |
| `Consumables.sol` | ERC-1155 | — | Consumibles: Algae Pellet, Brine Shrimp, Gotas Anti-Escarcha, Lámpara Infrarroja | GameController |
| `GameController.sol` | custom / Ownable | — | Hub central — único autorizado a mint/burn en todos los contratos | Admin wallet (Owner) |
| `Counter.sol` | utility | — | Contrato utilitario de contador (Foundry default / testing) | — |

## Notas sobre el Renombrado de Monedas (2026-06)

- `Axoficha.sol` (AXF) es el contrato **activo** de la moneda premium.
- `Axogema.sol` (AXG) es el contrato **legacy** — mismo patrón, nombre anterior. Ambos coexisten en el repositorio.
- `Frijolito.sol` (FRJ) es el contrato **activo** de la moneda de juego.
- `GemaAlga.sol` (GAL) es el contrato **legacy** — misma mecánica que FRJ.
- El backend usa alias (`wallet.axogemas = wallet.axofichas`) para compatibilidad con registros históricos.

## GameController — Hub Central

```
Backend (Treasury Wallet)
    ↓
GameController
    ├──→ Axoficha / Axogema / GemaAlga / Frijolito  (ERC-20 mint/burn)
    ├──→ Webitos / Axolotitos                         (ERC-721 mint)
    ├──→ CartasLoteria / Boosters / Consumables       (ERC-1155 mint/burn)
    └──→ TablasLoteria                                (ERC-721 mint/burn + escrow cartas)
```

- Solo el GameController puede mintear, quemar y transferir tokens del juego.
- El GameController emite eventos de auditoría: `TiendaCompra`, `PartidaJugada`, `AxolotitoNutrido`.
- Para el modo manual en tiempo real emite: `ManualGameStarted`, `CardCalled`, `LoteriaShouted`, `ManualGameEnded`.
- El modificador `onlyFRJ` bloquea envíos de AXF/ETH nativo en operaciones multijugador — solo acepta Frijolitos.

## Mecánicas On-Chain

### Webitos (Huevos)
- Fases 1-3 con oferta limitada: 420 / 1260 / 2520 huevos por fase.
- Cada Webito tiene un `webitoFase` (1, 2 o 3) registrado en mapping on-chain.
- La incubación ocurre off-chain (backend + frontend); solo el nacimiento mint el NFT Axolotito.

### Axolotitos (Mascotas NFT)
- Struct `Stats` almacena 8 valores on-chain: `salinity`, `luck`, `focus`, `stamina`, `charisma`, `agility`, `wisdom`, `strength`.
- El `dna_sequence` (uint256) se genera por el backend al eclosionar y se inscribe en la cadena.
- La blockchain es la fuente de verdad para ownership y stats al momento de compra/venta.

### CartasLoteria (54 Cartas)
- Token IDs 1-54 — una carta del mazo de Lotería Mexicana por ID.
- Las cartas pueden estar en el inventario del jugador o en escrow dentro del contrato `TablasLoteria`.

### TablasLoteria (Tableros)
- Al crear un tablero: las 16 cartas se transfieren al contrato (escrow) y se mintea 1 NFT de Tabla.
- Al disolver: se quema el NFT de Tabla y se devuelven 15 cartas (1 se destruye aleatoriamente, lógica off-chain).
- Las cartas en escrow cuentan para el staking pasivo.

### Replay Protection (off-chain)
El backend registra cada `tx_hash` procesado en `ProcessedTransaction` (UNIQUE) antes de acreditar recompensa. Ver [[backend]] — Patrones Obligatorios.

## Redes Soportadas

| Red | Chain ID | Puerto / URL |
|-----|---------|-------------|
| Local (Anvil) | 31337 | `http://localhost:8545` |
| Plasma Testnet | 9746 | URL de Plasma Testnet |
| Producción | pendiente | — |

## Direcciones de Contrato

Las direcciones se configuran exclusivamente via variables de entorno:

- **Frontend**: `NEXT_PUBLIC_CONTRACT_AXOFICHA`, `NEXT_PUBLIC_CONTRACT_FRIJOLITO`, `NEXT_PUBLIC_CONTRACT_AXOLOTITOS`, etc. (en `frontend/env.local`)
- **Backend**: variables en `backend/.env` leídas por `backend/app/core/config.py`

**Nunca hardcodear direcciones de contratos en el código.**

Ver [[../api/resumen_endpoints]] para los endpoints que interactúan con contratos vía `web3_service.py`.
