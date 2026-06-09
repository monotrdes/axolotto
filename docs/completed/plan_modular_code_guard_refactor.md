# Plan de Refactoring — Modular Code Guard

> Generado: 2026-06-04. Base: auditoría de `modular-code-guard` sobre todo el codebase.
> Objetivo: eliminar God Components, God Endpoints, y capas mezcladas. Sin romper comportamiento.

---

## Resumen de violaciones

| Severidad | Archivos | Criterio |
|---|---|---|
| CRÍTICO | 5 | 1500+ líneas |
| FUERTE | 10 | 800–1500 líneas |
| CONSIDERAR | 6 | 400–800 líneas con mezcla de responsabilidades |
| ESTRUCTURAL | — | Faltan `frontend/services/`, `frontend/types/`, `frontend/hooks/` como dirs propios |

---

## Fase 0 — Limpieza inmediata (sin riesgo)

### 0.1 Eliminar `Inventory_.tsx` (draft muerto)
- **Archivo:** `frontend/components/Inventory_.tsx` (2051 líneas)
- **Acción:** Confirmar que ningún import lo usa, luego `git rm`.
- **Verificación:** `grep -r "Inventory_" frontend/`

### 0.2 Crear directorios de separación faltantes
```bash
mkdir -p frontend/services
mkdir -p frontend/types
mkdir -p frontend/hooks   # los hooks actuales están sueltos en components/
```
- Mover hooks sueltos de `components/`:
  - `components/useBlockchainEvents.ts` → `hooks/useBlockchainEvents.ts`
  - `components/useEconomyToast.ts` → `hooks/useEconomyToast.ts`
  - `components/useMoonPayWidget.ts` → `hooks/useMoonPayWidget.ts`
  - `components/useTabVisibility.ts` → `hooks/useTabVisibility.ts`
- Actualizar imports en todos los archivos que los consumen.
- Verificación: `tsc --noEmit`

---

## Fase 1 — Frontend: God Components (CRÍTICO)

### Orden de extracción: tipos → constantes → utils → API calls → hooks → sub-componentes

### 1.1 `frontend/components/Santuario.tsx` (2208 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `frontend/types/santuario.ts` | `SpotType`, `SpotSlot`, `SelectedSlot`, `AxoPos`, `CaveItem`, `CaveData`, `InventoryItem`, interfaces inline |
| `frontend/constants/santuario.ts` | `traitNames`, `statNames`, `statColors` |
| `frontend/utils/santuario.ts` | `formatCooldown`, `obtenerEstiloHuevo`, `formatTiempoEscudo`, `getFrostPhase`, `obtenerFaseHuevo` |
| `frontend/services/santuarioService.ts` | Todas las llamadas `axios.post/get` al API (feed, sleep, set-main, cave equip, etc.) |
| `frontend/hooks/useSantuario.ts` | Estado principal del componente + efectos de carga de datos |
| `frontend/components/santuario/WeatherChip.tsx` | Componente `WeatherChip` |
| `frontend/components/santuario/NidoScene.tsx` | Componente `NidoScene` |
| `frontend/components/santuario/EggSheet.tsx` | Componente `EggSheet` |
| `frontend/components/santuario/SpotFluido.tsx` | Componente `SpotFluidoProps` |
| `frontend/components/santuario/CaveRoomModal.tsx` | Componente `CaveRoomModal` |
| `frontend/components/Santuario.tsx` | Queda como thin container que compone los de arriba |

**Meta de líneas post-refactor:** `Santuario.tsx` < 150 líneas.

### 1.2 `frontend/components/Inventory.tsx` (1994 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `frontend/types/inventory.ts` | Interfaces de items, axolotitos, cartas |
| `frontend/services/inventoryService.ts` | Llamadas axios a `/auth/inventory`, `/shop/cards`, etc. |
| `frontend/hooks/useInventory.ts` | useState + useEffect de carga, filtros, paginación |
| `frontend/components/inventory/CardGrid.tsx` | Grid de cartas |
| `frontend/components/inventory/AxolotitoCard.tsx` | Tarjeta individual de axolotito |
| `frontend/components/inventory/ItemList.tsx` | Lista de items consumibles |
| `frontend/components/Inventory.tsx` | Thin container |

### 1.3 `frontend/components/Store.tsx` (1650 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `frontend/types/store.ts` | Tipos de items, packs, estado de unboxing |
| `frontend/services/storeService.ts` | axios calls a `/shop/items`, `/shop/buy`, `/shop/gashapon`, etc. |
| `frontend/hooks/useStore.ts` | 30+ useState colapsados en hook reutilizable |
| `frontend/hooks/useUnboxing.ts` | Máquina de estado `pack → opening → reveal → summary` |
| `frontend/components/store/OfficialTab.tsx` | Tab de tienda oficial |
| `frontend/components/store/MarketTab.tsx` | Tab de mercado |
| `frontend/components/store/UnboxingFlow.tsx` | Flujo de apertura de packs |
| `frontend/components/Store.tsx` | Thin container con tabs |

### 1.4 `frontend/components/VipModal.tsx` (1347 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `frontend/types/vip.ts` | Tipos de tiers, stats VIP |
| `frontend/services/vipService.ts` | 27 llamadas axios |
| `frontend/hooks/useVip.ts` | Estado VIP, upgrade preview, polling |
| `frontend/components/vip/TierCard.tsx` | Tarjeta de tier individual |
| `frontend/components/vip/UpgradePanel.tsx` | Panel de upgrade |
| `frontend/components/VipModal.tsx` | Thin modal container |

---

## Fase 2 — Frontend: God Page

### 2.1 `frontend/app/play/page.tsx` (873 líneas, 41 hits de state/fetch)

God page — página que debería solo componer módulos.

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `frontend/services/playService.ts` | Todas las llamadas fetch/axios desde la página |
| `frontend/hooks/usePlaySession.ts` | Estado de sesión de juego, WebSocket, timers |
| `frontend/hooks/useGameRoom.ts` | Estado de sala, jugadores, turno |
| `frontend/components/play/GameHeader.tsx` | Header del juego |
| `frontend/components/play/PlayerPanel.tsx` | Panel de jugador |
| `frontend/app/play/page.tsx` | Solo compone componentes, sin fetch inline |

---

## Fase 3 — Backend: God Endpoints (lógica en endpoints, no en servicios)

Regla: los archivos en `api/v1/endpoints/` deben solo rutear y validar. La lógica va en `services/`.

### 3.1 `backend/app/api/v1/endpoints/board.py` (1235 líneas)

Funciones a mover a `backend/app/services/board_service.py` (ya existe parcialmente):

- `get_board_hourly_rate`, `get_accrued_staking`, `get_board_csr` → `board_service.py`
- `_deduct_staked_cards`, `_return_staked_cards`, `validate_card_availability` → `board_service.py`
- `get_slot_requirements` → `board_service.py`
- Lógica de rental market (`list_board_for_rent`, `rent_board`, `buy_board`) → `board_service.py` o nuevo `rental_service.py`
- Endpoint handlers quedan como thin wrappers que llaman al servicio.

### 3.2 `backend/app/api/v1/endpoints/shop.py` (1234 líneas)

Funciones a mover a `backend/app/services/shop_service.py`:

- `_add_to_inventory`, `_get_astral_egg`, `_get_foil_booster` → ya pertenecen al service
- `_try_legendary_drop`, `_try_tabla_forjada_drop` → `drop_service.py`
- `_roll_capsule`, `_daily_can_claim` → `capsule_service.py`
- VIP logic (`get_vip_tiers`, `get_vip_stats`, `vip_upgrade_preview`) → `vip_service.py`
- Forge/melt logic → `forge_service.py`

### 3.3 `backend/app/api/v1/endpoints/game.py` (956 líneas)

- `check_loterica_line`, `get_winning_line`, `_lucky_save` → `game_logic.py` (utils puros)
- `_ensure_npc_pool`, `_spawn_npc_replacement` → `npc_service.py`
- `_apply_imprinting_if_needed` → `incubation_service.py`
- `play_match` (la función más grande) → `multiplayer_service.py` o `game_service.py`
- Cave management (`get_cave`, `equip_cave_item`, `unequip_cave_item`) → `cave_service.py`

### 3.4 `backend/app/api/v1/endpoints/admin.py` (939 líneas)

- Crear `backend/app/services/admin_service.py`
- Mover toda lógica de negocio admin al service
- Endpoint queda con solo validación + llamada al service

### 3.5 `backend/app/api/v1/endpoints/user.py` (908 líneas)

- Crear `backend/app/services/user_service.py` (si no existe)
- Mover lógica de usuario al service

---

## Fase 4 — Tools: Taskboard (God Handler)

### 4.1 `tools/taskboard/routes.py` (1167 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `tools/taskboard/handlers/task_handler.py` | Lógica de tareas |
| `tools/taskboard/handlers/agent_handler.py` | Lógica de agentes |
| `tools/taskboard/handlers/usage_handler.py` | Lógica de usage/stats |
| `tools/taskboard/server.py` | Solo `ThreadingHTTPServer`, `run_server()` |
| `tools/taskboard/routes.py` | Solo dispatch de rutas |

### 4.2 `tools/taskboard/ai_router.py` (959 líneas)

**Qué extraer:**

| Destino | Contenido |
|---|---|
| `tools/taskboard/providers/base.py` | Clase abstracta `AIProvider` |
| `tools/taskboard/providers/claude.py` | `ClaudeProvider` |
| `tools/taskboard/providers/deepclaude.py` | `DeepClaudeProvider` |
| `tools/taskboard/rate_limiter.py` | `RateLimitTracker` |
| `tools/taskboard/ai_router.py` | Solo `AIRouter` y factories |

---

## Fase 5 — Backend: Servicios largos (400–800 líneas)

### 5.1 `backend/app/services/shop_service.py` (746 líneas)
- Separar lógica de drops en `drop_service.py`
- Separar lógica de capsulas en `capsule_service.py`

### 5.2 `backend/app/services/web3_service.py` (637 líneas)
- Separar por contrato: `web3_axolotitos.py`, `web3_cartas.py`, `web3_tablas.py`
- `web3_service.py` queda como facade

### 5.3 `backend/app/api/v1/endpoints/multiplayer.py` (742 líneas)
- Mover lógica de sala a `multiplayer_service.py` (ya existe)
- Endpoint queda thin

---

## Checklist de ejecución

```
Fase 0
[ ] Confirmar que Inventory_.tsx no tiene imports activos
[ ] git rm frontend/components/Inventory_.tsx
[ ] Crear frontend/services/ frontend/types/ frontend/hooks/
[ ] Mover 4 hooks de components/ a hooks/
[ ] Actualizar imports, verificar con tsc --noEmit

Fase 1 — God Components frontend
[ ] 1.1 Santuario.tsx: extraer tipos
[ ] 1.1 Santuario.tsx: extraer constantes + utils
[ ] 1.1 Santuario.tsx: extraer servicio API
[ ] 1.1 Santuario.tsx: extraer hook principal
[ ] 1.1 Santuario.tsx: extraer sub-componentes (5)
[ ] 1.2 Inventory.tsx: mismo patrón
[ ] 1.3 Store.tsx: mismo patrón + hook de unboxing
[ ] 1.4 VipModal.tsx: mismo patrón

Fase 2 — God Page
[ ] 2.1 play/page.tsx: extraer playService
[ ] 2.1 play/page.tsx: extraer usePlaySession + useGameRoom
[ ] 2.1 play/page.tsx: extraer sub-componentes

Fase 3 — God Endpoints backend
[ ] 3.1 board.py: mover lógica a board_service.py
[ ] 3.2 shop.py: crear drop_service, capsule_service, vip_service, forge_service
[ ] 3.3 game.py: crear game_logic utils + cave_service + mover a multiplayer_service
[ ] 3.4 admin.py: crear admin_service.py
[ ] 3.5 user.py: crear user_service.py

Fase 4 — Taskboard
[ ] 4.1 routes.py: extraer handlers por dominio
[ ] 4.2 ai_router.py: extraer providers + rate_limiter

Fase 5 — Servicios largos
[ ] 5.1 shop_service.py: separar drops y capsulas
[ ] 5.2 web3_service.py: separar por contrato
[ ] 5.3 multiplayer.py endpoint: mover lógica al service
```

---

## Reglas para ejecutar el refactor

1. **Una responsabilidad por PR.** No mezclar extracción de tipos con extracción de servicios.
2. **Mover sin editar lógica.** Si hay un bug, fix va en PR separado.
3. **Verificar imports después de cada extracción** (`tsc --noEmit` en frontend, `python -m pytest` en backend).
4. **Barrel exports** (`index.ts`) en carpetas nuevas para no romper call sites masivamente.
5. **No crear carpetas vacías.** Solo crear cuando se mueve código real.
6. **Target de líneas** por archivo post-refactor:
   - Componente React: < 300 líneas
   - Page file: < 150 líneas (solo composición)
   - Endpoint Python: < 200 líneas
   - Servicio Python: < 400 líneas
   - Hook: < 150 líneas
   - Servicio frontend: < 200 líneas
