# Webito Astral: Annual Cap & Premium Game Design Plan

## Goal Description
Implement the checklist item `### Límite Anual del Webito Astral (100 unidades)` and define a premium, non-Pay-to-Win (P2W) collectors' design for the **Webito Astral**:
1. **Annual Cap (100 units)**: Restrict sales globally to 100 units per calendar year. Reset on January 1st.
2. **Elite but Balanced Stats (Not P2W)**: Guarantees a higher stat floor (minimum 45, rolling between 45-85), making it solid out of the egg. However, a standard Axolotito with Hatchery care and accessories can easily exceed it.
3. **Cosmic Aesthetics**: Guaranteed `"astral"` skin color (80% chance) or `"gold"` skin color (20% chance), unlocking premium SVG gradient filters.
4. **Unique Visual Mutations**: Guaranteed rare visual traits like the Glowing Halo (`forehead_type = "halo"`) or Divine Mouth (`mouth_type = "divine"`).

---

> [!IMPORTANT] **User Review Required**
> - Confirm the pricing of **500 AXG** ($1000 MXN / $50 USD) for the Webito Astral.
> - Approve the 80% Astral / 20% Gold skin distribution.
> - Verify the proposed stat baselines (Min 45, Max 85).

---

## Proposed Changes

### Component 1: Database Seeding
#### [MODIFY] [seed_catalog.py](file:///home/monotr/axolotto/backend/app/scripts/seed_catalog.py)
- Ensure the `Webito Astral (Limitado)` is seeded:
  - `name = "Webito Astral (Limitado)"`
  - `max_supply = 100` (resets annually)
  - `price_axg = 500.0`, `price_gal = None` (exclusive premium currency purchase)
  - `item_metadata = {"fase": 1, "tag": "Astral", "is_astral": True}`

---

### Component 2: Backend Purchase Control
#### [MODIFY] [shop_service.py](file:///home/monotr/axolotto/backend/app/services/shop_service.py)
- **Annual Limit Check**:
  - In `ShopService.buy_item`, check if `item.item_metadata.get("is_astral")` is True.
  - Query `TransactionLedger` to count how many Astral Eggs have been sold in the current calendar year.
  - If >= 100, raise HTTP 400: *"Suministro anual agotado para el Webito Astral."*
  - Automatically deactivate the item (`is_active = False`) if the 100 limit is hit on purchase.

---

### Component 3: Eclosion & Genetics Logic
#### [MODIFY] [incubation.py](file:///home/monotr/axolotto/backend/app/api/v1/endpoints/incubation.py)
- **Hatch Check**:
  - In `hatch_webito`, determine if the egg item has `is_astral` metadata.
- **Elite Stat Baseline**:
  - If it is an Astral egg, stats (Luck, Focus, Stamina, Charisma, Agility, Wisdom, Strength) roll from an elevated range:
    - Normal range: `0 - 100` with high probability of lower values.
    - Astral range: `sys_rand.uniform(45.0, 85.0)`.
- **Aesthetic Customization**:
  - Guaranteed skin color: 80% chance `"astral"`, 20% chance `"gold"`.
  - Guaranteed rare traits: 50% chance `forehead_type = "halo"`, 50% chance `mouth_type = "divine"`.
  - Overwrite mapped traits with these premium values before saving the Axolotito.

---

### Component 4: SVG Render (Metadata Endpoint)
#### [MODIFY] [metadata.py](file:///home/monotr/axolotto/backend/app/api/v1/endpoints/metadata.py)
- Update `get_axolotito_svg` to check the `skin_color` field:
  - If `axolotito.skin_color == "astral"`, set `fill_color = "url(#astralGradient)"`.
  - If `axolotito.skin_color == "gold"`, set `fill_color = "url(#goldGradient)"`.
  - Otherwise, fallback to the standard `stat_luck` threshold.

---

### Component 5: Reset Cron Job
#### [NEW] [cron_reset_astral.py](file:///home/monotr/axolotto/backend/app/scripts/cron_reset_astral.py)
- Script scheduled for January 1st to search for the `Webito Astral (Limitado)` in the catalog and set `is_active = True`.

---

## Verification Plan

### Automated Verification
- Seed the catalog and verify the Astral egg catalog properties.
- Mock the transaction database to contain 99 Astral purchases, try to purchase, and verify the 100th purchase deactivates the item.
- Hatch 10 Astral eggs via testing endpoints and check stats are between 45-85, skin is Gold/Astral, and they have Halo or Divine mouth.

### Manual Verification
- Purchase Webito Astral from store and view in inventory.
- Verify its SVG rendering displays the premium gradient.
