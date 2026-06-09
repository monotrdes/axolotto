# Plan de Implementacion: Rediseno del Flujo Multijugador
## Arquitectura Unificada + Multiagentes

**Task:** task-1780814344-31
**Fecha:** 2026-06-07
**Estado:** planning → doing (revision 2 — arquitectura unificada)

---

## Principio Rector: One GameView, Three Control Modes

La Loteria es fundamentalmente el mismo juego en los 3 modos:
- Tablero 4x4 con cartas
- Cartas cantadas una por una (el "Griton")
- Marcar celdas que coinciden
- Ganar al completar linea/cuadrito/tablero lleno
- Tension creciente conforme avanza la partida

**Lo UNICO que cambia es QUIEN controla el marcado y COMO llega el stream de cartas:**

| Aspecto | CPU Mode | Auto Mode (AFK) | Manual Mode |
|---------|----------|-----------------|-------------|
| Quien marca | Bot (backend pre-calcula) | Bot con escrow (backend simula) | **El jugador** (taps en pantalla) |
| Stream de cartas | Resultado pre-calculado (1 sola llamada) | Polling cada 2s a `/game-state` | **WebSocket** en tiempo real |
| Interaccion | Solo observar | Observar + recall button | **Tappear + gritar Loteria** |
| Velocidad | Animacion fija (1200ms/tick) | Animacion interpolada | Ritmo del servidor (griton_delay_ms) |
| Escrow | No (pago por partida) | Si (presupuesto en custodia) | Si (buy-in en custodia) |

### Arquitectura Resultante

```
┌─────────────────────────────────────────────────────────┐
│                    GameScreen (UNIFICADO)                │
│  Props: boards, players, phase, tension, mode, config   │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ GritonBanner      ← "El Luchador #12" + timer     │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ BoardGrid         ← 4x4 tablero(s) del jugador    │  │
│  │ (interactive=true solo si mode='manual')          │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ OpponentStrip     ← mini-tableros de bots/oponentes│  │
│  ├───────────────────────────────────────────────────┤  │
│  │ AxoAvatar         ← reacciona a eventos del juego │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ TensionEffects    ← heartbeat, niebla, destellos  │  │
│  ├───────────────────────────────────────────────────┤  │
│  │ ActionBar         ← [💡 Pista] [📣 LOTERIA!]       │  │
│  │ (visible solo si mode='manual')                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           ▲              ▲              ▲
           │              │              │
    useCpuGame      useAutoGame    useManualGame
    (fetch once,    (poll 2s,      (WebSocket,
     replay anim)    interpolate)   real-time)
```

### Beneficios de esta arquitectura

1. **DRY**: Todos los modos comparten GritonBanner, BoardGrid, OpponentStrip, TensionEffects, AxoAvatar
2. **Mantenible**: Un cambio visual (ej. nuevo efecto de tension) aplica a los 3 modos
3. **Consistente**: El jugador ve la misma experiencia visual en CPU/Auto/Manual
4. **Testeable**: GameScreen se puede probar con props mock sin WebSocket ni backend
5. **Extensible**: Un futuro modo "Torneo" solo necesita otro hook, no otra pantalla

---

## Diagnostico Actual (sin cambios)

- **Auto Mode**: `PlayingScreen.tsx` es un dashboard estatico (balance + barra). CERO visor en vivo.
- **Manual Mode**: `manual_game_service.py` tiene los calculos de entorno pero no hay juego real: sin WebSocket, sin sorteo, sin validacion.
- **CPU Mode**: `CpuSimScreen.tsx` tiene tick-by-tick animation excelente — es la base para unificar.
- **WebSocket**: No existe en backend ni frontend.
- **BoardGrid**: `BoardCardGrid.tsx` es solo display, no acepta interaccion.
- **Moneda**: `gemas_alga` (FRJ) ya se usa en multiplayer. Falta blindaje explicito anti-AXF.

---

## FASE 1: Backend — Fundacion y WebSocket

### 1.1 `check_tension_status` (game_logic.py)
Funcion pura que evalua el estado de tension de cualquier partida:
- Input: lista de tableros con sus `marked_indices`, historial de cartas cantadas
- Output: `TensionStatus { level, near_win_players, hot_lines }`
- Usada por: CPU sim (modular velocidad), Auto (modular polling), Manual (broadcast WebSocket)

### 1.2 Blindaje FRJ-Only (bank_service.py + multiplayer.py)
- Constante `MULTIPLAYER_CURRENCY = CurrencyType.FRIJOLITO`
- Validacion: `/register` y `/join-room` usan `wallet.frijolitos` (nunca `axofichas`)
- Nuevo campo `currency_type` en `GameRoom` (default `"frijolito"`)
- Guard en `BankService.assert_multijugador_currency()` — lanza 403 si toca AXF
- Migracion: sincronizar `frijolitos` = `gemas_alga` para cuentas legacy

### 1.3 Hard-cap: 2 Salas Oficiales (multiplayer_service.py)
- `rookie` → `rookie_pool`, `champion` → `champion_abyss`
- `get_or_create_waiting_room()` garantiza max 1 sala `waiting` por tipo
- Player-hosted rooms sin cambios

### 1.4 WebSocket Endpoint (NUEVO `api/v1/ws/game_ws.py`)
```
WS /api/v1/ws/game/{room_id}?token=<jwt>&mode=manual
```
Ciclo de vida: handshake JWT → lobby → countdown → juego → resultado

**Mensajes Server→Client:**
```json
{"type":"card_called","card_id":12,"numero":12,"name":"El Luchador","timestamp_ms":1718...,"window_ms":2400}
{"type":"tension_update","level":"high","near_win":[42,17],"hot_lines":[...]}
{"type":"loteria_validated","player_axo_id":42,"win_type":"line","cells":[0,1,2,3],"payout_frj":150}
{"type":"game_start","room_id":1,"players":[...],"speed_ms":2000}
{"type":"game_end","winner_axo_id":42,"payout_frj":150}
{"type":"hint_activated","cell_indices":[3,7,11]}
```

**Mensajes Client→Server:**
```json
{"type":"mark_cell","cell_index":7}
{"type":"shout_loteria"}
{"type":"use_hint"}
```

### 1.5 WS Manager (NUEVO `services/ws_manager.py`)
```python
class GameWSManager:
    active_games: Dict[int, GameSession]  # room_id → session
    connections: Dict[int, Dict[str, WebSocket]]
    
    async def broadcast(room_id, msg)
    async def handle_card_cycle(room_id)      # el Griton
    async def validate_loteria(room_id, uid)  # first-wins por timestamp
    async def start_game(room_id)
    async def handle_disconnect(room_id, uid) # mantiene estado 30s
```

### 1.6 Manual Game Service (extender `manual_game_service.py`)
- `run_card_cycle()` — baraja mazo, itera con `griton_delay_ms`, checkea tension
- `validate_loteria_shout()` — verifica celdas marcadas vs cartas cantadas
- `apply_stat_effects()` — Focus→window, Agility→delay, Luck→crit, Salinity→fog, Stamina→hints
- `compute_payout()` — calcula premio basado en win_type, luck crit, VIP bonus

### 1.7 Game State para Auto (multiplayer.py + lobby_models.py)
- Endpoint `GET /game-state/{axolotito_id}` devuelve snapshot de la partida en curso
- Modelo `ActiveGameState` — room_id, cards_drawn_json, player_states_json, turns_played
- `simulate_multiplayer_match()` escribe a `ActiveGameState` cada tick en vez de correr ciego

---

## FASE 2: Frontend — GameScreen Unificado

### 2.1 `GameScreen.tsx` (NUEVO — reemplaza CpuSimScreen + PlayingScreen + futuro ManualGameScreen)
**Archivo:** `frontend/components/screens/GameScreen.tsx`

Props:
```typescript
interface GameScreenProps {
  mode: 'cpu' | 'auto' | 'manual';
  playerBoards: PlayerBoardState[];     // 1-3 tableros del jugador
  opponentBoards: OpponentBoardState[]; // bots u otros jugadores
  allCards: Card[];                     // catalogo completo para resolver nombres/emoji
  phase: 'loading' | 'countdown' | 'playing' | 'result';
  tension: TensionStatus | null;
  currentCard: CalledCard | null;       // carta cantada actual + ventana
  onCellTap?: (boardIdx: number, cellIdx: number) => void;  // solo manual
  onShoutLoteria?: () => void;                               // solo manual
  onUseHint?: () => void;                                    // solo manual
  hintsRemaining?: number;                                   // solo manual
  showActionBar?: boolean;                                   // solo manual
  // Result
  result?: GameResult;
  onPlayAgain?: () => void;
  onChangeBoard?: () => void;
  onChangeAll?: () => void;
  // Auto-specific
  escrowBalance?: number;
  initialBudget?: number;
  onRecall?: () => void;
}
```

El componente renderiza condicionalmente basado en `mode`:
- `mode='cpu'` → ActionBar oculto, board no interactivo, animacion fija
- `mode='auto'` → ActionBar oculto, board no interactivo, escrow bar visible, recall button
- `mode='manual'` → ActionBar visible (hints + Loteria button), board interactivo

### 2.2 Hooks por Modo

#### `useCpuGame.ts` (NUEVO — extrae logica de CpuSimScreen)
```typescript
function useCpuGame(axo, boardId, room, token) {
  // 1. POST /game/play → obtiene resultado pre-calculado
  // 2. Replay tick-by-tick con setTimeout chain (TICK_MS)
  // 3. Retorna: { phase, boards, opponents, currentCard, tension, result }
}
```

#### `useAutoGame.ts` (NUEVO)
```typescript
function useAutoGame(axoId, token) {
  // 1. GET /game-state/{axoId} cada 2s
  // 2. Interpola linear entre snapshots para animacion fluida
  // 3. Retorna: { phase, boards, opponents, currentCard, tension, escrowBalance }
}
```

#### `useManualGame.ts` (NUEVO)
```typescript
function useManualGame(roomId, axoId, token) {
  // 1. new WebSocket(`ws://.../game/${roomId}`)
  // 2. Maneja mensajes: card_called, tension_update, game_start, game_end
  // 3. Envia: mark_cell, shout_loteria, use_hint
  // 4. Retorna: { phase, boards, opponents, currentCard, tension, sendMark, sendShout, sendHint }
}
```

#### `useWebSocket.ts` (NUEVO — hook generico)
```typescript
function useWebSocket<T>(url: string, handlers: Record<string, (data: any) => void>) {
  // Connect, reconnect (exponential backoff), heartbeat, cleanup
  // Retorna: { send, readyState, lastMessage }
}
```

### 2.3 Sub-componentes Compartidos

#### `GritonBanner.tsx` (NUEVO)
Muestra la carta cantada actual con:
- Imagen/emoji grande de la carta
- Numero y nombre
- Barra de tiempo restante de la ventana (se vacia en `window_ms`)
- Animacion de entrada: slide-up + glow
- En modo manual: la barra es roja cuando quedan <30% del tiempo

#### `BoardGrid.tsx` (EXTENDER `BoardCardGrid.tsx`)
Anadir soporte para interactividad:
- Nueva prop `interactive?: boolean`
- Nueva prop `highlightedCell?: number` — la celda que el jugador deberia marcar
- Nueva prop `onCellTap?: (idx: number) => void`
- Estados visuales adicionales:
  - `highlighted`: borde dorado pulsante (carta cantada que esta en el tablero)
  - `salinity_fog`: blur+sal cuando salinity la oculta
  - `crit_ready`: mini-destello en celdas donde aplica critico

#### `OpponentStrip.tsx` (NUEVO)
Strip horizontal de mini-tableros de oponentes:
- Cada oponente: miniatura del tablero + nombre + barra de progreso
- En CPU/Auto: bots con nivel de amenaza (cpuThreat)
- En Manual: jugadores reales con avatar + nombre
- Layout responsivo: scroll horizontal en mobile, grid en desktop

#### `TensionEffects.tsx` (NUEVO)
Overlay de efectos visuales basado en `tension_level`:
- `low` → nada
- `medium` → bordes del tablero ligeramente pulsantes
- `high` → heartbeat animation en el contenedor principal
- `critical` → heartbeat + vignette rojo + sonido (si esta permitido)

#### `AxoAvatar.tsx` (NUEVO)
Avatar del Axolotito que reacciona a eventos:
- `idle` → animacion `animate-axo-bob` suave
- `card_called` → mirada hacia la carta (rotate)
- `cell_marked` → mini bounce + chispas
- `cell_missed` → shake + sudor
- `tension_critical` → respiracion agitada (scale pulse)
- `won` → salto + sparkles + confetti
- `lost` → se desmaya (rotate + fade)

### 2.4 Integracion en PlayMode.tsx

El Wizard actual se simplifica — en lugar de 8 vistas, ahora son 5 + GameScreen:

```
axo-select → mode-select → board-select → budget → sala-select
                                                      │
                                              ┌───────┴───────┐
                                              ▼               ▼
                                         GameScreen       GameScreen
                                         (mode='cpu')    (mode='auto' o 'manual')
```

Cambios en `GameView`:
```typescript
type GameView =
  | 'axo-select'
  | 'mode-select'
  | 'board-select'
  | 'budget'
  | 'sala-select'
  | 'game';  // UNIFICADO — el modo lo determina gameMode + subMode
```

Se eliminan: `'cpu-sim'`, `'playing'`, `'settling'` como vistas separadas. El componente `GameScreen` maneja internamente el resultado y settlement.

---

## FASE 3: Contratos

### 3.1 GameController — Bloqueo AXF + Eventos Manual
**Archivo:** `contracts/src/GameController.sol`

```solidity
modifier onlyFRJ() {
    require(msg.value == 0, "GameController: AXF no aceptado en multijugador");
    _;
}

event ManualGameStarted(uint256 indexed roomId, uint256 timestamp);
event CardCalled(uint256 indexed roomId, uint8 cardNumber, uint256 timestamp);
event LoteriaShouted(uint256 indexed roomId, address player, uint256 axolotitoId, bool valid);
event ManualGameEnded(uint256 indexed roomId, address winner, uint256 payout);
```

### 3.2 TablasLoteria — Sin cambios criticos
El escrow de cartas ya funciona correctamente.

---

## FASE 4: Testing

### 4.1 Backend
- `tests/test_tension_status.py` — unit test puro (sin DB)
- `tests/test_game_ws.py` — WebSocket handshake + ciclo + validacion (pytest-asyncio)
- `tests/test_frj_enforcement.py` — verifica rechazo de AXF

### 4.2 Frontend
- `tests/e2e/cpu-game.spec.ts` — flujo CPU (ya existe, solo verificar que no se rompa)
- `tests/e2e/manual-game.spec.ts` — flujo manual con WebSocket mock
- `tests/e2e/auto-viewer.spec.ts` — visor auto con polling mock

### 4.3 GameScreen Unit Tests
- Renderiza en los 3 modos con props mock
- BoardGrid acepta taps solo en mode='manual'
- ActionBar visible solo en mode='manual'
- TensionEffects muestra heartbeat en critical

---

## Resumen de Archivos

### Backend (11 archivos)
| Archivo | Cambio |
|---------|--------|
| `backend/app/api/v1/ws/game_ws.py` | **NUEVO** — WebSocket endpoint unico para modo manual |
| `backend/app/services/ws_manager.py` | **NUEVO** — Connection manager + game sessions |
| `backend/app/services/game_logic.py` | Anadir `check_tension_status()`, `validate_win()` |
| `backend/app/services/manual_game_service.py` | Extender — ciclo de cartas, validacion Loteria, efectos stats |
| `backend/app/services/multiplayer_service.py` | Modificar — escribir ActiveGameState cada tick, exponer estado |
| `backend/app/api/v1/endpoints/multiplayer.py` | Anadir `/game-state/{axo_id}`, `/register` acepta `play_mode` (auto/manual) |
| `backend/app/models/lobby_models.py` | Anadir `ActiveGameState`, `currency_type` en `GameRoom` |
| `backend/app/services/bank_service.py` | Anadir `assert_multijugador_currency()` |
| `backend/app/core/prices.py` | Actualizar fees a FRJ explicitos |
| `backend/app/main.py` | Montar WebSocket router |
| `backend/app/models/manual_mode_event.py` | Activar/Usar el modelo existente |

### Frontend (13 archivos)
| Archivo | Cambio |
|---------|--------|
| `frontend/components/screens/GameScreen.tsx` | **NUEVO** — Vista unificada para CPU/Auto/Manual |
| `frontend/hooks/useCpuGame.ts` | **NUEVO** — Logica extraida de CpuSimScreen |
| `frontend/hooks/useAutoGame.ts` | **NUEVO** — Polling + interpolacion para modo auto |
| `frontend/hooks/useManualGame.ts` | **NUEVO** — WebSocket + estado para modo manual |
| `frontend/hooks/useWebSocket.ts` | **NUEVO** — Hook generico de WebSocket |
| `frontend/components/ui/GritonBanner.tsx` | **NUEVO** — Carta cantada + timer |
| `frontend/components/ui/OpponentStrip.tsx` | **NUEVO** — Mini-tableros de oponentes |
| `frontend/components/ui/TensionEffects.tsx` | **NUEVO** — Heartbeat, niebla, destellos |
| `frontend/components/ui/AxoAvatar.tsx` | **NUEVO** — Avatar reactivo del axolotito |
| `frontend/components/ui/BoardCardGrid.tsx` | Extender — prop `interactive`, `highlightedCell`, `onCellTap` |
| `frontend/components/PlayMode.tsx` | Simplificar — 6 vistas en vez de 8, `'game'` unificada |
| `frontend/components/screens/SalaSelectScreen.tsx` | Anadir selector auto vs manual |
| `frontend/components/screens/CpuSimScreen.tsx` | Deprecar — su logica migra a `useCpuGame` + `GameScreen` |

### Contratos (1 archivo)
| Archivo | Cambio |
|---------|--------|
| `contracts/src/GameController.sol` | Modifier `onlyFRJ`, eventos modo manual |

---

## Estrategia de Implementacion con Multiagentes

El plan se divide en **5 workstreams independientes** que pueden ejecutarse en paralelo:

```
                    ┌─ WS1: Backend Core ─────────────┐
                    │  F1.1 tension_status             │
                    │  F1.2 blindaje FRJ-only          │
                    │  F1.3 hard-cap 2 salas           │
                    │  F1.7 game-state endpoint        │
                    │  backend-dev agent               │
                    ├──────────────────────────────────┤
                    │                                  │
  FASE 0 ──────────┤  WS2: Backend WebSocket ─────────┤──► Integration ──► Testing
  (setup)          │  F1.4 WebSocket endpoint          │
                    │  F1.5 WS manager                 │
                    │  F1.6 manual game service ext    │
                    │  backend-dev agent               │
                    ├──────────────────────────────────┤
                    │                                  │
                    └─ WS3: Frontend Unificado ────────┘
                       F2.1 GameScreen.tsx
                       F2.2 useCpuGame + useAutoGame
                       F2.3 useManualGame + useWebSocket
                       F2.4 GritonBanner, OpponentStrip
                       F2.5 TensionEffects, AxoAvatar
                       F2.6 BoardCardGrid interactivo
                       frontend-dev agent

  WS4: Contratos ────► F3.1 GameController ────────────► (independiente)
  (contrato-dev)

  WS5: PlayMode      ► F2.7 Integracion Wizard ─────────► (depende de WS3)
  (frontend-dev)
```

### Secuencia recomendada

1. **Fase 0 (setup)**: Crear rama `feature/multiplayer-redesign`, verificar que backend + frontend compilan
2. **WS1 + WS2 + WS4 en paralelo** (3 agentes simultaneos):
   - `backend-dev` → F1 completa (tension_status, FRJ-only, 2 salas, WebSocket, ws_manager)
   - `contrato-dev` → F3 completa (GameController)
3. **WS3** (depende de WS1+WS2 completados):
   - `frontend-dev` → F2 completa (GameScreen + hooks + sub-componentes)
4. **WS5** (depende de WS3):
   - `frontend-dev` → Integracion en PlayMode, deprecar CpuSimScreen/PlayingScreen
5. **Fase 4**: `qa-tester` → tests backend + frontend + E2E

### Workflow tool para cada workstream

Cada workstream usara `Workflow` con `pipeline()` para procesar archivos en paralelo dentro del stream. Ejemplo para WS1:

```javascript
export const meta = {
  name: 'ws1-backend-core',
  description: 'Backend foundation: tension_status, FRJ-only, 2 rooms, game-state',
  phases: [
    { title: 'Implement', detail: 'Implement each backend module' },
    { title: 'Verify', detail: 'Verify each module compiles and passes tests' },
  ]
}

phase('Implement')
const modules = await pipeline(
  ['tension_status', 'frj_blindaje', 'room_hardcap', 'game_state'],
  mod => agent(`Implement ${mod} in backend/app/services/game_logic.py ...`, {
    agentType: 'backend-dev'
  }),
  impl => agent(`Verify ${impl.file} compiles and logic is correct`, {
    agentType: 'backend-dev'
  })
)
```

---

## Riesgos y Mitigaciones

1. **Latencia WebSocket en Windows** → Configurar `ws_ping_interval=15` en uvicorn, heartbeats cada 15s
2. **Race condition Loteria** → Backend resuelve first-wins por timestamp de mensaje WebSocket
3. **Desconexion manual** → WS manager mantiene estado 30s, permite reconnect con `reconnect_token`
4. **Compatibilidad mobile** → `BoardCardGrid` usa `onPointerDown` + `onClick`
5. **Regresion CPU mode** → `useCpuGame` extrae la logica existente de `CpuSimScreen` sin cambiarla; tests E2E confirman
6. **Complejidad de unificacion** → GameScreen usa composicion, no herencia; cada modo es una configuracion de props

---

## Estados del Axolotito

| Estado | Significado | Usado en |
|--------|------------|----------|
| `idle` | Disponible | Todos |
| `playing` | En sala auto (AFK) | Auto |
| `playing_manual` | En sala manual interactiva | Manual |
| `waiting_settlement` | Listo para corte de caja | Auto, Manual |
| `sleeping` | Descansando | Todos |
