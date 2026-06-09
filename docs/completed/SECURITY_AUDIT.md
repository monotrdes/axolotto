# Security Audit Report — Axolotto
**Date:** 2026-05-31  
**Auditor:** Claude Sonnet (claude-sonnet-4-6) via security-reviewer agent  
**Scope:** Backend (FastAPI), Smart Contracts (Solidity), Frontend env vars  

---

## Executive Summary

**Overall Risk Level: CRITICAL — Do not launch with real-money flows until SEV-1 through SEV-3 are resolved.**

The game infrastructure contains solid defensive thinking in many areas (replay-protection in checkout, pessimistic locking in P2P transfers, SystemRandom in multiplayer, comprehensive Sybil checks). However, three server-side vulnerabilities allow an attacker with no special knowledge to **print unlimited in-game currency**, **bypass payment entirely**, or **drain escrow funds**. These are fail-open defaults in configurations that are missing from the committed `.env` file and which default to disabled/None.

**Top 3 critical findings:**
1. `POST /api/v1/bank/admin/deposit` is publicly accessible with no authentication when `TRIDY_API_KEY` is unset — currently the case in the deployed `.env`.
2. The USDC payment verification (`verify_usdc_payment`) short-circuits to `True` when `USDC_ADDRESS` is unset or the hash starts with `"0x_mock"` — both conditions are true in the deployed `.env`.
3. The Privy JWT authentication system degrades to anonymous-user-controlled identity injection when `PRIVY_APP_ID` is unset — the current `.env` has no `PRIVY_APP_ID` set.

---

## Findings

---

### [SEV-1] Unauthenticated Admin Money-Printing Endpoint

- **Severity:** CRITICAL
- **Location:** `backend/app/api/v1/endpoints/bank.py:52-68`, `backend/app/core/config.py:95`
- **Description:** The `POST /api/v1/bank/admin/deposit` endpoint uses a guard `if settings.TRIDY_API_KEY and x_admin_token != settings.TRIDY_API_KEY`. When `TRIDY_API_KEY` is `None` (the default in `config.py` and the current state of the committed `.env` which has no `TRIDY_API_KEY` entry), the short-circuit evaluation makes the entire check falsy — skipped entirely. The endpoint accepts no `get_verified_user_id` dependency at all, so there is zero authentication. The request body is a `DepositRequest` with `user_id`, `amount`, `currency`, and `description` — all fully attacker-controlled. It calls `BankService.admin_deposit()` which performs both a database credit and an on-chain `mint()` call to the real AXG contract.
- **Impact:** Any anonymous internet user can mint unlimited AXG or GAL to any `user_id`, including their own account. On-chain minting is triggered in the same call. This completely collapses the game economy.
- **PoC:**
  ```bash
  curl -X POST https://api.axolot.to/api/v1/bank/admin/deposit \
    -H "Content-Type: application/json" \
    -d '{"user_id":"<attacker_privy_did>","amount":999999,"currency":"axogema","description":"free money"}'
  # No token required. Returns {"mensaje": "Depósito exitoso de 999999 axogema"}
  ```
- **Fix:** Add `get_verified_user_id` + `require_admin` as FastAPI dependencies on this endpoint. Do not rely solely on an optional API key that can be absent. Additionally, set `TRIDY_API_KEY` to a strong random secret in every deployment environment as a second factor.

---

### [SEV-2] Payment Bypass: USDC Verification Returns True Without a Real Transaction

- **Severity:** CRITICAL
- **Location:** `backend/app/services/web3_service.py:557-563`, `backend/app/core/config.py:88`, `backend/.env:25` (USDC_ADDRESS not set)
- **Description:** `verify_usdc_payment()` has two early-return `True` paths before any on-chain check occurs. First (line 558): if `tx_hash.startswith("0x_mock")`, returns `True` immediately. Second (lines 561-563): if `settings.USDC_ADDRESS` is empty (the default for `USDC_ADDRESS: str = ""`), prints a warning and returns `True`. The committed `.env` file has `USDC_ADDRESS=` (empty string). Both bypass conditions are currently active in any deployment using that `.env`. The `tx_hash` is a free-form string submitted by the user through `ConfirmPaymentRequest` — no server-side format validation occurs before this check.
- **Impact:** An attacker submits a checkout confirmation with `tx_hash="0x_mock_anything"` or any valid-looking hash while `USDC_ADDRESS` is empty. The system credits full AXG without receiving any USDC. The `ProcessedTransaction` unique constraint prevents reuse of the exact same hash string, but the attacker simply varies the suffix (`0x_mock_a`, `0x_mock_b`...) to generate unlimited credits. Each generates a real on-chain mint transaction.
- **PoC:** Create an order via `POST /api/v1/bank/checkout/crypto`, then confirm with `{"tx_hash": "0x_mock_exploit_001"}`. The response will return `status: completed` with full AXG credited.
- **Fix:** Remove both early-return `True` paths entirely from production code. If mock behavior is needed for local dev, gate it explicitly on `settings.BLOCKCHAIN_MODE == "local"`. Require `USDC_ADDRESS` to be non-empty before the service starts (add a validator in `Settings`). Consider rejecting any `tx_hash` that does not match the `0x[0-9a-f]{64}` format before processing.

---

### [SEV-3] Privy JWT Disabled: Full Auth Bypass via Query Parameter

- **Severity:** CRITICAL
- **Location:** `backend/app/core/auth.py:35-61`, `backend/app/core/config.py:92`, `backend/.env:21`
- **Description:** `get_verified_user_id()` has two fallback branches that activate when `settings.PRIVY_APP_ID` is `None` (the default in `config.py`; the `.env` file contains no `PRIVY_APP_ID` entry). Branch 1 (lines 35-46): If no token is provided, the function reads `user_id` from the query string (`?user_id=...`) and returns it as the authenticated identity. Branch 2 (lines 52-61): If a token is provided, it is decoded **without signature verification** (`options={"verify_signature": False}`), and the `sub` claim is trusted blindly. The `.env` commits `ADMIN_PRIVY_DID=did:privy:cmnn1tv0o02au0ckzho9ugkb2`.
- **Impact:** An attacker can impersonate any user — including the admin — by passing `?user_id=<target_privy_did>` on any endpoint that uses `get_verified_user_id`. Passing `?user_id=did:privy:cmnn1tv0o02au0ckzho9ugkb2` grants full admin access to all `require_admin`-gated endpoints. Any player's account can be drained, their inventory stolen, admin operations executed.
- **PoC:**
  ```bash
  curl "https://api.axolot.to/api/v1/admin/overview?user_id=did:privy:cmnn1tv0o02au0ckzho9ugkb2"
  # Returns full admin financial overview with no credentials.
  ```
- **Fix:** Set `PRIVY_APP_ID` in the production `.env` immediately. Consider removing the development-mode bypass entirely from the production codebase, or gate it on an explicit `ENVIRONMENT=development` env var that cannot be set in production. Never trust client-supplied identity strings as a fallback.

---

### [SEV-4] Escrow Double-Refund Race Condition in `settle_axolotito_escrow`

- **Severity:** HIGH
- **Location:** `backend/app/api/v1/endpoints/multiplayer.py:370-425`
- **Description:** The `POST /multiplayer/settle` endpoint reads the `Axolotito` and `Wallet` objects without acquiring a row lock (`for_update`). The status check `if axo.status != "waiting_settlement"` (line 382) occurs before any locking, so two concurrent requests both pass it and proceed. Both add `axo.escrow_balance_gal` to the user's wallet. This is an asymmetry with `register_axolotito` which correctly calls `BankService.get_or_create_wallet(session, verified_user_id, for_update=True)` (line 135).
- **Impact:** A player submitting two concurrent `settle` requests at the `waiting_settlement` state receives double the escrow payout. Since escrow represents real-money-backed GAL, this doubles real-value assets.
- **PoC:** Register an Axolotito, wait for `waiting_settlement` status, fire two simultaneous HTTP POST to `/multiplayer/settle`. Both pass the status check before either commits; both credit `escrow_balance_gal` to the wallet.
- **Fix:**
  ```python
  # In settle_axolotito_escrow:
  axo = session.exec(
      select(Axolotito)
      .where(Axolotito.id == axolotito_id)
      .with_for_update()
  ).first()
  wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
  # Re-check status AFTER acquiring the lock
  if axo.status != "waiting_settlement":
      raise HTTPException(...)
  ```

---

### [SEV-5] Market P2P Buy: Buyer Wallet Not Locked Before Balance Check

- **Severity:** HIGH
- **Location:** `backend/app/api/v1/endpoints/market.py:124-244`, specifically lines 145-161
- **Description:** In `buy_inventory_listing`, the `listing` row is correctly locked with `with_for_update()` (line 135). However, `buyer_wallet` and `seller_wallet` are fetched at lines 145-146 without any lock. The balance check (line 149) and deduction (line 161) are not atomic with other concurrent purchase requests by the same buyer. A buyer hitting two different listings simultaneously passes both balance checks, both deductions proceed, and the wallet can go negative.
- **Impact:** A buyer can purchase more than their balance allows if two market buy requests race simultaneously. This creates a negative GAL balance — a real liability since GAL is backed by AXG/USDC.
- **PoC:** Two simultaneous requests to buy different listings. Both pass the `buyer_wallet.gemas_alga < price` check before either deducts.
- **Fix:**
  ```python
  # Replace lines 145-146 in market.py:
  buyer_wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
  seller_wallet = BankService.get_or_create_wallet(session, listing.seller_id, for_update=True)
  ```

---

### [SEV-6] CORS Wildcard Origin Regex Bypasses Explicit Allowlist

- **Severity:** HIGH
- **Location:** `backend/app/main.py:302-309`
- **Description:** The CORS middleware is configured with both an explicit `allow_origins` list (lines 304) and `allow_origin_regex="https?://.*"` (line 305) alongside `allow_credentials=True` (line 306). In Starlette's CORS implementation, when `allow_origin_regex` is set, it is evaluated alongside `allow_origins`. The regex `https?://.*` matches **any** HTTP or HTTPS origin. The result is that the explicit allowlist is effectively irrelevant — any origin is accepted and the server reflects it in the `Access-Control-Allow-Origin` response header, combined with `Access-Control-Allow-Credentials: true`.
- **Impact:** A malicious website can make credentialed cross-origin requests to the API. Combined with Bearer token auth, this breaks the intended CORS protection and enables CSRF-style attacks.
- **Fix:** Remove `allow_origin_regex` entirely, or restrict it to `r"https://.*\.axolot\.to"`. The explicit list `["https://axolot.to", "https://www.axolot.to", "http://localhost:3000"]` is the correct baseline.

---

### [SEV-7] Insecure RNG for Legendary Drops (Mersenne Twister on Highest-Value Path)

- **Severity:** MEDIUM
- **Location:** `backend/app/api/v1/endpoints/shop.py:477`
- **Description:** The `_try_legendary_drop()` function uses `random.random()` (Python's Mersenne Twister PRNG) for the probability check of Webito Astral (0.1%) and Booster Foil (0.5%) drops. This directly contradicts the module-level `_rng = random.SystemRandom()` declaration (line 20) and `SECURITY.md` §4.3 which claims "Se utiliza la clase `random.SystemRandom` ... en todos los puntos críticos del código." The Mersenne Twister's state is 624 integers — predictable after observing sufficient outputs.
- **Impact:** An attacker who observes enough roll outcomes can statistically infer the PRNG state and predict when the next legendary drop will occur, timing their rolls to farm the highest-value items.
- **Fix:** Replace line 477 with `rand = _rng.random()` (using the already-defined `_rng = random.SystemRandom()`). One-character change with zero risk.

---

### [SEV-8] Secrets Committed to Git-Tracked `.env`

- **Severity:** HIGH
- **Location:** `backend/.env:1,5,21`
- **Description:** Three sensitive values are committed to the repository in a tracked `.env` file:
  1. Line 1: PostgreSQL connection string with credentials (`axolotto_admin:una_contraseña_super_perrona_y_larga@db_axolotto:5432/axolotto_app_db`)
  2. Line 5: `TREASURY_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` — Anvil's well-known public account #0 key. Harmless locally but **normalizes the pattern** of committing private keys.
  3. Line 21: `ADMIN_PRIVY_DID=did:privy:cmnn1tv0o02au0ckzho9ugkb2` — combined with SEV-3, this gives the exact string needed to impersonate admin.
- **Impact:** Committed DB password grants direct database access to anyone with repo access. The committed treasury key pattern makes a future mainnet key commit likely. The committed admin DID enables auth bypass (see SEV-3).
- **Fix:** `git rm --cached backend/.env` and add `.env` to `.gitignore` immediately. Rotate the database password. Move all secrets to environment-specific secrets management (Docker secrets, Vault, AWS Secrets Manager). Provide `backend/.env.example` with placeholder values. Consider cleaning git history with `git-filter-repo`.

---

### [SEV-9] Checkout Replay Protection Burns Legitimate Transactions (Stranded Order Bug)

- **Severity:** MEDIUM
- **Location:** `backend/app/services/checkout_service.py:199-231`
- **Description:** When `ProcessedTransaction` is inserted and `order.status = CONFIRMING` committed (lines 201-217), then the on-chain verification fails (line 222), the order is marked `FAILED` (line 228-232) but the `ProcessedTransaction` row is **not deleted**. The tx_hash is permanently consumed. If the user's USDC transaction was genuinely valid but temporarily unavailable (node sync delay, RPC timeout), their tx_hash is now burned — it cannot be submitted again, and the order is marked FAILED, stranding the user's real payment.
- **Impact:** Users who sent real USDC but whose transaction wasn't yet visible on the RPC node at confirmation time lose their funds (USDC sent, no AXG received, no retry possible). Also a griefing vector: submit a valid tx_hash of another user's legitimate USDC transfer to a different treasury to burn it.
- **Fix:** On verification failure, delete the `ProcessedTransaction` row (allowing retry), and change the order status back to `AWAITING_PAYMENT` with an appropriate error message. Add retry logic with configurable confirmation wait time. Add `re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash)` validation before processing.

---

### [SEV-10] `admin/simulation/run` Executes Subprocess with Admin-Controlled Parameters

- **Severity:** MEDIUM
- **Location:** `backend/app/api/v1/endpoints/admin.py:115-148`
- **Description:** `_run_sim_task()` builds a subprocess command using `str(params.players)`, `str(params.games)`, `str(params.include_user)`, etc. The `include_user` parameter is an arbitrary string appended as an argument. While `subprocess.Popen` with a list (not a shell string) prevents shell injection, if the simulation script processes `include_user` unsafely (e.g., passes it into a SQL query), this is a second-order injection. The `_sim_state` dict is not thread-safe. Also, a valid admin account can consume arbitrary server CPU by repeatedly spawning simulation processes.
- **Impact:** Potential second-order injection if simulation script uses `include_user` unsafely. Admin can crash backend with CPU exhaustion.
- **Fix:** Validate `include_user` strictly as a Privy DID format (`did:privy:[a-z0-9]+`) before adding it to the command. Replace `_sim_state` with `asyncio.Lock`. Consider moving simulation to a background job queue (Celery) rather than direct subprocess spawning.

---

### [SEV-11] Mass Assignment: `BuyRequest.user_id` Allows Fragile Authorization Pattern

- **Severity:** MEDIUM
- **Location:** `backend/app/api/v1/endpoints/shop.py:22-25, 104-118`
- **Description:** The `BuyRequest` Pydantic model exposes `user_id: str` as a client-supplied field. The endpoint checks `if request.user_id != verified_user_id` and raises 403. This is correct now, but it's a fragile design — the defense depends on a manual equality check. If the check is ever removed during a refactor, it silently becomes a privilege escalation. The same pattern appears in `GashaponRollRequest.user_id` (line 197-198).
- **Impact:** Currently mitigated. But if the check is removed (easy accident in refactor), any user can purchase items for any other user's account.
- **Fix:** Remove `user_id` from `BuyRequest` and `GashaponRollRequest`. The endpoint already has `verified_user_id` from the dependency — use it directly in the service call. Eliminates the bug class structurally.

---

### [SEV-12] Stock Count Uses `description.contains()` (LIKE Query) Instead of Exact Item ID

- **Severity:** MEDIUM
- **Location:** `backend/app/services/shop_service.py:63-113`
- **Description:** The annual Astral Webito supply cap (100/year) and booster supply cap are computed by counting `TransactionLedger` rows where `description.contains(item.name)` — a `LIKE '%<item_name>%'` query. If `item.name` contains SQL wildcard characters (`%`, `_`) or has a common substring matching other items, the count will be incorrect. Can be manipulated to trigger false sold-out conditions and premature phase transitions that can't be reversed.
- **Impact:** Artificial sold-out triggers cause premature phase transitions. Incorrect inventory counts inflate or deflate supply caps.
- **Fix:** Track sales via a dedicated `sales_count` column on `ItemCatalog` (incremented atomically with each purchase), or count `PlayerInventory` rows with the exact `item_id`. Remove the `description.contains()` queries.

---

### [SEV-13] Promo Code Redemption Accepts User-Supplied Email for Whitelist

- **Severity:** LOW
- **Location:** `backend/app/services/promo_service.py:10-75`
- **Description:** `redeem_promo_code` accepts an `email` parameter from the client and uses it to create a `WhitelistEntry`. There is no verification that the email matches the user's registered email in Privy. The `redeemed_by == user_id` check is correct, but the email stored in the whitelist entry may be arbitrary.
- **Impact:** A user can register arbitrary email addresses in the whitelist. If the whitelist email is used for marketing, gated access, or compliance purposes, it will contain attacker-controlled values.
- **Fix:** Use the user's verified email from the `User` table (`user.email`) rather than accepting it from the request body. If Privy-verified email isn't available, reject the request.

---

### [SEV-14] Admin Simulation Report Has Unvalidated File Path

- **Severity:** LOW
- **Location:** `backend/app/api/v1/endpoints/admin.py:703-711`
- **Description:** `admin_simulation_report` reads the file at `settings.SIMULATION_REPORT_PATH` and returns its full contents. This path comes from an environment variable and is not validated to be within a permitted directory.
- **Impact:** Low likelihood (requires env manipulation), but if exploited, full file disclosure including application secrets.
- **Fix:** Validate the path: `path = pathlib.Path(settings.SIMULATION_REPORT_PATH).resolve(); assert path.is_relative_to("/app/")`.

---

### [SEV-15] Smart Contracts: Backend is the Full Trust Point (Design Note)

- **Severity:** INFO
- **Location:** `contracts/src/TablasLoteria.sol`, `contracts/src/GameController.sol`
- **Description:** Contracts are well-structured. All use Solidity `^0.8.24` (checked arithmetic by default, no overflow risk). `onlyController`/`onlyOwner` on all mint/burn functions. `dissolveBoard` burns the NFT before transferring cards back (checks-effects-interactions pattern upheld). `ERC1155Holder` handles callbacks correctly. No identified reentrancy vulnerabilities.

  Design note: all on-chain asset safety is fully delegated to the backend via the treasury private key. If SEV-3 (auth bypass) or SEV-1 (unauthenticated deposit) are exploited, the backend willingly calls `mint()` with attacker-controlled parameters. The contracts themselves are not the attack surface — the backend is. Ensure `TREASURY_PRIVATE_KEY` is rotated before mainnet, stored in a hardware wallet or KMS, and the Anvil dev key (`0xac09...`) is NEVER used in production.

---

### [SEV-16] Frontend `.env.local` Committed with Sandbox Keys

- **Severity:** LOW
- **Location:** `frontend/.env.local:17`
- **Description:** `NEXT_PUBLIC_MOONPAY_PK=pk_test_...` is a sandbox/test publishable key — public by design. Contract addresses and RPC URLs as `NEXT_PUBLIC_` variables are also public by design. This is not currently a vulnerability.

  **Action required:** Verify that production `.env.local` never includes any MoonPay **secret key** or other non-`NEXT_PUBLIC_` secret. Add `frontend/.env.local` to `.gitignore` for good hygiene and create `frontend/.env.local.example`.

---

## Checklists

### [x] Critical — Must fix before any real-money launch

- [x] **SEV-1**: Gate `POST /api/v1/bank/admin/deposit` with `require_admin` dependency (`bank.py:53`)
- [x] **SEV-2**: Remove `startswith("0x_mock")` and empty-`USDC_ADDRESS` early-returns from `verify_usdc_payment`; set `USDC_ADDRESS` in production `.env` (Gated on `BLOCKCHAIN_MODE == "local"`)
- [x] **SEV-3**: Set `PRIVY_APP_ID` in production `.env`; remove or gate dev-mode auth bypass on explicit `ENVIRONMENT=development` (Gated on `BLOCKCHAIN_MODE == "local"`)
- [x] **SEV-8**: Run `git rm --cached backend/.env`; add `.env` to `.gitignore`; rotate DB password; create `.env.example`

### [x] High — Fix before launch

- [x] **SEV-4**: Add `with_for_update()` on Axolotito and Wallet reads in `settle_axolotito_escrow`; re-check status after acquiring lock
- [x] **SEV-5**: Add `for_update=True` to both wallet fetches in `buy_inventory_listing` (`market.py:145-146`)
- [x] **SEV-6**: Remove `allow_origin_regex="https?://.*"` from CORS middleware in `main.py`; use explicit allowlist only

### [x] Medium — Fix in next sprint

- [x] **SEV-7**: Replace `random.random()` with `_rng.random()` in `_try_legendary_drop()` (`shop.py:477`)
- [x] **SEV-9**: On payment verification failure, delete the `ProcessedTransaction` row and reset order to `AWAITING_PAYMENT`; add tx_hash format validation
- [x] **SEV-10**: Validate `include_user` as `did:privy:[a-z0-9]+` before subprocess; use `asyncio.Lock` for simulation state
- [x] **SEV-11**: Remove `user_id` from `BuyRequest` and `GashaponRollRequest`; derive identity from `verified_user_id` only
- [x] **SEV-12**: Replace description-based stock count with `item_id`-keyed counter or dedicated `sales_count` column on `ItemCatalog`

### [/] Low / Hardening — Fix eventually

- [x] **SEV-13**: Use verified email from `User` table in promo code redemption instead of user-supplied value
- [x] **SEV-14**: Validate `SIMULATION_REPORT_PATH` is within `/app/` before reading
- [ ] **SEV-15**: Rotate treasury private key before mainnet; store in KMS or hardware wallet; NEVER commit real keys
- [x] **SEV-16**: Add `frontend/.env.local` to `.gitignore`; create `frontend/.env.local.example`
- [ ] Add rate limiting (`slowapi`) on payment and auth endpoints
- [ ] Add negative balance database constraint on `Wallet.gemas_alga` and `Wallet.axogema`
- [ ] Add minimum tx_hash format validation (`re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash)`) at API boundary
- [x] Review board rental endpoints to confirm `renter_id`/`rent_expires_at` assignment verifies board ownership

---

## Action Plan

Priority-ordered with effort estimates:

### Day 1 — Stop bleeding (trivial changes, ~2-4 hours total)

1. **SEV-3 — Set `PRIVY_APP_ID`** (DevOps, 30 min): Add `PRIVY_APP_ID=<real_value>` to the production `.env` immediately. Enables JWT signature verification and disables anonymous identity injection. Zero code change.

2. **SEV-1 — Gate admin deposit endpoint** (Backend, 1 hour): Add `_: str = Depends(require_admin)` to `admin_deposit_funds()` in `backend/app/api/v1/endpoints/bank.py:53`. Also set `TRIDY_API_KEY` in production.

3. **SEV-8 — Remove `.env` from git** (DevOps, 1 hour):
   ```bash
   git rm --cached backend/.env
   echo "backend/.env" >> .gitignore
   # Create backend/.env.example with placeholder values
   # Rotate DB password
   # Consider git-filter-repo to clean history
   ```

### Day 2 — Fix payment security (4-8 hours)

4. **SEV-2 — Fix `verify_usdc_payment`** (Backend, 2 hours): Remove the `startswith("0x_mock")` and `not settings.USDC_ADDRESS` early returns. Gate mock behavior on `BLOCKCHAIN_MODE == "local"`. Set `USDC_ADDRESS` in all non-local environments. Add format validation for `tx_hash`.

5. **SEV-9 — Fix stranded orders** (Backend, 2 hours): On on-chain verification failure in `checkout_service.py`, delete the `ProcessedTransaction` row and reset order status to `AWAITING_PAYMENT`. Add `re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash)` validation.

### Week 1 — Fix race conditions (4-8 hours)

6. **SEV-4 — Fix settle race** (Backend, 2 hours): Lock Axolotito and Wallet rows with `for_update` in `settle_axolotito_escrow`; re-check status after acquiring lock.

7. **SEV-5 — Fix market buy race** (Backend, 1 hour): Add `for_update=True` to both wallet fetches in `buy_inventory_listing`.

8. **SEV-6 — Fix CORS** (Backend, 30 min): Remove `allow_origin_regex` line from `main.py`.

### Week 2 — Hardening sprint (8-16 hours)

9. **SEV-7 — Fix RNG** (Backend, 15 min): One-line fix: `rand = _rng.random()` in `_try_legendary_drop` at `shop.py:477`.

10. **SEV-11 — Remove mass-assignment pattern** (Backend, 2 hours): Refactor `BuyRequest` and `GashaponRollRequest` to remove `user_id` field; derive from `verified_user_id` dependency.

11. **SEV-12 — Fix stock counting** (Backend, 4 hours + migration): Add `sales_count` column to `ItemCatalog`; increment atomically on purchase; remove `description.contains()` queries.

12. **SEV-10 — Validate simulation params** (Backend, 2 hours): Add `include_user` format validation; use `asyncio.Lock` for simulation state.

### Pre-mainnet checklist (before real USDC in circulation)

- [ ] Rotate `TREASURY_PRIVATE_KEY` to hardware wallet or KMS-managed key; ensure Anvil default key is NEVER deployed
- [ ] Verify `PRIVY_APP_ID` is set and JWT expiry/audience validation is working end-to-end with a real Privy token
- [ ] Run full regression test against checkout flow with real USDC on testnet after SEV-2 fix
- [ ] Implement rate limiting (`slowapi`) on payment and auth endpoints
- [ ] Add database-level constraints: `CHECK (gemas_alga >= 0)`, `CHECK (axogema >= 0)` on `Wallet`
- [ ] Engage a third-party smart contract auditor before handling real funds on mainnet
- [ ] Set up monitoring/alerting on: negative balances, admin deposit calls, bulk mint transactions, failed auth attempts

---

## Files Audited

- `backend/.env`
- `backend/app/core/auth.py`
- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/api/v1/endpoints/bank.py`
- `backend/app/api/v1/endpoints/admin.py`
- `backend/app/api/v1/endpoints/checkout.py`
- `backend/app/api/v1/endpoints/shop.py`
- `backend/app/api/v1/endpoints/multiplayer.py`
- `backend/app/api/v1/endpoints/market.py`
- `backend/app/api/v1/endpoints/game.py`
- `backend/app/api/v1/endpoints/codes.py`
- `backend/app/api/v1/endpoints/whitelist.py`
- `backend/app/services/checkout_service.py`
- `backend/app/services/bank_service.py`
- `backend/app/services/shop_service.py`
- `backend/app/services/multiplayer_service.py`
- `backend/app/services/promo_service.py`
- `backend/app/services/web3_service.py`
- `backend/app/models/economy.py`
- `backend/app/models/user.py`
- `contracts/src/TablasLoteria.sol`
- `contracts/src/GameController.sol`
- `contracts/src/GemaAlga.sol`
- `contracts/src/Axogema.sol`
- `contracts/src/CartasLoteria.sol`
- `contracts/src/Axolotitos.sol`
- `contracts/src/Webitos.sol`
- `frontend/.env.local`
- `docs/SECURITY.md`
