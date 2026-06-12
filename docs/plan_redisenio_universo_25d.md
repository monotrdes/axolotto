# 🎨 Axolotto 2.0 — Plan de Rediseño Premium y Auditoría del Universo 2.5D

Este plan maestro consolida el estado de desarrollo del universo 2.5D de **Axolotto** (estética de **"Papel Picado Submarino"**). Audita el esqueleto técnico actualmente implementado en el codebase y traza una hoja de ruta clara para cerrar la **Brecha Premium**, elevando la experiencia a calidad de videojuego indie profesional.

---

## 🔍 1. Auditoría del Código Existente (Qué está implementado)

Se corroboró el estado del motor gráfico y de las escenas en la rama de desarrollo. El esqueleto técnico en PixiJS v8 y GSAP está completamente estructurado y funcional:

### A. Capa de Inicialización y Ciclo de Vida (Engine)
* **Motor Base ([WorldEngine.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/engine/WorldEngine.ts)):** Controla la inicialización de la `Application` de PixiJS v8, el ajuste del límite de FPS según la calidad detectada, la pausa del loop de renderizado cuando la pestaña del navegador pierde foco (visibilitychange) y la liberación de memoria VRAM en la GPU.
* **Cámara 2.5D ([CameraRig.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/engine/CameraRig.ts)):** Maneja el centrado responsivo, encuadres dinámicos (para móvil vertical 9:16 y escritorio 16:9) y desplazamientos (paneos) con curvas suavizadas.
* **Calidad Gráfica ([qualityTier.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/engine/qualityTier.ts)):** Detecta la memoria del dispositivo y la cantidad de núcleos de CPU para clasificar el hardware del jugador en tres perfiles: `'alta'`, `'media'` o `'ligera'`.
* **Capa Puente ([WorldBridge.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/WorldBridge.ts)):** Emisor de eventos ligero (`EventEmitter` modificado) para la comunicación bidireccional entre el canvas de PixiJS y las interfaces HTML del cliente React.
* **Envoltura React ([GameCanvas.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/world/GameCanvas.tsx)):** Expone una interfaz imperativa (`GameCanvasHandle`) para que [page.tsx](file:///D:/Axolotto_2026/axolotto/frontend/app/play/page.tsx) controle la carga de axolotitos, amigos y decoraciones, así como el foco de la cámara.

### B. Escenas y Dioramas por Macrozonas
* **El Santuario ([SantuarioScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/santuario/SantuarioScene.ts)):** chinampa vertical de 3 niveles con:
  - *Crianza (Nivel Superior):* 8 slots de nidos desbloqueables según el nivel de expansión de la cueva. Soporta visualización de huevos con auras de rareza, nidos vacíos, slots bloqueados por roca y camitas para Axolotitos adultos.
  - *Mesa Amistosa (Nivel Central):* Mesa de madera de juego central con mantel y sillas adaptados en tiempo real según el endpoint `/cave/decorations`.
  - *Decoración por Slots:* 5 categorías de decoración equipables (Ambiente, Luz, Mantel, Sillas, Adornos) con hotspots para re-decorar de manera interactiva.
  - *Embarcadero de Amigos (Nivel Inferior):* Trajineras meciéndose en el agua que cargan avatares de amigos en línea y despliegan burbujas de acción rápida (`❤️ Like`, `👁 Visitar Cueva`, `🎲 Invitar a Jugar`).
* **El Tianguis ([TianguisScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/tianguis/TianguisScene.ts)):** Mercado flotante con guirnaldas de banderines de papel picado ondulantes y 5 puestos interactivos (Sobres, Adopción, Banco, Forja, P2P) mapeados a los eventos de compra de React.
* **La Pirámide ([PiramideScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/piramide/PiramideScene.ts)):** Escena ancha de 3 pantallas con paneo horizontal libre de cámara que une:
  - *Explanada de Rankings:* Escalinata de piedra con el podio en tiempo real de los 3 mejores Axolotitos.
  - *Cámara de la Suerte:* 3 máquinas de Gashapón con domos llenos de cápsulas de colores y ranuras de salida.
  - *Cenote de las Salas:* Representación visual de las pozas competitivas (Charco de Novatos y Fosa del Campeón) a distintas profundidades.

### C. El Rig de Puppets Animados
* **Títeres Reales ([AxolotitoPuppet.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/AxolotitoPuppet.ts)):** Ensambla en tiempo real el cuerpo, cabeza, cola, extremidades y branquias de un Axolotito de acuerdo a su color de piel.
* **Física y Animaciones Procedurales:** Escribe loops sinusoidales de respiración (squash & stretch), parpadeos aleatorios, coleteos y balanceos de branquias desfasados. Soporta transiciones suaves de atenuación (*cross-fade*) de 200ms entre 4 perfiles de movimiento: `'idle'`, `'walking'`, `'sleeping'` y `'playing'`.
* **Robo-Axolotes ([RoboAxolotePuppet.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/RoboAxolotePuppet.ts)):** Versión robótica/metálica de bots oponentes con llave de cuerda oscilante e idle mecánico desfasado.

---

## ⚡ 2. La Brecha Premium: Qué falta implementar

Aunque el esqueleto es sólido, el juego aún utiliza gráficos vectoriales planos y componentes DOM genéricos que carecen de la fidelidad táctil de un juego premium. Se definen las siguientes mejoras prioritarias para cerrar la brecha:

```
┌────────────────────────────────────────────────────────┐
│  CÓMO ELEVAR EL ESQUELETO ACTUAL A CALIDAD PREMIUM     │
├────────────────────────────────────────────────────────┤
│ 1. Texturas de Papel Picado en lugar de Fills Planos   │
│ 2. Shaders de Distorsión de Agua Bioluminiscente      │
│ 3. Física de Frijolitos Rebotantes en el Cartón        │
│ 4. Unboxing de Sobres con Desgarre Táctil en Canvas    │
│ 5. Feedback de Partículas y Tensión Dinámica           │
│ 6. Capa de Sonido Web Audio (Papel, Agua y Jarana)     │
└────────────────────────────────────────────────────────┘
```

### 🖼️ A. Texturizado por Sprites (El Atlas de Papel)
* **El Problema:** [paperParts.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/paperParts.ts) y [roboParts.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/roboParts.ts) dibujan las piezas de los Axolotitos usando vectores sencillos (`g.ellipse()`, `g.roundRect()`) con colores planos. Las escenas en `buildBackdrop()` usan rectángulos y elipses sin texturas.
* **Solución Premium:** 
  1. Reemplazar los métodos de `paperParts.ts` y `roboParts.ts` para que retornen `Sprite` cargados desde un atlas de texturas (`axolotito-parts.json`).
  2. Dibujar las partes de los axolotitos con textura de papel de china arrugado, bordes blancos troquelados y sombras duras proyectadas en el canal alfa.
  3. Cargar imágenes de fondo estructuradas en capas con transparencias para que el parallax de las macrozonas revele las vetas y texturas de papel real.

### 🌊 B. Shaders de Distorsión de Agua (Displacement Filters)
* **El Problema:** El agua de las escenas se simula con simples rectángulos oscuros estáticos y banderines que rotan en un eje.
* **Solución Premium:**
  1. En [WorldEngine.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/engine/WorldEngine.ts), implementar un filtro de desplazamiento (`DisplacementFilter` de PixiJS) sobre el contenedor principal del fondo de agua.
  2. Utilizar una textura de ruido animada en loop para distorsionar la imagen de fondo de forma sinusoidal, simulando corrientes submarinas reales.
  3. Desactivar el filtro automáticamente en el perfil de calidad `'ligera'` y limitar la resolución en `'media'` para proteger el rendimiento en móviles.

### 🎴 C. Física de Frijolitos Rebotantes (Lotería Interactiva)
* **El Problema:** El marcado de casillas en el cartón de lotería manual ([LoteriaBoard.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/ui/LoteriaBoard.tsx)) utiliza un simple círculo plano que se activa al instante.
* **Solución Premium:**
  1. Implementar un efecto donde, al marcar una casilla, un **frijolito tridimensional recortado** cae desde el borde superior de la celda.
  2. La animación de caída debe usar la gravedad y un rebote elástico (GSAP `bounce.out`) para que rebote dos veces y se asiente en la casilla.
  3. En estado de *Match Point* (1-2 casillas para ganar), envolver la celda en un borde de papel picado dorado pulsante con partículas de confeti flotantes.

### 📦 D. Unboxing Táctil de Boosters en el Canvas
* **El Problema:** La compra de sobres de la tienda abre un modal HTML estándar que simplemente realiza un *fade-in* del resultado.
* **Solución Premium:**
  1. Al presionar "Abrir ahora" en [Store.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/Store.tsx) o [Inventory.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/Inventory.tsx), suspender la UI y mostrar el sobre en primer plano en el canvas de PixiJS.
  2. Exigir que el jugador deslice el dedo o el mouse a través de una línea troquelada para "rasgar" físicamente el sobre.
  3. Usar máscaras dinámicas de Pixi para romper el sprite del sobre por la mitad en una curva elástica, liberando las cartas que giran en 3D (GSAP 3D rotations) con destellos dorados y burbujas de rareza.

### 🔊 E. La Capa de Audio e Inmersión
* **El Problema:** El juego carece de efectos de sonido diegéticos y transiciones auditivas que acompañen el cambio de zonas.
* **Solución Premium:**
  1. Crear un controlador de sonido central (`AudioController.ts`) con soporte de volumen global y silenciamiento integrado con [SettingsModal.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/SettingsModal.tsx).
  2. Agregar sonidos para las siguientes interacciones:
     - *Papel Picado:* Sonido de papel arrugándose y abriéndose al desplegar pergaminos o en transiciones de cortina.
     - *Agua Cenote:* Splash líquido suave al tocar los nidos o eclosionar axolotitos.
     - *Feria Xochimilco:* Sonido metálico de engranaje al girar las manijas de las máquinas de Gashapón y monedas cayendo.
     - *Tensión Lotería:* Acoplar la intensidad y volumen del bucle musical de fondo con el `tension_level` devuelto por el WebSocket de la sala.

---

## 📅 Hoja de Ruta de Implementación de la Brecha Premium

El desarrollo se organizará en 4 sprints semanales enfocados en cubrir la brecha identificada sobre la base del código actual:

### Sprint 1: Integración de Texturas y Assets en Puppets
- [ ] Generar los spritesheets y metadatos JSON para el rig de axolotitos en `public/world/atlas/axolotito-parts.{webp,json}`.
- [ ] Refactorizar [paperParts.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/paperParts.ts) y [roboParts.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/puppet/roboParts.ts) para usar `Sprite.from()` en lugar de `Graphics` vectoriales de PixiJS.
- [ ] Cambiar los rectángulos de fondo en [SantuarioScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/santuario/SantuarioScene.ts), [TianguisScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/tianguis/TianguisScene.ts) y [PiramideScene.ts](file:///D:/Axolotto_2026/axolotto/frontend/components/world/zones/piramide/PiramideScene.ts) por texturas de agua de cenote de alta resolución con relieve.
- [ ] Validar que el rendimiento móvil (`detectQualityTier`) limite correctamente las texturas en perfiles de calidad baja para evitar cuelgues por VRAM.

### Sprint 2: Shaders de Cenote y Animación del Tianguis
- [ ] Implementar el `DisplacementFilter` de PixiJS para simular caustics de agua bioluminiscente en las 3 escenas.
- [ ] Desarrollar la animación en PixiJS del card-melting en el caldero de la Forja Mística (trajineras que lanzan chispas de confeti).
- [ ] Programar la física y la secuencia de desgarre táctil para el unboxing de sobres sellados dentro del diorama del Tianguis.
- [ ] Integrar el panel HTML de la tienda como un pergamino vertical deslizable que simula desenrollarse sobre el canvas.

### Sprint 3: Física de Frijolitos y Tensión en la Mesa de Juego
- [ ] Enlazar el cartón de lotería de [LoteriaBoard.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/ui/LoteriaBoard.tsx) con la animación elástica de caída de frijolitos.
- [ ] Sincronizar las animaciones y la textura facial de sorpresa del Gritón en [CenoteRoom.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/multiplayer/CenoteRoom.tsx) con el `tension_level` de la sala multijugador.
- [ ] Dibujar a los oponentes de la mesa (bots Robo-Axolote) usando texturas metálicas reales y engranajes mecánicos en movimiento.
- [ ] Programar el efecto Match Point (tablero de juego aumentado un 15% con glow de luz de luna y partículas doradas).

### Sprint 4: Sonido, Onboarding y QA General
- [ ] Implementar el módulo `AudioController.ts` y cablear los eventos de clics, eclosión, giros de manijas y reclamos.
- [ ] Adaptar la estética del tutorial de 11 actos de [TutorialFlow.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/tutorial/TutorialFlow.tsx) para guiar al Webito de forma interactiva a través del muelle, tianguis y la pirámide.
- [ ] Medir FPS y optimizar el recolector de basura visual en dispositivos móviles Android e iOS, garantizando 60 FPS consistentes.

---

## 📊 Presupuesto Técnico y Límites de Rendimiento

| Recurso | Límite Máximo | Estrategia de Control |
| :--- | :--- | :--- |
| **VRAM en GPU** | **≤ 32 MB** | Carga asíncrona de atlas mediante `Assets.load()` y descarga inmediata de recursos al cambiar de macrozona (`Assets.unload()`). |
| **Peso del Atlas** | **≤ 350 KB (Gzip)** | Compresión agresiva de spritesheets en formato `.webp` con opacidad escalada. |
| **FPS en Móviles** | **60 FPS** | Bloqueo automático de filtros avanzados (displacement shader, caustics) y reducción del conteo de partículas ambientales en hardware de gama baja. |
| **Llamadas a CPU** | **≤ 120 draw calls** | Batching automático de sprites de PixiJS agrupando todas las partes del Axolotito en un único contenedor ordenado. |

---

## 🎨 Prompts para Generación del Spritesheet (IA Image Generator)

Para cuando decidas generar o encargar los assets del spritesheet, puedes usar estos prompts diseñados para Midjourney, DALL-E 3 o Stable Diffusion XL:

### A. Prompt para Axolotitos de Papel Picado (Jugador/Amigos)
> A high-resolution modular sprite sheet containing separate 2D body parts of a cute cartoon axolotl character, designed in a premium Mexican "Papel Picado" craft style. The sheet includes: a main body trunk, a round head, 3 distinct pairs of feathery gills, 2 cute arms (limbs), 2 legs, a wavy tail, separate open cartoon eyes, separate closed blinking eyes, and mouth expressions (smiling, neutral, surprised). Every piece has a clean white cardstock paper cut-out border and a subtle hard drop-shadow underneath, looking like real layered paper craft. Bioluminescent sunset-cenote colors: vibrant bugambilia pink, cempasúchil orange, and turquoise accents. All parts are laid out cleanly on a solid neon green chroma-key background, isolated, flat 2D vector-like shapes, no overlap, professional asset sheet, game development assets --v 6.0 --style raw

### B. Prompt para Robo-Axolotes (Bots CPU)
> A high-resolution modular sprite sheet containing separate 2D mechanical body parts of a cute steampunk robot axolotl, designed in a layered cardboard and brass style. The sheet includes: a copper-plated body, a round brass head, mechanical clockwork gears instead of gills, rivet joints (arms and legs), a sheet metal tail with bolts, glowing turquoise lens-eyes, and a wind-up key (llave de cuerda) coming out of its back. Every piece has a clean white paper cut-out border and a subtle hard drop shadow, looking like a craft toy made of metal plates and paper. Placed flat and separate on a solid neon green chroma-key background, no overlap, game asset sheet --v 6.0 --style raw

