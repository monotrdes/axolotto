# Plan: Renombrar nombres legacy de monedas y contratos en todo el sistema

**Task ID**: `task-1780928574-56`
**Fecha**: 2026-06-08
**Estado**: Planning

## Contexto

Al hacer deploy de los contratos inteligentes en Anvil, la salida muestra los nombres viejos:
```
GAL (ERC-20):          0x5FbDB2315678afecb367f032d93F642f64180aa3
AXG (ERC-20):          0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
Boosters (ERC-1155):   0x5FC8d32690cc91D4c39d9d3abcBD16989F875707
```

Aunque el sistema ya tiene los nuevos contratos (`Axoficha.sol`, `Frijolito.sol`), el `GameController.sol` sigue importando y usando los contratos viejos. Además, hay cientos de referencias a los nombres viejos en backend, frontend, wiki, docs, agentes y scripts.

## Renames

| Viejo | Nuevo | Contexto |
|-------|-------|----------|
| `AXG` / `Axogema` / `axogema` | `AXF` / `Axoficha` / `axoficha` | Moneda principal |
| `GAL` / `GemaAlga` / `Gema Alga` | `FRJ` / `Frijolito` / `frijolito` | Moneda secundaria |
| `Boosters` / `boosters` | `Sobrecito` / `sobrecito` | Contrato ERC-1155 + producto |

## Lo que NO se modifica

1. **Archivos de migración Alembic** — registro histórico inmutable
2. **`docs/completed/`** — documentos archivados, no se modifican
3. **Variables de entorno** (`NEXT_PUBLIC_AXOGEMA_ADDRESS`, `NEXT_PUBLIC_GEMA_ALGA_ADDRESS`) — refieren a direcciones de contrato, no a la moneda
4. **Columnas de base de datos** — requieren migración separada y riesgo de downtime
5. **Aliases de backward-compat** en modelos Python (`Wallet.axogemas`, `AxgPurchaseRecord`) — se mantienen para compatibilidad
6. **`wiki/ai/gotchas.md`** — documenta intencionalmente el doble naming

---

## Fase 1: Contratos (crítico — afecta el deploy)

### 1.1 `contracts/src/GameController.sol`
- Cambiar imports: `GemaAlga.sol` → `Frijolito.sol`, `Axogema.sol` → `Axoficha.sol`
- Cambiar tipos: `GemaAlga` → `Frijolito`, `Axogema` → `Axoficha`
- Cambiar nombres de variables: `gal` → `frj`, `axg` → `axf`
- Cambiar nombres de funciones: `depositarGAL` → `depositarFRJ`, `depositarAXG` → `depositarAXF`, `cobrarGAL` → `cobrarFRJ`, `cobrarAXG` → `cobrarAXF`
- Cambiar parámetros: `precioAXG` → `precioAXF`, `precioGAL` → `precioFRJ`, `cuotaGAL` → `cuotaFRJ`, `premioGAL` → `premioFRJ`
- Cambiar strings en eventos/requires: `"AXG"` → `"AXF"`, `"GAL"` → `"FRJ"`
- Cambiar comentarios

### 1.2 `contracts/src/Boosters.sol`
- Cambiar comentarios y strings: `"Boosters:"` → `"Sobrecito:"`
- Cambiar nombres de eventos: `BoosterMinted` → `SobrecitoMint`, `BoosterOpened` → `SobrecitoAbierto`
- Cambiar nombres de funciones: `mintBooster` → `mintSobrecito`, `burnBooster` → `burnSobrecito`, `openBooster` → `abrirSobrecito`, `transferBooster` → `transferirSobrecito`
- **NOTA**: El nombre del contrato en sí (`Boosters`) se mantiene para la dirección desplegada, o se renombra a `Sobrecito` — decidir si se despliega nuevo contrato o se mantiene el nombre interno

### 1.3 `contracts/script/Deploy.s.sol`
- Cambiar labels de output: `DEPLOYED_AXG` → `DEPLOYED_AXF`, `DEPLOYED_GAL` → `DEPLOYED_FRJ`
- Cambiar variables internas y comentarios

---

## Fase 2: Backend

### 2.1 Services (prioridad alta — lógica de negocio)

**`backend/app/services/web3_service.py`:**
- `transferir_axogemas()` → `transferir_axofichas()`
- `burn_axogemas()` → `burn_axofichas()`
- `mint_gal()` → `mint_frj()`
- `burn_gal()` → `burn_frj()`
- `_load_abi("Axogema")` → `_load_abi("Axoficha")`
- `_load_abi("GemaAlga")` → `_load_abi("Frijolito")`
- `_load_abi("Boosters")` → `_load_abi("Sobrecito")`
- Comentarios con nombres viejos

**`backend/app/services/bank_service.py`:**
- Referencias a `CurrencyType.AXOGEMA` → mantener (enum internos) o cambiar strings
- `wallet.axogemas` → `wallet.axofichas` (usar propiedad nueva)
- `transferir_axogemas` → `transferir_axofichas`
- Comentarios

**`backend/app/services/shop_service.py`:**
- `payment_currency == CurrencyType.AXOGEMA` → mantener o actualizar según enum
- `wallet.axogemas` → `wallet.axofichas`
- `Web3Service.burn_axogemas` → `Web3Service.burn_axofichas`
- Comentarios "AXG", "AXG on-chain", "AXG -> GAL" → actualizar
- `welcome_boosters` → `welcome_sobrecitos`
- `credit_axg` → `credit_axf`
- Strings de UI "AXG" → "AXF", "GAL" → "FRJ"

**`backend/app/services/checkout_service.py`:**
- `AXG_PACKS` → `AXF_PACKS`
- `FIRST_PURCHASE_BONUS` comment → actualizar
- Comentarios "compras de AXG", "mintea AXG" → actualizar
- Error strings

**`backend/app/services/board_service.py`:**
- Strings player-facing: "25 GAL" → "25 FRJ", "cuesta 25 GAL" → "cuesta 25 FRJ", "50 GAL" → "50 FRJ"

**`backend/app/services/f2p_service.py`:**
- `DAILY_CAP_GAL` → `DAILY_CAP_FRJ`
- `_WIN_GAL` → `_WIN_FRJ`
- `_LOSS_GAL` → `_LOSS_FRJ`
- Return dict key `"gal"` → `"frj"` (verificar consumidores)

**`backend/app/services/dialogue_engine.py`:**
- Player-facing strings con "GAL" → "FRJ" (~10 ocurrencias)

**`backend/app/services/vip_scheduler.py`:**
- `wallet.axogemas` → `wallet.axofichas`
- Comentarios

**`backend/app/services/drop_service.py`, `admin_service.py`, `capsule_service.py`:**
- Variables `boosters` → `sobrecitos` (donde sea variable local)
- `max_boosters` → `max_sobrecitos`

### 2.2 Models (prioridad media — backward compat)

**`backend/app/models/economy.py`:**
- Revisar si `CurrencyType.AXOGEMA` y `CurrencyType.GEMA_ALGA` deben cambiar
- Propiedades alias `axogemas`, `gemas_alga` se mantienen (backward compat)
- `axg_amount` → mantener alias, usar `axf_amount` internamente
- `VIP_GAL_EXPIRED` → `VIP_FRJ_EXPIRED` (cuidado con DB)
- `AxgPurchaseRecord` alias → mantener

**`backend/app/models/user.py`:**
- `f2p_daily_gal_earned` → `f2p_daily_frj_earned` (requiere migración DB — EVALUAR)
- `vip_pending_gal` → `vip_pending_frj` (requiere migración DB — EVALUAR)

**Otros modelos (`board.py`, `axolotito.py`, `items.py`, `lobby_models.py`):**
- Campos `*_gal` → `*_frj` — SOLO si no requiere migración o se hace migración

### 2.3 Endpoints (prioridad media)

- `bank.py`: response field alias `"axogemas"` → mantener (backward compat con frontend)
- `checkout.py`: comentarios
- `cave_decor.py`, `cave_expansion.py`: `wallet.axogemas` → `wallet.axofichas`, strings
- `rewards.py`, `shop.py`: actualizar referencias

### 2.4 Config

**`backend/app/core/prices.py`:**
- Keys `"axg"` → `"axf"`, `"gal"` → `"frj"` en diccionarios de precios
- **ALERTA**: Esto afecta la carga de precios desde DB/JSON. Verificar compatibilidad.

**`backend/app/core/config.py`:**
- `"price_axg"` → `"price_axf"` en VIP tier configs
- `"welcome_boosters"` → `"welcome_sobrecitos"`

### 2.5 Tests

Actualizar todas las referencias en tests para que usen los nuevos nombres:
- `test_vip_system.py`: `make_wallet(axogemas=...)` → `make_wallet(axofichas=...)`
- `test_shop_service.py`: mocks de `burn_axogemas` → `burn_axofichas`
- `test_abi_sync.py`: nombres de ABI
- `test_blockchain_desync.py`: `transferir_axogemas` → `transferir_axofichas`

### 2.6 Scripts de simulación

- `simulate_universe.py`: variables `boosters_*` → `sobrecitos_*`, comentarios
- `simulation/phase_03_boosters.py` → renombrar archivo a `phase_03_sobrecitos.py`
- `simulation/phase_02_wallets.py`: `total_needed_axg` → `total_needed_axf`
- `simulation/sim_types.py`: `max_boosters`, `boosters_normal`, `boosters_foil` → actualizar
- `simulation/runner.py`: actualizar imports y referencias

---

## Fase 3: Frontend

### 3.1 Variables internas y tipos (NO UI strings — ya están correctos en su mayoría)

**`frontend/types/store.ts`:**
- `price_axg?` → `price_axf?`
- `price_gal?` → `price_frj?`
- `gal_rewarded?` → `frj_rewarded?`

**`frontend/types/vip.ts`:**
- `vip_pending_gal` → `vip_pending_frj`
- `pending_gal_expires_at` → `pending_frj_expires_at`
- `welcome_gal?` → `welcome_frj?`
- `claimed_gal?` → `claimed_frj?`

**`frontend/types/inventory.ts`:**
- `hourly_yield_gal` → `hourly_yield_frj`
- `accrued_staking_gal` → `accrued_staking_frj`
- `rent_fee_gal?` → `rent_fee_frj?`
- `cost_gal` → `cost_frj`
- `current_gal` → `current_frj`

### 3.2 Componentes

Actualizar TODAS las variables internas, props, y estados que usen `_gal`, `_axg`, `_boosters`:
- `CryptoCheckout.tsx`: `axg_base` → `axf_base`, `axg_total` → `axf_total`, `axg_amount` → `axf_amount`
- `Inventory.tsx`, `ItemList.tsx`: `sealedBoosters` → `sealedSobrecitos`, `boostersSheetOpen` → `sobrecitosOpen`
- `Santuario.tsx`: `price_axg` → `price_axf`, `price_gal` → `price_frj`, `axg_multiplier` → `axf_multiplier`, `gal_multiplier` → `frj_multiplier`, `booster_chance_bonus` → `sobrecito_chance_bonus`
- `PlayMode.tsx`: `budget_gal` → `budget_frj`, `refunded_gal` → `refunded_frj`
- `MarketP2P.tsx`, `RentalMarket.tsx`: `rent_fee_gal` → `rent_fee_frj`, `sale_price_gal` → `sale_price_frj`, `price_gal` → `price_frj`
- `ManualModeButton.tsx`: `bonus_gal_on_win` → `bonus_frj_on_win`
- `MultiplayerLobby.tsx`: `budget_gal` → `budget_frj`
- `ToastContext.tsx`: `gross_gal` → `gross_frj`, `net_gal` → `net_frj`, `gross_prize_gal` → `gross_prize_frj`, `claimed_gal` → `claimed_frj`
- Pantallas: `CpuSimScreen`, `PlayingScreen`, `GameScreen`, `SettlingScreen`, `AxoSelectScreen`, `BudgetScreen`
- Admin: `AdminEconomyCharts`, `AdminOverview`, `AdminPlayerDetail`, `AdminSimReport`
- Gashapon: `result.type === 'gal'` → `result.type === 'frj'`
- VIP: `ModeB.tsx`, `ModeA.tsx`
- F2P: `AwakeAxoSpectator.tsx`
- Store: `OfficialTab.tsx`

### 3.3 Hooks y servicios

- `useCpuGame.ts`: `bot_budget_axg` → `bot_budget_axf`, `bot_loss_limit_axg` → `bot_loss_limit_axf`, `bot_profit_limit_axg` → `bot_profit_limit_axf`, `prize_gal` → `prize_frj`
- `useVip.ts`: `welcome_gal` → `welcome_frj`, `claimed_gal` → `claimed_frj`
- `useInventory.ts`: `boostersSheetOpen` → `sobrecitosSheetOpen`, `sealedBoosters` → `sealedSobrecitos`, `accrued_staking_gal` → `accrued_staking_frj`
- `useBlockchainEvents.ts`: `GEMA_ALGA_EVENTS` → `FRIJOLITO_EVENTS`, `CONTRACT_ADDRESSES.GEMA_ALGA` → `CONTRACT_ADDRESSES.FRIJOLITO`
- `vipService.ts`: URL `claim-daily-gal` → verificar si el endpoint también cambia
- `inventoryService.ts`: `price_gal` → `price_frj`, `rent_fee_gal` → `rent_fee_frj`

### 3.4 Archivos core

- `lib/abis.ts`: `GEMA_ALGA_EVENTS` → `FRIJOLITO_EVENTS`
- `lib/blockchain.ts`: `GEMA_ALGA` → `FRIJOLITO`, `AXOGEMA` → `AXOFICHA` en CONTRACT_ADDRESSES
- `lib/vip.ts`: `welcome_boosters` → `welcome_sobrecitos`

---

## Fase 4: Wiki

### Actualizar (player-facing):
- `wiki/jugadores/tienda.md`: "Boosters" → "Sobrecitos"
- `wiki/jugadores/vip.md`: "Booster" → "Sobrecito"
- `wiki/jugadores/gashapon.md`: "Sobre (booster)" → "Sobrecito"
- `wiki/jugadores/multijugador.md`: revisar referencias

### Actualizar (técnico):
- `wiki/economia/monedas.md`: actualizar sección de nombres legacy
- `wiki/economia/tablas_precios.md`: actualizar nombres
- `wiki/arquitectura/contratos.md`: actualizar referencias a contratos
- `wiki/arquitectura/backend.md`: actualizar referencias
- `wiki/arquitectura/frontend.md`: actualizar referencias
- `wiki/arquitectura/base_de_datos.md`: notar columnas legacy
- `wiki/api/banco_y_economia.md`: actualizar campos alias
- `wiki/api/usuarios_y_perfil.md`: actualizar nombres de campos
- `wiki/api/juego_y_multijugador.md`: actualizar
- `wiki/00-INDEX.md`: actualizar referencias

### NO tocar:
- `wiki/ai/gotchas.md` — documenta el doble naming intencionalmente

---

## Fase 5: Agentes y Config

### `.claude/agents/`:
- `game-designer.md`: actualizar tablas de economía con nuevos nombres
- `economy-analyst.md`: actualizar ejemplos y referencias AXG→AXF, GAL→FRJ
- `contrato-dev.md`: actualizar nombres de contratos
- `qa-tester.md`: actualizar escenarios de prueba
- `frontend-dev.md`: actualizar env var references
- `backend-dev.md`: actualizar referencias

### `tools/taskboard/`:
- `project_context.py`: actualizar referencias documentadas
- `mcp_knowledge_server.py`: actualizar knowledge base
- `.context_cache/axolotto.txt`: regenerar cache

### Root:
- `CLAUDE.md`: ya está actualizado — verificar consistencia
- `docs/MASTER_PLAN_CRIADERO.md`: actualizar referencias si aplica
- `docs/000_PLAN_GLOBAL_PENDIENTES.md`: actualizar referencias

---

## Verificación

1. **Build de contratos**: `forge build` en `contracts/` sin errores
2. **Deploy local**: `forge script script/Deploy.s.sol --rpc-url http://localhost:8545` muestra nombres nuevos
3. **Backend tests**: `pytest backend/tests/ -x` todos pasan
4. **Frontend build**: `cd frontend && npm run build` sin errores de TypeScript
5. **Frontend runtime**: la UI sigue mostrando "AXF" y "FRJ" correctamente (ya lo hace en muchos lugares)
6. **Taskboard**: `.\tools\taskboard\bin\taskboard.ps1 list` no muestra errores

---

## Orden de implementación recomendado

1. Contratos (GameController.sol, Boosters.sol, Deploy.s.sol)
2. Backend services (web3_service.py primero — es la base)
3. Backend models y endpoints
4. Backend tests
5. Backend scripts
6. Frontend types (base para todo lo demás)
7. Frontend components y hooks
8. Wiki
9. Agentes y config
10. Verificación final end-to-end
