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

- **Fase activa**: Fase 0 — Cimientos
- **Último commit de avance**: (ninguno aún — primer checkpoint)
- **SIGUIENTE PASO**: Commit inicial de docs (plan + este checkpoint). Después: instalar
  `pixi.js@^8` y `gsap` en `frontend/`, crear tokens de paleta en `globals.css`,
  y carpeta de convención `frontend/public/world/atlas/`.

## Checklist de fases (espejo del plan §8 — marcar aquí, no en el plan)

### Fase 0 — Cimientos
- [ ] Deps: `pixi.js@^8` + `gsap` instaladas en frontend
- [ ] Tokens de paleta papel/agua en `globals.css`
- [ ] Convención de assets `frontend/public/world/atlas/` + README
- [ ] `WorldBridge.ts` (event emitter React↔mundo)
- [ ] `engine/qualityTier.ts` (detector Alta/Media/Ligera + override)
- [ ] `engine/WorldEngine.ts` (init Pixi, ticker, pausa por visibilidad)
- [ ] `engine/CameraRig.ts` (encuadres por subzona, paneo GSAP, fit 9:16/16:9)
- [ ] `zones/zoneConfig.ts` (3 macrozonas + subzonas Pirámide, mapeo TabId)
- [ ] `zones/ZoneManager.ts` (mount/unmount, carga perezosa subzonas)
- [ ] `GameCanvas.tsx` real detrás de `NEXT_PUBLIC_PAPER_WORLD` (contrato `GameCanvasHandle` intacto)
- [ ] `PaperCurtain.tsx` (cortina CSS entre macrozonas)
- [ ] `ZoneDock` v2: 3 botones macro + sub-pills de Pirámide (TabId legacy intacto)
- [ ] Cableado en `app/play/page.tsx` (ZONE_TABS → 3 macro, zoneToTab actualizado)
- [ ] Verificación: `npx tsc --noEmit` limpio + lint

### Fase 1 — Santuario + Puppet System
- [ ] Atlas/manifest de partes placeholder + `puppet/PuppetFactory.ts` (fromDna)
- [ ] `puppet/PuppetStateMachine.ts` (idle/walk/sleep/blink, cross-fade 200ms)
- [ ] Osciladores procedurales (respiración, bob, branquias, blink)
- [ ] Diorama Santuario: 3 niveles, parallax, nidos con cronómetro, cofre staking
- [ ] Transformación nido→camita al eclosionar
- [ ] Mesa de amigos: hotspot → HostingSetupModal / unirse a sala de amigo
- [ ] Decoraciones reales (⚠️ requiere endpoint backend — sub-tarea; mientras localStorage)
- [ ] Embarcadero social: trajineritas + burbujas like/visitar/invitar; canasta → AmigosPage
- [ ] Activar mundo en Santuario con flag

### Fase 2 — Tianguis, esqueleto Pirámide, transiciones
- [ ] (ver plan §8 Fase 2)

### Fase 3 — Cenote de las Salas y mesa de competencia
- [ ] (ver plan §8 Fase 3)

### Fase 4 — Cámara de la Suerte, cielo lunar, tutorial
- [ ] (ver plan §8 Fase 4)

### Fase 5 — Pulido, perf y rollout
- [ ] (ver plan §8 Fase 5)

## Bitácora de checkpoints

| Fecha (UTC) | Commit | Qué se hizo |
| :--- | :--- | :--- |
| 2026-06-11 | (este) | Worktree + rama creados; plan v2.1 y checkpoint iniciales |

## Notas para el verificador humano

- Para ver el mundo: `NEXT_PUBLIC_PAPER_WORLD=1` en `frontend/.env.local` y rebuild.
- Sin el flag, el juego debe verse y comportarse EXACTAMENTE igual que en `dev`.
