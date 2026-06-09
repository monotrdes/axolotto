---
title: "Plan: Unified Agent Orchestration con Agy Gateway"
date: 2026-06-08
status: doing
task_id: task-1780912378-99
tags: [architecture, agents, orchestration, agy, taskboard]
---

# Unified Agent Orchestration — Agy como Gateway Central

## Resumen

Migración del flujo multi-agente fragmentado (4 consolas) a una arquitectura unificada donde **Agy (Antigravity)** es el orquestador central, conectado al taskboard Kanban vía WebSocket.

## Arquitectura

```
AGY GATEWAY (ws://localhost:8642)
  ├── Orquestador Plan A: Gemini 3.5 Flash (agy gateway :8642)
  ├── Plan B (Chat IA): Claude / DeepSeek / Ollama
  └── Sub-agentes especialistas (NO restringidos):
      ├── Claude Opus 4.8 → critical_worker
      ├── Claude Sonnet 4.6 → frontend_ux
      ├── DeepSeek V4 Pro → simulation_math
      ├── DeepSeek V4 Flash → micro_tasks
      └── Qwen 2.5 Coder 7B (Ollama) → local_qa
          │
          ▼ WebSocket
TASKBOARD (http://localhost:8181)
  ├── UI Kanban 6-columnas
  ├── Git worktree isolation
  ├── Wiki auto-sync
  └── Agent console en tiempo real
```

## Especializaciones (Scoring Ponderado)

Cada agente es **especialista, NO restringido**. El routing usa scoring:

```
total = (specialization_match × 3) + (availability × 2)
      + (cost_efficiency × 1) + (load × -1)
      + (complexity_match × 2)
```

## Fases de Implementación

| # | Fase | Estado |
|---|---|---|
| 1 | Limpieza + fix .gitignore | pending |
| 2 | workspace.json registry | pending |
| 3 | AgyClient WebSocket + AgyProvider | pending |
| 4 | Agent definitions con modelos reales | pending |
| 5 | Routing scoring ponderado | pending |
| 6 | OllamaProvider + pipeline QA | pending |
| 7 | Agent Console UI básico | pending |
| 8 | Script dev-start.ps1 | pending |
| 9 | Taskboard super informativo | pending |

## Arranque

```powershell
.\dev-start.ps1                  # Completo (agy + ollama + taskboard)
.\dev-start.ps1 -NoAgy           # Sin agy (standalone)
.\dev-start.ps1 -TaskboardOnly   # Solo taskboard
```

## Archivos Clave

- `workspace.json` — Registry central de providers y especializaciones
- `tools/taskboard/agy_client.py` — Cliente WebSocket hacia agy
- `tools/taskboard/ai_router.py` — Providers + scoring
- `.claude/agents/*.md` — Modelos reales asignados
- `dev-start.ps1` — Script de arranque unificado

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
