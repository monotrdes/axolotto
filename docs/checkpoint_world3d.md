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
   NO arrancar servidores. Para iterar visualmente la **escena TS real**
   (untracked, recrear si faltan): `frontend/_harness3d.ts` +
   `docs/prototipos/_world3d_harness.html` —
   `npx esbuild _harness3d.ts --bundle --outfile=../docs/prototipos/_world3d_bundle.js --format=iife`
   y luego `node _shot.mjs _world3d_harness.html _world3d_shot.png 450 920`
   (Playwright; `_shot.mjs` también sirve para los prototipos HTML).
   OJO: el Read de imágenes reescala — comparar capturas con un HTML
   lado-a-lado a la misma escala, no a ojo entre lecturas.
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

- **Último commit de avance**: el commit que contiene este checkpoint (P2
  base). Anteriores: P1 `6a8cea8`, Tianguis 3D `278bd88`.
- Tianguis 3D con "manita de gato" (P1) + tenderos y transeúntes billboard
  (P2) detrás de los flags. tsc + eslint limpios. Verificado visualmente con
  el harness (captura `docs/prototipos/_world3d_shot.png`, untracked).
- ⏳ **Pendiente validación visual del usuario en la app real** (ya validó los
  prototipos; falta verlo en su build tras rebuild).

## PENDIENTES (en orden)

### P1 — "Manita de gato" al Tianguis 3D — ✅ HECHO
- [x] Grano de papel: `configurePaperStyle({grain})` + CanvasTexture 128px
      compartida en `paperMat` (GameCanvas lo apaga en tier "ligera").
- [x] Gradiente de atardecer (CanvasTexture en scene.background del motor:
      morado abajo → rosado cálido arriba) y cordillera trasera teal→durazno→
      arena→crema con capas más altas (paletas de longitud exacta — ojo: el
      wrap de `pal[i % len]` pone el color 0 en la cumbre si n > len).
- [x] Agua: ondas concéntricas expandiéndose (RingGeometry) en barcas y
      orillas + espuma de borde (`flat()` blobs aguaClara bajo las orillas).
- [x] Papel picado con troquelado real (medallón + 2 ojales + diamante como
      holes del shape).
- [x] Tipografía de letreros serif gruesa (Georgia 900).
- [x] Piedras del camino más orgánicas (irr 0.38, 2 tonos, rotación).
- [x] Micro-interacciones en el motor: rebote de cartón al tocar puesto
      (squash con decay) y highlight de hover +5% en desktop
      (`hover:hover and pointer:fine`), cursor pointer. Mapa `fx` por raíz
      de puesto, se aplica DESPUÉS de las animaciones de escena.
- [x] Viñeta: overlay radial-gradient dentro del host 3D en GameCanvas
      (pointer-events-none, igual al prototipo aprobado).

### P2 — Axolotitos puppet billboard 2D — ✅ HECHO (base)
- [x] `world3d/AxolotitoBillboard.ts`: plano con puppet de papel pintado en
      **Canvas2D propio** (decisión: 4 CanvasTextures por axolotito — frente
      pose A/B, frente parpadeo, espalda — y swap de `material.map`; NO se
      rendereó el rig Pixi offscreen para no acoplar motores; solo se reusan
      `skinToTint`/`gillAccent` de `world/puppet/paperParts`). `setWalk(dx,dz)`
      da la espalda al alejarse (dz<0) y espeja por dx. El motor fija el yaw
      de cámara vía `World3DScene.billboards` (deben colgar del root).
- [x] Tenderos en las 5 anclas `attendant:<id>` (skins fijas por puesto) con
      idle (respiración, vaivén de branquias por swap de pose, parpadeo);
      tocarlos dispara el hotspot de su puesto.
- [x] Transeúntes: hasta 4 axolotitos del usuario (no huevos, seed
      determinista por id) deambulan por la plaza con pasitos y pausas;
      espalda al caminar hacia el fondo. Snapshot al entrar a la zona (si
      cambian los axolotitos no se refresca hasta re-entrar — aceptado).
- [x] Sombra de contacto elíptica bajo cada billboard.
- [ ] (Mejora futura) ADN visual completo en el painter: hoy solo varía
      skin/seed; gill/eye/mouth/tail/forehead/limb _type quedan para cuando
      haya atlas de arte o se porte el painter por variantes.

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
| 2026-06-12 | 6a8cea8 | P1 completo: grano de papel por tier, fondo atardecer, colinas con más contraste, ondas+espuma de agua, troquelado real del picado, letreros serif, piedras orgánicas, hover+rebote de hotspots, viñeta en GameCanvas. Harness de captura de la escena TS real (esbuild+Playwright) |
| 2026-06-12 | (este) | P2 base: AxolotitoBillboard (Canvas2D, frente A/B + parpadeo + espalda), tenderos en los 5 puestos, transeúntes del usuario deambulando con espalda al alejarse, sombras de contacto, yaw de billboards en el motor |
| 2026-06-12 | (este) | Tianguis 3D pulido visual: copetes tradicionales en trajineras y overlays HTML/CSS en GameCanvas (guirnaldas animadas y listón inferior de papel) |
| 2026-06-12 | (este) | Tianguis 3D adaptabilidad y refinamiento: puestos compactados en X, zoom automático responsivo en pantallas ultraestrechas (Galaxy Fold/Pixel 7), agua en capas delgadas de papel y remoción del listón inferior |
| 2026-06-12 | (este) | Tianguis 3D pulido final: removidas etiquetas de esquina, 2 trajineras únicamente, letrero de trajineras ensanchado de poste a poste, reubicado puesto de sobresitos en tierra y corregida altura de tenderos en Reciclón, Sobrecitos y Webitos |
| 2026-06-12 | (este) | Efectos subacuáticos en ThreeWorldEngine: implementado fog verde de profundidad, gradiente de Xochimilco turbio para fondo, iluminación acuática bioluminiscente, refracción de luz animada en tiempo real y sistema optimizado de partículas de burbujas flotantes |
| 2026-06-12 | (este) | Tianguis 3D zoom móvil ajustado: reducido minW a 6.0 en ThreeWorldEngine para acercar la cámara y mejorar visibilidad en pantallas estrechas como Galaxy Fold 5 |
| 2026-06-12 | (este) | Ajuste estético subacuático: aclarados los colores del agua y neblina hacia turquesa/esmeralda cristalino y potenciada la intensidad luminosa para evocar un Xochimilco pre-hispánico mágico y alegre |
| 2026-06-12 | (este) | Corrección de visuales subacuáticos: reemplazada neblina exponencial por neblina lineal (THREE.Fog) para mantener nítido el primer plano y evitar que se opaque, y desvinculada la niebla de las burbujas para que resplandezcan siempre |
