---
name: taskboard
description: Gestiona el tablero Kanban de Axolotto vía taskboard.ps1 — crear, mover, comentar, listar tareas.
disable-model-invocation: true
context: fork
model: haiku
argument-hint: "<acción> — ej: crea \"Fix login\" en planning | mueve task-123 a review \"tests OK\" | lista doing"
allowed-tools: PowerShell(*taskboard.ps1*) Bash(*taskboard.ps1*)
---

# Taskboard — operador del tablero Kanban

Traduce la petición en `$ARGUMENTS` a UNA llamada del helper y ejecútala desde la raíz del repo (`D:\Axolotto_2026\axolotto`):

```powershell
.\tools\taskboard\bin\taskboard.ps1 <acción> <args>
```

## Comandos

| Petición | Comando |
|----------|---------|
| crear tarea | `create "título" "descripción" [columna] [categoría]` |
| mover + comentar (preferir sobre move/comment separados) | `status <task-id> <columna> "comentario" [agente]` |
| solo comentar | `comment <task-id> "texto"` |
| adjuntar/desvincular doc | `attach <task-id> <ruta-doc>` (`""` desvincula) |
| listar | `list [columna]` |
| detalle de una tarea | `get <task-id>` |

## Docs adjuntos

`attach` vincula un Markdown a la tarjeta y le pone el badge **📄 Plan** (al pulsarlo en el tablero se abre el visor de docs con ese archivo). La ruta es relativa al repo y DEBE estar dentro de `docs/` y terminar en `.md` (ej: `docs/plan_mi_feature.md`); si el archivo no existe, el API responde 400. Si escribes un plan/auditoría/diseño para una tarea, guárdalo en `docs/` y adjúntalo en el mismo paso.

- **Columnas**: `wishes` `concepts` `planning` `doing` `review` `done`
- **Categorías**: `frontend` `backend` `bug` `docs` `security` `finance` `game` `infra` `devops` `blockchain`
- **Agentes**: `claude` `deepclaude` `agy`

## Respuesta

Responde con UNA sola línea: task-id, columna resultante y confirmación (o el listado compacto si fue `list`/`get`). El resultado vuelve a la conversación principal — cada palabra extra cuesta tokens.

Si el `get` muestra "📄 doc/...", incluye ese path en la respuesta para que el agente principal pueda leer el plan.

$ARGUMENTS
