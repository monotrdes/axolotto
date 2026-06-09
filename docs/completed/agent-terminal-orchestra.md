# Agent Terminal Orchestra — Documento de Diseño

> **Versión:** 3.0 — Local-First Dev Workflow
> **Fecha:** 2026-06-04
> **Estado:** Plan Maestro — Pendiente de implementación
> **Historial:** v1 (todo en server) → v2 (split sshfs) → **v3 (local-first, git push)**

---

## 0. El Problema Real

El entorno actual es frágil y anti-patrón:

| Problema | Causa raíz |
|----------|-----------|
| RAM server saturada | Agentes IA + docker comparten CPU/RAM en server |
| VS Code crash = desastre | Terminales viven en VS Code, se pierden al reconectar |
| Sin GitHub | No hay remote, backups, ni PRs |
| Trabajo en master | Sin branches, cambios directos, riesgo de perder trabajo |
| sshfs complejo | Montar repo remoto agrega latencia y punto de fallo |
| Edición remota | VS Code Remote-SSH edita en server; si server cae, nada funciona |

**La solución no es parchar — es mover el entorno dev completo a local.**

---

## 1. Nueva Arquitectura: 3 Entornos Separados

```
┌─── WINDOWS / WSL (DEV) ───────────────────────────────────────────┐
│                                                                    │
│  Todo el desarrollo ocurre aquí. Server no participa.              │
│                                                                    │
│  Windows Terminal (app independiente)                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  $ wsl                                                        │  │
│  │  $ cd ~/axolotto                                              │  │
│  │  $ tmux attach -t axolotto-agents                             │  │
│  │                                                                │  │
│  │  ┌──────────────┬──────────────┐                                │  │
│  │  │ claude ●BUSY │ deepclaude   │  ← agentes editan archivos   │  │
│  │  │ > editando.. │ ○IDLE        │    LOCALMENTE en ~/axolotto  │  │
│  │  ├──────────────┼──────────────┤                                │  │
│  │  │ agy ○IDLE    │ monitor      │  ← dashboard + logs          │  │
│  │  └──────────────┴──────────────┘                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  ~/axolotto/   (git clone local)                             │  │
│  │  ├── backend/       ├── frontend/       ├── contracts/       │  │
│  │  ├── tools/taskboard/  ← taskboard v2 vive aquí              │  │
│  │  ├── docs/                                                  │  │
│  │  └── .git/          ← remote = github.com/tu-user/axolotto  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  taskboard server (Python, localhost:8181)                   │  │
│  │  ├── server.py                 ← gestiona kanban + DB        │  │
│  │  ├── tmux_orchestrator.py      ← controla tmux session       │  │
│  │  ├── agent_router.py           ← asigna tareas a agentes     │  │
│  │  ├── prompt_builder.py         ← construye prompts           │  │
│  │  └── task_lifecycle.py         ← workflow de tareas          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Navegador: http://localhost:8181   (LOCAL, sin SSH)               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Kanban (6 cols) + Agent Console (3 cards) + Status Board    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  VS Code: abre ~/axolotto/ en WSL                                 │
│  └── Editas código normalmente. Ya NO usas Remote-SSH para dev.  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                          │
                          │ git push / git pull
                          ▼
┌─── GITHUB ─────────────────────────────────────────────────────────┐
│                                                                     │
│  github.com/tu-user/axolotto                                        │
│  ├── main         ← rama principal (producción)                    │
│  ├── develop      ← rama de integración                            │
│  └── feature/*    ← ramas de features                              │
│                                                                     │
│  CI/CD (opcional futuro):                                           │
│  ├── Lint + tests en PR                                             │
│  └── Deploy a server en push a main                                 │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          │ git pull (manual o CI/CD)
                          ▼
┌─── SERVER (PRODUCCIÓN) ────────────────────────────────────────────┐
│                                                                     │
│  /home/monotr/axolotto/   (git clone, branch main, read-only)      │
│                                                                     │
│  docker compose up -d                                               │
│  ├── backend    :8001    ← FastAPI (código de git)                 │
│  ├── anvil      :8545    ← blockchain local                        │
│  ├── postgres   :5433    ← DB                                      │
│  └── frontend   :3000    ← Next.js (pm2)                            │
│                                                                     │
│  Eso es todo. NO hay agentes IA. NO hay taskboard.                  │
│  Solo ejecuta el juego.                                             │
│                                                                     │
│  Actualizar: git pull && docker compose restart                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Flujo de Trabajo Diario (El "Cómo")

### 2.1 Setup inicial (una sola vez)

```bash
# === EN WINDOWS ===
# 1. Instalar WSL si no está
wsl --install

# 2. En WSL, instalar dependencias
sudo apt update && sudo apt install tmux git python3-pip nodejs npm
pip3 install websockets

# 3. Configurar git
git config --global user.name "Axolotto Bot"
git config --global user.email "tu@email.com"

# 4. Clonar el repo (desde GitHub, después de crearlo)
cd ~
git clone https://github.com/tu-user/axolotto.git
cd axolotto

# 5. Instalar dependencias del proyecto
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# 6. Verificar agentes CLI
which claude    # debe existir en PATH de WSL
which agy       # debe existir en PATH de WSL
# deepclaude = claude con ANTHROPIC_BASE_URL=api.deepseek.com

# 7. Iniciar taskboard
cd ~/axolotto
python3 tools/taskboard/server.py &
# Abrir navegador Windows → http://localhost:8181
```

### 2.2 Workflow de una tarea

```
PASO 1: CREAR RAMA
──────────────────
$ git checkout -b feature/mi-feature develop
  (o desde main si no hay develop aún)

PASO 2: CREAR TAREA EN TASKBOARD
──────────────────────────────────
Navegador → localhost:8181 → "New Wish"
Escribir: "Agregar X al backend"
Categoría: backend
Mover a Concepts → AI genera título/scope
Mover a Planning → AI genera plan detallado
Revisar plan, aprobar

PASO 3: EJECUTAR
────────────────
Mover a Doing → taskboard asigna al mejor agente
Agente trabaja en ~/axolotto/ (cambios locales)
Ver output en vivo en Agent Console (web UI)
Opcional: Windows Terminal → wsl → tmux attach para intervenir

PASO 4: REVISAR
───────────────
Agente termina → auto-avanza a Review
$ git diff  (ver cambios)
$ git status
Corregir si es necesario (manualmente o re-abrir tarea)

PASO 5: COMMIT Y PUSH
──────────────────────
$ git add -A
$ git commit -m "feat(backend): agregar X"
$ git push origin feature/mi-feature

PASO 6: PULL REQUEST
────────────────────
GitHub → crear PR de feature/mi-feature → develop
Revisar diff, mergear

PASO 7: MOVER A DONE
─────────────────────
En taskboard: mover tarjeta a Done
(taskboard hace commit final si hay cambios pendientes)

PASO 8: DEPLOY (CUANDO SEA MOMENTO)
─────────────────────────────────────
$ ssh server
$ cd /home/monotr/axolotto
$ git pull origin main  (o develop)
$ docker compose restart backend frontend
```

### 2.3 Ramas

```
main        ← producción (server ejecuta esto)
  │
  └── develop   ← integración (features se mergean aquí)
        │
        ├── feature/nueva-mecanica
        ├── feature/vip-system
        ├── fix/auth-bug
        └── task/task-XXXX  (creadas por taskboard)
```

---

## 3. Taskboard v2 — Componentes

### 3.1 Todo corre en WSL

Nada del taskboard vive en el server. El server solo docker.

```
~/axolotto/tools/taskboard/
├── server.py              ← entry point (~30 líneas)
├── tmux_orchestrator.py   ← gestor de sesión tmux (~500 líneas)
├── agent_router.py        ← enrutador por fortalezas (~200 líneas)
├── prompt_builder.py      ← constructor de prompts (~150 líneas)
├── task_lifecycle.py      ← workflow de tareas (~300 líneas)
├── routes.py              ← REST API (~400 líneas)
├── db.py                  ← SQLite tasks.db
├── ai_router.py           ← procesamiento de concepto/plan
├── rate_limiter.py        ← anti-abuso
├── bin/
│   ├── tmux_init.sh       ← crea sesión tmux con 4 panes
│   └── tmux_monitor.sh    ← dashboard del pane monitor
├── modules/
│   ├── agent-console.js   ← frontend: 3 agent cards
│   ├── connection-status.js ← frontend: indicadores
│   ├── modal.js
│   ├── task-card.js
│   └── drag-drop.js
├── static/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── templates/
```

### 3.2 Tmux layout (en WSL)

```
tmux session: axolotto-agents
window 0: orchestra

┌──────────────────────────────┬────────────────────────────┐
│                              │                            │
│  PANE 0: claude              │  PANE 1: deepclaude        │
│  60% width × 60% height      │  40% width × 60% height    │
│                              │                            │
│  $ cd ~/axolotto             │  $ cd ~/axolotto           │
│  [BUSY: task-3]              │  [IDLE]                    │
│  > claude -p "prompt..."     │  > _                       │
│                              │                            │
├──────────────────────────────┼────────────────────────────┤
│                              │                            │
│  PANE 2: agy                 │  PANE 3: monitor           │
│  40% width × 40% height      │  60% width × 40% height    │
│                              │                            │
│  $ cd ~/axolotto             │  Agent Orchestra Monitor   │
│  [BUSY: task-7]              │  ─────────────────────     │
│  > agy -p "prompt..."        │  claude    BUSY task-3     │
│                              │  deepclaude IDLE           │
│                              │  agy       BUSY task-7     │
│                              │  Queue: 2 pending          │
│                              │  Log tail: task-3...       │
└──────────────────────────────┴────────────────────────────┘
```

### 3.3 Web UI

```
http://localhost:8181  (local, sin SSH)

┌─────────────────────────────────────────────────────────────┐
│              TASKBOARD v2           [🟢 3 agents] [git:feat]│
│─────────────────────────────────────────────────────────────│
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  WISHES │ CONCEPTS │ PLANNING │ DOING │ REVIEW │ DONE │  │
│  │  ───────│──────────│──────────│───────│────────│──────│  │
│  │   💡    │   📝     │   📋     │  🔧   │  👀    │  ✅  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  🟠 claude     │  🟢 deepclaude  │  🟠 agy            │  │
│  │  BUSY: task-3  │  IDLE           │  BUSY: task-7      │  │
│  │  > Fix auth..  │  Available      │  > Research PvP..  │  │
│  │  [Attach][Stop]│  [Send cmd]     │  [Attach][Stop]    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  🟢 Git: feature/mi-feature  |  Cambios sin commit: 2 │  │
│  │  Quick task: [________________________] [claude ▼] [▶] │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Setup Paso a Paso (Guía Completa)

### Paso 0: Preparar el server (mientras tanto)

```bash
# En el server, commitear TODO lo que esté sin commitear
cd /home/monotr/axolotto
git status
git add -A
git commit -m "chore: snapshot pre-migracion a GitHub"

# Crear un bundle para transferir el repo con historial
git bundle create ~/axolotto.bundle --all
# Copiar este bundle a Windows (scp, USB, lo que sea)
```

### Paso 1: Crear repo en GitHub

```bash
# Opción A: Usar gh CLI
gh repo create axolotto --private --description "Axolotto - Juego de lotería NFT"

# Opción B: Manual en github.com → New Repository → "axolotto" → Private
```

### Paso 2: Clonar en WSL

```bash
# En WSL (Windows):
cd ~

# Opción A: Clonar desde bundle (preserva TODO el historial)
git clone ~/axolotto.bundle axolotto
cd axolotto
git remote add origin https://github.com/tu-user/axolotto.git
git push --all origin
git push --tags origin

# Opción B: Empezar limpio desde GitHub
git clone https://github.com/tu-user/axolotto.git
cd axolotto
# Copiar archivos desde el server (scp) y hacer commit inicial
```

### Paso 3: Configurar ramas

```bash
cd ~/axolotto

# Crear develop desde main/master
git checkout -b develop
git push origin develop

# Poner main como default en GitHub (Settings → Branches → Default branch)
```

### Paso 4: Instalar todo en WSL

```bash
cd ~/axolotto

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..

# Taskboard
pip install websockets aiohttp  # dependencias adicionales

# Verificar
which claude && echo "OK" || echo "FALTA claude CLI"
which agy && echo "OK" || echo "FALTA agy CLI"
tmux -V && echo "OK" || echo "FALTA tmux"
```

### Paso 5: Crear scripts de inicio

```bash
# ~/axolotto/tools/taskboard/bin/tmux_init.sh
# (Ver sección 5 abajo para contenido completo)

# ~/axolotto/dev-start.sh  (script maestro diario)
#!/bin/bash
# Inicia todo el entorno dev

echo "=== Axolotto Dev Environment ==="

# 1. Iniciar tmux con agentes
echo "[1/3] Iniciando sesión tmux..."
~/axolotto/tools/taskboard/bin/tmux_init.sh

# 2. Iniciar taskboard server
echo "[2/3] Iniciando taskboard..."
cd ~/axolotto
python3 tools/taskboard/server.py &
TBPID=$!
echo "  Taskboard PID: $TBPID"

# 3. Abrir info
echo "[3/3] Listo."
echo ""
echo "  Taskboard:  http://localhost:8181"
echo "  Agentes:    tmux attach -t axolotto-agents"
echo ""
echo "Para detener: kill $TBPID && tmux kill-session -t axolotto-agents"

wait $TBPID
```

### Paso 6: Configurar server para solo producción

```bash
# En el server, simplificar:
cd /home/monotr/axolotto

# Asegurar que está en main
git checkout main
git pull origin main

# Detener taskboard v1 (ya no se necesita en server)
pm2 stop axolotto-taskboard
pm2 delete axolotto-taskboard

# El server ahora solo necesita:
# - docker compose up -d  (juego)
# - git pull origin main   (actualizar)
# - docker compose restart backend frontend  (aplicar cambios)
```

---

## 5. Scripts Clave

### 5.1 `tmux_init.sh`

```bash
#!/bin/bash
# tools/taskboard/bin/tmux_init.sh
# Crea sesión tmux con 4 panes para los 3 agentes + monitor

SESSION="axolotto-agents"
REPO="$HOME/axolotto"
STATE_DIR="$HOME/.axolotto-tmux-state"

mkdir -p "$STATE_DIR"/{prompts,logs,pending/{claude,deepclaude,agy}}

# Matar sesión existente
tmux kill-session -t "$SESSION" 2>/dev/null
sleep 0.5

# Pane 0: claude (60% width, luego se divide horizontal)
tmux new-session -d -s "$SESSION" -n orchestra -c "$REPO"
tmux send-keys -t "$SESSION":0.0 "source $STATE_DIR/claude.init.sh" Enter

# Pane 1: deepclaude (split vertical, 40% a la derecha)
tmux split-window -h -p 40 -t "$SESSION":0.0 -c "$REPO"
tmux send-keys -t "$SESSION":0.1 "source $STATE_DIR/deepclaude.init.sh" Enter

# Pane 2: agy (debajo de claude, 40% height)
tmux split-window -v -p 40 -t "$SESSION":0.0 -c "$REPO"
tmux send-keys -t "$SESSION":0.2 "source $STATE_DIR/agy.init.sh" Enter

# Pane 3: monitor (alineado con agy, 40% height)
tmux split-window -v -p 40 -t "$SESSION":0.1 -c "$REPO"
tmux send-keys -t "$SESSION":0.3 "python3 tools/taskboard/tmux_monitor.py" Enter

# Seleccionar monitor como foco inicial
tmux select-pane -t "$SESSION":0.3

echo "Session $SESSION creada."
echo "Attach: tmux attach -t $SESSION"
```

### 5.2 `claude.init.sh`

```bash
# ~/.axolotto-tmux-state/claude.init.sh
export ANTHROPIC_MODEL=claude-sonnet-4-6
export CLAUDE_CODE_EFFORT_LEVEL=max
export PS1='[claude] \w \$ '

source "$HOME/.axolotto-tmux-state/agent-common.sh"

echo "=== claude agent ready ==="
echo "Specialty: architecture, security, frontend, smart contracts"
echo "Waiting for tasks..."
echo ""
```

### 5.3 `deepclaude.init.sh`

```bash
# ~/.axolotto-tmux-state/deepclaude.init.sh
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY="${DEEPSEEK_API_KEY}"
export ANTHROPIC_MODEL=deepseek-v4-pro
export DEEPSEEK_EFFORT=max
export PS1='[deepclaude] \w \$ '

source "$HOME/.axolotto-tmux-state/agent-common.sh"

echo "=== deepclaude agent ready ==="
echo "Specialty: backend, refactors, tests, DevOps, SQL"
echo "Waiting for tasks..."
echo ""
```

### 5.4 `agy.init.sh`

```bash
# ~/.axolotto-tmux-state/agy.init.sh
export PS1='[agy] \w \$ '

source "$HOME/.axolotto-tmux-state/agent-common.sh"

echo "=== agy agent ready ==="
echo "Specialty: game design, docs, research, creative"
echo "Waiting for tasks..."
echo ""
```

### 5.5 `agent-common.sh`

```bash
# ~/.axolotto-tmux-state/agent-common.sh
# Funciones compartidas para todos los agentes

REPO="$HOME/axolotto"
STATE_DIR="$HOME/.axolotto-tmux-state"

run_task() {
    local TASK_ID="$1"
    local PROMPT_FILE="$STATE_DIR/prompts/${TASK_ID}.txt"
    local LOG_FILE="$STATE_DIR/logs/${TASK_ID}.log"
    local AGENT_NAME="${PS1%]*}"
    AGENT_NAME="${AGENT_NAME#[}"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  TASK_START: ${TASK_ID}"
    echo "║  Agent: ${AGENT_NAME}"
    echo "║  Time:  $(date -Iseconds)"
    echo "║  Branch: $(cd "$REPO" && git branch --show-current)"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    if [ "$AGENT_NAME" = "agy" ]; then
        timeout 600 agy -p "$(cat "$PROMPT_FILE")" \
            --add-dir "$REPO" \
            2>&1 | tee "$LOG_FILE"
    else
        timeout 600 claude -p "$(cat "$PROMPT_FILE")" \
            --add-dir "$REPO" \
            --dangerously-skip-permissions \
            2>&1 | tee "$LOG_FILE"
    fi

    local RC=$?

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  TASK_END: ${TASK_ID}:${RC}"
    echo "║  Time:  $(date -Iseconds)"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    return $RC
}

echo "  run_task <task-id> — ejecutar una tarea asignada"
```

---

## 6. Matriz de Routing de Agentes

Igual que v1/v2. El `agent_router.py` asigna automáticamente:

| Categoría | Primario | Secundario |
|-----------|----------|------------|
| Arquitectura | claude | deepclaude |
| Frontend | claude | agy |
| Backend | deepclaude | claude |
| Smart Contracts | claude | deepclaude |
| Refactor | deepclaude | claude |
| DB / SQL | deepclaude | claude |
| Documentación | agy | claude |
| Game Design | agy | claude |
| Bug hunting | claude | deepclaude |
| Tests | deepclaude | claude |
| DevOps | deepclaude | claude |
| Research | agy | claude |
| Seguridad | claude | — |
| UI/UX | claude | agy |
| Economía | agy | claude |
| Code Review | claude | deepclaude |
| Creativo | agy | — |

---

## 7. Plan de Implementación

### Fase 0: GitHub + Setup Local (HOY — 2 horas)

- [ ] **0.1** Commitear todo en server: `git add -A && git commit -m "chore: snapshot pre-migracion"`
- [ ] **0.2** Crear repo en GitHub (`gh repo create` o manual)
- [ ] **0.3** Crear git bundle en server: `git bundle create axolotto.bundle --all`
- [ ] **0.4** Copiar bundle a Windows (`scp` o cualquier método)
- [ ] **0.5** Clonar desde bundle en WSL: `git clone axolotto.bundle ~/axolotto`
- [ ] **0.6** Agregar remote y push: `git remote add origin <url> && git push --all`
- [ ] **0.7** Crear rama `develop`: `git checkout -b develop && git push origin develop`
- [ ] **0.8** Verificar: `git clone` limpio desde GitHub en otro dir funciona

### Fase 1: Entorno Dev Local (1 día)

- [ ] **1.1** Instalar dependencias en WSL: python, npm, tmux
- [ ] **1.2** Crear `~/axolotto-tmux-state/` con init scripts
- [ ] **1.3** Crear `tmux_init.sh` y probar sesión tmux con 4 panes
- [ ] **1.4** Crear `agent-common.sh` con `run_task`
- [ ] **1.5** Probar: mandar comando a un pane → agente ejecuta → output capturado
- [ ] **1.6** Crear `dev-start.sh` script maestro

### Fase 2: Taskboard Core en WSL (1-2 días)

- [ ] **2.1** Adaptar `server.py` para correr localmente (sin dependencias de server)
- [ ] **2.2** Crear `tmux_orchestrator.py` (maneja tmux local, no WebSocket)
- [ ] **2.3** Crear `agent_router.py` con matriz de asignación
- [ ] **2.4** Extraer `prompt_builder.py` de `agent_runner.py`
- [ ] **2.5** Modificar `task_lifecycle.py`:
  - planning→doing: `tmux_orchestrator.assign_task()`
  - Detectar TASK_END en output → advance to review
- [ ] **2.6** Agregar endpoints REST a `routes.py`
- [ ] **2.7** Deprecar `agent_runner.py`

**Verificación:**
```bash
# En WSL
python3 tools/taskboard/server.py &
curl localhost:8181/api/agents | jq
# Debe mostrar 3 agentes (los lee de tmux)
```

### Fase 3: Frontend Local (1 día)

- [ ] **3.1** Agregar Agent Console Panel HTML a `index.html`
- [ ] **3.2** Crear `modules/agent-console.js` (polling c/2s)
- [ ] **3.3** Agregar Git status indicator
- [ ] **3.4** Agregar Quick Task input
- [ ] **3.5** Estilos CSS para agent cards
- [ ] **3.6** Integrar en `app.js`

**Verificación:**
```bash
# Abrir http://localhost:8181 en navegador Windows
# Ver kanban + 3 agent cards + git status
```

### Fase 4: Server Cleanup (30 min)

- [ ] **4.1** Detener y remover taskboard v1 del server: `pm2 delete axolotto-taskboard`
- [ ] **4.2** Crear `server-update.sh` en server: `git pull && docker compose restart`
- [ ] **4.3** Simplificar `reiniciar.sh` (ya no inicia taskboard)
- [ ] **4.4** Actualizar `.gitignore` si es necesario
- [ ] **4.5** Commit todo y push a main

### Fase 5: Polish y Documentación (1 día)

- [ ] **5.1** Auto-recrear tmux session si muere
- [ ] **5.2** Watchdog de agentes (timeout, crash recovery)
- [ ] **5.3** Documentar workflow diario en README.md
- [ ] **5.4** Probar flujo completo: crear tarea → agente trabaja → commit → push → PR
- [ ] **5.5** Probar 3 tareas simultáneas
- [ ] **5.6** Actualizar memory files
- [ ] **5.7** Marcar `docs/agent-terminal-orchestra_v1-original.md` como deprecado

---

## 8. Comparativa Final

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANTES (AHORA)                                 │
├─────────────────────────────────────────────────────────────────┤
│ ¿Dónde editas?        Server (VS Code Remote-SSH)               │
│ ¿Dónde corren agentes? Server (subprocess headless)              │
│ ¿Dónde está el repo?  Solo en server, sin GitHub                  │
│ Ramas?                Trabajo en master, branches de taskboard   │
│ Taskboard?            En server, comparte CPU/RAM con docker     │
│ Si VS Code crashea?   Pierdes terminales, agentes mueren         │
│ Si server se apaga?   Pierdes TODO                               │
│ RAM server?           ~8GB+ (docker + agentes + taskboard)       │
│ Deploy?               Directo en server, edits en caliente       │
└─────────────────────────────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DESPUÉS (v3)                                  │
├─────────────────────────────────────────────────────────────────┤
│ ¿Dónde editas?        WSL local (~/axolotto)                     │
│ ¿Dónde corren agentes? WSL local (tmux interactivo)              │
│ ¿Dónde está el repo?  GitHub + clone local en WSL                │
│ Ramas?                main, develop, feature/*, fix/*            │
│ Taskboard?            En WSL, CPU/RAM dedicados                  │
│ Si VS Code crashea?   No pasa nada. Windows Terminal + tmux     │
│ Si laptop se apaga?   Server sigue corriendo el juego            │
│ RAM server?           ~2GB (solo docker)                         │
│ Deploy?               git push → PR → merge → server git pull    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Archivos del Plan

| Archivo | Versión | Descripción |
|---------|---------|-------------|
| `docs/agent-terminal-orchestra.md` | v3.0 | Este documento — plan maestro |
| `docs/agent-terminal-orchestra_v1-original.md` | v1.0 | Plan original (todo en server, deprecado) |

---

## Apéndice A: Preguntas Frecuentes

**P: ¿Y si quiero correr el juego localmente también (no solo el taskboard)?**

R: En WSL puedes correr `docker compose up -d` también. Tendrías backend en `localhost:8001`, frontend en `localhost:3000`, anvil en `localhost:8545`. El server de producción sería solo para acceso externo.

**P: ¿Qué pasa con los .env y secretos?**

R: Se mantienen en `.env` local (gitignored). No se suben a GitHub. El server tiene su propio `.env` de producción. Se copian manualmente una vez.

**P: ¿Y la base de datos de desarrollo?**

R: Puedes correr postgres en docker localmente también, o usar SQLite para desarrollo. La DB de producción está en el server.

**P: ¿Los contratos se deployan desde local?**

R: Sí. Desarrollo y test en anvil local de WSL. Deploy a Plasma Testnet desde local. Solo producción va desde server con keys seguras.
