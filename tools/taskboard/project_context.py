#!/usr/bin/env python3
from __future__ import annotations
"""Rich project context generator for AI agent prompts.

Replaces the old flat-directory-listing approach with structured,
semantic knowledge that dramatically reduces token waste during
AI planning and agent execution phases.

Design principle: every token of context should carry semantic meaning.
A flat list of 60 directories tells the AI almost nothing. A curated
list of 30 key files WITH their purposes tells the AI exactly what it
needs to start working.
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ── Cache configuration ──────────────────────────────────────────────────────
CONTEXT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".context_cache")
CONTEXT_CACHE_TTL_SECONDS = int(os.environ.get("TASKBOARD_CONTEXT_TTL", str(24 * 3600)))


def _cache_path(scope: str) -> str:
    os.makedirs(CONTEXT_CACHE_DIR, exist_ok=True)
    return os.path.join(CONTEXT_CACHE_DIR, f"{scope}.txt")


def load_cached(scope: str) -> str | None:
    """Return cached context if fresh, otherwise None."""
    path = _cache_path(scope)
    try:
        if not os.path.exists(path):
            return None
        if time.time() - os.path.getmtime(path) > CONTEXT_CACHE_TTL_SECONDS:
            return None
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content if content.strip() else None
    except OSError:
        return None


def save_cache(scope: str, content: str):
    path = _cache_path(scope)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"  ContextCache: Failed to write '{scope}': {e}", file=sys.stderr)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _run(cmd, timeout=5):
    """Run a shell command, return stdout or empty string."""
    try:
        r = subprocess.run(cmd, shell=True, cwd=REPO_ROOT,
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _git_log(n=5):
    """Last N commits, one-liner format."""
    out = _run(f'git log --oneline -{n} --no-decorate', timeout=3)
    return out if out else "(git unavailable)"


def _git_branch():
    out = _run("git rev-parse --abbrev-ref HEAD", timeout=2)
    return out if out else "unknown"


def _file_exists(rel_path: str) -> bool:
    return os.path.isfile(os.path.join(REPO_ROOT, rel_path))


# ── Semantic context builders ────────────────────────────────────────────────

def _build_axolotto_context() -> str:
    """Rich semantic context for the main Axolotto project."""
    lines = []

    # ── Header & Identity ──
    lines.append("=" * 70)
    lines.append("AXOLOTTO PROJECT CONTEXT — AI Agent Knowledge Base")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Branch: {_git_branch()}")
    lines.append("=" * 70)
    lines.append("")

    # ── 1. Architecture Overview ──
    lines.append("## 1. ARCHITECTURE OVERVIEW")
    lines.append("")
    lines.append("Axolotto is a Web3 metaverse lottery game with 4 main areas:")
    lines.append("")
    lines.append("  backend/     — FastAPI + SQLModel + PostgreSQL 16  (Docker :8001)")
    lines.append("                Auth: Privy JWT (X-Privy-Token header)")
    lines.append("                Blockchain: Web3.py -&gt; Anvil/Plasma Testnet")
    lines.append("                Key services: bank, game, multiplayer, shop, checkout, incubation")
    lines.append("")
    lines.append("  frontend/    — Next.js 16.2 App Router + React 19 + Tailwind CSS 4 (PM2 :3000)")
    lines.append("                Auth: @privy-io/react-auth (social login + self-custodial wallets)")
    lines.append("                Web3: Viem 2.47 (NO ethers.js)")
    lines.append("                Payments: MoonPay widget for USDC onramp")
    lines.append("                Key components: PlayMode, LoteriaBoard, Store, MultiplayerLobby,")
    lines.append("                Criadero, Santuario, Inventory, VipModal, CryptoCheckout, MarketP2P")
    lines.append("")
    lines.append("  contracts/   — Solidity + Foundry (Anvil :8545 local / Plasma Testnet chain 9746)")
    lines.append("                14 contracts: Frijolito(FRJ), Axoficha(AXF), Webitos(ERC-721),")
    lines.append("                Axolotitos(DNA), CartasLoteria, TablasLoteria(escrow),")
    lines.append("                Boosters, Consumables, GameController(orchestrator), Frijolito")
    lines.append("")
    lines.append("  tools/       — Self-hosted AI Kanban taskboard (Python stdlib + vanilla JS)")
    lines.append("                Path: tools/taskboard/ (SELF-CONTAINED, do not touch other areas)")
    lines.append("")

    # ── 2. Currency System ──
    lines.append("## 2. CURRENCY SYSTEM (renamed June 2026)")
    lines.append("")
    lines.append("  AXF = Axofichas  (formerly AXG/Axogemas)  — primary coin, ERC-20")
    lines.append("  FRJ = Frijolitos (formerly GAL/Gemas Alga) — secondary coin, ERC-20")
    lines.append("")
    lines.append("  Key prices (from backend/app/core/config.py):")
    lines.append("    Easy game (classic):      10 AXF")
    lines.append("    Hard game / 5 boards:     50 AXF")
    lines.append("    Booster pure (cheap):     60 AXF + 800 FRJ")
    lines.append("    Booster regular:         100 AXF + 1300 FRJ")
    lines.append("    Board creation (random):  25 FRJ")
    lines.append("    Board creation (custom):  50 FRJ")
    lines.append("    Board dissolution:        50 FRJ")
    lines.append("")
    lines.append("  VIP tiers: coral (100 AXF), dorado (250 AXF), axolite (500 AXF)")
    lines.append("  AXF-&gt;FRJ packs: 10-&gt;100, 50-&gt;600, 100-&gt;1500, 250-&gt;4000")
    lines.append("")

    # ── 3. Backend Structure ──
    lines.append("## 3. BACKEND — Key Files & Purposes")
    lines.append("")
    lines.append("  [API Endpoints] (backend/app/api/v1/endpoints/)")
    lines.append("    bank.py         — Wallet balance, deposit, withdraw, dual-currency ops")
    lines.append("    game.py         — Game lifecycle: create, play, resolve, rewards")
    lines.append("    multiplayer.py  — Room creation, lobby, real-time game coordination")
    lines.append("    shop.py         — Store items, boosters, currency packs")
    lines.append("    checkout.py     — Crypto onramp / MoonPay checkout flow")
    lines.append("    incubation.py   — Axolotito breeding, egg hatching, DNA combination")
    lines.append("    board.py        — Lottery board CRUD, customization")
    lines.append("    market.py       — P2P marketplace (listings, trades, offers)")
    lines.append("    ranking.py      — Leaderboards, player rankings")
    lines.append("    codes.py        — Promo code creation, validation, redemption")
    lines.append("    user.py         — User profile, preferences, stats")
    lines.append("    metadata.py     — NFT metadata generation, token URIs")
    lines.append("    rewards.py      — Daily rewards, achievement payouts")
    lines.append("    admin.py        — Admin panel data, management endpoints")
    lines.append("    f2p.py          — Free-to-play features, daily free games")
    lines.append("    tutorial.py     — Tutorial state, onboarding progress")
    lines.append("    whitelist.py    — Feature-gating, beta access control")
    lines.append("")
    lines.append("  [Services] (backend/app/services/)")
    lines.append("    bank_service.py        — Wallet logic, balance checks, ledger writes")
    lines.append("    game_logic.py          — Core lottery game rules engine")
    lines.append("    web3_service.py        — Blockchain RPC, contract interactions, tx tracking")
    lines.append("    shop_service.py        — Inventory management, purchase validation")
    lines.append("    checkout_service.py    — Crypto payment processing flow")
    lines.append("    multiplayer_service.py — Room state machine, turn management, WebSocket sync")
    lines.append("    incubation_service.py  — Breeding logic, DNA mixing, rarity calculation")
    lines.append("    vip_scheduler.py       — VIP tier checks, benefit distribution")
    lines.append("    rarity_service.py      — Item/axolotito rarity tiers and probabilities")
    lines.append("    promo_service.py       — Promo code validation, kit granting")
    lines.append("    user_service.py        — Profile management, stats aggregation")
    lines.append("")
    lines.append("  [Models] (backend/app/models/)")
    lines.append("    economy.py   — AxfPurchaseRecord, TransactionLedger, TreasuryVault, JackpotVault")
    lines.append("    user.py      — User, Wallet (with balance fields)")
    lines.append("    axolotito.py — Axolotito NFT data, DNA, stats")
    lines.append("    board.py     — PlayerBoard, lottery board config")
    lines.append("    items.py     — Inventory items, consumables, boosters")
    lines.append("    promo.py     — PromoCode, PromoBatch")
    lines.append("    lobby_models.py — GameRoom, room state, player slots")
    lines.append("")

    # ── 4. Frontend Structure ──
    lines.append("## 4. FRONTEND — Key Files & Purposes")
    lines.append("")
    lines.append("  [Pages & Layout]")
    lines.append("    frontend/app/layout.tsx  — Root layout: PrivyProvider, RealtimeContext, ToastContext")
    lines.append("    frontend/app/page.tsx    — Main game UI: tab switcher, screen routing")
    lines.append("")
    lines.append("  [Core Components] (frontend/components/)")
    lines.append("    PlayMode.tsx          — Core lottery gameplay (board selection, card draw)")
    lines.append("    LoteriaBoard.tsx      — 4×4 card grid renderer (ui/LoteriaBoard.tsx)")
    lines.append("    BoardEditor.tsx       — Custom board creation/editing UI")
    lines.append("    Store.tsx             — In-game store (boosters, items, currency packs)")
    lines.append("    Inventory.tsx         — Player inventory management")
    lines.append("    MultiplayerLobby.tsx  — Room browser, create/join flow")
    lines.append("    Criadero/             — Breeding/incubation screens")
    lines.append("    Santuario.tsx         — Axolotito sanctuary/collection view")
    lines.append("    VipModal.tsx          — VIP tier purchase/benefits modal")
    lines.append("    CryptoCheckout.tsx    — MoonPay onramp integration")
    lines.append("    MarketP2P.tsx         — Peer-to-peer marketplace UI")
    lines.append("    Rankings.tsx          — Leaderboards display")
    lines.append("    Gashapon.tsx          — Gashapon/loot box opening")
    lines.append("    CodeEntryPanel.tsx    — Promo code redemption UI")
    lines.append("")
    lines.append("  [Hooks] (frontend/hooks/)")
    lines.append("    useBlockchainEvents.ts — Listen to on-chain contract events")
    lines.append("    useMoonPayWidget.ts    — MoonPay integration hook")
    lines.append("    useInventory.ts        — Inventory state management")
    lines.append("    useStore.ts            — Store state, purchase flow")
    lines.append("    useVip.ts              — VIP status, tier checks")
    lines.append("    useTabVisibility.ts    — Tab focus/visibility tracking")
    lines.append("")

    # ── 5. Contracts ──
    lines.append("## 5. SMART CONTRACTS (contracts/src/)")
    lines.append("")
    lines.append("  Frijolito.sol       — FRJ token (ERC-20), minting, burning")
    lines.append("  Axoficha.sol        — AXF token (ERC-20), minting, burning")
    lines.append("  Webitos.sol        — Egg NFTs (ERC-721), hatching triggers")
    lines.append("  Axolotitos.sol     — Axolotito NFTs with on-chain DNA encoding")
    lines.append("  CartasLoteria.sol  — Individual lottery card NFTs (mint, burn)")
    lines.append("  TablasLoteria.sol  — Lottery board management, escrow for rewards")
    lines.append("  Sobrecito.sol       — Booster pack minting with rarity probabilities")
    lines.append("  Consumables.sol    — In-game consumable item tracking on-chain")
    lines.append("  GameController.sol — Central orchestrator: game creation, resolution, payouts")
    lines.append("  Frijolito.sol      — FRJ secondary logic, staking hooks")
    lines.append("  Axoficha.sol       — AXF primary logic, staking hooks")
    lines.append("  Counter.sol        — Test/development counter contract")
    lines.append("")
    lines.append("  Deployment: contracts/script/Deploy.s.sol (Foundry script)")
    lines.append("  Tests:      contracts/test/GameContracts.t.sol")
    lines.append("")

    # ── 6. Critical Rules ──
    lines.append("## 6. CRITICAL RULES (violating these breaks production)")
    lines.append("")
    lines.append("  1. CONCURRENCY: SELECT FOR UPDATE on Wallet/Inventory before any mutation.")
    lines.append("     Never trust a stale read — pessimistic locking is mandatory.")
    lines.append("  2. REPLAY PROTECTION: Every on-chain tx hash -&gt; ProcessedTransaction (UNIQUE).")
    lines.append("     Insert BEFORE crediting. If insert fails, tx was already processed — skip.")
    lines.append("  3. RANDOMNESS: random.SystemRandom() ONLY. Never random.random()/choice().")
    lines.append("  4. LEDGER: Every balance change MUST write a TransactionLedger row. No exceptions.")
    lines.append("  5. BLOCKCHAIN_MODE: Check settings.BLOCKCHAIN_MODE before choosing RPC/addresses.")
    lines.append("  6. CONTRACT ADDRESSES: Always from env (NEXT_PUBLIC_*) or settings. Never hardcode.")
    lines.append("  7. PRIVY AUTH: Check authenticated before any wallet/backend mutation.")
    lines.append("  8. NEVER PUSH TO MAIN/MASTER. Work on feature branches -&gt; merge to dev.")
    lines.append("  9. CONVENTIONAL COMMITS: feat(scope): desc | fix(scope): desc | docs: | refactor:")
    lines.append(" 10. IDEMPOTENT MIGRATIONS: DB has renamed columns. Use DO $$ blocks in Alembic.")
    lines.append("")

    # ── 7. Active Context ──
    lines.append("## 7. ACTIVE CONTEXT (current sprint / recent changes)")
    lines.append("")
    lines.append("  Currency rename in progress: AXG-&gt;AXF (Axofichas), GAL-&gt;FRJ (Frijolitos)")
    lines.append("  Economy models have compatibility aliases: AxgPurchaseRecord = AxfPurchaseRecord")
    lines.append("  Alembic merge migration: bb01d2e3f4a5 (two heads merged)")
    lines.append("  Landing page 'Flujo Corcholata' in planning: promo code redemption flow")
    lines.append("  Multiplayer game rooms: stabilization in progress")
    lines.append("")
    lines.append(f"  Recent commits (on {_git_branch()}):")
    for commit_line in _git_log(5).split("\n"):
        if commit_line.strip():
            lines.append(f"    {commit_line.strip()}")
    lines.append("")

    # ── 8. Directory Structure (compact) ──
    lines.append("## 8. DIRECTORY MAP (for file location reference)")
    lines.append("")
    dirs = _run(
        "find . -maxdepth 3 -type d "
        "-not -path './.git/*' -not -path './node_modules/*' "
        "-not -path './.venv/*' -not -path './.next/*' "
        "-not -path './frontend/node_modules/*' -not -path './frontend/.next/*' "
        "-not -path '*/__pycache__/*' -not -path '*/agent_logs/*' "
        "-not -path './.claude/skills/*' "
        "| sort | head -80",
        timeout=5
    )
    if dirs:
        for d in dirs.split("\n"):
            d = d.strip()
            if d and d != ".":
                lines.append(f"  {d}")
    lines.append("")

    # ── 9. Common Patterns ──
    lines.append("## 9. COMMON PATTERNS (code conventions)")
    lines.append("")
    lines.append("  Backend endpoint pattern:")
    lines.append("    router = APIRouter()")
    lines.append("    @router.post('/path')")
    lines.append("    async def endpoint(payload: Schema, user=Depends(get_current_user)):")
    lines.append("    -&gt; validate -&gt; service call -&gt; commit -&gt; return response")
    lines.append("")
    lines.append("  Frontend component pattern:")
    lines.append("    'use client'")
    lines.append("    export default function Component() {")
    lines.append("    -&gt; hooks (useState, usePrivy, custom hooks)")
    lines.append("    -&gt; handlers (async with try/catch)")
    lines.append("    -&gt; JSX with Tailwind classes")
    lines.append("    }")
    lines.append("")
    lines.append("  Service layer pattern:")
    lines.append("    async def service_operation(db: AsyncSession, user_id: UUID, ...):")
    lines.append("    -&gt; SELECT FOR UPDATE where needed")
    lines.append("    -&gt; business logic")
    lines.append("    -&gt; db.add(ledger_entry)")
    lines.append("    -&gt; await db.commit()")
    lines.append("")

    # ── 10. Key Environment Variables ──
    lines.append("## 10. KEY ENVIRONMENT FILES")
    lines.append("")
    lines.append("  backend/.env      — DB connection, BLOCKCHAIN_MODE, Privy keys, Web3 RPC")
    lines.append("  frontend/.env.local — NEXT_PUBLIC_API_URL, contract addresses, chain ID")
    lines.append("  .env              — Docker compose vars (AXO_DB_USER, AXO_DB_PASSWORD)")
    lines.append("")

    lines.append("=" * 70)
    lines.append("END OF PROJECT CONTEXT — This knowledge replaces ~50K tokens of exploration")
    lines.append("=" * 70)

    return "\n".join(lines)


def _build_taskboard_context() -> str:
    """Rich semantic context for the taskboard tool itself."""
    lines = [
        "=" * 60,
        "TASKBOARD TOOL CONTEXT — Self-Contained AI Kanban",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "=" * 60,
        "",
        "## Stack",
        "  Python 3.12 stdlib (http.server) + vanilla JS/HTML/CSS + SQLite",
        "  Path: tools/taskboard/ (SELF-CONTAINED — changes stay here)",
        "",
        "## Architecture",
        "  server.py          — HTTP server (main entry point, port from env)",
        "  routes.py          — REST API routes (tasks CRUD, AI triggers, git ops)",
        "  db.py              — SQLite persistence layer (tasks.json in dev, SQLite in prod)",
        "  ai_router.py       — Multi-provider AI (Claude + DeepClaude via CLI binaries)",
        "  agent_runner.py    — Agent spawn, git worktree isolation, queue management",
        "  task_lifecycle.py  — State machine: wishes-&gt;concepts-&gt;planning-&gt;doing-&gt;review-&gt;done",
        "  rate_limiter.py    — Rate limit tracking per AI provider",
        "  project_context.py — Rich semantic context generator (THIS FILE)",
        "",
        "## Frontend (tools/taskboard/)",
        "  index.html         — Single-page Kanban board UI",
        "  app.js             — Main app logic, WebSocket client, state management",
        "  styles.css         — All styling (dark theme, gradients, animations)",
        "  modules/           — JS modules: task-card, drag-drop, modal, terminals, etc.",
        "",
        "## Key Rules for Taskboard Work",
        "  1. ALL changes stay in tools/taskboard/ — NEVER touch backend/frontend/contracts",
        "  2. Taskboard uses Python stdlib + vanilla JS — NO frameworks allowed",
        "  3. AI providers: Claude CLI (anthropic) + DeepClaude (deepseek via claude CLI)",
        "  4. Agents run in isolated git worktrees under ../.axolotto_worktrees/",
        "  5. Context cache TTL: 24h — refresh with POST /api/refresh-context",
        "",
        "## AI Processing Pipeline",
        "  wishes/concepts -&gt; planning: AI generates full plan (SYSTEM_PLANNING prompt)",
        "  planning -&gt; doing: Agent spawned in isolated worktree",
        "  doing -&gt; review: Git diff -&gt; AI review (SYSTEM_REVIEW prompt)",
        "  review -&gt; done: Git merge to base branch",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


# ── Public API ───────────────────────────────────────────────────────────────

def generate(scope: str) -> str:
    """Generate rich semantic project context for the given scope.

    Args:
        scope: 'axolotto' (main project) or 'taskboard' (the tool itself)

    Returns:
        Multi-line string with structured, semantic project knowledge
        designed to give AI agents everything they need to start working
        without re-discovering the codebase from scratch.
    """
    if scope == "taskboard":
        return _build_taskboard_context()
    return _build_axolotto_context()


def get_context(scope: str) -> str:
    """Return cached context for *scope*, regenerating if expired/missing.

    This is the single entry point used by ai_router.py and agent_runner.py.
    """
    cached = load_cached(scope)
    if cached:
        return cached
    content = generate(scope)
    if content:
        save_cache(scope, content)
    return content


def refresh(scope: str | None = None) -> dict:
    """Force-regenerate context cache. Returns status dict."""
    scopes = [scope] if scope else ["axolotto", "taskboard"]
    results = []
    for s in scopes:
        content = generate(s)
        if content:
            save_cache(s, content)
            results.append({"scope": s, "size": len(content), "ok": True})
        else:
            results.append({"scope": s, "ok": False, "error": "empty content"})
    return {"scopes": results, "ok": all(r["ok"] for r in results)}
