---
tags: [conceptos, axolotitos, naturalezas]
description: "Las 6 naturalezas de Axolotito y cómo afectan el rendimiento en partida | The 6 Axolotito natures and how they affect gameplay performance"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Naturalezas y Personalidad

> **Cada Axolotito nace con una naturaleza.** No es un simple modificador de stats — es su personalidad, su estilo de juego, su forma de ver el mundo. La naturaleza define cómo rinde en partida, cómo responde al apadrinamiento de Webitos, y qué tipo de jugador se beneficia más de tenerlo. Esta página te explica las 6 naturalezas, sus efectos precisos, sus ventajas y sus sacrificios.

---

## ¿Qué es una Naturaleza?

La **naturaleza** es un rasgo innato que todo Axolotito recibe aleatoriamente al nacer (eclosionar). No se puede cambiar, no se puede comprar, no se puede heredar de forma garantizada. Es como el signo zodiacal del Axolotito — una inclinación cósmica que define su carácter.

**En términos de juego**, la naturaleza aplica dos tipos de efectos:

1. **Modificadores de stats base:** Algunas naturalezas suben o bajan directamente los stats del Axolotito (SUERTE, OJO, PILA, SAL). Estos modificadores son permanentes y se aplican desde el nacimiento.
2. **Bonificadores de imprinting:** Cuando un Axolotito actúa como **padrino** de un Webito (huevo en incubación), su naturaleza afecta qué tan bien transmite ciertas cualidades al futuro Axolotito. Por ejemplo, un padrino Metódico transfiere mejor el OJO; un padrino Suertudo transfiere mejor la SUERTE.

> **Importante:** La naturaleza se asigna **aleatoriamente** al eclosionar. NO puedes elegirla. NO puedes cambiarla después. Los Webitos Astrales pueden tener mejores probabilidades de naturalezas raras, pero esto no está confirmado oficialmente.

---

## Las 6 Naturalezas

---

### 1. Metódico (Methodical) 🧐

> *"Nunca pierde una carta. Revisa dos veces. Respira una vez. Gana."*

El Metódico es el perfeccionista del Cenote. Cada carta que el Gritón canta, él ya la tiene marcada antes de que termine la sílaba. Su concentración es legendaria. Los jugadores competitivos lo adoran; los bots lo respetan.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| OJO (Focus) | **+10** |
| PILA (Stamina) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Focus (`focus_delta`) es positivo | Se multiplica por **1.25** (25% más) |

Esto significa que un padrino Metódico que juega bien (marcando cartas con precisión) transmite MUCHO mejor el OJO a sus Webitos apadrinados. Es la naturaleza ideal para criar Axolotitos con OJO alto.

**¿Para quién es mejor?**

- Jugadores de CPU que quieren marcar cartas de forma consistente, sin fallos.
- Competidores de multijugador donde cada carta perdida cuesta el premio.
- Criadores (Padrinos) que buscan pasar OJO alto a la siguiente generación.
- Grinders que priorizan la precisión sobre la cantidad de partidas.

**El sacrificio:** -5 PILA significa ~5 puntos menos de energía máxima. En términos prácticos, media partida menos por ciclo de sueño. Apenas se nota. Es el precio más bajo de todas las naturalezas por un beneficio excelente.

**Resumen para rápidos:** El Metódico es probablemente la mejor naturaleza para jugadores serios. +10 OJO por -5 PILA es un intercambio muy favorable.

---

### 2. Suertudo (Lucky) 🍀

> *"El caos lo adora. Las cartas caen en su lugar como si estuviera escrito."*

El Suertudo nació con una estrella en la frente. No es que juegue mejor — es que el universo conspira a su favor. Los premios son más grandes, las Salvadas Milagrosas ocurren más seguido, y las cápsulas de Gashapon le dan mejores drops. Es el consentido del RNG.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| SUERTE (Luck) | **+10** |
| PILA (Stamina) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Suerte (`luck_delta`) es positivo | Se multiplica por **1.25** (25% más) |

Un padrino Suertudo que gana partidas transmite mucha más SUERTE al Webito. Si además logra un jackpot durante el imprinting (+20 fijo de delta), el bonus 1.25x lo convierte en +25. Es la naturaleza soñada para criar Axolotitos de altos premios.

**¿Para quién es mejor?**

- Jugadores que persiguen jackpots y premios grandes.
- Fans del Gashapon (la SUERTE afecta los drops de cápsulas).
- Competidores de multijugador donde los premios son acumulativos y cada punto de SUERTE = más porcentaje del pozo.
- Criadores que quieren Axolotitos con SUERTE alta desde el nacimiento.

**El sacrificio:** Mismo que el Metódico: -5 PILA. Media partida menos por ciclo. Imperceptible para la mayoría de jugadores. El +10 SUERTE se traduce en +1% de probabilidad en cada tirada de premio — no suena a mucho, pero en cientos de partidas la diferencia es real.

**Resumen para rápidos:** Si juegas por los premios (no por la consistencia), el Suertudo es tu naturaleza. +10 SUERTE = premios más gordos, punto.

---

### 3. Hiperactivo (Hyperactive) ⚡

> *"Dormir es opcional. Ganar es obligatorio."*

El Hiperactivo no se cansa. Bueno, sí se cansa — pero se recupera como si tuviera un cargador rápido enchufado directo al sol. Duerme menos, juega más, descansa más rápido. Es el Axolotito perfecto para sesiones maratónicas de grinding.

**Efectos en juego:**

| Efecto | Valor |
|--------|-------|
| Recuperación de sueño | **25% más rápida** |
| OJO (Focus) | **-5** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el delta de Stamina (`stamina_delta`) es positivo | Se multiplica por **1.25** (25% más) |
| Recuperación de sueño del padrino | **25% más rápida** (puede apadrinar más partidas por sesión) |

El Hiperactivo como padrino no solo transmite mejor la PILA — también completa sesiones de imprinting más rápido porque duerme menos entre partidas. Más partidas de imprinting por hora = el Webito eclosiona con mejores stats de stamina en menos tiempo real.

**¿Para quién es mejor?**

- Jugadores que quieren maximizar partidas por hora.
- Grinders que dejan el bot automático funcionando largas sesiones.
- Jugadores impacientes que odian esperar el sueño de 1 minuto.
- Criadores que quieren completar el imprinting rápido.

**El sacrificio:** -5 OJO = aproximadamente **1.5% más de probabilidad de fallo** al marcar cartas (de ~15% a ~16.5% en OJO base). Es un costo real pero manejable. Lo notas, pero no te arruina. Simplemente fallarás 1 o 2 cartas más por cada 100 cantadas.

**Resumen para rápidos:** Velocidad sobre precisión. Si juegas 50 partidas al día, el Hiperactivo te ahorra varios minutos de sueño. Si juegas 10 partidas al día, ni lo notas — mejor elige Metódico.

---

### 4. Glotón (Glutton) 🍽️

> *"Se come lo que sea. ¿Pellet? Desapareció. ¿Camaron? Desapareció. ¿La victoria? También desapareció, pero feliz."*

El Glotón vive para comer. Su metabolismo es una maravilla — exprime cada caloría de cada pellet como si fuera un banquete. Donde otros ven una Algae Pellet de 15 de energía, él ve 19.5. Donde otros ven un Brine Shrimp de 60, él ve 78.

**Efectos en juego:**

| Efecto | Valor |
|--------|-------|
| Energía restaurada por comida | **+30%** |
| OJO (Focus) | **-10** |

| Alimento | Energía normal | Energía para Glotón |
|----------|---------------|---------------------|
| Algae Pellet (30 FRJ) | +15 | **+19.5** |
| Brine Shrimp (150 FRJ) | +60 | **+78** |

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Si el padrino **pierde** una partida de imprinting | Todos los deltas negativos se reducen al **80%** de su magnitud |

Este es un efecto sutil pero poderoso. Cuando un padrino pierde, normalmente castiga los stats del Webito con deltas negativos (por ejemplo, -10 de SUERTE). Un padrino Glotón reduce ese castigo: el -10 se convierte en -8. No elimina el daño, pero lo amortigua. Es como un airbag para malas rachas.

**¿Para quién es mejor?**

- Jugadores con abundante FRJ que prefieren alimentar en vez de dormir.
- Jugadores F2P que optimizan cada pellet — estiras tu FRJ un 30% más.
- Espectadores que no quieren esperar el sueño y tienen FRJ de sobra.
- Criadores que quieren proteger a sus Webitos de los castigos por derrota durante el imprinting.

**El sacrificio:** -10 OJO = aproximadamente **3% más de probabilidad de fallo**. Es la penalización de OJO más grande entre todas las naturalezas. Con OJO base 50, pasas de ~15% de fallo a ~18%. Se nota. No es horrible, pero definitivamente sentirás que tu Axolotito "se distrae" más seguido.

**Resumen para rápidos:** Si tienes FRJ para gastar en comida, el Glotón te da mucha autonomía. Si estás corto de FRJ o juegas multijugador competitivo, el -10 OJO te va a doler.

---

### 5. Tímido (Shy) 🙈

> *"Se esconde de la voz del Gritón. Pero esconderse significa que las cartas malas tampoco lo encuentran."*

El Tímido no quiere problemas. Nace con la SAL más baja posible — casi como si el Cenote lo hubiera enjuagado antes de entregarlo. Es el Axolotito más puro, el menos contaminado, el que menos sufre los efectos negativos de la salinidad. En un mundo donde la SAL es el enemigo silencioso, el Tímido es un escudo.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| SAL (Salinity) | **-10** (al nacer) |
| SUERTE (Luck) | **-5** |

Con SAL base de 5, un Tímido empieza con **SAL = -5** que se ajusta a **SAL = 0** (el piso mínimo es 0). En otras palabras: nace sin salinidad. Cero. Nada. El sueño de todo jugador que odia el mecánico de SAL.

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Ninguno documentado actualmente | — |

El Tímido no tiene bonificadores de imprinting documentados en el sistema actual. Esto puede cambiar en futuras actualizaciones.

**¿Para quién es mejor?**

- Jugadores que ODIAN el mecánico de SAL y quieren la menor salinidad posible desde el día 1.
- Competidores de multijugador donde la SAL alta es devastadora (hasta 33% de slip).
- Jugadores que buscan un Axolotito "limpio" para criar — empezar con SAL 0 significa que los Webitos heredan menos salinidad base.
- Coleccionistas que valoran la pureza genética.

**El sacrificio:** -5 SUERTE = premios ligeramente más pequeños y ~0.25% menos de probabilidad de Salvada Milagrosa. Es un precio pequeño a cambio de eliminar completamente el problema de SAL.

**Dato curioso:** En el modo Saladito, donde los slips son BUENOS (te dan ventaja), el Tímido es la PEOR naturaleza posible. No te confundas — en Saladito quieres SAL alta, no baja. Para Saladito, busca un Sabio o cualquier naturaleza con SAL positiva.

**Resumen para rápidos:** La naturaleza anti-SAL. Si te desespera ver slips en multijugador, consigue un Tímido. Es la paz mental hecha Axolotito.

---

### 6. Sabio (Wise) 🦉

> *"Los Axolotitos más viejos son los más sabios. Pero la sabiduría viene con sal — han visto cosas."*

El Sabio es el tanque de energía definitivo. Ha vivido, ha jugado, ha perdido, ha ganado. Su experiencia se traduce en una resistencia física descomunal. Puede jugar más partidas que cualquier otro Axolotito antes de necesitar descanso. Pero la edad trae consigo una pizca de amargura — un poco de sal que se acumuló con los años.

**Efectos en stats:**

| Stat | Cambio |
|------|--------|
| PILA (Stamina) | **+15** |
| SAL (Salinity) | **+5** |

Con PILA base 100, un Sabio empieza con **PILA = 115**. Eso significa ~11-12 partidas por ciclo en vez de ~10. Con comida y buena gestión, puedes estirar las sesiones significativamente.

**Efecto en imprinting (como padrino):**

| Condición | Bonus |
|-----------|-------|
| Ninguno documentado actualmente | — |

El Sabio no tiene bonificadores de imprinting documentados en el sistema actual. Esto puede cambiar en futuras actualizaciones.

**¿Para quién es mejor?**

- Jugadores maratónicos que quieren el mayor pool de energía posible.
- Grinders que dejan el bot automático toda la noche — PILA 115 = más partidas antes del sueño obligatorio.
- Criadores que quieren pasar PILA alta a los Webitos (el factor de herencia es 10%-15% de la PILA del padrino).
- Jugadores que no temen un poco de SAL extra porque juegan principalmente CPU (donde la SAL es menos castigadora).

**El sacrificio:** +5 SAL = mayor probabilidad de slip y deck bias. En términos concretos, con SAL base 5 + 5 = SAL 10, tu probabilidad de slip en multijugador es aproximadamente **~3.3%** (comparado con ~1.7% en SAL 5). No es catastrófico, pero se nota. En CPU, tus cartas aparecerán ligeramente más tarde en el mazo.

**La compensación:** +15 PILA es el boost de stat individual más grande de todas las naturalezas. Si juegas principalmente CPU o no te preocupa tanto el slip en multijugador, el Sabio es un caballo de batalla.

**Resumen para rápidos:** Energía para días, pero con una pizca de sal. Si juegas muchas partidas y no te molesta un slip ocasional, el Sabio es excelente. Si juegas multijugador competitivo, la SAL extra puede ser frustrante.

---

## Resumen de las 6 Naturalezas

| Naturaleza | Efecto Principal | Sacrificio | Imprinting Bonus | Estilo de Juego |
|------------|-----------------|------------|------------------|-----------------|
| **Metódico** 🧐 | +10 OJO | -5 PILA | 1.25x a focus_delta positivo | Precisión y consistencia |
| **Suertudo** 🍀 | +10 SUERTE | -5 PILA | 1.25x a luck_delta positivo | Premios grandes |
| **Hiperactivo** ⚡ | Sueño 25% más rápido | -5 OJO | 1.25x a stamina_delta positivo | Velocidad y grinding |
| **Glotón** 🍽️ | +30% energía de comida | -10 OJO | Deltas negativos al 80% | Autonomía con FRJ |
| **Tímido** 🙈 | -10 SAL al nacer | -5 SUERTE | Ninguno documentado | Pureza anti-slip |
| **Sabio** 🦉 | +15 PILA | +5 SAL | Ninguno documentado | Maratones de partidas |

---

## Mejor Naturaleza por Modo de Juego

| Modo | Mejor Naturaleza | ¿Por qué? |
|------|-----------------|-----------|
| **CPU Rookies** | Metódico o Hiperactivo | OJO para marcar consistente, o velocidad para grinding rápido |
| **CPU Champions** | Metódico | Contra bots difíciles, cada carta fallada cuesta la partida. La consistencia lo es todo |
| **Multijugador competitivo** | Suertudo o Tímido | Suertudo = premios más grandes. Tímido = cero slips. Depende de tu prioridad |
| **Saladito** (3-4 AM) | Sabio o Hiperactivo | En Saladito los slips son BUENOS — quieres SAL alta, no baja. Sabio da +5 SAL. Cualquier naturaleza con PILA extra ayuda |
| **F2P / Espectador** | Glotón | Estira cada FRJ en comida. Menos dependencia del sueño. Buena autonomía |
| **Crianza (Padrino)** | Metódico o Suertudo | Bonus 1.25x en los stats más valiosos para la descendencia |
| **Grinding masivo (bot)** | Hiperactivo o Sabio | Más partidas por hora real. El Hiperactivo duerme más rápido; el Sabio aguanta más partidas por ciclo |

---

## Cómo Saber la Naturaleza de tu Axolotito

La naturaleza se muestra en la **AxoSheet** (la ficha de stats del Axolotito en el Nido). Busca la etiqueta junto al nombre del Axolotito — aparecerá como un ícono con el nombre de la naturaleza.

En la misma pantalla puedes ver:
- Los 4 stats principales (SUERTE, OJO, PILA, SAL) con los modificadores de naturaleza ya aplicados.
- El nivel actual y la XP acumulada.
- El historial de partidas y el rendimiento reciente.
- Si el Axolotito está actuando como padrino de algún Webito.

---

## Preguntas Frecuentes

### ¿Puedo cambiar la naturaleza de mi Axolotito?

**No.** La naturaleza es permanente. Se asigna al nacer y no hay objeto, ítem, ni mecánica en el juego que permita cambiarla. Es parte del ADN del Axolotito, grabado en la blockchain.

### ¿Los Webitos Astrales tienen mejores naturalezas?

Hay reportes de la comunidad que sugieren que los Webitos Astrales tienen mayor probabilidad de naturalezas "deseables" (Metódico, Suertudo, Hiperactivo), pero **esto no está confirmado oficialmente** por el equipo de desarrollo. Tómalo como rumor hasta que haya datos oficiales.

### ¿Qué naturaleza es la mejor para empezar?

**Metódico.** El +10 OJO te da una ventaja inmediata y visible (fallas menos cartas), y el -5 PILA apenas se nota. Además, si algún día decides criar, el bonus de imprinting 1.25x en Focus es excelente. Es la naturaleza más "redonda" para nuevos jugadores.

### ¿Qué naturaleza es la peor?

Ninguna naturaleza es objetivamente "mala". Cada una tiene un nicho. Dicho esto, si tuvieras que elegir la de menor utilidad general, probablemente sería **Glotón** — el -10 OJO es el castigo más severo, y el beneficio (+30% energía de comida) solo es útil si tienes FRJ para gastar. Pero incluso el Glotón tiene su público (F2P que optimizan recursos).

### ¿La naturaleza afecta el valor de reventa en el mercado P2P?

**Sí, y mucho.** Los Axolotitos con naturalezas "meta" (Metódico, Suertudo) se venden por más en el mercado P2P que aquellos con naturalezas menos populares. Un Axolotito Metódico con buenos stats puede valer el doble que uno Glotón con stats similares. La naturaleza es uno de los factores que los compradores revisan inmediatamente después de la SAL.

---

## English

> **Every Axolotito is born with a nature.** It is not a simple stat modifier — it is their personality, their playstyle, their way of seeing the world. The nature defines how they perform in matches, how they respond to imprinting Webitos (eggs), and which type of player benefits most from having them.

Axolotto features **6 natures**, assigned randomly at birth (hatching). You cannot choose or change them. Each nature modifies base stats and provides unique imprinting bonuses when the Axolotito acts as a godparent (padrino) for an incubating egg.

**The 6 natures are:**

| Nature | Stat Effect | Imprinting Bonus |
|--------|------------|------------------|
| **Methodical (Metódico)** | +10 Focus, -5 Stamina | 1.25x to positive focus deltas |
| **Lucky (Suertudo)** | +10 Luck, -5 Stamina | 1.25x to positive luck deltas |
| **Hyperactive (Hiperactivo)** | 25% faster sleep, -5 Focus | 1.25x to positive stamina deltas |
| **Glutton (Glotón)** | +30% food energy, -10 Focus | Negative deltas reduced to 80% |
| **Shy (Tímido)** | -10 Salinity at birth, -5 Luck | None currently documented |
| **Wise (Sabio)** | +15 Stamina, +5 Salinity | None currently documented |

**For competitive multiplayer**, Methodical is king — Focus reduces miss chance and every missed card costs prizes. Lucky is a close second for bigger prize shares. Shy is the anti-salinity pick, starting at SAL = 0 for near-zero slip chance.

**For grinding and marathon sessions**, Hyperactive (faster sleep = more games per hour) and Wise (larger energy pool = more games per cycle) excel.

**For F2P players**, Glutton stretches every FRJ spent on food by 30%, giving more autonomy without waiting for sleep.

**For breeding (imprinting)**, Methodical and Lucky are the best godparent natures — their 1.25x multiplier on positive Focus/Luck deltas produces Axolotitos with significantly better stats. Hyperactive is also valuable for completing imprinting sessions faster.

**Nature is permanent.** It is part of the Axolotito's DNA, recorded on-chain, and cannot be changed with any in-game item or mechanic. Choose your breeding strategy carefully.

---

## Quick Reference / Referencia Rápida

| Concept / Concepto | Value / Valor |
|---|---|
| Number of natures / Número de naturalezas | 6 |
| Nature assignment / Asignación de naturaleza | Random at hatching / Aleatorio al eclosionar |
| Can nature be changed? / ¿Se puede cambiar? | No (permanent / permanente) |
| Metódico OJO bonus | +10 |
| Metódico PILA penalty | -5 |
| Suertudo SUERTE bonus | +10 |
| Suertudo PILA penalty | -5 |
| Hiperactivo sleep speed / Velocidad de sueño | +25% faster / más rápido |
| Hiperactivo OJO penalty | -5 |
| Glotón food energy bonus / Bonus de energía de comida | +30% |
| Glotón OJO penalty | -10 |
| Glotón Algae Pellet (15 base) energy / energía | 19.5 |
| Glotón Brine Shrimp (60 base) energy / energía | 78 |
| Tímido SAL reduction at birth / Reducción de SAL al nacer | -10 (floor/piso = 0) |
| Tímido SUERTE penalty | -5 |
| Sabio PILA bonus | +15 |
| Sabio SAL penalty | +5 |
| Sabio default PILA / PILA por defecto | 115 |
| Methodical imprinting multiplier / Multiplicador imprinting Metódico | 1.25x on positive focus_delta |
| Lucky imprinting multiplier / Multiplicador imprinting Suertudo | 1.25x on positive luck_delta |
| Hyperactive imprinting multiplier / Multiplicador imprinting Hiperactivo | 1.25x on positive stamina_delta |
| Glutton imprinting effect / Efecto imprinting Glotón | Negative deltas reduced to 80% / Deltas negativos al 80% |
| Best for CPU grind / Mejor para CPU grind | Methodical or Hyperactive / Metódico o Hiperactivo |
| Best for multiplayer / Mejor para multijugador | Lucky or Shy / Suertudo o Tímido |
| Best for Saladito / Mejor para Saladito | Wise or Hyperactive (SAL is GOOD in Saladito) / Sabio o Hiperactivo |
| Best for F2P / Mejor para F2P | Glutton / Glotón |
| Best for breeding (padrino) / Mejor para criar | Methodical or Lucky / Metódico o Suertudo |
| Nature displayed in / Naturaleza visible en | AxoSheet (Nido) |
| Miss chance from -5 OJO / Probabilidad de fallo por -5 OJO | ~+1.5% |
| Miss chance from -10 OJO / Probabilidad de fallo por -10 OJO | ~+3.0% |
| Slip chance at SAL 0 / Probabilidad de slip en SAL 0 | Near 0% / Cerca de 0% |
| Slip chance at SAL 10 / Probabilidad de slip en SAL 10 | ~3.3% |

---

→ See also / Ver también: [[02-axolotitos]] · [[03-estadisticas-de-axolotito]] · [[11-webitos-y-crianza]] · [[26-consejos-y-estrategias]] · [[00-INDEX]]
