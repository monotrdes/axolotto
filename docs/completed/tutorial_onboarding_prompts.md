# Guía de Prompts de Imagen y UI para Gemini: Onboarding y Tutorial de Axolotto

Este documento sirve como referencia visual para generar representaciones fieles de la interfaz y la estética de **Axolotto** en cada una de las fases del flujo de onboarding y tutorial, detallado en [2026-05-30-onboarding-completo-landing-tutorial-branch.md](file:///home/monotr/axolotto/docs/superpowers/plans/2026-05-30-onboarding-completo-landing-tutorial-branch.md).

Las imágenes resultantes de estos prompts pueden ser utilizadas para mockups de diseño, referencias artísticas de UI, o material promocional para el proyecto.

---

## 🎨 Esencia Estética de Axolotto

Para que los prompts de Gemini generen imágenes fieles al juego, la dirección artística debe respetar la **Estética Dark Neon de Xochimilco**:
*   **Fondos**: Profundidades lacustres oscuras (azul marino profundo, negro, cerceta oscura) con raíces de ahuejotes, nenúfares y burbujas bioluminiscentes flotando.
*   **Acentos de Luz**: Brillos de neón con colores temáticos por sección:
    *   **Tienda**: Rosa Hot `#E4007C`
    *   **Nido / Cenote / Webito**: Teal / Cerceta `#2DD4BF` o `#00e5ff`
    *   **Rankings / Suerte**: Oro / Ámbar `#FBBF24`
    *   **Gashapón**: Violeta `#A855F7`
    *   **Cartas**: Índigo `#818CF8`
*   **Diseño**: Interfaces limpias, botones redondeados de estilo vidrio (glassmorphism), transparencias esmeriladas y efectos de brillo que sugieren tecnología Web3 oculta detrás de la mitología prehispánica mexicana.

---

## 🚪 Ventana 1: Landing Page (Acceso y Auth)

*   **Propósito**: Primera pantalla del usuario. Landing page estática donde se introduce el concepto de Axolotto, se permite canjear códigos de promoción y se da acceso directo a través de Privy (Google, Apple, Email).
*   **Elementos clave en pantalla**:
    *   Fondo de cenote oscuro con burbujas y destellos rosa neón.
    *   Logo de Axolotto: Estilo caricatura mexicana moderna de un ajolote con un boleto de lotería dorado en la boca.
    *   Gran botón de login en gradiente rosa/morado: `"¡Jugar gratis! →"`.
    *   Iconos de métodos de acceso Privy debajo (Google, Apple, sobre de Email).
    *   Sección de canje de código con diseño de bordes de neón.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
High-fidelity UI mockup for a web game landing page named "Axolotto". Dark neon aesthetic. Background is a deep, dark teal and navy blue Xochimilco cenote underwater scene with bioluminescent water lilies, glowing bubbles, and ancient tree roots. In the center, a stylized logo of a cute, glowing neon pink axolotl. Below the logo, a premium glassmorphic authentication card containing: a prominent, rounded button with a hot pink-to-purple gradient reading "¡Jugar gratis! →", small clean icons for Google, Apple, and Email login underneath, and a separate neon-bordered input field for "Código Promocional". Sleek, modern game interface, vector art, 8k resolution, flat game UI design.
```

---

## 🥚 Ventana 2: Introducción (El Webito Cae del Cielo)

*   **Propósito**: Se activa inmediatamente después de que un usuario nuevo entra por primera vez a `/play`. Un Webito cae con física cómica, rebota en el fondo del cenote y habla mediante un cuadro de diálogo flotante.
*   **Elementos clave en pantalla**:
    *   Fondo degradado radial azul oscuro a negro. Puntos de estrellas o partículas submarinas suspendidas.
    *   En el centro: Un huevo de ajolote (`🥚`) estilizado con brillos de neón cerceta (`#00e5ff`) flotando ligeramente. Pequeñas nubes de polvo/arena en la base denotando el impacto reciente de la caída.
    *   Abajo: Un cuadro de diálogo estilo cristal esmerilado con bordes brillantes.
    *   Texto del Webito en español: `"¡AY! ¡Me caí! Perdón perdón... llevo semanas dentro de este cascarón y finalmente escuché que tú llegaste..."`.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
Game screenshot of a character introduction screen. A glowing digital egg with neon cyan veins floats in the center of a deep underwater cenote with dark blue-to-black radial gradient. Subtle sand-dust impact clouds sit at the bottom of the egg, indicating it just fell. Below the egg, there is a frosted glass (glassmorphism) dialogue box with a glowing light blue border. Inside the dialogue box, Spanish text reads: "¡AY! ¡Me caí! Perdón perdón... llevo semanas dentro de este cascarón y finalmente escuché que tú llegaste." Cute game art style, vibrant neon accents, magical atmosphere, user interface mockup.
```

---

## 🧂 Ventana 3: Tutorial - Fase 1: Salinidad (Salinity)

*   **Propósito**: Primera partida de aprendizaje. El Webito explica que la salinidad representa su mala suerte incorporada, pero que debemos jugar.
*   **Elementos clave en pantalla**:
    *   Indicador de fase en la parte superior: `Fase 1: Salinidad` con tres círculos de progreso (el primero brilla en cian, los otros dos apagados).
    *   Tablero de Lotería: Rejilla de 4x4 con cartas tradicionales mexicanas adaptadas a Axolotto (ilustraciones modernas de "La Sirena", "El Catrín", "El Nopal", etc.).
    *   El Webito flotando en la esquina inferior izquierda.
    *   Cuadro de diálogo emergente al lado del Webito con el texto: `"¡Holaaa! Soy Webito, tu huevo de lotería! Vamos a jugar nuestra primera partida. Tengo mucha salinidad... ¡pero no importa, la suerte siempre llega!"`.
    *   Carta del "Gritón" (la carta cantada activa) flotando en un panel lateral.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
In-game screenshot of a tutorial phase for a lottery-themed web game. At the top, a clean step progress indicator reading "Fase 1: Salinidad" with glowing cyan indicators. The main screen displays a 4x4 grid of beautifully illustrated Mexican Lotería cards. In the bottom left corner, a cute cartoon egg with tiny pink gills is floating. A sleek glass dialogue bubble next to it displays Spanish text: "¡Holaaa! Soy Webito, tu huevo de lotería! Vamos a jugar nuestra primera partida. Tengo mucha salinidad... ¡pero no importa, la suerte siempre llega!" The interface has neon cyan glows, dark navy backdrop, and a card announcer deck on the right side. Flat 2D vector style.
```

---

## 👁️ Ventana 4: Tutorial - Fase 2: Enfoque (Focus y Distracción)

*   **Propósito**: Segunda partida del tutorial. Enseña la mecánica de concentración. El Webito se distrae y el usuario debe hacer tap en una carta iluminada.
*   **Elementos clave en pantalla**:
    *   Indicador de progreso superior: Círculos 1 y 2 brillan en cian (`Fase 2: Concentración`).
    *   El Webito aparece mareado o con ojos en espiral flotando sobre el tablero, distraído de la partida.
    *   Una carta específica en el tablero de 4x4 está rodeada por un contorno de neón cian parpadeante, invitando al jugador a hacer click.
    *   Cuadro de diálogo: `"¡Uy! Me distraje mirando esa carta tan bonita. ¡Tócala rápido para recuperar el tiempo perdido!"`.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
Game UI design screenshot of a tutorial screen focusing on character concentration. Top progress tracker reads "Fase 2: Concentración" with two glowing cyan dots. The center shows a 4x4 card grid, with one card pulsing with a bright neon cyan outline and target indicator. In the corner, a cute cartoon egg looks dizzy with comic swirls over its head. A sleek dark glass dialogue bubble says in Spanish: "¡Uy! Me distraje mirando esa carta tan bonita. ¡Tócala rápido para recuperar el tiempo perdido!" Game UI with hot pink and cyan glow highlights against dark aquatic backgrounds.
```

---

## ⚡ Ventana 5: Tutorial - Fase 3: Suerte y Cheat Astral

*   **Propósito**: Tercera partida. Introduce la mecánica de activar el "Cheat Astral" tocando 3 veces la pantalla rápidamente para obtener un buff de suerte.
*   **Elementos clave en pantalla**:
    *   Indicador superior: Los tres círculos brillan (`Fase 3: Suerte`).
    *   Toda la pantalla tiene un filtro místico con rayos de energía púrpura y violeta (`#A855F7`).
    *   El Webito brilla intensamente con un halo de luz mágica y partículas cósmicas.
    *   Destellos con ondas de choque que simulan "Taps" en pantalla en tres puntos centrales.
    *   Cuadro de diálogo: `"¡Ahora! ¡Activa el Cheat Astral! Toca la pantalla 3 veces seguido, ¡rápido! Siente el aura..."`.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
Action-packed game tutorial screen screenshot. The theme is magic and luck. At the top, progress dots glow bright purple, showing "Fase 3: Suerte". The entire screen is overlaid with a soft purple and gold cosmic aura. In the middle, three semi-transparent ripple circles signify rapid screen taps. A cute cartoon egg is charging with intense purple bioluminescent lightning. The dialogue bubble next to it reads in Spanish: "¡Ahora! ¡Activa el Cheat Astral! Toca la pantalla 3 veces seguido, ¡rápido! Siente el aura..." High-fidelity UI mockup, dark background with magical particles.
```

---

## 🔮 Ventana 6: Revelación de Karma (Karma Card)

*   **Propósito**: Tras acabar las 3 partidas, se calcula y revela el tipo de karma del Webito ("Suerte" o "Salado") en forma de carta mística antes de nacer.
*   **Elementos clave en pantalla**:
    *   Pantalla minimalista con fondo oscuro.
    *   En el centro, una gran carta mística flotante (tipo tarot) con bordes iluminados:
        *   **Opción A (Suerte)**: Bordes dorados con destellos ámbar (`#FBBF24`), un trébol de cuatro hojas (`🍀`) en el centro y el texto `"Karma de Suerte"`.
        *   **Opción B (Salado)**: Bordes cian brillante (`#00e5ff`), un salero de neón (`🧂`) en el centro y el texto `"Karma Salado"`.
    *   Un gran botón inferior en degradado a juego: `"¡Hacer eclosionar!"`.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
A mystical tarot-style card reveal screen for a video game. In the center, a large vertically-oriented card floats against a dark ambient background. The card has a thick, glowing gold and green borders with magical sparkles. At the center of the card, a stylized neon icon of a four-leaf clover is displayed above the title "Karma de Suerte". Below the card, a premium, wide button with a golden-yellow gradient reads "¡Hacer eclosionar!". The layout is symmetric, clean, cinematic lighting, dark background, premium game asset.
```

---

## 🐣 Ventana 7: Eclosión (Egg Hatching)

*   **Propósito**: La animación culminante donde el cascarón se fractura y nace el Axolotito.
*   **Elementos clave en pantalla**:
    *   El huevo en el centro abriéndose, con fragmentos flotando alrededor.
    *   Un estallido masivo de luz neón verde y cerceta que emana del interior del cascarón.
    *   Un lindo Axolotito bebé rosa (`🦎`) saliendo de la luz, sonriendo con sus branquias flotando felizmente.
    *   Título triunfal arriba: `"¡Tu Axolotito ha nacido!"` en una tipografía estilizada y brillante.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
Game reward screen showing an egg hatching animation. A central digital egg fractures, bursting with dramatic beams of neon green and turquoise light. Out of the glowing energy, a tiny, adorable pink baby axolotl with fluffy pink gills emerges, floating happily with closed eyes and a big smile. Glowing particles, air bubbles, and floating egg shell shards fill the scene. At the top, glowing text reads "¡Tu Axolotito ha nacido!" in a bold, modern gaming font. Premium game cinematic art.
```

---

## 🔀 Ventana 8: Bifurcación Post-Tutorial (Post-Tutorial Branch)

*   **Propósito**: Pantalla decisiva de onboarding. Permite al usuario elegir entre el camino de pago (Premium con tokens GAL) o el gratuito (F2P, espectando partidas).
*   **Elementos clave en pantalla**:
    *   El Axolotito bebé recién nacido flota en el centro con un diálogo entusiasta: `"¡Estoy listo para las ligas mayores! ¿Me llevas a una mesa?"`.
    *   Dos botones de acción verticales y contrastantes:
        1.  **Botón Premium (Principal)**: `"💎 ¡Que juegue de verdad!"` en un gradiente rosa/magenta brillante con una sombra de neón muy marcada. Subtexto: `"Compra GAL → acceso completo al juego"`.
        2.  **Botón F2P (Secundario)**: `"👁️ Primero quiero ver cómo se juega"` con bordes transparentes esmerilados (estilo outline). Subtexto: `"Entra gratis · tu Axolotito especta partidas reales"`.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
Game decision screen layout. In the upper half, a cute pink baby axolotl floats in clean water, speaking via a central dialog box: "¡Estoy listo para las ligas mayores! ¿Me llevas a una mesa?". In the lower half, two large selection cards are stacked vertically. The top card is a premium button with a hot pink-to-magenta gradient and glowing outline reading "💎 ¡Que juegue de verdad!" with small subtitle "Compra GAL -> acceso completo al juego". The bottom card is a dark glassmorphic button with thin white borders reading "👁️ Primero quiero ver cómo se juega" with subtitle "Entra gratis · tu Axolotito especta partidas reales". Clean game UI design, dark background.
```

---

## 👁️ Ventana 9: Modo Espectador F2P (AwakeAxoSpectator)

*   **Propósito**: Pantalla de juego para el usuario gratuito post-tutorial. El Axolotito acompaña desde "las gradas" del cenote mientras ve partidas reales y acumula fragmentos.
*   **Elementos clave en pantalla**:
    *   Mitad superior: Una partida de Lotería en vivo desarrollándose (tableros de otros jugadores marcándose).
    *   Mitad inferior/esquina: El Axolotito sentado en una grada de piedra oscura con unos pequeños binoculares o señalando emocionado.
    *   Diálogo cómico del Axolotito: `"Si tuviera GAL ahorita mismo, estaría ganando. Te lo juro."`.
    *   Un panel flotante de estadísticas de recompensas: `GAL hoy: +0.0` | `Fragmentos: +15` (icono de cristal morado).
    *   Botón prominente de upgrade: `"💎 Comprar GAL — que juegue de verdad"` con diseño rosa neón.

### 📝 Prompt para Gemini (Imagen 3 / Generador de UI):
```text
High-fidelity game UI mockup for a spectator mode. The upper section shows an active multiplayer Lotería game board being marked. In the lower section, a cute pink axolotl sits on a stone ledge wearing tiny binoculars, watching the game. A glassmorphic speech bubble shows Spanish text: "Si tuviera GAL ahorita mismo, estaría ganando. Te lo juro." Next to it, a modern stats card displays "GAL hoy: +0.0" and "Fragmentos: +15" with a glowing purple crystal icon. At the bottom, a glowing hot pink call-to-action button reads "💎 Comprar GAL — que juegue de verdad". Sleek dark theme UI, Xochimilco neon accents.
```
