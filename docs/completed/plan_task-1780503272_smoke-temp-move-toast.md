# Plan: SMOKE temp move toast

> Generado por **claude** · tarea `task-1780503272` · 2026-06-03T16:15:01.956081+00:00

## Descripción
SMOKE temp move toast

## Análisis de impacto
Cambio aislado a frontend. ToastProvider envuelve árbol en layout.tsx (root). Riesgo bajo: context nuevo no rompe componentes existentes. Riesgo de hidration mismatch si toasts SSR — montar solo client-side ('use client', portal). Toques opcionales en MarketP2P/VipModal solo si se cablea feedback real; tarea es SMOKE/temporal, mantener scope mínimo.

## Archivos a crear/modificar
- `frontend/components/ui/Toast.tsx`
- `frontend/components/ui/ToastProvider.tsx`
- `frontend/app/layout.tsx`
- `frontend/components/MarketP2P.tsx`
- `frontend/components/VipModal.tsx`

## Checklist de criterios de aceptación
- [ ] Componente Toast renderiza mensaje con tipo (success/error/info) y auto-dismiss configurable
- [ ] ToastProvider/context expone hook useToast() para disparar toasts desde cualquier componente
- [ ] Toasts apilan correctamente cuando hay múltiples activos sin solaparse
- [ ] Toast se cierra manual (botón X) y automático tras timeout
- [ ] Estilos Tailwind consistentes con tema del juego, sin layout shift
- [ ] Smoke test: disparar toast desde una accion existente (ej. compra shop o feedback multiplayer) y verificar render

## Propuestas / mejoras
- Usar portal (createPortal) para evitar z-index/overflow conflicts con modales existentes
- Variantes con iconos por tipo y barra de progreso de timeout
- Reemplazar alert()/console feedback disperso por toasts de forma incremental en una segunda tarea
- Soportar acciones en toast (ej. 'Deshacer') para flujos de market/inventory

## Notas de diseño
Toast es UI/frontend puro → agente claude. Patrón: ToastContext + useReducer para cola, ToastProvider en root layout, portal a document.body. Auto-dismiss via setTimeout limpiado en unmount. Tipos TS: ToastType = 'success'|'error'|'info'; Toast = {id, type, message, duration}. Animación entrada/salida con Tailwind transition. Marcado SMOKE/temp: mantener implementacion minima y reversible.

## Guía de verificación
1. cd frontend && npm run dev. 2. Abrir app, navegar a vista con accion cableada. 3. Disparar toast (compra/feedback). 4. Verificar: aparece, estilo correcto, auto-dismiss tras duration, cierre manual con X. 5. Disparar varios seguidos → apilan sin solapar. 6. npm run build verifica no hay error SSR/hydration. 7. Revisar consola sin warnings de React.
