---
tags: [ai-context, onboarding]
description: "Stack completo + reglas críticas para AI agents en menos de 1000 tokens"
last_modified: "2026-06-07"
source_files: ["CLAUDE.md", "memory/project_architecture.md"]
---

# Quick Start para AI Agents

## Stack (30 segundos)
| Capa | Tecnología | Puerto |
|------|-----------|--------|
| Backend | FastAPI (async) · SQLModel ORM · Alembic · PostgreSQL 16 | 8001 |
| Frontend | Next.js 16.2 App Router · React 19 · TypeScript 5 · Tailwind CSS 4 | 3000 |
| Contratos | Solidity · Foundry · Anvil local / Plasma Testnet (chain 9746) | 8545 |
| Auth | Privy JWT via header `X-Privy-Token` | — |
| Web3 FE | Viem 2.47 (NO ethers.js) | — |
| Proxy | Nginx → `api.axolot.to` → localhost:8001 | — |
| DB | PostgreSQL en Docker, expuesto en `127.0.0.1:5433` | 5433 |

## Monedas (renombradas 2026-06)
| Moneda | Símbolo | Alias en código | Uso | Cómo obtener |
|--------|---------|----------------|-----|-------------|
| Axofichas | AXF | `axg`, `axofichas`, `axf` | Premium: compras reales, VIP | MoonPay / USDC |
| Frijolitos | FRJ | `gal`, `frijolitos`, `frj` | Gameplay: salas, cápsulas, staking | Jugar, staking, daily rewards |

**CRÍTICO**: En modelos Python: `AxgPurchaseRecord = AxfPurchaseRecord` (alias de compatibilidad). Usar `AxfPurchaseRecord` en código nuevo.

## 5 Reglas que NUNCA Romper
1. **`SELECT FOR UPDATE`** antes de mutar Wallet o Inventory (evita race conditions — costó transacciones perdidas en producción)
2. **`ProcessedTransaction`** (columna UNIQUE) antes de acreditar recompensas on-chain (anti-replay)
3. **`random.SystemRandom()`** exclusivamente — jamás `random.random()` o `random.choice()`
4. **Direcciones de contrato** siempre desde `NEXT_PUBLIC_*` env vars o `settings.py` — nunca hardcode
5. **Nunca push a main/master** — feature branches → merge a `dev`
6. **Changelog obligatorio**: Todo merge a dev registra entrada en `wiki/CHANGELOG.md` (automatizado por taskboard).

## Archivos Más Importantes
| Propósito | Archivo |
|-----------|---------|
| Configuración economía (VIP, precios base) | `backend/app/core/config.py` |
| Lógica de juego (patrones, miss chance, lucky save) | `backend/app/services/game_logic.py` |
| Operaciones de wallet | `backend/app/services/bank_service.py` |
| Integración blockchain / replay protection | `backend/app/services/web3_service.py` |
| Modelos economía (ledger, purchase records) | `backend/app/models/economy.py` |
| Todos los modelos DB | `backend/app/models/` |
| Componente de juego principal | `frontend/components/PlayMode.tsx` |
| Tienda UI | `frontend/components/Store.tsx` |
| Lobby multijugador | `frontend/components/MultiplayerLobby.tsx` |
| Hub central de contratos | `contracts/src/GameController.sol` |

## Patrón de Código Backend
```
router → @router.post → Depends(get_current_user) → service → commit
service: SELECT FOR UPDATE → business logic → db.add(TransactionLedger) → commit
```

## Precios de Referencia (economy.py / HANDOFF)
| Item | Precio |
|------|--------|
| Partida fácil (clásica) | 10 AXF |
| Partida difícil / 5 tablas | 50 AXF |
| Booster pure (más barato) | 60 AXF + 800 FRJ |
| Booster regular | 100 AXF + 1300 FRJ |
| VIP Coral | 100 AXF |
| VIP Dorado | 250 AXF |
| VIP Axolite | 500 AXF |

## MCP Servers disponibles (usar antes de leer archivos)
- **axolotto-kb**: `get_architecture`, `get_economy`, `get_conventions` — evita 20-50K tokens de exploración manual
- **fog-context**: `fog_brief`, `fog_lookup`, `fog_impact` — índice de símbolos del codebase
- **shadowbrain**: `memory_search`, `memory_put` — memoria cross-session de agentes anteriores

## Workflow Obligatorio — Taskboard

**Antes de empezar cualquier tarea**: crear tarjeta en `http://localhost:8181`

```powershell
# 1. Crear tarjeta (activa badge categoría + #ID)
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" planning <categoría>

# 2. Mover a doing con agente (activa badge ⚡ agente)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> doing "Empezando..." <claude|deepclaude|agy>

# 3. Al terminar → review (esperar aprobación antes de done)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> review "Listo. Cambios en X. Verificar con Y."
```

Para vincular un plan con badge 📄: guardar el plan en `docs/plan_task-<id>_slug.md` y editar `planning_data.plan_doc_path` vía API.

→ Guía completa de badges, doc viewer y comandos: [[agent_routing#Workflow Obligatorio del Taskboard]]

→ Detalles: [[critical_rules]] · [[gotchas]] · [[agent_routing]]
