---
tags: [conceptos, axolotitos]
description: "Guia completa de Axolotitos — stats, naturaleza, rasgos, cuidado y nivelacion | Complete Axolotito guide — stats, natures, traits, care and leveling"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Axolotitos — Tus Companeros del Cenote

> **Los Axolotitos son el corazon de Axolotto.** Son tus mascotas digitales, tus jugadores estrella, tus amigos anfibios que compiten por ti en la Lotería Mexicana. Esta pagina te explica absolutamente TODO sobre ellos: como funcionan, como cuidarlos, como subirlos de nivel y como conseguir el equipo perfecto.

---

## Que es un Axolotito?

Un **Axolotito** es una criatura digital unica inspirada en el ajolote mexicano (*Ambystoma mexicanum*). Es mucho mas que una mascota virtual — es tu personaje jugador en el universo de Axolotto.

**En terminos tecnicos**, cada Axolotito es un **NFT ERC-721** con un ADN de 256 bits (`uint256`) grabado en la blockchain. Este ADN define su apariencia visual (color de piel, tipo de branquias, forma de ojos, cola, etc.) y sus estadisticas base. No existen dos Axolotitos identicos — cada uno es irrepetible.

**En terminos de juego**, tu Axolotito es quien realmente **juega la Lotería por ti**. Tu eliges el tablero, decides el presupuesto, configuras los limites de ganancia/perdida... y el Axolotito ejecuta las partidas. Tu solo revisas los resultados cuando quieras.

> **Dato curioso:** El ajolote real es una especie endemica de Xochimilco, Ciudad de Mexico, en peligro de extincion. Axolotto lo convierte en protagonista digital para celebrar su existencia y crear conciencia.

---

## Las 4 Estadisticas Principales

Todos los Axolotitos nacen con 4 stats fundamentales que determinan su rendimiento en el juego. Estas son las que mas te importan en el dia a dia.

### SUERTE 🍀 — La Estadistica del Exito

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 10 |
| Que hace | Aumenta tus premios y te salva de perder |

La **Suerte** es tu mejor amiga. Cada punto de Suerte mejora tus posibilidades en varios frentes:

- **Bonus en premios:** Al ganar una partida, la Suerte aplica un multiplicador extra sobre el premio base. Con Suerte alta, los premios grandes se vuelven enormes.
- **Salvada Milagrosa (Lucky Save):** Hasta **5% de probabilidad** de evitar que un bot gane cuando tu estas a punto de perder. Es ese momentito de "no me lo puedo creer" que te salva la cartera.
- **Mejores drops en Gashapon:** Los Axolotitos con Suerte alta tienden a obtener mejores resultados al abrir capsulas. La Suerte se toma en cuenta en el momento del drop.

> **Consejo:** Si te gusta el Gashapon o juegas en salas dificiles, prioriza Axolotitos con Suerte alta.

---

### OJO 👁️ — La Estadistica de Precision

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 50 |
| Que hace | Reduce la probabilidad de fallar cartas cantadas |

Cuando el Griton canta una carta, tu Axolotito debe **marcarla en su tablero**. Si la carta esta en el tablero pero el Axolotito no la marca... eso es un **fallo**. Y los fallos cuestan partidas.

El **OJO** (Enfoque / Focus) determina que tan probable es ese fallo:

| OJO | Probabilidad de Fallo |
|-----|----------------------|
| 0 | ~30% — casi una de cada tres cartas se le pasa |
| 25 | ~22% |
| 50 | ~15% — valor inicial, equilibrado |
| 75 | ~7% |
| 100 | 0% — no falla NUNCA |

> **Consejo:** Para multijugador competitivo, el OJO es probablemente el stat mas importante. Un Axolotito con OJO 100 nunca pierde por despiste.

---

### PILA 🔋 — La Estadistica de Resistencia

| Propiedad | Valor |
|-----------|-------|
| Rango | 50 a 200 |
| Valor inicial | 100 |
| Que hace | Determina cuantas partidas puedes jugar y que tan rapido descansas |

La **PILA** (Stamina) es tu barra de energia maxima. Es el stat que define tu ritmo de juego:

- **Mas energia maxima:** Con PILA 50, tu maximo de energia es 50 — pocas partidas. Con PILA 200, tienes el doble del maximo normal. Mas partidas antes de necesitar dormir.
- **Recuperacion acelerada:** Al dormir, un Axolotito con PILA alta recupera energia mas rapido. Con PILA 200, el sueno es hasta **65% mas rapido** que con PILA 50.
- **Cada partida cuesta 10 de energia.** Con PILA 100, juegas ~10 partidas. Con PILA 200, ~20 partidas antes de agotarte.

> **Consejo:** Si planeas largas sesiones de juego (tipo "dejar el bot toda la noche"), busca PILA alta.

---

### SAL 🧂 — La Anti-Estadistica

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 5 |
| Que hace | Entorpece el rendimiento — entre mas baja, mejor |

La **SAL** (Salinidad / Salinity) es la estadistica que **NO quieres**. Es un lastre, un factor de mala suerte que afecta negativamente el rendimiento:

- **Deslizamiento de cartas:** En partidas CPU, la SAL hace que tus cartas se deslicen al fondo del mazo, tardando mas en aparecer. Entre mas SAL, mas atras quedan tus cartas.
- **En multijugador:** La SAL se vuelve particularmente peligrosa. A SAL = 100, tienes hasta **33% de probabilidad de que una carta cantada NO se marque** en tu tablero (un "slip"). En otras palabras: el OJO y la SAL se oponen — pero la SAL se aplica DESPUES, asi que ni el OJO 100 te salva del todo.
- **Piensalo asi:** SUERTE, OJO y PILA jalan hacia arriba. SAL jala hacia abajo. Un Axolotito con stats decentes pero SAL alta rinde peor que uno con stats bajos y SAL cero.

> **Consejo crucial:** Al elegir un Axolotito para comprar o criar, revisa la SAL antes que cualquier otra cosa. Un Axolotito con SAL arriba de 30 ya empieza a ser problematico. Arriba de 60 es casi injugable en multijugador.

---

## El Sistema de Energia

La energia es el recurso que limita cuantas partidas puedes jugar antes de descansar. Entender el sistema de energia es clave para optimizar tu juego.

### Conceptos Clave

| Concepto | Explicacion |
|----------|-------------|
| **energy_current** | Tu energia actual. Empieza en 100. Gastas 10 por partida (CPU o multijugador). |
| **energy_max_current** | Tu energia maxima efectiva. Empieza en 100. Decae con el uso. |
| **Decaimiento** | Cada partida jugada reduce `energy_max_current` en **3 puntos**. Es acumulativo. |
| **Piso** | `energy_max_current` nunca baja de **10**. Siempre podras jugar al menos 1-2 partidas. |
| **Dormir** | Restaura `energy_current` y resetea `energy_max_current` a su valor original (tu PILA). |
| **Umbral de sueno** | Solo puedes dormir cuando tu energia actual esta por debajo del **85%** del maximo actual. |

### Ejemplo de una Sesion de Juego

```
Inicio: energy_current = 100, energy_max_current = 100
Partida 1: current 90, max 97
Partida 2: current 80, max 94
Partida 3: current 70, max 91
Partida 4: current 60, max 88
Partida 5: current 50, max 85
...
Partida 10: current 0, max 70  ← sin energia, toca dormir
Dormir (~1 min) → current 100, max 100 de nuevo
```

> **Importante:** No puedes saltar de partida en partida para siempre. El sistema de decaimiento del maximo asegura que eventualmente necesites una pausa. Esta disenado para ser saludable — el bot se detiene, tu Axolotito descansa, tu tambien respiras.

### Comida: Recuperar Energia Sin Dormir

Si no quieres esperar el sueno, puedes alimentar a tu Axolotito:

| Alimento | Costo | Energia Restaurada |
|----------|-------|-------------------|
| **Algae Pellet** | 30 FRJ | +15 de energia |
| **Brine Shrimp** | 150 FRJ | +60 de energia |

La comida restaura `energy_current` pero **NO** resetea `energy_max_current`. El decaimiento solo se cura con sueno.

### Dormir

- El sueno tarda aproximadamente **1 minuto**.
- Axolotitos con PILA alta duermen mas rapido — hasta **65% mas rapido** en PILA 200.
- El boton de dormir solo aparece cuando tu energia esta por debajo del 85% del maximo actual.
- Al despertar: `energy_current` y `energy_max_current` se restauran completamente.
- Cuando la energia llega a **0**, el Axolotito **debe dormir**. No puede jugar hasta descansar.

---

## Los 4 Estados del Axolotito

En todo momento, tu Axolotito esta en uno de estos cuatro estados:

### IDLE — Disponible 😊

Estado por defecto. Tu Axolotito esta despierto, con energia, listo para lo que necesites:
- Puede jugar (CPU o multijugador)
- Puede comer
- Puedes equiparle accesorios
- Puedes revisar sus stats

### PLAYING — En Partida 🎮

El Axolotito esta jugando Lotería. Durante este estado:
- No puedes modificar su equipo
- No puedes cambiar su tablero asignado
- El progreso de la partida se actualiza en tiempo real (o al recargar)
- Si es modo CPU con bot automatico, el Axolotito sigue jugando solo hasta que se cumplan los limites o se agote la energia

### SLEEPING — Durmiendo 😴

El Axolotito esta descansando para recuperar energia:
- No puede jugar ni hacer nada
- La barra de sueno muestra el progreso (~1 minuto)
- Al despertar, energia completamente restaurada
- `energy_max_current` se resetea al valor de PILA (eliminando el decaimiento acumulado)

### WAITING_SETTLEMENT — Esperando Reporte 📋

La sesion de juego termino y el Axolotito espera que revises los resultados. Este es el "corte de caja":
- Ves una **boleta de rendimiento** con: ganancias/perdidas netas, XP ganada, partidas jugadas, victorias y derrotas
- Al confirmar con "Gracias por el esfuerzo", las ganancias se transfieren a tu cartera y el Axolotito recibe Puntos de Lealtad
- Despues del settlement, el Axolotito generalmente se va a dormir

---

## Nivelacion: Como Subir de Nivel

Los Axolotitos ganan **experiencia (XP)** al jugar partidas. Acumular suficiente XP los hace subir de nivel, mejorando sus estadisticas.

### Umbral de Subida de Nivel

La formula es simple:

> **XP necesaria para subir de nivel = nivel actual x 100**

Por ejemplo: para pasar de nivel 1 a nivel 2 necesitas 100 XP. De nivel 5 a nivel 6 necesitas 500 XP. De nivel 10 a 11 necesitas 1000 XP.

### Cuanta XP Ganas por Partida

**Modo CPU:**

| Resultado | XP para el Axolotito |
|-----------|---------------------|
| Victoria (facil) | +35 XP |
| Victoria (dificil) | +75 XP |
| Derrota (facil) | +8 XP |
| Derrota (dificil) | +15 XP |

**Modo Multijugador:**

| Resultado | XP para el Axolotito |
|-----------|---------------------|
| Premio 1 (primer lugar) | +50 XP |
| Premio 2 (segundo lugar) | +20 XP |
| Consolacion | +5 XP |

### Que Mejora al Subir de Nivel?

Al subir de nivel, todas las estadisticas principales (SUERTE, OJO, PILA) reciben una mejora gradual. La SAL no se modifica al subir de nivel — solo cambia mediante crianza y genes.

Ademas, niveles mas altos desbloquean acceso a:
- Salas de mayor dificultad
- Mejores tasas de staking
- Mayor visibilidad en rankings

---

## Equipamiento y Accesorios

Puedes vestir a tu Axolotito con accesorios. El equipamiento es **puramente cosmetico** — no afecta las estadisticas de juego. Su valor es de coleccion, personalizacion y estatus.

### Los 3 Slots de Equipo

| Slot | Que va | Ejemplos |
|------|--------|----------|
| **Cabeza** 🎩 | Sombreros, coronas, cascos | Gorro de mariachi, Corona de lirio, Casco de buzo, Diadema astral |
| **Ojos** 👓 | Lentes, gafas, antifaces | Gafas de sol, Monoculo dorado, Goggles de buceo, Antifaz de luchador |
| **Cuerpo** 👘 | Ropa, capas, armaduras | Poncho de Xochimilco, Capa de campeon, Chaleco táctico, Armadura de obsidiana |

### Como Conseguir Accesorios

- **Gashapon:** La fuente principal. Las capsulas de Plata y Oro tienen buenas probabilidades de accesorios raros.
- **Mercado P2P:** Compra a otros jugadores — a veces encuentras piezas que ya no estan en rotacion.
- **Eventos especiales:** Algunos accesorios son exclusivos de temporada (Dia de Muertos, Navidad, aniversario).

> **Nota:** Los accesorios NO afectan stats. Un Axolotito con el casco mas epico del juego tiene exactamente el mismo rendimiento que uno sin nada puesto. La moda es para el alma, no para la SUERTE.

---

## Limite de Axolotitos y Slots

No puedes tener Axolotitos infinitos. El juego limita cuantos Axolotitos activos puedes mantener.

| Estado de Membresia | Slots de Axolotito |
|---------------------|-------------------|
| Sin VIP | 6 slots |
| VIP Coral | 6 slots |
| VIP Dorado | 6 slots |
| VIP Axolite | 7 slots |

### Que Pasa si mi VIP Axolite Expira?

Si tienes 7 Axolotitos y tu VIP Axolite expira, el septimo Axolotito (el mas reciente) entra en estado **congelado**:
- No puede jugar, comer, dormir, ni venderse
- Al intentar usarlo, el sistema responde con error **HTTP 423 (Locked)**
- Sigue ocupando un slot — no desaparece, solo queda inactivo
- **Solucion:** Renovar el VIP Axolite para descongelarlo, o liberar (quemar) un Axolotito para bajar a 6 y recuperar el acceso normal

> **Consejo:** Si estas en VIP Axolite y sabes que va a expirar, planea con anticipacion cual Axolotito liberar o vendelo en el mercado P2P antes de que expire.

---

## La Formula de Poder (Rankings)

El **PODER** es una metrica global que resume que tan fuerte es tu Axolotito. Se usa para rankings y comparaciones rapidas:

> **PODER = SUERTE + OJO + PILA + (100 - SAL)**

En otras palabras: sumas tus tres stats positivas, y sumas el "inverso" de la SAL (porque SAL baja = mejor). El valor maximo teorico es **500**:

| Stat | Maximo | Contribucion |
|------|--------|-------------|
| SUERTE | 100 | +100 |
| OJO | 100 | +100 |
| PILA | 200 | +200 |
| (100 - SAL) | 100 (cuando SAL=0) | +100 |
| **TOTAL maximo** | | **500** |

Esto hace que la PILA sea el stat con mas peso en el ranking (porque llega a 200), seguido de SUERTE y OJO (llegan a 100). Un Axolotito con PILA alta naturalmente tendra mas PODER que uno con SUERTE alta, aunque ambos sean igual de valiosos segun tu estilo de juego.

---

## Como Conseguir un Axolotito

Hay tres caminos para obtener tu primer (o siguiente) Axolotito:

### 1. Tutorial — Tu Primer Axolotito Gratis 🎁

Al completar el tutorial del juego, recibes tu primer Axolotito completamente gratis. Es un Axolotito basico con stats iniciales (SUERTE 10, OJO 50, PILA 100, SAL 5) y sin rasgos especiales, pero es 100% funcional y te permite empezar a jugar de inmediato.

### 2. Criar desde un Webito 🥚

El metodo principal para obtener Axolotitos con genes unicos:

1. **Compra un Webito** (huevo) en la Tienda. Los precios van de 400 a 3000 FRJ dependiendo del tipo (Genesis, Expansion, Retail, Astral).
2. **Colocalo en un slot de incubacion** en tu Cenote.
3. **Incubalo por 7 dias.** Durante este periodo controlas la temperatura y proteges el huevo del frio con escudos. El clima de Xochimilco afecta el progreso.
4. **Apadrina el Webito (Imprinting):** Durante la incubacion, puedes alimentar al huevo con items que modifican los stats del futuro Axolotito (ej. reducir SAL, aumentar SUERTE).
5. **Eclosiona:** Al completar los 7 dias, el huevo eclosiona y nace tu Axolotito con stats y rasgos determinados por la incubacion y el apadrinamiento.

> Ver la guia completa en: [[11-webitos-y-crianza]]

### 3. Mercado P2P 🛒

Compra un Axolotito ya existente a otro jugador:
- Puedes ver sus stats ANTES de comprar
- Los precios varian segun stats, rareza de rasgos, nivel y equipamiento
- Los Axolotitos con SAL baja y SUERTE/OJO altos suelen ser los mas caros
- Ver detalles en: [[19-mercado-p2p]]

---

## Resumen para Principiantes

Si eres nuevo en Axolotto y solo quieres lo esencial:

1. Tu primer Axolotito es **gratis** al completar el tutorial.
2. Los 4 stats clave son **SUERTE** (ganar mas), **OJO** (no fallar), **PILA** (jugar mas), y **SAL** (entre menos, mejor).
3. Cada partida cuesta **10 de energia**. Sin energia toca dormir (~1 min).
4. **No te obsesiones con stats perfectos al inicio.** Aprende a jugar con lo que tienes. La diferencia entre un Axolotito "bueno" y uno "perfecto" solo se nota en niveles altos de juego.
5. **La SAL es traicionera.** Si estas comprando en el mercado P2P, revisa la SAL antes del precio.
6. Los accesorios son **puramente cosmeticos** — viste a tu Axolotito como quieras, no afecta el juego.
7. **El bot automatico es tu amigo.** Configura presupuesto, limites de perdida/ganancia, y deja que tu Axolotito juegue solo. Revisa los resultados cuando quieras.

---

