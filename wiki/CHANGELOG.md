---
tags: [changelog]
description: "Historial de todos los cambios al wiki con fecha, motivo, autor y referencia al código"
last_modified: "2026-06-11"
---

# Wiki Changelog — Axolotto

> Registra CADA vez que se actualiza un valor en el wiki. Un agente AI que actualice precios, stats, o reglas DEBE añadir una entrada aquí antes del commit.

## Formato de entrada

```
## YYYY-MM-DD | archivo_modificado.md | Campo o sección cambiada
- **Campo**: nombre exacto del campo o valor
- **Anterior**: valor o texto previo (pon "—" si es creación inicial)
- **Nuevo**: valor o texto actualizado
- **Motivo**: razón del cambio (ej: "ajuste de balance", "corrección de bug", "nuevo feature")
- **Autor**: Claude / DeepClaude / AGY / [usuario]
- **Fuente en código**: `backend/app/core/prices.py:WEBITO_PRICES` o commit hash
```

---

## 2026-06-11 | frontend mundo papel picado + decoración del Cenote | Merge de task-1781159264-84 a dev
- **Campo**: Mundo 2.5D papel picado (PixiJS v8 + GSAP) detrás de `NEXT_PUBLIC_PAPER_WORLD`; sistema de decoración del Cenote (slots tipados AMBIENTE/LUZ/MESA/MANTEL/SILLAS/FONDO/ESPECIAL).
- **Anterior**: El mundo vivía solo en la rama `task/task-1781159264-84-rediseno-visual-papel-picado`; en dev quedaba un cableado viejo (decoración v1 con mocks/localStorage) y el router `cave_decor` sin montar (GET /cave/decorations → 404).
- **Nuevo**: Fases 0-2 mergeadas: motor Pixi, Santuario (nidos dinámicos, sala con slots de decoración comprables con FRJ, embarcadero social), Tianguis, Pirámide. Router `cave_decor` registrado en main.py; `DecorSlotPanel` + Bazar del Cenote; locking de partida (isGameLocked) integrado a los hotspots del mundo. Sin flag, el juego se comporta igual que antes.
- **Motivo**: Merge temprano a dev para evitar divergencia mayor con el trabajo activo en dev (conflictos crecientes en page.tsx).
- **Autor**: Claude
- **Fuente en código**: frontend/components/world/, backend/app/api/v1/endpoints/cave_decor.py, backend/app/main.py (merge de `248c178`)

## 2026-06-11 | backend/app/services/ws_manager.py | Concurrencia Multi-Ventana y Desplazamiento de WebSocket (task-89)
- **Campo**: `GameWSManager.connect`, `GameWSManager.reconnect`, `GameWSManager.disconnect` y `manual_game_ws`
- **Anterior**: Conexiones WebSocket concurrentes para el mismo usuario y sala pisaban la propiedad del WS en el estado, y cualquier desconexión (incluso de pestañas antiguas) cerraba la sesión activa del usuario forzando AFK kick erróneo.
- **Nuevo**: Implementado desplazamiento activo de WebSocket con código de salida `4008` (session replaced) y validación de instancia de WebSocket física al desconectar para ignorar cierres de conexiones obsoletas.
- **Motivo**: Control de concurrencia y prevención de bugs por session splitting en multijugador.
- **Autor**: AGY
- **Fuente en código**: backend/app/services/ws_manager.py, backend/app/api/v1/ws/game_ws.py (commit `d3bf66e`)

## 2026-06-11 | backend/app/core/prices.py | Remoción de consumibles de calor (task-78)
- **Campo**: `CONSUMABLE_PRICES`
- **Anterior**: Contenía los precios de "gotas" (200 FRJ) y "lampara" (200 AXF).
- **Nuevo**: Se eliminaron los consumibles de calentamiento ("gotas" y "lampara") del catálogo y configuración de precios.
- **Motivo**: Simplificación y remoción del sistema de calor/congelamiento en la crianza.
- **Autor**: AGY
- **Fuente en código**: backend/app/core/prices.py, backend/app/scripts/seed_catalog.py

## 2026-06-10 | backend/ + contracts/ + frontend/ | Integración de task-77 y task-79 en dev

### backend/app/core/config.py — VIP_CONFIG consolidado
- **Campo**: `VIP_CONFIG` (precios de coral/dorado/axolite, gal_daily y bonos multiplicadores)
- **Anterior**: Configuraciones VIP con bonos de multijugador activos (15.00% en axolite)
- **Nuevo**: VIP_CONFIG unificado con precios ajustados (50/120/300 AXF), recompensas diarias reducidas (20/50/130 FRJ) y sin multiplicadores de jackpot o multijugador (`multiplayer_discount_bps: 0`) por balance de economía.
- **Motivo**: Rebalance y seguridad de economía en multijugador, alineado con fixes de VULN-05.
- **Autor**: AGY / tridyland-glitch
- **Fuente en código**: commits `3e0b55d` y `f2fc8be`

### backend/ + contracts/src/MarketEscrow.sol — Escrow P2P y pagos simulados (task-77)
- **Campo**: `MarketEscrow.sol`, `ReconciliationService`, `MockPaymentGateway`
- **Anterior**: — (No existían)
- **Nuevo**: Contrato `MarketEscrow` para custodia on-chain de NFT y liberación via paymentRef; backend con flujos de pagos fiat y reconciliación contra blockchain en cuarentena de 72h.
- **Motivo**: Implementación del Tianguis P2P con escrow seguro de activos.
- **Autor**: AGY / tridyland-glitch
- **Fuente en código**: commit `3e0b55d` (task-77 merge)

### frontend/components/tutorial/ + docs/ — Refactor a juego manual (task-79)
- **Campo**: `ActGame.tsx`, `useTutorialManualGame.ts`, plan del tutorial
- **Anterior**: Flujo de tutorial vulnerable a loops de distracción infinitos
- **Nuevo**: Refactorización del Acto 6 del tutorial para el modo manual vs CPU, implementando el hook `useTutorialManualGame` y controlando las transiciones del loop de juego.
- **Motivo**: Corrección de loop infinito y estabilidad en onboarding de usuarios.
- **Autor**: AGY / tridyland-glitch
- **Fuente en código**: commit `b4e9c83` (task-79 merge)

---

## 2026-06-07 | wiki/ai/ | Workflow obligatorio del taskboard

### agent_routing.md — Nueva sección "Workflow Obligatorio del Taskboard"
- **Campo**: Sección nueva (antes no existía)
- **Anterior**: —
- **Nuevo**: Guía completa del ciclo de vida de tareas en el taskboard: crear tarjeta con todos los badges (#ID, ⚡ agente, categoría, prioridad, 📄 doc, 🧪 test), comandos PS1 con ejemplos reales, cómo vincular plan doc en `docs/` para el Doc Viewer, cuándo crear tarjeta y cuándo no
- **Motivo**: Los agentes AI necesitan saber que TODA tarea debe tener tarjeta en el taskboard, qué badges usar, y cómo activar el badge 📄 Doc con link funcional al Doc Viewer
- **Autor**: Claude
- **Fuente en código**: `tools/taskboard/bin/taskboard.ps1`, `tools/taskboard/server.py`

### critical_rules.md — Regla 11 añadida
- **Campo**: Regla #11 (Taskboard obligatorio)
- **Anterior**: 10 reglas
- **Nuevo**: 11 reglas — la #11 exige tarjeta en taskboard para toda tarea
- **Motivo**: Formalizar el workflow del taskboard como regla crítica obligatoria
- **Autor**: Claude

### QUICK_START.md — Sección "Workflow Obligatorio" añadida
- **Campo**: Nueva sección de taskboard en QUICK_START
- **Anterior**: Solo stack, monedas y archivos importantes
- **Nuevo**: 3 comandos esenciales + link a guía completa
- **Autor**: Claude

---

## 2026-06-10 | backend/ + contracts/src/Sobrecito.sol | VULN-07, VULN-08, VULN-09: Remediación seguridad media

### web3_service.py + checkout_service.py + config.py — VULN-07: Bypass de pagos desacoplado de BLOCKCHAIN_MODE
- **Campo**: `verify_usdc_payment`, `confirm_payment`, `Settings.ALLOW_DEV_PAYMENTS`
- **Anterior**: Mock hashes y tx vacíos se aceptaban como pago válido si `BLOCKCHAIN_MODE == "local"` (default)
- **Nuevo**: Nuevo flag `ALLOW_DEV_PAYMENTS: bool = False` independiente; el bypass de pagos ya NO se activa con el modo local por defecto
- **Motivo**: VULN-07 Auditoría 2026-06-09 — deploy accidental con defaults podía regalar AXF premium
- **Autor**: Claude Sonnet 4.6
- **Fuente en código**: commit `cb0e78f`

### contracts/src/Sobrecito.sol — VULN-08: abrirSobrecito protegido con onlyController
- **Campo**: `function abrirSobrecito(uint256 fase) external`
- **Anterior**: Función pública — cualquier holder podía quemar su sobrecito on-chain sin pasar por el backend
- **Nuevo**: `external onlyController` — solo el GameController puede abrir sobrecitos; previene pérdida de activos sin contraparte
- **Motivo**: VULN-08 Auditoría 2026-06-09 — jugador podía quemar sobre y no recibir cartas
- **Autor**: Claude Sonnet 4.6
- **Fuente en código**: commit `cb0e78f`

### staking_service.py — VULN-09: claim_all_staking respeta límite de slots
- **Campo**: `claim_all_staking` — query de axolotitos a reclamar
- **Anterior**: Iteraba TODOS los Axolotitos del usuario ignorando `get_staking_slots(user)`
- **Nuevo**: `ORDER BY id LIMIT get_staking_slots(user)` — solo los primeros N axolotitos (por id) acumulan staking
- **Motivo**: VULN-09 Auditoría 2026-06-09 — rendimiento pasivo desbalanceado por bypass del cap de slots
- **Autor**: Claude Sonnet 4.6
- **Fuente en código**: commit `cb0e78f`

---

## 2026-06-10 | backend/app/services/multiplayer_service.py | VULN-05: Fix inflación de premios

### multiplayer_service.py — Liquidación multijugador con invariante de conservación de fondos
- **Campo**: Reparto de Premio 1, Premio 2 y Jackpot bonus en `simulate_multiplayer_match`
- **Anterior**: `luck_bonus` y `vip_bonus` se sumaban ENCIMA del share base (fondos fantasma — no respaldados en ningún vault)
- **Nuevo**: Opción A (in-pool bonuses) — bonuses redistribuyen DENTRO del pool con aritmética basis-points. Si Σ raw > pool → normalización proporcional; remanente a tesorería. Invariante: `Σ premios ≤ (premio_1_pool + premio_2_pool)`
- **Motivo**: VULN-05 Auditoría de Seguridad Web3 2026-06-09 — inflación de FRJ por bonuses sin respaldo
- **Autor**: Claude Sonnet 4.6
- **Fuente en código**: commit `aebad48` — `multiplayer_service.py` + 5 tests en `test_prize_invariants.py`

---

## 2026-06-07 | wiki/ | Creación inicial del vault Obsidian

### 00-INDEX.md — Índice maestro
- **Campo**: Creación inicial
- **Anterior**: —
- **Nuevo**: Índice con navegación para AI agents y jugadores
- **Motivo**: Configuración inicial del vault Obsidian para onboarding AI en <400 tokens y docs para jugadores
- **Autor**: Claude
- **Fuente en código**: Rama `feature/multiplayer-redesign`, tarea `task-1780896719-51`

### wiki/ai/ — Contexto para AI agents
- **Campo**: 4 archivos (QUICK_START, critical_rules, gotchas, agent_routing)
- **Anterior**: —
- **Nuevo**: Creación inicial desde CLAUDE.md y memory/
- **Motivo**: Reducir tokens de exploración de ~15,000 a ~2,000 por sesión AI
- **Autor**: Claude (Agente A1)
- **Fuente en código**: `CLAUDE.md`, `memory/feedback_critical_rules.md`, `memory/project_gotchas.md`

### wiki/economia/ — Precios y economía
- **Campo**: 4 archivos (monedas, tablas_precios, vip_tiers, economia_general)
- **Anterior**: —
- **Nuevo**: Creación inicial desde config.py y prices.py
- **Motivo**: Centralizar todas las tablas de precios para referencia rápida
- **Autor**: Claude (Agente A2)
- **Fuente en código**: `backend/app/core/config.py`, `backend/app/core/prices.py`

### wiki/mecanicas/ — Mecánicas del juego
- **Campo**: 6 archivos (patrones, stats, staking, cueva, incubación, gashapon)
- **Anterior**: —
- **Nuevo**: Creación inicial con fórmulas exactas del código
- **Motivo**: Documentar reglas de juego con datos verificados del código fuente
- **Autor**: Claude (Agente A3)
- **Fuente en código**: `backend/app/services/game_logic.py`, `backend/app/models/axolotito.py`

### wiki/jugadores/ — Guías para jugadores
- **Campo**: 6 archivos en español casual
- **Anterior**: —
- **Nuevo**: Creación inicial de guías player-facing
- **Motivo**: Documentación pública para jugadores sobre mecánicas, precios y procesos
- **Autor**: Claude (Agente A4)
- **Fuente en código**: `docs/completed/AXOLOTTO_BIBLE.md`, síntesis de wiki/economia/ y wiki/mecanicas/

### wiki/arquitectura/ + wiki/api/ — Referencia técnica
- **Campo**: 8 archivos (backend, frontend, contratos, DB, 4 módulos API)
- **Anterior**: —
- **Nuevo**: Creación inicial de referencia de arquitectura
- **Motivo**: Onboarding técnico para desarrolladores y agentes AI nuevos
- **Autor**: Claude (Agente A5)
- **Fuente en código**: `backend/app/api/v1/endpoints/`, `frontend/components/`, `contracts/src/`
