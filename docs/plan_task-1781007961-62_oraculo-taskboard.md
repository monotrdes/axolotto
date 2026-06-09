# Plan: Integración del Oráculo (AnythingLLM) en el Taskboard

> **Task:** `task-1781007848-99` | **Categoría:** tools/taskboard | **Prioridad:** Alta  
> **Arquitecto:** Claude | **Estado:** Planning | **2026-06-09**

---

## Contexto

El proyecto tiene una wiki de conceptos completa (`wiki/conceptos-es/`, 27 archivos, 361KB) que documenta cada sistema del juego — Axolotitos, economía dual, Gashapon, VIP, cueva, staking, etc. Es la "biblia de diseño" de Axolotto.

El taskboard actual tiene 3 providers AI (Claude, DeepClaude, Ollama) para código y planificación, pero **ninguno tiene acceso a las reglas reales del juego**. Cuando Agy o cualquier agente diseña una feature, lo hace de memoria — sin validar contra la verdad documentada.

**Solución:** Integrar AnythingLLM (RAG local, open source) cargado con los 27 archivos de la wiki como un "oráculo" que se consulta antes de diseñar.

---

## Nuevo flujo de diseño

```
Idea ──→ 🦎 ORÁCULO ──→ Agy diseña ──→ Claude implementa ──→ Ollama QA
             │               │                 │                   │
        AnythingLLM    Game Designer      Worktree            Revisión
        + wiki (27)    (ahora informado)  (código)
             │
        "Esta idea afecta
         Gashapon + VIP.
         El sistema pity usa
         contadores independientes
         por tier. La propuesta
         colisiona con la regla
         de Triple Suerte..."
```

El oráculo no reemplaza a Agy — **lo hace más inteligente**.

---

## Arquitectura técnica

```
[Taskboard Frontend]          [Taskboard Backend]           [AnythingLLM]
   modal.js / task-card.js        routes.py / ai_router.py      localhost:3001
        │                              │                            │
        │  "Consultar Oráculo"         │                            │
        │ ──────────────────────────→  │                            │
        │                              │  POST /api/v1/workspace/   │
        │                              │  axolotto-oraculo/chat     │
        │                              │  mode: "query"             │
        │                              │ ──────────────────────────→│
        │                              │                            │  RAG sobre
        │                              │                            │  27 docs wiki
        │                              │  ← {textResponse, sources} │
        │                              │                            │
        │  ← {oracle_data}             │                            │
```

---

## Componentes a modificar

### 1. `tools/taskboard/oracle_prompts.py` — NUEVO
Prompts del sistema oráculo (SYSTEM_ORACLE). El prompt le pide al LLM analizar la idea y devolver: sistemas afectados, verdades del juego con citas, conflictos, sinergias, recomendación.

### 2. `tools/taskboard/ai_router.py` — Añadir AnythingLLMProvider
Nuevo provider siguiendo el patrón existente. Llama a la API REST de AnythingLLM con `mode: "query"` (RAG puro, sin historial de chat).

### 3. `tools/taskboard/post_routes.py` — Nuevo endpoint `POST /api/tasks/oracle/consult`
Recibe `task_id`, obtiene la task de DB, ejecuta AnythingLLMProvider, guarda resultado en `oracle_data`, devuelve al frontend.

### 4. `tools/taskboard/db.py` — Nueva columna `oracle_data TEXT DEFAULT '{}'`
Migración SQLite para persistir los resultados del oráculo.

### 5. `tools/taskboard/modules/modal.js` — Botón en NewIdeaModal
Checkbox "🦎 Consultar Oráculo" (default: on para columnas wishes/concepts). Al crear, llama al endpoint y muestra resultado.

### 6. `tools/taskboard/modules/task-card.js` — Panel en TaskDetailModal
Nueva sección "🦎 Oráculo" con resultado formateado. Botones: "Consultar Ahora" / "Re-consultar".

### 7. `tools/taskboard/bin/taskboard.ps1` — Comandos CLI
```powershell
taskboard.ps1 oracle <task-id>      # Consultar oráculo
taskboard.ps1 oracle-get <task-id>  # Ver último resultado
```

---

## Setup inicial (manual, una vez)

1. Instalar AnythingLLM Desktop desde [anythingllm.com](https://anythingllm.com)
2. Crear workspace `axolotto-oraculo`
3. Arrastrar los 27 archivos de `wiki/conceptos-es/` al workspace
4. Configurar LLM provider: **Ollama → DeepSeek R1 8B** (recomendado)
   - Alternativa: Claude API para mayor calidad
5. Settings → Developer API → generar API key
6. Agregar al `.env` del proyecto:
   ```
   ANYTHINGLLM_URL=http://localhost:3001
   ANYTHINGLLM_API_KEY=<key generada>
   ```

---

## LLM para el oráculo

| Opción | Motor | Costo | Razonamiento |
|--------|-------|-------|-------------|
| 🏆 **DeepSeek R1 8B** (Ollama) | Local, ~6GB RAM | Gratis | ⭐⭐⭐ |
| Claude Haiku (API) | Nube | ~$0.01/query | ⭐⭐⭐⭐ |
| Qwen 2.5 Coder 7B (Ollama) | Local, ya instalado | Gratis | ⭐⭐ |

**Recomendado:** DeepSeek R1 8B. Es un modelo de razonamiento — piensa paso a paso antes de responder, ideal para analizar mecánicas de juego y detectar conflictos.

---

## Estructura de `oracle_data`

```json
{
  "consulted_at": "2026-06-09T12:00:00",
  "provider": "anythingllm",
  "model": "deepseek-r1:8b",
  "systems_affected": ["gashapon", "vip", "lunar-cycle"],
  "relevant_facts": [
    {
      "fact": "El sistema pity del Gashapon usa contadores independientes por tier (Bronce 12, Plata 6, Oro 4)",
      "source": "14-capsulas-gashapon.md"
    }
  ],
  "conflicts": [
    "La propuesta de multiplicador colisiona con el hard cap de 1.65x en CPU mode"
  ],
  "synergies": [
    "Combina bien con el ciclo lunar — se podría añadir como recompensa de Luna 6"
  ],
  "recommended_priority": "medium",
  "raw_sources": [
    {"title": "14-capsulas-gashapon.md", "chunk": "..."},
    {"title": "15-vip-club.md", "chunk": "..."}
  ]
}
```

---

## Verificación

1. Iniciar AnythingLLM, verificar `curl http://localhost:3001/api/v1/workspaces`
2. Iniciar taskboard, abrir `localhost:8181`
3. Crear idea con "Consultar Oráculo" activado
4. Verificar panel de resultado con sistemas afectados, verdades, conflictos
5. Probar `taskboard.ps1 oracle task-xxx` desde terminal
6. Verificar persistencia en SQLite (reiniciar taskboard, la task conserva oracle_data)

---

## Fuentes

- Wiki de conceptos: `wiki/conceptos-es/` (27 archivos, 361KB)
- Taskboard server: `tools/taskboard/server.py` (port 8181)
- AI Router: `tools/taskboard/ai_router.py` (patrón de providers)
- DB schema: `tools/taskboard/db.py`
- Frontend: `tools/taskboard/modules/modal.js`, `task-card.js`
- AnythingLLM API: `https://docs.anythingllm.com/features/api`
