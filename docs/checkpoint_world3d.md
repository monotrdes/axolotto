# CHECKPOINT — Mundo Diorama 3D de Papel (task-1781252081-99)

> **⚠️ FUENTE DE VERDAD DE PROGRESO** del rediseño visual 3D. Si eres una IA
> reanudando tras un /clear: este archivo + `git log` de `dev` son la verdad.
> Ignora memorias de sesión que lo contradigan.

## Protocolo de reanudación

1. Trabaja en `D:\Axolotto_2026\axolotto`, rama `dev`, commits directos a `dev`
   (conventional commits). NUNCA pushear a main/master.
2. Lee la decisión y el plan: `docs/plan_migracion_estilo_diorama_isometrico.md`
   (bloque "ACTUALIZACIÓN 2026-06-12" al inicio).
3. Referencias visuales canónicas: los 2 concept art del usuario (sesión
   2026-06-12) reflejados en `docs/prototipos/tianguis_demo_3d.html` (prototipo
   aprobado con VoBo) y capturas `tianguis_shot*.png` en esa carpeta.
4. Tras cada unidad de trabajo: actualizar este checkpoint (estado + bitácora)
   y commitearlo EN EL MISMO commit del avance. Entrada en `wiki/CHANGELOG.md`
   en cambios significativos.
5. Verificación: `npx tsc --noEmit` y `npx eslint <archivos>` en `frontend/`.
   NO arrancar servidores. Para iterar visualmente los prototipos:
   `frontend/_shot.mjs` (untracked) — `node _shot.mjs <html> <out.png> <w> <h>`
   con Playwright, capturas en `docs/prototipos/`.
6. Validación visual del usuario al cierre de cada fase.

## Decisiones tomadas (NO re-litigar)

- **Motor: three.js** — mundo 3D de papel extruido ("maqueta en caja").
  Cámara ortográfica dimétrica **34°** (frontal suficiente para ver tenderos
  bajo los toldos). NO R3F — three vanilla + módulo propio.
- **Axolotitos: billboards/puppets 2D siempre orientados a cámara**, y DEBEN
  poder **dar la espalda** (vista frontal Y trasera; evaluar ¾ si hace falta).
- Las 3 macrozonas existentes se conservan (Santuario/Tianguis/Pirámide);
  solo cambia el estilo visual. Migración zona por zona; Pixi sigue
  rendereando las zonas no migradas (swap de canvas bajo la cortina).
- Flags: `NEXT_PUBLIC_PAPER_WORLD=1` + `NEXT_PUBLIC_WORLD3D=1` (ambos ya en
  `frontend/.env.local`; son build-time → rebuild para ver cambios).
- La forja ahora es **El Reciclón** (cartas de lotería repetidas → tickets).
  El hotspot conserva el id `forja` (cableado de page.tsx intacto).
- Ids de hotspot del Tianguis 3D: `fountain`=Banco, `forja`=El Reciclón,
  `booster`=Venta de Sobrecitos, `adopcion`=Webitos Adopción, `p2p`=Trajineras.
- Quality tiers reusados de `world/engine/qualityTier.ts` (sombras off en
  "ligera", DPR cap 1.5/2).

## Arquitectura (dónde está cada cosa)

- `frontend/components/world3d/ThreeWorldEngine.ts` — renderer/cámara/luz/loop,
  raycast de hotspots (`userData.stallId`), `focusStall`/`resetFocus` con lerp,
  parallax puntero, pausa por visibilidad/UI.
- `frontend/components/world3d/paperPrimitives.ts` — paleta PAL + helpers:
  `paper()` (extrusión con canto), `terraceStack`, `picadoShape`, `sign`,
  `textPlane`, `plant`, `blobShape`...
- `frontend/components/world3d/TianguisScene3D.ts` — escena del Tianguis
  (port literal del prototipo). Expone `World3DScene` (group/hotspots/
  animations/stallFocus/playMelt/dispose) y anclas vacías **`attendant:<id>`**
  en cada puesto para los tenderos billboard.
- `frontend/components/world/GameCanvas.tsx` — integración: listener de
  `zoneSettled` del bridge → si macro === "tianguis" monta three y oculta el
  canvas Pixi (y viceversa). `focusStall`/`resetFocus`/`playMeltAnimation`
  ya rutean a 3D cuando `active3dRef` está activo.

## Estado actual

- **Último commit de avance**: `278bd88` (Tianguis 3D + docs) y el commit que
  contiene este checkpoint.
- Tianguis 3D funcionando detrás de los flags. tsc + eslint limpios.
- ⏳ **Pendiente validación visual del usuario en la app real** (ya validó los
  prototipos; falta verlo en su build tras rebuild).

## PENDIENTES (en orden)

### P1 — "Manita de gato" al Tianguis 3D (acercarlo más al concept)
El port fue literal del prototipo procedural; falta el jugo visual del concept:
- [ ] Textura de grano de papel (overlay sutil en terrazas/fondo/agua; por tier,
      off en "ligera").
- [ ] Gradiente de atardecer en el fondo (papel morado → cálido arriba) y
      mejores colores de colinas (el concept va arena→durazno→teal con más
      contraste y capas más altas).
- [ ] Agua: caustics/ondas concéntricas suaves alrededor de orillas y barcas
      (ahora solo hay vetas elípticas), espuma de borde en plaza/rocas.
- [ ] Papel picado con troquelado real (agujeros en el shape, no solo dentado).
- [ ] Tipografía de letreros con más carácter (la del concept es serif gruesa
      tipo cartel; hoy es system-ui).
- [ ] Piedras del camino con forma más orgánica y mejor contraste.
- [ ] Micro-interacciones de hotspot: rebote de cartón al tocar un puesto
      (hoy solo navega), highlight al hover en desktop.
- [ ] Viñeta/marco: el prototipo HTML tiene viñeta CSS — en la app no se
      replicó. Decidir overlay equivalente (div con radial-gradient sobre el
      canvas 3D, pointer-events-none).

### P2 — Axolotitos puppet billboard 2D (siguiente fase grande)
- [ ] `world3d/AxolotitoBillboard.ts`: plano(s) con el puppet 2D estilo papel.
      **Requisito: vista frontal Y trasera** (dar la espalda) — decidir entre
      2 sets de texturas (front/back) con flip según dirección de movimiento
      vs cámara, o rig de partes en 2 planos. Reusar el sistema de partes por
      ADN existente (`world/puppet/parts/` — gill/eye/mouth/tail/forehead/limb
      _type + SKIN_COLORS) rendereado a CanvasTexture/offscreen.
- [ ] Tenderos estáticos en las anclas `attendant:<id>` de TianguisScene3D
      (5 puestos), con idle sutil (branquias, parpadeo).
- [ ] Transeúntes: 2-4 axolotitos del usuario deambulando por la plaza
      (paths sobre el plano del suelo, depth-sort automático del 3D, espalda
      cuando caminan hacia arriba/lejos).
- [ ] Sombra de contacto bajo cada billboard.

### P3 — Migrar Santuario al diorama 3D
- Mismo patrón que Tianguis (escena 3D + swap en zoneSettled). Conservar TODOS
  los contratos de datos: setAxolotitos/setCaveStatus/setDecoraciones/
  setAmigos, hotspots `nido-*`, `decor:<slot_id>`, mesa-amigos, eclosión.

### P4 — Migrar Pirámide (3 subzonas con paneo) + retirar Pixi
- Paneo de cámara entre subzonas en 3D (el motor ya tiene lerp de target).
- Al final: quitar pixi.js del bundle y limpiar `components/world/` muerto.

### P5 — Tarea taskboard
- task-1781252081-99 en el tablero — mantener actualizada con /taskboard
  (solo el usuario puede invocarlo; pedírselo cuando haga falta).

## Bitácora

| Fecha | Commit | Qué se hizo |
| :--- | :--- | :--- |
| 2026-06-12 | 278bd88 | Tianguis 3D: motor three.js + escena port del prototipo aprobado + swap Pixi↔three en GameCanvas + flags + docs/prototipos |
| 2026-06-12 | (este) | Checkpoint creado; flag WORLD3D agregado a .env.local del usuario; pendientes P1-P5 definidos |
