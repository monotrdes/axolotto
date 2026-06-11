# Plan de Implementación 2.0: Universo 2.5D de Papel Picado Submarino

> **Status**: Planning (Fase de Implementación)
> **Category**: `gamedesign`, `frontend`
> **Priority**: Crítica — Implementación del overhaul estético e interactivo
> **Taskboard**: `task-1781211910-96`
> **Dependencias**: Aprobación y merge de `task-1781159264-84` (Planificación v2.1)

---

## 🎨 1. Dirección de Arte & Experiencia de Usuario (UX) Game Design

Para transformar la experiencia actual de un "casino de menús" a un **videojuego indie inmersivo y artesanal (vibe *Paper Mario* / *Tearaway*)**, la estética del papel picado y la bioluminiscencia del cenote regirán cada interacción. No se trata solo de cambiar los fondos; toda la física, el movimiento y el HUD reaccionarán como papel recortado real.

### A. La Mesa de Juego Interactiva ("La Poza de la Lotería")
En lugar de una pantalla estática de cartones, la mesa de juego (online y contra CPUs) se sentirá como una superficie táctil real:
1. **La Tabla de Amate:** El cartón de lotería del jugador se renderiza con textura de papel amate rugoso. Cada casilla tiene un borde sutil troquelado y una sombra proyectada dura (2-3px offset, sin difuminado).
2. **Física de Frijolitos:** Al presionar una casilla marcada, un **frijolito de la suerte** cae desde la parte superior de la pantalla con una animación elástica de gravedad (bounce elástico en GSAP). Rebota dos veces sobre la casilla y se asienta, simulando que el usuario realmente colocó un frijol físico en su cartón.
3. **El Gritón Dinámico (Puppet Reactivo):** El Axolote Gritón que canta las cartas está presente en la esquina de la mesa. Sus branquias ondulan plácidamente. Sin embargo, a medida que el `tension_level` global de la sala sube (calculado en backend):
   - **Tensión Media:** Su animación idle se acelera y sus branquias vibran más rápido.
   - **Tensión Crítica / Match Point:** El Gritón empieza a sudar pequeñas burbujas físicas, sus ojos se abren con sorpresa (texture swap) y sostiene la carta cantada temblando sutilmente.
4. **Robo-Axolotes (Competidores CPU):** Los bots NPC se renderizan en la mesa con el set de texturas metálico. Tienen una llave de cuerda en la espalda que gira discretamente "clac-clac-clac" cada vez que marcan una carta. Sus mini-tableros flotan en su respectivo asiento, permitiendo al jugador ver el progreso de sus rivales y sentir la presión competitiva.
5. **Casi Canto (Match Point):** Si al usuario le falta 1 o 2 cartas para ganar, su tablero se agranda un 15%, pulsa con un brillo de luz lunar dorada y una ráfaga de confeti de papel picado sale de su Axolotito.

### B. El Tianguis Submarino ("Zoom & Scroll")
La tienda actual se convertirá en un mercado flotante navegable:
1. **Zoom de Enfoque:** Al presionar cualquiera de los 5 puestos (Booster Stalls, Adopción, Banco, Forja, P2P), la cámara del diorama realiza un paneo suave y un **zoom del 150%** centrándose en el puesto interactivo.
2. **Despliegue de Pergamino:** Una vez que la cámara hace foco, el panel HTML con los productos se despliega como un pergamino vertical que se desenrolla desde el borde de la pantalla con sonido físico de papel arrugado.
3. **Unboxing de Boosters:** Al comprar un sobre, este aparece en primer plano en el canvas de Pixi. El usuario desliza el dedo para "rasgar" el sobre de papel de china, liberando las cartas que flotan con destellos de confeti turquesa y rosa bugambilia.

### C. El Santuario: Eclosión y Camitas Morphing
1. **Teatro de Sombras al Eclosionar:** La eclosión de un huevo de Axolotito utiliza un efecto de silueta de papel recortado a contraluz. El usuario da taps para agrietar el huevo. Al romperse, el nido de paja se desensambla y se pliega físicamente en una pequeña camita de madera flotante donde vivirá el nuevo Axolotito, con su nombre tallado a mano en la base.

---

## 🤖 2. Matriz de Asignación por IA

Para lograr la máxima eficiencia en el consumo de tokens y asegurar la calidad del código, las tareas se dividen entre los agentes según su especialidad:

| Agente | Especialidad en el Rediseño | Herramientas Clave |
| :--- | :--- | :--- |
| 🦎 **Gemini / Antigravity** | Motor PixiJS v8, Rigging de Puppets, Animación procedural GSAP, Shaders, Partículas, Efectos de Luz, Audio. | PixiJS, GSAP, WebGL Shaders, Web Audio |
| 🧠 **Claude** | Componentes de UI HTML/React, Layouts responsivos de pergamino, Re-skin de pantallas viejas (Tienda, Mochila, Inventario), State Bridge. | React 19, Tailwind CSS 4, Zustand/Bridge |
| 🤖 **DeepSeek / DeepClaude** | Backend API, Concurrencia, WebSockets en tiempo real, Base de Datos para Decoración y Staking. | FastAPI, SQLModel, WebSockets, PostgreSQL |

---

## 📋 3. Checklists de Implementación por Fases

### Fase 0: Cimientos y Setup Gráfico (NEXT_PUBLIC_PAPER_WORLD=1)
*Objetivo: Configurar el motor de PixiJS v8, la integración con React, el pipeline de assets y el layout responsivo.*

*   [ ] **Setup del Motor Gráfico:** Instalar `pixi.js@^8` y `gsap` en el frontend. Implementar el cargador dinámico en `components/world/GameCanvas.tsx` para no cargar Pixi si el flag está apagado. *(🦎 Gemini)*
*   [ ] **Pipeline de Atlases:** Configurar el script de generación de spritesheets `.webp` y sus metadatos JSON correspondientes en `public/world/atlas/`. *(🦎 Gemini)*
*   [ ] **Sistema de Cámara y Paneo:** Implementar la cámara 2.5D con parallax responsivo que adapte la vista en móviles (vertical 9:16) y escritorio (horizontal 16:9). *(🦎 Gemini)*
*   [ ] **El Puente de Estado (WorldBridge):** Crear el emisor de eventos simple para comunicar clics del canvas a React y actualizaciones de estado de React al canvas. *(🧠 Claude)*
*   [ ] **CSS Tokens de Papel:** Añadir la paleta del cenote (`--papel-bugambilia`, `--papel-cempasuchil`, `--papel-amate`, etc.) en `globals.css` y configurar clases de bordes troquelados y sombras duras. *(🧠 Claude)*

### Fase 1: El Santuario y el Puppet DNA System
*Objetivo: Crear el sistema de títeres procedimentales controlados por el ADN del backend y dar vida al Santuario.*

*   [ ] **Puppet DNA Factory:** Crear `AxolotitoPuppet.ts` para renderizar Axolotitos en runtime ensamblando partes (ojos, cola, branquias, accesorios) basadas en el ADN de los metadatos del backend. *(🦎 Gemini)*
*   [ ] **Animaciones Procedurales en Loop:** Escribir las animaciones idle de respiración (squash & stretch), parpadeos aleatorios y ondulación sinusoidal desfasada de branquias. *(🦎 Gemini)*
*   [ ] **Chinampa del Santuario (3 niveles):** Crear el diorama del Santuario con parallax: nidos arriba, sala interactiva al centro, embarcadero abajo. *(🦎 Gemini)*
*   [ ] **Transformación Nido ➔ Camita:** Animación de plegado de papel que convierte el huevo roto en una camita permanente con el nombre del Axolotito. *(🦎 Gemini)*
*   [ ] **Embarcadero y Trajineras de Amigos:** Renderizar trajineras que flotan de manera sinusoidal. Conectar clics para abrir la vista social HTML. *(🧠 Claude / 🦎 Gemini)*
*   [ ] **Mesa de Amigos:** Ligar la mesa física central del Santuario con el trigger que abre el modal de hosteo/unión a partidas amistosas. *(🧠 Claude)*
*   [ ] **Backend de Decoraciones:** Crear los endpoints en FastAPI para persistir la posición y tipo de decoraciones compradas en la cueva. *(🤖 DeepSeek)*

### Fase 2: Tianguis Flotante y Re-skin del Comercio
*Objetivo: Integrar el zoom diegético de cámara en la tienda y transformar la UI HTML a la estética de papel picado.*

*   [ ] **Hotspots del Tianguis:** Configurar los 5 puestos interactivos en el canvas con animaciones de rebote elástico al pasar el cursor o hacer tap. *(🦎 Gemini)*
*   [ ] **Lógica de Enfoque y Zoom:** Programar la transición de cámara que se desplaza y hace zoom sobre el puesto seleccionado antes de abrir la UI de compra. *(🦎 Gemini)*
*   [ ] **Re-skin HTML de Tienda y Mochila:** Modificar `Store.tsx` e `Inventory.tsx` para convertirlos en pergaminos verticales que se deslizan sobre la pantalla con estilos de papel amate. *(🧠 Claude)*
*   [ ] **Caldero de la Forja Mística:** Implementar el efecto visual del caldero bioluminiscente con confeti de papel picado y burbujas brillantes en PixiJS. *(🦎 Gemini)*
*   [ ] **Unboxing de Sobres en Canvas:** Diseñar la animación en PixiJS donde el sobre de cartas se rasga de forma física y las cartas emergen girando. *(🦎 Gemini)*

### Fase 3: Lotería 2.5D y la Mesa de Competencia
*Objetivo: Integrar las partidas dinámicas contra CPUs y oponentes reales en la mesa tridimensional.*

*   [ ] **Asientos de la Mesa 2.5D:** Adaptar `CenoteRoom.tsx` y `CircularTable.tsx` para posicionar los puppets de los Axolotitos oponentes alrededor de la mesa con sus nombres. *(🦎 Gemini)*
*   [ ] **Robo-Axolotes (Bots):** Programar la variante visual metálica de los bots con la animación de tic-tac de su llave de cuerda en la espalda. *(🦎 Gemini)*
*   [ ] **El Gritón Tembloroso:** Renderizar al Gritón en la esquina de la mesa de juego, sincronizando sus reacciones y sudor de burbujas con el `tension_level`. *(🦎 Gemini)*
*   [ ] **Física de Frijolitos:** Crear el renderizador en el cartón de lotería HTML/Canvas para que al marcar una carta, caiga un frijolito elástico y rebote en su lugar. *(🦎 Gemini / 🧠 Claude)*
*   [ ] **Visualización de Tablas Oponentes:** Implementar mini-tableros sobre cada Axolotito en la mesa que actualizan su conteo de cartas restantes de acuerdo al WebSocket. *(🧠 Claude)*
*   [ ] **Efecto de Casi Canto (Match Point):** Programar el halo dorado y la lluvia de confeti local sobre el cartón y el títere de quien esté a una carta de ganar. *(🦎 Gemini)*

### Fase 4: Cámara de la Suerte (Gashapon) e Integración Lunar
*Objetivo: Implementar el área de Gashapon físico en Pixi y el ciclo de iluminación lunar global.*

*   [ ] **Máquinas Gashapon de Cartón:** Renderizar los 3 dispensadores de cápsulas empotrados en la piedra de la Pirámide con animaciones de manija. *(🦎 Gemini)*
*   [ ] **Termómetro de Karma:** Crear el termómetro visual de papel al lado de las máquinas que sube e indica cuando el "Karma está Caliente" tras múltiples tiradas fallidas. *(🦎 Gemini / 🧠 Claude)*
*   [ ] **Caída de Cápsula en Diorama:** Programar la caída y rebote físico de la esfera ganadora desde la ranura de la máquina hacia el centro de la pantalla antes del reveal. *(🦎 Gemini)*
*   [ ] **Shader de Luz Lunar Global:** Crear un filtro/tinte ambiental en el motor de PixiJS que reaccione al número de fase lunar actual del jugador, tiñendo el agua de todo el cenote. *(🦎 Gemini)*
*   [ ] **Onboarding y Tutorial en el Cenote:** Adaptar los fondos y diálogos del tutorial de 11 actos para que guíe al jugador físicamente a través de las 3 macrozonas en el orden correspondiente. *(🧠 Claude)*

### Fase 5: Optimización de Rendimiento y Rollout
*Objetivo: Asegurar 60 FPS estables en dispositivos móviles de gama media y habilitar el despliegue.*

*   [ ] **Quality Tiers Controller:** Programar la lógica de medición de FPS inicial y el detector de memoria para asignar los perfiles Alta, Media o Ligera de forma automática. *(🦎 Gemini)*
*   [ ] **Shader de Caustics de Agua:** Escribir el shader de distorsión WebGL para simular agua bioluminiscente en movimiento (solo Calidad Alta). *(🦎 Gemini)*
*   [ ] **Unload de VRAM:** Implementar un sistema estricto de recolección de basura visual que destruya texturas y atlases viejos al cambiar de macrozona. *(🦎 Gemini)*
*   [ ] **Retratos a Texturas Cacheables:** Reemplazar el emoji de `AxoAvatar` en la interfaz HTML por una textura estática generada en runtime una sola vez a partir de su rig de puppet. *(🦎 Gemini / 🧠 Claude)*
*   [ ] **Settings Gráficos:** Añadir los toggles de calidad de animación, sonido y parallax en el modal de configuración general. *(🧠 Claude)*

---

## 📈 4. Criterios de Aceptación y Rendimiento

1.  **Framerate:** 60 FPS estables en transiciones y paneos dentro del diorama de la Pirámide en dispositivos móviles tipo Moto G (gama media Android).
2.  **Consumo de Memoria:** Uso de VRAM residente inferior a 16MB en calidad Ligera y 48MB en calidad Alta.
3.  **Peso del Bundle:** El incremento neto en el bundle frontend al habilitar `NEXT_PUBLIC_PAPER_WORLD=1` debe estar aislado en chunks dinámicos (lazy load de PixiJS y escenas) menores a 250KB gzip.
4.  **Consistencia de Flujo:** Ningún cambio visual debe romper los flujos de compra, P2P, escrow, ni validaciones Web3 del backend.
