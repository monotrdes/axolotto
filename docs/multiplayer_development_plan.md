# Plan de Desarrollo: Reestructuración Multijugador (Auto & Manual)

Este documento detalla el plan de desarrollo, fases y listas de verificación para implementar el juego multijugador interactivo y espectador en Axolotto, con un enfoque en la extensibilidad de las reglas de juego y la seguridad de las divisas.

---

## 1. Diseño Técnico de Extensibilidad: Detección de "Casi Victoria"

Para asegurar que el sistema de tensión ("¡A una carta de ganar!") funcione con cualquier regla futura (líneas de 4, esquinas, cuadritos, cruz o tabla llena), implementaremos un **algoritmo genérico basado en operaciones de conjuntos de índices (0-15)**.

### Algoritmo de Tensión Genérico:
Definimos los patrones de victoria como una lista de conjuntos de índices.
```python
# Ejemplo de patrones en backend
WIN_PATTERNS = {
    "line": [{0, 1, 2, 3}, {4, 5, 6, 7}, ...], # Líneas
    "cuadrito": [{0, 1, 4, 5}, {1, 2, 5, 6}, ...], # Cuadritos
    "full_board": [{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}] # Tabla llena
}
```

Implementamos una función en el backend que calcula cuántas cartas le faltan a un tablero para completar cualquier patrón activo en la sala:
```python
def check_tension_status(marked_indices: set[int], active_patterns: list[set[int]]) -> int:
    """
    Retorna el número mínimo de cartas restantes para completar algún patrón ganador.
    Si retorna 1, el jugador está 'A una carta' de cantar Lotería (Tensión Máxima).
    """
    if not active_patterns:
        return 99
    
    # Calcular la diferencia de conjuntos por cada patrón activo
    remaining_cards_per_pattern = [
        len(pattern - marked_indices) 
        for pattern in active_patterns
    ]
    
    return min(remaining_cards_per_pattern)
```

### Ventajas:
* **Extensible:** Si en el futuro se añade un patrón de "Cruz" o "Esquinas", simplemente se añade a la lista de patrones de la sala. El motor de tensión detecta automáticamente cuándo falta 1 o 2 cartas sin modificar una sola línea de código lógico.
* **Cliente/Servidor Unificado:** Esta misma lógica se puede programar en TypeScript en el frontend para activar efectos visuales de forma instantánea sin esperar peticiones de red.

---

## 2. Fases de Desarrollo y Lista de Verificación

El desarrollo se divide en **4 fases incrementales**.

### FASE 1: Motor de Patrones y Auditoría de Divisas (Backend Core)
*Objetivo: Sentar las bases lógicas y asegurar que el juego sea legal y compatible con las reglas actuales.*

- [ ] **Estructura de Patrones:** Implementar `check_tension_status` en `backend/app/services/game_logic.py`.
- [ ] **Auditoría de Custodia (Escrow):** Auditar `backend/app/api/v1/endpoints/multiplayer.py` para asegurar que todas las operaciones y cobros validen estrictamente `Wallet.frijolitos` (alias `gemas_alga`) y bloqueen cualquier intento de uso de `axofichas` (AXF).
- [ ] **Consistencia de Nombres:** Añadir comentarios y documentación en la base de datos aclarando que las columnas `bot_budget_axg` y `bot_loss_limit_axg` almacenan Frijolitos (FRJ) por compatibilidad heredada.

### FASE 2: WebSockets y Lógica en Tiempo Real (Modo Manual)
*Objetivo: Crear el canal bidireccional y el servidor de juego en vivo.*

- [ ] **Servidor WebSocket:** Crear endpoint de WebSockets en `backend/app/api/v1/endpoints/multiplayer_ws.py` usando FastAPI.
- [ ] **Matchmaking Loop Manual:** Diseñar la transición automática del lobby al estado de juego en vivo cuando la sala se llene o expire el timeout.
- [ ] **Gritón Broadcast (Dealer):** Lógica del dealer en tiempo real que emite la carta cantada a todos los clientes conectados cada $N$ segundos (ej. 4s).
- [ ] **Validador de Lotería:** Endpoint/evento WebSocket `cantar_loteria` que reciba los índices del cliente y los valide usando `check_tension_status` == 0.

### FASE 3: Espectador Live e Interpolación de Tiempo (Modo Auto)
*Objetivo: Permitir que los usuarios vean el progreso en tiempo real de sus Axolotitos bots.*

- [ ] **Estado de Partida Activa:** Guardar el trace de cartas y timestamps del juego automático en una caché temporal (o tabla de base de datos) al iniciar el match.
- [ ] **Endpoint de Sincronía:** API `/api/v1/multiplayer/room/{room_id}/live` que retorne las cartas cantadas hasta el segundo actual.
- [ ] **Interpolador de Animación:** En el frontend, leer el estado e interpolar la animación para que coincida exactamente con el progreso real en el servidor.

### FASE 4: Frontend Interactivo y Efectos de Tensión (UX/UI)
*Objetivo: Integrar el cliente interactivo, los avatares proxy y los efectos de tensión.*

- [ ] **Tablero Manual Interactivo:** Crear pantalla de juego en tiempo real que permita hacer clic en las casillas y valide de forma local aciertos/errores.
- [ ] **Representación de Avatar Proxy:** Mostrar el Axolotito NFT elegido del jugador en pantalla reaccionando a las acciones del jugador (acierto = felicidad, error = frustración, casi-victoria = emoción).
- [ ] **Feedback Visual de Tensión:**
  - Latido cardíaco en los bordes de la pantalla (vignette roja/oro pulsante) cuando `check_tension_status` == 1.
  - Aceleración del tempo de la música ambiental en el frontend.
  - Sonido de redoble de tambor al estar a una carta de ganar.
- [ ] **Badge de Asignación en Kanban:** Asignar el agente encargado (`deepclaude`) y configurar el taskboard.
