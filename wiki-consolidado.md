# Axolotto — Wiki Completa

> **Generado:** 2026-06-09 05:17
> **Archivos:** 57 archivos markdown del wiki
> **Idioma:** Español
> **Script:** `scripts/build-wiki-consolidated.sh`

---


---

## Raiz

### 00-INDEX
> `00-INDEX.md`

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

### Wiki de Conceptos (bilingüe — para jugadores y Odysseus)
| Tarea | Archivo |
|-------|---------|
| 🦎 **Índice de conceptos** — 27 páginas estilo PokéWiki | [[conceptos/00-INDEX]] |
| Bienvenida y mundo del juego | [[conceptos/01-bienvenido-a-xochimilco]] |
| Guía completa de Axolotitos | [[conceptos/02-axolotitos]] |
| Cómo jugar Lotería (paso a paso) | [[conceptos/06-como-jugar-loteria]] |
| Economía dual AXF vs FRJ | [[conceptos/12-economia-dual]] |

> La wiki de conceptos reemplaza las guías básicas de jugadores. Ver [[conceptos/00-INDEX]] para el índice completo de 27 páginas.

### Para Jugadores (guías originales — legacy)
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


### CHANGELOG
> `CHANGELOG.md`

---
tags: [changelog]
description: "Historial de todos los cambios al wiki con fecha, motivo, autor y referencia al código"
last_modified: "2026-06-07"
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

## 2026-06-09 | wiki/conceptos/ | Creación del wiki de conceptos para jugadores

### wiki/conceptos/ — 27 archivos nuevos, bilingües (español/inglés)
- **Campo**: Creación inicial de wiki de conceptos estilo PokéWiki
- **Anterior**: Solo existían 6 guías básicas en wiki/jugadores/
- **Nuevo**: 27 páginas interconectadas con [[wikilinks]] cubriendo: mundo, Axolotitos (stats, naturalezas, rasgos visuales), gameplay (cómo jugar, patrones ganadores, modos de juego, cartas, tablas), crianza (webitos, incubación, imprinting), economía (AXF vs FRJ, tienda, gashapon, VIP), progresión (cueva 8 niveles, decoración, forja, mercado P2P, staking, ciclo lunar, jackpot), multijugador (salas, saladito, eventos), y guías (F2P, consejos avanzados). Formato Obsidian con frontmatter, sección English en cada página, tablas Quick Reference bilingües.
- **Motivo**: Crear una enciclopedia del juego para jugadores (no desarrolladores) que pueda subirse a Odysseus/PewDiePie para AI memory. La wiki técnica existente solo cubre el desarrollo.
- **Autor**: Claude (multi-agente — 27 agentes en paralelo en 4 fases)
- **Fuente en código**: `docs/completed/AXOLOTTO_BIBLE.md`, `backend/app/core/prices.py`, `backend/app/core/config.py`, `backend/app/models/axolotito.py`, `backend/app/services/game_logic.py`, `backend/app/services/imprinting_service.py`, `frontend/components/`

### wiki/00-INDEX.md — Añadida sección "Wiki de Conceptos"
- **Campo**: Nueva fila en tabla de navegación
- **Anterior**: Solo enlaces a wiki técnica y 6 guías de jugadores
- **Nuevo**: Enlace principal a [[conceptos/00-INDEX]] + 4 páginas headline + nota de migración

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



---

## Conceptos

### 00-INDEX
> `conceptos/00-INDEX.md`

---
tags: [conceptos, index]
description: "Wiki de conceptos de Axolotto para jugadores — bilingüe español/inglés | Axolotto concept wiki for players — bilingual Spanish/English"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# 🦎 Axolotto — Wiki de Conceptos

> **Bienvenido a la enciclopedia del jugador.** Aquí encuentras todo sobre el universo Axolotto: las criaturas, las reglas, los objetos, la economía y las estrategias. Escrito para jugadores, no para programadores.

---

## 🌎 El Mundo

| Página | De qué trata |
|--------|-------------|
| [[01-bienvenido-a-xochimilco]] | Xochimilco Digital, el universo del juego, la tradición de la Lotería Mexicana |

## 🦎 Axolotitos — Tus Compañeros

| Página | De qué trata |
|--------|-------------|
| [[02-axolotitos]] | Guía completa: stats, energía, cuidado, nivelación |
| [[03-estadisticas-de-axolotito]] | SUERTE, OJO, PILA y SAL — qué hace cada stat en partida |
| [[04-naturalezas-y-personalidad]] | Las 6 naturalezas y cómo afectan el rendimiento |
| [[05-rasgos-visuales-y-rareza]] | Colores, branquias, ojos, cola — rareza y valor en staking |

## 🎲 Cómo Jugar

| Página | De qué trata |
|--------|-------------|
| [[06-como-jugar-loteria]] | El juego explicado paso a paso: el tablero, el Gritón, ganar |
| [[07-patrones-ganadores]] | Líneas, cuadritos, esquinas, pocito — todos los patrones |
| [[08-modos-de-juego]] | CPU, Multijugador, Manual, Saladito, Espectador |
| [[09-cartas]] | Las 54 cartas de Lotería, rarezas, foil/brillante |
| [[10-tablas]] | Tableros 4×4: creación, tipos, staking, estrategia |

## 🥚 Webitos y Crianza

| Página | De qué trata |
|--------|-------------|
| [[11-webitos-y-crianza]] | Huevos, incubación, apadrinamiento (imprinting), eclosión |

## 💰 Economía

| Página | De qué trata |
|--------|-------------|
| [[12-economia-dual]] | AXF vs FRJ — las dos monedas, cómo obtenerlas, por qué existen |
| [[13-tienda-y-tianguis]] | Tienda oficial: sobres, webitos, consumibles, tablas |
| [[14-capsulas-gashapon]] | Gachapón: tiers, sistema pity, probabilidades |
| [[15-vip-club]] | Membresía VIP: Coral, Dorado, Axolite — beneficios y costos |

## ⛏️ Progresión

| Página | De qué trata |
|--------|-------------|
| [[16-el-cenote-cueva]] | Expansión de cueva: 8 niveles, logros, excavación |
| [[17-decoracion-de-cueva]] | Decora tu cenote, minijuegos (Pozo, Arcade) |
| [[18-forja-y-fundicion]] | Derrite cartas duplicadas, forja cartas específicas |
| [[19-mercado-p2p]] | Compra y vende entre jugadores |
| [[20-staking-ingresos-pasivos]] | Genera FRJ pasivo con tablas y Axolotitos |
| [[21-ciclo-lunar-y-recompensas]] | Recompensas diarias, racha lunar, cápsulas gratis |
| [[22-jackpot]] | El premio gordo global — cómo crece y cómo ganarlo |

## 🏟️ Multijugador y Eventos

| Página | De qué trata |
|--------|-------------|
| [[23-salas-y-multijugador]] | Salas, lobby, Gritón, premios, juego automático |
| [[24-saladito-y-modos-especiales]] | Modo Saladito (3-4 AM), PvP Manual, eventos temporales |

## 📖 Guías

| Página | De qué trata |
|--------|-------------|
| [[25-f2p-guia-gratis]] | Cómo jugar sin gastar dinero real |
| [[26-consejos-y-estrategias]] | Tips avanzados, errores comunes, optimización |

---

## 🧭 ¿Qué quieres hacer?

**🆕 Soy nuevo**
→ Empieza en [[01-bienvenido-a-xochimilco]] · Luego lee [[06-como-jugar-loteria]] · Después [[12-economia-dual]]

**🦎 Quiero entender mi Axolotito**
→ [[02-axolotitos]] · [[03-estadisticas-de-axolotito]] · [[04-naturalezas-y-personalidad]]

**🪙 No tengo dinero — quiero jugar gratis**
→ [[25-f2p-guia-gratis]] · [[21-ciclo-lunar-y-recompensas]] · [[20-staking-ingresos-pasivos]]

**🎰 Quiero abrir cápsulas**
→ [[14-capsulas-gashapon]] · [[21-ciclo-lunar-y-recompensas]]

**👑 ¿Vale la pena el VIP?**
→ [[15-vip-club]] · [[12-economia-dual]]

**🏆 Quiero mejorar mi estrategia**
→ [[26-consejos-y-estrategias]] · [[07-patrones-ganadores]] · [[10-tablas]]

**🥚 Quiero criar un Axolotito**
→ [[11-webitos-y-crianza]] · [[16-el-cenote-cueva]]

---



### 01-bienvenido-a-xochimilco
> `conceptos/01-bienvenido-a-xochimilco.md`

---
tags: [conceptos, mundo]
description: "Bienvenido al universo de Axolotto — un metaverso de Lotería Mexicana en los canales digitales de Xochimilco | Welcome to the Axolotto universe — a Mexican Lotería metaverse set in the digital canals of Xochimilco"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Bienvenido a Xochimilco — El Mundo de Axolotto

## ¿Qué es Axolotto?

Axolotto es un **juego de Lotería Mexicana en un metaverso Web3**, ambientado en una recreación digital de los canales de Xochimilco. Juegas con tablas de 4x4, eliges estadísticas para tus axolotitos, abres sobres sorpresa, incubas huevos, participas en torneos multijugador y ganas premios reales en criptomonedas (AXF y FRJ) mientras un misterioso **Gritón** canta las cartas desde las profundidades del cenote.

Pero antes de lanzarte a jugar, conozcamos este mundo.

## Xochimilco Digital — Los Canales Que Nunca Duermen

Imagina los canales de Xochimilco de noche, iluminados con neón. El agua refleja luces rosas, violetas y doradas. Las trajineras flotan silenciosamente entre chinampas digitales. El cielo siempre está estrellado, pero las estrellas son *código*.

En el centro de todo está **El Cenote** — una cueva inundada gigantesca, el corazón del juego. Es aquí donde el Gritón canta las cartas, donde los huevos eclosionan, donde los jugadores se reúnen. Rayos de luz atraviesan el agua desde la superficie. Burbujas suben lentamente. El eco rebota en las paredes de piedra.

La estética es **dark neon**: fondos casi negros con acentos rosa neón (`#E4007C`), verde azulado, dorado y violeta. Es un mundo 2.5D con capas de profundidad — las cosas cercanas se mueven más rápido que las lejanas, dándole vida al escenario como si fuera un diorama de papel animado.

### Dato curioso: El Axolote Real

Los axolotes (*Ambystoma mexicanum*) son salamandras reales, nativas de los canales de Xochimilco en la Ciudad de México. Están **críticamente en peligro de extinción**: quedan menos de 1,000 en vida silvestre. Pero en cautiverio hay millones — son populares en acuarios y laboratorios científicos.

¿Por qué laboratorios? Porque los axolotes tienen una habilidad increíble: **pueden regenerar extremidades completas, órganos internos, e incluso partes de su cerebro y médula espinal**. Los científicos los estudian para entender cómo aplicar esta regeneración en humanos.

Su nombre viene de **Xólotl**, el dios azteca del fuego, el rayo y la muerte — hermano gemelo de Quetzalcóatl. Según la leyenda, Xólotl se transformó en axolote para esconderse y evitar ser sacrificado.

Axolotto celebra esta herencia. Cada axolotito en el juego es un NFT único con ADN digital que determina su apariencia y habilidades.

## La Lotería — Una Tradición de 200+ Años

La Lotería Mexicana es un juego de cartas tradicional, similar al bingo, que se juega en ferias, reuniones familiares y fiestas desde hace más de **dos siglos**. Un mazo de 54 cartas con ilustraciones icónicas: El Corazón, La Sirena, El Borracho, La Muerte, El Sol.

En una partida tradicional, un **cantador** (o "gritón") va sacando cartas al azar y cantando sus nombres — a veces con rimas, albures o chistes. Los jugadores marcan sus tablas con frijolitos. El primero en completar una línea o tabla grita **"¡Lotería!"** y gana.

Axolotto digitaliza esta tradición conservando su esencia: las mismas 54 cartas, el mismo sistema de tablas, el mismo grito de victoria. Pero añade capas de estrategia: **selección de estadísticas, construcción de tablas personalizadas, gestión de presupuesto, y economía Web3 real**.

> Axolotto es un **concurso de destreza**, no un casino. La habilidad del jugador importa: elegir bien las estadísticas, construir tablas eficientes, y manejar tu presupuesto separa a un experto de un novato. La suerte ayuda, pero la estrategia decide.

## El Gritón — La Voz del Cenote

El **Gritón** es el cantador oficial de Axolotto. Una figura misteriosa cuyo rostro nadie ha visto. Su voz retumba a través del cenote cuando anuncia cada carta. Unos dicen que es un axolote ancestral despertado de un sueño milenario bajo los canales. Otros, que es simplemente un señor muy gritón.

El Gritón no solo canta cartas — también da la bienvenida a nuevos jugadores y preside ceremonias especiales como la eclosión de huevos raros. Escúchalo bien, porque sus rimas a veces esconden pistas.

## Las 5 Zonas del Mundo

El mundo de Axolotto tiene cinco zonas principales, cada una con su propio color y propósito:

| Zona | Icono | Color | ¿Qué haces aquí? |
|---|---|---|---|
| **Tianguis** | 🏪 | Rosa neón | Comprar sobres (boosters), huevos y consumibles en la tienda |
| **Sala** | 🎲 | Verde | Jugar partidas — fácil (10 AXF) o difícil (50 AXF), construir tablas, seleccionar estadísticas |
| **Nido** | 🪺 | Rosa | Incubar huevos, cuidar axolotitos bebés, gestionar su energía y sueño |
| **Pirámide** | 🏆 | Dorado | Ver rankings, tablas de líderes, logros y el salón de la fama |
| **Cápsulas** | 🎰 | Violeta | Gashapon — gasta fichas en la máquina de cápsulas para ganar premios sorpresa |

Usa los tabs en la interfaz para moverte entre zonas. Cada zona tiene su propia música ambiental y efectos de sonido.

## El Clima del Cenote — Día y Noche en Tiempo Real

El cenote obedece a un ciclo día-noche que refleja las condiciones reales de Xochimilco. El juego tiene **cuatro fases climáticas**:

- **Amanecer** 🌅 — Luces doradas tenues. Los huevos incubados al amanecer completan su ciclo un 10% más rápido.
- **Mañana** ☀️ — Brillante y cálido. Mayor actividad de jugadores.
- **Tarde** 🌤️ — Luz naranja suave. Eventos especiales suelen ocurrir en este horario.
- **Noche** 🌙 — Oscuridad con destellos neón. Los huevos retienen el calor por más tiempo durante la noche, lo que afecta su incubación positivamente.

La retención de calor varía según el momento del día: los huevos incubados de noche mantienen su temperatura interna por más tiempo que los del mediodía. Esto no es solo estético — afecta la velocidad de eclosión y puede influir en los traits que hereda tu axolotito.

## ¿Listo para Jugar?

Ahora que conoces el mundo, es hora de sumergirte. Consigue tu primer [[14-capsulas-gashapon|sobre]] en el Tianguis, adopta un [[02-axolotitos|axolotito]], construye tu tabla en la Sala, y prepárate para gritar **¡Lotería!** cuando el Gritón cante tu carta ganadora.

---



### 02-axolotitos
> `conceptos/02-axolotitos.md`

---
tags: [conceptos, axolotitos]
description: "Guia completa de Axolotitos — stats, naturaleza, rasgos, cuidado y nivelacion | Complete Axolotito guide — stats, natures, traits, care and leveling"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Axolotitos — Tus Companeros del Cenote

> **Los Axolotitos son el corazon de Axolotto.** Son tus mascotas digitales, tus jugadores estrella, tus amigos anfibios que compiten por ti en la Lotería Mexicana. Esta pagina te explica absolutamente TODO sobre ellos: como funcionan, como cuidarlos, como subirlos de nivel y como conseguir el equipo perfecto.

---

## Que es un Axolotito?

Un **Axolotito** es una criatura digital unica inspirada en el ajolote mexicano (*Ambystoma mexicanum*). Es mucho mas que una mascota virtual — es tu personaje jugador en el universo de Axolotto.

**En terminos tecnicos**, cada Axolotito es un **NFT ERC-721** con un ADN de 256 bits (`uint256`) grabado en la blockchain. Este ADN define su apariencia visual (color de piel, tipo de branquias, forma de ojos, cola, etc.) y sus estadisticas base. No existen dos Axolotitos identicos — cada uno es irrepetible.

**En terminos de juego**, tu Axolotito es quien realmente **juega la Lotería por ti**. Tu eliges el tablero, decides el presupuesto, configuras los limites de ganancia/perdida... y el Axolotito ejecuta las partidas. Tu solo revisas los resultados cuando quieras.

> **Dato curioso:** El ajolote real es una especie endemica de Xochimilco, Ciudad de Mexico, en peligro de extincion. Axolotto lo convierte en protagonista digital para celebrar su existencia y crear conciencia.

---

## Las 4 Estadisticas Principales

Todos los Axolotitos nacen con 4 stats fundamentales que determinan su rendimiento en el juego. Estas son las que mas te importan en el dia a dia.

### SUERTE 🍀 — La Estadistica del Exito

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 10 |
| Que hace | Aumenta tus premios y te salva de perder |

La **Suerte** es tu mejor amiga. Cada punto de Suerte mejora tus posibilidades en varios frentes:

- **Bonus en premios:** Al ganar una partida, la Suerte aplica un multiplicador extra sobre el premio base. Con Suerte alta, los premios grandes se vuelven enormes.
- **Salvada Milagrosa (Lucky Save):** Hasta **5% de probabilidad** de evitar que un bot gane cuando tu estas a punto de perder. Es ese momentito de "no me lo puedo creer" que te salva la cartera.
- **Mejores drops en Gashapon:** Los Axolotitos con Suerte alta tienden a obtener mejores resultados al abrir capsulas. La Suerte se toma en cuenta en el momento del drop.

> **Consejo:** Si te gusta el Gashapon o juegas en salas dificiles, prioriza Axolotitos con Suerte alta.

---

### OJO 👁️ — La Estadistica de Precision

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 50 |
| Que hace | Reduce la probabilidad de fallar cartas cantadas |

Cuando el Griton canta una carta, tu Axolotito debe **marcarla en su tablero**. Si la carta esta en el tablero pero el Axolotito no la marca... eso es un **fallo**. Y los fallos cuestan partidas.

El **OJO** (Enfoque / Focus) determina que tan probable es ese fallo:

| OJO | Probabilidad de Fallo |
|-----|----------------------|
| 0 | ~30% — casi una de cada tres cartas se le pasa |
| 25 | ~22% |
| 50 | ~15% — valor inicial, equilibrado |
| 75 | ~7% |
| 100 | 0% — no falla NUNCA |

> **Consejo:** Para multijugador competitivo, el OJO es probablemente el stat mas importante. Un Axolotito con OJO 100 nunca pierde por despiste.

---

### PILA 🔋 — La Estadistica de Resistencia

| Propiedad | Valor |
|-----------|-------|
| Rango | 50 a 200 |
| Valor inicial | 100 |
| Que hace | Determina cuantas partidas puedes jugar y que tan rapido descansas |

La **PILA** (Stamina) es tu barra de energia maxima. Es el stat que define tu ritmo de juego:

- **Mas energia maxima:** Con PILA 50, tu maximo de energia es 50 — pocas partidas. Con PILA 200, tienes el doble del maximo normal. Mas partidas antes de necesitar dormir.
- **Recuperacion acelerada:** Al dormir, un Axolotito con PILA alta recupera energia mas rapido. Con PILA 200, el sueno es hasta **65% mas rapido** que con PILA 50.
- **Cada partida cuesta 10 de energia.** Con PILA 100, juegas ~10 partidas. Con PILA 200, ~20 partidas antes de agotarte.

> **Consejo:** Si planeas largas sesiones de juego (tipo "dejar el bot toda la noche"), busca PILA alta.

---

### SAL 🧂 — La Anti-Estadistica

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 5 |
| Que hace | Entorpece el rendimiento — entre mas baja, mejor |

La **SAL** (Salinidad / Salinity) es la estadistica que **NO quieres**. Es un lastre, un factor de mala suerte que afecta negativamente el rendimiento:

- **Deslizamiento de cartas:** En partidas CPU, la SAL hace que tus cartas se deslicen al fondo del mazo, tardando mas en aparecer. Entre mas SAL, mas atras quedan tus cartas.
- **En multijugador:** La SAL se vuelve particularmente peligrosa. A SAL = 100, tienes hasta **33% de probabilidad de que una carta cantada NO se marque** en tu tablero (un "slip"). En otras palabras: el OJO y la SAL se oponen — pero la SAL se aplica DESPUES, asi que ni el OJO 100 te salva del todo.
- **Piensalo asi:** SUERTE, OJO y PILA jalan hacia arriba. SAL jala hacia abajo. Un Axolotito con stats decentes pero SAL alta rinde peor que uno con stats bajos y SAL cero.

> **Consejo crucial:** Al elegir un Axolotito para comprar o criar, revisa la SAL antes que cualquier otra cosa. Un Axolotito con SAL arriba de 30 ya empieza a ser problematico. Arriba de 60 es casi injugable en multijugador.

---

## El Sistema de Energia

La energia es el recurso que limita cuantas partidas puedes jugar antes de descansar. Entender el sistema de energia es clave para optimizar tu juego.

### Conceptos Clave

| Concepto | Explicacion |
|----------|-------------|
| **energy_current** | Tu energia actual. Empieza en 100. Gastas 10 por partida (CPU o multijugador). |
| **energy_max_current** | Tu energia maxima efectiva. Empieza en 100. Decae con el uso. |
| **Decaimiento** | Cada partida jugada reduce `energy_max_current` en **3 puntos**. Es acumulativo. |
| **Piso** | `energy_max_current` nunca baja de **10**. Siempre podras jugar al menos 1-2 partidas. |
| **Dormir** | Restaura `energy_current` y resetea `energy_max_current` a su valor original (tu PILA). |
| **Umbral de sueno** | Solo puedes dormir cuando tu energia actual esta por debajo del **85%** del maximo actual. |

### Ejemplo de una Sesion de Juego

```
Inicio: energy_current = 100, energy_max_current = 100
Partida 1: current 90, max 97
Partida 2: current 80, max 94
Partida 3: current 70, max 91
Partida 4: current 60, max 88
Partida 5: current 50, max 85
...
Partida 10: current 0, max 70  ← sin energia, toca dormir
Dormir (~1 min) → current 100, max 100 de nuevo
```

> **Importante:** No puedes saltar de partida en partida para siempre. El sistema de decaimiento del maximo asegura que eventualmente necesites una pausa. Esta disenado para ser saludable — el bot se detiene, tu Axolotito descansa, tu tambien respiras.

### Comida: Recuperar Energia Sin Dormir

Si no quieres esperar el sueno, puedes alimentar a tu Axolotito:

| Alimento | Costo | Energia Restaurada |
|----------|-------|-------------------|
| **Algae Pellet** | 30 FRJ | +15 de energia |
| **Brine Shrimp** | 150 FRJ | +60 de energia |

La comida restaura `energy_current` pero **NO** resetea `energy_max_current`. El decaimiento solo se cura con sueno.

### Dormir

- El sueno tarda aproximadamente **1 minuto**.
- Axolotitos con PILA alta duermen mas rapido — hasta **65% mas rapido** en PILA 200.
- El boton de dormir solo aparece cuando tu energia esta por debajo del 85% del maximo actual.
- Al despertar: `energy_current` y `energy_max_current` se restauran completamente.
- Cuando la energia llega a **0**, el Axolotito **debe dormir**. No puede jugar hasta descansar.

---

## Los 4 Estados del Axolotito

En todo momento, tu Axolotito esta en uno de estos cuatro estados:

### IDLE — Disponible 😊

Estado por defecto. Tu Axolotito esta despierto, con energia, listo para lo que necesites:
- Puede jugar (CPU o multijugador)
- Puede comer
- Puedes equiparle accesorios
- Puedes revisar sus stats

### PLAYING — En Partida 🎮

El Axolotito esta jugando Lotería. Durante este estado:
- No puedes modificar su equipo
- No puedes cambiar su tablero asignado
- El progreso de la partida se actualiza en tiempo real (o al recargar)
- Si es modo CPU con bot automatico, el Axolotito sigue jugando solo hasta que se cumplan los limites o se agote la energia

### SLEEPING — Durmiendo 😴

El Axolotito esta descansando para recuperar energia:
- No puede jugar ni hacer nada
- La barra de sueno muestra el progreso (~1 minuto)
- Al despertar, energia completamente restaurada
- `energy_max_current` se resetea al valor de PILA (eliminando el decaimiento acumulado)

### WAITING_SETTLEMENT — Esperando Reporte 📋

La sesion de juego termino y el Axolotito espera que revises los resultados. Este es el "corte de caja":
- Ves una **boleta de rendimiento** con: ganancias/perdidas netas, XP ganada, partidas jugadas, victorias y derrotas
- Al confirmar con "Gracias por el esfuerzo", las ganancias se transfieren a tu cartera y el Axolotito recibe Puntos de Lealtad
- Despues del settlement, el Axolotito generalmente se va a dormir

---

## Nivelacion: Como Subir de Nivel

Los Axolotitos ganan **experiencia (XP)** al jugar partidas. Acumular suficiente XP los hace subir de nivel, mejorando sus estadisticas.

### Umbral de Subida de Nivel

La formula es simple:

> **XP necesaria para subir de nivel = nivel actual x 100**

Por ejemplo: para pasar de nivel 1 a nivel 2 necesitas 100 XP. De nivel 5 a nivel 6 necesitas 500 XP. De nivel 10 a 11 necesitas 1000 XP.

### Cuanta XP Ganas por Partida

**Modo CPU:**

| Resultado | XP para el Axolotito |
|-----------|---------------------|
| Victoria (facil) | +35 XP |
| Victoria (dificil) | +75 XP |
| Derrota (facil) | +8 XP |
| Derrota (dificil) | +15 XP |

**Modo Multijugador:**

| Resultado | XP para el Axolotito |
|-----------|---------------------|
| Premio 1 (primer lugar) | +50 XP |
| Premio 2 (segundo lugar) | +20 XP |
| Consolacion | +5 XP |

### Que Mejora al Subir de Nivel?

Al subir de nivel, todas las estadisticas principales (SUERTE, OJO, PILA) reciben una mejora gradual. La SAL no se modifica al subir de nivel — solo cambia mediante crianza y genes.

Ademas, niveles mas altos desbloquean acceso a:
- Salas de mayor dificultad
- Mejores tasas de staking
- Mayor visibilidad en rankings

---

## Equipamiento y Accesorios

Puedes vestir a tu Axolotito con accesorios. El equipamiento es **puramente cosmetico** — no afecta las estadisticas de juego. Su valor es de coleccion, personalizacion y estatus.

### Los 3 Slots de Equipo

| Slot | Que va | Ejemplos |
|------|--------|----------|
| **Cabeza** 🎩 | Sombreros, coronas, cascos | Gorro de mariachi, Corona de lirio, Casco de buzo, Diadema astral |
| **Ojos** 👓 | Lentes, gafas, antifaces | Gafas de sol, Monoculo dorado, Goggles de buceo, Antifaz de luchador |
| **Cuerpo** 👘 | Ropa, capas, armaduras | Poncho de Xochimilco, Capa de campeon, Chaleco táctico, Armadura de obsidiana |

### Como Conseguir Accesorios

- **Gashapon:** La fuente principal. Las capsulas de Plata y Oro tienen buenas probabilidades de accesorios raros.
- **Mercado P2P:** Compra a otros jugadores — a veces encuentras piezas que ya no estan en rotacion.
- **Eventos especiales:** Algunos accesorios son exclusivos de temporada (Dia de Muertos, Navidad, aniversario).

> **Nota:** Los accesorios NO afectan stats. Un Axolotito con el casco mas epico del juego tiene exactamente el mismo rendimiento que uno sin nada puesto. La moda es para el alma, no para la SUERTE.

---

## Limite de Axolotitos y Slots

No puedes tener Axolotitos infinitos. El juego limita cuantos Axolotitos activos puedes mantener.

| Estado de Membresia | Slots de Axolotito |
|---------------------|-------------------|
| Sin VIP | 6 slots |
| VIP Coral | 6 slots |
| VIP Dorado | 6 slots |
| VIP Axolite | 7 slots |

### Que Pasa si mi VIP Axolite Expira?

Si tienes 7 Axolotitos y tu VIP Axolite expira, el septimo Axolotito (el mas reciente) entra en estado **congelado**:
- No puede jugar, comer, dormir, ni venderse
- Al intentar usarlo, el sistema responde con error **HTTP 423 (Locked)**
- Sigue ocupando un slot — no desaparece, solo queda inactivo
- **Solucion:** Renovar el VIP Axolite para descongelarlo, o liberar (quemar) un Axolotito para bajar a 6 y recuperar el acceso normal

> **Consejo:** Si estas en VIP Axolite y sabes que va a expirar, planea con anticipacion cual Axolotito liberar o vendelo en el mercado P2P antes de que expire.

---

## La Formula de Poder (Rankings)

El **PODER** es una metrica global que resume que tan fuerte es tu Axolotito. Se usa para rankings y comparaciones rapidas:

> **PODER = SUERTE + OJO + PILA + (100 - SAL)**

En otras palabras: sumas tus tres stats positivas, y sumas el "inverso" de la SAL (porque SAL baja = mejor). El valor maximo teorico es **500**:

| Stat | Maximo | Contribucion |
|------|--------|-------------|
| SUERTE | 100 | +100 |
| OJO | 100 | +100 |
| PILA | 200 | +200 |
| (100 - SAL) | 100 (cuando SAL=0) | +100 |
| **TOTAL maximo** | | **500** |

Esto hace que la PILA sea el stat con mas peso en el ranking (porque llega a 200), seguido de SUERTE y OJO (llegan a 100). Un Axolotito con PILA alta naturalmente tendra mas PODER que uno con SUERTE alta, aunque ambos sean igual de valiosos segun tu estilo de juego.

---

## Como Conseguir un Axolotito

Hay tres caminos para obtener tu primer (o siguiente) Axolotito:

### 1. Tutorial — Tu Primer Axolotito Gratis 🎁

Al completar el tutorial del juego, recibes tu primer Axolotito completamente gratis. Es un Axolotito basico con stats iniciales (SUERTE 10, OJO 50, PILA 100, SAL 5) y sin rasgos especiales, pero es 100% funcional y te permite empezar a jugar de inmediato.

### 2. Criar desde un Webito 🥚

El metodo principal para obtener Axolotitos con genes unicos:

1. **Compra un Webito** (huevo) en la Tienda. Los precios van de 400 a 3000 FRJ dependiendo del tipo (Genesis, Expansion, Retail, Astral).
2. **Colocalo en un slot de incubacion** en tu Cenote.
3. **Incubalo por 7 dias.** Durante este periodo controlas la temperatura y proteges el huevo del frio con escudos. El clima de Xochimilco afecta el progreso.
4. **Apadrina el Webito (Imprinting):** Durante la incubacion, puedes alimentar al huevo con items que modifican los stats del futuro Axolotito (ej. reducir SAL, aumentar SUERTE).
5. **Eclosiona:** Al completar los 7 dias, el huevo eclosiona y nace tu Axolotito con stats y rasgos determinados por la incubacion y el apadrinamiento.

> Ver la guia completa en: [[11-webitos-y-crianza]]

### 3. Mercado P2P 🛒

Compra un Axolotito ya existente a otro jugador:
- Puedes ver sus stats ANTES de comprar
- Los precios varian segun stats, rareza de rasgos, nivel y equipamiento
- Los Axolotitos con SAL baja y SUERTE/OJO altos suelen ser los mas caros
- Ver detalles en: [[19-mercado-p2p]]

---

## Resumen para Principiantes

Si eres nuevo en Axolotto y solo quieres lo esencial:

1. Tu primer Axolotito es **gratis** al completar el tutorial.
2. Los 4 stats clave son **SUERTE** (ganar mas), **OJO** (no fallar), **PILA** (jugar mas), y **SAL** (entre menos, mejor).
3. Cada partida cuesta **10 de energia**. Sin energia toca dormir (~1 min).
4. **No te obsesiones con stats perfectos al inicio.** Aprende a jugar con lo que tienes. La diferencia entre un Axolotito "bueno" y uno "perfecto" solo se nota en niveles altos de juego.
5. **La SAL es traicionera.** Si estas comprando en el mercado P2P, revisa la SAL antes del precio.
6. Los accesorios son **puramente cosmeticos** — viste a tu Axolotito como quieras, no afecta el juego.
7. **El bot automatico es tu amigo.** Configura presupuesto, limites de perdida/ganancia, y deja que tu Axolotito juegue solo. Revisa los resultados cuando quieras.

---



### 03-estadisticas-de-axolotito
> `conceptos/03-estadisticas-de-axolotito.md`

---
tags: [conceptos, axolotitos, stats]
description: "Estadisticas de Axolotito en detalle — SUERTE, OJO, PILA y SAL explicadas | Axolotito stats in detail — LUCK, FOCUS, STAMINA and SALINITY explained"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Estadisticas del Axolotito — Guia Profunda

> **Cada Axolotito tiene 4 estadisticas principales que definen como juega, cuanto gana y cuanto aguanta.** Esta pagina es la referencia definitiva: que hace cada stat, como se calculan sus efectos, como mejorarlas y como combinarlas segun tu estilo de juego.

---

## Las 4 Estadisticas Fundamentales

Tu Axolotito gira en torno a cuatro numeros. Entenderlos es la diferencia entre un jugador casual y uno que consistentemente gana mas.

---

## 1. SUERTE (Luck) 🍀

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 10 |
| Tipo | Estadistica ofensiva — te da mas recompensas y segundas oportunidades |

La Suerte es el stat que todo jugador quiere alta. No afecta directamente si ganas o pierdes una partida, pero hace que ganar sea mas rentable y que perder duela menos.

### Bonus de Premio

Cada vez que tu Axolotito gana una partida, la Suerte anade un extra de Frijolitos (FRJ) al premio base. El calculo es sencillo:

- **Bonus de FRJ** = (tu Suerte dividida entre 1000) multiplicado por el premio base
- Con **Suerte 100**, recibes un **+10%** de FRJ en cada premio
- Con Suerte 50, recibes +5%
- Con Suerte 10 (default), recibes +1%

No parece mucho al principio, pero a lo largo de cientos de partidas la diferencia es enorme. Un grinder con Suerte 100 gana significativamente mas FRJ que uno con Suerte 10, incluso si ambos ganan el mismo numero de partidas.

### Salvada Afortunada (Lucky Save)

Esta es quiza la mecanica mas querida de la Suerte. Cuando tu Axolotito esta a punto de perder una partida, la Suerte puede activar una **segunda oportunidad** y salvarte.

- **Probabilidad de salvada** = (Suerte dividida entre 1000) multiplicado por 0.5
- Con **Suerte 100**: **5%** de probabilidad de salvada (maximo)
- Con Suerte 50: 2.5%
- Con Suerte 10 (default): 0.5%

Solo se puede activar **una vez por partida**. Si ya te salvaste una vez y vuelves a estar a punto de perder, no hay segunda salvada. Aun asi, ese 5% en Suerte 100 significa que 1 de cada 20 partidas perdidas se convierte en victoria — una diferencia brutal en sesiones largas.

### Bonus en Gashapon

La Suerte tambien influye en las tiradas de Gashapon (capsulas de accesorios y cartas). Las tasas de drop de objetos raros mejoran ligeramente con Suerte alta. El efecto es pequeno pero consistente — como un empujoncito extra cada vez que abres una capsula.

### Como Aumentar la Suerte

- **Naturaleza Suertudo**: otorga **+10** de Suerte base
- **Impronta (imprinting)**: si tu padrino gana muchas partidas durante la fase de impronta, tu Suerte base sube
- **Subir de nivel**: cada nivel ganado da puntos que puedes distribuir; invertir en Suerte es una estrategia clasica

---

## 2. OJO (Focus) 👁️

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 50 |
| Tipo | Estadistica ofensiva/de precision — la mas importante para marcar cartas consistentemente |

El Ojo es, para muchos jugadores, **la estadistica mas importante del juego**. Controla que tan seguido tu Axolotito "ve" las cartas que el Griton canta.

### Probabilidad de Fallo (Miss Chance)

Cuando el Griton canta una carta que SI esta en tu tablero, tu Axolotito deberia marcarla. Pero no siempre lo hace — a veces "no la ve". Esa es la probabilidad de fallo:

- **miss_chance** = maximo 0, minimo entre 0.3 y (100 menos tu Ojo) multiplicado por 0.003
- Con **Ojo 100**: **0%** de fallo — jamas te pierdes una carta. Marcado perfecto.
- Con **Ojo 50** (default): aproximadamente **15%** de fallo
- Con **Ojo 0**: **30%** de fallo — casi una de cada tres cartas se te pasa

Traducido a partidas reales: con Ojo 50, de cada 10 cartas tuyas que el Griton canta, en promedio te pierdes 1 o 2. Con Ojo 100, las marcas todas. Con Ojo 0, te pierdes 3 de cada 10 — un desastre.

### Regla Practica

Cada **10 puntos de Ojo** equivalen aproximadamente a un **3% menos de probabilidad de fallo**. Subir de 50 a 70 reduce tu miss chance de ~15% a ~9% — una mejora notable que se siente en cada partida.

### Agilidad en Modo Manual

En el modo PvP manual, el Ojo se traduce en Agilidad: a mayor Ojo, mas rapido puedes marcar cartas en tu tablero (menor delay entre marcaciones). Esto solo aplica en modalidades manuales — en CPU auto-play, el Ojo solo afecta la probabilidad de fallo.

### Como Aumentar el Ojo

- **Naturaleza Metodico**: otorga **+10** de Ojo base
- **Impronta (imprinting)**: partidas con alta precision durante la impronta mejoran el Ojo base
- **Subir de nivel**: invertir puntos de nivel en Ojo es la estrategia recomendada para grinders de CPU

---

## 3. PILA (Stamina) 🔋

| Propiedad | Valor |
|-----------|-------|
| Rango | 50 a 200 |
| Valor inicial | 100 |
| Tipo | Estadistica de resistencia — cuantas partidas aguantas y que tan rapido te recuperas |

La PILA representa la energia fisica de tu Axolotito. No afecta si ganas o pierdes una partida individual, pero determina **cuantas partidas puedes jugar** antes de necesitar dormir y **que tan rapido te recuperas**.

### Reserva de Energia

Tu energia maxima es igual a tu PILA. Cada partida consume energia:

- Cada partida cuesta **10 de energia**
- Con **PILA 100**, puedes jugar alrededor de **10 partidas** antes de quedarte sin energia
- Con PILA 200, juegas **20 partidas** antes de necesitar dormir
- Con PILA 50 (minimo), solo **5 partidas**

Ademas, cada partida reduce tu energia maxima actual en **3 puntos** (piso minimo: 10). Esto simula el cansancio acumulado. Despues de 30 partidas sin dormir, tu maximo de energia puede bajar de 100 a 10 — practicamente necesitas dormir tras cada partida. **Dormir restaura completamente tu energia maxima a su valor original.**

### Velocidad de Sueno

No todos los Axolotitos duermen igual. La PILA controla que tan rapido te recuperas:

- **Formula**: tiempo de sueno = 1 minuto multiplicado por un factor
- El factor va de **1.0** (PILA 50, el mas lento) hasta **0.35** (PILA 200, el mas rapido)
- **PILA 200 recupera un 65% mas rapido que PILA 50**
- PILA 100 (default) tiene un factor intermedio de aproximadamente 0.74

En la practica: un Axolotito con PILA 200 duerme en ~21 segundos lo que a uno con PILA 50 le toma 1 minuto completo. Para jugadores que quieren grindear sin parar, PILA alta es obligatoria.

### Desgaste Maximo de Energia

Cada partida reduce tu energia maxima actual en 3 puntos, con un piso de 10. Esto significa:

- Empiezas con maximo = tu PILA (digamos 100)
- Tras 10 partidas: maximo bajo a 70
- Tras 20 partidas: maximo bajo a 40
- Tras 30 partidas: maximo bajo a 10 (el piso)
- **Dormir restaura el maximo a su valor completo (100)**

El mensaje es claro: duerme regularmente. No hay forma de evitar el desgaste, solo administrarlo.

### Como Aumentar la PILA

- **Naturaleza Sabio**: otorga **+15** de PILA base (el boost mas grande de stats por naturaleza)
- **Impronta (imprinting)**: jugar 3 o mas partidas en una misma sesion durante la impronta mejora la PILA
- **Subir de nivel**: ideal para jugadores que priorizan volumen de partidas sobre calidad

---

## 4. SAL (Salinity) 🧂

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 5 |
| Tipo | **ANTI-ESTADISTICA** — quieres tenerla LO MAS BAJA POSIBLE |

La SAL es la estadistica trampa. No lo parece al principio — empieza baja (5) y parece inofensiva. Pero si la dejas subir, arruina el rendimiento de tu Axolotito de formas sutiles pero devastadoras.

**Regla de oro: manten tu SAL por debajo de 10. Siempre.**

### Efecto en Modo CPU — Sesgo del Mazo (Deck Bias)

Este es el efecto mas insidioso de la SAL. Cuando juegas contra la CPU, las cartas que SI estan en tu tablero son empujadas hacia la segunda mitad del mazo:

- Probabilidad por carta = el valor menor entre 0.5 y tu SAL dividida entre 200
- Con **SAL 100**: cada carta tuya en la primera mitad del mazo tiene **50%** de probabilidad de ser enviada al final
- Con **SAL 50**: 25% de probabilidad
- Con **SAL 5** (default): solo **2.5%** de probabilidad — casi imperceptible

Esto significa que con SAL alta, tus cartas salen mas tarde en la partida. Y si tus cartas salen mas tarde, marcas menos, ganas menos patrones, y pierdes mas partidas. Es una desventaja silenciosa que se acumula partida tras partida.

### Efecto en Multijugador — Desliz (Slip)

En partidas multijugador, la SAL tiene un segundo efecto que se suma a la probabilidad de fallo del Ojo:

- **slip_chance** = el valor menor entre 0.333 y tu SAL dividida entre 300
- Con **SAL 100**: **33%** de probabilidad de desliz — una de cada tres cartas se te escapa
- Con **SAL 50**: ~16.7% de desliz
- Con **SAL 5** (default): solo **~1.7%** de desliz — casi irrelevante

Lo brutal es que el desliz **se acumula con la probabilidad de fallo del Ojo**. Un Axolotito con Ojo 50 (15% miss) y SAL 100 (33% slip) tiene una probabilidad combinada de fallo cercana al 45%. Es decir, casi la mitad de tus cartas no se marcan. En multijugador competitivo, esto es una sentencia de derrota.

### Entropia de Sala

En salas multijugador, el promedio de SAL de todos los jugadores humanos determina el nivel de "caos" o "desorden" visual de la sala. Es un efecto puramente estetico y de sabor — la sala se ve mas turbulenta o mas tranquila segun la SAL colectiva. No afecta la mecanica de juego directamente.

### Modo Saladito — Donde SAL es BUENA

Existe una excepcion fascinante: el **Modo Saladito**. En este modo especial, las reglas se invierten:

- **Gana quien marca MENOS cartas**, no mas
- Una SAL alta se convierte en ventaja — menos marcas = mas cerca de ganar
- Axolotitos con SAL alta, que normalmente serian descartados, se vuelven valiosos

Esto crea un nicho estrategico: puedes criar Axolotitos especificamente para Modo Saladito con SAL alta, Ojo bajo, y ser imparable en ese formato.

### Como AUMENTA la SAL (malo — quieres evitarlo)

- **Padrino con SAL alta** durante la impronta: transfiere parte de su SAL al Axolotito
- **Perder partidas** durante la impronta: cada derrota sube la SAL
- **Baja precision** durante la impronta: marcar pocas cartas correctamente aumenta la SAL

### Como DISMINUYE la SAL (bueno — quieres hacer esto)

- **Padrino con SAL baja** (menor a 20) durante la impronta: otorga un delta de **-6 a -10** de SAL
- **Naturaleza Timido**: otorga **-10** de SAL base (el mejor anti-SAL natural)
- **Ganar partidas** durante la impronta: cada victoria reduce la SAL

---

## Interacciones Entre Estadisticas

Las cuatro estadisticas no existen en el vacio. Se combinan de formas estrategicas clave:

### Ojo + SAL — La Pareja de la Precision

Tu probabilidad TOTAL de no marcar una carta es la combinacion de:
- **Miss Chance** (del Ojo): no ves la carta
- **Slip Chance** (de la SAL): la ves pero se te escapa

Ambas se acumulan. Un Axolotito con Ojo 50 y SAL 100 falla aproximadamente el 45% de las cartas. Uno con Ojo 100 y SAL 5 falla menos del 2%. La diferencia es astronomica.

**Regla practica**: si tu SAL esta por encima de 20, subir Ojo se vuelve menos efectivo. Primero baja la SAL, luego invierte en Ojo.

### Suerte + Ojo — El Combo Ofensivo

- **Ojo** te hace marcar cartas consistentemente (ganar mas partidas)
- **Suerte** hace que esas victorias paguen mas (ganar mas FRJ por partida)

Es la combinacion clasica para grinders de CPU: maximiza tu tasa de victorias con Ojo y maximiza tus recompensas con Suerte. En ese orden — de nada sirve +10% de premio si no ganas la partida.

### PILA + SAL — El Combo de Resistencia

- **PILA** te deja jugar mas partidas por ciclo de sueno
- **SAL baja** evita el sesgo del mazo que alarga tus partidas y reduce tus victorias

Un Axolotito con PILA 200 y SAL 5 puede grindear 20 partidas eficientes antes de dormir 21 segundos. Uno con PILA 50 y SAL 80 juega 5 partidas malas y duerme 1 minuto. La diferencia de productividad es mas de 10x.

---

## Estadisticas Secundarias

Existen cuatro estadisticas adicionales en el ADN del Axolotito, pero actualmente **no tienen efecto en la jugabilidad principal**. Son puramente cosmeticas o mapean rasgos visuales:

| Stat | Default | Proposito Actual |
|------|---------|-----------------|
| **Carisma** | 10 | Mapea el tipo de boca (rasgo visual). Sin efecto en juego. |
| **Agilidad** | 10 | En modo PvP manual, controla el delay entre marcaciones (800ms a 2500ms). Derivada del Ojo por conveniencia. |
| **Sabiduria** | 10 | Mapea el tipo de frente (rasgo visual). Sin efecto en juego. |
| **Fuerza** | 10 | Mapea el tipo de extremidades (rasgo visual). Sin efecto en juego. |

Estos stats existen en la blockchain y pueden verse en el ADN, pero no necesitas preocuparte por ellos para jugar. Si en el futuro se implementan mecanicas que los usen, esta pagina se actualizara.

---

## Prioridad de Stats por Estilo de Juego

No todos los jugadores necesitan lo mismo. Aqui esta la prioridad recomendada segun como juegas:

### Grinder de CPU
Si tu plan es dejar a tu Axolotito jugando solo contra la maquina por horas:

1. **Ojo** — marcar consistentemente es lo mas importante. Sin precision no hay victorias.
2. **PILA** — mas partidas por ciclo, sueno mas rapido, mas volumen total.
3. **Suerte** — premios mas grandes sobre las victorias que ya tienes.
4. **SAL** — mantenla lo mas baja posible; el sesgo de mazo destruye tu tasa de victorias.

### Competidor Multijugador
Si compites contra otros jugadores humanos:

1. **Ojo** — en PvP, cada carta no marcada es una derrota frente a oponentes atentos.
2. **Suerte** — premios mas grandes y las salvadas afortunadas pueden cambiar partidas cerradas.
3. **PILA** — aguanta sesiones largas sin tener que retirarte a dormir.
4. **SAL** — mantenla **extremadamente baja**. El desliz en multijugador es brutal y se suma al fallo de Ojo.

### Especialista Saladito
Si te dedicas al modo de reglas invertidas:

1. **SAL** — ALTA es mejor. Menos marcas = mas cerca de ganar.
2. **PILA** — mismo razonamiento que siempre: mas partidas, mejor.
3. **Ojo** — en Saladito, un Ojo bajo es preferible (menos marcas). Un Ojo alto te perjudica.

### Staker Pasivo
Si solo pones a tus Axolotitos en staking sin jugar partidas:

- Las estadisticas de juego **no importan**. El staking usa los rasgos visuales (boca, frente, extremidades, etc.), no las estadisticas de rendimiento. Invierte en Axolotitos con rasgos raros, no con stats altos.

---

## Resumen — La Regla de Oro

> **Ojo arriba, Suerte arriba, PILA arriba, SAL abajo.** Esa es la formula universal. Un Axolotito con Ojo 80+, Suerte 60+, PILA 150+, y SAL menor a 10 es una maquina de ganar en cualquier modo. Todo lo demas son matices.

---



### 04-naturalezas-y-personalidad
> `conceptos/04-naturalezas-y-personalidad.md`

---
tags: [conceptos, axolotitos, naturalezas]
description: "Las 6 naturalezas de Axolotito y cómo afectan el rendimiento en partida | The 6 Axolotito natures and how they affect gameplay performance"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Naturalezas y Personalidad

> **Cada Axolotito nace con una naturaleza.** No es un simple modificador de stats — es su personalidad, su estilo de juego, su forma de ver el mundo. La naturaleza define cómo rinde en partida, cómo responde al apadrinamiento de Webitos, y qué tipo de jugador se beneficia más de tenerlo. Esta página te explica las 6 naturalezas, sus efectos precisos, sus ventajas y sus sacrificios.

---

## ¿Qué es una Naturaleza?

La **naturaleza** es un rasgo innato que todo Axolotito recibe aleatoriamente al nacer (eclosionar). No se puede cambiar, no se puede comprar, no se puede heredar de forma garantizada. Es como el signo zodiacal del Axolotito — una inclinación cósmica que define su carácter.

**En términos de juego**, la naturaleza aplica dos tipos de efectos:

1. **Modificadores de stats base:** Algunas naturalezas suben o bajan directamente los stats del Axolotito (SUERTE, OJO, PILA, SAL). Estos modificadores son permanentes y se aplican desde el nacimiento.
2. **Bonificadores de imprinting:** Cuando un Axolotito actúa como **padrino** de un Webito (huevo en incubación), su naturaleza afecta qué tan bien transmite ciertas cualidades al futuro Axolotito. Por ejemplo, un padrino Metódico transfiere mejor el OJO; un padrino Suertudo transfiere mejor la SUERTE.

> **Importante:** La naturaleza se asigna **aleatoriamente** al eclosionar. NO puedes elegirla. NO puedes cambiarla después. Los Webitos Astrales pueden tener mejores probabilidades de naturalezas raras, pero esto no está confirmado oficialmente.

---

## Las 6 Naturalezas

---

### 1. Metódico (Methodical) 🧐

> *"Nunca pierde una carta. Revisa dos veces. Respira una vez. Gana."*

El Metódico es el perfeccionista del Cenote. Cada carta que el Gritón canta, él ya la tiene marcada antes de que termine la sílaba. Su concentración es legendaria. Los jugadores competitivos lo adoran; los bots lo respetan.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| OJO (Focus) | **+10** |
| PILA (Stamina) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Focus (`focus_delta`) es positivo | Se multiplica por **1.25** (25% más) |

Esto significa que un padrino Metódico que juega bien (marcando cartas con precisión) transmite MUCHO mejor el OJO a sus Webitos apadrinados. Es la naturaleza ideal para criar Axolotitos con OJO alto.

**¿Para quién es mejor?**

- Jugadores de CPU que quieren marcar cartas de forma consistente, sin fallos.
- Competidores de multijugador donde cada carta perdida cuesta el premio.
- Criadores (Padrinos) que buscan pasar OJO alto a la siguiente generación.
- Grinders que priorizan la precisión sobre la cantidad de partidas.

**El sacrificio:** -5 PILA significa ~5 puntos menos de energía máxima. En términos prácticos, media partida menos por ciclo de sueño. Apenas se nota. Es el precio más bajo de todas las naturalezas por un beneficio excelente.

**Resumen para rápidos:** El Metódico es probablemente la mejor naturaleza para jugadores serios. +10 OJO por -5 PILA es un intercambio muy favorable.

---

### 2. Suertudo (Lucky) 🍀

> *"El caos lo adora. Las cartas caen en su lugar como si estuviera escrito."*

El Suertudo nació con una estrella en la frente. No es que juegue mejor — es que el universo conspira a su favor. Los premios son más grandes, las Salvadas Milagrosas ocurren más seguido, y las cápsulas de Gashapon le dan mejores drops. Es el consentido del RNG.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| SUERTE (Luck) | **+10** |
| PILA (Stamina) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Suerte (`luck_delta`) es positivo | Se multiplica por **1.25** (25% más) |

Un padrino Suertudo que gana partidas transmite mucha más SUERTE al Webito. Si además logra un jackpot durante el imprinting (+20 fijo de delta), el bonus 1.25x lo convierte en +25. Es la naturaleza soñada para criar Axolotitos de altos premios.

**¿Para quién es mejor?**

- Jugadores que persiguen jackpots y premios grandes.
- Fans del Gashapon (la SUERTE afecta los drops de cápsulas).
- Competidores de multijugador donde los premios son acumulativos y cada punto de SUERTE = más porcentaje del pozo.
- Criadores que quieren Axolotitos con SUERTE alta desde el nacimiento.

**El sacrificio:** Mismo que el Metódico: -5 PILA. Media partida menos por ciclo. Imperceptible para la mayoría de jugadores. El +10 SUERTE se traduce en +1% de probabilidad en cada tirada de premio — no suena a mucho, pero en cientos de partidas la diferencia es real.

**Resumen para rápidos:** Si juegas por los premios (no por la consistencia), el Suertudo es tu naturaleza. +10 SUERTE = premios más gordos, punto.

---

### 3. Hiperactivo (Hyperactive) ⚡

> *"Dormir es opcional. Ganar es obligatorio."*

El Hiperactivo no se cansa. Bueno, sí se cansa — pero se recupera como si tuviera un cargador rápido enchufado directo al sol. Duerme menos, juega más, descansa más rápido. Es el Axolotito perfecto para sesiones maratónicas de grinding.

**Efectos en juego:**

| Efecto | Valor |
|--------|-------|
| Recuperación de sueño | **25% más rápida** |
| OJO (Focus) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Stamina (`stamina_delta`) es positivo | Se multiplica por **1.25** (25% más) |
| Recuperación de sueño del padrino | **25% más rápida** (puede apadrinar más partidas por sesión) |

El Hiperactivo como padrino no solo transmite mejor la PILA — también completa sesiones de imprinting más rápido porque duerme menos entre partidas. Más partidas de imprinting por hora = el Webito eclosiona con mejores stats de stamina en menos tiempo real.

**¿Para quién es mejor?**

- Jugadores que quieren maximizar partidas por hora.
- Grinders que dejan el bot automático funcionando largas sesiones.
- Jugadores impacientes que odian esperar el sueño de 1 minuto.
- Criadores que quieren completar el imprinting rápido.

**El sacrificio:** -5 OJO = aproximadamente **1.5% más de probabilidad de fallo** al marcar cartas (de ~15% a ~16.5% en OJO base). Es un costo real pero manejable. Lo notas, pero no te arruina. Simplemente fallarás 1 o 2 cartas más por cada 100 cantadas.

**Resumen para rápidos:** Velocidad sobre precisión. Si juegas 50 partidas al día, el Hiperactivo te ahorra varios minutos de sueño. Si juegas 10 partidas al día, ni lo notas — mejor elige Metódico.

---

### 4. Glotón (Glutton) 🍽️

> *"Se come lo que sea. ¿Pellet? Desapareció. ¿Camaron? Desapareció. ¿La victoria? También desapareció, pero feliz."*

El Glotón vive para comer. Su metabolismo es una maravilla — exprime cada caloría de cada pellet como si fuera un banquete. Donde otros ven una Algae Pellet de 15 de energía, él ve 19.5. Donde otros ven un Brine Shrimp de 60, él ve 78.

**Efectos en juego:**

| Efecto | Valor |
|--------|-------|
| Energía restaurada por comida | **+30%** |
| OJO (Focus) | **-10** |

| Alimento | Energía normal | Energía para Glotón |
|----------|---------------|---------------------|
| Algae Pellet (30 FRJ) | +15 | **+19.5** |
| Brine Shrimp (150 FRJ) | +60 | **+78** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el padrino **pierde** una partida de imprinting | Todos los deltas negativos se reducen al **80%** de su magnitud |

Este es un efecto sutil pero poderoso. Cuando un padrino pierde, normalmente castiga los stats del Webito con deltas negativos (por ejemplo, -10 de SUERTE). Un padrino Glotón reduce ese castigo: el -10 se convierte en -8. No elimina el daño, pero lo amortigua. Es como un airbag para malas rachas.

**¿Para quién es mejor?**

- Jugadores con abundante FRJ que prefieren alimentar en vez de dormir.
- Jugadores F2P que optimizan cada pellet — estiras tu FRJ un 30% más.
- Espectadores que no quieren esperar el sueño y tienen FRJ de sobra.
- Criadores que quieren proteger a sus Webitos de los castigos por derrota durante el imprinting.

**El sacrificio:** -10 OJO = aproximadamente **3% más de probabilidad de fallo**. Es la penalización de OJO más grande entre todas las naturalezas. Con OJO base 50, pasas de ~15% de fallo a ~18%. Se nota. No es horrible, pero definitivamente sentirás que tu Axolotito "se distrae" más seguido.

**Resumen para rápidos:** Si tienes FRJ para gastar en comida, el Glotón te da mucha autonomía. Si estás corto de FRJ o juegas multijugador competitivo, el -10 OJO te va a doler.

---

### 5. Tímido (Shy) 🙈

> *"Se esconde de la voz del Gritón. Pero esconderse significa que las cartas malas tampoco lo encuentran."*

El Tímido no quiere problemas. Nace con la SAL más baja posible — casi como si el Cenote lo hubiera enjuagado antes de entregarlo. Es el Axolotito más puro, el menos contaminado, el que menos sufre los efectos negativos de la salinidad. En un mundo donde la SAL es el enemigo silencioso, el Tímido es un escudo.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| SAL (Salinity) | **-10** (al nacer) |
| SUERTE (Luck) | **-5** |

Con SAL base de 5, un Tímido empieza con **SAL = -5** que se ajusta a **SAL = 0** (el piso mínimo es 0). En otras palabras: nace sin salinidad. Cero. Nada. El sueño de todo jugador que odia el mecánico de SAL.

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Ninguno documentado actualmente | — |

El Tímido no tiene bonificadores de imprinting documentados en el sistema actual. Esto puede cambiar en futuras actualizaciones.

**¿Para quién es mejor?**

- Jugadores que ODIAN el mecánico de SAL y quieren la menor salinidad posible desde el día 1.
- Competidores de multijugador donde la SAL alta es devastadora (hasta 33% de slip).
- Jugadores que buscan un Axolotito "limpio" para criar — empezar con SAL 0 significa que los Webitos heredan menos salinidad base.
- Coleccionistas que valoran la pureza genética.

**El sacrificio:** -5 SUERTE = premios ligeramente más pequeños y ~0.25% menos de probabilidad de Salvada Milagrosa. Es un precio pequeño a cambio de eliminar completamente el problema de SAL.

**Dato curioso:** En el modo Saladito, donde los slips son BUENOS (te dan ventaja), el Tímido es la PEOR naturaleza posible. No te confundas — en Saladito quieres SAL alta, no baja. Para Saladito, busca un Sabio o cualquier naturaleza con SAL positiva.

**Resumen para rápidos:** La naturaleza anti-SAL. Si te desespera ver slips en multijugador, consigue un Tímido. Es la paz mental hecha Axolotito.

---

### 6. Sabio (Wise) 🦉

> *"Los Axolotitos más viejos son los más sabios. Pero la sabiduría viene con sal — han visto cosas."*

El Sabio es el tanque de energía definitivo. Ha vivido, ha jugado, ha perdido, ha ganado. Su experiencia se traduce en una resistencia física descomunal. Puede jugar más partidas que cualquier otro Axolotito antes de necesitar descanso. Pero la edad trae consigo una pizca de amargura — un poco de sal que se acumuló con los años.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| PILA (Stamina) | **+15** |
| SAL (Salinity) | **+5** |

Con PILA base 100, un Sabio empieza con **PILA = 115**. Eso significa ~11-12 partidas por ciclo en vez de ~10. Con comida y buena gestión, puedes estirar las sesiones significativamente.

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Ninguno documentado actualmente | — |

El Sabio no tiene bonificadores de imprinting documentados en el sistema actual. Esto puede cambiar en futuras actualizaciones.

**¿Para quién es mejor?**

- Jugadores maratónicos que quieren el mayor pool de energía posible.
- Grinders que dejan el bot automático toda la noche — PILA 115 = más partidas antes del sueño obligatorio.
- Criadores que quieren pasar PILA alta a los Webitos (el factor de herencia es 10%-15% de la PILA del padrino).
- Jugadores que no temen un poco de SAL extra porque juegan principalmente CPU (donde la SAL es menos castigadora).

**El sacrificio:** +5 SAL = mayor probabilidad de slip y deck bias. En términos concretos, con SAL base 5 + 5 = SAL 10, tu probabilidad de slip en multijugador es aproximadamente **~3.3%** (comparado con ~1.7% en SAL 5). No es catastrófico, pero se nota. En CPU, tus cartas aparecerán ligeramente más tarde en el mazo.

**La compensación:** +15 PILA es el boost de stat individual más grande de todas las naturalezas. Si juegas principalmente CPU o no te preocupa tanto el slip en multijugador, el Sabio es un caballo de batalla.

**Resumen para rápidos:** Energía para días, pero con una pizca de sal. Si juegas muchas partidas y no te molesta un slip ocasional, el Sabio es excelente. Si juegas multijugador competitivo, la SAL extra puede ser frustrante.

---

## Resumen de las 6 Naturalezas

| Naturaleza | Efecto Principal | Sacrificio | Imprinting Bonus | Estilo de Juego |
|------------|-----------------|------------|------------------|-----------------|
| **Metódico** 🧐 | +10 OJO | -5 PILA | 1.25x a focus_delta positivo | Precisión y consistencia |
| **Suertudo** 🍀 | +10 SUERTE | -5 PILA | 1.25x a luck_delta positivo | Premios grandes |
| **Hiperactivo** ⚡ | Sueño 25% más rápido | -5 OJO | 1.25x a stamina_delta positivo | Velocidad y grinding |
| **Glotón** 🍽️ | +30% energía de comida | -10 OJO | Deltas negativos al 80% | Autonomía con FRJ |
| **Tímido** 🙈 | -10 SAL al nacer | -5 SUERTE | Ninguno documentado | Pureza anti-slip |
| **Sabio** 🦉 | +15 PILA | +5 SAL | Ninguno documentado | Maratones de partidas |

---

## Mejor Naturaleza por Modo de Juego

| Modo | Mejor Naturaleza | ¿Por qué? |
|------|-----------------|-----------|
| **CPU Rookies** | Metódico o Hiperactivo | OJO para marcar consistente, o velocidad para grinding rápido |
| **CPU Champions** | Metódico | Contra bots difíciles, cada carta fallada cuesta la partida. La consistencia lo es todo |
| **Multijugador competitivo** | Suertudo o Tímido | Suertudo = premios más grandes. Tímido = cero slips. Depende de tu prioridad |
| **Saladito** (3-4 AM) | Sabio o Hiperactivo | En Saladito los slips son BUENOS — quieres SAL alta, no baja. Sabio da +5 SAL. Cualquier naturaleza con PILA extra ayuda |
| **F2P / Espectador** | Glotón | Estira cada FRJ en comida. Menos dependencia del sueño. Buena autonomía |
| **Crianza (Padrino)** | Metódico o Suertudo | Bonus 1.25x en los stats más valiosos para la descendencia |
| **Grinding masivo (bot)** | Hiperactivo o Sabio | Más partidas por hora real. El Hiperactivo duerme más rápido; el Sabio aguanta más partidas por ciclo |

---

## Cómo Saber la Naturaleza de tu Axolotito

La naturaleza se muestra en la **AxoSheet** (la ficha de stats del Axolotito en el Nido). Busca la etiqueta junto al nombre del Axolotito — aparecerá como un ícono con el nombre de la naturaleza.

En la misma pantalla puedes ver:
- Los 4 stats principales (SUERTE, OJO, PILA, SAL) con los modificadores de naturaleza ya aplicados.
- El nivel actual y la XP acumulada.
- El historial de partidas y el rendimiento reciente.
- Si el Axolotito está actuando como padrino de algún Webito.

---

## Preguntas Frecuentes

### ¿Puedo cambiar la naturaleza de mi Axolotito?

**No.** La naturaleza es permanente. Se asigna al nacer y no hay objeto, ítem, ni mecánica en el juego que permita cambiarla. Es parte del ADN del Axolotito, grabado en la blockchain.

### ¿Los Webitos Astrales tienen mejores naturalezas?

Hay reportes de la comunidad que sugieren que los Webitos Astrales tienen mayor probabilidad de naturalezas "deseables" (Metódico, Suertudo, Hiperactivo), pero **esto no está confirmado oficialmente** por el equipo de desarrollo. Tómalo como rumor hasta que haya datos oficiales.

### ¿Qué naturaleza es la mejor para empezar?

**Metódico.** El +10 OJO te da una ventaja inmediata y visible (fallas menos cartas), y el -5 PILA apenas se nota. Además, si algún día decides criar, el bonus de imprinting 1.25x en Focus es excelente. Es la naturaleza más "redonda" para nuevos jugadores.

### ¿Qué naturaleza es la peor?

Ninguna naturaleza es objetivamente "mala". Cada una tiene un nicho. Dicho esto, si tuvieras que elegir la de menor utilidad general, probablemente sería **Glotón** — el -10 OJO es el castigo más severo, y el beneficio (+30% energía de comida) solo es útil si tienes FRJ para gastar. Pero incluso el Glotón tiene su público (F2P que optimizan recursos).

### ¿La naturaleza afecta el valor de reventa en el mercado P2P?

**Sí, y mucho.** Los Axolotitos con naturalezas "meta" (Metódico, Suertudo) se venden por más en el mercado P2P que aquellos con naturalezas menos populares. Un Axolotito Metódico con buenos stats puede valer el doble que uno Glotón con stats similares. La naturaleza es uno de los factores que los compradores revisan inmediatamente después de la SAL.

---



### 05-rasgos-visuales-y-rareza
> `conceptos/05-rasgos-visuales-y-rareza.md`

---
tags: [conceptos, axolotitos, rasgos]
description: "Rasgos visuales de Axolotito — colores, partes del cuerpo, rareza y valor en staking | Axolotito visual traits — colors, body parts, rarity and staking value"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Rasgos Visuales y Rareza

Cada Axolotito es una criatura visualmente única. Su apariencia no es aleatoria ni meramente cosmética: está determinada por sus 6 estadísticas base (SAL, PILA, OJO, CAR, AGI, SAB, FUE), y cada rasgo visual influye directamente en la tasa de staking que genera. Cuanto más raro es un rasgo, más FRJ/h produce.

La emoción central del breeding y la incubación es precisamente esa pregunta: **"¿cómo se verá mi Axolotito?"** Cada cruza es una apuesta genética, y abrir un Webito por primera vez es como destapar una carta foil: nunca sabes si te va a salir un Axolotito común rosita o uno Astral con Branquias Fénix, Boca Divina y Halo en la frente.

A continuación, los 7 rasgos visuales del Axolotito, sus variantes, rarezas, y los umbrales de estadística que los determinan.

---

## 1. Color de Piel (Skin Color)

Determinado por la estadística **Salinidad (SAL)**. La piel es el rasgo más visible y el que define el multiplicador base de staking.

| Umbral SAL | Color de Piel | Color (EN) | Rareza | Multiplicador Base |
|------------|--------------|------------|--------|-------------------|
| ≤10 | Rosa | Pink | Común | 0.05 FRJ/h |
| ≤30 | Gris-Rosa Claro | Gray-Light-Pink | Común | 0.05 FRJ/h |
| ≤60 | Gris Claro | Gray-Light | Común | 0.05 FRJ/h |
| ≤90 | Gris Oscuro | Gray-Dark | Rara | 0.15 FRJ/h |
| >90 | Gris Mar Muerto | Gray-Dead-Sea | Épica | 0.40 FRJ/h |

- **Piel Astral**: La más rara de todas. Se obtiene con un 80% de probabilidad al abrir un Webito Astral (el 20% restante es Piel Dorada). Su tasa base es de **2.50 FRJ/h**. Garantiza al menos un rasgo visual premium: 50% de probabilidad de Frente Halo, 50% de Boca Divina.
- **Piel Dorada (Gold)**: Segunda más rara. 20% de probabilidad desde Webito Astral. Tasa base de **1.00 FRJ/h**.

---

## 2. Branquias (Gills)

Determinado por la estadística **Pila (PILA)** — representa la energía y resistencia del Axolotito. Las branquias son los apéndices externos a los lados de la cabeza, característicos de los ajolotes.

| Umbral PILA | Tipo de Branquias | Gills Type | Rareza | Bono por Parte (FRJ/h) |
|-------------|-------------------|------------|--------|-------------------------|
| <80 | Cortas | Short | Común | 0.01 |
| <120 | Normales | Normal | Común | 0.01 |
| <160 | Plumosas | Feathery | Épica | 0.03 |
| <190 | Corona | Crown | Legendaria | 0.08 |
| ≥190 | Fénix | Phoenix | Mítica | 0.20 |

Las Branquias Fénix son el rasgo más codiciado de esta categoría: parecen llamas ondulantes y tienen una animación de partículas ígneas. Pueden aparecer por rasgo Mítico si la pureza genética supera el 110% durante el imprinting (25% de probabilidad).

---

## 3. Ojos (Eyes)

Determinado por la estadística **Ojo (OJO)** — representa la concentración y enfoque del Axolotito.

| Umbral OJO | Tipo de Ojos | Eye Type | Rareza | Bono por Parte (FRJ/h) |
|------------|-------------|----------|--------|-------------------------|
| <20 | Derp | Derpy | Común | 0.01 |
| <50 | Soñador | Dreamer | Común | 0.01 |
| <80 | Tiernos | Cute | Épica | 0.03 |
| <95 | Intelectuales | Intellectual | Legendaria | 0.08 |
| ≥95 | Zen | Zen | Mítica | 0.20 |

Los Ojos Zen son hipnóticos: presentan un brillo etéreo con anillos concéntricos que rotan lentamente. Son el reflejo de un Axolotito en perfecto equilibrio mental.

---

## 4. Boca / Expresión (Mouth / Expression)

Determinado por la estadística **Carisma (CAR)** — representa el magnetismo y la expresividad social del Axolotito.

| Umbral CAR | Tipo de Boca | Mouth Type | Rareza | Bono por Parte (FRJ/h) |
|------------|-------------|------------|--------|-------------------------|
| <20 | Plana | Flat | Común | 0.01 |
| <60 | Sonrisa | Smile | Común | 0.01 |
| <80 | Colmillo | Fang | Épica | 0.03 |
| <95 | Rockstar | Rockstar | Legendaria | 0.08 |
| ≥95 | Divina | Divine | Mítica | 0.20 |

La Boca Divina tiene un sutil brillo dorado y una expresión de serenidad absoluta. Si el Axolotito tiene Piel Astral, hay un 50% de probabilidad de que herede automáticamente este rasgo.

---

## 5. Cola (Tail)

Determinado por la estadística **Agilidad (AGI)** — representa la velocidad y destreza de movimiento.

| Umbral AGI | Tipo de Cola | Tail Type | Rareza | Bono por Parte (FRJ/h) |
|------------|-------------|-----------|--------|-------------------------|
| <30 | Estándar | Standard | Común | 0.01 |
| <60 | Ondulada | Wavy | Común | 0.01 |
| <85 | Betta | Betta | Épica | 0.03 |
| ≥85 | Plasma | Plasma | Legendaria | 0.08 |

La Cola Plasma es translúcida y emite un resplandor neón que cambia de color según el estado de ánimo del Axolotito. Disponible como rasgo Mítico con 25% de probabilidad si pureza ≥110%.

---

## 6. Frente (Forehead)

Determinado por la estadística **Sabiduría (SAB)** — representa la inteligencia y percepción espiritual.

| Umbral SAB | Tipo de Frente | Forehead Type | Rareza | Bono por Parte (FRJ/h) |
|------------|---------------|---------------|--------|-------------------------|
| <40 | Ninguno | None | Común | 0.01 |
| <70 | Rayas | Stripes | Común | 0.01 |
| <90 | Gema | Gem | Épica | 0.03 |
| ≥90 | Halo | Halo | Legendaria | 0.08 |

El Halo es un anillo luminoso que flota sobre la cabeza del Axolotito. Es el rasgo premium garantizado más frecuente en Piel Astral (50% de probabilidad). También disponible como rasgo Mítico con 25% de probabilidad si pureza ≥110%.

---

## 7. Extremidades (Limbs)

Determinado por la estadística **Fuerza (FUE)** — representa la potencia física y capacidad de excavación.

| Umbral FUE | Tipo de Extremidades | Limb Type | Rareza | Bono por Parte (FRJ/h) |
|------------|---------------------|-----------|--------|-------------------------|
| <40 | Suaves | Soft | Común | 0.01 |
| <75 | Garras | Claws | Común | 0.01 |
| <95 | Escamas | Scales | Épica | 0.03 |
| ≥95 | Coral | Coral | Legendaria | 0.08 |

Las Extremidades Coral tienen crecimientos de coral bioluminiscente que brillan en la oscuridad. Disponible como rasgo Mítico con 25% de probabilidad si pureza ≥110%.

---

## Tabla de Rareza y Valor en Staking

Cada rasgo contribuye a la tasa de generación pasiva de FRJ. El cálculo es:

> **Tasa total = Multiplicador de Piel + Suma de los 6 bonos de parte**

Esa tasa base se multiplica luego por el bono de nivel: `(1 + 0.1 × nivel)`.

| Rareza | Borde Visual | Multiplicador Piel (FRJ/h) | Bono por Parte (FRJ/h) |
|--------|-------------|---------------------------|------------------------|
| Común (Common) | Gris sutil (Slate gray) | 0.05 | 0.01 |
| Rara (Uncommon) | Verde azulado (Teal) | — | — |
| Épica (Rare) | Cian brillante (Bright cyan) | 0.15 | 0.03 |
| Legendaria (Epic) | Violeta (Violet) | 0.40 | 0.08 |
| Mítica (Legendary) | Dorado con brillo animado (Gold glow) | 1.00 | 0.20 |
| Astral | Especial (Special) | 2.50 | — |

### Ejemplo de cálculo de staking

Imagina un Axolotito con estas características:

- **Piel**: Gris Oscuro (Épica) = 0.15 FRJ/h base
- **Branquias**: Plumosas (Épica) = 0.03
- **Ojos**: Tiernos (Épica) = 0.03
- **Boca**: Colmillo (Épica) = 0.03
- **Cola**: Betta (Épica) = 0.03
- **Frente**: Gema (Épica) = 0.03
- **Extremidades**: Escamas (Épica) = 0.03

**Tasa base** = 0.15 + (6 × 0.03) = **0.33 FRJ/h**

Si este Axolotito está en **nivel 20**:
- Bono de nivel = 1 + (0.1 × 20) = 3.0×
- Tasa final = 0.33 × 3.0 = **0.99 FRJ/h**

Ahora compáralo con un Axolotito **Mítico completo**:

- **Piel**: Gris Mar Muerto (Épica) = 0.40... ¡no, aún mejor! Piel Dorada = 1.00 FRJ/h
- **6 partes Míticas**: 6 × 0.20 = 1.20
- **Tasa base** = 1.00 + 1.20 = **2.20 FRJ/h**

A nivel 20: 2.20 × 3.0 = **6.60 FRJ/h** — ¡más de 6 veces lo que genera el Axolotito Épico completo!

Y un **Astral completo** con rasgos Míticos:
- Piel Astral: 2.50 FRJ/h base
- 6 partes Míticas: 6 × 0.20 = 1.20
- Tasa base: 3.70 FRJ/h
- A nivel 20: 3.70 × 3.0 = **11.10 FRJ/h**

---

## Rasgos Míticos por Pureza Genética

Durante el proceso de imprinting (incubación avanzada), existe la posibilidad de que la **pureza genética** supere el 110%. Cuando esto ocurre — un evento extremadamente raro — hay un **25% de probabilidad** de que el Axolotito herede uno de estos rasgos Míticos:

- **Branquias Fénix** (Phoenix Gills)
- **Cola Plasma** (Plasma Tail)
- **Frente Halo** (Halo Forehead)
- **Boca Divina** (Divine Mouth)
- **Extremidades Coral** (Coral Limbs)

Un rasgo Mítico no solo se ve espectacular, sino que añade **0.20 FRJ/h** por esa parte, el bono más alto posible por pieza individual.

---

## Colores de Borde por Rareza en el Juego

Cada Axolotito muestra un borde visual alrededor de su carta que indica su rareza general:

| Rareza | Color de Borde | Efecto Visual |
|--------|---------------|---------------|
| Común | Gris pizarra (Slate gray) | Estático |
| Rara | Verde azulado (Teal cyan) | Estático |
| Épica | Cian brillante (Bright cyan) | Estático |
| Legendaria | Violeta (Violet) | Brillo sutil |
| Mítica | Dorado (Gold) | Brillo animado ondulante |
| Astral | Especial | Efecto único |

---

## Slots de Equipamiento Cosmético

Los Axolotitos tienen 3 slots de equipamiento puramente cosmético (no afectan estadísticas ni staking):

| Slot | Ejemplos de Ítems |
|------|------------------|
| **Cabeza** (Head) | Sombreros, coronas, cascos |
| **Ojos** (Eyes) | Lentes, gafas, goggles |
| **Cuerpo** (Body) | Ropa, capas, armaduras |

Estos ítems se obtienen en:
- **Gashapon** (máquina de cápsulas estilo japonés)
- **Mercado P2P** (compra/venta entre jugadores)
- **Eventos especiales** (temporadas, torneos, colaboraciones)

---

## Valor en el Mercado P2P

Los rasgos visuales raros disparan el precio de un Axolotito en el mercado P2P. La percepción de rareza y belleza impulsa la demanda:

- Un Axolotito **Común rosa** con todas las partes básicas puede valer poco más que el costo de incubación.
- Un Axolotito **Astral** con Branquias Fénix y Boca Divina puede valer entre **10× y 50×** el precio de un Común.
- Los **rasgos Míticos individuales** (Fénix, Plasma, Halo, Divina, Coral) multiplican el valor incluso en pieles no-Astrales.
- El **borde dorado animado** de un Mítico es inmediatamente reconocible y muy cotizado por coleccionistas.

La caza de rasgos — "trait hunting" — es uno de los pilares de la economía de Axolotto: incubar, cruzar, vender y coleccionar los Axolotitos más raros y hermosos del metaverso.

---



### 06-como-jugar-loteria
> `conceptos/06-como-jugar-loteria.md`

---
tags: [conceptos, gameplay]
description: "Cómo jugar Lotería en Axolotto — guía completa del loop de juego | How to play Lotería in Axolotto — complete game loop guide"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Cómo Jugar Lotería en Axolotto

¡Bienvenidx al corazón de Axolotto! Esta es tu guía completa para entender cada mecánica, cada regla, y cada truco del juego. Si solo lees una página de esta wiki, que sea esta.

---

## ¿Qué es la Lotería?

La Lotería es un juego de cartas tradicional mexicano con más de 200 años de historia, similar al bingo pero infinitamente más colorido. En lugar de números, tienes 54 cartas únicas con personajes icónicos:

> 🐓 **El Gallo** · 🌙 **La Luna** · ☀️ **El Sol** · 👩 **La Dama** · 🌵 **El Nopal** · 💀 **La Calavera** · 🌹 **La Rosa** · 🐟 **El Pescado** · 🕷️ **La Araña** · 🎻 **El Violoncello** ... y 44 más.

Un **cantador** (en Axolotto lo llamamos el **Gritón** 🤖) va anunciando cartas una por una. Tú marcas las que coinciden con tu **Tabla** (tu tablero personal de 4×4). El primero en completar un patrón ganador... ¡gana!

---

## Tu Tabla: El Tablero de 4×4

Tu Tabla es una cuadrícula de **4×4 = 16 cartas** que seleccionas de tu colección personal. Es tu "cartón de bingo", pero con personajes en vez de números.

### Datos clave sobre las Tablas:

| Propiedad | Detalle |
|-----------|---------|
| **Tamaño** | 4 filas × 4 columnas = 16 posiciones |
| **Origen de las cartas** | Tu colección personal (las obtienes en Sobrecitos, el mercado P2P, o con Códigos) |
| **¿Importa la posición?** | ¡Sí! Cada posición es estratégica — ciertos patrones ganadores requieren posiciones específicas |
| **Creación aleatoria** | Cuesta **25 FRJ** — el sistema elige 16 cartas al azar de tu colección |
| **Creación manual** | Cuesta **50 FRJ** — tú decides exactamente qué carta va en cada celda |
| **¿Cuántas puedo tener?** | Las que quieras. Puedes coleccionar múltiples Tablas y elegir cuál usar en cada partida |

> 🎯 **Tip estratégico:** Diseñar tu Tabla manualmente vale la pena. Puedes optimizar posiciones para patrones específicos o armar "zonas calientes" donde concentras tus mejores cartas.

---

## El Loop de Juego, Paso a Paso

Cada partida de Lotería en Axolotto sigue este flujo exacto:

### 🦎 Paso 1 — Elige tu Axolotito
Tu Axolotito es tu avatar y tu "mano" en el juego. Sus estadísticas importan:
- **OJO (Focus)** → afecta la probabilidad de marcar cartas correctamente
- **SUERTE (Luck)** → afecta premios y salvaciones milagrosas
- **SAL (Salinity)** → afecta la posición de tus cartas en el mazo

### 📋 Paso 2 — Elige tu(s) Tabla(s)
- **Modo CPU (Solo):** 1 Tabla por partida
- **Modo Multijugador:** hasta 3 Tablas simultáneas

### 🏠 Paso 3 — Elige la Sala
| Sala | Entrada (buy-in) | Dificultad / Jugadores |
|------|-------------------|------------------------|
| **Novatos (Rookies)** | 25 FRJ | 1 bot fácil (CPU) · hasta 30 humanos (multi) |
| **Campeones (Champions)** | 100 FRJ | 5 bots difíciles (CPU) · hasta 30 humanos (multi) |

### ✖️ Paso 4 — Ajusta el Multiplicador (opcional)
Puedes multiplicar tu apuesta para premios proporcionalmente mayores:
- **1×** (normal) · **2×** · **5×** · **10×**

El multiplicador aplica tanto a tu entrada como a tus premios. Alto riesgo, alta recompensa.

### 🎤 Paso 5 — El Gritón Canta las Cartas
El Gritón baraja un mazo completo de 54 cartas y empieza a anunciarlas una por una. Tu Axolotito automáticamente intenta marcar las cartas que coinciden con tu Tabla.

### 🎯 Paso 6 — Mecánica de Marcado (Miss Chance)
Aquí está el truco: **no siempre marcas la carta aunque esté en tu Tabla.**

- Tu stat de **OJO (Focus)** determina tu precisión
- Hay una probabilidad de fallo del **0% al 30%** dependiendo de qué tan alto sea tu OJO
- A más OJO, menos fallos. Simple.

### 🧂 Paso 7 — Sesgo del Mazo (Salinity)
Tu stat de **SAL (Salinity)** es MALO para ti:
- Empuja tus cartas hacia el **final del mazo**
- A más SAL, más tarde aparecen tus cartas
- Esto significa que jugadores con menos SAL tienen ventaja — sus cartas salen antes

### 🏆 Paso 8 — Determinar Ganador
El primero en completar un **patrón ganador** gana la ronda. Hay dos premios en juego:

### 🏆 Paso 9 — Premios
| Premio | Condición | Porcentaje del pozo |
|--------|-----------|---------------------|
| **Premio 1** | Primer patrón completado (línea, cuadrito, esquinas, etc.) | **35%** del pozo |
| **Premio 2 (¡Lotería!)** | Tabla completa — las 16 cartas marcadas | **55%** del pozo |
| **Jackpot** | Contribución automática | **5%** del pozo |
| **Tesorería (House)** | Comisión del sistema | **5%** del pozo |

- Los premios se reparten entre todos los ganadores del mismo nivel
- **Regla del Doble Ganador:** ¡el mismo jugador PUEDE ganar Premio 1 Y Premio 2 en la misma partida!

---

## Modo CPU (Solo / vs Bots)

Perfecto para practicar, jugar rápido, o cuando no hay salas multijugador disponibles.

| Característica | Sala Novatos | Sala Campeones |
|----------------|-------------|----------------|
| **Bots** | 1 bot fácil | 5 bots difíciles |
| **Entrada** | 25 FRJ | 100 FRJ |
| **Premio por ganar** | 85 FRJ | 400 FRJ |
| **Consolación (no ganar)** | 8 FRJ | 20 FRJ |
| **Resolución** | Instantánea (segundos) | Instantánea (segundos) |

### Racha de Victorias (Win Streak)
- Cada victoria consecutiva te da un **+15% de bonificación** sobre el premio
- El bono se acumula hasta un máximo de **+50%**
- Si pierdes una partida, la racha se reinicia a 0

---

## Modo Multijugador

El verdadero corazón competitivo de Axolotto.

### Características principales:
- **Hasta 30 jugadores humanos** por sala
- **Tiempo real:** todos juegan simultáneamente contra el mismo Gritón
- **Auto-AFK:** ¿Te tienes que ir? Tu Axolotito sigue jugando por ti automáticamente
- **Presupuesto inteligente:** configura límites de stop-loss (pérdida máxima) y take-profit (ganancia objetivo)
- **Auto-reinscripción:** tu Axolotito se re-inscribe automáticamente en nuevas rondas hasta que se alcancen tus límites o se agote su energía
- **Settlement (liquidación):** al terminar tu sesión, reclamas tu saldo acumulado + puntos de lealtad ganados

> 🤖 **El Gritón es compartido.** Todos los jugadores en la sala escuchan las mismas cartas en el mismo orden. Es justo para todos.

---

## Mecánicas Clave que Afectan tus Probabilidades

### 🎯 Miss Chance (Probabilidad de Fallo)
- **Depende de:** OJO (Focus) de tu Axolotito
- **Efecto:** Puede que NO marques una carta aunque esté en tu Tabla
- **Rango:** 0% (OJO máximo) hasta 30% (OJO mínimo)
- **Estrategia:** Entrena el OJO de tu Axolotito. Es la stat más importante para ganar.

### 🧂 Deck Bias / Sesgo del Mazo (Salinity)
- **Depende de:** SAL (Salinity) de tu Axolotito
- **Efecto:** Tus cartas se empujan hacia el final del mazo de 54 cartas
- **Estrategia:** Mantén la SAL baja. Usa items o mecánicas que reduzcan la salinidad.

### 🍀 Lucky Save (Salvación Milagrosa)
- **Depende de:** SUERTE (Luck) de tu Axolotito
- **Efecto:** Hasta **5% de probabilidad** de evitar una derrota cuando otro jugador está a punto de ganar
- **Estrategia:** La suerte no es tu plan A, pero puede salvarte el día.

### 🔥 Win Streak (Racha de Victorias)
- **Efecto:** Victorias consecutivas dan **+15% de bonus por victoria**, acumulable hasta **+50%**
- **Estrategia:** Si vienes ganando, sube el multiplicador. El riesgo vale la pena con el bono acumulado.

---

## El Jackpot (Pozo Acumulado Global) 💰

El Jackpot es un pozo global que crece con cada partida multijugador.

### Cómo funciona:
- Cada partida multijugador contribuye **5% del pozo** al Jackpot
- El Jackpot es **global** — compartido entre todas las salas y partidas

### Cómo ganarlo:
- Completar **Premio 1** (primer patrón) dentro de las primeras **4 a 6 cartas** cantadas por el Gritón
- Debe haber al menos **5 Tablas humanas** de **2+ wallets diferentes** en la sala
- El ganador se lleva **90% del Jackpot acumulado**

### Datos del Jackpot:
- **Semilla inicial:** 1,000 FRJ
- **Contribución por partida:** 5% del pozo total
- **Premio:** 90% del acumulado para quien lo rompa
- **Mínimo de jugadores:** 5 Tablas humanas, 2+ wallets distintas

> 🌟 Romper el Jackpot es el logro más épico de Axolotto. Requiere una combinación de Tabla perfecta, OJO altísimo, y un poquito de magia.

---

## Sistema de Tensión

Para hacer cada partida emocionante, Axolotto tiene un **sistema visual de tensión** que refleja qué tan cerca está alguien de ganar:

| Nivel | Significado | Efecto visual |
|-------|-------------|---------------|
| **Baja (Low)** | Todos lejos de ganar | Interfaz tranquila, colores normales |
| **Media (Medium)** | Alguien se acerca a un patrón | Ligero calentamiento de la paleta de colores |
| **Alta (High)** | Varios jugadores cerca de ganar | Efectos de pulso, bordes vibrantes |
| **Crítica (Critical)** | Alguien a 1 celda de completar patrón | Viñeta de "latido" (heartbeat vignette), máxima intensidad |

El sistema de tensión NO afecta las mecánicas — es puramente cosmético. Pero convierte cada partida en un momento dramático digno de stream.

---

## Resumen Rápido para Novatos

1. 🦎 Consigue un Axolotito con buen OJO
2. 📋 Crea una Tabla (25 FRJ aleatoria o 50 FRJ manual)
3. 🏠 Entra a la sala Novatos (25 FRJ)
4. ✖️ Deja el multiplicador en 1× por ahora
5. 🎤 Mira al Gritón cantar cartas — tu Axolotito juega solo
6. 🏆 Si ganas Premio 1: 35% del pozo · Si completas la tabla (Premio 2): 55%
7. 🔥 Gana varias seguidas para acumular Win Streak (+15% por victoria, máx +50%)
8. 💰 Cuando te sientas listx, salta a Campeones o al Multijugador

---

## Preguntas Frecuentes (FAQ)

**¿Puedo cambiar de Tabla a media partida?**
No. La Tabla se bloquea al inicio de cada ronda.

**¿Qué pasa si dos jugadores completan el mismo patrón en la misma carta?**
El premio se divide equitativamente entre ambos.

**¿Puedo jugar sin Axolotito?**
No. Necesitas un Axolotito para jugar — es quien marca las cartas por ti.

**¿El Gritón favorece a alguien?**
No. El mazo se baraja con aleatoriedad criptográfica (`SystemRandom`). Es completamente justo.

**¿Puedo ganar Premio 1 y Premio 2 en la misma partida?**
¡Sí! La regla del Doble Ganador lo permite. Si completas un patrón primero Y luego terminas tu tabla completa, te llevas ambos premios.

**¿El Jackpot aplica en modo CPU?**
No. Solo partidas multijugador con 5+ Tablas humanas y 2+ wallets distintas.

**¿Qué pasa si me salgo a media partida en multijugador?**
Tu Axolotito sigue jugando en Auto-AFK hasta que termine la ronda. Recibes tus premios normalmente.

---



### 07-patrones-ganadores
> `conceptos/07-patrones-ganadores.md`

---
tags: [conceptos, gameplay, patrones]
description: "Todos los patrones ganadores de Lotería — líneas, cuadritos, cruz, esquinas y más | All winning Lotería patterns — lines, squares, cross, corners and more"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Patrones Ganadores

En Axolotto, ganar una ronda de Lotería significa marcar en tu Tabla un **patrón específico** de celdas antes que los demás jugadores. El patrón requerido depende del modo de juego y de la sala donde estés jugando. No todas las salas usan los mismos patrones: las salas Rookies mantienen las cosas simples, mientras que las salas de Campeones y las salas alojadas por jugadores desbloquean patrones más difíciles (y más gratificantes).

---

## El Tablero (4×4)

Todas las Tablas de Lotería en Axolotto son cuadrículas de 4 filas × 4 columnas, con posiciones numeradas del 0 al 15:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

Cada celda contiene una carta del mazo tradicional de Lotería Mexicana (El Gallo, La Dama, El Corazón, etc.). El dealer saca cartas una por una, y tú marcas las celdas que coinciden.

---

## 1. Línea (Line)

Una línea completa es **4 celdas consecutivas en cualquier dirección**: fila, columna o diagonal.

**Total de variantes: 10**

### Filas (4 variantes)

```
Fila 0:               Fila 1:               Fila 2:               Fila 3:
 ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·           ■  ■  ■  ■
 Celdas: {0,1,2,3}    Celdas: {4,5,6,7}    Celdas: {8,9,10,11}  Celdas: {12,13,14,15}
```

### Columnas (4 variantes)

```
Col 0:                Col 1:                Col 2:                Col 3:
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 ■  ·  ·  ·           ·  ■  ·  ·           ·  ·  ■  ·           ·  ·  ·  ■
 Celdas: {0,4,8,12}   Celdas: {1,5,9,13}   Celdas: {2,6,10,14}  Celdas: {3,7,11,15}
```

### Diagonales (2 variantes)

```
Diagonal ↘            Diagonal ↙
 ■  ·  ·  ·           ·  ·  ·  ■
 ·  ■  ·  ·           ·  ·  ■  ·
 ·  ·  ■  ·           ·  ■  ·  ·
 ·  ·  ·  ■           ■  ·  ·  ·
 Celdas: {0,5,10,15}  Celdas: {3,6,9,12}
```

**Dificultad**: Fácil (4 celdas)

**Disponible en**: TODAS las salas — Rookies, Champions y salas alojadas por jugadores.

**Premio**: Premio 1 (el premio base por patrón). Es el patrón más común y el primero que todo jugador aprende a buscar.

**Estrategia**: Revisa siempre las 10 líneas posibles cada vez que marques una celda. Las esquinas (0, 3, 12, 15) aparecen en más líneas que las celdas del borde medio, y las celdas del centro (5, 6, 9, 10) aparecen en aún más patrones. Prioriza tablas que ya tengan varias celdas en una misma línea.

---

## 2. Cuadrito (2×2 Block)

Un bloque de **2 filas × 2 columnas** contiguas. Cualquier grupo de 4 celdas que formen un cuadrado.

**Total de variantes: 9**

```
Top-Izquierda         Top-Centro            Top-Derecha
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Celdas: {0,1,4,5}    Celdas: {1,2,5,6}    Celdas: {2,3,6,7}

Mid-Izquierda         Centro                Mid-Derecha
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 Celdas: {4,5,8,9}    Celdas: {5,6,9,10}   Celdas: {6,7,10,11}

Bottom-Izquierda      Bottom-Centro         Bottom-Derecha
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ·  ·  ·  ·           ·  ·  ·  ·           ·  ·  ·  ·
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 ■  ■  ·  ·           ·  ■  ■  ·           ·  ·  ■  ■
 Celdas: {8,9,12,13}  Celdas: {9,10,13,14} Celdas: {10,11,14,15}
```

**Dificultad**: Media (4 celdas, pero contiguas en 2D)

**Disponible en**: TODAS las salas — Rookies, Champions y salas alojadas por jugadores.

**Estrategia**: El cuadrito recompensa tener celdas agrupadas en una misma zona del tablero. Si tu tabla tiene un "cluster" natural de cartas marcadas en una esquina, enfócate en completar ese cuadrito. Las celdas centrales (5, 6, 9, 10) pertenecen a 4 cuadritos distintos — son las más valiosas para este patrón.

---

## 3. Pocito (Center)

Exactamente el **bloque central de 2×2**. A diferencia del Cuadrito general, el Pocito es un patrón fijo: solo hay una ubicación posible.

```
Pocito
 ·  ·  ·  ·
 ·  ■  ■  ·
 ·  ■  ■  ·
 ·  ·  ·  ·
 Celdas: {5, 6, 9, 10}
```

**Dificultad**: Media (4 celdas, pero ubicación fija)

**Disponible en**: Sala Champions + salas alojadas por jugadores. **No disponible en Rookies.**

**Estrategia**: Como el Pocito siempre está en el centro, vale la pena priorizar las cartas centrales (posiciones 5, 6, 9, 10) desde el inicio si estás en una sala donde este patrón está activo. Estas mismas celdas también te ayudan con Línea y Cuadrito, así que nunca son una mala inversión.

---

## 4. Esquinas (4 Corners)

Las **4 esquinas** del tablero. Otro patrón fijo de una sola ubicación.

```
Esquinas
 ■  ·  ·  ■
 ·  ·  ·  ·
 ·  ·  ·  ·
 ■  ·  ·  ■
 Celdas: {0, 3, 12, 15}
```

**Dificultad**: Media (4 celdas, dispersas)

**Disponible en**: Sala Champions + salas alojadas por jugadores. **No disponible en Rookies.**

**Estrategia**: Las esquinas son celdas de alto valor porque también participan en Líneas (son extremos de filas, columnas y una diagonal). Marcar esquinas temprano te acerca a múltiples patrones simultáneamente. Si ya tienes 2 o 3 esquinas marcadas y estás en Champions, cambia tu prioridad a conseguir la cuarta.

---

## 5. Cruz (Cross)

Una **fila completa + una columna completa** que se intersectan. El resultado es una cruz en el tablero.

**Total de variantes: 16** (4 filas × 4 columnas)

**Ejemplo — Fila 0 + Columna 2:**

```
Cruz (Fila 0, Col 2)
 ■  ■  ■  ■
 ·  ·  ■  ·
 ·  ·  ■  ·
 ·  ·  ■  ·
 Celdas: {0,1,2,3, 6,10,14}
```

```
Cruz (Fila 1, Col 0)        Cruz (Fila 2, Col 3)        Cruz (Fila 0, Col 0)
 ■  ·  ·  ·                  ·  ·  ·  ■                  ■  ■  ■  ■
 ■  ■  ■  ■                  ·  ·  ·  ■                  ■  ·  ·  ·
 ■  ·  ·  ·                  ■  ■  ■  ■                  ■  ·  ·  ·
 ■  ·  ·  ·                  ·  ·  ·  ■                  ■  ·  ·  ·
 Celdas: {0,4,5,6,7,8,12}    Celdas: {3,7,8,9,10,11,15}  Celdas: {0,1,2,3,4,8,12}
```

**Dificultad**: Difícil (7 celdas — 4 de la fila + 4 de la columna, menos 1 de la intersección)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: Con 7 celdas requeridas, la Cruz es un patrón de media partida. Necesitas que el dealer saque cartas de una fila y una columna específicas. Busca intersecciones donde ya tengas varias celdas marcadas en ambas direcciones. La celda de intersección cuenta una sola vez, así que si ya la tienes, solo necesitas 6 celdas adicionales.

---

## 6. Cruz Diagonal (X Shape)

**Ambas diagonales** simultáneamente, formando una X completa en el tablero.

```
Cruz Diagonal (X)
 ■  ·  ·  ■
 ·  ■  ■  ·
 ·  ■  ■  ·
 ■  ·  ·  ■
 Celdas: {0, 3, 5, 6, 9, 10, 12, 15}
```

**Dificultad**: Muy Difícil (8 celdas — las 4 de cada diagonal; las celdas centrales 5,6,9,10 NO se intersectan con las diagonales principales, por lo que el patrón completo abarca 8 celdas distintas)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Nota importante**: Las dos diagonales del tablero 4×4 son:
- Diagonal ↘: {0, 5, 10, 15}
- Diagonal ↙: {3, 6, 9, 12}

Estas 8 celdas NO comparten ninguna posición entre sí, por lo que la Cruz Diagonal requiere marcar exactamente 8 celdas. Sin embargo, 4 de ellas son esquinas (0, 3, 12, 15), que son celdas de alto valor estratégico.

**Estrategia**: Este patrón combina perfectamente con Esquinas (4 esquinas + 4 celdas internas de las diagonales). Si el host activa ambos patrones, prioriza las esquinas y las celdas {5, 6, 9, 10} para maximizar tu progreso hacia ambos patrones.

---

## 7. L-Shape

Una **L** que abarca un borde completo del tablero: una fila completa + una columna completa que nacen de una misma esquina.

**Total de variantes: 4** (una por cada esquina)

```
L Noroeste (NW)        L Noreste (NE)         L Suroeste (SW)        L Sureste (SE)
 ■  ■  ■  ■            ■  ■  ■  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ·  ·  ·            ·  ·  ·  ■
 ■  ·  ·  ·            ·  ·  ·  ■            ■  ■  ■  ■            ■  ■  ■  ■
 Celdas:                Celdas:                Celdas:                Celdas:
 {0,1,2,3, 4,8,12}     {0,1,2,3, 7,11,15}    {12,13,14,15, 0,4,8}  {12,13,14,15, 3,7,11}
 7 celdas               7 celdas               7 celdas               7 celdas
```

**Dificultad**: Difícil (7 celdas en NW y SW; 6 celdas en NE y SE porque la esquina se comparte — pero en NW y SW la esquina de intersección 0 o 12 ya pertenece a la fila, así que son 7 celdas en los 4 casos: 4 de fila + 3 de columna adicionales, ya que la celda esquina pertenece a ambas)

Nota: En los 4 casos, la celda de la esquina se comparte entre la fila y la columna. Son 4 celdas de la fila + 4 celdas de la columna − 1 compartida = 7 celdas.

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: Si tu tabla tiene una esquina marcada y varias celdas en la fila y columna adyacentes, una L-Shape puede ser tu camino más rápido a la victoria. Las L-Shapes NW y SW comparten la columna izquierda; las NE y SE comparten la columna derecha.

---

## 8. Z-Shape

Un patrón en zigzag que recorre el tablero. Dos variantes: **Z normal** y **S (Z invertida)**.

**Total de variantes: 2**

```
Z-Shape (normal)                          S-Shape (Z invertida)
 ■  ■  ■  ■                               ·  ·  ·  ■
 ·  ·  ·  ■                               ·  ·  ■  ·
 ·  ■  ·  ·                               ·  ■  ·  ·
 ■  ■  ■  ■                               ■  ■  ■  ■
 Celdas:                                   Celdas:
 Fila 0 + celda 7 + celda 9 + Fila 3      Celda 3 + celda 6 + celda 9 + Fila 3
 = {0,1,2,3, 7, 9, 12,13,14,15}          = {3, 6, 9, 12,13,14,15}
 10 celdas                                 7 celdas

Nota: La Z-Shape requiere:
- Z normal: Fila 0 entera + Fila 3 entera + celda 7 (conecta fila 0 con fila 2) + celda 9 (conecta fila 2 con fila 3)
           = {0,1,2,3, 7, 9, 12,13,14,15} → 10 celdas
- S invertida: celda 3 (fila 0) + celda 6 (fila 1) + celda 9 (fila 2) + Fila 3 entera
             = {3, 6, 9, 12,13,14,15} → 7 celdas
```

**Dificultad**: Muy Difícil (10 celdas para Z normal; 7 celdas para S invertida)

**Disponible en**: **Solo salas alojadas por jugadores**. No disponible en Rookies ni Champions.

**Estrategia**: La Z-Shape normal es el patrón más grande después de Tabla Llena (10 de 16 celdas). Requiere paciencia y una tabla favorable. La S-Shape es más accesible con 7 celdas. En ambos casos, necesitas que el mazo coopere sacando cartas de zonas muy específicas del tablero.

---

## 9. Tabla Llena (Full Board) — ¡Lotería!

Las **16 celdas** marcadas. El patrón definitivo. Cuando gritas "¡Lotería!" con la tabla llena, has ganado el premio máximo de la ronda.

```
Tabla Llena
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 ■  ■  ■  ■
 Celdas: {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}
```

**Dificultad**: Extrema (las 16 celdas — requiere que el dealer saque prácticamente todo el mazo)

**Disponible en**: **TODAS las salas** — Rookies, Champions y salas alojadas por jugadores.

**Premio**: Siempre es **Premio 2** (el premio mayor). En salas Rookies y Champions, Tabla Llena paga más que cualquier otro patrón. En salas alojadas, el host puede configurar la escala de premios.

**Estrategia**: Tabla Llena no se "busca" activamente — simplemente sucede si nadie gana con los patrones más pequeños y el dealer sigue sacando cartas. Si llegas a 12+ celdas marcadas sin que nadie haya ganado, empieza a prestar mucha atención: estás cerca. La tensión en este punto es máxima.

---

## Resumen de Patrones

| # | Patrón | Celdas | Dificultad | Rookies | Champions | Player-Hosted |
|---|--------|--------|------------|---------|-----------|---------------|
| 1 | Línea | 4 | Fácil | ✅ | ✅ | ✅ |
| 2 | Cuadrito | 4 | Media | ✅ | ✅ | ✅ |
| 3 | Pocito | 4 | Media | ❌ | ✅ | ✅ |
| 4 | Esquinas | 4 | Media | ❌ | ✅ | ✅ |
| 5 | Cruz | 7 | Difícil | ❌ | ❌ | ✅ |
| 6 | Cruz Diagonal | 8 | Muy Difícil | ❌ | ❌ | ✅ |
| 7 | L-Shape | 7 | Difícil | ❌ | ❌ | ✅ |
| 8 | Z-Shape | 7-10 | Muy Difícil | ❌ | ❌ | ✅ |
| 9 | Tabla Llena | 16 | Extrema | ✅ | ✅ | ✅ |

---

## El Sistema de Tensión (Tension System)

A medida que los jugadores se acercan a completar un patrón, el sistema de tensión de Axolotto ajusta la experiencia de juego. La barra de tensión indica qué tan cerca está **alguien** (tú u otro jugador) de ganar. No es un valor por jugador — es un estado global de la sala que todos pueden ver.

**Niveles de Tensión:**

| Nivel | Significado | Efecto |
|-------|-------------|--------|
| **Baja (Low)** | Nadie tiene más de 2 celdas en ningún patrón activo. El juego apenas comienza. | Ritmo normal. Sin presión. |
| **Media (Medium)** | Al menos un jugador tiene 3 celdas en un patrón activo (a 1 de ganar en Línea/Cuadrito/Pocito/Esquinas). | La música se intensifica ligeramente. Los jugadores empiezan a prestar más atención a las cartas que salen. |
| **Alta (High)** | Al menos un jugador está a **1 celda** de completar un patrón — o varios jugadores tienen 3 celdas en patrones distintos. | Efectos visuales en la UI (bordes del tablero pulsan). El dealer saca cartas más rápido. La adrenalina sube. |
| **Crítica (Critical)** | Múltiples jugadores están a 1 celda de ganar, o alguien está a 1 celda de Tabla Llena (15/16). | Efectos visuales máximos. La sala entera sabe que el próximo turno puede ser el último. |

**Cómo usar el Sistema de Tensión a tu favor:**

- Si la tensión está **Baja**, juega relajado. Prioriza marcar celdas que te sirvan para múltiples patrones.
- Si la tensión está **Media**, enfócate en el patrón donde estás más cerca. No te disperses.
- Si la tensión está **Alta**, revisa el tablero rápido: ¿quién está a punto de ganar? Si eres tú, aguanta la respiración. Si es otro, prepárate para la derrota.
- Si la tensión está **Crítica**, todo puede terminar en la próxima carta. Es el momento de mayor emoción en Axolotto.

---

## Configuración en Salas Alojadas por Jugadores

Cuando un jugador crea una sala (Player-Hosted Room), puede elegir qué patrones están activos. Esto permite modos de juego personalizados:

- **Modo Clásico**: Solo Línea + Cuadrito + Tabla Llena (como Rookies).
- **Modo Avanzado**: Línea + Cuadrito + Pocito + Esquinas + Tabla Llena (como Champions).
- **Modo Caótico**: Todos los patrones activos. Hasta 9 formas distintas de ganar en una sola ronda.
- **Modo Personalizado**: El host elige manualmente qué patrones activar. ¿Solo Cruz y Cruz Diagonal? ¿Solo L-Shapes? La decisión es tuya.

El host también puede configurar:
- **Premios por patrón**: Cuánto paga cada patrón en AXF y FRJ.
- **Límite de tiempo por ronda**: Tiempo máximo antes de que la ronda termine automáticamente.
- **Número máximo de ganadores**: ¿Gana el primero o pueden ganar varios?

---

## Consejos Generales para Todos los Patrones

1. **Las celdas centrales (5, 6, 9, 10) son las más valiosas**: Participan en 2 diagonales + 2 filas + 2 columnas + 4 cuadritos + 1 Pocito. Son las celdas más conectadas del tablero.

2. **Las esquinas (0, 3, 12, 15) son el segundo mejor grupo**: Cada esquina participa en 1 fila + 1 columna + 1 diagonal + 1 cuadrito + Esquinas + L-Shape + Cruz Diagonal.

3. **Las celdas del borde medio (1, 2, 4, 7, 8, 11, 13, 14) son las menos conectadas**: Solo participan en 1 fila + 1 columna (las de la mitad de borde) o 1 diagonal (si están en la diagonal). Planifica con cuidado.

4. **No te cases con un solo patrón**: La mejor estrategia es mantener abiertas varias rutas hacia la victoria. Marcar una celda debe acercarte a al menos 2 patrones simultáneamente.

5. **Observa a tus rivales**: En multijugador, si ves que alguien está a punto de completar un patrón, considera si puedes ganar antes con otro patrón diferente.

---



### 08-modos-de-juego
> `conceptos/08-modos-de-juego.md`

---
tags: [conceptos, gameplay, modos]
description: "Todos los modos de juego en Axolotto — CPU, Multijugador, PvP Manual, Saladito y Espectador | All game modes in Axolotto — CPU, Multiplayer, Manual PvP, Saladito and Spectator"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Modos de Juego

Axolotto ofrece **cinco modos de juego** distintos para que cada tipo de jugador encuentre su lugar, desde el competidor casual que quiere echar una partida rápida contra bots hasta el coleccionista F2P que apenas está empezando y quiere ganar sus primeras recompensas sin tener un axolotito propio. Aquí te explicamos cada uno en detalle.

---

## 1. Modo CPU (Solo vs Bots)

El modo principal PvE del juego. Te enfrentas a bots controlados por el sistema en partidas rápidas de Lotería. Perfecto para practicar, farmear Frijolitos y subir de nivel a tus axolotitos sin la presión de jugar contra humanos.

### Salas disponibles

| Sala | Nombre | Bots | Dificultad | Entrada | Premio | Consuelo |
|------|--------|------|------------|---------|--------|----------|
| Rookies | Charco de Novatos | 1 bot fácil | Focus 40 (~18% fallo) | 25 FRJ | 85 FRJ | 8 FRJ |
| Champions | Fosa del Campeón | 5 bots duros | Focus 80 (~6% fallo) | 100 FRJ | 400 FRJ | 20 FRJ |

### Multiplicadores

Puedes multiplicar tu apuesta y ganancias con estos multiplicadores:

| Multiplicador | Entrada Rookies | Premio Rookies | Entrada Champions | Premio Champions |
|---------------|-----------------|----------------|-------------------|------------------|
| 1× | 25 FRJ | 85 FRJ | 100 FRJ | 400 FRJ |
| 2× | 50 FRJ | 170 FRJ | 200 FRJ | 800 FRJ |
| 5× | 125 FRJ | 425 FRJ | 500 FRJ | 2,000 FRJ |
| 10× | 250 FRJ | 850 FRJ | 1,000 FRJ | 4,000 FRJ |

### Experiencia (axo XP)

- **Rookies**: 25–35 axo XP por victoria, 8 axo XP por derrota
- **Champions**: 60–75 axo XP por victoria, 15 axo XP por derrota

### Racha de victorias

Cada victoria consecutiva suma **+15%** de bonificación sobre el premio base, con un tope máximo de **+50%** (4 victorias seguidas). Si pierdes, la racha se reinicia.

### Costo de energía

Siempre **10 de energía** por partida, sin importar el multiplicador o la sala.

### Cómo jugar

1. Selecciona tu axolotito activo desde tu inventario
2. Elige un tablero de Lotería (o crea uno nuevo en el Editor de Tableros)
3. Escoge la sala: Charco de Novatos o Fosa del Campeón
4. Selecciona tu multiplicador
5. ¡Presiona Jugar! El resultado se resuelve en segundos

---

## 2. Modo Multijugador (Auto-AFK)

El modo competitivo principal. Partidas en tiempo real con hasta **30 jugadores humanos** por sala. Tu axolotito juega automáticamente — tú configuras la estrategia y él se encarga del resto.

### Salas multijugador

| Sala | Entrada | Premio base |
|------|---------|-------------|
| Rookies (Charco de Novatos) | 10 FRJ | Varía según participantes |
| Champions (Fosa del Campeón) | 50 FRJ | Varía según participantes |

### Auto-AFK: configura tu estrategia

- **Presupuesto (stop-loss)**: límite máximo de FRJ que estás dispuesto a perder. Cuando se alcanza, tu axolotito deja de jugar.
- **Take-profit**: límite de ganancias. Cuando lo alcanzas, retira tus ganancias automáticamente.
- **Auto-reinscripción**: tu axolotito se reinscribe automáticamente en nuevas partidas hasta que se alcancen los límites o se quede sin energía.

### Liquidación (Settlement)

Al terminar de jugar, reclamas manualmente:
- Tus ganancias acumuladas en escrow (depósito de garantía)
- Puntos de lealtad (Loyalty Points) por cada partida completada

### Llenado de salas

Si hay menos de **4 jugadores humanos**, el sistema llena la sala con bots para garantizar que la partida se juegue. Los bots en multijugador usan la misma lógica que en modo CPU pero con nombres aleatorios.

### Tiempos de inicio

| Tableros inscritos | Tiempo de espera |
|--------------------|------------------|
| 30+ tableros | Inicio instantáneo |
| 15–29 tableros | 15 segundos |
| 5–14 tableros | 30 segundos |
| 1–4 tableros | 60 segundos |

### Costo de energía

Fórmula: **10 + (salinity × 0.2)** por ronda, con un máximo de **30 de energía** por partida. Axolotitos con alta salinidad gastan más energía en multijugador — otro factor estratégico a considerar.

---

## 3. Modo PvP Manual (Interactivo)

El modo más intenso y competitivo. NO está abierto permanentemente — solo se activa durante **eventos especiales** creados por los administradores.

### Diferencias clave con los otros modos

- **Marcado manual**: tú mismo haces clic en las cartas de tu tablero. No hay auto-marcado.
- **Estadística de Agilidad**: la velocidad con la que se marca una carta depende de tu stat de Agilidad. El retraso de marcado varía entre **800 ms** (agilidad alta) y **2,500 ms** (agilidad baja).
- **¡Lotería! manual**: puedes gritar "¡Lotería!" para reclamar la victoria en el momento exacto. Si gritas sin tener el patrón completo, pierdes puntos.
- **WebSocket en tiempo real**: conexión directa al servidor para latencia mínima.
- **El Gritón llama cartas**: un narrador automático (El Gritón) anuncia las cartas en un temporizador configurable por el admin.

### Salas hospedadas por jugadores (Cuevita Host)

Un jugador con suficientes Frijolitos puede crear su propia sala PvP privada:
- Configurar el temporizador del Gritón
- Invitar a amigos específicos
- Establecer la entrada y premios personalizados
- Elegir si aplicar reglas especiales (como Saladito)

### Multiplicadores de XP

Durante eventos PvP Manual, los multiplicadores de XP son **más altos** que en cualquier otro modo, haciendo que estos eventos sean la forma más rápida de levelear axolotitos raros.

---

## 4. Modo Saladito (Lotería Inversa)

El giro más divertido y caótico de la Lotería tradicional. Las reglas se **invierten**: gana el jugador que termine con **menos cartas marcadas** en su tablero.

### ¿Cuándo está disponible?

- **Automático**: todas las noches de **3:00 a 4:00 AM** hora del servidor (Ciudad de México, GMT-6)
- **Manual**: en salas privadas hospedadas por jugadores (Cuevita Host) en cualquier momento

### Reglas invertidas

- El Gritón sigue cantando cartas normalmente
- Tu axolotito intenta NO marcar cartas
- Gana quien tenga **menos cartas marcadas** al final de la ronda
- Si hay empate, gana el de mayor SAL (Salinidad)

### SAL se vuelve un beneficio

En modo normal, una SAL (Salinidad) alta es mala porque hace que las cartas se "resbalen" y no se marquen correctamente. Pero en modo Saladito, **esto es justo lo que quieres**. Un axolotito con SAL alta tiene más probabilidades de que las cartas se le resbalen — lo cual es BUENO en Saladito porque quieres tener pocas cartas marcadas.

Esto crea un meta divertido donde axolotitos que normalmente serían "malos" (alta salinidad) se vuelven repentinamente valiosos durante la hora Saladito.

### Recompensas especiales

- Premios en FRJ equivalentes al modo CPU Champions
- Posibilidad de obtener **Webitos con traits de Saladito** (rasgos especiales que solo se consiguen en este modo)
- Insignia temporal de "Rey del Saladito" si ganas 3 partidas consecutivas en una noche

---

## 5. Modo Espectador (F2P / El Espejo del Cenote)

El modo gratuito diseñado para jugadores que **no tienen axolotitos propios**. Puedes mirar partidas en vivo y ganar micro-recompensas participando como espectador.

### ¿Cómo funciona?

- Entras al **Espejo del Cenote**, el lobby de espectadores
- Eliges una partida activa para mirar
- Recibes un **Tablero Espejo** (Mirror Board): una copia exacta del tablero de un jugador real en esa partida
- Ves la partida en tiempo real desde la perspectiva de ese jugador

### Recompensas para espectadores

| Acción | Recompensa |
|--------|------------|
| El tablero espejo gana la partida | Hasta 10 FRJ/día |
| "Apoyar" (cheer) a un axolotito | Fragmentos Astrales de Webito |
| Tocar burbujas interactivas | Envías burbujas flotantes al jugador real |

### Fragmentos Astrales de Webito

- Los ganas al apoyar axolotitos y al mirar partidas completas
- **100 fragmentos = 1 Webito Común gratis**
- Límite diario: **10 fragmentos**

### Límites diarios

| Recurso | Límite diario |
|---------|---------------|
| FRJ | 10 FRJ |
| Fragmentos Astrales | 10 fragmentos |

### Toque interactivo

Como espectador, puedes tocar la pantalla para enviar **burbujas flotantes** al jugador que estás mirando. El jugador real ve estas burbujas aparecer en su pantalla — una forma divertida de mostrar apoyo sin afectar la partida.

---

## Tabla Comparativa

| Característica | CPU | Multijugador | PvP Manual | Saladito | Espectador |
|----------------|-----|--------------|------------|----------|------------|
| **Tipo** | PvE vs Bots | PvP Auto-AFK | PvP Interactivo | Lotería Inversa | Solo mirar |
| **Entrada** | 25–250 FRJ | 10–50 FRJ | Variable (evento) | 25–100 FRJ | Gratis |
| **Premio máx.** | 850 FRJ (10×) | Variable | Variable (alto) | 400 FRJ | 10 FRJ/día |
| **Jugadores** | 1 humano + bots | Hasta 30 humanos | 2–8 humanos | 1 humano + bots | Ilimitado |
| **Interacción** | Ninguna (auto) | Estrategia (config) | Clic manual | Ninguna (auto) | Burbujas tap |
| **Disponibilidad** | 24/7 | 24/7 | Solo eventos | 3–4 AM + privadas | 24/7 |
| **Energía** | 10 fija | 10–30 variable | 15 fija | 10 fija | 0 (no gasta) |
| **¿Requiere axolotito?** | Sí | Sí | Sí | Sí | No |
| **XP** | 8–75 axo XP | Similar a CPU | Multiplicado (evento) | Similar a CPU | 0 XP |
| **Racha** | +15%/victoria | +10%/victoria | +20%/victoria | No aplica | No aplica |

---



### 09-cartas
> `conceptos/09-cartas.md`

---
tags: [conceptos, gameplay, cartas]
description: "Las 54 cartas de Lotería Mexicana — rarezas, foil, colección | The 54 Mexican Lotería cards — rarities, foil, collection"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Cartas de Lotería

Las **Cartas de Lotería** son el corazón palpitante de Axolotto. Si el juego fuera un cuerpo, las cartas serían la sangre — fluyen por cada rincón del ecosistema, desde la tienda hasta el tablero, desde la forja hasta el mercado P2P. Sin cartas no hay tablas, sin tablas no hay partida, y sin partida… bueno, ¿para qué viniste?

Son 54 cartas únicas basadas en la Lotería Mexicana tradicional: **El Gallo**, **La Dama**, **El Diablito**, **La Luna**, **El Sol**, **El Corazón**, **La Mano**, **La Rosa**, **El Pescado**, **La Sirena**, **La Muerte**, **El Árbol**, **El Mundo**… cada una con su ilustración original estilo retro-moderno que mezcla la estética clásica del México vintage con un toque cyberpunk-axolote.

Cada carta es un token **ERC-1155**, lo que significa que pueden existir múltiples copias de la misma carta en circulación. No son únicas como los Axolotitos (ERC-721) — aquí la magia está en la rareza, el brillo, y la edición.

---

## Sistema de Rareza

No todas las cartas son iguales. Cuando abres un sobre, el universo decide qué te toca según este sistema de cinco niveles:

| Rareza | Color de Borde | Dificultad | Descripción |
|--------|---------------|------------|-------------|
| **Común** (Common) | Gris sutil | Base | Las ves en todos lados. El pan de cada día. Perfectas para empezar y para fundir en la forja. |
| **Rara** (Uncommon) | Verde azulado (teal) | Moderada | Ya empieza lo bueno. Un poquito más difíciles de conseguir, brillan con un borde cyan-verdoso. |
| **Épica** (Rare) | Cyan brillante | Difícil | Estas ya llaman la atención. El borde cyan eléctrico dice "mírame". Coleccionarlas todas es un logro. |
| **Legendaria** (Epic) | Violeta | Muy difícil | El borde violeta impone respeto. Cuando sale una en un sobre, el cuarto se ilumina. |
| **Mítica** (Legendary) | Dorado con resplandor | Extremadamente rara | Las *chase cards*. Borde dorado con glow animado. Si sacas una Mítica, tómale screenshot porque no pasa seguido. Son el santo grial de cualquier colección. |

El sistema de rareza no es cosmético — afecta el valor de tus tablas en partida, los fragmentos que obtienes al fundir, y por supuesto el precio en el mercado P2P.

---

## Variantes Especiales

Porque una carta no solo tiene rareza. También puede tener… *estilo*.

### Brillante (Foil / Shiny)

La variante **Brillante** aplica un degradado arcoíris animado sobre la ilustración de la carta. No es un PNG estático — la carta *vive*, reflejando colores que se mueven como una mancha de gasolina hipnótica.

- **Probabilidad**: ~3% en sobres foil, o como drop especial en Gashapon (según tier de cápsula).
- **Efecto en juego**: Cada carta foil en tu tabla otorga **+5% de rendimiento de FRJ** por partida, acumulable hasta **+80%** (16 cartas foil en una tabla 4x4). Si llenas una tabla completa de foil… eres leyenda.
- **Valor de mercado**: Altísimo. Los coleccionistas pagan lo que sea por foil de sus cartas favoritas. Una Mítica foil es básicamente un unicornio.

### Primera Edición (First Edition)

Marcada con una estrella dorada ⭐ en la esquina superior. Son las **primeras copias minteadas** de cada carta — las que salieron durante la Fase 1 (Genesis).

- **Valor de colección**: Significativamente mayor que una carta equivalente sin estrella.
- **Estatus**: Si tienes una ⭐, fuiste de los primeros. Eso se respeta.
- **Supply limitado**: Solo las unidades minteadas en Fase 1 reciben la marca. Cuando la fase se agota, no se producen más.

### Foil + Primera Edición

La **combinación definitiva**. Una carta que es Brillante Y Primera Edición es el objeto más raro del ecosistema de cartas. Si tienes una, enmárcala. Si tienes varias, abre un museo.

---

## Las 3 Fases de Emisión (Supply)

El suministro de cartas no es infinito. El sistema avanza por tres fases globales que determinan cuántas unidades se han emitido y a qué precio están los sobres.

### Fase 1 — Genesis (Primera Edición)

- **Unidades**: Primeras **420** unidades de cada sobre temático.
- **Brillo**: 15% de probabilidad de que una carta individual sea shiny.
- **Marcado**: Todas las cartas de esta fase reciben la estrella ⭐ de Primera Edición.
- **Estatus**: La fase de los early adopters. Cuando se agota, se acabó para siempre.

### Fase 2 — Expansión (Unlimited)

- **Unidades**: Siguientes **1,260** unidades de cada sobre temático.
- **Brillo**: 20% de probabilidad de que **una carta del sobre** sea shiny (no por carta, sino un slot garantizado con 20% de activarse).
- **Sin estrella**: Ya no llevan el marcador de Primera Edición.
- **Estatus**: La fase principal. La mayoría de jugadores empiezan aquí.

### Fase 3 — Retail

- **Unidades**: Últimas **2,520** unidades de cada sobre.
- **Precio**: Los sobres se encarecen en esta fase.
- **Estatus**: La recta final del suministro. Cuando Fase 3 se agota, ese tipo de sobre deja de venderse en tienda.

**Transición automática**: Cuando una fase se agota globalmente (todas las unidades vendidas), el sistema avanza a la siguiente sin intervención manual. No hay aviso previo — un día el sobre cuesta 6 AXF, y al siguiente amanece en Fase 2 a 10 AXF.

---

## Cómo Conseguir Cartas

Hay múltiples caminos hacia tu colección. No todos requieren abrir la cartera.

### 1. Sobres (Boosters) — La Tienda

La forma clásica. Vas a la tienda, compras un sobre, lo abres, y rezas a la diosa fortuna. Cada sobre contiene **7 cartas**.

Tipos de sobres:

| Tipo de Sobre | Cartas en el Pool | Temática |
|---------------|-------------------|----------|
| **Puro** | Las 54 cartas | Sin filtro — puede salir cualquier cosa. El sobre clásico. |
| **Fiesta** | 18 cartas | Colección festiva: El Gallo, La Dama, El Paraguas, El Sol, La Luna, y más — cartas de celebración. |
| **Nido** | 18 cartas | Colección naturaleza: El Árbol, La Rosa, El Pescado, La Sirena, El Camarón, El Pájaro — fauna y flora. |
| **Cosmos** | 18 cartas | Colección mística: La Muerte, El Diablito, La Estrella, El Mundo, La Luna — cartas del más allá. |
| **Foil (Brillante)** | 54 cartas, garantizado foil | Cada una de las 7 cartas es foil garantizado. El sobre premium. |

### 2. Precios por Fase

| Tipo | Fase 1 (AXF + FRJ) | Fase 2 (AXF + FRJ) | Fase 3 (AXF + FRJ) |
|------|---------------------|---------------------|---------------------|
| **Puro** | 6 AXF + 60 FRJ | 10 AXF + 100 FRJ | 15 AXF + 150 FRJ |
| **Fiesta** | 10 AXF + 100 FRJ | 15 AXF + 150 FRJ | 20 AXF + 200 FRJ |
| **Nido** | 10 AXF + 100 FRJ | 15 AXF + 150 FRJ | 20 AXF + 200 FRJ |
| **Cosmos** | 10 AXF + 100 FRJ | 15 AXF + 150 FRJ | 20 AXF + 200 FRJ |
| **Foil** | 80 AXF + 800 FRJ | — | — |

> **Nota**: El sobre Foil está limitado a **100 unidades por mes a nivel global**. Solo existe en Fase 1. Cuando se anuncian, se agotan en minutos. Activa notificaciones.

### 3. Gashapon — Las Cápsulas

Las máquinas de cápsulas Gashapon pueden soltar cartas como parte de su pool de premios. La probabilidad varía:

- **Tier básico**: ~28% de que una cápsula contenga al menos una carta.
- **Tier premium**: ~43% de probabilidad.
- **Tier VIP**: Hasta 50%, con posibilidad de rarezas altas y foil.

Ver [[14-capsulas-gashapon]] para el detalle completo.

### 4. Mercado P2P

¿Te sobra un duplicado de La Sirena foil? ¿Necesitas desesperadamente El Corazón para completar tu colección? El mercado P2P es tu lugar. Compra y vende cartas directamente con otros jugadores, en AXF o FRJ. Los precios los pone la comunidad.

Ver [[13-tienda-y-tianguis]] para más detalles.

### 5. Forja y Fundición (Card Melter)

¿Muchas duplicadas? La forja es tu salida. Convierte cartas que no necesitas en algo mejor. Ver [[18-forja-y-fundicion]] para el sistema completo.

Resumen rápido de fundición:

| Acción | Requisito | Costo | Resultado |
|--------|-----------|-------|-----------|
| **Fundir Común** | 5 cartas idénticas Comunes (no foil, no ⭐) | 100 FRJ | 1 carta Rara aleatoria + 10 fragmentos |
| **Fundir Rara** | 5 cartas idénticas Raras (no foil, no ⭐) | 250 FRJ | 1 carta Épica aleatoria + 10 fragmentos |
| **Fundir Épica** | 5 cartas idénticas Épicas (no foil, no ⭐) | 1,500 FRJ | 1 carta Legendaria aleatoria + 10 fragmentos |

- Las cartas **Legendarias y Míticas no se pueden fundir** — una vez que llegan a ese nivel, se quedan.
- Cada fundición genera **10 fragmentos** (común, raro, épico, o legendario según corresponda). Los fragmentos se usan para forjar cartas específicas.
- Las cartas foil y Primera Edición **no se pueden usar como material de fundición**. Están protegidas. Si intentas fundir una foil, el sistema te dice "¿estás loco?" (bueno, no literalmente, pero casi).

### 6. Cápsulas VIP

Si tienes membresía VIP, recibes cápsulas mensuales gratuitas que pueden contener cartas, incluyendo rarezas altas. Es una de las ventajas más valoradas del club VIP.

---

## Tableros: De las Cartas al Juego

Las cartas no son solo para coleccionar — son la materia prima para construir **tablas de Lotería**. Una tabla es un grid de 4x4 (16 cartas) que usas para jugar.

- Cada tabla se registra on-chain como un token único (ERC-721 TablasLoteria).
- Las cartas que pones en tu tabla no se consumen — simplemente se "asignan" a esa tabla. Puedes reutilizarlas en otras tablas.
- El bono foil (+5% FRJ por carta foil en la tabla) aplica durante la partida.
- Diferentes combinaciones de cartas pueden desbloquear logros ocultos.

Ver [[10-tablas]] para el sistema completo de construcción de tableros.

---

## Colección: Las 54 Cartas

La colección completa son 54 cartas. Aquí va la lista para que lleves tu checklist mental:

**Clásicas imprescindibles**: El Gallo, El Diablito, La Dama, El Catrín, El Paraguas, La Sirena, La Escalera, La Botella, El Barril, El Árbol, El Melón, El Valiente, El Gorrito, La Muerte, La Pera, La Bandera, El Bandolón, El Violoncello, La Garza, El Pájaro, La Mano, La Bota, La Luna, El Cotorro, El Borracho, El Negrito, El Corazón, La Sandía, El Tambor, El Camarón, Las Jaras, El Músico, La Araña, El Soldado, La Estrella, El Cazo, El Mundo, El Apache, El Nopal, El Alacrán, La Rosa, La Calavera, La Campana, El Cantarito, El Venado, El Sol, La Corona, La Chalupa, El Pino, El Pescado, La Palma, La Maceta, El Arpa, La Rana.

---

## Tips de Coleccionista

- **Usa los filtros del inventario**: Filtra por rareza, por foil, por "no tengo". El inventario te dice exactamente cuántas te faltan para completar la colección base.
- **No fundas foil ni ⭐**: Nunca. Jamás. Aunque tengas 20 duplicadas foil de El Gallo (cosa que no va a pasar), valen más en el mercado que convertidas en una Rara aleatoria.
- **Mercado P2P para completar**: Cuando te falten 2 o 3 cartas para terminar la colección, el mercado P2P es más eficiente que seguir abriendo sobres y rezar.
- **Sobres temáticos para cazar**: Si buscas una carta específica, el sobre temático reduce el pool de 54 a 18, triplicando tus probabilidades.
- **Activa notificaciones de foil**: Los sobres foil vuelan. Configura alertas para no quedarte fuera.
- **La paciencia paga**: Una colección completa de foil no se construye en una semana. Disfruta el viaje, celebra cada foil que cae, y presume tus hallazgos en la comunidad.

---

*Abrir un sobre es un ritual. El momento entre que haces clic y las cartas se revelan — ese segundo de suspense donde todo es posible. Donde puede salir una Mítica foil de El Corazón. Ese segundo es Axolotto.*

---



### 10-tablas
> `conceptos/10-tablas.md`

---
tags: [conceptos, gameplay, tablas]
description: "Tableros 4×4 — creación, tipos, staking, renta y estrategia | 4×4 Boards — creation, types, staking, rental and strategy"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Tablas — Tus Tableros de Juego

## ¿Qué es una Tabla?

La **tabla** es tu herramienta principal de juego en Axolotto. Es una cuadrícula de **4×4** que contiene exactamente **16 cartas** de tu colección personal. Cada tabla es un **NFT ERC-721 único** — te pertenece, puedes venderla, rentarla, mejorarla y presumirla.

Sin tabla no hay juego. Necesitas **al menos 1 tabla** para sentarte a jugar cuando el Gritón empiece a cantar.

La **posición de cada carta IMPORTA**. No es lo mismo tener El Corazón en la esquina que en el centro. Algunos patrones ganadores — como las esquinas, las cruces o los cuadritos 2×2 — requieren posiciones específicas en la cuadrícula. Construir bien tu tabla es la diferencia entre gritar ¡Lotería! o ver cómo otro se lleva el premio.

> Piensa en tu tabla como un escuadrón de 16 soldados. La formación decide la batalla.

---

## Crear una Tabla

Puedes crear tablas desde la **Sala** en la sección "Mis Tablas". Hay dos métodos:

### Aleatorio — 25 FRJ
El sistema selecciona 16 cartas al azar de tu colección y las coloca automáticamente. Es rápido, barato y a veces el caos funciona. Ideal cuando:
- Estás empezando y no tienes muchas cartas para elegir
- Quieres probar suerte sin invertir mucho
- Necesitas una tabla extra rápido para staking o renta

### Diseño Manual — 50 FRJ
El **Editor de Tablas** te da control total. Arrastras y sueltas cada carta en la casilla exacta que quieres. Ves el tablero completo mientras construyes. Este método es **estratégicamente superior** porque te permite:
- Colocar tus mejores cartas en posiciones que formen múltiples patrones
- Distribuir rarezas para cubrir filas, columnas y diagonales
- Evitar puntos ciegos — zonas sin cobertura de patrones
- Crear tablas especializadas (anti-Rookies, anti-Champions, balanceadas)

Consejo de veterano: **siempre diseña manualmente tus tablas competitivas**. Los 25 FRJ extra se pagan solos con tu primera victoria.

---

## Tipos de Tabla — Tiers

No todas las tablas son iguales. El **tipo** determina propiedades base y en qué tipo de partidas puedes usarla:

| Tipo | Costo de partida | Descripción |
|---|---|---|
| **Clásica** | 10 AXF | La tabla básica. Perfecta para aprender y farmear FRJ en partidas fáciles. Tu primera tabla siempre será Clásica. |
| **Suerte** | 50 AXF | Mayor multiplicador de recompensas. Para jugadores que confían en su estrategia y quieren ganancias serias. |
| **Plasma** | 150 AXF | Tabla de alto riesgo. Premios enormes pero partidas más difíciles. Solo para expertos con bankroll sólido. |
| **Cósmica** | 200 AXF | El tier definitivo. Los mejores multiplicadores del juego. Partidas contra los oponentes más duros. Si ganas con una Cósmica, el Gritón recordará tu nombre. |

Cada tabla mantiene su tipo de por vida. No puedes "subir de tier" una Clásica a Suerte — pero puedes tener múltiples tablas de diferentes tiers y elegir cuál usar según la ocasión.

---

## Espacios para Tablas (Slots)

Empiezas con **3 espacios** gratuitos. Cada espacio = 1 tabla que puedes tener activa simultáneamente:

| Slot | Cómo desbloquearlo |
|---|---|
| Slots 1–3 | **Gratis** — disponibles desde el inicio |
| Slot 4 | **VIP Dorado** (+1 slot, 4 total) |
| Slot 5 | **VIP Axolite** (+2 slots, 5 total) |
| Slot 4+ | Compra con FRJ (ver tabla abajo) |

### Compra de slots adicionales con FRJ

| Slot # | Costo en FRJ |
|---|---|
| Slot 4 | 500 FRJ |
| Slot 5 | 1,000 FRJ |
| Slot 6 | 2,500 FRJ |
| Slot 7 | 5,000 FRJ |
| Slot 8 | 10,000 FRJ |
| Slot 9 (máx.) | 15,000 FRJ |

El máximo absoluto es **9 slots** (3 base + 2 VIP Axolite + 4 comprados). Con 9 tablas activas, tu potencial de staking y renta se dispara.

---

## Estadísticas de la Tabla

Cada tabla acumula estadísticas que reflejan su historial y rendimiento. Son tu carta de presentación ante compradores y rentadores:

### Nivel (Level)
Tu tabla gana **XP** en cada partida que juegas con ella. La fórmula es la misma que para los axolotitos: `nivel × 100 XP` para subir al siguiente nivel. Una tabla nivel 5 necesitará 500 XP para llegar a nivel 6.

Subir de nivel **mejora las tasas de staking** (generas más FRJ pasivo) y **aumenta el valor P2P** de la tabla.

### CSR — Coeficiente de Suerte y Rendimiento (Win Rate)
Una puntuación de **0 a 100** que mide qué tan bien rinde tu tabla. Se calcula combinando:
- Tu porcentaje de victorias con esta tabla
- La dificultad de los oponentes que has vencido
- El tier de la tabla (ganar con una Clásica contra Champions pesa más)

Un CSR 80+ es excelente. Un CSR 95+ es de otro mundo. Las tablas con CSR alto se rentan y venden por mucho más.

### Etiqueta de Suerte
Dos etiquetas divertidas que el sistema asigna automáticamente:
- **Tabla más suertuda**: la tabla con mejor racha de victorias (mayor porcentaje en los últimos 20 juegos)
- **Tabla más salada**: la tabla con peor racha — todos tenemos una

Estas etiquetas son solo sabor, pero los compradores sí las miran.

### Récord de por vida
- **Partidas Totales**: cuántas veces has jugado con esta tabla
- **Victorias Totales**: cuántas veces has gritado ¡Lotería! con ella
- **Racha actual**: victorias consecutivas (o derrotas consecutivas)

---

## XP por Partida — Cuánto Ganas

La XP que recibe tu tabla depende del tipo de partida y el resultado:

### Partidas CPU

| Resultado | Rookies (10 AXF) | Champions (50 AXF) |
|---|---|---|
| **Victoria** | 25 XP | 60 XP |
| **Derrota** | 8 XP | 15 XP |

Incluso perdiendo aprendes algo. Tus tablas siempre progresan, aunque más lento.

### Partidas Multijugador

| Premio | XP extra |
|---|---|
| **Premio 1** (ganador principal) | +15 XP |
| **Premio 2** (segundo lugar) | +45 XP |

### Multiplicador 10×
Cuando activas el multiplicador **10×**, la XP base se multiplica por **√10 ≈ 3.16×**. No es 10× directo para mantener el progreso balanceado, pero sigue siendo una aceleración notable.

---

## Staking — Ingreso Pasivo con tus Tablas

Tus tablas **generan FRJ automáticamente** mientras no las estás usando para jugar. Es el sistema de staking pasivo de Axolotto: tus tablas "trabajan" para ti.

### ¿Cuánto genera cada tabla?

La tasa de generación depende de dos factores:
1. **Rareza de las cartas** en la tabla — cartas más raras = más FRJ/hora
2. **Nivel de la tabla** — a mayor nivel, mejor tasa base

### Regla Play-to-Stake
Para mantener el staking activo debes jugar **al menos 1 partida cada 24 horas**. Si pasas 24 horas sin jugar, tus tablas dejan de generar FRJ hasta que vuelvas a jugar. Esta regla existe para que el staking sea una recompensa por participación activa, no un ingreso gratuito eterno.

### Tope de acumulación — 24 horas
Tus tablas acumulan FRJ por un máximo de **24 horas**. Si no reclamas antes de ese límite, dejas de acumular. **Reclama tus FRJ regularmente** — ponte una alarma si eres olvidadizo.

### Cartas Foil — Bonus de rendimiento
Cada **carta foil** (variante holográfica brillante) en tu tabla añade un **+5% de rendimiento** al staking. Con 16 cartas foil, puedes llegar a un **+80%** de bonus. Las cartas foil son raras pero transforman tu tabla en una máquina de generar FRJ.

> Estrategia: si tienes una tabla solo para staking, llénala con tus cartas foil de mayor rareza. No importa tanto la posición — solo la rareza y el foil.

---

## Renta de Tablas (Scholarship)

¿Tienes una tabla poderosa que no usas todo el tiempo? **Réntala**. ¿No tienes una tabla competitiva pero quieres jugar en tiers altos? **Renta una**.

### Como Dueño (Arrendador)
1. Pones tu tabla en alquiler desde "Mis Tablas"
2. Fijas un **precio en FRJ por 24 horas** de renta
3. Defines el **porcentaje de ganancias** que te llevas cuando el rentador gane (owner share)
4. Recibes FRJ **sin riesgo** — te pagan aunque el rentador pierda todas sus partidas
5. La tabla sigue siendo tuya. El rentador solo la usa, no la modifica

### Como Rentador (Scholar)
- **Prueba antes de comprar**: renta una tabla para ver si te gusta antes de invertir en construir una similar
- **Juega en tiers altos**: renta una Cósmica o Plasma aunque no tengas cartas para construir una propia
- **Aprende de los mejores**: estudia cómo los top players posicionan sus cartas
- Puedes rentar tablas directamente desde el **Ranking** — las mejores tablas suelen estar disponibles para alquiler

> El sistema de scholarships hace que Axolotto sea accesible para todos. No necesitas ser ballena para jugar en Cósmica — solo necesitas un buen dueño que confíe en ti.

---

## Venta P2P de Tablas

Puedes vender tablas completas en el **Mercado P2P** (Tianguis). La venta incluye:
- La tabla como NFT ERC-721 (si ambas partes tienen billetera vinculada)
- Las 16 cartas que contiene
- Todo su historial: nivel, CSR, récord, etiquetas de suerte

### Comisión del mercado
| VIP Tier | Comisión |
|---|---|
| Sin VIP | 5% |
| VIP Dorado | 4% |
| VIP Axolite | 3% |
| VIP Leyenda | 1.5% |

Una tabla nivel 20 con CSR 90+ y racha ganadora puede valer miles de FRJ. Construir una buena tabla es una inversión que se recupera con creces.

---

## Desmantelar una Tabla

A veces necesitas empezar de cero. Tienes dos opciones:

### Desmantelamiento Básico — 50 FRJ
Destruye la tabla. **1 carta aleatoria se pierde para siempre**. Las otras **15 cartas regresan a tu inventario**. Es un riesgo: asegúrate de no tener una carta irremplazable en esa tabla antes de desmantelar.

### Pegamento Solvente — 120 FRJ
Un consumible especial que disuelve la tabla sin dañar las cartas. **Las 16 cartas regresan intactas** a tu inventario. Vale cada FRJ si tienes cartas foil, legendarias o de alto nivel sentimental.

> Regla de oro: si tu tabla tiene aunque sea 1 carta foil o legendaria, usa Pegamento Solvente. Los 120 FRJ son nada comparado con perder una carta que vale 10,000+ FRJ.

---

## Estrategia — Construir Tablas Como un Pro

### Regla #1: Cobertura de patrones
El objetivo no es solo tener 16 cartas poderosas. Es **cubrir la mayor cantidad de patrones ganadores posible**. Cada posición en la cuadrícula 4×4 pertenece a múltiples patrones:
- **4 filas** (horizontal)
- **4 columnas** (vertical)
- **2 diagonales** (principal y secundaria)
- **4 esquinas** (las 4 posiciones de cada esquina)
- **9 cuadritos** (bloques 2×2)
- **1 cuadrado central** (las 4 casillas del centro)

Cada carta que colocas está participando en 2–4 patrones simultáneamente. Una carta mal colocada es una oportunidad perdida.

### Regla #2: Distribuye tus rarezas
- **Legendarias y Épicas** en posiciones de alto tráfico (centro, esquinas, diagonal principal)
- **Raras** en filas y columnas para asegurar cobertura de línea
- **Comunes** en posiciones que solo participan en 1–2 patrones

No amontones tus mejores cartas en una sola fila. Si esa fila no sale, perdiste.

### Regla #3: Especialízate por modo de juego

**Para Rookies (partidas fáciles):**
- Prioriza cobertura de **líneas** (filas y columnas) — los patrones más comunes
- No necesitas cobertura perfecta de cuadritos; los Rookies rara vez completan patrones complejos
- Una tabla balanceada con 2–3 cartas raras por línea es suficiente

**Para Champions (partidas difíciles):**
- Necesitas cobertura de **cuadritos 2×2** y **esquinas** además de líneas
- Los oponentes Champions también buscan patrones complejos — compites por los mismos
- Invierte en cartas foil y legendarias para estas tablas
- Una tabla especializada en cuadritos puede ser devastadora en Champions

### Regla #4: Tabla de staking vs Tabla de juego
Mantén al menos **dos tablas con propósitos distintos**:
- **Tabla de juego**: optimizada para ganar partidas (posiciones estratégicas, cartas versátiles)
- **Tabla de staking**: optimizada para generar FRJ (máxima rareza, máximo foil, el nivel y posición no importan tanto)

### Regla #5: El CSR es tu currículum
Cada victoria mejora tu CSR. Cada derrota lo baja. Un CSR alto hace que:
- Tu tabla se rente más rápido y por más FRJ
- El precio de venta P2P se dispare
- Otros jugadores te reconozcan en el Ranking

Cuida tu CSR. Si estás en mala racha, cambia a otra tabla para no dañar el récord de tu tabla principal.

---



### 11-webitos-y-crianza
> `conceptos/11-webitos-y-crianza.md`

---
tags: [conceptos, crianza, webitos]
description: "Webitos y crianza de Axolotitos — huevos, incubación, imprinting y eclosión | Webitos and Axolotito breeding — eggs, incubation, imprinting and hatching"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Webitos y Crianza de Axolotitos

## ¿Qué es un Webito?

Un **Webito** es un huevo — un NFT ERC-721 — que contiene la esencia de un futuro Axolotito. No es un simple ítem de inventario: es vida en estado latente, esperando las condiciones adecuadas para despertar.

El ciclo de vida completo es:

1. **Comprar** un huevo en la tienda o recibirlo como recompensa
2. **Colocarlo** en un Nido — uno de los 7 espacios disponibles en tu Cueva del Cenote
3. **Incubar** durante 7 días, manteniendo el calor necesario
4. **Improntar (Apadrinar)** — la fase más importante: un Axolotito adulto guía al huevo a través de partidas de Lotería, moldeando su ADN con cada victoria y cada derrota
5. **Eclosionar** — el huevo se rompe y nace tu nuevo Axolotito
6. **Dar la bienvenida** a un nuevo compañero con estadísticas, naturaleza y rasgos visuales únicos

Cada paso del proceso deja una huella en el ADN del Axolotito. Dos huevos del mismo tipo pueden producir criaturas completamente diferentes según cómo fueron incubados y quién los apadrinó.

## Tipos de Huevo

No todos los huevos son iguales. Existen distintas generaciones y rarezas, cada una con su precio, disponibilidad y características.

### Huevos por Fase

| Huevo | Precio AXF | Suministro | Notas |
|-------|-----------|------------|-------|
| **Fase 1 (Genesis)** | 400 AXF | 420 unidades | Primera generación. Los Axolotitos nacidos de estos huevos llevan un aura dorada que los distingue para siempre. Son los más escasos. |
| **Fase 2 (Expansión)** | 800 AXF | 1,260 unidades | Suministro medio. Buenos stats base, mayor disponibilidad que Genesis. |
| **Fase 3 (Retail)** | 1,200 AXF | 2,520 unidades | Edición estándar. La puerta de entrada más común para nuevos jugadores. |

### Huevo Astral

| Huevo | Precio AXF | Suministro | Notas |
|-------|-----------|------------|-------|
| **Astral** | 3,000 AXF | 100 / año | Premium garantizado. Stats base entre **45–85** (sin floor bajo). **80%** probabilidad de skin astral, **20%** de skin dorada. Un rasgo visual raro **garantizado**: halo celestial o boca divina. Si puedes ahorrar para uno, vale cada AXF. |

### Huevo Tutorial

Cada jugador nuevo recibe un **Webito gratuito** durante el tutorial. Este huevo está diseñado para ser balanceado: buenas estadísticas iniciales sin ser dominante, perfecto para aprender las mecánicas del juego. Es tu primer compañero, y siempre tendrá un lugar especial en tu colección.

## El Proceso de Incubación

Colocas el huevo en un Nido (tienes hasta 7 espacios en tu Cueva del Cenote — ver [[16-el-cenote-cueva]]) y comienza la cuenta regresiva: **7 días** de incubación base.

### El Sistema de Calor

El **Calor** es la moneda de progreso de la incubación. No es binario (incubando / no incubando): es un espectro.

- **Sano** (100% – 50%): El huevo está cálido y feliz. La incubación avanza normalmente.
- **Frío** (49% – 25%): El huevo empieza a tiritar. El progreso se ralentiza.
- **Helándose** (24% – 10%): Peligro. El progreso casi se detiene.
- **Congelado** (<10%): El huevo se **congela**. La incubación se **pausa por completo** hasta que recuperes el calor.

Si el calor llega a **0%**, el huevo entra en estado de congelación total. No perderás el huevo, pero el reloj de 7 días se detiene hasta que lo descongeles.

### El Clima Afecta el Calor

El ciclo día-noche del Cenote influye directamente en la retención de calor:

- **Amanecer**: pérdida de calor moderada — el sol apenas toca el agua
- **Mañana**: pérdida de calor baja — las aguas están tibias
- **Tarde**: pérdida de calor moderada-alta — el sol se va
- **Noche**: pérdida de calor alta — las aguas profundas se enfrían

Planifica tus acciones de mantenimiento según la hora del día.

### Acciones del Jugador

No eres un espectador pasivo. Tienes herramientas para proteger a tu huevo:

| Acción | Costo | Efecto |
|--------|-------|--------|
| **Calentar** | FRJ (variable) | Sube la temperatura del huevo. La cantidad de FRJ necesaria depende de qué tan frío esté. |
| **Poner Escudo** | 200 FRJ (Gotas Anticongelantes) | Protección temporal contra congelamiento. El escudo absorbe el daño por frío durante un período. |
| **Lámpara Infrarroja** | 200 AXF | Descongelamiento **instantáneo**. Saca al huevo del estado Congelado de inmediato. Uso de emergencia. |

### Estrategia de Incubación

- Revisa tus huevos al menos **2 veces al día** (mañana y noche) para mantener el calor en zona Sano
- Si sabes que no podrás conectarte por varias horas, **pon un escudo** antes de irte
- Guarda una **Lámpara Infrarroja** en tu inventario para emergencias — un huevo congelado a las 3 AM no debería arruinarte la noche
- Los huevos en slots de cueva con mejoras de aislamiento pierden calor más lento

## Apadrinamiento (Imprinting) — La Mecánica Clave

Aquí es donde la magia realmente ocurre. El imprinting es lo que convierte a un huevo genérico en **tu** Axolotito único.

### ADN Incompleto

Cuando compras un Webito, su ADN está **incompleto**. Las estadísticas iniciales son de rango medio, sin afinar. El huevo tiene potencial, pero necesita ser moldeado. Aquí entra el **Padrino**.

### ¿Qué es un Padrino?

Un **Padrino** (godparent) es un Axolotito adulto de tu colección que acepta guiar al huevo. El Padrino lleva al huevo a través de partidas de Lotería, y cada partida — cada victoria, cada derrota, cada jugada precisa — deja una marca en el ADN del huevo.

### Requisitos del Padrino

No cualquier Axolotito puede ser Padrino. Debe cumplir:

- **No estar congelado** por penalización VIP
- **No estar dormido** (debe tener energía disponible)
- **Menos de 3 ahijados previos** en su vida (máximo 3 mentorías por Axolotito)
- **No estar apadrinando** otro Webito activo en este momento

Elige con cuidado. Un Padrino solo puede mentorizar **3 veces en toda su vida**.

### Partidas de Imprinting

El Padrino y el huevo juegan juntos. El número de partidas depende de la rareza del huevo:

| Rareza del Huevo | Partidas Requeridas |
|------------------|---------------------|
| **Común** | 3 partidas |
| **Raro** | 5 partidas |
| **Épico** | 7 partidas |
| **Legendario** | 7 partidas |

Cada partida puede jugarse contra CPU o contra otros jugadores. Durante el imprinting, **jugar contra CPU Rookies** es una estrategia intencional — quieres victorias limpias para maximizar las estadísticas del huevo.

### Cómo las Partidas Moldean las Estadísticas

Después de cada partida, las estadísticas del huevo se modifican según el desempeño:

| Evento de Partida | Efecto en el Huevo |
|-------------------|---------------------|
| **Victoria** | +8 a +15 Suerte |
| **Jackpot** (ganar con carta especial) | +20 Suerte |
| **Derrota** | -8 a -12 Suerte |
| **Precisión >= 80%** | +10 a +18 Concentración |
| **Precisión <= 50%** | -8 a -14 Concentración |
| **Partida 3+** (el huevo ya calentó) | +10 a +15 Aguante |
| **Partida 1** (primera partida) | -5 Aguante (¡el huevo necesita calentar!) |
| **Padrino SAL < 20** (baja salinidad) | -6 a -10 Salinidad (BUENO — menor es mejor) |
| **Padrino SAL > 50** (alta salinidad) | +8 a +12 Salinidad (MALO — sube la sal) |

### Estadísticas Iniciales desde el Padrino

Antes de comenzar las partidas, el huevo recibe una semilla inicial de las estadísticas de su Padrino:

- **10% – 15%** de cada stat del Padrino se transfiere como base
- **15%** si el Padrino es nivel 20 o superior
- **10%** si el Padrino es nivel 1–19

Un Padrino de nivel alto con buenas estadísticas le da a tu huevo una ventaja significativa desde el principio.

### Sellado del ADN

Después de completar las N partidas requeridas, el ADN del huevo se **sella**. Ya no puede modificarse. Las estadísticas quedan fijas: son el reflejo de cada victoria, cada error, y cada momento de brillo que el Padrino y el huevo compartieron en el campo de Lotería.

El huevo está listo para eclosionar.

## Ceremonia de Eclosión

La eclosión no es un contador que llega a cero. Es una **ceremonia** — una secuencia cinematográfica de 7 pasos que celebra el nacimiento de un nuevo Axolotito.

### La Secuencia

1. **Pantalla en oscuridad**. El huevo palpita con una luz interna que crece y se atenúa, como un latido.
2. **El cascarón se quiebra**. Una silueta brillante emerge — el Axolotito, todavía sin detalles, solo luz pura.
3. **El nombre aparece letra por letra**, con efecto de máquina de escribir. *Tac... tac... tac...*
4. **La Naturaleza se revela** con una fanfarria. ¿Será Audaz? ¿Serena? ¿Traviesa? El momento de descubrirlo.
5. **Las 4 estadísticas se muestran** como cartas de Lotería girando una por una, revelando sus valores finales.
6. **Frase de origen**: *"Aprendió jugando con [nombre del Padrino]. Ganó [N] de [M] partidas."* — un resumen poético del viaje.
7. **Botón "Conoce a [Nombre]"** — y el Axolotito aparece en tu colección, completo y único.

### Duración por Rareza

| Rareza | Duración | Efectos Especiales |
|--------|----------|---------------------|
| **Común** | ~12 segundos | Secuencia estándar, limpia y emotiva |
| **Raro** | ~18 segundos | Partículas de agua flotando durante la revelación de estadísticas |
| **Legendario** | ~25 segundos | **Pantalla completa**. Confeti dorado. La fanfarria es más intensa. Las cartas de estadísticas tienen brillo dorado. |

Cada eclosión es un momento que recordarás. La primera vez que ves nacer a un Axolotito Legendario... no hay nada igual.

## Recompensas para el Padrino

Ser Padrino no es solo un honor — tiene recompensas tangibles:

- **+150 XP** para el Padrino (una inyección significativa de experiencia)
- **+2.0 puntos permanentes** en la estadística que tuvo el mayor delta positivo durante el imprinting (la estadística que más mejoró en el huevo)
- **mentorship_count** del Padrino aumenta en 1 (máximo 3 de por vida)
- El Padrino es celebrado con una insignia visual temporal y una animación especial

Ser Padrino deja una huella permanente. Un Axolotito que ha guiado a 3 huevos es una leyenda viviente.

## Post-Eclosión: Cómo Mejoran las Estadísticas

Una vez que el Axolotito ha nacido, sus estadísticas no son estáticas. Pueden mejorar por varias vías:

| Método | Tipo | Efecto |
|--------|------|--------|
| **Equipamiento** (accesorios) | Permanente mientras se lleva equipado | Bonificaciones a stats específicos según el ítem |
| **Objetos especiales** (Polvo de Suerte, etc.) | Temporal | Boost durante un número limitado de partidas o tiempo |
| **Subir de nivel** (XP) | Permanente | Mejora de stats base al alcanzar nuevos niveles |

### Pureza Genética

La **Pureza Genética** es una medida de la calidad general de las estadísticas de un Axolotito. Se calcula como porcentaje relativo al máximo teórico de su rareza.

Si la pureza genética alcanza **>= 110%** (rango Mítico), hay una probabilidad del **25%** de que el Axolotito manifieste un **rasgo visual raro**:

- **Branquias de Fénix** — branquias que brillan con tonos fuego y se regeneran visualmente
- **Cola de Plasma** — cola con efecto de energía pulsante
- **Halo en la Frente** — un anillo de luz flotando sobre la cabeza
- **Boca Divina** — patrón de boca con brillo celestial
- **Extremidades de Coral** — patas y brazos con textura y colores de coral vivo

Estos rasgos son puramente visuales (no afectan gameplay) pero son extremadamente raros y codiciados por coleccionistas.

## Consejos para una Buena Crianza

### Elige bien a tu Padrino

- **Concentración y Suerte** son las estadísticas más importantes para transferir. Un Padrino con alta Concentración ayudará al huevo a tener mejor precisión en sus partidas de imprinting, creando un ciclo positivo.
- La **Salinidad baja** del Padrino es crucial — recuerda que SAL alta del Padrino **sube** la salinidad del huevo, y una SAL baja es mejor para el rendimiento en partidas.

### Juega inteligente durante el Imprinting

- **Juega contra CPU Rookies** durante las partidas de imprinting. Son más fáciles de vencer y cada victoria suma Suerte al huevo.
- **No juegues con el Padrino cansado**. Un Padrino con baja energía rinde peor. Revisa su energía antes de comenzar una sesión de imprinting.
- **La primera partida** siempre penaliza el Aguante del huevo (-5). No te alarmes — es normal. El huevo necesita "calentar motores". De la partida 3 en adelante, el Aguante se recupera y mejora.

### Planifica a largo plazo

- **El Webito Astral vale la pena**. 3,000 AXF no es barato, pero el floor de stats en 45, el rasgo visual raro garantizado, y las skins premium lo convierten en la mejor inversión a largo plazo.
- **Los Padrinos solo pueden mentorizar 3 veces**. No desperdicies una mentoría en un huevo común si tienes un Padrino excepcional. Reserva sus slots para huevos Épicos o Astrales.
- **Los huevos Genesis** (Fase 1, 400 AXF) son limitados a 420 unidades. Una vez que se agoten, no habrá más. Si puedes conseguir uno, hazlo.

### Mantenimiento de incubación

- **Dos revisiones al día**: una en la mañana (cuando la pérdida de calor es baja) y una en la noche (antes del período de mayor frío).
- **Escudo antes de dormir**: si no podrás revisar el huevo por 8+ horas, gasta los 200 FRJ en Gotas Anticongelantes. Es más barato que una Lámpara Infrarroja de emergencia.
- **Coordina con el clima**: si puedes, haz las acciones de Calentar durante la Mañana (menor costo de FRJ por el clima favorable).

---



### 12-economia-dual
> `conceptos/12-economia-dual.md`

---
tags: [conceptos, economia]
description: "AXF vs FRJ — las dos monedas de Axolotto explicadas para jugadores | AXF vs FRJ — Axolotto's two currencies explained for players"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Economía Dual — AXF y FRJ

Axolotto usa **dos monedas** con propósitos muy diferentes. Entender la diferencia entre ellas es lo primero que debe saber cualquier jugador nuevo. Aquí va todo, sin fórmulas ni tecnicismos.

---

## Las Dos Monedas de un Vistazo

| Característica | AXF (Axofichas) | FRJ (Frijolitos) |
|---|---|---|
| Tipo | Moneda premium (dinero real) | Moneda de juego (ganada jugando) |
| ¿Es crypto? | Sí — token ERC-20 en Plasma Chain | No — solo existe en la base de datos del juego |
| ¿Cómo se consigue? | Comprando con dinero real | Jugando, staking, premios, VIP, mercado P2P |
| ¿Se puede retirar? | Sí (vía DevEx, condiciones abajo) | No (por diseño — protege la economía) |
| ¿Se usa en multijugador? | **Prohibido** (el código lo rechaza) | **Única moneda permitida** |
| Valor de referencia | 1 AXF ≈ $2 MXN (~$0.10 USD) | Sin valor en dinero real |

---

## AXF (Axofichas) — La Moneda Premium

Las Axofichas son el token **on-chain** de Axolotto. Viven en la blockchain de Plasma (chain ID 9746) como un token ERC-20 real. Eso significa que tú eres dueño de tus AXF: están en tu wallet, no en una base de datos del juego.

### Cómo Conseguir AXF

**Solo se compran con dinero real.** No hay forma de ganar AXF jugando — por diseño. Esto protege el valor del token y cumple con las regulaciones.

**Paquetes de compra:**

| Paquete | AXF recibidos | Precio (MXN) | Precio por AXF |
|---|---|---|---|
| Chico | 200 AXF | $35 MXN | ~$0.18 MXN c/u |
| Mediano | 550 AXF | $88 MXN | ~$0.16 MXN c/u |
| Grande | 1,725 AXF | $263 MXN | ~$0.15 MXN c/u |
| Ballena | 7,250 AXF | $875 MXN | ~$0.12 MXN c/u |

**Métodos de pago:**
- Tarjeta de crédito/débito (vía MoonPay o Mercado Pago)
- Transferencia bancaria SPEI
- Pago en efectivo OXXO
- USDT o USDC (5-10% de descuento por usar stablecoins)
- ETH o MATIC

### ¿Para Qué Sirve AXF?

- **Webitos (huevos)** — comprar huevos para incubar nuevos Axolotitos
- **Sobrecitos premium** — boosters con cartas raras y consumibles
- **Suscripción VIP** — membresía Coral, Dorado o Axolite (pago mensual en AXF)
- **Desbloquear slots de tablero** — más ranuras para crear y stakear tablas
- **Acelerar expansión de cueva** — saltar tiempos de espera en excavación
- **Comprar en el Mercado P2P** — adquirir cartas, tablas y Axolotitos de otros jugadores

### El Modelo de Reserva 80/20

Por cada AXF vendido, el sistema separa automáticamente:

- **80% a la reserva de respaldo** — intocable, garantiza que siempre haya liquidez para DevEx
- **20% a la tesorería operativa** — gastos del proyecto, desarrollo, servidores

Después de impuestos y comisiones de pasarela de pago, el neto real que entra al proyecto es de aproximadamente **$8.17 MXN** por cada $10 MXN en AXF vendidos. Esto asegura que Axolotto sea sostenible a largo plazo sin depender de nuevos jugadores pagando a los antiguos (no es un esquema Ponzi).

### DevEx — Cómo Retirar Dinero Real

El programa **DevEx** (Developer Exchange, heredado del ecosistema Roblox) permite convertir tu progreso en el juego en dinero real. Así funciona la ruta completa:

1. **Juega y gana FRJ** participando en partidas, staking, VIP, mercado P2P
2. **Compra o crea activos valiosos** — cartas raras, tablas con buen staking, Axolotitos con stats altos
3. **Vende esos activos en el Mercado P2P** — recibe AXF como pago de otros jugadores
4. **Solicita DevEx** desde tu panel de usuario — los AXF que recibiste por ventas P2P se convierten en dinero real
5. **Recibe tu pago** en pesos mexicanos (transferencia SPEI) o USDT (red Polygon)

**Condiciones del DevEx:**
- Periodo de espera de **14 días** desde la compra del AXF (anti-lavado)
- Verificación de identidad (**KYC**) obligatoria
- Tasa de recompra: aproximadamente **70%** del valor nominal del AXF
- **Solo aplica para AXF recibidos por ventas P2P** — los AXF comprados directamente no califican para DevEx (debes hacerlos circular en la economía primero)

> **Importante:** El DevEx no es un "cajero automático". Está diseñado para jugadores que crean valor real en el ecosistema (cartas raras, Axolotitos bien criados, tablas optimizadas). No es una forma de comprar AXF y retirar inmediatamente.

---

## FRJ (Frijolitos) — La Moneda de Juego

Los Frijolitos son la moneda con la que realmente **juegas**. No son crypto — existen solo en la base de datos del juego. No tienen valor en dinero real y **no se pueden retirar** por diseño. Esto es lo que permite que Axolotto opere como un concurso de habilidad y no como un casino.

### Cómo Conseguir FRJ (Gratis)

Hay muchas formas de ganar Frijolitos sin gastar un solo peso:

#### 1. Ganar Partidas (Modo CPU)

| Dificultad | Entrada | Premio por victoria |
|---|---|---|
| Rookies (principiante) | 25 FRJ | 85 FRJ (ganancia neta: +60) |
| Champions (experto) | 100 FRJ | 400 FRJ (ganancia neta: +300) |

Juega contra la CPU, gana consistentemente y acumula FRJ. El win rate promedio de jugadores activos ronda el 30% — la casa tiene ventaja matemática, como en cualquier juego de azar con habilidad.

#### 2. Premios Multijugador

En las salas multijugador los premios salen del pozo total recolectado por las entradas de todos los jugadores:

- **Premio 1 (primer Lotería):** 35% del pozo total, repartido entre los ganadores
- **Premio 2 (Tabla Llena):** 55% del pozo total, repartido entre quienes completen la tabla
- **Jackpot:** 90% del bote global acumulado (ver [[22-jackpot]] para condiciones)

El 10% restante del pozo se divide entre la tesorería del juego (5%) y el bote del jackpot (5%).

#### 3. Recompensas Diarias — Ciclo Lunar

Cada día que entras al juego recibes FRJ gratis. La cantidad crece durante la semana:

| Día de la semana | FRJ diario |
|---|---|
| Días 1-2 | 50 FRJ |
| Días 3-4 | 80 FRJ |
| Días 5-6 | 130 FRJ |
| Día 7 | Bonus especial (cápsula gratis + FRJ extra) |

La racha se reinicia cada lunes (ciclo lunar semanal). Ver [[21-ciclo-lunar-y-recompensas]].

#### 4. Staking — Ingresos Pasivos

Puedes "stakear" tus tableros y Axolotitos para generar FRJ por hora, incluso cuando no estás jugando. Las cartas más raras en tu tablero producen más FRJ por hora:

| Rareza de carta | FRJ por hora (por carta) |
|---|---|
| Común | 0.05 |
| Rara | 0.15 |
| Épica | 0.40 |
| Legendaria | 1.00 |

Un tablero completo de 16 cartas Legendarias nivel 10 genera hasta **35.20 FRJ por hora** (844.80 FRJ al día). El staking requiere haber jugado al menos una partida en las últimas 24 horas. Ver [[20-staking-ingresos-pasivos]].

#### 5. Mercado P2P — Vender a Otros Jugadores

Vende cartas duplicadas, tableros que ya no uses, o Axolotitos criados por ti a otros jugadores. Tú pones el precio en FRJ. Ver [[19-mercado-p2p]].

#### 6. VIP Diario

Cada nivel de VIP incluye un reclamo diario de FRJ:

| Nivel VIP | FRJ diario |
|---|---|
| Coral | 40 FRJ |
| Dorado | 100 FRJ |
| Axolite | 200 FRJ |

Ver [[15-vip-club]].

#### 7. Modo Espectador

Puedes ver partidas multijugador sin jugar y ganar hasta **10 FRJ al día** completamente gratis. Ideal para aprender estrategias mientras generas algo de moneda.

### ¿Para Qué Sirve FRJ?

- **Entradas a partidas** — 25 FRJ (Rookies) o 100 FRJ (Champions)
- **Crear tableros** — 25 a 50 FRJ por tablero nuevo
- **Cápsulas Gashapon** — desde 1,500 hasta 22,500 FRJ por tirada
- **Consumibles:**
  - Alimento para Axolotito: 30 a 150 FRJ
  - Anti-congelante (Solvente): 200 FRJ
  - Gotas de energía: varios precios
- **Comprar en el Mercado P2P** — cartas, tablas, Axolotitos de otros jugadores
- **Expansión de cueva** — desde 500 FRJ (nivel básico) hasta 60,000 FRJ (niveles profundos)
- **Fundición de cartas (Card Melter)** — 100 a 1,500 FRJ por destruir duplicadas y recibir material

---

## Cambio de Moneda — El Banco de Algas

El **Banco de Algas** es la única forma de convertir AXF en FRJ. No existe la conversión inversa (FRJ → AXF) — eso requeriría pasar por el mercado P2P.

**Paquetes de conversión AXF → FRJ:**

| Paquete | Costo en AXF | FRJ recibidos | Bonus |
|---|---|---|---|
| Alga Común | 10 AXF | 100 FRJ | — |
| Alga Abundante | 50 AXF | 600 FRJ | +20% |
| Alga Imperial | 100 AXF | 1,500 FRJ | +50% |
| Súper Carga | 250 AXF | 4,000 FRJ | +60% |

Mientras más grande el paquete, mejor la tasa de conversión. El paquete Súper Carga te da 16 FRJ por AXF, comparado con solo 10 FRJ por AXF en el paquete básico.

**Recomendación para nuevos jugadores:** Si vas a comprar AXF para convertirlos a FRJ, el paquete Alga Imperial (100 AXF → 1,500 FRJ) es el mejor balance costo-beneficio para empezar.

---

## ¿Por Qué Dos Monedas?

Esta es la pregunta más importante. La respuesta corta: **cumplimiento legal.**

En muchos países (México incluido), los juegos donde apuestas dinero real para ganar dinero real se consideran casinos y requieren licencias especiales. Al separar las monedas:

1. **FRJ es la moneda de juego** — no tiene valor en dinero real, no se puede comprar ni retirar. Las partidas multijugador solo aceptan FRJ. Esto permite que Axolotto opere como un **concurso de habilidad** con premios virtuales, no como un juego de azar con apuestas.

2. **AXF es la moneda de coleccionables** — representa propiedad sobre activos digitales (NFTs). Su valor fluctúa en el mercado P2P según oferta y demanda de los objetos del juego, no según resultados de partidas.

3. **El código lo refuerza** — cualquier intento de usar AXF en una sala multijugador es rechazado con error **HTTP 402**. La restricción está programada a nivel del servidor y no se puede saltar.

4. **La ruta del dinero real es indirecta** — para retirar dinero debes: jugar bien → ganar FRJ → crear/obtener activos valiosos → venderlos en el mercado P2P → recibir AXF de otro jugador → solicitar DevEx. Esto toma tiempo, habilidad y esfuerzo. No es un casino disfrazado.

---

## Estrategia — ¿Cuál Moneda Me Conviene?

### Si eres Free-to-Play (F2P)

Tu mundo son los **Frijolitos.** No necesitas AXF para nada esencial:
- Juega partidas CPU para ganar FRJ
- Reclama tus recompensas diarias del Ciclo Lunar sin falta
- Stakea tus mejores tableros para ingreso pasivo
- Vende cartas duplicadas en el Mercado P2P
- Ahorra FRJ para cápsulas Gashapon y expansión de cueva
- Ver la guía completa: [[25-f2p-guia-gratis]]

### Si inviertes dinero real

Compra **AXF** y úsalo inteligentemente:
- **Mejor uso:** VIP mensual (beneficios pasivos que se acumulan) + Sobrecitos premium
- **Conversión eficiente:** Alga Imperial o Súper Carga para maximizar FRJ por AXF
- **Inversión a largo plazo:** Webitos para criar Axolotitos raros y venderlos en el mercado P2P
- **No recomendado:** Gastar AXF en aceleraciones pequeñas o consumibles básicos (desperdicias el valor premium)

### Si quieres retirar dinero (DevEx)

Esta es la ruta del jugador "profesional":
1. Domina el juego — consistencia en victorias
2. Cría Axolotitos con stats altos y naturalezas deseables
3. Construye tableros optimizados para staking
4. Vende tus activos en el Mercado P2P por AXF
5. Solicita DevEx cuando tengas un colchón de AXF de ventas P2P

---

## Nota Histórica

Los nombres de las monedas cambiaron en junio de 2026 para alinearse mejor con la identidad del juego:

- **AXG (Axogemas)** pasó a llamarse **AXF (Axofichas)**
- **GAL (Gemas Alga)** pasó a llamarse **FRJ (Frijolitos)**

Si ves "AXG" o "GAL" en alguna interfaz antigua, screenshot o video de YouTube, son exactamente lo mismo que AXF y FRJ — solo cambió el nombre. Los contratos en la blockchain conservan sus nombres originales (`Axogema.sol`, `GemaAlga.sol`) por inmutabilidad.

---



### 13-tienda-y-tianguis
> `conceptos/13-tienda-y-tianguis.md`

---
tags: [conceptos, economia, tienda]
description: "La Tienda oficial de Axolotto — sobres, webitos, consumibles y tablas | The official Axolotto Shop — boosters, eggs, consumables and boards"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# La Tienda — El Tianguis

## Resumen General

La Tienda oficial de Axolotto se llama **El Tianguis**, en honor a los mercados tradicionales mexicanos al aire libre. Tiene ese mismo ambiente vibrante y colorido: puestos llenos de mercancía, precios visibles en AXF y FRJ, y una sección donde puedes comprar casi todo lo que necesitas para jugar, criar, decorar y presumir tu colección.

El Tianguis tiene tres sub-pestañas:

| Pestaña | Descripción | Página detallada |
|---------|-------------|-------------------|
| **Tienda Oficial** | Sobres, webitos, consumibles y tablas vendidos directamente por el sistema | Esta página |
| **Forja (Card Melter)** | Funde cartas repetidas para fabricar cartas brillantes (foil) | [[18-forja-y-fundicion]] |
| **Mercado P2P** | Compra-venta entre jugadores (tablas, cartas, consumibles) | [[19-mercado-p2p]] |

Esta página cubre exclusivamente la **Tienda Oficial**. Las otras dos secciones tienen sus propias páginas de referencia.

---

## 1. Sobres (Boosters) — Paquetes de Cartas

Cada sobre contiene **7 cartas únicas** (sin repetidas dentro del mismo sobre). Hay 5 tipos de sobres, cada uno con una temática y un pool de cartas distinto.

### Tipos de Sobres

| Sobre | Tema | Pool de Cartas | AXF (Fase 1) | FRJ (Fase 1) |
|-------|------|----------------|-------------|-------------|
| **Puro (Pure)** | Mixto | Las 54 cartas del juego | 6 | 60 |
| **Fiesta** | Temática Fiesta | 18 cartas temáticas | 10 | 100 |
| **Nido** | Temática Nido | 18 cartas temáticas | 10 | 100 |
| **Cosmos** | Temática Cosmos | 18 cartas temáticas | 10 | 100 |
| **Brillante (Foil)** | Cartas foil/brillantes | 5 de 7 cartas son foil | 80 | 800 |

### Precios por Fase

Los precios de los sobres aumentan con cada fase económica del juego:

| Sobre | Fase 1 (Genesis) | Fase 2 (Expansión) | Fase 3 (Retail) |
|-------|-----------------|--------------------|--------------------|
| Puro | 6 AXF · 60 FRJ | 9 AXF · 90 FRJ | 12 AXF · 120 FRJ |
| Fiesta | 10 AXF · 100 FRJ | 15 AXF · 150 FRJ | 20 AXF · 200 FRJ |
| Nido | 10 AXF · 100 FRJ | 15 AXF · 150 FRJ | 20 AXF · 200 FRJ |
| Cosmos | 10 AXF · 100 FRJ | 15 AXF · 150 FRJ | 20 AXF · 200 FRJ |
| Brillante | 80 AXF · 800 FRJ | 120 AXF · 1,200 FRJ | 160 AXF · 1,600 FRJ |

- **Fase 2**: precios multiplicados por 1.5× respecto a Fase 1.
- **Fase 3**: precios multiplicados por 2× respecto a Fase 1.

### Reglas del Sobre Brillante (Foil)

- **Límite global**: máximo 100 unidades por mes en todo el sistema. Una vez agotado, no se puede comprar hasta el siguiente mes.
- **Contenido garantizado**: 5 de las 7 cartas del sobre son foil (brillantes). Las otras 2 son normales.

### Probabilidad de Brillo por Fase

Durante la **Fase 1 (First Edition)**, cada carta individual dentro de cualquier sobre tiene un **15% de probabilidad** de salir brillante (shiny). A partir de la **Fase 2 en adelante**, exactamente **1 carta por sobre** sale brillante (20% de probabilidad de que sea una segunda, pero el estándar es 1 por sobre).

---

## 2. Webitos (Huevos NFT)

Los Webitos son huevos NFT (ERC-721) que eclosionan en Axolotitos. Se compran exclusivamente con AXF (sin FRJ).

| Tipo de Webito | Precio AXF | FRJ | Suministro Total |
|----------------|-----------|-----|------------------|
| **Fase 1 (Genesis)** | 400 | — | 420 unidades |
| **Fase 2 (Expansión)** | 800 | — | 1,260 unidades |
| **Fase 3 (Retail)** | 1,200 | — | 2,520 unidades |
| **Astral** | 3,000 | — | 100 por año |

### Webito Astral

El Webito Astral es el huevo más exclusivo del juego. Sus garantías:

- **Stats garantizados**: mínimo 45 / máximo 85 en cada atributo (los webitos normales tienen rangos más amplios y menos predecibles).
- **Skin**: 80% de probabilidad de skin "astral", 20% de probabilidad de skin "gold" (dorada).
- **Visual raro garantizado**: halo o boca divina (dos de los traits visuales más codiciados).
- **Suministro**: solo 100 unidades por año calendario. Se renueva cada enero.

Para más detalles sobre crianza e incubación, ver [[11-webitos-y-crianza]].

---

## 3. Consumibles

Los consumibles son items de un solo uso que afectan a tus Axolotitos, huevos o tablas.

| Item | Precio | Moneda | Efecto |
|------|-------|--------|--------|
| **Alimento Común (Algae Pellet)** | 30 | FRJ | +15 de energía al Axolotito |
| **Alimento Premium (Brine Shrimp)** | 150 | FRJ | +60 de energía al Axolotito |
| **Gotas Anti-Escarcha (Anti-Frost Drops)** | 200 | FRJ | Previene que un webito se congele durante la incubación |
| **Lámpara Infrarroja Pro (Infrared Lamp Pro)** | 200 | AXF | Descongela instantáneamente un webito congelado |
| **Solvente de Pegamento (Glue Solvent)** | 120 | FRJ | Desarma una tabla recuperando las 16 cartas (sin perder ninguna) |

### Notas sobre Consumibles

- Las **Gotas Anti-Escarcha** se aplican antes de que el webito entre en estado de congelación. No revierten una congelación ya ocurrida — para eso necesitas la Lámpara Infrarroja.
- El **Solvente de Pegamento** es la única forma de desarmar una tabla sin perder las cartas. Si desarmas una tabla sin solvente, las cartas se pierden permanentemente.
- El **Alimento Común** es la opción más económica para mantener a tu Axolotito con energía. Ideal para el día a día.

---

## 4. Tablas (Boards)

Las tablas de lotería son el tablero 4×4 donde colocas tus cartas para jugar. Hay 4 tipos disponibles en la tienda:

| Tipo de Tabla | Precio AXF | Precio FRJ |
|---------------|-----------|------------|
| **Clásica** | 10 | 130 |
| **Suerte** | 50 | 520 |
| **Plasma** | 150 | 1,560 |
| **Cósmica** | 200 | 0 (solo AXF) |

Cada tipo de tabla tiene propiedades visuales y mecánicas distintas. Para el desglose completo de tipos de tabla, multiplicadores y reglas, ver [[10-tablas]].

---

## 5. Pases VIP

Los pases VIP se compran en la tienda y otorgan beneficios exclusivos durante 30 días.

| Nivel VIP | Precio | Duración |
|-----------|--------|----------|
| **Coral** | 400 AXF | 30 días |
| **Dorado** | 600 AXF | 30 días |
| **Axolite** | 1,800 AXF | 30 días |

Cada nivel desbloquea beneficios progresivamente mejores: descuentos en tienda, bonus de recompensas, slots de incubación extra, y acceso a salas exclusivas. Para el desglose completo de cada tier, ver [[15-vip-club]].

---

## 6. Cómo Comprar AXF (CryptoCheckout)

Si necesitas AXF y no tienes suficientes, la tienda integra el widget de **MoonPay** para comprar con dinero real (fiat).

### Métodos de Pago Disponibles

- Tarjeta de crédito/débito (MXN)
- Mercado Pago
- Transferencia SPEI
- Pago en efectivo OXXO

### Transferencia Crypto (con descuento)

Si pagas directamente con crypto, obtienes un descuento:

- **USDT / USDC**: 5–10% de descuento sobre el precio fiat
- **ETH / MATIC**: descuento variable según red

### Paquetes de AXF

| Paquete | Cantidad AXF |
|---------|-------------|
| **Small** | 200 AXF |
| **Medium** | 550 AXF |
| **Large** | 1,725 AXF |
| **Whale** | 7,250 AXF |

Para la tabla de precios completa en MXN y USD, ver [[12-economia-dual]].

---

## 7. Límites de Compra por Usuario

- **Sobres**: máximo 100 sobres por usuario (acumulado de todos los tipos). Una vez alcanzado el límite, no puedes comprar más sobres.
- **Webitos**: limitado por los slots de incubación disponibles en tu cueva. Si no tienes espacios vacíos, no puedes comprar más webitos. Ver [[11-webitos-y-crianza]].
- **Cualquier item** en el catálogo puede tener un campo `max_per_user` que impone un límite individual. Estos límites pueden cambiar entre fases.
- **Sobres Brillantes**: además del límite por usuario, existe el límite global de 100 unidades/mes. Si el límite global se alcanza, nadie puede comprar aunque tenga cupo personal disponible.

---

## 8. Consejos de Compra

Estos tips vienen de jugadores veteranos y están pensados para maximizar el valor de tus AXF y FRJ, especialmente cuando estás empezando:

1. **Mejor primera compra: Alimento Común (Algae Pellets)**. Mantener a tu Axolotito alimentado es barato (30 FRJ) y evita que se muera de hambre. Los FRJ se ganan gratis jugando, así que nunca deberías quedarte sin ellos.

2. **Mejor sobre calidad-precio: Puro (Pure)**. Es el más barato (6 AXF + 60 FRJ) y tiene acceso a las 54 cartas del juego. Los sobres temáticos solo valen la pena si estás buscando completar una colección específica.

3. **Ahorra AXF para VIP y Webitos**. Son las compras que más valor a largo plazo te dan. Un pase VIP se paga solo con los descuentos y bonus. Un webito puede salir con stats excepcionales que valen mucho más que su precio de compra.

4. **Nunca compres FRJ con AXF a menos que estés completamente seco y necesites jugar ya**. Los FRJ se ganan gratis en cada partida. Gastar AXF en FRJ es la conversión menos eficiente del juego.

5. **Guarda un Solvente de Pegamento en tu inventario**. Nunca sabes cuándo vas a querer reorganizar una tabla valiosa. Perder 16 cartas por no tener uno duele mucho más que los 120 FRJ que cuesta.

6. **El Alimento Premium (Brine Shrimp)** vale la pena durante eventos o sesiones largas de juego. Recupera 60 de energía de un golpe en vez de ir sumando de 15 en 15. Es 5× más eficiente por FRJ que el Alimento Común (2.5 FRJ por punto de energía vs 2.0 FRJ por punto).

---



### 14-capsulas-gashapon
> `conceptos/14-capsulas-gashapon.md`

---
tags: [conceptos, economia, gashapon]
description: "Cápsulas Gashapon — el sistema gacha de Axolotto con tiers, pity y probabilidades | Gashapon Capsules — Axolotto's gacha system with tiers, pity and probabilities"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Cápsulas Gashapon — La Suertuda

**La Suertuda** es el sistema gacha de Axolotto: una máquina de cápsulas donde gastas FRJ para girar y recibir premios aleatorios. Cada giro es una pequeña dosis de adrenalina — el sonido del mecanismo, la cápsula cayendo, la animación de revelado... y si te toca un legendario, ¡celebración a pantalla completa!

Es importante que entiendas bien cómo funciona: las probabilidades son transparentes, el sistema de "karma" está de tu lado, y hay opciones para todos los presupuestos. Pero recuerda: **nunca te gastes tus últimos FRJ en cápsulas** — guarda siempre para cuotas de entrada y comida para tus Axolotitos.

---

## ¿Qué es La Suertuda?

La Suertuda es la máquina de cápsulas del universo Axolotto. Piensa en ella como las máquinas gashapon japonesas: introduces tus fichas, giras la perilla, y recibes una cápsula con una sorpresa adentro. Nunca sabes exactamente qué te va a tocar, y esa incertidumbre es parte de la diversión.

Puedes ganar:
- **FRJ** — recuperas parte de lo invertido (o a veces más)
- **Cartas** — desde Común hasta Legendaria, incluyendo Cartas Raras
- **Accesorios** — para decorar a tus Axolotitos
- **Sobrecitos (Boosters)** — packs de contenido, a veces en versión Foil
- **Tablas Forjadas** — exclusivo de Oro: tablas retiradas de NPCs de nivel 10+ con historial de batalla

## Los Tres Tiers

Cada tier tiene su propio costo, límite de karma, y probabilidad de premios legendarios:

| Tier | Costo (FRJ) | Límite de Karma | Pre-Check Legendario |
|------|-------------|-----------------|---------------------|
| Bronce | 1,500 | 12 giros | 0.2% |
| Plata | 5,000 | 6 giros | 0.5% |
| Oro | 20,000 | 4 giros | 1.0% |

### Bronce — El Entry-Level

El tier más accesible. Ideal para jugadores nuevos o F2P que quieren probar suerte sin arriesgar demasiado. Las recompensas son modestas, pero el límite de karma de 12 giros significa que eventualmente te llevarás una Carta Rara sí o sí. Además, con solo 1,500 FRJ por giro, puedes permitirte varios intentos.

### Plata — El Punto Dulce

La mejor relación valor/FRJ gastado. Con 5,000 FRJ por giro, las probabilidades mejoran notablemente: más cartas Raras y Épicas, mejores accesorios, y el límite de karma baja a solo 6 giros. Si ya llevas un rato jugando y tienes un colchón de FRJ, Plata es tu tier.

### Oro — Para Coleccionistas y Ballenas

20,000 FRJ por giro. Caro, sí, pero las recompensas lo valen: 1% de pre-check legendario, 15% de Carta Rara, accesorios Épicos/Legendarios, y el 3% de posibilidades de recibir una **Tabla Forjada**. Solo para quienes tienen FRJ de sobra y buscan lo mejor de lo mejor.

---

## Triple Suerte — El Combo

**Costo: 22,500 FRJ** — 15% de descuento vs comprar los tres tiers por separado (26,500 FRJ).

La Triple Suerte gira los tres tiers (Bronce, Plata, Oro) en una sola operación. Recibes tres resultados independientes, uno de cada tier. Pero tiene una ventaja CRUCIAL:

> **Protección anti-duplicados**: si en una misma Triple Suerte te tocaría el mismo objeto raro dos veces, el sistema re-rolla automáticamente el duplicado. No puedes recibir dos Cartas Raras idénticas (mismo ID) en un solo combo.

Es la opción con mejor valor del juego. Si puedes ahorrar 22,500 FRJ, hazlo — vale la pena.

---

## Pool de Premios por Cápsula

Esto es EXACTAMENTE lo que puede salir de cada cápsula, con sus probabilidades reales:

| Resultado | Bronce | Plata | Oro |
|-----------|--------|-------|-----|
| **FRJ** | 55% (40-120 FRJ) | 30% (150-450 FRJ) | 12% (400-2,000 FRJ) |
| **Carta** | 28% (Común/Rara) | 40% (Rara/Épica) | 43% (Épica/Legendaria) |
| **Accesorio** | 10% (Común) | 15% (Raro) | 18% (Épico/Legendario) |
| **Sobre (Booster)** | 5% | 10% | 12% |
| **Carta Rara** | 2% (Rara/Épica) | 5% (Épica/Legendaria) | 15% (Épica/Legendaria) |

### Notas sobre el pool:
- **FRJ** es el resultado más común — en Bronce, más de la mitad de los giros devuelven FRJ. Esto es por diseño: recuperas algo, pero generalmente menos de lo que gastaste. Los giros de Oro pueden devolver hasta 2,000 FRJ, lo cual es un 10% de retorno.
- **Carta** vs **Carta Rara**: son categorías separadas con pools distintos. La Carta Rara tiene su propio slot de probabilidad y es la que activa el sistema de karma.
- **Accesorios** mejoran en rareza con el tier: solo Comunes en Bronce, hasta Legendarios en Oro.
- **Sobre** puede ser normal o Foil (ver abajo).

---

## Sistema de Karma (Pity)

El Karma es el sistema que garantiza que **nunca te vas con las manos vacías después de muchos giros**. Funciona así:

1. Cada tier tiene su propio **contador de karma**, independiente y rastreado por jugador.
2. El contador sube +1 con cada giro donde NO recibes una **Carta Rara**.
3. Cuando el contador llega al límite de ese tier, el siguiente giro **GARANTIZA** una Carta Rara.
4. El contador se **reinicia a cero** cuando:
   - Recibes una Carta Rara (por probabilidad normal o por karma)
   - Recibes un drop Legendario de cualquier tipo (carta, accesorio, o sobre foil legendario)

### Límites por tier:
| Tier | Límite de Karma | Giros máximos sin Carta Rara |
|------|----------------|------------------------------|
| Bronce | 12 | 11 — el 12º es garantizado |
| Plata | 6 | 5 — el 6º es garantizado |
| Oro | 4 | 3 — el 4º es garantizado |

### La Barra de Karma en la UI

Junto a la máquina de cápsulas, verás una barra que se va llenando:
- **Vacía (azul frío)**: recién empezando, todo normal.
- **Media (amarillo)**: va subiendo, el karma se acumula.
- **Caliente (naranja/rojo)**: ¡estás cerca del límite! El siguiente giro podría ser EL giro.
- **GARANTIZADO (dorado pulsante)**: has llegado al límite. Tu próximo giro en este tier **SÍ O SÍ** te da una Carta Rara. La barra muestra "¡KARMA ACTIVADO!" con efectos visuales.

La barra añade una capa de estrategia: ¿giras una vez más en Bronce para activar el karma, o ahorras para una Triple Suerte? Esas decisiones son parte del juego.

---

## Probabilidad de Sobre Foil

Cuando el resultado de tu giro es "Sobre" (Booster), hay una probabilidad secundaria de que sea **Foil** (brillante, edición especial) en lugar de un sobre normal:

| Tier | Probabilidad de Foil |
|------|---------------------|
| Bronce | 5% |
| Plata | 12% |
| Oro | 22% |

Los sobres Foil contienen objetos de mayor rareza que los sobres normales del mismo tipo. Visualmente, la cápsula brilla con un efecto arcoíris antes de abrirse — no te lo pierdes.

---

## Tabla Forjada — Exclusiva de Oro

**Probabilidad: 3%** en cápsulas de Oro.

Las **Tablas Forjadas** son tableros de lotería retirados de NPCs de nivel 10+ que tienen un historial de batalla real. Son piezas únicas con historia: cada una viene con su registro de partidas, victorias, derrotas, y un texto de origen que cuenta de dónde viene.

Características:
- Tableros con nivel 10 o superior
- Historial de batalla documentado (partidas jugadas, ganadas, perdidas)
- Historia de origen generada proceduralmente
- Solo disponibles si tienes **slots de tablero libres** en tu inventario. Si no tienes espacio, la Tabla Forjada no puede ser reclamada — ¡asegúrate de tener slots antes de girar en Oro!

Conseguir una Tabla Forjada es uno de los momentos más emocionantes de La Suertuda. La animación de revelado es épica: la cápsula de Oro se resquebraja, el tablero emerge con un brillo cegador, y aparece su historia de origen en pantalla.

---

## ¿Qué Tier Deberías Comprar?

### Jugador Nuevo / F2P
**Ve por Bronce.** Bajo riesgo, 1,500 FRJ por giro, y el karma te respalda. La experiencia de revelado es igual de divertida en todos los tiers. Cuando puedas, ahorra para una Triple Suerte — los 22,500 FRJ duelen, pero el 15% de descuento y la protección anti-duplicados lo compensan.

### Mid-Game (ya tienes varios Axolotitos y FRJ estables)
**Plata es tu mejor amigo.** Mejor valor por FRJ gastado. Buenas probabilidades de Carta Rara (5%), accesorios Raros, y solo 6 giros para el karma. Con 5,000 FRJ por giro, puedes hacer varias tiradas sin arruinarte.

### Ballena / Coleccionista
**Oro, sin duda.** Mayor probabilidad de legendarios (1% pre-check), 15% de Carta Rara, accesorios Épicos/Legendarios, y la posibilidad de una Tabla Forjada (3%). Cada giro es una experiencia premium.

### Mejor Valor Absoluto
**Triple Suerte (22,500 FRJ).** 15% más barato que comprar los tres tiers por separado, protección anti-duplicados, y tres revelados seguidos que son pura dopamina. Si puedes ahorrar esa cantidad, es la mejor inversión en La Suertuda.

### Regla de Oro
> **NUNCA te gastes tus últimos FRJ en cápsulas.** Los FRJ también los necesitas para cuotas de entrada a partidas, comida para tus Axolotitos, y otras mecánicas del juego. La Suertuda es diversión y emoción, no necesidad. Juega con responsabilidad.

---

## Cápsulas Gratis

No todo en La Suertuda cuesta FRJ. Hay formas de conseguir giros gratis:

### Membresía VIP
Los miembros del Club VIP reciben cápsulas mensuales según su nivel:
- **Coral**: 2× Bronce al mes
- **Dorado**: 2× Bronce + 1× Plata al mes
- **Axolite**: 3× Bronce + 2× Plata + 1× Oro al mes

### Ciclo Lunar — Día 7
Cada séptimo día del Ciclo Lunar otorga recompensas que pueden incluir cápsulas. Ver [[21-ciclo-lunar-y-recompensas]] para los detalles completos.

Las cápsulas gratis **no cuentan para el karma** — el contador de karma solo avanza con giros pagados. Pero los premios que obtengas de cápsulas gratis son tuyos para siempre.

---

## Estrategia y Psicología del Gacha

La Suertuda está diseñada para ser divertida, justa, y transparente. Aquí van algunos consejos de jugadores veteranos:

1. **El karma es tu red de seguridad.** No es un castigo por tener mala suerte — es una garantía de que eventualmente recibirás algo bueno. Bronce con 12 giros de karma significa que, en el peor caso, gastas 18,000 FRJ para una Carta Rara garantizada.
2. **No persigas el legendario.** La probabilidad de pre-check legendario es baja (0.2%-1.0%). Si te toca, celébralo como el evento especial que es. Si no, disfruta el viaje.
3. **La Triple Suerte es matemáticamente superior.** 15% de descuento + protección anti-duplicados. Si tienes la paciencia de ahorrar, hazlo.
4. **Diversifica.** Alterna entre La Suertuda, la Tienda, el Tianguis, y las partidas normales. No pongas todos tus FRJ en un solo sistema.
5. **Las cápsulas VIP son un beneficio pasivo.** Si estás considerando hacerte VIP, valora las cápsulas gratis como parte del paquete.

---



### 15-vip-club
> `conceptos/15-vip-club.md`

---
tags: [conceptos, economia, vip]
description: "Club VIP de Axolotto — Coral, Dorado y Axolite, beneficios, costos y análisis | Axolotto VIP Club — Coral, Dorado and Axolite, benefits, costs and analysis"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Club VIP — Membresía Premium

El **Club VIP de Axolotto** es un sistema de membresía premium por suscripción mensual (30 días) que ofrece beneficios exclusivos en toda la plataforma: generación diaria de FRJ, descuentos en tienda, cápsulas gashapon gratuitas, slots extra y más. Todos los precios se pagan en **AXF (Axofichas)**. No es pay-to-win — todo lo que otorga el VIP se puede obtener también con FRJ, solo que más lento.

---

## Los Tres Niveles

Cada nivel tiene una duración de **30 días** desde el momento de activación. Los precios y beneficios son fijos y no cambian entre renovaciones.

### Tabla Comparativa de Beneficios

| Beneficio | Coral | Dorado | Axolite |
|-----------|-------|--------|---------|
| **Precio (AXF/mes)** | 400 | 600 | 1,800 |
| **Costo aprox. MXN** | ~$800 MXN | ~$1,200 MXN | ~$3,600 MXN |
| **FRJ diario (claim)** | 40/día | 100/día | 200/día |
| **FRJ máximo mensual** | 1,200 | 3,000 | 6,000 |
| **Descuento en tienda** | 5% | 12% | 20% |
| **Cápsulas mensuales** | 2× Bronce | 2× Bronce + 1× Plata | 3× Bronce + 2× Plata + 1× Oro |
| **Slots extra de tablero** | 0 | +1 | +2 |
| **Slots extra de Axolotito** | 0 | 0 | +1 |
| **Comisión P2P** | 4% | 3% | 1.5% |
| **Descuento en Multijugador** | 0% | 0% | 15% |
| **Bonus de Jackpot** | 0% | 0% | +5% |
| **Bono FRJ de bienvenida** | 200 | 500 | 1,000 |
| **Sobrecito de bienvenida** | Ninguno | 1× Normal | 1× Foil |
| **Descuento expansión Cueva** | 50% FRJ, 50% tiempo | 50% FRJ, 50% tiempo | 50% FRJ, 50% tiempo |
| **Bypass niveles Cueva** | Nivel 6 | Niveles 6+7 | Niveles 6+7+8 |
| **Marco visual** | Teal animado | Dorado + corona | Gradiente oro→rosa→violeta |

---

## Análisis de Rentabilidad (Break-Even)

### Nivel Coral — 400 AXF/mes

- **1,200 FRJ/mes** equivale a ~120 AXF al tipo de cambio del Banco de Algas (10 FRJ ≈ 1 AXF).
- **Descuento del 5%** en tienda: si gastas 2,000 AXF/mes en tienda, ahorras 100 AXF.
- **2 cápsulas Bronce**: valor aproximado de ~3,000 FRJ en el mercado de cápsulas.
- **Valor total estimado**: 120 AXF (FRJ) + 100 AXF (descuento) + ~300 AXF (cápsulas) = **~520 AXF** de valor por 400 AXF invertidos.
- **Veredicto**: Excelente para jugadores casuales. Se paga solo con los FRJ y las cápsulas.

### Nivel Dorado — 600 AXF/mes

- **3,000 FRJ/mes** equivale a ~300 AXF.
- **Descuento del 12%** en tienda: si gastas 2,000 AXF/mes, ahorras 240 AXF.
- **4 cápsulas (2 Bronce + 1 Plata)**: valor aproximado de ~8,500 FRJ (~850 AXF equivalentes).
- **+1 slot de tablero**: te permite jugar una partida extra simultánea.
- **Valor total estimado**: 300 AXF (FRJ) + 240 AXF (descuento) + ~850 AXF (cápsulas) = **~1,390 AXF** de valor por 600 AXF invertidos.
- **Veredicto**: La mejor relación calidad-precio para jugadores activos. El nivel más popular por una razón.

### Nivel Axolite — 1,800 AXF/mes

- **6,000 FRJ/mes** equivale a ~600 AXF.
- **Descuento del 20%** en tienda: si gastas 2,000 AXF/mes, ahorras 400 AXF. Si gastas 5,000 AXF, ahorras 1,000 AXF.
- **7 cápsulas (3 Bronce + 2 Plata + 1 Oro)**: valor aproximado de ~33,000 FRJ (~3,300 AXF equivalentes).
- **+2 slots de tablero** y **+1 slot de Axolotito**: máxima flexibilidad de juego.
- **15% descuento en Multijugador** y **+5% bonus de jackpot**: aumentan ganancias significativamente para jugadores intensivos.
- **Comisión P2P reducida al 1.5%**: ideal para traders frecuentes.
- **Valor total estimado**: 600 AXF (FRJ) + 400-1,000 AXF (descuento) + ~3,300 AXF (cápsulas) = **~4,300-4,900 AXF** de valor por 1,800 AXF invertidos.
- **Veredicto**: Imprescindible para jugadores hardcore que juegan varias horas al día. El ROI es masivo si aprovechas todos los beneficios.

---

## Mecánica de Reclamo Diario (Daily Claim)

El FRJ diario del VIP **NO se acredita automáticamente**. Debes entrar al juego y reclamarlo manualmente cada día. Esto es intencional — queremos que entres al Nido todos los días.

- **Acumulación máxima**: 2 días. Si no reclamas hoy, el FRJ de hoy se guarda para mañana.
- **Caducidad**: Al tercer día sin reclamar, el lote más antiguo expira y se pierde.
- **Animación**: Al reclamar, monedas FRJ vuelan hacia tu contador con una animación satisfactoria. Es un pequeño momento de alegría diaria.
- **Consejo**: Entra aunque sea 1 minuto al día para reclamar tu FRJ. Es el beneficio más valioso del VIP.

---

## Recompensas por Racha VIP (VIP Streak Rewards)

Mantener tu suscripción VIP activa durante meses consecutivos desbloquea recompensas **permanentes** que no pierdes aunque tu VIP expire después.

| Meses consecutivos | Recompensa | Tipo |
|--------------------|------------|------|
| **3 meses** | Insignia "Constante" | Permanente |
| **6 meses** | Marco cosmético "Veteran" | Permanente |
| **12 meses** | Título "Axolotto Original" + 1 Webito Astral GRATIS | Permanente |
| **24 meses** | Marco "Legend of the Nido" — el más raro del juego | Permanente |

### Seguimiento de racha

- La racha se registra como `vip_streak_months` en tu perfil.
- Para mantener la racha, debes renovar tu VIP dentro de una **ventana de 27 a 63 días** desde la activación anterior.
- Si dejas pasar **más de 63 días** sin VIP activo, la racha se **reinicia a cero**.
- Las recompensas ya obtenidas son tuyas para siempre, incluso si la racha se reinicia.

---

## Mecánica de Upgrade (Mejora de Nivel)

Si ya tienes un nivel VIP activo y quieres subir a uno superior, el sistema aplica un **crédito proporcional** por los días no utilizados de tu plan actual.

### Fórmula

```
crédito = (precio_plan_actual / 30) × días_restantes
precio_final = precio_plan_nuevo - crédito
```

### Ejemplo

Tienes **Coral (400 AXF)** con **15 días restantes**. Quieres subir a **Dorado (600 AXF)**.

- Crédito: (400 / 30) × 15 = **200 AXF**
- Precio final: 600 - 200 = **400 AXF**

Solo pagas 400 AXF por la mejora, y tus 15 días restantes no se desperdician.

### Notas importantes sobre upgrades

- La **primera activación** de cada nivel (la primera vez que compras Coral, Dorado o Axolite) siempre otorga los bonos de bienvenida: FRJ extra y sobrecitos.
- Si ya recibiste el bono de bienvenida de Dorado en el pasado, un upgrade posterior a Dorado no lo vuelve a dar.
- Las **cápsulas mensuales** se entregan al momento de la compra o renovación. Al hacer upgrade, recibes las cápsulas del nuevo nivel de inmediato (proporcionales a los días restantes).

---

## ¿Qué Pasa Cuando el VIP Expira?

Cuando tu suscripción VIP termina, no pierdes nada permanente, pero los beneficios extra se desactivan:

### Efectos inmediatos al expirar

- **FRJ diario**: Dejas de recibir el bono diario.
- **Descuentos**: Vuelven a los precios base sin descuento.
- **Comisiones P2P**: Vuelven a la tasa estándar (5%).
- **Cápsulas mensuales**: No se entregan más hasta renovar.

### Slots extra (efecto de congelamiento)

- **Slots de tablero extra**: Los tableros más nuevos (los que ocupan los slots extra) se **congelan** y devuelven HTTP 423 Locked si intentas acceder a ellos. No se borran — al renovar, se descongelan automáticamente.
- **Slot de Axolotito extra (Axolite)**: El Axolotito más reciente se congela. Si era tu Axolotito principal, el sistema reasigna automáticamente al siguiente disponible.

### Período de gracia

- Tienes **7 días de gracia** después de la expiración.
- Recibirás notificaciones a los **7, 3 y 1 días** antes de que expire tu VIP.
- Durante el período de gracia, algunos beneficios menores pueden persistir (como el marco visual).
- Tus Axolotitos y tableros **no desaparecen** — solo quedan bloqueados hasta que renueves.

---

## Auto-Renovación

El sistema de auto-renovación te permite mantener tu VIP activo sin preocuparte por renovar manualmente.

- **Activación**: Toggle ON/OFF en la sección VIP de tu Perfil.
- **Funcionamiento**: Al final de tu período de 30 días, el sistema descuenta automáticamente el costo en AXF de tu wallet y renueva por otros 30 días.
- **Requisito**: Debes tener saldo suficiente de AXF al momento del cobro.
- **Si no hay saldo suficiente**: La auto-renovación falla, recibes una notificación, y tu VIP expira normalmente (con el período de gracia de 7 días).
- **Recomendación**: Mantenla activada si juegas regularmente. Es un "set and forget" que te asegura no perder tu racha VIP por olvido.

---

## ¿Qué VIP Es Para Ti? (Guía para Jugadores)

### Jugador Casual (pocas partidas por semana)
**Elige Coral.** Por 400 AXF al mes (~$800 MXN), obtienes 1,200 FRJ, 5% de descuento y 2 cápsulas Bronce. El valor total (~520 AXF) supera el costo. Ideal si juegas fines de semana o algunas tardes.

### Jugador Activo (juegas a diario)
**Elige Dorado.** Por 600 AXF al mes (~$1,200 MXN), obtienes 3,000 FRJ, 12% de descuento, +1 slot de tablero, y 4 cápsulas. Es el nivel más popular porque ofrece la **mejor relación valor/AXF** de los tres. El valor total (~1,390 AXF) duplica la inversión.

### Jugador Hardcore (varias horas al día)
**Elige Axolite.** Por 1,800 AXF al mes (~$3,600 MXN), obtienes el paquete completo: 6,000 FRJ, 20% descuento, 7 cápsulas incluyendo 1 de Oro, +2 slots de tablero, +1 slot de Axolotito, 15% descuento en Multijugador, y +5% de bonus en jackpot. El valor total estimado (~4,300-4,900 AXF) triplica la inversión si aprovechas todos los beneficios.

### Free-to-Play (F2P)
**No necesitas VIP.** Todo lo que ofrece el Club VIP se puede obtener también sin pagar AXF real, solo que más lento. Los FRJ se ganan jugando, las cápsulas se compran en el Gashapon, y los descuentos no aplican. El VIP es una _aceleración_, no una barrera. Axolotto está diseñado para que jugadores F2P y VIP convivan en el mismo ecosistema.

---

## Preguntas Frecuentes

**¿Puedo cambiar de nivel VIP sin perder mis días restantes?**
Sí. El sistema de upgrade aplica un crédito proporcional por los días no usados. Solo pagas la diferencia.

**¿Las recompensas de racha se pierden si mi VIP expira?**
No. Las recompensas de racha (insignias, marcos, títulos, Webito Astral) son **permanentes**. Si tu racha se reinicia, no pierdes lo ya obtenido.

**¿Puedo regalar VIP a otro jugador?**
Actualmente no. El VIP es personal e intransferible. Estamos evaluando agregar "gift cards" de VIP en el futuro.

**¿El VIP se paga con FRJ?**
No. El VIP solo se paga con AXF. Sin embargo, los beneficios del VIP generan FRJ que puedes usar en el juego.

**¿Qué pasa si tengo VIP y el servidor se cae un día que no reclamé?**
El sistema de claim diario tiene 2 días de acumulación precisamente para cubrir imprevistos. Si el servidor está caído más de 2 días, contacta a soporte.

---



### 16-el-cenote-cueva
> `conceptos/16-el-cenote-cueva.md`

---
tags: [conceptos, progresion, cueva]
description: "El Cenote — sistema de expansión de cueva de 8 niveles con logros y bonificaciones | The Cenote — 8-level cave expansion system with achievements and bonuses"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# El Cenote — Expansión de Cueva

El Cenote es tu santuario submarino personal en el corazón del Xochimilco Digital. No es solo una cueva: es tu hogar, tu centro de operaciones, y la columna vertebral de tu progresión en Axolotto. Aquí incubas Webitos, alojas a tus axolotitos, recibes visitas, decoras, y desbloqueas multiplicadores permanentes que transforman toda tu economía.

## ¿Qué es el Cenote?

Imagina una escena inmersiva 2.5D bajo el agua: capas de profundidad que se desvanecen en un azul místico, rayos de luz que atraviesan la superficie, burbujas que ascienden lentamente, y tus axolotitos nadando libremente entre formaciones rocosas cubiertas de musgo luminiscente. Así es El Cenote.

- **Santuario personal**: Tu espacio privado en Xochimilco Digital, visible para otros jugadores que pueden visitarte y dejar likes.
- **7 ranuras de incubación**: Nidos acuáticos donde depositas Webitos para que eclosionen en axolotitos.
- **NO se compra directamente**: Cada expansión requiere primero cumplir un logro, y luego pagar su costo en FRJ + esperar el tiempo de excavación.
- **Cada nivel desbloquea**: Más espacios para axolotitos, ranuras de decoración, asientos de mesa, slots de staking, y multiplicadores económicos.

> La cueva es el camino principal de progresión. Cada nivel te hace más fuerte económicamente. No es cosmético: es estratégico.

---

## Los 8 Niveles del Cenote

Expandir tu cueva es una travesía épica desde un modesto nicho hasta un palacio astral. Cada nivel tiene un nombre, un requisito, un costo en FRJ, un tiempo de excavación, y un desbloqueo clave.

| Nvl | Nombre | Logro Requerido | Costo FRJ | Excavación | Espacios Axo | Desbloqueo Clave |
|-----|--------|-----------------|-----------|------------|-------------|------------------|
| 1 | **El Nicho** | Tutorial (automático) | Gratis | Instantáneo | 1 | Tu primer hogar |
| 2 | **La Gruta** | 10 juegos + axo principal nivel 3 | 500 | 2 horas | 2 | +2% multiplicador FRJ en todas las ganancias |
| 3 | **La Caverna** | Ganar 3 juegos + racha de 3 días | 1,500 | 6 horas | 3 | +1 carta inicial en juegos, 2 asientos para hostear mesas |
| 4 | **El Salón** | 1 Jackpot O 25 juegos multijugador | 4,000 | 12 horas | 4 | +5% probabilidad de drop de boosters, 4 asientos |
| 5 | **El Santuario** | Axo principal nivel 15 | 8,000 | 24 horas | 5 | +1 ranura global de incubación, 6 asientos |
| 6 | **El Abismo** | 50 juegos + 100 feeds O VIP Coral+ | 15,000 | 36 horas | 6 | -5% reducción de comisión P2P |
| 7 | **El Templo** | 100 juegos + 15 victorias O VIP Dorado+ | 30,000 | 48 horas | 7 | 1 sobrecito Foil gratis al mes |
| 8 | **Palacio Astral** | 200 juegos + axo épico/legendario O VIP Axolite | 60,000 | 72 horas | 8 | +10% multiplicador ecosistema AXF |

### Bonificaciones por Nivel

Cada nivel de cueva no solo te da más espacio: te da poder económico permanente que se acumula con cada expansión.

| Nivel | Bonificación | Impacto |
|-------|-------------|---------|
| 2 | **+2% multiplicador FRJ** | Ganas 2% más FRJ en absolutamente todo: juegos, staking, ventas P2P, recompensas diarias. |
| 3 | **+1 carta inicial en juegos** | Empiezas cada partida de lotería con una carta extra en tu mano. Ventaja táctica inmediata. |
| 3 | **2 asientos para hostear** | Puedes crear mesas de juego y recibir a 2 jugadores. |
| 4 | **+5% drop de boosters** | Los sobres y boosters tienen 5% más probabilidad de aparecer en tus recompensas. |
| 4 | **4 asientos de mesa** | Hostea partidas para hasta 4 jugadores. |
| 5 | **+1 ranura global de incubación** | Un espacio extra de incubación que se suma a todos los demás. Aceleras tu crianza masivamente. |
| 5 | **6 asientos de mesa** | Hostea partidas para hasta 6 jugadores. |
| 6 | **-5% comisión P2P** | Pagas 5% menos de fee en todas tus ventas del marketplace P2P. |
| 7 | **1 sobrecito Foil gratis mensual** | Cada mes recibes un sobrecito Foil sin costo. Los Foil contienen las cartas más raras y valiosas. |
| 8 | **+10% multiplicador ecosistema AXF** | Ganas 10% más AXF en todas las ventas P2P. El multiplicador definitivo para el endgame. |

### Capacidad de la Cueva por Nivel

| Característica | Nvl 1 | Nvl 2 | Nvl 3 | Nvl 4 | Nvl 5 | Nvl 6 | Nvl 7 | Nvl 8 |
|---------------|-------|-------|-------|-------|-------|-------|-------|-------|
| Espacios para axolotitos | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| Ranuras de decoración | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
| Asientos de mesa | — | — | 2 | 4 | 6 | 8 | 8 | 8 |
| Slots de staking | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

---

## Mecánica de Excavación

Expandir el Cenote no es instantáneo: cada nivel requiere una **excavación en tiempo real**. Tu axolotito principal excava la cueva mientras el temporizador corre.

| Nivel | Tiempo de Excavación |
|-------|----------------------|
| 1 → 2 | 2 horas |
| 2 → 3 | 6 horas |
| 3 → 4 | 12 horas |
| 4 → 5 | 24 horas |
| 5 → 6 | 36 horas |
| 6 → 7 | 48 horas |
| 7 → 8 | 72 horas |

- **Tiempo real**: El temporizador avanza aunque no estés en el juego. Inicias la excavación y vuelves cuando termine.
- **Aceleración con AXF**: Puedes acelerar la excavación pagando **4 AXF por cada hora restante** (redondeada hacia arriba). Ejemplo: quedan 11 horas = 44 AXF.
- **⚠️ ADVERTENCIA**: Si aceleras una expansión, **pierdes el huevo de recompensa** de ese nivel. Los huevos son extremadamente valiosos — piensa dos veces antes de acelerar.
- **Celebración de subida de nivel**: Al completarse la excavación (naturalmente), se activa una cinemática con overlay que revela el nuevo nombre, diseño y funcionalidades del nivel.

> **Estrategia**: Inicia las excavaciones largas (24h+) antes de irte a dormir o cuando sepas que no jugarás por un rato. La paciencia paga con huevos gratis.

---

## Huevos de Recompensa por Nivel

Cada expansión completada de forma natural (sin aceleración AXF) te otorga un huevo Webito como recompensa. Estos huevos tienen rareza creciente.

| Nivel | Huevo de Recompensa | Rareza |
|-------|--------------------|--------|
| 1 | Ninguno (tutorial) | — |
| 2 | Webito Fase 1 | Común |
| 3 | Webito Fase 1+ | Común mejorado |
| 4 | Webito Fase 2 | Poco común |
| 5 | Webito Fase 2 + elección de naturaleza | Poco común (elige rasgo) |
| 6 | Webito Fase 2 + elección de naturaleza | Poco común (elige rasgo) |
| 7 | **Webito ASTral** | ¡Mítico! (valor: 3,000 AXF) |
| 8 | **Webito ASTral** | ¡Mítico! (valor: 3,000 AXF) |

Los Webitos ASTrales de los niveles 7 y 8 son los más valiosos del juego: cada uno vale 3,000 AXF en el mercado. Completar la expansión completa de forma natural te da **dos Webitos ASTrales** (6,000 AXF de valor total). Esto por sí solo justifica no acelerar ninguna excavación.

---

## Slots de Staking desde la Cueva

El staking es una mecánica de ingresos pasivos: dejas a tus axolotitos generando FRJ mientras no juegas. Tu nivel de cueva determina cuántos puedes stakear simultáneamente.

- **Fórmula**: `nivel_cueva + 1 = slots de staking`
- Nivel 1: 2 slots. Nivel 8: 9 slots.
- Cada axolotito stakeado genera FRJ pasivo por hora.
- Mientras un axolotito está stakeado, no puede usarse en juegos ni mostrarse en la cueva.

> Con 9 slots al nivel 8, puedes tener un ecosistema completo de staking generando ingresos las 24 horas.

---

## Decoración de la Cueva

Tu Cenote es tu lienzo. A medida que expandes, desbloqueas ranuras de decoración para personalizar cada rincón.

- **4 categorías**: SUELO, PARED, AGUA, ESPECIAL
- **Ranuras**: 2 en nivel 1, +2 por nivel (máximo 16 en nivel 8)
- **2 minijuegos**:
  - **Pozo de los Deseos**: Lanza 20 FRJ y pide un deseo (recompensa aleatoria).
  - **Arcade Submarino**: Juega por 1 AXF (minijuego de habilidad).
- **Exhibición**: Muestra tu axolotito estrella y trofeos.
- **Visitantes**: Otros jugadores pueden visitar tu Cenote y dejar likes.

→ Ver detalles completos en [[17-decoracion-de-cueva]]

---

## Beneficios VIP en la Cueva

Los miembros VIP reciben ventajas masivas en la expansión de la cueva.

| Beneficio VIP | Detalle |
|---------------|---------|
| **50% descuento en FRJ** | Todos los costos de expansión se reducen a la mitad. |
| **50% menos tiempo de excavación** | Los temporizadores corren al doble de velocidad. |
| **Bypass de logros** | VIP Coral+ saltea logro del nivel 6. VIP Dorado+ saltea logros del 6 y 7. VIP Axolite saltea logros del 6, 7 y 8. |

Con VIP Axolite, expandir al nivel 8 cuesta 30,000 FRJ (en vez de 60,000) y la excavación toma 36 horas (en vez de 72). Una diferencia abismal.

---

## Estrategia de Progresión

No todos los niveles son igual de importantes. Este es el orden de prioridad recomendado:

1. **Nivel 3 cuanto antes** — Desbloquea hosteo de mesas y la carta inicial extra. Es el primer gran salto de poder.
2. **Nivel 5 después** — La ranura de incubación extra acelera tu crianza masivamente. Más axolotitos = más staking = más FRJ.
3. **Nivel 7 a continuación** — El sobrecito Foil mensual gratuito es un ingreso pasivo brutal. Y el Webito ASTral de regalo vale 3,000 AXF.
4. **Nivel 8 como objetivo final** — El multiplicador +10% AXF es el premio definitivo del endgame.

### Consejos Clave

- **Ahorra FRJ para expansiones**: Son mejoras permanentes. Cada nivel se paga solo con el tiempo.
- **VIP transforma la experiencia**: 50% menos costo y 50% menos tiempo es una ventaja enorme.
- **Nunca aceleres una excavación**: Los huevos gratis, especialmente los ASTrales, valen mucho más que el costo de aceleración.
- **Inicia excavaciones antes de pausas**: Si vas a dormir o trabajar, inicia la excavación y deja que el tiempo haga su trabajo.
- **El Webito ASTral del nivel 7** es uno de los objetos más valiosos del ecosistema: 3,000 AXF. No lo pierdas por acelerar.

---



### 17-decoracion-de-cueva
> `conceptos/17-decoracion-de-cueva.md`

---
tags: [conceptos, cueva, decoracion, minijuegos]
description: "Decora tu Cenote con items cosmeticos y funcionales — 4 categorias, 2 minijuegos, bonificaciones apilables | Decorate your Cenote with cosmetic and functional items — 4 categories, 2 minigames, stackable bonuses"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Decoracion de Cueva y Minijuegos

Tu Cenote no es solo un espacio funcional: es tu lienzo, tu galeria, tu arcade privado y tu carta de presentacion ante la comunidad. La decoracion transforma una cueva espartana en un santuario unico que refleja tu personalidad, atrae visitas, y ademas te da bonificaciones reales de gameplay. Y cuando necesitas un descanso de la loteria, dos minijuegos te esperan dentro de tu propia cueva.

## ¿Que es la Decoracion de Cueva?

Personalizar tu Cenote con items decorativos es una de las mecanicas mas creativas y sociales de Axolotto. No es puramente cosmetico: muchas decoraciones otorgan bonificaciones que mejoran tu economia y la eficiencia de tus axolotitos.

- **Personaliza tu Cenote**: Elige entre docenas de items decorativos para hacer tu cueva unica.
- **Visitable por otros jugadores**: Tu cueva aparece en listados publicos. Otros jugadores pueden entrar, explorar, y dejar likes.
- **Bonificaciones de gameplay**: Algunas decoraciones mejoran la recuperacion de enfoque, el staking de FRJ, o la incubacion de Webitos.
- **Expresion creativa**: Combina categorias, temas y colores. Algunos jugadores crean cuevas tematicas (pirata, galactica, selva, minimalista...).

> Una cueva bien decorada no solo es bonita: es mas eficiente. Las bonificaciones se acumulan y escalan con tu nivel de cueva y tu coleccion de axolotitos.

---

## Categorias de Decoracion

Cada item decorativo pertenece a una categoria y ocupa un tipo de ranura especifico. No puedes poner un item de PARED en una ranura de SUELO.

| Categoria | Ejemplos | Tipo de Ranura |
|-----------|----------|----------------|
| **PISO** (FLOOR) | Lechos de algas, estatuas, cofres del tesoro, alfombras de arena | Ranuras de suelo |
| **PARED** (WALL) | Musgo bio-luminiscente, banderines VIP, pinturas rupestres, estalactitas decorativas | Ranuras de pared |
| **AGUA** (WATER) | Lirios flotantes, juguetes flotantes, corrientes de burbujas, medusas decorativas | Ranuras de agua |
| **ESPECIAL** (SPECIAL) | Jukebox de coral, maquina arcade, calentador termico (interactivos) | Ranuras especiales |
| **EXHIBICION** (EXHIBIT) | Exhibe tu axolotito estrella + trofeos ganados | Ranuras de exhibicion |

Cada categoria tiene su propia coleccion de items, y algunas categorias (como ESPECIAL) contienen objetos interactivos que tu y tus visitantes pueden usar.

---

## Ranuras de Decoracion por Nivel de Cueva

A medida que expandes tu Cenote, desbloqueas mas ranuras para decorar. Mas ranuras = mas decoraciones = una cueva mas impresionante.

| Nivel de Cueva | Ranuras de Decoracion |
|---------------|----------------------|
| 1 | 2 |
| 2 | 4 |
| 3 | 6 |
| 4 | 8 |
| 5 | 10 |
| 6 | 12 |
| 7 | 14 |
| 8 | 16 |

- **Formula**: `nivel_cueva x 2 = ranuras de decoracion`
- **Maximo**: 16 ranuras en nivel 8
- **Progresion lineal**: +2 ranuras por cada nivel que expandes

---

## Bonificaciones por Decoraciones

No todo es estetica. Algunas decoraciones proporcionan bonificaciones reales que mejoran tu eficiencia en el juego. Estas bonificaciones se acumulan entre si.

| Bonificacion | Efecto | Escala con... | Maximo |
|-------------|--------|---------------|--------|
| **Impulso de Recuperacion de Enfoque** (Focus Recovery Boost) | Tus axolotitos recuperan enfoque mas rapido | Nivel de cueva | — |
| **Multiplicador de Staking FRJ** (Staking FRJ Multiplier) | Aumenta el FRJ generado por axolotitos stakeados | Cantidad de axolotitos activos | — |
| **Impulso Termico de Incubacion** (Incubation Thermal Boost) | Mantiene los Webitos mas calientes, acelerando la incubacion | Fijo | **+20%** |

- **Las bonificaciones se acumulan**: Una cueva con decoraciones de recuperacion, staking, e incubacion recibe las tres bonificaciones simultaneamente.
- **Sinergia con el nivel de cueva**: El Impulso de Recuperacion escala con tu nivel de cueva, haciendo que cada expansion sea doblemente valiosa.
- **Sinergia con la coleccion**: El Multiplicador de Staking escala con cuantos axolotitos activos tienes, recompensando a los criadores dedicados.

> Una cueva bien decorada no es un lujo: es una inversion. Las bonificaciones se pagan solas con el tiempo.

---

## Minijuego 1 — Pozo de los Deseos (Wishing Well)

Ubicado en tu cueva, el Pozo de los Deseos es un minijuego de azar accesible y adictivo. Lanzas 20 FRJ al pozo, pides un deseo, y el pozo decide tu destino.

- **Costo**: 20 FRJ por intento
- **Premios aleatorios**:
  - FRJ (a veces recibes mas de lo que lanzaste — el pozo es generoso... a veces)
  - Items decorativos
  - Accesorios para axolotitos
  - Y de vez en cuando... nada. El pozo tambien sabe ser caprichoso.
- **Sin limite diario**: Puedes lanzar tantos deseos como quieras... mientras tengas FRJ.
- **Diversion tipo "gambling-lite"**: No te gastes la renta aqui. Es para entretenerse, no para hacerte rico.

> "El pozo de los deseos da, y el pozo de los deseos quita." — Proverbio axolotito

El Pozo de los Deseos es el pasatiempo perfecto entre partidas. Bajo riesgo, alta recompensa potencial, y ese subidon de dopamina cuando el pozo te devuelve 100 FRJ de un lanzamiento de 20.

---

## Minijuego 2 — Arcade Submarino (Underwater Arcade)

El Arcade Submarino es un minijuego de habilidad instalado en tu cueva. A diferencia del Pozo, aqui tu destreza determina el resultado.

- **Costo**: 1 AXF por partida
- **Leaderboard local**: Cada cueva tiene su propia tabla de puntuaciones maximas. Solo se registran las partidas jugadas en TU arcade.
- **Competencia con visitantes**: Otros jugadores pueden jugar en tu arcade cuando visitan tu cueva, y sus puntuaciones aparecen en tu leaderboard. Defiende tu primer puesto.
- **Puramente por diversion y orgullo**: No hay premios economicos directos. El premio es ver tu nombre en la cima del leaderboard... y que los visitantes lo vean tambien.
- **Tematico**: Estetica retro de arcade adaptada al mundo submarino.

> "Gaming retro, pero mas mojado." — Eslogan del Arcade Submarino

El Arcade es el lugar perfecto para retar a tus amigos. "Visita mi cueva y supera mi puntuacion... si puedes."

---

## Funcionalidades Sociales

La decoracion no existe en el vacio: tu cueva es un espacio social. Otros jugadores pueden visitarte, explorar tu decoracion, jugar en tu arcade, y dejar likes.

- **Visitas**: Cualquier jugador puede visitar tu Cenote desde el listado de cuevas publicas.
- **Likes**: Los visitantes pueden dejar likes en cuevas que les gusten. Es el equivalente axolotito de un corazon en Instagram.
- **Visibilidad en el lobby**: Las cuevas mejor decoradas y con mas likes aparecen mas arriba en los listados de partidas. Decorar bien atrae jugadores a tus mesas.
- **Exhibicion**: La ranura de EXHIBICION muestra tu axolotito estrella y tus trofeos mas preciados. Es tu carta de presentacion: "Este es mi mejor axolotito, estos son mis logros."
- **Jukebox de coral**: Si instalas este item ESPECIAL, los visitantes pueden escuchar musica ambiental en tu cueva.
- **Calentador termico**: Otro item ESPECIAL interactivo que beneficia la incubacion de Webitos (bonificacion de +20% termica).

---

## Como Conseguir Decoraciones

Hay multiples fuentes para obtener items decorativos. Algunas son mas accesibles que otras.

| Fuente | Detalle |
|--------|---------|
| **Capsulas Gashapon** | La fuente mas comun. Las capsulas pueden contener decoraciones de todas las categorias. |
| **Mercado P2P** | Compra decoraciones a otros jugadores en el Tianguis. Algunos items raros solo se encuentran aqui. |
| **Eventos especiales** | Temporadas festivas, torneos, y eventos comunitarios otorgan decoraciones exclusivas. |
| **Recompensas VIP** | Los miembros VIP reciben decoraciones exclusivas que no se pueden obtener de otra forma. |
| **Expansion de cueva** | Algunos niveles de cueva desbloquean decoraciones unicas como recompensa por la expansion. |

> Las decoraciones de eventos especiales y VIP suelen ser las mas valiosas y cotizadas en el mercado P2P. Si participaste en un evento limitado, guarda bien ese item: puede valer una fortuna en unos meses.

---



### 18-forja-y-fundicion
> `conceptos/18-forja-y-fundicion.md`

# 18 — Forja y Fundición (Forge & Melter)

> **English Summary**: The crafting system has two halves: the **Card Melter** ("El Cenote Místico") destroys 5 identical non-shiny, non-first-edition duplicates to reward fragments + FRJ + 1 random card of a higher tier; the **Forge** spends fragments + FRJ to craft a *specific* card from the 54-card catalog with no randomness. Fragments (común/raro/épico/legendario) are wallet-tracked and non-tradable. Commons are best melted, valuable singles are best sold on the P2P market, and the Forge is your tool when you need one exact card to finish a collection or optimize a board.

---

## Quick Reference

| Concept | Key Rule |
|---------|----------|
| **Fundición (Melter)** | Burn 5 identical copies → fragments + FRJ + 1 random higher-rarity card |
| **Forja (Forge)** | Spend fragments + FRJ → craft 1 **specific** card of your choice |
| **Cannot melt** | Shiny/foil, first edition, or legendary cards |
| **Fragment storage** | Wallet-tracked, non-tradable, non-transferable |
| **Best melt** | Common duplicates (5+ copies) |
| **Best sell** | Foils, first editions, high-market-value rares/legendaries (see [[19-mercado-p2p]]) |
| **Best forge** | When 1–2 cards away from completing a collection or building a board strategy |

---

## 1. La Fundición de Cartas — "El Cenote Místico"

La Fundición es un caldero místico donde sacrificas cartas duplicadas para obtener recursos de crafteo y una carta de rareza superior. Es el sistema principal para convertir cartas excedentes en valor real.

### Reglas de fundición

- Debes quemar **5 copias idénticas** de la misma carta.
- Las 5 copias deben ser **no brillantes (non-shiny)** y **no primera edición (non-first-edition)**.
- **No se pueden fundir** cartas legendarias, cartas foil/shiny, ni cartas de primera edición.
- Recibes: **fragmentos + FRJ + 1 carta aleatoria de una rareza superior**.

### Costos y recompensas

| Input (5 cartas) | Costo FRJ | Fragmentos ganados | Output (1 carta) |
|------------------|-----------|---------------------|------------------|
| 5 Comunes | 100 FRJ | +10 frag_común | 1 Rara aleatoria |
| 5 Raras | 250 FRJ | +10 frag_raro | 1 Épica aleatoria |
| 5 Épicas | 1,500 FRJ | +10 frag_épico | 1 Legendaria aleatoria |
| 5 Legendarias | No permitido | — | — |

> La salida es **aleatoria** dentro de la rareza superior. No puedes elegir qué carta recibes al fundir.

---

## 2. Tipos de Fragmentos

Los fragmentos son la moneda de crafteo. Se almacenan en tu wallet y **no son transferibles ni comerciables** en el [[19-mercado-p2p|Mercado P2P]].

| Fragmento | Color | Se obtiene al fundir | Se usa para forjar |
|-----------|-------|----------------------|---------------------|
| `frag_común` | Verde | 5 Comunes | Cartas Comunes |
| `frag_raro` | Azul | 5 Raras | Cartas Raras |
| `frag_épico` | Púrpura | 5 Épicas | Cartas Épicas |
| `frag_legendario` | Dorado | — (ver Forja) | Cartas Legendarias |

> Los fragmentos legendarios **no se obtienen fundiendo** (porque no se pueden fundir legendarias). Se obtienen por otras vías (eventos, recompensas especiales, [[13-tienda-y-tianguis|Tienda]]).

---

## 3. La Forja — Crafteo de cartas específicas

A diferencia de la Fundición, la Forja te permite crear una **carta exacta** del catálogo de 54 cartas (ver [[09-cartas]]). **Sin aleatoriedad**: tú eliges cuál quieres.

### Costos de forja

| Rareza objetivo | Fragmentos requeridos | Costo FRJ |
|-----------------|-----------------------|-----------|
| Común | 50 frag_común | 100 FRJ |
| Rara | 100 frag_raro | 500 FRJ |
| Épica | 250 frag_épico | 1,000 FRJ |
| Legendaria | 500 frag_legendario | 3,000 FRJ |

> Forjar una Legendaria (500 frags + 3,000 FRJ) es un objetivo de largo plazo. Requiere acumular fragmentos legendarios consistentemente.

---

## 4. Estrategia — ¿Fundir o Vender?

La decisión de fundir una carta o venderla en el [[19-mercado-p2p|Mercado P2P]] depende de su rareza, edición y valor de mercado:

| Situación | Acción recomendada | Razón |
|-----------|--------------------|-------|
| 5+ duplicados de una Común | **Fundir** | Las comunes rara vez tienen alto valor P2P; los fragmentos son más útiles |
| Carta foil/shiny o primera edición | **Vender en P2P** | No se puede fundir de todos modos; valor de colección alto |
| Rara con buen precio de mercado | **Vender en P2P** | Revisa precios primero; puede valer más que los fragmentos |
| Épica duplicada | **Pensar con cuidado** | Evalúa si el precio P2P justifica no fundir |
| Legendaria duplicada | **Vender en P2P** | No se puede fundir; siempre tiene valor de mercado |
| A 1–2 cartas de completar colección | **Forjar** | Usa los fragmentos acumulados para cerrar la colección |
| Necesitas carta específica para estrategia de tablero | **Forjar** | La Forja te da control total sobre cuál recibes |

### Regla general

- **Comunes → Fundir.** Conviertes "basura" en recursos de crafteo.
- **Raras con valor → Vender.** Consulta el [[19-mercado-p2p|Mercado P2P]] antes.
- **Épicas → Analizar caso por caso.**
- **Legendarias → Vender.** No hay otra opción; su valor P2P suele ser alto.
- **Para completar colecciones → Forjar.** Es la única forma garantizada de obtener la carta exacta que te falta.

---

## 5. Gestión de Fragmentos

- Los fragmentos se acumulan **pasivamente** al fundir cartas. No requieren acción adicional.
- Consulta tu saldo en la **interfaz del Cenote Místico (Fundición)**.
- **No acumules fragmentos indefinidamente.** Úsalos para forjar cartas que realmente necesitas, ya sea para completar una colección o para armar estrategias de tablero específicas.
- Prioriza forjar cartas que tengan sinergia con tu [[09-cartas|colección actual]] y tu estilo de juego.

---

## 6. Flujo completo recomendado

1. **Abre sobres** en la [[13-tienda-y-tianguis|Tienda]] para obtener cartas.
2. **Identifica duplicados**: separa commons repetidas, foil/primera-edición, y cartas con valor P2P.
3. **Vende** las cartas con alto valor en el [[19-mercado-p2p|Mercado P2P]].
4. **Funde** las comunes sobrantes para generar fragmentos y una carta de rareza superior.
5. **Forja** cartas específicas cuando te falten pocas para completar una colección o necesites una carta clave para tu tablero.
6. **Repite.** El ciclo abrir-fundir-forjar-vender mantiene tu colección en crecimiento constante.

---

**Wikilinks**: [[09-cartas]] · [[13-tienda-y-tianguis]] · [[19-mercado-p2p]] · [[00-INDEX]]


### 19-mercado-p2p
> `conceptos/19-mercado-p2p.md`

---
tags: [conceptos, economia, mercado, p2p]
description: "Mercado P2P de Axolotto — compra y venta entre jugadores, subasta de cartas, tablas y Axolotitos, sistema de comisiones VIP y renta de tablas | Axolotto P2P Marketplace — player-to-player trading, card & board auctions, VIP commission system and board rentals"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Mercado P2P — Compra y Venta Entre Jugadores

El **Mercado P2P de Axolotto** es un bazar impulsado por los jugadores donde TÚ pones los precios. Compra y vende cartas individuales, tableros completos, Axolotitos y accesorios. Todo se comercia en **FRJ**, la moneda de juego. Es el corazón de la economía circular de Axolotto: los jugadores crean valor y otros jugadores lo compran.

---

## ¿Qué Puedes Vender?

El mercado acepta cinco tipos de artículos:

| Tipo de artículo | ¿Es NFT on-chain? | Notas |
|---|---|---|
| **Cartas individuales** | No (off-chain) | De tu colección personal. Las cartas foil valen 5-50x más |
| **Tableros completos** | Sí (ERC-721) | Transferencia on-chain del NFT [[10-tablas]] |
| **Axolotitos** | Sí (ERC-721) | Solo se recomienda vender duplicados — ¡necesitas al menos 1 para jugar! |
| **Accesorios y cosméticos** | No (off-chain) | Marcos, skins, decoraciones de cueva |
| **Sobrecitos sellados** | No (off-chain) | Boosters sin abrir — atractivos para compradores que buscan la emoción del unboxing |

---

## Publicar un Artículo

Publicar un artículo en el mercado es gratis y sin penalización por cancelar.

### Proceso de publicación

1. Abre tu **Inventario**
2. Selecciona el artículo que quieres vender
3. Pulsa **"Publicar en Mercado"**
4. Configura los parámetros de venta (varían según el tipo)

### Parámetros por tipo de artículo

**Cartas individuales:**
- Precio de venta en FRJ
- La carta queda bloqueada (no se puede usar en tableros mientras esté listada)

**Tableros completos:**
- Precio de venta en FRJ
- Opciones de renta (ver sección Renta de Tableros más abajo)
- El tablero se retira de tus slots activos al listarlo
- Si el tablero tiene staking activo, el staking se pausa automáticamente

**Axolotitos:**
- Precio de venta en FRJ
- El Axolotito debe tener al menos **24 horas de enfriamiento** desde su última partida
- No puedes vender tu último Axolotito (necesitas al menos 1 para jugar)
- Las stats, naturaleza y rasgos visuales se muestran en el listing

**Sobrecitos sellados:**
- Precio de venta en FRJ
- El sobrecito no puede estar abierto (obviamente)

### Gestión de listings

- Tu artículo permanece listado **hasta que se venda o lo canceles**
- Puedes cancelar un listing en cualquier momento sin costo ni penalización
- Al cancelar, el artículo vuelve inmediatamente a tu inventario
- Puedes modificar el precio de un listing activo sin necesidad de cancelarlo y volverlo a publicar

---

## Comisiones del Mercado (Commission)

El mercado cobra una pequeña comisión sobre cada venta para mantener la economía saludable. La comisión **la paga el vendedor** (se descuenta del precio de venta).

### Tabla de Comisiones por Nivel VIP

| Estatus VIP | Comisión de Venta | Comisión de Renta | Destino Venta | Destino Renta |
|---|---|---|---|---|
| Sin VIP | 5% | 5% | TreasuryVault | Quemado (BURN) |
| Coral | 4% | 4% | TreasuryVault | Quemado (BURN) |
| Dorado | 3% | 3% | TreasuryVault | Quemado (BURN) |
| Axolite | 1.5% | 1.5% | TreasuryVault | Quemado (BURN) |
| Cueva Nivel 6+ | -5% adicional | -5% adicional | — | — |

### Entendiendo las comisiones

- **Comisión de venta:** Va al **TreasuryVault** (la tesorería del juego). Estos FRJ se reinvierten en premios de jackpot, eventos especiales y recompensas comunitarias. No desaparecen — circulan de vuelta al ecosistema.
- **Comisión de renta:** Se **QUEMA** (se destruye permanentemente). Esto reduce la oferta total de FRJ en circulación y ayuda a controlar la inflación. Los FRJ quemados desaparecen para siempre del ecosistema.
- **Bonus de Cueva Nivel 6+:** Los jugadores con Cueva nivel 6 o superior reciben una reducción adicional de 5 puntos porcentuales en ambas comisiones. Este bonus se **acumula** con el descuento VIP.

### Ejemplo de cálculo

Vendes una carta Legendaria Foil por **10,000 FRJ**:

| Tu nivel | Comisión | Recibes |
|---|---|---|
| Sin VIP | 5% = 500 FRJ | 9,500 FRJ |
| Coral | 4% = 400 FRJ | 9,600 FRJ |
| Dorado | 3% = 300 FRJ | 9,700 FRJ |
| Axolite | 1.5% = 150 FRJ | 9,850 FRJ |
| Axolite + Cueva 6+ | -3.5% → 0% (mínimo) | 10,000 FRJ |

> **Importante:** La comisión efectiva nunca baja de 0%. No hay comisiones "negativas" — el mercado no te paga por vender.

---

## Renta de Tableros (Scholarship)

El sistema de renta de tableros es una de las mecánicas más innovadoras y populares del Mercado P2P. Permite a dueños de tableros generar ingresos pasivos y a jugadores sin buenos tableros acceder a equipo de alto nivel.

### Cómo funciona

1. **El dueño configura la renta:**
   - Precio de renta en **FRJ por 24 horas**
   - Porcentaje de ganancias que recibe el dueño si el rentador gana partidas (**owner share %**)
2. **El rentador paga el precio** y recibe el tablero por 24 horas
3. **Si el rentador gana partidas** con ese tablero, el dueño recibe su porcentaje de las ganancias
4. Al terminar las 24 horas, el tablero vuelve automáticamente al dueño

### Ejemplo de renta

- Dueño lista el tablero "Destructor Estelar" (CSR 78%):
  - Precio de renta: **200 FRJ / 24h**
  - Owner share: **15%**
- Rentador paga 200 FRJ y juega durante 24 horas
- El rentador gana 3 partidas Champions: 3 x 400 = **1,200 FRJ** en premios
- El dueño recibe 15% de 1,200 = **180 FRJ** adicionales
- **Dueño gana:** 200 + 180 = 380 FRJ | **Rentador gana:** 1,200 - 200 - 180 = 820 FRJ netos

### Win-win para ambos

- **Dueño:** Ingreso pasivo sin jugar. Mientras más gane el rentador, más gana el dueño — incentivo alineado.
- **Rentador:** Acceso a tableros premium que no podría construir todavía. Ideal para nuevos jugadores o para probar builds antes de comprar.

### Rentar desde el Ranking

Puedes rentar tableros directamente desde la **tabla de clasificaciones (Rankings)**. Los tableros con alto CSR (win rate) y buen historial de staking aparecen destacados. Esto hace que el mercado sea transparente — los mejores tableros son visibles para todos.

---

## Comprar Artículos

El proceso de compra está diseñado para ser simple pero seguro.

### Flujo de compra

1. **Explora el mercado** — lista infinita con scroll, filtrable por:
   - Tipo de artículo (cartas, tableros, Axolotitos, accesorios, sobres)
   - Rareza (Común, Rara, Épica, Legendaria)
   - Estado foil (normal, foil)
   - Rango de precio en FRJ
   - Ordenar por: precio (asc/desc), rareza, fecha de publicación
2. **Encuentra tu artículo** y revisa sus detalles
3. **Mantén presionado para confirmar** (hold-to-confirm) — evita compras accidentales
4. Los **FRJ se descuentan de tu wallet**
5. El artículo aparece en tu **inventario** inmediatamente
6. Si es un NFT (tablero, Axolotito), la **transferencia on-chain** se ejecuta automáticamente

### Requisitos para transferencias NFT

Para comprar o vender artículos que son NFTs (tableros, Axolotitos), **tanto el comprador como el vendedor** deben tener una wallet vinculada a su cuenta. Si alguna de las partes no tiene wallet, la transacción se rechaza con un mensaje explicativo.

---

## Seguridad del Mercado

El Mercado P2P está diseñado con múltiples capas de protección para que todas las transacciones sean seguras:

- **Escrow del servidor:** Todas las transacciones son mediadas por el servidor del juego. No hay transferencias directas wallet-a-wallet — el juego actúa como intermediario de confianza.
- **Artículos bloqueados al listar:** Un artículo listado en el mercado no puede usarse en partidas, staking ni otras mecánicas mientras esté a la venta. Esto evita conflictos y duplicaciones.
- **Transferencias atómicas:** Las transferencias on-chain son todo-o-nada. Si algún paso falla, la transacción completa se revierte. No existe el estado intermedio donde "el comprador pagó pero no recibió el NFT".
- **Sin riesgo de estafa:** Como el juego media todo, no hay forma de que un vendedor "se lleve el dinero y no entregue el artículo" ni de que un comprador "reciba el artículo y no pague".

---

## Tips Para el Mercado P2P

### Para vendedores

- **Revisa los precios del mercado antes de fundir cartas.** Una carta duplicada puede valer mucho más en el mercado que los materiales que obtendrías al fundirla. Compara siempre.
- **Las cartas foil raras se venden por 5 a 50 veces más** que su contraparte común. No las fundas por accidente.
- **Los tableros con alto CSR (win rate)** pueden cobrar precios premium en renta. Un CSR de 60%+ ya es atractivo para rentadores.
- **El mejor momento para vender es durante eventos especiales**, cuando la demanda sube por la emoción y las recompensas limitadas.
- **Incluye una buena descripción** en tu listing. Los compradores confían más en vendedores que detallan lo que ofrecen.

### Para compradores

- **El mejor momento para comprar es en horas valle** (madrugada o días entre semana), cuando hay menos competencia y los vendedores bajan precios.
- **Usa los filtros.** Con cientos o miles de listings, los filtros son tu mejor amigo para encontrar exactamente lo que buscas.
- **Renta antes de comprar.** Si estás considerando comprar un tablero caro, renta uno similar primero para ver si se adapta a tu estilo de juego.
- **Compara precios.** El mismo tipo de carta puede tener precios muy distintos entre vendedores. Tómate tu tiempo.

### Regla de oro

**Nunca vendas tu último Axolotito.** Necesitas al menos 1 Axolotito para jugar. Si vendes tu último, te quedarás sin poder participar en partidas hasta que incube uno nuevo o compre otro.

---



### 20-staking-ingresos-pasivos
> `conceptos/20-staking-ingresos-pasivos.md`

---
tags: [conceptos, economia, staking]
description: "Staking en Axolotto — genera FRJ pasivo con tus tablas y Axolotitos | Staking in Axolotto — earn passive FRJ with your boards and Axolotitos"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Staking — Ingresos Pasivos de FRJ

El staking es la fuente de ingresos pasivos mas estable de Axolotto. Mientras tus tablas no estan jugando y tus Axolotitos estan inactivos, generan Frijolitos (FRJ) automaticamente. No hay riesgo: no importa si ganas o pierdes partidas, el staking produce FRJ igual. Es la base economica que permite a los jugadores financiar su gameplay diario — entradas a partidas, comida para Axolotitos, capsulas — sin depender exclusivamente de los premios de cada ronda.

Hay dos tipos de staking que funcionan simultaneamente: **Staking de Tablas** y **Staking de Axolotitos**. Ambos se acumulan. Un jugador con buenas tablas y una coleccion de Axolotitos fuertes puede generar cientos de FRJ al dia sin mover un dedo... bueno, casi. Porque hay una regla importante: la regla **Play-to-Stake**.

## Staking de Tablas

Cualquier tabla que NO este jugando una partida activa puede ponerse en staking. La tasa de generacion depende de dos factores: la rareza de sus 16 cartas y el nivel de la tabla. El nivel de la tabla multiplica la tasa base: el multiplicador es `1 + 0.1 x nivel`. Una tabla nivel 20 genera el triple que una tabla nivel 1. Ademas, cada carta foil en la tabla otorga un **+5% de rendimiento adicional**, acumulable hasta un maximo de +80% si las 16 cartas son foil. Una tabla completamente foil de nivel alto es una maquina de imprimir FRJ.

Para cobrar, ve a tu inventario y haz clic en "Cobrar" sobre la tabla, o usa "Cobrar Todo" para reclamar todas las tablas de una vez. Hay un limite de acumulacion de **24 horas**: si no reclamas en ese plazo, el FRJ excedente se pierde. No lo dejes pasar.

**Regla Play-to-Stake para Tablas**: debes haber jugado al menos 1 partida en cualquier modo en las ultimas 24 horas. Si no, el staking se pausa hasta que vuelvas a jugar. Esto asegura que el staking sea una recompensa por participar activamente en el ecosistema, no un mecanismo de "farm and forget".

## Staking de Axolotitos

Los Axolotitos que no estan jugando ni durmiendo pueden asignarse a los espacios de staking dentro de tu cueva (el Cenote). La cantidad de espacios disponibles depende del nivel de tu cueva: `nivel_cueva + 1` espacios. Una cueva nivel 8 te da 9 espacios para stakear Axolotitos simultaneamente.

La tasa de generacion de cada Axolotito se calcula a partir de **dos factores combinados**: la rareza de su skin (cuerpo base) y la rareza de sus 6 partes individuales (ojos, branquias, cresta, cola, aletas, patron). La skin define la tasa base por hora, y cada parte anade un bonus adicional.

### Multiplicadores de Skin (tasa base por hora)

| Rareza de Skin | FRJ/hora |
|----------------|----------|
| Comun (rosa, gris) | 0.05 |
| Rara (cyan, morado) | 0.15 |
| Epica (neon, coral) | 0.40 |
| Legendaria (oro) | 1.00 |
| Astral | 2.50 |

### Bonos por Parte (cada una de las 6 partes suma)

| Rareza de Parte | FRJ/hora por parte |
|-----------------|---------------------|
| Rasgo Comun | 0.01 |
| Rasgo Raro | 0.03 |
| Rasgo Epico | 0.08 |
| Rasgo Legendario | 0.20 |

### Como se calcula la tasa horaria

Se parte de la tasa base de la skin y se suman los bonos de las 6 partes. Luego, el nivel del Axolotito aplica un multiplicador: `1 + 0.1 x nivel`. Cada nivel aumenta el rendimiento un 10%.

**Ejemplo con un Axolotito Epico nivel 15**:
- Skin Epica (neon): 0.40 FRJ/h base
- Partes: 3 raras + 2 epicas + 1 legendaria = 3x0.03 + 2x0.08 + 1x0.20 = 0.09 + 0.16 + 0.20 = 0.45 FRJ/h en bonos
- Base total: 0.40 + 0.45 = 0.85 FRJ/h
- Con nivel 15: 0.85 x (1 + 0.1 x 15) = 0.85 x 2.5 = 2.125 FRJ/h
- Por dia: 2.125 x 24 = **51 FRJ/dia**
- Con 8 Axolotitos similares stakedos: aproximadamente **400 FRJ/dia**

**Ejemplo Legendario Completo (mejor caso realista)**:
- Skin Legendaria Oro: 1.00 FRJ/h
- 6 partes Legendarias: 6 x 0.20 = 1.20 FRJ/h
- Base total: 2.20 FRJ/h
- Nivel 30: 2.20 x (1 + 0.1 x 30) = 2.20 x 4.0 = 8.8 FRJ/h
- Por dia: 8.8 x 24 = **211 FRJ/dia por Axolotito**
- Con 9 stakedos: aproximadamente **1,900 FRJ/dia** — ahora si estamos hablando en serio

**Ejemplo Astral (maximo absoluto)**:
- Skin Astral: 2.50 FRJ/h
- 6 partes Legendarias: 1.20 FRJ/h
- Base total: 3.70 FRJ/h
- Nivel 30: 3.70 x 4.0 = 14.8 FRJ/h
- Por dia: **355 FRJ/dia por Axolotito**

## Regla Play-to-Stake

Esta regla aplica a AMBOS tipos de staking. Debes jugar al menos **1 partida en cualquier modo** en las ultimas 24 horas. Si no juegas, el staking se pausa completamente hasta que vuelvas a participar. Esto no es un castigo — es un recordatorio de que Axolotto es un juego de habilidad y competencia, no una inversion pasiva. El staking recompensa a quienes participan activamente.

## Limites de Acumulacion

| Tipo de Staking | Limite de acumulacion | Frecuencia optima de cobro |
|-----------------|-----------------------|----------------------------|
| Tablas | 24 horas | 1 vez al dia |
| Axolotitos | 12 horas | 2 veces al dia |

El FRJ no reclamado que exceda el limite se **PIERDE**. Si dejas un Axolotito Legendario 30 sin cobrar por 24 horas, solo recibiras 12 horas de FRJ — el resto desaparece. Pon una alarma o entra a cobrar en la manana y en la noche.

## Como Maximizar tus Ingresos Pasivos

- **Expande tu cueva**: mas espacios de staking = mas Axolotitos generando FRJ simultaneamente. Una cueva nivel 8 te da 9 espacios.
- **Cria por rasgos raros**: skins Astrales y Legendarias, y partes Legendarias, multiplican dramaticamente las tasas. Cada cruza es una inversion a largo plazo.
- **Sube de nivel a tus Axolotitos**: cada nivel es +10% de rendimiento. Un nivel 30 cuadruplica la tasa base.
- **Construye tablas foil**: cada carta foil en la tabla suma +5% al rendimiento. Una tabla 100% foil rinde +80%.
- **Juega a diario**: manten activa la regla Play-to-Stake. Una partida rapida es suficiente.
- **Cobra regularmente**: no dejes que los limites de acumulacion desperdicien tu FRJ.
- **El VIP ayuda indirectamente**: mas espacios de tablas, mas espacios de Axolotitos, expansion de cueva mas rapida.

## Por Que Stakeear?

El staking es el ingreso de FRJ mas estable del juego. No depende de ganar partidas, no tiene riesgo de perder, y escala con todo lo que haces en Axolotto: jugar, criar, mejorar tu coleccion. Los jugadores de endgame pueden financiar todo su gameplay — entradas, comida, capsulas, crianza — unicamente con staking. Y lo mejor: funciona en segundo plano mientras tu te diviertes jugando.

---



### 21-ciclo-lunar-y-recompensas
> `conceptos/21-ciclo-lunar-y-recompensas.md`

# 21 — Ciclo Lunar y Recompensas Diarias

> **Lunar Cycle and Daily Rewards** — A 3-loop reward system inspired by moon phases. Log in, claim, and watch your streak turn into escalating rewards. The F2P player's best friend.

**Wikilinks:** [[12-economia-dual]] · [[14-capsulas-gashapon]] · [[25-f2p-guia-gratis]] · [[00-INDEX]]

---

## Quick Reference

| Concept | Detail |
|---------|--------|
| **Loop 1 — Weekly** | 7 daily rewards (50–130 FRJ + Day-7 capsule) |
| **Loop 2 — Luna Phases** | 6 escalating weeks (Bronce → Plata → Oro capsules) |
| **Loop 3 — Full Cycle** | 42 perfect days = celebration + permanent badge |
| **Miss 1 day** | No penalty |
| **Miss 2–7 days** | Daily streak resets to Day 1; Luna (week) stays |
| **Miss 8+ days** | FULL reset — back to Luna 1, Day 1 |
| **Claim method** | Manual — click the HUD button daily |
| **Best free reward** | Luna 6 Day 7: 1× Oro capsule (~20,000 FRJ value) |

---

## 1. What is the Lunar Cycle? · ¿Qué es el Ciclo Lunar?

**English:** A 3-loop reward system inspired by moon phases that replaces the old "daily capsule + daily FRJ" system. It rewards you for logging in every day — the longer your streak, the better the rewards. A moon phase indicator in the HUD shows your current position so you always know where you stand.

**Español:** Un sistema de recompensas de 3 ciclos inspirado en las fases lunares, que reemplaza el antiguo sistema de "cápsula diaria + FRJ diario". Te premia por iniciar sesión cada día — cuanto más larga sea tu racha, mejores serán las recompensas. Un indicador de fase lunar en el HUD muestra tu posición actual para que siempre sepas dónde estás.

**Key idea:** Every day you log in, you get something. Every week you complete, the next week gets better. Every 6 weeks you complete a full cycle, you earn a permanent badge. Miss too many days? The moon resets.

---

## 2. Loop 1 — Weekly (7 Days) · Ciclo Semanal

> **Siete días, una cápsula gratis.**

| Day | Reward | Running Total |
|-----|--------|---------------|
| Day 1 | 50 FRJ | 50 FRJ |
| Day 2 | 65 FRJ | 115 FRJ |
| Day 3 | 80 FRJ | 195 FRJ |
| Day 4 | 95 FRJ | 290 FRJ |
| Day 5 | 110 FRJ | 400 FRJ |
| Day 6 | 130 FRJ | 530 FRJ |
| **Day 7** | **Capsule** (based on Luna level) | 530 FRJ + 1 capsule |

**Week total:** 530 FRJ + 1 capsule — completely free, just for showing up.

The daily FRJ payout ramps up through the week. The real treasure is Day 7: a capsule whose rarity depends on which Luna phase you are in (see Loop 2 below). The higher your Luna, the better the capsule — from Bronce all the way up to Oro.

---

## 3. Loop 2 — Luna Phases (6 Weeks) · Fases Lunares

> **Cada Luna completada mejora la cápsula del Día 7.**

| Luna | Day 7 Reward | Cumulative Capsules |
|------|-------------|---------------------|
| Luna 1 | 1× Bronce capsule | 1 Bronce |
| Luna 2 | 2× Bronce capsules | 3 Bronce |
| Luna 3 | 1× Plata capsule | 3 Bronce + 1 Plata |
| Luna 4 | 1× Plata + 1× Bronce | 4 Bronce + 2 Plata |
| Luna 5 | 2× Plata capsules | 4 Bronce + 4 Plata |
| **Luna 6** | **1× Oro capsule** | 4 Bronce + 4 Plata + **1 Oro** |

Each week you complete advances your Luna by 1. As you progress, the Day-7 reward escalates dramatically:

- **Lunas 1–2:** Bronce capsules — solid, useful, get you started.
- **Lunas 3–5:** Plata capsules — rarer items, better odds, higher value.
- **Luna 6:** Oro capsule — the best free reward in the entire game.

The Luna phase is displayed in the HUD as `L1`, `L2`, ... `L6`, always visible next to your current day.

---

## 4. Loop 3 — Full Lunar Cycle (42 Perfect Days) · Ciclo Lunar Completo

> **42 días seguidos = celebración + insignia permanente.**

Complete all 6 Lunas (42 consecutive daily claims) and you trigger:

- **Celebration:** Special visual effects across the entire HUD. Confetti, moon glow, the works. The game celebrates WITH you.
- **Permanent Badge:** `"Axolotl Lunar — Cycle I"` — a seasonal badge that stays on your profile forever. It is never removed, never expires, and never degrades.
- **Cycle Counter:** After Cycle I, you start Cycle II. Then Cycle III. Badges stack — a Cycle V player flexes hard.
- **Badges are PERMANENT:** Show off your dedication. Other players see your cycle badges and know you are consistent.

**Total rewards over a full 42-day cycle:**

| Resource | Amount |
|----------|--------|
| FRJ | 3,180 (6 weeks × 530 FRJ) |
| Bronce capsules | 4 |
| Plata capsules | 4 |
| Oro capsules | 1 |
| Permanent badge | 1 ("Axolotl Lunar — Cycle I") |

At Luna 6 Day 7 alone, that Oro capsule is worth approximately 20,000 FRJ — completely free. This single reward can sustain weeks of F2P gameplay.

---

## 5. Streak Rules · Reglas de Racha

> **El ciclo lunar perdona… pero no demasiado.**

| Scenario | Consequence |
|----------|-------------|
| **Miss 1 day** | No penalty. The system is forgiving — life happens. |
| **Miss 2–7 days** | Daily streak resets to Day 1. **Your Luna (week) stays the same.** You restart the current week from Day 1. |
| **Miss 8+ days** | **FULL reset.** Back to Luna 1, Day 1. All progress lost. Ouch. |

**Moral:** Don't miss more than a week, ever. One missed day is free. Two to seven days costs you the daily streak but preserves your Luna. Eight days or more? The moon forgets you.

**Strategy tip:** Even on days you cannot play, log in for 30 seconds and hit the claim button. It costs nothing and keeps your cycle alive.

---

## 6. Claiming Rewards · Reclamar Recompensas

**How it works step by step:**

1. **Look at the HUD:** The Daily Claim button shows your position — e.g., `L1 D3/7` means Luna 1, Day 3 of 7.
2. **Tap the button:** A bottom sheet slides up with the full lunar phase visualization.
3. **Day grid:** Shows which days you have already claimed (checkmark), which day is today (glowing), and the rewards for future days (dimmed).
4. **Claim animation:** Coins and items fly from the lunar display to your counter. Feels satisfying every time.
5. **IMPORTANT:** Rewards do NOT auto-credit. You MUST claim manually each day. If you log in but don't claim, the day does not count.

**The bottom sheet shows:**
- Current Luna phase (moon icon, waxing/waning visual)
- 7-day grid with claim status
- Next capsule preview (what you get on Day 7)
- Cycle badge progress bar

---

## 7. F2P Value of the Lunar Cycle · Valor F2P

> **El mejor amigo del jugador gratuito.**

The Lunar Cycle is designed to make free-to-play sustainable and rewarding:

| Metric | Value |
|--------|-------|
| Weekly FRJ (minimum) | 530 FRJ |
| Full cycle FRJ | 3,180 FRJ |
| Full cycle capsules | 1 Oro + 4 Plata + 4 Bronce |
| Best single reward | Oro capsule at Luna 6 Day 7 (~20,000 FRJ value) |
| Cost to player | 0 AXF, 0 FRJ, 0 real money — just time and consistency |

**Why this matters for F2P:**

- 530 FRJ per week covers multiple cheap game entries (easy games cost 10 AXF, but FRJ is the secondary currency used for boosters, sobrecitos, and market trades — see [[12-economia-dual]]).
- The escalating capsules give you a steady stream of items without spending a single AXF — see [[14-capsulas-gashapon]] for what each capsule tier contains.
- The Oro capsule at the end of a full cycle is genuinely game-changing for a F2P player.
- See [[25-f2p-guia-gratis]] for a complete F2P strategy that centers around the Lunar Cycle.

**Comparison with old system:** The old daily system gave a flat reward every day with no escalation and no streak incentives. The Lunar Cycle rewards consistency and patience — exactly what F2P players can offer.

---

## 8. Tips · Consejos

1. **Make daily login a habit.** Even if you don't play, just open the app and claim. Thirty seconds keeps the moon bright.
2. **The Oro capsule at Luna 6 Day 7 is the best free reward in the game.** Plan your item usage around it — save your best strategies for when that Oro capsule drops.
3. **Never miss more than 7 days.** One week is the hard boundary between "annoying reset" and "devastating reset." Set a calendar reminder if you travel.
4. **Permanent badges are social proof.** Other players see your cycle count. A Cycle III+ badge tells the community you are dedicated and consistent.
5. **Set a phone reminder.** Daily claim takes less than a minute. A 30-second daily notification is the difference between Cycle I and never leaving Luna 1.
6. **Claim even on "off" days.** You don't need to play a single game — just log in, tap the claim button, and close the app. Your streak stays alive.
7. **Stack your claims with other dailies.** If the game adds more daily activities, do them all in one quick session. Efficiency is king.

---

## Summary · Resumen

| Loop | Duration | What You Get |
|------|----------|--------------|
| Weekly (Loop 1) | 7 days | 530 FRJ + 1 capsule per week |
| Luna Phases (Loop 2) | 6 weeks | Escalating capsule rarity (Bronce → Plata → Oro) |
| Full Cycle (Loop 3) | 42 days | 3,180 FRJ + 9 capsules + permanent badge |

**The golden rule:** Claim every day. Miss one day? Free pass. Miss a week? Painful but recoverable. Miss more? Start over. The moon watches, and the moon rewards the faithful.

---

*Last updated: 2026-06-09 · See [[00-INDEX]] for related concepts.*


### 22-jackpot
> `conceptos/22-jackpot.md`

---
tags: [conceptos, multijugador, jackpot]
description: "El Jackpot de Axolotto — cómo crece el premio gordo global y cómo ganarlo | The Axolotto Jackpot — how the global grand prize grows and how to win it"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# El Jackpot — El Premio Gordo

El Jackpot es el corazón palpitante del multijugador en Axolotto. Es un pozo de premios **global** que crece con cada partida multijugador que se juega en toda la plataforma. No importa en qué sala estés, no importa contra quién juegues: cada partida contribuye. Y cuando alguien lo gana, todo el mundo se entera.

## ¿Qué es el Jackpot?

Imagina un premio que nunca deja de crecer. Un número que ves en el lobby multijugador y que sube, partido tras partido, hora tras hora. Ese es el Jackpot. Es un pozo acumulado de **Frijolitos (FRJ)** — la moneda secundaria del juego — que se lleva quien logre una hazaña casi imposible: ganar una partida multijugador en los **primeros 4 a 6 naipes cantados**.

El Jackpot no tiene límite teórico. Puede llegar a cantidades enormes: 5,000 FRJ un martes tranquilo, 50,000 FRJ un fin de semana pico, o más. Es el premio más codiciado de todo Axolotto, y el momento más electrizante que un jugador puede vivir.

El Jackpot está **siempre visible** en el lobby multijugador. Cualquiera puede ver cuánto hay acumulado en este momento. Cuando alguien gana, una **notificación global** llega a todos los jugadores conectados. Es un evento comunitario.

## ¿Cómo Crece?

Cada partida multijugador contribuye al Jackpot automáticamente. Así de simple:

- **El 5% del pozo total de cada partida** se aparta para el Jackpot.
- Esto ocurre sin que los jugadores tengan que hacer nada. Es invisible, automático, parte del sistema.

Veamos ejemplos concretos:

| Sala | Jugadores | Entrada por jugador | Pozo total | 5% al Jackpot |
|------|-----------|---------------------|------------|---------------|
| Principiantes (Rookies) | 30 | 10 FRJ | 300 FRJ | **15 FRJ** |
| Campeones (Champions) | 30 | 50 FRJ | 1,500 FRJ | **75 FRJ** |
| Intermedia | 20 | 20 FRJ | 400 FRJ | **20 FRJ** |

Cada partida aporta su granito. En horas pico, con docenas de salas activas simultáneamente, el Jackpot puede crecer cientos de FRJ por minuto. En horas valle, crece más despacio pero nunca se detiene mientras haya partidas.

## ¿Cómo se Gana?

Aquí viene lo difícil. Ganar el Jackpot requiere cumplir **TODAS** estas condiciones simultáneamente:

1. ✅ **Completar Premio 1** — el primer patrón ganador de tu tabla (línea, cuadrito, esquinas, lo que sea).
2. ✅ **Ganar en los PRIMEROS 4 a 6 naipes cantados** — esta es la parte brutalmente difícil.
3. ✅ **La sala debe tener 5+ tablas HUMANAS** — los bots no cuentan para este requisito.
4. ✅ **Al menos 2 direcciones de wallet DIFERENTES** — medida anti-sybil. No puedes farmear el Jackpot tú solo con multicuentas.
5. ✅ **Solo jugadores humanos** — los bots no pueden disparar el Jackpot aunque cumplan las demás condiciones.

### ¿Por qué es tan increíblemente difícil?

Pongámoslo en perspectiva:

- El mazo tiene **54 naipes** en total.
- Los primeros 4 naipes representan solo el **7% del mazo**.
- La mayoría de los patrones de Premio 1 requieren al menos **4 posiciones específicas** en tu tabla 4×4.
- Estadísticamente, acertar una línea en los primeros 4 naipes con sorteos aleatorios tiene una probabilidad de aproximadamente **0.01% por partida** (1 en 10,000).

Y eso es solo la probabilidad base. Además necesitas que haya suficientes humanos en la sala, que no sean multicuentas, y que justo ese día el mazo te sonría.

Para tener una oportunidad real, necesitas:

- 🎯 **Una tabla excelente** con cobertura amplia de patrones (múltiples caminos al Premio 1).
- 🧠 **Alta estadística de Concentración (Focus)** para reducir tu probabilidad de fallo.
- 🧂 **Baja Salinidad** para que tus naipes lleguen temprano en el sorteo.
- 🍀 **Altísima Suerte** para que el Lucky Save te rescate si fallas por poco.
- 👥 **Una sala con suficientes humanos** (al menos 5 tablas humanas, 2 wallets distintas).
- 🃏 **Que los primeros 4-6 naipes coincidan PERFECTAMENTE** con tu tabla.

Es como pedirle al universo que alinee cinco planetas. Pero cuando se alinean... sucede lo imposible.

## El Pago

Cuando alguien gana el Jackpot, así se reparte:

| Destino | Porcentaje | Descripción |
|---------|-----------|-------------|
| **Ganador(es)** | **90%** | El premio principal. Si hay múltiples ganadores, se divide equitativamente. |
| **Resiembra** | **10%** | Vuelve al Jackpot para la siguiente ronda. Siempre hay algo que ganar. |

### Reglas adicionales del pago:

- **Múltiples ganadores**: Si varios jugadores completan Premio 1 en el mismo naipe calificado, el 90% se **divide en partes iguales** entre todos ellos. No hay un "primero" — si empatan en el mismo naipes, comparten.
- **Resiembra mínima**: Si el 10% de resiembra resulta en menos de **1,000 FRJ**, el tesoro del sistema inyecta la diferencia. El Jackpot **nunca baja de 1,000 FRJ**.
- **Bonus VIP Axolite**: Los jugadores con rango VIP Axolite reciben un **+5% extra** sobre SU porción del Jackpot. Es decir, si te tocan 4,500 FRJ, con VIP Axolite recibes 4,725 FRJ. El 5% extra no sale del pozo de los demás — es un bonus que añade el sistema.

## La Resiembra (Seed)

El Jackpot nunca desaparece del todo. Así funciona el ciclo:

1. **Se gana el Jackpot** → se paga el 90% al ganador.
2. **El 10% restante** se convierte en la semilla del nuevo Jackpot.
3. **Si ese 10% es menor a 1,000 FRJ**, el tesoro del juego inyecta la diferencia hasta alcanzar el mínimo.
4. **Al lanzar el sistema** (primera vez, sin Jackpot previo): se siembra con 1,000 FRJ directamente del tesoro.

Esto garantiza que **siempre haya un Jackpot activo**, sin importar cuándo se ganó el anterior. Nunca verás el Jackpot en cero.

## Ejemplos

### Ejemplo 1 — Jackpot pequeño, día entre semana

- Jackpot actual: **5,000 FRJ**
- Estás en sala Principiantes con 8 jugadores humanos (cumple el mínimo de 5).
- El naipes #5 canta "La Sirena"... ¡y completas Premio 1!
- **Tu premio**: 5,000 × 0.90 = **4,500 FRJ**
- **Con VIP Axolite**: 4,500 × 1.05 = **4,725 FRJ**
- Nueva semilla del Jackpot: 500 FRJ → el tesoro completa a **1,000 FRJ**

Con 4,500 FRJ puedes comprar 7 Sobrecitos de Pureza (60 AXF + 800 FRJ cada uno en FRJ), o 450 Algae Pellets, o financiar semanas de juego intensivo.

### Ejemplo 2 — Jackpot grande, fin de semana pico

- Jackpot actual: **50,000 FRJ**
- Estás en sala Campeones con 20 jugadores humanos.
- El naipes #4 canta "El Sol" ¡y tu tabla se ilumina! Premio 1 completado.
- **Tu premio**: 50,000 × 0.90 = **45,000 FRJ**
- **Con VIP Axolite**: **47,250 FRJ**
- Nueva semilla: 5,000 FRJ (supera el mínimo de 1,000, no necesita inyección).

Con 45,000 FRJ puedes comprar **3 Webitos Astrales**, o más de **2,250 Algae Pellets**, o financiar **meses enteros** de juego sin preocuparte por los FRJ. Es un premio que te cambia la experiencia de juego por completo.

### Ejemplo 3 — Múltiples ganadores

- Jackpot actual: **30,000 FRJ**
- En el naipes #5, TRES jugadores completan Premio 1 simultáneamente (todos cumplen las condiciones).
- **Premio a repartir**: 30,000 × 0.90 = 27,000 FRJ
- **Cada ganador recibe**: 27,000 ÷ 3 = **9,000 FRJ**
- Con VIP Axolite: 9,000 × 1.05 = **9,450 FRJ** cada uno
- Nueva semilla: 3,000 FRJ (supera el mínimo).

## Seguimiento en la Interfaz

El Jackpot está siempre presente en el lobby multijugador:

- 📊 **Monto actual** visible para todos en el lobby principal.
- 📋 **Panel de Jackpot** que muestra ganadores recientes, montos ganados y fecha.
- 🔄 **Actualización en tiempo real**: el monto sube automáticamente conforme las partidas terminan.
- 🌐 **Notificación global**: cuando alguien gana, TODOS los jugadores conectados reciben una alerta. Es un momento de celebración comunitaria — aunque no hayas ganado tú, sabes que acabas de presenciar algo legendario.

## Consejos (¡No persigas el Jackpot!)

Seamos honestos: el Jackpot es increíblemente raro. No deberías jugar diferente intentando ganarlo. Aquí van consejos realistas:

- 🚫 **No cambies tu estrategia** por el Jackpot. La probabilidad es tan baja que intentar forzarlo solo te hará perder FRJ.
- ✅ **Juega multijugador por los premios regulares** — Premio 1 y Premio 2 son consistentes y pagan bien por sí solos.
- ✅ **Piensa en el Jackpot como un boleto de lotería gratuito** que recibes con cada partida multijugador. No cuesta nada extra, y algún día... quién sabe.
- ✅ **El +5% de VIP Axolite** es un bonus agradable, pero no compres VIP solo por esto. El valor real de VIP está en las tasas de staking, los Sobrecitos platino, y el 3% de cashback diario.
- ✅ **El ingreso real** viene del juego consistente: Premio 1 y Premio 2 frecuentes, staking de Axolotitos, y ventas en el mercado P2P.
- 🎉 **Si ALGÚN DÍA ganas el Jackpot...** ¡felicidades! Has vencido probabilidades astronómicas. Eres leyenda. Disfruta tus FRJ, cuéntaselo a la comunidad, y presume tu hazaña. Momentos como ese son los que hacen grande a Axolotto.

---



### 23-salas-y-multijugador
> `conceptos/23-salas-y-multijugador.md`

---
tags: [conceptos, multijugador]
description: "Salas multijugador en detalle — lobby, Gritón, premios, juego automático | Multiplayer rooms in detail — lobby, Gritón, prizes, auto-play"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Salas y Multijugador

El multijugador es el corazón competitivo de Axolotto. No es un modo extra ni un afterthought — es donde el juego cobra vida, donde las estrategias chocan, y donde los premios de verdad se ganan. Aquí va absolutamente todo lo que necesitas saber sobre las salas, desde el lobby hasta el settlement final.

---

## Tipos de Sala

Axolotto tiene dos grandes categorías de salas multijugador: las oficiales (manejadas por el sistema) y las de anfitriones (creadas y administradas por jugadores como tú).

### Salas Oficiales

Estas salas siempre están abiertas, siempre tienen tráfico, y son el punto de entrada natural para cualquier jugador.

| Sala | Entrada (buy-in) | Jugadores máx | Dificultad |
|------|-------------------|---------------|------------|
| **Charco de Novatos** | 10 FRJ | 30 | Casual — ideal para aprender, probar Tablas nuevas, o jugar sin presión |
| **Fosa del Campeón** | 50 FRJ | 30 | Competitivo — donde los jugadores serios van a demostrar sus stats y estrategias |

**Características de las salas oficiales:**
- El Gritón es controlado por el servidor, con velocidad fija (modo normal, 1.0×)
- Sin comisión de anfitrión — todo el pozo va a los jugadores (menos el 5% de tesorería y 5% de Jackpot)
- Bots automáticos rellenan la sala si hay menos de 4 Tablas humanas
- Abiertas 24/7, sin contraseña, visibles para todos

### Salas de Anfitriones (Player-Hosted Rooms)

¿Quieres control total? Crea tu propia sala. Las salas de anfitriones son el espacio donde la comunidad construye sus propias reglas, torneos privados, y experiencias personalizadas.

**Parámetros configurables por el anfitrión:**

| Parámetro | Opciones | Notas |
|-----------|----------|-------|
| **Buy-in** | 10 – 1,000 FRJ | El anfitrión elige la entrada. A mayor buy-in, mayor el pozo... y mayor el riesgo |
| **Jugadores** | 2 – 8 | Salas más íntimas, más estratégicas. Sin bots |
| **Velocidad** | Normal (1.0×) · Rápido (0.6×) · Turbo (0.3×) | Afecta el delay entre cartas del Gritón. Turbo es pura adrenalina |
| **Visibilidad** | Pública · Amigos · Privada (contraseña) | Control total sobre quién entra |
| **Patrones ganadores** | Configurables | El anfitrión decide qué patrones aplican para Premio 1 en su sala |

**Comisión del anfitrión:** el creador de la sala recibe el **5% del pozo total** de cada partida. Esto significa que hostear salas populares es un negocio legítimo dentro de Axolotto. Un anfitrión con una sala de 8 jugadores a 1,000 FRJ cada uno está moviendo 8,000 FRJ por partida y ganando 400 FRJ solo en comisión.

> 🏠 **Tip de anfitrión:** Las salas rápidas (rápido o turbo) generan más partidas por hora. Aunque el buy-in suela ser más bajo, el volumen compensa. Una sala turbo de 50 FRJ con 8 jugadores puede generar más comisiones por hora que una sala normal de 200 FRJ.

---

## La Cuevita como Host

Cada Axolotito tiene su Cuevita — su guarida personal en Xochimilco. Y cada Cuevita puede hostear partidas.

**Calidad de decoración = visibilidad en el lobby.** Entre más decorada esté tu Cuevita (más objetos, mejor rareza, expansiones completadas), más arriba aparece tu sala en el listado del lobby. Esto no es cosmético — es posicionamiento estratégico. Una Cuevita premium atrae más jugadores, lo que genera más comisiones, lo que paga la decoración.

**Beneficios de hostear desde tu Cuevita:**
- Tu sala muestra el nombre y la imagen de tu Axolotito
- Los jugadores pueden visitar tu Cuevita desde el lobby (modo espectador)
- Las expansiones de Cuevita desbloquean slots adicionales de sala (máximo 3 salas simultáneas por Cuevita)
- Decoraciones raras dan un borde especial a tu listing en el lobby

---

## Flujo de Registro (Cómo Entrar a una Sala)

Entrar a una sala multijugador no es solo darle click a un botón. Hay un proceso de registro que protege tu economía y prepara a tu Axolotito para la sesión.

### Paso a Paso del Registro

1. **Selecciona tu Axolotito** — es quien jugará por ti. Sus stats importan: OJO para marcar, SUERTE para premios y salvaciones, SAL para posición en el mazo.

2. **Elige de 1 a 3 Tablas** — puedes registrar hasta 3 Tablas simultáneas en una misma sala. Cada Tabla juega de forma independiente (como si fueran 3 "cartones" separados). Más Tablas = más chances de ganar, pero también más costo.

3. **El presupuesto (FRJ) se mueve a un escrow en tu Axolotito** — al registrarte, los FRJ que vas a usar no se descuentan inmediatamente, pero se apartan en un escrow ligado a tu Axolotito. Esto garantiza que siempre tengas fondos para cubrir tus partidas.

4. **Presupuesto mínimo** = `fee_per_board × number_of_boards`. Si registras 3 Tablas en Fosa del Campeón (50 FRJ c/u), necesitas mínimo 150 FRJ en escrow.

5. **Configura tus límites de riesgo:**
   - **Stop-loss:** pérdida máxima que toleras. Cuando tu balance de escrow cae a este nivel, tu Axolotito deja de reinscribirse automáticamente. Ejemplo: entras con 300 FRJ, pones stop-loss en 100 FRJ. Si pierdes 200 FRJ, te retiras.
   - **Take-profit:** ganancia objetivo. Cuando tu balance de escrow alcanza este nivel, tu Axolotito deja de reinscribirse y aseguras las ganancias. Ejemplo: entras con 300 FRJ, pones take-profit en 600 FRJ. Si duplicas, te retiras con ganancia.

6. **Límites del sistema:**
   - Máximo **1 registro por usuario** por tipo de sala (no puedes estar en dos Charco de Novatos al mismo tiempo)
   - Máximo **1 registro por wallet address** por tipo de sala (anti-multicuentas)
   - Máximo **5 Tablas totales** entre todas tus inscripciones activas
   - Puedes estar en una sala oficial Y una sala de anfitrión simultáneamente (son tipos distintos)

---

## Matchmaking: Cómo Arrancan las Partidas

El sistema de matchmaking de Axolotto corre en un loop de backend cada **10 segundos**, evaluando todas las salas activas. Su objetivo es simple: arrancar partidas lo más rápido posible sin sacrificar la calidad del emparejamiento.

### Tiempos de Espera por Cantidad de Tablas

| Tablas Registradas | Tiempo de Espera | Descripción |
|---------------------|------------------|-------------|
| **30+** | **Instantáneo** | Sala llena. La partida arranca inmediatamente |
| **21 – 29** | 15 segundos | Alta demanda. Espera mínima para captar algún rezagado |
| **11 – 20** | 20 segundos | Buen tamaño. Se da un respiro para llegar a mejor match |
| **6 – 10** | 25 segundos | Sala mediana. Tiempo razonable para atraer más jugadores |
| **3 – 5** | 35 segundos | Sala pequeña. Un poco más de paciencia |
| **1 – 2** | 60 segundos | Sala mínima. Espera máxima para evitar que juegues solo |

### Regla de Bots

Si al cumplirse el tiempo de espera hay **menos de 4 Tablas humanas** registradas, el sistema rellena la sala con **bots** hasta alcanzar un mínimo de 4 participantes. Esto garantiza que nunca juegues completamente solo y que siempre haya un pozo razonable en juego.

Los bots tienen stats aleatorias balanceadas — no son regalos, pero tampoco son imbatibles. Están diseñados para dar una experiencia justa mientras llegan más humanos.

> 🎯 **Nota importante:** Las salas de anfitriones NUNCA usan bots. Si no se llena el cupo mínimo de humanos, la sala simplemente espera. Parte del arte de ser anfitrión es saber cuándo abrir sala para garantizar que se llene.

---

## Flujo de la Partida

Una vez que el matchmaking dispara el inicio, esto es lo que pasa en orden:

### 1. Cobro de Entrada

La entrada (buy-in) se descuenta del escrow de cada Axolotito registrado. Si eres **VIP Axolite**, recibes un **15% de descuento** sobre el buy-in. Este descuento es automático y aplica tanto en salas oficiales como en salas de anfitriones.

### 2. Deducción de Energía

Cada partida consume energía de tu Axolotito:

- **Costo base:** 10 de energía por partida
- **Costo extra por salinidad:** `round(SAL × 0.2)` adicional
- **Rango total:** 10 a 30 de energía por partida

Un Axolotito con SAL baja (0-10) paga 10-12 de energía por partida. Uno con SAL alta (80-100) paga 26-30. Mantener la salinidad baja no solo mejora tu posición en el mazo — también te deja jugar más partidas por sesión.

### 3. Decaimiento de Energía Máxima

Además del costo por partida, tu **energía máxima** decae en **3 puntos por partida**. Esto simula el cansancio acumulado de tu Axolotito. Después de varias partidas seguidas, tu capacidad total de energía se reduce, obligándote eventualmente a descansar.

### 4. El Gritón Canta

El mazo de 54 cartas se baraja con aleatoriedad criptográfica (`SystemRandom`). El Gritón empieza a anunciar cartas una por una. La velocidad entre cartas depende del tipo de sala:

| Tipo de Sala | Delay entre Cartas | Sensación |
|--------------|-------------------|-----------|
| **Oficial** | Normal (fijo) | Ritmo clásico de Lotería |
| **Anfitrión Normal** | ~3-4 segundos | Tranquilo, social |
| **Anfitrión Rápido (0.6×)** | ~2 segundos | Ágil, mantiene la atención |
| **Anfitrión Turbo (0.3×)** | ~1 segundo | Frenético, pura adrenalina |

### 5. Dos Pozos de Premios por Partida

Cada partida multijugador tiene **dos pozos de premios independientes**, más las contribuciones automáticas:

| Destino | Porcentaje del Pozo | Notas |
|---------|---------------------|-------|
| **Tesorería (casa)** | 5% | Fee del sistema, mantiene los servidores |
| **Jackpot** | 5% | Se acumula en el pozo global |
| **Comisión de anfitrión** | 5% | Solo en salas de anfitriones. En oficiales es 0% |
| **Premio 1** | 35% (30% con host) | Primer patrón completado |
| **Premio 2** | 55% | Tabla llena — ¡Lotería! |

---

## Distribución de Premios

### Premio 1 — El Primer Patrón

**Condición:** ser la primera Tabla en completar **cualquiera de los patrones ganadores configurados** para esa sala.

En salas oficiales, los patrones incluyen: línea horizontal, línea vertical, línea diagonal, las 4 esquinas, y cuadrito central (2×2). En salas de anfitriones, el host puede elegir exactamente qué patrones aplican — puede ser tan restrictivo ("solo diagonal") o tan generoso ("todos los patrones clásicos") como quiera.

**Reparto:** si múltiples Tablas completan el mismo patrón ganador en la misma carta exacta, el pozo de Premio 1 se divide **en partes iguales** entre todas ellas. Si una Tabla completa un patrón en la carta 12 y otra en la carta 15, gana la primera.

### Premio 2 — ¡Lotería!

**Condición:** ser la primera Tabla en llenar **las 16 celdas** (tabla completa). Esto es la Lotería clásica, el grito de "¡Buenas!" que todo jugador sueña con dar.

El pozo de Premio 2 es siempre el **55%** del pozo total, sin importar si hay anfitrión o no. Es el premio gordo de cada partida.

**¿Puede el mismo jugador ganar ambos premios?** ¡Sí! La Regla del Doble Ganador lo permite. Si completas un patrón ganador primero (Premio 1) y además eres el primero en llenar tu tabla completa (Premio 2), te llevas ambos pozos. Es raro, pero cuando pasa... la sala entera lo celebra.

### Bonus de Suerte

Todos los premios (Premio 1, Premio 2, y Jackpot) reciben un **bonus por SUERTE (Luck):**

```
tu_share_final = tu_share_base × (1 + axo_luck / 1000)
```

Un Axolotito con 100 de SUERTE recibe un 10% extra sobre su parte del premio. Uno con 200 de SUERTE recibe 20% extra. La suerte no te hace ganar más seguido — pero cuando ganas, ganas más.

---

## El Jackpot en Multijugador

El Jackpot es el pozo global acumulado que crece con cada partida multijugador. Para detalles completos, consulta [[22-jackpot]], pero aquí va el resumen desde la perspectiva de las salas:

### Requisitos para ser Elegible

- **Mínimo 5 Tablas humanas** registradas en la sala
- **Mínimo 2 wallets distintas** entre los participantes (anti-sybil: evita que una sola persona con múltiples cuentas manipule el sistema)

### Gatillo del Jackpot

El Jackpot se activa únicamente cuando **Premio 1 se gana en las cartas 4, 5, o 6**. Es decir, alguien completa un patrón ganador extremadamente temprano en la partida, cuando apenas han salido las primeras cartas del Gritón. Esto requiere una combinación brutal de:
- Una Tabla perfectamente optimizada para el patrón
- OJO altísimo para no fallar marcas
- SUERTE para que tus cartas salgan temprano
- SAL baja para que no te empujen al final del mazo

### Pago del Jackpot

- **90%** del pozo acumulado se entrega al ganador (o se divide entre ganadores simultáneos)
- **10%** se re-siembra para la siguiente ronda
- Si después de re-sembrar el Jackpot queda en **menos de 1,000 FRJ**, la tesorería del juego completa la diferencia automáticamente
- Los jugadores **VIP Axolite** reciben un **+5% de bonus** sobre sus ganancias de Jackpot

> 🌟 Ganar el Jackpot es el logro más épico de Axolotto. No solo por el premio — sino porque requiere que absolutamente todo salga perfecto: tu Tabla, tus stats, y el momento justo de suerte.

---

## Auto-Reinscripción: Tu Axolotito No Duerme

Una de las mecánicas más poderosas del multijugador: no necesitas estar pegado a la pantalla. Una vez registrado, tu Axolotito puede seguir jugando partida tras partida automáticamente.

### Condiciones para Reinscribirse

Después de cada partida, el sistema evalúa si tu Axolotito debe reinscribirse automáticamente a la siguiente. Las condiciones son:

1. **No ha alcanzado el stop-loss** — tu balance de escrow sigue por encima del límite de pérdida que configuraste
2. **No ha alcanzado el take-profit** — tu balance de escrow no ha llegado al objetivo de ganancia
3. **Energía actual >= 10** — tiene suficiente energía para al menos una partida más
4. **Tiene fondos para la entrada** — el escrow cubre el buy-in de la siguiente partida
5. **No ha sido retirado manualmente** — no presionaste "Dejar de Jugar"

Si todas las condiciones se cumplen, tu Axolotito se reinscribe automáticamente y sigue jugando. Puedes irte a dormir, trabajar, o lo que sea — tu Axolotito sigue ahí, marcando cartas, ganando premios.

### Cómo Salir: Dejar de Jugar

Cuando quieras detenerte, haces click en el botón **"Dejar de Jugar"**. Esto NO saca a tu Axolotito inmediatamente — termina la partida actual y luego se detiene. Es una salida elegante, no un rage-quit.

### Settlement (Liquidación Final)

Cuando tu Axolotito termina su sesión (ya sea por stop-loss, take-profit, energía agotada, o retiro manual), entra en Settlement:

1. **Balance del escrow se devuelve a tu wallet** — los FRJ que no gastaste vuelven a ti
2. **Puntos de lealtad otorgados:**
   - **5 puntos base** por participar en la sesión
   - **+1 punto extra por cada 10 FRJ de ganancia neta**
   - Ejemplo: terminaste con 150 FRJ de ganancia neta = 5 + 15 = 20 puntos de lealtad
3. **Tu Axolotito pasa a estado SLEEPING** — necesita descansar. Durante el sueño, recupera energía y reduce salinidad. Consulta [[02-axolotitos]] para el sistema de sueño completo.

---

## El Gritón (El Cantador)

El Gritón es el alma de cada partida. Es la voz (generada por el sistema) que anuncia las cartas una por una, marcando el ritmo del juego.

### En Salas Oficiales

- Controlado completamente por el servidor
- Velocidad fija (modo normal)
- Sin intervención humana posible
- La misma voz, el mismo ritmo, para todos

### En Salas de Anfitriones

El anfitrión configura la velocidad del Gritón al crear la sala:

| Modo | Multiplicador | Sensación |
|------|---------------|-----------|
| **Normal** | 1.0× | Clásico. ~3-4 segundos entre cartas. Ideal para salas sociales |
| **Rápido** | 0.6× | ~2 segundos. Buen ritmo sin ser abrumador |
| **Turbo** | 0.3× | ~1 segundo. Para los que quieren acción pura |

### Modo Manual (Avanzado)

En salas de anfitriones, existe un modo manual donde el host puede:
- Repetir la última carta anunciada (para dar tiempo extra)
- Configurar el comportamiento en caso de empate (primer patrón simultáneo)
- Pausar brevemente entre cartas para generar tensión

El modo manual es para anfitriones avanzados que quieren crear una experiencia más teatral, estilo streamer.

---

## Reputación de Anfitrión

Ser anfitrión no solo paga en FRJ — también construye tu reputación en la comunidad.

### Sistema de Reputación

| Acción | Reputación Ganada |
|--------|-------------------|
| Hostear una partida completada | +1 |
| Sala llena al 80%+ de capacidad | +5 extra (total +6 por esa partida) |

**Ejemplo práctico:** tienes una sala de 8 jugadores. Si 7 u 8 se llenan (80%+), ganas +6 de reputación por partida. En una hora de sala turbo llena, puedes fácilmente sumar +60 de reputación.

### Beneficios de Alta Reputación

- **Mejor visibilidad en el lobby:** las salas de anfitriones con alta reputación aparecen más arriba en los listados
- **Insignia de anfitrión:** distintivos visuales que muestran tu nivel como host (Bronce, Plata, Oro, Axolite)
- **Confianza de la comunidad:** los jugadores prefieren salas de hosts con buena reputación — saben que la experiencia será justa y divertida
- **Mayor tráfico = más comisiones:** es un círculo virtuoso

---

## Estrategia en Multijugador

Unos consejos rápidos para dominar las salas:

### Para Jugadores

- **Registra 3 Tablas siempre que puedas** — triplicas tus chances de ganar Premio 1. El costo extra vale cada FRJ.
- **Configura stop-loss y take-profit con cabeza** — un stop-loss muy ajustado te saca antes de tiempo. Un take-profit muy ambicioso nunca se alcanza. Encuentra tu equilibrio.
- **La SAL importa más en multijugador** — en CPU puedes compensar SAL baja con volumen. En multi, donde todos comparten el mismo Gritón, una SAL baja es ventaja competitiva real.
- **Elige la velocidad de sala que se adapte a tu estilo** — si tienes buen OJO pero malos reflejos, juega en normal. Si confías en tu Tabla y quieres volumen, ve a turbo.
- **La auto-reinscripción es tu amiga** — configura tus límites, regístrate, y deja que tu Axolotito trabaje. Revisa cada hora para ajustar.

### Para Anfitriones

- **Abre sala en horas pico** — menos competencia por visibilidad, más jugadores buscando partida
- **Turbo con buy-in bajo atrae volumen** — muchos jugadores prefieren 10 partidas rápidas de 20 FRJ que una lenta de 200 FRJ
- **Decora tu Cuevita** — cada objeto decorativo es una inversión en visibilidad de lobby. Se paga solo con comisiones
- **Sé consistente** — un anfitrión que abre sala regularmente construye comunidad. Los jugadores regresan a salas conocidas
- **Elige patrones interesantes** — si solo aceptas diagonal como Premio 1, las partidas serán más largas y tensas. Si aceptas todos los patrones, serán más rápidas y caóticas. Encuentra tu nicho.

---



### 24-saladito-y-modos-especiales
> `conceptos/24-saladito-y-modos-especiales.md`

# 24 — Saladito y Modos Especiales 🧂🎮🏆

> **Quick Reference** — Saladito inverts Lotería rules (fewest marks wins), Manual PvP makes clicking a real-time skill game, Copa del Cenote brings complex-pattern high-stakes rooms, and seasonal events keep the calendar fresh. See [[08-modos-de-juego]] for standard modes, [[23-salas-y-multijugador]] for room mechanics, and [[06-como-jugar-loteria]] for basic gameplay.

---



### 25-f2p-guia-gratis
> `conceptos/25-f2p-guia-gratis.md`

# 25 — Guía Free-to-Play · Free-to-Play Guide

> **How to enjoy Axolotto without spending a single peso, satoshi, or dollar.**

---

## Quick Reference · Referencia Rápida

| Concept | Detail |
|---------|--------|
| Can I play 100% free? | **Yes.** FRJ unlocks everything. |
| First free rewards | Tutorial axo, starting FRJ, free board, daily Lunar Cycle (50–130 FRJ/day), Spectator (10 FRJ/day) |
| Best early grind | CPU Rookies — 25 FRJ entry, 85 FRJ win (60 net profit) |
| Week 1 target | ~500–800 FRJ saved + Bronce capsule + some cards |
| Month 1 target | Axo Lv 10–15, Cave 3–4, 3+ boards |
| Year 1 target | All cave levels, competitive multiplayer, Astral axolotito |
| F2P cannot get directly | VIP membership, foil booster, instant cave acceleration (all tradeable or earnable with patience) |
| Core mindset | **Skill > wallet. Patience is your currency.** |

---

## 1. La Promesa F2P · The F2P Promise

**Yes, you CAN play Axolotto completely free.** This is not a "free trial" — it is a fully viable path to the endgame.

- Everything in the game is accessible with FRJ, the currency you **earn by playing.**
- AXF (premium currency) is convenient but **never required** to access any game mode, item, or reward.
- The F2P path is slower — but it is also the path where **skill, strategy, and consistency** determine your progress, not your wallet.
- Many of the top-ranked players on the leaderboard are F2P. They did not buy their way up — they outplayed the competition.

> **Skill > wallet. Always.** A well-built board and a leveled axolotito beat a credit card every time.

---

## 2. Lo Que Recibes Gratis · What You Get for Free

| Reward | How | Value |
|--------|-----|-------|
| **Tutorial Axolotito** | Complete the tutorial | Balanced-stats companion for life |
| **Starting FRJ** | Tutorial completion | Enough for several CPU Rookies runs |
| **Starting Board** | Tutorial completion | Ready to play immediately |
| **Daily Lunar Cycle** | Login each day · [[21-ciclo-lunar-y-recompensas]] | 50–130 FRJ/day |
| **Spectator Mode** | Watch live games · [[24-saladito-y-modos-especiales]] | 10 FRJ + 10 fragments/day |
| **Cave Level 1** | Unlocked by default | Free permanent cave tier |
| **Webito (from cave)** | Excavate naturally without acceleration | Egg NFT at no cost |

The game gives you **everything you need to start** — the rest is earned through play.

---

## 3. Tu Primera Semana · Your First Week (F2P Roadmap)

### Day 1 — Welcome to the Cenote
- Complete the **tutorial** — this is non-negotiable and gives you your axolotito, starting FRJ, and first board.
- Play **CPU Rookies** (25 FRJ entry). Winning earns 85 FRJ — that is **60 FRJ net profit.**
- Goal: get comfortable with the game loop and win at least 3–4 games.

### Day 2 — The Daily Habit
- Claim your **daily Lunar Cycle reward** (50 FRJ minimum) · [[21-ciclo-lunar-y-recompensas]].
- Play more CPU Rookies. Stockpile FRJ — do not spend on anything except algae pellets yet.
- Goal: 100+ FRJ in the bank after expenses.

### Day 3 — Streak Building
- Reach your **3-day login streak** — this matters for cave expansion requirements later.
- Continue the Rookies grind. If you have extra FRJ, consider crafting a second board (25–50 FRJ).
- Goal: 200+ FRJ saved.

### Days 4–6 — Snowball
- Daily claims + CPU games every day.
- Start experimenting with board layouts — a well-designed board wins more consistently · [[08-modos-de-juego]].
- If your axo is leveling well, try **one** CPU Champions game to test the waters (100 FRJ entry; only if you have 300+ FRJ banked).
- Goal: 400+ FRJ saved.

### Day 7 — First Milestone!
- Claim your **Bronce capsule + 130 FRJ** — your first full-week reward.
- Take stock: you should have **~500–800 FRJ saved**, some cards from capsules, and an axolotito around level 3–5.
- Celebrate. You earned this.

---

## 4. Cómo Ganar FRJ Sin Gastar · How to Earn FRJ Without Spending

| Method | FRJ Earned | Effort | Consistency |
|--------|-----------|--------|-------------|
| **CPU Rookies wins** | 85 FRJ/win (25 entry = 60 net) | Low | Play anytime |
| **CPU Champions wins** | 400 FRJ/win (100 entry = 300 net) | Medium | Need good board + leveled axo |
| **Daily Lunar rewards** | 50–130 FRJ/day | Zero (just log in) | Every day |
| **Spectator mode** | Up to 10 FRJ/day | Zero (watch games) | Daily cap |
| **Staking (boards + axos)** | 10–200+ FRJ/day | Zero (passive) | Claim regularly · [[20-staking-ingresos-pasivos]] |
| **P2P market sales** | 100–10,000+ FRJ | Medium (list items) | When you have extras |
| **Multiplayer prizes** | 100–1,000+ FRJ | High | Needs competitive axo |

### Strategy: Stack the passive sources.

Daily Lunar (50–130) + Spectator (10) + Staking (10–200+) = **70–340+ FRJ/day without playing a single game.** Add a handful of Rookies wins and you are pulling 200–500 FRJ/day with minimal effort.

> The passive-income engine is the F2P superpower. Build it early. · [[20-staking-ingresos-pasivos]]

---

## 5. Gastos Inteligentes Siendo F2P · Smart F2P Spending

Every FRJ counts. Here is your priority order:

| Priority | Purchase | Cost | Why |
|----------|----------|------|-----|
| **1** | Algae Pellets | 30 FRJ | Your axo must be fed to play. Non-negotiable. |
| **2** | Rookies entry fees | 25 FRJ/game | Your FRJ printer — grind consistent wins |
| **3** | Board creation | 25–50 FRJ | Better boards = more wins = more FRJ |
| **4** | Cave expansion | 500–60,000 FRJ | Permanent upgrades that pay for themselves · [[12-economia-dual]] |
| **5** | Gashapon capsules | 1,500+ FRJ | Treat yourself — cards and surprises |

### Three Things to Avoid (Until You Are Ready)

- **Champions room** — do not touch it until your axo is leveled (10+) and your board is optimized. Losing 100 FRJ hurts.
- **Banco de Algas (FRJ conversion)** — this requires buying AXF first with real money. F2P players should never use this route.
- **Oro capsules (20,000 FRJ)** — that is a fortune. Wait until you have a thriving passive-income engine and a fat bank. This is a month-6+ purchase, not a week-1 fantasy.

---

## 6. Hitos de Progresión F2P · F2P Progression Milestones

| Timeline | Axo Level | Cave Level | Boards | Passive Income | Key Unlock |
|----------|-----------|------------|--------|----------------|------------|
| **Week 1** | 3–5 | 1 | 1–2 | ~50 FRJ/day | Bronce capsule, basic game loop mastered |
| **Month 1** | 10–15 | 3–4 | 3+ | ~70–120 FRJ/day | Champions room viable, first cave expansions |
| **Month 3** | 20+ | 5–6 | 5+ | ~50–150+ FRJ/day | Staking engine running, P2P trading active |
| **Month 6** | 30+ | 7–8 | 8+ | ~100–200+ FRJ/day | Breeding your own axolotitos, regular Champions wins |
| **Year 1** | 40+ | All levels | Optimized | ~200+ FRJ/day | Astral axolotito from cave, competitive multiplayer dominance |

> These are realistic, not aspirational. Consistent daily play — even just 20 minutes — gets you here.

---

## 7. Lo Que F2P NO Puede Obtener Directamente · What F2P CAN'T Get (Without Trading)

This list is short — and everything on it has a workaround:

| Item | Why Locked? | Workaround |
|------|-------------|------------|
| **Webito Astral (direct)** | AXF purchase required | Earn from **Cave Level 7+** or buy on P2P market |
| **VIP membership** | AXF required | Cannot be earned (cosmetic/prestige only — no gameplay advantage) |
| **Foil booster** | AXF required | Get foil cards from **Gashapon capsules** and **P2P market** instead |
| **Instant cave acceleration** | AXF required | Just be patient — natural excavation works fine |

**None of these lock you out of any game mode, reward, or competitive advantage.** The VIP membership is purely prestige/cosmetic. Foil cards are available through free methods. The Astral Webito is earnable. Cave acceleration is optional — time does the same job for free.

---

## 8. Mentalidad F2P · The F2P Mindset

**You are not a second-class player.** The game was designed with you in mind.

- **Patience is your currency.** Everything can be earned with time. The paying player buys speed; you earn depth. By the time you reach endgame, you will understand every system, every strategy, and every edge case — because you lived it.
- **Skill matters MORE than money.** A skilled F2P player with a well-built board will beat a paying novice every single game. The lottery mechanics reward probability management, not wallet size.
- **This is not a pay-to-win casino.** It is a skill contest with optional convenience purchases. The core loop — build boards, level axolotitos, win games — is completely walled off from the premium currency.
- **The systems support you.** The Lunar Cycle rewards daily logins. Spectator Mode pays you to watch and learn. Cave eggs give you free NFT companions. Staking turns your collection into passive income. These were all built so F2P players thrive.
- **The community respects the grind.** An F2P player with an Astral axolotito earned through a year of cave excavation commands more respect than someone who swiped a card. You did not buy it — you *earned* it.

---

## See Also · Véase También

- [[12-economia-dual]] — How AXF and FRJ interact, and why F2P thrives on FRJ
- [[21-ciclo-lunar-y-recompensas]] — Maximize your daily login rewards
- [[20-staking-ingresos-pasivos]] — Build your passive FRJ engine
- [[08-modos-de-juego]] — Master every game mode without spending
- [[24-saladito-y-modos-especiales]] — Spectator mode and special events for free rewards
- [[00-INDEX]] — Full wiki index

---

*Last updated: 2026-06-09 — Corresponds to game version with dual-currency economy, Lunar Cycle, Spectator Mode, and full cave progression.*


### 26-consejos-y-estrategias
> `conceptos/26-consejos-y-estrategias.md`

---
tags: [conceptos, estrategia, guia-avanzada]
description: "Consejos y estrategias avanzadas de Axolotto — sabiduria colectiva de jugadores experimentados | Advanced Axolotto tips and strategies — collective wisdom from experienced players"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Consejos y Estrategias — Sabiduria de Veterano

Esta es la pagina que todo jugador nuevo deberia leer. No es teoria — es la coleccion de cosas que los veteranos aprendieron a golpes, errores, y partidas perdidas. Aqui va TODO lo que desearia haber sabido cuando empece en Axolotto. Si vienes de [[25-f2p-guia-gratis]], esto es el siguiente nivel. Si ya llevas semanas jugando, probablemente encuentres algo que no sabias.

**Wikilinks:** [[02-axolotitos]] · [[06-como-jugar-loteria]] · [[07-patrones-ganadores]] · [[10-tablas]] · [[12-economia-dual]] · [[14-capsulas-gashapon]] · [[20-staking-ingresos-pasivos]] · [[25-f2p-guia-gratis]] · [[00-INDEX]]

---

## 1. Construccion de Tablas — Donde Todo Empieza

Tu Tabla es tu arma principal. Una buena Tabla te gana partidas. Una mala Tabla te cuesta FRJ. Construir bien es la diferencia entre un jugador que sobrevive y uno que prospera.

### La Jerarquia de Celdas

No todas las celdas de tu Tabla 4x4 valen lo mismo. Algunas participan en mas patrones ganadores que otras. Esta es la jerarquia, de mas valiosa a menos:

| Prioridad | Celdas | Patrones que cubren |
|-----------|--------|---------------------|
| **Oro** | 5, 6, 9, 10 (centro 2x2) | Lineas horizontales, verticales, diagonales, cuadritos, pocito, cruz |
| **Plata** | 0, 3, 12, 15 (esquinas) | Esquinas, lineas horizontales, verticales, diagonales |
| **Bronce** | 1, 2, 4, 7, 8, 11, 13, 14 (bordes medios) | Solo lineas horizontales y verticales |

**Regla de oro:** tus MEJORES cartas (mayor rareza) van en el centro. Tus segundas mejores, en las esquinas. El resto, en los bordes. Una carta legendaria en la celda 5 participa en mas patrones que una carta legendaria en la celda 1.

### Estrategia de Cobertura — Rookies

Si estas empezando y juegas en Charco de Novatos, tu prioridad es simple: **cobertura de lineas**. Asegurate de que:

- Cada fila tenga al menos 1 carta fuerte (rara o mejor)
- Cada columna tenga al menos 1 carta fuerte
- Cada diagonal tenga al menos 1 carta fuerte

Esto maximiza tus chances de completar UN patron — lo unico que necesitas para ganar en Rookies. No te obsesiones con cubrir cuadritos o pocito todavia. Una cosa a la vez.

**Test rapido:** Mira tu Tabla y cuenta cuantas lineas (filas, columnas, diagonales) tienen al menos 2 cartas raras o mejor. Si el numero es menor a 6, tu Tabla necesita trabajo.

### Estrategia de Cobertura — Champions

En Fosa del Campeon, los patrones ganadores incluyen cuadritos (2x2), pocito (anillo exterior), y cruz. Tu Tabla necesita cubrirlos TODOS:

- **Cuadritos:** las celdas del centro (5,6,9,10) son el corazon de los 4 cuadritos posibles
- **Pocito (anillo):** las 12 celdas del borde exterior deben tener cartas decentes. No necesitas leyendas — pero si todas son comunes, el pocito nunca sale
- **Cruz:** fila 1 + columna 1. La celda 0 (esquina) es la unica que esta en AMBAS

**Consejo de veterano:** arma 2 Tablas distintas. Una optimizada para lineas (Rookies, partidas rapidas) y otra optimizada para cobertura total (Champions, torneos). No intentes que una sola Tabla haga todo — se queda a medias en ambos.

### No Te Cases con una Tabla

Tu Tabla no es para siempre. A medida que consigas mejores cartas (capsulas, P2P, premios), actualizala. Una Tabla que era buena hace 2 semanas probablemente ya es mediocre hoy. Los jugadores que no actualizan sus Tablas son los que se preguntan por que dejaron de ganar.

---

## 2. Prioridades de Build de Axolotito

Tus stats importan. Mucho. Y no todos los stats importan para lo mismo. Aqui va la guia definitiva de prioridades segun tu estilo de juego.

### Para Juego General (Tu Main)

**FOCO > SUERTE > AGUANTE >>> SAL**

El Foco (OJO) es el rey. Determina que tan rapido y preciso marcas las cartas. Un OJO alto significa menos cartas perdidas, menos slips, mas patrones completados. Es el stat que gana partidas.

La Suerte (SUERTE) es la reina. No te hace ganar mas seguido, pero cuando ganas, ganas MAS. El bonus es `1 + SUERTE/1000`. Con 200 de SUERTE, tus premios son 20% mas grandes. En el largo plazo, eso es una fortuna.

El Aguante determina cuanta energia tienes. Mas energia = mas partidas por sesion. Simple.

La Salinidad (SAL) es tu enemiga. Mantenla lo mas baja posible. Una SAL alta te empuja al final del mazo en multijugador, te hace pagar mas energia por partida, y aumenta tu chance de slip. **Nunca subas SAL voluntariamente.**

### Para Grindeo de CPU

**Naturaleza: Hiperactivo.** Duerme mas rapido = mas partidas por hora = mas FRJ por dia. En CPU no importa tanto la precision porque el ritmo es mas lento, asi que prioriza volumen sobre calidad.

Build recomendado: FOCO medio (40-60), SUERTE media (30-50), AGUANTE alto (60+), SAL minima. El objetivo es jugar muchas partidas seguidas sin dormir.

### Para Multijugador

**Naturaleza: Metodico o Suertudo.**

- **Metodico:** consistencia en el marcado. En multi, donde la velocidad del Griton es implacable, un Metodico no se salta cartas. Ganas mas Premios 1.
- **Suertudo:** premios mas grandes. En multi los pozos son mas gordos (mas jugadores), asi que el bonus de SUERTE multiplica cantidades mayores. Un Suertudo en Fosa del Campeon puede ganar 20-30% mas FRJ por premio.

Build recomendado: FOCO alto (80+), SUERTE media-alta (60-80), AGUANTE medio (40-50), SAL lo mas bajo posible (<20 idealmente). En multi, un slip puede costarte el premio — la SAL baja es NON-NEGOTIABLE.

### Gestion de Energia

- **Alimenta cuando la energia baje de 30.** No esperes a llegar a 0. La comida es barata comparada con el FRJ que pierdes por no poder jugar.
- **Duerme cuando la energia actual baje del 85% de tu energia maxima.** La energia maxima decae con cada partida. Dormir la resetea a tu stat de PILA. Si dejas que la energia maxima decaiga demasiado (digamos, a 20), cada ciclo de sueno te da solo 20 de energia — practicamente inutil.
- **No dejes que `energy_max_current` decaiga a menos de 50.** Llegar a 10 de energia maxima significa 1 partida por ciclo de sueno. Es un hoyo del que cuesta mucho salir.

### Antes de Criar, Sube de Nivel a tu Padrino

El padrino (el Axolotito que usas para criar) transmite sus stats al huevo. Un padrino nivel 30 con stats altas produce un huevo significativamente mejor que un padrino nivel 5 con stats mediocres. Subir de nivel a tu main ANTES de criar es la inversion mas rentable del juego. Cada nivel del padrino mejora el piso de stats del huevo.

---

## 3. Economia — Como No Quedarte Pobre

El FRJ y el AXF no son iguales. Tratarlos como si lo fueran es el error economico mas comun.

### La Regla de los 100 FRJ

**Nunca gastes tus ultimos 100 FRJ.** Siempre, SIEMPRE, guarda suficiente para:
- La entrada de tu modo de juego principal (10 o 50 FRJ)
- Comida para tu Axolotito (~20-30 FRJ)
- Un colchon de emergencia

Sin FRJ no puedes jugar. Sin jugar no generas mas FRJ. Es la espiral de la muerte economica. Tus ultimos 100 FRJ son sagrados.

### El Banco de Algas es una Trampa (para F2P)

El Banco de Algas te permite cambiar AXF por FRJ. Suena util. NO LO ES para jugadores gratuitos. El AXF es escaso si no pagas — cada AXF que gastas en el banco es un AXF que no usas para comprar una Tabla, expandir tu cueva, o acelerar algo que de verdad importa. El FRJ se genera jugando. El AXF no. No cambies algo que no se regenera por algo que si.

### FRJ es Abundante, AXF es Escaso

Internaliza esto: si eres consistente jugando, el FRJ llega solo. Staking, premios, Ciclo Lunar, ventas en el P2P — hay docenas de fuentes de FRJ. El AXF solo llega si pagas (o ganas torneos grandes, o vendes items muy raros en el mercado). Trata el AXF como el recurso premium que es.

### Mejores Compras, en Orden

1. **Comida** — sin energia no juegas. Sin jugar, no hay ingresos. Es el gasto mas basico y mas importante.
2. **Entradas a partidas** — cada partida es una oportunidad de ganar FRJ, subir de nivel, y progresar. Las entradas se pagan solas.
3. **Tablas** — una buena Tabla es una inversion que se amortiza en premios. No compres 10 Tablas mediocres. Compra 2-3 BUENAS.
4. **Expansion de Cueva** — mas espacios de staking, mas slots de incubacion, mas salas para hostear. Prioridad media.
5. **Capsulas Gashapon** — divertidas, emocionantes... y un lujo. No son prioridad. Compra capsulas con tu EXCEDENTE de FRJ, nunca con tus fondos operativos.
6. **Aceleracion de excavacion** — casi nunca vale la pena. Los huevos gratis por esperar son mejores que gastar AXF en acelerar.

### El VIP se Paga Solo... Si Juegas a Diario

VIP Coral cuesta 400 AXF al mes. Recibes 1,200 FRJ/mes en beneficios directos (Ciclo Lunar mejorado, bonos, descuentos). Si juegas todos los dias, el VIP se autofinancia en FRJ. Si juegas 2-3 veces por semana, quizas no. Haz las cuentas antes de comprarlo.

**Beneficios clave del VIP que generan retorno:**
- 15% descuento en entradas de multijugador
- +5% bonus en premios de Jackpot
- Espacios extra de Tablas y Axolotitos
- Ciclo Lunar acelerado

### Vende Duplicados en el P2P, No los Derritas

Antes de derretir (fundir) una carta duplicada, REVISA su precio en el Mercado P2P. Las cartas foil, first-edition, o de rareza alta pueden valer mucho mas en el mercado que el FRJ que obtienes al derretirlas. Un foil epico puede valer 5,000 FRJ en el P2P... o 200 FRJ si lo derrites. La diferencia es brutal.

---

## 4. Errores Clasicos de Principiante

Errores que TODOS cometemos. Aprende de nuestros moretones.

### Error 1: Jugar Champions CPU con un Axo Nivel 1

**Por que duele:** La entrada cuesta 50 FRJ. Un axo nivel 1 tiene stats bajisimas, tarda en marcar, y se salta cartas. Vas a perder. Y cuando pierdes, pierdes 50 FRJ que podrian haberte dado 5 partidas en Rookies.

**Solucion:** Juega Rookies (10 FRJ) hasta que tu axo tenga nivel 10+ y una Tabla con buena cobertura. Luego prueba Champions.

### Error 2: Gastar Todo en Capsulas Gashapon

**Por que duele:** Abrir 5 capsulas es divertido. Quedarte con 0 FRJ despues NO. Sin FRJ no puedes jugar, y sin jugar no generas mas. Las capsulas son un lujo, no una necesidad.

**Solucion:** Define un "presupuesto de capsulas" — por ejemplo, 20% de tu FRJ total. Si tienes 5,000 FRJ, gastas maximo 1,000 en capsulas. El resto es intocable para jugar y mantener a tu axo.

### Error 3: Nunca Dormir a tu Axolotito

**Por que duele:** Cada partida reduce tu energia maxima en 3 puntos. Despues de 20 partidas sin dormir, tu energia maxima paso de 100 a 40. Despues de 30 partidas, esta en 10. Con 10 de energia maxima, cada ciclo de sueno te da... 10 de energia. Una partida. DUERME A TU AXO.

**Solucion:** Programa el sueno como parte de tu rutina. Juega 10-15 partidas, duerme. O configura la auto-reinscripcion para que tu axo descanse cuando llegue a cierto umbral de energia.

### Error 4: Derretir Cartas Raras Sin Verificar el P2P

**Por que duele:** Derretir una carta foil legendaria te da quiza 500 FRJ. Venderla en el P2P te puede dar 20,000+. Ya lo dijimos, pero merece repetirse: REVISA EL MERCADO antes de derretir.

### Error 5: Ignorar el Ciclo Lunar

**Por que duele:** El Ciclo Lunar te da 530 FRJ gratis por semana SOLO POR ENTRAR al juego. No tienes que jugar. No tienes que ganar. Solo entrar y hacer clic en "Reclamar". Ignorarlo es literalmente tirar FRJ gratis a la basura.

**Solucion:** Entra TODOS los dias, aunque sea 30 segundos. Reclama tu premio diario. Es el habito mas rentable de Axolotto.

### Error 6: No Stakear Tablas y Axos Inactivos

**Por que duele:** Tus Tablas que no estan jugando y tus Axos que no estan activos pueden estar generando FRJ pasivo. Si no los stakeas, estan ahi sentados sin producir nada. Es como tener un terreno y no construir nada en el.

**Solucion:** Despues de cada sesion de juego, revisa tu inventario. Todo lo que no este en uso, al staking. Acostumbrate a cobrar el staking una vez al dia.

### Error 7: Olvidar Cobrar el Staking

**Por que duele:** El FRJ de staking tiene limite de acumulacion. Si no cobras a tiempo, el excedente se PIERDE. Un Axolotito Legendario puede generar 200+ FRJ al dia... que desaparecen si no los reclamas.

**Solucion:** Pon una alarma diaria. O hazlo parte de tu rutina: entrar, reclamar Ciclo Lunar, cobrar staking, jugar. En ese orden.

### Error 8: Perseguir el Jackpot

**Por que duele:** La probabilidad de ganar el Jackpot es aproximadamente 0.01% por partida. Es un evento epico, no una estrategia. Si juegas "para ganar el Jackpot", vas a perder muchisimo FRJ en el camino. Juega para ganar partidas normales. Si el Jackpot llega, que te agarre jugando bien — no jugando desesperado.

**Solucion:** Disfruta el juego. Gana partidas, mejora tu axo, construye tus Tablas. El Jackpot es la cereza del pastel, no el pastel entero.

---

## 5. Guia de Supervivencia en Multijugador

El multijugador es donde el juego se pone serio. Aqui no hay bots que te perdonen — hay jugadores reales con Tablas optimizadas y axos nivel 30+. Vas a necesitar preparacion.

### Antes de Entrar

1. **Tu axo debe ser nivel 10+.** Con menos nivel, tus stats son demasiado bajas para competir. Juega CPU hasta llegar ahi.
2. **Tu Tabla debe tener un CSR (Coverage Success Rate) decente.** Si no sabes que es el CSR, no estas listo para multi. Juega mas CPU.
3. **Empieza en Charco de Novatos (10 FRJ).** Arriesgas poco, aprendes el flujo del multijugador, y ves como juegan otros humanos. La Fosa del Campeon (50 FRJ) es para cuando ya tienes confianza.

### Gestion de Riesgo — Stop-Loss y Take-Profit

Estos dos numeros son lo unico que separa una sesion rentable de una catastrofe:

- **Stop-loss al 50% de tu presupuesto de escrow.** Si entras con 300 FRJ, configuras stop-loss en 150 FRJ. Pierdes la mitad, te retiras. Vives para jugar otro dia.
- **Take-profit al 200% de tu presupuesto de escrow.** Si entras con 300 FRJ, configuras take-profit en 600 FRJ. Duplicas, aseguras ganancias, te vas contento.

**La psicologia del stop-loss:** cuando estas perdiendo, tu instinto dice "una mas, una mas, ya mero recupero". El stop-loss existe para protegerte DE TI MISMO. Configuralo y no lo toques.

**La psicologia del take-profit:** cuando estas ganando, tu instinto dice "esto sigue, esto sigue, puedo ganar mas". Y luego pierdes todo. El take-profit existe para que te vayas con ganancias reales, no con la ilusion de lo que "pudiste haber ganado".

### No Registres Mas Tablas de las que Puedes Costear

Registrar 3 Tablas en Fosa del Campeon cuesta 150 FRJ en escrow SOLO PARA EMPEZAR. Si tu balance total es de 200 FRJ, no registres 3 Tablas. Registra 1. La regla es simple: `escrow_total >= 3 x entrada_por_tabla`. Asi tienes margen para perder un par de partidas sin quedarte fuera.

### El Lobby es Informacion Gratuita

Antes de registrarte, mira el lobby:
- Salas con pocos jugadores arrancan mas rapido (menos competencia por Premio 1)
- Salas con muchos jugadores tienen pozos mas gordos
- Los nombres de los jugadores te dicen nada... pero los niveles de sus axos, si los ves, te dicen mucho
- Salas de anfitriones con buy-ins raros (37 FRJ, 89 FRJ) suelen tener menos trafico = menos competencia

### SAL es tu Enemiga Numero 1 en Multi

En CPU, una SAL de 60 es molesta. En multijugador, una SAL de 60 es un desastre. Te empuja al final del mazo, recibes las cartas mas tarde que los demas, y los patrones se los llevan otros antes que tu. Si tu axo tiene SAL alta, NO JUEGUES MULTI. Baja esa SAL primero (duerme, usa consumibles, mejora tu PILA).

---

## 6. Crianza para el Exito

Criar Axolotitos no es solo coleccionar monitos lindos — es el sistema de progresion a largo plazo mas poderoso del juego. Un buen programa de crianza te da axos con stats que no puedes conseguir de otra forma.

### El Mejor Padrino

Para criar, busca un padrino con:
1. **FOCO alto (80+)** — se transmite al huevo como stat base
2. **SUERTE alta (70+)** — idem
3. **SAL baja (<20 ideal, <30 aceptable)** — la SAL tambien se transmite. No quieres un huevo salado
4. **Nivel alto** — el nivel del padrino eleva el piso de stats del huevo. Un padrino nivel 30 produce huevos consistentemente mejores que uno nivel 10

### La Impronta — Juega CPU Rookies

Durante la fase de impronta (imprinting), necesitas ganar partidas para maximizar el potencial del huevo. Juega CPU Rookies — es el modo mas facil, las partidas son rapidas, y cada victoria cuenta. No te compliques jugando Champions o Multi durante la impronta. No es el momento de presumir — es el momento de asegurar un buen huevo.

### El Padrino Tambien Gana — +150 XP por Tutoria

Cada vez que tu padrino completa una tutoria (cria), gana **+150 XP**. Esto es enorme. Significa que criar no solo te da un huevo — tambien sube de nivel a tu mejor axo. Muchos jugadores de endgame usan la crianza como su metodo principal de leveo para sus mains. Tres tutorias = 450 XP practicamente gratis.

### Maximo 3 Tutorias por Axolotito

Cada axo puede ser padrino maximo 3 veces. Esto significa que tienes 3 oportunidades de transmitir sus stats a la siguiente generacion. Elige sabiamente con quien criar. No desperdicies una tutoria en una cruza mediocre.

### Webito Astral — El Santo Grial de la Crianza

Un Webito Astral garantiza:
- **Rareza visual minima: Rara** (no puede salir un axo comun)
- **Piso de stats de 45** en todos los atributos
- **Posibilidad de rasgos Astrales** (los mas raros y valiosos del juego)

Si consigues un Webito Astral, NO lo uses con un padrino cualquiera. Guardalo para cuando tengas un padrino nivel 25+ con stats elite. Un Webito Astral es el recurso mas valioso para crianza que existe. No lo desperdicies.

### No Subestimes tu Tutorial Webito

El Webito que recibes al empezar el juego (Tutorial Webito) produce un axo perfectamente viable. No es el mejor del mundo, pero tiene stats decentes y es mas que suficiente para llevarte hasta nivel 15-20 en CPU. Demasiados jugadores lo ignoran y se desesperan por conseguir algo "mejor" antes de tiempo. Tu primer axo es como tu primer auto: no es un Ferrari, pero te lleva a donde necesitas ir.

---

## 7. Prioridad de Expansion de Cueva

La Cueva (Cenote) es tu base de operaciones. Expandirla desbloquea funcionalidad critica. Este es el orden optimo:

### Nivel 3 — LA PRIORIDAD ABSOLUTA

**Que desbloquea:** Hosting de salas + 1 carta extra al empezar.

Llegar a Cueva nivel 3 es tu primer gran objetivo de infraestructura. Poder hostear tus propias salas significa comisiones pasivas de FRJ. La carta extra al empezar mejora tus chances en cada partida. No hay excusa para no tener Cueva 3 lo antes posible.

### Nivel 5 — Segundo Hito

**Que desbloquea:** +1 espacio de incubacion (2 huevos simultaneos).

Dos huevos a la vez significa el doble de velocidad de crianza. Si estas en la etapa de mejorar tu coleccion de axos, esto acelera todo. Llega a Cueva 5 apenas tengas los recursos.

### Nivel 7 — El Gran Premio

**Que desbloquea:** 1 Sobre Foil gratis al mes + 1 Webito Astral gratis.

Este es el nivel donde la Cueva se vuelve rentable de verdad. Un Sobre Foil mensual son cartas foil garantizadas sin gastar FRJ. El Webito Astral ya explicamos por que es valioso. Cueva 7 es el punto donde la inversion en expansion empieza a pagarse sola.

### Nivel 8 — Endgame

**Que desbloquea:** Multiplicador de +10% en todos los ingresos de AXF.

Si estas en la etapa donde el AXF te importa (compras VIP, aceleras cosas, tradeas en el mercado), Cueva 8 es tu destino final. Ese +10% se acumula con otros bonos y, a largo plazo, es una cantidad significativa de AXF extra.

### No Aceleres la Excavacion (a Menos que Seas Rico)

Acelerar la excavacion de la Cueva cuesta AXF. Si aceleras, pierdes los huevos gratis que recibes por esperar. La paciencia es literalmente rentable en la Cueva. Solo acelera si tienes AXF de sobra Y necesitas el siguiente nivel de Cueva urgentemente (por ejemplo, para un torneo que empieza manana). En cualquier otro caso: espera.

---

## 8. Sabiduria Gashapon

Las capsulas Gashapon son la mecanica mas divertida del juego... y la mas peligrosa para tu economia si no tienes control. Aqui va como disfrutarlas sin arruinarte.

### Triple Suerte es el Mejor Valor

La capsula Triple Suerte (22,500 FRJ) es, matematiamente, la que mas valor da por FRJ gastado. Si tienes el FRJ para costearla sin comprometer tu presupuesto operativo, es la mejor opcion. Viene con 3 items garantizados y la tasa de rareza mas alta.

**Pero ojo:** 22,500 FRJ es muchisimo. No compres una Triple Suerte si eso te deja con menos de 5,000 FRJ en tu wallet. La regla es: despues de comprar la capsula, debes poder seguir jugando normalmente.

### La Regla de las 5,000 FRJ

**Nunca tires capsulas si tu balance total esta por debajo de 5,000 FRJ.** Punto. Si tienes 4,500 FRJ y gastas 2,500 en una Plata... te quedan 2,000. Dos partidas de Champions, comida, y estas en cero. No lo hagas.

### El Sistema de Pity es tu Amigo

El sistema de "karma" o pity garantiza que, despues de cierto numero de tiradas sin un item raro, la siguiente tirada te da algo bueno. Esto significa que:
- **Las tiradas nunca son completamente "perdidas"** — cada tirada que no da algo bueno te acerca a la siguiente que SI dara algo bueno
- **Lleva la cuenta mental de tu karma** — si llevas 10 tiradas sin nada epico+, la 11va tiene probabilidades altisimas
- **Las capsulas baratas construyen pity igual que las caras** — una Bronce (barata) avanza el pity tanto como una Oro

### Capsulas Bronze — Perfectas para Principiantes

Son baratas, construyen pity, y de vez en cuando sueltan algo decente. Si estas empezando, las capsulas Bronce son tu entrada al sistema Gashapon sin arriesgar tu economia. Abre 2-3 por semana, construye tu pity, y eventualmente el sistema te recompensara.

### Capsulas Oro — Para Endgame

20,000 FRJ es una inversion seria. No es para principiantes. Es para cuando ya tienes una cueva expandida, un axo nivel 30, y FRJ que no sabes en que gastar. Una capsula Oro mal timing puede retrasar tu progresion semanas.

### Capsulas Gratis (VIP, Ciclo Lunar) No Avanzan el Pity

Importante: las capsulas que recibes GRATIS (por VIP, por Ciclo Lunar, por recompensas) NO cuentan para el sistema de pity. Solo las tiradas que PAGAS con FRJ avanzan tu karma. Esto es intencional — el pity es una recompensa por invertir, no por recibir regalos.

### Disfruta el Momento

Las capsulas Gashapon son, ante todo, diversion. La animacion de apertura, el suspenso, la posibilidad de ese item legendario... eso es parte del juego. No te obsesiones con la "eficiencia" al punto de olvidar por que juegas. Abre capsulas con responsabilidad, pero abre capsulas. La emocion de un buen pull vale mas que cualquier hoja de calculo.

---

## Resumen Para Llevar

Si solo recuerdas 10 cosas de esta pagina, que sean estas:

1. **Tus mejores cartas van en el centro de la Tabla.** Siempre.
2. **FOCO > SUERTE > AGUANTE.** La SAL mantenla en el suelo.
3. **Nunca gastes tus ultimos 100 FRJ.** Siempre guarda para entrada + comida.
4. **El Banco de Algas (AXF -> FRJ) es una trampa F2P.**
5. **Duerme a tu axo.** La energia maxima que decae demasiado es un desastre.
6. **Vende duplicados en el P2P antes de derretirlos.** La diferencia es brutal.
7. **Stop-loss al 50%, take-profit al 200%.** No los toques.
8. **Cueva nivel 3 es tu prioridad absoluta.** Hosting + carta extra.
9. **No tires capsulas por debajo de 5,000 FRJ.**
10. **Diviertete.** Esto es un juego. Si te estresas mas de lo que disfrutas, bajale una marcha.

---




---

## AI

### QUICK_START
> `ai/QUICK_START.md`

---
tags: [ai-context, onboarding]
description: "Stack completo + reglas críticas para AI agents en menos de 1000 tokens"
last_modified: "2026-06-07"
source_files: ["CLAUDE.md", "memory/project_architecture.md"]
---

# Quick Start para AI Agents

## Stack (30 segundos)
| Capa | Tecnología | Puerto |
|------|-----------|--------|
| Backend | FastAPI (async) · SQLModel ORM · Alembic · PostgreSQL 16 | 8001 |
| Frontend | Next.js 16.2 App Router · React 19 · TypeScript 5 · Tailwind CSS 4 | 3000 |
| Contratos | Solidity · Foundry · Anvil local / Plasma Testnet (chain 9746) | 8545 |
| Auth | Privy JWT via header `X-Privy-Token` | — |
| Web3 FE | Viem 2.47 (NO ethers.js) | — |
| Proxy | Nginx → `api.axolot.to` → localhost:8001 | — |
| DB | PostgreSQL en Docker, expuesto en `127.0.0.1:5433` | 5433 |

## Monedas (renombradas 2026-06)
| Moneda | Símbolo | Alias en código | Uso | Cómo obtener |
|--------|---------|----------------|-----|-------------|
| Axofichas | AXF | `axg`, `axofichas`, `axf` | Premium: compras reales, VIP | MoonPay / USDC |
| Frijolitos | FRJ | `gal`, `frijolitos`, `frj` | Gameplay: salas, cápsulas, staking | Jugar, staking, daily rewards |

**CRÍTICO**: En modelos Python: `AxgPurchaseRecord = AxfPurchaseRecord` (alias de compatibilidad). Usar `AxfPurchaseRecord` en código nuevo.

## 5 Reglas que NUNCA Romper
1. **`SELECT FOR UPDATE`** antes de mutar Wallet o Inventory (evita race conditions — costó transacciones perdidas en producción)
2. **`ProcessedTransaction`** (columna UNIQUE) antes de acreditar recompensas on-chain (anti-replay)
3. **`random.SystemRandom()`** exclusivamente — jamás `random.random()` o `random.choice()`
4. **Direcciones de contrato** siempre desde `NEXT_PUBLIC_*` env vars o `settings.py` — nunca hardcode
5. **Nunca push a main/master** — feature branches → merge a `dev`
6. **Changelog obligatorio**: Todo merge a dev registra entrada en `wiki/CHANGELOG.md` (automatizado por taskboard).

## Archivos Más Importantes
| Propósito | Archivo |
|-----------|---------|
| Configuración economía (VIP, precios base) | `backend/app/core/config.py` |
| Lógica de juego (patrones, miss chance, lucky save) | `backend/app/services/game_logic.py` |
| Operaciones de wallet | `backend/app/services/bank_service.py` |
| Integración blockchain / replay protection | `backend/app/services/web3_service.py` |
| Modelos economía (ledger, purchase records) | `backend/app/models/economy.py` |
| Todos los modelos DB | `backend/app/models/` |
| Componente de juego principal | `frontend/components/PlayMode.tsx` |
| Tienda UI | `frontend/components/Store.tsx` |
| Lobby multijugador | `frontend/components/MultiplayerLobby.tsx` |
| Hub central de contratos | `contracts/src/GameController.sol` |

## Patrón de Código Backend
```
router → @router.post → Depends(get_current_user) → service → commit
service: SELECT FOR UPDATE → business logic → db.add(TransactionLedger) → commit
```

## Precios de Referencia (economy.py / HANDOFF)
| Item | Precio |
|------|--------|
| Partida fácil (clásica) | 10 AXF |
| Partida difícil / 5 tablas | 50 AXF |
| Booster pure (más barato) | 60 AXF + 800 FRJ |
| Booster regular | 100 AXF + 1300 FRJ |
| VIP Coral | 100 AXF |
| VIP Dorado | 250 AXF |
| VIP Axolite | 500 AXF |

## MCP Servers disponibles (usar antes de leer archivos)
- **axolotto-kb**: `get_architecture`, `get_economy`, `get_conventions` — evita 20-50K tokens de exploración manual
- **fog-context**: `fog_brief`, `fog_lookup`, `fog_impact` — índice de símbolos del codebase
- **shadowbrain**: `memory_search`, `memory_put` — memoria cross-session de agentes anteriores

## Workflow Obligatorio — Taskboard

**Antes de empezar cualquier tarea**: crear tarjeta en `http://localhost:8181`

```powershell
# 1. Crear tarjeta (activa badge categoría + #ID)
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" planning <categoría>

# 2. Mover a doing con agente (activa badge ⚡ agente)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> doing "Empezando..." <claude|deepclaude|agy>

# 3. Al terminar → review (esperar aprobación antes de done)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> review "Listo. Cambios en X. Verificar con Y."
```

Para vincular un plan con badge 📄: guardar el plan en `docs/plan_task-<id>_slug.md` y editar `planning_data.plan_doc_path` vía API.

→ Guía completa de badges, doc viewer y comandos: [[agent_routing#Workflow Obligatorio del Taskboard]]

→ Detalles: [[critical_rules]] · [[gotchas]] · [[agent_routing]]


### agent_routing
> `ai/agent_routing.md`

---
tags: [ai-context, agentes, taskboard]
description: "Qué agente usar por tarea + workflow obligatorio del taskboard (crear tarjeta, badges, doc viewer, columnas)"
last_modified: "2026-06-07"
source_files: ["AGENTS.md", ".claude/agents/", "tools/taskboard/bin/taskboard.ps1"]
---

# Routing de Agentes Especializados

## Tabla de Decisión Rápida
| Tipo de tarea | Agente | Categoría taskboard |
|--------------|--------|-------------------|
| FastAPI endpoints, SQLModel, Alembic, wallet/bank, game logic | `backend-dev` | backend |
| Next.js, React, Tailwind, Privy, Viem, MoonPay UI | `frontend-dev` | frontend |
| Solidity, Foundry, ABIs, deployment scripts, contratos | `contrato-dev` | contracts |
| Docker Compose, PM2, Nginx, Anvil, deploy scripts, puertos | `devops` | infra |
| Simulación de economía, AXF/FRJ emission vs burn, VIP revenue | `economy-analyst` | economy |
| Auditoría de seguridad, auth checks, exploits económicos | `security-reviewer` | security |
| Mecánicas de juego, balanceo, GDD, retention loops | `game-designer` | design |
| Tests pytest, Playwright E2E, simulate_universe.py, QA | `qa-tester` | qa |

## Reglas de Despacho

- Si la tarea toca `backend/` → `backend-dev`
- Si la tarea toca `frontend/` → `frontend-dev`
- Si la tarea toca `contracts/` → `contrato-dev`
- Si la tarea toca `docker-compose.yaml`, `.env`, PM2, Nginx → `devops`
- Si la tarea mezcla layers → despachar múltiples agentes en paralelo (ver superpowers:dispatching-parallel-agents)
- Si la tarea involucra fondos, wallets, checkout, market → **SIEMPRE** incluir `security-reviewer` como revisión posterior
- Si el contrato cambia ABI → despachar `contrato-dev` + `backend-dev` (el backend necesita actualizar ABIs en `web3_service.py`)
- Si la economía cambia (precios, emission rates, VIP) → despachar `economy-analyst` para validar impacto antes de implementar

## Agentes Disponibles (8 especializaciones)

### `backend-dev`
**Archivo**: `.claude/agents/backend-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: FastAPI, SQLModel ORM, Alembic, Web3.py, dual-currency economy engine, concurrencia con SELECT FOR UPDATE, Privy JWT auth, multiplayer, checkout flows, VIP system
**Dominios**: `backend/app/api/`, `backend/app/services/`, `backend/app/models/`, `backend/app/core/`

### `frontend-dev`
**Archivo**: `.claude/agents/frontend-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Next.js 16.2, React 19, TypeScript, Tailwind 4, Privy login, Viem 2.47 (no ethers.js), MoonPay, WebSocket UI
**Componentes clave**: PlayMode, LoteriaBoard, BoardEditor, MultiplayerLobby, Criadero, Santuario, Store, Inventory, VipModal, CryptoCheckout, MarketP2P
**Dominios**: `frontend/app/`, `frontend/components/`, `frontend/hooks/`, `frontend/context/`

### `contrato-dev`
**Archivo**: `.claude/agents/contrato-dev.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Solidity 0.8.24, OpenZeppelin, Foundry (forge compile/test/script), despliegue en Anvil/Plasma Testnet
**Contratos**: GemaAlga (FRJ), Axogema (AXF), Axolotitos (DNA bit-packing), Webitos, CartasLoteria (IDs 1-54), Boosters, TablasLoteria (escrow), Consumables, GameController
**Dominios**: `contracts/src/`, `contracts/test/`, `contracts/script/`

### `devops`
**Archivo**: `.claude/agents/devops.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: Docker Compose, PM2, Nginx reverse proxy, Anvil, scripts de restart/deploy
**Scripts clave**: `reiniciar.sh` (full stack restart), `scripts/deploy_local.sh` (compile + deploy contratos + write addresses to backend/.env)
**Dominios**: `docker-compose.yaml`, `backend/.env`, `frontend/.env.local`, configuración de red

### `economy-analyst`
**Archivo**: `.claude/agents/economy-analyst.md`
**Herramientas**: Read, Write, Bash, Grep, Glob
**Especialidad**: Modelado de economía dual AXF/FRJ, emisión vs burn rates, proyecciones VIP, jackpot accumulation, análisis de simulate_universe.py
**Red flags que detecta**: GAL inflation (emission/burn > 1.5), AXG deflation, jackpot runaway, staking dominance
**Script de simulación**: `python backend/app/scripts/simulate_universe.py` → `backend/simulation_report.txt`

### `security-reviewer`
**Archivo**: `.claude/agents/security-reviewer.md`
**Herramientas**: Read, Grep, Glob (solo lectura — no modifica código)
**Especialidad**: Auth/authorization checks, replay attacks, race conditions, economic exploits, OWASP API Top 10, contratos (re-entrancy, integer overflow, access control)
**Invocar obligatoriamente cuando**: nueva feature toca wallets/checkout/market/multiplayer, antes de merge a dev de endpoints financieros
**Formato de reporte**: `[CRITICAL/HIGH/MEDIUM/LOW]` — descripción — archivo:línea — fix recomendado

### `game-designer`
**Archivo**: `.claude/agents/game-designer.md`
**Herramientas**: Read, Write, Grep, Glob
**Especialidad**: Mecánicas de Lotería mexicana, balanceo de economía dual, stats de Axolotitos (luck, focus, stamina, etc.), drop rates de boosters, VIP tier benefits, engagement loops
**Documentos que mantiene**: `docs/GDD.md`, `docs/vip_club_design.md`, `docs/plan_*.md`

### `qa-tester`
**Archivo**: `.claude/agents/qa-tester.md`
**Herramientas**: Read, Write, Edit, Bash, Grep, Glob
**Especialidad**: pytest para FastAPI, Playwright E2E para Next.js, forge test para contratos, simulate_universe.py
**Flujos críticos que cubre**: economy integrity, board lifecycle, multiplayer rooms, checkout replay protection, incubation, VIP scheduler, P2P market
**DB de test**: SQLite (`DATABASE_URL=sqlite:///./test.db`) para tests aislados

---

## Workflow Obligatorio del Taskboard

> **REGLA**: Toda tarea, idea o plan que se inicie DEBE tener una tarjeta en el taskboard. Sin tarjeta no existe la tarea. Esto aplica a todos los agentes AI y al usuario.

### URL del Taskboard
```
http://localhost:8181
```

### Ciclo Completo de una Tarea

```
1. CREAR tarjeta  →  column: planning  (o wishes/concepts si es idea)
2. MOVER a doing  →  asignar agente    (activa badge ⚡ agente)
3. TRABAJAR       →  actualizar con comentarios de progreso
4. MOVER a review →  describir qué se hizo y cómo verificar
5. ESPERAR OK     →  el usuario aprueba con: "ok", "dale", "bien", "aprobado"
6. MOVER a done   →  SOLO después de aprobación explícita
```

**NUNCA** mover a `done` sin aprobación. **NUNCA** hacer commit sin que esté en `review` o `done`.

---

### Crear una Tarjeta con TODOS los Badges

```powershell
# Paso 1: Crear con categoría (genera badge de categoría + #ID en footer)
.\tools\taskboard\bin\taskboard.ps1 create "Título de la tarea" "Descripción detallada de qué se necesita hacer y por qué" planning <categoría>

# Paso 2: Mover a doing CON agente (activa badge ⚡ agente)
.\tools\taskboard\bin\taskboard.ps1 status <task-id> doing "Empezando: [descripción breve del primer paso]" <agente>

# Al terminar: mover a review
.\tools\taskboard\bin\taskboard.ps1 status <task-id> review "Listo. Cambios en: [archivos]. Verificar con: [comando o pasos]."
```

**Categorías disponibles** (para el badge de categoría):
| Valor | Cuándo usarlo |
|-------|--------------|
| `backend` | Endpoints, servicios, modelos, migraciones |
| `frontend` | Componentes React, hooks, páginas |
| `contracts` | Solidity, Foundry, ABIs |
| `bug` | Fixes de cualquier capa |
| `docs` | Documentación, wiki, planes |
| `security` | Auditoría, auth, exploits |
| `finance` | Economía, precios, simulaciones |
| `gamedesign` | Mecánicas, balanceo, GDD |
| `infra` | Docker, PM2, Nginx, deploy |
| `tools` | Taskboard, scripts internos |

**Agentes válidos** (para el badge ⚡):
| Valor | Agente |
|-------|--------|
| `claude` | Claude (Anthropic) — frontend, security, contracts |
| `deepclaude` | DeepClaude (DeepSeek) — backend, DB, infra |
| `agy` | AGY (Google) — docs, research, game design |

---

### Sistema de Badges — Referencia Completa

Cada tarjeta puede mostrar estos badges según los campos configurados:

| Badge | Cómo activarlo | Ejemplo visual |
|-------|---------------|----------------|
| **#ID** | Automático al crear | `#51` en el footer |
| **⚡ agente** | `status <id> doing "msg" <agente>` | `⚡ claude` |
| **Categoría** | Parámetro al crear | `backend`, `docs`, `bug` |
| **Prioridad** | Campo `priority` (ver abajo) | `🔴 critical`, `🟡 medium` |
| **📄 Doc** | Plan guardado en `docs/` (ver abajo) | `📄 Doc` en el panel de detalles |
| **🧪 test** | Campo `test_command` vía API edit | `🧪 test` |
| **🌿 rama** | Automático al crear worktree en `doing` | `🌿 task-51-wiki` |
| **📊 progreso** | Requisitos en `planning_data.requirements` | `2/5 reqs` |
| **🔒 bloqueada** | Dependencias sin completar | `🔒 Bloqueada` |
| **✓ en dev** | Merge exitoso a rama base | `✓ en dev` (solo en `done`) |

**Fijar prioridad** (vía API directa, no hay parámetro en PS1):
```powershell
# Usar curl o la UI del taskboard para editar prioridad
Invoke-RestMethod -Uri "http://localhost:8181/api/tasks/edit" -Method POST `
  -ContentType "application/json" `
  -Body '{"id":"task-ID","priority":"high"}'
# Valores: low | medium | high | critical
```

---

### Badge 📄 Doc — Cómo Vincular un Plan a la Tarjeta

El badge `📄 Doc` aparece en el **panel de detalles** de la tarjeta y permite abrir el documento directamente en el Doc Viewer del taskboard (`http://localhost:8181` → botón "📄 Docs").

**IMPORTANTE**: El Doc Viewer solo puede leer archivos `.md` dentro de `docs/` del repositorio.

**Flujo correcto para vincular un plan:**
```powershell
# 1. Guardar el plan en docs/ (NO en C:\Users\... ni en otros lugares)
# Ejemplo: docs/plan_task-1780896719-51.md

# 2. Vincular el documento a la tarjeta vía API
Invoke-RestMethod -Uri "http://localhost:8181/api/tasks/edit" -Method POST `
  -ContentType "application/json" `
  -Body '{"id":"task-ID","planning_data":{"plan_doc_path":"docs/plan_task-ID.md"}}'

# 3. Verificar: abrir el taskboard → click en la tarjeta → ver "📄 Documento vinculado"
# O consultar desde PS1:
.\tools\taskboard\bin\taskboard.ps1 get task-ID
# Si hay doc, mostrará: "📄 docs/plan_task-ID.md"
```

**Naming convention para planes:**
```
docs/plan_task-<task-id>_<slug-del-titulo>.md
# Ejemplo: docs/plan_task-1780896719-51_obsidian-wiki.md
```

---

### Comandos PS1 — Referencia Rápida

```powershell
# Crear (columna y categoría son opcionales, default: planning / backend)
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" [columna] [categoría]

# Mover + comentar + asignar agente (en un solo comando)
.\tools\taskboard\bin\taskboard.ps1 status <id> <columna> ["comentario"] [agente]

# Solo comentar sin mover
.\tools\taskboard\bin\taskboard.ps1 comment <id> "Comentario de progreso"

# Ver lista de tareas en una columna
.\tools\taskboard\bin\taskboard.ps1 list [doing|review|planning|done]

# Ver detalles completos de una tarea (incluye doc path si existe)
.\tools\taskboard\bin\taskboard.ps1 get <task-id>
```

**Ejemplos reales:**
```powershell
# Crear tarea de bug con alta prioridad
.\tools\taskboard\bin\taskboard.ps1 create "Fix: login falla con token expirado" "El endpoint /api/v1/user/sync devuelve 500 cuando el JWT de Privy expiró hace >24h. Reproducir: login normal, esperar 24h, refrescar." planning bug

# Empezar a trabajar (asignarse como claude)
.\tools\taskboard\bin\taskboard.ps1 status task-1234567890-0 doing "Investigando en user.py y auth middleware" claude

# Comentar progreso sin mover
.\tools\taskboard\bin\taskboard.ps1 comment task-1234567890-0 "Encontrado: el middleware no llama token_refresh cuando exp < now(). Fix en auth.py:87"

# Mover a review al terminar
.\tools\taskboard\bin\taskboard.ps1 status task-1234567890-0 review "Fix aplicado en backend/app/middleware/auth.py:87. Test: pytest backend/tests/test_auth.py::test_expired_token"
```

---

### Cuándo Crear Tarjeta (y cuándo no)

**SÍ crear tarjeta cuando:**
- El usuario pide una feature, mejora, o cambio de comportamiento
- El usuario reporta un bug
- Se va a iniciar trabajo que tarda >15 minutos
- Se inicia un plan o investigación
- Se va a modificar lógica de economía, contratos, o endpoints de fondos

**NO crear tarjeta cuando:**
- Es una pregunta exploratoria sin acción concreta ("¿qué hace X?")
- Es un fix de typo o renombrado trivial (<5 minutos)
- Es una respuesta de solo lectura / análisis sin cambios en código

---

## Flujos Complejos — Qué Agentes Combinar

| Escenario | Agentes en orden |
|-----------|-----------------|
| Nueva feature de checkout/pagos | `security-reviewer` (diseño) → `backend-dev` (implementación) → `qa-tester` (tests) → `security-reviewer` (revisión final) |
| Cambio en contrato + backend | `contrato-dev` (ABI update) → `backend-dev` (web3_service.py sync) → `qa-tester` (forge test + pytest) |
| Nueva mecánica de economía | `game-designer` (spec + balance) → `economy-analyst` (validar emisión/burn) → `backend-dev` (implementar) → `qa-tester` (simulation) |
| Fix urgente en producción | `backend-dev` → `security-reviewer` → push a feature branch → PR a dev |
| Nuevo tipo de item/booster | `game-designer` (drop rates) → `contrato-dev` (si nuevo token) → `backend-dev` (shop/inventory) → `frontend-dev` (UI) → `qa-tester` |

## Referencias de Contexto (para planning de AI)
- Contexto principal auto-cargado: `CLAUDE.md`
- Detalles de diseño del juego: `docs/GDD.md`
- Estado actual del proyecto: `HANDOFF_ANTIGRAVITY.md`
- Internos del taskboard: `tools/taskboard/.context_cache/taskboard.txt`
- Contexto cacheado del proyecto: `tools/taskboard/.context_cache/axolotto.txt`

## Token-saving Tips
1. Usar `fog_brief` / `fog_lookup` (MCP fog-context) antes de leer archivos para entender estructura
2. Usar `memory_search` (shadowbrain) — agentes previos pueden haber resuelto el mismo problema
3. Leer archivos con `offset`/`limit` — no cargar archivos de 2000 líneas completos
4. Después de completar trabajo, guardar descubrimientos: `memory_put` con kind=`pattern`|`gotcha`|`decision`

→ Ver [[QUICK_START]] para el stack completo
→ Ver [[critical_rules]] para las reglas que aplican a todos los agentes
→ Ver [[gotchas]] para trampas conocidas por área del proyecto


### critical_rules
> `ai/critical_rules.md`

---
tags: [ai-context, reglas]
description: "Reglas inviolables de desarrollo con explicación del WHY"
last_modified: "2026-06-07"
source_files: ["CLAUDE.md", "memory/feedback_critical_rules.md"]
---

# Reglas Críticas de Desarrollo

| # | Regla | WHY (consecuencia de violarla) | Dónde aplica |
|---|-------|-------------------------------|-------------|
| 1 | Nunca push a main/master — feature branches → dev → master | Master es lo que ven los usuarios en producción. Un push directo puede romper el juego en vivo. | Git workflow |
| 2 | Conventional Commits: `feat(scope): desc`, `fix(scope): desc`, `docs:`, `refactor:` | Sin convención el historial es ilegible y el taskboard no puede parsear cambios automáticamente. | Todo commit |
| 3 | `SELECT FOR UPDATE` antes de mutar Wallet/Inventory | Race condition probada en producción: dos requests concurrentes pueden leer el mismo balance y ambas acreditar, causando doble cobro o doble crédito con dinero real. | `backend/app/services/bank_service.py`, todos los servicios que tocan balance |
| 4 | `ProcessedTransaction` (UNIQUE) — INSERT antes de acreditar | Un tx on-chain puede ser procesado dos veces si el request hace retry. Sin el INSERT previo, el jugador recibe AXF/FRJ dos veces por la misma transacción blockchain. | `backend/app/services/web3_service.py`, endpoint checkout |
| 5 | `random.SystemRandom()` exclusivamente — jamás `random.random()` | Requisito de fairness criptográfica para sorteos de lotería. `random.random()` es predecible y puede ser explotado para predecir resultados. Grep `random.random\|random.choice` antes de cualquier commit de game logic. | Toda aleatoriedad en backend |
| 6 | Direcciones de contrato siempre desde env vars (`NEXT_PUBLIC_*`) o `settings.py` | Los contratos se redeploy en testnet constantemente. Las direcciones hardcodeadas se rompen silenciosamente — el juego parece funcionar pero las transacciones fallan en chain. | `contracts/`, `frontend/hooks/`, `backend/app/services/web3_service.py` |
| 7 | Verificar `authenticated` (Privy) antes de cualquier mutación de wallet | Sin esta verificación cualquier request no-autenticado puede mutar el estado del juego. | Todos los endpoints con `Depends(get_current_user)` y componentes frontend con `usePrivy()` |
| 8 | Taskboard solo en `tools/taskboard/` — nunca tocar backend/frontend/contracts desde tareas de taskboard | Aislamiento: el taskboard es una herramienta interna. Si una tarea del taskboard describe cambios en el juego, esos cambios son para el scope del juego — no para el propio taskboard. | `tools/taskboard/` |
| 9 | Agentes trabajan en worktrees aislados bajo `../.axolotto_worktrees/` | Evita contaminar la rama principal durante desarrollo paralelo. Worktrees huérfanos (sin rama activa) deben limpiarse periódicamente. | Git worktrees, agentes AI |
| 10 | No iniciar servidores desde tareas de agente | Los agentes deben verificar con unit tests o análisis estático, no levantando el stack completo. Iniciar servidores desde agentes puede causar conflictos de puerto y estado impredecible. | Todos los agentes |

## Regla 11: Taskboard obligatorio para toda tarea

**Regla**: Toda tarea, idea o plan que se inicie DEBE registrarse en el taskboard como tarjeta. Sin tarjeta no existe la tarea.

| Acción | Qué hacer |
|--------|-----------|
| Al iniciar trabajo | Crear tarjeta → mover a `doing` con agente asignado |
| Al terminar | Mover a `review` con descripción de qué se hizo |
| Al recibir aprobación | Mover a `done` — NUNCA sin aprobación explícita del usuario |
| Al publicar plan en `docs/` | Vincular el doc a la tarjeta para activar badge 📄 |

```powershell
# Crear con todos los badges activados:
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" planning <categoría>
.\tools\taskboard\bin\taskboard.ps1 status <id> doing "Comenzando" <claude|deepclaude|agy>
```

→ Ver guía completa en [[agent_routing]] sección "Workflow Obligatorio del Taskboard"

| 12 | Changelog obligatorio | Cada merge a `develop` debe registrar entrada en `wiki/CHANGELOG.md`. El taskboard lo automatiza; si falla, revisar manualmente. Sin changelog el historial de cambios del wiki queda incompleto. | Taskboard → DONE, todo merge a dev |

## Regla extra: Ledger obligatorio
Cada cambio de balance (AXF o FRJ) **debe** escribir una fila en `TransactionLedger`. Sin esto la auditoría y el debug de economía son imposibles. Aplica en todos los servicios de `backend/app/services/`.

## Cómo aplicar las reglas en la práctica

**Antes de cualquier commit de game logic:**
```bash
# Verificar que no hay random.random() o random.choice()
grep -r "random\.random\|random\.choice" backend/app/
```

**Patrón correcto para mutación de wallet:**
```python
# En service layer:
wallet = session.exec(
    select(Wallet).where(Wallet.user_id == user_id).with_for_update()
).one()
# ... lógica de negocio ...
session.add(TransactionLedger(...))
session.commit()
```

**Patrón correcto para replay protection:**
```python
# INSERT ANTES de acreditar:
try:
    session.add(ProcessedTransaction(tx_hash=tx_hash))
    session.flush()  # lanza IntegrityError si ya existe
except IntegrityError:
    return  # ya procesado, ignorar silenciosamente
# ... acreditar AXF/FRJ aquí ...
```

→ Ver [[gotchas]] para casos edge donde estas reglas tienen matices
→ Ver [[agent_routing]] para qué agente especializado aplica cada regla


### gotchas
> `ai/gotchas.md`

---
tags: [ai-context, bugs, gotchas]
description: "Trampas conocidas que han causado problemas — leer antes de tocar las áreas afectadas"
last_modified: "2026-06-07"
source_files: ["memory/project_gotchas.md", "HANDOFF_ANTIGRAVITY.md"]
---

# Gotchas — Trampas Conocidas

## Base de Datos / Alembic

### Columnas renombradas fuera de Alembic
**Problema**: Hubo renombrados manuales de columnas en producción que Alembic no registró. Las migraciones estándar fallan porque intentan renombrar columnas que ya tienen el nombre nuevo (o crear columnas que ya existen).

**Solución**: Escribir siempre migraciones idempotentes con bloques `DO $$ ... $$`:
```sql
DO $$ BEGIN
    ALTER TABLE axf_purchase_record RENAME COLUMN axg_amount TO axf_amount;
EXCEPTION
    WHEN undefined_column THEN NULL;
    WHEN duplicate_column THEN NULL;
END $$;
```

### Dos Alembic heads — ya resuelto, no recrear
**Problema**: Existieron dos ramas paralelas de migración que causaban errores 502 al iniciar el backend.

**Resolución**: Se creó `backend/alembic/versions/bb01d2e3f4a5_merge_heads.py` para unirlas.

**Regla**: Antes de crear una nueva migración, verificar que solo hay un head:
```bash
alembic heads
# Debe mostrar exactamente 1 head. Si hay 2, crear merge migration primero.
```

### Startup migrations en main.py
El backend aplica migraciones de schema al iniciar vía `main.py`. Al agregar columnas nuevas, verificar si el cambio ya está en la lógica de startup antes de crear una migración Alembic separada para evitar conflictos.

---

## Monedas / Aliases

### AXF vs AXG, FRJ vs GAL
Las monedas fueron renombradas en junio 2026. El código legacy usa los nombres viejos:

| Nombre nuevo | Símbolo nuevo | Alias viejo en código | Contrato |
|-------------|--------------|----------------------|---------|
| Axofichas | AXF | `axg`, `AXG`, `axogema` | `Axogema.sol` |
| Frijolitos | FRJ | `gal`, `GAL`, `gema_alga` | `GemaAlga.sol` |

**En modelos Python**: `AxgPurchaseRecord = AxfPurchaseRecord` — ambos nombres funcionan. Usar `AxfPurchaseRecord` en código nuevo.

**En agente economy-analyst**: Los archivos del agente aún usan `GAL`/`AXG` internamente (son los mismos alias). No hay bug — es nomenclatura interna del agente.

**Trampas frecuentes**:
- El frontend `.env.local` puede tener `NEXT_PUBLIC_AXOGEMA_ADDRESS` (nombre de contrato, no de moneda) — esto es correcto
- Variables de entorno de contratos no cambiaron nombre porque los contratos Solidity siguen llamándose `GemaAlga.sol` y `Axogema.sol`

---

## Multijugador

### Moneda obligatoria: FRJ
El multiplayer solo acepta FRJ (Frijolitos). AXF está explícitamente prohibido en escrow de salas. Si se intenta usar AXF en una sala multijugador, la lógica debe rechazarlo. Verificar `MULTIPLAYER_CURRENCY = "frijolito"` en `config.py`.

### Mock players y auto-start
Existe un sistema de mock player injection para desarrollo. Las salas con solo mock players NO deben auto-iniciar. Un bug previo causaba que rooms con solo mocks arrancaran automáticamente, lo que distorsionaba las métricas de economía.

---

## MCP Servers — usar antes de leer archivos

### axolotto-kb registrado en .claude/settings.json
El MCP server `axolotto-kb` está registrado y provee tools: `get_architecture`, `get_module`, `get_economy`, `get_conventions`, `search_knowledge`, `get_live_status`.

**Por qué importa**: Los agentes que no usan estas tools pueden desperdiciar 20-50K tokens explorando archivos manualmente. Llamar `get_live_status` al inicio de sesión es una buena práctica.

---

## Taskboard

### Aislamiento estricto
El taskboard (`tools/taskboard/`) es completamente autónomo. Los cambios en el taskboard NUNCA deben afectar backend/frontend/contracts. Si una descripción de tarea del taskboard menciona cambios en el juego, eso significa que el agente de la tarea debe actuar sobre el juego — el taskboard en sí no toca esos archivos.

### Worktrees huérfanos
Los agentes que trabajaron en worktrees bajo `../.axolotto_worktrees/` pueden dejar worktrees sin rama activa. Verificar periódicamente con:
```bash
git worktree list
git worktree prune
```

### Context cache con TTL de 24h
Los archivos `tools/taskboard/.context_cache/axolotto.txt` y `taskboard.txt` tienen TTL de 24h. Si un agente ve información desactualizada del taskboard, refrescar con `POST /api/refresh-context` en el servidor del taskboard.

---

## Issues del HANDOFF (estado al 2026-06-01)

### Backend 502 — resuelto
El 502 que afectaba `api.axolot.to` fue causado por los dos Alembic heads + columnas renombradas. Ya resuelto con:
1. Merge migration `bb01d2e3f4a5_merge_heads.py`
2. Migración idempotente `fa92a8e3d1f4_rename_tokens_and_add_promo_rewards.py`
3. Clase renombrada a `AxfPurchaseRecord` con alias `AxgPurchaseRecord`

### Feature Flujo Corcholata — en planificación
Sistema de códigos promocionales para onboarding físico (corcholatas/tapas). Estado:
- Schema DB diseñado (`promo_codes`, `promo_batches`)
- Endpoint `POST /api/v1/codes/redeem` pendiente de implementación completa
- Archivos backend relevantes: `backend/app/api/v1/endpoints/codes.py`, `backend/app/models/promo.py`, `backend/app/services/promo_service.py`
- Frontend pendiente: componente `CodeEntryPanel` con dos variantes (foco login vs foco código)

### Kit de bienvenida configurado en /admin
```
axf_amount = 139   # intencional: deja 9 AXF tras ~13 partidas fáciles, creando retención
frj_amount = 1000
code_expires_days = 365
```

### Rate limit en códigos
3 intentos por `user_id` para validar código de corcholata. El contador se decrementa por intento fallido, no se resetea.

→ Ver [[critical_rules]] para las reglas de seguridad relacionadas con checkout y replay protection
→ Ver [[agent_routing]] para qué agente manejar cada issue pendiente



---

## Arquitectura

### backend
> `arquitectura/backend.md`

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


### base_de_datos
> `arquitectura/base_de_datos.md`

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


### contratos
> `arquitectura/contratos.md`

---
tags: [arquitectura, contratos, solidity, web3]
description: "Suite de 12 contratos Solidity: tipos, propósitos y relaciones"
last_modified: "2026-06-07"
source_files: ["contracts/src/*.sol"]
---

# Contratos Solidity — Suite Axolotto

## Tabla de Contratos

| Contrato | Tipo | Token/Symbol | Propósito | Caller autorizado |
|----------|------|-------------|-----------|------------------|
| `Axoficha.sol` | ERC-20 | AXF (Axoficha) | Moneda premium actual — adquirida con dinero real (SPEI/cripto) | GameController |
| `Axogema.sol` | ERC-20 | AXG (Axogema) | Moneda premium legacy — nombre anterior de AXF, misma mecánica | GameController |
| `GemaAlga.sol` | ERC-20 | GAL (Gema Alga) | Moneda de juego legacy (nombre anterior de FRJ), gana jugando | GameController |
| `Frijolito.sol` | ERC-20 | FRJ (Frijolito) | Moneda de juego actual — se gana jugando, paga entradas, tienda | GameController |
| `Webitos.sol` | ERC-721 | WEBITO | Huevos NFT únicos — incuban en Axolotitos con cariñitos | GameController |
| `Axolotitos.sol` | ERC-721 | — | Mascotas NFT con DNA y stats (8 stats) almacenados on-chain | GameController |
| `CartasLoteria.sol` | ERC-1155 | — | 54 cartas de Lotería semi-fungibles (token IDs 1-54) | GameController |
| `Boosters.sol` | ERC-1155 | — | Sobres sellados de 7 cartas; 3 fases (420/1260/2520 por fase) | GameController |
| `TablasLoteria.sol` | ERC-721 + ERC-1155Holder | — | Tableros 4x4 NFT; las 16 cartas quedan en escrow on-chain | GameController |
| `Consumables.sol` | ERC-1155 | — | Consumibles: Algae Pellet, Brine Shrimp, Gotas Anti-Escarcha, Lámpara Infrarroja | GameController |
| `GameController.sol` | custom / Ownable | — | Hub central — único autorizado a mint/burn en todos los contratos | Admin wallet (Owner) |
| `Counter.sol` | utility | — | Contrato utilitario de contador (Foundry default / testing) | — |

## Notas sobre el Renombrado de Monedas (2026-06)

- `Axoficha.sol` (AXF) es el contrato **activo** de la moneda premium.
- `Axogema.sol` (AXG) es el contrato **legacy** — mismo patrón, nombre anterior. Ambos coexisten en el repositorio.
- `Frijolito.sol` (FRJ) es el contrato **activo** de la moneda de juego.
- `GemaAlga.sol` (GAL) es el contrato **legacy** — misma mecánica que FRJ.
- El backend usa alias (`wallet.axogemas = wallet.axofichas`) para compatibilidad con registros históricos.

## GameController — Hub Central

```
Backend (Treasury Wallet)
    ↓
GameController
    ├──→ Axoficha / Axogema / GemaAlga / Frijolito  (ERC-20 mint/burn)
    ├──→ Webitos / Axolotitos                         (ERC-721 mint)
    ├──→ CartasLoteria / Boosters / Consumables       (ERC-1155 mint/burn)
    └──→ TablasLoteria                                (ERC-721 mint/burn + escrow cartas)
```

- Solo el GameController puede mintear, quemar y transferir tokens del juego.
- El GameController emite eventos de auditoría: `TiendaCompra`, `PartidaJugada`, `AxolotitoNutrido`.
- Para el modo manual en tiempo real emite: `ManualGameStarted`, `CardCalled`, `LoteriaShouted`, `ManualGameEnded`.
- El modificador `onlyFRJ` bloquea envíos de AXF/ETH nativo en operaciones multijugador — solo acepta Frijolitos.

## Mecánicas On-Chain

### Webitos (Huevos)
- Fases 1-3 con oferta limitada: 420 / 1260 / 2520 huevos por fase.
- Cada Webito tiene un `webitoFase` (1, 2 o 3) registrado en mapping on-chain.
- La incubación ocurre off-chain (backend + frontend); solo el nacimiento mint el NFT Axolotito.

### Axolotitos (Mascotas NFT)
- Struct `Stats` almacena 8 valores on-chain: `salinity`, `luck`, `focus`, `stamina`, `charisma`, `agility`, `wisdom`, `strength`.
- El `dna_sequence` (uint256) se genera por el backend al eclosionar y se inscribe en la cadena.
- La blockchain es la fuente de verdad para ownership y stats al momento de compra/venta.

### CartasLoteria (54 Cartas)
- Token IDs 1-54 — una carta del mazo de Lotería Mexicana por ID.
- Las cartas pueden estar en el inventario del jugador o en escrow dentro del contrato `TablasLoteria`.

### TablasLoteria (Tableros)
- Al crear un tablero: las 16 cartas se transfieren al contrato (escrow) y se mintea 1 NFT de Tabla.
- Al disolver: se quema el NFT de Tabla y se devuelven 15 cartas (1 se destruye aleatoriamente, lógica off-chain).
- Las cartas en escrow cuentan para el staking pasivo.

### Replay Protection (off-chain)
El backend registra cada `tx_hash` procesado en `ProcessedTransaction` (UNIQUE) antes de acreditar recompensa. Ver [[backend]] — Patrones Obligatorios.

## Redes Soportadas

| Red | Chain ID | Puerto / URL |
|-----|---------|-------------|
| Local (Anvil) | 31337 | `http://localhost:8545` |
| Plasma Testnet | 9746 | URL de Plasma Testnet |
| Producción | pendiente | — |

## Direcciones de Contrato

Las direcciones se configuran exclusivamente via variables de entorno:

- **Frontend**: `NEXT_PUBLIC_CONTRACT_AXOFICHA`, `NEXT_PUBLIC_CONTRACT_FRIJOLITO`, `NEXT_PUBLIC_CONTRACT_AXOLOTITOS`, etc. (en `frontend/env.local`)
- **Backend**: variables en `backend/.env` leídas por `backend/app/core/config.py`

**Nunca hardcodear direcciones de contratos en el código.**

Ver [[../api/resumen_endpoints]] para los endpoints que interactúan con contratos vía `web3_service.py`.


### frontend
> `arquitectura/frontend.md`

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



---

## API

### banco_y_economia
> `api/banco_y_economia.md`

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


### juego_y_multijugador
> `api/juego_y_multijugador.md`

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


### resumen_endpoints
> `api/resumen_endpoints.md`

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


### usuarios_y_perfil
> `api/usuarios_y_perfil.md`

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



---

## Economia

### economia_general
> `economia/economia_general.md`

---
tags: [economia, balance]
description: "Modelo económico: house edge, jackpot, staking de boards, emisión FRJ, mecanismos anti-inflación"
last_modified: "2026-06-07"
source_files: ["backend/simulation_report.txt", "backend/app/core/config.py", "backend/app/services/multiplayer_service.py", "backend/app/services/board_service.py", "backend/app/models/lobby_models.py"]
---

# Economía General — Modelo y Balance

---

## Modelo de Reserva (Distribución del Pozo Multijugador)

Fuente: `multiplayer_service.py` — función de settlement de sala.

Cuando inicia una partida multijugador, el pozo total (`total_collected_gal`) se distribuye así:

| Destino | Porcentaje | Descripción |
|---------|-----------|-------------|
| Premio 1 (primer Lotería) | 35% | Dividido entre todos los ganadores del primer Lotería |
| Premio 2 (Tabla Llena) | 55% | Dividido entre los ganadores de tabla completa |
| Tesorería (TreasuryVault) | 5% | House commission acumulada en DB |
| Jackpot (JackpotVault) | 5% | Contribución al bote acumulado global |
| **Total** | **100%** | — |

> Cuando la sala tiene anfitrión (cave room con host), el 5% extra del anfitrión sale del Premio 1 (que baja a 30%), manteniendo el Premio 2 en 55% y las comisiones en 10%.

---

## House Edge por Sala (Resultados de Simulación)

Fuente: `backend/simulation_report.txt` — simulación real ejecutada con 12 jugadores en el backend.

> Nota: el reporte disponible corresponde a una corrida de prueba del simulador v3 con 12 usuarios (no 50 000 partidas). Los datos de win rate provienen de esa muestra.

### Partidas Individuales (147 jugadas)

| Métrica | Valor |
|---------|-------|
| Partidas totales | 147 |
| Victorias | 44 |
| Win rate jugadores | 29.9% |
| FRJ obtenidas por jugadores | 4 988.82 |
| Partidas autojuego (bot) | 27 |

### Salas Multijugador (13 partidas registradas)

| Sala | Partidas | Victorias | Win rate | Neto promedio ganador FRJ |
|------|----------|-----------|----------|--------------------------|
| Charco de Novatos (`rookie_pool`) | 8 | 3 | ~37.5% | +50.5 a +94.0 (muestra) |
| Fosa del Campeón (`champion_abyss`) | 5 | 1 victorias limpias | ~40% | +57.8 a +136.2 (muestra) |
| **Total multijugador** | 13 | 4 | 31% | — |

**Neto total de jugadores**: -111.5 FRJ (la casa/jackpot retiene el 10% del pozo).

> El house edge efectivo del 10% (5% Tesorería + 5% Jackpot) es el esperado por diseño. En la muestra pequeña el neto negativo refleja que más jugadores perdieron que ganaron, lo cual es estadísticamente normal con n=13.

---

## Jackpot

Fuente: `lobby_models.py` (modelo `JackpotVault`) + `multiplayer_service.py` (lógica de pago).

| Parámetro | Valor |
|-----------|-------|
| Semilla inicial | 1 000 FRJ (fondos de proyecto) |
| Semilla de reinicio estándar | 1 000 FRJ |
| Contribución por partida | 5% del pozo total de la sala |
| Pago al ganador | 90% del JackpotVault acumulado |
| Resto tras pagar | 10% del JackpotVault (mínimo 1 000 FRJ; si cae por debajo, la Tesorería aporta la diferencia) |

### Condición para Ganar el Jackpot

El jackpot solo es elegible si se cumplen **todas** estas condiciones en la sala:

1. El primer Lotería ocurre en el **turno 4, 5 o 6** (ventana estrecha de cartas)
2. La sala tiene **al menos 5 tablas humanas** (no bots)
3. La sala tiene **al menos 2 wallet_address únicas** (anti-sybil)

El ganador recibe el 90% del bote. Si hay múltiples ganadores simultáneos, el 90% se divide entre ellos.

### Bonus Jackpot VIP Axolite

Los jugadores con VIP Axolite reciben un +5% adicional sobre su share individual del jackpot (y también sobre Premio 1 y Premio 2). Se aplica en el momento del settlement.

---

## Staking de Boards (Emisión Pasiva de FRJ)

Fuente: `board_service.py` — funciones `get_board_hourly_rate` y `get_accrued_staking`.

Los boards emiten FRJ pasivamente según la rareza de sus cartas. La tasa base es la suma de los bonos de rareza de las 16 cartas del board, multiplicada por un factor de nivel.

### Bonos por Rareza de Carta (FRJ/hora por carta)

| Rareza | FRJ/hora |
|--------|---------|
| Common | 0.05 |
| Rare | 0.15 |
| Epic | 0.40 |
| Legendary | 1.00 |

> La rareza Uncommon no aparece en el mapa; usa el fallback de 0.05 FRJ/hora (igual que Common).

### Fórmula de Cálculo

```
hourly_rate = sum(rarity_bonus per card) * (1.0 + board.level / 10.0)
accrued_gal = hours_elapsed * hourly_rate   (máximo 24 horas acumuladas sin reclamar)
```

**Ejemplo** — Board nivel 1, 16 cartas Common:
- `hourly_rate = 16 × 0.05 × (1 + 1/10) = 0.88 FRJ/hora`
- `max_24h = 21.12 FRJ`

**Ejemplo** — Board nivel 5, 4 Legendary + 12 Common:
- `hourly_rate = (4×1.00 + 12×0.05) × (1 + 5/10) = 4.60 × 1.5 = 6.90 FRJ/hora`
- `max_24h = 165.6 FRJ`

### Play-to-Stake

El staking pasivo está condicionado a actividad reciente: si el jugador no jugó ninguna partida en las últimas **24 horas**, el acumulado devuelve 0. Esto incentiva la participación activa.

---

## Mecanismos Anti-Inflación

| Mecanismo | Descripción | Moneda quemada |
|-----------|-------------|----------------|
| **Card Melting** | Quemar cartas duplicadas a cambio de FRJ (burn mechanism) | Cartas NFT → FRJ emitidos |
| **Consumibles** | Gastar FRJ en alimento (30–150 FRJ), Solvente (120 FRJ), Gotas (200 FRJ) | FRJ |
| **Entry fees multijugador** | Cada partida recircula FRJ al ecosistema (premios + tesorería + jackpot) | FRJ circula, no se destruye |
| **Desbloqueo de slots** | Gastar FRJ para más ranuras de board (500 → 15 000 FRJ por slot) | FRJ |
| **Cápsulas Gashapon** | Gastar FRJ (1 500 – 22 500) por premios aleatorios | FRJ |
| **VIP diarios** | La emisión VIP es controlada y acotada por tier (40/100/200 FRJ/día máximo) | — (emisión, no quema) |

---

→ Ver [[vip_tiers]] para análisis de valor VIP · [[tablas_precios]] para fees exactos de salas y consumibles · [[../mecanicas/staking]] para tasas de emisión (pendiente de crear)


### monedas
> `economia/monedas.md`

---
tags: [economia, monedas]
description: "AXF y FRJ: diferencias, aliases, cómo obtenerlas, restricciones de uso"
last_modified: "2026-06-07"
source_files: ["backend/app/core/config.py", "backend/app/core/prices.py"]
---

# Monedas del Juego

---

## Tabla Comparativa

| Característica | AXF (Axofichas) | FRJ (Frijolitos) |
|---------------|----------------|-----------------|
| Nombre completo | Axofichas | Frijolitos |
| Nombre anterior | AXG / Axogemas | GAL / Gemas Alga |
| Alias en código (Wallet) | `axg`, `axofichas`, `axf` | `gal`, `frijolitos`, `frj` |
| Contrato Solidity | `Axogema.sol` / `AXOGEMA_ADDRESS` | `GemaAlga.sol` / `GEMA_ALGA_ADDRESS` |
| Tipo | Moneda premium | Moneda de gameplay |
| Cómo obtener | Compra real (MoonPay / USDC onramp) | Jugar, staking de boards, FRJ VIP diarios, P2P, premios multijugador |
| Valor nominal | $2.00 MXN por AXF | Sin valor en dinero real ($0.175 MXN de referencia) |
| Usos principales | VIP, Webitos, Boosters, Boards, Lámpara Infrarroja, Upgrade Slots | Salas multijugador, Cápsulas Gashapon, Alimentos, Solvente, Slots de cueva |
| ¿Usable en multijugador? | **PROHIBIDO en escrow/lobby** | **UNICA moneda permitida** |
| ¿Tiene DevEx? | Sí (70% bruto = $1.40 MXN / 70% neto = $1.14 MXN) | No |

---

## Aliases en el Código

```python
# Wallet model: estos pares acceden al MISMO campo en la DB
wallet.axg         # alias legacy — no usar en código nuevo
wallet.axofichas   # nombre correcto — SIEMPRE usar este en código nuevo

wallet.gal         # alias legacy — no usar en código nuevo
wallet.frijolitos  # nombre correcto — SIEMPRE usar este en código nuevo
```

Los aliases `axg` y `gal` existen para compatibilidad con endpoints y scripts legacy que aún usan los nombres anteriores. El código nuevo debe usar `axofichas` y `frijolitos`.

---

## Restricción de Multijugador

Fuente: `config.py` — `MULTIPLAYER_CURRENCY: str = "frijolito"`

> Por compliance legal, el juego multijugador **SOLO** acepta Frijolitos (FRJ).
> Axofichas (AXF) está prohibido en cualquier operación de lobby, salas o escrow.

Esta restricción está hardcodeada como constante de módulo en `config.py`. Ningún endpoint de lobby/multiplayer debe aceptar o procesar AXF. El servicio de multiplayer (`multiplayer_service.py`) valida esto en el registro de sala.

---

## Cómo Obtener AXF

1. **Compra con USDC** vía MoonPay widget (onramp fiat → USDC → AXF)
2. **Checkout crypto** directo — `POST /api/v1/checkout/create-order` (Polygon Amoy)
3. **Modo local/dev** — todo usuario nuevo recibe `DEV_AUTO_REWARD_AXF = 50 000 AXF` automáticamente

## Cómo Obtener FRJ

1. **Ganar partidas individuales** — pago en FRJ por victoria (campo `GAL obtenidas` en simulación)
2. **Staking de boards** — emisión pasiva por hora según rareza de cartas en la tabla (ver [[economia_general]])
3. **FRJ VIP diarios** — 40/100/200 FRJ por día según tier (ver [[vip_tiers]])
4. **Premios multijugador** — el ganador recibe el premio de la sala en FRJ
5. **P2P marketplace** — vender cartas, boards o Axolotitos a otros jugadores
6. **Modo local/dev** — todo usuario nuevo recibe `DEV_AUTO_REWARD_FRJ = 500 000 FRJ` automáticamente

---

## Historia del Renombre (2026-06)

- **AXG (Axogemas) → AXF (Axofichas)**: renombre para simplificar y estandarizar la identidad de marca
- **GAL (Gemas Alga) → FRJ (Frijolitos)**: renombre temático alineado al universo acuático mexicano
- Los aliases `axg` / `gal` se mantienen en el modelo `Wallet` para compatibilidad con código legacy, clientes existentes y datos en DB
- Los contratos Solidity mantienen sus nombres originales (`Axogema.sol`, `GemaAlga.sol`) — el renombre es solo en capa de producto/UI

---

→ Ver todos los precios en [[tablas_precios]] · VIP y FRJ diarios en [[vip_tiers]]


### tablas_precios
> `economia/tablas_precios.md`

---
tags: [economia, precios]
description: "Tablas completas de precios de todos los items — fuente: backend/app/core/prices.py"
last_modified: "2026-06-07"
source_files: ["backend/app/core/prices.py", "backend/app/core/config.py"]
---

# Tablas de Precios — Axolotto

> Si un precio cambia en el código, actualizar esta tabla Y añadir entrada en [[../CHANGELOG]].
>
> Moneda: **AXF** = Axofichas (premium). **FRJ** = Frijolitos (gameplay).
> Los alias en el código son `axg`/`gal` — ver [[monedas]] para el detalle completo.

---

## Webitos (Huevos NFT)

Precio en AXF. Fuente: `WEBITO_PRICES` en `prices.py`.

| Fase | Nombre | Precio AXF |
|------|--------|-----------|
| 1 | Génesis | 400 |
| 2 | Expansión | 800 |
| 3 | Retail | 1 200 |
| Especial | Astral | 3 000 |

---

## Boosters (Packs de 7 Cartas)

Fuente: `BOOSTER_PRICES` en `prices.py`. Cada tipo se puede comprar con AXF (premium) o FRJ (earned).

### Fase 1 — First Edition

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 10 | 100 |
| Nido | 10 | 100 |
| Cosmos | 10 | 100 |
| Pure (solo 1 carta) | 6 | 60 |

### Fase 2 — Unlimited

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 15 | 150 |
| Nido | 15 | 150 |
| Cosmos | 15 | 150 |
| Pure | 10 | 100 |

### Fase 3 — Retail / Standard

| Tipo | AXF | FRJ |
|------|-----|-----|
| Fiesta | 20 | 200 |
| Nido | 20 | 200 |
| Cosmos | 20 | 200 |
| Pure | 15 | 150 |

### Especial — Booster Brillante (Foil)

| Tipo | AXF | FRJ |
|------|-----|-----|
| Foil | 80 | 800 |

---

## Cápsulas Gashapon

Fuente: `GASHAPON_TIER_COSTS` en `prices.py`. Precio en FRJ.

| Tier | Costo FRJ |
|------|-----------|
| Bronce | 1 500 |
| Plata | 5 000 |
| Oro | 20 000 |
| Triple (pack 3) | 22 500 |

---

## Tablas de Juego (Boards)

Fuente: `BOARD_PRICES` en `prices.py`.

| Tipo de Tabla | AXF | FRJ |
|---------------|-----|-----|
| Clásica | 10 | 130 |
| Suerte | 50 | 520 |
| Plasma | 150 | 1 560 |
| Cósmica | 200 | 0 |

> La tabla Cósmica solo acepta pago en AXF; el campo FRJ está en 0 en el código.

---

## Slots de Cueva (Desbloqueo de Boards adicionales)

Fuente: `BOARD_SLOT_COSTS` en `prices.py`. Precio en FRJ. Los primeros 3 slots están incluidos por defecto; estos son los desbloqueos adicionales.

| Slot # | Costo FRJ |
|--------|-----------|
| 4 | 500 |
| 5 | 1 000 |
| 6 | 2 000 |
| 7 | 4 000 |
| 8 | 8 000 |
| 9 | 15 000 |

---

## Multijugador (siempre en FRJ)

Fuente: `MULTIPLAYER_ROOMS` en `prices.py`. Solo FRJ por mandato legal (`MULTIPLAYER_CURRENCY = "frijolito"` en `config.py`).

| Sala | Entry Fee FRJ | Premio 1er lugar FRJ | Consolación FRJ | XP Ganador (Board/Axo) | XP Perdedor (Board/Axo) |
|------|--------------|---------------------|----------------|------------------------|-------------------------|
| Charco de Novatos (`rookie_pool`) | 25 | 85 | 8 | 25 / 35 | 8 / 8 |
| Fosa del Campeón (`champion_abyss`) | 100 | 400 | 20 | 60 / 75 | 15 / 15 |

> Salas cave (player-hosted) usan `buy_in_frj` configurable por el anfitrión.

---

## Consumibles

Fuente: `CONSUMABLE_PRICES` en `prices.py`.

| Item | Precio | Moneda |
|------|--------|--------|
| Gotas Anti-Escarcha | 200 | FRJ |
| Lámpara Infrarroja Pro | 200 | AXF |
| Alimento Común — Algae Pellet | 30 | FRJ |
| Alimento Premium — Brine Shrimp | 150 | FRJ |
| Solvente de Pegamento | 120 | FRJ |
| Upgrade Board Slots | 300 | AXF |

---

## VIP (Membresía 30 días)

Fuente: `CONSUMABLE_PRICES` en `prices.py` y `VIP_CONFIG` en `config.py`.

| Tier | Precio AXF |
|------|-----------|
| Coral | 400 |
| Dorado | 600 |
| Axolite | 1 800 |

> Desglose completo de beneficios en [[vip_tiers]].

---

## Valor Nominal

Fuente: `prices.py` líneas 4-8.

| Concepto | Valor |
|----------|-------|
| 1 AXF en MXN (nominal) | $2.00 MXN |
| Paquete de referencia (FRJ) | 200 FRJ = $35 MXN |
| 1 FRJ en MXN (aproximado) | $0.175 MXN |
| DevEx 70% bruto | $1.40 MXN por AXF |
| DevEx 70% neto | $1.14 MXN por AXF |
| DevEx 50% bruto | $1.00 MXN por AXF |

---

→ Ver estructura de beneficios VIP en [[vip_tiers]] · Modelo económico en [[economia_general]] · Diferencias entre monedas en [[monedas]]


### vip_tiers
> `economia/vip_tiers.md`

---
tags: [economia, vip]
description: "Comparativa completa de tiers VIP con todos los beneficios — fuente: config.py:VIP_CONFIG"
last_modified: "2026-06-07"
source_files: ["backend/app/core/config.py:VIP_CONFIG", "backend/app/core/prices.py:CONSUMABLE_PRICES"]
---

# Membresía VIP — Comparativa de Tiers

> Duración: 30 días. Renovación automática configurable desde el perfil del jugador.
>
> Fuente autoritativa: `VIP_CONFIG` en `backend/app/core/config.py`.

---

## Tabla de Beneficios

| Beneficio | Sin VIP | Coral | Dorado | Axolite |
|-----------|---------|-------|--------|---------|
| **Precio AXF** | — | 400 | 600 | 1 800 |
| **FRJ diarios** | 0 | 40 | 100 | 200 |
| **Descuento tienda** | 0% | 5% | 12% | 20% |
| **Slots de tabla extra** | 0 | 0 | +1 | +2 |
| **Slots de Axolotito extra** | 0 | 0 | 0 | +1 |
| **Comisión P2P** | 5% | 4% | 3% | 1.5% |
| **Bonus jackpot** | 0% | 0% | 0% | +5% |
| **Descuento multijugador** | 0% | 0% | 0% | 15% |
| **FRJ al activar** | — | 200 | 500 | 1 000 |
| **Boosters al activar** | — | Ninguno | 1x Normal | 1x Foil |
| **Cápsulas mensuales** | — | 2x Bronce | 2x Bronce + 1x Plata | 3x Bronce + 2x Plata + 1x Oro |
| **Popular** | — | No | Sí | No |

---

## Descripción de los Beneficios de Bienvenida

Al activar el VIP por primera vez (o al renovar), el sistema acredita inmediatamente:

| Tier | Bienvenida |
|------|-----------|
| Coral | 200 FRJ en cuenta |
| Dorado | 500 FRJ + 1 Booster Normal |
| Axolite | 1 000 FRJ + 1 Booster Foil |

---

## Cápsulas Gashapon Mensuales

Las cápsulas se acumulan en cuenta y son reclamables con `POST /api/v1/rewards/lunar/claim`.

| Tier | Bronce | Plata | Oro |
|------|--------|-------|-----|
| Coral | 2 | — | — |
| Dorado | 2 | 1 | — |
| Axolite | 3 | 2 | 1 |

---

## Notas Importantes

- **Caducidad**: si el VIP caduca, los Axolotitos extra que ocupaban el slot bonus quedan **CONGELADOS** hasta renovar. No se borran, pero no son jugables ni rentables.
- **FRJ diarios**: se acumulan en la cuenta Xochimilco. Son reclamables manualmente desde la UI. No se transfieren automáticamente a la wallet activa.
- **Auto-renovación**: configurable desde el perfil del jugador. Si está activa y la wallet tiene saldo, la renovación se ejecuta al expirar el período de 30 días.
- **Bonus jackpot Axolite**: el +5% aplica sobre el share individual del jugador en Premio 1, Premio 2 y Jackpot de Oro. Se aplica en `multiplayer_service.py` durante el settlement de la sala.
- **Descuento multijugador Axolite**: 15% sobre el entry fee de la sala. Solo aplica en salas públicas (`rookie_pool`, `champion_abyss`).

---

## Análisis de Valor: Recuperación por FRJ Diarios

Cuántos días de FRJ diarios se necesitan para recuperar el costo del VIP, asumiendo que los FRJ valen $0.175 MXN cada uno y el AXF $2.00 MXN.

| Tier | Costo AXF | Costo MXN equiv. | FRJ/día | FRJ/día en MXN | Días para recuperar |
|------|-----------|-----------------|---------|----------------|---------------------|
| Coral | 400 AXF | $800 MXN | 40 FRJ | $7.00 MXN | ~114 días |
| Dorado | 600 AXF | $1 200 MXN | 100 FRJ | $17.50 MXN | ~69 días |
| Axolite | 1 800 AXF | $3 600 MXN | 200 FRJ | $35.00 MXN | ~103 días |

> Nota: estos cálculos usan los precios nominales de `prices.py`. La rentabilidad real depende de cómo se usen los FRJ obtenidos (competir, comprar cápsulas, etc.). El descuento de tienda del 20% (Axolite) y los boosters de bienvenida mejoran sustancialmente el valor efectivo.

---

→ Ver precios de membresía en [[tablas_precios]] · Historial de cambios: [[../CHANGELOG]]



---

## Mecanicas

### estadisticas_axolotito
> `mecanicas/estadisticas_axolotito.md`

---
tags: [mecanicas, axolotito, stats]
description: "Las 8 estadísticas del Axolotito con rangos exactos, fórmulas y efectos en juego"
last_modified: "2026-06-07"
source_files: ["backend/app/models/axolotito.py", "backend/app/services/game_logic.py", "backend/app/services/imprinting_service.py"]
---

# Estadísticas del Axolotito

## Tabla de Stats

| Stat | Campo en código | Tipo | Default | Rango | Efecto en juego |
|------|----------------|------|---------|-------|-----------------|
| Suerte | `stat_luck` | float | 10.0 | 0.0 – 100.0 | Probabilidad de Lucky Save (ver fórmula abajo) |
| Concentración | `stat_focus` | float | 50.0 | 0.0 – 100.0 | Probabilidad de miss al marcar carta (ver fórmula abajo) |
| Energía Máxima | `stat_stamina` | int | 100 | 50 – 200 | Tope máximo de `energy_current`; afecta recuperación |
| Salinidad | `stat_salinity` | float | 5.0 | 0.0 – 100.0 | Mala suerte; afecta deltas de imprinting en Webitos |
| Carisma | `stat_charisma` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |
| Agilidad | `stat_agility` | float | 10.0 | 0.0 – 100.0 | Igual a Focus en el sistema de imprinting (`stat_agility = focus`) |
| Sabiduría | `stat_wisdom` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |
| Fuerza | `stat_strength` | float | 10.0 | 0.0 – 100.0 | (dato no usado activamente en game_logic.py actual — verificar manualmente) |

Nota: `stat_charisma`, `stat_wisdom` y `stat_strength` existen en el modelo pero `imprinting_service.py` los fija en `0.0` al eclosionar un Webito. El diseño 4-stats activo es: **Luck, Focus, Stamina, Salinity**.

---

## Fórmula: Miss Chance

Definida en `game_logic.py`, función `_miss_chance(focus)`:

```
miss_chance = max(0.0, min(0.3, (100.0 - focus) * 0.003))
```

| `stat_focus` | Miss Chance | Descripción |
|-------------|-------------|-------------|
| 100 | 0.0 % | Sin fallos |
| 80 | 6.0 % | Bot Campeón (`bot_focus=80`) |
| 50 | 15.0 % | Jugador típico |
| 40 | 18.0 % | Bot Novato (`bot_focus=40`) |
| 0 | 30.0 % | Máximo posible (techo en 30 %) |

El techo es 30 % (`min(0.3, ...)`). El piso es 0 % (`max(0.0, ...)`). La fórmula es lineal entre focus 0 y focus 100.

---

## Fórmula: Lucky Save

Definida en `game_logic.py`, función `_lucky_save(axo_luck, already_used)`:

```
chance = (axo_luck / 1000.0) * 0.5
```

- Se activa **como máximo una vez por partida** (`already_used` guard).
- Cuando se activa, cancela un evento negativo para el jugador.

| `stat_luck` | Probabilidad Lucky Save |
|------------|------------------------|
| 0 | 0.0 % |
| 10 | 0.5 % |
| 50 | 2.5 % |
| 100 | 5.0 % (máximo) |

---

## Energía y Recuperación

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `energy_current` | int | 100 | Energía restante. Se consume por partida. Se recupera al dormir. |
| `stat_stamina` | int | 50–200 | Energía máxima del Axolotito. Default 100. |
| `sleep_expires_at` | datetime | null | Timestamp en que termina el sueño y se restaura la energía. |
| `status` | str | `"idle"` | Estados posibles: `idle`, `expedition`, `resting`, `studying`, `playing`, `sleeping`, `waiting_settlement` |

El diseño indica 10 partidas por ciclo de sueño (energy_current se consume y se recupera con `sleep_expires_at`). Los bots no consumen energía.

---

## Sistema de Imprinting

Campos en el modelo `Axolotito` que afectan a los Webitos que este Axolotito apadrina:

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `nature` | str (opcional) | `null` | Naturaleza del Axolotito. Modifica los deltas de imprinting. |
| `mentorship_count` | int | 0 | Número de Webitos que este Axolotito ha apadrinado. |
| `tutored_by_id` | int (opcional) | `null` | ID del Axolotito que apadrinó a este cuando era Webito. |

### Natures disponibles y sus efectos

Definidas en `imprinting_service.py`, función `compute_deltas`:

| Nature | Efecto |
|--------|--------|
| `lucky` | Si `luck_delta > 0`, se multiplica por 1.25 |
| `methodical` | Si `focus_delta > 0`, se multiplica por 1.25 |
| `hyperactive` | Si `stamina_delta > 0`, se multiplica por 1.25 |
| `glutton` | Si el padrino pierde, todos los deltas negativos se reducen al 80 % de su magnitud (amortiguador de pérdida) |

### Herencia genética del padrino al Webito

Al iniciar el imprinting (`initial_base_stats` en `imprinting_service.py`), los stats base del Webito se calculan con rangos aleatorios más un bonus del padrino:

| Stat | Rango base aleatorio | Factor herencia (nivel ≤20) | Factor herencia (nivel >20) |
|------|---------------------|----------------------------|----------------------------|
| `luck` | 20.0 – 50.0 | `padrino.stat_luck × 0.10` | `padrino.stat_luck × 0.15` |
| `focus` | 25.0 – 55.0 | `padrino.stat_focus × 0.10` | `padrino.stat_focus × 0.15` |
| `stamina` | 70.0 – 110.0 | `padrino.stat_stamina × 0.10` | `padrino.stat_stamina × 0.15` |
| `salinity` | 10.0 – 30.0 | `padrino.stat_salinity × 0.10` | `padrino.stat_salinity × 0.15` |

El factor sube de 10 % a 15 % cuando el padrino supera el nivel 20.

---

## Stats finales al eclosionar (imprinting_service.py → `final_stats`)

| Stat final | Fórmula | Clamp |
|-----------|---------|-------|
| `stat_luck` | `base_stat_luck + bonus_luck` | 0.0 – 100.0 |
| `stat_focus` | `base_stat_focus + bonus_focus` | 0.0 – 100.0 |
| `stat_stamina` | `base_stat_stamina + bonus_stamina` | 50.0 – 200.0 (int) |
| `stat_salinity` | `base_stat_salinity + bonus_salinity_adj` | 0.0 – 100.0 |
| `stat_agility` | igual a `stat_focus` | — |
| `stat_charisma` | `0.0` (fijo al eclosionar) | — |
| `stat_wisdom` | `0.0` (fijo al eclosionar) | — |
| `stat_strength` | `0.0` (fijo al eclosionar) | — |

Los bonus acumulados en `WebitoIncubation` están limitados a ±50 (luck, focus, salinity) y ±60 (stamina) mediante `_clamp`.

---

## Campos adicionales relevantes

| Campo | Descripción |
|-------|-------------|
| `cpu_win_streak` | Racha consecutiva de victorias vs CPU. Se reinicia al perder. |
| `loyalty_points` | Puntos de afecto/lealtad acumulados (sistema de progresión pendiente). |
| `escrow_balance_gal` | FRJ en custodia del Axolotito (escrow interno). |
| `is_frozen_by_vip` | `True` si el dueño bajó de tier VIP y el slot extra fue revocado. |
| `is_main` | Marca al Axolotito principal del jugador. |
| `is_tutorial` | `True` si es el Axolotito creado durante el tutorial. |
| `blockchain_token_id` | Token ID en el contrato `Axolotitos.sol` (único en la cadena). |
| `dna_sequence` | Representación string del uint256 de ADN en cadena. |

Ver también: [[staking]], [[incubacion_imprinting]], [[patrones_ganadores]]


### expansion_cueva
> `mecanicas/expansion_cueva.md`

---
tags: [mecanicas, cueva, progresion]
description: "Los 8 niveles de expansión de cueva con costos, beneficios y requisitos exactos"
last_modified: "2026-06-07"
source_files: ["backend/app/api/v1/endpoints/cave_expansion.py"]
---

# Expansión de Cueva (Cenote) — 8 Niveles

El jugador tiene una sola cueva (Cenote) que se expande progresivamente hasta 8 niveles. Cada expansión requiere cumplir un logro de desbloq y pagar en FRJ. Los miembros VIP reciben un 50 % de descuento en FRJ y un 50 % menos de tiempo de excavación.

Aceleración de excavación: **4 AXF por hora restante** (redondeado arriba, mínimo 1 AXF).

---

## Tabla Completa de Niveles

| Nivel | Nombre | Spots Axo | Slots Decor | Mesa | Asientos | Excav. (h) | Costo FRJ | Huevo recompensa |
|-------|--------|-----------|-------------|------|----------|------------|-----------|-----------------|
| 1 | El Nicho | 1 | 2 | No | — | — | Gratis (tutorial) | — |
| 2 | La Gruta | 2 | 4 | No | — | 2.0 | 500 | fase1 |
| 3 | La Caverna | 3 | 6 | Sí | 2 | 6.0 | 1,500 | fase1_plus |
| 4 | El Salón | 4 | 8 | Sí | 4 | 12.0 | 4,000 | fase2 |
| 5 | El Santuario | 5 | 10 | Sí | 6 | 24.0 | 8,000 | fase2_nature |
| 6 | El Abismo | 6 | 12 | Sí | 8 | 36.0 | 15,000 | fase2_nature |
| 7 | El Templo | 7 | 14 | Sí | 8 | 48.0 | 30,000 | astral |
| 8 | Palacio Astral | 8 | 16 | Sí | 8 | 72.0 | 60,000 | astral |

**Nota VIP**: costo FRJ efectivo = `costo × 0.5`; tiempo excavación efectivo = `horas × 0.5`.

---

## Requisitos de Logro por Nivel

### Nivel 2 — La Gruta
- **Requisito**: 10 partidas jugadas (total) AND Axolotito principal nivel ≥ 3.

### Nivel 3 — La Caverna
- **Requisito**: 3 victorias totales AND racha de 3 días consecutivos jugando.

### Nivel 4 — El Salón
- **Requisito**: al menos 1 Jackpot ganado.

### Nivel 5 — El Santuario
- **Requisito**: Axolotito principal nivel ≥ 15.

### Nivel 6 — El Abismo
- **Requisito**: (50 partidas totales AND 100 alimentaciones a Axolotitos) OR ser VIP Coral, Dorado o Axolite.

### Nivel 7 — El Templo
- **Requisito**: (100 partidas totales AND 15 victorias totales) OR ser VIP Dorado o Axolite.

### Nivel 8 — Palacio Astral
- **Requisito**: (200 partidas totales AND poseer al menos un Axolotito con skin `gold` o `astral`) OR ser VIP Axolite.

---

## Descripción de Bonus Pasivos (`CAVE_PASSIVE_BONUSES`)

Los bonos son acumulativos: al llegar al nivel N se activan todos los bonos de los niveles anteriores.

| Nivel desbloqueado | Bonus pasivo | Descripción |
|-------------------|-------------|-------------|
| 1 | (ninguno) | Cueva inicial sin bonos |
| 2 | `gal_multiplier: 1.02` | +2 % sobre ganancias de FRJ (Frijolitos) |
| 3 | `extra_starting_card: True` | +1 carta en la mano inicial al comenzar partida |
| 4 | `booster_chance_bonus: 0.05` | +5 % de probabilidad de obtener booster como drop |
| 5 | `global_incubation_slot: 1` | +1 slot global de incubación de Webitos |
| 6 | `p2p_fee_reduction: 0.05` | -5 % de comisión en transacciones del mercado P2P |
| 7 | `monthly_foil_booster: 1` | 1 booster foil por mes |
| 8 | `axg_multiplier: 1.10` | +10 % de AXF en el ecosistema |

Los bonos multiplicativos (`gal_multiplier`, `axg_multiplier`) se multiplican entre sí si se acumulan; los aditivos (`booster_chance_bonus`, `p2p_fee_reduction`) se suman.

---

## Mecánica de Excavación

1. El jugador llama a `POST /api/v1/cave/expand` si cumple el logro y tiene FRJ suficientes.
2. Se descuenta el FRJ y se registra `cave_expansion_started_at` (timestamp de inicio) y `cave_expansion_target_level`.
3. La cueva no sube de nivel inmediatamente: hay un timer de excavación de 2 a 72 horas según el nivel.
4. Al hacer `GET /api/v1/cave/status`, el backend auto-verifica si el timer ya expiró y sube el nivel automáticamente, entregando el huevo de recompensa.
5. El jugador puede acelerar pagando AXF vía `POST /api/v1/cave/expand/accelerate` (ratio: 4 AXF/hora restante, ceil, mínimo 1 AXF).

### Truco de timestamp VIP
Para el descuento de tiempo VIP, el backend desplaza `cave_expansion_started_at` hacia el pasado en `(total_hours - effective_hours)` horas, de modo que el check de auto-completado (que siempre usa `total_hours` como referencia) se satisface antes.

---

## Slots de Staking derivados

La cantidad de Axolotitos que pueden hacer staking simultáneamente es `cave_level + 1` (ver [[staking]]).

---

## Tipos de Huevo de Recompensa

| Tipo | Descripción |
|------|-------------|
| `fase1` | Huevo estándar de fase 1 |
| `fase1_plus` | Huevo de fase 1 con rareza rara/épica/legendaria |
| `fase2` | Huevo de fase 2 (item_metadata `fase: 2`) |
| `fase2_nature` | Huevo de fase 2 (se usa la misma búsqueda que `fase2`) |
| `astral` | Huevo con `is_astral: true` en metadata, o nombre con "astral" |

Ver también: [[staking]], [[incubacion_imprinting]], [[estadisticas_axolotito]]


### gashapon
> `mecanicas/gashapon.md`

---
tags: [mecanicas, gashapon, capsulas]
description: "Sistema de cápsulas Gashapon: pity, probabilidades, recompensas del Ciclo Lunar"
last_modified: "2026-06-08"
source_files: ["backend/app/services/capsule_service.py", "backend/app/services/lunar_streak_service.py", "backend/app/services/daily_reward_service.py"]
---

# Cápsulas Gashapon

---

## Tiers de Cápsulas

| Tier | Costo FRJ | Pity (rolls sin Axolotito → garantía) |
|------|----------|--------------------------------------|
| Bronce | 1,500 | 12 |
| Plata | 5,000 | 6 |
| Oro | 20,000 | 4 |
| Triple Suerte | 22,500 | (aplica el pity de cada tier incluido) |

La Triple Suerte (`TRIPLE_COST = 22500.0`) incluye los tres tiers en un solo paquete. El costo base sumado sería 26,500 FRJ; los 22,500 representan un descuento aproximado del 15 % (ahorro de 4,000 FRJ).

Además, la Triple Suerte aplica **prevención de duplicados**: si un ítem ya salió en uno de los tiers de la misma tirada, el sistema intenta evitar repetirlo en los tiers siguientes (hasta 3 re-intentos).

---

## Tabla de Probabilidades — Pool Normal (`TIER_POOLS`)

Los breakpoints son **acumulados** (se compara contra un único roll `_rng.random()`):

### Bronce (1,500 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.55 | FRJ | 55 % |
| 0.55 – 0.83 | Carta | 28 % |
| 0.83 – 0.93 | Accesorio | 10 % |
| 0.93 – 0.98 | Sobre (booster) | 5 % |
| 0.98 – 1.00 | Carta Rara | 2 % |

### Plata (5,000 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.30 | FRJ | 30 % |
| 0.30 – 0.70 | Carta | 40 % |
| 0.70 – 0.85 | Accesorio | 15 % |
| 0.85 – 0.95 | Sobre (booster) | 10 % |
| 0.95 – 1.00 | Carta Rara | 5 % |

### Oro (20,000 FRJ)

| Rango | Outcome | Probabilidad |
|-------|---------|-------------|
| 0.00 – 0.12 | FRJ | 12 % |
| 0.12 – 0.55 | Carta | 43 % |
| 0.55 – 0.73 | Accesorio | 18 % |
| 0.73 – 0.85 | Sobre (booster) | 12 % |
| 0.85 – 1.00 | Carta Rara | 15 % |

---

## Rangos de FRJ al obtener outcome "gal" (`FRJ_RANGES`)

| Tier | FRJ mínimo | FRJ máximo |
|------|-----------|-----------|
| Bronce | 40 | 120 |
| Plata | 150 | 450 |
| Oro | 400 | 2,000 |

Los valores son `_rng.uniform(lo, hi)`, redondeados a 1 decimal.

---

## Rareza mínima de cartas y accesorios por tier

### Cartas (`TIER_CARD_RARITIES`)

| Tier | Rarezas posibles |
|------|----------------|
| Bronce | COMMON, RARE |
| Plata | RARE, EPIC |
| Oro | EPIC, LEGENDARY |

### Accesorios (`TIER_ACC_RARITIES`)

| Tier | Rarezas posibles |
|------|----------------|
| Bronce | COMMON |
| Plata | RARE |
| Oro | EPIC, LEGENDARY |

---

## Probabilidad de Booster Foil cuando sale "Sobre" (`FOIL_FROM_SOBRE`)

Dentro del outcome "sobre", hay un check secundario de que el booster sea FOIL:

| Tier | Probabilidad de Foil |
|------|---------------------|
| Bronce | 5 % |
| Plata | 12 % |
| Oro | 22 % |

---

## Drops Legendarios Pre-check (`CAPSULE_LEGENDARY_PROBS`)

Antes del pool normal, se evalúan drops especiales. Si sale, el pity se reinicia a 0 y no cuenta como roll normal:

| Tier | Booster Foil (pre-check) |
|------|------------------------|
| Bronce | 0.2 % |
| Plata | 0.5 % |
| Oro | 1.0 % |

Nota: el Webito Astral **ya no** se obtiene por cápsula directamente. Ahora se obtiene como recompensa al desbloquear el nivel 7 u 8 de la Cueva (ver [[expansion_cueva]]).

---

## Sistema Pity (`CapsulaPity`)

El modelo `CapsulaPity` en `backend/app/models/items.py` tiene tres contadores:

| Campo en BD | Tier al que corresponde | Threshold |
|------------|------------------------|-----------|
| `pity_cobre` | Bronce | 12 rolls sin Axolotito → garantía |
| `pity_plata` | Plata | 6 rolls sin Axolotito → garantía |
| `pity_oro` | Oro | 4 rolls sin Axolotito → garantía |

Nota histórica: el campo se llama `pity_cobre` (no `pity_bronce`) porque el tier se llamaba "Cobre" en una versión anterior. El mapeo actual en `capsule_service.py` es `PITY_FIELD_MAP = {"bronce": "pity_cobre", "plata": "pity_plata", "oro": "pity_oro"}`.

El pity se **reinicia a 0** cuando:
- Sale un Axolotito por el pool normal.
- Sale un drop legendario pre-check (Booster Foil).
- Sale una Tabla Forjada.

El pity **aumenta en 1** para todos los demás outcomes.

---

## Sistema de Ciclo Lunar (Recompensas Diarias)

El Ciclo Lunar reemplaza y unifica el sistema de cápsula diaria gratuita y las recompensas de racha. Se reclama una vez por día calendario (zona horaria Mexico City, UTC-6).

### Estructura del Ciclo

- **Loop 1 (días 1–6)**: cada día otorga FRJ según `DAILY_FRJ`.
- **Loop 2 (día 7)**: en lugar de FRJ, se otorgan cápsulas según la Luna activa (`LUNA_REWARDS`).
- **Loop 3 (ciclo completo)**: completar Luna 6 reinicia el ciclo a Luna 1 y suma 1 a `lunar_cycles_completed`.

### Recompensas FRJ diarias (`DAILY_FRJ`)

| Día | FRJ |
|-----|-----|
| 1 | 50 |
| 2 | 65 |
| 3 | 80 |
| 4 | 95 |
| 5 | 110 |
| 6 | 130 |
| 7 | Cápsulas según Luna activa |

### Recompensas del Día 7 por Luna (`LUNA_REWARDS`)

| Luna | Recompensa |
|------|-----------|
| 1 | 1× Cápsula Bronce |
| 2 | 2× Cápsulas Bronce |
| 3 | 1× Cápsula Plata |
| 4 | 1× Cápsula Plata + 1× Cápsula Bronce |
| 5 | 2× Cápsulas Plata |
| 6 | 1× Cápsula Oro |

### Reglas de Racha

| Condición | Efecto |
|-----------|--------|
| Gap ≤ 1 día | La racha continúa normalmente |
| Gap > 1 día y ≤ 7 días | `lunar_streak_day` se reinicia a 0, pero la Luna (semana) no cambia |
| Gap > 7 días | `lunar_streak_day` se reinicia a 0 Y `lunar_week` vuelve a Luna 1 |

### Recompensas Diarias Legacy (`DailyRewardService`)

El archivo `daily_reward_service.py` contiene un sistema anterior más simple, aún presente en el código:

| Día de racha | FRJ | Fórmula |
|-------------|-----|---------|
| 1 | 15 | base |
| 2 | 20 | base + 1×5 |
| 3 | 25 | base + 2×5 |
| 4 | 30 | base + 3×5 |
| 5 | 35 | base + 4×5 |
| 6 | 40 | base + 5×5 |
| 7 | 45 | base + 6×5 (máximo) |

- `BASE_REWARD = 15.0 FRJ`
- `STREAK_BONUS = 5.0 FRJ por día consecutivo`
- `MAX_STREAK = 7 días`

Este servicio legacy puede estar activo en paralelo o reemplazado por el Ciclo Lunar — (verificar manualmente qué endpoint lo usa actualmente).

---

## Relacion Costo-Beneficio

Basándose en los datos del código:

- **Bronce**: mayor probabilidad de FRJ (55 %), bueno para acumular capsulas baratas. Pity en 12 asegura carta rara cada 12 rolls como máximo.
- **Plata**: mejor balance carta/accesorio, pity en 6 rolls.
- **Oro**: 15 % base de carta rara sin depender del pity, drops legendarios 5× más frecuentes que Bronce. Mayor cantidad de FRJ posible (400–2,000 por drop de FRJ). Pity garantizado en solo 4 rolls.

El Ciclo Lunar (día 7 en Luna 6) entrega 1 Cápsula Oro gratis, equivalente a 20,000 FRJ de valor nominal, cada 6 semanas de juego consistente.

Ver también: [[incubacion_imprinting]], [[expansion_cueva]], [[estadisticas_axolotito]]


### incubacion_imprinting
> `mecanicas/incubacion_imprinting.md`

---
tags: [mecanicas, incubacion, crianza]
description: "Sistema de incubación de huevos Webito e imprinting con Axolotitos padrinos"
last_modified: "2026-06-07"
source_files: ["backend/app/models/items.py:WebitoIncubation", "backend/app/services/incubation_service.py", "backend/app/services/imprinting_service.py"]
---

# Incubación e Imprinting

Los Webitos son huevos que se incuban mediante calor (clicks) y cuidados. El sistema de imprinting permite que un Axolotito padrino moldee los stats del Axolotito que nacerá.

---

## Modelo WebitoIncubation — Campos Completos

### Sistema Térmico del Huevo

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `calor_actual` | float | 0.0 | Temperatura del huevo, rango 0–100 %. Sube con clicks. |
| `clicks_hoy` | int | 0 | Clicks recibidos en el día actual. |
| `clicks_totales` | int | 0 | Total histórico de clicks. |
| `is_frozen` | bool | False | Si el huevo está congelado (pierde calor en lugar de ganarlo). |
| `frozen_clicks_left` | int | 0 | Clicks restantes en estado congelado antes de volver a la normalidad. |
| `protected_until` | datetime | null | Timestamp hasta el que el huevo no puede ser dañado. |
| `genetic_purity` | float | 100.0 | Pureza genética del huevo. Decrece con eventos negativos durante la incubación. |
| `fecha_inicio` | datetime | utcnow | Fecha de inicio de la incubación. |
| `fecha_eclosion_estimada` | datetime | requerido | Fecha estimada de eclosión. |
| `ultimo_click` | datetime | utcnow | Timestamp del último click recibido. |

### Sistema de Cuidados (Cariñitos)

Tres tipos de cuidado con cooldowns distintos. Los bonos se acumulan en los campos `bonus_*` y se aplican al nacer.

| Tipo de cuidado | Campo timestamp | Cooldown | Stat bonificado |
|----------------|----------------|----------|----------------|
| Acariciar (petting) | `last_petting` | 4 horas | `bonus_strength` y `bonus_agility` |
| Cantarle (singing) | `last_singing` | 8 horas | `bonus_wisdom` y `bonus_focus` |
| Alimentar (feeding) | `last_feeding` | 12 horas | `bonus_stamina` y `bonus_luck` |

Los cooldowns **no están definidos en `items.py`** con constantes explícitas; el valor "4h / 8h / 12h" proviene del comentario en el campo del modelo. Verificar en el endpoint de incubación si difieren.

### Campos de Bonus Acumulados (cuidados)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `bonus_strength` | 0.0 | Acumulado por acariciar |
| `bonus_agility` | 0.0 | Acumulado por acariciar |
| `bonus_wisdom` | 0.0 | Acumulado por cantarle |
| `bonus_focus` | 0.0 | Acumulado por cantarle (también afectado por imprinting) |
| `bonus_stamina` | 0.0 | Acumulado por alimentar (también afectado por imprinting) |
| `bonus_luck` | 0.0 | Acumulado por alimentar (también afectado por imprinting) |

---

## Sistema de Imprinting con Padrino Axolotito

El imprinting reemplaza al sistema de cooldown de cuidados: en lugar de clicks, es el padrino quien juega partidas y su desempeño moldea los stats del Webito.

### Juegos Requeridos por Rareza del Huevo

Definido en `imprinting_service.py`, constante `_REQUIRED_GAMES`:

| Rareza del huevo | Juegos de imprinting requeridos |
|-----------------|--------------------------------|
| common | 3 |
| rare | 5 |
| epic | 7 |
| legendary | 7 |

Cuando `imprinting_games_played >= required`, el campo `imprinting_complete` se pone en `True` y el ADN queda sellado.

### Campos de Imprinting en WebitoIncubation

| Campo | Default | Descripción |
|-------|---------|-------------|
| `imprinting_games_played` | 0 | Partidas completadas con el padrino. |
| `imprinting_padrino_id` | null | ID del Axolotito que actúa como padrino. |
| `base_stat_luck` | 0.0 | Stat base de suerte (asignado al iniciar imprinting). |
| `base_stat_focus` | 0.0 | Stat base de concentración. |
| `base_stat_stamina` | 0.0 | Stat base de stamina. |
| `base_stat_salinity` | 0.0 | Stat base de salinidad. |
| `bonus_salinity_adj` | 0.0 | Ajuste de salinidad acumulado durante imprinting. |
| `imprinting_complete` | False | True cuando el ADN está sellado y listo para eclosionar. |

---

## Herencia Genética

Los stats base se generan al iniciar el imprinting (`imprinting_service.py → initial_base_stats`):

```
base_luck    = random(20.0, 50.0) + padrino.stat_luck    × factor
base_focus   = random(25.0, 55.0) + padrino.stat_focus   × factor
base_stamina = random(70.0, 110.0) + padrino.stat_stamina × factor
base_salinity = random(10.0, 30.0) + padrino.stat_salinity × factor
```

- `factor = 0.10` si `padrino.level <= 20`
- `factor = 0.15` si `padrino.level > 20`

### Deltas por Partida (imprinting_service.py → compute_deltas)

Los deltas se acumulan en `bonus_luck`, `bonus_focus`, `bonus_stamina`, `bonus_salinity_adj`.

**Suerte (luck_delta)**

| Condición | Delta |
|-----------|-------|
| Padrino tuvo jackpot | +20.0 (fijo) |
| Padrino ganó | +random(8.0, 15.0) |
| Padrino perdió | -random(8.0, 12.0) |

**Concentración (focus_delta)**

| Condición | Delta base |
|-----------|-----------|
| mark_accuracy ≥ 0.80 | +random(10.0, 18.0) |
| mark_accuracy ≤ 0.50 | -random(8.0, 14.0) |
| padrino_energy_pct > 0.80 | +5.0 adicional |

**Stamina (stamina_delta)**

| Condición | Delta |
|-----------|-------|
| session_game_count ≥ 3 | +random(10.0, 15.0) |
| session_game_count == 1 | -5.0 |
| padrino_energy_pct > 0.80 | +8.0 adicional |

**Salinidad (salinity_delta)**

| Condición | Delta |
|-----------|-------|
| padrino_sal < 20.0 | -random(6.0, 10.0) |
| padrino_sal > 50.0 | +random(8.0, 12.0) |
| mark_accuracy < 0.40 | +5.0 adicional |

### Clamps de bonus acumulados

| Bonus | Rango permitido |
|-------|----------------|
| `bonus_luck` | -50.0 – +50.0 |
| `bonus_focus` | -50.0 – +50.0 |
| `bonus_stamina` | -60.0 – +60.0 |
| `bonus_salinity_adj` | -50.0 – +50.0 |

### Genetic Purity

El campo `genetic_purity` (default 100.0) existe en el modelo. Su lógica de reducción no está definida en `imprinting_service.py` ni `incubation_service.py` — (dato no encontrado en código — verificar manualmente en el endpoint de incubación).

---

## Tutorial de Incubación

Campos del tutorial en `WebitoIncubation`:

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `tutorial_phase` | int | 0 | Fase activa: 0 = sin tutorial, 1–3 = activo, 4 = karma, 5 = completo |
| `tutorial_act_index` | int | 0 | Acto exacto del script del tutorial (0–11) |
| `tutorial_karma` | str | null | Karma resultante: `"lucky"` o `"salty"` |
| `tutorial_board_card_ids` | list | null | 16 card IDs determinísticos para el tablero del tutorial |

Las fases 0–5 definen el progreso del tutorial de incubación:

| Fase | Descripción |
|------|-------------|
| 0 | Sin tutorial activo (huevo real o no iniciado) |
| 1–3 | Tutorial activo — el jugador recibe instrucciones guiadas |
| 4 | Fase de karma — se determina si el Axolotito nacerá con karma `lucky` o `salty` |
| 5 | Tutorial completo — el Axolotito nació |

La lógica detallada de cada acto (0–11) del script del tutorial no está en `incubation_service.py` — (dato no encontrado en código — verificar en `tutorial_service.py`).

---

## Stats Finales al Eclosionar

```
stat_luck     = clamp(base_stat_luck + bonus_luck, 0.0, 100.0)
stat_focus    = clamp(base_stat_focus + bonus_focus, 0.0, 100.0)
stat_stamina  = int(clamp(base_stat_stamina + bonus_stamina, 50.0, 200.0))
stat_salinity = clamp(base_stat_salinity + bonus_salinity_adj, 0.0, 100.0)
stat_agility  = stat_focus  (alias)
stat_charisma = 0.0
stat_wisdom   = 0.0
stat_strength = 0.0
```

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]], [[gashapon]]


### patrones_ganadores
> `mecanicas/patrones_ganadores.md`

---
tags: [mecanicas, juego, patrones]
description: "Los patrones ganadores del juego con grids ASCII y índices exactos de cada celda"
last_modified: "2026-06-07"
source_files: ["backend/app/services/game_logic.py"]
---

# Patrones Ganadores

El tablero de Lotería es una grilla 4×4 con índices 0–15 en orden row-major:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

`X` = celda requerida, `.` = celda libre.

---

## Patrón: `line` — Línea recta (10 variantes)

Cualquiera de las 10 líneas de la constante `WINNING_LINES` en `game_logic.py`.

### Filas (4 variantes)

**Fila 0**
```
X X X X
. . . .
. . . .
. . . .
```
Índices: `{0, 1, 2, 3}`

**Fila 1**
```
. . . .
X X X X
. . . .
. . . .
```
Índices: `{4, 5, 6, 7}`

**Fila 2**
```
. . . .
. . . .
X X X X
. . . .
```
Índices: `{8, 9, 10, 11}`

**Fila 3**
```
. . . .
. . . .
. . . .
X X X X
```
Índices: `{12, 13, 14, 15}`

### Columnas (4 variantes)

**Columna 0**
```
X . . .
X . . .
X . . .
X . . .
```
Índices: `{0, 4, 8, 12}`

**Columna 1**
```
. X . .
. X . .
. X . .
. X . .
```
Índices: `{1, 5, 9, 13}`

**Columna 2**
```
. . X .
. . X .
. . X .
. . X .
```
Índices: `{2, 6, 10, 14}`

**Columna 3**
```
. . . X
. . . X
. . . X
. . . X
```
Índices: `{3, 7, 11, 15}`

### Diagonales (2 variantes)

**Diagonal principal (↘)**
```
X . . .
. X . .
. . X .
. . . X
```
Índices: `{0, 5, 10, 15}`

**Diagonal anti-principal (↙)**
```
. . . X
. . X .
. X . .
X . . .
```
Índices: `{3, 6, 9, 12}`

**Total variantes `line`: 10**

---

## Patrón: `cuadrito` — Cuadrado 2×2 (9 variantes)

Definido en `WINNING_CUADRITOS`. Cualquiera de los nueve cuadrados 2×2 posibles.

**Cuadrito (0,1,4,5) — superior izquierdo**
```
X X . .
X X . .
. . . .
. . . .
```
Índices: `{0, 1, 4, 5}`

**Cuadrito (1,2,5,6)**
```
. X X .
. X X .
. . . .
. . . .
```
Índices: `{1, 2, 5, 6}`

**Cuadrito (2,3,6,7) — superior derecho**
```
. . X X
. . X X
. . . .
. . . .
```
Índices: `{2, 3, 6, 7}`

**Cuadrito (4,5,8,9)**
```
. . . .
X X . .
X X . .
. . . .
```
Índices: `{4, 5, 8, 9}`

**Cuadrito (5,6,9,10) — centro**
```
. . . .
. X X .
. X X .
. . . .
```
Índices: `{5, 6, 9, 10}`

**Cuadrito (6,7,10,11)**
```
. . . .
. . X X
. . X X
. . . .
```
Índices: `{6, 7, 10, 11}`

**Cuadrito (8,9,12,13)**
```
. . . .
. . . .
X X . .
X X . .
```
Índices: `{8, 9, 12, 13}`

**Cuadrito (9,10,13,14)**
```
. . . .
. . . .
. X X .
. X X .
```
Índices: `{9, 10, 13, 14}`

**Cuadrito (10,11,14,15) — inferior derecho**
```
. . . .
. . . .
. . X X
. . X X
```
Índices: `{10, 11, 14, 15}`

**Total variantes `cuadrito`: 9**

---

## Patrón: `pocito` — Centro 2×2 (1 variante)

Definido en `WINNING_POCITO = frozenset({5, 6, 9, 10})`.

```
. . . .
. X X .
. X X .
. . . .
```
Índices: `{5, 6, 9, 10}`

**Total variantes `pocito`: 1**

---

## Patrón: `esquinas` — 4 Esquinas (1 variante)

Definido en `WINNING_ESQUINAS = frozenset({0, 3, 12, 15})`.

```
X . . X
. . . .
. . . .
X . . X
```
Índices: `{0, 3, 12, 15}`

**Total variantes `esquinas`: 1**

---

## Patrón: `cruz` — Cruz recta (función `check_cruz_recta`)

Cualquier fila completa + cualquier columna completa simultáneas. 4 filas × 4 columnas = **16 variantes** posibles. Las celdas de intersección solo se requieren una vez.

Ejemplo (fila 0 + columna 0):
```
X X X X
X . . .
X . . .
X . . .
```
Índices variables según la fila y columna elegidas.

**Total variantes `cruz`: 16**

---

## Patrón: `cruz_diagonal` — La X (1 variante)

Definido en `WINNING_CRUZ_DIAGONAL = frozenset({0, 3, 5, 6, 9, 10, 12, 15})`.

```
X . . X
. X X .
. X X .
X . . X
```
Índices: `{0, 3, 5, 6, 9, 10, 12, 15}`

**Total variantes `cruz_diagonal`: 1**

---

## Patrón: `l_shape` — Forma L (4 variantes)

Definido en `WINNING_L_SHAPES`. Una esquina + su fila completa + su columna completa.

**L top-left**
```
X X X X
X . . .
X . . .
X . . .
```
Índices: `{0, 1, 2, 3, 4, 8, 12}`

**L top-right**
```
X X X X
. . . X
. . . X
. . . X
```
Índices: `{0, 1, 2, 3, 7, 11, 15}`

**L bottom-left**
```
X . . .
X . . .
X . . .
X X X X
```
Índices: `{0, 4, 8, 12, 13, 14, 15}`

**L bottom-right**
```
. . . X
. . . X
. . . X
X X X X
```
Índices: `{3, 7, 11, 12, 13, 14, 15}`

**Total variantes `l_shape`: 4**

---

## Patrón: `z_shape` — Forma Z/S (2 variantes)

Definido en `WINNING_Z_SHAPES`. Fila superior + 2 celdas diagonales medias + fila inferior.

**Z**
```
X X X X
. . X .
. X . .
X X X X
```
Índices: `{0, 1, 2, 3, 6, 9, 12, 13, 14, 15}`

**S (Z espejo)**
```
X X X X
. X . .
. . X .
X X X X
```
Índices: `{0, 1, 2, 3, 5, 10, 12, 13, 14, 15}`

**Total variantes `z_shape`: 2**

---

## Patrón: `full_board` — Tablero lleno (1 variante)

Verificado en `check_full_board`: `len(marked) == 16`. Todas las 16 celdas marcadas.

```
X X X X
X X X X
X X X X
X X X X
```
Índices: `{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}`

**Total variantes `full_board`: 1**

---

## Patrones activos por sala

| Sala | Modo | Patrones habilitados |
|------|------|----------------------|
| `rookie_pool` / `rookie` | Fácil | `line`, `cuadrito` |
| `champion_abyss` / `champion` | Difícil | `line`, `cuadrito`, `pocito`, `esquinas` |

Los patrones `cruz`, `cruz_diagonal`, `l_shape`, `z_shape`, `full_board` existen en el código (`PATTERN_CHECKERS`) pero no están asignados a ninguna sala en `ROOM_CONFIG`. Se usan en `validate_win` para validación de backend.

---

## Resumen de totales

| Patrón | Variantes |
|--------|-----------|
| `line` | 10 |
| `cuadrito` | 9 |
| `pocito` | 1 |
| `esquinas` | 1 |
| `cruz` | 16 |
| `cruz_diagonal` | 1 |
| `l_shape` | 4 |
| `z_shape` | 2 |
| `full_board` | 1 |
| **Total** | **45** |

---

## Sistema de Tensión

`check_tension_status` en `game_logic.py` evalúa los tableros de todos los jugadores y devuelve un nivel de tensión:

| Nivel | Condición |
|-------|-----------|
| `low` | Ninguna hot_line activa |
| `medium` | Al menos 1 hot_line (≤2 celdas faltantes en cualquier patrón) |
| `high` | Al menos 2 jugadores a ≤2 celdas de ganar |
| `critical` | Al menos 1 jugador a ≤1 celda de ganar |

Una "hot_line" se activa cuando un jugador tiene ≤2 celdas faltantes para completar una `line` o un `cuadrito`.

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]]


### staking
> `mecanicas/staking.md`

---
tags: [mecanicas, staking, economia]
description: "Sistema de staking: multiplicadores por rareza de skin y partes, tasa de emisión FRJ/hora"
last_modified: "2026-06-07"
source_files: ["backend/app/services/staking_service.py"]
---

# Staking — Ganancias Pasivas de FRJ

Los Axolotitos generan FRJ (Frijolitos) pasivamente mientras su dueño siga jugando al menos 1 partida cada 24 horas (regla Play-to-Stake).

---

## Multiplicadores por Color de Skin

El color de skin determina la rareza, y la rareza determina el multiplicador base por hora.

### Mapeo skin_color → rareza (`SKIN_RARITY_MAP`)

| skin_color | Rareza |
|-----------|--------|
| `pink` | comun |
| `gray` | comun |
| `gray_light` | comun |
| `gray_dark` | comun |
| `cyan` | rara |
| `purple` | rara |
| `neon` | epica |
| `coral` | epica |
| `gold` | legendaria |
| `astral` | astral |

Cualquier color no listado se trata como `comun`.

### Multiplicador base por rareza (`SKIN_MULTIPLIER`, FRJ/hora)

| Rareza | FRJ/hora (skin base) |
|--------|---------------------|
| comun | 0.05 |
| rara | 0.15 |
| epica | 0.40 |
| legendaria | 1.00 |
| astral | 2.50 |

---

## Bonus por Rareza de Partes

Cada una de las 6 partes corporales contribuye con un bonus adicional de FRJ/hora según su rareza. Si un valor de trait no está mapeado, se trata como `comun` (0.01 FRJ/hora).

### `PARTS_BONUS_BY_RARITY`

| Rareza de parte | Bonus FRJ/hora |
|----------------|---------------|
| comun | 0.01 |
| rara | 0.03 |
| epica | 0.08 |
| legendaria | 0.20 |

### Rareza de cada trait (`_TRAIT_RARITY`)

**gill_type (branquias)**

| Valor | Rareza |
|-------|--------|
| `short` | comun |
| `normal` | comun |
| `feathery` | rara |
| `crown` | epica |
| `phoenix` | legendaria |

**eye_type (ojos)**

| Valor | Rareza |
|-------|--------|
| `cute` | comun |
| `derp` | comun |
| `dreamer` | rara |
| `cool` | epica |
| `zen` | legendaria |

**mouth_type (boca)**

| Valor | Rareza |
|-------|--------|
| `flat` | comun |
| `smile` | comun |
| `fang` | rara |
| `rockstar` | epica |
| `divine` | legendaria |

**tail_type (cola)**

| Valor | Rareza |
|-------|--------|
| `standard` | comun |
| `wavy` | comun |
| `betta` | rara |
| `plasma` | epica |

**forehead_type (frente)**

| Valor | Rareza |
|-------|--------|
| `none` | comun |
| `stripes` | comun |
| `gem` | rara |
| `halo` | epica |

**limb_type (extremidades)**

| Valor | Rareza |
|-------|--------|
| `soft` | comun |
| `claws` | comun |
| `scales` | rara |
| `coral` | epica |

Nota: `tail_type`, `forehead_type` y `limb_type` no tienen variantes `legendaria` en la tabla actual.

---

## Fórmula Completa de Tasa Horaria

Definida en `StakingService.calculate_axolotito_hourly_rate`:

```
hourly_rate = SkinMultiplier × (1 + 0.1 × level) + SUM(PartsBonus)
```

- **SkinMultiplier**: valor de `SKIN_MULTIPLIER` según rareza del `skin_color`.
- **level**: campo `level` del Axolotito (comienza en 1).
- **SUM(PartsBonus)**: suma de los bonus de las 6 partes (`gill_type`, `eye_type`, `mouth_type`, `tail_type`, `forehead_type`, `limb_type`).

### Ejemplos de cálculo

**Axolotito mínimo** (skin pink, nivel 1, todas las partes comun):
```
0.05 × (1 + 0.1×1) + (0.01×6) = 0.05 × 1.1 + 0.06 = 0.055 + 0.06 = 0.115 FRJ/hora
```

**Axolotito máximo teórico** (skin astral, nivel con partes legendarias):
```
2.50 × (1 + 0.1×nivel) + (0.20×3 + 0.08×3)  [3 legendarias + 3 épicas, aproximación]
```

---

## Regla Play-to-Stake

- **Condición**: el jugador debe haber completado al menos 1 partida en las últimas 24 horas.
- **Campo evaluado**: `user.last_play_date` comparado contra `datetime.utcnow() - timedelta(hours=24)`.
- **Si inactivo**: `calculate_accrued_frj` retorna `0.0` y no se acumula nada.
- **Constante**: `PLAY_TO_STAKE_HOURS = 24`

---

## Cap de Acumulación

- **Máximo de acumulación**: `MAX_ACCUMULATION_HOURS = 12` horas.
- El Axolotito nunca acumula más de `12 × hourly_rate` FRJ sin reclamar, incluso si pasan más de 12 horas.
- Al reclamar por primera vez (`last_staking_claim is None`), se otorga directamente el equivalente a 12 horas.

---

## Slots de Staking

La cantidad de Axolotitos que pueden generar staking simultáneamente depende del nivel de cueva del usuario:

```
staking_slots = user.cave_level + 1
```

| Nivel de cueva | Slots de staking |
|---------------|-----------------|
| 1 (El Nicho) | 2 |
| 2 (La Gruta) | 3 |
| 3 (La Caverna) | 4 |
| 4 (El Salón) | 5 |
| 5 (El Santuario) | 6 |
| 6 (El Abismo) | 7 |
| 7 (El Templo) | 8 |
| 8 (Palacio Astral) | 9 |

Para aumentar slots se debe expandir la cueva (ver [[expansion_cueva]]).

---

## Cómo Calcular Tu Ganancia Estimada

```
ganancia_estimada = hourly_rate × horas_activas
```

Donde `horas_activas` es el tiempo transcurrido desde el último claim, con tope en `MAX_ACCUMULATION_HOURS = 12`.

Si tienes múltiples Axolotitos, la ganancia total es la suma de cada uno hasta sus respectivos caps individuales.

Ver también: [[estadisticas_axolotito]], [[expansion_cueva]]



---

## Jugadores

### axolotitos
> `jugadores/axolotitos.md`

---
tags: [jugadores, axolotitos]
description: "Guía en español para jugadores sobre los Axolotitos — mascotas, stats, energía y cuidados"
last_modified: "2026-06-07"
audience: jugadores
---

# Axolotitos — Tu Mascota y Jugador

Los Axolotitos son el corazón de Axolotto. No son solo una imagen bonita — son tu **jugador dentro del juego**, y sus características afectan directamente cuánto ganas o pierdes en cada partida.

---

## ¿Qué es un Axolotito?

Es una criatura digital única, inspirada en el ajolote mexicano (*Ambystoma mexicanum*), ese anfibio rarísimo que solo se encuentra en Xochimilco. En el juego, cada Axolotito tiene:

- **Apariencia única**: combinación de color de piel, tipo de branquias, forma de ojos, cola y extremidades. Nunca habrá dos exactamente iguales.
- **Estadísticas únicas**: determina qué tan bien juega en cada partida.
- **Nivel**: sube con la experiencia ganada jugando partidas.
- **Energía**: se gasta con cada partida y se recupera durmiendo.

Tu Axolotito juega **automáticamente** mientras tú haces otra cosa. Lo configuras, lo mandas a una sala, y cuando termina le cobras los resultados.

---

## ¿Por qué importa tu Axolotito?

Imagina que mandas a un amigo a jugar lotería en tu nombre. Si tu amigo es distraído, va a fallar cartas que debería haber marcado. Si tiene buena suerte, puede salvarse en momentos clave. Si se cansa rápido, se va antes de tiempo.

Exactamente así funcionan las stats de tu Axolotito:

- Un Axolotito con **mucho Enfoque** casi nunca falla una carta cantada — marca todo correcto
- Un Axolotito con **mucha Suerte** puede salvarse de perder en situaciones límite
- Un Axolotito con **mucha Energía** aguanta más partidas antes de necesitar descanso

Invertir en un buen Axolotito, o subir de nivel al que ya tienes, se nota directamente en tus resultados.

---

## Estadísticas explicadas en simple

Tu Axolotito tiene 8 stats. Aquí te las explico sin tecnicismos:

| Stat | Nombre técnico | ¿Qué hace en el juego? |
|------|---------------|------------------------|
| **Enfoque** | Focus | Qué tan seguido falla al marcar cartas cantadas. Más Enfoque = menos errores = más cartas marcadas correctamente |
| **Suerte** | Luck | Chance de salvarse de perder en momentos críticos. También sube el multiplicador de premios especiales |
| **Energía** | Stamina | Cuántas partidas puede jugar antes de quedarse agotado y necesitar dormir |
| **Salinidad** | Salinity | El "mala suerte" del Axolotito. A más Salinidad, más chance de que pase algo negativo. Quieres esta BAJA |
| **Carisma** | Charisma | Descuentos en la tienda del criadero — el Axolotito "negocia" mejor los precios |
| **Agilidad** | Agility | Resiste mejor los efectos del clima en salas avanzadas — el frío de Xochimilco le afecta menos |
| **Sabiduría** | Wisdom | Maneja mejor las situaciones adversas durante la partida |
| **Fuerza** | Strength | Aguanta más los eventos negativos en salas difíciles de alto riesgo |

**Los más importantes para empezar:** Enfoque y Suerte. Estos dos tienen el impacto más directo en tus resultados diarios. La Salinidad también importa — si está muy alta, tu Axolotito tendrá mala racha seguido.

---

## Cómo subir el nivel de tu Axolotito

Cada vez que tu Axolotito juega una partida, gana **XP (puntos de experiencia)**:

| Sala | XP por GANAR | XP por PERDER |
|------|-------------|--------------|
| Charco de Novatos (Rookie) | 35 XP | 8 XP |
| Fosa del Campeón (Champion) | 75 XP | 15 XP |

Al acumular suficiente XP, el Axolotito sube de nivel. Cada nivel aumenta ligeramente sus stats base. No hay un tope fijo de nivel — entre más juegues, más crece.

**Consejo:** No te preocupes si pierdes partidas. Igual ganas XP. Las derrotas son parte del entrenamiento.

---

## Cómo alimentar y cuidar a tu Axolotito

Un Axolotito bien cuidado juega mejor y se recupera más rápido. En la pantalla del Nido puedes cuidarlo:

### Alimentación

| Alimento | Precio | Efecto |
|----------|--------|--------|
| Algae Pellet (Alimento Común) | 30 FRJ | Recuperación básica de energía |
| Brine Shrimp (Alimento Premium) | 150 FRJ | Recuperación mayor, pequeño boost temporal |

Alimentarlo regularmente ayuda a mantener sus stats en buen estado y acelera la recuperación de energía.

### Descanso

El Axolotito necesita dormir para recuperar energía después de jugar. Puedes:
- **Dejarlo descansar naturalmente** — recupera energía con el tiempo (gratis)
- **Usar Gotas Anti-Escarcha** (200 FRJ) — aceleran procesos en el Nido

### Personalidades

Al nacer, tu Axolotito recibe una personalidad que modifica un poco su comportamiento:

| Personalidad | Lo bueno | Lo malo |
|-------------|----------|---------|
| **Metódico** | +15% Enfoque (falla menos cartas) | Gasta 10% más energía por partida |
| **Suertudo** | +15% Suerte (más salvadas y drops raros) | -5% Agilidad |
| **Hiperactivo** | Se recupera 20% más rápido de energía | 10% más de probabilidad de fallar cartas |

---

## ¿Qué pasa si se queda sin energía?

Si tu Axolotito se agota, entra en estado **Durmiendo**. Mientras duerme:
- No puede entrar a salas ni jugar partidas
- No puedes interactuar con él
- Se recupera solo con el tiempo

Cuando termina de descansar, vuelve a estar disponible al 100% de energía.

**¿Cuándo se agota?** Depende de su stat de Energía. Los Axolotitos con Energía alta aguantan muchas más partidas antes de necesitar descanso.

**¿Y si un Axolotito está "en partida"?** Mientras juega, está en modo **Jugando** y tampoco puedes interrumpirlo. Cuando la sesión termina entra en modo **Esperando Reporte** — ahí sí puedes cobrar los resultados y mandarlo a descansar.

---

## Rareza visual — colores y apariencia

Los Axolotitos tienen diferente rareza visual según su apariencia. Los colores más raros (como el Axolotito translúcido o el dorado) no solo se ven increíbles sino que tienen más valor en el mercado P2P.

La rareza visual **no afecta directamente las stats del juego**, pero sí afecta el **staking pasivo** — un Axolotito de mayor rareza visual puede generar más FRJ/hora cuando está en tu Nido descansando (detalle sujeto a la fase actual del juego).

Los Axolotitos más raros nacen de Webitos especiales como el **Webito Astral** (3,000 AXF) o el **Webito Génesis** (400 AXF).

---

## ¿Cuántos Axolotitos puedo tener?

| Estado VIP | Slots disponibles |
|-----------|-----------------|
| Sin VIP | 6 Axolotitos máximo |
| VIP Axolite | 7 Axolotitos |

Si tienes VIP Axolite activo y se te vence, el séptimo Axolotito (el del slot extra) se **congela** — sigue siendo tuyo pero no puede jugar ni generar nada hasta que renueves. Ve a [[vip]] para más detalles.

---

## Preguntas frecuentes

**¿Mi Axolotito puede morir para siempre?**
No. Los Axolotitos no mueren. Solo se quedan sin energía y necesitan dormir. Siempre van a estar ahí.

**¿Qué tan seguido tengo que revisar a mi Axolotito?**
No tienes que estar pegado al juego. Puedes configurar la sesión, irte a hacer tus cosas, y revisar cuando quieras. El juego te avisa cuando la sesión termina.

**¿Vale la pena comprar un Webito caro para tener mejores stats?**
Un Webito más caro da más probabilidades de mejores stats al nacer, pero no es garantía. El Axolotito de inicio que te regala el juego está bien para aprender. Cuando ya sepas qué stats te convienen más, ahí sí tiene sentido invertir en un Webito bueno.

**¿Puedo tener varios Axolotitos jugando al mismo tiempo?**
Sí, mientras tengas slots disponibles. Cada Axolotito puede estar en una sala diferente al mismo tiempo. Más Axolotitos = más partidas simultáneas = más FRJ ganados.

---

→ Ver cómo conseguir más Axolotitos en [[tienda]] · Entender el multijugador en [[multijugador]] · Beneficios VIP en [[vip]]


### capsulas
> `jugadores/capsulas.md`

---
tags: [jugadores, capsulas]
description: "Guía en español para jugadores sobre las cápsulas Gashapon — tiers, pity system y recompensa diaria"
last_modified: "2026-06-07"
audience: jugadores
---

# Cápsulas Gashapon — La Máquina de Premios

¿Conoces esas máquinas de juguetitos de 5 pesos con bolita de plástico que girabas en los supermercados? Axolotto tiene su versión digital — los **Gashapon**. Metes FRJ, giras la cápsula, y puede salirte desde una carta común hasta un Axolotito rarísimo.

---

## ¿Qué son las cápsulas Gashapon?

Son **máquinas de premios aleatorios** que se compran con FRJ (Frijolitos). Cada cápsula tiene un costo diferente y premia con items distintos — cartas de lotería, consumibles, o en el mejor de los casos, un Axolotito.

La gracia del Gashapon es que **no sabes exactamente qué vas a sacar** — hay un pool de premios posibles y el sistema elige uno al azar. A mayor tier de la cápsula, mejores chances de sacar algo bueno.

---

## Los Cuatro Tiers de Cápsulas

| Cápsula | Costo FRJ | ¿Qué puedes ganar? |
|---------|----------|-------------------|
| **Bronce** | 1,500 FRJ | Cartas comunes, consumibles básicos, FRJ extras |
| **Plata** | 5,000 FRJ | Cartas poco comunes o raras, consumibles, pequeña chance de Axolotito |
| **Oro** | 20,000 FRJ | Cartas raras a épicas, chance alta de Axolotito, items premium |
| **Triple Suerte** | 22,500 FRJ | Pack de 3 cápsulas con probabilidades mejoradas |

### Bronce — 1,500 FRJ

La más accesible. Perfecta para abrirla cuando acumulas FRJ del día a día sin gastarlos en salas. Los premios son modestos — cartas comunes, FRJ de consolación, alimentos básicos para tu Axolotito — pero se llegan a sacar cartas poco comunes también.

**¿Cuándo usarla?** Cuando tienes FRJ de sobra y no los necesitas para salas. También es la cápsula gratuita de los VIPs — recibes 2 cada mes con Coral, 2 con Dorado y 3 con Axolite.

### Plata — 5,000 FRJ

El salto de calidad. Aquí ya hay chances reales de sacar cartas raras que suben el valor de tus tablas. Si juntas FRJ jugando seguido, esta es la que más te conviene para construir colección.

**¿Cuándo usarla?** Cuando ya dominas el juego básico y quieres cartas de mayor rareza. VIP Dorado te regala 1 al mes, VIP Axolite te regala 2.

### Oro — 20,000 FRJ

El tier premium. Los premios incluyen cartas épicas, legendarias y posibilidad de Axolotito directamente. No es frecuente poder abrirla, pero cuando tienes los FRJ, la experiencia vale mucho.

**¿Cuándo usarla?** Cuando tienes muchos FRJ ahorrados y quieres un salto de calidad real en tu colección. VIP Axolite te regala 1 al mes — es el beneficio más valioso de esa membresía.

### Triple Suerte — 22,500 FRJ

Son **3 cápsulas en un paquete** a precio reducido. Si compraras 3 Bronce por separado pagarías 4,500 FRJ; la Triple Suerte ofrece más valor por FRJ gastado con odds mejoradas.

**¿Cuándo usarla?** Cuando tienes exactamente ese presupuesto y quieres multiplicar tus chances.

---

## El Sistema Pity — Tu Garantía de Premio Especial

El Pity es la red de seguridad del Gashapon. Funciona así:

**Si abres muchas cápsulas sin sacar un Axolotito o premio especial, el sistema garantiza que una próxima cápsula te lo incluya.**

Es el equivalente digital de "no puede ser que me salgan puras cartas comunes para siempre". El contador de Pity sube cada vez que abres una cápsula sin premio especial, y cuando llega al límite, la siguiente cápsula sí te da el premio garantizado.

> El número exacto de cápsulas para activar el Pity se muestra en pantalla mientras abres (ver tienda en el juego para los valores actuales).

**Importante:** El contador de Pity es por tier de cápsula — el contador de Bronce no afecta al de Plata y viceversa. Cada tier tiene su propio sistema de garantía.

---

## Recompensa Lunar Diaria — FRJ Gratis Cada Día

Todos los días puedes reclamar **FRJ gratis** en la sección de recompensas — no importa si tienes VIP o no.

**¿Cómo reclamarla?**
1. Entra al juego cada día
2. Ve a la sección de **Recompensas** (o desde tu perfil)
3. Presiona **"Reclamar Lunar"**
4. Los FRJ aparecen en tu cuenta al instante

Si tienes VIP, la recompensa diaria de FRJ del VIP se apila con la Lunar Diaria. Son dos fuentes distintas.

**¿Qué pasa si no la reclamo un día?**
La recompensa del día se pierde — no se acumula de un día al siguiente (a diferencia de los FRJ diarios VIP que sí se guardan). Vale la pena hacer el hábito de entrar cada día aunque sea solo para reclamarla.

---

## ¿Cuál cápsula conviene más?

Depende de cuántos FRJ tienes y qué buscas:

| Situación | Recomendación |
|-----------|--------------|
| Tengo 1,500-4,999 FRJ | Bronce — aprovecha lo que tienes |
| Tengo 5,000-19,999 FRJ | Plata — mejor retorno de inversión para cartas |
| Tengo 20,000+ FRJ ahorrados | Oro — el mejor premio potencial |
| Tengo 22,500 FRJ y quiero optimizar | Triple Suerte — más chances por FRJ gastado |
| Tengo poco tiempo de juego | Reclamar la Lunar Diaria siempre, acumular para Plata |

**El cálculo de valor:**

- 1 Cápsula Bronce = 1,500 FRJ
- 1 Cápsula Plata = 5,000 FRJ = 3.3 veces el precio de Bronce
- 1 Cápsula Oro = 20,000 FRJ = 4 veces el precio de Plata

Si la Plata tiene más del triple de probabilidades de sacar algo bueno respecto a la Bronce, conviene la Plata. La lógica aplica al comparar Plata vs. Oro.

**Consejo práctico:** Si tienes VIP Dorado o Axolite, ya recibes Bronces y Platas gratis cada mes. En ese caso, guarda tus FRJ ganados jugando para apuntar a cápsulas Oro en lugar de gastarlos en Bronces que ya te regalan.

---

## Preguntas frecuentes

**¿Los premios son completamente aleatorios?**
Sí, cada apertura es independiente. Pero el sistema Pity garantiza que si tienes mala racha, eventualmente recibes un premio especial. No es puro azar sin fin — hay una red de seguridad.

**¿Hay garantía de ganar algo bueno?**
El Pity garantiza que llegado cierto número de aperturas sin Axolotito, la siguiente sí lo incluye. Para cartas raras y épicas, hay probabilidades más altas en los tiers superiores — no es garantía en cada apertura, pero la probabilidad acumulada sube.

**¿Puedo reclamar la Recompensa Lunar sin VIP?**
Sí, la Recompensa Lunar Diaria es para todos los jugadores, tengan o no VIP. Es gratis con solo entrar al juego cada día.

**¿Las cápsulas se me vencen si no las abro?**
Las cápsulas VIP que recibes mensualmente no se van a ir — se quedan en tu inventario hasta que decidas abrirlas. Ábrelas cuando quieras, no hay urgencia.

---

→ Consigue más FRJ para cápsulas jugando salas en [[multijugador]] · Recibe cápsulas gratis cada mes con [[vip]] · Explora qué más hay en la tienda en [[tienda]]


### guia_inicio
> `jugadores/guia_inicio.md`

---
tags: [jugadores, inicio]
description: "Guía en español para jugadores sobre cómo empezar en Axolotto"
last_modified: "2026-06-07"
audience: jugadores
---

# Guía de Inicio — Bienvenido a Axolotto

¡Qué onda! Si llegaste acá es porque alguien te habló de Axolotto o ya la viste en redes y quieres saber de qué va. Tranqui, aquí te explico todo sin rodeos ni tecnicismos raros.

---

## ¿Qué es Axolotto?

Axolotto es básicamente la **Lotería Mexicana de toda la vida… pero digital, con mascotas y con premios reales**. El juego se lleva a cabo en un mundo virtual inspirado en Xochimilco — con agua, cenotes, luz teal y ese ambiente de Ciudad de México que se siente en el alma.

Aquí no estás jugando tú directamente: **entrenas a tu Axolotito** (una mascota tipo ajolote) y lo mandas a jugar por ti. El Axolotito marca las cartas solo mientras tú andas haciendo otra cosa, y cuando termina la sesión ves cuánto ganaste o perdiste.

La gracia está en que **tienes cartas, armas tablas 4×4 con esas cartas, y compites contra otros jugadores** para ver quién completa líneas o la tabla completa primero. Igual que la lotería de tu abuela, pero con stats, rareza, jackpots y monedas que puedes usar para comprar cosas dentro del juego.

---

## Paso 1: Crear tu cuenta

Entrar es facilísimo — no necesitas saber nada de tecnología:

1. Abre Axolotto en el navegador
2. Haz clic en **"Entrar"**
3. Elige: **Google**, **Apple** o **correo electrónico**
4. Listo, ya tienes cuenta

Al entrar por primera vez, el juego te lleva por un **tutorial corto** donde te explica lo básico: qué son las cartas, cómo funciona el juego y cómo usar tus monedas. Dura unos 5 minutos y al terminarlo te regalan recursos para que arranques sin gastar nada.

**¿Qué te regalan al empezar?**
- Un Axolotito básico para que puedas jugar de inmediato
- Algunas Fichas (AXF) para explorar la tienda
- Frijolitos (FRJ) para tus primeras partidas
- Una tabla de juego lista para usar

> Nota: En modo de desarrollo local el juego regala saldos de práctica muy generosos. En producción los regalos son más modestos pero suficientes para empezar.

---

## Paso 2: Entiende tus monedas

En Axolotto hay dos tipos de moneda y es importante que las distingas desde el principio:

| Moneda | Nombre completo | ¿Cómo se consigue? | ¿Para qué sirve? |
|--------|----------------|-------------------|-----------------|
| **AXF** | Axofichas | Las compras con dinero real (tarjeta/transferencia) | Comprar cosas de valor: huevos, packs de cartas, membresía VIP |
| **FRJ** | Frijolitos | Las ganas jugando, completando misiones, en cápsulas diarias | Pagar la entrada a salas de juego, comprar cápsulas, consumibles |

Piensa en las **AXF como fichas de casino** — las compras en la caja y las usas para adquirir cosas buenas. Las **FRJ son como puntos de lealtad** — las vas acumulando jugando y te sirven dentro del juego.

Lo padre es que **no necesitas comprar AXF para jugar**. Con los FRJ que ganas jugando puedes participar en salas multijugador y comprar cápsulas. Pero si quieres crecer más rápido, comprar AXF acelera mucho el proceso.

---

## Paso 3: Tu primer Axolotito

Un **Axolotito es tu mascota-jugador**. Es un ajolote digital único que tú crías y mandas a competir. Sin Axolotito no puedes jugar.

**¿Por qué importa?** Cada Axolotito tiene estadísticas únicas (como personajes en un videojuego): qué tanto falla al marcar cartas, qué tanta suerte tiene, cuánta energía aguanta. A mejor Axolotito, mejores resultados en las partidas.

**¿Cómo nace tu primer Axolotito?**

1. Tu Axolotito de inicio llega **listo para jugar** — no tienes que hacer nada extra
2. Si quieres criar uno desde cero, compras un **Webito** (un huevo) en la tienda
3. El huevo va a tu **Nido** (una pantalla de cenote donde nadan tus mascotas)
4. En unos días eclosiona y nace un Axolotito con genes únicos

Cada Axolotito tiene una apariencia diferente — color, branquias, ojos, cola — todo es irrepetible. Ve a [[axolotitos]] para saber más sobre sus stats y cómo subirlos de nivel.

---

## Paso 4: Tu primera partida

El modo CPU es perfecto para practicar. Aquí juegas contra bots del sistema, sin presión ni competencia real.

**Paso a paso:**

1. **Selecciona tu Axolotito** — el que tienes de inicio sirve perfecto
2. **Selecciona tu tabla** — también tienes una tabla lista para usar
3. **Elige la sala** — para empezar, modo CPU es lo más tranquilo
4. **Configura tu presupuesto** — cuántos FRJ arriesgas máximo y cuándo parar si ganas
5. **Manda a jugar** — el Axolotito juega solo mientras tú haces otra cosa
6. **Recoge resultados** — cuando termina, ves tu boleta y cobras los FRJ ganados

¿Qué pasa durante el juego? El "Cantador" va sacando cartas al azar del mazo. Si esa carta está en tu tabla, tu Axolotito la marca automáticamente. El primero en completar una línea (horizontal, vertical o diagonal) gana el Hito 1. El primero en llenar toda la tabla gana el Hito 2. ¡Como la lotería normal, pero tu mascota juega sola!

**Premios en modo CPU:**
- Ganar Hito 1 (línea): parte del pozo
- Ganar Hito 2 (tabla completa): parte mayor del pozo
- Perder: igual ganas XP para tu Axolotito y tu tabla

---

## ¿Cuánto cuesta empezar?

| Opción | Inversión | Qué puedes hacer |
|--------|-----------|-----------------|
| **Gratis (F2P)** | $0 | Jugar modo CPU, ganar FRJ, abrir cápsulas básicas, participar en salas rookie |
| **Arranque suave** | ~$35 MXN (200 FRJ aprox.) | Lo anterior + más cápsulas y salas, empezar a construir colección |
| **Con tabla nueva** | ~$20 MXN en AXF (10 AXF) | Comprar tabla Clásica y armar tu estrategia personalizada |
| **Con Axolotito nuevo** | ~$800 MXN en AXF (400 AXF) | Incubar tu primer Webito Génesis y criar tu Axolotito personalizado |

**La ruta recomendada para principiantes:** Empieza gratis, juega unas partidas con lo que te dan de regalo, aprende las mecánicas, y cuando le agarres el gusto invierte lo que quieras.

---

## Preguntas frecuentes

**¿Necesito saber de criptomonedas o tecnología para jugar?**
No, para nada. El juego funciona como cualquier app — creas cuenta con Google, juegas y listo. La tecnología de fondo existe pero está completamente escondida.

**¿Puedo perder dinero real?**
En modo gratis, no. Solo usas FRJ que ganas jugando. Si compras AXF con dinero real y los gastas en el juego, sí puedes perderlos si no juegas bien — igual que en cualquier juego con compras opcionales.

**¿Mi Axolotito puede morir?**
No muere, pero se queda sin energía y necesita "dormir" antes de volver a jugar. Si cuidas su energía y lo alimentas, siempre está disponible.

**¿Cuánto tiempo necesito para jugar cada día?**
Puedes jugar de forma muy relajada. Configuras tu Axolotito, lo mandas a jugar y revisas los resultados cuando quieras. No hay que estar pegado a la pantalla.

**¿Es lo mismo que la lotería tradicional de azar?**
Se parece mucho en las cartas y los patrones, pero tu Axolotito tiene stats que afectan el resultado. No es puro azar — la crianza y entrenamiento de tu mascota importa.

**¿Qué pasa con mis cosas si dejo de jugar un tiempo?**
Tus cartas, tablas y Axolotitos siguen siendo tuyos. Si tenías VIP activo y se vence, tus Axolotitos extra se "congelan" (no pueden jugar) pero no desaparecen. Al renovar vuelven a activarse.

**¿Puedo jugar con amigos?**
Sí. En modo multijugador puedes unirte a salas públicas donde hay otros jugadores reales, o crear una sala privada para invitar a quien quieras. Ve a [[multijugador]] para los detalles.

---

→ Siguiente paso: conoce a tu Axolotito a fondo en [[axolotitos]] · Entérate de qué hay en la tienda en [[tienda]] · Ve cómo funciona el multijugador en [[multijugador]]


### multijugador
> `jugadores/multijugador.md`

---
tags: [jugadores, multijugador]
description: "Guía en español para jugadores sobre el modo multijugador — salas, premios, reglas y consejos"
last_modified: "2026-06-07"
audience: jugadores
---

# Multijugador — Compite en Tiempo Real

En el multijugador ya no juegas contra bots del sistema — estás compitiendo contra **otros jugadores reales** en salas donde todos tienen sus propios Axolotitos y tablas. Aquí el nivel sube y los premios también.

---

## ¿Cómo funciona el multijugador?

Es básicamente la Lotería Mexicana de toda la vida, pero en tiempo real con otras personas conectadas al mismo tiempo:

1. **Entras a una sala** pagando el entry fee en FRJ (Frijolitos)
2. El sistema espera a que se llene (máximo 30 tableros por sala)
3. Si hay menos de 4 jugadores cuando el contador llega a 0, el sistema rellena con bots para que la partida empiece
4. El **Cantador** va sacando cartas al azar del mazo de 54
5. Tu Axolotito marca automáticamente las cartas que están en tu tabla
6. El primero en completar un patrón gana su Hito y su parte del pozo

Las actualizaciones son en tiempo real — puedes ver cómo avanzan los otros jugadores mientras tu Axolotito juega.

---

## Modos de sala

### Charco de Novatos (Rookie Pool) — Sala para principiantes

La sala más accesible. Ideal si estás empezando con el multijugador o quieres partidas rápidas con menos riesgo.

- **Ambiente:** Tranquilo, hay mezcla de jugadores nuevos y bots de relleno
- **Perfil ideal:** Jugadores que están aprendiendo, o quienes quieren muchas partidas sin arriesgar mucho

### Fosa del Campeón (Champion Abyss) — Sala avanzada

La sala de los veteranos. Los jugadores aquí ya saben lo que hacen, sus Axolotitos están más entrenados y los premios valen más.

- **Ambiente:** Más competitivo, menos bots, jugadores con Axolotitos de buen nivel
- **Perfil ideal:** Jugadores con Axolotito entrenado y buenas tablas armadas

### Sala Privada (Cave) — Crea tu propia sala

¿Quieres jugar solo con amigos o establecer tus propias reglas? Puedes crear una sala privada (Cave) con un entry fee personalizado en FRJ. Tú decides cuánto cuesta entrar.

- **Cómo crear una:** Desde el Lobby multijugador, selecciona "Crear sala" y configura el buy-in en FRJ
- **Ideal para:** Amigos que quieren competir entre sí o jugadores que buscan condiciones específicas

---

## Entry Fees y Premios

El multijugador usa **exclusivamente FRJ (Frijolitos)**. No se puede pagar con AXF. Esto es por mandato legal — el juego está diseñado así desde la base.

| Sala | Entry Fee | Premio 1er lugar | Consolación | XP Axolotito (ganar/perder) | XP Tabla (ganar/perder) |
|------|-----------|-----------------|-------------|---------------------------|------------------------|
| **Charco de Novatos** | 25 FRJ | 85 FRJ | 8 FRJ | 35 / 8 | 25 / 8 |
| **Fosa del Campeón** | 100 FRJ | 400 FRJ | 20 FRJ | 75 / 15 | 60 / 15 |
| **Sala Privada (Cave)** | Configurable | Configurable | — | Según sala | Según sala |

**¿Qué es la consolación?** Si entras a una sala, juegas y no ganas ningún Hito, igual recibes una cantidad pequeña de FRJ de consolación para que no te quedes en cero. Es como el "aunque sea el camión" de la lotería.

**Ejemplo Charco de Novatos:** Pagas 25 FRJ para entrar. Si ganas el Hito 1 (primera línea), te llevas parte del pozo. Si ganas el Hito 2 (tabla llena), te llevas la parte mayor. Si pierdes todo, recibes 8 FRJ de consolación. Tu Axolotito gana XP de todas formas.

**Ejemplo Fosa del Campeón:** Pagas 100 FRJ. Si ganas, el premio de 400 FRJ multiplica 4x tu inversión. El riesgo es mayor pero la recompensa también.

---

## El Jackpot — El premio gordo

El Jackpot de Oro es el premio acumulado global del juego — **crece con cada partida que se juega** en todas las salas.

**¿Cómo funciona?**
- El 5% de cada bolsa de cada partida se va acumulando al Jackpot
- El pozo empieza con 1,000 FRJ de semilla y no para de crecer
- Para ganarlo, un jugador humano tiene que completar el **Hito 1 antes de que se canten 5 ó 6 cartas** — es decir, formar una línea casi al instante del inicio

**¿Por qué es tan difícil?** Porque necesitas que las primeras cartas cantadas sean exactamente las que tienes en una línea de tu tabla. Es cuestión de azar, pero cuando pasa, el ganador se lleva el **90% del pozo acumulado**.

**Restricciones:**
- Solo jugadores humanos pueden ganarlo (no bots)
- La sala debe tener al menos 5 tableros humanos de 2 jugadores distintos
- El 10% restante queda como semilla para el siguiente Jackpot

**VIP Axolite:** Si tienes membresía Axolite activa, recibes un +5% extra sobre lo que ganes del Jackpot.

---

## Reglas del juego en sala

### Los patrones de victoria (Hitos)

| Hito | ¿Qué necesitas? | Premio |
|------|----------------|--------|
| **Hito 1** (Línea o Cuadrito) | Primera línea de 4 cartas — horizontal, vertical, diagonal — O un cuadro de 2×2 | 35% del pozo |
| **Hito 2** (¡Lotería! / Tabla Llena) | Primero en marcar las 16 cartas de su tabla | 55% del pozo |

El 5% del pozo va al Jackpot global y el 5% restante a la tesorería del juego.

### El Cantador (Griton)

El Cantador es el DJ de la partida — va anunciando las cartas una a una. En Axolotto el Cantador es el **Griton**, un personaje virtual que canta las cartas con el estilo de la lotería tradicional (con el dicho de cada carta: "¡El que con la cola pica, el Alacráaan!").

La velocidad a la que el Griton canta las cartas varía según la sala — las salas más avanzadas pueden ir más rápido.

### Errores de marcado

¿Recuerdas el stat de **Enfoque** de tu Axolotito? Aquí es donde importa. Si tu Axolotito tiene poco Enfoque, hay probabilidad de que falle al marcar una carta que el Cantador anunció — y eso te pone en desventaja frente a jugadores con Axolotitos más entrenados.

---

## Consejos para ganar

**Enfoca tu Axolotito:** El stat de Enfoque es el más importante para el multijugador. Si falla cartas, pierdes posiciones aunque las cartas estén en tu tabla.

**Suerte para momentos clave:** Un Axolotito con buena Suerte puede salvarte de situaciones límite — cuando estás a punto de perder en un tira y afloja.

**Elige el nivel correcto:** Si tu Axolotito tiene nivel bajo, empieza en el Charco de Novatos. Tira a la Fosa del Campeón cuando ya tengas Axolotito entrenado y tabla bien armada.

**Arma tu tabla estratégicamente:** Coloca las cartas más raras (que tienen mayor probabilidad de aparecer cuando conviene) en posiciones de línea. Un tablero manual bien pensado tiene ventaja sobre uno armado al azar. Ve a [[tienda]] para comprar tablas mejores.

**Aprovecha el VIP Axolite:** Si juegas mucho en la Fosa del Campeón, el 15% de descuento en entry fee del VIP Axolite se acumula rápido. 100 FRJ de entrada se vuelven 85 FRJ con ese descuento.

---

## ¿Por qué se usa FRJ en multijugador y no AXF?

Buena pregunta. La respuesta corta es: **por ley**.

El juego multijugador donde los jugadores apuestan y compiten por premios entra en la categoría de "juego de apuesta" bajo las regulaciones mexicanas. Las AXF (Axofichas) tienen valor real respaldado — son básicamente dinero. Usar AXF directamente en apuestas multijugador activaría regulaciones bancarias y de juegos de azar que el juego no quiere (ni puede fácilmente) cumplir todavía.

Los FRJ son moneda de juego que no se puede convertir a dinero real — existen solo dentro del ecosistema de Axolotto. Eso los pone en una categoría legal diferente y más segura para este tipo de competencia.

En simple: **FRJ = fichas de videojuego, AXF = dinero real**. La ley dice que las apuestas multijugador solo pueden usar las fichas de videojuego.

---

## Preguntas frecuentes

**¿Puedo jugar multijugador completamente gratis?**
Sí, si tienes suficientes FRJ. Los ganas jugando modo CPU, completando misiones, abriendo cápsulas diarias y otras actividades. No es necesario comprar AXF para entrar a salas multijugador.

**¿Qué pasa si me desconecto en medio de una partida?**
Tu Axolotito sigue jugando de forma autónoma. El juego no requiere que estés conectado mientras la partida corre. Al volver, verás el resultado.

**¿Hay partidas a deshoras donde no hay jugadores reales?**
Puede pasar. El sistema rellena las salas con bots para que la partida siempre empiece. Igual ganas XP y consolación, pero los bots no aportan tanto a la bolsa como los jugadores reales.

**¿Puedo ver quién está en la sala antes de entrar?**
Sí. En el Lobby puedes ver los jugadores registrados en cada sala, sus Axolotitos y si tienen marco VIP. Eso te da idea del nivel de competencia antes de pagar el entry fee.

---

→ Entrena mejor a tu Axolotito en [[axolotitos]] · Consigue más FRJ con las cápsulas en [[capsulas]] · Los beneficios VIP para multijugador en [[vip]]


### tienda
> `jugadores/tienda.md`

---
tags: [jugadores, tienda]
description: "Guía en español para jugadores sobre la tienda — boosters, huevos, Card Melter y cómo comprar AXF"
last_modified: "2026-06-07"
audience: jugadores
---

# La Tienda — El Tianguis de Axolotto

Aquí es donde consigues todo lo que necesitas para crecer en el juego: packs de cartas, huevos para criar Axolotitos, consumibles y más. Puedes pagar con AXF (Axofichas, la moneda premium) o con FRJ (Frijolitos, los que ganas jugando) dependiendo del artículo.

---

## La Tienda (Tianguis)

El Tianguis es la tienda oficial del juego. Desde ahí puedes comprar:

- **Boosters** — sobres con cartas de lotería
- **Webitos** — huevos para incubar y criar Axolotitos
- **Tablas de juego** — cuadrículas 4×4 para armar tu estrategia
- **Consumibles** — alimentos para tu Axolotito, protecciones para huevos, solventes
- **Membresías VIP** — para más beneficios (ver [[vip]])

Todos los precios están fijos por el sistema — no hay regateo, pero con VIP activo tienes descuento automático en todo.

---

## Boosters de Cartas

Los Boosters son **sobres con 7 cartas de lotería** (excepto el Pure que da 1 carta). Abrir sobres es cómo construyes tu colección para armar tablas mejores.

### ¿Cuántos tipos hay?

Hay 4 tipos de Boosters normales y 1 especial, organizados por "Fase" según el momento del juego:

### Fase 1 — First Edition (las originales, las más buscadas)

| Tipo | Precio AXF | Precio FRJ | Contenido |
|------|-----------|-----------|-----------|
| **Fiesta** | 10 AXF | 100 FRJ | 7 cartas — mezcla festiva |
| **Nido** | 10 AXF | 100 FRJ | 7 cartas — temática naturaleza |
| **Cosmos** | 10 AXF | 100 FRJ | 7 cartas — temática cosmos |
| **Pure** | 6 AXF | 60 FRJ | 1 sola carta |

### Fase 2 — Unlimited

| Tipo | Precio AXF | Precio FRJ |
|------|-----------|-----------|
| Fiesta | 15 AXF | 150 FRJ |
| Nido | 15 AXF | 150 FRJ |
| Cosmos | 15 AXF | 150 FRJ |
| Pure | 10 AXF | 100 FRJ |

### Fase 3 — Retail / Standard

| Tipo | Precio AXF | Precio FRJ |
|------|-----------|-----------|
| Fiesta | 20 AXF | 200 FRJ |
| Nido | 20 AXF | 200 FRJ |
| Cosmos | 20 AXF | 200 FRJ |
| Pure | 15 AXF | 150 FRJ |

### Especial — Booster Brillante (Foil)

| Tipo | Precio AXF | Precio FRJ |
|------|-----------|-----------|
| **Foil (Brillante)** | 80 AXF | 800 FRJ |

El Booster Brillante tiene ~3% de probabilidad de soltar cartas holográficas (Foil). Estas cartas se ven increíbles y las tablas armadas con ellas generan un pequeño bonus de rendimiento.

**¿Cuál conviene?** Si apenas empiezas, los Boosters de Fase 1 son los más baratos. Si quieres cartas raras y tienes presupuesto, el Booster Brillante es la apuesta.

---

## Webitos (Huevos)

Los Webitos son los **huevos de los que nacen tus Axolotitos**. Los compras en la tienda, los colocas en tu Nido y los incubas durante ~7 días. Al eclosionar, nace un Axolotito con genes y stats únicos.

| Fase / Tipo | Precio AXF | ¿Qué obtienes? |
|-------------|-----------|----------------|
| **Génesis** (Fase 1) | 400 AXF | Axolotito de primera generación — aura dorada |
| **Expansión** (Fase 2) | 800 AXF | Segunda generación |
| **Retail** (Fase 3) | 1,200 AXF | Generación estándar |
| **Astral** (Especial) | 3,000 AXF | Rarísimo — stats y apariencia excepcionales |

**¿Cómo funciona la incubación?**
1. Compras el Webito
2. Lo colocas en un slot de tu Nido (tienes 7 slots)
3. El huevo necesita calor — si el clima virtual de Xochimilco está frío, pierde calor y la incubación se pausa
4. Puedes gastar FRJ para calentar el huevo y acelerar el proceso
5. Cuando las horas llegan a 0 y el huevo pulsa en rosa — ¡a darle tap para que nazca!

Ve a [[axolotitos]] para saber más sobre las stats que puede tener tu Axolotito recién nacido.

---

## Card Melter — Transforma cartas duplicadas en FRJ

¿Tienes muchas copias de la misma carta que no usas? El **Card Melter** te permite quemar cartas duplicadas a cambio de FRJ.

**¿Cómo funciona?**

Seleccionas las cartas que quieres fundir y el sistema te da FRJ según la rareza de cada carta:

- Cartas Comunes: el valor más bajo
- Cartas Raras: más FRJ
- Cartas Épicas/Legendarias: más FRJ aún

**Ejemplo práctico:** Si tienes 5 copias de "El Gallo" (carta común) y solo necesitas 1 para tu tabla, puedes fundir las otras 4 y recuperar FRJ que puedes usar en salas de juego o cápsulas.

> Los valores exactos del Card Melter aparecen en pantalla al seleccionar las cartas (ver tienda en el juego).

**¿Cuándo usarlo?** Cuando tengas muchos duplicados acumulados. No destruyas cartas que uses en tus tablas activas — primero revisa si alguna tabla las necesita.

---

## Mercado P2P — Compra y vende con otros jugadores

El **Mercado P2P** es donde los jugadores intercambian directamente entre sí. No hay intermediario del juego — es como un tianguis real donde pones tu precio y esperas comprador.

### ¿Qué se puede vender?
- Cartas de lotería individuales
- Tablas de juego completas armadas
- Axolotitos (en fases avanzadas)

### Comisiones del mercado

Cada venta tiene una comisión que se queda el sistema:

| Estado VIP | Comisión |
|-----------|---------|
| Sin VIP | 5% |
| VIP Coral | 4% |
| VIP Dorado | 3% |
| VIP Axolite | 1.5% |

Si vendes una carta en 1,000 FRJ sin VIP, recibes 950 FRJ. Con VIP Axolite recibirías 985 FRJ.

**¿Cómo vender?**
1. Abre el Mercado P2P
2. Selecciona el ítem que quieres vender
3. Pon el precio que quieras en FRJ
4. Espera a que alguien lo compre

**Consejo:** Revisa qué precio tienen las mismas cartas en el mercado antes de poner el tuyo — si pones muy caro, nadie compra; si pones muy barato, regalas.

---

## Tablas de Juego

Las tablas son las cuadrículas 4×4 con las que juegas. Puedes comprar tablas adicionales para tener diferentes estrategias:

| Tipo de Tabla | Precio AXF | Precio FRJ |
|---------------|-----------|-----------|
| **Clásica** | 10 AXF | 130 FRJ |
| **Suerte** | 50 AXF | 520 FRJ |
| **Plasma** | 150 AXF | 1,560 FRJ |
| **Cósmica** | 200 AXF | (solo AXF) |

Sin VIP tienes 3 slots de tabla. Con VIP Dorado tienes 4 y con VIP Axolite tienes 5.

---

## Cómo comprar AXF

Las AXF (Axofichas) son la moneda premium y se compran con dinero real. El proceso es simple:

### Con tarjeta de crédito/débito (MoonPay)

1. Ve a la sección **"Comprar AXF"** dentro del juego
2. Se abre el widget de **MoonPay** — una plataforma de pagos segura
3. Elige cuánto quieres comprar en pesos mexicanos (MXN) o dólares (USD)
4. Paga con tu tarjeta de crédito, débito o transferencia SPEI
5. En minutos las AXF aparecen en tu cuenta del juego

### Con USDC (crypto)

Si ya tienes USDC (una criptomoneda estable en dólares), también puedes enviarla directamente para obtener AXF.

**¿Cuánto vale 1 AXF?**
Precio de referencia: ~$2 MXN por AXF. Es decir, 100 AXF cuestan aproximadamente $200 MXN.

> Los precios exactos los muestra el widget de MoonPay al momento de comprar, ya que pueden variar por tipo de cambio.

---

## Preguntas frecuentes

**¿Puedo jugar completamente gratis?**
Sí. Con los FRJ que ganas jugando puedes entrar a salas, comprar cápsulas y obtener cartas. No es necesario comprar AXF para disfrutar el juego. Comprar AXF acelera el progreso y da acceso a contenido premium.

**¿Las cartas que compro son mías para siempre?**
Sí. Tus cartas, tablas y Axolotitos son tuyos. Los puedes usar, vender en el P2P o guardar. No desaparecen si dejas de jugar.

**¿Qué pasa si abro muchos boosters y me salen puras cartas comunes?**
Es parte del azar. Las cartas comunes también sirven para armar tablas y las puedes fundir en el Card Melter. Si quieres más probabilidad de raras, el Booster Brillante (Foil) tiene mejores odds.

**¿Puedo devolver o cambiar una compra?**
Las compras dentro del juego son finales. Si compraste un Booster y ya lo abriste, no hay vuelta atrás. Las AXF compradas con tarjeta tampoco se reembolsan una vez acreditadas (a menos que haya un error técnico — contacta soporte en ese caso).

---

→ Aprende sobre el sistema de cápsulas Gashapon en [[capsulas]] · Beneficios con VIP en [[vip]] · Cómo jugar con tus cartas en [[multijugador]]


### vip
> `jugadores/vip.md`

---
tags: [jugadores, vip]
description: "Guía en español para jugadores sobre la membresía VIP — tiers, beneficios y análisis de valor"
last_modified: "2026-06-07"
audience: jugadores
---

# Membresía VIP — ¿Vale la Pena?

El VIP es una membresía mensual de 30 días que te da un montón de ventajas: FRJ gratis cada día, descuentos en la tienda, cápsulas mensuales y más. No es obligatorio para jugar, pero si juegas seguido, puede ayudarte a crecer mucho más rápido.

---

## ¿Qué es el VIP?

Es una suscripción de 30 días que activas una sola vez y se mantiene activa durante ese período. Al activarla:
- Recibes FRJ de bienvenida de inmediato
- Empiezas a acumular FRJ diarios que puedes reclamar cada día
- Desbloqueas descuentos automáticos en la tienda
- Recibes cápsulas Gashapon gratis cada mes

Hay tres niveles — Coral, Dorado y Axolite — cada uno más caro pero con más beneficios.

---

## Los Tres Niveles VIP

| Beneficio | Sin VIP | Coral | Dorado ⭐ Popular | Axolite |
|-----------|---------|-------|-----------------|---------|
| **Precio (AXF)** | — | 400 AXF | 600 AXF | 1,800 AXF |
| **FRJ diarios** | 0 | 40 FRJ/día | 100 FRJ/día | 200 FRJ/día |
| **Descuento en tienda** | 0% | 5% | 12% | 20% |
| **FRJ al activar** | — | 200 FRJ | 500 FRJ | 1,000 FRJ |
| **Booster de bienvenida** | — | Ninguno | 1× Booster Normal | 1× Booster Brillante (Foil) |
| **Cápsulas mensuales gratis** | — | 2× Bronce | 2× Bronce + 1× Plata | 3× Bronce + 2× Plata + 1× Oro |
| **Slots de tabla extra** | 0 | +0 | +1 (total 4) | +2 (total 5) |
| **Slots de Axolotito extra** | 0 | +0 | +0 | +1 (total 7) |
| **Comisión en ventas P2P** | 5% | 4% | 3% | 1.5% |
| **Descuento en entry fee multijugador** | 0% | 0% | 0% | 15% |
| **Bonus en Jackpot ganado** | 0% | 0% | 0% | +5% |

---

## ¿Vale la pena? Análisis por tier

### Coral — 400 AXF (~$800 MXN)

**Recibes al activar:** 200 FRJ en cuenta.

**Por 30 días:** 40 FRJ/día × 30 días = **1,200 FRJ en total**.

**Cápsulas gratuitas:** 2× Cápsula Bronce = 2× lo que costaría 1,500 FRJ cada una = 3,000 FRJ de valor en cápsulas.

**FRJ total acumulado (diarios + cápsulas):** ~4,200 FRJ entre lo que recibes directo y las cápsulas.

**Descuento 5% en tienda:** Si compras Boosters Fase 1 por 100 FRJ c/u, el descuento te ahorra 5 FRJ por Booster — no es mucho de forma aislada, pero se acumula.

**Resumen Coral:** Ideal si juegas casual. Los FRJ diarios y las cápsulas de bienvenida cubren bastante. La recuperación del costo en FRJ puros es lenta (~114 días si solo usas los FRJ diarios), pero las cápsulas y el descuento mejoran el valor real.

---

### Dorado — 600 AXF (~$1,200 MXN) ⭐ El más popular

**Recibes al activar:** 500 FRJ + 1 Booster Normal.

**Por 30 días:** 100 FRJ/día × 30 días = **3,000 FRJ en total**.

**Cápsulas gratuitas:** 2× Bronce + 1× Plata = (3,000 FRJ + 5,000 FRJ) = 8,000 FRJ de valor en cápsulas.

**FRJ total (diarios + bienvenida + cápsulas):** ~11,500 FRJ entre todo lo que recibes.

**Slot extra de tabla:** Puedes tener 4 tablas activas simultáneamente — eso significa poder diversificar estrategias o tener un Axolotito jugando en una sala mientras otro hace otra cosa.

**Descuento 12%:** En Booster Fase 1 (100 FRJ), 12 FRJ de descuento por sobre. Si abres 20 sobres en el mes, ahorras 240 FRJ.

**Resumen Dorado:** La mejor relación precio-beneficio para jugadores activos. Los 100 FRJ/día son mucho más útiles que los 40 del Coral, y el slot de tabla extra marca diferencia si ya tienes dos o tres Axolotitos.

---

### Axolite — 1,800 AXF (~$3,600 MXN)

**Recibes al activar:** 1,000 FRJ + 1 Booster Brillante (Foil — vale 800 FRJ o 80 AXF).

**Por 30 días:** 200 FRJ/día × 30 días = **6,000 FRJ en total**.

**Cápsulas gratuitas:** 3× Bronce + 2× Plata + 1× Oro = (4,500 + 10,000 + 20,000) = **34,500 FRJ de valor en cápsulas**.

**FRJ total (todo incluido):** ~41,500 FRJ de valor entre lo que recibes directamente y las cápsulas.

**Descuento 20% en tienda:** Significativo si compras mucho — en Boosters Brillantes de 800 FRJ, el descuento son 160 FRJ por sobre.

**Descuento 15% entry fee multijugador:** En la Fosa del Campeón (100 FRJ de entrada), pagas solo 85 FRJ. Si juegas 50 partidas en el mes, ahorras 750 FRJ.

**Bonus +5% en Jackpot:** Si algún día ganas el Jackpot de Oro, ese 5% extra puede ser mucho dinero.

**Resumen Axolite:** Para jugadores muy activos o que compran bastante en la tienda. La cápsula de Oro gratuita mensual (20,000 FRJ de valor) por sí sola ya justifica buena parte del costo si eres de los que abre cápsulas seguido.

---

## ¿Qué pasa si se caduca el VIP?

Si los 30 días pasan y no renuevas:

- **Pierdes los beneficios** — ya no recibes FRJ diarios, se quita el descuento, no hay cápsulas mensuales
- **Los Axolotitos extra se CONGELAN** — si tienes VIP Axolite y usabas el séptimo slot, ese Axolotito se congela: sigue siendo tuyo pero no puede jugar, no genera nada, no se puede enviar a salas
- **Al renovar, se descongelan** — al activar VIP Axolite de nuevo, el Axolotito congelado vuelve a estar disponible de inmediato

Los Axolotitos congelados no desaparecen, no se borran. Solo están en pausa.

---

## Cómo activar y renovar

1. Ve a tu **Perfil** dentro del juego
2. Selecciona **"VIP"**
3. Elige el tier que quieres: Coral, Dorado o Axolite
4. Confirma el pago en AXF
5. ¡Listo! Los beneficios se activan al instante (los FRJ de bienvenida aparecen de inmediato)

Para **renovar**, el proceso es el mismo — entras al perfil antes o después de que expire y compras de nuevo.

---

## Auto-renovación

La auto-renovación hace que el VIP se renueve solo cuando se acaba, sin que tengas que acordarte.

**¿Cómo activarla?**
- Desde la sección de VIP en tu Perfil, activa el toggle de "Auto-renovar"

**¿Cómo desactivarla?**
- En el mismo lugar — desactiva el toggle antes de que venza el período actual

**Importante:** La auto-renovación descuenta AXF automáticamente de tu cuenta. Asegúrate de tener el saldo suficiente si la tienes activa. Si al momento de renovar no hay AXF en la cuenta, la renovación falla y el VIP caduca normalmente.

---

## Preguntas frecuentes

**¿Los FRJ diarios se acumulan si no los reclamo?**
Sí, se guardan en tu cuenta hasta que los reclames. No se pierden si no entras un día — pero sí dejarán de generarse cuando expire el VIP. Reclamar es manual desde la UI del VIP en tu perfil.

**¿Puedo cambiar de tier VIP en medio del período?**
En la versión actual, el tier VIP se activa por 30 días completos. Si quieres un tier más alto, tendrías que esperar a que expire el actual o contactar soporte (ver tienda en el juego para opciones actuales).

**¿El descuento VIP aplica en el Mercado P2P entre jugadores?**
El descuento de tienda aplica en compras de la tienda oficial. La reducción de comisión P2P es un beneficio separado — todos los tiers tienen comisión reducida vs. el 5% estándar.

**¿Qué pasa si compro VIP pero no entro a jugar en 30 días?**
El VIP se activa por 30 días corridos desde la compra, no solo días que juegues. Si no entras, los FRJ diarios se acumulan y los puedes reclamar todos cuando vuelvas — hasta que expire el período.

---

→ Ver precios exactos de boosters y cápsulas en [[tienda]] · Cómo usar los FRJ en salas de juego en [[multijugador]] · El sistema de cápsulas en [[capsulas]]


