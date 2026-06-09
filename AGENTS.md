# AGENTS.md — Axolotto AI Agent Router

This file routes AI agents to the right knowledge for the task at hand. CLAUDE.md is loaded by default; the resources below are loaded on-demand.

## Quick Reference

- **Project overview & architecture** → `CLAUDE.md` (auto-loaded)
- **Game design details** → `docs/GDD.md`
- **VIP / economy design** → `docs/vip_club_design.md`
- **Latest handoff / state** → `HANDOFF_ANTIGRAVITY.md`
- **Taskboard internals** → `tools/taskboard/.context_cache/taskboard.txt`

## Specialized Agents

The project defines these sub-agents in `.claude/agents/`. Invoke them for domain-specific work:

| Agent | File | When to use |
|-------|------|-------------|
| **backend-dev** | `.claude/agents/backend-dev.md` | FastAPI, SQLModel, Web3.py, bank/wallet, multiplayer, checkout |
| **frontend-dev** | `.claude/agents/frontend-dev.md` | Next.js, React, Tailwind, Privy, Viem, MoonPay |
| **contrato-dev** | `.claude/agents/contrato-dev.md` | Solidity, Foundry, contract deployment, ABIs |
| **devops** | `.claude/agents/devops.md` | Docker, PM2, Nginx, Anvil, deploy scripts |
| **economy-analyst** | `.claude/agents/economy-analyst.md` | Economy simulation, AXF/FRJ emission vs burn, VIP revenue |
| **security-reviewer** | `.claude/agents/security-reviewer.md` | Security audit, auth checks, economic exploits |
| **game-designer** | `.claude/agents/game-designer.md` | Game mechanics, balancing, GDD updates |
| **qa-tester** | `.claude/agents/qa-tester.md` | Tests, Playwright E2E, pytest, simulation scripts |

## Context Files (for AI planning)

The taskboard uses these cached context files:

- `tools/taskboard/.context_cache/axolotto.txt` — Main project context (auto-generated, 24h TTL)
- `tools/taskboard/.context_cache/taskboard.txt` — Taskboard tool context (auto-generated, 24h TTL)

Refresh manually: `POST /api/refresh-context` on the taskboard server.

## MCP Servers

- **fog-context**: Codebase knowledge graph — `fog_brief`, `fog_lookup`, `fog_impact`
- **shadowbrain**: Cross-session memory — `memory_search`, `memory_put`
- **axolotto-kb**: Custom project knowledge — `get_architecture`, `get_economy`, `get_conventions`

See `.claude/settings.json` for MCP server configuration.

## Session Context (auto-injected)

On every session start, the following is injected via hooks:
1. `CLAUDE.md` — Architecture, stack, rules (loaded by Claude Code automatically)
2. Project brief from `.claude/context/project-brief.md`
3. Latest git log (last 5 commits) for recent change awareness

## Token-saving Tips for Agents

1. Use `fog_brief` / `fog_lookup` instead of reading files to understand structure
2. Use `memory_search` in shadowbrain before exploring — prior agents may have solved this
3. Read files with `offset`/`limit` — don't load 2000-line files whole
4. Delegate domain-specific work to the specialized agents listed above
5. After completing work, store discoveries in shadowbrain: `memory_put` with kind=`pattern`|`gotcha`|`decision`

<!-- fog-context -->
## fog-context MCP - Agent Instructions

> [!WARNING]
> **⚠️ ALL `fog_*` commands are MCP Tools.** Do NOT run them via bash/shell.

### MANDATORY PROTOCOL
1. **Call `fog_brief` First:** Always check index health.
2. **Before Editing:** Run `fog_impact({ "target": "<symbol>" })` to check blast radius.
3. **After Editing:** Run `fog_decisions` to log WHY the code was changed.

### MCP Tools
- **Orient:** `fog_domains`, `fog_lookup`
- **Understand:** `fog_inspect`, `fog_trace`
- **Verify:** `fog_impact`
- **Record:** `fog_decisions`

⚠️ **Anti-Blackbox Rule:** You MUST NOT bypass cross-validation. 
Even with a detailed prompt, ALWAYS verify real codebase state via `fog_inspect` before modifying code.

### MANDATORY: End-of-Session Context Update
After completing code changes, update if session introduced:
- New entry points → `.fog-context/security.toml` [sources]
- New DB queries or shell calls → `.fog-context/security.toml` [sinks]
- New validation functions → `.fog-context/security.toml` [sanitizers]
- New sensitive data models → `.fog-context/labels.toml` [pii]
After editing configs, run `fog_overlay` to apply to graph.


### 🔴 First-time Setup — MANDATORY Knowledge Layer Bootstrap
> fog-context indexed Layer 1 (Physical: 2872 symbols). Semantic Layers 2-4 are empty — Knowledge Score: 0/100.
> Complete these steps **once** to unlock full intelligence:

```
Step 1 - Layer 2 (Business Domains): fog_assign
Step 2 - Layer 3 (Constraints): fog_constraints
Step 3 - Layer 4 (Decisions): fog_decisions
```
<!-- /fog-context -->