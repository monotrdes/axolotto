# Plan: Tableros NPC Reales para Bots CPU → Gashapon Legendario

## Problema raíz del bug actual

`CpuSimScreen.tsx` usa `fakeCpuBoard()` (números aleatorios 1-54). El backend usa tableros generados fresh por partida (`_rng.sample(all_card_ids, 16)`). Nunca coinciden. El frontend no puede reproducir fielmente la victoria CPU, generando el bug: "CPU gana con carta no cantada".

**Fix definitivo:** Backend usa tableros persistidos reales. Frontend recibe esos mismos números. Ambos lados alineados → bug imposible.

---

## Arquitectura: Tableros NPC del Sistema

### Usuario NPC del sistema

`PlayerBoard` requiere `user_id`. Solución sin cambio de schema: un usuario especial.

```
privy_did = "npc_axolotto_system"
email     = null
wallet    = null
```

No puede autenticarse, no tiene wallet, es solo propietario de tableros del sistema.

### Campos nuevos en `PlayerBoard`

```python
is_npc_pool:  bool           = False   # pertenece al pool de bots
npc_room:     Optional[str]  = None    # "rookie" | "champion"
npc_retired:  bool           = False   # graduado, esperando en reserva para gashapon
```

Una migración Alembic.

### Pool inicial (script seed)

| Pool | Cantidad | Room | Notas |
|------|----------|------|-------|
| Rookie pool | 20 tableros | rookie | cartas variadas del catálogo |
| Champion pool | 20 tableros | champion | cartas de mayor rareza si aplica |

Los tableros se crean con cartas del catálogo (sin descontar inventario — es el NPC).

---

## Flujo del juego CPU con tableros reales

### Backend `game.py` — cambios en `play_match()`

```python
# ANTES:
opponents_boards = [_rng.sample(all_card_ids, 16) for _ in range(bot_count)]

# DESPUÉS:
npc_room = "rookie" if room_name == "rookie" else "champion"
npc_boards_db = session.exec(
    select(PlayerBoard)
    .where(PlayerBoard.is_npc_pool == True)
    .where(PlayerBoard.npc_room == npc_room)
    .where(PlayerBoard.npc_retired == False)
).all()
# Selección aleatoria del pool (evitar repetir siempre el mismo)
chosen = _rng.sample(npc_boards_db, min(bot_count, len(npc_boards_db)))
opponents_boards = [b.card_ids for b in chosen]
chosen_board_ids = [b.id for b in chosen]
```

### Respuesta añade datos del tablero bot

```python
# Añadir al response:
"bot_board_nums": [
    [card_map_num[cid] for cid in b.card_ids]  # lotería numbers, not item IDs
    for b in chosen
],
"bot_board_ids": chosen_board_ids,  # debug / futura UI
```

### XP para tableros NPC

Después de cada partida, los tableros NPC que participaron acumulan XP:
- Bot ganó: `+15 XP` (mismo que un tablero de jugador en Rookie)
- Bot perdió: `+5 XP`
- Champion: valores Champion (+40/+10)

Level-up sigue la fórmula existente: `level * 100 XP` por nivel.

### Graduación al pool de gashapon

**Nivel de graduación:** **Nivel 10**

Cálculo de por qué nivel 10 es adecuado:
- XP necesario nivel 1→10: 100+200+300+400+500+600+700+800+900 = **4,500 XP**
- XP promedio por partida (mezcla wins/losses): ~10-15 XP
- Si el pool de 20 tableros recibe 200 partidas/día distribuidas entre todos: cada tablero participa ~10 veces/día
- Partidas para llegar a nivel 10: ~350-450
- Días necesarios: **35-45 días** de actividad moderada

Un tablero nivel 10 tiene historial de cientos de batallas. Premio raro, merecido.

```python
# Al actualizar XP de tablero NPC:
if npc_board.level >= 10 and not npc_board.npc_retired:
    npc_board.npc_retired = True
    session.add(npc_board)
    # El pool tiene 1 tablero menos → crear reemplazo
    _spawn_replacement_npc_board(session, npc_board.npc_room)
```

---

## Frontend `CpuSimScreen.tsx` — eliminar `fakeCpuBoard()`

### Cambios

```typescript
// SimResult: añadir
bot_board_nums?: number[][];  // arrays de 16 lotería-numbers por bot

// Estado:
// ANTES:
const [cpuBoardsNums] = useState<number[][]>(() => 
  Array.from({ length: BOT_COUNT }, () => fakeCpuBoard())
);

// DESPUÉS: inicializar vacío, poblar cuando llega result
const [cpuBoardsNums, setCpuBoardsNums] = useState<number[][]>([]);

// En fetchResult, después de setResult(res.data):
if (res.data.bot_board_nums?.length) {
  setCpuBoardsNums(res.data.bot_board_nums);
} else {
  // fallback solo si backend no envía datos (compatibilidad temporal)
  setCpuBoardsNums(Array.from({ length: BOT_COUNT }, () => fakeCpuBoard()));
}
```

### Eliminaciones

- `fakeCpuBoard()` — función eliminada (o marcada deprecated)
- Fallback de `calcPriorityLine` en el path `idx >= cards.length` — ya no necesario porque tableros coinciden
- El fix de parche anterior (cambio en `finishWithCpuWin`) puede quedar como safety net o revertirse

---

## Gashapon: Tableros Legendarios (bola de oro)

### Conceptos de diseño

- Nombre: **"Tabla Veterana"** o **"Tabla Forjada"**
- Los tableros NPC retirados (`npc_retired = True`) se guardan en un pool de premios gashapon
- Solo obtenibles con **bola de oro** (tier más raro del gashapon)
- Cuando el jugador gana uno, se le asigna: `user_id` cambia al ganador, `is_npc_pool = False`

### Metadatos especiales del tablero

Al graduarse, se registran stats permanentes en un campo nuevo o en los existentes:

```python
# Se puede usar el nombre del tablero como "etiqueta histórica":
npc_board.name = f"Tabla Forjada Nv.{npc_board.level} — {npc_board.games_played} batallas"
```

O campo nuevo `origin_story: Optional[str]` con texto generado:
```
"Forjada en 412 batallas. Ganó 38% de sus partidas. Nunca se rindió."
```

### Rareza y probabilidad

| Tipo gashapon | Probabilidad tabla forjada |
|---------------|--------------------------|
| Bola normal   | 0%                        |
| Bola de plata | 0%                        |
| Bola de oro   | ~2-5% (ajustable)         |

Solo se puede ganar UNA tabla forjada por tirada de bola de oro que toque.

### Backend: endpoint gashapon

En el endpoint de gashapon (buscar en `shop.py` o similar), añadir lógica:
- Si el premio seleccionado es "tabla_forjada" y hay tableros en el pool retirado:
  - Tomar el tablero retirado más antiguo (FIFO o random)
  - Asignar al usuario: `board.user_id = user_id`, `board.is_npc_pool = False`, `board.npc_retired = False`
  - Retornar datos del tablero con sus stats
- Si no hay tableros disponibles: fallback a otro premio

---

## Ideas adicionales y mejoras

### Idea: "Tablero en Servicio Activo" como badge en market

Cuando se liste para venta un tablero que tiene `is_npc_pool = True` (en teoría no aplica porque NPC los posee, pero para tableros de jugadores): mostrar badge "Activo en arena" si fue usado recientemente como bot en partidas de otros jugadores.

### Idea: Fase 3 — "Préstamo voluntario al bot pool"

Jugadores con tableros en el market pueden activar: `contribute_to_bot_pool = True`.
- Su tablero se usa como oponente CPU en partidas Rookie/Champion
- Gana XP bonus (2x la tasa normal) mientras espera comprador
- Mostrar en el listing: "🏟️ Activo en arena — +50 XP esta semana"
- Para compradores: tablero con historial real es más atractivo

### Idea: Clasificación de tableros forjados

No todos los tableros NPC llegan al mismo nivel. Se podría crear categorías:
- Nivel 10: **Forjado** (base)
- Nivel 15: **Legendario** (más raro, requiere más actividad del juego)
- Nivel 20: **Mítico** (extremadamente raro, puede llevar meses)

Cada categoría tiene probabilidades distintas en gashapon (mítico = 0.5% en bola de oro).

### Idea: Stats visibles del tablero forjado en UI

En el Inventory/board detail, si el tablero tiene origen NPC, mostrar mini-tarjeta:
```
⚔️ TABLA FORJADA
412 batallas · Nivel 10 · CSR 38%
Graduada el 2026-04-15
```

### Idea: Notificación global cuando se gradúa un tablero

Toast o evento en tiempo real: "🏆 Una nueva Tabla Forjada ha entrado al Gashapon"
Crea FOMO y recuerda a jugadores que existe esta recompensa.

---

## Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `backend/app/models/board.py` | +3 campos NPC |
| `backend/alembic/versions/XXX_npc_board_fields.py` | Migración nueva |
| `backend/app/api/v1/endpoints/game.py` | Query NPC boards, XP update, respuesta con bot_board_nums |
| `backend/app/scripts/seed_npc_boards.py` | Nuevo: crear user NPC + 40 tableros |
| `backend/app/api/v1/endpoints/shop.py` (o gashapon endpoint) | Premiar tablero forjado |
| `frontend/components/screens/CpuSimScreen.tsx` | Usar bot_board_nums, eliminar fakeCpuBoard |

---

## Fases de implementación

| Fase | Descripción | Prioridad |
|------|-------------|-----------|
| **1a** | Migración + campos NPC en model | Alta |
| **1b** | Script seed: user NPC + 40 tableros | Alta |
| **1c** | game.py: query real boards + bot_board_nums en response | Alta |
| **1d** | CpuSimScreen: usar bot_board_nums | Alta |
| **2a** | XP update para tableros NPC post-partida | Media |
| **2b** | Graduación a nivel 10 + spawn reemplazo | Media |
| **2c** | Gashapon bola de oro: premio tabla forjada | Media |
| **3a** | Origin story / nombre dinámico del tablero forjado | Baja |
| **3b** | Préstamo voluntario al bot pool (tableros de jugadores) | Baja |
| **3c** | Categorías Forjado/Legendario/Mítico | Baja |

---

## Verificación Fase 1 (bug fix)

1. Jugar partida Rookie: tablero CPU en pantalla = tablero real de DB
2. Perder partida: todas cartas marcadas en tablero CPU están en cantadas (emoji bar)
3. Ganar partida: victoria del jugador con línea válida
4. Con admin query: tableros NPC muestran XP creciente
5. Nivel de tableros NPC sube tras suficientes partidas (simular con simulate_universe.py)
