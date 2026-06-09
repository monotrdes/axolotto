# El Nido — Diseño Cenote Subacuático 2.5D

## Concepto Central

**El Nido** es un cenote mexicano habitado por Axolotitos. El jugador lo ve desde adentro, como si estuviera dentro del agua, mirando hacia el fondo donde hay cuevitas (los nidos de incubación). Los axolotitos ya eclosionados nadan libremente en la columna de agua. La luz viene de arriba, filtrándose en rayos danzantes.

Los axolotes mexicanos (*Ambystoma mexicanum*) viven naturalmente en cenotes y lagos subterráneos. Este escenario honra eso.

---

## Arquitectura de capas

```
┌─────────────────────────────────────────────────────┐  ← superficie (luz)
│  ≈≈≈ rayos de luz bailando ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈  │  z-1
│  ○    ○    burbujas subiendo    ○    ○    ○          │  z-3
│                                                     │
│    🦎(pequeño, profundo)   🦎(mediano)              │  z-50–70
│          🦎(grande, cerca)                          │
│                                                     │
│  ▓▓▓  🥚  ▓▓▓▓▓▓▓  🥚  ▓▓▓▓▓▓▓  🥚  ▓▓▓           │  z-20 (back, 0.72x)
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓       │  z-10 (far rocks)
│  🥚      ▓▓▓  🥚    ▓▓▓    🥚       ▓▓▓   🥚       │  z-40 (front, 1.0x)
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ FONDO DE PIEDRA ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  z-30
└─────────────────────────────────────────────────────┘
```

---

## Paleta de colores

| Elemento | Color |
|----------|-------|
| Agua profunda | `#020C16 → #080F1A` (gradiente fondo) |
| Paredes cueva | `#1E1008 → #0A0501` (marrón oscuro) |
| Luz de superficie | `rgba(45,212,191, 0.12)` (teal claro) |
| Bioluminiscencia | `rgba(0,255,150, 0.4)` (verde-cyan) |
| Calor de nido | `rgba(251,146,60, 0.25+)` (naranja cálido) |
| Glow axolotito | `rgba(228,0,124, 0.25)` (rosa Axolotto) |
| Escarcha | `rgba(6,182,212, 0.5)` (cyan frío) |
| Roca del fondo | `#2D1A08 → #1A0D04` (marrón oscuro) |

---

## Dimensiones del canvas

- **Mobile portrait** (base): `h-[340px]`, `w-full`
- **Desktop** (`sm:` 640px+): `h-[500px]`
- **Overflow**: `hidden` — todo cabe en pantalla, sin scroll horizontal

---

## Nidos (NidoCave)

Cada cave slot dibuja:

1. **Glow halo** detrás del arco — cambia según estado
2. **Arco de cueva** — `borderRadius: '50% 50% 8px 8px / 68% 68% 8px 8px'`
   - Dark gradient interior con `box-shadow: inset`
   - Border de 1.5px según estado
3. **Contenido**:
   - `egg`: emoji 🥚/🐣 con drop-shadow + barra de calor en el fondo
   - `empty`: 🪺 tenue + hint visual
4. **Roca base**: div absoluto debajo del arco
5. **Badge flotante**: chip encima de la cueva (¡Listo! / ❄️ PAUSADO)

### Estados del nido

| Estado | Border | Glow |
|--------|--------|------|
| Normal (calor >70%) | amber/orange | cálido naranja |
| Normal (calor <70%) | marrón sutil | mínimo |
| Congelado | cyan | azul frío |
| Listo | pink | rosa pulsante |
| Escudo | amber dorado | dorado suave |
| Vacío | casi invisible | ninguno |

### Posicionamiento

Back nidos (scale 0.72, transformOrigin: bottom center):
- Left: `9%`, `39%`, `70%` — Bottom: `44%`, `49%`, `44%`

Front nidos (scale 1.0):
- Left: `2%`, `26%`, `50%`, `73%` — Bottom: `4%`

---

## Axolotitos — Sprites Libres

Cada axolotito eclosionado nada libremente en la columna de agua (sin slot fijo).

**Posición inicial** (calculada en `useEffect`, guardada en ref para SSR safety):
```tsx
{
  left:     12 + random() * 68,   // % del ancho
  bottom:   26 + random() * 36,   // % del alto (zona media)
  depth:    0.3 + random() * 0.7, // 0=fondo, 1=superficie
  duration: 8 + random() * 8,     // duración ciclo swim (s)
  delay:    random() * 5,          // delay inicio (s)
  driftX:   ±(18 + random() * 30), // amplitud horizontal (px)
}
```

**Depth → visual**:
- `scale`: `size = 40 + depth * 24` px (40–64px)
- `opacity`: `0.55 + depth * 0.45` (0.55–1.0)
- `zIndex`: `50 + round(depth * 15)` (50–65)

**Animación CSS única por axolotito** (inyectada via `<style>`):
```css
@keyframes axo-swim-{id} {
  0%   { transform: translateX(0)      translateY(0)    scaleX(1);  }
  25%  { transform: translateX(dx*0.4) translateY(-7px) scaleX(1);  }
  50%  { transform: translateX(dx)     translateY(-12px) scaleX(sign); }
  75%  { transform: translateX(dx*0.4) translateY(-5px)  scaleX(-1); }
  100% { transform: translateX(0)      translateY(0)    scaleX(1);  }
}
```

**Estados visuales**:
| Status | Ícono flotante |
|--------|----------------|
| `sleeping` | 💤 (-top-4) |
| `expedition` | 🧭 (-top-4) |
| `resting` / `idle` | ninguno |

**Interacción**:
- Hover → border ring rosa `#E4007C/60` + nombre en tooltip debajo
- Click → pausa animación (`animation: none`) + abre AxoSheet

**Drop shadow especial**:
- `stat_luck > 99`: `drop-shadow(0 0 8px rgba(6,182,212,0.6))` (aura legendary)
- `stat_luck > 80`: `drop-shadow(0 0 6px rgba(245,158,11,0.5))` (alta suerte)

---

## Mecánica de Congelamiento (Fases Progresivas)

```
CALOR 100–50%  ✅ Sano      → glow naranja cálido, timer corre normal
CALOR 49–25%   ⚠️ Frío      → glow apagado, vaho visual, timer normal
CALOR 24–10%   🧊 Helándose → border cyan tenue, timer lento (backend)
CALOR <10%     ❄️ CONGELADO  → is_frozen = true, timer pausado
```

### Estado CONGELADO — UI

- Badge `❄️ ⏸` sobre el nido en escena
- Header del panel: `❄️ CONGELADO · TIMER PAUSADO`
- Tiempo: `"⏸️ PAUSADO"` en vez de horas restantes
- Barra: `frozen_clicks_left / MAX_CLICKS` de progreso
- Botón principal: "Romper escarcha (N clicks)"
- Cuidados (acariciar/cantar): deshabilitados mientras está congelado

### Descongelamiento

Jugador tap el huevo → cada tap reduce `frozen_clicks_left` en 1 (optimistic UI, sync cada 3s).
Ítem "Lámpara Infrarroja Pro" → descongela instantáneamente vía API.

---

## Acciones de Cuidado (WebitoPanel)

Solo 2 acciones (sin alimentar):

| Acción | Emoji | Cooldown | Bonifica |
|--------|-------|----------|---------|
| Acariciar | 💖 | 4h | STR + AGI |
| Cantar | 🎵 | 8h | WIS + FOC |

---

## CSS Keyframes adicionales (inline `<style>`)

```css
@keyframes cenote-bubble-rise {
  0%   { opacity: 0.4; transform: translateY(0)     scale(1);   }
  60%  { opacity: 0.6; }
  100% { opacity: 0;   transform: translateY(-310px) scale(0.4); }
}
@keyframes ray-flicker {
  0%,100% { opacity: 0.04; }
  50%     { opacity: 0.11; }
}
@keyframes shimmer-heat {
  0%,100% { opacity: 0.04; }
  50%     { opacity: 0.10; }
}
@keyframes golden-float {
  0%   { opacity: 0; transform: translateY(0);    }
  20%  { opacity: 0.6; }
  100% { opacity: 0; transform: translateY(-70px); }
}
@keyframes axo-swim-{id}  { /* único por axolotito */ }
```

(El resto — `sheet-up`, `animate-float-up`, `egg-frozen`, `axo-bob` — vienen de `globals.css`)

---

## Mejoras vs versión anterior

| Feature | Antes | Nuevo |
|---------|-------|-------|
| Ambiente | Grid plano con orbs | Cenote 2.5D, 6 capas CSS |
| Axolotitos | Celdas estáticas | Sprites nadando libremente |
| Perspectiva | 2 rows con scale | Scale + opacity continua por depth |
| Interacción huevo | Solo en panel | Click directo en escena + panel |
| Feedback directo | n/a | Tap = calor, sin abrir panel |
| Freeze visual | Badge texto | Glow cyan + badge + counter en cueva |
| Clima | Widget expandible | Overlay visual en canvas (escarcha/calor) |
| Axolotitos en nido | Fijo en slot | Solo eggs en nidos, axos libres |
| Acciones webito | 2 ya (sin alimentar) | 2 confirmado |

---

## Notas Técnicas

- **No new deps** — CSS puro + SVG inline. Sin librerías de animación.
- **SSR safe** — Posiciones de axolotitos calculadas en `useEffect`, no en render.
- **Performance** — Sprites usan `will-change: transform` implícito. Máx. 7 keyframe únicos por axolotito.
- **Accesibilidad** — Caves con `role="button"` + `aria-label`. `tabIndex={0}` + `onKeyDown`.
- **Props idénticas** — `{ userId, token, cambiarTab? }` sin cambios.
- **Backend intacto** — Todos los endpoints idénticos.
