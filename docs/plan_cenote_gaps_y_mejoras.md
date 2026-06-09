# Plan de Refinamiento: "Mi Cenote" (ex-Criadero) — Gaps, Mejoras y Progresión

Este documento detalla el análisis del flujo del nuevo criadero de Axolotitos, la propuesta de renombre, el estado actual de la implementación, los gaps técnicos pendientes y una serie de propuestas premium para enriquecer la experiencia de usuario.

---

## 1. Propuesta de Redefinición y Nombre

> **Propuesta:** Cambiar el nombre del módulo de **"Criadero"** / **"Santuario"** a **"Mi Cenote"** (o simplemente **"Cenote"**).
> 
> * **Justificación Narrativa:** "Criadero" (Hatchery) suena a producción industrial o comercial, lo cual choca con la idea de crear un vínculo emocional con los Axolotitos NFT. "Santuario" es aceptable, pero **"Mi Cenote"** es íntimo, místico y se alinea perfectamente con la ambientación subacuática de la península de Yucatán y el lore de Axolotto.
> * **Justificación de UX:** Refuerza la idea de que la cueva no es solo una pantalla de inventario de mascotas, sino **el hogar del jugador en el metaverso**, donde además hostea sus partidas de Lotería en su propia mesa física.

---

## 2. Flujo Conceptual Unificado

El Cenote es una caverna personal que evoluciona verticalmente a lo largo de **8 niveles**:

```
        ┌────────────────────────────────────────────┐
        │         ☀️ SUPERFICIE (Luz Cenital)         │
        │  ≈≈≈ rayos de luz ≈≈≈ burbujas ≈≈≈≈≈≈≈≈≈  │
        │                                             │
        │   🦎 Axolotitos nadando libremente          │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │     ZONA DE VIDA (Spots Fluidos)  │      │
        │  │  🥚/🦎  🥚/🦎  🥚/🦎  🥚/🦎     │      │
        │  │  Nidos adaptables (Incubación    │      │
        │  │  o Descanso según se requiera)   │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │     🎴 MESA DE HOSTING (Lvl 3+)   │      │
        │  │  [Tablero] [Cartas] [Fichas]     │      │
        │  │  Hostea con tus reglas custom    │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │  🏆 EXHIBICIÓN + 👥 VISITANTES    │      │
        │  │  (Entrada de la cueva — Abajo)    │      │
        │  │  Trofeos, Axo Estrella, Likes    │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        └────────────────────────────────────────────┘
              ↑ Entrada de visitas por la parte profunda (inferior)
```

---

## 3. Estado de Avance: Planificado vs. Implementado

### 3.1 Lo que ya está Listo (Backend & Frontend)
- [x] **Base de Datos:** Campos `cave_level` (User), `cave_decorations` (User JSON) y campos en `GameRoom` (`host_id`, `room_config`, `visibility`, `password_hash`) integrados en Alembic.
- [x] **Endpoints Backend:**
  - `GET /cave/status` y `POST /cave/expand` (con lógica de cobro en FRJ y cálculo de tiempos).
  - `POST /cave/expand/accelerate` (aceleración por AXF a razón de 4 AXF/hora).
  - `POST /multiplayer/create-room` (hosting de sala con reglas custom y comisión de host).
- [x] **Interfaz 2.5D (Santuario.tsx):**
  - Renderizado en canvas 2.5D con capas verticales (Superficie arriba, Entrada abajo).
  - Componente interactivo `SpotFluido` con 3 modos: Vacío, Incubando huevo (EggSheet) o Descansando (AxoSheet).
  - Toggle de "Gestionar" para alinear a los Axolotitos en sus lechos y facilitar su cuidado en mobile.
  - Mesa de juego en 2.5D que invoca el modal `HostingSetupModal.tsx` para configurar partidas.

---

## 4. Gaps Críticos por Resolver (Lo que falta)

Para completar la **Fase 1 y 2 del MVP**, restan implementar los siguientes puntos técnicos:

### 4.1 Backend
1. **Auto-resolución del Timer de Excavación:**
   * *Gap:* Cuando el jugador inicia una excavación (`POST /cave/expand`), el temporizador corre, pero no hay un proceso en segundo plano que actualice el `cave_level` cuando finaliza.
   * *Solución:* En el endpoint `GET /cave/status`, comprobar si `cave_expansion_started_at` + `excavation_hours` ha pasado. Si es así, actualizar `cave_level += 1`, limpiar el timer y otorgar la recompensa (huevo correspondiente al nivel) antes de responder al frontend.
2. **Límite de Axolotitos Dinámico por Nivel:**
   * *Gap:* En `shop_service.py` y `vip_scheduler.py`, el límite de Axolotitos en inventario es un número estático `7 + VIP`.
   * *Solución:* Modificar para que la capacidad sea `cave_level + 6` (otorgando de 7 slots a nivel 1 hasta 14 slots a nivel 8), vinculando el crecimiento del cenote con la colección de personajes.

### 4.2 Frontend
3. **Botones de Acción en el Panel de Expansión:**
   * *Gap:* El modal de requisitos muestra qué falta para expandirse, pero no permite hacer click en "Comenzar Excavación" ni en "Acelerar con AXF" cuando el temporizador está corriendo.
   * *Solución:* Conectar los endpoints de `POST /cave/expand` y `POST /cave/expand/accelerate` al modal en `Santuario.tsx`.
4. **Lobby Multijugador - Tab "Salas de Jugadores":**
   * *Gap:* Las salas creadas por hosts no se muestran en ningún lado en el frontend.
   * *Solución:* Añadir un tercer tab en `MultiplayerLobby.tsx` titulado **"Salas de Anfitriones"** que llame a `GET /multiplayer/player-rooms`, renderice las salas con sus configuraciones y gestione la contraseña si son privadas.
5. **Animación de Excavación (Feedback Visual):**
   * *Gap:* La expansión ocurre de forma instantánea al clickear o terminar el timer, sin feedback visual.
   * *Solución:* Disparar una animación temporal en el canvas: temblor de pantalla (CSS shake), partículas de rocas cayendo, y un filtro marrón translúcido simulando agua turbia que se aclara gradualmente revelando el nuevo nivel.

### 4.3 Sistema de Decoraciones y Social (Post-MVP Mediano)
6. **Colocación de Objetos:** Implementar la interfaz para arrastrar decoraciones desde el inventario a los slots de decoración disponibles por nivel en la escena 2.5D.
7. **Social y Visitas:** Permitir que los jugadores busquen la cueva de sus amigos, carguen sus datos públicos (`GET /cave/public/{user_id}`) en modo de solo lectura y les dejen "aplausos" (likes).

---

## 5. Propuestas de Mejoras Premium (Ideas a Agregar)

Para llevar la estética y jugabilidad a un nivel excepcional, proponemos incorporar:

### 5.1 Paisajes Sonoros Evolutivos
* **Nivel 1 (El Nicho):** Sonido de goteo de agua lento y eco cavernoso básico.
* **Nivel 4 (El Salón):** Música subacuática ambiental relajante (instrumentos de viento suaves, arpa).
* **Nivel 8 (Palacio Astral):** Música mística celestial/cósmica con sintetizadores suaves y coros distantes.

### 5.2 Iluminación Cenital Sincronizada con el Tiempo Real
* Sincronizar el tono del degradado del cenote y los rayos de luz (`ray-light`) con la hora local del usuario:
  * **06:00 - 11:00 (Amanecer):** Tonos rosados y anaranjados suaves filtrándose desde la superficie.
  * **11:00 - 17:00 (Mediodía):** Rayos de luz blanca intensa, agua azul esmeralda vibrante.
  * **17:00 - 20:00 (Atardecer):** Luz cálida dorada/marrón.
  * **20:00 - 06:00 (Noche):** Oscuridad profunda, luz de luna plateada/cyan pulsando sutilmente, con algas y cristales bioluminiscentes encendiéndose en la cueva.

### 5.3 Interacciones Autónomas con Decoraciones
* Que los Axolotitos que están en "modo libre" no naden de forma aleatoria pura, sino que busquen interactuar con la decoración colocada:
  * Si hay un *Coral de Fuego*, se acercan a calentarse.
  * Si hay una *Roca Hueca*, se meten dentro a asomar la cabeza.
  * Si hay un *Incienso*, nadan a través del humo haciendo piruetas.

### 5.4 Mural de Anuncios Físico (Pizarra del Cenote)
* Permitir que el host escriba un mensaje corto (ej. "¡Torneo hoy a las 8 PM!", "Buscando retadores de 100 FRJ") en una roca tallada o pizarra física visible para cualquiera que visite su Cenote o se una a su mesa.

### 5.5 Calentador Geotérmico (Acelerador de Incubación Craftable)
* Un objeto de decoración funcional que, al colocarse en un slot adyacente a la zona de vida, reduce pasivamente el tiempo de incubación de todos los huevos en esa sección en un 10%. Esto incentiva la economía de crafteo y el mercado P2P.

---

## 6. Enlace a Tareas y Progresión
Este plan de refinamiento está vinculado a la tarjeta del Taskboard [task-1780816599-34](file:///D:/Axolotto_2026/axolotto/tools/taskboard/tasks.db) para su seguimiento y aprobación de requisitos.
