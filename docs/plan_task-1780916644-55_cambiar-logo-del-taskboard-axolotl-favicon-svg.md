# Plan: Cambiar logo del taskboard: ðŸ‘¾ â†’ ðŸ¦Ž axolotl + favicon SVG

> Generado por **deepclaude** · tarea `task-1780916644-55` · 2026-06-08T11:05:03.133248+00:00

## Descripción
cambia el logo de taskboard

## Análisis de impacto
Cambio puramente cosmÃ©tico limitado a 2 archivos en tools/taskboard/. El HTML solo cambia el emoji del div.logo-axolotl (lÃ­nea 19). El favicon.svg se reescribe con un diseÃ±o de axolotl estilizado. CSS no requiere cambios porque las reglas existentes (cÃ­rculo con gradiente, animaciÃ³n pulse) son agnÃ³sticas al contenido. Sin impacto en backend, frontend, contratos ni lÃ³gica alguna.

## Archivos a crear/modificar
- `tools/taskboard/index.html`
- `tools/taskboard/favicon.svg`

## Checklist de criterios de aceptación
- [ ] El emoji del logo en el header refleja la temÃ¡tica axolotl (ðŸ¦Ž o diseÃ±o SVG custom)
- [ ] El favicon.svg tiene coherencia visual con el nuevo logo
- [ ] Los estilos CSS del .logo-axolotl siguen funcionando correctamente con el nuevo contenido
- [ ] No se rompe ningÃºn otro elemento del header ni la animaciÃ³n pulse

## Propuestas / mejoras
- Usar ðŸ¦Ž (lagartija) como emoji â€” es lo mÃ¡s cercano a un axolotl disponible en Unicode
- Alternativa: reemplazar el div emoji por un SVG inline de axolotl dentro del mismo .logo-axolotl para un look mÃ¡s profesional
- El favicon.svg deberÃ­a ser un axolotl estilizado en pixel-art o silueta simple para mantener consistencia con el diseÃ±o del taskboard

## Notas de diseño
El logo actual ðŸ‘¾ (space invader) no guarda relaciÃ³n con el proyecto Axolotto. La clase CSS se llama .logo-axolotl pero muestra un alien. El cambio mÃ¡s seguro es reemplazar el emoji por ðŸ¦Ž (U+1F98E) que es visualmente similar a un axolotl. Si se quiere mayor calidad, crear un SVG inline con la silueta de un axolotl y ajustar el CSS para que herede el gradiente. El favicon puede ser una versiÃ³n simplificada del mismo SVG. Mantener dimensiones actuales (40x40px logo, 32x32 favicon).

## Guía de verificación
1. Abrir tools/taskboard/index.html en navegador
2. Verificar que el logo en el header muestra el nuevo emoji/diseÃ±o (no ðŸ‘¾)
3. Confirmar que la animaciÃ³n pulse y el gradiente circular siguen funcionando
4. Verificar que el favicon en la pestaÃ±a del navegador muestra el nuevo diseÃ±o
5. Confirmar que el header mantiene su layout (tÃ­tulo, subtÃ­tulo, botones alineados)
