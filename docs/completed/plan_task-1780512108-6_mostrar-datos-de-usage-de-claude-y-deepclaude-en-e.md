# Plan: Mostrar datos de /usage de Claude y DeepClaude en el frontend del Taskboard

> Generado por **deepclaude** · tarea `task-1780512108-6` · 2026-06-03T18:47:42.554929+00:00

## Descripción
cambios en tool taskboard: para revisar uso de claude y deepclaude debes entrar a cada uno y ejecutar /usage, sacar datos de lo impreso y mostrarlo en front

## Análisis de impacto
Cambio mínimo: solo se añade HTML/CSS/JS en index.html. El backend (server.py) ya expone GET /api/usage con toda la lógica de parseo. No se toca backend, ai_router.py, rate_limiter.py ni Dockerfile. Riesgo: nulo — es solo UI adicional que consulta un endpoint existente.

## Archivos a crear/modificar
- `tools/taskboard/index.html`

## Checklist de criterios de aceptación
- [x] Añadir botón/sección en el header o rate-limit-bar para consultar usage de ambos providers
- [x] Al hacer clic, llamar GET /api/usage (ya existe en server.py) y mostrar los datos parseados
- [x] Mostrar costos totales (USD), tokens (input/output/cache read/cache write), duración (API/wall), líneas añadidas/eliminadas
- [x] Manejar caso en que un provider no esté disponible (binary not found, timeout, error)
- [x] Mostrar timestamp de cuándo se refrescaron los datos (refreshed_at)
- [x] Incluir botón para refrescar manualmente los datos de usage

## Propuestas / mejoras
- Auto-refrescar usage cada 60s mientras el modal/panel esté abierto
- Añadir mini-gráfico de barras para tokens (input vs output) para comparativa visual rápida
- Persistir histórico de usage en SQLite para ver tendencias (fuera de alcance, pero valioso a futuro)

## Notas de diseño
Añadir una sección colapsable '📊 Usage Report' en el header (debajo de rate-limit-bar) o un modal dedicado. Al abrirse/expandirse, hace fetch a /api/usage. Muestra dos cards lado a lado (Claude y DeepClaude) con los campos parseados: Total Cost, Tokens (input/output/cache r/w), Duration (API/wall), Code changes (±lines). Si un provider falla, mostrar mensaje de error específico. El endpoint ya devuelve {claude: {...}, deepclaude: {...}, refreshed_at: '...'}. Usar los mismos estilos CSS del taskboard (variables, gradients, cards).

## Guía de verificación
1. Abrir http://localhost:8181. 2. Hacer clic en el botón '📊 Usage' en el header. 3. Verificar que aparecen datos de Claude y DeepClaude (o mensaje de error si algún binary no está disponible). 4. Verificar que los campos de tokens, costos, duración y líneas se muestran correctamente. 5. Hacer clic en 'Refrescar' y verificar que se actualizan los datos y el timestamp.
