# 🎮 Axolotto — Plan de Mejora Game UX
> Objetivo: convertir la app de "web app con skin de juego" a "juego que también tiene web app"  
> Metodología: una fase a la vez, verificar antes de avanzar, marcar checks al completar

---

## Reglas del plan
- No avanzar a la siguiente fase hasta verificar la actual
- Cada tarea tiene criterio de aceptación explícito
- Los cambios de UI se verifican visualmente en móvil (375px) y desktop (1280px)
- TypeScript debe compilar sin errores (`tsc --noEmit`) antes de marcar cualquier tarea

---

## FASE 1 — Fundación: componentes compartidos
> Sin esto el resto del plan genera más inconsistencia. Hacerlo primero.

### 1.1 Componente `<LoteriaCard>` universal

- [x] Extraer el componente `LoteriaCard` de `BoardEditor.tsx` a `components/ui/LoteriaCard.tsx`
  - Mantener: LOTERIA_EMOJI map, RARITY_RING map, colores generativos por número, holo-overlay para shiny/legendaria
  - Agregar prop `size` con valores predefinidos: `'xxs'` (18px) · `'xs'` (28px) · `'sm'` (44px) · `'md'` (60px) · `'lg'` (80px) — también acepta número directo para compatibilidad con BoardEditor
  - Agregar prop `interactive?: boolean` para hover/scale effects (onMouseEnter/Leave)
- [x] Actualizar `BoardEditor.tsx` para importar desde la nueva ruta (sin cambios visuales)
- [x] **Verificación:** `tsc --noEmit` limpio ✅

### 1.2 Componente `<BottomSheet>` unificado

- [x] Crear `components/ui/BottomSheet.tsx`
  - Props: `open`, `onClose`, `children`, `title?`, `accent?` (color string para el borde superior)
  - Estructura: backdrop `bg-black/40 backdrop-blur-sm` + panel `fixed bottom-0 animate-sheet-up max-h-[85dvh]` con handle bar
  - Usa `createPortal` hacia `document.body`
  - El panel es flex column: handle (shrink-0) + scrollable body (flex-1 min-h-0 overflow-y-auto scrollbar-hide)
- [x] Migrar los 2 drawers de `Store.tsx` (Sobres y Webitos) al nuevo componente
- [x] Migrar los 3 bottom sheets de `Santuario.tsx` (EggSheet, AxoSheet, empty-slot sheet) al nuevo componente
- [x] Migrar el board detail sheet de `Inventory.tsx` al nuevo componente
- [ ] **Verificación visual pendiente:** Abrir cada sheet en móvil — el contenido no desborda la pantalla · El handle es visible · El backdrop cierra al tap

### 1.3 Sistema de Toast (eliminar `alert()`)

- [x] Crear `context/ToastContext.tsx` (sistema unificado — ver nota de decisión abajo)
  - Variantes simples (top-center, auto-dismiss 4s): `'ok'` (verde) · `'error'` (rojo) · `'info'` (azul) · `'reward'` (dorado pulsante)
  - **Variantes ricas unificadas** (bottom corners, duración extendida): `'vip'` (tier color) · `'game'` (verde/rosa)
  - `createPortal` a `document.body`, guarded por `mounted` state
- [x] Proveer `ToastProvider` en `PrivyProviderWrapper.tsx` (cliente, no requiere cambios en layout.tsx)
- [x] Reemplazar todos los `alert(...)` de `Store.tsx` con `toast.error(...)` (3 instancias)
- [x] Reemplazar todos los `alert(...)` de `Inventory.tsx` con `toast.error(...)` (1 instancia)
- [x] Migrar `vipToasts` state + `addVipToast` de `page.tsx` → `toast.vip()`
- [x] Migrar `gameToasts` state + `setGameToasts` de `page.tsx` → `toast.game()`
- [x] **Verificación:** `tsc --noEmit` limpio ✅

---

## FASE 2 — Estandarización visual: carta y tabla

### 2.0 Componentes base (fundación para todo el resto)

- [x] Actualizar `LoteriaCard.tsx`:
  - Bordes completamente rectangulares (eliminado `rounded-[12%]`)
  - Nueva prop `isFirstEdition?: boolean` → badge ⭐ top-right con glow dorado
  - Prop `size` ya soporta `'xxs'` (18px) para chip
- [x] Crear `components/ui/BoardPreview.tsx`
  - Grid 4×4 de `LoteriaCard` con 3 tamaños: `'chip'`(xxs/gap-1) · `'sheet'`(xs/gap-1.5) · `'editor'`(sm/gap-2)
  - Slots vacíos: div dashed border proporcional
- [x] **Verificación:** `tsc --noEmit` limpio ✅

### 2.1 Grid de Cartas (Inventory mode='cartas')

- [x] Reemplazar el `div` con `🃏` placeholder por `<LoteriaCard size='sm' interactive isFirstEdition={hasFirstEdition} showQty={false} />`
- [x] Cartas no poseídas: `opacity-40 grayscale` en el wrapper externo (preservando tooltip/modal handlers)
- [x] **Verificación:** `tsc --noEmit` ✅ · Pendiente verificación visual

### 2.2 Mini-preview en Board Chip (grid compacto de tablas)

- [x] Reemplazar los dots `border rounded-[3px] gap-0.5` por `<BoardPreview size='chip' board={board} allCards={allCards} />`
- [x] **Verificación:** `tsc --noEmit` ✅ · Pendiente verificación visual

### 2.3 Grid 4×4 en Bottom Sheet de Tablas

- [x] Reemplazar grid inline del board detail sheet por `<BoardPreview size='sheet' board={selectedBoard} allCards={allCards} />`
- [x] **Verificación:** `tsc --noEmit` ✅ · Pendiente verificación visual

### 2.4 Unboxing summary (Store.tsx)

- [x] `<LoteriaCard size='lg' interactive isFirstEdition={isFirstEd} showQty={false} />` en estado summary
- [x] Animación de reveal (flip 3D) intacta — solo se tocó el path ya-reveladas/summary
- [x] Badges flotantes "Shiny / 1st Ed. Shiny / NUEVA" conservados como overlays externos
- [x] **Verificación:** `tsc --noEmit` ✅ · Pendiente verificación visual

---

## FASE 3 — Feedback y juice de recompensas

### 3.1 Flying rewards en el header

- [x] En `page.tsx`, detectar cuando `datosBanco.gemas_alga` (GAL) aumenta (comparar valor anterior con `useRef`)
- [x] Lanzar 3–5 instancias de un `FloatingReward` (`+X 🌿`) que salen del chip GAL con `animate-float-up`
- [x] Hacer lo mismo para `datosBanco.axogemas` (AXG) cuando aumenta
- [x] **Verificación:** Cobrar staking de una tabla → los floaters suben desde el chip GAL en el header · En AXG igual al hacer exchange

### 3.2 Celebración al cobrar staking (Tablas)

- [x] Al hacer click en "Cobrar" en el board detail sheet, antes de recargar: mostrar un toast variante `'reward'` con el monto: `🌿 +X.XX GAL`
- [x] **Verificación:** Cobrar con GAL pendiente → toast dorado visible · Luego el balance en header se actualiza con el floater de fase 3.1

### 3.3 Transición de sección (fade entre tabs)

- [x] En `page.tsx`, agregar `key={tabActiva}` al div wrapper de sección con `animate-in fade-in duration-200`
- [x] **Verificación:** `tsc --noEmit` limpio ✅ · Pendiente verificación visual

### 3.4 Reveal dramático al reclamar racha diaria

- [x] Al hacer click en "Reclamar Diaria", mostrar un mini overlay de 2s (centrado, fondo oscuro blur) con el premio (`dailyRewardResult`) antes de cerrar automáticamente
- [x] El overlay tiene la misma energía que un unboxing pequeño: emoji grande + nombre del reward + animación de entrada
- [x] **Verificación:** Reclamar racha → overlay aparece 2s con el premio → se cierra solo → toast reward confirma

---

## FASE 4 — Apertura de boosters desde Inventario

### 4.1 Detectar boosters sellados en mochila

- [x] En `Inventory.tsx`, al cargar el inventario filtrar items donde `item_type === 'booster'` y `quantity > 0`
- [x] Guardar en estado `sealedBoosters`

### 4.2 Sección "Pendiente de abrir" en modo Cartas

- [x] Si `sealedBoosters.length > 0`, mostrar un banner al tope del grid de cartas:
  - `📦 Tienes X sobre(s) sin abrir` con botón `Abrir`
  - Al tap, abrir un pequeño sheet listando los boosters con botón "Abrir ahora" por cada uno
- [x] El botón "Abrir ahora" llama a la API `/shop/booster/open` con el `inventory_item_id`

### 4.3 Compartir el UnboxingModal

- [x] Extraer el modal de unboxing completo de `Store.tsx` a `components/ui/UnboxingModal.tsx`
  - Props: `open`, `onClose`, `pack`, `cards` (resultado), `txHash`
  - Mantiene todos los estados internos: pack → opening → reveal → summary
  - Mantiene las partículas temáticas
- [x] `Store.tsx` usa `<UnboxingModal>` en lugar del JSX inline
- [x] `Inventory.tsx` usa `<UnboxingModal>` para abrir los boosters sellados
- [x] **Verificación:** Comprar booster en tienda → unboxing igual que antes · Abrir booster desde mochila → mismo unboxing cinematográfico

---

## FASE 5 — El Nido: ambiente vivo

### 5.1 Partículas de burbuja en habitat canvas

- [x] Activar la clase `animate-bubble` (ya definida en globals.css) en 4–6 divs pequeños distribuidos por el canvas del habitat
- [x] Las burbujas deben tener delays escalonados para que no suban sincronizadas
- [x] **Verificación:** El Nido → se ven burbujas pequeñas subiendo suavemente por el canvas

> ✅ 14 burbujas con `cenote-bubble` keyframe inline en `NidoScene`, posiciones y delays distribuidos

### 5.2 Aura de huevo según fase

- [x] En `NidoCave` y `EggSheet`, aplicar `--egg-shadow` como CSS var inline para color dinámico por tipo de huevo
- [x] Usar la clase `animate-egg-pulse` cuando el huevo está en fase 1 (incubación temprana) — keyframe corregido: `brightness()` movido a `filter`, usa `var(--egg-shadow)` para color dinámico
- [x] Usar `animate-egg-frozen` cuando está congelado
- [x] **Verificación:** Los huevos Génesis tienen aura dorada pulsante · Los huevos Fundador tienen aura púrpura

### 5.3 Partículas de corazón al dar cariño

- [x] Al hacer click en "Dar Cariño" (o tap en el huevo), lanzar 3 partículas de corazón `💕` con offsets escalonados (−28px, 0, +28px) usando el sistema `animate-float-up`
- [x] **Verificación:** Dar cariño a un huevo → 3 corazones suben desde el nido · El contador de clicks incrementa visualmente

---

## FASE 6 — Framing de lenguaje y micro-copy

### 6.1 Tablas: reemplazar lenguaje DeFi por lenguaje de lotería

- [x] `"Staking GAL"` ➔ `"🪙 Corcholatas acumuladas"` (Tapas)
- [x] `"Hourly Yield"` ➔ `"Generación/h"` or `"Ganancia/h"` (COR/h)
- [x] `"Win Rate"` ➔ `"Racha de Suerte"`
- [x] `"HUD strip: Slots X/Y"` ➔ `"Espacios X/Y"`
- [x] `"CSR"` no se muestra (ya se usa `suerte_tag` directamente — verificar que así sea)
- [x] **Verificación:** Recorrer tablas — ningún término financiero visible para el usuario final

### 6.2 Inventory Cartas: separadores por rareza y progreso de colección (OMITIDA / PENDIENTE DE RE-PLANEAR)

- [ ] Agrupar las 54 cartas por `dynamic_rarity`: Legendaria → Épica → Rara → Poco Común → Común
- [ ] Mostrar un separador entre grupos: `[⭐ LEGENDARIAS — 1/2]` con barra de progreso mini
- [ ] Al tener el 100% de una rareza, el separador tiene un glow celebratorio
- [ ] **Verificación:** Grid de cartas muestra grupos separados · El conteo por rareza es correcto · Secciones completas brillan

### 6.3 Ticker global de actividad (minimal)

- [x] Añadir una línea de ticker en el header (debajo del logo, encima del contenido) con actividad reciente: `🎉 @usuario obtuvo una Legendaria · 🍀 @usuario obtuvo ...`
- [x] Usar los datos de `capsuleFeed` de la API de Axolotto
- [x] Auto-scroll horizontal (`ticker-track` ya definido en globals.css)
- [x] Mostrar solo cuando hay datos; ocultar si el array está vacío
- [x] **Verificación:** El ticker se mueve suavemente · Se pausa al hover · No rompe el layout en móvil

---

## FASE 7 — Pulido final y QA completo

### 7.1 Revisión de estados disabled en todos los botones

- [ ] Recorrer cada botón que tenga `disabled` — verificar que visualmente se vea inactivo (opacity-40 mínimo) y no tenga cursor-pointer
- [ ] **Verificación:** Todos los botones disabled se ven claramente no clickeables

### 7.2 Revisión mobile completa (375px)

- [ ] Tienda: scroll, drawer de sobres, drawer de webitos, unboxing completo
- [ ] Cartas: grid responsive, tooltip (verificar que en móvil no aparece tooltip hover — usar tap-to-show si es necesario)
- [ ] Tablas: grid 2-col, bottom sheet board detail, BoardEditor tap-to-assign
- [ ] El Nido: habitat canvas, bottom sheets de huevo y axolotito
- [ ] **Verificación:** Ninguna sección requiere scroll horizontal · Ningún texto está cortado · Los botones son tap-friendly (mínimo 44px de área)

### 7.3 TypeScript final

- [ ] `tsc --noEmit` sin errores en todos los archivos modificados
- [ ] **Verificación:** Output limpio

### 7.4 Revisión de performance

- [ ] Verificar que el ticker y las partículas no causan janks (usar DevTools Performance en móvil)
- [ ] Las animaciones CSS usan `transform` y `opacity` (no `width`/`height`) — ya es el caso, confirmar
- [ ] **Verificación:** Scroll fluido en grids grandes (54 cartas) · Animaciones a 60fps en el habitat

---

## FASE 8 — Estandarización de Popups, Fichas de Gashapón y Simplificación de Axolotitos

### 8.1 Centrado Absoluto de Popups mediante React Portals
- [x] En `Store.tsx`, importar `createPortal` de `react-dom` y renderizar `dailyRewardResult` y `modalAdopcionAbierto` dentro de un portal al `document.body` para evitar el desplazamiento vertical por transforms de los contenedores padres.
- [x] En `Inventory.tsx`, envolver el modal de venta P2P (`showListModal`) y el modal de creación de tabla aleatoria (`showCreateModal`) en portales.
- [x] Unificar estilos de inputs, botones y bordes en los modales de creación y venta para darles identidad de videojuego (gradientes, glows y consistencia).

### 8.2 Acumulación y Uso de Fichas de Gashapón
- [ ] Cargar el inventario en `Gashapon.tsx` y contar las `"Ficha de Gashapón"` poseídas por el usuario.
- [ ] Mostrar un contador destacado `🎟️ Fichas: X` en el header de Gashapón.
- [ ] Implementar la máquina de Gashapón (Accesorios / Comida) con botones para tirar con GAL o usar una Ficha (gratis).
- [ ] Renderizar el resultado del Gashapón (`ResultOverlay`) como un popup flotante centrado con portal en lugar de sustituir toda la vista del componente.

### 8.3 Simplificación de Selección y Stats de Axolotitos (PlayMode)
- [x] En `PlayMode.tsx`, eliminar el estado de hover (`hoveredAxo`) y el portal de stats flotantes en hover/tap.
- [x] Eliminar el icono de info (`<Info />`) y el botón asociado.
- [x] Modificar el clic en la tarjeta de Axolotito para que alterne (toggle) su selección y despliegue inline las estadísticas correspondientes.

---

## Checklist de fases

| Fase | Descripción | Estado |
|---|---|---|
| Fase 1 | Fundación: LoteriaCard · BottomSheet · Toast | 🟢 Código listo — verificación visual pendiente |
| Fase 2 | Estandarización visual: carta y tabla | 🟢 Código listo — verificación visual pendiente |
| Fase 3 | Feedback y juice de recompensas | 🟢 Completado |
| Fase 4 | Apertura de boosters desde Inventario | 🟢 Completado |
| Fase 5 | El Nido: ambiente vivo | 🟢 Completado |
| Fase 6 | Framing de lenguaje y micro-copy | 🟡 Parcial (6.1 y 6.3 listos, 6.2 omitida) |
| Fase 7 | Pulido final y QA completo | ⬜ Pendiente |
| Fase 8 | Popups unificados · Fichas de Gashapón · Axos | 🟡 Parcial (Popups y Axos listos) |

---

## Notas de decisión

**¿Por qué primero los componentes compartidos (Fase 1) antes que el arte (Fase 2)?**  
Si hacemos las cartas primero y luego movemos LoteriaCard a un archivo compartido, tenemos que tocar los mismos archivos dos veces. La Fase 1 es la base que evita retrabajo.

**¿Por qué el UnboxingModal se extrae en Fase 4 y no en Fase 1?**  
El unboxing tiene estado complejo y partículas temáticas. Extraerlo cuando ya tenemos BottomSheet y Toast funcionando es más seguro — si algo falla, el componente más crítico (la compra) sigue andando desde Store.tsx.

**¿Por qué el Toast unifica VIP + game toasts en lugar de solo reemplazar `alert()`?**  
Al arrancar la Fase 1.3 se encontró que ya existían dos sistemas de notificaciones ad-hoc en `page.tsx`: `vipToasts` (bottom-izquierda) y `gameToasts` (bottom-derecha). Unificarlos en `ToastContext` elimina ~90 líneas de state/JSX de `page.tsx` y garantiza que todas las notificaciones futuras usen una sola API (`toast.ok/error/info/reward/vip/game`). El posicionamiento diferenciado (top-center vs bottom-corners) se mantiene porque los casos de uso son distintos.

**`xxs` (18px) agregado al plan original de LoteriaCard**  
El plan original pedía `xs/sm/md/lg`. Se agregó `xxs` (18px) porque la Fase 2.3 requiere un mini-preview de 18px en chips de tabla. Mejor definirlo ahora que crear un tamaño ad-hoc después.

**¿Qué NO está en el plan?**  
- Cambios de lógica de negocio / API
- Nuevas features (rankings, gashapon, etc.)
- Refactor de estado global (posiblemente Zustand/Context) — eso es un proyecto separado
- Cambios en el sistema de autenticación (Privy)
