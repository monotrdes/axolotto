# 📋 Plan: Explicación de Tablas y Creación del "Acta de Nacimiento" en el Tutorial

> **ID de Tarea**: `task-1781063373-71`  
> **Estado**: 📝 PROPUESTO (En Columna `planning`)  
> **Objetivo**: Integrar la explicación didáctica de que las tablas de Lotería se componen de una selección de cartas del mazo general, y renombrar formalmente la primera tabla del Webito como su "Acta de Nacimiento" (vinculada a su ADN).

---

## 1. Introducción y Concepto

En la versión actual de la Lotería de Axolotto:
1. El jugador obtiene un Webito (huevo) cuyo ADN se traduce determinísticamente en estadísticas y en una tabla de 16 posiciones.
2. Sin embargo, no se explica de forma explícita al jugador novato que **la Tabla (el tablero de juego 4x4) está compuesta por un subconjunto de 16 cartas seleccionadas a partir del mazo estándar de 54 cartas de Lotería**.
3. Al eclosionar el Webito, se le asigna esta tabla en la base de datos bajo el nombre genérico `"Tabla Tutorial"`.

### Nueva Propuesta Educativa y Narrativa:
* **El Concepto de la Tabla:** Durante el **Acto 3 (Board Preview)**, el Webito explicará didácticamente que las tablas son plantillas formadas por 16 cartas únicas.
* **El "Acta de Nacimiento":** La primera tabla que recibe el Webito no es una tabla cualquiera: es su **Acta de Nacimiento**. Nace directamente de la combinación de genes (ADN) del huevo y será su identidad inicial en el juego.

---

## 2. Plan de Cambios en Frontend

### A. Nuevos Diálogos Didácticos (`frontend/components/tutorial/dialogues.ts`)

Modificaremos `ACT3_BOARD_INTRO` en `frontend/components/tutorial/dialogues.ts` para que cada personalidad del Webito introduzca explícitamente:
- Que la tabla es su **"Acta de Nacimiento"**.
- Que la tabla se compone de **16 cartas extraídas de la baraja total de 54**.

#### Propuesta de Diálogos Actualizados:

```typescript
export const ACT3_BOARD_INTRO: Record<Nature, string> = {
  hyperactive: 
    "¡¡MIRA!! ¡¡ESTA ES MI TABLA!! Es mi 'Acta de Nacimiento' oficial. " +
    "¿Sabías que una tabla se forma eligiendo 16 cartas de las 54 del mazo total? " +
    "¡Y esta combinación nació única gracias a mi ADN! ¡Juguemos una demo ya ya ya!",

  lucky:       
    "Esta es mi tabla del destino, que también es mi 'Acta de Nacimiento'. " +
    "Representa 16 cartas seleccionadas especialmente para mí de entre las 54 de la baraja. " +
    "La suerte eligió una gran combinación. Hagamos una demo.",

  salty:       
    "Esta es mi tabla. Básicamente es mi 'Acta de Nacimiento'. " +
    "Son 16 cartas elegidas al azar de un mazo de 54, decididas por mi ADN. " +
    "A ver si el Gritón canta las mías hoy o si la mala suerte me persigue. Márcalas.",

  methodical:  
    "Generando mi 'Acta de Nacimiento'. Este objeto representa una tabla de juego, " +
    "la cual consiste en una matriz de 16 cartas seleccionadas del conjunto universal de 54 naipes. " +
    "Su composición deriva directamente de mi secuencia de ADN. Iniciando demostración.",

  shy:         
    "Esta es mi tabla... la llaman 'Acta de Nacimiento' porque se genera con mi ADN. " +
    "Son 16 cartas del mazo de 54 que me acompañarán siempre. " +
    "¿Me ayudas a marcar las mías en esta prueba?",
};
```

---

### B. Ajustes Visuales en el Tablero (`frontend/components/tutorial/acts/ActBoardPreview.tsx`)

1. **Título de la Fase Intro:** Cambiaremos el título estático de la fase `intro` en `ActBoardPreview.tsx` para reforzar la identidad del Acta de Nacimiento.
   - *Antes:* `Tu Tabla del Destino — generada de tu ADN`
   - *Después:* `📜 Acta de Nacimiento — Tu Tabla Inicial (16 de 54 Cartas)`
2. **Subtítulo o Indicador Visual:** Se puede añadir una etiqueta flotante o un pequeño indicador con tooltip debajo del título explicando brevemente la regla:
   > *"Una Tabla de Lotería contiene 16 cartas aleatorias del mazo completo. La tuya está vinculada genéticamente a este Axolotito."*

---

## 3. Plan de Cambios en Backend

### A. Renombrar Tabla en la Creación (`backend/app/services/tutorial_service.py`)

Cuando el tutorial se completa con éxito, el backend ejecuta `TutorialService.complete_tutorial` y crea el registro `PlayerBoard` correspondiente.

Modificaremos la inicialización en `tutorial_service.py`:

```python
# ANTES:
tutorial_board = PlayerBoard(
    user_id=user_id,
    name="Tabla Tutorial",
    card_ids=tutorial_board_card_ids,
    card_first_editions=[False] * 16,
    is_tutorial=True,
)

# DESPUÉS:
tutorial_board = PlayerBoard(
    user_id=user_id,
    name="Acta de Nacimiento", # <-- Renombrado didáctico
    card_ids=tutorial_board_card_ids,
    card_first_editions=[False] * 16,
    is_tutorial=True, # Mantiene la bandera de tutorial para las validaciones de negocio
)
```

> [!NOTE]
> Dado que todos los endpoints y servicios de validación (`board_service.py`) como la prohibición de venta, desarmado y renta de la tabla de inicio utilizan la propiedad `board.is_tutorial` y no el campo string `name`, cambiar el nombre de `"Tabla Tutorial"` a `"Acta de Nacimiento"` es **100% seguro** y no romperá las reglas de negocio de la economía.

---

## 4. Plan de Pruebas

Para asegurar la correcta integración:
1. **Prueba de Flujo de Interfaz:** Iniciar el tutorial desde el frontend en modo de desarrollo, llegar al Acto 3 y validar que los diálogos de las personalidades y los títulos reflejen el nuevo texto didáctico del Acta de Nacimiento y las 16/54 cartas.
2. **Eclosión y Verificación de BD:** Terminar el tutorial simulado, provocar la eclosión, y verificar en la base de datos (PostgreSQL/SQLModel) que el `PlayerBoard` resultante tenga `name="Acta de Nacimiento"` y esté asignado al axolotito creado.
3. **Ejecución de Test Suite:** Correr `pytest backend/tests/test_tutorial_service.py` para asegurar que las aserciones no fallen por este cambio narrativo.

---

## 5. Próximos Pasos (Fase de Desarrollo)
Una vez que el usuario apruebe este plan en la columna **Planning**, la tarea se moverá a **Doing** y procederemos a la edición de los archivos correspondientes en frontend y backend.
