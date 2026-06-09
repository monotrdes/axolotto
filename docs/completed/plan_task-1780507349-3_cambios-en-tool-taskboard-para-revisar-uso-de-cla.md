# Plan: cambios en tool taskboard: para revisar uso de cla...

> Generado por **claude** · tarea `task-1780507349-3` · 2026-06-03T17:23:35.505185+00:00

## Descripción
cambios en tool taskboard: para revisar uso de claude y deepclaude debes entrar a cada uno y ejecutar /usage, sacar datos de lo impreso y mostrarlo en front

## Análisis de impacto
Bajo impacto. Cambios autónomos en el módulo taskboard. Se agrega 1 endpoint GET /api/usage que ejecuta subprocess contra los binarios CLI (operación bloqueante, ~2-5s). Se agrega sección UI en la rate-limit-bar o panel dedicado. No modifica endpoints existentes ni lógica de negocio. Riesgo: si los binarios no existen o timeout, el endpoint debe devolver datos parciales sin crashear.

## Archivos a crear/modificar
- `tools/taskboard/server.py`
- `tools/taskboard/index.html`

## Checklist de criterios de aceptación
- [ ] Backend: agregar endpoint GET /api/usage que ejecute `claude /usage` y `deepclaude /usage`, parseando la salida en JSON estructurado para cada proveedor
- [ ] Backend: manejar graceful fallback cuando el binario no existe o falla (ej. deepclaude no instalado), devolviendo unavailable + error
- [ ] Backend: agregar un botón en la UI para refrescar los datos de usage on-demand (no polling automático, es una operación lenta)
- [ ] Frontend: mostrar panel de usage en la barra superior (rate-limit-bar) o en una sección dedicada, con costo total, tokens input/output/cache, duración y líneas de código cambiadas por cada proveedor
- [ ] Frontend: mostrar indicador visual de si los datos son frescos o stale (timestamp del último refresh)
- [ ] Mantener consistencia con estilos existentes (CSS variables, tema oscuro, model-claude/model-deepclaude gradients)

## Propuestas / mejoras
- Cachear resultado de /usage por 30-60s para evitar spam de subprocess en refrescos repetidos
- Agregar toggle en UI para refresh automático cada 5min (útil en sesiones largas de desarrollo)
- Mostrar diff entre dos snapshots de usage ("desde el último refresh") para ver consumo incremental de la sesión actual
- Agregar columna de costos acumulados por provider en la sección de rate limits ya existente

## Notas de diseño
Endpoint /api/usage: ejecuta `claude /usage` y `deepclaude /usage` vía subprocess.run(timeout=10), parsea cada línea con regex (clave: valor). Devuelve JSON: {"claude": {"available": true, "total_cost": "$0.0000", "total_duration_api": "0s", "total_duration_wall": "0s", "code_changes_added": 0, "code_changes_removed": 0, "usage_input": 0, "usage_output": 0, "usage_cache_read": 0, "usage_cache_write": 0, "error": null, "fetched_at": "ISO"}, "deepclaude": {...}}. Si binario no existe, available=false con error descriptivo. Frontend: sección colapsable en header o al lado de rate-limit-bar. Estilos reutilizan CSS variables existentes + model-claude/model-deepclaude gradients. Botón 'Refresh Usage' dispara fetch a /api/usage y actualiza el panel.

## Guía de verificación
1. Iniciar taskboard server: cd tools/taskboard && python server.py
2. Abrir http://localhost:8181 en navegador
3. Verificar que la sección de usage aparece (con botón 'Refresh Usage')
4. Hacer clic en 'Refresh Usage' — debe mostrar datos de claude (costos, tokens, etc.)
5. Verificar que deepclaude muestra 'unavailable' si no está instalado, o datos si sí lo está
6. Abrir consola del navegador, verificar que GET /api/usage devuelve JSON válido sin errores 500
7. Ejecutar `curl http://localhost:8181/api/usage | jq` para inspeccionar estructura JSON
