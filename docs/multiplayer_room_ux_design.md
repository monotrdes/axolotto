# Game Design Document (GDD) & UX: Sala Multijugador 2.5D
**Mesa de Bingo Cenote & Visor de Tensión**
*Autor: Antigravity AI & Game Design Specialist × deepclaude*
*Fecha: 2026-06-07 | Actualizado: 2026-06-07*

---

## 0. Estado de Implementación

### ✅ Hecho (Commit `e4d34c0` — Core Técnico)
| Componente | Archivo |
|-----------|---------|
| WebSocket Manager (card cycle, Gritón, reconexión) | `backend/app/services/ws_manager.py` |
| WebSocket endpoint (`WS /api/v1/ws/game/{room_id}`) | `backend/app/api/v1/ws/game_ws.py` |
| GameScreen unificado (CPU/Auto/Manual, 544 líneas) | `frontend/components/screens/GameScreen.tsx` |
| Hooks de juego (useWebSocket, useCpuGame, useAutoGame, useManualGame) | `frontend/hooks/` |
| Componentes UI base (GritonBanner, OpponentStrip, TensionEffects, AxoAvatar) | `frontend/components/ui/` |
| Lógica de tensión (`check_tension_status`, `validate_win`) | `backend/app/services/game_logic.py` |
| Patrones de victoria expandidos (Pocito, Esquinas, Cruz, L, Z, Full Board) | `backend/app/services/game_logic.py` |
| FRJ-only hardening (`assert_multijugador_currency`, `onlyFRJ` modifier) | `backend/app/services/bank_service.py`, `contracts/src/GameController.sol` |
| Campo `nature` en modelo Axolotito | `backend/app/models/axolotito.py` |

### 🔨 En Progreso (Task `task-1780814924-32`)
| Fase | Descripción | Estado |
|------|------------|--------|
| FASE 1 | Entorno 2.5D — CenoteRoom, mesa circular, asientos radiales, CSS parallax | 🔨 Implementando |
| FASE 2 | Personalidad — personality-config, AxoAvatar con nature, ws_manager update | 🔨 Implementando |
| FASE 3 | Tablas Calientes — HotBoardOverlay, levitación+glow, RippleEffect | 🔨 Implementando |
| FASE 4 | Juice Final — VictoryGeyser, CasiCanto, GritonCharacter, useAudioTension | 📋 Planificado |

---

## 1. Visión General del Entorno 2.5D

El objetivo principal es transformar el multijugador de Axolotto de un simple script en segundo plano a una **experiencia visual premium, social y emocionante**, tanto para el juego manual como para el automático (espectador). 

Nos inspiramos en la calidez de las **salas de bingo tradicionales** y las combinamos con la estética mística de un **cenote subterráneo o una cantina subacuática**.

### Estructura Visual:
- **Perspectiva 2.5D (Capas de Profundidad + Parallax):** El escenario se divide en 3 capas con parallax que reaccionan al movimiento del mouse (o tilt del dispositivo en móvil):
  1. **Capa Profunda (Deep Layer):** Paredes rocosas del cenote, luz mística filtrándose desde la superficie, partículas flotantes. Factor parallax: 0.01.
  2. **Capa Media (Mid Layer):** Estalagmitas, algas flotantes que se mecen, bancos de pececitos neón que derivan horizontalmente. Factor parallax: 0.03.
  3. **Capa Frontal (Front Layer):** Burbujas ascendentes, destellos de partículas bioluminiscentes. Factor parallax: 0.06.

- **Plano Medio (Mesa de Juego):** Una gran mesa circular de piedra tallada con runas/patrones geométricos alrededor de la cual están sentados en semicírculo los **Axolotitos** (hasta 8 jugadores). Posicionamiento radial: cada asiento se calcula como `angle = (i/N) * 2π - π/2`.

- **Profundidad por Z-Index:** Los asientos en la mitad inferior (más cercanos al espectador) tienen mayor z-index. Los asientos superiores (más lejanos) son ligeramente más pequeños (scale 0.85-0.95).

- **Primer Plano (HUD del Jugador):** El tablero principal del usuario (en modo manual) o el panel de control del Axolotito (en modo automático) se superpone sobre la escena.

- **Nivel de Agua Dinámico:** Un overlay azul sutil cuya intensidad varía con el nivel de tensión general de la sala (`--water-depth` CSS custom property).

### Componentes Nuevos (FASE 1):
- `CenoteRoom.tsx` — Contenedor principal del escenario 2.5D
- `CenoteBackground.tsx` — Tres capas de fondo con parallax
- `CircularTable.tsx` — Mesa de piedra circular renderizada con CSS gradients
- `TableSeat.tsx` — Asientos radiales alrededor de la mesa

---

## 2. Axolotito Proxy (Representación en Modo Manual vs. Auto)

Un dilema clave de diseño es: *Si en el modo manual el jugador es quien marca su propia tabla en tiempo real, ¿qué hace su Axolotito en la mesa?*

### La Solución: El Axolotito como Avatar Proxy (Mascota Representante)
Tanto en modo automático como en manual, **el jugador envía a uno de sus Axolotitos como su representante físico (avatar) en la mesa**.

- **En Modo Automático (AFK Farming):** El Axolotito actúa de forma autónoma. Se le ve concentrado, mirando su tabla y marcando los frijoles sobre ella con sus manitas cuando se canta una carta.

- **En Modo Manual (Real-Time Play):** El jugador controla el marcado con sus taps en la pantalla, pero su Axolotito está sentado en la mesa y actúa como un **espejo de su desempeño**:
  - Si el jugador marca a tiempo, el Axolotito celebra.
  - Si al jugador se le "escapa" una carta (missed call), el Axolotito se duerme o se distrae.
  - Si el jugador hace tap en una carta falsa (error), el Axolotito se golpea la frente o pone cara de susto.
  - Este modelo preserva la utilidad de los NFT Axolotitos y sus stats de rareza en ambas modalidades.

---

## 3. Escala Dinámica de Tablas ("Tablas Calientes")

En una partida con múltiples jugadores y hasta 3 tablas por jugador, mostrar todos los tableros en pantalla al mismo tiempo saturaría la interfaz. 

### Regla de Visualización Inteligente y Tensión:
1. **Vista General (Reposo):** Los tableros de los rivales se muestran simplificados (en miniatura en frente de cada Axolotito o como un simple contador de marcas, ej: `12 / 16`).

2. **El Disparador de Tensión ("¡A una carta!"):** Cuando una tabla (sea del jugador, de un rival o de un bot) alcanza **14 o 15 aciertos de 16** (está a 1 o 2 cartas de cantar Lotería), la tabla se vuelve una **"Tabla Caliente"**.

3. **Escalado Dinámico:**
   - La tabla caliente **se desprende físicamente de la mesa y levita** (flota sobre la cabeza del Axolotito que la posee).
   - **Crece en tamaño** (un 150%) para destacar sobre el resto.
   - Se rodea de un **halo de color vibrante con animación pulsante**:
     - **Esmeralda** (`rgba(52,211,153,0.6)`) — Amenaza nivel 3 (75% de una línea)
     - **Índigo** (`rgba(99,102,241,0.7)`) — Amenaza nivel 4 (línea casi completa)
     - **Dorado** (`rgba(251,191,36,0.8)`) — 14+ marcas en el tablero (a 1-2 de cantar)
   - **Ondas en el Agua (Ripple Effect):** La tabla caliente emite ondas expansivas concéntricas que se propagan sobre la superficie de la mesa — como una gota cayendo en agua.
   - Gotas de agua "caen hacia arriba" desde la tabla levitante (inversión visual del efecto de gravedad bajo el agua).
   - Todos los espectadores y jugadores en la sala pueden ver instantáneamente quiénes son los competidores más peligrosos.

```
       [ TABLA CALIENTE (15/16) ]  <-- Levita, escala 150%, glow dorado + ondas en el agua
         💧  | | |  💧            <-- Gotitas subiendo
               (  O.O  )          <-- Axolotito reacciona emocionado
              /========= \
             /  [Tabla]   \       <-- Tablas normales (reposo) sobre la mesa de piedra
    ~~~~~~~~~~~~~~~~~~~~~~~~~~   <-- Ondas/ripples en el agua desde la tabla caliente
```

### Componentes Nuevos (FASE 3):
- `HotBoardOverlay.tsx` — Overlay de levitación + glow + gotas
- `RippleEffect.tsx` — Ondas expansivas concéntricas

---

## 4. Personalidades (Natures) y Animaciones de Reacción

Cada Axolotito reacciona de acuerdo a su personalidad (`nature`), aumentando el "jugo" (juice) visual y la retención del jugador. **Cada personalidad tiene un aura de partículas única** que la hace visualmente identificable a cualquier escala.

### Sistema de Auras por Personalidad:
| Personalidad | Aura | Color | Descripción Visual |
|-------------|------|-------|-------------------|
| **Hiperactivo** | ⚡ Chispas eléctricas | Ámbar/amarillo | Pequeños rayos que saltan alrededor del axo |
| **Tímido / Calmado** | 💧 Gotitas suaves | Azul claro | Gotitas que flotan y se esconden tímidamente |
| **Presumido / Orgulloso** | ✨ Destellos dorados | Dorado VIP | Brillos que rotan con actitud ostentosa |
| **Curioso** | 👁️ Ojitos flotantes | Verde menta | Ojos pequeños que examinan todo alrededor |

### Tabla de Reacciones por Personalidad:

| Trigger | Hiperactivo | Tímido/Calmado | Presumido/Orgulloso | Curioso |
|---------|------------|----------------|---------------------|---------|
| **Acierto (Hit)** | Da vueltas rápidas, branquias vibran con ⚡ destellos. Grita "¡Sí!" | Sonríe sutilmente y asiente lento. Susurra "bien..." | Se cruza de brazos, le caen lentes de sol flotantes 👑. Infla el pecho. | Se acerca mucho a la carta con ojos 👁️ gigantes. "¡Ajá!" |
| **Se le escapó (Miss)** | Gira en espiral mareado, nadando en círculos. "¡Nooo!" | Se esconde detrás de su tablero, asomando solo los ojitos. Silencio. | Pone los ojos en blanco y bosteza con desdén. "Uf, qué aburrido." | Se distrae mirando otra cosa, anota en su libreta. "Interesante..." |
| **A una carta (Near-Win)** | Tiembla de emoción en su asiento, agita brazos acelerados. "¡CASI CASI!" | Se sonroja y se esconde detrás del tablero, asomando solo los ojos. Respira rápido. | Mira de reojo a los rivales con superioridad, bosteza fingiendo desinterés. | Saca una lupa de agua 🔍 y examina el tablero concentrado. "Mmm..." |
| **Victoria (Win)** | Salto mortal fuera del agua + confeti acuático 🎆. "¡GANÉÉÉ!" | Aplauso suave y se cubre la cara con timidez. "Qué pena..." | Pose de victoria flotando de espaldas con destellos VIP ✨. "Obvio." | Examina el premio y flota alrededor de él. "Fascinante..." |
| **Derrota (Loss)** | Berrinche nadando boca abajo, tira frijolitos 💢. "¡GRRR!" | Suspira aliviado, encoge hombros. "Ni modo..." 💤 | Da la espalda a la mesa con desdén, brazos cruzados. "Estaba arreglado." | Observa la tabla ganadora y toma notas en libreta 📝. "La próxima vez..." |

### Componentes Nuevos (FASE 2):
- `data/personality-config.ts` — Datos estáticos del mapeo personalidad×trigger
- `PersonalityReactions.tsx` — Render de reacción con aura de partículas por personalidad

---

## 5. Diseño de Sonido y "Juice" de Tensión

Para lograr que el jugador sienta la adrenalina cuando le falte llenar una sola carta, se implementan los siguientes efectos sensoriales:

### 5.1 Latido de Corazón Visual (Heartbeat Effect)
Al estar a 1 carta de ganar, los bordes de la pantalla del jugador comienzan a pulsar con un degradado **dorado** (no rojo — el dorado es más premium y menos "peligro"). El latido acelera progresivamente:
- A 2 cartas: pulso cada 1.2s (suave)
- A 1 carta: pulso cada 0.6s (intenso, dorado brillante)
- Al cantar ¡Lotería!: destello blanco instantáneo
- Acompañado de vibración háptica ligera en dispositivos móviles.

### 5.2 "Casi-Canto" — Anticipación Colectiva
Cuando cualquier jugador está a 1 carta de ganar:
- Un susurro visual "¡CASI!" recorre la pantalla (texto dorado que se desvanece de izquierda a derecha)
- Todas las cabezas de los Axolotitos (en sus asientos) giran hacia el jugador near-win
- El tablero del near-winner emite un heartbeat dorado
- La música de fondo se modula — sube ligeramente el tempo

### 5.3 El Gritón como Personaje
En lugar de un simple banner, el Gritón es un **Axolotito anciano más grande** que preside la mesa:
- Tiene una burbuja de diálogo que emerge de su boca — la carta cantada aparece dentro
- Para cartas normales: la burbuja aparece suavemente, la carta se materializa dentro
- Para cartas críticas (cuando alguien está near-win): hace un lean-in dramático, la burbuja crece y tiembla, la carta surge con delay dramático
- Dice frases como: *"¡Y la que todos esperan... el A-XO-LO-TL!"* con ritmo pausado
- La carta sale con animación de "surgir del agua" (sube desde abajo)

### 5.4 Zoom de Clímax
La "cámara" 2.5D hace un zoom-in lento (CSS transform scale en el contenedor de la escena) hacia el Axolotito y tablero del jugador que está en puerta de ganar, oscureciendo sutilmente los bordes para centrar atención.

### 5.5 Géiser de Victoria
Cuando alguien gana, se desata un espectáculo:
- Un géiser de burbujas y luz emerge de la posición del axolotito ganador
- Partículas de confeti subacuático "llueven" sobre toda la mesa
- La tabla ganadora hace un flip 3D (rotateY 180deg) y muestra el patrón iluminado
- Los perdedores tienen animación de "salpicadura" (water splash) — fueron vencidos

### 5.6 Arquitectura de Audio (useAudioTension)
Se crea la interfaz `useAudioTension` hook que expone:
- `setTempo(speed: number)` — 1.0 normal, 1.3 tensión media, 1.6 tensión alta
- `playDrumroll()` — tambor de suspenso
- `playCardCall(n: number)` — sonido de carta cantada
- `playVictory()` / `playDefeat()` — stingers de resultado
- Los assets de audio reales se añadirán en follow-up; la arquitectura queda lista

### Componentes Nuevos (FASE 4):
- `GritonCharacter.tsx` — El Gritón como personaje con burbuja de diálogo
- `VictoryGeyser.tsx` — Géiser de burbujas/luz + confeti
- `CasiCanto.tsx` — Overlay de anticipación "¡CASI!"
- `hooks/useAudioTension.ts` — Hook de audio (interfaz, assets pendientes)

---

## 6. Hoja de Ruta de Implementación

### Task: `task-1780814924-32` | Rama: `feature/multiplayer-redesign` | Asignado: `deepclaude`

### FASE 1: Entorno 2.5D + Mesa Circular 🔨
**Objetivo**: Crear el escenario base del cenote.

| Componente | Archivo | Acción |
|-----------|---------|--------|
| CenoteRoom | `frontend/components/multiplayer/CenoteRoom.tsx` | NUEVO |
| CenoteBackground | `frontend/components/multiplayer/CenoteBackground.tsx` | NUEVO |
| CircularTable | `frontend/components/multiplayer/CircularTable.tsx` | NUEVO |
| TableSeat | `frontend/components/multiplayer/TableSeat.tsx` | NUEVO |
| Animaciones CSS | `frontend/app/globals.css` | Agregar @keyframes |

### FASE 2: Personalidad y Reacciones 🔨
**Objetivo**: Hacer que cada Axolotito cobre vida con reacciones únicas según su `nature`.

| Componente | Archivo | Acción |
|-----------|---------|--------|
| Personality Config | `frontend/data/personality-config.ts` | NUEVO |
| PersonalityReactions | `frontend/components/multiplayer/PersonalityReactions.tsx` | NUEVO |
| AxoAvatar | `frontend/components/ui/AxoAvatar.tsx` | MODIFICAR |
| PlayerState (nature) | `backend/app/services/ws_manager.py` | MODIFICAR |
| Animaciones CSS | `frontend/app/globals.css` | Agregar @keyframes |

### FASE 3: Tablas Calientes — Levitación, Glow y Ripple 🔨
**Objetivo**: Implementar el sistema visual de "Hot Boards" que genera tensión.

| Componente | Archivo | Acción |
|-----------|---------|--------|
| HotBoardOverlay | `frontend/components/multiplayer/HotBoardOverlay.tsx` | NUEVO |
| RippleEffect | `frontend/components/multiplayer/RippleEffect.tsx` | NUEVO |
| OpponentStrip | `frontend/components/ui/OpponentStrip.tsx` | MODIFICAR |
| TensionEffects | `frontend/components/ui/TensionEffects.tsx` | MODIFICAR |
| Animaciones CSS | `frontend/app/globals.css` | Agregar @keyframes |

### FASE 4: Juice Final — Géiser, Casi-Canto, Sonido 📋
**Objetivo**: Pulir la experiencia con toques premium.

| Componente | Archivo | Acción |
|-----------|---------|--------|
| VictoryGeyser | `frontend/components/multiplayer/VictoryGeyser.tsx` | NUEVO |
| CasiCanto | `frontend/components/multiplayer/CasiCanto.tsx` | NUEVO |
| GritonCharacter | `frontend/components/multiplayer/GritonCharacter.tsx` | NUEVO |
| useAudioTension | `frontend/hooks/useAudioTension.ts` | NUEVO |
| Animaciones CSS | `frontend/app/globals.css` | Agregar @keyframes |
| GameScreen | `frontend/components/screens/GameScreen.tsx` | MODIFICAR (integración total) |

### Requisitos de Verificación por Fase:
1. **F1**: Abrir GameScreen modo multiplayer → mesa circular renderiza, asientos radiales con 2-8 axos, parallax responde al mouse, burbujas ascienden
2. **F2**: Registrar axolotitos con distintas naturalezas → cada uno reacciona diferente al mismo trigger, auras de partículas visibles
3. **F3**: Tabla llega a 14+ marcas → levita 12px, escala 150%, glow del color correcto (esmeralda/índigo/dorado), ondas expansivas emanan de la tabla
4. **F4**: Alguien gana → géiser + confeti + flip 3D. Near-win → "¡CASI!" + heartbeat dorado + drumroll. Gritón personaje con burbuja de diálogo
5. **Regresión**: Modo CPU sigue funcionando sin cambios visuales (GameScreen detecta `mode="cpu"` y omite la escena 2.5D)
