---
tags: [api, juego, multijugador]
description: "Endpoints del flujo de juego CPU y del sistema multijugador"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/game.py", "backend/app/api/v1/endpoints/multiplayer.py"]
---

# API — Juego y Multijugador

## game.py — Juego CPU y Gestión del Axolotito

Prefijo: `/api/v1/game`

### `POST /game/play`
Simula una partida completa de Lotería contra la casa, consumiendo energía del Axolotito y cobrando la entrada.
- Auth: Si
- Body:
  ```json
  {
    "axolotito_id": int,
    "room_name": "rookie" | "champion",
    "bot_enabled": bool,
    "bot_budget_gal": float,
    "bot_loss_limit_pct": float,
    "bot_profit_limit_pct": float,
    "multiplier": int
  }
  ```
- Salas: `rookie` (10 AXF) / `champion` (50 AXF)
- Delega a `GameService.play_match()`

### `POST /game/axolotitos/{axo_id}/feed`
Alimenta al Axolotito, deduciendo FRJ de la wallet y restaurando energía.
- Auth: Si
- Body: `{ food_type: "pellet" | "shrimp" }`
- Pellet: restaura ~15 energía / Shrimp: restaura ~60 energía

### `POST /game/axolotitos/{axo_id}/sleep`
Pone al Axolotito a dormir para restaurar energía completa gratis tras un cooldown.
- Auth: Si
- Cooldown proporcional a `stat_stamina` (multiplicador de `pila_service`)

### `POST /game/axolotitos/{axo_id}/wake`
Despierta al Axolotito si el cooldown de sueño ya expiró.
- Auth: Si
- Respuesta: energía restaurada a máximo si el timer expiró

### `GET /game/axolotitos/{axo_id}/cave`
Devuelve los ítems de cueva equipados y la capacidad de slots del Axolotito.
- Auth: Si

### `POST /game/axolotitos/{axo_id}/cave/equip`
Equipa un ítem de cueva desde el inventario del jugador al Axolotito.
- Auth: Si
- Body: `{ item_id: int }`

### `POST /game/axolotitos/{axo_id}/cave/unequip`
Retira un ítem de la cueva del Axolotito y lo regresa al inventario.
- Auth: Si
- Body: `{ item_id: int }`

---

## multiplayer.py — Salas Multijugador

Prefijo: `/api/v1/multiplayer`

La moneda del multijugador es **FRJ exclusivamente** — AXF está bloqueado por compliance.

### `GET /multiplayer/unread-logs`
Devuelve los resultados de partidas no leídas y los marca como notificados.
- Auth: Si
- Respuesta: lista de `{ id, outcome, axo_name, room_name, net_gal, xp_gained }`

### `POST /multiplayer/register`
Inscribe un Axolotito y sus tableros en una sala de espera automática. Retiene el presupuesto en escrow.
- Auth: Si
- Body:
  ```json
  {
    "axolotito_id": int,
    "room_type": "rookie" | "champion",
    "boards": [int, ...],      // 1 a 3 board IDs
    "budget_gal": float,
    "loss_limit_pct": float,
    "profit_limit_pct": float
  }
  ```
- Validaciones: Axolotito en estado `idle`, energía >= 10, tableros propios o rentados, presupuesto suficiente
- Anti-sybil: 1 registro activo por usuario/billetera por tipo de sala, máx 5 tableros por usuario en la sala
- El presupuesto pasa a escrow (`axo.escrow_balance_gal`)

### `GET /multiplayer/lobby`
Retorna las salas en espera con detalles de Axolotitos y tableros registrados.
- Auth: No (público)
- Incluye: `seconds_until_start` calculado por cantidad de tableros y tiempo transcurrido

### `GET /multiplayer/jackpot`
Retorna el acumulado del Jackpot de Oro e historial de los últimos 10 ganadores.
- Auth: No (público)
- Respuesta: `{ current_amount, seed_amount, history: [{axo_name, user_nickname, amount_won, cards_drawn_count, won_at}] }`

### `POST /multiplayer/create-room`
Crea una sala hosted por el jugador desde su mesa de la cueva.
- Auth: Si
- Body:
  ```json
  {
    "name": str,
    "game_type": "lotería_clásica" | "lotería_rápida",
    "buy_in_frj": float,        // 10 a 1000
    "max_players": int,         // 2 a 8
    "visibility": "public" | "friends" | "private",
    "speed": "normal" | "rápido" | "turbo",
    "win_patterns": ["line", "cuadrito", ...],
    "password": str | null
  }
  ```
- La sala aparece en el lobby bajo "Salas de Jugadores"

### `GET /multiplayer/player-rooms`
Lista las salas hosted por jugadores visibles públicamente.
- Auth: No (público)
- Query param: `?search=` para filtrar por nombre o nickname del host
- Respuesta: `{ rooms: [{id, name, host_name, buy_in_frj, max_players, current_players, speed, win_patterns, has_password, ...}] }`

### `POST /multiplayer/join-room/{room_id}`
Unirse a una sala hosted por un jugador.
- Auth: Si
- Body:
  ```json
  {
    "axolotito_id": int,
    "boards": [int, ...],
    "budget_gal": float,
    "loss_limit_pct": float,
    "profit_limit_pct": float,
    "password": str | null
  }
  ```
- Valida contraseña si la sala tiene una
- Mueve fondos a escrow (FRJ)

### `POST /multiplayer/recall`
Retira al Axolotito de la sala de espera o lo marca para salir al terminar la partida actual.
- Auth: Si
- Query param o body: `axolotito_id: int`
- Si la sala aún está en `waiting`: retiro inmediato + estado `waiting_settlement`
- Si ya está jugando: establece `axo.wants_to_stop = True`

### `POST /multiplayer/settle`
Realiza el corte de caja del Axolotito en estado `waiting_settlement`. Devuelve el escrow a la wallet.
- Auth: Si
- Query param o body: `axolotito_id: int`
- Calcula rendimiento neto, otorga Puntos de Afecto (loyalty), pone el Axolotito a dormir
- Usa `SELECT FOR UPDATE` en el Axolotito antes de liquidar

### `GET /multiplayer/game-state/{axolotito_id}`
Devuelve el estado en vivo de la partida para el visor de modo auto (AFK/espectador).
- Auth: Si
- El frontend hace polling cada ~2 segundos para animar el tablero tick-a-tick
- Respuesta:
  ```json
  {
    "phase": "playing" | "finished",
    "room_name": str,
    "turns_played": int,
    "cards_drawn": [int, ...],
    "player_boards": [{ "board_id", "marked_indices", "missed_indices" }],
    "bot_boards": [{ "board_id", "marked_count" }],
    "tension_level": "low" | "medium" | "high" | "critical",
    "escrow_balance": float,
    "current_card": { "card_id", "numero", "name" } | null
  }
  ```

### `GET /multiplayer/manual-env/{axolotito_id}`
Devuelve los parámetros de entorno para el modo manual (ventana de tiempo, delay del gritón, pistas visuales, críticos).
- Auth: Si
- Modulados por los stats del Axolotito
- Respuesta: `{ axolotito_id, axolotito_name, stats: {suerte, ojo, pila, sal}, env: {...}, crit_probability_at_100_luck }`

---

## WebSocket — Modo Manual

URL: `ws://localhost:8001/api/v1/ws/...`

El modo manual de Lotería en tiempo real usa WebSocket (gestionado por `ws_manager.py`).
El frontend se conecta para recibir eventos de carta cantada, marcado del jugador y resultado final.

---

## Lógica de Salas Automáticas

Las salas `rookie_pool` y `champion_abyss` son gestionadas por el scheduler de `multiplayer_service.py`:

1. El scheduler corre en loop periódico
2. Cuando hay suficientes tableros en espera (o timeout), inicia la partida
3. Distribuye resultados, actualiza escrow, marca Axolotitos con `waiting_settlement`
4. El jugador llama `/settle` para recuperar fondos

El pool de NPCs (`npc_service.py`) rellena salas cuando no hay suficientes jugadores humanos.
