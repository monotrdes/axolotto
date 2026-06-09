# Plan: Refactorizar Taskboard Tool en estructura modular de componentes

> Generado por **deepclaude** · tarea `task-1780507395-3` · 2026-06-03T18:40:56.168178+00:00

## Descripción
el codigo del tool esta creciendo mucho, darle una nueva estructura en componentes y demás

## Análisis de impacto
Refactorización interna del tool taskboard. No toca backend principal (FastAPI), frontend Next.js, contratos, ni base de datos principal. Riesgo: romper funcionalidad existente del kanban (drag-drop, WebSocket, spawning de agentes). Mitigación: hacer refactor por etapas verificando cada módulo. El Dockerfile necesita ajuste si server.py deja de ser entrypoint único o si static files cambian de ubicación.

## Archivos a crear/modificar
- `tools/taskboard/server.py`
- `tools/taskboard/index.html`
- `tools/taskboard/Dockerfile`

## Checklist de criterios de aceptación
- [ ] server.py (1888 líneas) dividido en módulos: db.py, websocket.py, task_lifecycle.py, agent_runner.py, routes.py como entrypoint delgado
- [ ] index.html (2227 líneas) separado en archivos: styles.css, app.js, modules/task-card.js, modules/drag-drop.js, modules/websocket-client.js, modules/modal.js
- [ ] ai_router.py se integra como módulo interno del paquete taskboard, sin cambios funcionales
- [ ] rate_limiter.py se mantiene como utilidad compartida entre módulos
- [ ] WebSocket re-conecta al cliente tras refactorización JS sin pérdida de funcionalidad
- [ ] Drag-and-drop de tareas dependientes funciona igual que antes del refactor
- [ ] Sistema de columnas (6 etapas: wishes→concepts→planning→doing→review→done) intacto
- [ ] Dockerfile actualizado si cambian puntos de entrada o paths de módulos

## Propuestas / mejoras
- Agregar tests unitarios para cada módulo nuevo (db.py, task_lifecycle.py) — actualmente no hay tests del taskboard
- Considerar migrar de SQLite puro a SQLModel para consistencia con el stack del proyecto principal
- Separar agent_logs/ a un directorio de datos fuera del código fuente
- Agregar pyproject.toml o requirements.txt al tool para documentar dependencias (aunque use stdlib, para claridad)
- Evaluar extraer el frontend del taskboard a un micro-framework (Alpine.js, htmx) en vez de vanilla JS monolítico

## Notas de diseño
Estructura propuesta: tools/taskboard/ como paquete Python con __init__.py. Backend: routes.py (HTTP endpoints, thin), db.py (SQLite conexión + queries), task_lifecycle.py (máquina de estados de columnas), agent_runner.py (spawn de agy/claude CLI), websocket.py (manejo de conexiones). Frontend: static/ con CSS separado, app.js como entrypoint que importa módulos ES6 desde static/modules/. El server.py original queda como entrypoint delgado que ensambla los módulos. ai_router.py y rate_limiter.py se mantienen como módulos hermanos, importados por agent_runner.py. Orden de refactor: 1) extraer db.py (sin dependencias), 2) extraer task_lifecycle.py (depende de db), 3) extraer agent_runner.py (depende de ai_router + rate_limiter), 4) extraer websocket.py, 5) crear routes.py, 6) adelgazar server.py a entrypoint, 7) refactorizar frontend.

## Guía de verificación
1) Iniciar server: python tools/taskboard/server.py --port 8181. 2) Abrir http://localhost:8181 en navegador. 3) Verificar que cargan las 6 columnas con tareas existentes. 4) Crear nueva tarea en 'wishes', verificar que aparece y se persiste. 5) Mover tarea entre columnas con drag-drop, verificar que la secuencia dependiente se respeta. 6) Abrir modal de tarea, verificar campos. 7) Spawnear agente en tarea, verificar que el log aparece. 8) Verificar WebSocket: cambios en una pestaña se reflejan en otra sin recargar. 9) Verificar que Dockerfile construye y corre correctamente: docker build -t taskboard tools/taskboard && docker run -p 8181:8181 -v $(pwd):/repo taskboard.
