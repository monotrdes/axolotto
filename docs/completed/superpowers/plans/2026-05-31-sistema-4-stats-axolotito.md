# Sistema de 4 Stats del Axolotito — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar el Axolotito de 8 stats a 4 (✨SUERTE, 👁️OJO, 🔋PILA, 🧂SAL) con nombres mexicanos casuales, nuevas mecánicas de SAL (deck bias solo, slip + entropía multi) y recuperación por PILA, sin migración de DB ni cambios de ABI.

**Architecture:** Las columnas de PostgreSQL y la ABI de la chain NO cambian — los 4 stats retirados (charisma, wisdom, strength, agility) se congelan en 0 o se espejan (agility=focus) al nacer, y se ocultan del UI/API. Todo el cambio es lógica + API responses + frontend. El modo manual deja de aplicar modificadores de stat (el jugador ES el Axolotito). Spec completo: `docs/superpowers/specs/2026-05-31-sistema-4-stats-axolotito-design.md`.

**Tech Stack:** FastAPI, SQLModel, pytest (backend); Next.js 14, TypeScript, Tailwind (frontend).

---

## Asignación de Agentes

| Fase | Tareas | Agente sugerido |
|------|--------|-----------------|
| FASE 0 | Setup ramas/baseline | `devops` o inline |
| FASE 1 | Mecánicas nuevas (deck bias, slip, entropía, recuperación PILA) | `backend-dev` |
| FASE 2 | Eclosión + remover stats muertos | `backend-dev` |
| FASE 3 | API surface (ranking, metadata, admin, multiplayer JSON) | `backend-dev` |
| FASE 4 | Servicios narrativos (dialogue, names, tutorial, manual) | `backend-dev` |
| FASE 5 | Frontend (4 stats UI + tutorial) | `frontend-dev` |
| FASE 6 | QA: simulación + regresión | `qa-tester` |

Cada tarea es autónoma y commitea al terminar. Las FASES 1-4 son backend y deben ir en orden (dependencias de datos). FASE 5 puede empezar cuando FASE 3 termina. FASE 6 al final.

---

## Mapa de Archivos

**Crear:**
- `backend/app/services/sal_service.py` — funciones puras de mecánica SAL (deck bias, slip, entropía).
- `backend/app/services/pila_service.py` — función pura de multiplicador de recuperación.
- `backend/tests/unit/test_sal_service.py`, `backend/tests/unit/test_pila_service.py`.

**Modificar (backend):** `services/multiplayer_service.py`, `api/endpoints/game.py`, `api/endpoints/multiplayer.py`, `api/endpoints/incubation.py`, `api/endpoints/ranking.py`, `api/endpoints/metadata.py`, `api/endpoints/admin.py`, `api/endpoints/board.py`, `services/shop_service.py`, `services/dialogue_engine.py`, `services/axo_names.py`, `services/tutorial_service.py`, `services/manual_game_service.py`, `scripts/seed_catalog.py`, varios `tests/`.

**Modificar (frontend):** `components/AxoStatusBar.tsx`, `Santuario.tsx`, `Criadero.tsx`, `Inventory.tsx`, `MarketP2P.tsx`, `screens/AxoSelectScreen.tsx`, `screens/BoardSelectScreen.tsx`, `screens/CpuSimScreen.tsx`, `tutorial/TutorialFlow.tsx`, `tutorial/TutorialCpuGame.tsx`, `tutorial/dialogues.ts`.

---

## FASE 0 — Baseline

### Task 0: Verificar suite verde antes de empezar

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Correr la suite de tests actual**

Run: `cd backend && python -m pytest tests/ -q 2>&1 | tail -20`
Expected: registrar cuántos pasan/fallan AHORA (baseline). Si algo ya falla, anotarlo para no atribuirlo a este trabajo.

- [ ] **Step 2: Confirmar rama de trabajo**

Run: `git rev-parse --abbrev-ref HEAD`
Expected: `feat/sistema-4-stats`. Si no, `git checkout feat/sistema-4-stats`.

---

## FASE 1 — Mecánicas Nuevas (funciones puras + TDD)

### Task 1: Servicio de mecánica SAL — deck bias (solo/bot)

**Files:**
- Create: `backend/app/services/sal_service.py`
- Test: `backend/tests/unit/test_sal_service.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# backend/tests/unit/test_sal_service.py
import random
from app.services.sal_service import apply_sal_bias, sal_slip_chance, room_entropy


def test_sal_zero_does_not_change_deck():
    rng = random.Random(42)
    deck = list(range(54))
    board = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    result = apply_sal_bias(deck.copy(), board, sal=0.0, rng=rng)
    assert result == deck  # sal=0 → deck idéntico


def test_sal_bias_pushes_board_cards_to_second_half():
    # Con SAL alta y semilla fija, al menos una carta del tablero que estaba
    # en la primera mitad debe terminar en la segunda mitad.
    rng = random.Random(1)
    deck = list(range(54))
    board = list(range(16))  # cartas 0-15, todas en la primera mitad inicialmente
    result = apply_sal_bias(deck.copy(), board, sal=100.0, rng=rng)
    half = len(deck) // 2  # 27
    first_half_board = [c for c in result[:half] if c in board]
    # Con sal=100 (prob 0.5 por carta) deben quedar menos cartas del tablero
    # en la primera mitad que las 16 originales.
    assert len(first_half_board) < 16


def test_sal_bias_preserves_all_cards():
    rng = random.Random(7)
    deck = list(range(54))
    board = [3, 9, 21, 40]
    result = apply_sal_bias(deck.copy(), board, sal=60.0, rng=rng)
    assert sorted(result) == sorted(deck)  # ninguna carta se pierde ni duplica
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `cd backend && python -m pytest tests/unit/test_sal_service.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'app.services.sal_service'`.

- [ ] **Step 3: Implementar `sal_service.py`**

```python
# backend/app/services/sal_service.py
"""
sal_service.py — Mecánica del stat SAL (🧂).

SAL es el anti-stat: a mayor valor, peor desempeño del Axolotito.

  - Solo/Bot:   deck bias  → empuja las cartas del tablero al final del mazo.
  - Multi:      slip       → carta cantada puede "escaparse" sin marcarse.
  - Multi:      entropía    → SAL promedio de la sala = nivel de caos.

Todas las funciones son puras y reciben un rng inyectado para testabilidad.
"""

import random
from typing import List


def apply_sal_bias(
    deck: List[int],
    board_card_ids: List[int],
    sal: float,
    rng: random.Random,
) -> List[int]:
    """
    Empuja las cartas del tablero (board_card_ids) que estén en la primera mitad
    del mazo hacia la segunda mitad, con probabilidad sal/200 por carta.

    Modifica y retorna `deck` (lista de IDs ya barajada). sal=0 → sin cambios.
    """
    if sal <= 0:
        return deck

    prob = min(0.5, sal / 200.0)
    half = len(deck) // 2
    board_set = set(board_card_ids)

    for i in range(half):
        if deck[i] in board_set and rng.random() < prob:
            # Intercambiar con una posición aleatoria de la segunda mitad
            j = rng.randint(half, len(deck) - 1)
            deck[i], deck[j] = deck[j], deck[i]

    return deck


def sal_slip_chance(sal: float) -> float:
    """
    Probabilidad de que una carta cantada se "escape" en multijugador.
    sal/300, máximo 33% (sal=100). Roll independiente del miss chance de OJO.
    """
    return max(0.0, min(0.3333, sal / 300.0))


def room_entropy(sal_values: List[float]) -> float:
    """
    Nivel de caos de una sala multijugador: SAL promedio / 100, en [0, 1].
    Sala vacía → 0.0.
    """
    if not sal_values:
        return 0.0
    return min(1.0, (sum(sal_values) / len(sal_values)) / 100.0)
```

- [ ] **Step 4: Correr el test para verificar que pasa**

Run: `cd backend && python -m pytest tests/unit/test_sal_service.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/sal_service.py backend/tests/unit/test_sal_service.py
git commit -m "feat(sal): servicio de mecanica SAL (deck bias, slip, entropia)"
```

---

### Task 2: Servicio de recuperación por PILA

**Files:**
- Create: `backend/app/services/pila_service.py`
- Test: `backend/tests/unit/test_pila_service.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# backend/tests/unit/test_pila_service.py
from app.services.pila_service import recovery_multiplier


def test_pila_min_is_full_time():
    assert recovery_multiplier(50) == 1.0  # PILA mínima = tiempo completo


def test_pila_max_is_floor():
    assert recovery_multiplier(200) == 0.5  # (1 - 150/300) = 0.5


def test_pila_base_is_between():
    m = recovery_multiplier(100)
    assert 0.8 < m < 0.85  # 1 - 50/300 ≈ 0.833


def test_pila_clamped_below_floor():
    # Aunque la fórmula diera <0.35, el clamp lo mantiene en 0.35
    assert recovery_multiplier(10000) == 0.35
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run: `cd backend && python -m pytest tests/unit/test_pila_service.py -v`
Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: Implementar `pila_service.py`**

```python
# backend/app/services/pila_service.py
"""
pila_service.py — Mecánica del stat PILA (🔋).

PILA determina la energía máxima (ya existente como stat_stamina) y, nuevo,
la velocidad de recuperación al dormir: más PILA = duerme menos.
"""


def recovery_multiplier(pila: float) -> float:
    """
    Multiplicador del tiempo de sueño según PILA (rango stat 50-200).
    sleep_mult = clamp(1.0 - ((pila - 50) / 300), 0.35, 1.0)

    PILA 50  → 1.0  (tiempo completo)
    PILA 100 → ~0.83
    PILA 200 → 0.5
    """
    raw = 1.0 - ((pila - 50.0) / 300.0)
    return max(0.35, min(1.0, raw))
```

- [ ] **Step 4: Correr el test para verificar que pasa**

Run: `cd backend && python -m pytest tests/unit/test_pila_service.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/pila_service.py backend/tests/unit/test_pila_service.py
git commit -m "feat(pila): servicio de velocidad de recuperacion por PILA"
```

---

### Task 3: Integrar deck bias en el modo solo (game.py)

**Files:**
- Modify: `backend/app/api/v1/endpoints/game.py` (zona del `deck` ~línea 307-326)

- [ ] **Step 1: Localizar el shuffle del deck**

Run: `cd backend && grep -n "_rng.shuffle(deck)\|deck = list(card_map" app/api/v1/endpoints/game.py`
Expected: línea ~307-308 (`deck = list(card_map.keys())` seguido de `_rng.shuffle(deck)`).

- [ ] **Step 2: Importar y aplicar el bias después del shuffle**

Añadir el import al principio del archivo (junto a los demás `from app.services...`):

```python
from app.services.sal_service import apply_sal_bias
```

Justo después de `_rng.shuffle(deck)` (la del jugador solo, ~línea 308), insertar:

```python
    # SAL: empuja las cartas del tablero del jugador al final del mazo (solo/bot).
    apply_sal_bias(deck, player_card_ids, axo.stat_salinity, _rng)
```

(`player_card_ids` ya existe en este scope; `_rng` es el SystemRandom del módulo, compatible con `random.Random` para `.random()`/`.randint()`.)

- [ ] **Step 3: Verificar que la suite de game no se rompe**

Run: `cd backend && python -m pytest tests/unit/test_jackpot_inflation.py -q`
Expected: PASS (los tests usan stat_focus=100 / salinity default; el bias con sal baja casi no altera el resultado).

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/game.py
git commit -m "feat(game): aplicar SAL deck bias en modo solo"
```

---

### Task 4: Integrar slip de SAL + entropía en multijugador

**Files:**
- Modify: `backend/app/services/multiplayer_service.py` (loop de cartas ~línea 312-322; map de board ~229-230)

- [ ] **Step 1: Añadir import**

Al principio de `multiplayer_service.py`, junto a los imports de servicios:

```python
from app.services.sal_service import sal_slip_chance, room_entropy
```

- [ ] **Step 2: Guardar la SAL del axo en el dict del board**

En el bloque que arma `participating_boards` (~línea 222-231), añadir `axo_salinity`:

```python
                        participating_boards.append({
                            "board_id": board.id,
                            "axo_id": axo.id,
                            "user_id": axo.user_id,
                            "card_ids": board.card_ids,
                            "is_bot": False,
                            "marked_indices": set(),
                            "axo_focus": axo.stat_focus,
                            "axo_luck": axo.stat_luck,
                            "axo_salinity": axo.stat_salinity,
                        })
```

- [ ] **Step 3: Aplicar el slip en el loop de marcado**

Localizar el bloque (~línea 313-322) que marca cartas de jugadores humanos con el miss_chance de OJO/focus. Reemplazarlo por:

```python
                # 5.1 Actualizar marcas en cada tablero
                for pb in participating_boards:
                    if card_drawn in pb["card_ids"]:
                        idx = pb["card_ids"].index(card_drawn)
                        if pb["is_bot"]:
                            pb["marked_indices"].add(idx)
                        else:
                            # OJO (focus): chance de fallar marcar la carta
                            miss_chance = max(0.0, min(0.3, (100.0 - pb["axo_focus"]) * 0.003))
                            # SAL slip: roll independiente — la carta "se escapa"
                            slip_chance = sal_slip_chance(pb.get("axo_salinity", 0.0))
                            if _rng.random() < miss_chance:
                                continue  # falló por OJO
                            if _rng.random() < slip_chance:
                                continue  # se le escapó por SAL
                            pb["marked_indices"].add(idx)
```

- [ ] **Step 4: Calcular y loguear entropía de sala (antes del loop de cartas)**

Justo después de armar `participating_boards` y antes del `for card_drawn in deck:` (~línea 308), añadir:

```python
            # Entropía de sala: nivel de caos según SAL promedio de humanos.
            human_sal_values = [pb["axo_salinity"] for pb in participating_boards if not pb["is_bot"]]
            sala_entropy = room_entropy(human_sal_values)
            print(f"🌊 [Multiplayer] Sala '{room.name}' entropía SAL: {sala_entropy:.2f}")
```

- [ ] **Step 5: Verificar tests de multiplayer**

Run: `cd backend && python -m pytest tests/unit/test_multiplayer_limits.py tests/unit/test_jackpot_vault.py -q`
Expected: PASS (los axos de test usan focus=50/100 y salinity default ~5, slip ≈ 1.6%, no rompe asserts).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/multiplayer_service.py
git commit -m "feat(multi): SAL slip individual + entropia de sala"
```

---

### Task 5: Recuperación por PILA reemplaza agility en el sueño

**Files:**
- Modify: `backend/app/api/v1/endpoints/game.py:642-649`
- Modify: `backend/app/api/v1/endpoints/multiplayer.py:415-421`

- [ ] **Step 1: Añadir import en game.py**

```python
from app.services.pila_service import recovery_multiplier
```

- [ ] **Step 2: Reemplazar el cálculo en game.py (~línea 643-646)**

Reemplazar:

```python
    # Sleep duration: 1 minute for quick gameplay testing, reduced by agility
    base_recovery_minutes = 1.0
    agility_factor = max(0.5, 1.0 - (axo.stat_agility / 200.0))
    recovery_minutes = base_recovery_minutes * agility_factor
    if axo.nature == "hyperactive":
        recovery_minutes *= 0.75  # 25% faster recovery
```

por:

```python
    # Sleep duration: 1 minute base, reducido por PILA (mas PILA = duerme menos)
    base_recovery_minutes = 1.0
    recovery_minutes = base_recovery_minutes * recovery_multiplier(axo.stat_stamina)
    if axo.nature == "hyperactive":
        recovery_minutes *= 0.75  # 25% faster recovery
```

- [ ] **Step 3: Mismo reemplazo en multiplayer.py (~línea 415-420)**

Añadir el import `from app.services.pila_service import recovery_multiplier` y reemplazar el bloque idéntico de `agility_factor` por:

```python
    # Sleep duration: 1 minute base, reducido por PILA (mas PILA = duerme menos)
    base_recovery_minutes = 1.0
    recovery_minutes = base_recovery_minutes * recovery_multiplier(axo.stat_stamina)
    if axo.nature == "hyperactive":
        recovery_minutes *= 0.75  # 25% faster recovery
```

- [ ] **Step 4: Verificar imports y arranque**

Run: `cd backend && python -c "from app.api.v1.endpoints import game, multiplayer; print('ok')"`
Expected: `ok`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/game.py backend/app/api/v1/endpoints/multiplayer.py
git commit -m "feat(pila): recuperacion de sueno por PILA reemplaza agility"
```

---

## FASE 2 — Eclosión y Remoción de Stats Muertos

### Task 6: Eclosión — agility espeja focus, bonus_wisdom→suerte, sin strength

**Files:**
- Modify: `backend/app/api/v1/endpoints/incubation.py` (cálculo de stats finales ~770-790 y construcción del Axolotito ~963-970)

- [ ] **Step 1: Leer la zona de cálculo de stats finales**

Run: `cd backend && sed -n '770,800p' app/api/v1/endpoints/incubation.py`
Expected: ver dónde se calculan `final_focus`, `final_agility`, `final_wisdom`, etc. desde `p_*_bonus`.

- [ ] **Step 2: Mapear bonus_wisdom a SUERTE y espejar agility=focus**

En la zona donde se computan los `final_*` (después de calcular `p_luck_bonus`, `p_focus_bonus`, etc.), asegurar este mapeo. Localizar las asignaciones `final_luck = ...`, `final_focus = ...` y dejarlas así (añadir la suma de wisdom a luck/suerte y espejar agility):

```python
    # 4 STATS: SUERTE absorbe bonus_wisdom; OJO (focus) absorbe agility.
    final_luck = base_luck + p_luck_bonus + p_wisdom_bonus      # SUERTE
    final_focus = base_focus + p_focus_bonus + p_agility_bonus  # OJO (focus+agility)
    final_agility = final_focus       # espejo: agility = OJO
    final_stamina = base_stamina + p_stamina_bonus              # PILA
    final_salinity = base_salinity                              # SAL (del karma)
    # Stats retirados: congelados en 0
    final_charisma = 0.0
    final_wisdom = 0.0
    final_strength = 0.0
```

> NOTA AL EJECUTOR: los nombres `base_luck`, `base_focus`, `p_*_bonus` deben coincidir con los existentes en el archivo. Si el archivo usa otros nombres (p.ej. inicializa `final_luck` directamente sin `base_`), ajustar conservando la intención: SUERTE = luck + wisdom_bonus, OJO = focus + agility_bonus, agility = focus, charisma/wisdom/strength = 0. Leer el bloque real con el Step 1 antes de editar.

- [ ] **Step 3: Ajustar los modificadores de Naturaleza a 4 stats**

Run: `cd backend && grep -n "methodical\|lucky\|hyperactive\|shy\|wise\|glutton\|nature" app/api/v1/endpoints/incubation.py | head -30`
Expected: localizar el bloque donde la naturaleza elegida modifica los `final_*` (los `+10 Focus`, `-5 Stamina`, etc. del plan de gamificación).

Reemplazar los modificadores por los del spec §6 (aplicados a los stats vivos, ANTES de espejar agility=focus en Step 2 — reordenar para que las modificaciones de nature ocurran antes del espejo):

```python
    # Modificadores de naturaleza — sistema de 4 stats (spec §6)
    if chosen_nature == "lucky":        # Suertudo
        final_luck += 10; final_stamina -= 5
    elif chosen_nature == "methodical": # Metódico
        final_focus += 10; final_stamina -= 5
    elif chosen_nature == "glutton":    # Glotón (energía por comida se aplica en game.py; sin penalización aquí)
        pass
    elif chosen_nature == "shy":        # Tímido
        final_salinity = max(0.0, final_salinity - 10); final_luck -= 5
    elif chosen_nature == "hyperactive":# Hiperactivo (vel. sueño en game.py)
        final_focus -= 5
    elif chosen_nature == "wise":       # Sabio — rediseño +15 PILA / -5 SAL
        final_stamina += 15; final_salinity = max(0.0, final_salinity - 5)

    # Clamp de rangos
    final_luck = max(0.0, min(100.0, final_luck))
    final_focus = max(0.0, min(100.0, final_focus))
    final_stamina = max(50, min(200, final_stamina))
    final_salinity = max(0.0, min(100.0, final_salinity))

    # Espejo agility = OJO (DESPUÉS de aplicar nature)
    final_agility = final_focus
```

> NOTA AL EJECUTOR: si el archivo YA tiene un bloque de modificadores de nature (del plan de gamificación previo), reemplazarlo por este. Mover la línea `final_agility = final_focus` del Step 2 para que quede aquí, después del clamp. Verificar los nombres exactos de las naturalezas (`lucky/methodical/glutton/shy/hyperactive/wise`) contra el enum real.

- [ ] **Step 4: La construcción del Axolotito ya pasa los final_* — verificar**

El `Axolotito(...)` en ~línea 963-970 ya recibe `stat_agility=final_agility`, `stat_wisdom=final_wisdom`, etc. Con los Steps 2-3, agility queda = focus (post-nature) y los muertos en 0. No requiere cambio adicional aquí.

- [ ] **Step 5: Actualizar la respuesta JSON de stats a 4 stats**

Reemplazar el bloque `"stats": { ... }` (~línea 1011-1020) por:

```python
            "stats": {
                "suerte": nuevo_axolote.stat_luck,
                "ojo": nuevo_axolote.stat_focus,
                "pila": nuevo_axolote.stat_stamina,
                "sal": nuevo_axolote.stat_salinity,
            },
```

- [ ] **Step 6: Verificar arranque**

Run: `cd backend && python -c "from app.api.v1.endpoints import incubation; print('ok')"`
Expected: `ok`.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/v1/endpoints/incubation.py
git commit -m "feat(hatch): 4 stats al nacer (agility=ojo, wisdom->suerte, muertos en 0)"
```

---

### Task 7: Remover efectos de wisdom/charisma/strength del gameplay

**Files:**
- Modify: `backend/app/api/v1/endpoints/game.py:338-355` (wisdom en miss_chance)
- Modify: `backend/app/services/shop_service.py:193-194` (charisma discount)
- Modify: `backend/app/api/v1/endpoints/board.py:68` (wisdom_bonus staking)

- [ ] **Step 1: Simplificar el marcado del jugador en game.py (quitar wisdom)**

Reemplazar el bloque "2. Update Player" (~línea 338-355) por:

```python
        # 2. Update Player (OJO/focus miss check)
        if card_drawn in player_card_ids:
            player_index = player_card_ids.index(card_drawn)
            if _rng.random() < player_miss_chance:
                player_misses.append(card_name)
            else:
                player_marked.add(player_index)
```

> NOTA: esto elimina `_get_priority_line`, `is_priority`, `effective_miss`, `wisdom_saves`. Buscar y eliminar referencias colgantes a `wisdom_saves` en el resto de la función (Run: `grep -n "wisdom_saves\|_get_priority_line" app/api/v1/endpoints/game.py`). Si `wisdom_saves` se reporta en la respuesta, quitar esa key.

- [ ] **Step 2: Eliminar el descuento de carisma en shop_service.py**

Localizar (~línea 190-194):

```python
                charisma_discount = min(0.10, main_axo.stat_charisma * 0.001)
                price = round(price * (1 - charisma_discount), 2)
```

Eliminar ambas líneas (y el `if main_axo:` envolvente si queda vacío). El precio queda sin descuento por carisma.

- [ ] **Step 3: Eliminar wisdom_bonus del staking en board.py**

Reemplazar (~línea 60-75):

```python
    wisdom_bonus = 1.0 + ((main_axo.stat_wisdom / 1000.0) if main_axo else 0.0)

    # Bono de Staking pasivo Sabio (+1% extra por nivel del Axolotito)
    wise_multiplier = 1.0
    if main_axo and main_axo.nature == "wise":
        wise_multiplier = 1.0 + (main_axo.level * 0.01)

    return total_bonus * level_multiplier * wisdom_bonus * wise_multiplier
```

por:

```python
    # Bono de Staking pasivo Sabio (+1% extra por nivel del Axolotito principal)
    wise_multiplier = 1.0
    if main_axo and main_axo.nature == "wise":
        wise_multiplier = 1.0 + (main_axo.level * 0.01)

    return total_bonus * level_multiplier * wise_multiplier
```

(La naturaleza Sabio se redefine en spec como +PILA/-SAL, pero su bono de staking por nivel se conserva como identidad de la nature.)

- [ ] **Step 4: Verificar arranque y tests de game**

Run: `cd backend && python -c "from app.api.v1.endpoints import game, board; from app.services import shop_service; print('ok')"`
Then: `cd backend && python -m pytest tests/unit/test_jackpot_inflation.py -q`
Expected: `ok` y PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/game.py backend/app/services/shop_service.py backend/app/api/v1/endpoints/board.py
git commit -m "refactor(stats): remover efectos de wisdom/charisma del gameplay"
```

---

## FASE 3 — Superficie de API

### Task 8: Nueva fórmula de poder + JSON de 4 stats en ranking

**Files:**
- Modify: `backend/app/api/v1/endpoints/ranking.py:28-80`

- [ ] **Step 1: Reemplazar `power_expr` (orden SQL, ~línea 28-39)**

```python
    elif sort_by == "power":
        power_expr = (
            Axolotito.stat_luck +
            Axolotito.stat_focus +
            Axolotito.stat_stamina +
            (100 - Axolotito.stat_salinity)
        )
        statement = statement.order_by(power_expr.desc())
```

- [ ] **Step 2: Reemplazar el cálculo de `power` en Python (~línea 46-55)**

```python
        power = (
            axo.stat_luck +
            axo.stat_focus +
            axo.stat_stamina +
            (100 - axo.stat_salinity)
        )
```

- [ ] **Step 3: Reemplazar el bloque `"stats": {...}` (~línea 72-81)**

```python
            "stats": {
                "suerte": axo.stat_luck,
                "ojo": axo.stat_focus,
                "pila": axo.stat_stamina,
                "sal": axo.stat_salinity,
            },
```

- [ ] **Step 4: Verificar arranque**

Run: `cd backend && python -c "from app.api.v1.endpoints import ranking; print('ok')"`
Expected: `ok`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/ranking.py
git commit -m "feat(ranking): fórmula poder SUERTE+OJO+PILA+(100-SAL) y JSON 4 stats"
```

---

### Task 9: JSON de 4 stats en multiplayer, metadata y admin

**Files:**
- Modify: `backend/app/api/v1/endpoints/multiplayer.py:463-480`
- Modify: `backend/app/api/v1/endpoints/metadata.py`
- Modify: `backend/app/api/v1/endpoints/admin.py:449-456`

- [ ] **Step 1: multiplayer.py — limpiar respuesta de stats**

Localizar el dict que expone `focus/agility/stamina/luck/salinity` (~línea 472-476) y reemplazar por:

```python
            "suerte": axo.stat_luck,
            "ojo": axo.stat_focus,
            "pila": axo.stat_stamina,
            "sal": axo.stat_salinity,
```

El `ManualGameService.get_env_params(focus=..., agility=..., stamina=...)` y `crit_probability(...)` (~línea 463-480) ya NO deben aplicarse en manual (ver Task 13). Si este bloque calcula params manuales, quitarlo en Task 13; aquí solo limpiar las keys de stats expuestas.

- [ ] **Step 2: metadata.py — exponer solo 4 stats en el NFT**

Run: `cd backend && sed -n '1,90p' app/api/v1/endpoints/metadata.py`
Reemplazar las `attributes`/lecturas de los 8 stats por las 4. Cada `trait_type` usa los nombres nuevos:

```python
    sal = axolotito.stat_salinity
    suerte = axolotito.stat_luck
    ojo = axolotito.stat_focus
    pila = axolotito.stat_stamina
    # (eliminar lecturas de charisma, agility, wisdom, strength)
```

Y en la lista de `attributes` del metadata, dejar solo:

```python
        {"trait_type": "Suerte", "value": suerte},
        {"trait_type": "Ojo", "value": ojo},
        {"trait_type": "Pila", "value": pila},
        {"trait_type": "Sal", "value": sal},
```

> NOTA AL EJECUTOR: leer el archivo completo primero; conservar la estructura existente de `attributes` (rasgos físicos como skin/gill se mantienen). Solo se remueven los 4 stats muertos.

- [ ] **Step 3: admin.py — mostrar 4 stats (mantener crudos para debug)**

Reemplazar el bloque `"salinity"/"luck"/.../"strength"` (~línea 449-456) por:

```python
                    "suerte": a.stat_luck,
                    "ojo": a.stat_focus,
                    "pila": a.stat_stamina,
                    "sal": a.stat_salinity,
```

- [ ] **Step 4: Verificar arranque**

Run: `cd backend && python -c "from app.api.v1.endpoints import multiplayer, metadata, admin; print('ok')"`
Expected: `ok`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/multiplayer.py backend/app/api/v1/endpoints/metadata.py backend/app/api/v1/endpoints/admin.py
git commit -m "feat(api): exponer solo 4 stats en multiplayer/metadata/admin"
```

---

## FASE 4 — Servicios Narrativos

### Task 10: dialogue_engine — quitar wisdom/strength, renombrar focus→ojo/salinity→sal

**Files:**
- Modify: `backend/app/services/dialogue_engine.py`
- Modify: `backend/tests/test_dialogue_engine.py` (ajustar tests afectados)

- [ ] **Step 1: Eliminar los bancos de líneas muertos**

En `_STAT_LINES` (~línea 45-227), eliminar las entradas completas `"wisdom": {...}` (línea ~156) y `"strength": {...}` (línea ~178). Eliminar también `"agility": {...}` (~línea 134) si existe como banco separado, ya que OJO lo absorbe.

- [ ] **Step 2: Mantener compatibilidad de claves**

`get_line(stat=...)` recibe strings. Para no romper llamadas, añadir un alias al inicio de `get_line`:

```python
        # Alias de stats al nuevo sistema de 4
        _ALIAS = {"focus": "focus", "agility": "focus", "salinity": "salinity", "luck": "luck", "stamina": "stamina"}
        stat = _ALIAS.get(stat, stat)
```

(focus y agility comparten banco; no se crean bancos nuevos "ojo"/"sal" — se reusan los existentes "focus"/"salinity" internamente.)

- [ ] **Step 3: Simplificar `infer_personality_from_incubation`**

Ya recibe `bonus_luck, bonus_focus, bonus_stamina` (sin wisdom/strength). Verificar que no referencia los removidos (Run: `grep -n "wisdom\|strength" app/services/dialogue_engine.py`). Eliminar cualquier referencia colgante.

- [ ] **Step 4: Correr y arreglar tests del engine**

Run: `cd backend && python -m pytest tests/test_dialogue_engine.py -q`
Expected: si algún test referencia `stat="wisdom"`/`"strength"`, ajustarlo a `"focus"`/`"luck"`. Repetir hasta PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/dialogue_engine.py backend/tests/test_dialogue_engine.py
git commit -m "refactor(dialogue): 4 stats — quitar wisdom/strength, alias agility->focus"
```

---

### Task 11: axo_names — generador de nombres con 4 stats

**Files:**
- Modify: `backend/app/services/axo_names.py`

- [ ] **Step 1: Revisar el StatKey y los bancos de nombres**

Run: `cd backend && sed -n '130,230p' app/services/axo_names.py`
Expected: ver `StatKey = Literal[...]` y los diccionarios de nombres por stat.

- [ ] **Step 2: Reducir StatKey a 4 stats**

```python
StatKey = Literal["luck", "focus", "stamina", "salinity"]
```

- [ ] **Step 3: Eliminar los bancos de nombres muertos**

Eliminar las entradas de los diccionarios para `"strength"`, `"wisdom"`, `"charisma"`, `"agility"`. Conservar `"luck"`, `"focus"`, `"stamina"`, `"salinity"`. Si la función elige el stat dominante de un dict `{"luck": .., "focus": .., ...}`, asegurar que solo considere las 4 claves vivas (filtrar las que lleguen).

- [ ] **Step 4: Verificar arranque + uso**

Run: `cd backend && python -c "from app.services.axo_names import generate_name; print(generate_name({'luck': 80.0, 'focus': 20.0, 'stamina': 30.0, 'salinity': 5.0}))"`
Expected: imprime un nombre sin error (firma real puede variar; ajustar la llamada al API real de la función).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/axo_names.py
git commit -m "refactor(names): generador de nombres con 4 stats"
```

---

### Task 12: tutorial_service — consolidar a 4 stats

**Files:**
- Modify: `backend/app/services/tutorial_service.py`
- Modify: `backend/tests/test_tutorial_service.py`

- [ ] **Step 1: Ajustar la mini-simulación de Fase 2 (focus + agility → solo OJO/focus)**

En `advance_phase`, bloque `elif current == 2` (~línea 190-226), reemplazar la lectura de agility:

```python
        elif current == 2:
            focus = _get_incubation_stat(incubation, "focus")
            agility = _get_incubation_stat(incubation, "agility")
            ojo = focus + agility  # OJO unifica ambos cuidados
            wins = _simulate_phase_wins(ojo, ojo)
```

(El resto del bloque — diálogos focus/agility moment — se conserva; son narrativos.)

- [ ] **Step 2: Verificar que karma sigue usando bonus_luck (SUERTE)**

`_evaluate_karma` ya usa `bonus_luck` para decidir lucky/salty. SUERTE = luck, así que no cambia. Confirmar (Run: `grep -n "bonus_luck\|_get_incubation_stat" app/services/tutorial_service.py`).

- [ ] **Step 3: Correr tests del tutorial**

Run: `cd backend && python -m pytest tests/test_tutorial_service.py -q`
Expected: PASS. Si algún test asume el viejo cálculo de wins de fase 2, ajustar el valor esperado al nuevo `ojo = focus + agility`.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/tutorial_service.py backend/tests/test_tutorial_service.py
git commit -m "refactor(tutorial): fase 2 unifica focus+agility en OJO"
```

---

### Task 13: manual_game_service — modo manual sin modificadores de stat

**Files:**
- Modify: `backend/app/api/v1/endpoints/multiplayer.py` (llamadas a `ManualGameService` ~línea 438, 463-480)
- Modify: `backend/app/services/manual_game_service.py` (constantes fijas)
- Modify: `backend/tests/test_manual_game_service.py`

- [ ] **Step 1: Convertir ManualGameService a parámetros fijos**

Reemplazar el cuerpo de `get_env_params` para que NO dependa de stats — retornar constantes estándar para todos los jugadores:

```python
    # Parámetros fijos: en manual el jugador ES el Axolotito; sin modificadores de stat.
    STANDARD_WINDOW_MS: int = 2500
    STANDARD_GRITON_DELAY_MS: int = 1600
    STANDARD_VISUAL_HINTS: int = 0   # sin pistas — la habilidad es del jugador

    def get_env_params(self, *args, **kwargs) -> ManualEnvParams:
        """Modo manual: parámetros fijos, idénticos para todos los jugadores."""
        return ManualEnvParams(
            highlight_window_ms=self.STANDARD_WINDOW_MS,
            griton_delay_ms=self.STANDARD_GRITON_DELAY_MS,
            visual_hints=self.STANDARD_VISUAL_HINTS,
            crit_window_ms=int(self.STANDARD_WINDOW_MS * 0.30),
        )

    def crit_probability(self, *args, **kwargs) -> float:
        """Modo manual: sin críticos por stat. Siempre 0."""
        return 0.0
```

(Acepta `*args, **kwargs` para no romper los call sites existentes que pasan focus/agility/stamina/luck.)

- [ ] **Step 2: Actualizar tests del servicio manual**

Run: `cd backend && python -m pytest tests/test_manual_game_service.py -q`
Expected: los tests viejos asumían escalado por stat → FALLARÁN. Reescribir `test_manual_game_service.py` para asertar los valores fijos:

```python
from app.services.manual_game_service import ManualGameService

def test_env_params_are_fixed_regardless_of_stats():
    svc = ManualGameService()
    p_low  = svc.get_env_params(focus=0, agility=0, stamina=50)
    p_high = svc.get_env_params(focus=100, agility=100, stamina=200)
    assert p_low == p_high  # los stats no afectan el modo manual
    assert p_low.highlight_window_ms == 2500
    assert p_low.visual_hints == 0

def test_crit_probability_is_zero_in_manual():
    svc = ManualGameService()
    assert svc.crit_probability(luck=100, marked_in_window=True) == 0.0
```

- [ ] **Step 3: Correr tests reescritos**

Run: `cd backend && python -m pytest tests/test_manual_game_service.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/manual_game_service.py backend/tests/test_manual_game_service.py backend/app/api/v1/endpoints/multiplayer.py
git commit -m "feat(manual): modo manual sin modificadores de stat (jugador = axolotito)"
```

---

### Task 14: seed_catalog — remapear bonus de equipo/items

**Files:**
- Modify: `backend/app/scripts/seed_catalog.py` (item_metadata ~línea 442-487)

- [ ] **Step 1: Remapear los bonus de accesorios**

En las definiciones de items con `item_metadata`, aplicar:
- `bonus_salinity` → se mantiene (reduce SAL, sigue válido).
- `bonus_focus` → se mantiene (OJO).
- `bonus_luck` → se mantiene (SUERTE).
- `bonus_stamina` → se mantiene (PILA).
- `bonus_wisdom` → cambiar a `bonus_luck` (SUERTE).
- `bonus_charisma` → cambiar a `bonus_luck` (SUERTE).
- `bonus_agility` → cambiar a `bonus_focus` (OJO).

Ejemplo concreto (línea ~460 y ~487):

```python
                item_metadata={"slot": "body", "bonus_luck": 15.0}            # era bonus_wisdom: 5.0 -> fusionado a luck
...
                item_metadata={"slot": "head", "bonus_luck": 25.0}            # era bonus_charisma: 10.0 -> luck
...
                item_metadata={"slot": "eyes", "bonus_focus": 15.0}           # era bonus_wisdom -> focus(ojo)
```

> NOTA AL EJECUTOR: leer cada item con `bonus_wisdom/charisma/agility` y consolidar el valor al stat vivo correspondiente (sumando si ya hay un bonus de ese stat en el mismo item).

- [ ] **Step 2: Verificar que el script importa sin error**

Run: `cd backend && python -c "import app.scripts.seed_catalog; print('ok')"`
Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/scripts/seed_catalog.py
git commit -m "refactor(catalog): remapear bonus de items a 4 stats"
```

---

### Task 15: Limpiar fixtures de tests con stats viejos

**Files:**
- Modify: `backend/tests/unit/test_axo_stats.py`, `backend/tests/unit/test_jackpot_inflation.py`, `backend/tests/conftest.py` (si aplica)

- [ ] **Step 1: Buscar fixtures con stats removidos**

Run: `cd backend && grep -rn "stat_agility\|stat_wisdom\|stat_strength\|stat_charisma" tests/`
Expected: lista de tests que setean stats removidos.

- [ ] **Step 2: Actualizar test_axo_stats.py**

Los tests de `stat_agility=100` (agility_factor en sueño) y `stat_strength=100` (mitigation) ya no aplican. Reescribir esos casos para validar la NUEVA mecánica:
- Sueño: usar `stat_stamina` y `recovery_multiplier` (ver `test_pila_service.py`, ya cubierto — eliminar el test de agility-sleep aquí o convertirlo a un test de integración de PILA).
- Mitigation de strength: eliminar el test (la mecánica ya no existe).

- [ ] **Step 3: Quitar kwargs muertos donde se crean Axolotitos de test**

Donde un helper haga `Axolotito(..., stat_agility=X, stat_wisdom=Y)`, quitar esos kwargs (usan default 0 ahora). Mantener `stat_focus`, `stat_luck`, `stat_stamina`, `stat_salinity`.

- [ ] **Step 4: Correr toda la suite**

Run: `cd backend && python -m pytest tests/ -q 2>&1 | tail -25`
Expected: PASS (o el mismo set de fallos pre-existentes del baseline de Task 0, nada nuevo roto).

- [ ] **Step 5: Commit**

```bash
git add backend/tests/
git commit -m "test(stats): limpiar fixtures de stats removidos; cubrir nuevas mecanicas"
```

---

## FASE 5 — Frontend (4 Stats UI + Tutorial)

### Task 16: Catálogo de stats compartido en frontend

**Files:**
- Create: `frontend/lib/stats.ts`

- [ ] **Step 1: Crear el módulo de definición de stats**

```typescript
// frontend/lib/stats.ts
// Definición única de los 4 stats del Axolotito para todo el frontend.

export type StatKey = "suerte" | "ojo" | "pila" | "sal";

export interface StatDef {
  key: StatKey;
  label: string;
  icon: string;
  color: string;
  isNegative: boolean;
  tooltip: string;
}

export const STATS: StatDef[] = [
  { key: "suerte", label: "Suerte", icon: "✨", color: "#fbbf24", isNegative: false,
    tooltip: "Mejores premios al ganar y más drops raros." },
  { key: "ojo", label: "Ojo", icon: "👁️", color: "#2dd4bf", isNegative: false,
    tooltip: "Marca más cartas sin fallar cuando juega solo." },
  { key: "pila", label: "Pila", icon: "🔋", color: "#60a5fa", isNegative: false,
    tooltip: "Más energía y se recupera más rápido al dormir." },
  { key: "sal", label: "Sal", icon: "🧂", color: "#f87171", isNegative: true,
    tooltip: "¡Mala suerte! Entre más alta, peor le va. Mantenla baja." },
];

// Mapea la respuesta de la API (objeto stats) a un arreglo ordenado para render.
export function statsFromApi(apiStats: Record<string, number>): { def: StatDef; value: number }[] {
  return STATS.map((def) => ({ def, value: apiStats?.[def.key] ?? 0 }));
}
```

- [ ] **Step 2: Verificar compilación de tipos**

Run: `cd frontend && npx tsc --noEmit lib/stats.ts 2>&1 | head -5`
Expected: sin errores (o solo warnings de config no relacionados).

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/stats.ts
git commit -m "feat(fe): catalogo compartido de 4 stats"
```

---

### Task 17: Render de 4 stats en los componentes de inventario/santuario

**Files:**
- Modify: `frontend/components/AxoStatusBar.tsx`, `Santuario.tsx`, `Criadero.tsx`, `Inventory.tsx`, `MarketP2P.tsx`, `screens/AxoSelectScreen.tsx`, `screens/BoardSelectScreen.tsx`, `screens/CpuSimScreen.tsx`

- [ ] **Step 1: Inventariar cómo cada componente lee stats hoy**

Run: `cd frontend && grep -rn "salinity\|focus\|agility\|wisdom\|strength\|charisma\|stat_" components/AxoStatusBar.tsx components/Santuario.tsx components/Criadero.tsx components/Inventory.tsx components/MarketP2P.tsx components/screens/`
Expected: lista de accesos a stats por componente.

- [ ] **Step 2: Reemplazar cada bloque de stats por el catálogo compartido**

En cada componente que renderiza stats, importar y usar `STATS`/`statsFromApi`:

```tsx
import { STATS, statsFromApi } from "@/lib/stats";

// Donde antes se mapeaban 8 stats:
{statsFromApi(axo.stats).map(({ def, value }) => (
  <div key={def.key} className="flex items-center gap-1.5" title={def.tooltip}>
    <span>{def.icon}</span>
    <span className="text-xs font-bold" style={{ color: def.color }}>{def.label}</span>
    <span className="text-xs" style={{ color: def.isNegative ? "#f87171" : "#fff" }}>{value}</span>
  </div>
))}
```

> NOTA AL EJECUTOR: cada componente tiene su propio layout. No imponer este markup exacto — adaptar al estilo existente del componente, pero leyendo SIEMPRE de `STATS`/`statsFromApi` y mostrando solo los 4. Eliminar cualquier referencia a `agility/wisdom/strength/charisma`.

- [ ] **Step 3: Verificar build**

Run: `cd frontend && npx tsc --noEmit 2>&1 | grep -i "error" | head -20`
Expected: sin errores nuevos relacionados a stats.

- [ ] **Step 4: Commit**

```bash
git add frontend/components/
git commit -m "feat(fe): render de 4 stats en inventario/santuario/screens"
```

---

### Task 18: Consolidar el tutorial a 4 stats

**Files:**
- Modify: `frontend/components/tutorial/TutorialFlow.tsx`, `TutorialCpuGame.tsx`, `dialogues.ts`

- [ ] **Step 1: Renombrar las etiquetas de fase en TutorialFlow.tsx**

Localizar (~línea 352):

```tsx
    const phaseLabel = ["Salinidad", "Concentración", "Suerte"][phaseNum - 1];
```

Reemplazar por:

```tsx
    const phaseLabel = ["Sal", "Ojo", "Suerte y Pila"][phaseNum - 1];
```

- [ ] **Step 2: Consolidar props de stats**

En `TutorialFlowProps` (~línea 36-52), los props `bonusFocus/bonusLuck/bonusAgility/bonusStamina/bonusSalinity` se mantienen como entrada (vienen del huevo), pero internamente `bonusAgility` se suma a `bonusFocus` al pasarlos a `TutorialCpuGame`. En `sharedGameProps` (~línea 271-286):

```tsx
  const sharedGameProps = {
    incubationId: tutorialId ?? 0,
    userId,
    token,
    bonusOjo: bonusFocus + bonusAgility,   // OJO unifica focus + agility
    bonusSuerte: bonusLuck,
    bonusPila: bonusStamina,
    bonusSal: bonusSalinity,
    inferredNature,
    selectedAxo,
    selectedBoardId,
    playerBoards,
    allCards,
    onTutorialComplete: handleTutorialComplete,
  };
```

- [ ] **Step 3: Actualizar TutorialCpuGame para recibir los 4 props**

En `TutorialCpuGame.tsx`, actualizar la interfaz de props a `bonusOjo/bonusSuerte/bonusPila/bonusSal` y usar esos nombres internamente. Donde se mostraban labels de "Focus"/"Agility"/"Salinity", usar "Ojo"/"Suerte"/"Pila"/"Sal".

- [ ] **Step 4: Revisar dialogues.ts**

Run: `cd frontend && grep -n "focus\|agility\|salinity\|wisdom\|strength\|Concentración\|Salinidad" components/tutorial/dialogues.ts`
Reemplazar referencias visibles de stats por los nombres nuevos (Ojo/Sal/Suerte/Pila). El contenido narrativo del Webito se conserva; solo cambian las menciones explícitas de stats.

- [ ] **Step 5: Verificar build**

Run: `cd frontend && npx tsc --noEmit 2>&1 | grep -i "error" | head -20`
Expected: sin errores nuevos.

- [ ] **Step 6: Commit**

```bash
git add frontend/components/tutorial/
git commit -m "feat(fe): tutorial consolidado a 4 stats (Sal/Ojo/Suerte/Pila)"
```

---

## FASE 6 — QA y Verificación

### Task 19: Simulación de universo con 4 stats

**Files:**
- Modify (si aplica): `backend/app/scripts/simulate_universe.py`

- [ ] **Step 1: Correr la simulación existente**

Run: `cd backend && python -m app.scripts.simulate_universe 2>&1 | tail -40`
Expected: corre sin error. Si referencia stats removidos, ajustar (la sim usa `stat_stamina` para energía — eso sigue válido).

- [ ] **Step 2: Revisar el reporte**

Run: `cat simulation_report.txt | head -60`
Expected: verificar que las tasas de victoria/economía siguen razonables (no inflación descontrolada por las nuevas mecánicas SAL/PILA).

- [ ] **Step 3: Commit (si hubo ajustes)**

```bash
git add backend/app/scripts/simulate_universe.py simulation_report.txt
git commit -m "test(sim): simulacion de universo con 4 stats"
```

---

### Task 20: Regresión completa + verificación de la división manual/bot

**Files:** ninguno (verificación)

- [ ] **Step 1: Suite backend completa**

Run: `cd backend && python -m pytest tests/ -q 2>&1 | tail -25`
Expected: PASS salvo fallos pre-existentes del baseline (Task 0).

- [ ] **Step 2: Verificar manualmente la división manual/bot**

Levantar el backend y confirmar por código/logs que:
- Una partida bot/multi aplica miss_chance (OJO), bonus de premio (SUERTE), slip+deck bias (SAL).
- Una partida manual NO consulta stats para timing/hints/crits (params fijos de `ManualGameService`).

Run: `cd backend && grep -n "get_env_params\|crit_probability" app/api/v1/endpoints/multiplayer.py`
Expected: si aún se llaman, confirmar que retornan constantes fijas (Task 13). Si el modo manual ya no las necesita, removerlas.

- [ ] **Step 3: Build frontend limpio**

Run: `cd frontend && npm run build 2>&1 | tail -20`
Expected: build exitoso.

- [ ] **Step 4: Commit final / merge readiness**

```bash
git add -A
git commit -m "test(stats): regresion completa sistema 4 stats" --allow-empty
```

- [ ] **Step 5: Resumen de verificación**

Confirmar contra el spec (`docs/superpowers/specs/2026-05-31-sistema-4-stats-axolotito-design.md`):
- [ ] 4 stats expuestos en todas las API responses (ranking, metadata, admin, multiplayer, hatch).
- [ ] charisma/wisdom/strength sin efecto de gameplay; agility = focus al nacer.
- [ ] SAL: deck bias (solo), slip + entropía (multi), drena energía (todos).
- [ ] PILA: energía máx + recuperación.
- [ ] Manual sin modificadores de stat.
- [ ] Tutorial muestra Sal/Ojo/Suerte/Pila.
- [ ] DB sin ALTER TABLE; ABI sin cambios.

---

## Notas de Ejecución Multi-Agente

- **Orden obligatorio:** FASE 0 → 1 → 2 → 3 → 4 → 5 → 6. Dentro de una fase, las tareas son secuenciales salvo indicación.
- **Paralelizable:** FASE 5 (frontend) puede arrancar en paralelo cuando FASE 3 (API surface) termina, ya que el frontend depende del contrato JSON de 4 stats.
- **Punto de no-retorno seguro:** nada toca DB ni ABI; todo es reversible por `git revert`.
- **Si un test del baseline ya fallaba (Task 0):** no es responsabilidad de este plan — anotarlo y seguir.
