# Reporte de Diseño & UX — Axolotto

> **Generado:** 2026-05-28
> **Scope:** Análisis basado en lectura directa del código fuente (frontend/).
> **Contexto clave:** El Nido ya es el prototipo funcional de la visión 2.5D. Todas las demás vistas seguirán ese patrón en el futuro.

---

## Sistema de Diseño Global

### Fortalezas

- **Identidad visual coherente:** Los tokens CSS (`--world-void`, `--world-deep`, `--world-mid`, `--world-surface`) crean atmósfera oscura consistente. El `#E4007C` como acento de marca es memorable.
- **Color por dominio:** Cada sección tiene color temático propio (pink → tienda, indigo → cartas, teal → nido, amber → rankings, purple → gashapón). El usuario desarrolla memoria espacial visual.
- **Librería de animaciones robusta:** Keyframes de calidad — `holo-shift`, `axo-bob`, `axo-swim`, `cenote-bubble`, `ray-flicker`. Hay intención real de polish.

### Problemas globales

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| `globals.css` declara `Arial, Helvetica` como fallback del body en lugar de Inter | 🟡 Moderado | Unificar: `font-family: var(--font-geist-sans), 'Inter', sans-serif` |
| Sin pantalla de onboarding ni tutorial | 🔴 Crítico | Un nuevo usuario llega al HUD con 7 tabs y sin contexto del juego ni de la economía |
| Paleta de rareza nunca explicada in-game | 🟡 Moderado | Tooltip "?" que abra un glosario de rareza desde inventario |
| Componentes monolíticos (Store 97KB, Inventory 103KB, Santuario 102KB) | 🟡 Moderado | Ralentiza TTI y dificulta estados de carga parciales |

---

## Vista por Vista

---

### 1. Navegación Global (HUD) — `page.tsx`

**Layout actual:**
```
[ Tienda | Cartas | Tablas ]  [  🎮 JUGAR  ]  [ El Nido | Rankings | Gashapón ]
```

**Fortalezas:** El FAB central elevado para JUGAR comunica la acción primaria. El patrón bottom-dock iOS es correcto para móvil.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| 7 destinos visibles simultáneamente — demasiados para usuario nuevo | 🔴 Crítico | Agrupar: `Colección` (cartas+tablas), revelar Gashapón después del primer uso |
| El tab activo no tiene tratamiento visual de "estás aquí" claramente diferenciado | 🟡 Moderado | Añadir barra inferior sólida o tab elevado al activo |
| VIP chip muestra datos (días, COR pendiente) sin contexto suficiente | 🟡 Moderado | Si hay COR reclamable: badge/dot rojo y animación de atención más obvia |
| Botón de logout demasiado prominente junto a saldos | 🟢 Menor | Moverlo a un menú de perfil |
| No hay indicador de qué tab tiene notificaciones/novedades | 🟡 Moderado | Dot badges: nuevo item en Tienda, huevo listo en Nido, partida terminada |
| Tabs `criadero` y `axolotitos` son legado (dead code) | 🟢 Menor | Eliminar del tipado TabId cuando sea seguro |

**Ideas nuevas:**
- **Mapa rápido radial:** Al mantener pulsado el FAB aparece un círculo radial con todos los destinos. Perfecto para la visión 2.5D futura (pisar el centro teletransporta al jugador).
- **Notificaciones de nido:** Animación/pulso en el tab de El Nido cuando un huevo esté próximo a eclosionar.

---

### 2. El Nido (Santuario) — `Santuario.tsx` ⭐ Vista de referencia 2.5D

**Descripción actual:** Escena de cenote con capas CSS — rayos de luz, burbujas, axolotitos posicionados aleatoriamente con perspectiva por escala, y cuevas-nido en filas frontal/trasera.

**Fortalezas:**
- El concepto de cenote (agua, burbujas, rayos de luz) es coherente con axolotls (Xochimilco). Hay cuidado cultural genuino.
- El tinte por período del día (`Madrugada → cyan`, `Tarde → naranja`, `Noche → violeta`) da dinamismo sin assets adicionales.
- Las cuevas-arco con estados visuales (calor, congelado, listo) son legibles de un vistazo.
- El CSS de swim generado dinámicamente por axolotito (`axo-swim-{id}`) es técnicamente elegante.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| Altura 340px en móvil es demasiado pequeña — escena apretada con 7 cuevas + axolotitos | 🔴 Crítico | Mínimo 420px móvil, preferible `60vh` con max de 520px |
| Axolotitos son emojis Unicode — pixelados en high-DPI, no escalan bien | 🔴 Crítico | Reemplazar con SVGs o sprites. Un SVG básico de 3-4 frames da mucho más carácter |
| Cuevas-nido son CSS puro (border-radius arch) — funcionan pero se ven genéricas | 🟡 Moderado | SVGs de cuevas con variantes (vacía, ocupada, lista) — prioridad alta para 2.5D |
| No hay suelo/floor definido — los axolotitos "flotan" sobre el gradiente | 🟡 Moderado | Línea de fondo con piedras/algas en SVG o con CSS border/gradient en el bottom |
| Cuevas frontales a `bottom: 4%` — muy pegadas al borde inferior | 🟡 Moderado | `bottom: 8-10%` + una "orilla" de piedra al pie del contenedor |
| La acción de calefactar no muestra cuánto COR costará ANTES del tap | 🔴 Crítico | Tooltip con costo al hover/longpress antes de ejecutar la acción económica |
| WeatherChip tiene datos técnicos (loss_rate %, heat_multiplier) sin iconografía intuitiva | 🟡 Moderado | El % de pérdida/hora debería ser rojo con ícono de peligro si > 10% |
| Sin forma de ver qué axolotito es cuál desde la escena | 🟡 Moderado | Al tap en un axolotito: mini-card con nombre, nivel y stats principales |

**Para la versión 2.5D completa:**
1. **Cámara con plano inclinado real** — `perspective: 800px` + `rotateX(20-30deg)` en el plano del suelo para perspectiva isométrica real sin 3D.
2. **Más capas de parallax:** Fondo (paredes) → Capa media (cuevas traseras, algas) → Capa frontal (suelo, cuevas delanteras, axolotitos) → HUD.
3. **Axolotito seleccionado como "personaje jugador"** — Si el axolotito está seleccionado para jugar, aparece en primer plano con idle distinto. Conecta mecánica con narrativa visual.
4. **Interacciones diegéticas:** Arrastrar carbones (🔥) a una cueva para calentarla, en lugar de un modal.
5. **Diferenciación visual axolotito activo vs en descanso** — El que está "jugando" aparece con equipamiento y un icono de JUGAR flotante sobre él.

---

### 3. Jugar (PlayMode) — `PlayMode.tsx` + `screens/`

**Flujo actual (7 pasos):**
```
mode-select → axo-select → board-select → budget → sala-select → [cpu-sim | playing] → settling
```

**Fortalezas:**
- `WizardDots` como indicador de paso es comprensible.
- Guardar presupuesto en `localStorage` por axolotito es un detalle bien pensado.
- Las animaciones `slide-step`/`slide-back` dan dirección al flujo.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| El wizard inicia en `'axo-select'` (línea 83) — se salta la pantalla de selección de modo | 🔴 Crítico | Cambiar estado inicial a `'mode-select'`. Un nuevo usuario no sabe que hay CPU vs Multijugador |
| `BudgetScreen` pide presupuesto + límite de pérdida + límite de ganancia — muy técnico | 🔴 Crítico | Modo "Simple" (solo presupuesto) y modo "Avanzado" (los 3 campos) |
| No hay resumen previo al juego | 🟡 Moderado | Pantalla de confirmación final: "Axolotito X · Tablero Y · Sala Z · Apuesta W COR" |
| `SalaSelectScreen` (Rookie/Champion) no muestra diferencia de premios/riesgos | 🟡 Moderado | Mostrar pool de premios, jugadores activos y costo de entrada en cada sala |
| Durante el juego no se puede colapsar el `AxoStatusBar` | 🟢 Menor | Opción de minimizar el status bar para ver la tabla completa |
| `SettlingScreen` es transitorio — el usuario no puede volver a ver el resultado | 🟡 Moderado | Resumen guardado post-settling con historial de cartas llamadas |

**Para la versión 2.5D:**
1. **El flujo del juego EN la escena** — En lugar de wizard overlay, el jugador "camina" hasta la Sala de Lotería y la cámara hace dolly.
2. **Cartas llamadas como objetos físicos** — La carta "cae" o "aparece" en el centro de la mesa cuando el dealer la llama.
3. **NPCs como jugadores CPU** — Axolotito rival visible en el otro lado de la mesa.
4. **"¡Lotería!" diegético** — Al completar un patrón, el axolotito del jugador salta y grita con animación.

---

### 4. Tienda — `Store.tsx`

**Fortalezas:**
- Los paquetes con nombres (Fiesta, Nido, Cosmos, Brillante) dan personalidad.
- `UnboxingModal` con animación de apertura y volteo de cartas es el momento "wow" más importante.
- La Racha Diaria como mecánica de retención es efectiva.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| 4 secciones en un componente sin separación visual clara de jerarquía | 🔴 Crítico | Sub-tabs o headers claramente distintos. La Racha Diaria al top (siempre visible) |
| Precio en COR sin referencia a USD/MXN equivalente | 🟡 Moderado | Mostrar precio aproximado en fiat junto al precio en COR |
| Sin historial de compras accesible | 🟡 Moderado | Ícono "mis compras" o link al historial desde la tienda |
| Probabilidades de rareza no visibles antes de la compra | 🔴 Crítico | Las drop rates deben ser visibles antes de cualquier compra (ético y regulatorio) |
| El flujo de pago cripto está embebido en el layout de tienda | 🟡 Moderado | `CryptoCheckout` debería ser un modal flotante limpio |

**Para la versión 2.5D:**
1. **Mercado como espacio físico** — Puesto de mercado en Xochimilco donde los paquetes están en estantes.
2. **Vendedor NPC axolotito** — Reacciona a las compras con animaciones.
3. **Racha diaria como altar** — Un "altar de recompensa" que el jugador visita cada día.

---

### 5. Inventario — `Inventory.tsx` (Cartas + Tablas)

**Fortalezas:**
- El sistema de rareza visual en las cartas (glow rings) es inmediatamente legible.
- Los tamaños de carta adaptativos (xxs a xl) permiten vistas densas o detalladas.
- El desmontaje para recuperar cartas añade estrategia económica.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| Cartas y Tableros como tabs separados en navegación principal usando el mismo componente | 🟡 Moderado | Unificar en un tab "Colección" con sub-tabs internos |
| `BoardEditor` embebido en `Inventory` crea UI profundamente nested | 🟡 Moderado | El editor de tableros debería ser su propia vista/modal de pantalla completa |
| Sin búsqueda ni filtro por nombre de carta | 🟡 Moderado | Campo de búsqueda quick-filter es esencial con 54+ cartas |
| Sin instrucción visible para drag-and-drop en el editor | 🟡 Moderado | Tooltip "Arrastra cartas aquí" o instrucciones en `BoardEditor` en el primer uso |
| "Desmontaje en lote" sin preview de qué se recuperará | 🔴 Crítico | Siempre mostrar el resumen económico antes de acciones destructivas |

**Para la versión 2.5D:**
1. **Galería de cartas** — Las cartas están en marcos en las paredes de una sala. Las Legendarias tienen marcos especiales con iluminación.
2. **Mesa de trabajo para tableros** — Espacio físico donde las cartas se arrastran desde el inventario a la mesa.

---

### 6. Rankings — `Rankings.tsx`

**Fortalezas:**
- Podio de top 3 con medallas es estándar y legible.
- Badges de tier (Cobre/Plata/Oro/Leyenda) dan jerarquía visual rápida.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| No muestra la posición del usuario actual en la lista | 🔴 Crítico | Row fijo al fondo mostrando la posición del jugador aunque esté en el puesto 500 |
| Sin filtros por período (semana, mes, all-time) | 🟡 Moderado | Rankings sin período pierden sentido para jugadores nuevos |
| Sin historial de cambios de posición | 🟢 Menor | Flecha ↑↓ indicando si el jugador subió/bajó esta semana |
| La acción "alquilar tablero desde ranking" no tiene label claro | 🟡 Moderado | Añadir tooltip/label "Alquilar este tablero" |

---

### 7. Gashapón — `Gashapon.tsx`

**Fortalezas:**
- Los 3 tiers con precios escalados (150/500/2000 COR) dan opciones claras.
- La celebración de Legendaria con partículas es el momento de máxima emoción.
- El sistema de pity con contador visible ("2/10 until guaranteed") reduce la ansiedad.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| Probabilidades de rareza no expuestas claramente | 🔴 Crítico | Tabla de drop rates visible antes de la compra |
| El triple roll no comunica el beneficio vs. 3 singles | 🟡 Moderado | Comunicar explícitamente el valor (ej: "Triple roll: 10% de bonus COR") |
| Sin historial de pulls recientes | 🟡 Moderado | "Mis últimos 10 pulls" con las cartas obtenidas |
| Sin preview de cartas posibles antes de comprar | 🟡 Moderado | Opción "ver catálogo de este tier" antes de hacer el pull |

**Para la versión 2.5D:**
1. **Máquina gacha física en la escena** — El jugador se acerca, inserta monedas, y la cápsula cae físicamente.
2. **Cápsula rodando por el suelo** — La cápsula rebota, rueda y abre — mucho más satisfactorio que un modal.

---

### 8. Sistema VIP — `VipModal.tsx`

**Fortalezas:**
- Los 3 tiers diferenciados visualmente con animaciones distintas por tier.
- "Most Popular" en Dorado sigue buenas prácticas de conversión.
- `pendingGal` claim como razón diaria para abrir el modal.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| Beneficios en lista de texto — difícil comparar across tiers | 🟡 Moderado | Tabla comparativa horizontal: feature por fila, tier por columna, checkmarks |
| Racha VIP sin visualización de progreso | 🟡 Moderado | Ring/bar de progreso de streak |
| Los días restantes en el VIP chip no tienen acción directa de renovar | 🟡 Moderado | Tap en el chip abre el modal directamente en "renovar" |
| Beneficio "reducción de fees P2P" sin explicación | 🟡 Moderado | Tooltips o links a explicación de cada beneficio |

---

### 9. Vista de Juego (CpuSimScreen) — `screens/CpuSimScreen.tsx`

**Fortalezas:**
- `cpu-win-surge` y `player-win-bloom` diferencian bien los estados de victoria.
- `card-call` (200ms) da respuesta inmediata a cada carta llamada.

**Problemas:**

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
| No hay display prominente de la carta más reciente llamada | 🟡 Moderado | Un "call feed" lateral o display central grande de la última carta |
| Tablero propio vs tablero rival sin diferencia visual suficiente | 🔴 Crítico | Clara etiqueta y color diferente entre "Mi tablero" y "Tablero rival" |
| Si las stats del axolotito influyen en tiempo real, no se comunica | 🟡 Moderado | Animación/notificación cuando se activa un bonus de stat (luck, focus, etc.) |

---

## Visión 2.5D: Arquitectura del Mundo

### Mapa propuesto

```
┌────────────────────────────────────────────────────────────────┐
│                    Mapa del Mundo Axolotto                      │
│                                                                 │
│  [🏪 Mercado]  ←──→  [🏠 El Nido/Cenote]  ←──→  [🎮 Sala]    │
│       ↕                      ↕                        ↕         │
│  [🎰 Gacha]   ←──→  [🃏 Galería/Inventario] ←──→ [🏆 Arena]  │
│                              ↕                                  │
│                       [💎 Club VIP]                             │
└────────────────────────────────────────────────────────────────┘
```

### Lo que El Nido ya enseña

El Nido tiene los principios correctos:
- **Parallax por z-index** (back slots vs front slots)
- **Escala como profundidad** (`isBack ? 0.72 : 1.0`)
- **Iluminación ambiental** (rayos, tints de período)
- **Elementos vivos** (burbujas, axolotitos con swim animation)

**Lo que falta para completar la ilusión:**
1. Assets visuales reales (SVGs/sprites) — no emojis ni CSS puro
2. Un plano de suelo explícito (textura, no solo gradiente)
3. Más capas de profundidad (actualmente solo 2: back/front)
4. Oclusión — objetos del frente que tapen parcialmente los del fondo

### Transición entre vistas en el mundo 2.5D

| Consideración | Recomendación |
|---------------|---------------|
| Cómo entrar/salir de vistas | Transición "walk-through door" — el axolotito camina y la cámara sigue |
| Mobile: espacio limitado | Mantener el dock como shortcut. El movimiento libre sería "modo exploración" |
| Performance | Pre-renderizar escenas adyacentes (lazy load de 1 escena atrás/adelante) |
| First-time user | El onboarding sería el axolotito guiando al jugador por cada zona |

### Nuevas ideas para el mundo 2.5D

1. **Personalización de habitat:** El cenote con decoraciones comprables (plantas, piedras, iluminación) — P2P de items cosméticos.
2. **Axolotito personal persistente:** En la esquina inferior de TODAS las vistas, el axolotito principal del jugador hace idle. Al tapearlo, muestra sus stats. Consistencia de identidad.
3. **Clima en tiempo real en todas las escenas:** Ya tienes los tints de período — llevarlo a assets completos. Si nieva en Xochimilco, la escena entera tiene nieve.
4. **Eventos del mundo como NPCs:** "¡El axolotito Aqua ganó en la Sala Champion!" como un NPC que cruza la escena con un cartel.
5. **Mercado P2P como stands físicos:** Stands de diferentes jugadores con sus cartas/tableros exhibidos.
6. **Transición de día/noche en tiempo real:** El cielo del mundo cambia en todas las escenas según el período. La lógica ya existe, solo faltan los assets.

---

## Prioridades de Implementación

| # | Qué | Por qué |
|---|-----|---------|
| 1 | Onboarding/tutorial para nuevos usuarios | Sin esto, cualquier mejora visual es para nadie |
| 2 | Probabilidades de drop visibles antes de compra (Gashapón + Tienda) | Confianza y cumplimiento regulatorio |
| 3 | Posición del usuario propio en Rankings | Motivación de juego fundamental |
| 4 | Confirmación de costo antes de acciones económicas (calefactar, desmontar) | Previene pérdidas accidentales de COR/AXG |
| 5 | SVG/sprites para axolotitos en El Nido | El cambio visual más impactante para la visión 2.5D |
| 6 | Fix: `GameView` inicial debe ser `'mode-select'` en `PlayMode.tsx:83` | Bug de flujo en el wizard de juego |
| 7 | Dot badges en tabs de navegación (huevo listo, nueva partida, etc.) | Retención diaria — el jugador sabe cuándo hay algo que atender |
| 8 | Altura de El Nido a mínimo 420px en móvil | La escena principal necesita más canvas |
| 9 | Sub-tabs en Tienda con Racha Diaria siempre visible al top | La racha diaria es el hook de retención más fuerte |
| 10 | Pantalla de resumen antes de iniciar partida | Reduce abandono por error y fricciones post-compra |

---

*Ver también: `GDD.md`, `nido_design.md`, `UX_IMPROVEMENTS_PLAN.md`, `vip_club_design.md`*
