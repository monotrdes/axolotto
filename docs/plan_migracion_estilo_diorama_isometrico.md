# Plan extendido — Migración al estilo "Diorama Isométrico de Papel" (concept art 2026-06-12)

> **⚠️ ACTUALIZACIÓN 2026-06-12 (decisión del usuario, VoBo explícito):**
> 1. **Motor: three.js real**, NO proyección falsa en Pixi (§3.1 queda obsoleto).
>    El mundo es 3D de papel extruido ("maqueta en caja", cámara ortográfica
>    dimétrica ~34°); **los axolotitos serán billboards 2D siempre orientados
>    a cámara**. Prototipos aprobados: `docs/prototipos/diorama_demo_3d.html`
>    y `docs/prototipos/tianguis_demo_3d.html` (referencia visual canónica).
> 2. **Las zonas existentes se conservan** (Santuario/Tianguis/Pirámide) —
>    solo cambia el estilo visual. Migración zona por zona, empezando por el
>    Tianguis (implementado en `frontend/components/world3d/`, flag
>    `NEXT_PUBLIC_WORLD3D=1` adicional a `NEXT_PUBLIC_PAPER_WORLD=1`).
> 3. **La forja se rediseñó como "El Reciclón"** (cambio de cartas de lotería
>    repetidas por tickets). El hotspot conserva el id `forja` para no tocar
>    el cableado de page.tsx. Puestos del Tianguis 3D: BANCO (`fountain`),
>    EL RECICLÓN (`forja`), VENTA DE SOBRECITOS (`booster`), WEBITOS ADOPCIÓN
>    (`adopcion`), TRAJINERAS P2P (`p2p`).
> 4. Toldos altos y casi planos + cámara 34° para que el **tendero de cada
>    puesto sea visible** detrás del mostrador (anclas `attendant:<id>` listas
>    en la escena para los billboards).

> **Referencia visual**: concept art entregado por el usuario (Gemini, 2026-06-12) —
> diorama isométrico de papel recortado con axolotitos cuadrúpedos jugando lotería
> en una mesa, rueda "JUGAR" tallada en el terreno, cofre de monedas y banderines
> de papel picado como marco y como botones.
>
> **Relación con el trabajo existente**: esto NO arranca de cero. Es la evolución
> visual del Mundo Papel Picado 2.5D (plan `plan_task-1781159264-84_rediseno_visual_papel_picado.md`,
> checkpoint `checkpoint_task-1781080168-76.md`). El motor (PixiJS v8 + GSAP), el
> WorldBridge, las zonas, los hotspots, el quality tier y el feature flag
> `NEXT_PUBLIC_PAPER_WORLD` se conservan. Lo que cambia: **ángulo de cámara,
> composición, terreno, rig del puppet y pipeline de assets**.

---

## 1. Análisis del concept art (game design + UX)

### 1.1 Cámara y proyección

- **Proyección dimétrica tipo "diorama en caja"** (~30° de elevación, rotación ~45°):
  el escenario es un rombo visto desde arriba-frente, como una maqueta sobre una
  mesa. NO es isometría de tiles — es una **escena pintada en falsa perspectiva**:
  cada asset se dibuja ya proyectado y se compone en 2D con depth-sort por `y`.
- El fondo exterior al rombo es **papel oscuro morado/índigo** con viñeta — el
  diorama "flota" sobre la mesa de trabajo. Esto da un marco natural para UI HTML
  (toasts, contadores) sin invadir la escena.
- **Implicación técnica**: seguimos en Pixi 2D. No se necesita three.js ni motor
  iso. Lo que cambia es la convención de dibujo de TODOS los assets (proyectados a
  ~2:1) y que el suelo gana profundidad real: los personajes caminan "hacia
  dentro" (cambian `y` y escala levemente), no solo de lado a lado.

### 1.2 Composición asimétrica (lo que la hace funcionar)

Lectura en Z del concept:

1. **Foco primario** (centro-izquierda): la mesa con 6 axolotitos jugando — vida,
   narrativa, social. Es el "corazón" y NO está centrado: está desplazado para
   dejar respirar al CTA.
2. **CTA dominante** (arriba-derecha): la rueda "JUGAR" tallada en el terreno
   (verde limón, el color más saturado y la forma más grande). Es UI diegética:
   el botón de jugar ES parte del mundo.
3. **Economía** (abajo-centro): cofre "CORCHOLATAS Y FRIJOLITOS" sobre un montículo
   — punto de entrada al banco/wallet.
4. **Navegación secundaria** (derecha-medio): banderines colgados "OPCIONES" y
   "TIENDA" con iconos (maraca, cofre) — botones colgantes de papel.
5. **Masa de equilibrio** (izquierda): formaciones rocosas en terrazas con plantas
   — peso visual sin interactividad, compensa la rueda.
6. **Marco**: guirnaldas de papel picado en los 4 bordes del rombo; los banderines
   de las esquinas inferiores son **etiquetas de zona** ("EL BARRIL", "EL FRIJOLITO")
   — señalética diegética de a dónde lleva cada lado del diorama.
7. **Flujo**: un río/camino de agua clara serpentea desde abajo-izquierda hacia el
   centro — guía la mirada y es el "carril" por donde nadan/entran los axolotitos.

**Principios extraíbles** (aplicar a TODAS las zonas, no copiar el layout literal):
- 1 foco vivo (personajes) + 1 CTA diegético dominante + 1-2 anclas de economía/nav.
- Nada centrado; pesos balanceados en diagonal.
- El agua como conector de composición y como sistema de spawn/despawn de puppets.
- Bordes = papel picado que enmarca y etiqueta (cada lado del rombo puede ser un
  "portal" hacia otra macrozona → afordancia de navegación entre Santuario,
  Tianguis y Pirámide).

### 1.3 Estilo de arte

- **Papel recortado apilado**: el terreno son **terrazas topográficas** — pilas de
  capas de papel/cartón con bordes redondeados irregulares, cada capa con su
  sombra interior suave. Las rocas, montículos y la pirámide se construyen igual.
- **Sombras**: drop-shadow suave y corta (luz cenital-frontal), + oclusión sutil
  donde una capa toca otra. Nada de sombras duras largas.
- **Textura**: grano de papel/fibra visible en zonas grandes (fondo morado, agua,
  terrazas). En Pixi: overlay de textura de ruido tileada con blend `multiply`/
  `overlay` a baja alfa, por quality tier (apagada en tier ligera).
- **Paleta** (muestreada del concept; refinar los tokens `--papel-*`/`--agua-*`):
  - Agua: teal saturado `#1798A8 → #0F7E96`, caminos de agua clara `#BDE8E4`.
  - Terrazas: verdes salvia/oliva `#7FA86E / #9DBE8A / #C7D9A8` y arenas `#E8DEC4`.
  - CTA: verde limón `#B8D94A`.
  - Madera: café cálido `#9C6B3F / #7A4E2C`.
  - Axolotito base: rosa `#F6A8BC` con branquias `#E8889E`.
  - Papel picado: magenta `#E04A7A`, amarillo `#F2C23E`, teal `#2FB8B0`, crema.
  - Fondo exterior: índigo/morado `#3A3151 → #2A2440` con viñeta.
- **Borde de papel**: el filo blanco actual (`PAPER_EDGE`) se mantiene como sello
  del estilo, pero más fino y solo en personajes/props, no en terrazas (ellas se
  definen por capas + sombra).

### 1.4 El axolotito (cambio mayor)

El concept muestra axolotitos **cuadrúpedos**, naturalistas-chibi:

- Cuerpo regordete horizontal, cabeza enorme (~40-45% del largo), sin cuello.
- **4 patas cortas** en postura "sprawl" (codos hacia afuera), con deditos.
- **3 branquias por lado** bien separadas, con tallo + filamentos — el rasgo
  identitario; en el concept ondean independientes.
- Cola ancha con aleta que continúa como **cresta dorsal** sobre el lomo.
- Cara mínima: ojos de punto negro con brillo, sonrisa simple, mejillas opcionales.
- Posturas del concept: sentado a la mesa (erguido sobre patas traseras, manitas
  sobre la mesa), caminando en sprawl, nadando (cuerpo extendido, patas plegadas).

**Decisión**: migrar el rig bípedo actual a un **rig cuadrúpedo con 3 stances**
(sprawl-walk / sit-upright / swim). El bípedo actual ya tiene la infraestructura
correcta (osciladores, perfiles de movimiento, cross-fade, partes por ADN) — se
reusa la arquitectura, cambia la jerarquía y las proporciones.

### 1.5 UI diegética y UX móvil-first

- **Todo botón principal vive dentro del mundo**: rueda JUGAR (tallada, gira al
  presionar), banderines colgantes (TIENDA/OPCIONES — se mecen, tirón al tocar),
  cofre (rebota/se abre → panel banco). Los paneles HTML overlay existentes se
  conservan tal cual; solo cambian los gatillos visuales.
- **Targets táctiles**: cada hotspot diegético necesita hit-area ≥ 88×88 px
  lógicos en el encuadre móvil, aunque el dibujo sea menor.
- **Móvil (9:16)**: el rombo completo no cabe — la cámara encuadra una **vista
  vertical del diorama** (foco + CTA visibles juntos; el resto se descubre con
  paneo suave o queda en overscan). Mantener el sistema actual de
  `Framing`/`PAINTED_BOUNDS` con encuadres re-diseñados por zona.
- **Web (16:9)**: el rombo completo con su marco de papel picado y fondo morado —
  ahí el concept se reproduce literal.
- **Jerarquía por saturación**: el CTA siempre es el elemento más saturado de la
  escena (verde limón); la economía en dorados; navegación en banderines de color
  papel picado. Regla simple y consistente entre zonas.

---

## 2. Gap analysis — estado actual → destino

| Dimensión | Hoy (papel picado v1) | Destino (concept) |
|---|---|---|
| Cámara | Frontal 2.5D, capas planas verticales | Dimétrica ~30°, diorama en rombo con profundidad de suelo |
| Terreno | Bandas/Graphics planos | Terrazas topográficas apiladas pre-proyectadas |
| Puppet | Bípedo erguido, 9 grupos de partes Graphics | Cuadrúpedo 3-stance, ~20 partes, atlas de sprites |
| Movimiento | X lineal + bob | Pathing en plano proyectado (x,y) con escala por profundidad y depth-sort |
| UI | Dock HTML + hotspots simples | UI diegética (rueda/banderines/cofre) + dock HTML reducido |
| Assets | 100% Graphics procedurales | Atlas PNG por zona + partes de puppet (Graphics queda de fallback) |
| Marco | Sin marco | Guirnaldas papel picado perimetrales + fondo papel morado + viñeta |

Lo que NO cambia: WorldEngine, CameraRig, ZoneManager, WorldBridge, quality tiers,
flag `NEXT_PUBLIC_PAPER_WORLD`, paneles HTML overlay, contratos de datos
(`setAxolotitos`, `setCaveStatus`, `setDecoraciones`, `setAmigos`, `setPodio`),
hotspot ids (`nido-*`, `decor:*`, puestos del tianguis, etc.).

---

## 3. Arquitectura técnica de la migración

### 3.1 Proyección y suelo

- Nuevo módulo `world/engine/projection.ts`: helpers del plano diegético —
  `groundToScreen(gx, gy)` (rombo 2:1), `depthScale(gy)` (escala 0.92→1.06 según
  profundidad), `sortY(container)` para z-index automático.
- Cada escena define su **GroundPlan**: polígono del rombo, máscaras de agua,
  caminos navegables (splines para wanderController), y anclas de props.
- `wanderController` pasa de 1D (x) a 2D sobre el camino del agua/suelo con
  depth-sort y escala.

### 3.2 Terreno por terrazas

- `world/props/terraces.ts`: builder de pila topográfica — recibe contornos
  (array de blobs con offset/altura/color) y genera capas con sombra interior.
  Fase Graphics primero (blobs procedurales con ruido), atlas después.
- Sombra de contacto y highlight de borde superior por capa (baked en atlas; en
  Graphics, stroke sutil + sombra elipse).

### 3.3 Puppet v2 — separación en partes para ADN (pedido explícito del usuario)

Nuevo `puppet/quadRig.ts` + `puppet/quadAnimator.ts` (conviven con biped hasta
paridad; un flag interno `PUPPET_V2` decide cuál construye `AxolotitoPuppet`).

**Inventario de partes v2** (cada una es un nodo independiente del rig, sustituible
por sprite del atlas, y candidata a gen del ADN):

| # | Parte | Nodos | Gen que la controla | Estado del gen |
|---|---|---|---|---|
| 1 | Cráneo/cabeza | 1 | `skin_color` (tinte) + forma por especie | existe |
| 2 | Hocico/snout | 1 | futuro `snout_type` | nuevo |
| 3 | Mejillas/rubor | 2 | futuro `blush_type` (none/dot/heart) | nuevo |
| 4 | Frente/corona | 1 | `forehead_type` | existe |
| 5 | Ojos — iris+pupila+brillo | 2×3 capas | `eye_type` (+ futuro `eye_color`) | existe |
| 6 | Párpados (abierto/cerrado/entrecerrado) | 2×3 | `eye_type` | existe |
| 7 | Boca (variantes + expresiones happy/o/uh) | 1×N | `mouth_type` | existe |
| 8 | Branquias: **6 tallos individuales** (3/lado) | 6 | `gill_type` | existe (hoy 1 grupo/lado → pasar a 3 nodos/lado con fase de oscilación en cascada) |
| 9 | Filamentos de branquia (hijo de cada tallo) | 6 | `gill_type` | existe |
| 10 | Torso | 1 | `skin_color` | existe |
| 11 | Panza (parche color secundario) | 1 | futuro `belly_color` | nuevo |
| 12 | Patrón/marcas (overlay moteado/rayas/leucístico) | 1 | futuro `pattern_type` | nuevo |
| 13 | Cresta dorsal (lomo→cola) | 1 | `tail_type` (comparte gen con cola) | existe |
| 14 | Patas delanteras: muslo + manita (4 deditos) | 2×2 | `limb_type` | existe |
| 15 | Patas traseras: muslo + pata (5 deditos) | 2×2 | `limb_type` | existe |
| 16 | Cola: base + aleta + punta | 3 | `tail_type` | existe |
| 17 | Sombra de contacto | 1 | — | existe |
| 18 | Anchors de accesorios: cabeza/cuello/espalda | 3 vacíos | inventario (futuro) | nuevo |

- `parts/types.ts` extiende `PartCtx` con `bellyTint`, `patternTint`, `stance`.
- Los genes nuevos (`snout_type`, `blush_type`, `belly_color`, `pattern_type`,
  `eye_color`) se diseñan en el rig desde YA con valor default, y se conectan al
  backend/contrato DNA en una sub-tarea posterior (el encoding de `Axolotitos.sol`
  tiene bits libres — verificar antes de prometer on-chain).
- **Stances** (perfiles de `motionProfiles` nuevos): `sprawl-idle`, `sprawl-walk`,
  `sit` (mesa/jugar), `swim`, `sleep`. Cross-fade existente se reusa.
- Branquias: oscilador con desfase por índice (0.0/0.15/0.3s) → el "ondeo en
  cascada" del concept. En swim, amplitud ×1.6.

### 3.4 Pipeline de assets

1. **Fase Graphics-proyectado** (sin artista): re-dibujar terrazas/props/puppet en
   proyección dimétrica con Graphics — valida composición, cámara y gameplay.
2. **Fase Atlas**: convención ya existente `frontend/public/world/atlas/` —
   - `terrain-<zona>.json/png`: terrazas, agua, props grandes.
   - `axolotito-parts.json/png`: TODAS las partes v2 en blanco/gris neutro para
     tintar por `skin_color` (las marcas/panza en capa aparte).
   - `ui-diegetica.json/png`: rueda JUGAR, banderines, cofre, guirnaldas.
   - `getTextureOrFallback` ya implementa el swap sprite↔Graphics: cada parte cae
     a su Graphics si el atlas no está — el rollout de arte es incremental.
3. Resolución: assets @2x sobre el espacio de diseño 1080; DPR cap 2 ya existe.
4. Presupuesto: ≤ 2 atlas de 2048² por zona en tier alta; tier ligera usa solo
   terrain + puppet (sin overlays de textura de papel).

### 3.5 Encuadres móvil/web

- Espacio de diseño por zona pasa a **rombo apaisado** (~1920×1280 + marco).
  `DESIGN_SPACE`/`PAINTED_BOUNDS`/`MACRO_FRAMINGS` se recalculan:
  - Web: encuadre = rombo completo + marco (concept literal).
  - Móvil: encuadre vertical sobre foco+CTA; paneo horizontal limitado para
    descubrir el resto (clamp ya soportado por CameraRig).
- La Pirámide (5160 de ancho) se re-plantea como **3 dioramas-rombo** conectados
  por agua abierta — el paneo entre subzonas se conserva.

---

## 4. Composición objetivo por zona (aplicando §1.2)

| Zona | Foco vivo | CTA diegético | Economía/nav | Etiquetas perimetrales |
|---|---|---|---|---|
| **Santuario** | nidos/camitas arriba + axolotitos deambulando | mesa de amigos (hospedar) | cofre de decoración FRJ; banderín "TIANGUIS →" | "EL NIDO", "LA CASA" |
| **Tianguis** (≈ el concept) | mesa social / NPCs | rueda JUGAR → tab jugar | cofre banco; banderines TIENDA/OPCIONES; 5 puestos como montículos-terraza | "EL BARRIL", "EL FRIJOLITO" |
| **Pirámide-Explanada** | podio top-3 con puppets | escalinata (rankings) | — | "LA PIRÁMIDE" |
| **Pirámide-Cenote salas** | mesas de sala activas | poza Novatos / Fosa Campeón | — | "EL CENOTE" |
| **Pirámide-Cápsulas** | gashapones | palanca de cápsula | — | "LA SUERTE" |

(El concept es UNA pantalla-hub; nosotros tenemos 3 macrozonas — la rueda JUGAR
vive en el Tianguis/hub y también como FAB del dock. Validar con el usuario si
quiere colapsar hacia un hub único más adelante.)

---

## 5. Fases de trabajo

### F0 — Cimientos de proyección (sin romper nada)
- `projection.ts` + GroundPlan + depth-sort + wander 2D.
- Marco: fondo papel morado + viñeta + guirnaldas perimetrales (Graphics).
- Recalcular encuadres móvil/web. Flag interno `WORLD_ISO=1` para comparar A/B.
- ✅ Criterio: Santuario actual renderiza en rombo con puppets depth-sorteados;
  `tsc --noEmit` + lint limpios; sin flag todo idéntico.

### F1 — Puppet v2 cuadrúpedo
- `quadRig` + `quadAnimator` + stances + branquias×6 en cascada + partes nuevas
  con defaults; mapeo de genes existentes intacto.
- Posturas: sprawl-walk, sit (en banco/mesa), swim por el agua, sleep en camita.
- ✅ Criterio: paridad funcional con bípedo en las 3 zonas; validación visual usuario.

### F2 — Tianguis = concept de referencia
- Terrazas, río, mesa central con axolotitos sentados (los del usuario + amigos),
  rueda JUGAR, cofre banco, banderines TIENDA/OPCIONES, puestos como montículos.
- ✅ Criterio: captura móvil y web comparada lado a lado con el concept; validación usuario.

### F3 — Santuario y Pirámide re-proyectados
- Migrar SantuarioScene (nidos/camitas/decoración/embarcadero) y PiramideScene
  (3 rombos) a terrazas + GroundPlan. Hotspots y datos intactos.
- ✅ Criterio: todos los flujos actuales (incubar, decorar, amigos, podio, salas)
  funcionando; validación usuario por zona.

### F4 — Atlas de arte
- Producir/integrar atlas (terrain, puppet-parts, ui-diegetica) con swap
  incremental vía `getTextureOrFallback`. Textura de papel global por tier.
- ✅ Criterio: tier alta con atlas completo ≥ 55 fps móvil medio; ligera estable.

### F5 — Genes nuevos end-to-end (sub-tarea backend/contratos)
- `pattern_type`, `belly_color`, `blush_type`, `eye_color`, `snout_type`:
  modelo backend + breeding/incubation + (si hay bits) DNA on-chain + sobrecitos.
- ✅ Criterio: tests backend de herencia; render correcto de combinaciones.

### F6 — Pulido y rollout
- Micro-interacciones (rueda gira, banderín tirón, cofre rebote), reduced-motion,
  partículas por tier, QA cross-device, borrar rig bípedo muerto, CHANGELOG.

**Orden y dependencias**: F0 → F1 ⊥ F2(necesita F0) → F3 → F4 (puede solapar F3)
→ F5 ⊥ F6. Validación visual del usuario al cierre de CADA fase (igual que el
flujo del checkpoint actual).

---

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El cambio de cámara invalida layouts ya validados por el usuario | Flag interno `WORLD_ISO` para comparar; migrar zona por zona, no big-bang |
| Rig cuadrúpedo: "sentado a la mesa" tapa la carita en vista dimétrica | Sentado de ¾ con cabeza girada a cámara (como el concept: todos miran ligeramente al frente) |
| Overdraw de terrazas (muchas capas) en móviles bajos | `cacheAsTexture` de la pila de terreno estático tras el build; tier ligera con menos capas |
| Atlas tarda (dependencia de arte) | Fase Graphics-proyectado entrega el look estructural sin artista; swap incremental |
| Genes nuevos sin bits en el contrato DNA | F5 valida `Axolotitos.sol` antes de prometer on-chain; fallback: genes off-chain en backend |
| Móvil: el rombo recortado pierde la gracia del marco | Marco parcial superior/inferior en móvil + viñeta; validar temprano con el usuario en F0 |

---

## 7. Criterios de aceptación globales

1. Sin `NEXT_PUBLIC_PAPER_WORLD` el juego queda EXACTAMENTE igual (regla vigente).
2. Cámara dimétrica, terrazas y marco de papel picado en las 3 macrozonas.
3. Puppet cuadrúpedo con ≥ 18 partes independientes, todas tintables/sustituibles
   por atlas, branquias ×6 con ondeo en cascada, 5 stances.
4. UI diegética: JUGAR/TIENDA/OPCIONES/banco operables desde el mundo en móvil
   con targets ≥ 88px; paneles HTML overlay intactos.
5. 55+ fps en móvil de gama media (tier media), sin regresión de tier ligera.
6. Todos los datos/flujos existentes (incubación, decoración, amigos, podio,
   salas, tienda) funcionando sobre el nuevo render.
7. `npx tsc --noEmit` y `npm run lint` limpios; validación visual del usuario
   por fase; CHANGELOG en cada merge.

---

## 8. Primer paso concreto

F0: crear `frontend/components/world/engine/projection.ts` con `groundToScreen`/
`depthScale`/`sortY`, GroundPlan del Tianguis, y el marco (fondo morado + viñeta +
guirnaldas) — todo detrás de `WORLD_ISO`, con el Santuario actual intacto.
