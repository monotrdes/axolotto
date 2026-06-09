# Plan de Mejora Game UX — Fase 6 (Lenguaje de Corcholatas y Ticker Global)

Este plan detalla los cambios propuestos para la **Fase 6** del plan de mejora de Game UX, enfocándose en la estandarización del vocabulario (reemplazando conceptos DeFi por "Axogemas", "Corcholatas" y "Fichas") y la adición del Ticker de Actividad Global en el header, omitiendo la Fase 6.2 según lo solicitado.

## Proposed Changes

### 1. Estandarización de Lenguaje (6.1)

#### [MODIFY] [Inventory.tsx](file:///home/monotr/axolotto/frontend/components/Inventory.tsx)
- Reemplazar el texto `"🌿 Staking GAL"` por `"🪙 Corcholatas acumuladas"` (o `"Tapas acumuladas"`).
- Reemplazar la abreviatura `GAL` por `COR` en los balances del inventario de tablas.
- Reemplazar el texto `"Win Rate"` por `"Racha de Suerte"` (Línea 1152).
- Reemplazar el texto `"Slots"` por `"Espacios"` (Línea 957).
- Reemplazar la etiqueta de rendimiento por hora para que sea más clara:
  - Cambiar `{selectedBoard.hourly_yield_gal} GAL/h` a `Generación: {selectedBoard.hourly_yield_gal} COR/h` (Línea 1164).

#### [MODIFY] [page.tsx](file:///home/monotr/axolotto/frontend/app/page.tsx)
- Reemplazar el icono `🌿` y texto `GAL` del header por el icono `🪙` y la abreviación `COR` (en el chip de balance de la moneda secundaria).
- Ajustar las variables internas/textos de presentación para que hagan referencia a "Corcholatas" en lugar de "Gemas Alga".

---

### 2. Ticker Global de Actividad (6.3)

#### [MODIFY] [page.tsx](file:///home/monotr/axolotto/frontend/app/page.tsx)
- **Estado de Feed:**
  - Definir el estado `tickerFeed` para almacenar la actividad reciente.
  - Añadir un `useEffect` que consulte periódicamente (cada 30 segundos) el endpoint `https://api.axolot.to/api/v1/shop/capsule/feed` y cargue los últimos resultados.
- **Renderizado del Ticker Sub-bar:**
  - Insertar un contenedor fixed `fixed top-14 left-0 right-0 z-30 h-6 bg-[#080816]/90 backdrop-blur-md border-b border-white/5` justo debajo del header principal.
  - Usar la clase CSS `.ticker-track` (ya definida en `globals.css`) para desplazar horizontalmente los eventos.
  - Estructura de cada evento: `🎉 @usuario obtuvo una Legendaria` o `🍀 @usuario obtuvo ...`.
- **Ajuste Dinámico de Layout:**
  - Ajustar el padding superior del tag `<main>` para que cambie dinámicamente de `pt-14` a `pt-20` cuando el ticker tenga datos cargados, evitando superposiciones.

---

## Verification Plan

### Automated Tests
- Validar compilación exitosa sin errores de tipado de TypeScript:
  `npx tsc --noEmit` en el directorio `/home/monotr/axolotto/frontend`.

### Manual Verification
- **Estandarización de Textos (Mochila):**
  - Ve a la pestaña **Mochila / Tablas**.
  - Abre el detalle de cualquier tabla y confirma que los textos digan "🪙 Corcholatas acumuladas", "Racha de Suerte" y "Generación: X COR/h".
  - En la barra superior de estadísticas de la mochila, valida que se muestre "Espacios" en lugar de "Slots".
- **Ticker Global:**
  - Recarga la aplicación y valida que aparezca la barra del ticker justo debajo del menú de navegación.
  - Confirma que el scroll horizontal sea suave y continuo.
  - Coloca el cursor sobre el ticker y confirma que la animación se pausa (`animation-play-state: paused`).
  - Verifica que se adapte correctamente en pantallas móviles sin desbordar.
