# Análisis y Diseño: Patrones de Victoria Expandidos, Dinámica de Doble Ganador y Modos Especiales (El Saladito y Eventos Complejos)

Este documento presenta el análisis, las propuestas de diseño y el plan de implementación para la tarea [task-1780815770-winning-patterns](file:///D:/Axolotto_2026/axolotto/tasks.json#L591). El objetivo es enriquecer el juego de Lotería tanto en el modo solitario (vs. CPU) como en el multijugador, introduciendo patrones clásicos de la Lotería Mexicana, una regla de "Doble Ganador", el ritual nocturno de "El Saladito" y eventos especiales de patrones complejos.

---

## 1. Catálogo Completo de Patrones de Victoria (4x4)

Se definen formalmente los conjuntos de índices (0 a 15) para los tableros de 4x4 en la base de datos y la lógica del motor de juego:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

### A. Patrones Rápidos (Tamaño = 4 celdas)
1. **Líneas (Línea)**: 
   - **Horizontales (4)**: `{0,1,2,3}`, `{4,5,6,7}`, `{8,9,10,11}`, `{12,13,14,15}`
   - **Verticales (4)**: `{0,4,8,12}`, `{1,5,9,13}`, `{2,6,10,14}`, `{3,7,11,15}`
   - **Diagonales (2)**: `{0,5,10,15}` (descendente), `{3,6,9,12}` (ascendente)
2. **El Pocito (Centro)**: `{5, 6, 9, 10}` (los 4 del centro del tablero).
3. **Las Esquinas (Esquinas)**: `{0, 3, 12, 15}` (las 4 esquinas exteriores).
4. **Cuadritos (Cuadrito)**: 9 bloques de 2x2. Por ejemplo, `{0, 1, 4, 5}`, `{5, 6, 9, 10}` (coincide con pocito), etc.

### B. Patrones Complejos (Tamaño = 7 a 10 celdas)
5. **La Cruz (Cruz)**:
   - **Cruz Recta (Ortogonal)**: Intersección de cualquier fila central y columna central. Existen 4 variantes posibles. Por ejemplo, Fila 1 + Columna 1 (intersección en 5): `{1, 4, 5, 6, 7, 9, 13}`.
   - **Cruz Diagonal (La X)**: Fusión de ambas diagonales. Tamaño = 8 celdas. Índices: `{0, 3, 5, 6, 9, 10, 12, 15}`.
6. **La L**: Fila exterior + columna exterior que se intersectan en una esquina. Existen 4 variantes posibles. Por ejemplo, Fila 3 + Columna 0: `{0, 4, 8, 12, 13, 14, 15}` (7 celdas).
7. **La Z**: Fila superior + diagonal derecha-izquierda + fila inferior. Existen 2 variantes.
   - Variante clásica: `{0, 1, 2, 3, 6, 9, 12, 13, 14, 15}` (10 celdas).
   - Variante espejo: `{0, 1, 2, 3, 5, 10, 12, 13, 14, 15}` (10 celdas).

### C. Patrón Completo (Tamaño = 16 celdas)
8. **Tabla Llena (Full Board)**: Las 16 celdas del tablero completadas.

---

## 2. Propuestas de Mejora y Expansión (Valor Agregado)

### 💡 Propuesta 1: Ajuste Dinámico de Elegibilidad del Jackpot
Actualmente, el Jackpot global de salas multijugador requiere ganar en los turnos **4, 5 o 6**. Sin embargo, esto es físicamente imposible para patrones complejos como **La Cruz (7 celdas)**, **La X (8 celdas)** o **La Z (10 celdas)**.
*   **Mejora**: Hacer que el rango de turnos elegibles para el Jackpot escale dinámicamente según el tamaño mínimo del patrón activo:
    - Patrones de 4 celdas (Línea, Pocito, Esquinas, Cuadrito): Turnos 4 a 6.
    - Patrones de 7 celdas (Línea L, Cruz Recta): Turnos 7 a 9.
    - Patrones de 8 celdas (La X): Turnos 8 a 10.
    - Patrones de 10 celdas (La Z): Turnos 10 a 12.
    - Tabla Llena (16 celdas): Turnos 16 a 20.

### 💡 Propuesta 2: Regla de "Doble Ganador" en Multijugador (Premio 1 + Premio 2)
Para evitar que los jugadores abandonen cuando alguien grita "¡Lotería!" temprano en la partida, el juego multijugador implementará por defecto la regla de dos premios:
1.  **Premio 1 (Premio del Patrón)**: Se otorga al primer jugador que complete el patrón activo (ej. Pocito o Esquinas). Equivale al **40% de la bolsa**.
2.  **Premio 2 (Premio de Tabla Llena)**: Una vez reclamado el Premio 1, la partida **continúa** y el gritón sigue cantando cartas. El primer jugador en completar su Tabla Llena gana el Premio 2 (**60% de la bolsa**).
3.  **Doble Corona**: Si el mismo jugador que ganó el Premio 1 logra llenar su tabla primero, se lleva ambos premios (100% de la bolsa).

### 💡 Propuesta 3: El Ritual del "Saladito" (Lotería Invertida)
Inspirado en los bingos tradicionales, introducimos un modo nocturno donde el objetivo del juego se invierte: **¡el jugador más salado (el de peor suerte) gana!**
*   **Activación:** Automáticamente todos los días de **3:00 AM a 4:00 AM (Server Time)**, o seleccionable en cualquier momento para salas privadas (`game_type = "saladito"`).
*   **Mecánica de Juego:**
    - Los jugadores marcan sus cartas de forma normal cuando son cantadas por el gritón.
    - El juego termina inmediatamente cuando el primer jugador **completa** el patrón objetivo (ej. una Línea o El Pocito). Ese jugador actúa como el "detonador" de la partida.
    - **El Ganador del Pozo:** El premio principal (100% de la bolsa de entrada) se otorga al jugador (o jugadores) que tenga la **menor cantidad de celdas marcadas** en su tablero al momento de terminar la partida (es decir, el jugador más "salado").
    - **Premio de Consolación:** El jugador que completó el patrón y terminó la partida recibe un pequeño reembolso o bono fijo de FRJ como compensación.
*   **El Poder de la Salinidad (SAL):**
    - En el motor físico de Axolotto, la salinidad (`stat_salinity`) determina la probabilidad de que una carta cantada "se escape" sin ser marcada (`sal_slip_chance`).
    - En una partida normal, tener SAL alta es un debuff perjudicial.
    - **En el Saladito, tener SAL alta es una bendición suprema**, ya que los escapes evitan que se marquen tus celdas. Esto genera un meta invertido divertidísimo, donde los Axolotitos con alta salinidad y bajo focus (normalmente ignorados) se vuelven los más valiosos y cotizados del mercado para este ritual nocturno.

### 💡 Propuesta 4: Eventos Especiales de Patrones Complejos (Copa del Cenote / Sorteo Mayor)
Para dar uso a los **Patrones Complejos** (La Cruz, La X, La L, La Z), que normalmente alargan demasiado las partidas rápidas cotidianas, creamos eventos especiales de alta tensión.
*   **Activación:** 
    - **Por Tiempo:** Una sala de evento especial abre automáticamente cada 4 horas.
    - **Por Jackpot:** Se activa de forma automática una "Copa del Cenote" en el lobby cuando el Jackpot acumulado global supera un umbral de **10,000 FRJ**.
*   **Mecánica:**
    - **Obligatoriedad de Patrón Complejo:** La sala sortea exclusivamente un patrón complejo (ej. La Z o La X).
    - **High-Stakes & Multiplicadores:** La entrada está fijada en apuestas altas (ej. multiplicador 5x o 10x).
    - **Subsidio de la Casa:** La plataforma inyecta un 20% extra al pozo final (bono acumulativo) y duplica la XP obtenida por los Axolotitos.
    - **Diseño Visual Premium:** La sala se renderiza en el lobby con un marco dorado brillante y una animación de partículas de agua. El tablero de juego muestra las celdas del patrón complejo con un brillo de neón púrpura o verde agua.

---

## 3. Resolución de Empates (Ties & Splits)

En un juego de azar en tiempo real como la Lotería, los empates ocurren cuando dos o más jugadores marcan la celda decisiva en el mismo turno de la carta cantada. Se definen las reglas para manejar estos casos:

1. **Empates en Premio 1 (Patrón):**
   - Si múltiples jugadores completan el patrón en el mismo turno, la porción del Premio 1 (40% de la bolsa) se **divide en partes iguales** entre todos los ganadores del patrón.
   - Todos los ganadores reciben el bono de XP completo para su Axolotito y Tabla.

2. **Empates en Premio 2 (Tabla Llena):**
   - Si múltiples jugadores llenan su tabla en el mismo turno, la porción del Premio 2 (60% de la bolsa) se **divide en partes iguales** entre todos ellos.
   - Todos los ganadores reciben el bono de XP completo.

3. **Empates en Modo "Saladito" (Menor Cantidad de Marcas):**
   - Al terminar la partida, si hay un empate en el valor de marcas mínimas (ej. dos jugadores empatan con solo 2 celdas marcadas), el pozo principal (100% de la bolsa) se **divide en partes iguales** entre los empatados.

4. **Empates en el "Detonador" del Saladito:**
   - Si dos jugadores completan el patrón de detención en la misma carta, ambos actúan como detonadores y reciben el premio fijo de consolación individual.

5. **Resolución de Empates vs. CPU (Singleplayer):**
   - Si el jugador humano y uno o más bots de la CPU completan el patrón en el mismo turno, **la victoria se otorga al jugador humano de forma prioritaria** (mecanismo clásico de retención y UX amigable).

---

## 4. Arquitectura del Flujo y Cambios Técnicos

### 🎮 A. Juego vs. CPU (Singleplayer)
Cuando el usuario presiona "Jugar" contra la CPU:
1.  El endpoint elige un patrón al azar de un pool de Patrones Rápidos.
2.  El motor de juego en `game_service.py` simula la partida verificando únicamente el patrón sorteado.
3.  El JSON de respuesta incluye `"target_pattern": "pocito"` y la lista de celdas correspondientes para que el frontend las dibuje.

### 👥 B. Juego Multijugador (Lobby & Salas de Jugadores)
*   **Esquema de Base de Datos:**
    - En `GameRoom.room_config`, añadir:
      - `game_type`: `"lotería_clásica" | "saladito"`
      - `win_pattern`: `"line" | "cuadrito" | "pocito" | "esquinas" | "cruz" | "l_shape" | "z_shape" | "full_board" | "random"`
      - `game_rule`: `"single_winner" | "double_winner"`
      - `special_event`: `boolean` (indica si es Copa del Cenote / Sorteo Mayor)

#### Lógica del Ciclo de Juego Invertido (Modo Saladito):
```
Gritón canta carta
  └─ Jugadores marcan celdas (sal_slip_chance puede hacer fallar la marca)
  └─ ¿Alguien completó el win_pattern?
       ├─ NO → Sigue el juego.
       └─ SÍ (Fin del Juego) →
           ├─ El que completó el patrón es catalogado como "Trigger" (Premio Consolación).
           ├─ Se evalúan los tableros de todos los participantes.
           ├─ Ganador(es) del Pozo = Jugadores con len(marked_indices) mínimo (aplica división si hay empate).
           └─ Distribuir bolsa y registrar en logs.
```

---

## 5. Plan de Implementación Paso a Paso

### Fase 1: Backend - Lógica de Negocio y Constantes (`game_logic.py`)
- Definir constantes de índices para todos los patrones (`WINNING_POCITO`, `WINNING_ESQUINAS`, `WINNING_CROSSES`, `WINNING_L_SHAPES`, `WINNING_Z_SHAPES`).
- Implementar la función `validate_win_pattern(marked_indices, called_card_ids, board_card_ids, pattern_name)`.
- Crear el validador especial para **El Saladito** que compute el jugador con el conteo mínimo de marcas al terminar la partida.

### Fase 2: Backend - Integración vs. CPU (`game_service.py`)
- Modificar `play_match()` para que al inicio seleccione un patrón al azar de los patrones rápidos.
- Soportar que si se inicia en la hora del "Saladito" (3:00 - 4:00 AM), las reglas vs. CPU apliquen la lógica inversa de menor cantidad de celdas para ganar.

### Fase 3: Backend - Integración Multijugador (`multiplayer_service.py`)
- En el loop de simulación del juego, evaluar si la sala está en modo `saladito` o `classic`.
- Aplicar la regla de Doble Ganador (Premio 1 = Patrón Complejo, Premio 2 = Tabla Llena) si `game_rule == "double_winner"`.
- Manejar empates de forma segura dividiendo el botín de la bolsa entre los ganadores del Premio 1, Premio 2 o Saladito.
- Manejar eventos especiales (`special_event`): inyectar el subsidio de la casa en el pozo de recompensas y aumentar el multiplicador de XP.
- Escalar el rango de turnos del Jackpot en base al tamaño del patrón.

### Fase 4: Backend - Endpoints y Esquemas (`multiplayer.py`)
- Modificar `CreateRoomRequest` para soportar `game_type` (con opción `"saladito"`), `win_pattern` (incluyendo los complejos) y `game_rule`.
- Añadir validación horaria automática para forzar modo "Saladito" en el lobby de 3:00 a 4:00 AM.

### Fase 5: Frontend - Interfaz de Hosting, Lobby y Tablero
- **`HostingSetupModal.tsx`**: Añadir toggle de "Modo Saladito" (con icono de salero 🧂) y dropdown de patrones (los complejos se marcan con insignia dorada 🏆).
- **`SalaSelectScreen.tsx`**: Renderizar salas de evento especial con marco dorado y salas de Saladito con color temático verde-azul salino.
- **`LoteriaBoard.tsx` & `PlayMode.tsx`**:
  - Resaltar las celdas del patrón complejo activo.
  - En modo Saladito, mostrar un contador visible de cuántas celdas tiene marcadas cada participante e indicar quién es el "Líder Salado" (menor marcas).

---

## 6. Pruebas y Validación
Se escribirán pruebas automatizadas en `backend/tests/unit/test_multiplayer_service.py` para asegurar que:
1.  En modo Saladito, el jugador con menor cantidad de marcas sea el que reciba el premio principal de la sala.
2.  La probabilidad de slip de salinidad (`sal_slip_chance`) funcione a favor del jugador en el modo Saladito.
3.  Los patrones complejos activen el rango de Jackpot dinámico correcto y que las recompensas extras se paguen correctamente en salas de evento especial.
4.  La división por empates distribuya correctamente el saldo exacto del pozo y prevenga race conditions en la base de datos al realizar las transacciones.
