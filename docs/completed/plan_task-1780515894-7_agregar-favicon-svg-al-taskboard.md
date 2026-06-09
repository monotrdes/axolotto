# Plan: Agregar favicon SVG al Taskboard

> Generado por **deepclaude** · tarea `task-1780515894-7` · 2026-06-03T19:51:13.481392+00:00

## Descripción
agregar un favicon al taskboard tool

## Análisis de impacto
Cambio cosmético mínimo. Se toca el <head> de index.html (1 línea), el handler estático de server.py (1 elif para image/svg+xml), y se crea un archivo SVG nuevo. Sin riesgo funcional. El handler estático ya sirve archivos desconocidos con text/plain, pero browsers pueden ignorar favicon con MIME incorrecto — se agrega el content-type correcto.

## Archivos a crear/modificar
- `tools/taskboard/index.html`
- `tools/taskboard/server.py`

## Checklist de criterios de aceptación
- [ ] Crear archivo favicon.svg en tools/taskboard/ con diseño representativo del Taskboard
- [ ] Agregar <link rel="icon"> en <head> de index.html apuntando a /favicon.svg
- [ ] Agregar content-type image/svg+xml en handler de archivos estáticos de server.py
- [ ] El favicon se muestra en la pestaña del navegador sin errores 404 en consola

## Propuestas / mejoras
- Usar SVG inline con emoji 🎴 o diseño geométrico simple — evita dependencia externa
- Diseñar con colores del tema (--doing-color #ff9f43 o --planning-color #a55eea) para consistencia visual
- Considerar también un favicon.ico como fallback para navegadores viejos

## Notas de diseño
SVG inline simple (32x32 viewBox) con formas geométricas que evoquen columnas Kanban. Colores del tema oscuro (#080911 bg, accent #ff9f43). El handler estático en server.py línea 1014-1022 solo tiene content-types para .html/.css/.js/.json — agregar `elif file_path.endswith('.svg'): content_type = 'image/svg+xml'`. El <link> va después del <title> en index.html línea 6.

## Guía de verificación
1. Iniciar server: python3 tools/taskboard/server.py. 2. Abrir http://localhost:8181 en navegador. 3. Verificar que el favicon aparece en la pestaña (no el ícono default de página). 4. Abrir DevTools > Network, filtrar por 'favicon', confirmar status 200 y MIME image/svg+xml. 5. Verificar que no hay errores 404 en consola.
