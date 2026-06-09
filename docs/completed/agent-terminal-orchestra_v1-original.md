# Agent Terminal Orchestra — Documento de Diseño

> **Versión:** 1.0
> **Fecha:** 2026-06-04
> **Estado:** Plan Maestro — Pendiente de implementación

---

## 1. Visión General

### 1.1 Problema

El taskboard actual (`tools/taskboard/`) spawnea agentes IA como **subprocesos headless**: corre `claude -p "prompt"` en background, captura stdout a un archivo de log, y el frontend hace polling de ese archivo. El usuario **no ve** a los agentes trabajar en tiempo real, **no puede interactuar** con ellos, y el sistema está limitado a **1 solo agente a la vez** (`MAX_CONCURRENT_AGENTS=1`).

### 1.2 Solución

**Agent Terminal Orchestra** — un sistema de orquestación que:

- Usa **tmux** para mantener **3 terminales siempre visibles** en una sola ventana
- Cada terminal corre un **agente IA distinto**: `claude`, `deepclaude`, `agy`
- Las tareas se **asignan automáticamente** al agente óptimo según el tipo de trabajo
- El **taskboard web** se mejora con un Agent Console Panel que muestra el output en vivo
- El usuario puede **ver todo el proceso** y **saltar a cualquier terminal** para interactuar

### 1.3 Principios de diseño

1. **Visibilidad total** — todo output de agentes es observable en tiempo real
2. **Interactividad** — el usuario puede intervenir en cualquier momento
3. **Especialización** — cada agente recibe tareas que aprovechan sus fortalezas
4. **Simplicidad** — una sola ventana tmux, un solo panel web, estado en archivos
5. **Reciclaje** — se reutiliza ~80% del código del taskboard actual

---

## 2. Arquitectura

### 2.1 Diagrama de sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NAVEGADOR WEB                                    │
│                   http://localhost:8181                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    KANBAN BOARD (6 columnas)                      │   │
│  │  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ ┌────────┐ ┌────┐│   │
│  │  │ WISHES │→│ CONCEPTS │→│ PLANNING │→│ DOING │→│ REVIEW │→│DONE││   │
│  │  └────────┘ └──────────┘ └──────────┘ └───────┘ └────────┘ └────┘│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  AGENT CONSOLE PANEL (3 cards)                    │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │   │
│  │  │    claude    ●   │ │  deepclaude  ○  │ │      agy     ●   │     │   │
│  │  │ BUSY: task-3     │ │ IDLE            │ │ BUSY: task-7     │     │   │
│  │  │ ┌───────────────┐│ │ ┌───────────────┐│ │ ┌───────────────┐│     │   │
│  │  │ │ > Analizando  ││ │ │ > _           ││ │ │ > Investigando││     │   │
│  │  │ │   auth flow.. ││ │ │               ││ │ │   mechanics.. ││     │   │
│  │  │ └───────────────┘│ │ └───────────────┘│ │ └───────────────┘│     │   │
│  │  │ [Attach] [Stop]  │ │ [Attach] [Send]  │ │ [Attach] [Stop]  │     │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                     HTTP REST + Polling (2s)
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                    TASKBOARD SERVER (Python)                             │
│                    Puerto 8181, gestionado por PM2                       │
│                                                                          │
│  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────┐   │
│  │ tmux_orchestrator │  │   agent_router     │  │ prompt_builder   │   │
│  │ (session/pane     │  │   (fortalezas,     │  │ (construye       │   │
│  │  mgmt, status,    │  │    asignación      │  │  prompts para    │   │
│  │  capture, watch)  │  │    automática)     │  │  cada agente)    │   │
│  └───────┬───────────┘  └────────┬───────────┘  └────────┬─────────┘   │
│          │                       │                        │             │
│  ┌───────┴───────────────────────┴────────────────────────┴─────────┐   │
│  │  routes.py  │  task_lifecycle.py  │  db.py  │  ai_router.py      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                    tmux send-keys / capture-pane
                    .tmux_state/ (status files)
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│              TMUX SESSION: "axolotto-agents"                             │
│              Una ventana, 4 panes en grid                                │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  azolotto-agents                  │claude BUSY│deep IDLE│agy BUSY │  │
│  │  Status bar with per-agent status │           │         │         │  │
│  ├────────────────────────┬──────────┴───────────┴────────────────────┤  │
│  │                        │                                            │  │
│  │   PANE 0: claude       │   PANE 1: deepclaude                      │  │
│  │                        │                                            │  │
│  │   $ claude             │   $ claude                                │  │
│  │   [BUSY: task-3]       │   [IDLE]                                  │  │
│  │                        │   > _                                     │  │
│  │   > Analizando el      │                                            │  │
│  │     sistema de auth    │                                            │  │
│  │     para identificar   │                                            │  │
│  │     vulnerabilidades.. │                                            │  │
│  │                        │                                            │  │
│  │                        ├────────────────────────────────────────────┤  │
│  │                        │                                            │  │
│  │                        │   PANE 2: agy                             │  │
│  │                        │                                            │  │
│  │                        │   $ agy                                   │  │
│  │                        │   [BUSY: task-7]                          │  │
│  │                        │                                            │  │
│  │                        │   > Investigando mecánicas                │  │
│  │                        │     de juego para el nuevo                │  │
│  │                        │     modo PvP...                           │  │
│  │                        │                                            │  │
│  ├────────────────────────┴────────────────────────────────────────────┤  │
│  │   PANE 3: monitor                                                    │  │
│  │                                                                      │  │
│  │   ┌──────────────────────────────────────────────────────────────┐   │  │
│  │   │  Agent Orchestra Monitor v1.0                   2026-06-04    │   │  │
│  │   │──────────────────────────────────────────────────────────────│   │  │
│  │   │  claude      │ BUSY │ task-3 │ 12m elapsed │ auth-middleware │   │  │
│  │   │  deepclaude  │ IDLE │ --     │ --          │ --             │   │  │
│  │   │  agy         │ BUSY │ task-7 │ 5m elapsed  │ game-mechanics │   │  │
│  │   │──────────────────────────────────────────────────────────────│   │  │
│  │   │  Queue: 2 pending                                            │   │  │
│  │   │  task-8 → claude (frontend: login page)                      │   │  │
│  │   │  task-9 → deepclaude (backend: rate limiter)                 │   │  │
│  │   │──────────────────────────────────────────────────────────────│   │  │
│  │   │  Log tail (task-3):                                          │   │  │
│  │   │  > Read auth_middleware.py:45-120                            │   │  │
│  │   │  > Found: token validation uses < instead of <=              │   │  │
│  │   │  > Writing fix...                                            │   │  │
│  │   └──────────────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
                               ▲
                               │  tmux attach -t axolotto-agents
                               │  (usuario ve los 4 panes, puede
                               │   navegar entre ellos y escribir)
┌──────────────────────────────┴──────────────────────────────────────────┐
│                         TERMINAL DEL USUARIO                             │
│  $ tmux attach -t axolotto-agents                                       │
│  (Ctrl+B ←→↑↓ para navegar entre panes)                                │
│  (Ctrl+B d para desconectarse)                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de una tarea

```
USUARIO                    TASKBOARD                       TMUX + AGENTES
───────                    ────────                       ───────────────
  │                          │                                │
  │  1. Crea "Nueva Idea"    │                                │
  │─────────────────────────>│                                │
  │                          │                                │
  │  2. AI procesa concepto  │                                │
  │     (título, scope,      │                                │
  │      categoría)          │                                │
  │                          │                                │
  │  3. Mueve a "Planning"   │                                │
  │─────────────────────────>│                                │
  │                          │                                │
  │  4. AI genera plan       │                                │
  │     (requisitos, files,  │                                │
  │      impact, design)     │                                │
  │                          │                                │
  │  5. Aprueba plan         │                                │
  │─────────────────────────>│                                │
  │                          │                                │
  │  6. Mueve a "Doing"      │                                │
  │─────────────────────────>│                                │
  │                          │  7. agent_router selecciona    │
  │                          │     mejor agente por categoría │
  │                          │                                │
  │                          │  8. Crea git worktree aislado  │
  │                          │                                │
  │                          │  9. Escribe prompt en          │
  │                          │     .tmux_state/prompts/       │
  │                          │                                │
  │                          │ 10. tmux send-keys             │
  │                          │     "run_task task-X"          │
  │                          │─────────────────────────────>│
  │                          │                                │
  │                          │      ┌─────────────────────┐   │
  │  11. Ve output en vivo   │      │ Agente ejecuta      │   │
  │     en web UI            │<─────│ claude -p ...       │   │
  │                          │      │ output → pane + log │   │
  │                          │      └─────────────────────┘   │
  │                          │                                │
  │                          │      ┌─────────────────────┐   │
  │  12. Opcional: se mete  │      │ Usuario salta al     │   │
  │      a la terminal       │      │ pane, interactúa    │   │
  │─────────────────────────────────>│ con el agente       │   │
  │                          │      └─────────────────────┘   │
  │                          │                                │
  │                          │ 13. Watcher detecta            │
  │                          │     TASK_END:task-X:0          │
  │                          │<────────────────────────────   │
  │                          │                                │
  │                          │ 14. Auto-avanza a "Review"     │
  │                          │                                │
  │  15. Revisa diff + AI    │                                │
  │      review summary      │                                │
  │─────────────────────────>│                                │
  │                          │                                │
  │  16. Mueve a "Done"      │                                │
  │─────────────────────────>│                                │
  │                          │  17. Commit + merge + cleanup  │
  │                          │      worktree                  │
  │                          │                                │
  │  18. Tarea completada ✓  │                                │
```

---

## 3. Los Tres Agentes

### 3.1 Perfiles

#### Claude (`claude`)

```
┌─────────────────────────────────────────────────────────┐
│  CLAUDE — Anthropic Claude (modelo: claude-sonnet-4-6)  │
│                                                         │
│  CLI: claude                                            │
│  API: Anthropic API directa                             │
│                                                         │
│  ▸ FORTALEZAS                                           │
│    • Arquitectura y diseño de sistemas                  │
│    • Razonamiento complejo multi-step                   │
│    • Seguridad — revisión de vulnerabilidades           │
│    • Frontend: React, Next.js, TypeScript, Tailwind     │
│    • Smart contracts: Solidity, patrones DeFi           │
│    • Code review con contexto profundo                  │
│    • Debugging de bugs sutiles                          │
│    • Planeación técnica detallada                       │
│                                                         │
│  ▸ DEBILIDADES                                          │
│    • Puede ser más lento que DeepSeek                   │
│    • Mayor costo por token                              │
│    • No tiene acceso a Google Search                   │
│    • Overthinking en tareas simples                     │
│                                                         │
│  ▸ ASIGNAR CUANDO:                                      │
│    • La tarea requiere diseño arquitectónico            │
│    • Hay implicaciones de seguridad                     │
│    • Es código frontend complejo                        │
│    • Se necesita revisión crítica de código             │
│    • El bug es esquivo y requiere razonamiento          │
│    • Se están tocando contratos inteligentes            │
└─────────────────────────────────────────────────────────┘
```

#### DeepClaude (`deepclaude`)

```
┌─────────────────────────────────────────────────────────┐
│  DEEPCLAUDE — Claude CLI → DeepSeek API                 │
│  (modelo: deepseek-v4-pro)                              │
│                                                         │
│  CLI: claude (con ANTHROPIC_BASE_URL=api.deepseek.com)  │
│  API: DeepSeek Anthropic-compatible API                 │
│                                                         │
│  ▸ FORTALEZAS                                           │
│    • Velocidad — más rápido que Claude directo          │
│    • Boilerplate y código repetitivo                    │
│    • Backend: FastAPI, SQLModel, Python puro            │
│    • Refactors mecánicos (renombrar, mover archivos)    │
│    • Migraciones de base de datos                       │
│    • Tests unitarios y de integración                   │
│    • SQL queries y optimización                         │
│    • DevOps: Docker, CI/CD, configs                     │
│    • Procesamiento de datos / batch operations          │
│                                                         │
│  ▸ DEBILIDADES                                          │
│    • Menos matizado en decisiones de diseño             │
│    • Menos creativo en soluciones                       │
│    • Puede pasar por alto edge cases sutiles            │
│    • No tan bueno en UX/design decisions                │
│                                                         │
│  ▸ ASIGNAR CUANDO:                                      │
│    • La tarea es mecánica o repetitiva                  │
│    • Se necesita velocidad sobre profundidad            │
│    • Es código backend/FastAPI/SQLModel                 │
│    • Hay que escribir/migrar tests                      │
│    • Es una migración de DB o refactor grande           │
│    • Tarea de DevOps (Docker, deploy, CI)              │
└─────────────────────────────────────────────────────────┘
```

#### Agy (`agy`)

```
┌─────────────────────────────────────────────────────────┐
│  AGY — Google Antigravity (Gemini)                      │
│  (modelo: Gemini vía Antigravity CLI)                   │
│                                                         │
│  CLI: agy                                               │
│  API: Google Gemini vía Antigravity proxy               │
│                                                         │
│  ▸ FORTALEZAS                                           │
│    • Creatividad y diseño de juego                      │
│    • Documentación — excelente redactor                 │
│    • Game design: mecánicas, balance, GDD              │
│    • Brainstorming e ideación                           │
│    • Investigación (tiene acceso a Google Search)       │
│    • Explicaciones y tutoriales                         │
│    • Traducción y contenido multilingüe                 │
│    • Análisis de tendencias y mercado                   │
│                                                         │
│  ▸ DEBILIDADES                                          │
│    • Menos preciso en código complejo                   │
│    • Puede divagar en soluciones técnicas               │
│    • No tan riguroso en seguridad                       │
│    • Más lento en iteraciones de código                 │
│                                                         │
│  ▸ ASIGNAR CUANDO:                                      │
│    • Se necesita documentación o GDD                    │
│    • La tarea es de game design                         │
│    • Se requiere investigación externa                  │
│    • Brainstorming de features nuevas                   │
│    • Planeación conceptual (no técnica)                 │
│    • Contenido creativo: lore, nombres, descripciones   │
│    • Análisis de economía del juego                     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Matriz de asignación automática

```
┌──────────────────────────────────────────────────────────────┐
│                     AGENT ROUTING MATRIX                     │
├────────────────────────────┬──────────┬──────────┬───────────┤
│ CATEGORÍA / TIPO           │ CLAUDE   │DEEPCLAUDE│ AGY       │
├────────────────────────────┼──────────┼──────────┼───────────┤
│ Arquitectura / sistemas    │ ● PRIM   │ ○ SEC    │ -         │
│ Frontend (React/TSX/Next)  │ ● PRIM   │ -        │ ○ SEC     │
│ Backend (FastAPI/SQLModel) │ ○ SEC    │ ● PRIM   │ -         │
│ Smart Contracts (Solidity) │ ● PRIM   │ ○ SEC    │ -         │
│ Refactor mecánico          │ -        │ ● PRIM   │ -         │
│ Migración DB / SQL         │ ○ SEC    │ ● PRIM   │ -         │
│ Documentación              │ ○ SEC    │ -        │ ● PRIM    │
│ Game Design / GDD          │ ○ SEC    │ -        │ ● PRIM    │
│ Bug hunting / debugging    │ ● PRIM   │ ○ SEC    │ -         │
│ Tests (unit / integration) │ ○ SEC    │ ● PRIM   │ -         │
│ DevOps / Docker / CI       │ -        │ ● PRIM   │ -         │
│ Investigación / research   │ -        │ -        │ ● PRIM    │
│ Seguridad / auditoría      │ ● PRIM   │ -        │ -         │
│ Diseño de UI/UX            │ ● PRIM   │ -        │ ○ SEC     │
│ Economía / balance         │ ○ SEC    │ -        │ ● PRIM    │
│ Code review / PR           │ ● PRIM   │ ○ SEC    │ -         │
│ Tooling / taskboard        │ ○ SEC    │ ● PRIM   │ -         │
│ Contenido creativo         │ -        │ -        │ ● PRIM    │
│ General / no clasificado   │ ○ SEC    │ ○ SEC    │ ● PRIM    │
└────────────────────────────┴──────────┴──────────┴───────────┘

● PRIM = Agente primario (primera opción)
○ SEC  = Agente secundario (fallback si primario está ocupado)
-      = No recomendado
```

---

## 4. Layout tmux — Diseño Detallado

### 4.1 Grid de panes

```
┌──────────────────────────────────────────────────────────────────┐
│ tmux session: axolotto-agents                                     │
│ window 0: orchestra                                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────┐ ┌────────────────────────────┐  │
│  │                              │ │                            │  │
│  │   PANE 0: claude             │ │   PANE 1: deepclaude       │  │
│  │   ─────────────────────      │ │   ──────────────────────   │  │
│  │   60% width × 60% height     │ │   40% width × 60% height   │  │
│  │                              │ │                            │  │
│  │   Environment:               │ │   Environment:             │  │
│  │   ANTHROPIC_MODEL=           │ │   ANTHROPIC_BASE_URL=      │  │
│  │     claude-sonnet-4-6        │ │     api.deepseek.com/      │  │
│  │   CLAUDE_CODE_EFFORT_LEVEL   │ │       anthropic            │  │
│  │     =max                     │ │   ANTHROPIC_MODEL=         │  │
│  │                              │ │     deepseek-v4-pro        │  │
│  │   PS1=[claude] \w \$         │ │   DEEPSEEK_EFFORT=max      │  │
│  │                              │ │   PS1=[deepclaude] \w \$   │  │
│  │   > _                        │ │   > _                      │  │
│  │                              │ │                            │  │
│  └──────────────────────────────┘ └────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────┐ ┌────────────────────────────┐  │
│  │                              │ │                            │  │
│  │   PANE 2: agy                │ │   PANE 3: monitor          │  │
│  │   ─────────────────────      │ │   ──────────────────────   │  │
│  │   40% width × 40% height     │ │   60% width × 40% height   │  │
│  │                              │ │                            │  │
│  │   Environment:               │ │   Dashboard auto-refresh   │  │
│  │   GEMINI_API_KEY=...         │ │   Status de agentes        │  │
│  │   PS1=[agy] \w \$            │ │   Cola de tareas           │  │
│  │                              │ │   Log tail en vivo         │  │
│  │   > _                        │ │   Atajos de teclado        │  │
│  │                              │ │                            │  │
│  └──────────────────────────────┘ └────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Comandos de inicialización

```bash
#!/bin/bash
# tools/taskboard/bin/tmux_init.sh
# Crea la sesión tmux con el layout de 4 panes

SESSION="axolotto-agents"
REPO="/home/monotr/axolotto"

# Matar sesión existente si hay
tmux kill-session -t "$SESSION" 2>/dev/null

# Crear sesión con primer pane (claude, 60% width × 60% height)
tmux new-session -d -s "$SESSION" -n orchestra \
  -x 200 -y 60 \
  "cd $REPO && bash .tmux_state/claude.init.sh"

# Split vertical → pane 1 (deepclaude, 40% width a la derecha)
tmux split-window -h -p 40 -t "$SESSION":0.0 \
  "cd $REPO && bash .tmux_state/deepclaude.init.sh"

# Ir al pane 0, split horizontal → pane 2 (agy, 40% height abajo)
tmux split-window -v -p 40 -t "$SESSION":0.0 \
  "cd $REPO && bash .tmux_state/agy.init.sh"

# Ir al pane 1, split horizontal → pane 3 (monitor, alineado)
tmux split-window -v -p 40 -t "$SESSION":0.1 \
  "cd $REPO && bash tools/taskboard/bin/tmux_monitor.sh"

# Configurar status bar
tmux set -t "$SESSION" status-style fg=white,bg=#1a1a2e
tmux set -t "$SESSION" status-left '#[fg=#00d4ff]#S#[default]'
tmux set -t "$SESSION" status-right '#(cat /home/monotr/axolotto/.tmux_state/status-bar.txt 2>/dev/null)'
tmux set -t "$SESSION" status-interval 2

# Layout final: seleccionar pane 3 (monitor) como foco inicial
tmux select-pane -t "$SESSION":0.3

echo "Session $SESSION creada. Adjuntar con: tmux attach -t $SESSION"
```

### 4.3 Scripts de inicialización por agente

**`.tmux_state/claude.init.sh`:**
```bash
#!/bin/bash
export ANTHROPIC_MODEL=claude-sonnet-4-6
export CLAUDE_CODE_EFFORT_LEVEL=max
export PS1='[claude] \w \$ '

source /home/monotr/axolotto/.tmux_state/agent-common.sh

echo "=== claude agent ready ==="
echo "Specialty: architecture, security, frontend, smart contracts"
echo "Waiting for tasks..."
echo ""

# Iniciar claude en modo interactivo
claude --dangerously-skip-permissions
```

**`.tmux_state/deepclaude.init.sh`:**
```bash
#!/bin/bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY="${DEEPSEEK_API_KEY}"
export ANTHROPIC_MODEL=deepseek-v4-pro
export DEEPSEEK_EFFORT=max
export PS1='[deepclaude] \w \$ '

source /home/monotr/axolotto/.tmux_state/agent-common.sh

echo "=== deepclaude agent ready ==="
echo "Specialty: backend, refactors, tests, DevOps, SQL"
echo "Waiting for tasks..."
echo ""

claude --dangerously-skip-permissions
```

**`.tmux_state/agy.init.sh`:**
```bash
#!/bin/bash
export PS1='[agy] \w \$ '

source /home/monotr/axolotto/.tmux_state/agent-common.sh

echo "=== agy agent ready ==="
echo "Specialty: game design, docs, research, creative"
echo "Waiting for tasks..."
echo ""

agy
```

**`.tmux_state/agent-common.sh`** (compartido por los 3):
```bash
# Funciones compartidas para todos los agentes
REPO="/home/monotr/axolotto"
STATE_DIR="${REPO}/.tmux_state"

# run_task: ejecuta una tarea asignada por el taskboard
run_task() {
    local TASK_ID="$1"
    local PROMPT_FILE="${STATE_DIR}/prompts/${TASK_ID}.txt"
    local LOG_FILE="${STATE_DIR}/logs/${TASK_ID}.log"
    local WORKTREE="${REPO}/.agents/worktrees/${TASK_ID}"
    local AGENT_NAME="${PS1%]*}"
    AGENT_NAME="${AGENT_NAME#[}"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  TASK START: ${TASK_ID}"
    echo "║  Agent: ${AGENT_NAME}"
    echo "║  Time:  $(date -Iseconds)"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    # Ejecutar claude/agy con el prompt de la tarea
    if [ "$AGENT_NAME" = "agy" ]; then
        agy -p "$(cat "$PROMPT_FILE")" \
            --add-dir "$WORKTREE" \
            2>&1 | tee "$LOG_FILE"
    else
        claude -p "$(cat "$PROMPT_FILE")" \
            --add-dir "$WORKTREE" \
            --dangerously-skip-permissions \
            2>&1 | tee "$LOG_FILE"
    fi

    local RC=$?

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  TASK END: ${TASK_ID}:${RC}"
    echo "║  Time:  $(date -Iseconds)"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    return $RC
}

echo "  run_task <task-id> — ejecutar una tarea asignada"
```

---

## 5. Sistema de Archivos de Estado

### 5.1 `.tmux_state/` — Directorio de estado compartido

```
/home/monotr/axolotto/.tmux_state/
│
├── claude.status              # JSON: estado actual del agente claude
├── deepclaude.status          # JSON: estado actual del agente deepclaude
├── agy.status                 # JSON: estado actual del agente agy
│
├── claude.last_output         # Últimas 50 líneas de output del pane
├── deepclaude.last_output
├── agy.last_output
│
├── status-bar.txt             # Texto para la status bar de tmux
│
├── claude.init.sh             # Script de inicialización del pane claude
├── deepclaude.init.sh         # Script de inicialización del pane deepclaude
├── agy.init.sh                # Script de inicialización del pane agy
├── agent-common.sh            # Funciones compartidas (run_task, etc.)
│
├── prompts/                   # Archivos de prompt para tareas
│   ├── task-1749123456-0.txt
│   └── task-1749123457-1.txt
│
├── logs/                      # Output logs de ejecución
│   ├── task-1749123456-0.log
│   └── task-1749123457-1.log
│
└── pending/                   # Cola de tareas pendientes por agente
    ├── claude/
    │   └── task-1749123458-2.json
    ├── deepclaude/
    └── agy/
        └── task-1749123459-3.json
```

### 5.2 Formato de archivos de estado

**`claude.status`** (ejemplo):
```json
{
  "agent": "claude",
  "status": "busy",
  "task_id": "task-1749123456-0",
  "task_title": "Fix auth middleware token validation",
  "category": "backend",
  "started_at": "2026-06-04T15:30:00-06:00",
  "worktree": "/home/monotr/axolotto/.agents/worktrees/task-1749123456-0",
  "branch": "task/task-1749123456-0-fix-auth-middleware",
  "pid": 12345,
  "assignment_reason": "bug hunting → claude primary"
}
```

**`status-bar.txt`** (ejemplo, generado por monitor cada 2s):
```
claude ●BUSY:task-3 | deepclaude ○IDLE | agy ●BUSY:task-7
```

---

## 6. Componentes de Software

### 6.1 `tmux_orchestrator.py` — Orquestador principal (NUEVO)

```python
"""
tmux_orchestrator.py — Reemplaza agent_runner.py

Responsabilidades:
  - Crear/destruir sesión tmux
  - Seleccionar agente para cada tarea (vía agent_router)
  - Enviar comandos a panes vía tmux send-keys
  - Capturar output de panes vía tmux capture-pane
  - Mantener archivos de estado (.tmux_state/*.status)
  - Detectar completitud de tareas (watcher thread)
  - Gestionar cola de tareas pendientes
"""

class TmuxOrchestrator:
    SESSION = "axolotto-agents"
    STATE_DIR = "/home/monotr/axolotto/.tmux_state"
    AGENTS = ["claude", "deepclaude", "agy"]
    
    # Mapeo de agente → índice de pane en tmux
    PANE_MAP = {"claude": 0, "deepclaude": 1, "agy": 2}
    
    def initialize_session(self) -> bool: ...
    def is_session_alive(self) -> bool: ...
    def assign_task(self, task: dict) -> dict: ...
    def _select_agent(self, task: dict) -> str: ...
    def _send_to_agent(self, agent: str, task: dict) -> None: ...
    def capture_pane_output(self, agent: str, lines: int = 50) -> str: ...
    def get_agent_status(self, agent: str) -> dict: ...
    def _watcher_loop(self) -> None: ...
    def _check_for_completions(self) -> None: ...
```

### 6.2 `agent_router.py` — Enrutador por fortalezas (NUEVO)

```python
"""
agent_router.py — Selecciona el mejor agente para cada tarea
basado en categoría, tipo de trabajo, y disponibilidad.
"""

# Matriz de asignación
ROUTING_MATRIX = {
    "architecture":    {"primary": "claude",     "secondary": "deepclaude"},
    "frontend":        {"primary": "claude",     "secondary": "agy"},
    "backend":         {"primary": "deepclaude", "secondary": "claude"},
    "contracts":       {"primary": "claude",     "secondary": "deepclaude"},
    "refactor":        {"primary": "deepclaude", "secondary": "claude"},
    "database":        {"primary": "deepclaude", "secondary": "claude"},
    "documentation":   {"primary": "agy",        "secondary": "claude"},
    "game-design":     {"primary": "agy",        "secondary": "claude"},
    "bug":             {"primary": "claude",     "secondary": "deepclaude"},
    "testing":         {"primary": "deepclaude", "secondary": "claude"},
    "devops":          {"primary": "deepclaude", "secondary": "claude"},
    "research":        {"primary": "agy",        "secondary": "claude"},
    "security":        {"primary": "claude",     "secondary": "deepclaude"},
    "ui-ux":           {"primary": "claude",     "secondary": "agy"},
    "economy":         {"primary": "agy",        "secondary": "claude"},
    "code-review":     {"primary": "claude",     "secondary": "deepclaude"},
    "tooling":         {"primary": "deepclaude", "secondary": "claude"},
    "creative":        {"primary": "agy",        "secondary": "claude"},
    "general":         {"primary": "agy",        "secondary": "claude"},
}

class AgentRouter:
    def __init__(self, orchestrator: TmuxOrchestrator): ...
    def select_agent(self, task: dict) -> tuple[str, str]: ...
    def is_agent_available(self, agent: str) -> bool: ...
    def get_queue_for(self, agent: str) -> list[dict]: ...
```

### 6.3 `prompt_builder.py` — Constructor de prompts (NUEVO, extraído)

```python
"""
prompt_builder.py — Extraído de agent_runner.py

Construye prompts específicos para cada agente,
incluyendo contexto del proyecto, worktree isolation,
y formato esperado de respuesta.
"""

def build_agent_prompt(task: dict, agent_type: str) -> str:
    """Construye prompt optimizado para el agente específico."""
    ...

def slugify(text: str) -> str:
    """Genera slug para nombres de branch."""
    ...

def build_worktree_path(task_id: str) -> str:
    """Retorna path del worktree para una tarea."""
    ...
```

### 6.4 `modules/agent-console.js` — Panel de agentes en frontend (NUEVO)

```javascript
/**
 * modules/agent-console.js
 * 
 * Renderiza 3 agent cards en el frontend.
 * Hace polling de /api/agents cada 2 segundos.
 * Muestra status, output en vivo, y botones de acción.
 */

class AgentConsole {
    constructor() {
        this.agents = ['claude', 'deepclaude', 'agy'];
        this.pollInterval = 2000;
    }
    
    async refresh() { /* GET /api/agents → update cards */ }
    renderCard(agent, status) { /* DOM update */ }
    updateStatusDot(agent, status) { /* green/orange/red */ }
    updateOutput(agent, output) { /* <pre> with auto-scroll */ }
    attachToAgent(agent) { /* copy tmux attach command */ }
    stopAgent(agent) { /* POST /api/agents/<agent>/stop */ }
    sendCommand(agent, cmd) { /* POST /api/agents/<agent>/send */ }
}
```

---

## 7. API REST — Nuevos Endpoints

### 7.1 Endpoints de agentes

| Método | Ruta | Request | Response |
|--------|------|---------|----------|
| `GET` | `/api/agents` | — | `{ claude: {...}, deepclaude: {...}, agy: {...} }` |
| `GET` | `/api/agents/<agent>` | — | `{ status, task_id, task_title, output, ... }` |
| `GET` | `/api/agents/<agent>/pane?lines=50` | — | `{ output: "...", captured_at: "..." }` |
| `POST` | `/api/agents/<agent>/send` | `{ command: "..." }` | `{ success: true, sent_to: "claude" }` |
| `POST` | `/api/agents/<agent>/stop` | — | `{ success: true, message: "Ctrl+C sent" }` |
| `POST` | `/api/agents/assign` | `{ task_id: "...", agent: "claude" }` | `{ success: true, agent: "claude" }` |

### 7.2 Endpoints de tmux

| Método | Ruta | Request | Response |
|--------|------|---------|----------|
| `POST` | `/api/tmux/init` | — | `{ success: true, session: "axolotto-agents" }` |
| `GET` | `/api/tmux/status` | — | `{ alive: true, attached: true, clients: 1 }` |
| `POST` | `/api/tmux/restart` | — | `{ success: true }` |

---

## 8. Plan de Implementación

### Fase 0: Documento y setup (Día 0) ← AHORA
- ✅ Este documento en `docs/agent-terminal-orchestra.md`
- [ ] Crear `.tmux_state/` con estructura de directorios vacía
- [ ] Verificar que `tmux` funcione, que los 3 CLI estén disponibles

### Fase 1: Fundación (Día 1)

**Objetivo**: Sesión tmux funcional con 3 agentes corriendo, sin integración con taskboard todavía.

- [ ] `tools/taskboard/bin/tmux_init.sh` — script de inicialización
- [ ] `.tmux_state/agent-common.sh` — funciones compartidas
- [ ] `.tmux_state/claude.init.sh` — init pane claude
- [ ] `.tmux_state/deepclaude.init.sh` — init pane deepclaude
- [ ] `.tmux_state/agy.init.sh` — init pane agy
- [ ] `tools/taskboard/bin/tmux_monitor.sh` — dashboard del pane monitor
- [ ] `tools/taskboard/tmux_orchestrator.py` — clase principal
  - `initialize_session()`, `is_session_alive()`
  - `capture_pane_output()`, `_read_status_file()`, `_write_status_file()`
- [ ] `tools/taskboard/prompt_builder.py` — extraer de agent_runner.py
- [ ] `tools/taskboard/agent_router.py` — enrutador con matriz de fortalezas

**Verificación**:
```bash
./tools/taskboard/bin/tmux_init.sh
tmux has-session -t axolotto-agents  # → "axolotto-agents"
tmux list-panes -t axolotto-agents:0  # → 4 panes
ls .tmux_state/claude.status  # → existe
```

### Fase 2: Integración con taskboard (Día 2)

**Objetivo**: El taskboard puede asignar tareas a agentes tmux, detectar completitud, y reflejar estado en la DB.

- [ ] Agregar endpoints REST a `routes.py` (7 endpoints nuevos)
- [ ] Modificar `task_lifecycle.py` — `handle_move_stage_transition`:
  - `planning → doing`: llamar `TmuxOrchestrator.assign_task()` en vez de `spawn_agent()`
- [ ] Implementar `_watcher_loop()` en tmux_orchestrator.py (background thread)
- [ ] Wire completion detection → `TASK_END:<id>:<rc>` → update DB → advance to review
- [ ] Modificar `server.py` para inicializar TmuxOrchestrator en startup
- [ ] Implementar manejo de cola de tareas (`.tmux_state/pending/`)

**Verificación**:
```bash
# Probar asignación de tarea
curl -X POST localhost:8181/api/tasks/move \
  -H 'Content-Type: application/json' \
  -d '{"id":"task-test","status":"doing","force":true}'
# El agente claude debe recibir el comando y empezar a ejecutar
curl localhost:8181/api/agents | jq .claude.status  # → "busy"
# Esperar a que termine...
curl localhost:8181/api/tasks | jq '.[] | select(.id=="task-test") | .status'  # → "review"
```

### Fase 3: Frontend (Día 3)

**Objetivo**: El panel web muestra los 3 agentes en tiempo real con output y botones de acción.

- [ ] Agregar Agent Console Panel HTML a `index.html`
- [ ] Crear `modules/agent-console.js`
  - Polling de `/api/agents` cada 2s
  - Renderizado de 3 agent cards con status dot y output
  - Botones: Attach (copia comando tmux), Stop, Send Command
- [ ] Modificar `app.js` — integrar `refreshAgentConsoles()` en el poll loop existente
- [ ] Agregar estilos CSS para agent cards
- [ ] Agregar asignación manual de agente en el modal de tarea (dropdown)

**Verificación**:
- Abrir localhost:8181 → ver 3 agent cards debajo del kanban
- Status dots: verde (idle), naranja (busy), rojo (error)
- Output en vivo aparece en el `<pre>` de cada card
- Botón Attach copia `tmux attach -t axolotto-agents` al portapapeles

### Fase 4: Polish y limpieza (Día 4)

**Objetivo**: Sistema robusto, sin código legacy, probado con carga real.

- [ ] Marcar `agent_runner.py` como `_deprecated` (no borrar hasta verificar)
- [ ] Remover `MAX_CONCURRENT_AGENTS=1` y sistema de cola viejo
- [ ] Remover referencias a `agent_logs/` (reemplazado por `.tmux_state/logs/`)
- [ ] Auto-restart de sesión tmux si se muere (health check en watcher)
- [ ] Supervivencia a restart del taskboard (leer estado de archivos al iniciar)
- [ ] Probar con 3 tareas simultáneas (una por agente)
- [ ] Probar con 5+ tareas (cola de pending)
- [ ] Probar intervención manual del usuario (Ctrl+C, escribir comandos)
- [ ] Actualizar `reiniciar.sh` para incluir inicialización tmux
- [ ] Actualizar `memory/taskboard_agents_git.md` con nueva arquitectura

**Verificación final**:
```bash
# 3 tareas en paralelo
curl -X POST localhost:8181/api/tasks/move -d '{"id":"t1","status":"doing","category":"frontend"}'
curl -X POST localhost:8181/api/tasks/move -d '{"id":"t2","status":"doing","category":"backend"}'
curl -X POST localhost:8181/api/tasks/move -d '{"id":"t3","status":"doing","category":"game-design"}'
# t1 → claude, t2 → deepclaude, t3 → agy (según matriz)
# Los 3 deben ejecutarse simultáneamente

# Taskboard restart recovery
pm2 restart axolotto-taskboard
curl localhost:8181/api/agents | jq '.claude.status'  # → debe seguir "busy"
```

---

## 9. Errores y Edge Cases

| Escenario | Manejo |
|-----------|--------|
| tmux no instalado | Detectar en startup, fallback a subprocess viejo, mostrar warning |
| Sesión tmux muerta | Auto-recrear en `assign_task()`, loggear incidente |
| Pane de agente crasheado | Detectar pane muerto, recrear, reassignar tarea |
| Los 3 agentes ocupados | Encolar en `.tmux_state/pending/<agent>/`, mostrar posición en UI |
| `TASK_END` no detectado | Scan de últimas 100 líneas del pane; botón "Mark Done" manual en UI |
| Usuario escribe mientras se mandan keys | `tmux send-keys` es seguro para input concurrente |
| Usuario hace Ctrl+C en agente | Tarea marcada como "interrupted", status → "doing" con error comment |
| Claude/agy se cuelga | Timeout en `run_task` wrapper: `timeout 600 claude -p ...` |
| DeepSeek API caída | Tarea falla con error, reintentar automáticamente en claude |
| Taskboard muere, tmux sigue | Agentes continúan trabajando; al reiniciar taskboard, watcher retoma estado |
| Múltiples tareas completan a la vez | Watcher thread procesa secuencialmente (1 por iteración) |
| Worktree conflict (branch ya existe) | Usar timestamp en nombre de branch: `task/<id>-<ts>-<slug>` |

---

## 10. Experiencia de Usuario Día a Día

### 10.1 Arranque diario

```bash
# Opción A: automático con reiniciar.sh (recomendado)
./reiniciar.sh all
# Esto levanta: docker compose, taskboard, frontend, Y la sesión tmux

# Opción B: manual
./tools/taskboard/bin/tmux_init.sh
tmux attach -t axolotto-agents  # ver agentes en vivo (opcional)
```

### 10.2 Flujo de trabajo típico

1. **Mañana**: Abrir navegador en `localhost:8181`. Ver kanban + agent consoles.
2. **Crear tarea**: "Nueva Idea" → escribir prompt → categoría detectada automáticamente.
3. **Planear**: Mover a planning → AI genera requisitos y diseño. Revisar, aprobar.
4. **Ejecutar**: Mover a doing → sistema asigna al mejor agente automáticamente.
   - Ver output en tiempo real en la agent card del panel web.
   - Si quiero ver más: hacer tmux attach y ver los 3 agentes en grid.
   - Si quiero intervenir: Ctrl+B → navegar al pane → escribir.
5. **Revisar**: Agente termina → auto-avanza a review → ver diff y AI review summary.
6. **Completar**: Mover a done → commit + merge automático.

### 10.3 Atajos de tmux para el usuario

```
Ctrl+B ← → ↑ ↓   Navegar entre panes
Ctrl+B ;          Último pane activo
Ctrl+B z          Zoom a un pane (fullscreen temporal)
Ctrl+B d          Desconectarse (agentes siguen corriendo)
Ctrl+B [          Modo scroll (ver output anterior)
Ctrl+B :resize-pane -L/D/U/R 10   Redimensionar panes
```

---

## 11. Diagrama de Estados de Agente

```
                    ┌─────────────────┐
                    │   INITIALIZING  │ ← sesión tmux creada,
                    │   (agente       │   claude/agy iniciando
                    │    arrancando)  │
                    └────────┬────────┘
                             │ init.sh termina, claude> prompt aparece
                             ▼
                    ┌─────────────────┐
          ┌────────│      IDLE       │◄───────────────────────┐
          │        │  (esperando     │                        │
          │        │   tarea)        │                        │
          │        └────────┬────────┘                        │
          │                 │ taskboard envía "run_task X"     │
          │                 ▼                                 │
          │        ┌─────────────────┐                        │
          │        │    EXECUTING    │                        │
          │        │  (claude -p...) │                        │
          │        └────────┬────────┘                        │
          │                 │                                 │
          │          ┌──────┴──────┐                          │
          │          ▼              ▼                          │
          │  ┌──────────────┐ ┌──────────────┐               │
          │  │  COMPLETED   │ │   FAILED     │               │
          │  │  (rc=0)      │ │  (rc≠0 o     │               │
          │  │              │ │   timeout)   │               │
          │  └──────┬───────┘ └──────┬───────┘               │
          │         │                │                        │
          │         ▼                ▼                        │
          │  ┌──────────────┐ ┌──────────────┐               │
          │  │ TASK →       │ │ TASK queda   │               │
          │  │ REVIEW       │ │ en DOING     │               │
          │  │ (auto)       │ │ con [ERROR]   │               │
          │  └──────┬───────┘ └──────┬───────┘               │
          │         │                │                        │
          │         ▼                │                        │
          │  ┌──────────────┐        │                        │
          │  │ Agente →     │        │                        │
          │  │ IDLE         │◄───────┘                        │
          │  └──────────────┘                                 │
          │                                                   │
          │  ┌──────────────┐                                 │
          │  │ INTERRUPTED  │ ← usuario hace Ctrl+C           │
          │  │ (SIGINT)     │                                 │
          │  └──────┬───────┘                                 │
          │         │                                          │
          └─────────┘                                          │
```

---

## 12. Resumen de Archivos

### A crear (8 archivos)

| Archivo | Líneas estimadas | Propósito |
|---------|-----------------|-----------|
| `docs/agent-terminal-orchestra.md` | ~600 | Este documento de diseño |
| `tools/taskboard/tmux_orchestrator.py` | ~500 | Orquestador principal tmux |
| `tools/taskboard/agent_router.py` | ~200 | Enrutador por fortalezas |
| `tools/taskboard/prompt_builder.py` | ~150 | Constructor de prompts |
| `tools/taskboard/bin/tmux_init.sh` | ~80 | Script de inicialización tmux |
| `tools/taskboard/bin/tmux_monitor.sh` | ~60 | Dashboard del pane monitor |
| `tools/taskboard/modules/agent-console.js` | ~200 | Panel de agentes frontend |
| `.tmux_state/agent-common.sh` | ~50 | Funciones shell compartidas |

### A crear (config files, 3 archivos)

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `.tmux_state/claude.init.sh` | ~20 | Init pane claude |
| `.tmux_state/deepclaude.init.sh` | ~20 | Init pane deepclaude |
| `.tmux_state/agy.init.sh` | ~20 | Init pane agy |

### A modificar (6 archivos)

| Archivo | Cambios |
|---------|---------|
| `tools/taskboard/routes.py` | +7 endpoints REST, ~150 líneas |
| `tools/taskboard/task_lifecycle.py` | Cambiar `spawn_agent()` → `TmuxOrchestrator.assign_task()`, ~20 líneas |
| `tools/taskboard/server.py` | Inicializar TmuxOrchestrator en startup, ~10 líneas |
| `tools/taskboard/app.js` | Integrar agent console polling, ~30 líneas |
| `tools/taskboard/index.html` | Agregar Agent Console Panel HTML, ~50 líneas |
| `tools/taskboard/styles.css` | Estilos para agent cards, ~60 líneas |

### Sin cambios

- `tools/taskboard/db.py`
- `tools/taskboard/ai_router.py`
- `tools/taskboard/rate_limiter.py`
- `tools/taskboard/modules/drag-drop.js`
- `tools/taskboard/modules/modal.js`
- `tools/taskboard/modules/task-card.js`

### A deprecar

- `tools/taskboard/agent_runner.py` → marcar como `_agent_runner_deprecated.py` después de migrar

---

## 13. Notas de Implementación

### 13.1 Singleton enforcement

```python
# En server.py, al iniciar:
import tmux_orchestrator
orchestrator = tmux_orchestrator.TmuxOrchestrator.get_instance()

# El orquestador usa el mismo PID file que el taskboard
# para evitar múltiples instancias compitiendo por tmux
```

### 13.2 Thread safety

El watcher thread corre en background capturando output. Las escrituras a `agent-N.status` y `agent-N.last_output` usan `atomic_write()` (write to temp + rename).

### 13.3 Logging

```python
# tmux_orchestrator.py
import logging
logger = logging.getLogger("tmux_orchestrator")
# Logs van a tools/taskboard/tmux_orchestrator.log
```

### 13.4 Configuración

Variables de entorno para configuración (en `.env`):
```bash
# Agent Terminal Orchestra
TASKBOARD_TMUX_SESSION=axolotto-agents
TASKBOARD_TMUX_STATE_DIR=.tmux_state
TASKBOARD_AGENT_TIMEOUT=600       # timeout para run_task wrapper
TASKBOARD_WATCHER_INTERVAL=2      # segundos entre captures de pane
```

---

## Apéndice A: Comparación Antes/Después

```
┌─────────────────────────────────────────────────────────────────┐
│                      ANTES (taskboard actual)                    │
├─────────────────────────────────────────────────────────────────┤
│ Ejecución:    subprocess.Popen (headless, background)           │
│ Output:       archivos de log en agent_logs/                    │
│ Concurrencia: MAX 1 agente                                      │
│ Visibilidad:  polling de logs cada 3s, output con delay         │
│ Interacción:  NINGUNA — el usuario no puede intervenir          │
│ Agentes:      solo claude y deepclaude (agy no implementado)    │
│ Routing:      manual (usuario elige assigned_to)                │
│ Timeout:      1200s fijo, watchdog mata el proceso              │
└─────────────────────────────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DESPUÉS (Agent Terminal Orchestra)             │
├─────────────────────────────────────────────────────────────────┤
│ Ejecución:    tmux send-keys → terminal interactiva visible     │
│ Output:       pane en tiempo real + archivos en .tmux_state/    │
│ Concurrencia: 3 agentes simultáneos (uno por pane)              │
│ Visibilidad:  output EN VIVO en web UI y en terminal            │
│ Interacción:  TOTAL — usuario puede adjuntarse a cualquier pane │
│ Agentes:      claude + deepclaude + agy (los 3 funcionales)     │
│ Routing:      automático por matriz de fortalezas               │
│ Timeout:      600s configurable en wrapper, Ctrl+C disponible   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Apéndice B: Glosario

| Término | Definición |
|---------|-----------|
| **tmux** | Terminal multiplexer — permite múltiples terminales en una sola ventana |
| **sesión tmux** | Contenedor persistente de ventanas y panes (sobrevive a desconexiones) |
| **ventana tmux** | Una "pestaña" dentro de una sesión (como tabs en un navegador) |
| **pane tmux** | Una división dentro de una ventana (split vertical/horizontal) |
| **Orquestador** | `tmux_orchestrator.py` — componente que maneja la sesión tmux y los agentes |
| **Router** | `agent_router.py` — selecciona el mejor agente para cada tarea |
| **Watcher** | Thread que monitorea output de panes y detecta tareas completadas |
| **Worktree** | Git worktree aislado donde el agente hace cambios sin afectar el repo principal |
| **Agent Console Panel** | Sección del frontend que muestra los 3 agentes con output en vivo |
| **TASK_START / TASK_END** | Marcadores en el output del agente que delimitan la ejecución de una tarea |
| **agy** | CLI de Google Antigravity (Gemini) |
| **deepclaude** | Claude CLI enrutado a API de DeepSeek (Anthropic-compatible) |
