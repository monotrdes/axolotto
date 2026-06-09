# Criadero, Webitos e Imprinting — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el sistema de cuidados con cooldown por imprinting via partidas, añadir ceremonia de nacimiento cinematográfica, sistema de eventos de modo manual configurable desde admin, y ajustes menores (SUERTE de usuario, Glotón).

**Architecture:** Backend-first TDD: servicios puros primero, luego hooks en endpoints existentes, finalmente componentes frontend. El `imprinting_service.py` es puro (sin DB) para facilitar testing. Los nuevos campos de DB se añaden via `main.py` startup migrations (patrón existente en el proyecto). El `ManualModeEvent` es un modelo independiente con sus propios endpoints.

**Tech Stack:** FastAPI, SQLModel, PostgreSQL, pytest, Next.js 14, React, TypeScript, Tailwind CSS, Privy auth.

**Complementa:** `docs/superpowers/plans/2026-05-31-sistema-4-stats-axolotito.md` (4-stats). Este plan asume que el modelo `Axolotito` sigue teniendo los 8 campos de stat en DB.

---

## FASE 0 — Modelos y Migraciones

### Task 1: Modelo ManualModeEvent

**Files:**
- Create: `backend/app/models/manual_mode_event.py`
- Modify: `backend/tests/conftest.py` — importar el nuevo modelo
- Modify: `backend/app/main.py` — crear tabla en startup

- [ ] **Step 1: Crear el modelo**

```python
# backend/app/models/manual_mode_event.py
from __future__ import annotations
from datetime import date, datetime, time
from typing import Optional
from sqlmodel import Field, SQLModel


class ManualModeEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                                      # "Noche de Lotería #1 🌙"
    start_date: date
    end_date: date
    daily_open_time: Optional[time] = Field(default=None, nullable=True)   # None = todo el día
    daily_close_time: Optional[time] = Field(default=None, nullable=True)
    timezone: str = Field(default="America/Mexico_City")

    # Economía
    tabla_cost_gal: float = Field(default=10.0)
    max_tablas_per_player: int = Field(default=3)
    prize_pool_pct: float = Field(default=0.80)
    platform_fee_pct: float = Field(default=0.10)
    jackpot_contribution_pct: float = Field(default=0.10)
    bonus_gal_on_win: float = Field(default=0.0)
    drop_multiplier: float = Field(default=1.0)
    xp_bonus_pct: float = Field(default=0.0)

    # Mecánicas
    griton_delay_ms: int = Field(default=2000)     # 800–3000
    griton_repeats: bool = Field(default=True)
    win_condition: str = Field(default="tabla_llena")  # línea_h|línea_v|esquinas|tabla_llena|cruz|l_invertida
    max_game_duration_s: Optional[int] = Field(default=None, nullable=True)
    tie_behavior: str = Field(default="split")     # split|replay
    allowed_modes: str = Field(default="both")     # manual|bot|both

    # Jugadores
    max_players_per_room: int = Field(default=10)
    min_players_to_start: int = Field(default=2)
    room_wait_timeout_s: int = Field(default=90)
    vip_only: bool = Field(default=False)
    min_axo_level: Optional[int] = Field(default=None, nullable=True)
    first_time_only: bool = Field(default=False)

    # Comunicación
    broadcast_message: Optional[str] = Field(default=None, nullable=True)
    broadcast_sent: bool = Field(default=False)
    broadcast_sent_at: Optional[datetime] = Field(default=None, nullable=True)
    auto_reminder: bool = Field(default=True)
    notify_room_start: bool = Field(default=True)
    post_event_summary: bool = Field(default=True)

    # Meta
    is_active: bool = Field(default=True)
    created_by: str                                # privy_did del admin
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] **Step 2: Importar en conftest.py**

Añadir al bloque de imports en `backend/tests/conftest.py` (después de la línea de `Axolotito`):

```python
from app.models.manual_mode_event import ManualModeEvent  # noqa: F401
```

- [ ] **Step 3: Registrar en main.py startup**

En `backend/app/main.py`, en el bloque de imports del archivo (línea 6):

```python
from app.api.v1.endpoints import (
    bank, user, shop, incubation, metadata, legacy, board, game,
    ranking, multiplayer, checkout, market, leonardo, admin, whitelist,
    codes, f2p, tutorial, webito_slots,
)
from app.models.manual_mode_event import ManualModeEvent  # noqa: F401 — registra tabla
```

El `SQLModel.metadata.create_all(engine)` en `on_startup` creará la tabla automáticamente.

- [ ] **Step 4: Verificar que la tabla se crea**

```bash
cd backend
python -c "
from app.models.manual_mode_event import ManualModeEvent
from sqlmodel import SQLModel
print('ManualModeEvent table name:', ManualModeEvent.__tablename__)
print('Columns:', [c.name for c in ManualModeEvent.__table__.columns])
"
```

Esperado: lista de columnas sin error.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/manual_mode_event.py backend/tests/conftest.py backend/app/main.py
git commit -m "feat(events): add ManualModeEvent model"
```

---

### Task 2: Campos de Imprinting en WebitoIncubation

**Files:**
- Modify: `backend/app/models/items.py` — añadir campos de imprinting
- Modify: `backend/app/main.py` — migración dinámica en startup

- [ ] **Step 1: Añadir campos al modelo WebitoIncubation**

En `backend/app/models/items.py`, después de la línea `tutorial_karma`:

```python
    # --- SISTEMA DE IMPRINTING (reemplaza cooldown care) ---
    imprinting_games_played: int = Field(default=0)
    imprinting_padrino_id: Optional[int] = Field(
        default=None, nullable=True, foreign_key="axolotito.id"
    )
    # Stats base al inicio del imprinting (se setean al llamar start_imprinting)
    base_stat_luck: float = Field(default=0.0)
    base_stat_focus: float = Field(default=0.0)
    base_stat_stamina: float = Field(default=0.0)
    base_stat_salinity: float = Field(default=0.0)
    # bonus_salinity acumulado durante imprinting (nuevo — los otros bonus_* ya existen)
    bonus_salinity_adj: float = Field(default=0.0)
    # imprinting completado (ADN sellado, listo para eclosión)
    imprinting_complete: bool = Field(default=False)
```

- [ ] **Step 2: Añadir migración dinámica en main.py**

En `backend/app/main.py`, dentro del bloque `async def on_startup()`, después del bloque de `cols_to_add` existente:

```python
        # --- Imprinting 1.0 ---
        imprinting_cols = [
            ("imprinting_games_played", "INTEGER DEFAULT 0"),
            ("imprinting_padrino_id",   "INTEGER"),
            ("base_stat_luck",          "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_focus",         "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_stamina",       "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_salinity",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_salinity_adj",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("imprinting_complete",     "BOOLEAN DEFAULT FALSE"),
        ]
        for col_name, col_type in imprinting_cols:
            if col_name not in existing_cols:
                conn.execute(text(
                    f"ALTER TABLE webitoincubation ADD COLUMN {col_name} {col_type};"
                ))
        conn.commit()
```

- [ ] **Step 3: Verificar**

```bash
cd backend
python -c "
from app.models.items import WebitoIncubation
cols = [c.name for c in WebitoIncubation.__table__.columns]
assert 'imprinting_games_played' in cols
assert 'base_stat_luck' in cols
assert 'bonus_salinity_adj' in cols
print('OK:', cols)
"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/items.py backend/app/main.py
git commit -m "feat(imprinting): add imprinting fields to WebitoIncubation"
```

---

## FASE 1 — Imprinting Service (TDD)

### Task 3: imprinting_service.py — lógica pura

**Files:**
- Create: `backend/app/services/imprinting_service.py`
- Create: `backend/tests/unit/test_imprinting_service.py`

- [ ] **Step 1: Escribir los tests primero**

```python
# backend/tests/unit/test_imprinting_service.py
"""Tests del servicio de imprinting. Sin DB — lógica pura."""
import pytest
from app.services.imprinting_service import (
    ImprintingGameResult,
    StatDeltas,
    compute_deltas,
    final_stats,
    required_games_for_rarity,
    _clamp,
)
from app.models.items import Rarity


# ---------------------------------------------------------------------------
# required_games_for_rarity
# ---------------------------------------------------------------------------

def test_required_games_common():
    assert required_games_for_rarity(Rarity.COMMON) == 3

def test_required_games_rare():
    assert required_games_for_rarity(Rarity.RARE) == 5

def test_required_games_legendary():
    assert required_games_for_rarity(Rarity.LEGENDARY) == 7

def test_required_games_epic_same_as_legendary():
    assert required_games_for_rarity(Rarity.EPIC) == 7


# ---------------------------------------------------------------------------
# compute_deltas — SUERTE
# ---------------------------------------------------------------------------

def test_suerte_jackpot_gives_20():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=True,
        mark_accuracy=0.9, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.luck_delta == 20.0

def test_suerte_win_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.9, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert 8.0 <= d.luck_delta <= 15.0

def test_suerte_loss_negative():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.5, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert -12.0 <= d.luck_delta <= -8.0


# ---------------------------------------------------------------------------
# compute_deltas — OJO
# ---------------------------------------------------------------------------

def test_ojo_high_accuracy_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.85, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.focus_delta >= 10.0

def test_ojo_low_accuracy_negative():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.40, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.focus_delta <= -8.0

def test_ojo_padrino_energy_bonus():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.85, session_game_count=1,
        padrino_energy_pct=0.85, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    # base +10-18 plus +5 energy bonus
    assert d.focus_delta >= 15.0


# ---------------------------------------------------------------------------
# compute_deltas — PILA
# ---------------------------------------------------------------------------

def test_pila_long_session_positive():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=3,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert 10.0 <= d.stamina_delta <= 15.0

def test_pila_single_short_game_negative():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    assert d.stamina_delta == -5.0

def test_pila_padrino_high_energy_bonus():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=3,
        padrino_energy_pct=0.85, padrino_sal=10.0,
    )
    d = compute_deltas(result)
    # base +10-15 plus +8 energy bonus
    assert d.stamina_delta >= 18.0


# ---------------------------------------------------------------------------
# compute_deltas — SAL
# ---------------------------------------------------------------------------

def test_sal_clean_game_negative():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=10.0,  # SAL < 20
    )
    d = compute_deltas(result)
    assert -10.0 <= d.salinity_delta <= -6.0

def test_sal_high_padrino_sal_increases():
    result = ImprintingGameResult(
        won=True, had_jackpot_bonus=False,
        mark_accuracy=0.7, session_game_count=1,
        padrino_energy_pct=0.5, padrino_sal=60.0,  # SAL > 50
    )
    d = compute_deltas(result)
    assert 8.0 <= d.salinity_delta <= 12.0

def test_sal_many_misses_adds():
    result = ImprintingGameResult(
        won=False, had_jackpot_bonus=False,
        mark_accuracy=0.35, session_game_count=1,  # < 40%
        padrino_energy_pct=0.5, padrino_sal=25.0,
    )
    d = compute_deltas(result)
    assert d.salinity_delta >= 5.0


# ---------------------------------------------------------------------------
# final_stats
# ---------------------------------------------------------------------------

class FakeIncubation:
    base_stat_luck = 35.0
    base_stat_focus = 40.0
    base_stat_stamina = 90.0
    base_stat_salinity = 20.0
    bonus_luck = 15.0
    bonus_focus = -5.0
    bonus_stamina = 12.0
    bonus_salinity_adj = -8.0

def test_final_stats_computes_correctly():
    inc = FakeIncubation()
    stats = final_stats(inc)
    assert stats["stat_luck"] == pytest.approx(50.0)
    assert stats["stat_focus"] == pytest.approx(35.0)
    assert stats["stat_stamina"] == 102
    assert stats["stat_salinity"] == pytest.approx(12.0)
    assert stats["stat_agility"] == pytest.approx(35.0)  # mirrors focus
    assert stats["stat_charisma"] == 0.0
    assert stats["stat_wisdom"] == 0.0
    assert stats["stat_strength"] == 0.0

def test_final_stats_clamped():
    inc = FakeIncubation()
    inc.bonus_luck = 200.0  # would exceed 100
    stats = final_stats(inc)
    assert stats["stat_luck"] == 100.0

def test_final_stats_stamina_min():
    inc = FakeIncubation()
    inc.bonus_stamina = -200.0
    stats = final_stats(inc)
    assert stats["stat_stamina"] == 50


# ---------------------------------------------------------------------------
# _clamp helper
# ---------------------------------------------------------------------------

def test_clamp_within():
    assert _clamp(50.0, 0.0, 100.0) == 50.0

def test_clamp_below():
    assert _clamp(-5.0, 0.0, 100.0) == 0.0

def test_clamp_above():
    assert _clamp(150.0, 0.0, 100.0) == 100.0
```

- [ ] **Step 2: Ejecutar tests — deben fallar**

```bash
cd backend
pytest tests/unit/test_imprinting_service.py -v 2>&1 | head -20
```

Esperado: `ModuleNotFoundError: No module named 'app.services.imprinting_service'`

- [ ] **Step 3: Implementar el servicio**

```python
# backend/app/services/imprinting_service.py
"""
imprinting_service.py — Lógica de imprinting para Webitos.

El ADN incompleto del Webito se moldea por las partidas del padrino.
Los deltas se acumulan en WebitoIncubation.bonus_* fields.
Al completar N partidas (según rareza), el ADN se sella y eclosa.

Puro: sin imports de DB ni FastAPI para facilitar testing.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

from app.models.items import Rarity

_rng = random.SystemRandom()

# Partidas requeridas por rareza
_REQUIRED_GAMES: dict[str, int] = {
    "common":    3,
    "rare":      5,
    "epic":      7,
    "legendary": 7,
}

# Rangos de stats base al inicio del imprinting (valor inicial ± variación)
_BASE_RANGES: dict[str, tuple[float, float]] = {
    "luck":     (20.0, 50.0),
    "focus":    (25.0, 55.0),
    "stamina":  (70.0, 110.0),
    "salinity": (10.0, 30.0),
}


@dataclass
class ImprintingGameResult:
    """Datos de una partida que alimentan el imprinting del Webito."""
    won: bool
    had_jackpot_bonus: bool       # True si el premio incluyó jackpot/bonus
    mark_accuracy: float          # 0.0–1.0: fracción de cartas del tablero marcadas
    session_game_count: int       # games_played + 1 (el actual), para detectar sesión larga
    padrino_energy_pct: float     # energy_current / stat_stamina al terminar (0.0–1.0)
    padrino_sal: float            # stat_salinity del padrino al terminar (0–100)


@dataclass
class StatDeltas:
    """Cambios a aplicar a los stats del Webito tras una partida."""
    luck_delta: float = 0.0
    focus_delta: float = 0.0
    stamina_delta: float = 0.0
    salinity_delta: float = 0.0


def required_games_for_rarity(rarity: Rarity) -> int:
    """Devuelve cuántas partidas de imprinting necesita el Webito según su rareza."""
    return _REQUIRED_GAMES.get(rarity.value, 3)


def initial_base_stats() -> dict[str, float]:
    """
    Genera los stats base iniciales del Webito al iniciar el imprinting.
    Llamar UNA SOLA VEZ al inicio del imprinting y almacenar en WebitoIncubation.
    """
    return {
        "base_stat_luck":     _rng.uniform(*_BASE_RANGES["luck"]),
        "base_stat_focus":    _rng.uniform(*_BASE_RANGES["focus"]),
        "base_stat_stamina":  _rng.uniform(*_BASE_RANGES["stamina"]),
        "base_stat_salinity": _rng.uniform(*_BASE_RANGES["salinity"]),
    }


def compute_deltas(result: ImprintingGameResult) -> StatDeltas:
    """
    Calcula los deltas de stats para el Webito a partir del resultado de una partida.
    Puro, sin efectos secundarios. Testeable en aislamiento.
    """
    d = StatDeltas()

    # --- ✨ SUERTE ---
    if result.had_jackpot_bonus:
        d.luck_delta = 20.0
    elif result.won:
        d.luck_delta = _rng.uniform(8.0, 15.0)
    else:
        d.luck_delta = -_rng.uniform(8.0, 12.0)

    # --- 👁️ OJO ---
    if result.mark_accuracy >= 0.80:
        d.focus_delta = _rng.uniform(10.0, 18.0)
    elif result.mark_accuracy <= 0.50:
        d.focus_delta = -_rng.uniform(8.0, 14.0)
    if result.padrino_energy_pct > 0.80:
        d.focus_delta += 5.0

    # --- 🔋 PILA ---
    if result.session_game_count >= 3:
        d.stamina_delta = _rng.uniform(10.0, 15.0)
    elif result.session_game_count == 1:
        d.stamina_delta = -5.0
    if result.padrino_energy_pct > 0.80:
        d.stamina_delta += 8.0

    # --- 🧂 SAL ---
    if result.padrino_sal < 20.0:
        d.salinity_delta = -_rng.uniform(6.0, 10.0)
    elif result.padrino_sal > 50.0:
        d.salinity_delta = _rng.uniform(8.0, 12.0)
    if result.mark_accuracy < 0.40:
        d.salinity_delta += 5.0

    return d


def apply_deltas_to_incubation(incubation, deltas: StatDeltas) -> None:
    """
    Aplica los deltas al WebitoIncubation en memoria.
    El caller debe hacer session.add(incubation) y session.commit().
    """
    incubation.bonus_luck         = _clamp(incubation.bonus_luck + deltas.luck_delta,         -50.0, 50.0)
    incubation.bonus_focus        = _clamp(incubation.bonus_focus + deltas.focus_delta,        -50.0, 50.0)
    incubation.bonus_stamina      = _clamp(incubation.bonus_stamina + deltas.stamina_delta,    -60.0, 60.0)
    incubation.bonus_salinity_adj = _clamp(
        incubation.bonus_salinity_adj + deltas.salinity_delta, -50.0, 50.0
    )
    incubation.imprinting_games_played += 1


def final_stats(incubation) -> dict:
    """
    Calcula los stats finales del Axolotito al eclosionar.
    base_stat_* + bonus_* clampeados a rangos válidos.
    """
    luck     = _clamp(incubation.base_stat_luck + incubation.bonus_luck,              0.0, 100.0)
    focus    = _clamp(incubation.base_stat_focus + incubation.bonus_focus,            0.0, 100.0)
    stamina  = int(_clamp(incubation.base_stat_stamina + incubation.bonus_stamina,    50.0, 200.0))
    salinity = _clamp(
        incubation.base_stat_salinity + incubation.bonus_salinity_adj, 0.0, 100.0
    )
    return {
        "stat_luck":     luck,
        "stat_focus":    focus,
        "stat_stamina":  stamina,
        "stat_salinity": salinity,
        "stat_agility":  focus,    # OJO = Focus = Agility (spec §2, 4-stats)
        "stat_charisma": 0.0,
        "stat_wisdom":   0.0,
        "stat_strength": 0.0,
    }


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
```

- [ ] **Step 4: Ejecutar tests — deben pasar**

```bash
cd backend
pytest tests/unit/test_imprinting_service.py -v
```

Esperado: todos los tests en PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/imprinting_service.py backend/tests/unit/test_imprinting_service.py
git commit -m "feat(imprinting): add imprinting_service with full TDD coverage"
```

---

## FASE 2 — Backend Hooks

### Task 4: incubation.py — Endpoints de Imprinting

**Files:**
- Modify: `backend/app/api/v1/endpoints/incubation.py`

Reemplazar las 3 acciones de cuidado (acariciar/cantar/alimentar) con dos endpoints nuevos: `start_imprinting` y `imprinting_status`.

- [ ] **Step 1: Añadir imports en incubation.py**

Al inicio del archivo, agregar:
```python
from app.services.imprinting_service import (
    initial_base_stats,
    required_games_for_rarity,
)
from app.models.axolotito import Axolotito
```

- [ ] **Step 2: Añadir modelo Pydantic para start_imprinting**

Después de `class InteractPayload`:

```python
class StartImprintingPayload(BaseModel):
    incubation_id: int
    padrino_axolotito_id: int
```

- [ ] **Step 3: Añadir endpoint POST /start-imprinting**

```python
@router.post("/start-imprinting")
def start_imprinting(
    payload: StartImprintingPayload,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Inicia el imprinting de un Webito. Asigna padrino y genera stats base."""
    incubation = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.id == payload.incubation_id)
    ).first()
    if not incubation or incubation.user_id != verified_user_id:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")
    if incubation.imprinting_games_played > 0:
        raise HTTPException(status_code=400, detail="El imprinting ya comenzó.")

    padrino = session.exec(
        select(Axolotito)
        .where(Axolotito.id == payload.padrino_axolotito_id)
        .where(Axolotito.user_id == verified_user_id)
    ).first()
    if not padrino:
        raise HTTPException(status_code=404, detail="Padrino no encontrado.")

    # Verificar que el padrino no ya es padrino de otro webito
    already_padrino = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.imprinting_padrino_id == padrino.id)
        .where(WebitoIncubation.user_id == verified_user_id)
        .where(WebitoIncubation.imprinting_complete == False)
    ).first()
    if already_padrino and already_padrino.id != incubation.id:
        raise HTTPException(
            status_code=400,
            detail=f"{padrino.name} ya está siendo padrino de otro Webito.",
        )

    # Generar stats base y asignar padrino
    base = initial_base_stats()
    incubation.base_stat_luck     = base["base_stat_luck"]
    incubation.base_stat_focus    = base["base_stat_focus"]
    incubation.base_stat_stamina  = base["base_stat_stamina"]
    incubation.base_stat_salinity = base["base_stat_salinity"]
    incubation.imprinting_padrino_id = padrino.id

    # Obtener rareza del huevo para saber cuántas partidas necesita
    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    session.add(incubation)
    session.commit()
    session.refresh(incubation)

    return {
        "message": f"¡Imprinting iniciado! Lleva a {padrino.name} a {required} partidas.",
        "incubation_id": incubation.id,
        "padrino": {"id": padrino.id, "name": padrino.name},
        "required_games": required,
        "games_played": 0,
    }
```

- [ ] **Step 4: Añadir endpoint GET /imprinting-status/{incubation_id}**

```python
@router.get("/imprinting-status/{incubation_id}")
def imprinting_status(
    incubation_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Estado actual del imprinting de un Webito."""
    incubation = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.id == incubation_id)
    ).first()
    if not incubation or incubation.user_id != verified_user_id:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")

    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    padrino_name = None
    if incubation.imprinting_padrino_id:
        padrino = session.exec(
            select(Axolotito).where(Axolotito.id == incubation.imprinting_padrino_id)
        ).first()
        padrino_name = padrino.name if padrino else None

    return {
        "incubation_id": incubation.id,
        "imprinting_started": incubation.imprinting_padrino_id is not None,
        "imprinting_complete": incubation.imprinting_complete,
        "games_played": incubation.imprinting_games_played,
        "required_games": required,
        "padrino_name": padrino_name,
        # Stats parciales (visibles para el jugador durante imprinting)
        "current_stats": {
            "suerte_delta": round(incubation.bonus_luck, 1),
            "ojo_delta":    round(incubation.bonus_focus, 1),
            "pila_delta":   round(incubation.bonus_stamina, 1),
            "sal_delta":    round(incubation.bonus_salinity_adj, 1),
        },
    }
```

- [ ] **Step 5: Verificar sintaxis**

```bash
cd backend
python -c "from app.api.v1.endpoints.incubation import router; print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/v1/endpoints/incubation.py
git commit -m "feat(imprinting): add start_imprinting and imprinting_status endpoints"
```

---

### Task 5: game.py — Hook de Imprinting al Terminar Partida Bot

**Files:**
- Modify: `backend/app/api/v1/endpoints/game.py`

Al final de cada partida bot (después de actualizar XP y antes del `return`), aplicar imprinting si el padrino tiene un Webito en imprinting activo.

- [ ] **Step 1: Añadir imports en game.py**

```python
from app.services.imprinting_service import (
    ImprintingGameResult,
    compute_deltas,
    apply_deltas_to_incubation,
    final_stats,
    required_games_for_rarity,
)
from app.models.items import WebitoIncubation, ItemCatalog
```

- [ ] **Step 2: Añadir helper _apply_imprinting_if_needed**

Justo antes del `@router.post("/play")` en game.py, añadir:

```python
def _apply_imprinting_if_needed(
    axo,           # Axolotito — el padrino
    is_win: bool,
    had_jackpot: bool,
    mark_accuracy: float,
    session,
) -> dict | None:
    """
    Si el Axolotito es padrino de un Webito en imprinting, aplica los deltas.
    Devuelve info del imprinting si ocurrió, None si no.
    """
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.imprinting_padrino_id == axo.id)
        .where(WebitoIncubation.imprinting_complete == False)
    ).first()
    if not incubation:
        return None

    energy_pct = (axo.energy_current / axo.stat_stamina) if axo.stat_stamina > 0 else 0.0

    result = ImprintingGameResult(
        won=is_win,
        had_jackpot_bonus=had_jackpot,
        mark_accuracy=mark_accuracy,
        session_game_count=incubation.imprinting_games_played + 1,
        padrino_energy_pct=min(1.0, energy_pct),
        padrino_sal=axo.stat_salinity,
    )
    deltas = compute_deltas(result)
    apply_deltas_to_incubation(incubation, deltas)

    # Verificar si completó el imprinting
    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    if incubation.imprinting_games_played >= required:
        incubation.imprinting_complete = True

    session.add(incubation)
    # No commit aquí — el caller ya commitea todo junto

    return {
        "imprinting_game": incubation.imprinting_games_played,
        "required": required,
        "complete": incubation.imprinting_complete,
        "deltas": {
            "suerte": round(deltas.luck_delta, 1),
            "ojo":    round(deltas.focus_delta, 1),
            "pila":   round(deltas.stamina_delta, 1),
            "sal":    round(deltas.salinity_delta, 1),
        },
    }
```

- [ ] **Step 3: Llamar al helper en el endpoint de juego**

En el endpoint `POST /play` de game.py, después de `axo.status = "idle"` (línea ~449) y antes del `session.commit()` final, añadir:

```python
    # --- IMPRINTING: aplicar si este axo es padrino de un Webito ---
    # mark_accuracy: ratio de cartas del tablero marcadas en la partida.
    # En modo bot, el miss_chance del axo determina cuántas se pierden.
    from app.api.v1.endpoints.game import _miss_chance  # si es función local
    _miss_rate = _miss_chance(axo.stat_focus) if hasattr(axo, 'stat_focus') else 0.1
    _mark_accuracy = max(0.0, 1.0 - _miss_rate)
    _imprinting_info = _apply_imprinting_if_needed(
        axo=axo,
        is_win=is_win,
        had_jackpot=prize_awarded > win_prize * 1.5,  # heurística: premio > 150% del base = tuvo bonus
        mark_accuracy=_mark_accuracy,
        session=session,
    )
```

Y en el `return` del endpoint, añadir el campo:

```python
        "imprinting": _imprinting_info,   # None si no hay webito en imprinting
```

- [ ] **Step 4: Verificar sintaxis**

```bash
cd backend
python -c "from app.api.v1.endpoints.game import router; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/game.py
git commit -m "feat(imprinting): hook imprinting deltas at end of bot game"
```

---

### Task 6: incubation.py — Eclosión Automática al Completar Imprinting

**Files:**
- Modify: `backend/app/api/v1/endpoints/incubation.py`

Modificar el endpoint `POST /hatch/{incubation_id}` para usar `imprinting_service.final_stats()` cuando `imprinting_complete=True`.

- [ ] **Step 1: Añadir import de final_stats**

```python
from app.services.imprinting_service import final_stats as imprinting_final_stats
```

- [ ] **Step 2: Localizar el endpoint de eclosión**

Buscar `@router.post("/hatch/{incubation_id}")` o similar en `incubation.py` (alrededor de línea 900+).

- [ ] **Step 3: Reemplazar bloque de cálculo de stats finales**

Reemplazar el bloque que calculaba stats desde `calor_actual` y `bonus_*` (líneas ~773-798) con:

```python
    # --- IMPRINTING: stats finales ---
    if incubation.imprinting_complete:
        # Usar los stats moldeados por el imprinting
        computed = imprinting_final_stats(incubation)
        final_luck      = computed["stat_luck"]
        final_focus     = computed["stat_focus"]
        final_stamina   = computed["stat_stamina"]
        final_salinity  = computed["stat_salinity"]
        final_agility   = computed["stat_agility"]
        final_charisma  = 0.0
        final_wisdom    = 0.0
        final_strength  = 0.0
        purity          = 100.0
        mutation_type   = "imprinting"
        salinity_penalty = 0.0
    else:
        raise HTTPException(
            status_code=400,
            detail="El imprinting no está completo. Juega más partidas con tu padrino.",
        )
```

- [ ] **Step 4: Actualizar el response JSON del endpoint de eclosión**

En el `return` de la eclosión (líneas ~1002-1025), reemplazar las claves de stats:

```python
            "stats": {
                "suerte":   nuevo_axolote.stat_luck,
                "ojo":      nuevo_axolote.stat_focus,
                "pila":     nuevo_axolote.stat_stamina,
                "sal":      nuevo_axolote.stat_salinity,
                # Campos legacy (para compatibilidad con ABI)
                "salinity": nuevo_axolote.stat_salinity,
                "luck":     nuevo_axolote.stat_luck,
                "focus":    nuevo_axolote.stat_focus,
                "stamina":  nuevo_axolote.stat_stamina,
                "agility":  nuevo_axolote.stat_agility,
                "charisma": 0.0,
                "wisdom":   0.0,
                "strength": 0.0,
            },
            "imprinting_summary": {
                "padrino_id":    incubation.imprinting_padrino_id,
                "games_played":  incubation.imprinting_games_played,
            },
```

- [ ] **Step 5: Verificar**

```bash
cd backend
python -c "from app.api.v1.endpoints.incubation import router; print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/v1/endpoints/incubation.py
git commit -m "feat(imprinting): auto-eclosion uses imprinting final_stats"
```

---

### Task 7: user.py — player_luck() + Glotón fix

**Files:**
- Modify: `backend/app/api/v1/endpoints/user.py`
- Modify: `backend/app/scripts/seed_catalog.py`

- [ ] **Step 1: Añadir función player_luck y exponerla en el perfil**

En `backend/app/api/v1/endpoints/user.py`, añadir después de los imports:

```python
def _player_luck(axolotitos: list) -> float:
    """SUERTE del usuario = promedio de stat_luck de todos sus Axolotitos."""
    if not axolotitos:
        return 0.0
    return sum(a.stat_luck for a in axolotitos) / len(axolotitos)
```

En el endpoint `GET /profile` o `GET /me` (el que devuelve el perfil del usuario), añadir al response:

```python
    axolotitos = session.exec(
        select(Axolotito).where(Axolotito.user_id == verified_user_id)
    ).all()
    player_luck_value = _player_luck(axolotitos)
    # ... agregar al return dict:
    # "player_luck": round(player_luck_value, 1),
```

- [ ] **Step 2: Verificar sintaxis user.py**

```bash
cd backend
python -c "from app.api.v1.endpoints.user import router; print('OK')"
```

- [ ] **Step 3: Fix Glotón en seed_catalog.py**

En `backend/app/scripts/seed_catalog.py`, buscar la entrada de la naturaleza Glotón (puede estar como `"gluttony"` o `"gloton"`) y modificar su `item_metadata`:

```python
# Antes:
{
    "nature": "gloton",
    "stamina_food_bonus_pct": 30,
    # sin penalización
}

# Después:
{
    "nature": "gloton",
    "stamina_food_bonus_pct": 30,
    "focus_modifier": -10,   # −10 OJO al nacer
}
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/user.py backend/app/scripts/seed_catalog.py
git commit -m "feat(user): add player_luck to profile; fix Gloton nature -10 OJO"
```

---

## FASE 3 — Sistema de Eventos de Modo Manual

### Task 8: admin_events.py — CRUD + Broadcast

**Files:**
- Create: `backend/app/api/v1/endpoints/admin_events.py`
- Modify: `backend/app/main.py` — registrar router

- [ ] **Step 1: Crear el endpoint**

```python
# backend/app/api/v1/endpoints/admin_events.py
"""
admin_events.py — CRUD de eventos de modo manual para admins.

Endpoints:
  POST   /api/v1/admin/events
  GET    /api/v1/admin/events
  PATCH  /api/v1/admin/events/{id}
  DELETE /api/v1/admin/events/{id}
  POST   /api/v1/admin/events/{id}/broadcast
  GET    /api/v1/admin/events/{id}/stats
"""
from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id, require_admin
from app.database import get_session
from app.models.manual_mode_event import ManualModeEvent

router = APIRouter()


# --- Schemas ---

class EventCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    daily_open_time: Optional[time] = None
    daily_close_time: Optional[time] = None
    timezone: str = "America/Mexico_City"
    tabla_cost_gal: float = 10.0
    max_tablas_per_player: int = 3
    prize_pool_pct: float = 0.80
    platform_fee_pct: float = 0.10
    jackpot_contribution_pct: float = 0.10
    bonus_gal_on_win: float = 0.0
    drop_multiplier: float = 1.0
    xp_bonus_pct: float = 0.0
    griton_delay_ms: int = 2000
    griton_repeats: bool = True
    win_condition: str = "tabla_llena"
    max_game_duration_s: Optional[int] = None
    tie_behavior: str = "split"
    allowed_modes: str = "both"
    max_players_per_room: int = 10
    min_players_to_start: int = 2
    room_wait_timeout_s: int = 90
    vip_only: bool = False
    min_axo_level: Optional[int] = None
    first_time_only: bool = False
    broadcast_message: Optional[str] = None
    auto_reminder: bool = True
    notify_room_start: bool = True
    post_event_summary: bool = True


class EventPatch(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    daily_open_time: Optional[time] = None
    daily_close_time: Optional[time] = None
    is_active: Optional[bool] = None
    broadcast_message: Optional[str] = None
    bonus_gal_on_win: Optional[float] = None
    drop_multiplier: Optional[float] = None
    griton_delay_ms: Optional[int] = None
    max_players_per_room: Optional[int] = None


# --- Endpoints ---

@router.post("")
def create_event(
    payload: EventCreate,
    session: Session = Depends(get_session),
    admin_id: str = Depends(require_admin),
):
    """Crea un nuevo evento de modo manual."""
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date debe ser >= start_date.")
    if payload.prize_pool_pct + payload.platform_fee_pct + payload.jackpot_contribution_pct > 1.01:
        raise HTTPException(status_code=400, detail="La suma de porcentajes no puede superar 100%.")

    event = ManualModeEvent(
        created_by=admin_id,
        **payload.model_dump(),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("")
def list_events(
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Lista todos los eventos ordenados por fecha de inicio descendente."""
    events = session.exec(
        select(ManualModeEvent).order_by(ManualModeEvent.start_date.desc())
    ).all()
    now = datetime.utcnow()

    def status(e: ManualModeEvent) -> str:
        today = now.date()
        if not e.is_active:
            return "cancelled"
        if e.end_date < today:
            return "past"
        if e.start_date > today:
            return "upcoming"
        return "active"

    return [{"event": e, "status": status(e)} for e in events]


@router.patch("/{event_id}")
def patch_event(
    event_id: int,
    payload: EventPatch,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Actualiza campos de un evento. Solo si no ha terminado."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    if event.end_date < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="No se puede editar un evento terminado.")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(event, field, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
def cancel_event(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Desactiva (cancela) un evento."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    event.is_active = False
    session.add(event)
    session.commit()
    return {"message": f"Evento '{event.name}' cancelado."}


@router.post("/{event_id}/broadcast")
def send_broadcast(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """
    Marca el evento como 'convocatoria enviada'.
    La notificación real se implementa en event_notification_service.py (Task 9).
    """
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    if not event.broadcast_message:
        raise HTTPException(status_code=400, detail="El evento no tiene mensaje de convocatoria.")

    event.broadcast_sent = True
    event.broadcast_sent_at = datetime.utcnow()
    session.add(event)
    session.commit()

    # TODO Task 9: llamar event_notification_service.send_broadcast(event)

    return {
        "message": f"Convocatoria marcada como enviada para '{event.name}'.",
        "sent_at": event.broadcast_sent_at.isoformat(),
    }


@router.get("/{event_id}/stats")
def event_stats(
    event_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_admin),
):
    """Stats básicos de un evento (placeholder — se expande con logs de partida)."""
    event = session.get(ManualModeEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    return {
        "event_id": event_id,
        "name": event.name,
        "broadcast_sent": event.broadcast_sent,
        # TODO: agregar conteo de partidas y jugadores desde MultiplayerGameLog
    }
```

- [ ] **Step 2: Registrar en main.py**

En `backend/app/main.py`, línea 6 (imports de endpoints):

```python
from app.api.v1.endpoints import (
    bank, user, shop, incubation, metadata, legacy, board, game,
    ranking, multiplayer, checkout, market, leonardo, admin, whitelist,
    codes, f2p, tutorial, webito_slots, admin_events,
)
```

Y en el bloque de `app.include_router(...)` (buscar los otros routers):

```python
app.include_router(admin_events.router, prefix="/api/v1/admin/events", tags=["admin-events"])
```

- [ ] **Step 3: Verificar**

```bash
cd backend
python -c "from app.api.v1.endpoints.admin_events import router; print('OK', [r.path for r in router.routes])"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/admin_events.py backend/app/main.py
git commit -m "feat(events): add admin events CRUD endpoints"
```

---

### Task 9: events.py — Endpoint Público + Registro de Routers

**Files:**
- Create: `backend/app/api/v1/endpoints/events.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Crear endpoint público**

```python
# backend/app/api/v1/endpoints/events.py
"""
events.py — Endpoint público para consultar el estado del modo manual.

GET /api/v1/events/manual-mode
→ { active_event: {...} | null, next_event: {...} | null }
"""
from datetime import date, datetime, time

from fastapi import APIRouter, Depends
from sqlmodel import Session, and_, or_, select

from app.database import get_session
from app.models.manual_mode_event import ManualModeEvent

router = APIRouter()


def _event_is_active_now(event: ManualModeEvent) -> bool:
    """Comprueba si el evento está activo en este momento (UTC, sin conversión tz)."""
    now = datetime.utcnow()
    today = now.date()
    current_time = now.time()

    if not event.is_active:
        return False
    if event.start_date > today or event.end_date < today:
        return False
    if event.daily_open_time is None:
        return True  # todo el día
    return event.daily_open_time <= current_time <= event.daily_close_time


def _event_is_upcoming(event: ManualModeEvent) -> bool:
    today = datetime.utcnow().date()
    return event.is_active and event.start_date > today


@router.get("/manual-mode")
def manual_mode_status(session: Session = Depends(get_session)):
    """
    Devuelve el evento activo ahora y el próximo evento programado.
    Usado por el frontend para mostrar/deshabilitar el botón de modo manual.
    """
    all_events = session.exec(
        select(ManualModeEvent)
        .where(ManualModeEvent.is_active == True)
        .order_by(ManualModeEvent.start_date.asc())
    ).all()

    active = next((e for e in all_events if _event_is_active_now(e)), None)
    upcoming = next((e for e in all_events if _event_is_upcoming(e)), None)

    def _serialize(e: ManualModeEvent | None) -> dict | None:
        if e is None:
            return None
        return {
            "id": e.id,
            "name": e.name,
            "start_date": e.start_date.isoformat(),
            "end_date": e.end_date.isoformat(),
            "daily_open_time": e.daily_open_time.isoformat() if e.daily_open_time else None,
            "daily_close_time": e.daily_close_time.isoformat() if e.daily_close_time else None,
            "bonus_gal_on_win": e.bonus_gal_on_win,
            "drop_multiplier": e.drop_multiplier,
            "xp_bonus_pct": e.xp_bonus_pct,
            "griton_delay_ms": e.griton_delay_ms,
            "win_condition": e.win_condition,
            "allowed_modes": e.allowed_modes,
            "max_players_per_room": e.max_players_per_room,
        }

    return {
        "active_event": _serialize(active),
        "next_event": _serialize(upcoming) if active is None else None,
    }
```

- [ ] **Step 2: Registrar en main.py**

Añadir import y router:

```python
from app.api.v1.endpoints import (
    ..., admin_events, events,
)
# ...
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
```

- [ ] **Step 3: Test rápido manual**

```bash
cd backend
uvicorn app.main:app --reload &
sleep 3
curl http://localhost:8000/api/v1/events/manual-mode
# Esperado: {"active_event": null, "next_event": null}
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/events.py backend/app/main.py
git commit -m "feat(events): add public manual-mode status endpoint"
```

---

## FASE 4 — Frontend

### Task 10: ManualModeButton.tsx

**Files:**
- Create: `frontend/components/ManualModeButton.tsx`

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/ManualModeButton.tsx
"use client";
import { useEffect, useState } from "react";

interface EventInfo {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  daily_open_time: string | null;
  daily_close_time: string | null;
  bonus_gal_on_win: number;
  drop_multiplier: number;
}

interface ManualModeStatus {
  active_event: EventInfo | null;
  next_event: EventInfo | null;
}

interface Props {
  onPlay: () => void;
}

export function ManualModeButton({ onPlay }: Props) {
  const [status, setStatus] = useState<ManualModeStatus | null>(null);
  const [timeLeft, setTimeLeft] = useState<string>("");

  useEffect(() => {
    fetch("/api/v1/events/manual-mode")
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ active_event: null, next_event: null }));
  }, []);

  // Countdown al próximo evento
  useEffect(() => {
    if (!status?.next_event) return;
    const interval = setInterval(() => {
      const target = new Date(`${status.next_event!.start_date}T${status.next_event!.daily_open_time ?? "00:00:00"}`);
      const diff = target.getTime() - Date.now();
      if (diff <= 0) {
        setTimeLeft("¡Abriendo!");
        clearInterval(interval);
        return;
      }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      setTimeLeft(d > 0 ? `${d}d ${h}h` : `${h}h ${m}m`);
    }, 1000);
    return () => clearInterval(interval);
  }, [status?.next_event]);

  if (!status) {
    return (
      <button disabled className="opacity-40 px-6 py-3 rounded-2xl bg-white/5 text-white/30 font-bold text-sm">
        Cargando...
      </button>
    );
  }

  const { active_event, next_event } = status;

  if (active_event) {
    return (
      <div className="flex flex-col items-center gap-2">
        <div className="text-xs font-bold text-green-400 uppercase tracking-widest">
          🎉 {active_event.name}
        </div>
        {active_event.bonus_gal_on_win > 0 && (
          <div className="text-xs text-yellow-400 font-semibold">
            +{active_event.bonus_gal_on_win} GAL al ganar
            {active_event.drop_multiplier > 1 && ` · ${active_event.drop_multiplier}× drops`}
          </div>
        )}
        <button
          onClick={onPlay}
          className="px-8 py-3 rounded-2xl bg-green-400/20 border border-green-400/40 text-green-400 font-bold text-sm hover:bg-green-400/30 transition-all"
        >
          Jugar modo manual →
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        disabled
        className="px-8 py-3 rounded-2xl bg-white/5 border border-white/10 text-white/30 font-bold text-sm cursor-not-allowed"
      >
        🌙 Modo manual cerrado
      </button>
      {next_event ? (
        <div className="text-center">
          <div className="text-2xl font-black text-blue-400">{timeLeft}</div>
          <div className="text-xs text-white/30 mt-1">
            {next_event.name} · {new Date(next_event.start_date).toLocaleDateString("es-MX", { month: "short", day: "numeric" })}
          </div>
        </div>
      ) : (
        <div className="text-xs text-white/25">Próximamente</div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep ManualModeButton
```

Esperado: sin errores relacionados con ManualModeButton.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/ManualModeButton.tsx
git commit -m "feat(frontend): add ManualModeButton with event countdown"
```

---

### Task 11: ImprintingProgress.tsx

**Files:**
- Create: `frontend/components/ImprintingProgress.tsx`

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/ImprintingProgress.tsx
"use client";

interface ImprintingStatus {
  incubation_id: number;
  imprinting_started: boolean;
  imprinting_complete: boolean;
  games_played: number;
  required_games: number;
  padrino_name: string | null;
  current_stats: {
    suerte_delta: number;
    ojo_delta: number;
    pila_delta: number;
    sal_delta: number;
  };
}

interface Props {
  status: ImprintingStatus;
  onSelectPadrino?: () => void;
}

function DeltaChip({ value, label, color }: { value: number; label: string; color: string }) {
  const positive = value >= 0;
  const bg = positive ? "rgba(74,222,128,0.12)" : "rgba(239,68,68,0.1)";
  const textColor = positive ? "#4ade80" : "#f87171";
  return (
    <div className="flex flex-col items-center gap-1 px-3 py-2 rounded-xl" style={{ background: bg }}>
      <span className="text-xs font-bold" style={{ color: textColor }}>
        {positive ? "+" : ""}{value}
      </span>
      <span className="text-[10px] font-semibold opacity-50">{label}</span>
    </div>
  );
}

export function ImprintingProgress({ status, onSelectPadrino }: Props) {
  const pct = status.required_games > 0
    ? Math.min(1, status.games_played / status.required_games)
    : 0;
  const dots = Array.from({ length: status.required_games });

  if (!status.imprinting_started) {
    return (
      <div className="flex flex-col items-center gap-3 p-4 rounded-2xl bg-white/3 border border-white/8">
        <div className="text-sm font-bold text-white/60">🥚 ADN incompleto</div>
        <div className="text-xs text-white/30 text-center">
          Elige un padrino para iniciar el imprinting
        </div>
        {onSelectPadrino && (
          <button
            onClick={onSelectPadrino}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-purple-400/15 border border-purple-400/30 text-purple-300"
          >
            Elegir padrino →
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-4 rounded-2xl bg-white/3 border border-white/8">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold text-white/50 uppercase tracking-widest">Imprinting</div>
        {status.padrino_name && (
          <div className="text-xs text-purple-300 font-semibold">
            🐾 Padrino: {status.padrino_name}
          </div>
        )}
      </div>

      {/* Dots de progreso */}
      <div className="flex gap-2 justify-center">
        {dots.map((_, i) => (
          <div
            key={i}
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all"
            style={{
              background: i < status.games_played ? "rgba(167,139,250,0.3)" : "rgba(255,255,255,0.05)",
              borderColor: i < status.games_played ? "rgba(167,139,250,0.6)" : "rgba(255,255,255,0.1)",
              color: i < status.games_played ? "#c084fc" : "rgba(255,255,255,0.2)",
            }}
          >
            {i < status.games_played ? "✓" : i + 1}
          </div>
        ))}
      </div>

      <div className="text-center text-xs text-white/40">
        {status.games_played}/{status.required_games} partidas
        {status.imprinting_complete && (
          <span className="ml-2 text-green-400 font-bold">· ¡Listo para nacer!</span>
        )}
      </div>

      {/* Deltas acumulados */}
      {status.games_played > 0 && (
        <div className="flex gap-2 justify-center flex-wrap">
          <DeltaChip value={status.current_stats.suerte_delta} label="SUERTE" color="yellow" />
          <DeltaChip value={status.current_stats.ojo_delta}    label="OJO"    color="teal" />
          <DeltaChip value={status.current_stats.pila_delta}   label="PILA"   color="blue" />
          <DeltaChip value={status.current_stats.sal_delta}    label="SAL"    color="red" />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep ImprintingProgress
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/ImprintingProgress.tsx
git commit -m "feat(frontend): add ImprintingProgress component"
```

---

### Task 12: BirthCeremony.tsx

**Files:**
- Create: `frontend/components/BirthCeremony.tsx`

- [ ] **Step 1: Crear componente de ceremonia**

```tsx
// frontend/components/BirthCeremony.tsx
"use client";
import { useEffect, useState } from "react";

interface BirthStats {
  suerte: number;
  ojo: number;
  pila: number;
  sal: number;
}

interface Props {
  axolotitoName: string;
  nature: string;
  natureIcon: string;
  stats: BirthStats;
  rarity: "common" | "rare" | "legendary";
  padrinoName: string;
  gamesWon: number;
  totalGames: number;
  onComplete: () => void;
}

const NATURE_COLORS: Record<string, string> = {
  suertudo:   "#fbbf24",
  metodico:   "#2dd4bf",
  gloton:     "#f97316",
  timido:     "#a78bfa",
  hiperactivo:"#f87171",
  sabio:      "#60a5fa",
};

const STAT_CONFIG = [
  { key: "suerte" as const, icon: "✨", label: "SUERTE", color: "#fbbf24" },
  { key: "ojo"    as const, icon: "👁️", label: "OJO",    color: "#2dd4bf" },
  { key: "pila"   as const, icon: "🔋", label: "PILA",   color: "#60a5fa" },
  { key: "sal"    as const, icon: "🧂", label: "SAL",    color: "#f87171" },
];

type Step = "dark" | "crack" | "name" | "nature" | "stats" | "flavor" | "done";

export function BirthCeremony({
  axolotitoName, nature, natureIcon, stats, rarity,
  padrinoName, gamesWon, totalGames, onComplete,
}: Props) {
  const [step, setStep] = useState<Step>("dark");
  const [revealedStats, setRevealedStats] = useState<number>(0);
  const [displayName, setDisplayName] = useState("");

  const stepDelay: Record<Step, number> = {
    dark:   1800,
    crack:  1500,
    name:   2000,
    nature: 2000,
    stats:  totalGames * 800 + 1200,
    flavor: 2500,
    done:   0,
  };

  const STEPS: Step[] = ["dark", "crack", "name", "nature", "stats", "flavor", "done"];

  useEffect(() => {
    if (step === "done") return;
    const idx = STEPS.indexOf(step);
    const delay = stepDelay[step];
    const timer = setTimeout(() => setStep(STEPS[idx + 1] as Step), delay);
    return () => clearTimeout(timer);
  }, [step]);

  // Typewriter effect for name
  useEffect(() => {
    if (step !== "name") return;
    let i = 0;
    const interval = setInterval(() => {
      setDisplayName(axolotitoName.slice(0, i + 1));
      i++;
      if (i >= axolotitoName.length) clearInterval(interval);
    }, 120);
    return () => clearInterval(interval);
  }, [step, axolotitoName]);

  // Stats reveal one by one
  useEffect(() => {
    if (step !== "stats") return;
    let i = 0;
    const interval = setInterval(() => {
      setRevealedStats(i + 1);
      i++;
      if (i >= 4) clearInterval(interval);
    }, 800);
    return () => clearInterval(interval);
  }, [step]);

  const natureColor = NATURE_COLORS[nature?.toLowerCase()] ?? "#a78bfa";
  const isLegendary = rarity === "legendary";
  const isRare = rarity === "rare" || isLegendary;

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center z-50"
      style={{
        background: step === "dark"
          ? "#000"
          : `radial-gradient(ellipse at 50% 80%, ${natureColor}18 0%, #050508 70%)`,
        transition: "background 1s ease",
      }}
    >
      {/* Step 1-2: Huevo */}
      {(step === "dark" || step === "crack") && (
        <div
          className="text-8xl transition-all duration-700"
          style={{
            filter: step === "crack" ? `drop-shadow(0 0 30px ${natureColor})` : "none",
            transform: step === "crack" ? "scale(1.15)" : "scale(1)",
          }}
        >
          {step === "dark" ? "🥚" : "✨"}
        </div>
      )}

      {/* Step 3+: Axolotito + nombre + nature + stats */}
      {step !== "dark" && step !== "crack" && (
        <div className="flex flex-col items-center gap-5 px-6 max-w-sm w-full">
          {/* Axolotito */}
          <div
            className="text-7xl"
            style={{ filter: `drop-shadow(0 0 ${isLegendary ? 40 : 20}px ${natureColor})` }}
          >
            🦎
          </div>

          {/* Nombre */}
          <div className="text-3xl font-black text-white tracking-wide min-h-[2.5rem]">
            {displayName}
            {step === "name" && <span className="animate-pulse">|</span>}
          </div>

          {/* Naturaleza */}
          {(step === "nature" || step === "stats" || step === "flavor" || step === "done") && (
            <div
              className="text-sm font-bold uppercase tracking-widest px-4 py-1.5 rounded-full"
              style={{ background: `${natureColor}20`, color: natureColor, border: `1px solid ${natureColor}40` }}
            >
              {natureIcon} Naturaleza {nature}
            </div>
          )}

          {/* Stats como cartas */}
          {(step === "stats" || step === "flavor" || step === "done") && (
            <div className="flex gap-3 justify-center w-full">
              {STAT_CONFIG.map((s, i) => (
                <div
                  key={s.key}
                  className="flex-1 flex flex-col items-center gap-1 py-3 rounded-2xl transition-all duration-500"
                  style={{
                    background: i < revealedStats ? `${s.color}18` : "rgba(255,255,255,0.03)",
                    border: `1.5px solid ${i < revealedStats ? s.color + "40" : "rgba(255,255,255,0.08)"}`,
                    opacity: i < revealedStats ? 1 : 0.2,
                    transform: i < revealedStats ? "scale(1)" : "scale(0.9)",
                  }}
                >
                  <span className="text-xl">{s.icon}</span>
                  <span className="text-[10px] font-bold uppercase opacity-50">{s.label}</span>
                  <span
                    className="text-xl font-black"
                    style={{ color: i < revealedStats ? s.color : "transparent" }}
                  >
                    {stats[s.key]}
                  </span>
                  {s.key === "sal" && i < revealedStats && stats.sal < 15 && (
                    <span className="text-[9px] text-green-400 font-bold">¡Bajo!</span>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Flavor text */}
          {(step === "flavor" || step === "done") && (
            <p className="text-sm text-white/35 italic text-center leading-relaxed">
              "Aprendió jugando con {padrinoName}. Ganaron {gamesWon} de {totalGames} partidas."
            </p>
          )}

          {/* Botón final */}
          {step === "done" && (
            <button
              onClick={onComplete}
              className="mt-2 px-8 py-3 rounded-2xl font-bold text-sm transition-all"
              style={{
                background: `${natureColor}20`,
                border: `1.5px solid ${natureColor}40`,
                color: natureColor,
              }}
            >
              Conocer a {axolotitoName} →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep BirthCeremony
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/BirthCeremony.tsx
git commit -m "feat(frontend): add BirthCeremony cinematographic component"
```

---

### Task 13: Criadero.tsx — Refactor a Imprinting

**Files:**
- Modify: `frontend/components/Criadero.tsx` (o ruta equivalente)

- [ ] **Step 1: Localizar el archivo**

```bash
find frontend -name "Criadero*" -o -name "criadero*" 2>/dev/null
```

- [ ] **Step 2: Reemplazar el bloque de cariñitos (acariciar/cantar/alimentar)**

Buscar el JSX que renderiza los 3 botones de cuidado con cooldown (buscar `"acariciar"`, `"cantar"`, `"alimentar"` en el archivo). Reemplazar esas secciones con:

```tsx
import { ImprintingProgress } from "@/components/ImprintingProgress";
import { BirthCeremony } from "@/components/BirthCeremony";

// En el estado del componente:
const [imprintingStatus, setImprintingStatus] = useState<any>(null);
const [showCeremony, setShowCeremony] = useState(false);
const [ceremonyData, setCeremonyData] = useState<any>(null);

// Fetch del status de imprinting para el huevo seleccionado:
useEffect(() => {
  if (!selectedIncubationId) return;
  fetch(`/api/v1/incubation/imprinting-status/${selectedIncubationId}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
    .then((r) => r.json())
    .then(setImprintingStatus);
}, [selectedIncubationId]);

// Handler de eclosión cuando imprinting_complete:
const handleHatch = async () => {
  const res = await fetch(`/api/v1/incubation/hatch/${selectedIncubationId}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const data = await res.json();
  if (data.axolotito) {
    setCeremonyData(data);
    setShowCeremony(true);
  }
};

// En el JSX, reemplazar los botones de cuidado con:
{imprintingStatus && (
  <ImprintingProgress
    status={imprintingStatus}
    onSelectPadrino={() => setShowPadrinoSelector(true)}
  />
)}
{imprintingStatus?.imprinting_complete && (
  <button onClick={handleHatch}
    className="w-full py-3 rounded-2xl bg-green-400/20 border border-green-400/40 text-green-400 font-bold text-sm mt-3">
    🥚 ¡Eclosionar!
  </button>
)}

{showCeremony && ceremonyData && (
  <BirthCeremony
    axolotitoName={ceremonyData.axolotito.name}
    nature={ceremonyData.axolotito.nature ?? "desconocida"}
    natureIcon="🌿"
    stats={{
      suerte: Math.round(ceremonyData.axolotito.stats.suerte),
      ojo:    Math.round(ceremonyData.axolotito.stats.ojo),
      pila:   ceremonyData.axolotito.stats.pila,
      sal:    Math.round(ceremonyData.axolotito.stats.sal),
    }}
    rarity={ceremonyData.axolotito.rarity ?? "common"}
    padrinoName={imprintingStatus?.padrino_name ?? "tu Axolotito"}
    gamesWon={Math.round((imprintingStatus?.required_games ?? 3) * 0.6)}
    totalGames={imprintingStatus?.required_games ?? 3}
    onComplete={() => { setShowCeremony(false); router.refresh(); }}
  />
)}
```

- [ ] **Step 3: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep -i criadero
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/Criadero.tsx
git commit -m "feat(frontend): refactor Criadero to use imprinting system"
```

---

### Task 14: Página Admin de Eventos

**Files:**
- Create: `frontend/app/admin/events/page.tsx` (o `frontend/pages/admin/events.tsx` según estructura del proyecto)

- [ ] **Step 1: Verificar estructura de páginas admin**

```bash
find frontend -path "*/admin*" -name "*.tsx" 2>/dev/null | head -10
```

- [ ] **Step 2: Crear la página**

```tsx
// frontend/app/admin/events/page.tsx
"use client";
import { useEffect, useState } from "react";
import { usePrivy } from "@privy-io/react-auth";

interface EventData {
  id?: number;
  name: string;
  start_date: string;
  end_date: string;
  daily_open_time: string;
  daily_close_time: string;
  tabla_cost_gal: number;
  max_tablas_per_player: number;
  prize_pool_pct: number;
  bonus_gal_on_win: number;
  drop_multiplier: number;
  xp_bonus_pct: number;
  griton_delay_ms: number;
  griton_repeats: boolean;
  win_condition: string;
  max_players_per_room: number;
  min_players_to_start: number;
  room_wait_timeout_s: number;
  vip_only: boolean;
  broadcast_message: string;
  auto_reminder: boolean;
  notify_room_start: boolean;
  post_event_summary: boolean;
}

const EMPTY_EVENT: EventData = {
  name: "", start_date: "", end_date: "",
  daily_open_time: "15:00", daily_close_time: "23:00",
  tabla_cost_gal: 10, max_tablas_per_player: 3,
  prize_pool_pct: 0.80, bonus_gal_on_win: 0,
  drop_multiplier: 1.0, xp_bonus_pct: 0,
  griton_delay_ms: 2000, griton_repeats: true,
  win_condition: "tabla_llena",
  max_players_per_room: 10, min_players_to_start: 2, room_wait_timeout_s: 90,
  vip_only: false, broadcast_message: "",
  auto_reminder: true, notify_room_start: true, post_event_summary: true,
};

export default function AdminEventsPage() {
  const { getAccessToken } = usePrivy();
  const [events, setEvents] = useState<any[]>([]);
  const [form, setForm] = useState<EventData>(EMPTY_EVENT);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  const headers = async () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${await getAccessToken()}`,
  });

  const load = async () => {
    const res = await fetch("/api/v1/admin/events", { headers: await headers() });
    const data = await res.json();
    setEvents(data);
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    setSaving(true);
    const res = await fetch("/api/v1/admin/events", {
      method: "POST",
      headers: await headers(),
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (res.ok) {
      setMsg(`✅ Evento "${data.name}" creado`);
      setForm(EMPTY_EVENT);
      load();
    } else {
      setMsg(`❌ Error: ${data.detail}`);
    }
    setSaving(false);
  };

  const handleBroadcast = async (id: number) => {
    const res = await fetch(`/api/v1/admin/events/${id}/broadcast`, {
      method: "POST",
      headers: await headers(),
    });
    const data = await res.json();
    setMsg(res.ok ? `📣 ${data.message}` : `❌ ${data.detail}`);
    load();
  };

  const handleCancel = async (id: number) => {
    if (!confirm("¿Cancelar este evento?")) return;
    await fetch(`/api/v1/admin/events/${id}`, { method: "DELETE", headers: await headers() });
    load();
  };

  const f = (key: keyof EventData) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const val = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked
              : e.target.type === "number"   ? Number(e.target.value)
              : e.target.value;
    setForm(prev => ({ ...prev, [key]: val }));
  };

  return (
    <div className="max-w-3xl mx-auto p-6 text-white">
      <h1 className="text-2xl font-black mb-6">🎮 Eventos de Modo Manual</h1>

      {msg && <div className="mb-4 p-3 rounded-xl bg-white/5 text-sm">{msg}</div>}

      {/* FORM */}
      <div className="bg-white/3 border border-white/8 rounded-2xl p-6 mb-8">
        <h2 className="text-sm font-bold uppercase tracking-widest text-white/40 mb-4">Crear evento</h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            ["name", "Nombre del evento", "text", "col-span-2"],
            ["start_date", "Fecha inicio", "date"],
            ["end_date", "Fecha fin", "date"],
            ["daily_open_time", "Hora apertura", "time"],
            ["daily_close_time", "Hora cierre", "time"],
            ["tabla_cost_gal", "Costo por tabla (GAL)", "number"],
            ["max_tablas_per_player", "Tablas por jugador", "number"],
            ["bonus_gal_on_win", "Bonus GAL al ganar", "number"],
            ["drop_multiplier", "Multiplicador drops", "number"],
            ["griton_delay_ms", "Delay gritón (ms)", "number"],
            ["max_players_per_room", "Máx jugadores/sala", "number"],
            ["min_players_to_start", "Mín para iniciar", "number"],
          ].map(([key, label, type, cls]) => (
            <div key={key} className={cls ?? ""}>
              <label className="text-[10px] font-bold uppercase text-white/30 block mb-1">{label}</label>
              <input
                type={type}
                value={String(form[key as keyof EventData])}
                onChange={f(key as keyof EventData)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/70 font-mono"
              />
            </div>
          ))}
          <div className="col-span-2">
            <label className="text-[10px] font-bold uppercase text-white/30 block mb-1">Mensaje de convocatoria</label>
            <textarea
              value={form.broadcast_message}
              onChange={f("broadcast_message")}
              rows={3}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/70 resize-none"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button onClick={handleSave} disabled={saving}
            className="px-6 py-2 rounded-xl text-sm font-bold bg-purple-400/20 border border-purple-400/40 text-purple-300 disabled:opacity-40">
            {saving ? "Guardando..." : "💾 Guardar"}
          </button>
        </div>
      </div>

      {/* LIST */}
      <div className="flex flex-col gap-3">
        {events.map(({ event: e, status }) => (
          <div key={e.id}
            className="flex items-center gap-4 p-4 rounded-xl bg-white/2 border border-white/7">
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              status === "active" ? "bg-green-400 shadow-[0_0_8px_#4ade80]"
              : status === "upcoming" ? "bg-blue-400"
              : "bg-white/20"
            }`} />
            <div className="flex-1 min-w-0">
              <div className="font-bold text-sm truncate">{e.name}</div>
              <div className="text-xs text-white/35">
                {e.start_date} → {e.end_date} · {e.daily_open_time}–{e.daily_close_time}
                {e.bonus_gal_on_win > 0 && ` · +${e.bonus_gal_on_win} GAL`}
              </div>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              {!e.broadcast_sent && e.broadcast_message && (
                <button onClick={() => handleBroadcast(e.id)}
                  className="px-3 py-1 text-xs font-bold rounded-lg bg-green-400/12 border border-green-400/25 text-green-400">
                  📣
                </button>
              )}
              {status !== "past" && status !== "cancelled" && (
                <button onClick={() => handleCancel(e.id)}
                  className="px-3 py-1 text-xs font-bold rounded-lg bg-red-400/10 border border-red-400/20 text-red-400">
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
        {events.length === 0 && (
          <div className="text-center text-white/25 text-sm py-8">Sin eventos creados</div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep -i "admin/events"
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/admin/events/page.tsx
git commit -m "feat(frontend): add admin events page with full CRUD"
```

---

### Task 15: Alinear TutorialFlow con Imprinting

**Files:**
- Modify: `frontend/components/tutorial/TutorialFlow.tsx`

- [ ] **Step 1: Buscar referencias a los nombres de fases viejos**

```bash
grep -n "Salinidad\|Concentración\|bonus_agility\|bonus_wisdom\|bonus_strength\|cooldown" \
  frontend/components/tutorial/TutorialFlow.tsx | head -20
```

- [ ] **Step 2: Renombrar labels de fases**

Reemplazar los 3 nombres de fases del tutorial:

```tsx
// Antes:
const PHASE_LABELS = ["Salinidad", "Concentración", "Suerte"];

// Después:
const PHASE_LABELS = ["Sal 🧂", "Ojo 👁️", "Suerte & Pila"];
```

- [ ] **Step 3: Actualizar props de stats del tutorial**

El tutorial pasa props como `bonusFocus`, `bonusAgility`, `bonusLuck`, `bonusStamina`, `bonusSalinity`. Añadir alias para los nuevos nombres en el componente que consume estos props:

```tsx
// Donde se renderizan los stats al final del tutorial:
const displayStats = [
  { icon: "✨", label: "SUERTE", value: Math.round(bonusLuck) },
  { icon: "👁️", label: "OJO",   value: Math.round((bonusFocus + bonusAgility) / 2) },
  { icon: "🔋", label: "PILA",  value: Math.round(bonusStamina) },
  { icon: "🧂", label: "SAL",   value: Math.round(bonusSalinity), inverted: true },
];
```

- [ ] **Step 4: Verificar TypeScript**

```bash
cd frontend
npx tsc --noEmit 2>&1 | grep -i tutorial
```

- [ ] **Step 5: Commit final**

```bash
git add frontend/components/tutorial/TutorialFlow.tsx
git commit -m "feat(tutorial): align phase labels and stats display to 4-stat system"
```

---

## Self-Review

**Spec coverage check:**

| Sección del spec | Tarea que la implementa |
|---|---|
| §2 Imprinting — concepto + N partidas por rareza | Task 3 (`required_games_for_rarity`), Task 4 (`start_imprinting`) |
| §2.3 ADN de inicio (base stats) | Task 3 (`initial_base_stats`), Task 4 (endpoint) |
| §2.4 Mapeo evento → delta | Task 3 (`compute_deltas`) |
| §2.5 Progresión visual del ADN | Task 11 (`ImprintingProgress`) |
| §2.6 Quién puede ser padrino | Task 4 (validación de padrino único) |
| §3 Ceremonia cinematográfica 7 pasos | Task 12 (`BirthCeremony`) |
| §3.2 Variación por rareza | Task 12 (isLegendary, isRare flags) |
| §3.3 Nombre generado | Existente en `axo_names.py` — sin cambio requerido |
| §4 Post-nacimiento: equipo + items + niveles | Out of scope (specs separados) |
| §5 ManualModeEvent modelo | Task 1 |
| §5.2 Botón con countdown | Task 10 (`ManualModeButton`) |
| §5.4 `get_active_event` logic | Task 9 (`_event_is_active_now`) |
| §5.5 Notificaciones broadcast | Task 8 (endpoint `/broadcast` marca sent) |
| §5.6 Endpoints admin | Task 8 (`admin_events.py`) |
| §5.7 Endpoint público | Task 9 (`events.py`) |
| §5.3 Admin UI | Task 14 |
| §6 `player_luck()` | Task 7 |
| §7 Glotón −10 OJO | Task 7 (`seed_catalog.py`) |
| Tutorial alignment | Task 15 |

**Nota:** el hook de imprinting para partidas multiplayer (Task 5 replica en `multiplayer.py`) no tiene tarea propia. Añadir como Task 5b si se quiere paridad exacta — la función `_apply_imprinting_if_needed` es la misma, solo llamarla desde `multiplayer.py` igual que se hace en `game.py`.