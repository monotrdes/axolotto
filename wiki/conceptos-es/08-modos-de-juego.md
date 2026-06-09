---
tags: [conceptos, gameplay, modos]
description: "Todos los modos de juego en Axolotto — CPU, Multijugador, PvP Manual, Saladito y Espectador | All game modes in Axolotto — CPU, Multiplayer, Manual PvP, Saladito and Spectator"
last_modified: "2026-06-09"
audience: jugadores
language: es-en
---

# Modos de Juego

Axolotto ofrece **cinco modos de juego** distintos para que cada tipo de jugador encuentre su lugar, desde el competidor casual que quiere echar una partida rápida contra bots hasta el coleccionista F2P que apenas está empezando y quiere ganar sus primeras recompensas sin tener un axolotito propio. Aquí te explicamos cada uno en detalle.

---

## 1. Modo CPU (Solo vs Bots)

El modo principal PvE del juego. Te enfrentas a bots controlados por el sistema en partidas rápidas de Lotería. Perfecto para practicar, farmear Frijolitos y subir de nivel a tus axolotitos sin la presión de jugar contra humanos.

### Salas disponibles

| Sala | Nombre | Bots | Dificultad | Entrada | Premio | Consuelo |
|------|--------|------|------------|---------|--------|----------|
| Rookies | Charco de Novatos | 1 bot fácil | Focus 40 (~18% fallo) | 25 FRJ | 85 FRJ | 8 FRJ |
| Champions | Fosa del Campeón | 5 bots duros | Focus 80 (~6% fallo) | 100 FRJ | 400 FRJ | 20 FRJ |

### Multiplicadores

Puedes multiplicar tu apuesta y ganancias con estos multiplicadores:

| Multiplicador | Entrada Rookies | Premio Rookies | Entrada Champions | Premio Champions |
|---------------|-----------------|----------------|-------------------|------------------|
| 1× | 25 FRJ | 85 FRJ | 100 FRJ | 400 FRJ |
| 2× | 50 FRJ | 170 FRJ | 200 FRJ | 800 FRJ |
| 5× | 125 FRJ | 425 FRJ | 500 FRJ | 2,000 FRJ |
| 10× | 250 FRJ | 850 FRJ | 1,000 FRJ | 4,000 FRJ |

### Experiencia (axo XP)

- **Rookies**: 25–35 axo XP por victoria, 8 axo XP por derrota
- **Champions**: 60–75 axo XP por victoria, 15 axo XP por derrota

### Racha de victorias

Cada victoria consecutiva suma **+15%** de bonificación sobre el premio base, con un tope máximo de **+50%** (4 victorias seguidas). Si pierdes, la racha se reinicia.

### Costo de energía

Siempre **10 de energía** por partida, sin importar el multiplicador o la sala.

### Cómo jugar

1. Selecciona tu axolotito activo desde tu inventario
2. Elige un tablero de Lotería (o crea uno nuevo en el Editor de Tableros)
3. Escoge la sala: Charco de Novatos o Fosa del Campeón
4. Selecciona tu multiplicador
5. ¡Presiona Jugar! El resultado se resuelve en segundos

---

## 2. Modo Multijugador (Auto-AFK)

El modo competitivo principal. Partidas en tiempo real con hasta **30 jugadores humanos** por sala. Tu axolotito juega automáticamente — tú configuras la estrategia y él se encarga del resto.

### Salas multijugador

| Sala | Entrada | Premio base |
|------|---------|-------------|
| Rookies (Charco de Novatos) | 10 FRJ | Varía según participantes |
| Champions (Fosa del Campeón) | 50 FRJ | Varía según participantes |

### Auto-AFK: configura tu estrategia

- **Presupuesto (stop-loss)**: límite máximo de FRJ que estás dispuesto a perder. Cuando se alcanza, tu axolotito deja de jugar.
- **Take-profit**: límite de ganancias. Cuando lo alcanzas, retira tus ganancias automáticamente.
- **Auto-reinscripción**: tu axolotito se reinscribe automáticamente en nuevas partidas hasta que se alcancen los límites o se quede sin energía.

### Liquidación (Settlement)

Al terminar de jugar, reclamas manualmente:
- Tus ganancias acumuladas en escrow (depósito de garantía)
- Puntos de lealtad (Loyalty Points) por cada partida completada

### Llenado de salas

Si hay menos de **4 jugadores humanos**, el sistema llena la sala con bots para garantizar que la partida se juegue. Los bots en multijugador usan la misma lógica que en modo CPU pero con nombres aleatorios.

### Tiempos de inicio

| Tableros inscritos | Tiempo de espera |
|--------------------|------------------|
| 30+ tableros | Inicio instantáneo |
| 15–29 tableros | 15 segundos |
| 5–14 tableros | 30 segundos |
| 1–4 tableros | 60 segundos |

### Costo de energía

Fórmula: **10 + (salinity × 0.2)** por ronda, con un máximo de **30 de energía** por partida. Axolotitos con alta salinidad gastan más energía en multijugador — otro factor estratégico a considerar.

---

## 3. Modo PvP Manual (Interactivo)

El modo más intenso y competitivo. NO está abierto permanentemente — solo se activa durante **eventos especiales** creados por los administradores.

### Diferencias clave con los otros modos

- **Marcado manual**: tú mismo haces clic en las cartas de tu tablero. No hay auto-marcado.
- **Estadística de Agilidad**: la velocidad con la que se marca una carta depende de tu stat de Agilidad. El retraso de marcado varía entre **800 ms** (agilidad alta) y **2,500 ms** (agilidad baja).
- **¡Lotería! manual**: puedes gritar "¡Lotería!" para reclamar la victoria en el momento exacto. Si gritas sin tener el patrón completo, pierdes puntos.
- **WebSocket en tiempo real**: conexión directa al servidor para latencia mínima.
- **El Gritón llama cartas**: un narrador automático (El Gritón) anuncia las cartas en un temporizador configurable por el admin.

### Salas hospedadas por jugadores (Cuevita Host)

Un jugador con suficientes Frijolitos puede crear su propia sala PvP privada:
- Configurar el temporizador del Gritón
- Invitar a amigos específicos
- Establecer la entrada y premios personalizados
- Elegir si aplicar reglas especiales (como Saladito)

### Multiplicadores de XP

Durante eventos PvP Manual, los multiplicadores de XP son **más altos** que en cualquier otro modo, haciendo que estos eventos sean la forma más rápida de levelear axolotitos raros.

---

## 4. Modo Saladito (Lotería Inversa)

El giro más divertido y caótico de la Lotería tradicional. Las reglas se **invierten**: gana el jugador que termine con **menos cartas marcadas** en su tablero.

### ¿Cuándo está disponible?

- **Automático**: todas las noches de **3:00 a 4:00 AM** hora del servidor (Ciudad de México, GMT-6)
- **Manual**: en salas privadas hospedadas por jugadores (Cuevita Host) en cualquier momento

### Reglas invertidas

- El Gritón sigue cantando cartas normalmente
- Tu axolotito intenta NO marcar cartas
- Gana quien tenga **menos cartas marcadas** al final de la ronda
- Si hay empate, gana el de mayor SAL (Salinidad)

### SAL se vuelve un beneficio

En modo normal, una SAL (Salinidad) alta es mala porque hace que las cartas se "resbalen" y no se marquen correctamente. Pero en modo Saladito, **esto es justo lo que quieres**. Un axolotito con SAL alta tiene más probabilidades de que las cartas se le resbalen — lo cual es BUENO en Saladito porque quieres tener pocas cartas marcadas.

Esto crea un meta divertido donde axolotitos que normalmente serían "malos" (alta salinidad) se vuelven repentinamente valiosos durante la hora Saladito.

### Recompensas especiales

- Premios en FRJ equivalentes al modo CPU Champions
- Posibilidad de obtener **Webitos con traits de Saladito** (rasgos especiales que solo se consiguen en este modo)
- Insignia temporal de "Rey del Saladito" si ganas 3 partidas consecutivas en una noche

---

## 5. Modo Espectador (F2P / El Espejo del Cenote)

El modo gratuito diseñado para jugadores que **no tienen axolotitos propios**. Puedes mirar partidas en vivo y ganar micro-recompensas participando como espectador.

### ¿Cómo funciona?

- Entras al **Espejo del Cenote**, el lobby de espectadores
- Eliges una partida activa para mirar
- Recibes un **Tablero Espejo** (Mirror Board): una copia exacta del tablero de un jugador real en esa partida
- Ves la partida en tiempo real desde la perspectiva de ese jugador

### Recompensas para espectadores

| Acción | Recompensa |
|--------|------------|
| El tablero espejo gana la partida | Hasta 10 FRJ/día |
| "Apoyar" (cheer) a un axolotito | Fragmentos Astrales de Webito |
| Tocar burbujas interactivas | Envías burbujas flotantes al jugador real |

### Fragmentos Astrales de Webito

- Los ganas al apoyar axolotitos y al mirar partidas completas
- **100 fragmentos = 1 Webito Común gratis**
- Límite diario: **10 fragmentos**

### Límites diarios

| Recurso | Límite diario |
|---------|---------------|
| FRJ | 10 FRJ |
| Fragmentos Astrales | 10 fragmentos |

### Toque interactivo

Como espectador, puedes tocar la pantalla para enviar **burbujas flotantes** al jugador que estás mirando. El jugador real ve estas burbujas aparecer en su pantalla — una forma divertida de mostrar apoyo sin afectar la partida.

---

## Tabla Comparativa

| Característica | CPU | Multijugador | PvP Manual | Saladito | Espectador |
|----------------|-----|--------------|------------|----------|------------|
| **Tipo** | PvE vs Bots | PvP Auto-AFK | PvP Interactivo | Lotería Inversa | Solo mirar |
| **Entrada** | 25–250 FRJ | 10–50 FRJ | Variable (evento) | 25–100 FRJ | Gratis |
| **Premio máx.** | 850 FRJ (10×) | Variable | Variable (alto) | 400 FRJ | 10 FRJ/día |
| **Jugadores** | 1 humano + bots | Hasta 30 humanos | 2–8 humanos | 1 humano + bots | Ilimitado |
| **Interacción** | Ninguna (auto) | Estrategia (config) | Clic manual | Ninguna (auto) | Burbujas tap |
| **Disponibilidad** | 24/7 | 24/7 | Solo eventos | 3–4 AM + privadas | 24/7 |
| **Energía** | 10 fija | 10–30 variable | 15 fija | 10 fija | 0 (no gasta) |
| **¿Requiere axolotito?** | Sí | Sí | Sí | Sí | No |
| **XP** | 8–75 axo XP | Similar a CPU | Multiplicado (evento) | Similar a CPU | 0 XP |
| **Racha** | +15%/victoria | +10%/victoria | +20%/victoria | No aplica | No aplica |

---

