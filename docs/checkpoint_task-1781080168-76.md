# CHECKPOINT — task-1781080168-76 — Mundo Papel Picado 2.5D

> **⚠️ FUENTE DE VERDAD DE PROGRESO.** Si eres una IA (o humano) reanudando este trabajo,
> este archivo + el `git log` de esta rama son la verdad. **Ignora memorias de sesión,
> resúmenes de contexto o notas externas si contradicen lo que dice aquí.**

## Protocolo de reanudación (leer SIEMPRE antes de tocar código)

1. Trabaja SOLO en el worktree: `D:\Axolotto_2026\.axolotto_worktrees\task-1781080168-76\`
   Rama: `task/task-1781080168-76-santuario-layout-mvil-vertical-nuevas-categor` (base: `dev`).
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

- **Fase activa**: Fase 1 — Santuario + Puppet System (núcleo puppet + escena base HECHOS)
- **Último commit de avance**: el commit que contiene esta edición (feat(world): fase 1 puppets)
- **SIGUIENTE PASO**: Fase 1 restante, en orden:
  1. **Embarcadero social** en `SantuarioScene` (nivel inferior y=1500): trajineritas
     de amigos (datos: hook `useSocial` / `AmigosPage`) con burbujas ❤️/👁/🎲; requiere
     pasar lista de amigos al canvas (nuevo método en `GameCanvasHandle.setAmigos?` o
     prop via WorldScene) + canasta que abre AmigosPage (tab `amigos`).
  2. **Mesa de amigos**: el hotspot ya emite `onStallClick("mesa-amigos")` — falta que
     `app/play/page.tsx` lo maneje (abrir HostingSetupModal o navegar a jugar).
  3. **Decoraciones**: persistencia localStorage (backend endpoint = sub-tarea aparte)
     y render en el diorama (`setCaveDecorations`).
  4. **Burbujas Zzz** al dormir + partículas burbujas al nadar (solo tier alta/media).
  Después → Fase 2 restante: diorama de la PIRÁMIDE (escena ancha 3240px con las 3
  subzonas: Explanada/podio con puppets del top-3, Cámara de la Suerte con 3
  gashapones, Cenote de las Salas con 2 pozas) + sub-tab del Store según puesto
  tocado (forja→melter, p2p→market: requiere prop initialTab en Store).

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
- [x] Hotspot mesa-amigos → tab `amigos` (provisional; TODO HostingSetupModal)
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
- [ ] Burbujas de acción ❤️/👁/🎲 directas sobre la trajinerita (hoy: tap → AmigosPage)
- [ ] page.tsx: `mesa-amigos` → HostingSetupModal (hoy: tab amigos)
- [ ] Decoraciones reales (⚠️ endpoint backend = sub-tarea; mientras localStorage)
- [ ] Transformación animada nido→camita (hoy es swap estático)
- [x] Mundo activo validado por usuario en móvil y web ✓

### Fase 2 — Tianguis, esqueleto Pirámide, transiciones
- [x] TianguisScene: 5 puestos tocables + guirnalda de banderines (ver Fase 1 arriba)
- [x] **PiramideScene**: escena ancha 3240px con las 3 subzonas — Cámara de la Suerte
      (3 gashapones con domo de cápsulas), Explanada (pirámide escalonada + podio con
      **puppets reales del top-3** vía GET /ranking/axolotitos), Cenote de las Salas
      (Charco de Novatos + Fosa del Campeón). Hotspots: podio→rankings,
      gashapon→cápsulas, salas→jugar. `GameCanvasHandle.setPodio` + fetch en page.tsx
- [ ] Re-skin HTML por tokens (Store boletos, SettlingScreen recibo, Inventory códice, VipModal)
- [ ] Store: prop initialTab para abrir melter (forja) / market (p2p) según puesto

### Fase 3 — Cenote de las Salas y mesa de competencia
- [ ] (ver plan §8 Fase 3)

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
| 2026-06-11 | (este) | Embarcadero social (trajineritas + canasta) y partículas Zzz/burbujas por tier |

## Notas para el verificador humano

- Para ver el mundo: `NEXT_PUBLIC_PAPER_WORLD=1` en `frontend/.env.local` y rebuild.
- Sin el flag, el juego debe verse y comportarse EXACTAMENTE igual que en `dev`.
