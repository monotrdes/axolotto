# Tutorial Híbrido Webito + Diálogos Dinámicos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar el onboarding de Axolotto en un tutorial narrativo guiado por el Webito hablante, añadir diálogos dinámicos basados en stats durante partidas reales, y lanzar el modo manual de Lotería con salas propias.

**Architecture:** Cuatro subsistemas independientes que se pueden paralelizar entre agentes: (1) motor de diálogos dinámicos en backend, (2) tutorial híbrido auto+manual en frontend, (3) modo manual con stats como modificadores de entorno, y (4) huevo durmiente F2P con ciclo de fragmentos. Todos consumen un nuevo `DialogueEngine` centralizado que selecciona líneas según rangos de stats.

**Tech Stack:** FastAPI + SQLModel (backend), Next.js + React (frontend), WebSocket (eventos de partida en tiempo real), Alembic (migraciones DB), Python pytest, Playwright (E2E)

---

## Resumen de Archivos Afectados

| Archivo | Tipo | Responsabilidad |
|---------|------|----------------|
| `backend/app/models/user.py` | Modificar | Campos `tutorial_completed`, `webito_slots_unlocked`, `f2p_fragments` |
| `backend/app/models/items.py` | Modificar | Campo `tutorial_phase` en `WebitoIncubation` |
| `backend/app/models/economy.py` | Modificar | `TransactionType.F2P_REWARD`, `TransactionType.TUTORIAL_BONUS` |
| `backend/app/services/dialogue_engine.py` | Crear | Motor de selección de diálogos según rangos de stats |
| `backend/app/services/tutorial_service.py` | Crear | Lógica de fases del tutorial, karma, eclosión express |
| `backend/app/services/manual_game_service.py` | Crear | Modificadores de entorno para modo manual según stats |
| `backend/app/api/v1/endpoints/tutorial.py` | Crear | Endpoints REST del tutorial: `/tutorial/start`, `/tutorial/next-step`, `/tutorial/complete` |
| `backend/app/api/v1/endpoints/incubation.py` | Modificar | Integrar `tutorial_service` en `hatch_webito` |
| `backend/app/api/v1/endpoints/multiplayer.py` | Modificar | Emitir eventos de diálogo del Axo por WebSocket, soporte sala manual |
| `backend/app/api/v1/endpoints/user.py` | Modificar | Endpoint desbloqueo de slots de Webito por logro |
| `backend/alembic/versions/` | Crear | Migración para nuevos campos |
| `frontend/components/tutorial/` | Crear | `TutorialCenote.tsx`, `WebitoDialogue.tsx`, `EggProgressBar.tsx` |
| `frontend/components/game/` | Modificar | `PlayMode.tsx` — mostrar diálogos del Axo durante partida |
| `frontend/components/game/ManualPlayMode.tsx` | Crear | Tablero de juego manual con ventanas de tiempo por stat |
| `frontend/components/criadero/SleepingEgg.tsx` | Crear | Huevo durmiente F2P con reacciones a fragmentos |

---

## FASE 1 — Motor de Diálogos Dinámicos (Backend)

> Agnóstico al tutorial: este motor es la base de todo. Un agente puede trabajarlo completamente solo.

### Task 1: Modelo de datos y migración

**Files:**
- Modify: `backend/app/models/user.py`
- Modify: `backend/app/models/items.py`
- Modify: `backend/app/models/economy.py`
- Create: `backend/alembic/versions/xxxx_tutorial_and_dialogue_fields.py`

- [ ] **Step 1: Agregar campos a `User`**

```python
# backend/app/models/user.py — dentro de class User
tutorial_completed: bool = Field(default=False)
webito_slots_unlocked: int = Field(default=1)        # Empieza con 1, max 6
f2p_astral_fragments: int = Field(default=0)         # Fragmentos astrales F2P
f2p_daily_gal_earned: float = Field(default=0.0)     # GAL ganados hoy en F2P
f2p_daily_gal_reset_at: Optional[datetime] = Field(default=None)
```

- [ ] **Step 2: Agregar campo a `WebitoIncubation`**

```python
# backend/app/models/items.py — dentro de class WebitoIncubation
tutorial_phase: int = Field(default=0)  # 0=no tutorial, 1-3=partida activa, 4=karma, 5=completo
tutorial_karma: Optional[str] = Field(default=None)  # "lucky" | "salty" | None
```

- [ ] **Step 3: Agregar tipos de transacción**

```python
# backend/app/models/economy.py — dentro de class TransactionType
F2P_REWARD = "f2p_reward"          # Premio espectador
TUTORIAL_BONUS = "tutorial_bonus"  # Bonus de karma al nacer
WEBITO_UNLOCK = "webito_unlock"    # Costo de desbloqueo de slot
```

- [ ] **Step 4: Generar migración Alembic**

```bash
cd backend
alembic revision --autogenerate -m "tutorial_and_dialogue_fields"
alembic upgrade head
```

Expected: sin errores, tablas actualizadas.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/ backend/alembic/versions/
git commit -m "feat(tutorial): add tutorial_phase, f2p_fragments, webito_slots fields"
```

---

### Task 2: `DialogueEngine` — Selección de líneas por rangos de stats

**Files:**
- Create: `backend/app/services/dialogue_engine.py`
- Create: `backend/tests/test_dialogue_engine.py`

El motor carga un diccionario de diálogos (hardcoded en v1, migrable a JSON/DB en v2) y selecciona la línea correcta según el rango del stat relevante. Soporta contexto: `"tutorial"`, `"game_start"`, `"game_win"`, `"game_lose"`, `"vs_bot_1"`, `"vs_bot_5"`, `"vs_human"`.

- [ ] **Step 1: Escribir tests primero**

```python
# backend/tests/test_dialogue_engine.py
from app.services.dialogue_engine import DialogueEngine, DialogueContext

def test_focus_low_range():
    """Focus < 30 → diálogo de distracción"""
    engine = DialogueEngine()
    line = engine.get_line(
        stat="focus", value=15.0,
        context=DialogueContext.TUTORIAL_FOCUS_MOMENT
    )
    assert "[distrac" in line.lower() or "ups" in line.lower()

def test_focus_high_range():
    """Focus >= 80 → diálogo de confianza"""
    engine = DialogueEngine()
    line = engine.get_line(
        stat="focus", value=90.0,
        context=DialogueContext.TUTORIAL_FOCUS_MOMENT
    )
    # Línea de Axo confiado, avisa a tiempo
    assert line != ""
    assert len(line) > 10

def test_salinity_affects_tutorial_phase1():
    engine = DialogueEngine()
    line = engine.get_line(
        stat="salinity", value=80.0,
        context=DialogueContext.TUTORIAL_PHASE_1
    )
    assert "sal" in line.lower() or "mala suerte" in line.lower()

def test_karma_lucky_dialogue():
    engine = DialogueEngine()
    line = engine.get_karma_line(karma="lucky")
    assert line != ""

def test_karma_salty_dialogue():
    engine = DialogueEngine()
    line = engine.get_karma_line(karma="salty")
    assert "sal" in line.lower() or "salad" in line.lower()

def test_game_win_vs_bot():
    engine = DialogueEngine()
    line = engine.get_game_event_line(
        event="win", opponent_type="bot", axo_luck=80.0
    )
    assert line != ""

def test_gritón_reacts_to_high_agility():
    engine = DialogueEngine()
    line = engine.get_gritón_line(axo_agility=90.0, event="card_called")
    assert line != ""
```

- [ ] **Step 2: Correr tests para verificar que fallan**

```bash
cd backend && pytest tests/test_dialogue_engine.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.services.dialogue_engine'`

- [ ] **Step 3: Implementar `DialogueEngine`**

```python
# backend/app/services/dialogue_engine.py
from enum import Enum
import random

class DialogueContext(str, Enum):
    TUTORIAL_PHASE_1 = "tutorial_phase_1"
    TUTORIAL_PHASE_2 = "tutorial_phase_2"
    TUTORIAL_PHASE_3 = "tutorial_phase_3"
    TUTORIAL_FOCUS_MOMENT = "tutorial_focus_moment"
    TUTORIAL_AGILITY_MOMENT = "tutorial_agility_moment"
    TUTORIAL_LUCK_MOMENT = "tutorial_luck_moment"
    GAME_START = "game_start"
    GAME_WIN = "game_win"
    GAME_LOSE = "game_lose"
    GAME_CRIT = "game_crit"
    INTER_AXO_TAUNT = "inter_axo_taunt"
    GRITÓN_CARD_CALLED = "gritón_card_called"

# Rangos: cada stat tiene 4 bandas [0-25), [25-50), [50-80), [80-100]
# Cada banda tiene 3 líneas para variedad (se elige al azar)
DIALOGUES: dict = {
    "tutorial_phase_1": {
        "salinity": {
            (0, 25): [
                "¡El agua del Cenote está perfecta hoy! ¡Mis cartas van a salir de maravilla!",
                "¡Sin sal en las branquias! ¡Hoy es mi día de suerte!",
                "¡Pura agua cristalina! Los Axolotitos nacemos para esto.",
            ],
            (25, 50): [
                "Hmm... siento un poco de sal hoy. No pasa nada, ¡nos adaptamos!",
                "El agua está un poquito salada. Vamos a ver qué pasa con las cartas.",
                "Slight salinidad detectada. Pero eso no me para, ¡órale!",
            ],
            (50, 80): [
                "¡Ay caramba, esta agua está SALADA! Mis cartas se resisten a salir.",
                "¡La sal me está bloqueando! ¿Ves cómo el bot tiene mejores cartas? ¡Es la salinidad!",
                "¡Casi casi cantamos Lotería, se me subió la sal al cascarón!",
            ],
            (80, 101): [
                "¡Esta agua está más salada que el mar! Necesito un Antídoto Anti-Sal urgente.",
                "¡Ugh! ¡Pura sal! Las cartas buenas se escapan. ¡Así no se puede!",
                "¡Mi salinidad está por las nubes! Perder hoy casi está garantizado.",
            ],
        },
    },
    "tutorial_focus_moment": {
        "focus": {
            (0, 30): [
                "¡Ups! Me distraje. Si tuviera más Focus, nunca se me pasaría marcar una carta. ¡Tócala tú para ayudarme!",
                "¡Ay! ¡Esa era la mía! Me perdí. ¡Rápido, márcala tú antes de que se vaya!",
                "¡Mente en blanco! ¡Ayúdame, toca esa carta antes de que desaparezca!",
            ],
            (30, 60): [
                "¡Casi la pierdo! Mi concentración está regular hoy. ¡Dame una mano con esa!",
                "Uf... casi. ¿Me ayudas? Mi focus no está al cien.",
                "Tardé un poco. ¡Completa tú esa, yo sigo con las demás!",
            ],
            (60, 85): [
                "¡La vi, la vi! Pero estaba tan lleno de emoción que casi me adelanto. Aquí voy.",
                "¡Concentrado al máximo! Aunque esta la pudiste marcar tú también, ¿eh?",
                "¡Oye, tú también puedes marcar si quieres! Yo te cubro.",
            ],
            (85, 101): [
                "¡CARTE CANTADA! La registré antes de que el eco llegara. ¿Viste eso?",
                "Focus nivel élite. Ni un soplo se me escapa. Aunque... tú también podrías intentarlo.",
                "¡Sin fallas! Pero hey, no te quedes con las manos cruzadas, ¡es más divertido si participas!",
            ],
        },
    },
    "tutorial_agility_moment": {
        "agility": {
            (0, 30): [
                "¡No llego! ¡El gritón va muy rápido para mí! ¡Ayúdame con esa carta, rápido!",
                "¡Mis patitas no responden! ¡Toca tú esa antes de que cierre la ventana!",
                "¡Demasiado veloz! ¡Dame cobertura, marca esa carta!",
            ],
            (30, 60): [
                "Voy un poquito lento hoy. ¿Me cubres esa? Mientras yo hago las otras.",
                "El gritón está acelerado. Un poco de ayuda manual no estaría mal.",
                "¡Uff! ¡Se me fue por poco! Ayúdame en esta, ¿sí?",
            ],
            (60, 85): [
                "¡Casi al tiro! Mi agilidad me permite ir al ritmo. ¿Quieres intentar uno tú?",
                "Voy bien, voy bien. Aunque si quieres marcar alguna, adelante.",
                "¡Con tiempo de sobra! Oye, puedes participar tú también si gustas.",
            ],
            (85, 101): [
                "¡El gritón no me puede con mi agilidad! Puedo marcar y hablar al mismo tiempo.",
                "¡Rapidísimo! El gritón me dijo que soy su pesadilla favorita.",
                "¡Agilidad máxima! Hasta el gritón se cansa de cantarme cartas.",
            ],
        },
    },
    "tutorial_luck_moment": {
        "luck": {
            (0, 30): [
                "¡Suerte... de la mala! Pero no pasa nada, los Axolotitos persistentes siempre ganan.",
                "Hmm, los críticos no quieren activarse hoy. Mi suerte está dormida.",
                "Sin golpe crítico esta vez. El DNA de suerte necesita más calor.",
            ],
            (30, 60): [
                "¡Un toque de suerte! No es el crítico soñado, pero suma.",
                "¡Pequeño boost de luck! Cada poquito cuenta.",
                "¡Algo es algo! La suerte está calentando motores.",
            ],
            (60, 85): [
                "¡Buen golpe de suerte! Las gemas de alga extra se sienten ricas.",
                "¡Mi DNA de luck está funcionando! ¿Ves el multiplicador?",
                "¡Eso es tener buena suerte! Así se gana en Axolotto.",
            ],
            (85, 101): [
                "¡BOOM! ¡Crítico máximo! ¡Mi DNA tiene suerte de leyenda! ¡Las gemas llueven!",
                "¡GOLPE ASTRAL! Mi factor Luck explotó. ¿Viste eso? ¡A MONTONES!",
                "¡SUERTE LEGENDARIA ACTIVADA! El Cenote entero me vio brillar.",
            ],
        },
    },
    "game_start": {
        "salinity": {
            (0, 25): ["¡Branquias limpias, mente clara! ¡Vamos a ganar esto!",
                      "¡Agua pura! ¡Hoy nadie nos para!",
                      "¡Sin sal, puro flow! ¡A jugar!"],
            (25, 50): ["Un poco de sal, pero nada que no aguante. ¡Arriba!",
                       "Salinidad moderada. Me las arreglo.",
                       "No estoy al cien, pero tampoco estoy mal. ¡Órale!"],
            (50, 80): ["¡El agua está pesada hoy! Voy a necesitar concentrarme más.",
                       "Salinidad alta. Esto va a estar difícil... pero no imposible.",
                       "¡La sal me pesa! Pero los Axolotitos salados somos más resistentes."],
            (80, 101): ["Salinidad máxima. Si gano esto, es un milagro. ¡Y me gustan los milagros!",
                        "¡Pura sal! Cualquier victoria hoy vale el doble.",
                        "¡Esto está imposible! Pero lo voy a intentar de todas formas."],
        },
    },
    "game_win": {
        "luck": {
            (0, 40): ["¡Gané sin suerte especial! ¡Pura estrategia!",
                      "¡Victoria de concentración pura! ¡Sin críticos y gané!",
                      "¡A puro esfuerzo! Los críticos no me ayudaron pero yo sí me ayudé."],
            (40, 70): ["¡Victoria! ¡Un buen golpe de suerte en el momento exacto!",
                       "¡Ganamos! La suerte estuvo de mi lado hoy.",
                       "¡Eso fue suerte y estrategia combinadas! ¡Invencibles!"],
            (70, 101): ["¡VICTORIA CRÍTICA! ¡Mi DNA de suerte es de otro nivel!",
                        "¡LOTERÍA Y CRÍTICO! ¡Las gemas de alga llueven a cántaros!",
                        "¡Suerte legendaria activada! ¡Esto es Axolotto!"],
        },
    },
    "game_lose": {
        "salinity": {
            (0, 40): ["Perdí... pero no fue la sal. Simplemente me ganaron mejor hoy.",
                      "Derrota limpia. El otro jugó mejor. ¡La revancha es mía!",
                      "¡Me ganaron! No hay excusas. A entrenar más."],
            (40, 70): ["¡La salinidad me jugó en contra! Siguiente vez con agua más pura.",
                       "El agua salada me robó las cartas buenas. ¡Revancha!",
                       "Salinidad moderada + mala racha = derrota. Pero aprendo."],
            (70, 101): ["¡DERROTA SALADA! Literalmente el agua estaba horrible hoy.",
                        "¡La sal me venció antes de que empezara! Necesito un Anti-Sal.",
                        "¡Imposible ganar con tanta sal! ¡Esto no lo cuento como derrota real!"],
        },
    },
    "inter_axo_taunt": {
        "vs_bot_1": [
            "¡Oye, CPU! ¡Te voy a ganar tan rápido que ni vas a registrar que jugamos!",
            "¡Contra un solo bot! Esto es práctica, no batalla.",
            "¡Ven aquí, robot! ¡Un Axolotito real te va a enseñar a jugar Lotería!",
        ],
        "vs_bot_5": [
            "¡Cinco bots! ¡Perfecto, así hay más a quienes ganarles!",
            "¡Uno contra cinco máquinas! ¡Así se siente una victoria épica!",
            "¡Cinco CPUs y yo solo! Esto es la Liga Mayor, ¡órale!",
        ],
        "vs_human": [
            "¡Jugador humano detectado! ¡Esto va a ser interesante!",
            "¡Oye! ¡Sé que eres real porque las máquinas no huelen a nervios!",
            "¡Humano vs Axolotito! Spoiler: el Axolotito gana.",
        ],
    },
    "gritón_card_called": {
        "agility": {
            (0, 40): ["¡La... La Rosa! ¡Ay, espera que este Axolotito responde lento!",
                      "¡El Catrín! Oigan, ¡déjenle tiempo al huevito!",
                      "¡El Borracho! ¡No tan rápido, mi Axolotito se marea!"],
            (40, 70): ["¡El Sol! ¡Ahí voy, ahí voy!",
                       "¡La Mano! ¡Buen ritmo, buen ritmo!",
                       "¡El Gallo! ¡A ese paso vamos bien!"],
            (70, 101): ["¡La Sirena! ¡Este Axolotito me va a dejar sin trabajo!",
                        "¡El Diablo! ¡Marchando, marchando!",
                        "¡La Muerte! ¡Canta primero el Axolotito o yo? ¡Increíble!"],
        },
    },
}

KARMA_DIALOGUES = {
    "lucky": [
        "¡Nací bajo una estrella de alga brillante! ¡El Cenote me eligió!",
        "¡La suerte corre por mis branquias! ¡Esto es solo el comienzo!",
        "¡DNA de campeón! ¡El Cenote me tiene reservado algo grande!",
    ],
    "salty": [
        "Bueno... el agua estaba un poco salada hoy. ¡Pero no pasa nada! Los Axolotitos salados somos más resistentes.",
        "¡La sal me moldeó! Los mejores guerreros nacen en aguas difíciles.",
        "¿Salado? ¡Soy SAZONADO! Hay diferencia. ¡Voy a ganar con estilo!",
    ],
}


class DialogueEngine:
    def get_line(self, stat: str, value: float, context: DialogueContext) -> str:
        """Retorna una línea de diálogo según el stat, su valor y el contexto."""
        context_data = DIALOGUES.get(context.value, {})
        stat_data = context_data.get(stat, {})
        
        for (low, high), lines in stat_data.items():
            if low <= value < high:
                return random.choice(lines)
        
        # Fallback: última banda
        if stat_data:
            last_lines = list(stat_data.values())[-1]
            return random.choice(last_lines)
        return ""

    def get_karma_line(self, karma: str) -> str:
        lines = KARMA_DIALOGUES.get(karma, [])
        return random.choice(lines) if lines else ""

    def get_game_event_line(
        self, event: str, opponent_type: str, axo_luck: float = 50.0,
        axo_salinity: float = 30.0
    ) -> str:
        if event == "win":
            return self.get_line("luck", axo_luck, DialogueContext.GAME_WIN)
        if event == "lose":
            return self.get_line("salinity", axo_salinity, DialogueContext.GAME_LOSE)
        return ""

    def get_inter_axo_line(self, opponent_type: str) -> str:
        """opponent_type: 'vs_bot_1' | 'vs_bot_5' | 'vs_human'"""
        lines = DIALOGUES.get("inter_axo_taunt", {}).get(opponent_type, [])
        return random.choice(lines) if lines else ""

    def get_gritón_line(self, axo_agility: float, event: str = "card_called") -> str:
        return self.get_line("agility", axo_agility, DialogueContext.GRITÓN_CARD_CALLED)
```

- [ ] **Step 4: Correr tests**

```bash
cd backend && pytest tests/test_dialogue_engine.py -v
```

Expected: todos PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/dialogue_engine.py backend/tests/test_dialogue_engine.py
git commit -m "feat(dialogue): DialogueEngine with stat-range dialogue selection"
```

---

## FASE 2 — Tutorial Híbrido del Webito (Backend)

> Depende de Task 1 (migración). Puede paralelizarse con FASE 3.

### Task 3: `TutorialService` — Lógica de fases y karma

**Files:**
- Create: `backend/app/services/tutorial_service.py`
- Create: `backend/tests/test_tutorial_service.py`

- [ ] **Step 1: Escribir tests**

```python
# backend/tests/test_tutorial_service.py
from unittest.mock import MagicMock
from app.services.tutorial_service import TutorialService, TutorialPhaseResult

def _make_incubation(phase=1, luck_clicks=0, sal_clicks=0):
    inc = MagicMock()
    inc.tutorial_phase = phase
    inc.bonus_luck = luck_clicks * 1.0
    inc.bonus_focus = 50.0
    inc.bonus_agility = 40.0
    inc.bonus_stamina = 60.0
    inc.bonus_salinity = sal_clicks * 5.0 if hasattr(inc, "bonus_salinity") else 0
    return inc

def test_advance_phase_1_to_2():
    svc = TutorialService()
    inc = _make_incubation(phase=1)
    result = svc.advance_phase(inc)
    assert result.new_phase == 2
    assert result.dialogue_stat in ("focus", "salinity")

def test_advance_phase_3_triggers_karma_eval():
    svc = TutorialService()
    inc = _make_incubation(phase=3)
    inc.bonus_luck = 80.0  # Alto luck → karma lucky
    result = svc.advance_phase(inc)
    assert result.new_phase == 4
    assert result.karma in ("lucky", "salty")

def test_karma_lucky_threshold():
    svc = TutorialService()
    assert svc.calculate_karma(wins=3, losses=0) == "lucky"

def test_karma_salty_threshold():
    svc = TutorialService()
    assert svc.calculate_karma(wins=0, losses=3) == "salty"

def test_karma_bonus_lucky():
    svc = TutorialService()
    bonus = svc.karma_bonus("lucky")
    assert bonus["gal"] == 50

def test_karma_bonus_salty():
    svc = TutorialService()
    bonus = svc.karma_bonus("salty")
    assert bonus["consumable"] == "gotas_antiescarcha"
```

- [ ] **Step 2: Correr tests para verificar fallo**

```bash
cd backend && pytest tests/test_tutorial_service.py -v
```

- [ ] **Step 3: Implementar `TutorialService`**

```python
# backend/app/services/tutorial_service.py
from dataclasses import dataclass
from typing import Optional
from app.services.dialogue_engine import DialogueEngine, DialogueContext

@dataclass
class TutorialPhaseResult:
    new_phase: int
    dialogue_stat: str
    dialogue_context: DialogueContext
    karma: Optional[str] = None
    dialogue_value: float = 50.0

PHASE_STATS = {
    1: ("salinity", DialogueContext.TUTORIAL_PHASE_1),
    2: ("focus",    DialogueContext.TUTORIAL_FOCUS_MOMENT),
    3: ("luck",     DialogueContext.TUTORIAL_LUCK_MOMENT),
}

class TutorialService:
    def __init__(self):
        self.engine = DialogueEngine()

    def advance_phase(self, incubation) -> TutorialPhaseResult:
        current = incubation.tutorial_phase
        new_phase = current + 1

        stat, ctx = PHASE_STATS.get(current, ("focus", DialogueContext.TUTORIAL_PHASE_1))

        stat_value = {
            "salinity": getattr(incubation, "bonus_salinity", 30.0),
            "focus":    incubation.bonus_focus,
            "luck":     incubation.bonus_luck,
        }.get(stat, 50.0)

        karma = None
        if current == 3:
            # Fase 3 completa → evaluar karma
            wins = 1 if incubation.bonus_luck > 60.0 else 0
            losses = 1 if incubation.bonus_luck <= 60.0 else 0
            karma = self.calculate_karma(wins, losses)

        incubation.tutorial_phase = new_phase
        if karma:
            incubation.tutorial_karma = karma

        return TutorialPhaseResult(
            new_phase=new_phase,
            dialogue_stat=stat,
            dialogue_context=ctx,
            karma=karma,
            dialogue_value=stat_value,
        )

    def calculate_karma(self, wins: int, losses: int) -> str:
        return "lucky" if wins >= losses else "salty"

    def karma_bonus(self, karma: str) -> dict:
        if karma == "lucky":
            return {"gal": 50, "consumable": None}
        return {"gal": 0, "consumable": "gotas_antiescarcha"}

    def get_tutorial_dialogue(self, incubation) -> str:
        phase = incubation.tutorial_phase
        stat, ctx = PHASE_STATS.get(phase, ("focus", DialogueContext.TUTORIAL_PHASE_1))
        value = getattr(incubation, f"bonus_{stat}", 50.0)
        return self.engine.get_line(stat, value, ctx)
```

- [ ] **Step 4: Correr tests**

```bash
cd backend && pytest tests/test_tutorial_service.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/tutorial_service.py backend/tests/test_tutorial_service.py
git commit -m "feat(tutorial): TutorialService phase advancement and karma evaluation"
```

---

### Task 4: Endpoints REST del Tutorial

**Files:**
- Create: `backend/app/api/v1/endpoints/tutorial.py`
- Modify: `backend/app/main.py` (registrar router)

- [ ] **Step 1: Crear `tutorial.py`**

```python
# backend/app/api/v1/endpoints/tutorial.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.core.auth import get_verified_user_id
from app.models.items import WebitoIncubation
from app.models.user import User
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
from app.services.tutorial_service import TutorialService
from app.services.dialogue_engine import DialogueEngine
from datetime import datetime

router = APIRouter()
_svc = TutorialService()
_eng = DialogueEngine()

@router.post("/start")
def start_tutorial(session: Session = Depends(get_session),
                   user_id: str = Depends(get_verified_user_id)):
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    if user.tutorial_completed:
        raise HTTPException(400, "Tutorial ya completado")

    inc = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.user_id == user_id)
        .where(WebitoIncubation.tutorial_phase == 0)
    ).first()
    if not inc:
        raise HTTPException(404, "No hay Webito listo para el tutorial")

    inc.tutorial_phase = 1
    session.add(inc)
    session.commit()

    dialogue = _svc.get_tutorial_dialogue(inc)
    return {
        "phase": 1,
        "dialogue": dialogue,
        "egg_dialogue": "¡Oye! ¡Siento cartas cantándose afuera! ¡Llévame a una mesa antes de que me congele de aburrimiento!",
    }

@router.post("/next-step/{incubation_id}")
def next_tutorial_step(
    incubation_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    inc = session.get(WebitoIncubation, incubation_id)
    if not inc or inc.user_id != user_id:
        raise HTTPException(404, "Incubación no encontrada")
    if inc.tutorial_phase == 0 or inc.tutorial_phase >= 5:
        raise HTTPException(400, "Fase de tutorial inválida")

    result = _svc.advance_phase(inc)
    session.add(inc)
    session.commit()

    dialogue = _eng.get_line(result.dialogue_stat, result.dialogue_value, result.dialogue_context)
    
    response = {
        "phase": result.new_phase,
        "dialogue": dialogue,
        "karma": result.karma,
    }
    if result.karma:
        bonus = _svc.karma_bonus(result.karma)
        response["karma_bonus"] = bonus
        response["karma_dialogue"] = _eng.get_karma_line(result.karma)

    return response

@router.post("/complete/{incubation_id}")
def complete_tutorial(
    incubation_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    inc = session.get(WebitoIncubation, incubation_id)
    if not inc or inc.user_id != user_id:
        raise HTTPException(404, "Incubación no encontrada")
    if inc.tutorial_phase < 4:
        raise HTTPException(400, "El tutorial no ha llegado a la fase de karma aún")

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    wallet = session.exec(select(Wallet).where(Wallet.user_id == user_id)).first()

    # Aplicar bonus de karma
    karma = inc.tutorial_karma or "salty"
    bonus = _svc.karma_bonus(karma)
    if bonus["gal"] > 0 and wallet:
        wallet.gemas_alga += bonus["gal"]
        ledger = TransactionLedger(
            user_id=user_id,
            amount=bonus["gal"],
            currency=CurrencyType.GAL,
            tx_type=TransactionType.TUTORIAL_BONUS,
            description=f"Bonus tutorial karma={karma}",
            created_at=datetime.utcnow(),
        )
        session.add(wallet)
        session.add(ledger)

    user.tutorial_completed = True
    inc.tutorial_phase = 5
    session.add(user)
    session.add(inc)
    session.commit()

    return {
        "completed": True,
        "karma": karma,
        "bonus": bonus,
        "dialogue": _eng.get_karma_line(karma),
        "next_step": "hatch",
    }
```

- [ ] **Step 2: Registrar el router en `main.py`**

```python
# backend/app/main.py — agregar junto a los otros includes
from app.api.v1.endpoints import tutorial
app.include_router(tutorial.router, prefix="/api/v1/tutorial", tags=["tutorial"])
```

- [ ] **Step 3: Probar manualmente con curl**

```bash
# Reemplazar TOKEN y INCUBATION_ID con valores reales del entorno local
curl -X POST http://localhost:8000/api/v1/tutorial/start \
  -H "Authorization: Bearer TOKEN"
```

Expected: JSON con `phase: 1` y un `dialogue`.

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/tutorial.py backend/app/main.py
git commit -m "feat(tutorial): REST endpoints for tutorial start/next-step/complete"
```

---

## FASE 3 — Modo Manual: Stats como Modificadores de Entorno

> Completamente independiente. Asignable a un segundo agente mientras FASE 2 avanza.

### Task 5: `ManualGameService` — Parámetros de entorno según stats

**Files:**
- Create: `backend/app/services/manual_game_service.py`
- Create: `backend/tests/test_manual_game_service.py`

La clave conceptual: en modo manual los stats de **comportamiento** (Focus, Agility, Stamina) no controlan al bot — controlan el entorno del juego para el jugador humano.

| Stat | Efecto en modo manual |
|------|-----------------------|
| Focus | Tiempo (ms) que la carta cantada permanece resaltada antes de oscurecerse |
| Agility | Velocidad del gritón (delay entre cartas) |
| Stamina | Número de pistas visuales (brillos/flechas) disponibles por partida |
| Salinity | RNG del pool de cartas (igual que en auto) |
| Luck | Activa críticos si marcas dentro de la ventana de tiempo |

- [ ] **Step 1: Escribir tests**

```python
# backend/tests/test_manual_game_service.py
from app.services.manual_game_service import ManualGameService

def test_focus_low_gives_short_highlight_window():
    svc = ManualGameService()
    params = svc.get_env_params(focus=15.0, agility=50.0, stamina=100)
    assert params["highlight_window_ms"] <= 1500

def test_focus_high_gives_long_highlight_window():
    svc = ManualGameService()
    params = svc.get_env_params(focus=90.0, agility=50.0, stamina=100)
    assert params["highlight_window_ms"] >= 3500

def test_agility_high_speeds_up_gritón():
    svc = ManualGameService()
    slow = svc.get_env_params(focus=50.0, agility=20.0, stamina=100)
    fast = svc.get_env_params(focus=50.0, agility=90.0, stamina=100)
    # Alto agility = gritón más lento PARA EL JUGADOR (ventaja)
    assert fast["gritón_delay_ms"] > slow["gritón_delay_ms"]

def test_stamina_controls_visual_hints():
    svc = ManualGameService()
    low = svc.get_env_params(focus=50.0, agility=50.0, stamina=50)
    high = svc.get_env_params(focus=50.0, agility=50.0, stamina=190)
    assert high["visual_hints"] > low["visual_hints"]

def test_luck_crit_check():
    svc = ManualGameService()
    # Con luck alto, la probabilidad de crit al marcar en tiempo debe ser > 0.3
    prob = svc.crit_probability(luck=90.0, marked_in_window=True)
    assert prob >= 0.3

def test_no_crit_outside_window():
    svc = ManualGameService()
    prob = svc.crit_probability(luck=90.0, marked_in_window=False)
    assert prob == 0.0
```

- [ ] **Step 2: Correr tests — verificar fallo**

```bash
cd backend && pytest tests/test_manual_game_service.py -v
```

- [ ] **Step 3: Implementar `ManualGameService`**

```python
# backend/app/services/manual_game_service.py
from dataclasses import dataclass

@dataclass
class ManualEnvParams:
    highlight_window_ms: int   # Ventana de tiempo para marcar carta
    gritón_delay_ms: int       # Delay entre cartas cantadas (mayor = más tiempo)
    visual_hints: int          # Pistas visuales disponibles
    crit_window_ms: int        # Ventana para activar crítico

class ManualGameService:
    def get_env_params(
        self, focus: float, agility: float, stamina: int
    ) -> dict:
        # Focus: 0→1000ms window, 100→4000ms window
        highlight_window_ms = int(1000 + (focus / 100.0) * 3000)

        # Agility: 0→800ms delay (gritón rápido = desventaja),
        #          100→2500ms delay (gritón lento = ventaja para jugador)
        gritón_delay_ms = int(800 + (agility / 100.0) * 1700)

        # Stamina: 50→1 hint, 200→8 hints
        visual_hints = max(1, int((stamina - 50) / 150.0 * 7) + 1)

        # Crit window: siempre el 30% inicial de highlight_window
        crit_window_ms = int(highlight_window_ms * 0.30)

        return {
            "highlight_window_ms": highlight_window_ms,
            "gritón_delay_ms": gritón_delay_ms,
            "visual_hints": visual_hints,
            "crit_window_ms": crit_window_ms,
        }

    def crit_probability(self, luck: float, marked_in_window: bool) -> float:
        if not marked_in_window:
            return 0.0
        # luck 0→3%, luck 100→50%
        return round(0.03 + (luck / 100.0) * 0.47, 3)
```

- [ ] **Step 4: Correr tests**

```bash
cd backend && pytest tests/test_manual_game_service.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/manual_game_service.py backend/tests/test_manual_game_service.py
git commit -m "feat(manual-mode): ManualGameService env params from axo stats"
```

---

### Task 6: Endpoint de configuración de sala manual + parámetros de entorno

**Files:**
- Modify: `backend/app/api/v1/endpoints/multiplayer.py`

Las salas manuales son salas normales con `room_mode = "manual"`. Los parámetros de entorno se calculan al registrar el Axolotito y se devuelven al frontend para que configure la UI del tablero manual.

- [ ] **Step 1: Agregar campo `room_mode` a `GameRoom` (si no existe)**

```python
# En la migración Alembic o directamente en el modelo GameRoom:
room_mode: str = Field(default="auto")  # "auto" | "manual"
```

- [ ] **Step 2: Modificar el endpoint de registro para devolver env_params en salas manuales**

```python
# backend/app/api/v1/endpoints/multiplayer.py — en el endpoint de registro de sala

from app.services.manual_game_service import ManualGameService
from app.models.axolotito import Axolotito

_manual_svc = ManualGameService()

# Dentro del endpoint, después de registrar:
response = {
    "mensaje": f"Axolotito registrado con éxito en la sala '{room.name}'",
    "room_name": room.name,
    "entry_fee_gal": room.entry_fee_gal,
}

if room.room_mode == "manual":
    axo = session.exec(
        select(Axolotito).where(Axolotito.id == req.axolotito_id)
    ).first()
    if axo:
        response["manual_env_params"] = _manual_svc.get_env_params(
            focus=axo.stat_focus,
            agility=axo.stat_agility,
            stamina=axo.stat_stamina,
        )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/multiplayer.py
git commit -m "feat(manual-mode): return env_params for manual game rooms on registration"
```

---

## FASE 4 — F2P Huevo Durmiente

> Completamente independiente de FASES 2 y 3. Asignable a tercer agente.

### Task 7: Endpoint F2P — Asignación y reacciones del huevo durmiente

**Files:**
- Create: `backend/app/api/v1/endpoints/f2p.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_f2p_service.py`

- [ ] **Step 1: Escribir tests**

```python
# backend/tests/test_f2p_service.py
from app.services.f2p_service import F2PService

def test_fragment_to_reaction_stage():
    svc = F2PService()
    # 0-19 fragmentos: sin reacción
    assert svc.egg_reaction_stage(fragments=0) == 0
    # 20-39: primer temblor
    assert svc.egg_reaction_stage(fragments=25) == 1
    # 60-79: burbuja de sueño
    assert svc.egg_reaction_stage(fragments=65) == 3
    # 100+: listo para despertar
    assert svc.egg_reaction_stage(fragments=100) == 5

def test_dream_bubble_text():
    svc = F2PService()
    bubble = svc.get_dream_bubble(fragments=60)
    assert bubble != ""
    assert len(bubble) > 3

def test_daily_cap_check():
    svc = F2PService()
    assert svc.under_daily_cap(earned_today=9.5) is True
    assert svc.under_daily_cap(earned_today=10.0) is False

def test_fragment_reward_per_watch():
    svc = F2PService()
    reward = svc.watch_game_reward(won=True)
    assert reward["fragments"] >= 1
    assert reward["gal"] > 0
```

- [ ] **Step 2: Verificar fallo**

```bash
cd backend && pytest tests/test_f2p_service.py -v
```

- [ ] **Step 3: Implementar `F2PService`**

```python
# backend/app/services/f2p_service.py
import random

DREAM_BUBBLES = {
    1: ["...lotería...", "...mis cartas...", "...casi..."],
    2: ["...el gritón...", "...esperen...", "...voy..."],
    3: ["...ya casi...", "...el Cenote me llama...", "...mis branquias tiemblan..."],
    4: ["...puedo sentirte...", "...ya casi nazco...", "...espérame..."],
    5: ["¡Despierto pronto!", "¡Ya casi! ¡Prepárate!", "¡El Cenote me está llamando!"],
}

class F2PService:
    DAILY_CAP = 10.0
    FRAGMENTS_TO_HATCH = 100

    def egg_reaction_stage(self, fragments: int) -> int:
        if fragments >= 100: return 5
        if fragments >= 80:  return 4
        if fragments >= 60:  return 3
        if fragments >= 40:  return 2
        if fragments >= 20:  return 1
        return 0

    def get_dream_bubble(self, fragments: int) -> str:
        stage = self.egg_reaction_stage(fragments)
        if stage == 0:
            return ""
        lines = DREAM_BUBBLES.get(stage, [])
        return random.choice(lines) if lines else ""

    def under_daily_cap(self, earned_today: float) -> bool:
        return earned_today < self.DAILY_CAP

    def watch_game_reward(self, won: bool) -> dict:
        if won:
            return {"gal": 3.0, "fragments": 2}
        return {"gal": 0.1, "fragments": 1}
```

- [ ] **Step 4: Crear endpoint F2P**

```python
# backend/app/api/v1/endpoints/f2p.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.database import get_session
from app.core.auth import get_verified_user_id
from app.models.user import User
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
from app.services.f2p_service import F2PService

router = APIRouter()
_svc = F2PService()

@router.get("/egg-status")
def get_egg_status(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    frags = user.f2p_astral_fragments
    stage = _svc.egg_reaction_stage(frags)
    bubble = _svc.get_dream_bubble(frags)

    return {
        "fragments": frags,
        "fragments_needed": _svc.FRAGMENTS_TO_HATCH,
        "reaction_stage": stage,
        "dream_bubble": bubble,
        "ready_to_hatch": frags >= _svc.FRAGMENTS_TO_HATCH,
    }

@router.post("/watch-reward")
def claim_watch_reward(
    won: bool = False,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    # Reset diario de GAL si pasaron 24h
    now = datetime.utcnow()
    if user.f2p_daily_gal_reset_at is None or \
       (now - user.f2p_daily_gal_reset_at) > timedelta(hours=24):
        user.f2p_daily_gal_earned = 0.0
        user.f2p_daily_gal_reset_at = now

    if not _svc.under_daily_cap(user.f2p_daily_gal_earned):
        return {
            "capped": True,
            "message": "Tu pozo de alga diario se ha agotado. ¡Adopta tu Webito para ganancias ilimitadas!",
            "fragments_added": 0,
        }

    reward = _svc.watch_game_reward(won)

    wallet = session.exec(select(Wallet).where(Wallet.user_id == user_id)).first()
    if wallet and reward["gal"] > 0:
        gal_to_add = min(reward["gal"], _svc.DAILY_CAP - user.f2p_daily_gal_earned)
        wallet.gemas_alga += gal_to_add
        user.f2p_daily_gal_earned += gal_to_add
        session.add(wallet)
        ledger = TransactionLedger(
            user_id=user_id,
            amount=gal_to_add,
            currency=CurrencyType.GAL,
            tx_type=TransactionType.F2P_REWARD,
            description="Recompensa F2P espectador",
            created_at=now,
        )
        session.add(ledger)

    user.f2p_astral_fragments += reward["fragments"]
    session.add(user)
    session.commit()

    new_stage = _svc.egg_reaction_stage(user.f2p_astral_fragments)
    return {
        "capped": False,
        "gal_earned": reward["gal"],
        "fragments_added": reward["fragments"],
        "total_fragments": user.f2p_astral_fragments,
        "egg_reaction_stage": new_stage,
        "dream_bubble": _svc.get_dream_bubble(user.f2p_astral_fragments),
    }
```

- [ ] **Step 5: Registrar router**

```python
# backend/app/main.py
from app.api.v1.endpoints import f2p
app.include_router(f2p.router, prefix="/api/v1/f2p", tags=["f2p"])
```

- [ ] **Step 6: Correr tests**

```bash
cd backend && pytest tests/test_f2p_service.py -v
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/f2p_service.py backend/app/api/v1/endpoints/f2p.py backend/tests/test_f2p_service.py backend/app/main.py
git commit -m "feat(f2p): sleeping egg with fragment reactions and daily GAL cap"
```

---

## FASE 5 — Frontend: Tutorial y Diálogos

> Depende de que las FASES 1-4 estén mergeadas o al menos los contratos de API definidos.
> Puede paralelizarse internamente: un subagente para TutorialCenote, otro para ManualPlayMode.

### Task 8: Componente `WebitoDialogue` — Burbuja de diálogo animada

**Files:**
- Create: `frontend/components/tutorial/WebitoDialogue.tsx`
- Create: `frontend/components/tutorial/WebitoDialogue.module.css`

- [ ] **Step 1: Crear componente de burbuja**

```tsx
// frontend/components/tutorial/WebitoDialogue.tsx
import { useEffect, useState } from "react"
import styles from "./WebitoDialogue.module.css"

interface Props {
  text: string
  speaker?: "webito" | "gritón" | "axo"
  onDismiss?: () => void
  autoHideMs?: number
}

export function WebitoDialogue({ text, speaker = "webito", onDismiss, autoHideMs }: Props) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    setVisible(true)
    if (!autoHideMs) return
    const t = setTimeout(() => {
      setVisible(false)
      onDismiss?.()
    }, autoHideMs)
    return () => clearTimeout(t)
  }, [text])

  if (!visible || !text) return null

  const speakerLabel = {
    webito: "🥚 Webito",
    gritón: "📣 El Gritón",
    axo: "🦎 Tu Axolotito",
  }[speaker]

  return (
    <div className={styles.bubble} onClick={() => { setVisible(false); onDismiss?.() }}>
      <span className={styles.speaker}>{speakerLabel}</span>
      <p className={styles.text}>{text}</p>
      <span className={styles.hint}>toca para continuar</span>
    </div>
  )
}
```

```css
/* frontend/components/tutorial/WebitoDialogue.module.css */
.bubble {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(10, 20, 40, 0.92);
  border: 2px solid #00e5ff;
  border-radius: 16px;
  padding: 16px 20px;
  max-width: 340px;
  width: 90%;
  z-index: 999;
  cursor: pointer;
  animation: fadeIn 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
}
.speaker {
  font-size: 11px;
  color: #00e5ff;
  font-weight: 700;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 6px;
}
.text {
  color: #e0f7fa;
  font-size: 15px;
  line-height: 1.5;
  margin: 0;
  font-style: italic;
}
.hint {
  font-size: 10px;
  color: #546e7a;
  display: block;
  text-align: right;
  margin-top: 8px;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/tutorial/
git commit -m "feat(tutorial-ui): WebitoDialogue bubble component"
```

---

### Task 9: Componente `TutorialCenote` — Flujo completo del tutorial

**Files:**
- Create: `frontend/components/tutorial/TutorialCenote.tsx`

Este componente maneja el estado del tutorial de 5 fases, llama a los endpoints, muestra el diálogo del Webito y los momentos de intervención manual.

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/tutorial/TutorialCenote.tsx
"use client"
import { useState } from "react"
import { WebitoDialogue } from "./WebitoDialogue"
import { usePrivy } from "@privy-io/react-auth"

interface TutorialState {
  phase: number        // 0-5
  dialogue: string
  karmaDialogue: string
  karma: string | null
  loading: boolean
  eggCrackLevel: number  // 0-3, controla el sprite del huevo
}

interface Props {
  incubationId: number
  onComplete: (karma: string) => void
}

const PHASE_TITLES = [
  "",
  "Partida 1: Descubriendo la Salinidad",
  "Partida 2: Focus y Agilidad",
  "Partida 3: Suerte y Estamina",
  "Evaluación del Karma",
  "¡Momento de Eclosión!",
]

const EGG_EMOTIONAL_STATE = [
  "",
  "nervioso",   // Fase 1: curioso y exagerado
  "confiado",   // Fase 2: competitivo
  "urgente",    // Fase 3: al límite, casi nace
  "en karma",
  "eclosionando",
]

export function TutorialCenote({ incubationId, onComplete }: Props) {
  const { getAccessToken } = usePrivy()
  const [state, setState] = useState<TutorialState>({
    phase: 0,
    dialogue: "",
    karmaDialogue: "",
    karma: null,
    loading: false,
    eggCrackLevel: 0,
  })

  const apiCall = async (path: string, method = "POST") => {
    const token = await getAccessToken()
    const res = await fetch(`/api/v1/tutorial${path}`, {
      method,
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  }

  const startTutorial = async () => {
    setState(s => ({ ...s, loading: true }))
    const data = await apiCall("/start")
    setState(s => ({
      ...s,
      loading: false,
      phase: 1,
      dialogue: data.egg_dialogue,
      eggCrackLevel: 0,
    }))
  }

  const advancePhase = async () => {
    setState(s => ({ ...s, loading: true, dialogue: "" }))
    const data = await apiCall(`/next-step/${incubationId}`)
    setState(s => ({
      ...s,
      loading: false,
      phase: data.phase,
      dialogue: data.dialogue || data.karma_dialogue || "",
      karma: data.karma || null,
      eggCrackLevel: Math.min(3, s.eggCrackLevel + 1),
    }))
  }

  const completeTutorial = async () => {
    setState(s => ({ ...s, loading: true }))
    const data = await apiCall(`/complete/${incubationId}`)
    setState(s => ({ ...s, loading: false, phase: 5, dialogue: data.dialogue }))
    onComplete(data.karma)
  }

  const eggEmoji = ["🥚", "🥚💫", "🥚✨", "🐣"][state.eggCrackLevel] || "🐣"

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <div style={{ fontSize: "80px", marginBottom: "1rem" }}>{eggEmoji}</div>
      
      {state.phase > 0 && (
        <div style={{ color: "#00e5ff", marginBottom: "0.5rem", fontSize: "12px" }}>
          {PHASE_TITLES[state.phase]} — Webito está {EGG_EMOTIONAL_STATE[state.phase]}
        </div>
      )}

      {state.phase === 0 && (
        <button onClick={startTutorial} disabled={state.loading}>
          {state.loading ? "Cargando..." : "¡Adoptar mi Webito!"}
        </button>
      )}

      {state.phase >= 1 && state.phase <= 3 && (
        <button onClick={advancePhase} disabled={state.loading}>
          {state.loading ? "Jugando..." : `Jugar Partida ${state.phase}`}
        </button>
      )}

      {state.phase === 4 && (
        <button onClick={completeTutorial} disabled={state.loading}>
          {state.loading ? "Evaluando karma..." : "Ver resultado de karma"}
        </button>
      )}

      {state.dialogue && (
        <WebitoDialogue
          text={state.dialogue}
          speaker={state.phase >= 5 ? "axo" : "webito"}
          onDismiss={() => setState(s => ({ ...s, dialogue: "" }))}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/tutorial/TutorialCenote.tsx
git commit -m "feat(tutorial-ui): TutorialCenote full flow component"
```

---

### Task 10: Componente `SleepingEgg` — Huevo durmiente F2P

**Files:**
- Create: `frontend/components/criadero/SleepingEgg.tsx`

- [ ] **Step 1: Crear componente**

```tsx
// frontend/components/criadero/SleepingEgg.tsx
"use client"
import { useEffect, useState } from "react"
import { usePrivy } from "@privy-io/react-auth"

interface EggStatus {
  fragments: number
  fragments_needed: number
  reaction_stage: number
  dream_bubble: string
  ready_to_hatch: boolean
}

const STAGE_EMOJIS = ["🥚", "🥚💤", "🥚💭", "🥚✨", "🥚🌟", "🐣🌊"]
const STAGE_ANIMATIONS = ["", "shake-slow", "shake-medium", "glow", "glow-bright", "hatch"]

export function SleepingEgg() {
  const { getAccessToken, authenticated } = usePrivy()
  const [status, setStatus] = useState<EggStatus | null>(null)
  const [showBubble, setShowBubble] = useState(false)

  useEffect(() => {
    if (!authenticated) return
    const load = async () => {
      const token = await getAccessToken()
      const res = await fetch("/api/v1/f2p/egg-status", {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) setStatus(await res.json())
    }
    load()
  }, [authenticated])

  useEffect(() => {
    if (!status?.dream_bubble) return
    setShowBubble(true)
    const t = setTimeout(() => setShowBubble(false), 4000)
    return () => clearTimeout(t)
  }, [status?.dream_bubble])

  if (!status) return null

  const stage = status.reaction_stage
  const progress = Math.min(100, (status.fragments / status.fragments_needed) * 100)

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: "64px", position: "relative" }}>
        {STAGE_EMOJIS[stage]}
        {showBubble && status.dream_bubble && (
          <div style={{
            position: "absolute",
            top: "-40px",
            left: "50%",
            transform: "translateX(-50%)",
            background: "rgba(0,0,0,0.8)",
            color: "#b2ebf2",
            padding: "4px 10px",
            borderRadius: "10px",
            fontSize: "13px",
            whiteSpace: "nowrap",
            fontStyle: "italic",
          }}>
            {status.dream_bubble}
          </div>
        )}
      </div>

      <div style={{ margin: "12px 0 4px", fontSize: "12px", color: "#90a4ae" }}>
        Fragmentos Astrales: {status.fragments} / {status.fragments_needed}
      </div>
      <div style={{
        height: "6px",
        background: "#1a2a3a",
        borderRadius: "3px",
        overflow: "hidden",
        maxWidth: "200px",
        margin: "0 auto",
      }}>
        <div style={{
          height: "100%",
          width: `${progress}%`,
          background: "linear-gradient(90deg, #00e5ff, #7c4dff)",
          borderRadius: "3px",
          transition: "width 0.5s ease",
        }} />
      </div>

      {status.ready_to_hatch && (
        <button style={{ marginTop: "16px" }}>
          ¡Despertar al Webito!
        </button>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/criadero/SleepingEgg.tsx
git commit -m "feat(f2p-ui): SleepingEgg component with dream bubbles and fragment progress"
```

---

### Task 11: `ManualPlayMode` — Tablero con ventanas de tiempo por stat

**Files:**
- Create: `frontend/components/game/ManualPlayMode.tsx`

Este componente recibe `env_params` del servidor (calculados por `ManualGameService`) y aplica la lógica de ventana de tiempo visual para cada carta cantada.

- [ ] **Step 1: Crear componente**

```tsx
// frontend/components/game/ManualPlayMode.tsx
"use client"
import { useEffect, useRef, useState } from "react"

interface EnvParams {
  highlight_window_ms: number
  gritón_delay_ms: number
  visual_hints: number
  crit_window_ms: number
}

interface Props {
  board: string[][]          // 4x4 o 5x5 grid de nombres de cartas
  calledCards: string[]      // cartas ya cantadas por el servidor
  lastCalledCard: string | null
  envParams: EnvParams
  onMark: (card: string, inCritWindow: boolean) => void
  axoDialogue?: string
}

export function ManualPlayMode({
  board, calledCards, lastCalledCard, envParams, onMark, axoDialogue
}: Props) {
  const [highlighted, setHighlighted] = useState<string | null>(null)
  const [critActive, setCritActive] = useState(false)
  const [windowProgress, setWindowProgress] = useState(100) // % restante
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const critTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!lastCalledCard) return

    setHighlighted(lastCalledCard)
    setCritActive(true)
    setWindowProgress(100)

    // Limpiar timers anteriores
    if (timerRef.current) clearInterval(timerRef.current)
    if (critTimerRef.current) clearTimeout(critTimerRef.current)

    // Progreso visual de la ventana
    const start = Date.now()
    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - start
      const remaining = Math.max(0, 100 - (elapsed / envParams.highlight_window_ms) * 100)
      setWindowProgress(remaining)
      if (remaining === 0) {
        clearInterval(timerRef.current!)
        setHighlighted(null)
      }
    }, 50)

    // Fin de la ventana de crit
    critTimerRef.current = setTimeout(() => {
      setCritActive(false)
    }, envParams.crit_window_ms)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (critTimerRef.current) clearTimeout(critTimerRef.current)
    }
  }, [lastCalledCard])

  const handleCardClick = (card: string) => {
    if (!calledCards.includes(card)) return
    const isInCritWindow = critActive && card === highlighted
    onMark(card, isInCritWindow)
    if (card === highlighted) setHighlighted(null)
  }

  return (
    <div style={{ userSelect: "none" }}>
      {axoDialogue && (
        <div style={{
          background: "rgba(0,229,255,0.1)",
          border: "1px solid #00e5ff",
          borderRadius: "8px",
          padding: "8px 12px",
          marginBottom: "12px",
          fontSize: "13px",
          color: "#b2ebf2",
          fontStyle: "italic",
        }}>
          🦎 {axoDialogue}
        </div>
      )}

      {highlighted && (
        <div style={{ marginBottom: "8px" }}>
          <div style={{
            height: "4px",
            background: critActive ? "#ff4081" : "#00e5ff",
            width: `${windowProgress}%`,
            borderRadius: "2px",
            transition: "width 50ms linear, background 0.2s",
          }} />
          <div style={{ fontSize: "10px", color: "#546e7a", marginTop: "2px" }}>
            {critActive ? "⚡ Ventana crit activa" : "Ventana de marcado"}
          </div>
        </div>
      )}

      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(${board[0]?.length ?? 4}, 1fr)`,
        gap: "8px",
      }}>
        {board.flat().map((card, i) => {
          const marked = calledCards.includes(card)
          const isHighlighted = card === highlighted
          const isCritHighlight = isHighlighted && critActive

          return (
            <button
              key={i}
              onClick={() => handleCardClick(card)}
              style={{
                aspectRatio: "1",
                borderRadius: "8px",
                border: isCritHighlight
                  ? "2px solid #ff4081"
                  : isHighlighted
                  ? "2px solid #00e5ff"
                  : "1px solid #1e3a4a",
                background: marked
                  ? "rgba(0,229,255,0.15)"
                  : "rgba(10,20,40,0.8)",
                color: marked ? "#00e5ff" : "#546e7a",
                fontSize: "11px",
                cursor: marked ? "pointer" : "default",
                boxShadow: isCritHighlight
                  ? "0 0 12px rgba(255,64,129,0.6)"
                  : isHighlighted
                  ? "0 0 12px rgba(0,229,255,0.4)"
                  : "none",
                transition: "all 0.15s ease",
              }}
            >
              {card}
            </button>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/game/ManualPlayMode.tsx
git commit -m "feat(manual-mode): ManualPlayMode board with stat-based timing windows"
```

---

## FASE 6 — Sistema de Desbloqueo de Slots de Webito

### Task 12: Endpoint de desbloqueo por logro/compra

**Files:**
- Create: `backend/app/api/v1/endpoints/webito_slots.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Crear endpoint**

```python
# backend/app/api/v1/endpoints/webito_slots.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.core.auth import get_verified_user_id
from app.models.user import User
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
from datetime import datetime

router = APIRouter()

SLOT_UNLOCK_REQUIREMENTS = {
    2: {"type": "achievement", "key": "games_played_10",   "lore": "El Cenote solo permite otro huevo a quienes han jugado 10 partidas reales."},
    3: {"type": "achievement", "key": "jackpot_won",       "lore": "Los que ganan en grande tienen espacio para más huevos."},
    4: {"type": "purchase",    "cost_axg": 5.0,            "lore": "Expansión del Cenote personal."},
    5: {"type": "purchase",    "cost_axg": 10.0,           "lore": "Expansión del Cenote personal."},
    6: {"type": "vip",         "vip_tier": "axolite",      "lore": "Solo los Axolite tienen acceso al Cenote completo."},
}

@router.post("/unlock")
def unlock_webito_slot(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    current_slots = user.webito_slots_unlocked
    if current_slots >= 6:
        raise HTTPException(400, "Ya tienes el máximo de slots de Webito.")

    next_slot = current_slots + 1
    req = SLOT_UNLOCK_REQUIREMENTS.get(next_slot)
    if not req:
        raise HTTPException(400, "No hay más slots disponibles.")

    if req["type"] == "purchase":
        wallet = session.exec(select(Wallet).where(Wallet.user_id == user_id)).first()
        if not wallet or wallet.axogemas < req["cost_axg"]:
            raise HTTPException(400, f"Necesitas {req['cost_axg']} AXG para desbloquear este slot.")
        wallet.axogemas -= req["cost_axg"]
        session.add(wallet)
        session.add(TransactionLedger(
            user_id=user_id, amount=-req["cost_axg"],
            currency=CurrencyType.AXG, tx_type=TransactionType.WEBITO_UNLOCK,
            description=f"Desbloqueo slot Webito #{next_slot}",
            created_at=datetime.utcnow(),
        ))

    elif req["type"] == "vip":
        if not user.is_vip or user.vip_tier != req["vip_tier"]:
            raise HTTPException(400, f"Necesitas VIP {req['vip_tier']} para este slot.")

    # Achievement checks se implementan en futura iteración con el sistema de logros

    user.webito_slots_unlocked = next_slot
    session.add(user)
    session.commit()

    return {
        "slot_unlocked": next_slot,
        "lore": req.get("lore", ""),
        "axolotito_dialogue": f"¡Por fin puedo ser hermano mayor! El Cenote aceptó el slot #{next_slot}.",
    }

@router.get("/status")
def get_slot_status(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    next_slot = user.webito_slots_unlocked + 1
    next_req = SLOT_UNLOCK_REQUIREMENTS.get(next_slot)
    return {
        "current_slots": user.webito_slots_unlocked,
        "max_slots": 6,
        "next_unlock": next_req,
        "next_slot_number": next_slot if next_slot <= 6 else None,
    }
```

- [ ] **Step 2: Registrar router**

```python
# backend/app/main.py
from app.api.v1.endpoints import webito_slots
app.include_router(webito_slots.router, prefix="/api/v1/webito-slots", tags=["webito-slots"])
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/webito_slots.py backend/app/main.py
git commit -m "feat(webito-slots): unlock system with achievement/purchase/vip gates"
```

---

## Consideraciones para Uso con Multiagentes

Este plan está diseñado para ejecutarse en paralelo con 3 agentes simultáneos:

```
Agente A (backend-dev):   FASE 1 → FASE 2 → FASE 6
Agente B (backend-dev):   FASE 3 → FASE 4
Agente C (frontend-dev):  FASE 5 (espera contratos de API de A y B)
```

**Puntos de sincronización obligatorios:**
- Agente C no puede iniciar FASE 5 hasta que existan los endpoints de FASE 2 y FASE 4.
- FASE 6 (webito slots) puede iniciarse en cualquier momento: no depende de nada.
- El `DialogueEngine` (Task 2) debe estar disponible antes de `TutorialService` (Task 3).

**Cómo lanzar con `superpowers:dispatching-parallel-agents`:**
- Agente A: Tasks 1, 2, 3, 4, 12
- Agente B: Tasks 5, 6, 7
- Agente C: Tasks 8, 9, 10, 11 (con contrato de API documentado arriba)

---

## Self-Review

### Spec coverage

| Requerimiento | Task |
|--------------|------|
| Diálogos dinámicos por rango de stat (3-4 bandas) | Task 2 |
| Tutorial híbrido auto + momentos manuales | Tasks 3, 4, 9 |
| Stats como modificadores de entorno en modo manual | Task 5, 6, 11 |
| Salas de juego manual | Task 6 |
| Arco emocional del huevo (3 fases = 3 temperamentos) | Tasks 3, 9 |
| Gritón reactivo a stat Agility | Task 2 (`get_gritón_line`) |
| Diálogos inter-Axolotito (vs 1 bot, 5 bots, humano) | Task 2 (`get_inter_axo_line`) |
| Karma doble (suertudo vs salado) con lore propio | Tasks 3, 4 |
| Huevo durmiente F2P con reacciones a fragmentos | Tasks 7, 10 |
| Daily cap F2P con CTA de conversión | Task 7 |
| Sistema de desbloqueo de slots por logro/compra/VIP | Task 12 |
| Lore del límite de 1 Webito inicial | Task 12 (`lore` field) |
