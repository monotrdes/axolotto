---
tags: [api, usuarios, perfil, recompensas, rankings]
description: "Endpoints de perfil de usuario, Axolotitos, recompensas del Ciclo Lunar y rankings"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/user.py", "backend/app/api/v1/endpoints/rewards.py", "backend/app/api/v1/endpoints/ranking.py"]
---

# API — Usuarios, Recompensas y Rankings

## user.py — Perfil y Gestión de Axolotitos

Prefijo: `/api/v1/auth`

### `POST /auth/sync`
Crea o actualiza el perfil del usuario a partir del JWT de Privy.
- Auth: Si
- Rate limit: 10/minuto
- Body: `{ privy_did, email?, wallet_address? }`
- Crea la wallet si no existe

### `GET /auth/inventory/{user_id}`
Devuelve el inventario completo del jugador (cartas, sobres, consumibles, accesorios).
- Auth: Si (solo puede consultar su propio inventario)

### `GET /auth/axolotitos/{user_id}`
Devuelve la lista de Axolotitos del jugador con sus stats, estado y equipamiento.
- Auth: Si

### `POST /auth/axolotitos/{axolotito_id}/bot-config`
Configura el bot de auto-juego del Axolotito (presupuesto, límites, tablero asignado).
- Auth: Si
- Body: `{ user_id, bot_enabled, bot_budget_axg, bot_loss_limit_axg, bot_profit_limit_axg, assigned_board_id? }`

### `GET /auth/axolotitos/market/sale`
Lista los Axolotitos en venta P2P en el mercado.
- Auth: No (público)
- Query params: `skip`, `limit`

### `GET /auth/axolotitos/market/rent`
Lista los Axolotitos disponibles para alquiler.
- Auth: No (público)
- Query params: `skip`, `limit`

### `POST /auth/axolotitos/{axolotito_id}/list-sale`
Pone un Axolotito a la venta en el mercado P2P.
- Auth: Si
- Body: `{ sale_price_gal: float }`

### `POST /auth/axolotitos/{axolotito_id}/cancel-sale`
Cancela la venta de un Axolotito.
- Auth: Si

### `POST /auth/axolotitos/{axolotito_id}/list-rent`
Pone un Axolotito disponible para alquiler.
- Auth: Si
- Body: `{ rent_fee_gal: float, rent_share_owner_pct: int }`

### `POST /auth/axolotitos/{axolotito_id}/cancel-rent`
Cancela la oferta de alquiler de un Axolotito.
- Auth: Si

### `GET /auth/vip-status`
Devuelve el estado VIP del usuario autenticado (tier, expiry, pending FRJ, streak).
- Auth: Si

### `POST /auth/vip/claim-daily-gal`
Reclama el FRJ diario pendiente del bonus Xochimilco VIP.
- Auth: Si

### `POST /auth/vip/auto-renew`
Activa o desactiva la renovación automática del VIP.
- Auth: Si
- Body: `{ enabled: bool }`

### `POST /auth/axolotitos/{axolotito_id}/rent`
Renta un Axolotito listado por otro jugador (el caller paga la tarifa).
- Auth: Si

### `POST /auth/axolotitos/{axolotito_id}/buy`
Compra un Axolotito listado para venta P2P.
- Auth: Si

### `POST /auth/axolotitos/{axolotito_id}/equip`
Equipa un accesorio del inventario en un slot del Axolotito.
- Auth: Si
- Body: `{ item_id: int, slot: "head" | "eyes" | "body" }`

### `POST /auth/axolotitos/{axolotito_id}/unequip`
Desequipa un accesorio y lo devuelve al inventario.
- Auth: Si
- Body: `{ slot: "head" | "eyes" | "body" }`

### `POST /auth/axolotitos/{axolotito_id}/set-main`
Marca un Axolotito como el principal del jugador.
- Auth: Si

---

## rewards.py — Recompensas

Prefijo: `/api/v1/rewards`

### `POST /rewards/claim`
Reclama el premio Corcholata pendiente después de completar el tutorial.
- Auth: Si
- Rate limit: 5/minuto
- Entrega: AXF + FRJ + ítem (según `PendingReward` del código canjeado)
- Usa `SELECT FOR UPDATE` en `PendingReward` y `Wallet` para prevenir doble reclamación

### `GET /rewards/daily-claim/status`
**DEPRECATED (410 Gone)** — Redirige a `GET /api/v1/rewards/lunar/status`

### `POST /rewards/daily-claim`
**DEPRECATED (410 Gone)** — Redirige a `POST /api/v1/rewards/lunar/claim`

### `GET /rewards/lunar/status`
Devuelve el estado actual del Ciclo Lunar del jugador.
- Auth: Si
- Rate limit: 30/minuto
- Respuesta (via `lunar_streak_service.get_status()`):
  ```json
  {
    "lunar_week": 1-6,
    "streak_day": 0-7,
    "last_claim_at": datetime | null,
    "can_claim": bool,
    "next_reward": {...},
    "cycles_completed": int
  }
  ```

### `POST /rewards/lunar/claim`
Reclama el día actual del Ciclo Lunar (recompensa diaria F2P).
- Auth: Si
- Rate limit: 10/minuto
- El Ciclo Lunar es un track de 7 días x 6 lunas (42 días). Los premios escalan con el día y la luna.
- Registra en `TransactionLedger` con `tx_type=f2p_reward`

---

## ranking.py — Leaderboards

Prefijo: `/api/v1/ranking`

### `GET /ranking/axolotitos`
Ranking de los mejores Axolotitos.
- Auth: No (público)
- Query params:
  - `sort_by`: `"level"` (default) | `"power"` — poder = suma de `luck + focus + stamina + (100 - salinity)`
  - `limit`: int (default 20)
- Respuesta: lista con `{ id, name, level, experience, poder, stats: {suerte, ojo, pila, sal}, owner_nickname, owner_vip_tier, skin/gill/eye/tail_type, ... }`

### `GET /ranking/boards/forjadas`
Lista las Tablas Forjadas: tableros NPC que llegaron al nivel 10 y esperan en el pool Gashapón.
- Auth: No (público)
- Respuesta: `{ id, name, level, xp, games_played, games_won, win_rate, origin_story, npc_room }`

### `GET /ranking/boards`
Ranking de los mejores tableros de juego.
- Auth: No (público)
- Query params:
  - `sort_by`: `"wins"` (default) | `"level"` | `"lucky"` (mayor CSR) | `"salty"` (menor CSR) | `"streak"` (mayor racha)
  - `limit`: int (default 20)
- Para criterios `lucky`, `salty`, `streak`: requiere mínimo 5 partidas jugadas
- El CSR (Card Score Rating) se calcula en `board_service.get_board_csr()`
- Respuesta: lista con `{ id, name, level, xp, games_played, games_won, win_rate, csr, streak, owner_nickname, owner_vip_tier, is_listed_for_rent, rent_fee_gal, ... }`

---

## Endpoints Relacionados (otros módulos)

### Staking (`/api/v1/staking`)

| Endpoint | Descripción |
|----------|-------------|
| `GET /staking/status` | Estado de staking de todos los Axolotitos del usuario |
| `POST /staking/claim/{axolotito_id}` | Reclama recompensas acumuladas de staking individual |
| `POST /staking/claim-all` | Reclama staking de todos los Axolotitos en lote |

### Códigos Promo (`/api/v1/codes`)

| Endpoint | Descripción |
|----------|-------------|
| `POST /codes/redeem` | Canjea un código de corcholata (`{ code, email }`) — crea `PendingReward` para reclamar al completar el tutorial |

### F2P (`/api/v1/f2p`)

| Endpoint | Descripción |
|----------|-------------|
| `GET /f2p/egg-status` | Estado del huevo durmiente F2P (fragmentos astrales, tope diario) |
| `POST /f2p/watch-reward` | Acredita FRJ y fragmentos astrales por ver una partida (con límite diario) |

### Tutorial (`/api/v1/tutorial`)

| Endpoint | Descripción |
|----------|-------------|
| `POST /tutorial/start` | Inicia el tutorial con el primer Webito del jugador |
| `POST /tutorial/next-step/{incubation_id}` | Avanza al siguiente acto/fase del script de diálogo |
| `POST /tutorial/complete/{incubation_id}` | Completa el tutorial, fija el karma (lucky/salty) y sella el DNA |

### Cenote (`/api/v1/cave`)

| Endpoint | Descripción |
|----------|-------------|
| `GET /cave/status` | Estado actual del Cenote del usuario (nivel, slots, decoraciones, timer de excavación) |
| `POST /cave/expand` | Inicia la expansión al siguiente nivel (paga en FRJ, comienza timer) |
| `POST /cave/expand/accelerate` | Acelera la excavación en curso (paga FRJ extra) |
| `GET /cave/public/{user_id}` | Vista pública del Cenote de otro jugador |
| `POST /cave/visit/{user_id}` | Visita el Cenote de otro jugador (interacción social) |
