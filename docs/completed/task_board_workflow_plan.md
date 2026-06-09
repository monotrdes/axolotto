# Taskboard Kanban — Arquitectura y Workflow

Documento de arquitectura del **Axolotto AI Taskboard**: tablero Kanban de 6 columnas con ruteo multi-proveedor de agentes AI (agy/Gemini, claude/Anthropic, deepclaude/DeepSeek) y orquestación Git integrada.

> **Evolución**: El diseño original (2026-05) proponía 5 columnas (Planning→ToDo→Doing→Review→Done) con `tasks.json`. La implementación real evolucionó a 6 columnas con SQLite, AIRouter multi-provider, y 3 etapas de procesamiento AI. Ver sección [Evolución desde el diseño original](#8-evolución-desde-el-diseño-original).

---

## 1. Arquitectura de Orquestación

El **Taskboard Backend Server** corre independiente en el puerto `8181`, desacoplado del backend principal de Axolotto (FastAPI en `8001`). Actúa como orquestador de agentes AI y operaciones Git.

```
+-------------------------------------------------------------------+
|               Navegador (Tablero Kanban 6 columnas)                |
|  [Wishes] → [Concepts] → [Planning] → [Doing] → [Review] → [Done] |
+------------------------------------+------------------------------+
                                     | API (Port 8181)
                                     v
+-------------------------------------------------------------------+
|        Taskboard Backend (tools/taskboard/server.py)               |
|  - SQLite DB (tasks.db) con WAL mode                               |
|  - Orquesta Git (branches, commits, merge)                         |
|  - Ejecuta Agentes (subprocess PTY para claude, manual para otros) |
|  - Corre validaciones de pruebas (pytest)                          |
|  - Rate limiting multi-provider (rate_limiter.py)                  |
+-------------------------------------------------------------------+
                                     |
                                     v
                 +-------------------+-------------------+-------------------+
                 |                   |                   |                   |
                 v                   v                   v                   v
          [agy/Gemini]       [claude/Sonnet]    [deepclaude/DeepSeek]   [API fallback]
          CLI + API key       CLI + API key      CLI only               Gemini/Claude
```

### Componentes

| Archivo | Rol |
|---------|-----|
| `tools/taskboard/server.py` | Servidor HTTP, endpoints REST, orquestación Git, spawn de agentes |
| `tools/taskboard/ai_router.py` | Router multi-proveedor AI, system prompts, stage processors |
| `tools/taskboard/rate_limiter.py` | Rate limiter thread-safe con cooldown por provider |
| `tools/taskboard/index.html` | Frontend Kanban completo (SPA vanilla JS + CSS) |
| `tools/taskboard/Dockerfile` | Containerización (python:3.12-slim, sin dependencias pip) |

---

## 2. Flujo de Trabajo (6 Columnas)

```
[ WISHES ] → [ CONCEPTS ] → [ PLANNING ] → [ DOING ] → [ REVIEW ] → [ DONE ]
   💜            💖              💜             🧡           ❤️           💚
```

### Fase A: WISHES (Ideas crudas)
- **Propósito**: Buzón de entrada para ideas sin procesar. Prioridad baja por defecto.
- **Creación**: El usuario escribe una idea rápida. Sin estructura.
- **AI trigger**: Al mover a **Concepts**, el AI analiza la idea.

### Fase B: CONCEPTS (Análisis AI inicial)
- **AI Concept Processing**: Al crear una tarea aquí (o mover desde Wishes), `trigger_ai_processing(id, "concept")` invoca al provider seleccionado.
- **Resultado**: El AI genera:
  - Título profesional resumido (max 80 chars)
  - Comentario de alcance (2-4 frases)
  - Categoría: `backend` | `frontend` | `bug` | `docs` | `tools`
  - Prioridad: `high` | `medium` | `low`
- **Refinamiento**: El usuario puede editar categoría/prioridad/título manualmente.
- **Transición**: Al mover a Planning, se dispara `trigger_ai_processing(id, "planning")`.

### Fase C: PLANNING (Planificación AI detallada)
1. **AI Planning**: El provider asignado (preferencia: claude → antigravity → deepclaude) recibe:
   - Descripción de la tarea
   - Contexto del proyecto (estructura de directorios)
2. **Resultado**: El AI decide si es tarea única o múltiple:
   - **Tarea única**: Genera checklist de requisitos (4-8 items), archivos a modificar, análisis de impacto, propuestas, recommended_agent, notas de diseño, guía de verificación.
   - **Múltiple**: Divide en subtareas independientes, cada una con su propio recommended_agent. Las subtareas se crean automáticamente en Planning.
3. **Plan Doc**: Se escribe `docs/plan_<task_id>_<slug>.md` con el plan completo en markdown.
4. **Checklist interactivo**: El usuario marca/desmarca requisitos vía `/api/tasks/requirements/toggle`.
5. **Aprobación**: Vía `/api/tasks/plan/approve`. La tarjeta activa estilo visual `glow-approved` (CSS `@keyframes plan-glow`).
6. **Comentarios**: El usuario puede comentar. AI responde vía `AIRouter.respond_to_comment()`. Fallback heurístico si no hay provider disponible.

### Fase D: DOING (Ejecución y Branching Automático)
1. **Disparador Git**: Al mover a Doing, `server.py`:
   - Guarda `git_base_branch` (rama actual)
   - Crea rama `task/<task_id>-<slug>` vía `git checkout -b`
2. **Disparador del Agente**: `spawn_agent(task)`:
   - **claude**: Auto-spawn vía `subprocess.Popen` con PTY (pseudo-terminal). Log en `agent_logs/<task_id>.log`. Al terminar (éxito), auto-avanza a Review.
   - **agy / deepclaude**: No se auto-spawnean. Se genera un comando paste-ready (guardado en `ai_analysis.execution.command`). El usuario pega el comando en su terminal. Al terminar, presiona "Marcar terminado → Review" (`/api/tasks/exec-done`).
3. **Indicador visual**: CSS `task-doing-pulse` (bordes pulsantes naranja). Status del agente vía `/api/agent-status/<task_id>`.
4. **Log streaming**: Endpoint `/api/agent-log/<task_id>?lines=N`. Visible en tab "Log del Agente" del modal.

### Fase E: REVIEW (Revisión de Cambios)
1. **AI Review Processing**: Al entrar a Review, `trigger_ai_processing(id, "review")`:
   - Obtiene `git diff` de la rama
   - Genera: resumen de cambios, instrucciones de prueba manual (3-5 pasos), edge cases (2-4)
2. **Test automático**: Si la tarea tiene `test_command`, se ejecuta antes de permitir mover a Review o Done (bloqueante).
3. **Diff Viewer**: Modal tab "Review y Git Diff" muestra diff coloreado (`diff-added` / `diff-removed`).
4. **Review Feedback**: Endpoint `/api/tasks/review-feedback`. El usuario envía feedback, AI responde con ajustes sugeridos.
5. **Ciclo de revisión**: Si el feedback requiere cambios, la tarjeta puede regresar a Doing.

### Fase F: DONE (Commit Convencional e Integración)
1. **Validación Final**: Se ejecuta `test_command` nuevamente (si existe).
2. **Force merge guard**: Si `git_base_branch == "main"`, se requiere confirmación explícita (`force_merge: true`). Sin esto, el servidor devuelve `"reason": "confirm_merge_main"`.
3. **Commit Automático**:
   - Convencional: `feat(task-id): título` / `fix(task-id): título` / `docs(task-id): título`
   - Body con checklist de requisitos (marcados `[x]` / `[ ]`)
4. **Merge**: `git checkout <base>` → `git merge <branch>` → `git branch -d <branch>`

---

## 3. Esquema de Datos (SQLite)

Tabla `tasks` en `tasks.db` (repo root):

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                -- "task-<unix_timestamp>"
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'concepts',  -- wishes|concepts|planning|doing|review|done
    assigned_to TEXT NOT NULL DEFAULT 'unassigned',  -- claude|agy|deepclaude|unassigned
    priority TEXT NOT NULL DEFAULT 'medium',  -- high|medium|low
    category TEXT NOT NULL DEFAULT 'tools',   -- backend|frontend|bug|docs|tools
    test_command TEXT NOT NULL DEFAULT '',
    git_branch TEXT NOT NULL DEFAULT '',
    git_base_branch TEXT NOT NULL DEFAULT '',
    needs_agent_generation INTEGER NOT NULL DEFAULT 0,
    planning_data TEXT NOT NULL DEFAULT '{}',   -- JSON: requirements[], notes, approved, verification_guide, plan_doc_path, plan_preview
    comments TEXT NOT NULL DEFAULT '[]',        -- JSON: {author, text, timestamp}[]
    stage_history TEXT NOT NULL DEFAULT '[]',   -- JSON: {stage, entered_at, ai_triggered, ai_model}[]
    ai_analysis TEXT NOT NULL DEFAULT '{}',     -- JSON: {concept, planning, review, execution}
    created_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT ''
);
```

### Campos JSON clave

**`planning_data`**:
```json
{
  "requirements": [{"id": "req-1", "text": "Crear endpoint...", "completed": false}],
  "notes": "Detalles técnicos...",
  "approved": false,
  "verification_guide": "1. Abrir app\n2. Probar...",
  "plan_doc_path": "docs/plan_task-12345_mi-feature.md",
  "plan_preview": "Primeros 600 chars del plan doc..."
}
```

**`ai_analysis.execution`** (solo agy/deepclaude):
```json
{
  "agent": "agy",
  "command": "agy -p '...' --dangerously-skip-permissions",
  "awaiting": true,
  "binary_present": true,
  "created_at": "2026-06-03T..."
}
```

---

## 4. API Endpoints

### Tasks CRUD
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/tasks` | Lista todas las tareas + rate_limits + agent_status |
| `POST` | `/api/tasks/create` | Crea tarea en `wishes` o `concepts`. Dispara AI concept |
| `POST` | `/api/tasks/move` | Mueve tarea entre columnas. Dispara Git/Agentes/AI |
| `POST` | `/api/tasks/edit` | Edita campos de tarea |
| `POST` | `/api/tasks/delete` | Elimina tarea |
| `POST` | `/api/tasks/exec-done` | Marca ejecución manual como terminada → Review |

### Planning & Requirements
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/tasks/requirements/toggle` | Toggle checkbox de requisito |
| `POST` | `/api/tasks/requirements/edit` | Edita lista completa de requisitos + notas + guía |
| `POST` | `/api/tasks/plan/approve` | Toggle aprobación del plan |

### Comentarios & Review
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/tasks/comment` | Añade comentario. AI responde automáticamente |
| `POST` | `/api/tasks/review-feedback` | Feedback en etapa review con respuesta AI |

### AI & Agentes
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/ai/process-concept` | Re-procesa concepto con AI |
| `POST` | `/api/ai/process-plan` | Re-genera plan con AI |
| `POST` | `/api/ai/process-review` | Re-genera review con AI |
| `POST` | `/api/ai/retry-concept` | Reintenta concepto para tareas huérfanas |
| `GET` | `/api/agent-status/<task_id>` | Estado del agente en ejecución |
| `GET` | `/api/agent-log/<task_id>?lines=50` | Tail del log del agente |

### Utilidades
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/tasks/diff?id=<task_id>` | Git diff de la rama de la tarea |
| `GET` | `/api/rates` | Estado de rate limits por provider |
| `POST` | `/api/restart-axo` | Reinicia ecosistema Axolotto (sin taskboard) |

---

## 5. Sistema de Ruteo AI

### Proveedores

| Provider | Binario | Fallback | Fortalezas |
|----------|---------|----------|------------|
| **GeminiProvider** (`antigravity`) | `agy` CLI | Gemini API key | general, tools, docs, quick |
| **ClaudeProvider** (`claude`) | `claude` CLI | Anthropic API key | frontend, design, reasoning, planning, review |
| **DeepClaudeProvider** (`deepclaude`) | `deepclaude` CLI | — (CLI-only) | backend, bug, code-analysis, refactoring |

### Selección por etapa

| Etapa | Orden de preferencia |
|-------|---------------------|
| `concept` (backend/bug) | claude → antigravity → deepclaude |
| `concept` (frontend) | claude → antigravity → deepclaude |
| `concept` (otros) | antigravity → claude → deepclaude |
| `planning` | claude → antigravity → deepclaude |
| `review` | claude → antigravity → deepclaude |

### Rate Limiting

`RateLimitTracker` (thread-safe):
- Límites por provider: antigravity=1500 RPM, claude=100 RPM, deepclaude=500 RPM
- Cooldown automático en 429 (agy: 5h, otros: 30-60s)
- Auto-recuperación al expirar cooldown
- Ventana deslizante de 1 minuto por provider

---

## 6. Ejecución de Agentes

### Claude (auto-spawn)
```
spawn_agent(task) → Thread → subprocess.Popen + PTY
  → Log en agent_logs/<task_id>.log
  → Éxito: auto-avanza a Review
  → Fallo: se queda en Doing con comentario del error
```

### agy / deepclaude (manual paste-command)
```
spawn_agent(task) → _set_manual_exec_command(task)
  → Guarda comando en ai_analysis.execution.command
  → Usuario copia y pega en su terminal
  → Usuario presiona "Marcar terminado" → POST /api/tasks/exec-done
  → Avanza a Review + trigger AI review
```

---

## 7. Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY server.py ai_router.py rate_limiter.py index.html /app/
COPY agent_logs /app/agent_logs
EXPOSE 8181
WORKDIR /repo
CMD ["python3", "-B", "/app/server.py"]
```

El contenedor espera el repo montado en `/repo` (contiene `tasks.db`). Sin dependencias pip — solo stdlib.

---

## 8. Evolución desde el diseño original

### Cambios estructurales
| Diseño original (2026-05) | Implementación real (2026-06) |
|---------------------------|-------------------------------|
| 5 columnas: Planning → ToDo → Doing → Review → Done | 6 columnas: Wishes → Concepts → Planning → Doing → Review → Done |
| `tasks.json` archivo único | SQLite `tasks.db` con WAL |
| `scripts/task_planner.py` | `ai_router.py` AIRouter multi-provider |
| 1 etapa AI (planning) | 3 etapas AI (concept, planning, review) |
| Branch + commit en server | Branch + commit + merge + force guard + PTY agent spawn |
| Sin rate limiting | RateLimitTracker con cooldown por provider |

### Features añadidas (no en diseño original)
- **Wishes + Concepts**: Dos columnas pre-planning para granularidad de ideas
- **Multi-task splitting**: AI divide ideas complejas en subtareas independientes
- **Plan docs**: AI escribe `docs/plan_<id>_<slug>.md` con análisis completo
- **Agent log streaming**: Logs en tiempo real vía API + visor en UI
- **Dual execution mode**: Auto-spawn (claude) + paste-command (agy/deepclaude)
- **Review feedback loop**: Feedback del usuario con respuesta AI en etapa review
- **Force merge guard**: Protección contra merge accidental a main
- **Docker support**: Containerización lista para deploy
- **Restart ecosystem**: `/api/restart-axo` llama a `reiniciar.sh axo`

### Lo que NO se implementó del diseño original
- **Columna "To Do"**: Reemplazada por Wishes + Concepts. Las tareas van directo de Planning a Doing.
- **Glow visual completo**: El CSS tiene `.glow-approved` implementado, pero sin el comportamiento completo descrito (aprobación automática al completar todos los requisitos).

---

## 9. Estado de Implementación

- [x] Diseñar el plan extendido con Planning, Review, Git branching y commits
- [x] Crear interfaz de Planning y checklist en `index.html` — checklist interactivo, chat de comentarios, tabs Planning/Review/Log, diff viewer
- [x] Integrar operaciones automáticas de Git en `server.py` — branch create, conventional commit, merge, force guard
- [x] Diseñar el agente/script automatizado — `ai_router.py` con 3 providers, 3 etapas AI, fallbacks heurísticos

### Pendientes (mejoras futuras)
- [ ] E2E tests del flujo completo de taskboard
- [ ] Webhook notifications al completar tareas (Discord/Slack)
- [ ] Métricas de productividad por agente (tareas completadas, tiempo promedio)
- [ ] Hotkeys en el UI para mover tareas rápidamente
