# Plan: Detectar auto-avance de Doing→Review en el poller y refrescar el board

> Generado por **deepclaude** · tarea `task-1780517494-9` · 2026-06-03T20:13:20.181127+00:00

## Descripción
al terminar el proceso de doing se pasa correctamente a la columna review, pero no se esta refrescando el front, tengo que dar refresh F5

## Análisis de impacto
Cambio localizado en refreshDoingTasks() (línea 984). No toca backend, no cambia API, no afecta server.py. El poller actual solo actualiza metadatos de agente en tareas 'doing'. Se amplía para detectar transiciones de status: si una tarea local 'doing' ya no lo es en el servidor, se actualiza su status, se dispara renderBoard() y startAIPolling(). Riesgo bajo: es añadir un bloque condicional extra dentro del mismo poll ya existente.

## Archivos a crear/modificar
- `tools/taskboard/index.html`

## Checklist de criterios de aceptación
- [ ] Al auto-avanzar un agente una tarea de Doing→Review en backend, el frontend detecta el cambio de status en el poll de 3s sin necesidad de F5
- [ ] La tarjeta aparece visualmente en la columna Review tras el auto-avance
- [ ] Se inicia el polling de IA (startAIPolling) para la tarea recién llegada a Review, igual que cuando se mueve manualmente
- [ ] El movimiento manual drag-and-drop a Review sigue funcionando igual (fetchTasks + startAIPolling ya lo cubren)
- [ ] El banner de 'agente corriendo' se actualiza correctamente cuando una tarea sale de Doing
- [ ] No se rompe el polling de metadata de agente (_agent_elapsed, _agent_status) para tareas que siguen en Doing

## Propuestas / mejoras
- Considerar unificar refreshDoingTasks() con fetchTasks() en una sola función de polling que refresque todo el board cada N segundos, simplificando la lógica
- Agregar un indicador visual tipo 'badge de auto-avance' en la tarjeta cuando el movimiento fue hecho por el agente y no por drag manual

## Notas de diseño
En refreshDoingTasks(), dentro del loop sobre freshTasks, agregar: si el task local existe Y su status local era 'doing' Y el status fresco es distinto (típicamente 'review'), entonces: (1) copiar todos los campos frescos al objeto local (no solo _agent_*), (2) marcar changed=true, (3) si el nuevo status es 'review', llamar startAIPolling(ft.id, 'review'). Al final del loop, si changed incluye transiciones de status, llamar renderBoard() además de updateRunningBanner(). La condición actual del if (ft.status === 'doing' || ft._agent_elapsed) debe expandirse para incluir también: (local && local.status === 'doing' && ft.status !== 'doing').

## Guía de verificación
1. Iniciar taskboard (python server.py). 2. Crear tarea con test_command vacío y un agente asignado. 3. Mover tarjeta a Doing manualmente. 4. Ejecutar 'Run Agent' desde modal de detalle. 5. Esperar a que el agente termine (ver log en server.py: 'Agent: Task X auto-advanced to review'). 6. Verificar que en ≤3s la tarjeta aparece en columna Review sin F5. 7. Verificar que aparece toast 'IA analizando (review)…'. 8. Verificar que el contador de Doing baja y el de Review sube.
