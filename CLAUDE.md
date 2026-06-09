> **Wiki / Onboarding rápido**: Leer `wiki/00-INDEX.md` para un mapa del sistema en <400 tokens antes de explorar el codebase.

# Axolotto — Metaverse Lottery Game

Web3-based lottery metaverse with dual-currency economy (AXF/FRJ), NFT Axolotitos, multiplayer game rooms, and a self-hosted AI Kanban taskboard.

## Architecture

```
axolotto/
├── backend/          FastAPI + SQLModel + PostgreSQL 16  (Docker, port 8001)
├── frontend/         Next.js 16 + React 19 + Tailwind 4  (PM2, port 3000)
├── contracts/        Solidity + Foundry                   (Anvil/Plasma Testnet)
├── tools/taskboard/  Python stdlib + vanilla JS Kanban    (autonomous AI agents)
└── docs/             Plans, GDD, architecture docs
```

- **Reverse proxy**: Nginx — `api.axolot.to` → localhost:8001
- **DB**: PostgreSQL in Docker, exposed on `127.0.0.1:5433`
- **Blockchain**: Local Anvil (port 8545) or Plasma Testnet (chain 9746)
- **Auth**: Privy JWT (social login + self-custodial wallets)

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (async), SQLModel ORM, Alembic, Web3.py, Python 3.12 |
| Frontend | Next.js 16.2 App Router, React 19, TypeScript 5, Tailwind CSS 4 |
| Contracts | Solidity, Foundry (forge + anvil), 14 contracts in `contracts/src/` |
| Auth | Privy (@privy-io/react-auth), JWT verification via `X-Privy-Token` |
| Web3 FE | Viem 2.47 (no ethers.js) |
| Payments | MoonPay widget for USDC onramp |
| Infra | Docker Desktop, PM2, Nginx, Windows |

## Currency

- **AXF = Axofichas** — primary coin
- **FRJ = Frijolitos** — secondary coin
- Key prices: easy game 10 AXF, hard game 50 AXF, sobrecito pure 60 AXF + 800 FRJ

## Critical Rules (ALL agents must follow)

1. **Never push to main/master** — work on feature branches, merge to `dev`
2. **Conventional Commits**: `feat(scope): desc`, `fix(scope): desc`, `docs:`, `refactor:`
3. **Backend concurrency**: always `SELECT FOR UPDATE` on Wallet/Inventory before mutation
4. **Replay protection**: insert into `ProcessedTransaction` (UNIQUE) before crediting
5. **Randomness**: `random.SystemRandom()` exclusively — never `random.random()`
6. **Contract addresses**: never hardcode — always from `NEXT_PUBLIC_*` env vars or `settings.py`
7. **Privy auth**: check `authenticated` before any wallet or backend mutation call
8. **Taskboard isolation**: taskboard changes stay in `tools/taskboard/` — never touch backend/frontend/contracts from taskboard tasks
9. **Worktrees**: agents work in isolated git worktrees under `../.axolotto_worktrees/`
10. **Do NOT start servers** from agent tasks — verify with unit tests or static analysis
11. **Changelog on merge**: every merge to `develop` MUST append an entry to `wiki/CHANGELOG.md` — automated by taskboard, but verify it ran

## Key Backend Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, startup migrations, CORS |
| `backend/app/api/v1/endpoints/bank.py` | Wallet, dual-currency operations |
| `backend/app/api/v1/endpoints/game.py` | Game lifecycle, rewards |
| `backend/app/api/v1/endpoints/multiplayer.py` | Rooms, lobby, real-time games |
| `backend/app/api/v1/endpoints/shop.py` | Store, boosters, purchases |
| `backend/app/api/v1/endpoints/checkout.py` | Crypto onramp checkout flow |
| `backend/app/api/v1/endpoints/market.py` | P2P marketplace |
| `backend/app/api/v1/endpoints/incubation.py` | Axolotito breeding/incubation |
| `backend/app/api/v1/endpoints/codes.py` | Promo code redemption |
| `backend/app/services/web3_service.py` | Blockchain RPC, contract calls |
| `backend/app/services/bank_service.py` | Wallet logic, dual-currency |
| `backend/app/services/game_logic.py` | Core game rules engine |
| `backend/app/services/vip_scheduler.py` | VIP tier management |
| `backend/app/models/economy.py` | AxfPurchaseRecord, TransactionLedger |
| `backend/app/core/config.py` | VIP tiers, BLOCKCHAIN_MODE, economy constants |

## Key Frontend Files

| File | Purpose |
|------|---------|
| `frontend/app/page.tsx` | Main game UI, tab switcher |
| `frontend/app/layout.tsx` | Root layout, PrivyProvider |
| `frontend/components/PlayMode.tsx` | Core gameplay component |
| `frontend/components/ui/LoteriaBoard.tsx` | 4×4 card grid renderer |
| `frontend/components/BoardEditor.tsx` | Board creation/editing |
| `frontend/components/Store.tsx` | In-game store |
| `frontend/components/Inventory.tsx` | Player inventory |
| `frontend/components/CryptoCheckout.tsx` | MoonPay integration |
| `frontend/components/MarketP2P.tsx` | P2P trading |
| `frontend/components/MultiplayerLobby.tsx` | Multiplayer lobby |
| `frontend/hooks/useBlockchainEvents.ts` | On-chain event listeners |
| `frontend/hooks/useMoonPayWidget.ts` | MoonPay widget hook |

## Key Contracts

| Contract | Purpose |
|----------|---------|
| `Frijolito.sol` | FRJ token (ERC-20) |
| `Axoficha.sol` | AXF token (ERC-20) |
| `Webitos.sol` | Egg NFTs (ERC-721) |
| `Axolotitos.sol` | Axolotito NFTs with DNA encoding |
| `CartasLoteria.sol` | Lottery card NFTs |
| `TablasLoteria.sol` | Lottery board escrow |
| `Sobrecito.sol` | Booster pack logic |
| `Consumables.sol` | In-game consumable items |
| `GameController.sol` | Central game orchestrator |

## Additional Resources

- **GDD**: `docs/GDD.md` — full game design document
- **VIP Design**: `docs/vip_club_design.md`
- **Architecture plans**: `docs/plan_*.md`
- **Taskboard docs**: `docs/completed/plan_*taskboard*.md`
- **Handoff notes**: `HANDOFF_ANTIGRAVITY.md`
- **Agent definitions**: `.claude/agents/*.md` — specialized sub-agents
- **Restart script**: `.\reiniciar.ps1` from repo root (Windows PowerShell)
