---
tags: [ai-context, agentes, taskboard]
description: "Qué agente usar por tarea + workflow obligatorio del taskboard (crear tarjeta, badges, doc viewer, columnas)"
last_modified: "2026-06-07"
source_files: ["AGENTS.md", ".claude/agents/", "tools/taskboard/bin/taskboard.ps1"]
---

# Routing de Agentes Especializados

## Tabla de Decisión Rápida
| Tipo de tarea | Agente | Categoría taskboard |
|--------------|--------|-------------------|
| FastAPI endpoints, SQLModel, Alembic, wallet/bank, game logic | `backend-dev` | backend |
| Next.js, React, Tailwind, Privy, Viem, MoonPay UI | `frontend-dev` | frontend |
| Solidity, Foundry, ABIs, deployment scripts, contratos | `contrato-dev` | contracts |
| Docker Compose, PM2, Nginx, Anvil, deploy scripts, puertos | `devops` | infra |
| Simulación de economía, AXF/FRJ emission vs burn, VIP revenue | `economy-analyst` | economy |
| Auditoría de seguridad, auth checks, exploits económicos | `security-reviewer` | security |
| Mecánicas de juego, balanceo, GDD, retention loops | `game-designer` | design |
| Tests pytest, Playwright E2E, simulate_universe.py, QA | `qa-tester` | qa |

## Reglas de Despacho

- Si la tarea toca `backend/` → `backend-dev`
- Si la tarea toca `frontend/` → `frontend-dev`
- Si la tarea toca `contracts/` → `contrato-dev`
- Si la tarea toca `docker-compose.yaml`, `.env`, PM2, Nginx → `devops`
- Si la tarea mezcla layers → despachar múltiples agentes en paralelo (ver superpowers:dispatching-parallel-agents)
- Si la tarea involucra fondos, wallets, checkout, market → **SIEMPRE** incluir `security-reviewer` como revisión posterior
- Si el contrato cambia ABI → despachar `contrato-dev` + `backend-dev` (el backend necesita actualizar ABIs en `web3_service.py`)
- Si la economía cambia (precios, emission rates, VIP) → despachar `economy-analyst` para validar impacto antes de implementar

## Agentes Disponibles (8 especializaciones)

### `backend-dev`
**Archivo**: `.claude/agents/backend-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: FastAPI, SQLModel ORM, Alembic, Web3.py, dual-currency economy engine, concurrencia con SELECT FOR UPDATE, Privy JWT auth, multiplayer, checkout flows, VIP system
**Dominios**: `backend/app/api/`, `backend/app/services/`, `backend/app/models/`, `backend/app/core/`

### `frontend-dev`
**Archivo**: `.claude/agents/frontend-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Next.js 16.2, React 19, TypeScript, Tailwind 4, Privy login, Viem 2.47 (no ethers.js), MoonPay, WebSocket UI
**Componentes clave**: PlayMode, LoteriaBoard, BoardEditor, MultiplayerLobby, Criadero, Santuario, Store, Inventory, VipModal, CryptoCheckout, MarketP2P
**Dominios**: `frontend/app/`, `frontend/components/`, `frontend/hooks/`, `frontend/context/`

### `contrato-dev`
**Archivo**: `.claude/agents/contrato-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Solidity 0.8.24, OpenZeppelin, Foundry (forge compile/test/script), despliegue en Anvil/Plasma Testnet
**Contratos**: GemaAlga (FRJ), Axogema (AXF), Axolotitos (DNA bit-packing), Webitos, CartasLoteria (IDs 1-54), Boosters, TablasLoteria (escrow), Consumables, GameController
**Dominios**: `contracts/src/`, `contracts/test/`, `contracts/script/`

### `devops`
**Archivo**: `.claude/agents/devops.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Docker Compose, PM2, Nginx reverse proxy, Anvil, scripts de restart/deploy
**Scripts clave**: `reiniciar.sh` (full stack restart), `scripts/deploy_local.sh` (compile + deploy contratos + write addresses to backend/.env)
**Dominios**: `docker-compose.yaml`, `backend/.env`, `frontend/.env.local`, configuración de red

### `economy-analyst`
**Archivo**: `.claude/agents/economy-analyst.md`
**Herramientas**: Read, Write, Bash, Grep, Glob
**Especialidad**: Modelado de economía dual AXF/FRJ, emisión vs burn rates, proyecciones VIP, jackpot accumulation, análisis de simulate_universe.py
**Red flags que detecta**: GAL inflation (emission/burn > 1.5), AXG deflation, jackpot runaway, staking dominance
**Script de simulación**: `python backend/app/scripts/simulate_universe.py` → `backend/simulation_report.txt`

### `security-reviewer`
**Archivo**: `.claude/agents/security-reviewer.md`
**Herramientas**: Read, Grep, Glob (solo lectura — no modifica código)
**Especialidad**: Auth/authorization checks, replay attacks, race conditions, economic exploits, OWASP API Top 10, contratos (re-entrancy, integer overflow, access control)
**Invocar obligatoriamente cuando**: nueva feature toca wallets/checkout/market/multiplayer, antes de merge a dev de endpoints financieros
**Formato de reporte**: `[CRITICAL/HIGH/MEDIUM/LOW]` — descripción — archivo:línea — fix recomendado

### `game-designer`
**Archivo**: `.claude/agents/game-designer.md`
**Herramientas**: Read, Write, Grep, Glob
**Especialidad**: Mecánicas de Lotería mexicana, balanceo de economía dual, stats de Axolotitos (luck, focus, stamina, etc.), drop rates de boosters, VIP tier benefits, engagement loops
**Documentos que mantiene**: `docs/GDD.md`, `docs/vip_club_design.md`, `docs/plan_*.md`

### `qa-tester`
**Archivo**: `.claude/agents/qa-tester.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: pytest para FastAPI, Playwright E2E para Next.js, forge test para contratos, simulate_universe.py
**Flujos críticos que cubre**: economy integrity, board lifecycle, multiplayer rooms, checkout replay protection, incubation, VIP scheduler, P2P market
**DB de test**: SQLite (`DATABASE_URL=sqlite:///./test.db`) para tests aislados

---

## Workflow Obligatorio del Taskboard

> **REGLA**: Toda tarea, idea o plan que se inicie DEBE tener una tarjeta en el taskboard. Sin tarjeta no existe la tarea. Esto aplica a todos los agentes AI y al usuario.

### URL del Taskboard
```
http://localhost:8181
```

### Ciclo Completo de una Tarea

```
1. CREAR tarjeta  →  column: planning  (o wishes/concepts si es idea)
2. MOVER a doing  →  asignar agente    (activa badge ⚡ agente)
3. TRABAJAR       →  actualizar con comentarios de progreso
4. MOVER a review →  describir qué se hizo y cómo verificar
5. ESPERAR OK     →  el usuario aprueba con: "ok", "dale", "bien", "aprobado"
6. MOVER a done   →  SOLO después de aprobación explícita
```

**NUNCA** mover a `done` sin aprobación. **NUNCA** hacer commit sin que esté en `review` o `done`.

---

### Crear una Tarjeta con TODOS los Badges

```powershell
# Paso 1: Crear con categoría (genera badge de categoría + #ID en footer)
.\tools\taskboard\bin\taskboard.ps1 create "Título de la tarea" "Descripción detallada de qué se necesita hacer y por qué" planning <categoría>

# Paso 2: Mover a doing CON agente (activa badge ⚡ agente)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> doing "Empezando: [descripción breve del primer paso]" <agente>

# Al terminar: mover a review
.\tools\taskboard\bin\taskboard.ps1 status <task-id> review "Listo. Cambios en: [archivos]. Verificar con: [comando o pasos]."
```

**Categorías disponibles** (para el badge de categoría):
| Valor | Cuándo usarlo |
|-------|--------------|
| `backend` | Endpoints, servicios, modelos, migraciones |
| `frontend` | Componentes React, hooks, páginas |
| `contracts` | Solidity, Foundry, ABIs |
| `bug` | Fixes de cualquier capa |
| `docs` | Documentación, wiki, planes |
| `security` | Auditoría, auth, exploits |
| `finance` | Economía, precios, simulaciones |
| `gamedesign` | Mecánicas, balanceo, GDD |
| `infra` | Docker, PM2, Nginx, deploy |
| `tools` | Taskboard, scripts internos |

**Agentes válidos** (para el badge ⚡):
| Valor | Agente |
|-------|--------|
| `claude` | Claude (Anthropic) — frontend, security, contracts |
| `deepclaude` | DeepClaude (DeepSeek) — backend, DB, infra |
| `agy` | AGY (Google) — docs, research, game design |

---

### Sistema de Badges — Referencia Completa

Cada tarjeta puede mostrar estos badges según los campos configurados:

| Badge | Cómo activarlo | Ejemplo visual |
|-------|---------------|----------------|
| **#ID** | Automático al crear | `#51` en el footer |
| **⚡ agente** | `status <id> doing "msg" <agente>` | `⚡ claude` |
| **Categoría** | Parámetro al crear | `backend`, `docs`, `bug` |
| **Prioridad** | Campo `priority` (ver abajo) | `🔴 critical`, `🟡 medium` |
| **📄 Doc** | Plan guardado en `docs/` (ver abajo) | `📄 Doc` en el panel de detalles |
| **🧪 test** | Campo `test_command` vía API edit | `🧪 test` |
| **🌿 rama** | Automático al crear worktree en `doing` | `🌿 task-51-wiki` |
| **📊 progreso** | Requisitos en `planning_data.requirements` | `2/5 reqs` |
| **🔒 bloqueada** | Dependencias sin completar | `🔒 Bloqueada` |
| **✓ en dev** | Merge exitoso a rama base | `✓ en dev` (solo en `done`) |

**Fijar prioridad** (vía API directa, no hay parámetro en PS1):
```powershell
# Usar curl o la UI del taskboard para editar prioridad
Invoke-RestMethod -Uri "http://localhost:8181/api/tasks/edit" -Method POST `
  -ContentType "application/json" `
  -Body '{"id":"task-ID","priority":"high"}'
# Valores: low | medium | high | critical
```

---

### Badge 📄 Doc — Cómo Vincular un Plan a la Tarjeta

El badge `📄 Doc` aparece en el **panel de detalles** de la tarjeta y permite abrir el documento directamente en el Doc Viewer del taskboard (`http://localhost:8181` → botón "📄 Docs").

**IMPORTANTE**: El Doc Viewer solo puede leer archivos `.md` dentro de `docs/` del repositorio.

**Flujo correcto para vincular un plan:**
```powershell
# 1. Guardar el plan en docs/ (NO en C:\Users\... ni en otros lugares)
# Ejemplo: docs/plan_task-1780896719-51.md

# 2. Vincular el documento a la tarjeta vía API
Invoke-RestMethod -Uri "http://localhost:8181/api/tasks/edit" -Method POST `
  -ContentType "application/json" `
  -Body '{"id":"task-ID","planning_data":{"plan_doc_path":"docs/plan_task-ID.md"}}'

# 3. Verificar: abrir el taskboard → click en la tarjeta → ver "📄 Documento vinculado"
# O consultar desde PS1:
.\tools\taskboard\bin\taskboard.ps1 get task-ID
# Si hay doc, mostrará: "📄 docs/plan_task-ID.md"
```

**Naming convention para planes:**
```
docs/plan_task-<task-id>_<slug-del-titulo>.md
# Ejemplo: docs/plan_task-1780896719-51_obsidian-wiki.md
```

---

### Comandos PS1 — Referencia Rápida

```powershell
# Crear (columna y categoría son opcionales, default: planning / backend)
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" [columna] [categoría]

# Mover + comentar + asignar agente (en un solo comando)
.\tools\taskboard\bin\taskboard.ps1 status <id> <columna> ["comentario"] [agente]

# Solo comentar sin mover
.\tools\taskboard\bin\taskboard.ps1 comment <id> "Comentario de progreso"

# Ver lista de tareas en una columna
.\tools\taskboard\bin\taskboard.ps1 list [doing|review|planning|done]

# Ver detalles completos de una tarea (incluye doc path si existe)
.\tools\taskboard\bin\taskboard.ps1 get <task-id>
```

**Ejemplos reales:**
```powershell
# Crear tarea de bug con alta prioridad
.\tools\taskboard\bin\taskboard.ps1 create "Fix: login falla con token expirado" "El endpoint /api/v1/user/sync devuelve 500 cuando el JWT de Privy expiró hace >24h. Reproducir: login normal, esperar 24h, refrescar." planning bug

# Empezar a trabajar (asignarse como claude)
.\tools\taskboard\bin\taskboard.ps1 status task-1234567890-0 doing "Investigando en user.py y auth middleware" claude

# Comentar progreso sin mover
.\tools\taskboard\bin\taskboard.ps1 comment task-1234567890-0 "Encontrado: el middleware no llama token_refresh cuando exp < now(). Fix en auth.py:87"

# Mover a review al terminar
.\tools\taskboard\bin\taskboard.ps1 status task-1234567890-0 review "Fix aplicado en backend/app/middleware/auth.py:87. Test: pytest backend/tests/test_auth.py::test_expired_token"
```

---

### Cuándo Crear Tarjeta (y cuándo no)

**SÍ crear tarjeta cuando:**
- El usuario pide una feature, mejora, o cambio de comportamiento
- El usuario reporta un bug
- Se va a iniciar trabajo que tarda >15 minutos
- Se inicia un plan o investigación
- Se va a modificar lógica de economía, contratos, o endpoints de fondos

**NO crear tarjeta cuando:**
- Es una pregunta exploratoria sin acción concreta ("¿qué hace X?")
- Es un fix de typo o renombrado trivial (<5 minutos)
- Es una respuesta de solo lectura / análisis sin cambios en código

---

## Flujos Complejos — Qué Agentes Combinar

| Escenario | Agentes en orden |
|-----------|-----------------|
| Nueva feature de checkout/pagos | `security-reviewer` (diseño) → `backend-dev` (implementación) → `qa-tester` (tests) → `security-reviewer` (revisión final) |
| Cambio en contrato + backend | `contrato-dev` (ABI update) → `backend-dev` (web3_service.py sync) → `qa-tester` (forge test + pytest) |
| Nueva mecánica de economía | `game-designer` (spec + balance) → `economy-analyst` (validar emisión/burn) → `backend-dev` (implementar) → `qa-tester` (simulation) |
| Fix urgente en producción | `backend-dev` → `security-reviewer` → push a feature branch → PR a dev |
| Nuevo tipo de item/booster | `game-designer` (drop rates) → `contrato-dev` (si nuevo token) → `backend-dev` (shop/inventory) → `frontend-dev` (UI) → `qa-tester` |

## Referencias de Contexto (para planning de AI)
- Contexto principal auto-cargado: `CLAUDE.md`
- Detalles de diseño del juego: `docs/GDD.md`
- Estado actual del proyecto: `HANDOFF_ANTIGRAVITY.md`
- Internos del taskboard: `tools/taskboard/.context_cache/taskboard.txt`
- Contexto cacheado del proyecto: `tools/taskboard/.context_cache/axolotto.txt`

## Token-saving Tips
1. Usar `fog_brief` / `fog_lookup` (MCP fog-context) antes de leer archivos para entender estructura
2. Usar `memory_search` (shadowbrain) — agentes previos pueden haber resuelto el mismo problema
3. Leer archivos con `offset`/`limit` — no cargar archivos de 2000 líneas completos
4. Después de completar trabajo, guardar descubrimientos: `memory_put` con kind=`pattern`|`gotcha`|`decision`

→ Ver [[QUICK_START]] para el stack completo
→ Ver [[critical_rules]] para las reglas que aplican a todos los agentes
→ Ver [[gotchas]] para trampas conocidas por área del proyecto
