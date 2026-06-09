# Migration Plan: Anvil (Local) → Base Sepolia Testnet 🔴

---

## 🎯 Goal
Deploy the full suite of **9 Axolotto smart contracts** to **Base Sepolia** and make the entire Web3 checkout flow (including MoonPay sandbox) work end‑to‑end in a staging environment.

---

## 📚 Context
- The game currently runs against an **Anvil local node** (`chainId = 31337`).
- MoonPay (via Privy) only supports a hard‑coded whitelist of testnets; **Base Sepolia** (chainId 84532) is the only supported network.
- Base Sepolia offers free faucet ETH and USDC (Circle) – perfect for low‑cost testing.

---

## ✅ Success Criteria
1. All 9 contracts deployed on Base Sepolia and their addresses stored in configuration.
2. Backend connects to Base Sepolia RPC and can query contract state.
3. Frontend uses Base Sepolia RPC, chain‑id, and contract addresses.
4. PrivyProvider defaults to Base Sepolia and MoonPay sandbox works.
5. End‑to‑end checkout flows (Mock, MoonPay sandbox, and real USDC) succeed.

---

## 🗂️ Files to Touch
| File | Change |
|---|---|
| `contracts/foundry.toml` | Add `[rpc_endpoints] base_sepolia = "https://sepolia.base.org"` |
| `backend/app/core/config.py` | Add `BASE_SEPOLIA_RPC_URL` and branch logic for `base_sepolia` in `rpc_url` / `chain_id` |
| `backend/.env` | `BLOCKCHAIN_MODE=base_sepolia`, treasury private key, contract addresses, `USDC_ADDRESS` |
| `frontend/.env.local` | `NEXT_PUBLIC_CHAIN_ID=84532`, `NEXT_PUBLIC_RPC_URL=https://sepolia.base.org`, contract addresses, USDC address |
| `frontend/lib/blockchain.ts` | Import `baseSepolia` from `viem/chains` and extend chain‑selection ternary |
| `frontend/components/PrivyProviderWrapper.tsx` | Set `defaultChain` and `supportedChains` to `baseSepolia` |
| `frontend/components/CryptoCheckout.tsx` | Update UI text “Plasma” → “Base”, swap explorer URLs to `sepolia.basescan.org` |
| `frontend/components/*` (Store, Santuario, Inventory, Criadero) | Replace any hard‑coded “Plasma” strings with “Base Sepolia” |
| `frontend/components/Store.tsx` | Update two explorer links to Basescan |

---

## 🛠️ Detailed Phases
### Phase 1 – Prepare Foundry & Deploy Contracts
1. **Update Foundry config** (`contracts/foundry.toml`):
   ```toml
   [rpc_endpoints]
   base_sepolia = "https://sepolia.base.org"
   ```
2. **Deploy** from `contracts/`:
   ```bash
   DEPLOYER_PRIVATE_KEY=0x<YOUR_SEPOLIA_KEY> \
   METADATA_BASE_URL=https://api.axolot.to/api/v1/metadata/ \
   forge script script/Deploy.s.sol \
     --rpc-url base_sepolia \
     --broadcast \
     -vvvv
   ```
   - The script prints **9 contract addresses**. Copy them to the backend and frontend env files (see below).

### Phase 2 – Backend Adjustments
1. **`backend/app/core/config.py`** – add constants and branch logic:
   ```python
   BASE_SEPOLIA_RPC_URL = "https://sepolia.base.org"
   ...
   if self.BLOCKCHAIN_MODE == "base_sepolia":
       return self.BASE_SEPOLIA_RPC_URL
   ```
2. **`backend/.env`** – set:
   ```env
   BLOCKCHAIN_MODE=base_sepolia
   TREASURY_PRIVATE_KEY=0x<SEPOLIA_TREASURY>
   # Deploy addresses (replace …)
   GEMA_ALGA_ADDRESS=0x...
   AXOGEMA_ADDRESS=0x...
   ...
   USDC_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
   ```
3. Restart the API service; ensure logs show `web3_service.is_connected() == True`.

### Phase 3 – Frontend Adjustments
1. **`.env.local`** – set public env vars:
   ```env
   NEXT_PUBLIC_CHAIN_ID=84532
   NEXT_PUBLIC_RPC_URL=https://sepolia.base.org
   NEXT_PUBLIC_USDC_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
   # Contract addresses from Phase 1
   NEXT_PUBLIC_GEMA_ALGA_ADDRESS=0x...
   NEXT_PUBLIC_AXOGEMA_ADDRESS=0x...
   ...
   ```
2. **`frontend/lib/blockchain.ts`** – import `baseSepolia` and extend chain selection:
   ```ts
   import { anvil, baseSepolia } from 'viem/chains';
   const chain = CHAIN_ID === 31337 ? anvil : CHAIN_ID === 84532 ? baseSepolia : customChain;
   ```
3. **PrivyProvider** – in `PrivyProviderWrapper.tsx`:
   ```ts
   defaultChain: baseSepolia,
   supportedChains: [baseSepolia],
   ```
4. **UI Text & URLs** – update every occurrence of “Plasma” to “Base Sepolia”, change explorer links to `https://sepolia.basescan.org/tx/…`.
   - `CryptoCheckout.tsx` (lines ~287 & ~490)
   - `Store.tsx`, `Santuario.tsx`, `Inventory.tsx`, `Criadero.tsx`

---

## 🧪 Post‑Migration Test Matrix
| Test | Steps | Expected Result |
|---|---|---|
| **A – Mock Checkout** | Use manual `0x_mock_usdc_test` token hash | Backend accepts mock, AXG minted, UI shows success |
| **B – MoonPay Sandbox** | Click *Buy with Card* → MoonPay sandbox popup → confirm → use mock hash | MoonPay opens, returns control, mock flow completes |
| **C – Real USDC (E2E)** | Treasury and tester wallets funded via faucets → Pay with Privy wallet | ERC‑20 transfer on Base Sepolia, backend verifies tx, AXG minted on‑chain, UI updates via `useBlockchainEvents` |

---

## 📅 Timeline (Suggested Sprint)
| Day | Milestone |
|---|---|
| **Day 1** | Prepare wallets, obtain Sepolia ETH & USDC faucets |
| **Day 2** | Update Foundry config & run contract deployment |
| **Day 3** | Backend env & config changes, restart services |
| **Day 4** | Frontend env, chain config, UI text updates |
| **Day 5** | Smoke test all three checkout flows, fix any mismatched addresses |
| **Day 6** | Full regression run, update documentation, merge to `staging` branch |

---

## ⚠️ Risks & Mitigations
- **Insufficient Sepolia ETH** – Ensure treasury wallet has at least 0.1 ETH before deployment (covers all 9 contracts). Use Coinbase faucet.
- **USDC faucet rate limits** – Pre‑fetch required USDC for tester wallets; keep a small reserve.
- **Privy chain whitelist** – Verify Privy dashboard lists Base Sepolia; otherwise contact support.
- **Hard‑coded chain IDs** – Search for `31337` literals; replace with env‑driven `NEXT_PUBLIC_CHAIN_ID`.

---

## 📂 Folder Structure
```
axolotto/
├─ contracts/
│   └─ foundry.toml               # updated with base_sepolia endpoint
├─ backend/
│   ├─ app/core/config.py         # new rpc/chain logic
│   └─ .env                      # BLOCKCHAIN_MODE=base_sepolia
├─ frontend/
│   ├─ .env.local                # public chain variables
│   ├─ lib/blockchain.ts          # viem baseSepolia import
│   └─ components/PrivyProviderWrapper.tsx
└─ base_sepolia_migration_plan.md # ← **THIS FILE**
```

---

## 📦 Verification Checklist (run after implementation)
- [ ] `forge script … --rpc-url base_sepolia` succeeds, prints 9 addresses.
- [ ] Backend logs show *connected to Base Sepolia*.
- [ ] `curl https://api.axolot.to/api/v1/bank/checkout/packs` returns 200.
- [ ] Frontend `window.ethereum.chainId` equals `0x84532`.
- [ ] MoonPay sandbox opens without CORS errors.
- [ ] All three checkout flows (A, B, C) pass in a local browser.

---

## 📖 References
- **Base Sepolia RPC:** `https://sepolia.base.org`
- **Base Sepolia Explorer:** `https://sepolia.basescan.org`
- **USDC Testnet (Circle):** `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **MoonPay sandbox docs** – Privy integration guide.

---

*Prepared by Antigravity – Advanced Agentic Coding*
