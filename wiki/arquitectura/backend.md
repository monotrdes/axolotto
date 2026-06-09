---
tags: [arquitectura, backend, fastapi]
description: "Arquitectura del backend FastAPI: capas, 25 módulos de endpoints, 32 servicios, patrones obligatorios"
last_modified: "2026-06-07"
source_files: ["backend/app/main.py", "backend/app/api/v1/", "backend/app/services/"]
---

# Backend — Arquitectura FastAPI

## Flujo de Request

```
HTTP Request
  → FastAPI Router (main.py)
  → Endpoint (api/v1/endpoints/*.py)   ← Privy JWT verificado aquí
  → Service (services/*.py)            ← Lógica de negocio
  → Model + DB (models/*.py + SQLModel) ← SELECT FOR UPDATE aquí
  → Response
```

## Los 25 Módulos de Endpoints

| Archivo | URL Prefix | Propósito |
|---------|-----------|-----------|
| `bank.py` | `/api/v1/bank` | Wallet, balances, depósito admin, transferencia P2P |
| `user.py` | `/api/v1/auth` | Sync de usuario, inventario, Axolotitos, VIP, P2P market de mascotas |
| `shop.py` | `/api/v1/shop` | Tienda: comprar ítems, Gashapón, cápsulas, boosters, fundidora, VIP tiers |
| `incubation.py` | `/api/v1/incubation` | Incubación de huevos Webito, cuidados (petting/singing/feeding), imprinting |
| `board.py` | `/api/v1/board` | Crear/editar/disolver tableros de Lotería, staking, rental, venta P2P |
| `game.py` | `/api/v1/game` | Partida CPU, alimentar/dormir/despertar Axolotito, equipar cueva |
| `multiplayer.py` | `/api/v1/multiplayer` | Registro en salas, lobby, jackpot, crear sala hosted, unirse, retiro (recall/settle), game-state |
| `checkout.py` | `/api/v1/bank/checkout` | Packs cripto, crear orden de compra, confirmar pago USDC, tipo de cambio |
| `market.py` | `/api/v1/market` | Marketplace P2P de inventario (listar, cancelar, comprar cartas/sobres) |
| `ranking.py` | `/api/v1/ranking` | Rankings de Axolotitos y tableros (nivel, poder, victorias, racha) |
| `metadata.py` | `/api/v1/metadata` | Metadata NFT compatible con OpenSea (Axolotitos y tableros) |
| `legacy.py` | `/api/v1/legacy` | Backers 2021 — reclamar Webitos Fundadores gratuitos |
| `rewards.py` | `/api/v1/rewards` | Reclamar premio Corcholata post-tutorial, ciclo lunar F2P |
| `staking.py` | `/api/v1/staking` | Staking pasivo de Axolotitos: estado, claim individual, claim masivo |
| `codes.py` | `/api/v1/codes` | Redención de códigos promocionales (corcholatas) |
| `f2p.py` | `/api/v1/f2p` | Huevo durmiente F2P: estado del huevo, micro-recompensa por ver partidas |
| `tutorial.py` | `/api/v1/tutorial` | Flujo del tutorial del primer Axolotito (start, next-step, complete) |
| `cave_expansion.py` | `/api/v1/cave` | Expansión del Cenote en 8 niveles (status, expand, accelerate, visita pública) |
| `admin.py` | `/api/v1/admin` | Panel admin: overview, jugadores, economía, simulador de partidas |
| `admin_events.py` | `/api/v1/admin/events` | Gestión de eventos temporales de Modo Manual (CRUD de ManualModeEvent) |
| `events.py` | `/api/v1/events` | Consulta de eventos activos (pública) |
| `whitelist.py` | `/api/v1/whitelist` | Registro en whitelist Fase 1 |
| `leonardo.py` | `/api/v1/leonardo` | Integración Leonardo.ai para generación de arte de cartas |
| `dev.py` | `/api/v1/dev` | Herramientas de desarrollo local (solo entorno dev) |
| `cave_decor.py` | *(sin prefix propio — incluido vía cave_expansion)* | Decoraciones de cueva |

Adicionalmente:
- `backend/app/api/v1/ws/game_ws.py` — WebSocket en `/api/v1/ws` para el modo manual en tiempo real

## Los 32 Servicios

| Servicio | Propósito |
|---------|-----------|
| `bank_service.py` | Operaciones de wallet (obtener, crear, depositar, transferir, acreditar/debitar) |
| `shop_service.py` | Lógica de compra de ítems y apertura de sobres (boosters) |
| `game_service.py` | Motor de partida CPU: simular Lotería, calcular premios, XP, energy |
| `game_logic.py` | Reglas nucleares de Lotería: barajar, marcar, detectar ganadores |
| `multiplayer_service.py` | Scheduler de salas multijugador, asignación, ejecución de rondas y liquidación |
| `manual_game_service.py` | Parámetros del modo manual (ventana de tiempo, delay del gritón, críticos) |
| `web3_service.py` | Llamadas RPC a contratos Solidity (mint NFT, verificar tx on-chain) |
| `checkout_service.py` | Crear/confirmar órdenes de compra USDC, packs y bonus de primera compra |
| `user_service.py` | Sync de usuario, getters de inventario/axolotitos, lógica de mercado P2P de mascotas |
| `incubation_service.py` | Calcular calor de incubación, gestionar fases, eclosión de Axolotito |
| `imprinting_service.py` | Sistema de imprinting: stats base, juegos requeridos, stats finales al eclosionar |
| `board_service.py` | Crear/editar/disolver tableros, CSR score, staking de tablero, rental market |
| `admin_service.py` | Lógica del panel admin: overview, buscar jugadores, simulador de economía |
| `vip_service.py` | Cálculos VIP: tiers, stats, preview de upgrade con crédito proporcional |
| `vip_scheduler.py` | Loop periódico: expirar VIP, generar GAL diario Xochimilco, auto-renew |
| `rarity_service.py` | Calcular rareza dinámica de cartas según circulación en inventarios |
| `drop_service.py` | Drops especiales (booster foil legendario), agregar al inventario |
| `capsule_service.py` | Rolls de cápsulas sorpresa (3 tiers: bronce/plata/oro) y pity counter |
| `forge_service.py` | Fundidor: fusionar cartas en fragmentos, forjar carta específica |
| `staking_service.py` | Acumulación y claim de recompensas pasivas de staking de Axolotitos |
| `cave_service.py` | Equipar/desequipar ítems de cueva por Axolotito |
| `promo_service.py` | Redención de códigos promocionales, crear PendingReward |
| `tutorial_service.py` | Validación y avance del flujo de tutorial (fases 1-5, karma) |
| `f2p_service.py` | Lógica del huevo durmiente F2P, límites diarios, fragmentos astrales |
| `dialogue_engine.py` | Motor de diálogos del tutorial del Axolotito (script por fase/acto) |
| `axo_names.py` | Generador de nombres únicos para Axolotitos |
| `npc_service.py` | Pool de tableros NPC para llenar salas sin suficientes jugadores humanos |
| `pila_service.py` | Cálculos de recuperación de stamina (multiplicador de sueño por stat_stamina) |
| `sal_service.py` | Mecánica de salinidad: penalización de mala suerte proporcional a stat_salinity |
| `lunar_streak_service.py` | Sistema de ciclo lunar: racha de 7 días x 6 lunas, premios por día |
| `daily_reward_service.py` | Lógica de recompensas diarias (servicio base; Ciclo Lunar lo reemplaza) |
| `ws_manager.py` | Gestor de conexiones WebSocket para el modo manual en tiempo real |

## Patrones Obligatorios

### SELECT FOR UPDATE (anti race condition)

```python
# SIEMPRE antes de mutar Wallet o PlayerInventory
wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)

# O directamente en SQLModel:
axo = session.exec(
    select(Axolotito)
    .where(Axolotito.id == axolotito_id)
    .with_for_update()
).first()
```

### ProcessedTransaction (anti replay)

```python
# SIEMPRE antes de acreditar recompensa on-chain
tx_record = ProcessedTransaction(
    tx_hash=tx_hash,
    user_id=user_id,
    purpose="checkout_usdc"
)
session.add(tx_record)
# Si el tx_hash ya existe, esto lanza IntegrityError (UNIQUE constraint)
# → el bloque no se acredita dos veces
session.commit()
```

### SystemRandom (aleatoriedad segura)

```python
# NUNCA usar random.random() ni random.choice() directamente
# SIEMPRE usar SystemRandom
_rng = random.SystemRandom()
resultado = _rng.choice(opciones)
numero = _rng.random()
```

### TransactionLedger (toda mutación de balance)

```python
# Cada cambio de saldo debe escribir una fila en TransactionLedger
session.add(TransactionLedger(
    user_id=user_id,
    amount=monto,
    currency=CurrencyType.FRIJOLITO,
    tx_type=TransactionType.REWARD,
    description="Premio por ganar partida",
))
```

## Cómo Corre el Backend

- **Docker**: `docker-compose up -d` desde la raíz del repo
- **Puerto interno**: 8001 → Nginx reverse proxy → `api.axolot.to`
- **DB**: PostgreSQL en `127.0.0.1:5433` (expuesta desde Docker)
- **Reiniciar todo**: `.\reiniciar.ps1` desde la raíz del repo (PowerShell)
- **Health check**: `GET /api/v1/health`

## Startup Migrations (main.py)

El backend ejecuta migraciones de esquema en `on_startup` antes de servir requests. El patrón estándar es:

```python
# Verificar si la columna existe antes de agregarla
result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tabla';"))
existing_cols = {row[0] for row in result.fetchall()}
if "nueva_columna" not in existing_cols:
    conn.execute(text("ALTER TABLE tabla ADD COLUMN nueva_columna TIPO DEFAULT valor;"))
conn.commit()
```

Schedulers que arranca:
1. `MultiplayerService.start_scheduler_loop()` — ejecuta rondas automáticas cada pocos segundos
2. `vip_scheduler_loop()` — expira VIPs, genera GAL diario, procesa auto-renew

## Modelos de Base de Datos

Ver detalles completos en [[base_de_datos]]
