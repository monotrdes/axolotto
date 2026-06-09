---
tags: [conceptos, axolotitos, stats]
description: "Estadisticas de Axolotito en detalle — SUERTE, OJO, PILA y SAL explicadas | Axolotito stats in detail — LUCK, FOCUS, STAMINA and SALINITY explained"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Estadisticas del Axolotito — Guia Profunda

> **Cada Axolotito tiene 4 estadisticas principales que definen como juega, cuanto gana y cuanto aguanta.** Esta pagina es la referencia definitiva: que hace cada stat, como se calculan sus efectos, como mejorarlas y como combinarlas segun tu estilo de juego.

---

## Las 4 Estadisticas Fundamentales

Tu Axolotito gira en torno a cuatro numeros. Entenderlos es la diferencia entre un jugador casual y uno que consistentemente gana mas.

---

## 1. SUERTE (Luck) 🍀

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 10 |
| Tipo | Estadistica ofensiva — te da mas recompensas y segundas oportunidades |

La Suerte es el stat que todo jugador quiere alta. No afecta directamente si ganas o pierdes una partida, pero hace que ganar sea mas rentable y que perder duela menos.

### Bonus de Premio

Cada vez que tu Axolotito gana una partida, la Suerte anade un extra de Frijolitos (FRJ) al premio base. El calculo es sencillo:

- **Bonus de FRJ** = (tu Suerte dividida entre 1000) multiplicado por el premio base
- Con **Suerte 100**, recibes un **+10%** de FRJ en cada premio
- Con Suerte 50, recibes +5%
- Con Suerte 10 (default), recibes +1%

No parece mucho al principio, pero a lo largo de cientos de partidas la diferencia es enorme. Un grinder con Suerte 100 gana significativamente mas FRJ que uno con Suerte 10, incluso si ambos ganan el mismo numero de partidas.

### Salvada Afortunada (Lucky Save)

Esta es quiza la mecanica mas querida de la Suerte. Cuando tu Axolotito esta a punto de perder una partida, la Suerte puede activar una **segunda oportunidad** y salvarte.

- **Probabilidad de salvada** = (Suerte dividida entre 1000) multiplicado por 0.5
- Con **Suerte 100**: **5%** de probabilidad de salvada (maximo)
- Con Suerte 50: 2.5%
- Con Suerte 10 (default): 0.5%

Solo se puede activar **una vez por partida**. Si ya te salvaste una vez y vuelves a estar a punto de perder, no hay segunda salvada. Aun asi, ese 5% en Suerte 100 significa que 1 de cada 20 partidas perdidas se convierte en victoria — una diferencia brutal en sesiones largas.

### Bonus en Gashapon

La Suerte tambien influye en las tiradas de Gashapon (capsulas de accesorios y cartas). Las tasas de drop de objetos raros mejoran ligeramente con Suerte alta. El efecto es pequeno pero consistente — como un empujoncito extra cada vez que abres una capsula.

### Como Aumentar la Suerte

- **Naturaleza Suertudo**: otorga **+10** de Suerte base
- **Impronta (imprinting)**: si tu padrino gana muchas partidas durante la fase de impronta, tu Suerte base sube
- **Subir de nivel**: cada nivel ganado da puntos que puedes distribuir; invertir en Suerte es una estrategia clasica

---

## 2. OJO (Focus) 👁️

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 50 |
| Tipo | Estadistica ofensiva/de precision — la mas importante para marcar cartas consistentemente |

El Ojo es, para muchos jugadores, **la estadistica mas importante del juego**. Controla que tan seguido tu Axolotito "ve" las cartas que el Griton canta.

### Probabilidad de Fallo (Miss Chance)

Cuando el Griton canta una carta que SI esta en tu tablero, tu Axolotito deberia marcarla. Pero no siempre lo hace — a veces "no la ve". Esa es la probabilidad de fallo:

- **miss_chance** = maximo 0, minimo entre 0.3 y (100 menos tu Ojo) multiplicado por 0.003
- Con **Ojo 100**: **0%** de fallo — jamas te pierdes una carta. Marcado perfecto.
- Con **Ojo 50** (default): aproximadamente **15%** de fallo
- Con **Ojo 0**: **30%** de fallo — casi una de cada tres cartas se te pasa

Traducido a partidas reales: con Ojo 50, de cada 10 cartas tuyas que el Griton canta, en promedio te pierdes 1 o 2. Con Ojo 100, las marcas todas. Con Ojo 0, te pierdes 3 de cada 10 — un desastre.

### Regla Practica

Cada **10 puntos de Ojo** equivalen aproximadamente a un **3% menos de probabilidad de fallo**. Subir de 50 a 70 reduce tu miss chance de ~15% a ~9% — una mejora notable que se siente en cada partida.

### Agilidad en Modo Manual

En el modo PvP manual, el Ojo se traduce en Agilidad: a mayor Ojo, mas rapido puedes marcar cartas en tu tablero (menor delay entre marcaciones). Esto solo aplica en modalidades manuales — en CPU auto-play, el Ojo solo afecta la probabilidad de fallo.

### Como Aumentar el Ojo

- **Naturaleza Metodico**: otorga **+10** de Ojo base
- **Impronta (imprinting)**: partidas con alta precision durante la impronta mejoran el Ojo base
- **Subir de nivel**: invertir puntos de nivel en Ojo es la estrategia recomendada para grinders de CPU

---

## 3. PILA (Stamina) 🔋

| Propiedad | Valor |
|-----------|-------|
| Rango | 50 a 200 |
| Valor inicial | 100 |
| Tipo | Estadistica de resistencia — cuantas partidas aguantas y que tan rapido te recuperas |

La PILA representa la energia fisica de tu Axolotito. No afecta si ganas o pierdes una partida individual, pero determina **cuantas partidas puedes jugar** antes de necesitar dormir y **que tan rapido te recuperas**.

### Reserva de Energia

Tu energia maxima es igual a tu PILA. Cada partida consume energia:

- Cada partida cuesta **10 de energia**
- Con **PILA 100**, puedes jugar alrededor de **10 partidas** antes de quedarte sin energia
- Con PILA 200, juegas **20 partidas** antes de necesitar dormir
- Con PILA 50 (minimo), solo **5 partidas**

Ademas, cada partida reduce tu energia maxima actual en **3 puntos** (piso minimo: 10). Esto simula el cansancio acumulado. Despues de 30 partidas sin dormir, tu maximo de energia puede bajar de 100 a 10 — practicamente necesitas dormir tras cada partida. **Dormir restaura completamente tu energia maxima a su valor original.**

### Velocidad de Sueno

No todos los Axolotitos duermen igual. La PILA controla que tan rapido te recuperas:

- **Formula**: tiempo de sueno = 1 minuto multiplicado por un factor
- El factor va de **1.0** (PILA 50, el mas lento) hasta **0.35** (PILA 200, el mas rapido)
- **PILA 200 recupera un 65% mas rapido que PILA 50**
- PILA 100 (default) tiene un factor intermedio de aproximadamente 0.74

En la practica: un Axolotito con PILA 200 duerme en ~21 segundos lo que a uno con PILA 50 le toma 1 minuto completo. Para jugadores que quieren grindear sin parar, PILA alta es obligatoria.

### Desgaste Maximo de Energia

Cada partida reduce tu energia maxima actual en 3 puntos, con un piso de 10. Esto significa:

- Empiezas con maximo = tu PILA (digamos 100)
- Tras 10 partidas: maximo bajo a 70
- Tras 20 partidas: maximo bajo a 40
- Tras 30 partidas: maximo bajo a 10 (el piso)
- **Dormir restaura el maximo a su valor completo (100)**

El mensaje es claro: duerme regularmente. No hay forma de evitar el desgaste, solo administrarlo.

### Como Aumentar la PILA

- **Naturaleza Sabio**: otorga **+15** de PILA base (el boost mas grande de stats por naturaleza)
- **Impronta (imprinting)**: jugar 3 o mas partidas en una misma sesion durante la impronta mejora la PILA
- **Subir de nivel**: ideal para jugadores que priorizan volumen de partidas sobre calidad

---

## 4. SAL (Salinity) 🧂

| Propiedad | Valor |
|-----------|-------|
| Rango | 0 a 100 |
| Valor inicial | 5 |
| Tipo | **ANTI-ESTADISTICA** — quieres tenerla LO MAS BAJA POSIBLE |

La SAL es la estadistica trampa. No lo parece al principio — empieza baja (5) y parece inofensiva. Pero si la dejas subir, arruina el rendimiento de tu Axolotito de formas sutiles pero devastadoras.

**Regla de oro: manten tu SAL por debajo de 10. Siempre.**

### Efecto en Modo CPU — Sesgo del Mazo (Deck Bias)

Este es el efecto mas insidioso de la SAL. Cuando juegas contra la CPU, las cartas que SI estan en tu tablero son empujadas hacia la segunda mitad del mazo:

- Probabilidad por carta = el valor menor entre 0.5 y tu SAL dividida entre 200
- Con **SAL 100**: cada carta tuya en la primera mitad del mazo tiene **50%** de probabilidad de ser enviada al final
- Con **SAL 50**: 25% de probabilidad
- Con **SAL 5** (default): solo **2.5%** de probabilidad — casi imperceptible

Esto significa que con SAL alta, tus cartas salen mas tarde en la partida. Y si tus cartas salen mas tarde, marcas menos, ganas menos patrones, y pierdes mas partidas. Es una desventaja silenciosa que se acumula partida tras partida.

### Efecto en Multijugador — Desliz (Slip)

En partidas multijugador, la SAL tiene un segundo efecto que se suma a la probabilidad de fallo del Ojo:

- **slip_chance** = el valor menor entre 0.333 y tu SAL dividida entre 300
- Con **SAL 100**: **33%** de probabilidad de desliz — una de cada tres cartas se te escapa
- Con **SAL 50**: ~16.7% de desliz
- Con **SAL 5** (default): solo **~1.7%** de desliz — casi irrelevante

Lo brutal es que el desliz **se acumula con la probabilidad de fallo del Ojo**. Un Axolotito con Ojo 50 (15% miss) y SAL 100 (33% slip) tiene una probabilidad combinada de fallo cercana al 45%. Es decir, casi la mitad de tus cartas no se marcan. En multijugador competitivo, esto es una sentencia de derrota.

### Entropia de Sala

En salas multijugador, el promedio de SAL de todos los jugadores humanos determina el nivel de "caos" o "desorden" visual de la sala. Es un efecto puramente estetico y de sabor — la sala se ve mas turbulenta o mas tranquila segun la SAL colectiva. No afecta la mecanica de juego directamente.

### Modo Saladito — Donde SAL es BUENA

Existe una excepcion fascinante: el **Modo Saladito**. En este modo especial, las reglas se invierten:

- **Gana quien marca MENOS cartas**, no mas
- Una SAL alta se convierte en ventaja — menos marcas = mas cerca de ganar
- Axolotitos con SAL alta, que normalmente serian descartados, se vuelven valiosos

Esto crea un nicho estrategico: puedes criar Axolotitos especificamente para Modo Saladito con SAL alta, Ojo bajo, y ser imparable en ese formato.

### Como AUMENTA la SAL (malo — quieres evitarlo)

- **Padrino con SAL alta** durante la impronta: transfiere parte de su SAL al Axolotito
- **Perder partidas** durante la impronta: cada derrota sube la SAL
- **Baja precision** durante la impronta: marcar pocas cartas correctamente aumenta la SAL

### Como DISMINUYE la SAL (bueno — quieres hacer esto)

- **Padrino con SAL baja** (menor a 20) durante la impronta: otorga un delta de **-6 a -10** de SAL
- **Naturaleza Timido**: otorga **-10** de SAL base (el mejor anti-SAL natural)
- **Ganar partidas** durante la impronta: cada victoria reduce la SAL

---

## Interacciones Entre Estadisticas

Las cuatro estadisticas no existen en el vacio. Se combinan de formas estrategicas clave:

### Ojo + SAL — La Pareja de la Precision

Tu probabilidad TOTAL de no marcar una carta es la combinacion de:
- **Miss Chance** (del Ojo): no ves la carta
- **Slip Chance** (de la SAL): la ves pero se te escapa

Ambas se acumulan. Un Axolotito con Ojo 50 y SAL 100 falla aproximadamente el 45% de las cartas. Uno con Ojo 100 y SAL 5 falla menos del 2%. La diferencia es astronomica.

**Regla practica**: si tu SAL esta por encima de 20, subir Ojo se vuelve menos efectivo. Primero baja la SAL, luego invierte en Ojo.

### Suerte + Ojo — El Combo Ofensivo

- **Ojo** te hace marcar cartas consistentemente (ganar mas partidas)
- **Suerte** hace que esas victorias paguen mas (ganar mas FRJ por partida)

Es la combinacion clasica para grinders de CPU: maximiza tu tasa de victorias con Ojo y maximiza tus recompensas con Suerte. En ese orden — de nada sirve +10% de premio si no ganas la partida.

### PILA + SAL — El Combo de Resistencia

- **PILA** te deja jugar mas partidas por ciclo de sueno
- **SAL baja** evita el sesgo del mazo que alarga tus partidas y reduce tus victorias

Un Axolotito con PILA 200 y SAL 5 puede grindear 20 partidas eficientes antes de dormir 21 segundos. Uno con PILA 50 y SAL 80 juega 5 partidas malas y duerme 1 minuto. La diferencia de productividad es mas de 10x.

---

## Estadisticas Secundarias

Existen cuatro estadisticas adicionales en el ADN del Axolotito, pero actualmente **no tienen efecto en la jugabilidad principal**. Son puramente cosmeticas o mapean rasgos visuales:

| Stat | Default | Proposito Actual |
|------|---------|-----------------|
| **Carisma** | 10 | Mapea el tipo de boca (rasgo visual). Sin efecto en juego. |
| **Agilidad** | 10 | En modo PvP manual, controla el delay entre marcaciones (800ms a 2500ms). Derivada del Ojo por conveniencia. |
| **Sabiduria** | 10 | Mapea el tipo de frente (rasgo visual). Sin efecto en juego. |
| **Fuerza** | 10 | Mapea el tipo de extremidades (rasgo visual). Sin efecto en juego. |

Estos stats existen en la blockchain y pueden verse en el ADN, pero no necesitas preocuparte por ellos para jugar. Si en el futuro se implementan mecanicas que los usen, esta pagina se actualizara.

---

## Prioridad de Stats por Estilo de Juego

No todos los jugadores necesitan lo mismo. Aqui esta la prioridad recomendada segun como juegas:

### Grinder de CPU
Si tu plan es dejar a tu Axolotito jugando solo contra la maquina por horas:

1. **Ojo** — marcar consistentemente es lo mas importante. Sin precision no hay victorias.
2. **PILA** — mas partidas por ciclo, sueno mas rapido, mas volumen total.
3. **Suerte** — premios mas grandes sobre las victorias que ya tienes.
4. **SAL** — mantenla lo mas baja posible; el sesgo de mazo destruye tu tasa de victorias.

### Competidor Multijugador
Si compites contra otros jugadores humanos:

1. **Ojo** — en PvP, cada carta no marcada es una derrota frente a oponentes atentos.
2. **Suerte** — premios mas grandes y las salvadas afortunadas pueden cambiar partidas cerradas.
3. **PILA** — aguanta sesiones largas sin tener que retirarte a dormir.
4. **SAL** — mantenla **extremadamente baja**. El desliz en multijugador es brutal y se suma al fallo de Ojo.

### Especialista Saladito
Si te dedicas al modo de reglas invertidas:

1. **SAL** — ALTA es mejor. Menos marcas = mas cerca de ganar.
2. **PILA** — mismo razonamiento que siempre: mas partidas, mejor.
3. **Ojo** — en Saladito, un Ojo bajo es preferible (menos marcas). Un Ojo alto te perjudica.

### Staker Pasivo
Si solo pones a tus Axolotitos en staking sin jugar partidas:

- Las estadisticas de juego **no importan**. El staking usa los rasgos visuales (boca, frente, extremidades, etc.), no las estadisticas de rendimiento. Invierte en Axolotitos con rasgos raros, no con stats altos.

---

## Resumen — La Regla de Oro

> **Ojo arriba, Suerte arriba, PILA arriba, SAL abajo.** Esa es la formula universal. Un Axolotito con Ojo 80+, Suerte 60+, PILA 150+, y SAL menor a 10 es una maquina de ganar en cualquier modo. Todo lo demas son matices.

---

## English

Axolotito stats are the four core numbers that define how your digital axolotl performs in the game. This page explains every mechanic in detail.

**LUCK (Suerte)** ranges from 0 to 100 and starts at 10. It gives you a prize bonus on every win — at 100 Luck you get +10% extra FRJ per prize — and a "Lucky Save" mechanic that can turn a loss into a win with up to 5% probability. It also slightly improves Gashapon drop rates. Luck is raised through the Suertudo nature (+10), winning imprinting matches, and leveling.

**FOCUS (Ojo)** is arguably the most important stat. Ranging from 0 to 100 (default 50), it controls how often your Axolotito misses marking a card that was called. At 100 Focus the miss chance is 0% — perfect marking. At 50 Focus it is about 15%, and at 0 Focus it hits 30%. Every 10 points of Focus removes roughly 3% miss chance. In manual PvP mode, Focus also maps to Agility (faster card marking). Raised via the Metodico nature (+10), high-accuracy imprinting matches, and leveling.

**STAMINA (Pila)** ranges from 50 to 200 (default 100) and controls endurance. Each match costs 10 energy, so a 100-PILA Axolotito can play roughly 10 matches before needing sleep, while a 200-PILA one can play 20. Sleep recovery speed scales from a 1.0x factor at PILA 50 down to 0.35x at PILA 200 — so high-PILA Axolotitos sleep 65% faster. Each match also decays your current max energy by 3 (floor 10); sleep fully restores it. Raised via the Sabio nature (+15, the biggest single-stat boost), playing 3+ matches in a session during imprinting, and leveling.

**SALINITY (Sal)** is the anti-stat — you want it as LOW as possible. Default 5 is good. In CPU mode, high SAL pushes your cards to the back half of the deck (up to 50% chance per card at SAL 100), making you mark later and lose more. In multiplayer, SAL adds a "slip" miss chance (up to 33% at SAL 100) that stacks with Focus miss chance. Low-SAL padrinos, the Timido nature (-10 SAL), and winning imprinting matches all decrease it. SAL increases through high-SAL padrinos, losing imprinting matches, and low accuracy.

The one exception is **Saladito Mode**, where rules are inverted (fewer marks = better) — high-SAL Axolotitos become valuable here.

**Stat priority by playstyle**: CPU grinders want Focus first, then PilA, then Luck, and minimal SAL. Multiplayer competitors want Focus first, then Luck, then PilA, and SAL kept extremely low. Saladito specialists want high SAL above all else. Passive stakers do not need combat stats at all — staking uses visual traits, not these numbers.

## Quick Reference / Referencia Rapida

| Concept / Concepto | Value / Valor |
|---|---|
| Suerte (Luck) rango | 0 a 100 |
| Suerte (Luck) default | 10 |
| Suerte 100 — bonus de premio | +10% FRJ extra por victoria |
| Suerte 100 — Lucky Save | 5% de salvada de derrota |
| Ojo (Focus) rango | 0 a 100 |
| Ojo (Focus) default | 50 |
| Ojo 100 — miss chance | 0% (marcado perfecto) |
| Ojo 50 — miss chance | ~15% de fallo |
| Ojo 0 — miss chance | 30% de fallo |
| PILA (Stamina) rango | 50 a 200 |
| PILA (Stamina) default | 100 |
| Energia por partida | 10 puntos |
| Partidas con PILA 100 | ~10 partidas por ciclo |
| Partidas con PILA 200 | ~20 partidas por ciclo |
| Tiempo de sueno (PILA 50) | 1 minuto (factor 1.0) |
| Tiempo de sueno (PILA 200) | ~21 segundos (factor 0.35) |
| Desgaste max por partida | -3 de energia maxima (piso 10) |
| SAL (Salinity) rango | 0 a 100 |
| SAL (Salinity) default | 5 (bueno, mantener bajo) |
| SAL 100 — Deck Bias CPU | 50% por carta (empujada al final) |
| SAL 100 — Slip MP | 33% de desliz adicional |
| SAL 5 — Deck Bias CPU | ~2.5% (casi imperceptible) |
| SAL 5 — Slip MP | ~1.7% (casi irrelevante) |
| Naturaleza Suertudo | +10 Suerte |
| Naturaleza Metodico | +10 Ojo |
| Naturaleza Sabio | +15 PILA (mayor boost individual) |
| Naturaleza Timido | -10 SAL (reduce la anti-stat) |
| Carisma default | 10 (cosmetico — tipo de boca) |
| Agilidad default | 10 (PvP manual — delay de marcacion) |
| Sabiduria default | 10 (cosmetico — tipo de frente) |
| Fuerza default | 10 (cosmetico — tipo de extremidades) |

---

→ See also / Ver tambien: [[02-axolotitos]] · [[04-naturalezas-y-personalidad]] · [[05-rasgos-visuales-y-rareza]] · [[11-webitos-y-crianza]] · [[00-INDEX]]
