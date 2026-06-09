# Plan: Sistema de DecoraciÃ³n de Cueva â€” DiseÃ±o, Modelos y UI

> Generado por **antigravity** · tarea `task-1780830394-41` · 2026-06-07T12:08:40.766908+00:00

## Descripción
definir en donde se van a poder poner items en la cueva, dan beneficios? solo salen de gashapon o se pueden comprar? supongo que en p2p también, no? definir subcategorias: piso, pared, mueble, electrodomestico o cosas asi.

## Análisis de impacto
Introduce el sistema de personalización del Santuario Cenote (Cueva). Afecta los modelos de ítems, inventarios de usuario, cálculos pasivos de staking de Axolotitos, mecánicas de recuperación de Foco y añade dos nuevos sumideros de tokens (FRJ y AXF).

## Archivos a crear/modificar
- `backend/app/models/items.py` (Validar compatibilidad CAVE_ITEM)
- `backend/app/api/v1/endpoints/cave_decor.py` (NUEVO: endpoints de actualización y minijuegos)
- `backend/app/services/cave_service.py` (NUEVO: lógica de negocio y cálculo de buffs pasivos)
- `frontend/components/multiplayer/CenoteRoom.tsx` (Agregar botones de interacción)
- `frontend/components/multiplayer/CaveDecorationPanel.tsx` (NUEVO: panel de edición de anclajes)
- `frontend/components/multiplayer/InteractiveArcade.tsx` (NUEVO: minijuego arcade de 1 AXF)
- `frontend/components/multiplayer/WishingWell.tsx` (NUEVO: pozo de deseos de 20 FRJ)

## Checklist de criterios de aceptación
- [ ] Catalogar decoraciones en ItemCatalog con tipo CAVE_ITEM y item_metadata conteniendo bonificaciones de Staking y Foco
- [ ] Implementar endpoint POST /api/v1/cave/decorations/update para guardar la colocación en User.cave_decorations validando inventarios y límites de slots
- [ ] Implementar lógica de cálculo dinámico para el Focus Recovery Boost (Tope variable basado en cave_level)
- [ ] Implementar lógica de cálculo dinámico para el FRJ Staking Multiplier (Tope variable basado en active_axolotitos)
- [ ] Diseñar y codificar el minijuego interactivo del Pozo de los Deseos para quema de FRJ (tasa retorno < 100%)
- [ ] Diseñar y codificar el Gabinete Arcade con cobro de 1 AXF y tabla de records local para social play
- [ ] Crear interfaz UI con anclajes fijos bioluminiscentes y drawer de inventario

## Propuestas / mejoras
- Implementar un sistema de anclajes fijos (Anchor Slot System) por capas para evitar clipping visual.
- Diseñar topes variables en las bonificaciones para incentivar la progresión: la velocidad de recuperación de foco se limita según el nivel de la cueva, y el multiplicador de staking se limita según el número de Axolotitos activos en staking.
- Agregar minijuegos de arcade cosméticos y competitivos de 1 AXF con rankings de puntuación local para visitantes.
- Agregar el minijuego del Pozo de los Deseos para quemar 20 FRJ de manera voluntaria.

## Notas de diseño
### 1. Sistema de Anclajes Predefinidos (Anchor Slots)
Cada nivel de cueva tiene posiciones específicas (slots) clasificadas en WALL (pared), FLOOR (piso), WATER (flotante) y SPECIAL (interactivo). Al tocar un slot, se abre el inventario filtrado de decoraciones compatibles.

### 2. Bonificaciones Pasivas con Tope Variable
- **Bono de Foco:** Muebles FLOOR/camas. Tope Foco = 10% + (cave_level * 5%). Máximo 50% al nivel 8.
- **Bono de Staking FRJ:** Estatuas/reliquias. Tope Staking = active_axolotitos * 3.5%. Máximo 28% con 8 Axolotitos.
- *Nota:* Se remueven todas las referencias al Hatchery / incubadora / Webitos, ya que este sistema ha sido descartado.

### 3. Minijuegos Quemadores de Tokens
- **Pozo de los Deseos (FRJ Burn):** Cuesta 20 FRJ. Quick-time event que premia con 30 FRJ o componentes comunes en caso de éxito perfecto, pero con un retorno neto promedio deficitario para quema de tokens.
- **Arcade de Algas (AXF Sink):** Cuesta 1 AXF por partida. Minijuego retro por records con ranking de visitantes locales (sin retorno financiero, meramente social/vanity).

## Guía de verificación
1. Crear decoraciones en ItemCatalog con item_metadata que contenga los bonos.
2. Equipar ítems en los slots del panel de edición de la cueva.
3. Validar que el endpoint guarda el JSON en User.cave_decorations.
4. Validar que la velocidad de recuperación de Foco de los Axolotitos resting y el rendimiento de Staking respetan los topes variables de acuerdo a active_axolotitos y cave_level.
5. Jugar una partida de Arcade, verificar el descuento de 1 AXF y la actualización del Scoreboard.
6. Lanzar frijoles al Pozo, verificar el descuento de 20 FRJ y la tasa de acierto/quema.
