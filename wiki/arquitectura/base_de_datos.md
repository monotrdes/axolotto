---
tags: [arquitectura, base-de-datos, sqlmodel]
description: "Modelos SQLModel de la base de datos: entidades, campos clave y relaciones"
last_modified: "2026-06-07"
source_files: ["backend/app/models/"]
---

# Base de Datos — Modelos SQLModel

## Modelos por Archivo

### `models/user.py`

**`User`** — Jugador registrado via Privy

| Campo clave | Tipo | Notas |
|-------------|------|-------|
| `privy_did` | str (UNIQUE) | ID principal de Privy — FK usada en toda la DB |
| `nickname` | str? | Nombre visible |
| `wallet_address` | str? (UNIQUE) | Dirección EVM |
| `cave_level` | int (default 1) | Nivel del Cenote (1-8); reemplaza `webito_slots_unlocked` |
| `tutorial_completed` | bool | Si completó el tutorial del primer Axolotito |
| `vip_tier` | str? | `"coral"` / `"dorado"` / `"axolite"` / `None` |
| `vip_expires_at` | datetime? | Expiración de la membresía VIP |
| `vip_pending_gal` | float | FRJ pendiente de reclamar (bono Xochimilco) |
| `lunar_streak_day` | int | Días completados en la semana lunar actual (0-7) |
| `lunar_week` | int | Luna actual (1-6) |
| `f2p_astral_fragments` | int | Fragmentos astrales acumulados (economía F2P) |

Propiedades calculadas: `is_vip`, `vip_bonus_table_slots`, `vip_bonus_axolotito_slots`.

---

### `models/economy.py`

**`Wallet`** — Billetera del jugador

| Campo clave | Tipo | Notas |
|-------------|------|-------|
| `user_id` | str (FK → User.privy_did, UNIQUE) | Un wallet por usuario |
| `axofichas` | float | Saldo AXF (moneda premium) — CHECK >= 0 |
| `frijolitos` | float | Saldo FRJ (moneda de juego) — CHECK >= 0 |
| `frag_comun/raro/epico/legendario` | int | Fragmentos de crafteo |

**`TransactionLedger`** — Registro contable de todos los cambios de saldo

| Campo clave | Tipo | Notas |
|-------------|------|-------|
| `user_id` | str (FK → User) | |
| `amount` | float | |
| `currency` | CurrencyType | `axoficha`, `frijolito`, `axogema` (legacy), `gema_alga` (legacy), `frag_*` |
| `tx_type` | TransactionType | `deposit`, `reward`, `market_buy`, `booster`, `crafting`, `burn`, etc. |
| `item_id` | int? (FK → ItemCatalog) | Ítem relacionado si aplica |
| `related_user_id` | str? | Para P2P: quién envió/recibió |

**`CryptoPurchaseOrder`** — Orden de compra de AXF con cripto

Campos clave: `pack_id`, `usdc_amount`, `axg_amount`, `treasury_address`, `tx_hash_payment` (UNIQUE), `status` (OrderStatus enum), `bonus_pct`, `expires_at`.

**`ProcessedTransaction`** — Registro anti-replay de transacciones blockchain

Campos clave: `tx_hash` (UNIQUE + INDEX), `user_id`, `purpose`.

**`AxfPurchaseRecord`** — Historial de compras de AXF con pesos (MXN). Alias: `AxgPurchaseRecord`.

---

### `models/axolotito.py`

**`Axolotito`** — Mascota NFT del jugador

| Campo clave | Tipo | Notas |
|-------------|------|-------|
| `user_id` | str (FK → User) | Dueño actual |
| `name` | str | Nombre del Axolotito |
| `skin_color`, `gill_type`, `eye_type`, `mouth_type`, `tail_type`, `forehead_type`, `limb_type` | str | Rasgos visuales |
| `level`, `experience` | int | Nivel y XP |
| `stat_salinity` | float 0-100 | Mala suerte (SAL) |
| `stat_luck` | float 0-100 | Suerte para drops y críticos |
| `stat_focus` | float 0-100 | Concentración / precisión |
| `stat_stamina` | int 50-200 | Energía máxima (PILA) |
| `energy_current` | int | Energía restante |
| `status` | str | `idle`, `playing`, `sleeping`, `waiting_settlement`, `expedition`, etc. |
| `escrow_balance_gal` | float | FRJ en custodia durante partida multijugador |
| `assigned_board_id` | int? (FK → PlayerBoard) | Tablero asignado al bot |
| `is_listed_for_sale`, `sale_price_gal` | bool / float | P2P venta |
| `is_rented`, `renter_id`, `rent_expires_at` | — | P2P alquiler |
| `equipped_head/eyes/body_item_id` | int? (FK → ItemCatalog) | Accesorios equipados |
| `cave_items` | JSON (list[int]) | IDs de ítems equipados en la cueva (máx 3) |
| `blockchain_token_id` | int? (UNIQUE) | Token ID on-chain del NFT |
| `dna_sequence` | str? | Representación del uint256 DNA |
| `cpu_win_streak` | int | Racha de victorias consecutivas en CPU |
| `nature` | str? | Naturaleza (ej: `"hyperactive"` — 25% menos tiempo de sueño) |
| `is_frozen_by_vip` | bool | Congelado si el dueño perdió la membresía Axolite que otorgaba el slot |

---

### `models/board.py`

**`PlayerBoard`** — Tablero de Lotería del jugador

| Campo clave | Tipo | Notas |
|-------------|------|-------|
| `user_id` | str (FK → User) | |
| `card_ids` | JSON (list[int]) | 16 IDs de cartas en posiciones 0-15 |
| `card_first_editions` | JSON (list[bool]) | Si cada posición es Primera Edición |
| `games_played`, `games_won` | int | Historial de partidas |
| `level`, `xp` | int | Nivel y experiencia del tablero |
| `recent_games_results` | JSON (list[bool]) | Últimas 5 partidas para racha y CSR |
| `is_dead` | bool | Tablero disuelto (ya no usable) |
| `blockchain_token_id` | int? (UNIQUE) | Token ID on-chain |
| `is_listed_for_rent`, `rent_fee_gal`, `rent_share_owner_pct` | — | Mercado de alquiler |
| `is_npc_pool` | bool | Tablero del pool de NPCs del sistema |
| `npc_retired` | bool | NPC graduado al nivel 10 (pool Gashapón) |
| `is_frozen_by_vip` | bool | Congelado si el dueño perdió la membresía |

---

### `models/items.py`

**`ItemCatalog`** — Catálogo maestro de ítems de la tienda

Campos clave: `name`, `item_type` (EGG, BOOSTER, CARD, ACCESSORY, BOARD, CONSUMABLE, CURRENCY_PACK, CAVE_ITEM), `rarity` (common/rare/epic/legendary), `price_axg` (precio AXF), `price_gal` (precio FRJ), `max_supply`, `max_per_user`, `item_metadata` (JSON flexible).

**`PlayerInventory`** — Inventario del jugador (cartas, sobres, consumibles, accesorios)

Campos clave: `user_id`, `item_id` (FK → ItemCatalog), `quantity`, `is_first_edition`, `is_shiny`.

**`WebitoIncubation`** — Estado de incubación de un huevo

Campos clave: `user_id`, `item_id`, `calor_actual` (0-100%), `genetic_purity`, `last_petting/singing/feeding` (timestamps de cariñitos), bonus stats acumulados, `imprinting_games_played`, `tutorial_phase/act_index/karma`.

**`CapsulaPity`** — Contadores pity por tier de Gashapón por usuario

Campos: `user_id` (PK), `pity_cobre`, `pity_plata`, `pity_oro`.

**`LegacyBacker`** — Inversores originales 2021 con derecho a Webitos Fundadores gratuitos.

**`InventoryMarketListing`** — Publicación de ítem de inventario en el mercado P2P.

**`WhitelistEntry`** — Registro en la whitelist de Fase 1.

---

### `models/lobby_models.py`

**`GameRoom`** — Sala de juego multijugador

Campos clave: `room_type` (`rookie_pool`, `champion_abyss`, `player_hosted`), `entry_fee_gal`, `status` (waiting/playing/finished), `host_id` (FK → User), `room_config` (JSON), `visibility` (public/friends/private), `password_hash`.

**`RoomRegistration`** — Inscripción de un Axolotito en una GameRoom

Campos: `room_id`, `axolotito_id`, `boards_json` (JSON list de board IDs).

**`ActiveGameState`** — Estado en vivo de la partida para polling del frontend

Campos: `room_id` (UNIQUE), `phase`, `cards_drawn_json`, `player_states_json`, `turns_played`, `current_card_id`, `tension_level`.

**`MultiplayerGameLog`** — Resultado de partida multijugador por jugador

Campos clave: `user_id`, `axolotito_id`, `outcome` (Victoria/Derrota), `net_gal`, `xp_gained`, `won_jackpot`, `notified`.

**`TreasuryVault`** — Acumulado de la comisión del 5% de la casa.

**`JackpotVault`** — Pozo del Jackpot de Oro (arranca en 1000 FRJ).

**`JackpotWin`** — Historial de victorias del Jackpot.

---

### `models/promo.py`

**`PromoCode`** — Código de corcholata promocional.

**`PendingReward`** — Premio pendiente de reclamar (se entrega al final del tutorial): `reward_axf`, `reward_frj`, `reward_item_id`.

---

### `models/manual_mode_event.py`

**`ManualModeEvent`** — Evento temporal de Modo Manual (configurado por admin).

Campos clave: `start_date/end_date`, `daily_open/close_time`, `tabla_cost_gal`, `max_tablas_per_player`, `win_condition`, `griton_delay_ms`, `vip_only`, `min_axo_level`.

---

## Relaciones Principales

```
User (privy_did)
  ├── 1:1  Wallet
  ├── 1:N  Axolotito          (user_id)
  ├── 1:N  PlayerBoard        (user_id)
  ├── 1:N  PlayerInventory    (user_id)
  ├── 1:N  WebitoIncubation   (user_id)
  ├── 1:N  TransactionLedger  (user_id)
  ├── 1:N  CryptoPurchaseOrder (user_id)
  ├── 1:N  MultiplayerGameLog (user_id)
  └── 1:N  GameRoom           (host_id — solo player_hosted)

Axolotito
  ├── FK   assigned_board_id → PlayerBoard
  ├── FK   renter_id         → User
  ├── FK   equipped_*_item_id → ItemCatalog
  └── 1:N  RoomRegistration  (via GameRoom)

PlayerBoard
  └── 1:N  RoomRegistration  (board IDs en boards_json)

ItemCatalog
  └── 1:N  PlayerInventory   (item_id)
  └── 1:N  TransactionLedger (item_id)

GameRoom
  ├── 1:N  RoomRegistration
  └── 1:1  ActiveGameState
```

## Campos con Aliases (IMPORTANTE)

```python
# Wallet — los siguientes pares acceden al MISMO campo en la BD
wallet.axogemas    = wallet.axofichas   # campo real: axofichas  (AXF)
wallet.gemas_alga  = wallet.frijolitos  # campo real: frijolitos (FRJ)

# Usar SIEMPRE los nombres nuevos en código nuevo:
wallet.axofichas   # correcto
wallet.frijolitos  # correcto

# AxfPurchaseRecord
record.axg_amount  # property → record.axf_amount (campo real)
```

Los alias existen para compatibilidad con registros históricos en la BD y código legacy del frontend.

## Alembic — Migraciones

- Directorio: `backend/alembic/`
- Comando: `alembic upgrade head` (desde el directorio `backend/`)
- Si falla con "multiple heads": `alembic merge heads -m "merge"` antes del upgrade
- Las migraciones incrementales recientes se aplican directamente en `main.py` `on_startup` usando `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`; ver [[backend]] para el patrón.

## PostgreSQL

- Host: `127.0.0.1:5433` (expuesto desde Docker)
- Nombre y credenciales: ver `backend/.env` o `backend/app/core/config.py`
- ORM: SQLModel (wrapper de SQLAlchemy async-compatible)
- Constraints de integridad: `axofichas >= 0`, `frijolitos >= 0` en la tabla `wallet`
