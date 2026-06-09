#!/usr/bin/env python3
"""Axolotto Knowledge Base — MCP Server.

A Model Context Protocol server that gives AI agents (Claude Code, Cursor, etc.)
instant, structured knowledge about the Axolotto project. Instead of agents
spending 50K+ tokens exploring the codebase, they call tools like
`get_architecture`, `get_module`, or `search_knowledge` and get precise,
curated answers in <1K tokens.

Protocol: MCP over stdio (JSON-RPC 2.0)
Dependencies: Python 3.12+ stdlib only (no pip packages needed)

Usage:
    python3 mcp_knowledge_server.py          # run as MCP server
    python3 mcp_knowledge_server.py --test   # test knowledge base output
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# Fix Windows console encoding for --test mode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# -- Paths --------------------------------------------------------------------
REPO_ROOT = os.environ.get(
    "AXOLOTTO_REPO_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# -- Knowledge Base -----------------------------------------------------------
# This is the structured knowledge that replaces ~50K tokens of codebase
# exploration per agent session. Keep it updated as the project evolves.

KNOWLEDGE = {
    "identity": {
        "name": "Axolotto",
        "tagline": "Metaverse Lottery Game on Web3",
        "repo": REPO_ROOT,
        "branch": "develop (default), master (production)",
        "server": "tridyland (WSL + Docker + PM2 + Nginx)",
        "updated": "2026-06-05",
    },
    "architecture": {
        "overview": (
            "Axolotto is a Web3 metaverse lottery game with 4 main areas: "
            "backend (FastAPI+SQLModel+PostgreSQL), frontend (Next.js 16+React 19+Tailwind 4), "
            "contracts (Solidity+Foundry, 14 contracts), and tools (self-hosted AI Kanban taskboard). "
            "The app runs on a single server (tridyland) with Docker for backend/DB/Anvil, "
            "PM2 for frontend, and Nginx as reverse proxy."
        ),
        "layers": {
            "backend": {
                "path": "backend/",
                "stack": "FastAPI (async) + SQLModel ORM + Alembic + Web3.py + Python 3.12",
                "runtime": "Docker container 'backend_axolotto' on port 8001",
                "database": "PostgreSQL 16 in Docker, exposed on 127.0.0.1:5433",
                "auth": "Privy JWT — verify X-Privy-Token header before mutating state",
                "blockchain": "Web3.py → Anvil (localhost:8545) or Plasma Testnet (chain 9746)",
                "key_dirs": {
                    "api/v1/endpoints/": "23 route modules (bank, game, multiplayer, shop, checkout, incubation, codes, market, ranking, rewards, admin, user, metadata, board, f2p, tutorial, whitelist, events, legacy, leonardo, cave_expansion, dev, admin_events)",
                    "services/": "28 service modules (bank, game_logic, web3, shop, checkout, multiplayer, incubation, vip, rarity, promo, user, admin, board, capsule, cave, dialogue_engine, drop, f2p, forge, imprinting, manual_game, npc, pila, sal, tutorial)",
                    "models/": "8 model modules (economy, user, axolotito, board, items, promo, lobby_models, manual_mode_event)",
                    "core/": "Configuration: VIP tiers, BLOCKCHAIN_MODE, economy constants, Privy JWT auth",
                },
            },
            "frontend": {
                "path": "frontend/",
                "stack": "Next.js 16.2 (App Router) + React 19 + TypeScript 5 + Tailwind CSS 4",
                "runtime": "PM2 on port 3000",
                "auth": "@privy-io/react-auth — social login + self-custodial wallets",
                "web3": "Viem 2.47 (NO ethers.js) — createPublicClient/createWalletClient",
                "payments": "MoonPay widget for USDC onramp",
                "key_files": {
                    "app/page.tsx": "Main game UI, tab switcher, screen routing",
                    "app/layout.tsx": "Root layout: PrivyProvider, RealtimeContext, ToastContext",
                    "components/PlayMode.tsx": "Core lottery gameplay",
                    "components/ui/LoteriaBoard.tsx": "4×4 card grid renderer",
                    "components/BoardEditor.tsx": "Custom board creation/editing",
                    "components/Store.tsx": "In-game store (boosters, items, currency)",
                    "components/Inventory.tsx": "Player inventory management",
                    "components/MultiplayerLobby.tsx": "Room browser, create/join",
                    "components/CryptoCheckout.tsx": "MoonPay onramp integration",
                    "components/MarketP2P.tsx": "Peer-to-peer marketplace",
                    "components/VipModal.tsx": "VIP tier purchase/benefits",
                    "components/Gashapon.tsx": "Loot box/gashapon opening",
                    "components/Rankings.tsx": "Leaderboards display",
                    "components/Santuario.tsx": "Axolotito sanctuary/collection",
                    "components/CodeEntryPanel.tsx": "Promo code redemption UI",
                    "hooks/useBlockchainEvents.ts": "On-chain event listeners",
                    "hooks/useMoonPayWidget.ts": "MoonPay integration hook",
                },
            },
            "contracts": {
                "path": "contracts/",
                "stack": "Solidity + Foundry (forge, anvil, cast)",
                "networks": "Anvil local (chain 31337) / Plasma Testnet (chain 9746)",
                "contracts": {
                    "Frijolito.sol": "FRJ token (ERC-20) — minting, burning, transfers",
                    "Axoficha.sol": "AXF token (ERC-20) — minting, burning, transfers",
                    "Webitos.sol": "Egg NFTs (ERC-721) — hatching triggers",
                    "Axolotitos.sol": "Axolotito NFTs with on-chain DNA encoding",
                    "CartasLoteria.sol": "Individual lottery card NFTs (mint, burn)",
                    "TablasLoteria.sol": "Lottery board management, escrow for rewards",
                    "Sobrecito.sol": "Booster pack minting with rarity probabilities",
                    "Consumables.sol": "In-game consumable item tracking",
                    "GameController.sol": "Central orchestrator: game create, resolve, payout",
                    "Frijolito.sol": "FRJ secondary logic, staking hooks",
                    "Axoficha.sol": "AXF primary logic, staking hooks",
                    "Counter.sol": "Test/development counter",
                },
                "deploy": "contracts/script/Deploy.s.sol (Foundry script)",
                "tests": "contracts/test/GameContracts.t.sol",
            },
            "taskboard": {
                "path": "tools/taskboard/",
                "stack": "Python 3.12 stdlib (http.server) + vanilla JS/HTML/CSS + SQLite",
                "note": "SELF-CONTAINED TOOL — changes stay in tools/taskboard/",
                "key_files": {
                    "server.py": "HTTP server (main entry point)",
                    "routes.py": "REST API routes (tasks CRUD, AI triggers, git ops)",
                    "db.py": "SQLite/JSON persistence layer",
                    "ai_router.py": "Multi-provider AI (Claude + DeepClaude via CLI)",
                    "agent_runner.py": "Agent spawn, git worktree isolation, queue system",
                    "task_lifecycle.py": "State machine: wishes→concepts→planning→doing→review→done",
                    "project_context.py": "Rich semantic context generator",
                    "mcp_knowledge_server.py": "THIS FILE — MCP knowledge server",
                    "SKILL.md": "Agent skill — taskboard workflow for Claude/DeepClaude/AGY",
                    "index.html": "Single-page Kanban board UI",
                    "app.js": "Main app logic, WebSocket client",
                },
            },
        },
    },
    "economy": {
        "currencies": {
            "AXF": {
                "name": "Axofichas",
                "formerly": "AXG / Axogemas",
                "type": "Primary coin (ERC-20)",
                "contract": "Axoficha.sol",
            },
            "FRJ": {
                "name": "Frijolitos",
                "formerly": "GAL / Gemas Alga",
                "type": "Secondary coin (ERC-20)",
                "contract": "Frijolito.sol",
            },
        },
        "prices": {
            "easy_game": "10 AXF",
            "hard_game_5_boards": "50 AXF",
            "booster_pure_cheap": "60 AXF + 800 FRJ",
            "booster_regular": "100 AXF + 1300 FRJ",
            "board_random": "25 FRJ",
            "board_custom": "50 FRJ",
            "board_dissolution": "50 FRJ",
        },
        "vip_tiers": {
            "coral": "100 AXF",
            "dorado": "250 AXF",
            "axolite": "500 AXF",
        },
        "axf_to_frj_packs": {
            "small": "10 AXF → 100 FRJ",
            "medium": "50 AXF → 600 FRJ",
            "large": "100 AXF → 1500 FRJ",
            "xl": "250 AXF → 4000 FRJ",
        },
        "config_file": "backend/app/core/config.py",
    },
    "conventions": {
        "commits": "Conventional Commits: feat(scope): desc | fix(scope): desc | docs: | refactor: | test: | chore:",
        "branches": "feature branches → dev (default) → master (production). NEVER push direct to master.",
        "backend_pattern": (
            "router = APIRouter() → @router.post('/path') → "
            "async def endpoint(payload: Schema, user=Depends(get_current_user)): → "
            "validate → service call → commit → return response"
        ),
        "frontend_pattern": (
            "'use client' → export default function Component() { → "
            "hooks (useState, usePrivy, custom) → handlers (async try/catch) → "
            "JSX with Tailwind classes }"
        ),
        "service_pattern": (
            "async def service_op(db: AsyncSession, user_id: UUID, ...): → "
            "SELECT FOR UPDATE where needed → business logic → "
            "db.add(ledger_entry) → await db.commit()"
        ),
    },
    "critical_rules": [
        "1. CONCURRENCY: SELECT FOR UPDATE on Wallet/Inventory before any mutation. Never trust a stale read.",
        "2. REPLAY PROTECTION: Every on-chain tx hash → ProcessedTransaction (UNIQUE). Insert BEFORE crediting.",
        "3. RANDOMNESS: random.SystemRandom() ONLY. Never random.random() or random.choice().",
        "4. LEDGER: Every balance change MUST write a TransactionLedger row. No exceptions.",
        "5. BLOCKCHAIN_MODE: Check settings.BLOCKCHAIN_MODE before choosing RPC URL or contract addresses.",
        "6. CONTRACT ADDRESSES: Always from env (NEXT_PUBLIC_*) or settings. Never hardcode.",
        "7. PRIVY AUTH: Check authenticated before any wallet or backend mutation call.",
        "8. NEVER PUSH TO MAIN/MASTER. Work on feature branches → merge to dev.",
        "9. IDEMPOTENT MIGRATIONS: DB has renamed columns. Use DO $$ blocks in Alembic.",
        "10. TASKBOARD ISOLATION: Taskboard changes stay in tools/taskboard/.",
    ],
    "active_context": {
        "sprint": "June 2026",
        "items": [
            "Currency rename in progress: AXG→AXF (Axofichas), GAL→FRJ (Frijolitos)",
            "Economy models have compatibility aliases: AxgPurchaseRecord = AxfPurchaseRecord",
            "Alembic merge migration: bb01d2e3f4a5 (two heads merged)",
            "Landing page 'Flujo Corcholata': promo code redemption flow in planning",
            "Multiplayer game rooms: stabilization in progress",
            "VIP tier economy balancing ongoing",
        ],
    },
    "env_files": {
        "backend/.env": "DB connection, BLOCKCHAIN_MODE, Privy keys, Web3 RPC URL, contract addresses",
        "frontend/.env.local": "NEXT_PUBLIC_API_URL, NEXT_PUBLIC_* contract addresses, chain ID",
        ".env": "Docker compose vars: AXO_DB_USER, AXO_DB_PASSWORD",
    },
    "endpoints_summary": {
        "bank": "Wallet balance, deposit, withdraw, dual-currency operations",
        "game": "Game lifecycle: create, play, resolve, rewards",
        "multiplayer": "Room creation, lobby, real-time game coordination",
        "shop": "Store items, boosters, currency packs",
        "checkout": "Crypto onramp / MoonPay checkout flow",
        "incubation": "Axolotito breeding, egg hatching, DNA combination",
        "board": "Lottery board CRUD, customization",
        "market": "P2P marketplace (listings, trades, offers)",
        "ranking": "Leaderboards, player rankings",
        "codes": "Promo code creation, validation, redemption",
        "user": "User profile, preferences, stats",
        "metadata": "NFT metadata generation, token URIs",
        "rewards": "Daily rewards, achievement payouts",
        "admin": "Admin panel data, management endpoints",
        "f2p": "Free-to-play features, daily free games",
        "tutorial": "Tutorial state, onboarding progress",
        "whitelist": "Feature-gating, beta access control",
    },
}


# -- MCP Protocol Implementation ---------------------------------------------

def _log(msg: str):
    """Log to stderr (stdout is the MCP transport)."""
    print(f"[axolotto-kb] {msg}", file=sys.stderr, flush=True)


def _rpc_response(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _rpc_error(id_, code: int, message: str):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


# -- Tool Implementations -----------------------------------------------------

def tool_get_architecture(args: dict) -> str:
    """Return full architecture overview."""
    arch = KNOWLEDGE["architecture"]
    out = ["# Axolotto Architecture\n", arch["overview"], "\n"]

    for name, info in arch["layers"].items():
        out.append(f"## {name.upper()} — {info['path']}")
        out.append(f"Stack: {info['stack']}")
        out.append(f"Runtime: {info.get('runtime', 'N/A')}")
        if "note" in info:
            out.append(f"⚠ {info['note']}")
        if "key_files" in info:
            out.append("\nKey files:")
            for fname, purpose in info["key_files"].items():
                out.append(f"  {info['path']}{fname} — {purpose}")
        elif "key_dirs" in info:
            out.append("\nKey directories:")
            for dname, desc in info["key_dirs"].items():
                out.append(f"  {info['path']}{dname} — {desc}")
        if "contracts" in info:
            out.append("\nContracts:")
            for cname, cpurpose in info["contracts"].items():
                out.append(f"  {cname} — {cpurpose}")
        out.append("")

    return "\n".join(out)


def tool_get_module(args: dict) -> str:
    """Return detailed info about a specific module."""
    module = (args.get("module") or args.get("name") or "").lower().strip()
    if not module:
        return "Error: specify a module name. Use 'backend', 'frontend', 'contracts', 'taskboard', or an endpoint name like 'bank', 'game', etc."

    # Check layers
    layers = KNOWLEDGE["architecture"]["layers"]
    if module in layers:
        info = layers[module]
        out = [f"# {module.upper()}\n"]
        for key, val in info.items():
            if key in ("key_files", "key_dirs"):
                out.append("## Files:")
                for name, desc in val.items():
                    out.append(f"  {name} — {desc}")
            elif key == "contracts":
                out.append("## Contracts:")
                for name, desc in val.items():
                    out.append(f"  {name} — {desc}")
            elif isinstance(val, dict):
                out.append(f"## {key}:")
                for k, v in val.items():
                    out.append(f"  {k}: {v}")
            else:
                out.append(f"{key}: {val}")
        return "\n".join(out)

    # Check endpoints
    eps = KNOWLEDGE.get("endpoints_summary", {})
    if module in eps:
        return f"# {module} endpoint\n{eps[module]}\nPath: backend/app/api/v1/endpoints/{module}.py"

    # Search contracts
    contracts = layers.get("contracts", {}).get("contracts", {})
    for cname, cdesc in contracts.items():
        if module in cname.lower():
            return f"# {cname}\n{cdesc}\nPath: contracts/src/{cname}"

    return f"Module '{module}' not found. Try: backend, frontend, contracts, taskboard, bank, game, multiplayer, shop, checkout, incubation, market, codes, economy, vip"


def tool_get_economy(args: dict) -> str:
    """Return economy constants, VIP tiers, and pricing."""
    econ = KNOWLEDGE["economy"]
    out = ["# Axolotto Economy\n"]

    out.append("## Currencies")
    for code, info in econ["currencies"].items():
        out.append(f"  {code} = {info['name']} (formerly {info['formerly']}) — {info['type']}")

    out.append("\n## Prices")
    for name, price in econ["prices"].items():
        out.append(f"  {name}: {price}")

    out.append("\n## VIP Tiers")
    for tier, cost in econ["vip_tiers"].items():
        out.append(f"  {tier}: {cost}")

    out.append("\n## AXF → FRJ Packs")
    for size, rate in econ["axf_to_frj_packs"].items():
        out.append(f"  {size}: {rate}")

    out.append(f"\nConfig file: {econ['config_file']}")
    return "\n".join(out)


def tool_get_conventions(args: dict) -> str:
    """Return code conventions, patterns, and critical rules."""
    conv = KNOWLEDGE["conventions"]
    rules = KNOWLEDGE["critical_rules"]
    out = ["# Axolotto Conventions & Rules\n"]

    out.append("## Commit & Branch Conventions")
    out.append(f"  {conv['commits']}")
    out.append(f"  {conv['branches']}")

    out.append("\n## Code Patterns")
    out.append(f"\n### Backend Endpoint\n  {conv['backend_pattern']}")
    out.append(f"\n### Frontend Component\n  {conv['frontend_pattern']}")
    out.append(f"\n### Service Layer\n  {conv['service_pattern']}")

    out.append("\n## Critical Rules (breaking any = production issue)")
    for rule in rules:
        out.append(f"  {rule}")

    return "\n".join(out)


def tool_get_contracts(args: dict) -> str:
    """Return smart contract details."""
    contracts = KNOWLEDGE["architecture"]["layers"]["contracts"]
    out = ["# Smart Contracts\n"]
    out.append(f"Stack: {contracts['stack']}")
    out.append(f"Networks: {contracts['networks']}")
    out.append(f"Deploy: {contracts['deploy']}")
    out.append(f"Tests: {contracts['tests']}")
    out.append("\n## Contract Files:")
    for name, desc in contracts["contracts"].items():
        out.append(f"  {name} — {desc}")
    return "\n".join(out)


def tool_get_recent_changes(args: dict) -> str:
    """Return recent git activity."""
    try:
        log = subprocess.run(
            ["git", "log", "--oneline", "-10", "--no-decorate"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=5
        )
        commits = log.stdout.strip() if log.returncode == 0 else "(git unavailable)"
    except Exception:
        commits = "(git unavailable)"

    active = KNOWLEDGE["active_context"]
    out = [
        "# Recent Activity\n",
        f"## Active Context ({active['sprint']})",
    ]
    for item in active["items"]:
        out.append(f"  • {item}")

    out.append(f"\n## Recent Commits\n  {commits}")
    return "\n".join(out)


def tool_search_knowledge(args: dict) -> str:
    """Full-text search across the entire knowledge base."""
    query = (args.get("query") or args.get("q") or "").lower().strip()
    if not query:
        return "Error: specify a search query."

    # Flatten and search the knowledge base
    results = []

    def _search_dict(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                new_path = f"{path} > {k}" if path else k
                if query in k.lower():
                    if isinstance(v, str) and len(v) < 300:
                        results.append(f"{new_path}: {v}")
                    else:
                        results.append(f"{new_path} (section match)")
                if isinstance(v, str) and query in v.lower() and query not in k.lower():
                    snippet = v[:300] + ("..." if len(v) > 300 else "")
                    results.append(f"{new_path}: {snippet}")
                elif isinstance(v, (dict, list)):
                    _search_dict(v, new_path)
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, str) and query in item.lower():
                    results.append(f"{path}: {item[:300]}")
                elif isinstance(item, dict):
                    _search_dict(item, path)

    _search_dict(KNOWLEDGE)

    if not results:
        return f"No results for '{query}'. Try: architecture, economy, contracts, bank, game, multiplayer, shop, conventions, rules, currency, AXF, FRJ, VIP"

    out = [f"# Search: '{query}' ({len(results)} results)\n"]
    for i, r in enumerate(results[:15]):
        out.append(f"{i+1}. {r}")
    if len(results) > 15:
        out.append(f"\n... and {len(results) - 15} more results. Narrow your query.")
    return "\n".join(out)


# -- Tool Registry ------------------------------------------------------------

TOOLS = {
    "get_architecture": {
        "description": "Get the full Axolotto architecture overview: all layers, key files, contracts, and infrastructure. Use this FIRST when starting any task to understand the project structure without reading dozens of files.",
        "handler": tool_get_architecture,
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "get_module": {
        "description": "Get detailed information about a specific module. Use for: 'backend', 'frontend', 'contracts', 'taskboard', or endpoint names like 'bank', 'game', 'multiplayer', 'shop', 'checkout', 'incubation', 'market', 'codes', 'economy', 'vip'.",
        "handler": tool_get_module,
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Module name: backend, frontend, contracts, taskboard, or an endpoint name"
                }
            },
            "required": ["module"],
        },
    },
    "get_economy": {
        "description": "Get economy constants: AXF/FRJ currencies, pricing for all game actions, VIP tiers and costs, AXF→FRJ exchange packs. Use when working on any feature involving coins, purchases, rewards, or VIP.",
        "handler": tool_get_economy,
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "get_conventions": {
        "description": "Get code conventions, critical rules, commit format, branch strategy, and code patterns for backend, frontend, and services. Use BEFORE writing any code to ensure it follows project standards.",
        "handler": tool_get_conventions,
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "get_contracts": {
        "description": "Get all smart contract details: 14 contracts with purposes, stack (Solidity+Foundry), networks, deployment scripts, and test files.",
        "handler": tool_get_contracts,
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "get_recent_changes": {
        "description": "Get the active sprint context and recent git commits. Use at the start of a session to understand what's currently being worked on and what changed recently.",
        "handler": tool_get_recent_changes,
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "search_knowledge": {
        "description": "Full-text search across the entire Axolotto knowledge base. Find anything: modules, contracts, endpoints, conventions, economy values, architecture decisions. Much faster than grepping the codebase.",
        "handler": tool_search_knowledge,
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query — can be a module name, concept, keyword, or question"
                }
            },
            "required": ["query"],
        },
    },
}


# -- MCP Server Main Loop -----------------------------------------------------

def _send(msg: dict):
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle_request(req: dict) -> dict | None:
    """Process a single JSON-RPC request. Returns response or None for notifications."""
    method = req.get("method", "")
    id_ = req.get("id")
    params = req.get("params", {})

    # -- Lifecycle methods --
    if method == "initialize":
        return _rpc_response(id_, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "axolotto-kb",
                "version": "1.0.0",
            },
        })

    if method == "notifications/initialized":
        return None  # No response for notifications

    if method == "ping":
        return _rpc_response(id_, {})

    # -- Tool listing --
    if method == "tools/list":
        tools_list = []
        for name, meta in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["inputSchema"],
            })
        return _rpc_response(id_, {"tools": tools_list})

    # -- Tool call --
    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        tool = TOOLS.get(tool_name)
        if not tool:
            return _rpc_error(id_, -32601, f"Unknown tool: {tool_name}")

        try:
            result_text = tool["handler"](tool_args)
            return _rpc_response(id_, {
                "content": [{"type": "text", "text": result_text}],
            })
        except Exception as e:
            return _rpc_error(id_, -32603, f"Tool error: {e}")

    # -- Unknown method --
    return _rpc_error(id_, -32601, f"Unknown method: {method}")


def serve():
    """Run the MCP server over stdio."""
    _log("Axolotto Knowledge Base MCP server starting...")
    _log(f"Repo root: {REPO_ROOT}")
    _log(f"Registered tools: {', '.join(TOOLS.keys())}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            _log(f"Invalid JSON: {e}")
            continue

        resp = handle_request(req)
        if resp is not None:
            _send(resp)


# -- CLI ----------------------------------------------------------------------

def _test():
    """Test the knowledge base by calling each tool and printing results."""
    print("=" * 60)
    print("AXOLOTTO KNOWLEDGE BASE — Test Run")
    print("=" * 60)

    for name, meta in TOOLS.items():
        print(f"\n{'-' * 40}")
        print(f"Tool: {name}")
        print(f"Description: {meta['description'][:100]}...")
        print(f"{'-' * 40}")

        try:
            # Use appropriate test args
            if name == "get_module":
                result = meta["handler"]({"module": "backend"})
            elif name == "search_knowledge":
                result = meta["handler"]({"query": "wallet"})
            else:
                result = meta["handler"]({})

            # Truncate for display
            lines = result.split("\n")
            if len(lines) > 30:
                print("\n".join(lines[:30]))
                print(f"... ({len(lines)} total lines, {len(result)} chars)")
            else:
                print(result)
            print(f"\n[OK] {name}: {len(lines)} lines, {len(result)} chars")
        except Exception as e:
            print(f"[ERR] {name} error: {e}")

    print(f"\n{'=' * 60}")
    print("All tools tested. Total KB size: ~{:,} chars".format(
        len(json.dumps(KNOWLEDGE, indent=2))
    ))
    print(f"Estimated token savings per agent session: ~40-50K tokens")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        serve()
