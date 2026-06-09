# Plan: Ampliar sistema de etiquetas (categorías) con nuevos tipos de tarea

> Generado por **deepclaude** · tarea `task-1780622810-2` · 2026-06-05T01:28:38.889415+00:00

## Descripción
hay que crear etiquetas para las tareas, cada que se planee se debe de adjuntar de que tipo es la tarea: backend, front, contrato, finanzas, admin, game design, etc, etc, etc

## Análisis de impacto
Cambio de bajo riesgo: la columna 'category' ya existe en SQLite como TEXT sin constraints. Las APIs ya aceptan el campo category en create y edit. Solo se expanden opciones de UI y se actualizan strings en prompts de IA. No hay migración de esquema. No se toca backend del juego ni contracts.

## Archivos a crear/modificar
- `tools/taskboard/index.html`
- `tools/taskboard/modules/modal.js`
- `tools/taskboard/ai_router.py`
- `tools/taskboard/styles.css`

## Checklist de criterios de aceptación
- [ ] Agregar selector de categoría visible en el modal 'Nueva Idea' (antes de crear la tarea)
- [ ] Ampliar opciones de categoría en todos los dropdowns: backend, frontend, contracts, game-design, admin, finances, devops, tools, bug, docs, research
- [ ] Actualizar prompts de IA (SYSTEM_CONCEPT, SYSTEM_PLANNING) para reconocer las nuevas categorías
- [ ] Pasar la categoría seleccionada al crear tarea vía POST /api/tasks/create
- [ ] Mostrar la categoría en la tarjeta fake mientras se genera (insertFakeCard)
- [ ] Agregar estilos de badge por categoría específica para distinción visual rápida
- [ ] Verificar que el endpoint /api/tasks/edit ya acepta category (ya lo hace, confirmar integridad)

## Propuestas / mejoras
- Considerar migrar 'category' a multi-etiqueta (tags array) en el futuro si una tarea puede ser backend+contracts simultáneamente
- Agregar colores de badge específicos por categoría en styles.css para escaneo visual rápido
- El dropdown de 'Nueva Idea' podría usar íconos junto al texto de cada categoría para mayor claridad

## Notas de diseño
Se reutiliza el campo 'category' existente (TEXT en SQLite, sin constraints). Catálogo completo de categorías: backend, frontend, contracts, game-design, admin, finances, devops, tools, bug, docs, research. Los valores viejos (backend, frontend, tools, bug, docs) se preservan. En el modal 'Nueva Idea' se agrega un <select> entre el textarea y el selector de columna. En el modal 'Edit Metadata' se amplía el <select> existente. En los prompts SYSTEM_CONCEPT y SYSTEM_PLANNING se reemplaza 'backend|frontend|bug|docs|tools' por la lista completa. No se añade migración DB porque el campo ya es TEXT libre.

## Guía de verificación
1. Abrir http://localhost:8181, botón 'Nueva Idea' → verificar que aparece selector de categoría con 11 opciones. 2. Crear una idea con categoría 'game-design', verificar que la tarjeta fake muestra 'game-design'. 3. Al cargar, la tarjeta real debe mostrar el badge 'game-design'. 4. Abrir modal 'Edit Metadata' en cualquier tarea → verificar dropdown con 11 opciones. 5. Cambiar categoría y guardar → verificar badge actualizado. 6. Mover tarea de Wishes a Planning → verificar que AI genera plan con categoría correcta (revisar log). 7. Ejecutar `sqlite3 tasks.db "SELECT DISTINCT category FROM tasks"` para confirmar que las categorías nuevas persisten.
