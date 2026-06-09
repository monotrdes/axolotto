---
tags: [arquitectura, frontend, nextjs]
description: "Arquitectura del frontend Next.js: rutas, componentes principales, hooks clave"
last_modified: "2026-06-07"
source_files: ["frontend/app/", "frontend/components/", "frontend/hooks/"]
---

# Frontend — Arquitectura Next.js

## Rutas (App Router)

| Ruta | Archivo | Propósito |
|------|---------|-----------|
| `/` | `frontend/app/page.tsx` | Landing page con social login (Privy) |
| `/play` | `frontend/app/play/page.tsx` | Hub principal del juego |
| Layout | `frontend/app/layout.tsx` | Root layout, PrivyProvider, estilos globales |

## Componentes Principales

| Componente | Archivo | Propósito |
|-----------|---------|-----------|
| `PlayMode` | `components/PlayMode.tsx` | Componente core de gameplay CPU: board, estado de partida, gritón |
| `CpuGameWrapper` | `components/CpuGameWrapper.tsx` | Wrapper del modo CPU que orquesta `PlayMode` con hooks de juego |
| `MultiplayerLobby` | `components/MultiplayerLobby.tsx` | Lobby de salas multijugador: registro, listado, estado de espera |
| `Store` | `components/Store.tsx` | Tienda in-game: catálogo de ítems, compra, filtros |
| `Inventory` | `components/Inventory.tsx` | Inventario del jugador: cartas, sobres, consumibles, accesorios |
| `BoardEditor` | `components/BoardEditor.tsx` | Editor de tableros: selección de 16 cartas, vista previa 4x4 |
| `Santuario` | `components/Santuario.tsx` | Zona Nido: gestión de Axolotitos, cueva, staking |
| `Gashapon` | `components/Gashapon.tsx` | Máquina Gashapón: tiradas de cápsulas con animación |
| `DailyClaim` | `components/DailyClaim.tsx` | Reclamación de recompensa diaria del Ciclo Lunar |
| `CryptoCheckout` | `components/CryptoCheckout.tsx` | Flujo de compra cripto: selección de pack, MoonPay, confirmación |
| `MarketP2P` | `components/MarketP2P.tsx` | Marketplace P2P de inventario y Axolotitos |
| `RentalMarket` | `components/RentalMarket.tsx` | Mercado de alquiler de tableros |
| `Rankings` | `components/Rankings.tsx` | Leaderboards de Axolotitos y tableros |
| `VipModal` | `components/VipModal.tsx` | Modal de compra/upgrade de membresía VIP |
| `CardMelter` | `components/CardMelter.tsx` | Fundidora: fusionar cartas duplicadas en fragmentos |
| `BirthCeremony` | `components/BirthCeremony.tsx` | Animación de eclosión del Webito en Axolotito |
| `ImprintingProgress` | `components/ImprintingProgress.tsx` | Barra de progreso del sistema de imprinting |
| `AxoStatusBar` | `components/AxoStatusBar.tsx` | Barra de estado del Axolotito activo: energía, stats, botones rápidos |
| `CodeEntryPanel` | `components/CodeEntryPanel.tsx` | Panel de entrada de códigos promocionales (corcholatas) |
| `CodeRedemption` | `components/CodeRedemption.tsx` | Flujo completo de canje de corcholata |
| `HostingSetupModal` | `components/HostingSetupModal.tsx` | Modal para configurar una sala hosted por jugador |
| `ManualModeButton` | `components/ManualModeButton.tsx` | Botón de acceso al modo manual (WebSocket) |
| `PrivyProviderWrapper` | `components/PrivyProviderWrapper.tsx` | Wrapper de `PrivyProvider` con configuración de cadenas |
| `WizardDots` | `components/WizardDots.tsx` | Indicador de pasos (dots) para wizards y onboarding |

### Subdirectorios de componentes

- `components/screens/` — Pantallas completas de flujo de juego (GameScreen, etc.)
- `components/world/hud/` — HUD del mundo: `MochilaFloating` (mochila flotante multi-tab)
- `components/inventory/` — Subcomponentes de inventario (`ItemGrid`, etc.)
- `components/ui/` — UI compartida: `CalledCardsHistory`, `MiniGriton`

## Hooks Clave

| Hook | Archivo | Propósito |
|------|---------|-----------|
| `useCpuGame` | `hooks/useCpuGame.ts` | Estado completo de la partida CPU: llamar carta, marcar, verificar ganador |
| `useManualGame` | `hooks/useManualGame.ts` | Lógica del modo manual: ventana de tiempo, gritón, críticos |
| `useAutoGame` | `hooks/useAutoGame.ts` | Modo automático (bot): polling del estado de partida multijugador |
| `useInventory` | `hooks/useInventory.ts` | Fetch y gestión del inventario del jugador |
| `useStore` | `hooks/useStore.ts` | Datos del catálogo de la tienda, filtros activos |
| `useWebSocket` | `hooks/useWebSocket.ts` | Conexión WebSocket al juego manual en tiempo real |
| `useBlockchainEvents` | `hooks/useBlockchainEvents.ts` | Listeners de eventos on-chain (Viem) para actualizar estado de wallet |
| `useMoonPayWidget` | `hooks/useMoonPayWidget.ts` | Integración del widget MoonPay para onramp USDC |
| `useVip` | `hooks/useVip.ts` | Estado VIP del usuario: tier, expiración, claim de GAL diario |
| `useEconomyToast` | `hooks/useEconomyToast.ts` | Toasts de cambios de saldo (AXF/FRJ ganados o gastados) |
| `useUnboxing` | `hooks/useUnboxing.ts` | Animación de apertura de sobre booster |
| `useAudioTension` | `hooks/useAudioTension.ts` | Audio adaptativo según nivel de tensión de la partida |
| `useTabVisibility` | `hooks/useTabVisibility.ts` | Detecta si la pestaña está activa para pausar pollings innecesarios |

## Sistema de Navegación

5 zonas en el dock principal:

1. **Nido (Santuario)** — breeding, cueva Cenote, staking de Axolotitos
2. **Tianguis (Store)** — tienda, Gashapón, boosters, mercado P2P
3. **Sala (Play Mode)** — juego CPU, modo manual, multijugador
4. **Pirámide (Rankings)** — leaderboards de Axolotitos y tableros
5. **Cápsulas** — sistema Gashapon y ciclo lunar

La mochila (backpack) flotante es accesible desde cualquier zona mediante `MochilaFloating`.

## Stack Técnico

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Next.js | 16.2 | App Router, SSR, rutas |
| React | 19 | UI |
| TypeScript | 5 | Tipos |
| Tailwind CSS | 4 | Estilos |
| Viem | 2.47 | Web3 — lectura/escritura on-chain (NO ethers.js) |
| Privy `@privy-io/react-auth` | — | Auth: social login + wallets auto-custodiales |
| WebSocket nativo | — | Modo manual en tiempo real |
| MoonPay widget | — | Onramp USDC (fiat → cripto) |

## Cómo Corre el Frontend

- **PM2**: `pm2 start ecosystem.config.js` o `pm2 restart frontend`
- **Puerto**: 3000
- **Variables de entorno**: `frontend/env.local` (o `frontend/.env.local`)
- **Variables clave**: `NEXT_PUBLIC_CONTRACT_*` para direcciones de contratos, `NEXT_PUBLIC_PRIVY_APP_ID`
- **Reiniciar todo**: `.\reiniciar.ps1` desde la raíz del repo (PowerShell)
