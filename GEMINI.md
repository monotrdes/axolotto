# Axolotto — Gemini Agent Context (GEMINI.md)

## Project Identity
Axolotto is a Web3 metaverse lottery game (axolot.to).
- **Backend**: FastAPI + SQLModel + PostgreSQL 16 (Docker, port 8001)  
- **Frontend**: Next.js 16 + React 19 + Tailwind 4 (PM2, port 3000)
- **Contracts**: 14 Solidity contracts via Foundry (Anvil / Plasma Testnet chain 9746)
- **Auth**: Privy JWT (`X-Privy-Token` header) + social login
- **Currency**: AXF (Axofichas, primary ERC-20) + FRJ (Frijolitos, secondary ERC-20)
- **Taskboard**: Self-hosted Kanban at localhost:8181 (tools/taskboard/)

## Your Role (AGY)
You specialize in: **docs, research, game design, economy analysis, balance**.
For backend/API work → defer to DeepClaude. For frontend/UI → defer to Claude.

## Critical Rules
1. NEVER push to main/master — feature branches → merge to dev
2. SELECT FOR UPDATE on Wallet/Inventory before any mutation
3. ProcessedTransaction insert BEFORE crediting on-chain payments  
4. random.SystemRandom() ONLY — never random.random()
5. Contract addresses from env vars — never hardcode
6. Privy auth check before wallet/backend mutations
7. Conventional Commits: `feat(scope): desc` | `fix(scope):` | `docs:` | `refactor:`
8. Taskboard changes stay in tools/taskboard/ ONLY

## Key Prices (backend/app/core/config.py)
- Easy game: 10 AXF | Hard game (5 boards): 50 AXF
- Booster cheap: 60 AXF + 800 FRJ | Booster regular: 100 AXF + 1300 FRJ
- VIP tiers: coral 100 AXF | dorado 250 AXF | axolite 500 AXF
- AXF→FRJ: 10→100 | 50→600 | 100→1500 | 250→4000

## Key Backend Files
- `backend/app/api/v1/endpoints/` — 23 route modules (bank, game, multiplayer, shop…)
- `backend/app/services/` — 28 service modules (bank, game_logic, web3, shop…)
- `backend/app/models/` — economy.py, user.py, axolotito.py, board.py, items.py
- `backend/app/core/config.py` — VIP tiers, economy constants, BLOCKCHAIN_MODE

## Key Frontend Files
- `frontend/app/page.tsx` — Main UI (tab switcher, screen routing)
- `frontend/components/PlayMode.tsx` — Core lottery gameplay
- `frontend/components/ui/LoteriaBoard.tsx` — 4×4 card grid
- `frontend/hooks/` — useBlockchainEvents, useMoonPayWidget, useInventory

## MCP Knowledge Server (axolotto-kb)
Use these tools BEFORE reading files:
- `get_live_status` — current branch + recent commits + open tasks (call FIRST)
- `get_architecture` — full project overview
- `get_module <name>` — backend | frontend | contracts | taskboard | bank | game | multiplayer…
- `get_economy` — all prices, VIP tiers, exchange rates
- `get_conventions` — code patterns + critical rules
- `search_knowledge <query>` — search everything

## Taskboard Workflow
- **URL**: http://localhost:8181
- **CLI**: `.\tools\taskboard\bin\taskboard.ps1 <action> <args>`
- **Columns**: wishes → concepts → planning → doing → review → done
- When starting work: move task to `doing` | When done: move to `review`

## Context Files (for AI planning)
- `.claude/context/project-brief.md` — Live sprint status (auto-regenerated)
- `tools/taskboard/.context_cache/axolotto.txt` — Full context (24h TTL)
- `AGENTS.md` — Agent routing and sub-agent definitions
- `docs/GDD.md` — Full game design document
- `docs/vip_club_design.md` — VIP economy design

## Session Tips (token efficiency)
1. Call `get_live_status` first — see what's actually being worked on
2. Use `get_module` instead of reading large files  
3. Read files with offset/limit when possible
4. Check AGENTS.md for specialized sub-agents before doing domain work
5. After work: update taskboard + brief notes on what changed
