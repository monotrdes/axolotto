---
tags: [index, ai-context, jugadores]
description: "Índice maestro del vault Obsidian Axolotto. Leer antes de cualquier otro archivo."
last_modified: "2026-06-07"
---

# Axolotto — Índice Maestro

> **AI agents:** Este es el primer archivo a leer. En <400 tokens sabrás exactamente qué archivo abrir para cada tema — sin explorar `docs/` ni el codebase.

## Qué es Axolotto
Juego de lotería Web3 multijugador. Los jugadores coleccionan cartas de Lotería Mexicana (54 cartas NFT), arman tablas 4×4, y compiten en salas de juego. Tienen Axolotitos (mascotas NFT) con stats que afectan el juego. Economía dual: **AXF** (moneda premium, dinero real) y **FRJ** (moneda de juego, se gana jugando).

## Navegación por Tema

### Para AI Agents
| Tarea | Archivo |
|-------|---------|
| Onboarding rápido (stack + 5 reglas) | [[ai/QUICK_START]] |
| Reglas que NUNCA romper | [[ai/critical_rules]] |
| Bugs y trampas conocidas | [[ai/gotchas]] |
| Qué agente usar para cada tarea | [[ai/agent_routing]] |

### Para Mecánicas y Economía
| Tarea | Archivo |
|-------|---------|
| Precios de TODO (items, boosters, salas, VIP) | [[economia/tablas_precios]] |
| AXF vs FRJ: diferencias y cómo obtenerlas | [[economia/monedas]] |
| Comparativa VIP Coral / Dorado / Axolite | [[economia/vip_tiers]] |
| House edge, jackpot, modelo 80/20 | [[economia/economia_general]] |
| Patrones ganadores del juego (con grids) | [[mecanicas/patrones_ganadores]] |
| Stats de Axolotito y sus fórmulas | [[mecanicas/estadisticas_axolotito]] |
| Staking: ganancias pasivas de FRJ | [[mecanicas/staking]] |
| Expansión de cueva (8 niveles) | [[mecanicas/expansion_cueva]] |
| Incubación e imprinting de huevos | [[mecanicas/incubacion_imprinting]] |
| Cápsulas Gashapon y sistema pity | [[mecanicas/gashapon]] |

### Para Jugadores (español)
| Tarea | Archivo |
|-------|---------|
| Primeros pasos | [[jugadores/guia_inicio]] |
| Mis Axolotitos: cuidado y stats | [[jugadores/axolotitos]] |
| La tienda (Tianguis) | [[jugadores/tienda]] |
| Jugar en multijugador | [[jugadores/multijugador]] |
| Membresía VIP | [[jugadores/vip]] |
| Cápsulas Gashapon | [[jugadores/capsulas]] |

### Para Desarrollo
| Tarea | Archivo |
|-------|---------|
| Arquitectura backend (FastAPI + servicios) | [[arquitectura/backend]] |
| Arquitectura frontend (Next.js + hooks) | [[arquitectura/frontend]] |
| Contratos Solidity (10 contratos) | [[arquitectura/contratos]] |
| Modelos de base de datos | [[arquitectura/base_de_datos]] |
| Los 26 módulos de endpoints | [[api/resumen_endpoints]] |
| Endpoints banco y economía | [[api/banco_y_economia]] |
| Endpoints juego y multijugador | [[api/juego_y_multijugador]] |
| Endpoints usuarios y perfil | [[api/usuarios_y_perfil]] |

## Archivos de Referencia (fuera del wiki)
- `CLAUDE.md` — instrucciones completas para AI agents
- `docs/000_PLAN_GLOBAL_PENDIENTES.md` — roadmap actualizado 2026-06-02
- `docs/completed/AXOLOTTO_BIBLE.md` — game design bible (38 KB)
- `.claude/agents/*.md` — definición de los 8 agentes especializados

## Historial de Cambios
→ Ver [[CHANGELOG]] para el registro completo de modificaciones al wiki
