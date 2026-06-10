---
name: taskboard
description: Kanban task tracker for Axolotto. Use when user reports bugs, requests features, asks you to investigate code, or makes significant changes to track. Create and move tasks through board columns (wishes concepts planning doing review done). Auto-trigger on phrases like bug, feature, investiga, implementa, crea task, arregla, revisa, analiza, añade, cambia, refactoriza, documenta.
---

# Taskboard Skill — Para Claude, DeepClaude, y AGY

Eres un agente de desarrollo trabajando en el proyecto **Axolotto**. Tienes acceso a un **tablero Kanban visual** que muestra el progreso de las tareas. El tablero NO ejecuta agentes automáticamente — **tú eres el que trabaja** y el tablero refleja tu progreso.

## El Tablero

- **URL**: http://localhost:8181
- **API**: REST en `localhost:8181/api/*`
- **Helper**: `.\tools\taskboard\bin\taskboard.ps1 <acción> <args>`

## Columnas

| Columna | Significado |
|---------|-------------|
| `wishes` | Ideas sin refinar, deseos, "algún día" |
| `concepts` | Idea analizada por AI (título formal, categoría, prioridad) |
| `planning` | Plan detallado (requisitos, archivos a modificar, guía de verificación) |
| `doing` | Estás trabajando ACTIVAMENTE en esto AHORA |
| `review` | Trabajo terminado — esperando feedback del usuario |
| `done` | Aprobado + commiteado + mergeado a develop |

## Cuándo crear tareas

**SÍ crea tarea cuando:**
- El usuario reporta un bug → `concepts` (el AI lo refinará a `planning`)
- El usuario pide una feature nueva → `wishes` o `concepts`
- El usuario dice "investiga X" → `planning`, muévelo a `doing` mientras investigas
- El usuario dice "task", "tarea", "crea task", "agrega al tablero"
- Estás haciendo un cambio grande que requiere tracking

**NO crees tarea cuando:**
- Es una pregunta simple ("¿qué hace X?") → solo responde
- Es una conversación exploratoria sin acción concreta
- El cambio es trivial (typo, formato) — solo hazlo

## Ciclo de trabajo

```
1. CREATE   → taskboard.ps1 create "título" "desc" [columna]
2. PLAN     → (opcional) AI genera plan en planning
3. DOING    → taskboard.ps1 status <id> doing "Investigando..."
4. TRABAJAR → haces el código, tests, docs
5. REVIEW   → taskboard.ps1 status <id> review "Fix listo en archivo X. Tests pasan."
6. ESPERAR  → el usuario revisa
7a. FEEDBACK → taskboard.ps1 status <id> doing "Corrigiendo: [feedback del usuario]"
7b. APPROVED → taskboard.ps1 status <id> done "Aprobado. Commiteado."
             → git add -A && git commit -m "feat: ..." && git merge
```

**Regla de oro**: NUNCA hagas commit sin que el usuario apruebe en `review`. Palabras de aprobación: "bien", "ok", "dale", "aprobado", "commit", "merge", "perfecto", "sí".

## Comandos rápidos

```powershell
# Crear
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción larga..." planning backend

# Mover
.\tools\taskboard\bin\taskboard.ps1 move task-1234567890-0 doing

# Mover + comentar (una sola llamada)
.\tools\taskboard\bin\taskboard.ps1 status task-1234567890-0 review "Fix en checkout.ts. Tests OK."

# Comentar sin mover
.\tools\taskboard\bin\taskboard.ps1 comment task-1234567890-0 "Esperando que el PR se mergee..."

# Adjuntar un doc a la tarjeta (badge 📄 Plan) — "" desvincula
.\tools\taskboard\bin\taskboard.ps1 attach task-1234567890-0 docs/plan_mi_feature.md

# Ver tareas
.\tools\taskboard\bin\taskboard.ps1 list doing
.\tools\taskboard\bin\taskboard.ps1 get task-1234567890-0
```

## Documentos adjuntos (plan_doc)

- Una tarea puede tener UN doc Markdown vinculado (`planning_data.plan_doc_path`).
- En el tablero, la tarjeta muestra el badge **📄 Plan**; al pulsarlo se abre el visor de docs directamente en ese archivo (acceso rápido). El panel de detalle muestra el mismo link clicable.
- La IA lo setea automáticamente al generar un plan en `planning`. Tú puedes setearlo con `attach`.
- Regla: si escribes un plan, auditoría o diseño para una tarea, guárdalo en `docs/` (ruta relativa al repo, terminado en `.md`) y adjúntalo con `attach` en el mismo paso. El API valida que el archivo exista dentro de `docs/`.
- Antes de trabajar una tarea, corre `get <id>`: si imprime "📄 docs/...", lee ese documento primero — contiene el plan detallado.

## Asignación por especialidad

| Agente | Especialidad | Categorías |
|--------|-------------|-----------|
| **Claude** (tú, si eres Claude) | Frontend, UI, security, contracts, blockchain, auth, wallets | `frontend`, `security`, `contracts`, `blockchain` |
| **DeepClaude** (tú, si eres DeepClaude) | Backend, API, SQL, DB, refactors, tests, Docker, infra, finanzas | `backend`, `bug`, `refactor`, `devops`, `finance` |
| **AGY** (tú, si eres AGY) | Docs, research, game design, economía, balance, análisis | `docs`, `research`, `game`, `gamedesign` |

Si el usuario no especifica agente, asígnate automáticamente según tu tipo y la categoría de la tarea.

## Git workflow

- El taskboard crea un **git worktree aislado** cuando mueves a `doing`
- Trabaja en ese worktree: `D:\Axolotto_2026\.axolotto_worktrees\<task-id>\`
- Cuando el usuario aprueba en `review`, mueve a `done` → el taskboard hace commit + merge a `develop` + wiki sync + changelog
- Si el merge automático falla, hazlo manualmente: `git merge --no-ff task/<task-id>-<slug>`

## Anti-patrones

- NO crees 10 tareas de una vez — solo las que vas a trabajar ya
- NO muevas a `done` sin aprobación explícita del usuario
- NO ignores el tablero — si estás trabajando en algo, debería reflejarse allí
- NO hagas commit en `doing` — solo en `done` después de aprobación
