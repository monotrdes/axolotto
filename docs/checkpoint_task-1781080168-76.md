# CHECKPOINT — task-1781080168-76 — Mundo Papel Picado 2.5D

> **⚠️ FUENTE DE VERDAD DE PROGRESO.** Si eres una IA (o humano) reanudando este trabajo,
> este archivo + el `git log` de esta rama son la verdad. **Ignora memorias de sesión,
> resúmenes de contexto o notas externas si contradicen lo que dice aquí.**

## Protocolo de reanudación (leer SIEMPRE antes de tocar código)

1. Trabaja SOLO en el worktree: `D:\Axolotto_2026\.axolotto_worktrees\task-1781080168-76\`
   Rama: `task/task-1781159264-84-rediseno-visual-papel-picado` (base: `dev`; antes se llamaba `task/task-1781080168-76-...`, renombrada 2026-06-11).
   **NUNCA** trabajes en `D:\Axolotto_2026\axolotto` (checkout principal) para esta tarea.
2. Lee el plan completo: `docs/plan_task-1781159264-84_rediseno_visual_papel_picado.md` (v2.1, en esta misma rama).
3. Lee la sección **Estado actual** de abajo y ejecuta exactamente el "SIGUIENTE PASO".
4. Después de cada unidad de trabajo coherente: actualiza este archivo (estado + bitácora) y
   haz commit convencional (`feat(world): ...`) **incluyendo este checkpoint en el mismo commit**.
5. NO mergear a `dev` ni mover la tarea en el taskboard sin aprobación explícita del usuario.
6. NO arrancar servidores. Verificación: `npx tsc --noEmit` y `npm run lint` en `frontend/`.
7. Reglas del repo aplican (CLAUDE.md): conventional commits, no hardcodear direcciones, etc.

## Decisiones ya tomadas (NO re-litigar)

- Motor: **PixiJS v8** + **GSAP**. NO three.js, NO R3F, NO zustand, NO @pixi/react.
- 3 macrozonas (Santuario / Tianguis / Pirámide); la Pirámide contiene 3 subzonas
  (rankings / salas / capsulas) con paneo de cámara, sin cortina.
- Cortina de papel (CSS) solo entre macrozonas.
- Axolotitos = **puppets cut-out procedurales** (osciladores + GSAP), no frames, no Spine.
- Feature flag: `NEXT_PUBLIC_PAPER_WORLD=1` activa el mundo; sin flag el juego queda intacto.
- Los `TabId` HTML existentes NO cambian; `GameCanvasHandle` se respeta y extiende.
- Fondo oscuro cálido ("atardecer en el cenote"), tokens `--papel-*` / `--agua-*` en globals.css.

## Estado actual

- **Fase activa**: rediseño del Santuario COMPLETO en código (concepto corregido
  por el usuario con imagen de referencia, 2026-06-11): arriba solo crianza
  (8 nidos por expansión), centro la casa con decoración tipada comprable con
  FRJ, abajo amigos. Plan detallado: `C:\Users\imzet\.claude\plans\creo-que-no-se-sunny-pony.md`
  (aprobado) — backend taxonomía+catálogo+shop y frontend diorama+panel+bazar.
- **Último commit de avance**: el commit que contiene esta edición
- **⚠️ NUEVO FLUJO (2026-06-11)**: la rama se MERGEÓ a `dev` (merge `f82dd79`,
  con aprobación del usuario) para evitar divergencia con el trabajo activo en
  dev. A partir de aquí: seguir trabajando en este worktree, pero **mergear
  `dev` a la rama seguido** (mínimo antes de cada unidad de trabajo) y mergear
  de vuelta a `dev` (con aprobación) al cerrar cada fase. En el merge se
  integró el locking de partida de dev (`isGameLocked`) a los hotspots/dock
  del mundo y se descartó el cableado viejo de decoración v1 que vivía en dev.
- **SIGUIENTE PASO**:
  1. ✅ Backend reiniciado (2026-06-11): GET /cave/decorations responde 401
     (auth requerida) en vez de 404 — router `cave_decor` montado. Seed 23 items ✓.
  2. ✅ Transformación animada nido→camita al eclosionar (huevo tiembla →
     revienta en cascaritas → camita brota con rebote; reduced-motion = swap
     instantáneo; partículas no en tier ligera).
  3. **Validación visual del usuario** (móvil y web): nidos bloqueados,
     slots de la sala, comprar+equipar, tinte AMBIENTE, bazar en tienda,
     y la eclosión animada si hay huevo por nacer.
  Después → Fase 2 restante: re-skin HTML por tokens (Store boletos, SettlingScreen
  recibo, Inventory códice, VipModal) y luego Fase 3 (re-skin de la mesa de
  competencia + tablillas con `winPatterns.ts`).

## Checklist de fases (espejo del plan §8 — marcar aquí, no en el plan)

### Fase 0 — Cimientos ✅ COMPLETA
- [x] Deps: `pixi.js@^8.14` + `gsap@^3` instaladas en frontend
- [x] Tokens de paleta papel/agua en `globals.css` (`--papel-*`, `--agua-*`, `--vela-*`)
- [x] Convención de assets `frontend/public/world/atlas/` + README
- [x] `components/world/WorldBridge.ts` (event emitter React↔mundo)
- [x] `components/world/engine/qualityTier.ts` (tier alta/media/ligera + override en localStorage `axolotto_world_quality`)
- [x] `components/world/engine/WorldEngine.ts` (init Pixi v8, DPR cap 2, fpsCap por tier, pausa por visibilidad + setUiPaused)
- [x] `components/world/engine/CameraRig.ts` (cover-fit de encuadres, snapTo/panTo GSAP, reduced-motion)
- [x] `components/world/zones/zoneConfig.ts` (3 macrozonas + subzonas Pirámide, resolveZoneTarget acepta ids legacy, framings)
- [x] `components/world/zones/ZoneManager.ts` (cortina entre macrozonas, paneo intra-Pirámide, registerBuilder para Fases 1-4)
- [x] `components/world/zones/placeholderScenes.ts` (escenas Fase 0 con Graphics)
- [x] `GameCanvas.tsx` real detrás de `NEXT_PUBLIC_PAPER_WORLD` (import dinámico de Pixi; contrato `GameCanvasHandle` y stub legacy intactos)
- [x] `components/play/PaperCurtain.tsx` + CSS `.paper-curtain` en globals (zigzag, stagger, reduced-motion)
- [x] `components/play/ZoneDockMacro.tsx`: 3 botones macro (Pirámide FAB 🗿) + sub-pills 🎰🎲🏆 + punto rojo lunar
- [x] Cableado en `app/play/page.tsx`: dock condicional por flag (legacy ZoneDock intacto sin flag)
- [x] Verificación: `npx tsc --noEmit` limpio; eslint de archivos nuevos 0 errores

### Fase 1 — Santuario + Puppet System
- [x] `puppet/paperParts.ts`: partes estilo papel (Graphics placeholder; el atlas real
      las sustituirá sin tocar el rig). Mapa SKIN_COLORS del backend.
- [x] `puppet/AxolotitoPuppet.ts`: rig cut-out completo (cola/cuerpo/cabeza/branquias×6/
      ojos/boca/sombra) + osciladores procedurales + máquina de estados
      idle/walking/sleeping/playing con cross-fade 200ms + blink aleatorio
- [x] `zones/santuario/SantuarioScene.ts`: diorama 3 niveles, nidos con anillo de
      progreso de incubación, **nido→camita con nombre** cuando el axolotito nació,
      deambular con pausas, mesa de amigos como hotspot interactivo
- [x] GameCanvas: builder del Santuario registrado, `setAxolotitos` en vivo,
      hotspots → `onStallClick` vía WorldBridge
- [x] Datos reales: `mapBackendAxolotito` (rows de GET /auth/axolotitos/{userId} →
      AxolotitoData) + fetch en page.tsx con flag (los axolotitos NO vienen en /auth/sync)
- [x] Santuario HTML viejo oculto con flag (tab santuario muestra el diorama;
      main con pointer-events-none para tocar el mundo)
- [x] Dev proxy same-origin `/api/v1`→:8001 en next.config (pruebas en :3001/LAN sin CORS)
- [x] **Fix web/desktop**: PAINTED_BOUNDS (overscan lateral) + CameraRig prioriza alto
      completo con clamp horizontal — en 16:9 se revelan laterales en vez de recortar
      el alto (plan §3.4). Escenas pintan el overscan; vegetación decorativa lateral
- [x] Hotspot mesa-amigos → HostingSetupModal (antes provisional a tab `amigos`)
- [x] **Sistema de paneles overlay**: con flag, los paneles HTML viven ocultos
      (`panelVisible` en page.tsx); se abren por hotspot del diorama o botón flotante
      📜 (PANEL_LABELS por tab) y el dock los cierra al navegar. Santuario HTML
      vuelve a estar disponible como panel de gestión
- [x] Huevos de incubación reales en los nidos (`mapIncubationToEgg` desde
      /incubation/user — horasRestantes; anillo dorado + tag "¡listo!" al terminar)
- [x] **TianguisScene** (Fase 2 parcial): 5 puestos tocables (booster/adopción/
      fountain-banco/forja/p2p) con rebote de cartón GSAP + guirnalda de banderines
      ondulando; hotspots → panel tienda (fountain abre banco)
- [x] Embarcadero social: trajineritas con toldo, punto online/offline, nickname,
      meciéndose en el agua (4 visibles + "+N en la canasta"); canasta 🧺 → AmigosPage.
      Datos: GET /social/friends → `mapFriendInfo` → `GameCanvasHandle.setAmigos`
- [x] Partículas según quality tier (no en ligera): Zzz al dormir, burbujas al nadar
- [x] Burbujas de acción ❤️/👁/🎲 sobre la trajinerita: ❤️ like en sitio (POST
      /social/like + toast, sin abrir panel), 👁 visita directa (AmigosPage prop
      `visitFriendId` → FriendCaveView), 🎲 invitar → HostingSetupModal con el
      amigo preseleccionado
- [x] page.tsx: `mesa-amigos` y burbuja 🎲 → HostingSetupModal sobre el mundo
      (visibilidad inicial "friends"; con invitado prellena nombre + banner).
      Valida mesa vía fetchCaveStatus (cacheado); sin mesa → toast + panel
      Santuario. Al crear: toast y se queda en el mundo
- [x] Fix carrera de datos del mundo: `canvasReady` (onReady de GameCanvas) gatea
      los fetch de axolotitos/amigos/podio — antes corrían con el token pero sin
      canvas montado (onboarding/datosBanco) y los `set*` caían al vacío (amigos
      nunca aparecían en el embarcadero)
- [x] **Rediseño del Santuario** (5 commits, 2026-06-11; reemplaza el primer
      intento de decoraciones-en-nidos con localStorage que fue descartado):
      - Backend: taxonomía AMBIENTE/LUZ/MESA/MANTEL/SILLAS/FONDO/ESPECIAL en
        `cave_decor.py` (`_slot_layout` cuadra con decor_slots 2→16; MANTEL
        exige MESA; slots omitidos del body vuelven al inventario; GET incluye
        `slots` + `items` detalle). 19 tests en `tests/unit/test_cave_decor.py`.
      - Backend: `seed_cave_decor.py` (23 CAVE_ITEM, precios CAVE_DECOR_PRICES
        300/900/2500/7500 FRJ) y CAVE_ITEM exento de wallet Web3 en /shop/buy.
      - Diorama: zona superior solo crianza — 8 slots en 2 filas según `spots`
        de /cave/status (`setCaveStatus`); bloqueados = roca+🔒+Nv; hotspots
        `nido-*` abren el panel Santuario.
      - Diorama: sala con `setDecoraciones` (GET /cave/decorations) — mesa con
        skin/mantel/sillas (table_seats reales), tinte AMBIENTE, chips de slot
        (+ punteado / emoji) con hotspot `decor:<slot_id>`.
      - `DecorSlotPanel` (tabs Equipar/Comprar con FRJ, bonos al pie) + fila
        "Bazar del Cenote" en OfficialTab. Borrados: decorStorage.ts,
        CuevaDecorPanel, CaveDecorationPanel legacy huérfano.
- [x] Transformación animada nido→camita (`playHatchAnimation`: huevo efímero
      tiembla → cascaritas + destello → camita con back.out; tracking de
      `prevNestKinds` por slot; reduced-motion lo salta)
- [x] Mundo activo validado por usuario en móvil y web ✓

### Fase 2 — Tianguis, esqueleto Pirámide, transiciones
- [x] TianguisScene: 5 puestos tocables + guirnalda de banderines (ver Fase 1 arriba)
- [x] **PiramideScene**: escena ancha 3240px con las 3 subzonas — Cámara de la Suerte
      (3 gashapones con domo de cápsulas), Explanada (pirámide escalonada + podio con
      **puppets reales del top-3** vía GET /ranking/axolotitos), Cenote de las Salas
      (Charco de Novatos + Fosa del Campeón). Hotspots: podio→rankings,
      gashapon→cápsulas, salas→jugar. `GameCanvasHandle.setPodio` + fetch en page.tsx
- [ ] Re-skin HTML por tokens (Store boletos, SettlingScreen recibo, Inventory códice, VipModal)
- [x] Store: props `initialSection`/`sectionNonce` — forja→melter, p2p→market,
      booster/adopción→official (cableado en page.tsx onStallClick)

### Fase 3 — Cenote de las Salas y mesa de competencia

> ⚠️ **Gap descubierto (2026-06-11)**: las salas hosteadas NO tienen UI de listado
> ni de join hoy — `MultiplayerLobby.tsx` quedó huérfano tras PlayMode v2 (nadie lo
> renderiza) y el wizard solo ofrece CPU/oficiales. Además `GET /multiplayer/player-rooms`
> solo lista `visibility == "public"` (las salas "friends" de la mesa de amigos son
> invisibles incluso ahí). Las "trajineras hosted" del Cenote deben resolver listado
> + join, y necesitarán endpoint autenticado que incluya salas de amigos (sub-tarea
> backend).
- [x] `lib/loteria/winPatterns.ts`: espejo cliente de los patrones del backend
      (line/cuadrito/pocito/esquinas/cruz/cruz_diagonal/l_shape/z_shape/full_board)
      + `cartasFaltantes(marked, winPatterns)` + `tablillaTension(faltantes)`
      (escala 0.6/1.0/1.4 + matchPoint). ⚠️ Mantener sincronizado con game_logic.py
- [ ] Re-skin papel de CenoteRoom/CircularTable/TableSeat/GritonCharacter
- [ ] Tablillas sobre cada asiento usando cartasFaltantes + tablillaTension
      (datos: player_states_json del game-state + win_patterns del room_config)
- [ ] PersonalityReactions extendido a 6 naturalezas (tabla en plan §5)
- [ ] Robo-Axolotes para boards NPC (is_npc_pool) — set de texturas latón en el puppet
- [ ] tension_level del backend → ambiente global (música/caustics/gritón)

### Fase 4 — Cámara de la Suerte, cielo lunar, tutorial
- [ ] (ver plan §8 Fase 4)

### Fase 5 — Pulido, perf y rollout
- [ ] (ver plan §8 Fase 5)

## Bitácora de checkpoints

| Fecha (UTC) | Commit | Qué se hizo |
| :--- | :--- | :--- |
| 2026-06-11 | 4601ff3 | Worktree + rama creados; plan v2.1 y checkpoint iniciales |
| 2026-06-11 | 06466f7 | Fase 0 completa: motor Pixi v8, cámara, zonas, cortina, dock macro, flag |
| 2026-06-11 | 0f961a4 | Fase 1 núcleo: rig puppet cut-out + SantuarioScene (nidos/camitas, deambular, mesa hotspot) |
| 2026-06-11 | 94a0174 | Dev proxy same-origin para probar en :3001/LAN sin CORS |
| 2026-06-11 | 22b8967 | Axolotitos reales en el diorama (fetch /auth/axolotitos + mapper) y Santuario HTML oculto con flag |
| 2026-06-11 | 9164784 | Fix cámara desktop (overscan + alto completo); mesa-amigos → tab amigos. Validado por usuario en móvil y web ✓ |
| 2026-06-11 | 4997950 | Paneles overlay ocultos por defecto + TianguisScene con 5 puestos + huevos de incubación reales. Validado ✓ |
| 2026-06-11 | df12139 | PiramideScene: 3 subzonas con paneo, podio top-3 con puppets reales, gashapones y pozas tocables. Validado ✓ |
| 2026-06-11 | a9a296f | Embarcadero social (trajineritas + canasta) y partículas Zzz/burbujas por tier |
| 2026-06-11 | 61cfd5f | Fix centrado de subzonas en web: `focusMaxW` (zoom de enfoque con recorrido de paneo) + clamp vertical de cámara |
| 2026-06-11 | 91af004 | Pirámide re-layout 5160px: subzonas separadas — en web una sección a la vez, extremas centradas. Validado ✓ ("quedó conmadres") |
| 2026-06-11 | 6fcfa82 | Store abre sección por puesto (forja→melter, p2p→market) + winPatterns.ts (cartasFaltantes/tablillaTension) base de Fase 3 |
| 2026-06-11 | 2d51702 | Burbujas de acción ❤️/👁/🎲 en trajineritas (like en sitio, visita directa a FriendCaveView, invitar provisional). Rama renombrada a task/task-1781159264-84-rediseno-visual-papel-picado |
| 2026-06-11 | b4b649c | Mesa de amigos y burbuja 🎲 → HostingSetupModal sobre el mundo (visibilidad friends, invitado preseleccionado, validación de mesa en la cueva) |
| 2026-06-11 | f584a43 | Fix QA usuario: canvasReady gatea fetches del mundo (amigos no salían), crear sala se queda en el mundo con toast (PlayMode no lista hosteadas). Gap Fase 3 documentado: salas hosteadas sin UI de listado/join |
| 2026-06-11 | 968c91a | Decoraciones de cueva v1 (localStorage alrededor de nidos) — DESCARTADO: el usuario corrigió el concepto con imagen de referencia |
| 2026-06-11 | 85510ea | Backend: taxonomía de slots tipados (`_slot_layout`, MANTEL exige MESA, removals devuelven a inventario) + 17 tests |
| 2026-06-11 | 547566d | Backend: seed de 23 decoraciones FRJ + CAVE_ITEM sin requisito de wallet en /shop/buy |
| 2026-06-11 | f6b8792 | Diorama: zona de crianza dinámica — 8 nidos en 2 filas, bloqueados con candado/Nv, hotspots nido-* |
| 2026-06-11 | 1991cc2 | Diorama: sala con slots tipados — mesa skin/mantel/sillas, tinte AMBIENTE, chips decor:<slot_id> |
| 2026-06-11 | — | DecorSlotPanel (Equipar/Comprar FRJ/bonos) + Bazar del Cenote en tienda + limpieza del sistema v1 |
| 2026-06-11 | (anterior) | Fix 404: registrar `cave_decor.router` en main.py (nunca se montó — el diorama no mostraba slots). Seed corrido (23 items) |
| 2026-06-11 | (este) | Backend reiniciado (router OK, 401 vs 404) + sync dev→rama + eclosión animada nido→camita en SantuarioScene. ⏳ Falta: validación visual del usuario |

## Notas para el verificador humano

- Para ver el mundo: `NEXT_PUBLIC_PAPER_WORLD=1` en `frontend/.env.local` y rebuild.
- Sin el flag, el juego debe verse y comportarse EXACTAMENTE igual que en `dev`.
