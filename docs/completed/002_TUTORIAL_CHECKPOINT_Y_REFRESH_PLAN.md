# Plan de Implementación: Guardado de Estado por Acto y Saludos Dinámicos en Refresh

Este plan describe los cambios propuestos para mejorar el sistema de guardado de estado en el tutorial del Axolotito, resolviendo el problema de que el usuario es redirigido directamente a la partida 1 si recarga la página al inicio, y añadiendo saludos dinámicos basados en la personalidad (nature) si recarga la página repetidamente en el Acto 1.

## Proposed Changes

### Backend

#### 1. items.py
- Añadir el campo `tutorial_act_index: int = Field(default=0)` al modelo `WebitoIncubation`.

#### 2. main.py
- En el evento de startup (`on_startup`), añadir `("tutorial_act_index", "INTEGER DEFAULT 0")` a la lista de columnas que se agregan de manera dinámica a `webitoincubation` si no existen.

#### 3. tutorial.py (Endpoints)
- Retornar `tutorial_act_index` en la respuesta de `/start` (tanto para tutoriales nuevos como ya iniciados).
- Crear un nuevo endpoint `POST /save-act/{incubation_id}` que acepte un body con `{ "act_index": int }` y lo persista en la base de datos.

#### 4. tutorial_service.py
- Reiniciar `tutorial_act_index` a `0` en `start_tutorial`.
- Actualizar `tutorial_act_index` en cada cambio de fase de `advance_phase`:
  - Fase 1 → 2 (Post Game SAL): `tutorial_act_index = 5` (Acto 6 OJO).
  - Fase 2 → 3 (Post Game OJO): `tutorial_act_index = 6` (Acto 7 SUERTE+PILA).
  - Fase 3 → 4 (Post Game SUERTE): `tutorial_act_index = 7` (Acto 8 KARMA).
- Actualizar `tutorial_act_index = 11` en `complete_tutorial`.

#### 5. dev.py (Dev Tools)
- Reiniciar `tutorial_act_index` a `0` cuando un desarrollador resetee el tutorial en `/reset-tutorial`.

---

### Frontend

#### 1. dialogues.ts
- Implementar la función `getAct1RefreshLines(nature: Nature, count: number): string[]` que retorne:
  - 1 a 4 refrescos: Una sola línea personalizada de saludo según la naturaleza del Webito.
  - 5 o más refrescos: Una secuencia de 2 líneas ("Tu Webito se durmió..." y la línea de despertar según naturaleza).

#### 2. ActDialogueScene.tsx
- Aceptar el prop `refreshCount?: number`.
- Si `actId === "acto-1-presentacion"` y `refreshCount` es mayor que 0, usar `getAct1RefreshLines(webito.nature, refreshCount)` en lugar de `ACT1_INTRO_LINES`.

#### 3. TutorialFlow.tsx
- Cargar `tutorial_act_index` desde la respuesta de `/start`.
- Calcular `startAct`: `freshStart ? 0 : (data.tutorial_act_index ?? resumeActIndex(phase))`.
- Si se reanuda en el acto 0 y no es `freshStart`, incrementar un contador `axolotto_tutorial_refresh_count` en `localStorage` y guardarlo en el estado React como `refreshCount`.
- Si se avanza a un acto posterior al 0, limpiar `axolotto_tutorial_refresh_count` del `localStorage`.
- Implementar la función `saveActIndex(index: number)` para llamar a `/tutorial/save-act/{id}` de manera asíncrona.
- En la función `advance()`, además de incrementar el `actIndex`, llamar a `saveActIndex(nextIndex)`.
- Si se detecta un auto-skip de actos por condiciones en el `useEffect`, también llamar a `saveActIndex(idx)`.
