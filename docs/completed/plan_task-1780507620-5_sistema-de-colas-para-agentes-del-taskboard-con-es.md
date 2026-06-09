# Plan: Sistema de colas para agentes del Taskboard con espera y reintento

> Generado por **deepclaude** · tarea `task-1780507620-5` · 2026-06-03T19:38:40.017217+00:00

## Descripción
sistema de colas, si ya se esta usando un agente y se solicita de nuevo, que espere a que se termine la tarea que esta ejecutando. si ninguno se pudo que se muestre que hubo error y haya boton de reintentar

## Análisis de impacto
Cambio localizado en tools/taskboard/. Se modifica spawn_agent() para usar cola por tipo de agente (claude/deepclaude). El flujo actual spawn_agent → _run thread se mantiene; se añade capa de cola que serializa ejecución. La función _run al terminar dispara dequeue del siguiente. El frontend ya tiene polling de agent_status cada 3s — se extiende para mostrar posición en cola. Riesgo bajo: no afecta backend del juego ni contratos. Riesgo medio: si la cola crece mucho sin workers disponibles, tareas se acumulan indefinidamente — mitigar con límite de cola (ej. 10 tasks) y mostrar advertencia.

## Archivos a crear/modificar
- `tools/taskboard/server.py`
- `tools/taskboard/index.html`

## Checklist de criterios de aceptación
- [ ] Al mover una tarea a 'doing', si el agente asignado ya está ejecutando otra tarea, la nueva tarea entra en cola de espera en lugar de fallar o spawnear un segundo proceso
- [ ] Cuando el agente termina su tarea actual (éxito o fallo), automáticamente procesa la siguiente tarea en la cola para ese mismo tipo de agente
- [ ] El frontend muestra estado de cola: posición en espera, tiempo estimado, y agente ocupado actualmente
- [ ] Si el agente falla al procesar una tarea encolada, se marca error en la tarjeta y aparece botón 'Reintentar' en el frontend
- [ ] El usuario puede cancelar una tarea en cola de espera (no iniciada aún) desde el frontend
- [ ] El endpoint GET /api/tasks incluye info de cola (_queue_position, _queue_agent) para tareas en espera
- [ ] La cola persiste entre reinicios del servidor (se reconstruye desde tareas en estado 'doing' sin agente activo al iniciar)

## Propuestas / mejoras
- Añadir límite máximo de cola (10 tareas) con mensaje 'Cola llena, intenta más tarde'
- Endpoint /api/queue/status para ver estado global de colas
- Badge visual en el kanban: '⏳ En cola #3 (Claude)' con tooltip
- Posibilidad de reasignar agente a una tarea en cola para balancear carga entre Claude y DeepClaude

## Notas de diseño
Cola implementada como dict Python en memoria: _agent_queues = {'claude': collections.deque(), 'deepclaude': collections.deque()}. Cada entrada: {'task_id': str, 'enqueued_at': float}. Al spawn_agent(): si _running_agents tiene entry para ese agent_type, hacer push a cola. Si no, spawnear directo. Al terminar _run (finally): pop de cola para ese agent_type, spawnear siguiente. Al iniciar servidor: escanear tareas 'doing' sin agente corriendo, encolar las que tengan assigned_to válido. Frontend: extender showRunningBanner() para tareas en cola mostrando posición y agente. Botón 'Cancelar espera' llama a POST /api/tasks/queue/cancel. Botón 'Reintentar' ya existe (retryDoingAgent) — verificar que funcione con cola.

## Guía de verificación
1. Iniciar taskboard: python tools/taskboard/server.py. 2. Crear 2 tareas asignadas a 'claude'. 3. Mover primera a 'doing' → verificar que agente inicia. 4. Mover segunda a 'doing' → verificar que aparece como 'En cola #1 (Claude)' en el frontend. 5. Esperar que primera termine → verificar que segunda inicia automáticamente. 6. Forzar fallo (matar proceso) → verificar botón Reintentar en tarjeta. 7. Cancelar tarea en cola → verificar que vuelve a 'planning'.
