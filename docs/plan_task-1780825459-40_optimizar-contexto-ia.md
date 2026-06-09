# Plan: Optimizar Uso de Tokens — Contexto Semántico para Agentes IA

> Análisis por **Claude** · tarea `task-1780825459-40` · 2026-06-07

---

## Descripción

Reducir el consumo de tokens y mejorar la calidad del contexto que reciben los agentes IA
(Claude, DeepClaude, AGY) al planificar o ejecutar tareas. El objetivo es que cada agente
llegue al trabajo con una foto precisa y actualizada del proyecto usando la menor cantidad
de tokens posible.

---

## Diagnóstico: Estado Actual

### Lo que ya existe (bien)
- `mcp_knowledge_server.py` — servidor MCP con 7 tools (`get_architecture`, `get_module`, etc.)
  registrado en `.claude/settings.json` bajo `axolotto-kb` ✅
- `project_context.py` — generador de contexto semántico con caché de 24h ✅
- `project-brief.md` — inyectado en cada sesión vía SessionStart hook ✅
- `ai_router.py` — inyecta contexto en prompts de planning ✅

### Problemas identificados

| # | Problema | Impacto |
|---|----------|---------|
| 1 | **Contexto estático** — `project-brief.md` lleva fecha `2026-06-05`, sprint items hardcodeados | Agentes trabajan con foto desactualizada |
| 2 | **Cuádruple duplicación** — CLAUDE.md + project-brief.md + project_context.py + KNOWLEDGE dict de MCP tienen la misma info en 4 lugares | Tokens desperdiciados en contexto repetido |
| 3 | **Sin auto-refresh** — el contexto no se actualiza al hacer commits o merges | Sprint items se vuelven stale rápidamente |
| 4 | **Contexto plano e indiscriminado** — ai_router inyecta TODOS los ~8K chars de contexto en cada tarea, sin importar si es frontend, backend o contracts | 60-70% del contexto es irrelevante para la tarea |
| 5 | **MCP KNOWLEDGE dict hardcodeado** — `mcp_knowledge_server.py` tiene `"updated": "2026-06-05"` y sprint items fijos | Los tools del MCP devuelven info obsoleta |
| 6 | **Agentes spawneados por agent_runner.py no reciben MCP config** — cuando el taskboard lanza un subprocess Claude, no pasa `--mcp-config` | El agente re-explora el codebase en vez de usar las tools del KB |
| 7 | **Sistema de memoria vacío** — `.claude/projects/D--Axolotto-2026-axolotto/memory/` no tiene ningún archivo | Cada sesión empieza sin conocimiento acumulado |

---

## Propuestas de Mejora

### PROPUESTA A — Auto-refresh de contexto en git hooks
**Prioridad: ALTA | Esfuerzo: BAJO**

Agregar un git hook `post-commit` (y opcionalmente `post-merge`) que ejecute automáticamente `refresh_context.py`. Así el contexto siempre refleja el estado real del repo.

```bash
# .git/hooks/post-commit
#!/bin/sh
python tools/taskboard/refresh_context.py --scope all 2>/dev/null &
```

También agregar trigger desde `task_lifecycle.py` cuando una tarea llega a `done` (merge completado).

**Archivos a modificar:**
- `.git/hooks/post-commit` (nuevo)
- `.git/hooks/post-merge` (nuevo)  
- `tools/taskboard/task_lifecycle.py` (agregar llamada a `refresh_context`)

---

### PROPUESTA B — Contexto activo dinámico (eliminar hardcodeo de sprint)
**Prioridad: ALTA | Esfuerzo: MEDIO**

Reemplazar los sprint items hardcodeados en `project_context.py` (sección 7) y en
`mcp_knowledge_server.py` (clave `active_context`) con generación dinámica desde:
1. `git log --oneline -8` — últimos commits reales
2. `git diff --name-only HEAD~5..HEAD` — archivos más modificados recientemente
3. API del taskboard `GET /api/tasks?status=doing,review` — qué se está trabajando ahora

Esto elimina el problema de que el contexto diga cosas como "Currency rename in progress"
cuando eso ya se completó hace semanas.

**Archivos a modificar:**
- `tools/taskboard/project_context.py` — reemplazar `_build_axolotto_context()` sección 7
- `tools/taskboard/mcp_knowledge_server.py` — reemplazar clave `active_context`
- `tools/taskboard/refresh_context.py` — agregar flag `--with-tasks` que consulte la API

---

### PROPUESTA C — Contexto escalonado por categoría (mayor ahorro de tokens)
**Prioridad: ALTA | Esfuerzo: MEDIO**

En `ai_router.py → _process_planning()`, en vez de inyectar el contexto completo (~8K chars),
construir un contexto enfocado según `task.category`:

```python
def _get_focused_context(scope: str, category: str) -> str:
    """Return only the context relevant to this category."""
    full = get_cached_project_context(scope)
    if category == "frontend":
        return extract_sections(full, ["ARCHITECTURE OVERVIEW", "FRONTEND", "CRITICAL RULES"])
    elif category == "backend":
        return extract_sections(full, ["ARCHITECTURE OVERVIEW", "BACKEND", "CRITICAL RULES"])
    elif category in ("contracts", "blockchain"):
        return extract_sections(full, ["CONTRACTS", "CURRENCY SYSTEM", "CRITICAL RULES"])
    elif category == "tools":
        return get_cached_project_context("taskboard")
    else:
        return full  # fallback: contexto completo
```

**Ahorro estimado**: 60-70% menos tokens en planning para tareas de categoria específica.

**Archivos a modificar:**
- `tools/taskboard/ai_router.py` — método `_get_project_context()` + `_process_planning()`
- `tools/taskboard/project_context.py` — agregar función `extract_sections()`

---

### PROPUESTA D — MCP tool para contexto vivo del proyecto
**Prioridad: MEDIA | Esfuerzo: MEDIO**

Agregar 2 tools nuevas al `mcp_knowledge_server.py`:

**Tool: `get_live_status`**
```json
{
  "name": "get_live_status",
  "description": "Current live project status: active git branch, recent commits, open tasks, modified files. Call this FIRST in any session — more accurate than get_recent_changes."
}
```
Implementación: ejecuta `git log --oneline -8`, `git diff --name-only HEAD~3..HEAD`,
consulta `localhost:8181/api/tasks?status=doing,review`.

**Tool: `get_file_context`**
```json
{
  "name": "get_file_context",
  "description": "Get the documentation context for a specific file path without reading it."
}
```
Implementación: busca en el KNOWLEDGE dict si existe info sobre esa ruta específica.

**Archivos a modificar:**
- `tools/taskboard/mcp_knowledge_server.py` — agregar ambos tools a `TOOLS` dict

---

### PROPUESTA E — Inicializar sistema de memoria del proyecto
**Prioridad: MEDIA | Esfuerzo: BAJO**

El directorio `.claude/projects/D--Axolotto-2026-axolotto/memory/` existe pero está vacío.
El sistema de memoria de Claude persiste entre sesiones y reduce significativamente la
exploración redundante.

Crear archivos de memoria para:
- `project_architecture.md` — arquitectura y stack (tipo: `project`)
- `critical_rules.md` — reglas que no se pueden romper (tipo: `feedback`)
- `known_gotchas.md` — problemas conocidos, trampas del DB/Alembic (tipo: `project`)
- `active_sprint.md` — qué se está trabajando ahora, actualizado manualmente (tipo: `project`)

**Beneficio**: Claude no tiene que re-explorar CLAUDE.md ni project_context.py en cada sesión;
los patrones críticos ya están en memoria cargada automáticamente.

---

### PROPUESTA F — Unificar las 4 fuentes de contexto en jerarquía clara
**Prioridad: MEDIA | Esfuerzo: ALTO**

Actualmente hay 4 canales que describen lo mismo:
1. `CLAUDE.md` (tablas de stack/archivos)
2. `project-brief.md` (inyectado en SessionStart)
3. `project_context.py` (para agentes del taskboard)
4. `mcp_knowledge_server.py` KNOWLEDGE dict (para Claude via MCP)

**Propuesta: jerarquía de responsabilidades:**
- `CLAUDE.md` → reglas de desarrollo y arquitectura **estable** (no cambia entre sprints)
- `project-brief.md` → **solo contexto dinámico**: rama actual, últimos 5 commits, tareas en `doing` (máx 500 tokens, se regenera automáticamente)
- `project_context.py` → contexto completo para agentes del **taskboard** (no Claude Code)
- `mcp_knowledge_server.py` → **deep lookup on demand** para Claude Code (no inyectar todo en el inicio)

Esto elimina la duplicación y reduce el overhead de sesión.

**Archivos a modificar:**
- `.claude/context/project-brief.md` — convertir a template dinámico
- `tools/taskboard/refresh_context.py` — regenerar también project-brief.md
- `CLAUDE.md` — remover tablas de archivos (ya están en MCP), dejar solo reglas críticas

---

### PROPUESTA G — Agentes spawneados con MCP config
**Prioridad: BAJA | Esfuerzo: BAJO**

Cuando `agent_runner.py` lanza un subprocess `claude -p ...`, agregar flag `--mcp-config`
apuntando a un archivo JSON temporal que incluye el `axolotto-kb` server.

```python
# En agent_runner.py, al construir el comando del agente:
mcp_config = {
    "mcpServers": {
        "axolotto-kb": {
            "command": "python",
            "args": [str(CURRENT_DIR / "mcp_knowledge_server.py")]
        }
    }
}
mcp_config_path = write_temp_json(mcp_config)
cmd = ["claude", "--mcp-config", mcp_config_path, "-p", prompt, ...]
```

**Beneficio**: Los agentes del taskboard usan `get_architecture()` en vez de explorar
el codebase con `find` y `cat` secuenciales.

---

## Plan de Implementación Sugerido

| Fase | Propuesta | Descripción | Tiempo est. |
|------|-----------|-------------|-------------|
| 1 | A + E | Auto-refresh hooks + Inicializar memoria | 30 min |
| 2 | B | Contexto activo dinámico (eliminar hardcodeos) | 1h |
| 3 | C | Contexto escalonado por categoría en ai_router | 1h |
| 4 | D | Nuevas MCP tools (`get_live_status`, `get_file_context`) | 45 min |
| 5 | F | Jerarquía unificada de fuentes de contexto | 2h |
| 6 | G | MCP config en agentes spawneados | 20 min |

**Orden lógico de dependencias:**
- B debe ir antes que F (para tener la generación dinámica antes de reestructurar)
- C es independiente, puede hacerse en cualquier momento
- G depende de que MCP esté bien configurado (verificar con Propuesta D)

---

## Estimación de Ahorro

| Mejora | Ahorro estimado de tokens por tarea |
|--------|-------------------------------------|
| Propuesta C (contexto escalonado) | ~4,000-5,000 tokens en planning |
| Propuesta B (eliminar duplicación dinámica) | ~500-800 tokens en planning |
| Propuesta E (memoria) | ~2,000-3,000 tokens en exploración inicial |
| Propuesta G (MCP en agentes) | ~10,000-20,000 tokens (evita file exploration) |
| **Total estimado por sesión de agente** | **~16,000-29,000 tokens** |

---

## Criterios de Aceptación (para implementación futura)

- [ ] `project-brief.md` se regenera automáticamente al hacer commit (no requiere refresh manual)
- [ ] El sprint status en project-brief.md muestra las tareas reales en `doing` del taskboard
- [ ] `ai_router._process_planning()` inyecta solo el contexto relevante a la categoría de la tarea
- [ ] `mcp_knowledge_server.py` tiene tool `get_live_status` con datos dinámicos (commits + tareas abiertas)
- [ ] El directorio de memoria tiene al menos 3 archivos inicializados con las reglas críticas
- [ ] Un agente spawneado por el taskboard puede llamar `get_architecture` sin explorar archivos

---

## Notas Adicionales

- Las propuestas A y E son las más rápidas de implementar y dan valor inmediato
- La propuesta F es la más arriesgada (toca CLAUDE.md que es el documento base del proyecto)
  — requiere consenso del equipo antes de ejecutar
- El MCP server `axolotto-kb` ya está registrado en settings.json; solo falta que se use
  activamente desde el primer turn de cada sesión llamando `get_live_status`
- Todos los cambios del taskboard deben mantenerse en `tools/taskboard/` (regla crítica #8)
