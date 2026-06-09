# Game Design Document (GDD) & Technical Plan: Chat & Reactions in Axolotto
**Fomentando la retención social mediante comunicación contextualizada**
*Autor: Antigravity AI × Experto en UX & Game Design*
*Fecha: 2026-06-07 | Estado: Propuesta para Revisión*

---

## 1. Análisis del Dilema de Diseño (UX vs. Ritmo de Juego)

La Lotería es un juego de ritmo rápido: se canta una carta cada 3-5 segundos. Si obligamos al jugador a escribir texto libre en un teclado durante el juego manual, creamos una experiencia de **alta fricción y penalización**:
- El jugador se distrae escribiendo → pierde el marcado de una carta → su Axolotito se duerme o se distrae.
- El chat se convierte en una fuente de frustración en lugar de diversión.

### La Solución: Comunicación en Tres Niveles de Tensión
Diseñamos un sistema híbrido adaptativo según el estado de la partida y el tipo de sala:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       SALA DE JUEGO (MULTIPLAYER)                       │
├──────────────────────────┬──────────────────────────┬───────────────────┤
│    FASE DE ESPERA        │    FASE ACTIVA (JUEGO)   │    FIN DE PARTIDA │
│    (Lobby de Sala)       │   (Tensión de Cartas)    │    (Scoreboard)   │
├──────────────────────────┼──────────────────────────┼───────────────────┤
│ • Chat de texto libre    │ • Chat manual: Desactiv. │ • Chat de texto   │
│ • Emojis y Stickers      │ • Quick-Reaction Wheel   │   libre y emotes  │
│ • Selección de Tablas    │ • Chat Auto/Espectador   │ • Felicitaciones  │
│                          │   de texto libre (AFK)   │   automáticas     │
└──────────────────────────┴──────────────────────────┴───────────────────┘
```

1. **Fase de Espera (Pre-game Lobby):** Chat de texto libre completo + envío de Stickers. Los jugadores socializan mientras la sala se llena.
2. **Fase Activa (Active Gameplay):**
   - **Jugadores Manuales:** El chat de texto se colapsa. Se comunican mediante la **Rueda de Reacciones Rápidas (Quick-Reaction Wheel)** de un solo tap (duración < 200ms).
   - **Jugadores Automáticos (AFK / CPU) y Espectadores:** Tienen acceso a un feed de chat completo y colapsable en el lateral. Como no tienen que marcar manualmente, pueden debatir y socializar activamente.
3. **Fase de Finalización (Post-game Scoreboard):** Se reactiva el chat de texto libre para celebrar o lamentar los resultados ("GG", "¡Casi!", "Revancha").

---

## 2. Definición del Entorno: Salas Públicas vs. Privadas

Para proteger la economía Web3 y evitar el abuso, la toxicidad y los enlaces fraudulentos (phishing de wallets), aplicamos reglas de seguridad diferenciadas por el tipo de sala:

| Característica | Salas Públicas (Multijugador Estándar) | Salas Privadas (Con Amigos) |
| :--- | :--- | :--- |
| **Acceso a Chat de Texto** | **Limitado/Moderado:** Solo frases predefinidas + texto libre filtrado por regex contra URLs, insultos y spam. | **Abierto:** Texto libre sin restricciones severas (filtro opcional para insultos graves). |
| **Moderación Automática** | Activa (Auto-mute de 5 mins en caso de spam o palabras ofensivas repetidas). | Ninguna (los usuarios controlan su propia sala). |
| **Stickers & Emojis** | Permitidos todos los desbloqueados. | Permitidos todos los desbloqueados. |
| **Integración Web3** | Bloqueo estricto de direcciones hexadecimales (`0x...`) para evitar scams de firmas de transacciones. | Advertencia visual sutil al escribir hashes, pero permitido. |

---

## 3. Integración en el Cenote 2.5D (UX Visual)

En lugar de un chat flotante flotando sobre la pantalla que tape el tablero, el chat se integra de forma inmersiva en el entorno 2.5D:

### A. Globos de Texto sobre los Asientos (Bubble Chats)
* Cuando un jugador (o bot) envía un mensaje o reacción, emerge un globo de texto con **estilo glassmorphism** directamente encima del `TableSeat` de su Axolotito en la mesa circular.
* **Comportamiento visual:**
  * El globo aparece con una animación de rebote acuático (escala de `0` a `1.0` con rebote).
  * Flota ligeramente hacia arriba (efecto de burbuja ascendente en el cenote).
  * Desaparece (fade-out) tras 3.5 segundos.
  * Si el mensaje contiene emojis, estos se renderizan un 40% más grandes que el texto.

### B. Barra de Reacción Rápida (Reaction HUD)
* Situada a un costado del tablero del jugador en el HUD frontal.
* Un botón circular con cara de Axolotito sonriente. Al hacer tap, despliega una **Rueda Radial** con 6 ranuras configurables:
  * 3 Emojis/Stickers rápidos.
  * 3 Frases predefinidas ajustadas a la naturaleza de su Axolotito.

### C. Feed de Historial Lateral (Collapsible Chat Feed)
* Ubicado en la esquina inferior izquierda (o derecha en móviles horizontales) de forma semi-transparente.
* Permite ver el historial de las últimas 5 líneas de conversación.
* Se puede colapsar a un simple ícono de notificación con indicador numérico.

```
       [ 🪸 Coral-User: ¡Casi gano! ]  <-- Globo flotante (glassmorphism) sobre el Axolotito
               (  O.O  )
              /========= \
             /  [Tabla]   \
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
  
    ┌─────────────────────────┐
    │ [✨ Gold-User]: GG!     │  <-- Feed lateral flotante, semi-transparente
    │ [🤖 Bot-Pedrito]: Casi..│
    └─────────────────────────┘
```

---

## 4. Gamificación, VIP Club e Integración de "Natures"

El chat de Axolotto no es solo funcional; es una extensión de la identidad del jugador y su economía.

### A. Beneficios por Niveles VIP (Monetización Directa)
Teniendo en cuenta el diseño de `vip_club_design.md`, el estatus VIP del propietario se refleja en cada mensaje:
* **🪸 Pase Coral:** Acceso a emojis animados básicos de Axolotl.
* **✨ Pase Dorado:**
  * Globos de texto en juego con **borde dorado shimmer** y tipografía estilizada.
  * Acceso a 4 Stickers exclusivos del tier.
* **🌟 Pase Axolite:**
  * **Nombre de usuario dorado en el chat feed** con partículas bioluminiscentes.
  * Globos de texto premium (gradiente oro-rosa-morado con micro-partículas flotando).
  * Badge de corona VIP al lado del nombre en el feed.

### B. Adaptación por Personalidad (Natures) del Axolotito
Las frases rápidas predefinidas de la Rueda de Reacciones cambian dinámicamente según la **naturaleza** del Axolotito activo en la mesa:

| Personalidad | Frase: Saludo | Frase: Presión (Casi gano) | Frase: Derrota | Efecto Visual en Chat |
| :--- | :--- | :--- | :--- | :--- |
| **Hiperactivo** | "¡HOLA A TODOS! ⚡" | "¡¡A UNA CARTA!! AAAH 🔥" | "¡Grrr, revancha ya! 💢" | Tipografía negrita, texto tiembla y suelta chispas amarillas. |
| **Tímido / Calmado**| "hola... 💧" | "estoy cerca... creo" | "ni modo, felicidades" | Tipografía pequeña, texto flota lento con burbujas azules. |
| **Presumido** | "Llegó el rey. 👑" | "Ya pueden irse a casa 😎" | "Estaba arreglado." | Tipografía elegante, cae confeti dorado sutil sobre el globo. |
| **Curioso** | "¿Listos para perder? 🔍" | "¿Qué carta falta? ¡Ah!" | "Interesante jugada..." | Tipografía monospace, iconos de lupa girando. |

### C. Fregadero de Tokens (Token Sinks)
Para apoyar la economía de quemado de FRJ (Frijolitos):
1. **Megáfonos de Sala (Room Megaphones):** Enviar un mensaje destacado en color brillante que se quede fijo en la parte superior del feed por 10 segundos cuesta **10 FRJ**.
2. **Tienda de Stickers:** Los jugadores pueden comprar paquetes de stickers temáticos en la tienda (diseñados por la comunidad o artistas de Axolotto) usando FRJ o AXG.

---

## 5. Arquitectura Técnica & Eventos WebSocket

La comunicación se gestiona sobre la conexión WebSocket existente en `ws_manager.py` y `game_ws.py`.

### A. Nuevos Eventos de Entrada (Cliente → Servidor)
Cuando un jugador envía un chat o reacción:

```json
{
  "action": "chat_message",
  "data": {
    "text": "¡Lotería o muerte! 🔥",
    "is_reaction": false,
    "sticker_id": null,
    "megaphone": false
  }
}
```

### B. Eventos de Salida (Servidor → Todos los Clientes en la Sala)
El servidor sanitiza, valida el saldo (si es megaphone), extrae el VIP/Nature del jugador y propaga el mensaje:

```json
{
  "type": "chat_broadcast",
  "data": {
    "player_id": "usr-9812",
    "username": "AxoMaster",
    "vip_tier": "axolite",
    "nature": "hiperactivo",
    "text": "¡Lotería o muerte! 🔥",
    "sticker_id": null,
    "megaphone": false,
    "timestamp": 1780832015
  }
}
```

### C. Lógica de Servidor (Python/FastAPI)
1. **Sanitización:** Uso de un filtro regex y biblioteca de censura de palabras. Bloqueo de URLs que no pertenezcan al dominio permitido (`axolot.to`).
2. **Rate-Limiter:** Límite de 1 mensaje cada 1.5 segundos por cliente (excepto reacciones rápidas que se agrupan o tienen cooldown visual de 1s en cliente).
3. **Cobro de FRJ:** Si `megaphone` es `true`, validar saldo en DB (`SELECT FOR UPDATE` en billetera) y descontar 10 FRJ antes de difundir.

---

## 6. Plan de Implementación (Hoja de Ruta Phased)

Dividimos el desarrollo en 4 fases incrementales para asegurar estabilidad y evitar regresiones en el modo CPU.

### 📋 FASE 1: Core de Backend & WebSocket Protocol
* **Objetivo:** Preparar la infraestructura de datos para mensajería en tiempo real.
* **Tareas:**
  1. Modificar `backend/app/services/ws_manager.py` para procesar el evento `"chat_message"`.
  2. Implementar sanitización básica (censor de insultos y URLs) en un nuevo servicio `backend/app/services/chat_moderator.py`.
  3. Integrar la lectura de `vip_tier` desde la sesión del usuario para inyectarla en el broadcast.
  4. Agregar tests de WebSocket para validar que el broadcast envía la información correcta de VIP y Nature.

### 📋 FASE 2: UI de Rueda de Reacción Rápida & Globos 2.5D
* **Objetivo:** Implementar la UX visual interactiva en la mesa del cenote.
* **Tareas:**
  1. Crear el componente `QuickReactionWheel.tsx` en el frontend, controlado por un botón en el HUD.
  2. Crear el componente `SpeechBubble.tsx` que flote sobre los `TableSeat` correspondientes al `player_id`.
  3. Modificar `CenoteRoom.tsx` y `TableSeat.tsx` para suscribirse a los eventos de chat entrantes y renderizar los globos dinámicos.
  4. Configurar las animaciones CSS en `frontend/app/globals.css` para el rebote y desvanecimiento de burbujas.

### 📋 FASE 3: Chat Feed Colapsable & Lobby de Sala
* **Objetivo:** Permitir conversación de texto libre en momentos de bajo estrés.
* **Tareas:**
  1. Implementar el componente `ChatFeed.tsx` (lista con scroll y modo colapsado/expandido).
  2. Habilitar la caja de texto libre en el Waiting Room (antes de iniciar partida) y en el Scoreboard final.
  3. Validar la restricción del teclado durante la partida activa para jugadores manuales.
  4. Añadir el filtro de spam y rate limit visual en el cliente.

### 📋 FASE 4: Personalizaciones de Nature & Tienda de Stickers
* **Objetivo:** Añadir el "juice" y monetización al sistema de comunicación.
* **Tareas:**
  1. Configurar las frases rápidas en `frontend/data/personality-config.ts` adaptadas a cada `nature`.
  2. Añadir los estilos visuales premium (borde dorado, gradiente Axolite, partículas animadas) a los globos de texto.
  3. Integrar la compra del "Megáfono" (10 FRJ) llamando al endpoint del banco de transacciones del backend.
  4. Diseñar y renderizar los primeros 4 stickers animados para VIPs y tienda.

---

## 7. Próximos Pasos Recomendados

Para proceder con esta tarea, se sugiere el siguiente flujo de acción:
1. **Aprobación de Diseño:** Validar si se desea comenzar la fase de backend en la rama actual o crear una nueva sub-tarea para la Fase 1.
2. **Revisión de Recursos:** Asegurar que los endpoints del banco existentes soporten el cobro directo de FRJ por acciones in-game (Megáfonos).
3. **Probar prototipos de animación:** Validar las burbujas CSS en el Cenote actual.
