# Plan: Rediseño Mochila Multidimensional: Pestañas Unificadas y UX Premium

> Generado por **deepclaude** · tarea `task-1780836075-48` · 2026-06-07T12:42:40.776879+00:00
> Actualizado: corrección de diseño — Axolotitos van en Santuario, no en Mochila

## Descripción
Rediseño de Mochila: Pestañas Unificadas y UX Premium

Implementar la Mochila Multidimensional unificando cartas, tablas y agregando la pestaña de objetos/consumibles con animaciones premium. Plan en [backpack_redesign_plan.md](file:///D:/Axolotto_2026/axolotto/docs/backpack_redesign_plan.md)

## Análisis de impacto
ALTO impacto visual, BAJO riesgo técnico. Cambios 100% frontend, sin tocar backend ni contratos. El blast radius es: (1) Inventory.tsx — refactor mayor del componente más grande del proyecto (~985 líneas), requiere extraer lógica existente de cartas/tablas/axolotitos a sub-componentes manteniendo toda la funcionalidad. (2) MochilaFloating.tsx — rediseño completo del botón y sus interacciones. (3) page.tsx — cambios puntuales: un solo tab `mochila` reemplaza los tabs separados `cartas` y `tablas`. (4) tipos/play.ts — agregar `mochila` al union type TabId. Riesgo principal: regresiones en flujos existentes de cartas (unboxing, filtros, P2P listing) y tablas (crear/editar/desarmar/staking/rentas). Mitigación: extraer la lógica existente del hook useInventory intacta, solo reorganizar la presentación.

## Archivos a crear/modificar
- `frontend/components/Inventory.tsx`
- `frontend/components/world/hud/MochilaFloating.tsx`
- `frontend/app/play/page.tsx`
- `frontend/types/play.ts`
- `frontend/types/inventory.ts`
- `frontend/hooks/useInventory.ts`
- `frontend/components/inventory/ItemGrid.tsx` (NUEVO)

## Checklist de criterios de aceptación
- [ ] Inventory.tsx transformado en dashboard unificado con 3 pestañas horizontales (Cartas, Tablas, Objetos) con transiciones de color dinámicas por pestaña — **Axolotitos NO van aquí, viven en el Santuario**
- [ ] La pestaña 'Objetos' (ItemGrid.tsx) muestra consumibles en cuadrícula: Gotas de Agua, Lámparas de Calor, Escudos del Santuario, Accesorios — con botón 'Usar' que redirige a la zona correspondiente
- [ ] MochilaFloating.tsx rediseñado con botón 2.5D (gradiente rosa-cyan), animación de rebote/jiggle al hover, y portal de apertura con backdrop-blur
- [ ] Transiciones premium implementadas con Tailwind v4 CSS animations: glow dinámico por pestaña (indigo→pink para cartas, emerald→teal para tablas, purple→amber para objetos)
- [ ] page.tsx actualizado: tab 'mochila' unificado reemplaza los tabs separados 'cartas' y 'tablas'. MochilaFloating abre el tab 'mochila' con la última pestaña visitada
- [ ] Footer de Mochila incluye enlace rápido "Ir al Santuario 🦎" para acceder a los Axolotitos
- [ ] La pestaña 'Cartas' mantiene funcionalidad completa: sobres sellados + album de 54 cartas con filtros de rareza/shiny/propiedad + unboxing integrado
- [ ] La pestaña 'Tablas' mantiene sub-pestañas (Mis Tablas + Mercado) con HUD de staking unificado, botón 'Cobrar Todo' premium, y acceso al editor de tablas

## Propuestas / mejoras
- Usar Tailwind v4 CSS animations en lugar de Framer Motion — evita nueva dependencia, el proyecto ya tiene Tailwind 4 configurado
- `useInventory` siempre precarga los datos de tablas (playerBoards + slotsStatus) para que el cambio de pestaña sea instantáneo
- Estado `mochilaInitialTab` en page.tsx para recordar la última pestaña visitada y reabrirla desde MochilaFloating

## Notas de diseño
- Los Axolotitos NO pertenecen a la Mochila. Viven en el Santuario (tab Nido del dock). La decisión fue tomada en 2026-06.
- El footer de la Mochila tiene un link de navegación rápida al Santuario.

## Guía de verificación
1. Abrir Mochila → debe mostrar 3 tabs (Cartas, Tablas, Objetos) — NO debe mostrar tab de Axolotitos
2. Tab Cartas: verificar sobres sellados + álbum de cartas con filtros
3. Tab Tablas: verificar sub-tabs Mis Tablas / Mercado, HUD de FRJ, botón Cobrar Todo
4. Tab Objetos: verificar cuadrícula de consumibles (puede estar vacía si el usuario no tiene items)
5. Footer: verificar enlace "Ir al Santuario 🦎" navega al tab correcto
6. MochilaFloating: verificar botones cartas/tablas/items abren el tab correcto
7. Store.tsx `cambiarTab('tablas')` debe seguir funcionando (abre Mochila en tab Tablas)
