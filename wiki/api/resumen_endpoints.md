---
tags: [api, endpoints]
description: "Resumen de los 25 módulos de endpoints de la API REST de Axolotto"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/"]
---

# API REST — Resumen de Endpoints

## Base URL

- Desarrollo: `http://localhost:8001/api/v1/`
- Producción: `https://api.axolot.to/api/v1/`
- Health check: `GET /api/v1/health`

## Autenticación

Todos los endpoints protegidos requieren el header:

```
X-Privy-Token: <privy_jwt_token>
```

Los endpoints marcados como "No (público)" devuelven datos sin verificar identidad.

## Módulos de Endpoints

| Módulo | URL Prefix | Propósito | Requiere Auth |
|--------|-----------|-----------|--------------|
| `bank.py` | `/api/v1/bank` | Wallet, balances, depósito admin, transferencia P2P | Si |
| `user.py` | `/api/v1/auth` | Sync usuario, inventario, Axolotitos, VIP, mercado de mascotas | Si |
| `shop.py` | `/api/v1/shop` | Tienda, Gashapón, cápsulas, boosters, fundidora, VIP | Mixto |
| `incubation.py` | `/api/v1/incubation` | Incubación de Webitos, cariñitos, imprinting, eclosión | Si |
| `board.py` | `/api/v1/board` | Crear/editar/disolver tableros, staking, rental, venta | Si |
| `game.py` | `/api/v1/game` | Partida CPU, alimentar/dormir/despertar Axolotito, cueva | Si |
| `multiplayer.py` | `/api/v1/multiplayer` | Registro, lobby, jackpot, salas hosted, game-state, recall/settle | Mixto |
| `checkout.py` | `/api/v1/bank/checkout` | Packs cripto, crear/confirmar orden USDC, tipo de cambio | Mixto |
| `market.py` | `/api/v1/market` | Marketplace P2P de inventario (cartas, sobres) | Si |
| `ranking.py` | `/api/v1/ranking` | Leaderboards de Axolotitos y tableros | No (público) |
| `metadata.py` | `/api/v1/metadata` | Metadata NFT (OpenSea-compatible) para Axolotitos y tableros | No (público) |
| `rewards.py` | `/api/v1/rewards` | Reclamar Corcholata post-tutorial, Ciclo Lunar F2P | Si |
| `staking.py` | `/api/v1/staking` | Staking pasivo: estado, claim individual y masivo | Si |
| `codes.py` | `/api/v1/codes` | Redención de códigos promocionales (corcholatas) | Si |
| `f2p.py` | `/api/v1/f2p` | Huevo durmiente F2P, micro-recompensa por ver partidas | Si |
| `tutorial.py` | `/api/v1/tutorial` | Flujo del tutorial: start, next-step, complete | Si |
| `cave_expansion.py` | `/api/v1/cave` | Cenote: status, expand, accelerate, cueva pública | Mixto |
| `admin.py` | `/api/v1/admin` | Panel admin: overview, jugadores, economía, simulador | Admin |
| `admin_events.py` | `/api/v1/admin/events` | Gestión de eventos de Modo Manual | Admin |
| `events.py` | `/api/v1/events` | Consulta de eventos activos | No (público) |
| `whitelist.py` | `/api/v1/whitelist` | Registro en whitelist Fase 1 | Si |
| `legacy.py` | `/api/v1/legacy` | Reclamar Webitos Fundadores (backers 2021) | Si |
| `leonardo.py` | `/api/v1/leonardo` | Generación de arte con Leonardo.ai | Admin |
| `dev.py` | `/api/v1/dev` | Herramientas de desarrollo (solo entorno dev) | Dev |
| `game_ws.py` (WS) | `/api/v1/ws` | WebSocket para modo manual en tiempo real | Si |

## Notas de Autenticación

- **Admin**: requiere además el header `X-Admin-Token: <TRIDY_API_KEY>` configurado en `settings.py`
- **Público**: devuelven datos sin token (rankings, metadata NFT, catálogo de tienda, jackpot)
- **Mixto**: algunos sub-endpoints del módulo son públicos y otros requieren auth

---

Detalles por dominio en:

- [[banco_y_economia]] — bank, checkout, shop
- [[juego_y_multijugador]] — game, multiplayer
- [[usuarios_y_perfil]] — user, rewards, ranking
