---
tags: [api, banco, economia, shop]
description: "Endpoints de banco (wallet), checkout (crypto), y tienda — operaciones económicas"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/bank.py", "backend/app/api/v1/endpoints/checkout.py", "backend/app/api/v1/endpoints/shop.py"]
---

# API — Banco, Checkout y Tienda

## bank.py — Wallet y Balances

Prefijo: `/api/v1/bank`

### `GET /bank/wallet/{user_id}`
Consulta el saldo del jugador.
- Auth: Si (solo puede consultar su propio wallet)
- Respuesta: `{ axofichas, frijolitos, axogemas (alias), gemas_alga (alias), fragmentos: {comunes, raros, epicos, legendarios} }`

### `POST /bank/admin/deposit`
Deposita moneda desde la nada (para pruebas y recargas manuales SPEI).
- Auth: Admin (requiere `X-Admin-Token`)
- Body: `{ user_id, amount, currency, description }`
- Llama `BankService.admin_deposit()`

### `POST /bank/transfer`
Transfiere fondos a otro jugador, cobrando comisión de la casa.
- Auth: Si
- Rate limit: 5/minuto
- Body: `{ sender_id, receiver_id, amount, currency }`
- Llama `BankService.transfer_p2p()`

---

## checkout.py — Crypto Onramp

Prefijo: `/api/v1/bank/checkout`

### `GET /bank/checkout/packs`
Catálogo de packs de AXF con precios USD/MXN y oferta flash del día.
- Auth: No (público)
- Respuesta: `{ packs: [...], usd_mxn: float }`
- Los packs disponibles: `huevito`, `axolotito`, `cenote`, `jackpot`

### `GET /bank/checkout/exchange-rate`
Tipo de cambio USD→MXN actualizado (llama API externa, TTL 1 hora).
- Auth: No (público)
- Respuesta: `{ usd_mxn, updated_at }`

### `POST /bank/checkout/crypto`
Crea una orden de compra de AXF con USDC.
- Auth: Si
- Rate limit: 10/minuto
- Body: `{ pack_id: str }`
- Respuesta: `{ order_id, pay_to (treasury address), usdc_amount, axg_amount, bonus_pct, expires_at, status }`
- La orden expira en 30 minutos

### `GET /bank/checkout/crypto/{order_id}`
Consulta el estado actual de la orden de compra.
- Auth: Si (solo puede ver su propia orden)
- Respuesta: `{ order_id, status, pack_id, axg_amount, bonus_pct, tx_hash_payment, tx_hash_mint, expires_at, completed_at }`

### `POST /bank/checkout/crypto/{order_id}/confirm`
El frontend informa el `tx_hash` después de enviar USDC. El backend verifica on-chain y mintea AXF si todo es correcto.
- Auth: Si
- Rate limit: 5/minuto
- Body: `{ tx_hash: "0x..." }` (pattern: `^(0x[0-9a-fA-F]{64}|0x_mock.*)$`)
- Replay protection: inserta en `ProcessedTransaction` (UNIQUE) antes de acreditar
- Respuesta: `{ status, axg_amount, bonus_pct, tx_hash_mint, polygon_scan }`

---

## shop.py — Tienda

Prefijo: `/api/v1/shop`

### `GET /shop/items`
Catálogo completo de ítems activos con stock vendido y cantidad propia del usuario.
- Auth: No (público; opcionalmente `?user_id=` para datos personalizados)
- Incluye: disponibilidad de nidos (slots de incubación) para ítems tipo EGG

### `POST /shop/buy`
Compra un ítem del catálogo usando AXF o FRJ.
- Auth: Si
- Body: `{ item_id: int, payment_currency: CurrencyType }`
- Delega a `ShopService.buy_item()`

### `GET /shop/activity`
Últimas 15 compras globales en la tienda (boosters y huevos).
- Auth: No (público)
- Respuesta: lista de `{ id, nickname, description, amount, currency, created_at }`

### `GET /shop/cards`
Catálogo maestro de las 54 cartas de Lotería con rareza dinámica según circulación.
- Auth: No (público)
- Respuesta: lista de cartas con `dynamic_rarity` y `circulation`

### `POST /shop/gashapon/roll`
Lanza el Gashapón de accesorios consumiendo FRJ.
- Auth: Si
- Body: `{ roll_type: "common" | "premium" }`
- Costo: 1,000 FRJ (common) / 2,500 FRJ (premium)
- Probabilidades common: 70% común, 25% raro, 5% épico
- Probabilidades premium: 45% raro, 45% épico, 10% legendario
- Drop especial: posibilidad de Booster Foil Legendario en cualquier tier

### `GET /shop/capsule/pity`
Retorna los contadores de pity por tier del sistema de cápsulas.
- Auth: Si
- Respuesta: `{ pity: { bronce, plata, oro } }`

### `POST /shop/capsule/roll`
Lanza una cápsula sorpresa de un tier específico (bronce/plata/oro).
- Auth: Si
- Body: `{ tier: "bronce" | "plata" | "oro", use_capsule: bool }`
- Si `use_capsule=true`, consume una cápsula del inventario en lugar de FRJ

### `POST /shop/capsule/triple-suerte`
Lanza las 3 cápsulas a la vez con descuento (ahorra 400 FRJ).
- Auth: Si

### `GET /shop/capsule/feed`
Últimos 15 rolls de cápsulas globales — "La Suertuda".
- Auth: No (público)

### `GET /shop/vip/tiers`
Lista de tiers VIP con precios y beneficios.
- Auth: No (público)
- Fuente canónica: `VIP_CONFIG` en `config.py`

### `GET /shop/vip/stats`
Número de usuarios con membresía VIP activa.
- Auth: No (público)

### `GET /shop/vip/upgrade-preview`
Calcula el precio de upgrade VIP con crédito proporcional del tier actual.
- Auth: Si
- Query param: `target_tier`

### `POST /shop/booster/open`
Abre un sobre sellado del inventario del usuario, generando 7 cartas aleatorias.
- Auth: Si
- Body: `{ item_id: int }`
- Delega a `ShopService.open_booster()`

### `POST /shop/melter/melt`
Funde 5 copias de una carta para obtener fragmentos y una carta aleatoria de rareza superior.
- Auth: Si
- Body: `{ card_id: int, is_first_edition: bool }`

### `POST /shop/melter/forge`
Forja una carta específica consumiendo fragmentos de su rareza y FRJ.
- Auth: Si
- Body: `{ target_card_id: int }`

---

## Constantes Económicas Relacionadas

| Operación | Costo |
|-----------|-------|
| Gashapón common | 1,000 FRJ |
| Gashapón premium | 2,500 FRJ |
| Tablero aleatorio | 25 FRJ |
| Tablero manual | 50 FRJ |
| Disolver tablero | 50 FRJ |
| Pack AXF "huevito" | ~$5 USD → 100 AXF |
| Pack AXF "axolotito" | ~$25 USD → 600 AXF |
| Pack AXF "cenote" | ~$50 USD → 1,500 AXF |
| Pack AXF "jackpot" | ~$125 USD → 4,000 AXF |

Ver [[../arquitectura/backend]] para las constantes completas en `config.py`.
