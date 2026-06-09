# Game Design Document (GDD) & Technical Plan: Cave Decorations in Axolotto
**Santuario Cenote: Personalización con Propósito y Beneficios Dinámicos**
*Autor: Antigravity AI × Experto en UX & Game Design*
*Fecha: 2026-06-07 | Estado: Confirmado y Aprobado*

---

## 1. Visión UX: Sistema de Anclajes Predefinidos (Anchor Slots) - *CONFIRMADO*

Para garantizar una experiencia fluida y visualmente armoniosa en dispositivos móviles y de escritorio, implementaremos de forma definitiva el **Sistema de Anclajes por Capas** en lugar de coordenadas libres:

```
┌─────────────────────────────────────────────────────────────┐
│ [W1] (Wall)               [CEILING]            [W2] (Wall)  │  ← Capa Fondo
│                                                             │
│         [WT1] (Water)              [WT2] (Water)            │  ← Capa Media
│                                                             │
│    [NIDO 1]           [ MESA DE JUEGO ]          [NIDO 2]   │  ← Capa Mesa
│                                                             │
│   [F1] (Floor)           [SP1] (Special)        [F2] (Floor) │  ← Capa Suelo
└─────────────────────────────────────────────────────────────┘
```

*   **Distribución:** Cada nivel de cueva habilitará puntos de anclaje preestablecidos en el plano. Esto elimina la superposición con Axolotitos nadando o nidos de incubación.
*   **Flujo:** Tocar un anclaje abre la lista de ítems compatibles en el cajón inferior para equipar/desequipar con un solo tap.

---

## 2. Clasificación de Ítems (Subcategorías)

| Subcategoría | Anclaje | Ejemplos de Items | Propósito Estético |
| :--- | :--- | :--- | :--- |
| **WALL** (Pared) | Pared rocosa trasera | Musgo bioluminiscente, Estandartes VIP. | Ambientación y color. |
| **FLOOR** (Piso) | Suelo de piedra | Camitas de algas, estatuas, cofres. | Confort y soporte. |
| **WATER** (Flotante) | Columna de agua | Lirios luminosos, juguetes flotantes. | Dinamismo y verticalidad. |
| **SPECIAL** (Interactivo) | Puntos fijos de gran tamaño | Rockola de coral, Gabinete Arcade, Calentador. | Funcionalidades y minijuegos. |

---

## 3. Beneficios Mecánicos & Sistema de Tope Variable (Variable Cap)

Para evitar la inflación en la economía del juego y mantener atractiva la progresión, los límites máximos (caps) de las bonificaciones serán **variables y escalables**:

### A. Bono de Regeneración de Foco (Focus Recovery Boost)
*   *Origen:* Camitas y sofás de suelo (`FLOOR`).
*   *Límite Variable:* Escalado de acuerdo al **Nivel de la Cueva (`cave_level`)**.
    *   *Fórmula del Tope:* `Tope Foco = 10% + (cave_level * 5%)`
    *   *Ejemplo:* En el nivel 1 el tope de regeneración es **15%**. Si el jugador expande su cueva al nivel 8, el tope aumenta a **50%**. Esto incentiva al jugador a expandir la cueva para desbloquear el verdadero potencial de sus muebles cómodos.

### B. Bono de Multiplicador de Staking FRJ (Staking Multiplier)
*   *Origen:* Estatuas, tótems y reliquias en suelo/pared.
*   *Límite Variable:* Escalado de acuerdo a la **Cantidad de Axolotitos Activos (`active_axolotitos`)** en la cueva.
    *   *Fórmula del Tope:* `Tope Staking = active_axolotitos * 3.5%`
    *   *Ejemplo:* Si el usuario tiene 2 Axolotitos en staking, el tope máximo de bono por decoraciones es **7%**. Si llena la cueva al nivel 8 con 8 Axolotitos, el tope sube a **28%**. Esto premia la colección de personajes y evita que un jugador con un solo Axolotito abuse de multiplicadores altos acumulando estatuas.

### C. Bono de Incubación (Incubation Thermal Boost)
*   *Origen:* Calentadores bioluminiscentes (`SPECIAL`).
*   *Límite Variable:* Fijo en un máximo de **+20%** de velocidad de incubación por cueva para salvaguardar los timers del Hatchery.

---

## 4. Ítems Interactivos & Sinks de Tokens (FRJ Burn / AXF Sink)

Los objetos de tipo `SPECIAL` no solo darán bonos pasivos, sino que ofrecerán minijuegos interactivos diseñados para quemar moneda o monetizar microtransacciones:

### A. Minijuegos Quemadores de Frijolitos (FRJ-Burning Games)
*   *Objeto:* *Mini-Gashapon oxidado* o *Pozo de los Deseos*.
*   *Mecánica:* Minijuegos basados en habilidad o azar con retorno esperado menor al 100% (estadísticamente deficitarios).
    *   *Ejemplo (Pozo de los Deseos):* El jugador lanza **20 FRJ** al pozo. Debe presionar un botón justo cuando una burbuja cruza un aro (quick-time event).
        *   *Éxito Perfecto:* Recupera **30 FRJ** o recibe un componente común de booster.
        *   *Fallo:* Pierde los 20 FRJ.
        *   *Propósito:* Actúa como un sumidero divertido y dinámico para combatir la inflación de Frijolitos de forma voluntaria.

### B. Arcade Subacuático (AXF Micro-Sink & Social Flex)
*   *Objeto:* *Gabinete Arcade de Algas* (Estilo Retro).
*   *Mecánica:* Minijuegos clásicos sencillos y adictivos sin recompensa económica directa (evitando regulaciones de apuestas).
    *   *Costo de Juego:* **1 AXF** (Aprox. $0.17 MXN) por partida.
    *   *Elemento Social:* El Arcade mantiene una **Tabla de Puntuaciones Locales (Local Scoreboard)** visible para cualquiera que visite el Cenote de ese usuario.
    *   *Flujo de Juego:* Los amigos que visitan la cueva vía `POST /visit/{user_id}` pueden gastar 1 AXF para intentar superar el récord del dueño.
    *   *Propósito:* Un excelente generador de monetización de muy bajo costo y alto valor social / competitivo (vanity scoreboard).

---

## 5. Diseño de Arquitectura Técnica

### A. Estructura de Catálogo (`ItemCatalog`)
```json
{
  "subcategory": "FLOOR",
  "placement_rules": {
    "can_rotate": true,
    "can_flip_x": true
  },
  "bonuses": {
    "focus_regen_multiplier": 0.05,
    "frj_staking_multiplier": 0.02
  }
}
```

### B. Representación de Cueva del Usuario (`User.cave_decorations`)
Se almacena en el campo de texto JSON de la base de datos:
```json
{
  "slots": {
    "floor_1": { "item_id": 105, "placed_at": "2026-06-07T11:45:00.000Z", "flip_x": false },
    "wall_1": { "item_id": 204, "placed_at": "2026-06-07T11:45:00.000Z", "flip_x": true }
  }
}
```

### C. Nuevos Endpoints en Backend
1.  **`POST /api/v1/cave/decorations/update`:** Valida inventarios, límites de slots por nivel y guarda el JSON.
2.  **`POST /api/v1/cave/arcade/play`:** Descuenta 1 AXF de la cartera del jugador y registra el inicio de partida para reportar puntuaciones.
3.  **`POST /api/v1/cave/wishing-well/throw`:** Valida y descuenta 20 FRJ para iniciar la ronda del pozo.

---

## 6. Plan de Implementación Phased

1.  **FASE 1: API Backend & Cálculo de Topes Variables (Backend):** Implementar la lógica de guardado y el cálculo dinámico de límites de bonificación basados en `active_axolotitos` y `cave_level`.
2.  **FASE 2: Canvas de Decoración & Anclajes (Frontend):** Construir la UI del Cenote con anclajes fijos e interfaz drawer de inventario.
3.  **FASE 3: Integración de Minijuegos (Arcade & Pozo):** Codificar las mecánicas simples de juego en el frontend y los endpoints de cobro (1 AXF / 20 FRJ) en el backend.
