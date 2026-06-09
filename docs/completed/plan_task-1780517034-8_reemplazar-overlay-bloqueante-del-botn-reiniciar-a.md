# Plan: Reemplazar overlay bloqueante del botón Reiniciar Axo por loading inline en el botón

> Generado por **deepclaude** · tarea `task-1780517034-8` · 2026-06-03T20:04:57.737065+00:00

## Descripción
al pulsar el boton de reiniciar axo, el loading debe verse en ese botón, que no me bloquee la pantalla, cuando termine que avise con un indicador

## Análisis de impacto
Cambio cosmético de UX en una sola función JS (restartAxo) y CSS. No afecta server.py ni endpoints. Sin riesgo de regresión funcional. El polling de salud sigue igual, solo se quita showLoading(true/false) y se añaden clases CSS temporales al botón para feedback visual.

## Archivos a crear/modificar
- `tools/taskboard/index.html`

## Checklist de criterios de aceptación
- [ ] Al pulsar Reiniciar Axo, NO se muestra el overlay fullscreen bloqueante (showLoading)
- [ ] El spinner y texto de carga se muestran DENTRO del botón (ya existe .spinner-mini, verificar que funcione)
- [ ] El taskboard sigue usable durante el reinicio: columnas, modales, otros botones responden
- [ ] Al completar con éxito, el botón muestra indicador visual de éxito (animación pulse/color verde breve) + toast existente
- [ ] Al fallar o timeout, el botón muestra indicador visual de error (animación shake/color rojo breve) + toast existente
- [ ] El botón permanece disabled durante el proceso para evitar doble click
- [ ] La barra de header sigue siendo interactiva (Recargar, Usage, Nueva Idea funcionan durante el reinicio)

## Propuestas / mejoras
- Añadir indicador de progreso estimado en tooltip del botón (ej: 'Reiniciando... (intento 5/40)')
- Si el health check responde antes del timeout con 503 (arrancando), mostrar estado 'Backend iniciando...' en vez de solo spinner genérico
- Considerar un sonido sutil o Notification API al completar para cuando el usuario está en otra pestaña

## Notas de diseño
Modificaciones en index.html: (1) Borrar línea 2194 showLoading(true,...). (2) Borrar líneas 2207,2217,2227 showLoading(false). (3) Añadir 3 clases CSS: .btn-restarting (opacity reducida + cursor wait), .btn-restart-success (bg verde 2s + pulse), .btn-restart-error (bg rojo 1s + shake). (4) En restartAxo(): aplicar btn.classList.add('btn-restarting') al inicio, reemplazar con btn-restart-success o btn-restart-error al terminar, con setTimeout para limpiar clases tras animación. (5) btn.disabled = true se mantiene. (6) No tocar server.py ni ai_router.py.

## Guía de verificación
1. Abrir taskboard en navegador. 2. Pulsar 'Reiniciar Axo'. 3. Confirmar diálogo. 4. Verificar que NO aparece overlay gris bloqueante. 5. Verificar que botón muestra spinner-mini + 'Reiniciando...'. 6. Hacer click en 'Recargar' o 'Usage' — debe funcionar. 7. Esperar a que backend responda (o forzar timeout). 8. Verificar animación de éxito/error en botón + toast. 9. Verificar que botón vuelve a estado normal.
