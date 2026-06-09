# Plan: Auditar docs/ y crear tasks pendientes para cada gap detectado en el Taskboard

> Generado por **deepclaude** · tarea `task-1780522775-9` · 2026-06-03T21:41:32.667112+00:00

## Descripción
revisa la carpeta docs y analiza todo, si encuentras tareas sin hacer, crea las tasks

## Análisis de impacto
Tarea de tools pura. No modifica backend FastAPI, frontend Next.js ni contratos Solidity. Solo crea registros INSERT en tasks.db vía API REST del taskboard (POST /api/tasks/create en localhost:8181). Lectura de docs/ estáticos y tasks.db existente vía sqlite3. Riesgo nulo para el ecosistema del juego. Esta tarea es orquestación y catalogación — el output son ~15-20 tasks nuevas en el Kanban.

## Archivos a crear/modificar
- `tasks.db`

## Checklist de criterios de aceptación
- [ ] Leer todos los archivos en docs/ (raíz) y docs/completed/ para catalogar todo el trabajo pendiente
- [ ] Cruzar hallazgos con tasks.db existentes — detectar gaps (ítems sin task) y plan_task huérfanos
- [ ] Crear tasks para FASE 0 (Seguridad Pre-Mainnet): SEV-15, constraints BD, tx_hash validation, auditoría externa, monitoreo, verificación PRIVY
- [ ] Crear tasks para FASE 1 (Polygon Amoy): deploy de contratos, actualizar addresses, flip del switch
- [ ] Crear tasks para FASE 2 (MercadoPago + On-Ramp): módulo MP, endpoints, webhook, store UI + Ramp/MoonPay pendientes
- [ ] Crear tasks para FASE 3 (Retiros DevEx): modelos BD, withdrawal_service, endpoints admin, UI WithdrawalPage
- [ ] Crear task para FASE 5 (Cenote 2.5D + Simulador CPU) como entry point, referenciando MASTER_PLAN_CRIADERO.md
- [ ] Crear tasks para FASE 6 (CI/CD + Playwright + reorganización tests)
- [ ] Crear tasks para FASE 7 (F2P WebSocket espectador + Daily Bounties)
- [ ] Crear tasks para quick wins del vip_club_panel_auditoria.md (R1-R4 redundancia, endpoint tiers, Modo A redesign)
- [ ] Crear tasks para pendientes del task_board_workflow_plan.md (E2E tests, webhooks, métricas, hotkeys)
- [ ] Resolver plan_task huérfanos: task-1780503272 (Toast smoke test) crear task; task-1780507349-3 marcar como superseded por task-1780512108-6 ya done
- [ ] Excluir tridyland_migracion_plan.md (proyecto externo, no Axolotto). Excluir MASTER_PLAN_CRIADERO.md fases 2-6 del batch inicial (solo Fase 1 como entry point)
- [ ] Reportar tabla final: total tasks creadas, gaps cubiertos, omisiones justificadas

## Propuestas / mejoras
- Agrupar tasks por prefijo de fase en el título: [FASE0], [FASE1], [FASE2], etc. para trazabilidad visual en el Kanban
- Para vip_club_panel_auditoria.md: crear UNA task 'Rediseño VIP Panel (Modo A + fuente única)' que cubra todo §9.2-§9.6 en vez de atomizar los 17 hallazgos
- Para MASTER_PLAN_CRIADERO.md: crear solo task 'Fase 1: Refactor modelo de datos del Criadero (cave_level, spots fluidos)' como entry point; referenciar fases 2-6 en descripción para no saturar el board con 30+ tasks
- Marcar task-1780507417-4 (concepts, 'sugerir modelo en planning') como superseded — cubierto por la lógica actual de ai_router.py que ya sugiere modelos. O crear task de cierre.
- Las propuestas creativas del Game Designer (Cosmic Shell, Nesting Guilds, Ink Stamping, Invasión) no son accionables aún — solo anotar en comentario de task FUTURE o crear una task 'Wish' en wishes

## Notas de diseño
Flujo del agente: (1) Leer tasks.db vía python3 -c sqlite3 para obtener todas las tasks existentes con status. (2) Leer docs/ raíz (000_PLAN_GLOBAL_PENDIENTES.md, MASTER_PLAN_CRIADERO.md, vip_club_panel_auditoria.md, task_board_workflow_plan.md) y docs/completed/ para contexto. (3) Construir matriz: fuente del pendiente × task existente. (4) Para cada gap detectado, hacer POST /api/tasks/create al taskboard en localhost:8181. Parámetros: title ≤80 chars con prefijo de fase, description con resumen del scope + referencia al doc fuente, category y priority según fase del plan global. (5) Para plan_task huérfano task-1780503272: crear task 'Sistema de Toast notifications (Smoke test)' en wishes o concepts. (6) Para plan_task huérfano task-1780507349-3: crear comentario en task-1780512108-6 indicando que lo cubre. (7) Crear tasks agrupadas por fase y complejidad: las fases grandes (FASE 2 MercadoPago, FASE 3 Retiros) pueden ser 2-3 tasks cada una para mantener granularidad manejable. (8) Reportar tabla final con conteo, gaps cubiertos, y omisiones justificadas. (9) Al terminar, mover este plan doc a docs/completed/.

## Guía de verificación
1. python3 -c "import sqlite3; conn=sqlite3.connect('tasks.db'); [print(f'{r[0]} | {r[2]} | {r[1][:70]}') for r in conn.execute('SELECT id, title, status FROM tasks ORDER BY created_at DESC LIMIT 25')]" — deben aparecer 15-20+ tasks nuevas. 2. Abrir http://localhost:8181 — las nuevas tarjetas deben verse en columna Wishes o Concepts con prefijos [FASE0], [FASE1], etc. 3. Verificar que no hay gaps grandes sin cubrir: FASE 0-7 del plan global deben tener al menos 1 task cada una. 4. Verificar que vip_club tiene task creada. 5. Verificar que taskboard pendientes (E2E, webhooks, métricas, hotkeys) tienen tasks. 6. Verificar que task-1780503272 (Toast) tiene task creada. 7. Verificar que tridyland NO tiene task creada. 8. Contar total ≥15 tasks nuevas.
