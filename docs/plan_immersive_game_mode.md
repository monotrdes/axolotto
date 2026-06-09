# Plan: Modo Inmersivo de Partida (`immersive-game-mode`)

> **Status**: Planning  
> **Category**: `game`, `frontend`  
> **Priority**: Alta — mejora directa de UX en el core loop  
> **Taskboard**: `task-1780824472-38`

---

## 1. Visión General

Cuando un jugador entra en partida (vs CPU, multijugador auto, o PvP manual), toda la interfaz de navegación debe replegarse para eliminar distracciones. El jugador debe sentir que "está dentro del tablero". Solo los elementos esenciales del juego permanecen visibles.

### Objetivos

1. **Eliminar el HUB inferior** (ZoneDock) durante partida activa → menos distracción, más espacio visual para el tablero
2. **Header mínimo no interactivo** → solo muestra balances AXF/FRJ como contadores fantasma, sin permitsir navegación
3. **El tablero es el centro absoluto** → único elemento interactuable en PvP manual; en CPU/auto es solo display
4. **Acelerador táctil x2 en vs CPU** → como Reels de Instagram: mantener pulsado acelera la animación carta-por-carta
5. **Transiciones fluidas** → entrada/salida del modo inmersivo con animaciones que refuercen el enfoque

---

## 2. Filosofía de Diseño (Game Design)

### El concepto de "La Mesa de Lotería"

En la lotería mexicana real, cuando el gritón empieza a cantar cartas, todo lo demás desaparece. Los jugadores se inclinan sobre la mesa. El ruido de fondo se silencia. Solo existe la tabla, las cartas, y el frijolito listo para marcar.

**Eso es lo que queremos replicar digitalmente.**

### Principios

| Principio | Aplicación |
|-----------|-----------|
| **Foco total** | Todo lo que no es juego se esconde. Sin excepciones. |
| **Inmersión progresiva** | La UI no desaparece bruscamente — se desliza y desvanece como un telón |
| **Toque mínimo** | En CPU, cero interacción. En PvP manual, solo el tablero. |
| **Velocidad como recompensa** | El acelerador x2 da agencia al jugador incluso en modo espectador |
| **Salida clara pero sutil** | Un botón de salida discreto — visible solo al hacer hover o esperar |

---

## 3. Modos de Juego y Comportamiento

### 3.1 CPU (vs Bots) — `mode="cpu"`

| Estado | Header | ZoneDock | Ticker | Tablero | Acción |
|--------|--------|----------|--------|---------|--------|
| **Pre-juego** (wizard) | Normal | Visible | Visible | — | Setup normal |
| **Loading** | Inmersivo | Oculto | Oculto | — | Spinner |
| **Animando** | Inmersivo | Oculto | Oculto | Display (no interactivo) | **Hold para x2** |
| **Resultado** | Inmersivo | Oculto | Oculto | Display | Botones: Jugar Otra Vez / Cambiar |

**Acelerador x2:**
- El jugador mantiene pulsado cualquier lugar de la pantalla (excepto botones de resultado)
- Tras 400ms de hold sostenido → la velocidad de animación se duplica (600ms por carta en vez de 1200ms)
- Se muestra un badge flotante "⚡ x2" con animación de pulso
- Al soltar → vuelve a velocidad normal (1200ms)
- En desktop: también funciona manteniendo la barra espaciadora
- Opcional: doble tap rápido → bloquea x2 permanente hasta nuevo tap (toggle)

### 3.2 Multijugador Auto (Servidor) — `mode="auto"`

| Estado | Header | ZoneDock | Ticker | Tablero | Acción |
|--------|--------|----------|--------|---------|--------|
| **Pre-juego** (wizard) | Normal | Visible | Visible | — | Setup normal |
| **Jugando** (`PlayingScreen`) | Inmersivo | Oculto | Oculto | Display (no interactivo) | Botón "Llamar de Regreso" permanece |
| **Settlement** | Inmersivo | Oculto | Oculto | — | Pantalla de liquidación |

**Nota:** El botón "Llamar de Regreso" es parte del juego, no del HUB. Permanece visible.

### 3.3 PvP Manual (WebSocket) — `mode="manual"`

| Estado | Header | ZoneDock | Ticker | Tablero | Acción |
|--------|--------|----------|--------|---------|--------|
| **Pre-juego** (wizard) | Normal | Visible | Visible | — | Setup + sala |
| **Partida activa** | Inmersivo | Oculto | Oculto | **Interactivo** (tap en celdas) | Botones de juego visibles: Pista + ¡LOTERÍA! |
| **Resultado** | Inmersivo | Oculto | Oculto | Display | Overlay de resultado |

**Nota:** La barra de acción (Pista + ¡LOTERÍA!) es parte del juego, no del HUB. Permanece visible. El acelerador NO aplica — es tiempo real contra humanos.

---

## 4. Especificaciones Técnicas

### 4.1 Estados de `gameView` y Modo Inmersivo

```typescript
// En PlayMode — estos gameView activan modo inmersivo:
const IMMERSIVE_VIEWS: GameView[] = ['game', 'playing', 'settling'];

// El resto permanece con UI normal:
// 'axo-select', 'mode-select', 'board-select', 'budget', 'sala-select'
```

### 4.2 Comunicación PlayMode → Page

```typescript
// PlayMode recibe nueva prop:
onGameActiveChange?: (active: boolean) => void;

// En useEffect dentro de PlayMode:
useEffect(() => {
  const isActive = IMMERSIVE_VIEWS.includes(gameView);
  onGameActiveChange?.(isActive);
}, [gameView]);
```

### 4.3 Header Inmersivo

El header normal y el inmersivo coexisten como variantes condicionales en `play/page.tsx`:

```
Header Normal (isGameActive === false):
┌──────────────────────────────────────────────────────┐
│ 🦎 AXOLOTTO    [VIP] [💎 150 AXF] [🪙 42.5 FRJ] [📥] [🚪] │
└──────────────────────────────────────────────────────┘

Header Inmersivo (isGameActive === true):
┌──────────────────────────────────────────────────────┐
│ ← Salir          💎 150 AXF    🪙 42.5 FRJ          │
└──────────────────────────────────────────────────────┘
```

**Cambios específicos:**
- Altura: `h-14` → `h-10` (más fino)
- Fondo: `bg-[#060610]/80` → `bg-[#060610]/40` (más translúcido)
- Brand: se oculta el texto "AXOLOTTO", solo queda 🦎 o se oculta todo
- VIP chip: oculto
- DailyClaim: oculto
- Logout: oculto
- AXF chip: sin `onClick`, `cursor-default`, sin `hover:bg-*`, sin borde interactivo. Solo display.
- FRJ chip: igual que AXF — solo display
- Botón "← Salir": sutil, opacidad baja, solo visible en hover (desktop) o tras 2s de inactividad (mobile). Al pulsar → `onBack` del wizard.

**Propiedad CSS clave:**
```css
.immersive-header .token-chip {
  cursor: default;
  pointer-events: none; /* no interactivo */
}
```

### 4.4 ZoneDock — Animación de Salida/Entrada

```typescript
// ZoneDock recibe nueva prop opcional:
visible?: boolean; // default true
```

**Animación de salida** (cuando `visible` pasa a `false`):
```css
@keyframes dock-exit {
  from { transform: translateY(0); opacity: 1; }
  to   { transform: translateY(100%); opacity: 0; }
}
.animate-dock-exit {
  animation: dock-exit 300ms ease-out forwards;
}
```

**Animación de entrada** (cuando `visible` pasa a `true`):
```css
@keyframes dock-enter {
  from { transform: translateY(100%); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}
.animate-dock-enter {
  animation: dock-enter 300ms ease-out forwards;
}
```

**Estrategia de montaje**: Para que la animación de salida se reproduzca antes de desaparecer el DOM, `ZoneDock` usa un estado interno `exiting`. Cuando `visible` pasa a `false`, se activa `exiting = true` y se reproduce la animación. Al terminar (`onAnimationEnd`), se notifica al padre vía callback para que deje de renderizar.

Alternativa más simple: siempre renderizar ZoneDock pero con `pointer-events-none` y opacidad 0 cuando está oculto, y con `pointer-events-auto` y opacidad 1 cuando está visible. Usar transiciones CSS:

```tsx
<nav className={`
  fixed bottom-0 left-0 right-0 z-40
  transition-all duration-300 ease-out
  ${visible
    ? 'translate-y-0 opacity-100 pointer-events-auto'
    : 'translate-y-full opacity-0 pointer-events-none'
  }
`}>
```

### 4.5 Acelerador x2 (CPU Mode)

#### Hook `useCpuGame` — Cambios

```typescript
// Nueva exportación del hook:
export interface UseCpuGameState {
  // ... existente ...
  speedMultiplier: number;
  setSpeedMultiplier: (m: number) => void;
}
```

**Implementación interna:**
```typescript
const speedRef = useRef(1);
const [speedMultiplier, setSpeedMultiplier] = useState(1);

// En el tick:
animTimerRef.current = setTimeout(tick, CPU_TICK_MS / speedRef.current);

// Cuando setSpeedMultiplier cambia:
useEffect(() => {
  speedRef.current = speedMultiplier;
}, [speedMultiplier]);
```

#### GameScreen — Interacción Hold

```typescript
// Estados internos para el acelerador:
const [holding, setHolding] = useState(false);
const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

const handlePointerDown = () => {
  holdTimerRef.current = setTimeout(() => {
    setHolding(true);
    onSpeedChange?.(2);  // nueva prop opcional
  }, 400); // 400ms de hold para activar
};

const handlePointerUp = () => {
  if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
  setHolding(false);
  onSpeedChange?.(1);
};
```

#### Indicador Visual "⚡ x2"

```tsx
{holding && (
  <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50
                  bg-amber-500/90 text-white font-black text-sm
                  px-4 py-1.5 rounded-full
                  shadow-[0_0_20px_rgba(245,158,11,0.5)]
                  animate-pulse">
    ⚡ x2
  </div>
)}
```

**Posiciones del hold:**
- En **todo el contenedor del juego** (GameScreen wrapper) — no solo el tablero
- El tablero en CPU mode no es interactivo, así que no hay conflicto
- En desktop adicional: `keydown`/`keyup` de barra espaciadora

### 4.6 Activity Ticker y MochilaFloating

- **Ticker**: se oculta con fade out (200ms) cuando `isGameActive === true`
- **MochilaFloating**: se oculta con fade out (200ms) cuando `isGameActive === true`
- Ambos usan la misma estrategia de CSS transition que ZoneDock

### 4.7 Botón de Salida (Escape Hatch)

En el header inmersivo, se añade un botón sutil para salir de la partida:

```tsx
<button
  onClick={onExitGame}
  className="text-slate-600 hover:text-red-400 transition-all duration-300
             opacity-0 group-hover:opacity-100  /* desktop: hover */
             md:opacity-0 md:hover:opacity-100
             opacity-100 touch-none"  /* mobile: siempre visible pero sutil */
  title="Salir de la partida"
>
  ← Salir
</button>
```

**Comportamiento al pulsar "Salir":**
- CPU mode: vuelve a `board-select` (el juego se descarta)
- Auto mode: vuelve a `playing` (el axo sigue jugando en servidor)
- Manual mode: muestra confirmación "¿Abandonar partida?" antes de desconectar WebSocket

---

## 5. Archivos a Modificar

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `frontend/app/play/page.tsx` | Añadir `isGameActive` state, callback a PlayMode, renderizado condicional de ZoneDock/ticker/MochilaFloating, variante de header inmersivo | 🔴 Core |
| `frontend/components/PlayMode.tsx` | Aceptar y llamar `onGameActiveChange` según `gameView` | 🔴 Core |
| `frontend/components/play/ZoneDock.tsx` | Añadir prop `visible` con transición CSS slide-out/in | 🔴 Core |
| `frontend/components/screens/GameScreen.tsx` | Añadir interacción hold para acelerador CPU, badge "⚡ x2", aceptar `onSpeedChange` | 🟡 Acelerador |
| `frontend/components/CpuGameWrapper.tsx` | Pasar `speedMultiplier` y `setSpeedMultiplier` entre hook y GameScreen | 🟡 Acelerador |
| `frontend/hooks/useCpuGame.ts` | Añadir `speedRef`, exponer `speedMultiplier`/`setSpeedMultiplier` | 🟡 Acelerador |
| `frontend/components/play/MochilaFloating.tsx` | Añadir prop `visible` (o leer de contexto) | 🟢 Secundario |

**Archivos nuevos (opcionales):**

| Archivo | Propósito |
|---------|-----------|
| `frontend/components/play/ImmersiveHeader.tsx` | Componente de header mínimo (si se prefiere extraer en vez de inline) |

---

## 6. Animaciones y Transiciones

### Resumen de Curvas

| Elemento | Trigger | Duración | Easing | Efecto |
|----------|---------|----------|--------|--------|
| ZoneDock exit | `isGameActive` → true | 300ms | ease-out | `translateY(100%)` + `opacity: 0` |
| ZoneDock enter | `isGameActive` → false | 300ms | ease-out | `translateY(0)` + `opacity: 1` |
| Header normal→inmersivo | `isGameActive` → true | 300ms | ease-in-out | Altura reduce, elementos fade-out |
| Ticker exit | `isGameActive` → true | 200ms | ease-out | `opacity: 0` + `max-height: 0` |
| Badge "⚡ x2" enter | hold 400ms | 200ms | ease-out | `scale(0.5)` → `scale(1)` + fade-in |
| Badge "⚡ x2" exit | release | 150ms | ease-in | fade-out + `scale(1.1)` |

### Coordinación

Todas las animaciones de salida (ZoneDock, ticker, MochilaFloating, header) se disparan simultáneamente al entrar en modo inmersivo. La duración máxima es 300ms. El tablero puede escalar ligeramente para llenar el espacio liberado:

```css
.game-board-immersive {
  transform: scale(1.03);
  transition: transform 400ms ease-out 150ms; /* ligero delay para que termine antes el hide */
}
```

---

## 7. Edge Cases y Consideraciones

### 7.1 ¿Qué pasa si el jugador minimiza/cierra durante partida?
- CPU: el juego es efímero (solo animación cliente), no pasa nada.
- Auto: el axo sigue jugando en servidor. Al volver, `PlayingScreen` retoma el polling.
- Manual WebSocket: la conexión se interrumpe. Al volver, reconexión automática con `game_state_sync`.

### 7.2 ¿Cómo afecta al tutorial?
El `TutorialCpuGame` usa internamente `useCpuGame`. Debería también mostrar el modo inmersivo para ser consistente. El tutorial ya tiene su propio overlay de instrucciones que está por encima.

### 7.3 Desktop vs Mobile
- **Acelerador desktop**: barra espaciadora (más natural que click hold) + click derecho sostenido
- **Acelerador mobile**: touch hold en cualquier parte
- **Salir en mobile**: botón tenue siempre visible (no depende de hover)
- **Salir en desktop**: visible solo en hover del header

### 7.4 Accesibilidad
- El acelerador debe ser opcional — no es necesario para jugar
- El botón de salida debe ser accesible vía teclado (Tab + Enter)
- El modo inmersivo no debe romper lectores de pantalla (usar `aria-label` en header mínimo)

### 7.5 Rendimiento
- Las transiciones CSS son GPU-accelerated (transform + opacity)
- No debería haber impacto de rendimiento perceptible
- El speedRef en useCpuGame evita re-renders innecesarios durante aceleración

---

## 8. Plan de Implementación

### Fase 1: Core — Ocultar HUB (2-3h)
1. Añadir `isGameActive` state en `play/page.tsx`
2. Pasar `onGameActiveChange` a `PlayMode`
3. Implementar `useEffect` en PlayMode para detectar gameViews inmersivos
4. Conditional render de ZoneDock con prop `visible`
5. Animación slide-out/in en ZoneDock
6. Ocultar ticker y MochilaFloating

### Fase 2: Header Inmersivo (1-2h)
1. Crear variante condicional del header en `play/page.tsx`
2. Desactivar interactividad en chips de monedas
3. Ocultar VIP, DailyClaim, Logout
4. Añadir botón de salida sutil
5. Animación de transición

### Fase 3: Acelerador x2 (2-3h)
1. Modificar `useCpuGame` con `speedRef` y exponer `setSpeedMultiplier`
2. Añadir handlers de pointer/teclado en `GameScreen`
3. Crear indicador visual "⚡ x2"
4. Wire up en `CpuGameWrapper`
5. Testing: verificar que la animación se acelera/suelta correctamente

### Fase 4: Pulido y QA (1-2h)
1. Probar los 3 modos (CPU, auto, manual)
2. Verificar transiciones en mobile viewport
3. Probar edge cases (salir durante partida, cambiar de tab, etc.)
4. Ajustar timings y curvas de animación

---

## 9. Métricas de Éxito

- Los jugadores pasan **más tiempo en partida continua** (menos abandono durante juego)
- El **feedback cualitativo** menciona "inmersión" o "foco"
- La tasa de "Jugar Otra Vez" en CPU aumenta (el acelerador reduce el tiempo entre partidas)
- Cero bugs reportados de "no podía salir de la partida"

---

## 10. Notas para el Futuro

- **Modo Cine**: una evolución donde incluso el header se oculta totalmente, solo tablero en pantalla completa. Activar con doble tap en área vacía.
- **Personalización de velocidad**: que el jugador configure velocidad default (1x, 1.5x, 2x) en settings.
- **Acelerador en replay**: ver partidas pasadas con control de velocidad (como playback).
- **Efectos de sonido**: el acelerador x2 podría ir acompañado de un pitch shift en los SFX de cartas (más agudo = más rápido), como en los juegos de ritmo.
