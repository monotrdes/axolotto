# VIP Club — Auditoría de Diseño y Propuesta de Rediseño del Panel

> Análisis del panel VIP CLUB (`components/VipModal.tsx` + `VipChip` en `app/play/page.tsx`).
> Enfoque: **mobile-first**, claridad, poder informativo, fuerza de invitación y **eliminación de redundancia**.
> Fecha: 2026-06-03

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
|---|---|
| **Componentes revisados** | 2 (`VipChip`, `VipModal` con 3 estados) |
| **Problemas encontrados** | 17 |
| **Score actual** | **62 / 100** |
| **Mayor fortaleza** | El dashboard (Modo B) es rico y el sistema de acordeón de upgrade es elegante |
| **Mayor debilidad** | Redundancia de beneficios (se listan hasta 3 veces) + el argumento de venta más fuerte (ROI positivo) **no se comunica** |

**Veredicto:** El panel es funcional y visualmente atractivo, pero **muestra de más** (repite beneficios, mezcla dos sistemas de tarjetas) y al mismo tiempo **dice de menos** en lo que importa para convertir: no explica que la membresía *se paga sola*, no muestra el marco cosmético antes de comprar, y no usa prueba social. En móvil, el Modo Ventas obliga a un scroll largo con 3 tarjetas siempre expandidas.

---

## 2. Estructura Actual (Mapa)

```
VipChip (barra superior, siempre visible)
 ├─ Sin VIP  → chip "👑 VIP ›" con shimmer
 └─ VIP      → "🪸 Coral · 28d"  /  "✨ Dorado · 80 FRJ" (si hay claim)  /  rojo si ≤5d

VipModal (max-w-lg, max-h-92vh, scroll vertical)
 ├─ Header sticky: 👑 VIP CLUB + badge de tier
 │
 ├─ MODO A — VENTAS (no VIP)
 │   ├─ Hero: 👑 "Únete a la élite"
 │   ├─ Banner "🎁 Bono de bienvenida" → +FRJ por tier (emoji + cifra)
 │   ├─ 3 tarjetas de tier APILADAS (todas expandidas, todos los beneficios)
 │   │     └─ cada una repite "+X FRJ al activar"
 │   └─ Footer: nota legal (días se apilan / slots se congelan)
 │
 ├─ MODO ÉXITO → 🎉 confirmación
 │
 └─ MODO B — DASHBOARD (VIP activo)
     ├─ Axolotito Principal + marco
     ├─ Suscripción: vence + días + barra progreso + racha
     ├─ Claim diario de FRJ
     ├─ "Tus beneficios activos" (grid completo)        ← (1)
     ├─ Auto-renovación (toggle)
     ├─ Historial de tiers
     └─ Acordeón "Subir de nivel / Renovar"
           └─ fila de renovación del tier actual
                 └─ repite stats + beneficios completos  ← (2) = duplica (1)
```

---

## 3. Hallazgos por Categoría

### 3.1 Redundancia — *lo que el usuario pidió eliminar* 🔴 PRIORIDAD

| # | Dónde | Qué se repite | Impacto |
|---|---|---|---|
| R1 | Modo A | El banner "Bono de bienvenida" lista `+X FRJ` por tier, **y** cada tarjeta vuelve a decir "+X FRJ al activar" | El usuario lee la misma cifra dos veces antes de llegar al botón |
| R2 | Modo B | "Tus beneficios activos" lista TODO el tier, **y** al expandir la fila *Renovar [tier actual]* del acordeón se listan otra vez los mismos stats + beneficios | Duplicación literal del bloque más pesado |
| R3 | Código | La lógica de "construir lista de beneficios" (`gal_daily`, `discount`, `formatCapsulas`, `p2p`, `extra`) está escrita **3 veces** (Modo A, Modo B activo, Modo B upgrade) | Riesgo de drift; ya hay inconsistencias de iconos |
| R4 | Modo A vs B | Dos renderizadores distintos para la **misma** fila de beneficio: Modo A usa `<Zap>`, Modo B usa emoji (🪙🏷️🎁🔄) | Inconsistencia visual del mismo dato |

**Recomendación:** un único componente `<BenefitRow>` y un único `getTierBenefits(tier)`. La fila *Renovar tier actual* del acordeón no debe re-listar beneficios — basta "Renovar 30 días · {precio} AXF".

### 3.2 Poder de Invitación / Conversión (Modo A) 🔴 PRIORIDAD

| # | Problema | Por qué importa |
|---|---|---|
| C1 | **No se comunica el ROI positivo.** La filosofía del sistema (doc §1) es que "el ROI en moneda sola ya es positivo". El UI nunca dice "recuperas más FRJ de lo que pagas". | Es el argumento de venta #1 y está ausente. Anclar valor: *"+1,200 FRJ/mes ≈ X AXF de valor por 400 AXF"*. |
| C2 | **El marco cosmético del Axolotito no se teasea.** Solo se ve en Modo B (ya comprado). | El estatus visible es emocional; el comprador no ve qué desbloquea. |
| C3 | **Sin prueba social.** El doc pedía "342 jugadores VIP activos 🔥". No está. | Reduce fricción de decisión. |
| C4 | **"P2P 3%", "Comisión P2P" sin contexto.** Un jugador nuevo no sabe qué es P2P ni su valor. | Beneficio invisible para no-iniciados. |
| C5 | **Recompensas de lealtad/racha invisibles en venta.** Badge Constante, marco Veterano, etc. (doc §9) son ganchos de retención fuertes y no aparecen. | Se vende solo el mes 1, no la relación a largo plazo. |

### 3.3 Mobile-First 🟠

| # | Problema | Detalle |
|---|---|---|
| M1 | **Modo A = scroll muy largo.** 3 tarjetas siempre expandidas con todos los beneficios (Axolite tiene 9). | No hay comparación lado a lado ni colapso. Contradice el patrón de acordeón que sí existe en Modo B. |
| M2 | **Tipografías por debajo del mínimo legible.** `text-[9px]`, `text-[10px]`, `text-[11px]` en abundancia. | 9-11px es difícil de leer en móvil; mínimo recomendado 12px (`text-xs`) para texto secundario. |
| M3 | **Targets táctiles pequeños.** Toggle auto-renovación 44×**24**px, botón cerrar ≈28px, chevrons 16px. | Mínimo accesible 44×44px (WCAG 2.5.5). |
| M4 | **Inconsistencia de flujo de compra.** Modo A = doble tap (Unirme → Confirmar). Modo B = tap único en CTA del acordeón. | Dos modelos mentales para la misma acción. |

### 3.4 Jerarquía y Claridad 🟠

| # | Problema |
|---|---|
| H1 | En Modo B, el **claim diario** (la razón #1 para abrir el modal a diario) compite con 6 bloques estáticos. Debería ser el elemento más prominente, arriba. |
| H2 | El bloque "Suscripción activa" y la "barra de progreso" cuentan lo mismo (días restantes) con dos representaciones; aceptable, pero el número `28d` aparece 2 veces muy cerca. |
| H3 | Terminología mezclada: el código usa **"Cápsula"**, el doc usa **"Gashapón"**. El usuario ve un nombre, el diseño otro. |
| H4 | El badge "Badge de Lealtad" se menciona como texto inline sin explicar qué es ni mostrar el roadmap de hitos (3/6/12/24 meses). |

### 3.5 Consistencia de Tokens / Código 🟡

| # | Problema |
|---|---|
| T1 | **Datos duplicados del backend.** `TIERS[]` está hardcodeado en el componente y duplica `VIP_CONFIG` de `config.py`. **Ya hay drift:** el doc dice 100/250/500 AXG, el componente cobra 400/600/1800 AXF. Single source of truth (endpoint o constante compartida). |
| T2 | **Opacidades por concatenación de string** (`tier.color + "22"`, `"33"`, `"44"`, `"66"`) repartidas por todo el archivo. Sin escala de tokens. |
| T3 | **Radios de borde ad hoc:** `rounded-2xl / xl / lg / full` sin criterio claro de elevación. |
| T4 | **Copys de CTA inconsistentes:** "Unirme a Coral" / "Confirmar — 400 AXF" / "Activar Coral VIP" / "Renovar Coral" para acciones equivalentes. |

---

## 4. Propuestas de Rediseño

### 4.1 Modo A (Ventas) — De "muro de beneficios" a "decisión guiada"

**Antes:** 3 tarjetas apiladas, todo expandido, beneficios repetidos.

**Propuesta — estructura mobile-first:**

```
┌─────────────────────────────────┐
│ 👑 VIP CLUB                  [x] │
├─────────────────────────────────┤
│  El club se paga solo.          │  ← hook de valor (ROI), no "élite"
│  Recuperas más FRJ de los       │
│  que inviertes cada mes.        │
│                                 │
│  [ Axolotito con marco Dorado ] │  ← TEASE del cosmético (C2)
│   "Tu axolotito luce tu rango"  │
│                                 │
│  🔥 342 VIP activos ahora       │  ← prueba social (C3)
│                                 │
│  ── Selector de nivel ──        │
│  [ 🪸 Coral ][✨ Dorado★][🌟 ]  │  ← TABS / segmented control
│                                 │
│  ┌───────────────────────────┐  │  ← UNA tarjeta a la vez
│  │ ✨ DORADO        600 AXF/m │  │
│  │ ───────────────────────── │  │
│  │ 💰 +3,000 FRJ/mes         │  │
│  │    ≈ 750 AXF de valor     │  │  ← anclaje de ROI (C1)
│  │ 🎁 +500 FRJ de bienvenida │  │  ← bono UNA sola vez (R1)
│  │ 🏷️ 12% descuento tienda   │  │
│  │ 🔄 Comisión P2P 3% ⓘ      │  │  ← tooltip explica P2P (C4)
│  │ ✦ +1 slot de tabla        │  │
│  │ ✦ 1 Booster/mes           │  │
│  │                           │  │
│  │   [ Unirme — 600 AXF ]    │  │
│  └───────────────────────────┘  │
│                                 │
│  🔒 Sube de racha y desbloquea  │  ← teaser de lealtad (C5)
│     marcos exclusivos →         │
│                                 │
│  Días se apilan · slots se      │
│  congelan, no se pierden        │
└─────────────────────────────────┘
```

**Beneficios del cambio:**
- **Una tarjeta visible a la vez** vía segmented control → móvil deja de ser un scroll infinito (M1) y permite comparar cambiando de tab.
- El bono de bienvenida aparece **una sola vez**, dentro de la tarjeta activa (elimina R1, quita el banner superior).
- Hueco para el **anclaje de ROI** (C1) y el **tease del marco** (C2).
- "Dorado" preseleccionado por defecto (es el POPULAR) → reduce parálisis de decisión.

### 4.2 Modo B (Dashboard) — Quitar la duplicación, subir el claim

**Reordenar por frecuencia de uso:**

```
1. Claim diario de FRJ          ← #1, arriba, prominente (H1)
2. Axolotito + marco + tier
3. Suscripción (días + barra)    ← fusionar el "28d" duplicado (H2)
4. Beneficios activos            ← ÚNICA vez (fuente: getTierBenefits)
5. Racha + roadmap de hitos      ← mostrar 3/6/12/24 con progreso (H4)
6. Auto-renovación
7. Subir de nivel                ← SOLO tiers superiores; sin fila "renovar=duplicado" (R2)
8. Historial (colapsable)
```

**Cambio clave (R2):** El acordeón "Subir de nivel" lista **solo upgrades reales**. La acción de *renovar el tier actual* se vuelve un botón secundario simple dentro del bloque de Suscripción ("Renovar 30 días · 600 AXF"), **sin** re-listar beneficios que ya están en "Beneficios activos".

### 4.3 Sistema — Componentes y fuente única

| Acción | Detalle |
|---|---|
| `getTierBenefits(tierId)` | Una función que devuelve la lista canónica de beneficios (icono + label). La usan Modo A, B y upgrade. Mata R3. |
| `<BenefitRow icon label />` | Un solo renderizador. Mata R4 (no más Zap vs emoji). |
| `<TierBadge tier size />` | Reutilizable en chip, header, historial. |
| **Fuente de datos** | Mover `TIERS[]` a un endpoint (`GET /shop/vip/tiers`) o constante compartida que refleje `VIP_CONFIG`. Mata T1 y el drift de precios. |
| Tokens | Definir `--vip-coral / --vip-dorado / --vip-axolite` y una escala de opacidad (`/10 /20 /40` de Tailwind) en vez de concatenar `"22"`. |

---

## 5. Quick Wins (alto impacto, bajo esfuerzo)

| Prioridad | Cambio | Esfuerzo |
|---|---|---|
| 1 | Eliminar el banner de bienvenida superior en Modo A (queda dentro de cada tarjeta) → mata R1 | XS |
| 2 | En el acordeón de Modo B, la fila "Renovar tier actual" no re-lista beneficios → mata R2 | S |
| 3 | Añadir línea de **anclaje de ROI** en cada tarjeta ("≈ X AXF de valor") → C1 | S |
| 4 | Subir las tipografías `text-[9/10/11px]` a mínimo `text-xs` (12px) → M2 | S |
| 5 | Agrandar toggle y botón cerrar a 44px de área táctil → M3 | XS |
| 6 | Extraer `getTierBenefits()` + `<BenefitRow>` → mata R3/R4 | M |
| 7 | Unificar copys de CTA ("Activar {tier} — {precio} AXF" en todos lados) → T4 | XS |

---

## 6. Mejoras de Mediano Plazo

1. **Segmented control de tiers en Modo A** (4.1) — el cambio estructural de mayor impacto en conversión móvil.
2. **Tease del marco cosmético** en Modo A renderizando un axolotito de ejemplo con el `vip-frame-*` correspondiente al tab activo.
3. **Roadmap de racha visual** en Modo B: `●─●─●─○─○` con etiquetas de hito (Constante 3m / Veterano 6m / Original 12m).
4. **Prueba social en vivo** — exponer un contador de VIPs activos desde backend (`GET /shop/vip/stats`).
5. **Tooltips contextuales** (ⓘ) en beneficios "jerga" (P2P, jackpot, slots) para jugadores nuevos.
6. **Fuente única de tiers** desde backend para matar el drift de precios (T1).

---

## 7. Checklist de Implementación

> **Estado revisado contra codebase: 2026-06-04**

```
Redundancia
[x] R1 — quitar banner bienvenida superior (Modo A) — bono dentro de TierCard
[x] R2 — fila "renovar actual" sin re-listar beneficios — renovar = botón simple en sección 3 de ModeB
[x] R3 — getTierBenefits() único — lib/vip.ts, usado por ModeA/ModeB/UpgradePanel/TierCard
[x] R4 — <BenefitRow> único — components/vip/BenefitRow.tsx con tooltip

Conversión (Modo A)
[x] C1 — línea de anclaje de ROI por tier — calcRoiAxf() en lib/vip.ts, renderizado en TierCard
[x] C2 — tease del marco cosmético — vip-frame-{selectedTierId} en ModeA
[x] C3 — contador de prueba social — fetchVipStats() + "🔥 N VIP activos ahora" en ModeA
[x] C4 — tooltips para P2P / jackpot / slots — tooltip field en getTierBenefits(), renderizado en BenefitRow
[x] C5 — teaser de recompensas de racha — sección al pie de ModeA con hitos 3/6/12/24m

Mobile
[x] M1 — segmented control (una tarjeta a la vez) — ModeA con tabs Coral/Dorado★/Axolite
[x] M2 — tipografía mínima text-xs — text-[10px] eliminado de TierCard (badge ★) y
         StreakRoadmap (labels de hito). Resto del modal limpio.
[x] M3 — targets táctiles ≥44px — min-h-[44px] en todos los CTAs; toggle min-w-[44px] min-h-[44px];
         botón cerrar w-11 h-11; botón ⓘ en BenefitRow ahora min-w/h 44px.
[x] M4 — flujo de compra unificado — HoldButton en TierCard (Modo A), renovar (Modo B)
         y UpgradePanel. confirmTier eliminado del hook y todos los componentes.

Jerarquía / tokens
[x] H1 — claim diario arriba en Modo B — sección 1 en ModeB (primera antes de todo)
[x] H2 — fusionar "28d" duplicado — daysRemaining aparece una sola vez en JSX
[x] H3 — unificar "Cápsula" vs "Gashapón" — lib/vip.ts usa "Gashapon" consistentemente
[x] H4 — roadmap de hitos de racha — StreakRoadmap.tsx (3/6/12/24 meses con hitos visuales)
[x] T1 — fuente única de tiers (backend) — TIERS[] eliminado; GET /shop/vip/tiers + /vip/stats
[x] T4 — copys de CTA unificados — "Activar {tier} — {precio} AXF" / "Confirmar — {precio} AXF"
```

### Pendientes menores

- **calcRoiAxf TODO** en `lib/vip.ts`: tasa 4 FRJ/AXF hardcodeada
  → exponer `frj_per_axf` desde el endpoint de precios cuando exista; mientras, documentado en config

### Mejoras adicionales propuestas (post-implementación)

1. **Prueba social en 0**: Si `active_vip_count === 0` (sistema nuevo), el contador se oculta
   correctamente. Considerar fallback "Sé de los primeros" para motivar early adopters.
2. **Verificar que `vip-frame-{tier}` CSS existe** en el global stylesheet. El tease del marco
   en ModeA aplica la clase pero si el CSS no está definido para esos IDs el efecto es invisible.
3. **T2 (concatenación de opacidades)** — `color + "22/33/44/66"` sigue presente en TierCard y
   UpgradePanel. Reemplazar por variantes Tailwind (`/10 /20 /40`) o CSS vars
   `--vip-coral-alpha` cuando haya tiempo; no es bloqueante.
4. **E2E Playwright** (Tarea E del plan) — no hay evidencia de que se ejecutaron los tests
   automatizados de ModeA/ModeB. Añadir al pipeline de CI.

---

## 8. Apéndice — Inventario de Tokens Detectados

| Categoría | Definidos | Hardcodeados encontrados |
|---|---|---|
| Colores de tier | 3 (en `TIERS[]`) | Centralizados ✅ pero con `+"22/33/44/66"` por concatenación |
| Colores neutros | 0 tokens | `#0A0A1A`, `#6B7280`, `rgba(255,255,255,0.x)` repetidos |
| Tipografía | escala Tailwind | abundan tamaños arbitrarios `text-[9/10/11px]` |
| Radios | — | `rounded-2xl/xl/lg/full` sin criterio de elevación |
| Sombras/glow | `tier.glow` | mezcla de `boxShadow` inline |

> **Decisión tomada (2026-06-03):** se adopta **FRJ (Frijolitos) / AXF (Axofichas)** con precios **400 / 600 / 1800** — que es exactamente lo que ya vive en `backend/app/core/config.py → VIP_CONFIG` (`price_axg` 400/600/1800, `gal_daily` 40/100/200). Las claves internas del backend conservan los nombres legacy `price_axg` / `gal_daily` / `welcome_gal`, pero **representan AXF / FRJ**; renombrarlas es un refactor aparte fuera de este alcance. La UI mostrará siempre FRJ/AXF.
>
> **El array `TIERS[]` hardcodeado en `VipModal.tsx` queda eliminado** y se reemplaza por datos servidos desde backend (ver §9).

---

## 9. Plan de Implementación — Modo A + Fuente Única (Multiagente)

> Alcance acordado: (1) rediseño del **Modo A** (§4.1), (2) **eliminar `TIERS[]` hardcodeado** y servir los valores económicos desde backend, (3) quick wins de redundancia R1–R4.

### 9.1 Estrategia de paralelización

Tres agentes especializados. El **contrato de API (§9.2)** se fija primero para que `backend-dev` y `frontend-dev` trabajen **en paralelo** sin bloquearse (el frontend desarrolla contra el contrato; integra al final).

```
            ┌─ Tarea A (backend-dev) ── GET /shop/vip/tiers ─┐
contrato ──►│                                                ├─► Tarea E (qa-tester)
  §9.2      └─ Tarea B (frontend-dev) ─ lib/vip + Modo A ────┘     E2E + verificación
                         │
                         └─ Tarea C depende de B (Modo B refactor)
```

| Agente | Tareas | Paralelizable |
|---|---|---|
| `backend-dev` | A | ✅ con B |
| `frontend-dev` | B → C | B ∥ A; C tras B |
| `qa-tester` | E | tras A+B |

> Nota: A y B son independientes gracias al contrato. C (refactor Modo B) depende de B porque reutiliza `lib/vip`. No spawnear agentes hasta confirmar este plan.

### 9.2 Contrato de API (fijar antes de empezar)

**`GET /shop/vip/tiers`** — público (sin auth, como `/shop/items`). Lee de `VIP_CONFIG` y devuelve, en orden coral → dorado → axolite:

```json
[
  {
    "id": "coral",
    "price_axf": 400,
    "frj_daily": 40,
    "frj_monthly": 1200,
    "discount": 0.05,
    "capsulas_mensuales": { "bronce": 2 },
    "p2p_commission": 0.04,
    "table_bonus_slots": 0,
    "axolotito_bonus_slots": 0,
    "jackpot_bonus": 0.0,
    "multiplayer_discount": 0.0,
    "welcome_frj": 200,
    "welcome_boosters": [],
    "popular": false
  }
]
```

**Reglas del contrato:**
- El backend **traduce** las claves legacy: `price_axg → price_axf`, `gal_daily → frj_daily`, `welcome_gal → welcome_frj`. `frj_monthly = frj_daily * 30`.
- `popular` es un campo nuevo en `VIP_CONFIG` (`dorado: true`, resto `false`).
- **Solo datos económicos.** Nada de colores/emoji/copy: eso vive en el frontend (`lib/vip.ts`).
- Orden garantizado por nivel (coral, dorado, axolite).

**`GET /shop/vip/stats`** — público, para prueba social (C3):

```json
{ "active_vip_count": 342 }
```

- `active_vip_count` = nº de usuarios con `is_vip == true` (membresía no expirada). Query: `User` donde `vip_expires_at > now()`.

### 9.3 Tarea A — Backend: endpoint de tiers (`backend-dev`)

```
[ ] A1 — Añadir "popular": true/false a cada tier en VIP_CONFIG (config.py)
[ ] A2 — Crear ShopService.get_vip_tiers() → mapea VIP_CONFIG a la forma del contrato §9.2
         (traduce price_axg→price_axf, gal_daily→frj_daily, welcome_gal→welcome_frj,
          calcula frj_monthly, ordena coral→dorado→axolite)
[ ] A3 — Endpoint GET /shop/vip/tiers en endpoints/shop.py (público, sin auth)
[ ] A4 — Test unitario: tiers presentes, claves traducidas, orden, frj_monthly correcto,
         popular solo en dorado (tests/unit/test_vip_system.py)
[ ] A5 — Verificar: curl localhost:8000/shop/vip/tiers devuelve los 3 tiers
[ ] A6 — Endpoint GET /shop/vip/stats → { active_vip_count } (count User con
         vip_expires_at > now()). Público. Test incluido. [C3]
```
**Archivos:** `core/config.py`, `services/shop_service.py`, `api/v1/endpoints/shop.py`, `tests/unit/test_vip_system.py`.

### 9.4 Tarea B — Frontend: capa única + Modo A (`frontend-dev`)

```
B — Fuente única (lib/vip.ts)
[ ] B1 — Tipo VipTier (forma del contrato §9.2) + fetchVipTiers() contra GET /shop/vip/tiers
[ ] B2 — Mapa de presentación VIP_PRESENTATION[id] = { emoji, color, glow, gradient, perks[] }
         (perks[] = copys NO numéricos: "Acceso anticipado 24h", "Nombre dorado en rankings"…)
[ ] B3 — getTierBenefits(tier): construye la lista canónica de beneficios desde los NÚMEROS
         del backend + perks de presentación. Mata R3.
[ ] B4 — <BenefitRow icon label /> y <TierBadge> únicos. Mata R4.
[ ] B5 — Hook/estado en VipModal: cargar tiers al abrir; loading/skeleton; fallback de error
[ ] B6 — ELIMINAR el array TIERS[] hardcodeado de VipModal.tsx

B — Rediseño Modo A (§4.1)
[ ] B7  — Hook de venta con valor: "El club se paga solo" (sustituye "élite")
[ ] B8  — Segmented control de tiers (Coral / Dorado★ / Axolite), Dorado preseleccionado [M1]
[ ] B9  — UNA tarjeta visible a la vez, con beneficios vía getTierBenefits [M1, R3]
[ ] B10 — Línea de anclaje de ROI por tier: "+X FRJ/mes ≈ Y AXF de valor" [C1]
[ ] B11 — Bono de bienvenida UNA sola vez dentro de la tarjeta; quitar banner superior [R1]
[ ] B12 — Tease del marco: axolotito de ejemplo con vip-frame-{tab activo} [C2]
[ ] B13 — Tooltip ⓘ en beneficios jerga (P2P, jackpot, slots) [C4]
[ ] B14 — Teaser de recompensas de racha (link/sección colapsada) [C5]
[ ] B15 — Tipografías mínimas a text-xs; targets táctiles ≥44px (toggle, cerrar) [M2, M3]
[ ] B16 — CTA unificado: "Activar {tier} — {precio} AXF" [T4]
[ ] B17 — Contador de prueba social: fetch GET /shop/vip/stats → "🔥 {n} VIP activos
         ahora" en el Modo A. Ocultar si falla o n==0. [C3]
```
**Archivos:** `lib/vip.ts` (nuevo), `components/VipModal.tsx`, `app/play/page.tsx` (VipChip puede consumir `VIP_PRESENTATION`).

### 9.5 Tarea C — Frontend: refactor Modo B (`frontend-dev`, tras B)

```
[ ] C1 — Modo B consume getTierBenefits() (sin re-implementar la lista)
[ ] C2 — Fila "Renovar tier actual" del acordeón NO re-lista beneficios;
         renovación pasa a botón simple en el bloque Suscripción [R2]
[ ] C3 — Claim diario reubicado arriba [H1]; fusionar "28d" duplicado [H2]
[ ] C4 — Unificar "Cápsula" vs "Gashapón" en copy [H3]
[ ] C5 — Roadmap de hitos de racha (3/6/12/24) [H4]
```
**Archivos:** `components/VipModal.tsx`.

### 9.6 Tarea E — QA y verificación (`qa-tester`, tras A+B)

```
[ ] E1 — Test API: GET /shop/vip/tiers responde 200 con los 3 tiers (contrato §9.2)
[ ] E2 — E2E Playwright: abrir modal sin VIP → segmented control cambia tarjeta;
         precios = 400/600/1800; bono aparece UNA vez; ROI visible
[ ] E3 — E2E: targets táctiles ≥44px; sin tipografías <12px en textos clave
[ ] E4 — Regresión: flujo de compra y claim siguen funcionando (Modo B)
[ ] E5 — Verificar que NO queda ningún precio/valor hardcodeado en VipModal.tsx
```

### 9.7 Decisiones tomadas

- **C3 (prueba social):** ✅ **incluida ahora** — endpoint `GET /shop/vip/stats` (A6) + wiring en Modo A (B17).
- **`perks[]` no numéricos** ("Acceso anticipado 24h", "Nombre dorado"): viven en frontend como copy. Si en el futuro se quieren togglear desde backend, se añadirían a `VIP_CONFIG`. Por ahora, frontend.

### 9.8 Orden de ejecución

1. Fijar contrato §9.2 (este documento). 
2. Spawnear en paralelo: `backend-dev` (Tarea A) ∥ `frontend-dev` (Tareas B + C).
3. Integrar (frontend apunta al endpoint real) → `qa-tester` (Tarea E).
4. `verification-before-completion` antes de declarar terminado.

---

## 10. Comandos de Invocación Multiagente

> Prompts listos para `Agent`. A y B se lanzan **en el mismo mensaje** (paralelos). E corre al final.

### 10.1 `backend-dev` — Tarea A (en paralelo con B)

```
subagent_type: backend-dev
description: "VIP tiers + stats endpoints"
prompt:
  Implementa dos endpoints públicos en el shop router del backend de Axolotto.
  Fuente de verdad: backend/app/core/config.py → VIP_CONFIG (NO lo dupliques).

  1) Añade "popular": <bool> a cada tier en VIP_CONFIG (dorado=true, coral/axolite=false).
  2) ShopService.get_vip_tiers() en services/shop_service.py: mapea VIP_CONFIG al contrato,
     traduciendo claves legacy: price_axg→price_axf, gal_daily→frj_daily, welcome_gal→welcome_frj,
     y calculando frj_monthly = frj_daily*30. Devuelve lista ordenada coral→dorado→axolite con:
     id, price_axf, frj_daily, frj_monthly, discount, capsulas_mensuales, p2p_commission,
     table_bonus_slots, axolotito_bonus_slots, jackpot_bonus, multiplayer_discount,
     welcome_frj, welcome_boosters, popular.
  3) GET /shop/vip/tiers (público, sin auth, como /shop/items) en api/v1/endpoints/shop.py.
  4) GET /shop/vip/stats (público) → { "active_vip_count": <int> } contando User con
     vip_expires_at > now() (usa la misma noción de "is_vip activo" que el resto del código).
  5) Tests en tests/unit/test_vip_system.py: contrato correcto, claves traducidas, orden,
     frj_monthly, popular solo en dorado, y stats cuenta solo VIPs no expirados.
  Verifica con los tests y reporta el JSON exacto que devuelve cada endpoint.
```

### 10.2 `frontend-dev` — Tareas B + C (en paralelo con A)

```
subagent_type: frontend-dev
description: "VIP Modo A redesign + fuente única"
prompt:
  Reescribe el panel VIP (components/VipModal.tsx) de Axolotto. Lee primero
  docs/vip_club_panel_auditoria.md §4.1, §9.2, §9.4 y §9.5. IMPORTANTE: esta versión
  de Next.js tiene cambios — consulta node_modules/next/dist/docs/ antes de escribir.

  CONTRATO de datos (el backend lo expone en paralelo; desarrolla contra esto):
    GET /shop/vip/tiers → array coral→dorado→axolite de objetos:
      { id, price_axf, frj_daily, frj_monthly, discount, capsulas_mensuales,
        p2p_commission, table_bonus_slots, axolotito_bonus_slots, jackpot_bonus,
        multiplayer_discount, welcome_frj, welcome_boosters, popular }
    GET /shop/vip/stats → { active_vip_count }

  TAREA B — fuente única:
    - Crea lib/vip.ts: tipo VipTier, fetchVipTiers(), fetchVipStats(),
      VIP_PRESENTATION[id] = { emoji, color, glow, gradient, perks[] } (copys NO numéricos),
      getTierBenefits(tier) que construye la lista de beneficios desde los NÚMEROS del backend,
      y componentes <BenefitRow> y <TierBadge> reutilizables.
    - ELIMINA el array TIERS[] hardcodeado de VipModal.tsx; carga tiers desde el endpoint
      al abrir (con skeleton de carga y fallback de error).
  TAREA B — Modo A (rediseño §4.1, mobile-first):
    - Hook de valor "El club se paga solo" (no "élite").
    - Segmented control de tiers (Dorado preseleccionado por ser popular); UNA tarjeta a la vez.
    - Anclaje de ROI: "+X FRJ/mes ≈ Y AXF de valor".
    - Bono de bienvenida UNA sola vez dentro de la tarjeta (elimina el banner superior duplicado).
    - Tease del marco: axolotito de ejemplo con la clase vip-frame-{tab activo}.
    - Tooltips ⓘ en P2P/jackpot/slots. Prueba social desde /shop/vip/stats ("🔥 N VIP activos").
    - Tipografías mínimo text-xs (12px); targets táctiles ≥44px (toggle, botón cerrar).
    - CTA unificado: "Activar {tier} — {precio} AXF".
  TAREA C — Modo B (refactor, reutiliza lib/vip):
    - Consume getTierBenefits() (no reimplementes la lista).
    - La fila "Renovar tier actual" del acordeón NO re-lista beneficios; mueve renovar a un botón
      simple en el bloque Suscripción.
    - Claim diario arriba; fusiona el "28d" duplicado; unifica copy "Cápsula"/"Gashapón";
      roadmap de hitos de racha (3/6/12/24).

  Moneda en UI: SIEMPRE FRJ (Frijolitos) / AXF (Axofichas). Precios 400/600/1800 vienen del
  backend, nunca hardcodeados. No rompas el flujo de compra/claim existente.
```

### 10.3 `qa-tester` — Tarea E (tras A + B)

```
subagent_type: qa-tester
description: "VIP panel E2E + verificación"
prompt:
  Verifica el rediseño del panel VIP de Axolotto (ver docs/vip_club_panel_auditoria.md §9.6).
  1) GET /shop/vip/tiers y /shop/vip/stats responden 200 con el contrato §9.2.
  2) E2E Playwright: abrir modal sin VIP → el segmented control cambia la tarjeta; precios
     mostrados = 400/600/1800; el bono de bienvenida aparece UNA sola vez; el ROI es visible;
     la prueba social aparece.
  3) Comprueba targets táctiles ≥44px y que no haya tipografías <12px en textos clave.
  4) Regresión: flujo de compra VIP y claim diario (Modo B) siguen funcionando.
  5) Grep en components/VipModal.tsx: que NO quede ningún precio/valor económico hardcodeado
     (sin array TIERS[], sin 400/600/1800 literales).
  Reporta fallos con archivo:línea.
```
