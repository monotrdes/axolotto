# Plan: Revisar docs/ y crear tasks pendientes del Taskboard (auto-avance + refactor)

> Generado por **deepclaude** · tarea `task-1780507930-6` · 2026-06-03T21:29:49.304054+00:00

## Descripción
revisa la carpeta docs y analiza todo, si encuentras tareas sin hacer, crea las tasks

## Análisis de impacto
Tarea de tools pura. No modifica backend FastAPI, frontend Next.js ni contratos. Solo crea registros en tasks.db. Riesgo nulo para el ecosistema del juego. La tarea es orquestación y catalogación. Los archivos leídos son docs estáticos. La escritura es solo INSERTs en SQLite vía API REST del taskboard (POST /api/tasks/create). El plan_task de este mismo task (1780507930-6) ya existe en docs/, generado por deepclaude — esta respuesta es la re-planificación solicitada por el usuario.

## Archivos a crear/modificar
- `tasks.db`

## Checklist de criterios de aceptación
- [ ] Leer todos los archivos en docs/ (root) y docs/completed/ para catalogar trabajo pendiente
- [ ] Leer tasks.db y cruzar con los plan_task-*.md huérfanos — detectar archivos plan sin task correspondiente
- [ ] Crear tareas en el Taskboard para cada ítem pendiente del 000_PLAN_GLOBAL_PENDIENTES.md que no tenga task
- [ ] Crear tarea(s) para el MASTER_PLAN_CRIADERO.md (al menos la Fase 1 como punto de entrada)
- [ ] Crear tareas para los quick wins y mejoras del vip_club_panel_auditoria.md si no existen ya
- [ ] Crear tareas para los pendientes del task_board_workflow_plan.md (E2E, webhooks, métricas, hotkeys)
- [ ] Detectar plan_task-*.md huérfanos (task-1780503272, task-1780507349-3) y crear sus tasks o marcarlos como superseded
- [ ] Excluir tridyland_migracion_plan.md — es proyecto separado, no Axolotto. Solo anotar en comentario.

## Propuestas / mejoras
- Considerar crear una tarea 'epic' o etiqueta para agrupar los ~40 items del plan global bajo fases (FASE0, FASE1, etc.)
- task-1780507349-3 (revisar uso de claude/deepclaude vía /usage) parece cubierto por task-1780512108-6 (done). Verificar si quedó algo pendiente o marcar plan doc como superseded
- task-1780507417-4 está en concepts sin plan doc — necesita planificación o cierre
- El MASTER_PLAN_CRIADERO.md tiene 6 fases con ~30 subtareas. Crear solo Fase 1 como entry point y referenciar el resto en descripción para no saturar el board

## Notas de diseño
Flujo del agente: (1) Leer tasks.db vía python3 -c sqlite3 para obtener todas las tasks existentes con su status. (2) Leer todos los archivos docs/ raíz y docs/completed/. (3) Construir matriz: fuente del pendiente × task existente. (4) Para cada gap detectado, hacer POST /api/tasks/create al endpoint del taskboard en localhost:8181. Parámetros: title (max 80 chars), description (resumen del scope), category, priority según la fase del plan global. (5) Para plan_task huérfanos (task-1780503272, task-1780507349-3), crear la task con los datos ya existentes del plan doc. (6) Para el plan global, crear tasks agrupadas por fase (FASE0 seguridad, FASE1 deploy Amoy, etc.) como tareas individuales. (7) Reportar tabla final: qué se creó, qué se omitió, y por qué.

## Guía de verificación
1. Revisar tasks.db con python3 -c 'SELECT id, title, status FROM tasks ORDER BY created_at DESC LIMIT 20' — deben aparecer las nuevas tasks. 2. Abrir el Taskboard en http://localhost:8181 — las nuevas tarjetas deben verse en columna Wishes o Concepts. 3. Verificar que no hay plan_task-*.md huérfanos sin task correspondiente (excepto tridyland). 4. Verificar que el plan_task-1780507930-6.md (este mismo) se movió a docs/completed/ al terminar. 5. Contar: al menos 10+ tareas nuevas creadas cubriendo FASE0, FASE1, FASE2, vip_club, taskboard pendientes, y plan_task huérfanos.
