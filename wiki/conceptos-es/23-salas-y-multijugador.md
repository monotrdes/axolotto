---
tags: [conceptos, multijugador]
description: "Salas multijugador en detalle — lobby, Gritón, premios, juego automático | Multiplayer rooms in detail — lobby, Gritón, prizes, auto-play"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Salas y Multijugador

El multijugador es el corazón competitivo de Axolotto. No es un modo extra ni un afterthought — es donde el juego cobra vida, donde las estrategias chocan, y donde los premios de verdad se ganan. Aquí va absolutamente todo lo que necesitas saber sobre las salas, desde el lobby hasta el settlement final.

---

## Tipos de Sala

Axolotto tiene dos grandes categorías de salas multijugador: las oficiales (manejadas por el sistema) y las de anfitriones (creadas y administradas por jugadores como tú).

### Salas Oficiales

Estas salas siempre están abiertas, siempre tienen tráfico, y son el punto de entrada natural para cualquier jugador.

| Sala | Entrada (buy-in) | Jugadores máx | Dificultad |
|------|-------------------|---------------|------------|
| **Charco de Novatos** | 10 FRJ | 30 | Casual — ideal para aprender, probar Tablas nuevas, o jugar sin presión |
| **Fosa del Campeón** | 50 FRJ | 30 | Competitivo — donde los jugadores serios van a demostrar sus stats y estrategias |

**Características de las salas oficiales:**
- El Gritón es controlado por el servidor, con velocidad fija (modo normal, 1.0×)
- Sin comisión de anfitrión — todo el pozo va a los jugadores (menos el 5% de tesorería y 5% de Jackpot)
- Bots automáticos rellenan la sala si hay menos de 4 Tablas humanas
- Abiertas 24/7, sin contraseña, visibles para todos

### Salas de Anfitriones (Player-Hosted Rooms)

¿Quieres control total? Crea tu propia sala. Las salas de anfitriones son el espacio donde la comunidad construye sus propias reglas, torneos privados, y experiencias personalizadas.

**Parámetros configurables por el anfitrión:**

| Parámetro | Opciones | Notas |
|-----------|----------|-------|
| **Buy-in** | 10 – 1,000 FRJ | El anfitrión elige la entrada. A mayor buy-in, mayor el pozo... y mayor el riesgo |
| **Jugadores** | 2 – 8 | Salas más íntimas, más estratégicas. Sin bots |
| **Velocidad** | Normal (1.0×) · Rápido (0.6×) · Turbo (0.3×) | Afecta el delay entre cartas del Gritón. Turbo es pura adrenalina |
| **Visibilidad** | Pública · Amigos · Privada (contraseña) | Control total sobre quién entra |
| **Patrones ganadores** | Configurables | El anfitrión decide qué patrones aplican para Premio 1 en su sala |

**Comisión del anfitrión:** el creador de la sala recibe el **5% del pozo total** de cada partida. Esto significa que hostear salas populares es un negocio legítimo dentro de Axolotto. Un anfitrión con una sala de 8 jugadores a 1,000 FRJ cada uno está moviendo 8,000 FRJ por partida y ganando 400 FRJ solo en comisión.

> 🏠 **Tip de anfitrión:** Las salas rápidas (rápido o turbo) generan más partidas por hora. Aunque el buy-in suela ser más bajo, el volumen compensa. Una sala turbo de 50 FRJ con 8 jugadores puede generar más comisiones por hora que una sala normal de 200 FRJ.

---

## La Cuevita como Host

Cada Axolotito tiene su Cuevita — su guarida personal en Xochimilco. Y cada Cuevita puede hostear partidas.

**Calidad de decoración = visibilidad en el lobby.** Entre más decorada esté tu Cuevita (más objetos, mejor rareza, expansiones completadas), más arriba aparece tu sala en el listado del lobby. Esto no es cosmético — es posicionamiento estratégico. Una Cuevita premium atrae más jugadores, lo que genera más comisiones, lo que paga la decoración.

**Beneficios de hostear desde tu Cuevita:**
- Tu sala muestra el nombre y la imagen de tu Axolotito
- Los jugadores pueden visitar tu Cuevita desde el lobby (modo espectador)
- Las expansiones de Cuevita desbloquean slots adicionales de sala (máximo 3 salas simultáneas por Cuevita)
- Decoraciones raras dan un borde especial a tu listing en el lobby

---

## Flujo de Registro (Cómo Entrar a una Sala)

Entrar a una sala multijugador no es solo darle click a un botón. Hay un proceso de registro que protege tu economía y prepara a tu Axolotito para la sesión.

### Paso a Paso del Registro

1. **Selecciona tu Axolotito** — es quien jugará por ti. Sus stats importan: OJO para marcar, SUERTE para premios y salvaciones, SAL para posición en el mazo.

2. **Elige de 1 a 3 Tablas** — puedes registrar hasta 3 Tablas simultáneas en una misma sala. Cada Tabla juega de forma independiente (como si fueran 3 "cartones" separados). Más Tablas = más chances de ganar, pero también más costo.

3. **El presupuesto (FRJ) se mueve a un escrow en tu Axolotito** — al registrarte, los FRJ que vas a usar no se descuentan inmediatamente, pero se apartan en un escrow ligado a tu Axolotito. Esto garantiza que siempre tengas fondos para cubrir tus partidas.

4. **Presupuesto mínimo** = `fee_per_board × number_of_boards`. Si registras 3 Tablas en Fosa del Campeón (50 FRJ c/u), necesitas mínimo 150 FRJ en escrow.

5. **Configura tus límites de riesgo:**
   - **Stop-loss:** pérdida máxima que toleras. Cuando tu balance de escrow cae a este nivel, tu Axolotito deja de reinscribirse automáticamente. Ejemplo: entras con 300 FRJ, pones stop-loss en 100 FRJ. Si pierdes 200 FRJ, te retiras.
   - **Take-profit:** ganancia objetivo. Cuando tu balance de escrow alcanza este nivel, tu Axolotito deja de reinscribirse y aseguras las ganancias. Ejemplo: entras con 300 FRJ, pones take-profit en 600 FRJ. Si duplicas, te retiras con ganancia.

6. **Límites del sistema:**
   - Máximo **1 registro por usuario** por tipo de sala (no puedes estar en dos Charco de Novatos al mismo tiempo)
   - Máximo **1 registro por wallet address** por tipo de sala (anti-multicuentas)
   - Máximo **5 Tablas totales** entre todas tus inscripciones activas
   - Puedes estar en una sala oficial Y una sala de anfitrión simultáneamente (son tipos distintos)

---

## Matchmaking: Cómo Arrancan las Partidas

El sistema de matchmaking de Axolotto corre en un loop de backend cada **10 segundos**, evaluando todas las salas activas. Su objetivo es simple: arrancar partidas lo más rápido posible sin sacrificar la calidad del emparejamiento.

### Tiempos de Espera por Cantidad de Tablas

| Tablas Registradas | Tiempo de Espera | Descripción |
|---------------------|------------------|-------------|
| **30+** | **Instantáneo** | Sala llena. La partida arranca inmediatamente |
| **21 – 29** | 15 segundos | Alta demanda. Espera mínima para captar algún rezagado |
| **11 – 20** | 20 segundos | Buen tamaño. Se da un respiro para llegar a mejor match |
| **6 – 10** | 25 segundos | Sala mediana. Tiempo razonable para atraer más jugadores |
| **3 – 5** | 35 segundos | Sala pequeña. Un poco más de paciencia |
| **1 – 2** | 60 segundos | Sala mínima. Espera máxima para evitar que juegues solo |

### Regla de Bots

Si al cumplirse el tiempo de espera hay **menos de 4 Tablas humanas** registradas, el sistema rellena la sala con **bots** hasta alcanzar un mínimo de 4 participantes. Esto garantiza que nunca juegues completamente solo y que siempre haya un pozo razonable en juego.

Los bots tienen stats aleatorias balanceadas — no son regalos, pero tampoco son imbatibles. Están diseñados para dar una experiencia justa mientras llegan más humanos.

> 🎯 **Nota importante:** Las salas de anfitriones NUNCA usan bots. Si no se llena el cupo mínimo de humanos, la sala simplemente espera. Parte del arte de ser anfitrión es saber cuándo abrir sala para garantizar que se llene.

---

## Flujo de la Partida

Una vez que el matchmaking dispara el inicio, esto es lo que pasa en orden:

### 1. Cobro de Entrada

La entrada (buy-in) se descuenta del escrow de cada Axolotito registrado. Si eres **VIP Axolite**, recibes un **15% de descuento** sobre el buy-in. Este descuento es automático y aplica tanto en salas oficiales como en salas de anfitriones.

### 2. Deducción de Energía

Cada partida consume energía de tu Axolotito:

- **Costo base:** 10 de energía por partida
- **Costo extra por salinidad:** `round(SAL × 0.2)` adicional
- **Rango total:** 10 a 30 de energía por partida

Un Axolotito con SAL baja (0-10) paga 10-12 de energía por partida. Uno con SAL alta (80-100) paga 26-30. Mantener la salinidad baja no solo mejora tu posición en el mazo — también te deja jugar más partidas por sesión.

### 3. Decaimiento de Energía Máxima

Además del costo por partida, tu **energía máxima** decae en **3 puntos por partida**. Esto simula el cansancio acumulado de tu Axolotito. Después de varias partidas seguidas, tu capacidad total de energía se reduce, obligándote eventualmente a descansar.

### 4. El Gritón Canta

El mazo de 54 cartas se baraja con aleatoriedad criptográfica (`SystemRandom`). El Gritón empieza a anunciar cartas una por una. La velocidad entre cartas depende del tipo de sala:

| Tipo de Sala | Delay entre Cartas | Sensación |
|--------------|-------------------|-----------|
| **Oficial** | Normal (fijo) | Ritmo clásico de Lotería |
| **Anfitrión Normal** | ~3-4 segundos | Tranquilo, social |
| **Anfitrión Rápido (0.6×)** | ~2 segundos | Ágil, mantiene la atención |
| **Anfitrión Turbo (0.3×)** | ~1 segundo | Frenético, pura adrenalina |

### 5. Dos Pozos de Premios por Partida

Cada partida multijugador tiene **dos pozos de premios independientes**, más las contribuciones automáticas:

| Destino | Porcentaje del Pozo | Notas |
|---------|---------------------|-------|
| **Tesorería (casa)** | 5% | Fee del sistema, mantiene los servidores |
| **Jackpot** | 5% | Se acumula en el pozo global |
| **Comisión de anfitrión** | 5% | Solo en salas de anfitriones. En oficiales es 0% |
| **Premio 1** | 35% (30% con host) | Primer patrón completado |
| **Premio 2** | 55% | Tabla llena — ¡Lotería! |

---

## Distribución de Premios

### Premio 1 — El Primer Patrón

**Condición:** ser la primera Tabla en completar **cualquiera de los patrones ganadores configurados** para esa sala.

En salas oficiales, los patrones incluyen: línea horizontal, línea vertical, línea diagonal, las 4 esquinas, y cuadrito central (2×2). En salas de anfitriones, el host puede elegir exactamente qué patrones aplican — puede ser tan restrictivo ("solo diagonal") o tan generoso ("todos los patrones clásicos") como quiera.

**Reparto:** si múltiples Tablas completan el mismo patrón ganador en la misma carta exacta, el pozo de Premio 1 se divide **en partes iguales** entre todas ellas. Si una Tabla completa un patrón en la carta 12 y otra en la carta 15, gana la primera.

### Premio 2 — ¡Lotería!

**Condición:** ser la primera Tabla en llenar **las 16 celdas** (tabla completa). Esto es la Lotería clásica, el grito de "¡Buenas!" que todo jugador sueña con dar.

El pozo de Premio 2 es siempre el **55%** del pozo total, sin importar si hay anfitrión o no. Es el premio gordo de cada partida.

**¿Puede el mismo jugador ganar ambos premios?** ¡Sí! La Regla del Doble Ganador lo permite. Si completas un patrón ganador primero (Premio 1) y además eres el primero en llenar tu tabla completa (Premio 2), te llevas ambos pozos. Es raro, pero cuando pasa... la sala entera lo celebra.

### Bonus de Suerte

Todos los premios (Premio 1, Premio 2, y Jackpot) reciben un **bonus por SUERTE (Luck):**

```
tu_share_final = tu_share_base × (1 + axo_luck / 1000)
```

Un Axolotito con 100 de SUERTE recibe un 10% extra sobre su parte del premio. Uno con 200 de SUERTE recibe 20% extra. La suerte no te hace ganar más seguido — pero cuando ganas, ganas más.

---

## El Jackpot en Multijugador

El Jackpot es el pozo global acumulado que crece con cada partida multijugador. Para detalles completos, consulta [[22-jackpot]], pero aquí va el resumen desde la perspectiva de las salas:

### Requisitos para ser Elegible

- **Mínimo 5 Tablas humanas** registradas en la sala
- **Mínimo 2 wallets distintas** entre los participantes (anti-sybil: evita que una sola persona con múltiples cuentas manipule el sistema)

### Gatillo del Jackpot

El Jackpot se activa únicamente cuando **Premio 1 se gana en las cartas 4, 5, o 6**. Es decir, alguien completa un patrón ganador extremadamente temprano en la partida, cuando apenas han salido las primeras cartas del Gritón. Esto requiere una combinación brutal de:
- Una Tabla perfectamente optimizada para el patrón
- OJO altísimo para no fallar marcas
- SUERTE para que tus cartas salgan temprano
- SAL baja para que no te empujen al final del mazo

### Pago del Jackpot

- **90%** del pozo acumulado se entrega al ganador (o se divide entre ganadores simultáneos)
- **10%** se re-siembra para la siguiente ronda
- Si después de re-sembrar el Jackpot queda en **menos de 1,000 FRJ**, la tesorería del juego completa la diferencia automáticamente
- Los jugadores **VIP Axolite** reciben un **+5% de bonus** sobre sus ganancias de Jackpot

> 🌟 Ganar el Jackpot es el logro más épico de Axolotto. No solo por el premio — sino porque requiere que absolutamente todo salga perfecto: tu Tabla, tus stats, y el momento justo de suerte.

---

## Auto-Reinscripción: Tu Axolotito No Duerme

Una de las mecánicas más poderosas del multijugador: no necesitas estar pegado a la pantalla. Una vez registrado, tu Axolotito puede seguir jugando partida tras partida automáticamente.

### Condiciones para Reinscribirse

Después de cada partida, el sistema evalúa si tu Axolotito debe reinscribirse automáticamente a la siguiente. Las condiciones son:

1. **No ha alcanzado el stop-loss** — tu balance de escrow sigue por encima del límite de pérdida que configuraste
2. **No ha alcanzado el take-profit** — tu balance de escrow no ha llegado al objetivo de ganancia
3. **Energía actual >= 10** — tiene suficiente energía para al menos una partida más
4. **Tiene fondos para la entrada** — el escrow cubre el buy-in de la siguiente partida
5. **No ha sido retirado manualmente** — no presionaste "Dejar de Jugar"

Si todas las condiciones se cumplen, tu Axolotito se reinscribe automáticamente y sigue jugando. Puedes irte a dormir, trabajar, o lo que sea — tu Axolotito sigue ahí, marcando cartas, ganando premios.

### Cómo Salir: Dejar de Jugar

Cuando quieras detenerte, haces click en el botón **"Dejar de Jugar"**. Esto NO saca a tu Axolotito inmediatamente — termina la partida actual y luego se detiene. Es una salida elegante, no un rage-quit.

### Settlement (Liquidación Final)

Cuando tu Axolotito termina su sesión (ya sea por stop-loss, take-profit, energía agotada, o retiro manual), entra en Settlement:

1. **Balance del escrow se devuelve a tu wallet** — los FRJ que no gastaste vuelven a ti
2. **Puntos de lealtad otorgados:**
   - **5 puntos base** por participar en la sesión
   - **+1 punto extra por cada 10 FRJ de ganancia neta**
   - Ejemplo: terminaste con 150 FRJ de ganancia neta = 5 + 15 = 20 puntos de lealtad
3. **Tu Axolotito pasa a estado SLEEPING** — necesita descansar. Durante el sueño, recupera energía y reduce salinidad. Consulta [[02-axolotitos]] para el sistema de sueño completo.

---

## El Gritón (El Cantador)

El Gritón es el alma de cada partida. Es la voz (generada por el sistema) que anuncia las cartas una por una, marcando el ritmo del juego.

### En Salas Oficiales

- Controlado completamente por el servidor
- Velocidad fija (modo normal)
- Sin intervención humana posible
- La misma voz, el mismo ritmo, para todos

### En Salas de Anfitriones

El anfitrión configura la velocidad del Gritón al crear la sala:

| Modo | Multiplicador | Sensación |
|------|---------------|-----------|
| **Normal** | 1.0× | Clásico. ~3-4 segundos entre cartas. Ideal para salas sociales |
| **Rápido** | 0.6× | ~2 segundos. Buen ritmo sin ser abrumador |
| **Turbo** | 0.3× | ~1 segundo. Para los que quieren acción pura |

### Modo Manual (Avanzado)

En salas de anfitriones, existe un modo manual donde el host puede:
- Repetir la última carta anunciada (para dar tiempo extra)
- Configurar el comportamiento en caso de empate (primer patrón simultáneo)
- Pausar brevemente entre cartas para generar tensión

El modo manual es para anfitriones avanzados que quieren crear una experiencia más teatral, estilo streamer.

---

## Reputación de Anfitrión

Ser anfitrión no solo paga en FRJ — también construye tu reputación en la comunidad.

### Sistema de Reputación

| Acción | Reputación Ganada |
|--------|-------------------|
| Hostear una partida completada | +1 |
| Sala llena al 80%+ de capacidad | +5 extra (total +6 por esa partida) |

**Ejemplo práctico:** tienes una sala de 8 jugadores. Si 7 u 8 se llenan (80%+), ganas +6 de reputación por partida. En una hora de sala turbo llena, puedes fácilmente sumar +60 de reputación.

### Beneficios de Alta Reputación

- **Mejor visibilidad en el lobby:** las salas de anfitriones con alta reputación aparecen más arriba en los listados
- **Insignia de anfitrión:** distintivos visuales que muestran tu nivel como host (Bronce, Plata, Oro, Axolite)
- **Confianza de la comunidad:** los jugadores prefieren salas de hosts con buena reputación — saben que la experiencia será justa y divertida
- **Mayor tráfico = más comisiones:** es un círculo virtuoso

---

## Estrategia en Multijugador

Unos consejos rápidos para dominar las salas:

### Para Jugadores

- **Registra 3 Tablas siempre que puedas** — triplicas tus chances de ganar Premio 1. El costo extra vale cada FRJ.
- **Configura stop-loss y take-profit con cabeza** — un stop-loss muy ajustado te saca antes de tiempo. Un take-profit muy ambicioso nunca se alcanza. Encuentra tu equilibrio.
- **La SAL importa más en multijugador** — en CPU puedes compensar SAL baja con volumen. En multi, donde todos comparten el mismo Gritón, una SAL baja es ventaja competitiva real.
- **Elige la velocidad de sala que se adapte a tu estilo** — si tienes buen OJO pero malos reflejos, juega en normal. Si confías en tu Tabla y quieres volumen, ve a turbo.
- **La auto-reinscripción es tu amiga** — configura tus límites, regístrate, y deja que tu Axolotito trabaje. Revisa cada hora para ajustar.

### Para Anfitriones

- **Abre sala en horas pico** — menos competencia por visibilidad, más jugadores buscando partida
- **Turbo con buy-in bajo atrae volumen** — muchos jugadores prefieren 10 partidas rápidas de 20 FRJ que una lenta de 200 FRJ
- **Decora tu Cuevita** — cada objeto decorativo es una inversión en visibilidad de lobby. Se paga solo con comisiones
- **Sé consistente** — un anfitrión que abre sala regularmente construye comunidad. Los jugadores regresan a salas conocidas
- **Elige patrones interesantes** — si solo aceptas diagonal como Premio 1, las partidas serán más largas y tensas. Si aceptas todos los patrones, serán más rápidas y caóticas. Encuentra tu nicho.

---

