---
tags: [changelog]
description: "Historial de todos los cambios al wiki con fecha, motivo, autor y referencia al código"
last_modified: "2026-06-07"
---

# Wiki Changelog — Axolotto

> Registra CADA vez que se actualiza un valor en el wiki. Un agente AI que actualice precios, stats, o reglas DEBE añadir una entrada aquí antes del commit.

## Formato de entrada

```
## YYYY-MM-DD | archivo_modificado.md | Campo o sección cambiada
- **Campo**: nombre exacto del campo o valor
- **Anterior**: valor o texto previo (pon "—" si es creación inicial)
- **Nuevo**: valor o texto actualizado
- **Motivo**: razón del cambio (ej: "ajuste de balance", "corrección de bug", "nuevo feature")
- **Autor**: Claude / DeepClaude / AGY / [usuario]
- **Fuente en código**: `backend/app/core/prices.py:WEBITO_PRICES` o commit hash
```

---

## 2026-06-07 | wiki/ai/ | Workflow obligatorio del taskboard

### agent_routing.md — Nueva sección "Workflow Obligatorio del Taskboard"
- **Campo**: Sección nueva (antes no existía)
- **Anterior**: —
- **Nuevo**: Guía completa del ciclo de vida de tareas en el taskboard: crear tarjeta con todos los badges (#ID, ⚡ agente, categoría, prioridad, 📄 doc, 🧪 test), comandos PS1 con ejemplos reales, cómo vincular plan doc en `docs/` para el Doc Viewer, cuándo crear tarjeta y cuándo no
- **Motivo**: Los agentes AI necesitan saber que TODA tarea debe tener tarjeta en el taskboard, qué badges usar, y cómo activar el badge 📄 Doc con link funcional al Doc Viewer
- **Autor**: Claude
- **Fuente en código**: `tools/taskboard/bin/taskboard.ps1`, `tools/taskboard/server.py`

### critical_rules.md — Regla 11 añadida
- **Campo**: Regla #11 (Taskboard obligatorio)
- **Anterior**: 10 reglas
- **Nuevo**: 11 reglas — la #11 exige tarjeta en taskboard para toda tarea
- **Motivo**: Formalizar el workflow del taskboard como regla crítica obligatoria
- **Autor**: Claude

### QUICK_START.md — Sección "Workflow Obligatorio" añadida
- **Campo**: Nueva sección de taskboard en QUICK_START
- **Anterior**: Solo stack, monedas y archivos importantes
- **Nuevo**: 3 comandos esenciales + link a guía completa
- **Autor**: Claude

---

## 2026-06-10 | backend/app/services/multiplayer_service.py | VULN-05: Fix inflación de premios

### multiplayer_service.py — Liquidación multijugador con invariante de conservación de fondos
- **Campo**: Reparto de Premio 1, Premio 2 y Jackpot bonus en `simulate_multiplayer_match`
- **Anterior**: `luck_bonus` y `vip_bonus` se sumaban ENCIMA del share base (fondos fantasma — no respaldados en ningún vault)
- **Nuevo**: Opción A (in-pool bonuses) — bonuses redistribuyen DENTRO del pool con aritmética basis-points. Si Σ raw > pool → normalización proporcional; remanente a tesorería. Invariante: `Σ premios ≤ (premio_1_pool + premio_2_pool)`
- **Motivo**: VULN-05 Auditoría de Seguridad Web3 2026-06-09 — inflación de FRJ por bonuses sin respaldo
- **Autor**: Claude Sonnet 4.6
- **Fuente en código**: commit `aebad48` — `multiplayer_service.py` + 5 tests en `test_prize_invariants.py`

---

## 2026-06-07 | wiki/ | Creación inicial del vault Obsidian

### 00-INDEX.md — Índice maestro
- **Campo**: Creación inicial
- **Anterior**: —
- **Nuevo**: Índice con navegación para AI agents y jugadores
- **Motivo**: Configuración inicial del vault Obsidian para onboarding AI en <400 tokens y docs para jugadores
- **Autor**: Claude
- **Fuente en código**: Rama `feature/multiplayer-redesign`, tarea `task-1780896719-51`

### wiki/ai/ — Contexto para AI agents
- **Campo**: 4 archivos (QUICK_START, critical_rules, gotchas, agent_routing)
- **Anterior**: —
- **Nuevo**: Creación inicial desde CLAUDE.md y memory/
- **Motivo**: Reducir tokens de exploración de ~15,000 a ~2,000 por sesión AI
- **Autor**: Claude (Agente A1)
- **Fuente en código**: `CLAUDE.md`, `memory/feedback_critical_rules.md`, `memory/project_gotchas.md`

### wiki/economia/ — Precios y economía
- **Campo**: 4 archivos (monedas, tablas_precios, vip_tiers, economia_general)
- **Anterior**: —
- **Nuevo**: Creación inicial desde config.py y prices.py
- **Motivo**: Centralizar todas las tablas de precios para referencia rápida
- **Autor**: Claude (Agente A2)
- **Fuente en código**: `backend/app/core/config.py`, `backend/app/core/prices.py`

### wiki/mecanicas/ — Mecánicas del juego
- **Campo**: 6 archivos (patrones, stats, staking, cueva, incubación, gashapon)
- **Anterior**: —
- **Nuevo**: Creación inicial con fórmulas exactas del código
- **Motivo**: Documentar reglas de juego con datos verificados del código fuente
- **Autor**: Claude (Agente A3)
- **Fuente en código**: `backend/app/services/game_logic.py`, `backend/app/models/axolotito.py`

### wiki/jugadores/ — Guías para jugadores
- **Campo**: 6 archivos en español casual
- **Anterior**: —
- **Nuevo**: Creación inicial de guías player-facing
- **Motivo**: Documentación pública para jugadores sobre mecánicas, precios y procesos
- **Autor**: Claude (Agente A4)
- **Fuente en código**: `docs/completed/AXOLOTTO_BIBLE.md`, síntesis de wiki/economia/ y wiki/mecanicas/

### wiki/arquitectura/ + wiki/api/ — Referencia técnica
- **Campo**: 8 archivos (backend, frontend, contratos, DB, 4 módulos API)
- **Anterior**: —
- **Nuevo**: Creación inicial de referencia de arquitectura
- **Motivo**: Onboarding técnico para desarrolladores y agentes AI nuevos
- **Autor**: Claude (Agente A5)
- **Fuente en código**: `backend/app/api/v1/endpoints/`, `frontend/components/`, `contracts/src/`
