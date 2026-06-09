# PlayMode v2 — Plan de Rediseño Completo
> Objetivo: convertir el Centro de Partidas en un flujo paso a paso full-pantalla con estética de videojuego 2.5D, igual de inmersivo que el Santuario/Nido.
> Fecha creación: 2026-05-27

---

## Reglas del plan
- No avanzar a la siguiente fase hasta que el build TypeScript esté limpio (`tsc --noEmit`)
- Cada UI se verifica en mobile 375px y desktop 1280px antes de marcar ✅
- El flujo viejo (`view: 'hub' | 'individual' | 'autoplay'`) se elimina en la Fase 0 — **no conviven**
- Las animaciones se definen primero en CSS (`globals.css`) antes de usarse en componentes

---

## Contexto y decisiones de diseño

### Moneda: COR (Corcholata)
- `gemas_alga` en la API = **COR** en la UI
- COR es moneda virtual 100% in-game, sin conversión a dinero real
- El modo CPU consume COR — es aceptable mostrar resultado + "jugar otra vez"
- Riesgo legal mínimo; sin embargo se mantiene delay de 2s antes de activar "Jugar Otra Vez"

### Feed & Sleep — Decisión UX
**Recomendación adoptada: Axo Status Bar persistente + BottomSheet**

Existe un componente `<AxoStatusBar>` que vive **encima del WizardStepBar** en todos los pasos excepto el Paso 1 (modo select, donde aún no hay axolotito elegido). Es una barra compacta de 48px:

```
┌──────────────────────────────────────────────────────────┐
│  [avatar 28px]  Axo-001  ▓▓▓▓▓░░  62%  [•Activo]  [⚡▾] │
└──────────────────────────────────────────────────────────┘
```

- Tap en cualquier parte → abre `BottomSheet` con feed/sleep/stats completos
- Si energía < 25%: la barra pulsa en rojo, badge `⚠️ Alimentar`
- Si está durmiendo: barra muestra timer countdown, badge `💤 Xm restantes`
- El botón `[⚡▾]` es el entry point explícito para mobile

**Por qué no solo en el Paso 2:**
El usuario puede llegar al Paso 3 o 5, darse cuenta de que el axolotito está sin energía, y necesita acceso sin perder el estado del wizard.

**Por qué no un FAB:**
El FAB compite visualmente con el botón JUGAR (CTA principal). La barra es menos intrusiva.

### Presupuesto — Persistencia
```ts
// Clave: `axolotto_budget_{userId}_{axoId}`
interface SavedBudget {
  budget: number;        // COR
  lossLimitPct: number;  // 5–80
  profitLimitPct: number; // 10–300
}
```
Se carga al entrar al Paso 4. Se guarda al presionar JUGAR.

### Recall / Retorno del Axolotito
Cuando el axolotito llega al límite de pérdidas o ganancias, entra en estado `waiting_settlement`. El usuario ve:
- Banner "Tu axolotito terminó su jornada"
- Botón primario: **"Confirmar Retorno y Cobrar"** (hace el settle)
- El botón NO es automático — requiere tap del usuario

---

## State Machine: `GameView`

```ts
type GameView =
  | 'axo-select'    // Paso 0 — Entrada: ¿qué axolotito? (+ settlement inline de axos waiting)
  | 'mode-select'   // Paso 1 — CPU o Multiplayer (axo ya elegido)
  | 'board-select'  // Paso 2 — ¿Con qué tabla(s)?
  | 'budget'        // Paso 3 (multi) — Presupuesto + límites
  | 'sala-select'   // Paso 4 (multi) — Elegir sala con stats vivos
  | 'cpu-sim'       // Simulador CPU (animación → resultado → re-play in-place)
  | 'playing'       // Axo activo en lobby multiplayer
  | 'settling';     // Corte de caja pendiente (multi)

type GameMode = 'cpu' | 'multi';
```

**Flujo de transiciones (v2.1):**
```
axo-select ──► mode-select ──[CPU]──► board-select ──► cpu-sim ──► [Jugar Otra Vez: remount in-place]
                                                    └──[Multi]──► budget ──► sala-select ──► playing ──► settling
```

- `axo-select` es el punto de entrada
- `AxoStatusBar` visible desde `mode-select` en adelante
- `WizardDots` visible desde `mode-select` en adelante (steps: `['Modo','Tabla']` CPU / `['Modo','Tablas','Presupuesto','Sala']` Multi)
- Axo con `waiting_settlement` → expandible con settlement inline en `axo-select` (NO auto-navega a settling desde ahí)

---

## Arquitectura de Componentes

```
PlayMode.tsx                          (orquestador principal, mantiene estado global)
  ├── AxoStatusBar.tsx                (barra persistente desde mode-select en adelante)
  ├── WizardDots.tsx                  (dots desde mode-select en adelante)
  ├── screens/
  │   ├── AxoSelectScreen.tsx         (ENTRADA — elige axo + settlement inline de waiting_settlement)
  │   ├── ModeSelectScreen.tsx        (Paso 1 — muestra nombre del axo elegido)
  │   ├── BoardSelectScreen.tsx       (Paso 2 — CPU o Multi)
  │   ├── BudgetScreen.tsx            (Paso 3 multi)
  │   ├── SalaSelectScreen.tsx        (Paso 4 multi)
  │   ├── CpuSimScreen.tsx            (Simulador — remount-key para "Jugar Otra Vez" in-place)
  │   ├── PlayingScreen.tsx           (Dashboard activo multi)
  │   └── SettlingScreen.tsx          (Corte de caja — para settlement desde PlayingScreen)
  └── ui/
      └── LoteriaBoard.tsx            (tabla de lotería animada para CpuSimScreen)
```

> Los screens viven en `components/screens/` o inline en `PlayMode.tsx` como componentes internos — a elección del dev, pero tipados como subcomponentes.

---

## FASE 0 — Limpieza y fundación
> Tiempo estimado: 2–4 horas

### 0.1 Tipos y constantes
- [x] Agregar el tipo `GameView` y `GameMode` a PlayMode.tsx (o a `lib/types.ts` si ya existe)
- [x] Reemplazar `view: 'hub' | 'individual' | 'autoplay'` con `gameView: GameView`
- [x] Reemplazar `step: number` con estado derivado del gameView (ya no se necesita step separado)
- [x] Crear helper `saveBudget(userId, axoId, budget)` / `loadBudget(userId, axoId)` con localStorage
- [x] **Verificación:** `tsc --noEmit` limpio ✅

### 0.2 Animaciones CSS nuevas en `globals.css`
- [x] `@keyframes slide-step` — entrada de pantalla desde derecha (translateX 40px → 0, opacity 0→1, 250ms ease-out)
- [x] `@keyframes slide-step-back` — salida hacia derecha al ir atrás (inverso)
- [x] `@keyframes card-call` — carta cantada: scale 1→1.2→1, glow burst, 400ms
- [x] `@keyframes board-fill-cell` — celda de tabla se ilumina: bg opacity 0→1 + glow, 300ms
- [x] `@keyframes cpu-win-surge` — tabla del CPU vuela al frente: translateY(-20%) + scale(1.1) + glow rojo
- [x] `@keyframes player-win-bloom` — tabla ganadora crece: scale(1→1.08) + glow esmeralda burst
- [x] `@keyframes result-fade-in` — pantalla de resultado: opacity 0→1 + scale(0.95→1), 400ms
- [x] **Verificación:** Build limpio, ninguna animación rota en Santuario.tsx ✅

---

## FASE 1 — Shell del wizard
> Tiempo estimado: 4–6 horas

### 1.1 `WizardDots` (reemplaza `WizardStepBar`)
- [x] Crear componente `WizardDots` con props: `steps: string[]`, `current: number`, `onBack: () => void`
- [x] Cada paso = punto circular; tamaños: completado 10px, activo 14px (pulsando), pendiente 8px
- [x] Línea conectora: `bg-brand-hot/30` completada, `bg-slate-800` pendiente
- [x] Labels debajo de cada punto (ocultos en mobile ≤375px)
- [x] Botón ← siempre visible (izquierda), vuelve a mode-select desde axo-select
- [x] Animación de avance: punto activo hace `scale` pulse (via `animate-pulse`) antes de llenarse
- [x] **Verificación visual:** mobile y desktop — pendiente prueba manual ⏳

### 1.2 `AxoStatusBar`
- [x] Crear componente con props: `axo: any | null`, `onAction: (action: 'feed-pellet' | 'feed-shrimp' | 'sleep' | 'wake') => void`
- [x] Cuando `axo === null`: no renderiza (paso 1 no tiene axo aún)
- [x] Avatar 28px SVG circular con borde de color por rareza
- [x] Nombre truncado a 12 chars + nivel XP pequeño
- [x] Barra de energía `w-20 h-1.5 rounded-full` — color semafórico (verde/amarillo/rojo)
- [x] Badge de estado: `•Listo` verde, `💤 Xm` azul pulsando, `🎮 En cancha` ámbar, `⚠️ Energía` rojo pulsando
- [x] Tap en barra → abre BottomSheet existente con controles de feed/sleep completos
- [x] **Verificación:** no rompe layout en Santuario.tsx (no se usa allá) ✅

### 1.3 Contenedor de transición de pasos
- [x] En PlayMode.tsx, envolver cada screen en un `<div key={gameView} className="animate-slide-step">`
- [x] Al ir hacia atrás (`onBack`): aplicar clase `animate-slide-step-back` en lugar de `animate-slide-step`
- [x] Usar `useRef` para saber la dirección (adelante/atrás) y seleccionar la animación correcta
- [x] **Verificación visual:** transición suave en mobile — pendiente prueba manual ⏳

---

## FASE 2 — Paso 1: Selección de Modo
> Tiempo estimado: 3–4 horas

### 2.1 `ModeSelectScreen`
- [x] Dos tarjetas grandes (stack vertical en mobile, row en desktop ≥768px)
- [x] Altura mínima 180px en desktop, 140px en mobile
- [x] Forma de arco: `border-radius: 50% 50% 12px 12px / 55% 55% 12px 12px` (igual que NidoCave)
- [x] **Tarjeta CPU:**
  - Fondo: gradiente `from-indigo-950 to-[var(--world-void)]`
  - Borde: `border-indigo-500/30`, hover `border-indigo-500/70`
  - Glow: `shadow-[0_0_30px_rgba(99,102,241,0.15)]` → hover `rgba(99,102,241,0.35)`
  - Partículas: 5 burbujas índigo pequeñas (`.animate-bubble-rise` existente) con delays diferentes
  - Ícono central: `🤖` en `text-5xl` con `animate-axo-bob`
  - Título: "VS CPU" — `text-3xl font-black uppercase tracking-tighter`
  - Sub: "Partida rápida · Resultado en segundos" — `text-xs text-slate-400`
  - Badge bottom-left: "Consumes COR" con `Coins` icon
- [x] **Tarjeta Multijugador:**
  - Fondo: gradiente `from-pink-950 to-[var(--world-void)]`
  - Borde: `border-[var(--brand-hot)]/25`, hover `border-[var(--brand-hot)]/60`
  - Glow: `shadow-[0_0_30px_var(--brand-glow)]` en hover
  - Partículas: burbujas rosas
  - Ícono central: `👥` con `animate-axo-wander`
  - Título: "MULTIJUGADOR"
  - Sub: "Compite contra otros jugadores en tiempo real"
  - Badge bottom-left: "Presupuesto por partida"
- [x] Click → `setGameMode(mode)` + `setGameView('axo-select')`
- [x] Sin `AxoStatusBar` ni `WizardDots` en este paso (aún no hay contexto de axo)
- [x] Título de sección encima: "🎮 Centro de Partidas" con gradiente indigo→pink
- [x] **Verificación visual:** pendiente prueba manual ⏳

---

## FASE 3 — Paso 2: Selección de Axolotito
> Tiempo estimado: 4–5 horas

### 3.1 `AxoSelectScreen`
- [x] Reusar lógica de renderizado de axolotitos del sidebar actual (líneas ~535–635)
- [x] Layout: grid de 1 columna (todas las anchos) — tarjetas horizontales de 72px de alto
- [x] Al seleccionar, tarjeta seleccionada se expande con acordeón (150ms ease) mostrando stats completos
- [x] **Tarjeta default (72px):**
  - Avatar SVG circular 40px
  - Nombre + badge de estado (derecha)
  - Barra de energía (20% del ancho, al fondo)
- [x] **Tarjeta expandida (adicional ~120px):**
  - Grid 4 cols de stats: Focus, Luck, Stamina, Salinity, Charisma, Agility, Wisdom, Strength
  - XP + Loyalty points
  - Botones inline: `Alga Pellet` y `Camarón Brine` (solo si no está durmiendo/jugando)
  - Botón `Dormir / Despertar`
- [x] Estado "En cancha": overlay con nombre de la tabla donde juega, no clickeable
- [x] Estado "Dormido": overlay con countdown, botón "Despertar" si ya terminó el timer
- [x] Sin axolotitos → card vacía con mensaje + link al Criadero
- [x] CTA: botón "Continuar →" aparece en footer fijo cuando hay axolotito seleccionado
- [x] **Verificación:** overflow scroll con 5+ axolotitos — pendiente prueba manual ⏳

---

## FASE 4 — Paso 3: Selección de Tabla(s)
> Tiempo estimado: 3–4 horas

### 4.1 `BoardSelectScreen`
- [x] Reusar `BoardGrid` existente (líneas ~330–418) como base
- [x] Grid: 3 cols desktop, 2 cols mobile
- [x] Altura de tarjeta: 100px (más generosa que el actual)
- [x] **Modo CPU:** selección única (click en una deselecciona la anterior)
- [x] **Modo Multi:** selección múltiple 1–3; tarjeta seleccionada muestra checkmark numerado (1, 2, 3)
- [x] Tooltip de hover al pasar mouse (mantener comportamiento actual, líneas 1053–1084)
- [x] Tabla "en juego por otro axo": overlay con nombre del axolotito, no seleccionable
- [x] Tabla seleccionada: `border-emerald-500`, `shadow-[0_0_15px_rgba(16,185,129,0.3)]`
- [x] Sin tablas disponibles: mensaje + link a Inventario
- [x] **Botón JUGAR (solo CPU):**
  - Aparece en footer fijo con `animate-sheet-up` cuando hay ≥1 tabla seleccionada
  - Altura: 64px, `border-radius: 20px`
  - Fondo: gradiente `from-[var(--brand-hot)] to-indigo-600`
  - Glow: `shadow-[0_0_30px_var(--brand-glow)]`
  - Texto: "▶ JUGAR" `text-xl font-black uppercase tracking-widest`
  - Hover: glow intensifica
  - Press: `scale(0.97)`
  - Click: `setGameView('cpu-sim')`
- [x] **Botón Continuar (solo Multi):**
  - Footer fijo, mismo estilo pero texto "Continuar →" y sin el glow de brand-hot
  - Click: `setGameView('budget')`
- [x] **Selector de sala inline (CPU):** Rookie / Campeón como compact selector
- [x] **Verificación:** pendiente prueba manual ⏳

---

## FASE 5 — Pasos 4 y 5: Budget y Sala (Multiplayer)
> Tiempo estimado: 5–6 horas

### 5.1 `BudgetScreen`
- [x] Cargar defaults con `loadBudget(userId, selectedAxo.id)` al montar
- [x] Slider presupuesto: `min=10`, `max=balances.gemas_alga`, step=5
  - Track color: verde si budget < saldo*0.5, ámbar si < saldo*0.8, rojo si más
  - Input numérico sincronizado (cambio en slider → actualiza input y vice-versa)
- [x] Slider límite pérdida %: `min=5`, `max=80`, step=5
  - Track rojo
- [x] Slider límite ganancia %: `min=10`, `max=300`, step=10
  - Track verde
- [x] **Panel de resumen calculado en vivo (siempre visible)**
- [x] Valores se actualizan en tiempo real mientras se mueven los sliders
- [x] Saldo disponible mostrado arriba: `Tu saldo: X COR`
- [x] Si budget > saldo: error inline "Presupuesto supera tu saldo"
- [x] Botón "Continuar →" en footer fijo (deshabilitado si budget > saldo)
- [x] Al presionar Continuar: `saveBudget(userId, axo.id, {...})` + `setGameView('sala-select')`
- [x] **Verificación:** localStorage persiste entre navegaciones — pendiente prueba manual ⏳

### 5.2 `SalaSelectScreen`
- [x] Polling de datos de sala cada 10 segundos (`useEffect` con `setInterval`)
- [x] **Tarjeta Rookie:**
  - Barra de llenado con fill animado
  - `X / Y jugadores` badge actualizado cada poll
  - Si sala al 80%+: borde pulsa cada 2s, badge "¡Sale pronto!" en ámbar pulsando
- [x] **Tarjeta Champion:** idéntica estructura, colores pink/rose
- [x] Click en tarjeta la marca como seleccionada (borde brillante, checkmark)
- [x] Cuando hay tarjeta seleccionada: botón JUGAR aparece con `animate-sheet-up`
  - Click → `handleMultiplayerRegister()` → si OK → `setGameView('playing')`
- [x] Estado de error inline si registro falla (sala llena, sin COR, etc.)
- [x] **Verificación:** polling funciona — pendiente prueba manual ⏳

---

## FASE 6 — Simulador CPU (la pieza más visual)
> Tiempo estimado: 2–3 días

### 6.1 Diseño del componente `LoteriaBoard`
- [x] Crear `components/ui/LoteriaBoard.tsx`
- [x] Props: `boardCards`, `matchedIndices`, `isWinner`, `depth`, `label`
- [x] Grid 4×4 de celdas de carta con emoji de lotería
- [x] Celda marcada: `animate-board-fill-cell` + color `emerald-400/80` + glow suave
- [x] Celda no marcada: fondo `world-surface`, borde `slate-800`
- [x] `depth='back'`: `scale(0.80)` + `opacity-50` + `filter blur(1px)`
- [x] `depth='mid'`: `scale(0.90)` + `opacity-70`
- [x] `depth='front'`: `scale(1.0)` + `opacity-100`
- [x] `isWinner=true`: `animate-player-win-bloom` + glow esmeralda burst
- [x] Label flotante arriba de la tabla
- [x] **Verificación:** 4 instancias simultáneas — pendiente prueba manual ⏳

### 6.2 Animación de carta cantada
- [x] Componente `CalledCard` inline en `CpuSimScreen`: muestra emoji+nombre de la carta
- [x] Entra desde arriba con `animate-card-call`: scale 0→1.2→1, glow burst, 400ms
- [x] Historial de últimas 3 cartas cantadas visible debajo (opacidad decreciente)
- [x] Fuente de datos: `drawn_cards_sample` del backend, reproducidas en secuencia
- [ ] Permanecer visible 1.2s antes de que empiece la siguiente carta (actualmente 800ms)

### 6.3 `CpuSimScreen` — orchestrador
- [x] Estado interno: `SimPhase = 'loading' | 'animating' | 'result'`
- [x] **Fase `loading`:** spinner + "Iniciando partida..." — obtener resultado del backend
- [x] **Fase `animating`:** reprodución de `drawn_cards_sample` cada 800ms
  - [x] Tabla CPU y tabla del jugador simultáneas
  - [ ] Tabla CPU posicionada absolutamente en el centro-fondo (actualmente en flujo normal)
  - [x] Celdas marcadas animadas con `animate-board-fill-cell`
  - [ ] Warning "⚠️ CPU cerca..." cuando CPU llega al 70% de llenado
- [x] **Fase `result`:**
  - [x] Overlay con `animate-result-fade-in`
  - [x] Victoria: gradiente esmeralda + texto + COR + XP
  - [x] Derrota: gradiente rosa + texto motivacional
  - [x] Stats: cartas cantadas, XP axo, XP tabla
  - [x] Botón "▶ JUGAR OTRA VEZ" con delay de 2s
  - [x] Botón "← Cambiar todo"
- [x] Timeout de API: botón "Reintentar" visible
- [x] **Verificación:** animación completa — pendiente prueba manual ⏳

---

## FASE 7 — Dashboard de Juego Activo (Multiplayer)
> Tiempo estimado: 3–4 horas

### 7.1 `PlayingScreen`
- [x] Refactor del panel `isPlaying` actual como screen dedicado
- [x] **Header:** ícono + nombre + badge "🎮 En las canchas"
- [x] **Métricas en vivo (3 cards):** Entró con | En custodia | Diferencia
  - Diferencia positiva: verde con +, negativa: roja
- [x] **Floating earnings:** comportamiento actual preservado
- [x] **Barra de límites:** zona roja/verde + marcador dinámico según `escrow_balance_gal`
- [x] **Sección recall:**
  - Si NO recall pedido: botón "📣 Llamar de Regreso" (outline rojo)
  - Si recall pedido: banner ámbar + spinner
- [x] Auto-navigate a `playing` cuando `selectedAxo.status === 'playing'`
- [x] **Verificación:** polling de 15s — pendiente prueba manual ⏳

### 7.2 `SettlingScreen`
- [x] Refactor del panel `isSettling` actual como screen dedicado
- [x] Banner principal: "🏆 Jornada Terminada"
- [x] Resumen: presupuesto inicial | retorno final | ganancia/pérdida neta (con color)
- [x] Botón principal: **"✅ Confirmar Retorno y Cobrar"** `text-xl font-black` en verde-esmeralda
- [x] Deshabilitar durante la llamada API + spinner
- [x] Después de confirmar: volver a `axo-select` con el axolotito recién actualizado
- [x] Auto-navigate a `settling` cuando `selectedAxo.status === 'waiting_settlement'` **y no estás en `axo-select`**
- [x] **Verificación:** pendiente prueba manual ⏳

---

## FASE 8 — Polish y QA
> Tiempo estimado: 1 día

### 8.1 Edge cases
- [x] Sin axolotitos eclosionados → card vacía con mensaje desde `axo-select`
- [x] Sin tablas disponibles → card con mensaje desde `board-select`
- [x] Si budget > saldo: deshabilitar "Continuar" en `budget` con mensaje
- [x] Timeout de API en simulador → botón "Reintentar" visible
- [ ] Axolotito sin energía (0) en modo CPU → warning pero dejar intentar (el backend rechazará)
- [ ] Sala llena al intentar inscribirse → error inline ya capturado por `withError`
- [ ] Navegación con botón atrás del sistema en mobile → debe activar `onBack` del wizard

### 8.2 Performance
- [x] Las animaciones del simulador CPU usan `setTimeout` — no `setInterval` para el frame loop
- [x] El polling de sala (10s) se cancela al desmontar `SalaSelectScreen`
- [x] El polling de jugador activo (15s) se cancela al cambiar a `settling` o al desmontar
- [ ] Las tablas de lotería en `CpuSimScreen` no re-renderizan completas en cada tick (optimización futura con `React.memo`)

### 8.3 Verificación final — pendiente pruebas manuales ⏳
- [x] Build TypeScript limpio: `tsc --noEmit` sin errores ✅
- [x] Build producción: `npm run build` exitoso ✅
- [ ] Flujo CPU completo: mode-select → axo → board → simulador (victoria) → jugar otra vez
- [ ] Flujo CPU completo: mode-select → axo → board → simulador (derrota) → jugar otra vez
- [ ] Flujo Multi completo: mode-select → axo → board → budget → sala → playing → settling
- [ ] Feed desde `AxoStatusBar` en paso 3, 4 y 5 funciona sin perder el estado del wizard
- [ ] Presupuesto persiste entre sesiones para el mismo axolotito
- [ ] Mobile 375px: nada se corta ni desborda
- [ ] Desktop 1280px: las arch cards del Paso 1 tienen buenas proporciones

---

## FASE 9 — Cambios de flujo v2.1
> Implementados en la misma sesión que el plan.

### 9.1 Axolotito como punto de entrada ✅
- [x] `PlayMode.tsx`: `gameView` inicial → `'axo-select'`
- [x] `PlayMode.tsx`: `onBack` actualizado (mode-select ← axo-select, board-select ← mode-select)
- [x] `PlayMode.tsx`: `AxoSelectScreen.onContinue` → `navigate('mode-select')` (antes iba a board-select)
- [x] `PlayMode.tsx`: `ModeSelectScreen.onSelect` → `navigate('board-select')` (antes iba a axo-select)
- [x] `PlayMode.tsx`: `wizardConfig` — dots empiezan en `mode-select` con labels `['Modo','Tabla']` / `['Modo','Tablas','Presupuesto','Sala']`
- [x] `PlayMode.tsx`: `showAxoStatusBar` — excluye `axo-select` en vez de `mode-select`
- [x] `ModeSelectScreen.tsx`: prop `selectedAxo` opcional — muestra nombre del axo en el subtítulo
- [x] `AxoSelectScreen.tsx`: header "🎮 Centro de Partidas" como pantalla de entrada
- [ ] **Verificación:** flujo completo axo → modo → tabla → jugar ⏳

### 9.2 Settlement inline en AxoSelectScreen ✅
- [x] `PlayMode.tsx`: función `handleSettleInline(axo)` — llama API, abre modal de reporte, recarga datos, NO navega
- [x] `PlayMode.tsx`: estado `settlingAxoId: number | null` para spinner de loading
- [x] `PlayMode.tsx`: auto-navigate a `settling` solo si NO estamos en `axo-select` (nuevo: `!['axo-select','settling'].includes(gameView)`)
- [x] `AxoSelectScreen.tsx`: props `onSettleInline` + `settlingAxoId`
- [x] `AxoSelectScreen.tsx`: card de `waiting_settlement` expandible (no más overlay bloqueante)
- [x] `AxoSelectScreen.tsx`: expanded view muestra métricas (Entró con / En custodia / Diferencia) + botón "✅ Confirmar Retorno y Cobrar"
- [x] `AxoSelectScreen.tsx`: después de settle, card vuelve a estado normal (data refresh)
- [ ] **Verificación:** settle desde axo-select sin navegar, modal de reporte aparece ⏳

### 9.3 "Jugar Otra Vez" in-place (CPU) ✅
- [x] `PlayMode.tsx`: estado `cpuSimKey: number` — incrementar remonta CpuSimScreen limpio
- [x] `PlayMode.tsx`: `CpuSimScreen` recibe `key={cpuSimKey}`, `onPlayAgainInPlace`, `onChangeBoard`
- [x] `PlayMode.tsx`: `onChangeAll` ahora navega a `axo-select` (no a mode-select, es el nuevo entry)
- [x] `CpuSimScreen.tsx`: props actualizados — `onPlayAgainInPlace`, `onChangeBoard`, `onChangeAll`
- [x] `CpuSimScreen.tsx`: 3 botones en fase result: **Jugar Otra Vez** (grande), **Cambiar Tabla o Sala** (outline), **Cambiar todo** (pequeño texto)
- [ ] **Verificación:** jugar 3 veces seguidas sin navegar; "Cambiar Tabla" va a board-select ⏳

### 9.4 Ideas adicionales implementadas ✅
- [x] **Recordar último modo** — `localStorage.setItem('axolotto_last_game_mode', mode)` al seleccionar, leído al montar con `useEffect([], [])`
- [x] **AxoStatusBar visible en mode-select** — antes se excluía; ahora el axo ya está elegido cuando llegas ahí

### 9.5 Ideas pendientes (deferred)
- [ ] **"Revancha" / "Jugar Rápido"** desde AxoSelectScreen — requiere `last_board_id` o `assigned_board_id` confiable desde backend
- [ ] **Mini confetti** tras settlement inline positivo — `animate-player-win-bloom` en el card
- [ ] **Indicador de tabla usada** en card de axo — requiere backend devolver `last_board_name`
- [ ] **Botón atrás del sistema (Android/iOS)** — `window.history.pushState` + listener `popstate` → `onBack()` del wizard

---

## Extras implementados (no estaban en el plan original)
- [x] **Selector de sala inline en `BoardSelectScreen` (CPU)** — Rookie / Campeón como compact selector compacto antes del botón JUGAR
- [x] **Auto-navigate automático** cuando `selectedAxo.status` cambia a `playing` o `waiting_settlement` (ajustado en v2.1 para no interferir con settlement inline)
- [x] **Dirección de transición bidireccional** — navegar atrás usa `animate-slide-step-back` para sensación de "regreso"
- [x] **Barra de límites dinámica en `PlayingScreen`** — marcador se mueve según `escrow_balance_gal` en tiempo real
- [x] **Input numérico sincronizado en `BudgetScreen`** — además del slider, se puede escribir el valor directamente
- [x] **Retorno automático a `axo-select` tras settle** — sin necesidad de click adicional
- [x] **Axolotito como punto de entrada** (v2.1) — flujo invertido: elige axo → modo → tabla
- [x] **Settlement inline** (v2.1) — axos `waiting_settlement` se cobran desde `axo-select` sin navegar
- [x] **"Jugar Otra Vez" in-place** (v2.1) — mismo axo/tabla/sala, remount vía key
- [x] **Recordar último modo** (v2.1) — `localStorage` persiste entre sesiones

---

## Notas de implementación

### Sobre el simulador CPU y datos del backend
El backend retorna `win: boolean` del endpoint individual. Para la animación se necesita también:
- Las cartas que se cantaron (en orden) — preguntar al backend si ya retorna esto
- Qué índices de las tablas del jugador coincidieron
- Si el backend no retorna esto, la animación puede ser *ilustrativa* (simular un orden aleatorio de cartas) sin afectar el resultado real

### Sobre `LoteriaBoard` y las cartas
Usar el componente `<LoteriaCard>` existente en `components/ui/LoteriaCard.tsx` para cada celda. Size recomendado: `'xs'` (28px) en la vista del simulador para que quepan 4×4 en pantallas de 375px.

### COR vs GAL en la UI
Renombrar todos los labels visibles de "GAL" a "COR" en PlayMode.tsx. Los campos de la API (`gemas_alga`, `bot_budget_axg`, etc.) no cambian — solo el texto que ve el usuario.

---

## Resumen de tiempos estimados

| Fase | Descripción | Estimado |
|------|-------------|---------|
| 0 | Limpieza y CSS | 2–4 h |
| 1 | Shell del wizard | 4–6 h |
| 2 | Paso 1: Modo | 3–4 h |
| 3 | Paso 2: Axolotito | 4–5 h |
| 4 | Paso 3: Tablas | 3–4 h |
| 5 | Pasos 4–5: Budget + Sala | 5–6 h |
| 6 | Simulador CPU | 2–3 días |
| 7 | Dashboard activo + settling | 3–4 h |
| 8 | Polish y QA | 1 día |
| **Total** | | **~5–6 días de dev** |

---

---

## FASE 10 — Game Design Review & Rebalanceo de Economía
> Documento vivo — actualizar cuando cambien las constantes del backend.

### Contexto del análisis

El modo CPU es un juego **Casa vs Jugador**: los bots no pagan entrada. La casa financia todos los premios. Por eso la matemática de sostenibilidad es crítica.

El multiplayer es un **pool de jugadores**: la casa solo cobra rake (10%). Esa estructura es correcta y no necesita cambios.

---

### 10.0 Análisis: ¿Qué está bien?

| Elemento | Veredicto | Por qué |
|---|---|---|
| **Multiplayer house edge (10%)** | ✅ Correcto | 90% RTP → atractivo para jugadores, sostenible para casa |
| **Jackpot 5% acumulativo** | ✅ Correcto | Es un premio diferido, no ganancia real — crea emoción |
| **Focus como mecánica de skill** | ✅ Correcto | Miss rate visible y mejorable → progresión real |
| **Consolation prize (nunca salís con 0)** | ✅ Correcto | Reduce frustración, fideliza jugadores |
| **Anti-sybil (1 axo por sala por user)** | ✅ Correcto | Protege la integridad del jackpot |
| **VIP Axolite -15% multiplayer fee** | ✅ Correcto | Incentivo real y diferenciado |
| **Loyalty points formula** | ✅ Correcto | Simple, predecible, justa |
| **Energy system** | ✅ Correcto | Gasto moderado (10/partida), recuperación gratis con sleep |

---

### 10.1 🔴 PROBLEMA CRÍTICO — CPU Mode: Casa pierde dinero

#### Matemática de punto de equilibrio

En CPU mode, el breakeven de la casa se calcula así:

```
win_rate_breakeven = (entrada - consolación) / (premio_win - consolación)
```

| Sala (actual) | Entrada | Premio | Consolación | Win% break-even |
|---|---|---|---|---|
| Rookie | 10 COR | 35 COR | 1 COR | **26.5%** |
| Champion | 50 COR | 200 COR | 5 COR | **23.1%** |

Con 4 participantes iguales (1 jugador + 3 bots), cada uno gana **25%** del tiempo.

- **Rookie**: 25% > 26.5% → casa **pierde ~1.8%** (marginal pero negativo)
- **Champion**: 25% > 23.1% → **casa pierde ~8.5% por partida** 🚨

Y esto con un jugador promedio (Focus=50). Un jugador con Focus=100 (0% miss) contra bots a Focus=50 (15% miss) tiene win rate ~35-40%:

```
Champion con Focus=100:
EV jugador = 0.38 × 200 + 0.62 × 5 = 79.1 COR
Inversión = 50 COR
Casa pierde 29.1 COR por partida → -58% de house edge
```

**La estructura actual de CPU mode no es sostenible.**

#### ¿Por qué pasó esto?

El número 3 de bots fue elegido sin calcular el break-even matemático. El premio de 200 COR (4x) suena razonable pero con solo 3 bots competencia, el jugador tiene ventaja.

---

### 10.2 🟡 PROBLEMA SECUNDARIO — Bots sin diferenciación de dificultad

Ambas salas usan bots con `focus=50, luck=10`. La diferencia entre Rookie y Champion es *solo* el precio y el premio — no la dificultad del oponente. Esto viola el principio de "mayor riesgo = mayor desafío narrativo".

---

### 10.3 🟡 PROBLEMA SECUNDARIO — Luck sin impacto tangible

```
luck_bonus = (stat_luck / 1000) × prize_gal
```

Con luck=100 en Rookie: +3.5 COR sobre 35 COR = **+10% máximo**.  
Con luck=0 en Champion: pierdes 20 COR máximo de bonus.

El jugador no *siente* la diferencia de Luck. La stat no está cumpliendo su rol narrativo.

---

### 10.4 🟡 PROBLEMA SECUNDARIO — Wisdom sin uso en gameplay

`stat_wisdom` no aparece en `game.py` ni en `multiplayer.py`. El jugador la ve en su axolotito pero nunca la siente en el juego. Stats sin efecto = sensación de inutilidad.

---

### 10.5 ✅ PROPUESTA — Rediseño CPU Mode: Bot count variable

**Propuesta recomendada por el equipo de diseño:**

> "¿no se debería diferenciar por que te enfrentas a 1 o 5 tablas de acuerdo al modo, así es más difícil ganar mucho?"

**Esta intuición es matemáticamente correcta.** Análisis:

#### Rookie → 1v1 (jugador vs 1 bot)

| Parámetro | Valor nuevo | Lógica |
|---|---|---|
| Bots | **1** | Solo un oponente |
| Bot focus | **30** | Distraído, comete más errores |
| Entrada | 10 COR (sin cambio) | |
| **Win prize** | **18 COR** | Recalibrado |
| **Consolación** | **2 COR** | Sube ligeramente |

**Cálculo de house edge — datos reales del simulador** (`scripts/sim_cpu_balance.py`, 50 000 partidas):

| Focus jugador | Win rate real | EV jugador | House edge |
|---|---|---|---|
| 0 (sin habilidad) | 35.9% | 7.03 COR | **+29.7%** ✅ |
| 30 (novato) | 47.7% | 8.68 COR | **+13.2%** ✅ |
| 50 (promedio) | 55.4% | 9.76 COR | **+2.4%** ✅ |
| 70 (veterano) | 62.1% | 10.69 COR | **-6.9%** ⚠️ |
| 100 (experto máx) | 71.0% | 11.94 COR | **-19.4%** ⚠️ |

> **Por qué está bien aceptar esto:** El focus=70+ requiere mucha inversión en stats del axolotito (AXG gastados). La ventaja del experto es el **retorno de esa inversión**, no un exploit. El energy system (10 partidas por sleep cycle) pone un techo de ~19.4 COR de ganancia diaria para el jugador óptimo — manejable. La sala Rookie tiene stakes bajos (entrada de solo 10 COR); el riesgo absoluto para la economía es bajo.

**Rookie FINAL implementado:**
- Bots: 1, `focus=40`
- Entrada: 10 COR
- Win prize: **16 COR** (neto: +6)
- Consolación: **2 COR** (neto: -8)

#### Champion → 1v5 (jugador vs 5 bots)

| Parámetro | Valor nuevo | Lógica |
|---|---|---|
| Bots | **5** | Tablero de lotería completo casi, muy difícil |
| Bot focus | **80** | Muy atentos, pocas misses |
| Entrada | 50 COR (sin cambio) | |
| **Win prize** | **290 COR** | Recalibrado |
| **Consolación** | **5 COR** (sin cambio) | |

**Cálculo de house edge — datos reales del simulador:**

| Focus jugador | Win rate real | EV jugador | House edge |
|---|---|---|---|
| 0 (sin habilidad) | 6.5% | 23.45 COR | **+53.1%** ✅ |
| 30 (novato) | 10.0% | 33.44 COR | **+33.1%** ✅ |
| 50 (promedio) | 12.9% | 41.71 COR | **+16.6%** ✅ |
| 70 (veterano) | 16.0% | 50.71 COR | **-1.4%** ⚠️ |
| 100 (experto máx) | 21.8% | 67.09 COR | **-34.2%** ⚠️ |

El focus=70+ pierde para la casa en ambas salas. Esto es **diseño intencional**: el jugador top es recompensado por su progresión. Para el jugador con focus=100, el Champion ofrece retorno positivo, pero requiere haber invertido significativamente en su axolotito.

**Narrativa mejorada:**
- Rookie: "Demuéstrale a UN adversario que eres mejor"
- Champion: "Supera a CINCO bots expertos — si lo logras, el botín es enorme"

---

### 10.6 ✅ PROPUESTA — Sala intermedia "La Laguna" (opcional)

Para jugadores que quieren algo entre Rookie y Champion:

| Parámetro | Valor |
|---|---|
| Bots | 3, `focus=60` |
| Entrada | 25 COR |
| Win prize | 80 COR (neto +55) |
| Consolación | 3 COR (neto -22) |
| Win rate estimado (focus=50) | ~22% |
| House edge (focus=50) | `0.22×80 + 0.78×3 = 17.6+2.34 = 19.94` → 0.06/25 = **0.2%** |

Esta sala tiene house edge casi cero — solo viable con alto volumen de partidas. **No implementar hasta tener base de jugadores activos.**

---

### 10.7 ✅ PROPUESTA — Luck: "Lucky Save" (salvavidas dramático)

#### El problema con Luck hoy

La fórmula actual es:
```
prize_bonus = (stat_luck / 1000) × prize_gal   →   max +10% del premio
```

Con luck=100 en Rookie: +1.6 COR extra sobre 16 COR. El jugador nunca *siente* la suerte — es solo un decimal invisible al final. La stat no cumple su promesa narrativa.

#### La solución: dos efectos de Luck

**Efecto 1 (existente):** Bonus de premio al ganar. Se mantiene igual.

**Efecto 2 (nuevo) — Lucky Save:**

> Cuando un bot está a punto de ganar (el backend detecta que la carta recién cantada completa la línea ganadora de un bot), existe una pequeña probabilidad de que ese bot "se distraiga" y falle ese marcado. El juego continúa un turno más, dando al jugador otra oportunidad.

```python
# backend/app/api/v1/endpoints/game.py
# En el loop de animación, justo cuando se detecta que un bot completaría línea:

lucky_save_chance = (axo.stat_luck / 1000.0) * 0.5  # max 5% con luck=100

if random.random() < lucky_save_chance:
    # El bot "pierde el marcado" de esa carta — mismo sistema que el miss del jugador
    # La carta se salta en el tablero del bot; el juego continúa
    result["lucky_save_occurred"] = True   # para animar en frontend
    # NO incrementar bot_matches ni disparar bot win
    # Continuar al siguiente tick normalmente
```

| stat_luck | Lucky Save % |
|---|---|
| 0 | 0% |
| 20 | 1% |
| 50 | 2.5% |
| 80 | 4% |
| 100 | **5%** |

#### ¿Cuándo se activa exactamente?

Solo una vez por partida (si ocurre, no se resetea para volver a activar). La condición es:
- El bot acaba de recibir la carta que sería su última para completar una línea
- **En ese preciso momento** se lanza el dado de Lucky Save
- Si sale: el bot "falla" esa carta, el juego continúa
- Si no sale: el bot gana normalmente

**Impacto narrativo:** El momento dramático clásico del juego de mesa — cuando ya creías que habías perdido y el adversario falla en el último segundo. La suerte de tu axolotito protegió la partida. 5% no es frecuente, pero cuando sucede **es memorable**.

#### Frontend: animar el evento

El backend retorna `lucky_save_occurred: true` en `SimResult`. En `CpuSimScreen.tsx`:

```tsx
// Cuando se detecta lucky_save_occurred durante la animación:
// 1. La celda del bot que "debería" haberse marcado destella en rojo y desaparece
// 2. Aparece overlay brief: "🍀 ¡Tu suerte intervino!"
// 3. El juego continúa la animación normalmente
```

**Impacto en house edge:** ~+1.5% en el win rate del jugador (raro pero real). Aceptable — el jugador que lo construyó invirtió en su axolotito.

---

### 10.8 ✅ PROPUESTA — Wisdom: "Enfoque Inteligente"

#### Por qué el diseño anterior estaba mal

La primera versión de esta propuesta planteaba un "hint" de línea para el jugador. **Eso no tiene sentido** porque el axolotito juega *completamente automático* — el jugador no toma decisiones durante la partida. No hay botón "enfocarme en esta línea".

La mecánica correcta actúa sobre el **comportamiento interno del axolotito**, no sobre el jugador.

#### El problema real: misses desperdiciados

Con Focus=50 (15% miss rate), el axolotito falla 1 de cada ~7 cartas que caen en su tablero. Pero falla al **azar sin ninguna inteligencia** — puede fallar:
- Una carta de la línea que está a punto de completar (costosísimo)
- Una carta aislada que no contribuye a ninguna línea en progreso (irrelevante)

Ambos fallos cuentan igual en el modelo actual. Un axolotito Wise debería ser menos propenso a fallar cuando *más importa*.

#### La mecánica: misses selectivos por línea prioritaria

Al inicio de cada tick (carta cantada), el backend identifica cuál línea del tablero del jugador está **más avanzada** (más celdas ya marcadas de 4). Esa es la "línea prioritaria".

```python
# backend/app/api/v1/endpoints/game.py

def get_priority_line(matched_indices: list[int]) -> list[int]:
    """Devuelve la línea con más celdas marcadas. En empate: la primera."""
    best_line = []
    best_count = 0
    for line in WINNING_LINES:
        count = sum(1 for i in line if i in matched_indices)
        if count > best_count:
            best_count = count
            best_line = line
    return best_line

# En el loop de cada carta cantada:
priority_line = get_priority_line(player_matches)

# Calcular miss chance efectivo para esta celda:
if cell_index in priority_line:
    # El axolotito "sabe" que esta celda importa — aplica extra atención
    effective_miss = miss_chance * (1.0 - axo.stat_wisdom / 100.0)
else:
    effective_miss = miss_chance  # sin cambio para celdas no prioritarias
```

#### Tabla de efecto por Wisdom

Con Focus=50 (miss_base = 15%):

| stat_wisdom | Miss en línea prioritaria | Miss en otras celdas |
|---|---|---|
| 0 | 15% (sin cambio) | 15% |
| 25 | 11.25% | 15% |
| 50 | 7.5% | 15% |
| 75 | 3.75% | 15% |
| 100 | **0%** (nunca falla la línea ganadora) | 15% |

**Conclusión práctica:** Con Wisdom=100, el axolotito *nunca* falla cuando está a punto de ganar. Sus misses "se acumulan" en cartas que no importan para el resultado. Con Wisdom=0, todos los misses son igual de aleatorios.

#### ¿Cómo "sabe" el axolotito qué línea tiene más probabilidad?

No necesita predecir el futuro. Solo observa el presente:

> **La línea con más celdas ya marcadas es la más avanzada.** Si Row 1 tiene 3/4 marcadas, solo falta UNA carta más. Si la Diagonal tiene 1/4 marcadas, faltan TRES. Matemáticamente, Row 1 es la apuesta más cercana.

Esta es información completamente disponible en cada turno (estado actual del tablero), no requiere conocer las cartas futuras. El axolotito "lee" su propio tablero en cada turno.

#### ¿Cuándo importa Wisdom?

Solo importa cuando Focus es medio-bajo (40-70 range). Con Focus=90+ el jugador casi nunca falla de todas formas y Wisdom no agrega nada. El sweet spot es:

- **Focus bajo + Wisdom alto** → Los pocos misses que ocurren son en celdas irrelevantes (build viable para jugadores que priorizan Wisdom sobre Focus)
- **Focus alto + Wisdom bajo** → Misses raros pero aleatorios (puede perder el match por un miss en la línea prioritaria)
- **Focus alto + Wisdom alto** → El build ideal, pero cuesta más mejorar dos stats

Esto crea diversidad de builds, que es buen diseño.

#### Frontend: visualizar la "atención" del axolotito

En `CpuSimScreen.tsx`, las celdas de la línea prioritaria se resaltan con un borde tenue que pulsa lentamente. El jugador puede *ver* en cuál línea su axolotito está "concentrado" en cada momento. Cuando la carta de esa línea cae, la animación es más intensa (el axolotito la marca con vigor). Cuando la cae una carta de otra línea, la animación es normal.

```tsx
// LoteriaBoard recibe prop adicional: priorityLine?: number[]
// Celdas de priorityLine: borde animado color amber + subtle glow
// Al marcarse: animación más fuerte que las celdas normales
```

El backend retorna en `SimResult`:
```python
"wisdom_priority_lines": [  # historial de qué línea fue prioritaria en cada turno
    {"turn": 0, "line": [0,1,2,3], "wisdom_applied": 0.75},
    {"turn": 1, "line": [0,1,2,3], "wisdom_applied": 0.75},
    ...
]
```

O más simple para empezar: solo retornar la línea prioritaria del turno en que el jugador marcó/falló cada celda, junto con un flag `wisdom_saved: bool` si Wisdom previno un miss.

---

### 10.9 ✅ PROPUESTA — CPU Win Streak Bonus

Para que el botón "▶ JUGAR OTRA VEZ" (ya implementado en v2.1) tenga consecuencias emocionantes:

#### La mecánica

Cada axolotito lleva un contador `cpu_win_streak` que se incrementa con cada victoria CPU consecutiva y se resetea a 0 en la primera derrota.

```
Streak 0 → Premio normal (sin bonus)
Streak 1 → Premio normal (se "activa" la racha, pero aún no hay bonus)
Streak 2 → Premio ×1.15  (+15%)
Streak 3 → Premio ×1.30  (+30%)
Streak 4+ → Premio ×1.50 (+50%, cap)
```

```python
# backend/app/api/v1/endpoints/game.py
# Después de calcular prize_gal base:

streak = axo.cpu_win_streak  # leer antes de actualizar
if resultado == "victoria":
    axo.cpu_win_streak = streak + 1
    if streak >= 1:  # el bonus aplica DESDE la segunda victoria consecutiva
        streak_bonus = min(0.50, streak * 0.15)
        prize_gal = round(prize_gal * (1 + streak_bonus), 2)
        result["streak_bonus_pct"] = int(streak_bonus * 100)
else:
    axo.cpu_win_streak = 0  # derrota rompe la racha
    result["streak_bonus_pct"] = 0
    result["streak_broken"] = streak > 0  # para animar "racha rota" en frontend

result["win_streak_after"] = axo.cpu_win_streak
```

#### ¿Por qué funciona psicológicamente?

- **Después de una victoria**: "Si gano otra vez, el siguiente premio tiene bonus. Juego otra vez."
- **Con racha activa**: "Ya llevo 3 seguidas, el +30% es demasiado bueno para no intentarlo."
- **Al perder**: La racha se rompe con un momento de drama. El jugador quiere recuperarla.

Crea el loop perfecto para el "Jugar Otra Vez" in-place que ya implementamos.

#### ¿Afecta el house edge?

Sí, pero mínimamente (~+3-5% en EV). Solo afecta partidas donde el jugador ya ganó antes. El jugador con Focus bajo (pierde frecuente) raramente llega a Streak 2+. Aceptable.

#### Frontend (`CpuSimScreen.tsx`)

- **Fase `loading`** (antes de iniciar): Si `axo.cpu_win_streak >= 1`, badge animado "🔥 Racha ×{N} — +{bonus}% al premio si ganas"
- **Resultado victoria**: "🔥 ¡RACHA ×{N}!" con animación de llama si hay `streak_bonus_pct > 0`. El COR ganado muestra el bonus destacado (ej: "16 COR + 4.8 COR bonus 🔥")
- **Resultado derrota con racha rota**: "💔 Racha rota" con animación de extinción de llama

---

### 10.10 ✅ PROPUESTA — Panel "Tus Stats" en BoardSelectScreen

Antes de confirmar la partida CPU, un panel compacto muestra al jugador exactamente qué aporta cada stat de su axolotito:

#### Por qué incluirlo

1. **Transparencia** — El jugador sabe para qué sirven sus stats. Sin caja negra.
2. **Motivación de progresión** — Ver "Precisión: 85%" vs "Precisión: 94%" hace que subir Focus sea un objetivo concreto.
3. **Evita frustración** — El jugador que pierde entiende sus odds de entrada; no se siente estafado.

#### Implementación en `BoardSelectScreen.tsx`

Cálculo 100% frontend, sin API call. Solo visible en modo CPU, debajo del room selector:

```tsx
const missRate  = Math.max(0, Math.min(30, (100 - axo.stat_focus) * 0.3));
const accuracy  = (100 - missRate).toFixed(1);
const luckBonus = ((axo.stat_luck  / 1000) * 100).toFixed(1);
const wisdomOn  = axo.stat_wisdom >= 50;
const streak    = axo.cpu_win_streak ?? 0;
const streakBonus = streak >= 1 ? Math.min(50, streak * 15) : 0;

<div className="bg-slate-950/60 rounded-2xl p-3 border border-slate-800/80 space-y-1.5">
  <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">
    Stats para esta batalla
  </p>
  <Row label={`🎯 Precisión (Focus ${axo.stat_focus})`}
       value={`${accuracy}%`}
       color={Number(accuracy) >= 90 ? 'emerald' : 'amber'} />
  <Row label={`🍀 Bonus COR al ganar (Luck ${axo.stat_luck})`}
       value={`+${luckBonus}%`}
       color="amber" />
  {wisdomOn && (
    <Row label={`📖 Enfoque inteligente (Wisdom ${axo.stat_wisdom})`}
         value="✓ activo"
         color="indigo" />
  )}
  {streakBonus > 0 && (
    <div className="border-t border-slate-800/60 pt-1.5">
      <Row label={`🔥 Bonus de racha ×${streak}`}
           value={`+${streakBonus}% al premio`}
           color="orange" />
    </div>
  )}
</div>
```

---

### 10.11 ✅ PROPUESTA — Multiplayer: timing dinámico de sala

#### El problema actual

La sala arranca cuando `elapsed >= 30s OR boards >= 30`. Con comunidad pequeña, puede arrancar con 1 humano + 3 bots. Consecuencia: prize pool mínimo, experiencia pobre.

#### La solución: esperar más cuando hay pocos jugadores

```python
# backend/app/services/multiplayer_service.py

def should_start_room(total_boards: int, elapsed_seconds: float) -> bool:
    """
    Escala el tiempo de espera inversamente al número de boards.
    Menos boards = más espera para atraer más jugadores humanos reales.
    """
    if total_boards >= 30: return True   # sala llena → arrancar inmediatamente
    if total_boards >= 21: return elapsed_seconds >= 15
    if total_boards >= 11: return elapsed_seconds >= 20
    if total_boards >=  6: return elapsed_seconds >= 25
    if total_boards >=  3: return elapsed_seconds >= 35
    return elapsed_seconds >= 60   # 1-2 boards: esperar hasta 1 minuto
```

#### Impacto

- Comunidad pequeña: Jugador espera hasta 60s en lugar de 30s. A cambio, mayor probabilidad de jugar con humanos → prize pool más grande → mejor experiencia → retención.
- Comunidad grande (10+ boards frecuentes): Comportamiento casi igual al actual.

**Frontend** (`SalaSelectScreen.tsx`): El countdown "La sala sale pronto" ya existe. Solo necesita recibir el `start_at` real del servidor en lugar de usar un timer local.

---

### 10.12 Tabla resumen de propuestas

| # | Propuesta | Impacto | Prioridad | Responsable |
|---|---|---|---|---|
| 10.5 | Bot count variable + rebalance premios | 🔴 Crítico — casa pierde dinero hoy | **P0** | backend-dev |
| 10.7 | Luck "Lucky Save" — drama en el último turno | 🟡 Narrativo + ligero balance | **P2** | backend-dev + frontend-dev |
| 10.8 | Wisdom "Enfoque Inteligente" — misses selectivos | 🟡 Progresión + builds diversos | **P2** | backend-dev + frontend-dev |
| 10.9 | CPU Win Streak — bonus en racha | 🟢 Engagement loop + incentiva play again | **P2** | backend-dev + frontend-dev |
| 10.10 | Panel "Tus Stats" en BoardSelectScreen | 🟢 UX + transparencia + motivación | **P3** | frontend-dev |
| 10.11 | Multiplayer timing dinámico | 🟢 Retención en early stage | **P3** | backend-dev |
| 10.6 | Sala "La Laguna" (intermedia) | 🔵 Expansión futura | **P4** | backend-dev |

---

### 10.13 Checklists de implementación

#### P0 — Balance crítico CPU `backend-dev` ✅ IMPLEMENTADO

> Prioridad máxima. El modo CPU actualmente pierde dinero para la casa con jugadores de Focus medio-alto.

- [x] `backend/app/api/v1/endpoints/game.py`: Diccionario `ROOM_CONFIG` al inicio del archivo con todas las constantes de sala
- [x] `game.py`: Todos los valores hardcodeados de fee, prize, consolation, bot config vienen de `ROOM_CONFIG[room_name]`
- [x] `game.py`: Loop de bots genera `bot_count` instancias (1 Rookie, 5 Champion)
- [x] `game.py`: Bots tienen su propia `bot_miss_chance` derivada de `bot_focus` (misma fórmula que el jugador)
  - Rookie bots: `focus=40` → miss ≈ 18 % (careless)
  - Champion bots: `focus=80` → miss ≈ 6 % (sharp but not perfect)
- [x] `game.py`: Respuesta incluye `bot_count`, `bot_focus`, `player_miss_chance_pct` para el frontend
- [x] `game.py`: Premios rebalanceados — Rookie: fee=10/prize=16/consolation=2, Champion: fee=50/prize=290/consolation=5
- [x] **Test estadístico**: `backend/scripts/sim_cpu_balance.py` — simula 50,000 partidas por sala y reporta win rate real + EV de casa. Ejecutado y resultados documentados en 10.5.

#### P0 — Frontend: comunicar el cambio al jugador `frontend-dev` ✅ IMPLEMENTADO

- [x] `BoardSelectScreen.tsx`: Room cards muestran badge de oponentes ("⚔️ 1v1 · 1 bot" / "⚔️ 1v5 · 5 bots") y el premio ganador (+16 / +290 COR)
- [ ] `CpuSimScreen.tsx`: Para Champion, mostrar las 5 tablas CPU (actualmente solo hay 1). Las 4 extras pueden ser versiones más pequeñas/opacas al fondo, creando la sensación visual de "estás rodeado".
  - Layout sugerido: 1 tabla central grande (el bot más adelantado) + 4 tablitas en fila arriba, opacas

---

#### P2 — Lucky Save `backend-dev` + `frontend-dev` ✅ IMPLEMENTADO

**Backend `game.py`:**
- [x] Añadir función helper `_lucky_save(axo_luck, already_used)` — max 5% chance a luck=100, una sola vez por partida
- [x] En el loop principal de la partida, justo cuando se detecta que un bot completó línea: pasar por `_lucky_save` antes de declarar victoria del bot. Si se activa: continuar al siguiente turno, registrar `lucky_save_turn = turns`
- [x] Respuesta incluye `lucky_save_occurred: bool` y `lucky_save_turn: int | None`

**Frontend `CpuSimScreen.tsx`:**
- [x] `SimResult` interface: campos `lucky_save_occurred` y `lucky_save_turn`
- [x] Estado `showLuckySave` + detección en tick cuando `idx === lucky_save_turn`
- [x] Overlay flotante "🍀 ¡Suerte de {axo.name}!" durante 1.6s con animación fade-in
- [x] Panel de resultado: badge "🍀 Lucky Save activado" con turno exacto si `lucky_save_occurred === true`

> Nota: la animación de "destello rojo en celda del bot" queda pendiente (requiere rastrear qué celda específica habría marcado el bot — actualmente las boards del bot son ilustrativas, no exactas). Se puede implementar en un follow-up si se decide sincronizar boards reales del backend.

---

#### P2 — Win Streak `backend-dev` + `frontend-dev` ✅ IMPLEMENTADO

**Backend modelo `axolotito.py`:**
- [x] Añadir campo: `cpu_win_streak: int = Field(default=0)` — después de `loyalty_points`
- [x] Migración Alembic `39d71ef65317_add_cpu_win_streak_to_axolotito.py` — aplicada (`alembic upgrade head`)
- [x] Guardia de startup en `main.py`: ALTER TABLE inline como fallback si Alembic no se corre

**Backend `game.py`:**
- [x] Leer `streak = axo.cpu_win_streak` antes del bloque win/loss
- [x] Victoria: `axo.cpu_win_streak = streak + 1`; `streak_bonus_pct = min(50, streak * 15)` si `streak >= 1`; bonus multiplicado sobre `prize_awarded` antes de añadir a wallet
- [x] Derrota: `axo.cpu_win_streak = 0`; `streak_broken = streak >= 1`
- [x] Respuesta incluye `win_streak_after`, `streak_bonus_pct`, `streak_broken`; ledger description con nota de racha

**Frontend `AxoSelectScreen.tsx`:**
- [x] Card expandido: badge "🔥 Racha ×N" si `cpu_win_streak >= 1`; muestra bonus próximo (+X%) si racha >= 2

**Frontend `CpuSimScreen.tsx`:**
- [x] `SimResult` interface: campos `win_streak_after`, `streak_bonus_pct`, `streak_broken`
- [x] Fase `loading`: banner ámbar "🔥 Racha ×N activa — Gana y obtendrás +X% COR extra"
- [x] Fase `result` / victoria con bonus: desglose Base / Bonus racha / Total
- [x] Fase `result` / derrota con racha rota: bloque "💔 Racha rota — Racha de N victorias terminada"

---

#### P2 — Wisdom "Enfoque Inteligente" `backend-dev` + `frontend-dev` ✅ IMPLEMENTADO

**Backend `game.py`:**
- [x] Helper `_get_priority_line(matched: set) -> set` — retorna la línea con más celdas ya marcadas
- [x] En el loop de marcado del jugador: `effective_miss = player_miss_chance * (1 - stat_wisdom/100)` si la celda está en la línea prioritaria; sin cambio si no
- [x] Conteo exacto de `wisdom_saves`: rol que pasó `effective_miss` pero habría fallado con `player_miss_chance` completo
- [x] `SimResult`: campo `wisdom_saves: int` (simplificado — el frontend calcula su propia priority line localmente)

**Frontend `LoteriaBoard.tsx`:**
- [x] Prop `priorityLine?: number[]` con default `[]`
- [x] Celda no marcada en priority line: borde ámbar `border-amber-500/40` + shadow hint
- [x] Celda marcada en priority line: glow verde intensificado + `ring-1 ring-emerald-400/20`

**Frontend `CpuSimScreen.tsx`:**
- [x] Helper `calcPriorityLine(matched)` a nivel de módulo (mismo algoritmo que backend)
- [x] Estado `priorityLine` recalculado en cada tick tras cualquier cambio en el tablero del jugador
- [x] `priorityLine` pasado al `<LoteriaBoard>` del jugador
- [x] Panel resultado: badge "📖 Wisdom activo — evitó N error{es} en tu línea prioritaria" si `wisdom_saves > 0`

---

#### P3 — Panel "Tus Stats" en BoardSelectScreen `frontend-dev` ✅ IMPLEMENTADO

- [x] `BoardSelectScreen.tsx`: Sub-componente `CpuStatsPanel` + constante `ROOM_DATA` antes del export principal
- [x] Calcula: `accuracy` (de `stat_focus`), `luckBonusPct` (de `stat_luck`), Wisdom activo/inactivo (de `stat_wisdom`), racha + bonus (de `cpu_win_streak`)
- [x] Sin API call — todo computable en frontend con las mismas fórmulas que `game.py`
- [x] Mobile: colapsable via toggle ▼▲; `sm+`: siempre visible (`sm:block`). Guard `selectedAxo &&` para no renderizar sin axo seleccionado

---

#### P3 — Multiplayer timing dinámico `backend-dev` ✅ IMPLEMENTADO

- [x] `multiplayer_service.py`: helpers `_max_wait_seconds(total_boards)` y `should_start_room(total_boards, elapsed_seconds)` — tabla escalonada: ≥30→0s, ≥21→15s, ≥11→20s, ≥6→25s, ≥3→35s, 1-2→60s
- [x] Condición inline `should_start` reemplazada por llamada a `should_start_room(total_tables, elapsed_seconds)`
- [x] Endpoint `/lobby`: campo `"seconds_until_start"` en cada sala (`max(0, max_wait - elapsed)`)
- [x] `MultiplayerLobby.tsx`: texto dinámico "⏱ Inicia en ~{N}s · o al llegar a 30 tablas" (reemplaza hardcoded "30s")

---

#### P4 — Sala "La Laguna" (cuando haya comunidad activa)

- [ ] Añadir entrada en `ROOM_CONFIG`: `'laguna': {bot_count: 3, bot_focus: 60, fee: 25.0, prize: 80.0, consolation: 3.0, ...}`
- [ ] Frontend: tercera tarjeta en room selector de BoardSelectScreen
- [ ] Solo activar cuando la base de jugadores justifique el volumen (house edge ~0.2% requiere muchas partidas para ser rentable)

---

### 10.14 Nota sobre builds de axolotito (estrategia de stats)

La combinación de mecánicas crea builds viables distintos, lo que hace el Criadero/Santuario más interesante:

| Build | Foco en | Efecto en CPU mode |
|---|---|---|
| **Precision** | Focus alto, Wisdom bajo | Casi nunca falla, pero cuando lo hace puede ser en la línea clave |
| **Strategic** | Focus medio, Wisdom alto | Falla poco en la línea prioritaria; más errores en celdas irrelevantes |
| **Lucky** | Luck alto, Focus medio | Lucky Save activo; bonus de premio; misses ocasionales |
| **Endurance** | Stamina alto | Más partidas por sesión antes de necesitar dormir |
| **Speedrun** | Agility alto | Recupera energía más rápido → más sesiones por día |
| **Balanced** | Stats distribuidos | Sin ventaja específica pero sin debilidad notable |

Estos builds emergen de forma orgánica de las mecánicas — no hace falta diseñarlos explícitamente. Solo comunicarlos en el Santuario/Criadero con tooltips que expliquen qué hace cada stat en el juego.

El simulador CPU (Fase 6) es el ítem más complejo y el que más valor visual aporta. Si hay restricción de tiempo, Fases 0–5 + P0 de Fase 10 dan un juego completamente funcional y económicamente sostenible.
