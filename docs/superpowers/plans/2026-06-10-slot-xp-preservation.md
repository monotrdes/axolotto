# Desintegración Gaming-Friendly: Slots con XP Persistente

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir el slot en la unidad de progresión: al desarmar una tabla el slot conserva el 80% del XP total acumulado, y la nueva tabla creada en ese slot hereda ese XP/nivel; stats de partidas (salinidad/suertudez) arrancan en blanco.

**Architecture:** Se agrega `PlayerBoardSlot` (modelo nuevo, un registro por usuario×slot) que persiste el XP preservado. Se agrega `slot_index` a `PlayerBoard` para saber a qué slot pertenece cada tabla. `delete_board_operation()` calcula el 80% del XP total y lo hace upsert en `PlayerBoardSlot`. `create_*_board_operation()` lee el XP del slot y arranca el tablero con ese nivel ya calculado (pero con games_played=0, games_won=0, recent_games_results=[] — salinidad/suertudez en blanco).

**Tech Stack:** FastAPI, SQLModel, PostgreSQL 16, Alembic, Next.js/TypeScript (Inventory.tsx)

---

## Context

El sistema actual castiga el desarmado de tablas con pérdida total del nivel (que determina el multiplicador de staking via `get_board_hourly_rate()` → `1.0 + board.level/10`). El GDD original indicaba pérdida de 1 carta, pero el código ya devuelve las 16; sin embargo la UI refleja la filosofía castigadora y el usuario pierde todo el progreso de nivel/XP acumulado.

Cambios requeridos:
1. Sin pérdida de cartas (ya implementado en código; limpiar comentarios/texto viejo)
2. Costo simbólico: **1 AXF** (era 120 FRJ; cambia de moneda secundaria a primaria — el solvente pasa a ser premium)
3. Slot conserva 80% del XP total al desarmar
4. Nueva tabla en el slot hereda ese XP/nivel
5. Stats de partidas (games_played, games_won, recent_games_results) inician en 0 → CSR/suertudez neutro
6. Badge de generación: GEN II, GEN III, etc. se muestra en la UI para tablas creadas en un slot con historial

---

## File Map

| Acción | Archivo |
|--------|---------|
| Modify (modelo nuevo + campo nuevo) | `backend/app/models/board.py` |
| Modify (helpers XP + disintegración + creación) | `backend/app/services/board_service.py` |
| Modify (slot status API) | `backend/app/services/board_service.py:1046-1199` |
| Modify (precio solvente) | `backend/app/core/prices.py` |
| Create (migration) | `backend/alembic/versions/<hash>_slot_xp_preservation.py` |
| Modify (UI modal + slot display + badge) | `frontend/components/Inventory.tsx` |
| Create (tests) | `backend/tests/test_board_slot_xp.py` |

---

## Task 1: Nuevo modelo `PlayerBoardSlot` + campo `slot_index` en `PlayerBoard`

**Files:**
- Modify: `backend/app/models/board.py`

- [ ] **Step 1: Agregar `PlayerBoardSlot` y campos en `board.py`**

```python
# Agregar al final de backend/app/models/board.py (después de PlayerBoard)
from sqlalchemy import UniqueConstraint

class PlayerBoardSlot(SQLModel, table=True):
    """Persiste el XP acumulado y la generación por slot después de desarmar una tabla."""
    __tablename__ = "playerboardslot"
    __table_args__ = (UniqueConstraint("user_id", "slot_index"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    slot_index: int
    preserved_xp: int = Field(default=0)
    boards_created: int = Field(default=0)  # cuántas tablas se han creado en este slot
```

En `PlayerBoard`, agregar después del campo `is_tutorial`:
```python
    slot_index: Optional[int] = Field(default=None, index=True)
    slot_generation: int = Field(default=1)  # GEN I=1, GEN II=2, etc.
```

- [ ] **Step 2: Commit**
```bash
git add backend/app/models/board.py
git commit -m "feat(board): PlayerBoardSlot model + slot_index + slot_generation on PlayerBoard"
```

---

## Task 2: Alembic migration con backfill

**Files:**
- Create: `backend/alembic/versions/<auto>_slot_xp_preservation.py`

- [ ] **Step 1: Generar migración**
```bash
cd backend
alembic revision --autogenerate -m "slot_xp_preservation"
```

- [ ] **Step 2: Verificar que incluya**
1. `CREATE TABLE playerboardslot (id, user_id, slot_index, preserved_xp, boards_created, UNIQUE(user_id, slot_index))`
2. `ALTER TABLE playerboard ADD COLUMN slot_index INTEGER`
3. `ALTER TABLE playerboard ADD COLUMN slot_generation INTEGER DEFAULT 1`

- [ ] **Step 3: Agregar backfill en `upgrade()`**

```python
op.execute("""
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn
        FROM playerboard
        WHERE is_dead = FALSE
    )
    UPDATE playerboard
    SET slot_index = ranked.rn
    FROM ranked
    WHERE playerboard.id = ranked.id
""")
```

- [ ] **Step 4: Aplicar migración**
```bash
alembic upgrade head
```

- [ ] **Step 5: Commit**
```bash
git add backend/alembic/versions/
git commit -m "feat(migration): slot_xp_preservation — PlayerBoardSlot + slot_index backfill"
```

---

## Task 3: Helpers XP en `board_service.py`

**Files:**
- Modify: `backend/app/services/board_service.py`

Agregar antes de `get_board_hourly_rate`:

- [ ] **Step 1: Agregar helpers de XP**

```python
def _total_board_xp(board: "PlayerBoard") -> int:
    """XP total acumulado = XP gastado en nivel-ups + XP actual del nivel."""
    return (board.level * (board.level - 1) // 2) * 100 + board.xp


def _apply_preserved_xp_to_board(board: "PlayerBoard", preserved_xp: int) -> None:
    """Aplica XP preservado a un tablero nuevo, calculando nivel resultante."""
    board.level = 1
    board.xp = preserved_xp
    while board.xp >= (board.level * 100):
        board.xp -= board.level * 100
        board.level += 1


def _level_from_total_xp(total_xp: int) -> int:
    """Nivel que resultaría de un total de XP dado."""
    level, xp = 1, total_xp
    while xp >= (level * 100):
        xp -= level * 100
        level += 1
    return level
```

- [ ] **Step 2: Importar `PlayerBoardSlot` en board_service.py**

```python
from app.models.board import PlayerBoard, PlayerBoardSlot
```

- [ ] **Step 3: Commit**
```bash
git add backend/app/services/board_service.py
git commit -m "feat(board): helpers XP para slot preservation"
```

---

## Task 4: Modificar `delete_board_operation()` — 1 AXF + 80% XP

**Files:**
- Modify: `backend/app/core/prices.py` (línea ~78)
- Modify: `backend/app/services/board_service.py:570-696`

- [ ] **Step 1: Cambiar costo en `prices.py`**

```python
"solvente": 1 * _AXF,    # Solvente de Pegamento — 1 AXF (era 120 FRJ)
```

- [ ] **Step 2: Actualizar validación de saldo y ledger en `delete_board_operation()`**

Reemplazar bloque de costo (líneas ~609-626):
```python
    cost = CONSUMABLE_PRICES["solvente"]   # 1 AXF
    wallet = BankService.get_or_create_wallet(session, user_id)
    if wallet.axofichas < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Desarmar cuesta {cost} AXF (Solvente de Pegamento).",
        )
    wallet.axofichas -= cost
    ledger_delete = TransactionLedger(
        user_id=user_id,
        amount=cost,
        currency=CurrencyType.AXOFICHA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Solvente de Pegamento para desarmar tabla #{board_id}",
    )
    session.add(ledger_delete)
```

- [ ] **Step 3: Insertar preservación de XP antes de `board.is_dead = True`**

```python
    # Preservar 80% del XP total en el slot
    if board.slot_index is not None:
        total_xp = _total_board_xp(board)
        preserved = int(total_xp * 0.8)
        slot_record = session.exec(
            select(PlayerBoardSlot).where(
                PlayerBoardSlot.user_id == user_id,
                PlayerBoardSlot.slot_index == board.slot_index,
            )
        ).first()
        if slot_record:
            slot_record.preserved_xp = preserved
            session.add(slot_record)
        else:
            session.add(PlayerBoardSlot(
                user_id=user_id,
                slot_index=board.slot_index,
                preserved_xp=preserved,
                boards_created=1,
            ))
    preserved_xp_out = int(_total_board_xp(board) * 0.8) if board.slot_index else 0
```

- [ ] **Step 4: Actualizar docstring + respuesta final**

```python
def delete_board_operation(...):
    """Desarma la tabla: devuelve las 16 cartas, cobra 1 AXF y preserva 80% del XP en el slot."""
```

```python
    return {
        "mensaje": "Tabla desarmada. Las 16 cartas han vuelto a tu inventario. El 80% del XP queda guardado en el slot.",
        "lost_card": None,
        "preserved_xp": preserved_xp_out,
        "tx_blockchain": tx_blockchain,
    }
```

- [ ] **Step 5: Commit**
```bash
git add backend/app/services/board_service.py backend/app/core/prices.py
git commit -m "feat(board): desarmar cuesta 1 AXF, preserva 80% XP en slot"
```

---

## Task 5: Modificar `create_*_board_operation()` — heredar XP + badge GEN

**Files:**
- Modify: `backend/app/services/board_service.py:321-534`

- [ ] **Step 1: Agregar `_assign_slot_index()`**

```python
def _assign_slot_index(user_id: str, session: Session) -> int:
    """Slot_index más bajo disponible para el usuario (sin tabla activa)."""
    used_slots = set(
        session.exec(
            select(PlayerBoard.slot_index)
            .where(PlayerBoard.user_id == user_id)
            .where(PlayerBoard.is_dead == False)
            .where(PlayerBoard.slot_index.is_not(None))
        ).all()
    )
    slot = 1
    while slot in used_slots:
        slot += 1
    return slot
```

- [ ] **Step 2: Bloque de herencia XP + generación (insertar antes de `session.add(new_board)` en ambas funciones)**

```python
    new_board.slot_index = _assign_slot_index(user_id, session)
    slot_record = session.exec(
        select(PlayerBoardSlot).where(
            PlayerBoardSlot.user_id == user_id,
            PlayerBoardSlot.slot_index == new_board.slot_index,
        )
    ).first()
    if slot_record:
        if slot_record.preserved_xp > 0:
            _apply_preserved_xp_to_board(new_board, slot_record.preserved_xp)
            slot_record.preserved_xp = 0
        slot_record.boards_created += 1
        new_board.slot_generation = slot_record.boards_created
        session.add(slot_record)
    else:
        new_board.slot_generation = 1
        session.add(PlayerBoardSlot(
            user_id=user_id,
            slot_index=new_board.slot_index,
            preserved_xp=0,
            boards_created=1,
        ))
```

- [ ] **Step 3: Agregar en el dict de respuesta**

```python
        "slot_index": new_board.slot_index,
        "slot_generation": new_board.slot_generation,
        "inherited_level": new_board.level,
```

- [ ] **Step 4: Commit**
```bash
git add backend/app/services/board_service.py
git commit -m "feat(board): asignar slot, heredar XP y badge de generación al crear tabla"
```

---

## Task 6: `get_slot_status_data()` — exponer XP preservado

**Files:**
- Modify: `backend/app/services/board_service.py:1046-1199`

- [ ] **Step 1: Para cada slot vacío, agregar consulta a `PlayerBoardSlot`**

```python
slot_xp_record = session.exec(
    select(PlayerBoardSlot).where(
        PlayerBoardSlot.user_id == user_id,
        PlayerBoardSlot.slot_index == slot_num,
    )
).first()
preserved_xp = slot_xp_record.preserved_xp if slot_xp_record else 0
```

En el dict del slot vacío:
```python
{
    "slot_index": slot_num,
    "status": "empty",
    "preserved_xp": preserved_xp,
    "preserved_level": _level_from_total_xp(preserved_xp),
    ...
}
```

- [ ] **Step 2: Commit**
```bash
git add backend/app/services/board_service.py
git commit -m "feat(board): slot status expone preserved_xp y preserved_level"
```

---

## Task 7: Frontend — modal desarmar + badge GEN

**Files:**
- Modify: `frontend/components/Inventory.tsx`

- [ ] **Step 1: Cambiar `120 FRJ` → `1 AXF` en el modal (líneas ~596, ~638)**

- [ ] **Step 2: Agregar ítems de XP Preservado y Stats en blanco en el modal**

```tsx
<li>
  <span className="text-amber-400 font-bold">XP Preservado:</span>{" "}
  El <span className="text-white font-bold">80% del XP</span> queda guardado
  en el slot para tu próxima tabla.
</li>
<li>
  <span className="text-slate-400 font-bold">Stats en blanco:</span>{" "}
  La nueva tabla inicia sin historial (salinidad/suertudez neutras).
</li>
```

- [ ] **Step 3: Mostrar `⚡ Nivel X guardado` en slots vacíos con XP**

```tsx
{slot.preserved_xp > 0 && (
  <span className="text-xs text-amber-400 font-mono">
    ⚡ Nivel {slot.preserved_level} guardado
  </span>
)}
```

- [ ] **Step 4: Badge GEN II/III junto al nombre de la tabla**

Helper (en el archivo o util local):
```ts
function toRoman(n: number): string {
  const vals = [10,'X',9,'IX',5,'V',4,'IV',1,'I'] as const;
  let result = '';
  for (let i = 0; i < vals.length; i += 2) {
    while (n >= (vals[i] as number)) { result += vals[i+1]; n -= vals[i] as number; }
  }
  return result;
}
```

Badge (solo si `slot_generation > 1`):
```tsx
{board.slot_generation > 1 && (
  <span className="text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded bg-violet-900/60 text-violet-300 border border-violet-700/40">
    GEN {toRoman(board.slot_generation)}
  </span>
)}
```

- [ ] **Step 5: Commit**
```bash
git add frontend/components/Inventory.tsx
git commit -m "feat(ui): badge GEN + 1 AXF + XP preservado en modal desarmar"
```

---

## Task 8: Tests unitarios

**Files:**
- Create: `backend/tests/test_board_slot_xp.py`

- [ ] **Step 1: Escribir y correr tests**

```python
import pytest
from app.models.board import PlayerBoard
from app.services.board_service import _total_board_xp, _apply_preserved_xp_to_board, _level_from_total_xp

def make_board(level: int, xp: int) -> PlayerBoard:
    b = PlayerBoard(user_id="test", name="T", card_ids=[], card_first_editions=[])
    b.level = level
    b.xp = xp
    return b

def test_total_xp_level1():
    assert _total_board_xp(make_board(1, 50)) == 50

def test_total_xp_level5():
    assert _total_board_xp(make_board(5, 150)) == 1150

def test_apply_zero_xp():
    b = make_board(1, 0)
    _apply_preserved_xp_to_board(b, 0)
    assert b.level == 1 and b.xp == 0

def test_apply_xp_crosses_levels():
    b = make_board(1, 0)
    _apply_preserved_xp_to_board(b, 920)
    assert b.level == 4 and b.xp == 320

def test_80_percent_roundtrip():
    b = make_board(5, 150)           # total=1150
    preserved = int(_total_board_xp(b) * 0.8)  # 920
    nb = make_board(1, 0)
    _apply_preserved_xp_to_board(nb, preserved)
    assert nb.level == 4             # bajó un nivel (20% perdido)
    assert nb.level < b.level

def test_level_from_total_xp():
    assert _level_from_total_xp(0) == 1
    assert _level_from_total_xp(100) == 2
    assert _level_from_total_xp(299) == 2
    assert _level_from_total_xp(300) == 3
```

```bash
cd backend && pytest tests/test_board_slot_xp.py -v
```

- [ ] **Step 2: Commit**
```bash
git add backend/tests/test_board_slot_xp.py
git commit -m "test(board): unit tests para helpers de XP de slot"
```

---

## Verification

1. `pytest backend/tests/test_board_slot_xp.py -v` → todos PASS
2. `alembic upgrade head` aplicado sin errores
3. Flujo manual:
   - Crear tabla → jugar partidas → desarmar
   - Verificar `SELECT preserved_xp, boards_created FROM playerboardslot WHERE user_id=...`
   - Crear nueva tabla → `level > 1`, `games_played = 0`, `slot_generation = 2`
   - UI muestra badge "GEN II" y modal muestra "1 AXF"
4. Staking rate mayor que una tabla nivel 1 gracias al nivel heredado
