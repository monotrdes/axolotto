# Plan v2.1: Rediseño Visual 2.5D — Universo de Papel Picado Submarino

> **Status**: Planning (v2.1 — 3 macrozonas; la Pirámide engloba juego, rankings y gashapon)
> **Category**: `gamedesign`, `frontend`
> **Priority**: Crítica — Redefinición estética y estructural del juego
> **Taskboard**: `task-1781159264-84`
> **Reemplaza**: v1 (3 zonas sin cobertura del flujo real, Three.js) y v2 (5 zonas planas)

---

## 0. Qué cambió respecto al plan v1 (y por qué)

| Tema | Plan v1 | Plan v2.1 (este) | Razón |
| :--- | :--- | :--- | :--- |
| Zonas | 3 zonas que omitían rankings/gashapon/lunar | **3 macrozonas**: Santuario, Tianguis y **Pirámide (hub de juego con 3 subzonas: Explanada de Rankings, Cámara de la Suerte, Cenote de las Salas)** | Menos fades y cargas (3 escenas en vez de 5); toda la mecánica de juego queda en una sola vista con continuidad espacial. Decisión del usuario, mejora sobre v2 |
| Navegación intra-zona | Fade entre todo | **Paneo de cámara 2.5D dentro de la Pirámide** (sin cortina); cortina de papel solo entre macrozonas | El paneo da la sensación tridimensional que buscaba el plan original, donde sí aporta |
| Motor | Three.js + R3F + drei + postprocessing | **PixiJS v8** (WebGPU con fallback WebGL) + GSAP | El encuadre es 2.5D fijo: geometría 3D real es peso muerto (~600KB+ de three). Pixi es sprite-first, ~3x más ligero, y rinde mejor en gama media Android |
| Estado | Zustand nuevo | React state existente + un `WorldBridge` (event emitter) | `GameCanvas` ya define un contrato imperativo (`GameCanvasHandle`); no se necesita otra librería de estado |
| Mesa multiplayer | Construir desde cero en 3D | **Re-skin y extensión de componentes DOM existentes** (`CenoteRoom`, `CircularTable`, `TableSeat`, `GritonCharacter`, `PersonalityReactions`, `VictoryGeyser`, `HotBoardOverlay`, `CasiCanto`) | Ya existen y funcionan con datos reales; portarlos a canvas es retrabajo sin beneficio |
| Personalidades | 3 (Metódico, Suertudo, Hiperactivo) | **6 naturalezas reales**: Metódico, Suertudo, Hiperactivo, Glotón, Tímido, Sabio | Definidas en `backend/app/models/axolotito.py` y `wiki/conceptos/04-naturalezas-y-personalidad.md` |
| Datos de tensión | Inventaba "cartas faltantes" | Usa `tension_level` (low/medium/high/critical) y `player_states_json` que **el backend ya calcula** en `ActiveGameState` | `backend/app/models/lobby_models.py`, `game_logic.py` |
| Cobertura | ~40% de las features del juego | **100%** — matriz de cobertura en §2 | El rediseño no puede dejar pantallas huérfanas con la estética vieja |
| Animación Axolotitos | No especificado | **Puppet modular tipo cut-out** (no frames) — spec completa en §6 | El ADN genera ~40,000+ combinaciones visuales; sprite-sheets por combinación es inviable |

---

## 1. Visión y Filosofía de Diseño

Transformar Axolotto de una interfaz de pestañas con estética "casino neón" a un **diorama interactivo de papel picado submarino**: un universo artesanal, cálido y tierno inspirado en los canales de Xochimilco, organizado en **3 macrozonas con identidad narrativa clara**:

* **El Santuario** — el hogar: donde los axolotitos nacen, viven y comparten partidas con amigos.
* **El Tianguis** — el comercio: todo lo que se compra, vende, forja y convierte.
* **La Pirámide** — el juego: gloria (rankings), suerte (gashapon) y competencia (salas de lotería) en un solo monumento.

### Principios rectores

1. **Diegético primero, HTML cuando importa**: la navegación y la ambientación viven en el mundo (canvas); las interfaces densas de datos (tienda, inventario, checkout) siguen siendo HTML re-tematizado como "pergaminos y papel amate". El canvas es *progressive enhancement* — el juego nunca depende de él para funcionar.
2. **Móvil manda**: encuadre vertical 9:16 como composición base, 60 FPS en Android gama media, presupuesto de memoria GPU estricto, modo calidad reducida automático.
3. **El papel es el lenguaje**: todo se mueve como papel — piezas rígidas que pivotan (cut-out), rebotes elásticos de cartón, transiciones de cortina, confeti de papel picado. Nada de motion blur ni físicas realistas.
4. **No romper nada**: cada flujo transaccional existente (compras, escrow, settlement, P2P) conserva su lógica; solo cambia la piel y el contexto espacial.

### Vibe shift estético

| Elemento | Actual (Neón) | Nuevo (Papel Picado) |
| :--- | :--- | :--- |
| Paleta | Azul oscuro `#060610`, violeta, cian eléctrico | **Atardecer en el cenote**: agua turquesa profunda (no negra), rosa bugambilia (conservar `#E4007C` — ya es rosa mexicano), cempasúchil `#F59E0B`, terracota, verde hoja |
| Materiales | Vidrio, metal, hologramas | Papel de china calado, cartón corrugado, madera de trajinera, piedra volcánica |
| Iluminación | Bloom de neón | Velas y faroles de papel cálidos, bioluminiscencia suave de lotos, rayos de luz acuática (god rays como tiras de papel celofán) |
| Paneles HTML | Cards oscuras con bordes glow | Pergaminos de amate con bordes troquelados, sombras de papel apilado (2-3px offset duro, no blur) |
| Tono | Casino Web3 frío | Feria artesanal acogedora, "hecho con amor" |

> **Decisión de diseño — fondo oscuro cálido, no claro**: se mantiene base oscura (agua profunda al atardecer) en lugar de fondo claro. Razones: (a) re-tematizar los ~40 componentes HTML a tema claro es un proyecto aparte, (b) OLED móvil ahorra batería, (c) las luces cálidas de papel destacan más sobre agua profunda. El "anti-casino" se logra con calidez y textura, no con brillo.

**Tokens**: extender `frontend/app/globals.css` con la nueva paleta (`--papel-bugambilia`, `--papel-cempasuchil`, `--papel-turquesa`, `--papel-amate`, `--agua-profunda`, `--agua-superficie`) y migrar componentes HTML por fases usando los tokens — nunca colores hardcodeados nuevos.

### Audio y micro-interacciones

* Tap en cualquier elemento del mundo → rebote elástico de cartón (scale 1 → 1.08 → 0.97 → 1, ~250ms) + sonido de papel.
* Faroles y tiras de papel ondulan con corrientes (sine waves desfasadas).
* Audio: jarana suave, burbujas, papel doblándose. Reusar `useAudioTension` y `TensionEffects` existentes; añadir capa ambiental por macrozona (Santuario: arrullo acuático / Tianguis: bullicio de feria / Pirámide: percusión ceremonial que se intensifica con `tension_level`).
* Respetar `prefers-reduced-motion` y el toggle de sonido de `SettingsModal`.

---

## 2. Matriz de Cobertura — Todo el flujo actual mapeado al mundo

Cada feature existente recibe un "hogar" diegético. **HTML** = sigue siendo overlay HTML re-tematizado; **Canvas** = se renderiza en el diorama; **Híbrido** = punto de entrada en canvas, interacción en HTML.

> **Compatibilidad**: los `TabId` existentes (`santuario`, `tienda`, `jugar`, `rankings`, `gashapon`...) NO cambian — siguen siendo las vistas HTML. Lo que cambia es el mapeo zona→tab: ahora `jugar`, `rankings` y `gashapon` son **subzonas de la macrozona Pirámide**.

### Macrozona 1 — El Santuario (tab `santuario`) 🪺

El hogar de los axolotitos y el espacio social del jugador. Chinampa vertical de 3 niveles.

| Feature existente | Archivo | Tratamiento |
| :--- | :--- | :--- |
| Webitos e incubación (progreso, acelerar, eclosionar, cuidados: acariciar/cantar/alimentar con cooldowns) | `EggSheet`, `HatchSheet`, `incubation.py` | **Híbrido — Nivel superior (Los Nidos)**: nidos de paja con huevos y cronómetro de papel; tap → sheet HTML. 🌟 **Al eclosionar, el nido se transforma en camita** con animación de papel que se repliega: el mismo slot es el hogar permanente del axolotito, con su nombre tallado en madera. La cuna del huevo y la cama del adulto son el mismo objeto narrativo |
| Slots de cueva + Axolotitos (energía, estados idle/sleeping/playing) | `Santuario.tsx`, `AxoSheet` | **Canvas — Niveles superior y central**: axolotitos-títere deambulan por la sala de estar, duermen en su camita con burbujas Zzz, juegan entre ellos |
| Imprinting / padrino | `ActImprinting`, `WebitoIncubation` | **Híbrido**: el padrino se sienta junto al nido del huevo en el diorama |
| Decoración de cuevas | `CuevaDecorPanel` (hoy con datos mock) | **Canvas** + ⚠️ **backend gap**: crear endpoint de persistencia (hoy `TODO: persist to backend` en `play/page.tsx`) |
| Expansión de cueva (excavación) | `CaveExpansion`, `cave_expansion.py` | **Canvas**: nivel/nido nuevo de chinampa aparece con animación de tierra/papel |
| **Mesa de Lotería del Santuario** — partidas con amigos | `HostingSetupModal`, salas `player_hosted` con `visibility: friends/private` (`lobby_models.py`) | **Híbrido — Nivel central** 🌟 *mejora clave*: la mesa central NO es solo decorativa — es el punto funcional para **hostear y unirse a partidas con amigos**. Tap en la mesa → `HostingSetupModal` (crear sala privada/de amigos) o unirse a la sala activa de un amigo. Las salas competitivas oficiales viven en la Pirámide; las casuales/sociales nacen aquí. Refuerza la identidad: *Santuario = jugar con los tuyos, Pirámide = competir* |
| Staking / claim de rentas de tablas | `fetchStakingStatus`, `claimAllStaking` | **Híbrido**: cofre de madera en la base del nido con badge de monto |
| **Embarcadero de Visitas** (amigos: like, visitar, solicitudes, discover, **referidos**, block) | `social/AmigosPage.tsx` (4 sub-tabs) | **Híbrido — Nivel inferior**: amigos llegan en trajineritas a la orilla con burbujas ❤️/👁/🎲 (like / visitar / **invitar a la mesa**); canasta de mimbre abre el pergamino HTML con los 4 sub-tabs completos (solicitudes, discover y referidos NO se pierden) |
| Vista de cueva de amigo | `FriendCaveView` | **Canvas**: misma escena de Santuario renderizada con datos del amigo, marco de "postal" |

### Macrozona 2 — El Tianguis (tab `tienda`) 🏪

Todo lo que hoy tiene el Tianguis, sin cambios de alcance.

| Feature existente | Archivo | Tratamiento |
| :--- | :--- | :--- |
| Sobrecitos (tiers, unboxing) | `store/OfficialTab.tsx`, `UnboxingModal` | **Híbrido**: puesto de bambú con manteles; tap → drawer HTML. Unboxing se mantiene HTML (ya tiene animación buena) |
| Webitos en venta (**Nido de Adopción**) | `OfficialTab` (webitosDrawer) | **Híbrido**: puesto de paja con Axolotito sabio NPC |
| **Banco** FRJ↔AXF (conversión) | `openBanco` flow | **Híbrido**: fuente del cenote (el stall `fountain` ya existe en `onStallClick`) |
| Crypto Checkout / MoonPay / fiat | `CryptoCheckout.tsx`, `useMoonPayWidget` | **HTML** puro (requisito de compliance del widget) — accesible desde el banco |
| Forja / Card Melter | `CardMelter.tsx` | **Híbrido**: Cenote Místico — caldero bioluminiscente; tap → CardMelter HTML re-tematizado |
| Mercado P2P (venta/renta, filtros, escrow) | `MarketP2P.tsx` | **Híbrido**: Trajineras P2P amarradas al muelle con listados flotantes; tap → MarketP2P HTML |
| Slots de cueva en venta | `OfficialTab` | Se integra al puesto de sobrecitos |

### Macrozona 3 — La Pirámide (tabs `jugar` + `rankings` + `gashapon`) 🗿

**El hub de toda la mecánica de juego en una sola vista.** Un monumento de piedra volcánica y papel dorado emergiendo del cenote. Tres subzonas dentro de la misma escena, conectadas por **paneos de cámara** (sin cortina — la continuidad espacial vende la tridimensionalidad):

```
                    ☁ superficie / luz lunar ☁
                ┌────────────────────────────────┐
                │        LA PIRÁMIDE             │
                │   (encuadre general al llegar) │
                │                                │
   [Cámara de   │      ▲▲▲ escalinata ▲▲▲       │  [Cenote de
    la Suerte]◄─┤     EXPLANADA DE RANKINGS      ├─►  las Salas]
   (gashapon,   │   estelas + podio de títeres   │  (lotería, al
   ala lateral) │        (la entrada)            │   fondo/interior)
                └────────────────────────────────┘
```

* **Encuadre de llegada**: vista general de la Pirámide — se leen las 3 subzonas de un vistazo. Hotspots con letreros de madera + el sub-dock contextual (§3.2) permiten saltar.
* 🌟 **Narrativa de paneo**: ir a las Salas = la cámara se *sumerge* hacia el interior del cenote (cuanto más compites, más profundo); ir a Rankings = la cámara *asciende* hacia la cima (la gloria está arriba); el gashapon queda en el ala lateral festiva (la suerte es un desvío del camino). El movimiento de cámara refuerza la metáfora sin costo de carga.

#### Subzona 3a — Explanada de Rankings (tab `rankings`, la entrada)
| Feature existente | Archivo | Tratamiento |
| :--- | :--- | :--- |
| 3 sub-tabs: Axolotitos / Boards / Forjadas + renta desde ranking | `Rankings.tsx` | **Híbrido**: estelas de piedra grabadas a la entrada; top 3 = axolotitos-títere reales en el podio de la escalinata (cargados de su ADN); lista completa en pergamino HTML |
| Badges VIP en rankings | `VipChip` | Aureolas de papel dorado/plata/cobre sobre los títeres del podio |

#### Subzona 3b — Cámara de la Suerte (tab `gashapon`, ala lateral)
| Feature existente | Archivo | Tratamiento |
| :--- | :--- | :--- |
| 3 máquinas (Bronce/Plata/Oro) con karma/pity, probabilidades | `Gashapon.tsx`, `MachineCard` | **Híbrido**: 3 gashapones de cartón troquelado y latón empotrados en la piedra; medidor de karma = termómetro de papel que se enciende ("KARMA HOT") |
| RevealSequence (caída, giro, reveal, LegendaryOverlay) | `RevealSequence`, `Particles` | **Canvas**: portar la secuencia al diorama — la cápsula cae DE la máquina física. Partículas legendarias = confeti de papel picado |
| **Recompensa Lunar** (6 lunas × 7 días, día 7 cápsula) | `DailyClaim.tsx`, `rewardsService` | **Híbrido** + 🌟 **idea nueva**: la fase lunar actual del jugador se refleja en el CIELO del agua de TODO el mundo (luz lunar que atraviesa la superficie). Claim = sheet HTML existente |

#### Subzona 3c — Cenote de las Salas (tab `jugar`, el fondo/interior)
| Feature existente | Archivo | Tratamiento |
| :--- | :--- | :--- |
| Wizard completo: ModeSelect → AxoSelect → BoardSelect → Budget → SalaSelect | `PlayMode.tsx`, `components/screens/*` | **HTML** re-tematizado como secuencia de "boletos de feria"; el diorama de fondo muestra las pozas |
| Salas oficiales (Charco de Novatos / Fosa del Campeón) + player-hosted públicas | `SalaSelectScreen`, `MultiplayerLobby` | **Híbrido**: dos pozas visibles a distinta profundidad (charco somero cálido arriba, fosa abisal abajo — la cámara baja al elegir Champion); salas hosted públicas como trajineras con farolito. *Las salas de amigos/privadas se hostean desde la mesa del Santuario (§Macrozona 1), pero también son visibles aquí* |
| Mesa de competencia en vivo (espectador/AFK) | `CenoteRoom`, `CircularTable`, `TableSeat` | **Re-skin DOM + nuevas mecánicas** — ver §5 |
| Juego manual (LoteriaBoard 4×4, gritón, historial, tensión) | `useManualGame`, `LoteriaBoard`, `GritonBanner`, `CalledCardsHistory`, `TensionEffects` | **HTML re-skin**: tabla como cartón de lotería real (papel con textura), fichas = frijolitos |
| Modo CPU/AFK (escrow, recall, reinscripción) | `CpuGameWrapper`, `useCpuGame` | **Híbrido**: tu axolotito visible jugando en la mesa del diorama |
| SettlingScreen / corte de caja (loyalty, match history) | `SettlingScreen` | **HTML** re-tematizado: recibo de papel impreso que "sale" de una caja registradora antigua |

### Transversales (visibles en todas las zonas)
| Feature | Archivo | Tratamiento |
| :--- | :--- | :--- |
| HUD: balances AXF/FRJ, floating earnings, VipChip | `play/page.tsx` header | **HTML** fijo, re-skin a marco de papel; floaters de monedas se mantienen |
| Ticker global de cápsulas | `play/page.tsx` | **HTML**: banderín de papel picado que cruza la parte superior |
| MochilaFloating (cartas/tablas/items, BoardEditor, equip, renta) | `MochilaFloating`, `Inventory.tsx`, `BoardEditor.tsx` | **HTML**: botón = morralito tejido flotante; el inventario completo (3 tabs + editor) se re-tematiza como códice desplegable |
| VIP Modal (tiers, compra, dashboard) | `VipModal.tsx` | **HTML** re-skin; los marcos vip-frame-* existentes se adaptan a marcos de papel metálico |
| Settings (sonido, PWA, logout) | `SettingsModal.tsx` | **HTML** + nuevo toggle "Calidad gráfica: Auto/Alta/Ligera" |
| Onboarding: WebitoIntro → Tutorial 11 actos → PostTutorialBranch | `TutorialFlow.tsx`, `onboarding/*` | **Re-skin progresivo**: el tutorial transcurre EN el mundo (el Webito te guía por las 3 macrozonas en los actos de world-intro — recorrido natural: naces en el Santuario, conoces el Tianguis, terminas frente a la Pirámide). Mantener flujo y actos intactos; cambiar fondos y assets |
| Landing + corcholatas | `app/page.tsx`, `CodeEntryPanel` | **Fase final**: hero de la landing muestra el diorama del Tianguis renderizado (screenshot o canvas ligero) |
| Eventos blockchain en vivo | `useBlockchainEvents` | Sin cambios de lógica; los eventos disparan reacciones en el mundo (ej: compra → humo de papel en el puesto) |

---

## 3. Arquitectura Técnica

### 3.1 Stack elegido (y por qué no Three.js)

| Capa | Elección | Justificación |
| :--- | :--- | :--- |
| Render | **PixiJS v8** (WebGPU + fallback WebGL2) | 2.5D por capas = caso ideal de sprites; ~150KB gzip vs ~650KB de three+R3F+drei; batching automático; soporte webp/atlas nativo |
| Tweens | **GSAP** (núcleo, sin plugins de pago) | Curvas elásticas para rebote de papel y paneos de cámara; gratis desde 2024 |
| Integración React | **Imperativa** vía `GameCanvasHandle` existente — NO @pixi/react | El contrato ya está definido en `components/world/GameCanvas.tsx` (`setAxolotitos`, `navigateToZone`, `onZoneClick`, `onCaveClick`, `onStallClick`...). Evita reconciliación React en el game loop |
| Estado puente | `WorldBridge` — mini event-emitter propio (`components/world/WorldBridge.ts`) | React → mundo: props vía handle. Mundo → React: callbacks ya definidos. No se necesita Zustand |
| Assets | Texture atlases `.webp` + JSON spritesheet (≤2048×2048 por atlas) | 1 atlas compartido de axolotito-partes + atlases por macrozona (la Pirámide divide el suyo por subzona para carga perezosa) |
| Efecto agua | Shader de desplazamiento ligero (DisplacementFilter de Pixi con noise texture) **solo en tier alto** | Un filtro fullscreen es lo más caro en móvil; degradable |

**Regla**: el canvas vive detrás del HTML (`z-0`), exactamente como ya está montado en `play/page.tsx`. Se activa cambiando `visible={false}` → `visible` cuando cada fase esté lista (feature flag `NEXT_PUBLIC_PAPER_WORLD=1`).

### 3.2 Navegación: 3 macrozonas + subzonas con paneo

**Dos mecánicas de transición, según la distancia narrativa:**

1. **Entre macrozonas** (Santuario ↔ Tianguis ↔ Pirámide): **Cortina de Papel** (~600ms) — tiras de papel picado caen y cubren la pantalla (300ms, overlay CSS para que funcione aunque el canvas cargue), `destroy()` + `Assets.unload()` de la escena saliente, `Assets.load()` de la entrante (con precarga especulativa de la vecina más probable), cortina se abre (300ms).
2. **Entre subzonas de la Pirámide** (Explanada ↔ Cámara de la Suerte ↔ Cenote de las Salas): **paneo de cámara GSAP** (~700ms, ease-out elástico suave) dentro de la misma escena montada. Sin carga, sin cortina — continuidad espacial total. Las capas de la subzona destino se cargan perezosamente la primera vez (placeholder de siluetas de papel mientras llega el atlas).

**ZoneDock rediseñado** (`frontend/components/play/ZoneDock.tsx` + `ZONE_TABS` en `play/page.tsx`):

```
        [ 🪺 Santuario ]  [ 🏪 Tianguis ]  [ 🗿 Pirámide ]
                                            └─ al estar activa, despliega sub-pills:
                                               [🏆 Rankings] [🎲 Salas] [🎰 Cápsulas]
```

* Dock principal de **3 botones** (botón Pirámide = FAB central elevado, es el corazón del juego).
* Con la Pirámide activa, un **sub-dock contextual** (3 pills que emergen como banderines) selecciona subzona → cambia `tabActiva` + paneo de cámara.
* Los `TabId` HTML no cambian; el mapeo `zoneToTab` de `play/page.tsx` se actualiza: `nido→santuario`, `tianguis→tienda`, `piramide.rankings→rankings`, `piramide.salas→jugar`, `piramide.capsulas→gashapon`. Deep-links y redirects legacy intactos.
* El punto rojo de recompensa lunar (hoy en el botón gashapon) vive en el botón Pirámide y se repite en la pill de Cápsulas.

### 3.3 Parallax y profundidad

* 4-6 capas por escena: fondo de agua → rayos de luz → plano lejano → plano medio (interactivo) → primer plano decorativo → partículas (burbujas/motas).
* La Pirámide es una escena ancha (~3 pantallas lógicas): las capas tienen anchos distintos para que el paneo entre subzonas produzca parallax horizontal real — el momento "wow" de profundidad.
* Parallax fino reacciona a: drag suave del usuario (±20px) y giroscopio en móvil (`deviceorientation`, con permiso iOS gestionado y fallback silencioso).

### 3.4 Responsive

* Cámara con `fit: cover` vertical: en 9:16 se ve el encuadre íntimo; en 16:9 (desktop) se revelan los laterales decorativos. En la Pirámide, el encuadre 16:9 puede mostrar dos subzonas a la vez — los hotspots siguen funcionando.
* DPR cap a 2. Resize con debounce. Safe-areas iOS (notch) ya consideradas por el HUD HTML.

---

## 4. Anatomía del mundo (resumen visual)

```
        [ HUD superior HTML: balances, VIP, lunar ]
┌──────────────────────────────────────────────────┐
│   ~ superficie del agua + luz de la LUNA actual ~ │   ← fase lunar real del DailyClaim
│                                                  │
│   MACROZONA (diorama Pixi, 4-6 capas parallax)   │
│   elementos interactivos con rebote de cartón     │
│                                                  │
│   [ contenido HTML de la tab actual, overlay ]    │
└──────────────────────────────────────────────────┘
   [ Dock: 🪺 Santuario · 🗿 Pirámide · 🏪 Tianguis ]
            (Pirámide despliega 🏆 🎲 🎰)
```

1. **El Santuario**: chinampa vertical 3 niveles — Nidos/camitas arriba (cada nido se vuelve la cama del axolotito que nació en él), sala de estar con la **Mesa de partidas con amigos** al centro, embarcadero social abajo.
2. **El Tianguis**: mercado flotante — puesto de sobrecitos, nido de adopción, fuente-banco, caldero-forja, trajineras P2P.
3. **La Pirámide**: explanada de rankings en la entrada (podio con títeres reales), Cámara de la Suerte en el ala lateral (gashapones), Cenote de las Salas al fondo/interior (pozas oficiales a distinta profundidad + trajineras hosted). Cámara: asciende a la gloria, se sumerge a la competencia, se desvía a la suerte.

---

## 5. Mesa de Competencia (Espectador / AFK) — datos reales

**Base**: extender los componentes DOM existentes (`CenoteRoom`, `CircularTable`, `TableSeat`, `GritonCharacter`, `PersonalityReactions`, `VictoryGeyser`, `HotBoardOverlay`, `CasiCanto`) con re-skin de papel. No portar a canvas en esta tarea. La misma mesa sirve para salas oficiales (Pirámide) y salas de amigos (Santuario) — solo cambia el fondo del diorama.

**Fuentes de datos (ya existen)**:
* `GET /multiplayer/game-state/{axolotito_id}` (polling 2s modo auto) y WebSocket `/ws/game/{room_id}/{user_id}` (modo manual) — `backend/app/services/ws_manager.py`.
* `ActiveGameState`: `cards_drawn_json`, `current_card_id`, `player_states_json` (marked/missed por board), `tension_level` (low/medium/high/critical — **ya calculado por el backend**), `turns_played`.
* Bots: boards del pool NPC (`is_npc_pool`, `npc_service.py`) → se renderizan como **Robo-Axolotes** de latón y cuerda con engranajes de cartón.

**Escalado dinámico de tablillas** (mini-tabla sobre cada jugador):
* Cálculo en cliente: `cartasFaltantes = min` sobre todos los patrones activos de la sala (`win_patterns` de `room_config`: líneas, cuadritos, pocito, esquinas, cruz, L, Z — definidos en `game_logic.py`) usando `marked_indices`.
* Lejos (>8 faltantes): escala 0.6, opacidad 0.5 · Cerca (3-8): escala 1.0 · **Match point (1-2)**: escala 1.4, borde de papel dorado pulsante + chispas de confeti + audio `CasiCanto` (ya existe).
* `tension_level` global controla: velocidad de caustics del fondo, capa musical, y nerviosismo del `GritonCharacter`.

**Reacciones por naturaleza** (extender `PersonalityReactions` de 3 a 6):

| Naturaleza | Al marcar carta | Al perder | Al ganar |
| :--- | :--- | :--- | :--- |
| Metódico | Asiente, mira fijo su tabla | Cruza brazos, arruga su papel de estrategia | Reverencia precisa + confeti ordenado |
| Suertudo | Brinquito + confeti | Se rasca la cabeza desconcertado | Baile de la suerte girando |
| Hiperactivo | Vibra + burbujas rápidas | Berrinche con burbujas de enojo | Saltos caóticos por toda la mesa |
| Glotón | Mordisquea un frijolito | Come por estrés (bolsa de papel) | Banquete celebratorio |
| Tímido | Marca escondido tras su tabla | Se encoge y se tapa con la tabla | Celebración tímida que crece a euforia |
| Sabio | Cierra los ojos y asiente lento | Acaricia su barba de papel, sereno | Levita en pose zen con aureola |

---

## 6. Plan de Animación de los Axolotitos: **Puppets (cut-out), no frames**

### 6.1 Decisión y justificación

**Títere modular de recorte (cut-out puppet) animado por transformaciones**, NO sprite-sheets de frames:

1. **El ADN lo exige**: `axolotito.py` codifica 5 `skin_color` × 5 `gill_type` × 5 `eye_type` × 5 `mouth_type` × 4 `tail_type` × 4 `forehead_type` × 4 `limb_type` + 3 slots de accesorios equipados = **decenas de miles de combinaciones**. Frames pre-renderizados por combinación es combinatoriamente imposible; un puppet compone las piezas en runtime.
2. **Es temáticamente perfecto**: el papel picado real se anima como teatro de sombras/títeres de papel con broches — piezas rígidas que pivotan. La limitación técnica ES el estilo artístico.
3. **Peso**: 1 atlas de partes (~30-40 piezas webp) sirve para TODOS los axolotitos del juego vs cientos de sheets.
4. **Frames solo para FX**: confeti, splash, polvo de eclosión — vía sistema de partículas de Pixi o mini-sheets de 6-8 frames.

### 6.2 Rig (jerarquía de piezas)

```
AxolotitoPuppet (Container)
├─ tail        (pivot en base — vaivén sinusoidal constante, +amplitud al nadar)
├─ body        (squash & stretch: scaleY 0.95↔1.05 en loop de respiración)
│   ├─ limb_back_L / limb_back_R     (remo sutil)
│   ├─ accessory_body                (slot equipped_body_item_id)
│   └─ head    (pivot en cuello — tilt ±8°)
│       ├─ gills_L / gills_R  (3 piezas c/u, ondulación desfasada — el "alma" del axolote)
│       ├─ eyes               (blink por swap de textura: open/closed; variante por eye_type)
│       ├─ mouth              (swap: neutral/feliz/sorpresa/triste)
│       ├─ forehead           (gema/halo/rayas según forehead_type)
│       └─ accessory_head / accessory_eyes  (slots equipados)
└─ shadow      (elipse suave, escala con la altura del bob)
```

* **Ensamblado**: `PuppetFactory.fromDna(axo)` lee los campos visuales del backend (ya llegan en el sync de `/auth/sync` → `datosBanco.axolotitos`) y selecciona texturas del atlas `axolotito-parts.webp`. Tinte (`tint`) ajusta variaciones de `skin_color`.
* **Producción de arte**: cada parte se dibuja UNA vez por variante en estilo papel recortado (borde blanco de papel + sombra dura interior). Total estimado: ~120 piezas únicas → 1-2 atlases de 2048px.

### 6.3 Animación procedural (sin esqueleto externo)

No usar Spine/DragonBones (herramienta extra, runtime extra, licencias). Las animaciones son **procedurales por composición de osciladores + tweens GSAP** sobre los pivotes del rig:

* **Idle**: respiración (scaleY), bob vertical (sine 2.5s), branquias ondulando (sine 1.8s desfasado por pieza), blink aleatorio cada 3-7s.
* **Nadar/caminar**: bob más rápido + tilt de cuerpo en dirección + cola amplia + estela de burbujas.
* **Dormir**: acostado en su camita (el nido transformado, §2), respiración lenta, burbujas Zzz (partículas), branquias caídas.
* **Marcar carta**: head tilt rápido hacia la tabla + brazo estampa la ficha + squash de impacto.
* **Emociones** (tabla §5): cada una es una secuencia GSAP de 1-2s sobre los mismos pivotes + swap de boca/ojos + partículas.
* **Estados** ya existen en datos: `status` del backend (`idle|playing|playing_manual|sleeping|waiting_settlement`) y `state` en `AxolotitoData` (`idle|walking|sleeping|playing`) → máquina de estados `PuppetStateMachine` con transiciones suaves (cross-fade de 200ms entre loops).

### 6.4 Niveles de detalle (LOD)

| Contexto | Detalle |
| :--- | :--- |
| Santuario (3-8 puppets) | Rig completo + comportamiento ambiente (deambular, dormir, jugar en la mesa) |
| Mesa de competencia (hasta ~10 asientos) | Rig completo pero solo loops idle/reacción; sin deambular |
| Podio de la Explanada (3) | Rig completo estático + idle |
| Listas/HTML (rankings, sheets) | Retrato estático generado del mismo rig (render a textura 1 vez, cacheado) — reemplaza gradualmente al `AxoAvatar` de emoji |
| Tier "Ligera" móvil | Osciladores reducidos a bob+branquias; sin partículas |

### 6.5 Robo-Axolotes (CPU)

Mismo rig con set de texturas alterno (latón, remaches, llave de cuerda en la espalda que gira). Animación idle: tic-tac mecánico (rotaciones discretas en pasos, no sinusoidales) — comunica "soy bot" sin texto.

---

## 7. Rendimiento Móvil — presupuesto y degradación

* **Presupuesto por macrozona**: ≤ 2 atlases residentes (≤16MB VRAM; la Pirámide admite 3 con carga perezosa por subzona, descargando la subzona no visitada más antigua si hay presión de memoria), ≤ 150 sprites activos, ≤ 1 filtro fullscreen (solo tier alto), 0 filtros por-sprite.
* **Quality tiers** (auto-detect: `deviceMemory`, `hardwareConcurrency`, primer frame-time medido; override manual en Settings):
  * **Alta**: parallax 6 capas, shader de agua, partículas plenas, 60 FPS.
  * **Media**: 4 capas, sin shader (las "ondas" se simulan moviendo la capa de rayos de luz), partículas al 50%.
  * **Ligera**: 2 capas estáticas + puppets simplificados, 30 FPS cap, ticker reducido; el paneo de la Pirámide se mantiene (es solo translación de contenedores, barato).
* **Pausa total** del ticker cuando la tab no es visible (integrar con `useTabVisibility` / `RealtimeContext` existente) y cuando un modal HTML fullscreen cubre el canvas.
* `prefers-reduced-motion` → tier Ligera + sin parallax de giroscopio + paneos de cámara instantáneos.
* Unload agresivo entre macrozonas (`Assets.unload` + `texture.destroy`), verificado con snapshot de VRAM en Chrome DevTools.
* Métrica de salida: 60 FPS estables en Android gama media (ej. Moto G-series) en Santuario con 8 puppets y en el paneo completo de la Pirámide.

---

## 8. Fases de Desarrollo

### Fase 0 — Cimientos (sin impacto visual)
- [ ] Instalar `pixi.js@^8` y `gsap`. NO instalar three/R3F/zustand.
- [ ] Pipeline de assets: script de empaquetado de atlas (TexturePacker free CLI o `@assetpack/core`), convención `public/world/atlas/<zona>[.<subzona>].{webp,json}`.
- [ ] Implementar `GameCanvas` real detrás de `NEXT_PUBLIC_PAPER_WORLD` (respetando el `GameCanvasHandle` existente), `WorldBridge`, detector de quality tier, cortina de papel CSS.
- [ ] Sistema de cámara: encuadres por subzona + paneo GSAP + fit responsive 9:16/16:9.
- [ ] Definir tokens de paleta papel en `globals.css`.
- [ ] `ZoneDock` v2: 3 botones macro + sub-dock contextual de la Pirámide (mapeo `TabId` legacy intacto).

### Fase 1 — El Santuario + Puppet System (máximo valor emocional primero)
- [ ] `PuppetFactory.fromDna` + atlas de partes + `PuppetStateMachine` (idle/walk/sleep/blink).
- [ ] Diorama del Santuario (3 niveles, parallax, nidos con cronómetro, cofre de staking).
- [ ] **Transformación nido→camita** al eclosionar (animación de papel + nombre tallado).
- [ ] Mesa de partidas con amigos: hotspot → `HostingSetupModal` / unirse a sala de amigo.
- [ ] Decoraciones reales: reemplazar `getMockDecorations()`; ⚠️ requiere endpoint backend de persistencia de decoraciones (sub-tarea backend).
- [ ] Embarcadero social: trajineritas de amigos + burbujas like/visitar/invitar; canasta → AmigosPage HTML (4 sub-tabs intactos).
- [ ] Activar mundo en Santuario para usuarios con flag.

### Fase 2 — Tianguis, esqueleto de la Pirámide y transiciones
- [ ] Diorama del Tianguis (5 puestos interactivos cableados a `onStallClick`).
- [ ] Escena de la Pirámide: encuadre general + Explanada de Rankings (podio con puppets del top-3) + hotspots y paneos a las otras dos subzonas (con arte placeholder).
- [ ] Sistema completo de transición: cortina entre macrozonas + carga perezosa por subzona + precarga especulativa.
- [ ] Re-skin HTML por tokens: Store, wizard de PlayMode ("boletos de feria"), SettlingScreen (recibo), Inventory (códice), VipModal.

### Fase 3 — Cenote de las Salas y mesa de competencia
- [ ] Subzona Salas completa: pozas a distinta profundidad (cámara se sumerge al elegir Champion), trajineras hosted.
- [ ] Re-skin papel de `CenoteRoom`/`CircularTable`/`TableSeat`/`GritonCharacter`.
- [ ] Puppets sentados a la mesa desde ADN real; Robo-Axolotes para boards NPC.
- [ ] Escalado dinámico de tablillas (cálculo de `cartasFaltantes` vs `win_patterns` de la sala) + match-point dorado + `CasiCanto`.
- [ ] `PersonalityReactions` extendido a 6 naturalezas (marcar/ganar/perder) + `tension_level` controlando ambiente global.

### Fase 4 — Cámara de la Suerte, cielo lunar y tutorial
- [ ] Subzona Cápsulas: gashapones físicos empotrados, termómetro de karma, RevealSequence portada al diorama con confeti de papel.
- [ ] Cielo lunar global: la fase del `DailyClaim` tiñe la luz superficial de las 3 macrozonas.
- [ ] Tutorial re-skin: el Webito guía por las 3 macrozonas (naces en el Santuario → conoces el Tianguis → terminas frente a la Pirámide); flujo de 11 actos intacto.

### Fase 5 — Pulido, perf y rollout
- [ ] Shader de agua (solo tier Alta) + god rays.
- [ ] Auditoría de VRAM/FPS en 3 dispositivos reales (Android gama media, iPhone, desktop); ajustar tiers. Caso crítico: paneo completo de la Pirámide.
- [ ] `prefers-reduced-motion`, pausa por visibilidad, toggle de calidad en Settings.
- [ ] Retratos puppet en HTML (reemplazo de emoji `AxoAvatar`), landing con diorama, retirar flag.

---

## 9. Riesgos y dependencias

| Riesgo | Mitigación |
| :--- | :--- |
| Producción de arte (atlas de ~120 piezas + 3 escenas por capas, la Pirámide es ancha) es el camino crítico | Empezar Fase 1 con arte placeholder vectorial (formas planas con borde de papel); el rig no depende del arte final |
| La escena de la Pirámide (3 subzonas) puede exceder presupuesto de VRAM en gama baja | Carga perezosa por subzona + descarga de la subzona no visitada más antigua; en tier Ligera, las subzonas no visibles se reducen a siluetas |
| Persistencia de decoraciones no existe en backend | Sub-tarea backend pequeña (tabla + 2 endpoints) antes de Fase 1; mientras, localStorage |
| Filtros fullscreen matan móviles gama baja | Shader solo en tier Alta; degradación probada en Fase 0 |
| Doble fuente de verdad de navegación (dock HTML + letreros canvas + sub-dock) | Una sola ruta: todo converge en `setTabActiva` + `navigateToZone(zona, subzona?)`, cableado en `play/page.tsx` |
| Re-skin de ~40 componentes HTML es enorme | Por tokens CSS y por fases — nunca un big-bang; cada fase deja el juego consistente |
| iOS pide permiso para giroscopio | Parallax por drag como base; giroscopio es mejora opt-in |
| Confusión salas de amigos (Santuario) vs oficiales (Pirámide) | Las salas de amigos también se listan en el Cenote de las Salas; el Santuario es un acceso directo social, no un silo |
