# Booster Purchase Flow & Phase System Enhancements

## Goal Description
Redesign the booster purchase and card unboxing system to ensure premium game design, marketing appeal, and collection value:
1. **Duplicate Prevention**: All cards within any booster pack must be unique (no duplicate card IDs).
2. **Monthly Shiny Booster Cap**: Limit the `Booster Brillante (Foil)` to exactly 100 purchases per calendar month globally. Each contains exactly 5 unique shiny cards + 2 unique normal cards.
3. **Phase-Based Limits & Seeding**: Lower limits for Phase 1 boosters to build collectors' FOMO, and seed Phase 2 & 3 boosters to automatically take over when preceding phases sell out.
4. **First Edition Shiny Status**: Any shiny card pulled from a Phase 1 booster is automatically marked as **Shiny + 1st Edition** (both flags set to true).
5. **Normal Booster Shiny Rules**: Normal boosters (Phase > 1) can contain at most one shiny card per pack. First Edition boosters have a much higher shiny probability (each card has an independent 15% chance).
6. **Stunning Frontend Animations & UX**: Add interactive unboxing animations, holographic diagonal shine gradients for shiny cards, and badges showing 1st Edition and Shiny status in the Unboxing Modal and Inventory.

---

## Proposed Changes

### Component 1: Backend Database Seeding
Modify the seed catalog to lower Phase 1 limits and seed Phase 2 and Phase 3 boosters with recommended supplies.

#### [MODIFY] [seed_catalog.py](file:///home/monotr/axolotto/backend/app/scripts/seed_catalog.py)
- **Phase 1 Boosters**:
  - `Booster Fiesta (Fase 1)`: Limit `max_supply = 1000` (was 3000)
  - `Booster Nido (Fase 1)`: Limit `max_supply = 1000` (was 3000)
  - `Booster Cosmos (Fase 1)`: Limit `max_supply = 1000` (was 3000)
  - `Booster Mezclado (Fase 1)`: Limit `max_supply = 1500` (was 5000)
- **Phase 2 Boosters (Unlimited - Inactive by default)**:
  - `Booster Fiesta (Fase 2)`: Limit `max_supply = 2500`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Nido (Fase 2)`: Limit `max_supply = 2500`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Cosmos (Fase 2)`: Limit `max_supply = 2500`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Mezclado (Fase 2)`: Limit `max_supply = 4000`, price `15 AXG / 300 GAL`, `is_active = False`
- **Phase 3 Boosters (Retail - Inactive by default)**:
  - `Booster Fiesta (Fase 3)`: Limit `max_supply = 5000`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Nido (Fase 3)`: Limit `max_supply = 5000`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Cosmos (Fase 3)`: Limit `max_supply = 5000`, price `30 AXG / 500 GAL`, `is_active = False`
  - `Booster Mezclado (Fase 3)`: Limit `max_supply = 10000`, price `15 AXG / 300 GAL`, `is_active = False`
- **Booster Brillante (Foil)**: Set `max_supply = 999999` (as the limit is enforced dynamically per calendar month).

---

### Component 2: Backend Booster Logic
Implement duplicate prevention, shiny booster limit, shiny rules, and return structured card metadata.

#### [MODIFY] [shop_service.py](file:///home/monotr/axolotto/backend/app/services/shop_service.py)
- **Monthly Cap Enforcement**:
  - For `Booster Brillante (Foil)`, query `TransactionLedger` for purchases in the current calendar month. Raise an exception if >= 100.
- **Card Generation Logic**:
  - Filter card catalog based on thematic categories (`FIESTA_CARDS`, `NIDO_CARDS`, `COSMOS_CARDS` or all 54 cards).
  - Use `random.sample` to select 7 unique card records to guarantee **no duplicates**.
  - Apply specific shiny rules:
    - **Booster Brillante (Foil)**: Generate exactly 5 shiny cards and 2 normal cards (all 7 are unique).
    - **Phase 1 Boosters (First Edition)**: Each of the 7 cards has an independent 15% chance to be shiny. Shiny cards are marked `is_shiny=True` AND `is_first_edition=True` (Shiny + 1st Edition).
    - **Normal Boosters (Phase 2 & 3)**: Limit shiny cards to at most 1 per pack. There is a 20% chance that the pack contains exactly 1 shiny card (randomly chosen from the 7 cards).
- **Structured Response**:
  - Return a `cards` list of dictionaries containing: `id`, `name`, `rarity`, `dynamic_rarity`, `is_shiny`, `is_first_edition`.

---

### Component 3: Frontend Unboxing & Visual Feedback
Enable the frontend to process the cards array directly and render high-fidelity animations for shiny pulls.

#### [MODIFY] [Store.tsx](file:///home/monotr/axolotto/frontend/components/Store.tsx)
- **API Response Handling**:
  - Read `res.data.cards` and store them in `cartasObtenidasObjects` with their `is_shiny` and `is_first_edition` properties intact.
- **Visual Styles & CSS Keyframes**:
  - Define a shiny diagonal shine sweep gradient animation:
    ```css
    @keyframes shine-sweep {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    ```
  - Define a premium sparkle animation using floating emojis/effects.
- **Card Render Component in Unboxing Modal**:
  - If a card is `is_shiny`, render it with a holographic overlay, a moving diagonal shine effect, and a `✨ Brillante` badge.
  - If a card is `is_first_edition`, render a gold stamp badge `⭐ 1st Ed`.
  - If a card is BOTH, display a gorgeous combined badge: `✨⭐ 1st Ed. Brillante` with animated text shadow.
  - Increase the border glow intensity for shiny legendary cards.

---

### Component 4: Frontend Inventory View
Update the inventory page to properly show "1st Edition Shiny" copies.

#### [MODIFY] [Inventory.tsx](file:///home/monotr/axolotto/frontend/components/Inventory.tsx)
- Split the possession breakdown into four categories:
  - **1st Ed. Brillante**: `is_first_edition && is_shiny`
  - **Brillante**: `!is_first_edition && is_shiny`
  - **1st Edition**: `is_first_edition && !is_shiny`
  - **Edición Normal**: `!is_first_edition && !is_shiny`
- Apply proper gradients and styling to the badges matching the unboxing modal.

---

## Verification Plan

### Automated Verification
- Run backend unit tests or execute seeding scripts to verify new item metadata.
- Check database constraints and SQL queries.

### Manual Verification
- Purchase all types of boosters in the developer environment.
- Verify that **no duplicates** occur in any pack.
- Verify that a Phase 1 booster shiny card is flagged as both First Edition and Shiny.
- Open multiple normal boosters and verify they contain at most 1 shiny.
- Open a Foil Booster and verify it contains exactly 5 shiny cards.
- Try to buy more than 100 Foil Boosters (or mock the ledger count to 100) and verify the buy endpoint blocks it.
- Inspect the unboxing modal to confirm:
  - Card front shows `⭐ 1st Ed` badge for First Edition.
  - Card front shows diagonal holographic shine animation and `✨ Brillante` badge for shiny cards.
- View the Album/Inventory page and verify the separate counts for 1st Edition Shiny copies.
