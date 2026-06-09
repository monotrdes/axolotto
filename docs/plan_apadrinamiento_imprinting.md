# Análisis y Diseño: Eclosión de Webitos Reales mediante Apadrinamiento (Imprinting)

Este documento presenta un análisis y diseño detallado para el sistema de eclosión de webitos reales (no-tutorial) mediante la dinámica de **Apadrinamiento** (o *Imprinting*). Se revisa el estado actual en el codebase, se proponen mejoras estructurales y se introducen ideas creativas para enriquecer la experiencia de juego, el balance de estadísticas y la conexión emocional entre el jugador y sus axolotitos.

---

## 1. Estado Actual en el Codebase

La base técnica de este sistema ya existe de forma parcial en el backend y frontend de Axolotto, estructurada en los siguientes componentes:

1. **Estructura del Modelo**:
   - `WebitoIncubation` (en [models/items.py](file:///D:/Axolotto_2026/axolotto/backend/app/models/items.py#L85-L105)) contiene campos dedicados al imprinting:
     - `imprinting_padrino_id`: Identificador del Axolotito padrino.
     - `imprinting_games_played`: Contador de partidas completadas con el padrino.
     - `imprinting_complete`: Flag booleano que indica que el proceso ha concluido.
     - `bonus_luck`, `bonus_focus`, `bonus_stamina`, `bonus_salinity_adj`: Acumuladores de las estadísticas moldeadas durante las partidas.
     - `base_stat_*`: Estadísticas base generadas al iniciar la incubación.

2. **Lógica de Negocio Pura**:
   - [imprinting_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/imprinting_service.py) define:
     - `required_games_for_rarity()`: Asigna partidas requeridas según la rareza (Común: 3, Raro: 5, Épico/Legendario: 7).
     - `initial_base_stats()`: Genera estadísticas base aleatorias dentro de rangos preestablecidos (Suerte: 20-50, Ojo/Focus: 25-55, Pila/Stamina: 70-110, Sal/Salinity: 10-30).
     - `compute_deltas()`: Calcula los deltas para cada estadística en base al resultado de la partida (`ImprintingGameResult`).
     - `apply_deltas_to_incubation()`: Incrementa `imprinting_games_played` y aplica los deltas limitándolos a ciertos límites acumulables (ej. ±50.0).
     - `final_stats()`: Suma base + delta para generar los valores definitivos al nacer.

3. **Invocación en Partidas (Solo Mode)**:
   - [incubation_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/incubation_service.py) contiene el helper `_apply_imprinting_if_needed`, el cual es llamado en [game_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/game_service.py#L413) al resolver partidas contra la CPU. Evalúa si el axolotito participante es padrino de algún huevo activo y actualiza los deltas.

4. **Flujo de Eclosión**:
   - El endpoint `POST /hatch/{incubation_id}` en [endpoints/incubation.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/incubation.py#L204) valida que el imprinting esté completo y llama a la función interna `_perform_hatch` (línea 262). Esta calcula los stats finales, genera una personalidad/naturaleza aleatoria, determina rasgos físicos basados en estadísticas y acuña el NFT correspondiente a través de `Web3Service`.

5. **Frontend**:
   - [ImprintingProgress.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/ImprintingProgress.tsx) provee un panel de hebras de ADN que animan los deltas tras cada partida y permite la selección del padrino.
   - [HatchSheet.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/santuario/HatchSheet.tsx) despliega la tarjeta del axolotito recién nacido tras la ceremonia.

---

## 2. Gaps Identificados y Áreas de Mejora

Se detectan los siguientes problemas y áreas de oportunidad en la versión base actual:

1. **Falta de Integración Multijugador (Multiplayer Gap)**:
   - **Problema**: `_apply_imprinting_if_needed` solo se invoca en partidas de un solo jugador (`game_service.py`). Si un jugador usa su Axolotito padrino en el Lobby Multijugador ([multiplayer_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/multiplayer_service.py)), la partida **no cuenta** para el imprinting del webito ni modifica sus estadísticas.
   - **Solución**: Hookear la llamada de imprinting al resolver partidas multijugador, asegurando paridad mecánica entre modos.

2. **Apadrinamiento Unidireccional (Sin beneficio al Padrino)**:
   - **Problema**: El padrino gasta energía en las partidas y guía al bebé, pero no recibe ninguna recompensa, bonus, ni reconocimiento por su esfuerzo de mentoría. Esto disminuye el valor del apadrinamiento a nivel de lore y de progresión.
   - **Solución**: Introducir un bonus del mentor (XP adicional, desbloqueo de rasgos de tutor o recarga de energía parcial) al completarse exitosamente la eclosión.

3. **Independencia Genética (Estadísticas Base Aleatorias)**:
   - **Problema**: `initial_base_stats()` genera números puramente aleatorios sin considerar los stats del padrino elegido. Un padrino con estadísticas nivel élite transmite exactamente la misma base genética que uno débil.
   - **Solución**: Implementar una fórmula de **herencia / mentoría de stats base**, donde un porcentaje de las estadísticas del padrino modifique positivamente el rango de los stats iniciales del webito.

4. **Flujo Visual Desconectado en el Cenote**:
   - **Problema**: El webito y el padrino se asocian mediante menús en una hoja de detalles (`EggSheet`), pero no existe una representación visual en la escena 2.5D del Cenote que muestre este lazo.
   - **Solución**: Dibujar un vínculo visual sutil (un lazo brillante o una animación del padrino cuidando del nido del huevo) cuando estén asignados en el hábitat.

---

## 3. Propuesta de Mejoras e Ideas Nuevas

Para convertir el apadrinamiento en una mecánica inolvidable y estratégica, proponemos las siguientes adiciones:

### A. Integración y Paridad en Todos los Modos de Juego
- **Multiplayer Hook**: Integrar la llamada de imprinting en [multiplayer_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/multiplayer_service.py) para que las salas hosteadas y las partidas oficiales cuenten hacia el imprinting de los jugadores humanos participantes.

### B. Herencia Genética e Influencia del Padrino (Stats Base)
Para premiar el esfuerzo de subir de nivel a un Axolotito, sus estadísticas influenciarán directamente la base del huevo:
- **Influencia de Mentoría**: Modificar `initial_base_stats()` para aceptar un parámetro `padrino`.
- **Fórmula de Stats Base**:
  $$\text{Base Final} = \text{Base Aleatoria (Rango Estándar)} + (\text{Stat Padrino} \times \text{Mentorship Factor})$$
  - El $\text{Mentorship Factor}$ será de **$0.10$** ($10\%$) para estadísticas normales y **$0.15$** ($15\%$) si el padrino es de nivel superior a 20.
  - Esto incentiva a los jugadores a usar a sus mejores Axolotitos como padrinos para asegurar mejores estadísticas base de inicio en sus nuevos huevos.

### C. Arquetipos de Mentoría (Estilos de Apadrinamiento)
Dependiendo de la personalidad/naturaleza del padrino, se alterarán las ganancias de estadísticas en las partidas del imprinting (multiplicador de delta):
1. **Mentor Suertudo** (*Lucky Nature*): Aumenta un $25\%$ el delta positivo de la estadística **Suerte** (Luck).
2. **Mentor Metódico** (*Methodical Nature*): Aumenta un $25\%$ el delta de **Ojo** (Focus).
3. **Mentor Hiperactivo** (*Hyperactive Nature*): Aumenta un $25\%$ el delta de **Pila** (Stamina).
4. **Mentor Glotón** (*Glutton Nature*): Otorga resistencia, reduciendo las pérdidas de stats en caso de derrota en un $20\%$.

### D. Retroalimentación Genética (Beneficio Permanente al Padrino al Eclosionar)
Cuando la ceremonia de eclosión se completa en `_perform_hatch`:
- **Incremento Permanente de Estadísticas**: El Padrino recibe un incremento permanente de **$+2.0$ puntos** en la estadística en la que el bebé acumuló el mayor delta de bonificación durante las partidas de imprinting. Esto representa la retroalimentación y aprendizaje mutuo durante el entrenamiento.
- **Límite de Apadrinamiento**: Para evitar inflación descontrolada de estadísticas, un Axolotito solo puede ser Padrino un máximo de **3 veces** a lo largo de su vida. Esto se rastrea mediante el campo `mentorship_count` (entero, por defecto 0) en el modelo `Axolotito`. Si `mentorship_count >= 3`, el Axolotito no puede ser seleccionado como padrino.
- **Relación de Mentoría**: El nuevo Axolotito nacido almacena el ID del padrino en el campo `tutored_by_id` para conservar el registro histórico y habilitar diálogos o interacciones visuales futuras.
- **Recompensa de Experiencia**: El padrino recibe adicionalmente $+150\text{ XP}$ de forma permanente.

### E. Apoyo Visual durante la Partida (Sideline Cheering)
- **El Huevo en el Tablero**: Cuando el jugador está jugando una partida con un Axolotito que es padrino activo, el Webito aparece flotando en una pequeña burbuja animada al lado del tablero del jugador.
- **Reacciones Dinámicas**:
  - Si el jugador marca una casilla correctamente: el huevo salta y emite chispas brillantes.
  - Si el jugador pierde una carta o falla: el huevo tiembla sutilmente.
  - Al ganar la partida: el huevo da vueltas de alegría en su burbuja.

### F. Ceremonia de Eclosión Enriquecida (Bestowment)
- En el paso 6 de la ceremonia cinematográfica de eclosión, añadir la frase de lore descriptiva de la mentoría:
  > *"Bajo la sabia tutela de **[Nombre del Padrino]**, este pequeño Webito aprendió el arte de la Lotería. Juntos jugaron **[N]** partidas, heredando su gran determinación."*

---

## 4. Plan de Implementación Técnica (Roadmap)

### Fase 1: Backend Core (Herencia y Multiplayer)
1. **Modificar `initial_base_stats`**:
   - Ajustar firma en [imprinting_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/imprinting_service.py#L58) para recibir los stats del padrino y calcular el incremento genético.
   - Pasar el padrino en `start_imprinting` en [endpoints/incubation.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/incubation.py#L535).
2. **Implementar Hook Multijugador**:
   - Importar `_apply_imprinting_if_needed` en [multiplayer_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/multiplayer_service.py).
   - Recorrer a todos los participantes humanos al resolver una partida, comprobando si su Axolotito es padrino de algún huevo activo y aplicando el imprinting correspondiente.
3. **Agregar Recompensa en `_perform_hatch`**:
   - Otorgar XP al padrino si `imprinting_padrino_id` está configurado.
   - Registrar la relación de mentoría en el modelo del Axolotito (campo opcional `tutored_by_id` o similar).

### Fase 2: Ajuste de Balances (Arquetipos de Mentoría)
1. **Multiplicadores de Delta por Naturaleza**:
   - Actualizar `compute_deltas` para tomar en cuenta la naturaleza del padrino, aplicando el modificador del arquetipo.
2. **Unit Tests**:
   - Escribir tests unitarios en `tests/unit/test_imprinting_service.py` para validar la fórmula de herencia genética y los modificadores de arquetipos.

### Fase 3: Frontend (Visuales y Feedback)
1. **Lazo del Cenote**:
   - En [NidoScene.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/santuario/NidoScene.tsx) o [SpotFluido.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/santuario/SpotFluido.tsx), si un spot contiene un huevo con padrino asignado, mostrar un icono o glow especial conectándolo visualmente al spot del padrino.
2. **Burbuja de Apoyo en PlayMode**:
   - Si la partida actual activa el imprinting, renderizar la burbuja del huevo animado en la pantalla de juego.
3. **Frase de Mentoría en Eclosión**:
   - Ajustar el paso de texto de origen en [HatchSheet.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/santuario/HatchSheet.tsx) para plasmar el mensaje de agradecimiento y aprendizaje con el mentor.

---

## 5. Vinculación con Tareas del Proyecto

Este diseño se vincula con la siguiente tarea del Taskboard de Axolotto:
- **Task ID**: [task-1780820796-35](http://localhost:8181/#/concepts)
- **Título**: `concepts: Apadrinamiento e Imprinting de Webitos Reales`
- **Categoría**: `gamedesign` / `game`
- **Asignado**: `AGY` (Game design, economía, balance, análisis)
- **Documento Técnico de Referencia**: [plan_apadrinamiento_imprinting.md](file:///D:/Axolotto_2026/axolotto/docs/plan_apadrinamiento_imprinting.md)
