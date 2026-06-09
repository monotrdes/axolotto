# Axolotto Project Brief (auto-injected on session start)
# Generated: 2026-06-05 — Refresh after major architecture changes

## Project Identity
- **Name**: Axolotto — Metaverse Lottery Game
- **Repo**: D:\Axolotto_2026\axolotto
- **Branch**: develop (default), master (production)
- **Server**: tridyland (Windows + Docker Desktop + PM2 + Nginx)

## Active Context (June 2026)
- Currency renamed: AXG→AXF (Axofichas), GAL→FRJ (Frijolitos)
- Token rename migration in progress (models, endpoints, contracts being updated)
- Landing page "Flujo Corcholata" feature in planning (promo code redemption)
- Economy constants being recalibrated for AXF/FRJ

## Architecture at a Glance
- **Backend**: FastAPI + SQLModel + PostgreSQL (Docker, port 8001)
- **Frontend**: Next.js 16 + React 19 + Tailwind 4 (PM2, port 3000)
- **Contracts**: 14 Solidity contracts via Foundry (Anvil :8545)
- **Auth**: Privy (social login + JWT)
- **Taskboard**: Self-hosted Kanban with AI agents (Python stdlib + vanilla JS)

## Current Priorities (sprint)
1. Complete AXG→AXF / GAL→FRJ rename across all layers
2. Implement promo code redemption flow (Corcholata)
3. Stabilize multiplayer game rooms
4. VIP tier economy balancing

## Active Gotchas
- DB has renamed columns that Alembic doesn't know about — use idempotent migrations with DO $$ blocks
- Two Alembic heads were merged (bb01d2e3f4a5) — don't create new branches off old heads
- Economy models have compatibility aliases (AxgPurchaseRecord = AxfPurchaseRecord)
- Taskboard agents use isolated git worktrees — main repo stays clean
