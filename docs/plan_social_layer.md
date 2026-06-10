# Plan: Capa Social Unificada — Sistema de Amigos + Referidos

**Tasks vinculadas:** `task-1780974961-58` (sistema de amigos), `task-1780974969-59` (sistema de referidos)
**Estado:** planning
**Fecha:** 2026-06-10
**Autor:** Claude (game design · UX · marketing · tokenomics)

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Cliente Meta & Personas](#2-cliente-meta--personas)
3. [Arquitectura Social Unificada](#3-arquitectura-social-unificada)
4. [Game Design: Mecánicas & Loops](#4-game-design-mecánicas--loops)
5. [UX Design: Flujos & Pantallas](#5-ux-design-flujos--pantallas)
6. [Monetización & Tokenomics Social](#6-monetización--tokenomics-social)
7. [Marketing & Estrategia de Crecimiento](#7-marketing--estrategia-de-crecimiento)
8. [Arquitectura Técnica](#8-arquitectura-técnica)
9. [Plan de Implementación por Fases](#9-plan-de-implementación-por-fases)
10. [KPIs & Métricas de Éxito](#10-kpis--métricas-de-éxito)

---

## 1. Resumen Ejecutivo

### El Problema

Axolotto tiene retención (santuario, rachería VIP, incuación, coleccionables) pero **no tiene adquisición orgánica**. Cada usuario nuevo viene de marketing pagado o casualidad. No hay loop viral. La pestaña "Amigos" en el nav es un placeholder vacío. El sistema de referidos se menciona en 4 documentos distintos como "idea para después". Las salas de juego tienen visibilidad `friends` pero no existe el grafo social para validarlo.

### La Oportunidad

Los juegos mobile con mecánicas sociales tienen **2-5x mayor retención D30** que los single-player. Un sistema de referidos bien diseñado puede reducir el CAC (costo de adquisición) en **40-70%** comparado con paid acquisition. En el mercado LATAM de juegos móviles, el boca-a-boca y los grupos de WhatsApp son el canal #1 de descubrimiento.

### La Solución

Una **Capa Social Unificada** donde:

```
ADQUISICIÓN              ACTIVACIÓN               RETENCIÓN              MONETIZACIÓN
(Referidos)      →       (Primer Amigo)    →      (Interacción      →   (Gifting + Social
                         Automático               Diaria Social)          Status + Boosts)
    ↓                                                                    ↓
    └──────────────────── LOOP VIRAL CERRADO ──────────────────────────┘
```

### Por Qué Amigos + Referidos Juntos

| Si construimos solo | Qué pasa |
|---------------------|----------|
| **Solo amigos** | Jugadores conectan entre sí pero no hay mecanismo para traer nuevos. La red no crece. |
| **Solo referidos** | Usuarios entran por link, reciben reward, y se van. Sin amigos no hay arraigo social. |
| **Ambos juntos** | Referido → primer amigo automático (el referidor) → interacción diaria → invita a más → loop viral |

### Principios de Diseño

1. **Presencia Social, no Red Social** — No competimos con WhatsApp/Discord. La capa social existe para potenciar el juego, no para reemplazar el chat.
2. **Interacción Asimétrica** — Visitar la cueva de un amigo, mandar regalo, dar like. Sin requisito de estar online simultáneamente.
3. **Web3-Nativo** — Los axolotitos, decoraciones, y badges on-chain SON el perfil social. No hay "perfil vacío".
4. **Culturalmente Latino** — Compadrazgo, regalitos, "visitar la cueva", echar la lotería en sala de amigos.
5. **Mobile-First, Santuario-Céntrico** — La experiencia social vive en el Santuario (ZonaInferior + ZonaCentral con visitantes), no en una pantalla separada tipo "inbox".

---

## 2. Cliente Meta & Personas

### Demografía Principal

| Dimensión | Perfil |
|-----------|--------|
| Edad | 18–35 (core: 22–28) |
| Geografía | LATAM urbano (MX, CO, AR, PE, CL) + US Hispanic |
| Dispositivo | Móvil Android gama media (90%), iOS (10%) |
| Conexión | 4G/WiFi intermitente, datos limitados |
| Crypto XP | Curioso pero no experto — tiene Metamask/Phantom "por si acaso" |
| Lenguaje | Español nativo, memes, stickers, emojis |

### Psicografía

| Rasgo | Implicación de diseño |
|-------|----------------------|
| **Social por naturaleza** | Comparte memes, stickers, logros en WhatsApp/IG/TikTok |
| **Status-seeking** dentro de su grupo | Badges, rankings entre amigos, cuevas más decoradas |
| **FOMO moderado** | Notificaciones de "X visitó tu cueva" o "Y te mandó un regalo" = re-engagement |
| **Gasto impulsivo pequeño** | Microtransacciones de $1–$5 USD, regalos a amigos |
| **Coleccionista** | Quiere completar colecciones, mostrar rareza |
| **Juega en ráfagas cortas** | Sesiones de 3–8 minutos, múltiples veces al día |

### Personas

#### Persona A: "Kevin" — El Social Gamer (22, CDMX)
- Juega en el metro camino al trabajo. Tiene 5 amigos que también juegan.
- **Motivación**: Competir con sus amigos, presumir sus axolotitos raros, mandar regalitos.
- **Fricción actual**: No puede agregar amigos en el juego. Usa WhatsApp para coordinarse.
- **Gasto**: $5–15/mes en sobrecitos y decoraciones.

#### Persona B: "Valentina" — La Coleccionista (26, Medellín)
- Pasa horas decorando su cueva. Quiere que otros la visiten y den likes.
- **Motivación**: Validación social a través de su colección. Le encantaría un sistema de visitas/ratings.
- **Fricción actual**: Nadie puede ver su cueva. Sus decoraciones son privadas.
- **Gasto**: $10–30/mes en ítems raros y ediciones limitadas.

#### Persona C: "Bryan" — El Crypto-Curious (19, Lima)
- Entró por un anuncio de "juega y gana crypto". No entiende mucho de wallets.
- **Motivación**: Ganar algo de valor real, aprender sobre crypto jugando.
- **Fricción actual**: No conoce a nadie que juegue. Si recibiera un link de un amigo, sería 5x más probable que se quede.
- **Gasto**: $0–5/mes. Podría convertirse si ve que sus amigos ganan rewards.

### ¿Qué Resuelve la Capa Social para Cada Persona?

| Persona | Sin Capa Social | Con Capa Social |
|---------|----------------|-----------------|
| Kevin | Coordina por WhatsApp, no ve progreso de amigos | Amigos en ZonaInferior, salas solo amigos, rankings entre amigos |
| Valentina | Cueva privada, cero visitas | Cueva pública, likes, visitas de amigos, modo "cueva destacada" |
| Bryan | Juega solo, abandona en D3 | Entra por link de referido, su amigo lo guía, se queda por la comunidad |

---

## 3. Arquitectura Social Unificada

### El Social Graph como núcleo

```
┌─────────────────────────────────────────────────────────┐
│                    SOCIAL GRAPH (DB)                      │
│                                                          │
│  ┌──────────────┐       ┌──────────────┐                │
│  │ FriendRelation│───────│ ReferralEdge │                │
│  │ • user_a      │       │ • referrer   │                │
│  │ • user_b      │       │ • referred   │                │
│  │ • status      │       │ • code_used  │                │
│  │ • friends_since│      │ • reward_paid│                │
│  │ • interaction │       │ • converted  │                │
│  └──────────────┘       └──────────────┘                │
│         │                      │                         │
│         └──────────┬───────────┘                         │
│                    │                                     │
│  ┌─────────────────▼────────────────────┐               │
│  │         SOCIAL ACTIONS                │               │
│  │  • gifts_sent / gifts_received       │               │
│  │  • cave_visits / likes_given         │               │
│  │  • games_played_together             │               │
│  │  • referrals_made / rewards_earned   │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Estados de Relación

```
DESCONOCIDO ──→ PENDIENTE ──→ AMIGO ──→ MEJOR AMIGO (recíproco + 30+ días)
                     │            │
                     └─→ BLOQUEADO (ticket de soporte)
                     
REFERIDO ──→ AMIGO (automático al aceptar referido)
```

- **Amigo**: Relación aceptada mutuamente. Desbloquea: visitar cueva, mandar regalos, invitar a sala, ver estado online.
- **Mejor Amigo**: 30+ días de amistad + 10+ interacciones mutuas. Desbloquea: gifts diarios bonus, boost en sala compartida, insignia especial.
- **Referido → Amigo**: Cuando un usuario entra por código de referido, el referidor se agrega automáticamente como amigo (el nuevo usuario puede rechazar después).

### Capacidades por Tipo de Relación

| Capacidad | Amigo | Mejor Amigo | Referido (sin confirmar) |
|-----------|-------|-------------|--------------------------|
| Ver perfil/cueva | ✅ | ✅ | ❌ |
| Visitar cueva | ✅ | ✅ | ❌ |
| Like diario | ✅ | ✅ | ❌ |
| Mandar regalo | ✅ | ✅ | ❌ |
| Invitar a sala | ✅ | ✅ | ❌ |
| Ver online/offline | ✅ | ✅ | ❌ |
| Gift diario bonus | ❌ | ✅ | ❌ |
| Boost en sala juntos | ❌ | ✅ | ❌ |
| Aparecer en ZonaInferior | ✅ | ✅ | ❌ |

---

## 4. Game Design: Mecánicas & Loops

### 4.1 Core Social Loop (Diario)

```
ABRIR SANTUARIO
    │
    ▼
VER AMIGOS EN ZONA INFERIOR (4 más activos/recientes)
    │
    ├──→ ❤️ LIKE rápido (1 click, +1 FRJ para ambos, animación de corazón)
    │
    ├──→ 👁 VISITAR CUEVA (ver decoraciones, axolotitos, dejar like extendido)
    │
    ├──→ 🎁 MANDAR REGALO (seleccionar ítem, confirmar, animación de entrega)
    │
    └──→ 🎲 INVITAR A JUGAR (crear sala "solo amigos" con visibilidad restringida)
    
RECOMPENSA DIARIA: 3+ interacciones sociales = bonus de "Socializador" (+5 AXF, +20 FRJ)
```

### 4.2 Sistema de Amigos

#### Agregar Amigos — 4 Canales

| Canal | Flujo | UX |
|-------|-------|-----|
| **Código de amigo** | Código único de 6 caracteres (ej: `AX-X3K9P`) — el estándar mobile | Copiar/pegar, compartir vía sheet nativo del OS |
| **Búsqueda por nickname** | Buscar `nickname#1234` en directorio | Barra de búsqueda en pantalla de Amigos |
| **Jugadores recientes** | Gente con la que jugaste en salas públicas | Lista automática, botón "Agregar" |
| **Sugerencias** | Amigos de amigos (si ambos permiten visibilidad) | Sección "Quizás conozcas" opcional |

#### UX de Solicitud de Amistad

```
[Pantalla Amigos > Solicitudes]
┌──────────────────────────────────┐
│  Solicitudes (2)                 │
│                                  │
│  🦎 Nickname#1234               │
│  "Jugamos juntos en sala #lobby" │
│  [Aceptar]  [Rechazar]           │
│                                  │
│  🐸 OtroPlayer#5678              │
│  "Te encontró por búsqueda"      │
│  [Aceptar]  [Rechazar]           │
└──────────────────────────────────┘
```

#### Límites

- Máximo **100 amigos** por jugador (es un juego, no una red social)
- Máximo **20 solicitudes pendientes** enviadas
- Rate-limit: 10 solicitudes por hora (anti-spam)

### 4.3 Sistema de Referidos

#### El Código de Referido como Identidad

Cada jugador tiene UN código de referido único, permanente, y personalizado:
- Formato: `AXOLOTO-KEVIN` (prefijo + nickname) o `AX-X3K9P` (si no tiene nickname)
- Se genera al crear cuenta (lazy: la primera vez que el usuario lo consulta)
- Visible en: Perfil, pantalla de Amigos, y post-game (después de ganar)

#### Flujo de Referido (New User)

```
1. USUARIO NUEVO recibe link: "axolot.to/join/AXOLOTO-KEVIN"
2. Landing page ligera (sin descargar nada):
   - "Kevin te invitó a jugar Axolotto 🦎"
   - Muestra avatar de Kevin + su cueva (3 axolotitos visibles)
   - "Juega lotería, cría axolotitos, decora tu cueva"
   - [JUGAR AHORA] → va al juego principal
3. Al crear cuenta (Privy), el código de referido se guarda en el backend
4. Kevin recibe notificación: "¡Alguien usó tu código! 🎉"
5. Cuando el nuevo usuario completa el tutorial (D0):
   - Ambos reciben recompensa inicial
   - Kevin se convierte automáticamente en amigo del nuevo usuario
```

#### Estructura de Recompensas (Progresiva)

| Hito del Referido | Recompensa Referidor | Recompensa Referido |
|-------------------|---------------------|---------------------|
| Registro completado | +50 FRJ | +50 FRJ (boost inicial) |
| Tutorial completado | +20 AXF | +20 AXF |
| Primera partida jugada | +30 FRJ | — (ya jugó, está engaged) |
| D7 retención | +100 FRJ + item decorativo "Corcholata del Compadre" | Item decorativo "Corcholata del Ahijado" |
| Primera compra (AXG onramp) | +5% bonus en su siguiente purchase | +5% bonus en esta compra |
| Sube a VIP Coral | +3 días VIP extra | +3 días VIP extra |

#### Límites y Anti-Abuse

- Máximo **10 referidos activos por mes** (los que pasan de registro)
- Máximo **100 referidos de por vida**
- Los rewards se entregan con **24h de delay** (ventana de detección de fraude)
- No se puede referir a la misma wallet/dirección IP/dispositivo
- Si un referido no juega en 30 días, se marca como "inactivo" (no cuenta para límites pero no genera más rewards)

### 4.4 Interacción Social en Santuario

#### ZonaInferior — Amigos Activos

```
┌──────────────────────────────────────────┐
│  👥 Amigos (4/20 online)                 │
│                                          │
│  🦎 Kevin      ❤️  🎁  👁  🎲           │
│  🐸 Valentina  ❤️  🎁  👁  🎲           │
│  🦋 Bryan      ❤️  🎁  👁  🎲           │
│  🐙 Daniel     ❤️  🎁  👁  🎲           │
│                                          │
│  [Ver todos →]          [+ Agregar]      │
└──────────────────────────────────────────┘
```

Comportamiento de la lista:
- Muestra **4 amigos** priorizados por: online > interacción reciente > mejor amigo
- Cada amigo tiene 4 acciones rápidas (un toque)
- ❤️ Like: sin confirmación, feedback háptico + partículas
- 🎁 Gift: abre mini-panel con ítems enviables
- 👁 Visitar: transición a la cueva del amigo (reemplaza ZonaCentral)
- 🎲 Invitar: crea sala privada con ese amigo pre-invitado

#### ZonaCentral en Modo Visita

Cuando visitas la cueva de un amigo:
- La ZonaCentral muestra SU diorama (sus decoraciones, sus axolotitos, su mantel)
- El HUD sigue mostrando TUS recursos
- Badge: "Visitando la cueva de Kevin" con botón [Volver a mi santuario]
- Puedes dejar un "like" que aparece como notificación para el dueño

#### Notificaciones Sociales (In-Game, no Push)

```
┌──────────────────────────────┐
│  🔔 Notificaciones     (3)   │
│                              │
│  ❤️  Valentina le gusta      │
│      tu cueva. ¡Visítala!    │
│                              │
│  🎁  Kevin te envió un       │
│      "Loto de Papel" 🌸      │
│                              │
│  👤  Bryan aceptó tu         │
│      solicitud de amistad    │
└──────────────────────────────┘
```

### 4.5 Gifting (Regalos entre Amigos)

Sistema de envío de ítems entre amigos:

| Regla | Valor |
|-------|-------|
| Máximo de regalos por día | 5 (total, todos los amigos) |
| Máximo al mismo amigo | 1 por día |
| Ítems enviables | Decoraciones, consumibles, FRJ (no AXF, no axolotitos) |
| Costo de envío | 0 (el regalo es el costo) |
| Animación | El ítem "vuela" de tu cueva a la de tu amigo |

**¿Por qué gifting?** Es una de las mecánicas sociales más poderosas en juegos mobile. Genera reciprocidad ("me mandó algo, le tengo que mandar algo"), refuerza vínculos, y crea momentos de alegría asimétrica.

### 4.6 Rankings entre Amigos

Un leaderboard **solo visible para amigos mutuos** con métricas de juego:

| Métrica | Período |
|---------|--------|
| Partidas ganadas esta semana | Semanal |
| Axolotitos coleccionados | Total |
| Cueva más visitada (likes recibidos) | Semanal |
| Mejor referidor | Mensual |

Sin castigo — solo celebración social. El "peor" del ranking no sale. Solo top 5.

---

## 5. UX Design: Flujos & Pantallas

### 5.1 Arquitectura de Pantallas

```
SANTUARIO (casa)
    │
    ├── ZonaInferior: mini-lista de 4 amigos + acciones rápidas
    │
    └── Nav: [Santuario] [Jugar] [Mercado] [Amigos] [Perfil]
                                    │
                                    ▼
┌───────────────────────────────────────────────────┐
│              PANTALLA DE AMIGOS                     │
│                                                     │
│  [Código: AXOLOTO-KEVIN  📋]  [✉️ Solicitudes (2)] │
│                                                     │
│  ┌─ Buscar jugador... ─────────────────────────┐   │
│  │                                               │   │
│  └───────────────────────────────────────────────┘   │
│                                                     │
│  📊 Ranking entre Amigos                            │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🥇 Kevin       12 wins                       │   │
│  │ 🥈 Valentina    8 wins                       │   │
│  │ 🥉 Tú           7 wins  ← highlighted        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  👥 Mis Amigos (23/100)                             │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🟢 Kevin       ❤️ 🎁 👁 🎲                  │   │
│  │ 🟢 Valentina   ❤️ 🎁 👁 🎲                  │   │
│  │ ⚫ Bryan (2h)  ❤️ 🎁 👁 🎲                  │   │
│  │ ⚫ Daniel (1d) ❤️ 🎁 👁 🎲                  │   │
│  │ ... scroll vertical ...                       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  💌 Referidos                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │ Has traído 5 amigos. ¡Gana +100 FRJ!        │   │
│  │ [Ver mis referidos]  [Compartir código]      │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [🏠 Santuario] [🎲 Jugar] [🛒 Mercado] [👥 Amigos] [👤 Perfil] │
└───────────────────────────────────────────────────┘
```

### 5.2 Flujo de Agregar Amigo (El más crítico)

```
Desde Santuario (ZonaInferior)
    │
    ▼
[+ Agregar] → Sheet inferior (iOS/Android nativo)
    │
    ├── 📋 "Mi código: AXOLOTO-KEVIN" [Copiar] [Compartir]
    │
    ├── 🔍 "Buscar por nickname" → campo de texto → resultados → [Agregar]
    │
    ├── 🕐 "Jugadores recientes" (últimas 5 salas públicas)
    │
    └── 💡 "Quizás conozcas" (amigos de amigos, opt-in)
```

### 5.3 Flujo de Referido (El más importante para growth)

```
PANTALLA DE AMIGOS
    │
    ▼
[Compartir código] → Sheet nativa del OS
    │
    ├── 📱 Compartir por WhatsApp  → "¡Juega Axolotto conmigo! 🦎 Usa mi código AXOLOTO-KEVIN y gana 50 FRJ 🎁 axolot.to/join/AXOLOTO-KEVIN"
    ├── 📸 Compartir por Instagram → Sticker/story con QR del código
    ├── 🐦 Compartir por Twitter/X  → Texto + link
    ├── 📋 Copiar link
    └── ⬇️ Descargar QR para compartir en persona/stream
```

### 5.4 Perfil Social

El Perfil (pestaña 5 del nav) se convierte en tu "tarjeta de presentación social":

```
┌──────────────────────────────────┐
│         👤 PERFIL                │
│                                  │
│  🦎 [Axolotito Principal]        │
│  Kevin#1234                      │
│  ⭐ VIP Coral · Nivel 42         │
│                                  │
│  🏆 Logros: 12                   │
│  🦎 Colección: 47 axolotitos     │
│  🏠 Cueva: 23 decoraciones       │
│  👥 Amigos: 23                   │
│  💌 Referidos: 5                 │
│                                  │
│  🎨 Cueva destacada:             │
│  [Preview miniatura de la cueva] │
│  ❤️ 127 likes recibidos          │
│                                  │
│  📋 Código: AXOLOTO-KEVIN        │
│  [Compartir código]              │
│                                  │
│  ⚙️ Configuración                │
│  - Visibilidad de cueva: Amigos  │
│  - Sugerencias: Activado         │
│  - Notificaciones sociales: Sí   │
└──────────────────────────────────┘
```

### 5.5 Principios UX Mobile-First

| Principio | Aplicación |
|-----------|-----------|
| **Cero fricción** | Like = un toque sin confirmación. Gift = dos toques. |
| **Sheets nativos** | Usar bottom sheets del OS, no modales custom. Compartir usa el share sheet nativo. |
| **Háptico generoso** | Cada like, gift, y solicitud aceptada tiene feedback háptico. |
| **Animaciones con significado** | El like vuela de tu botón a la cueva del amigo. El gift "cae" en su santuario. |
| **Modo offline-friendly** | Las interacciones sociales funcionan sin que el otro esté online. |
| **Sin scroll en santuario** | El santuario mantiene su layout fijo. Solo la pantalla de Amigos tiene scroll. |

---

## 6. Monetización & Tokenomics Social

### 6.1 Principios Económicos

1. **Las interacciones sociales básicas son GRATIS** — likes, visitas, agregar amigos = 0 costo.
2. **Gifting usa ítems reales** — el regalo sale de tu inventario, incentivando compras.
3. **Referidos generan valor para ambos** — no es extractivo, es generoso.
4. **Los boosts sociales son el monetizable** — aceleradores, no paywalls.

### 6.2 Fuentes de Ingreso Vinculadas a lo Social

| Fuente | Mecánica | Estimación |
|--------|----------|-----------|
| **Gift Shop social** | Ítems diseñados específicamente para regalar: stickers, mini-decoraciones, "detallitos" | $1–3 USD c/u |
| **Boost de "Cueva Destacada"** | Aparecer en el directorio de cuevas públicas por 24h | 50 AXF (~$2.50 USD) |
| **Sobre sorpresa de amigo** | Comprar un "sobrecito" que solo se puede regalar (no abrir uno mismo) | 30 AXF (~$1.50 USD) |
| **Extender límites sociales** | +25 slots de amigos, +10 gifts/día (VIP Dorado+) | Parte del VIP |
| **Personalización de código** | Cambiar tu código de referido (1 vez gratis, siguientes: 200 FRJ) | ~$2 USD |
| **Recompensa de referido premium** | Si el referido compra AXG, el referidor gana 5% en su siguiente purchase | Variable |

### 6.3 Tokenomics de Referidos

```
COSTO DE ADQUISICIÓN POR REFERIDO (para el sistema)
─────────────────────────────────────────────────
Recompensa registro:           50 FRJ (~$0.15 USD*)
Recompensa tutorial:           20 AXF (~$1.00 USD*)
Recompensa D7 retención:      100 FRJ + ítem (~$0.50 USD*)
Recompensa primera compra:     variable (5% de la compra)
                               
TOTAL por referido retenido:   ~$1.65 USD en rewards
```
*\*Valor estimado basado en precios actuales de AXF/FRJ*

**Comparación**: CAC vía Meta Ads en LATAM gaming ≈ $2.50–5.00 USD. El referido cuesta $1.65 en rewards Y solo se paga si el usuario se retiene 7 días + completa tutorial.

### 6.4 Prevención de Exploits Económicos

| Riesgo | Mitigación |
|--------|-----------|
| Crear cuentas fake para auto-referirse | Detección de misma wallet/IP/dispositivo. Los rewards D7+ requieren actividad real (partidas jugadas). |
| Farming de gifts entre cuentas | Límite diario de gifts. Los ítems regalados son "soulbound" (no se pueden re-vender en P2P market). |
| Spam de solicitudes de amistad | Rate-limit 10/hr, máximo 20 pendientes. Los usuarios molestos pueden bloquear. |
| Suplantación de códigos famosos | Los códigos son únicos y ligados a nickname. No se pueden "robar" códigos. |

---

## 7. Marketing & Estrategia de Crecimiento

### 7.1 El Norte Estratégico

> **Objetivo**: Que el 30% de nuevos usuarios (D30) vengan de referidos, reduciendo el CAC blended en 40%.

### 7.2 Coeficiente Viral

```
K = N × C × R

Donde:
N = Número de invitaciones enviadas por usuario activo/mes
C = Tasa de conversión de invitación a registro
R = Tasa de retención D7 del referido

Meta realista para Axolotto:
K = 8 invitaciones × 15% conversión × 60% retención D7 = 0.72

Un K de 0.72 significa que cada 100 usuarios generan 72 nuevos.
Con paid acquisition complementaria, esto es crecimiento sostenible.
```

### 7.3 Canales de Distribución del Código de Referido

| Canal | Estrategia | Timing |
|-------|-----------|--------|
| **WhatsApp** | Mensaje pre-escrito con link. Es el canal #1 en LATAM. | Al compartir código |
| **TikTok/IG Story** | QR animado con axolotito bailando. "¡Juega conmigo!" | Post-ganar partida difícil |
| **Twitter/X** | "Acabo de ganar 12 partidas seguidas en Axolotto 🦎 ¿Me ganas? axolot.to/join/..." | Post-partida |
| **Twitch/Stream** | QR en overlay del streamer. Código personalizado para creadores de contenido. | En vivo |
| **En persona** | QR descargable para mostrar en la pantalla del cel. Útil en eventos/escuelas/universidades. | Cualquier momento |

### 7.4 Programa de Creadores (Fase Futura)

Códigos de referido especiales para creadores de contenido con:
- 10% de revenue share en compras de sus referidos (primeros 90 días)
- Dashboard de analytics (cuántos referidos, cuánto generaron, earnings)
- Badge de "Creador Verificado" en el juego
- Early access a nuevos axolotitos para mostrar en stream

### 7.5 Momentos de "Compartir" en el Juego

El botón de compartir código NO debería estar solo en la pantalla de Amigos. Momentos naturales:

| Momento | Gatillante emocional | Mensaje |
|---------|---------------------|---------|
| **Ganar partida difícil** | Euforia, orgullo | "¡Gané en modo difícil! ¿Puedes vencerme? 🏆" |
| **Eclosionar axolotito legendario** | Sorpresa, presumir | "¡Acabo de sacar un Axolotito Legendario! ✨" |
| **Subir de nivel VIP** | Estatus, logro | "¡Soy VIP Dorado en Axolotto! ⭐ Juega conmigo" |
| **Cueva decorada con ítems raros** | Orgullo de colección | "Mi cueva en Axolotto 🏠 ¿Cómo está la tuya?" |
| **Día 7 de racha** | Compromiso, rutina | "7 días seguidos jugando Axolotto 🦎 ¡Únete!" |

---

## 8. Arquitectura Técnica

### 8.1 Modelos de Base de Datos

#### FriendRelation

```python
# backend/app/models/social.py (NUEVO)

class FriendStatus(str, enum.Enum):
    PENDING = "pending"        # Solicitud enviada, no aceptada aún
    ACTIVE = "active"          # Amigos confirmados
    BLOCKED = "blocked"        # Bloqueado (unilateral)
    REMOVED = "removed"        # Eliminado (soft delete)

class FriendRelation(SQLModel, table=True):
    __tablename__ = "friend_relations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_a: str = Field(foreign_key="users.privy_did", index=True)  # quien envió solicitud
    user_b: str = Field(foreign_key="users.privy_did", index=True)  # quien recibe
    status: FriendStatus = Field(default=FriendStatus.PENDING)
    friends_since: Optional[datetime] = None
    interaction_count: int = 0       # total interacciones (likes + gifts + visits + games)
    last_interaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_a", "user_b", name="uq_friend_pair"),
        Index("idx_friend_status", "status"),
        Index("idx_friend_user_b_status", "user_b", "status"),
    )
```

#### ReferralCode

```python
class ReferralCode(SQLModel, table=True):
    __tablename__ = "referral_codes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.privy_did", unique=True, index=True)
    code: str = Field(unique=True, index=True, max_length=30)
    total_uses: int = 0
    active_referrals: int = 0
    rewards_earned_frj: int = 0
    rewards_earned_axf: int = 0
    created_at: datetime
    updated_at: datetime
```

#### ReferralTracking

```python
class ReferralStatus(str, enum.Enum):
    REGISTERED = "registered"        # Creó cuenta con el código
    TUTORIAL_DONE = "tutorial_done"  # Completó tutorial
    D7_RETAINED = "d7_retained"      # Jugó en D7
    CONVERTED = "converted"          # Hizo primera compra
    CHURNED = "churned"              # 30 días sin jugar

class ReferralTracking(SQLModel, table=True):
    __tablename__ = "referral_tracking"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    referrer_id: str = Field(foreign_key="users.privy_did", index=True)
    referred_id: str = Field(foreign_key="users.privy_did", unique=True, index=True)
    code_used: str = Field(foreign_key="referral_codes.code")
    status: ReferralStatus = Field(default=ReferralStatus.REGISTERED)
    rewards_given_to_referrer: str = "{}"  # JSON: {"tutorial": true, "d7": false, ...}
    rewards_given_to_referred: str = "{}"
    referred_at: datetime
    converted_at: Optional[datetime] = None
    churned_at: Optional[datetime] = None
```

#### SocialActionLog (para analytics y anti-abuse)

```python
class SocialActionType(str, enum.Enum):
    LIKE_GIVEN = "like_given"
    GIFT_SENT = "gift_sent"
    CAVE_VISITED = "cave_visited"
    GAME_INVITE_SENT = "game_invite_sent"
    FRIEND_REQUEST_SENT = "friend_request_sent"
    FRIEND_REQUEST_ACCEPTED = "friend_request_accepted"

class SocialActionLog(SQLModel, table=True):
    __tablename__ = "social_action_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: str = Field(foreign_key="users.privy_did", index=True)
    target_id: str = Field(foreign_key="users.privy_did", index=True)
    action_type: SocialActionType
    metadata_json: str = "{}"  # item_id, quantity, etc.
    created_at: datetime
```

### 8.2 Endpoints API

#### Friends

```
GET    /social/friends                          → Lista de amigos (con status online/offline)
POST   /social/friends/request                  → Enviar solicitud { target_user_id }
POST   /social/friends/accept/{request_id}      → Aceptar solicitud
POST   /social/friends/reject/{request_id}      → Rechazar solicitud
DELETE /social/friends/{friend_id}              → Eliminar amigo
POST   /social/friends/block/{user_id}          → Bloquear usuario
GET    /social/friends/pending                  → Solicitudes pendientes recibidas
GET    /social/friends/sent                     → Solicitudes enviadas (no respondidas)
GET    /social/friends/suggestions              → Sugerencias (amigos de amigos, recientes)
GET    /social/friends/search?q=nickname        → Buscar jugadores
GET    /social/friends/recent-players           → Jugadores de últimas salas públicas
GET    /social/friends/{friend_id}/cave         → Datos de cueva de amigo (visita)
```

#### Social Actions

```
POST   /social/like/{target_user_id}            → Dar like a cueva de amigo (1/día/amigo)
POST   /social/gift/{target_user_id}            → Enviar regalo { item_id, quantity }
POST   /social/visit/{target_user_id}           → Registrar visita a cueva
GET    /social/notifications                    → Notificaciones sociales pendientes
GET    /social/leaderboard/friends              → Ranking entre amigos (semanal)
```

#### Referrals

```
GET    /referrals/code                          → Obtener mi código de referido
POST   /referrals/claim/{code}                  → Reclamar código al registrarse
GET    /referrals/dashboard                     → Mi dashboard de referidos (cuántos, rewards)
GET    /referrals/rewards/history               → Historial de recompensas ganadas
```

### 8.3 Servicios Backend (Nuevos)

```
backend/app/services/social_service.py
    - send_friend_request()
    - accept_friend_request()
    - remove_friend()
    - get_friends_list()
    - get_online_status()
    - process_like()
    - process_gift()
    - validate_gift_eligibility()

backend/app/services/referral_service.py
    - generate_referral_code()
    - claim_referral()
    - process_referral_reward()
    - check_referral_eligibility()
    - validate_anti_fraud()
```

### 8.4 Componentes Frontend (Nuevos/Modificados)

```
NUEVOS:
frontend/components/social/AmigosPage.tsx         → Pantalla completa de amigos
frontend/components/social/FriendRequestPanel.tsx → Panel de solicitudes
frontend/components/social/ReferralDashboard.tsx  → Dashboard de referidos
frontend/components/social/ShareCodeSheet.tsx     → Sheet de compartir código
frontend/components/social/SocialNotifications.tsx → Campanita de notificaciones
frontend/components/social/FriendCaveView.tsx     → Vista de cueva de amigo
frontend/components/social/GiftPanel.tsx          → Panel de envío de regalos

MODIFICADOS:
frontend/components/santuario/ZonaInferior.tsx    → Conectar a datos reales
frontend/components/play/ZoneDock.tsx             → Vincular tab "Amigos"
frontend/components/HostingSetupModal.tsx         → Validar visibilidad "friends"
frontend/app/page.tsx                             → Agregar ruta de pantalla Amigos

HOOKS:
frontend/hooks/useSocial.ts                       → useFriends, useFriendRequests, useSocialActions
frontend/hooks/useReferrals.ts                    → useReferralCode, useReferralDashboard
```

### 8.5 Tareas de Infraestructura

- [ ] Migración: crear tablas `friend_relations`, `referral_codes`, `referral_tracking`, `social_action_logs`
- [ ] Rate-limiting por IP + user_id en endpoints sociales
- [ ] Job nocturno: detectar y marcar referidos como `churned` (30d sin actividad)
- [ ] Job nocturno: calcular y actualizar `interaction_count` en FriendRelation
- [ ] Evento: al aceptar referido → crear FriendRelation automáticamente
- [ ] Modificar `POST /multiplayer/create-room` para validar visibilidad `friends` contra el grafo social
- [ ] Migración de datos: generar códigos de referido para usuarios existentes

---

## 9. Plan de Implementación por Fases

### Fase 1: Core Social Graph (task-1780974961-58) — 2-3 semanas

**Objetivo**: Tener amigos funcionales. Poder agregar, aceptar, listar, y ver cuevas.

| # | Tarea | Archivos | Prioridad |
|---|-------|----------|-----------|
| 1.1 | Crear `backend/app/models/social.py` con `FriendRelation` + `SocialActionLog` | Nuevo | P0 |
| 1.2 | Migración Alembic para tablas sociales | Nuevo | P0 |
| 1.3 | `social_service.py`: send/accept/reject/remove/list friends | Nuevo | P0 |
| 1.4 | Endpoints CRUD de amigos en `backend/app/api/v1/endpoints/social.py` | Nuevo | P0 |
| 1.5 | Endpoint `GET /social/friends/search` + `GET /social/friends/recent-players` | social.py | P1 |
| 1.6 | Hook `useSocial.ts` en frontend | Nuevo | P0 |
| 1.7 | Componente `AmigosPage.tsx` (pantalla principal de amigos) | Nuevo | P0 |
| 1.8 | `FriendRequestPanel.tsx` (solicitudes pendientes) | Nuevo | P1 |
| 1.9 | Vincular pestaña "Amigos" en `ZoneDock.tsx` → `AmigosPage` | Modificar | P0 |
| 1.10 | Conectar `ZonaInferior.tsx` a datos reales (lista de 4 amigos) | Modificar | P0 |
| 1.11 | `FriendCaveView.tsx`: visitar cueva de amigo (reemplaza ZonaCentral) | Nuevo | P1 |
| 1.12 | Likes: `POST /social/like` + botón ❤️ funcional | Ambos | P1 |
| 1.13 | Validar visibilidad `friends` en `create-room` contra grafo social real | Modificar | P1 |

**Verificación Fase 1:**
- [ ] Puedo buscar un jugador por nickname y enviarle solicitud
- [ ] El otro jugador recibe la solicitud y puede aceptar/rechazar
- [ ] Amigos aparecen en ZonaInferior (4 más activos)
- [ ] Puedo tocar 👁 y ver la cueva de un amigo
- [ ] ❤️ Like funciona (1 toque, feedback háptico, +1 FRJ ambos)
- [ ] Sala con visibilidad "friends" solo deja entrar a amigos

### Fase 2: Referral System (task-1780974969-59) — 2 semanas

**Objetivo**: Sistema de referidos completo con recompensas progresivas.

| # | Tarea | Archivos | Prioridad |
|---|-------|----------|-----------|
| 2.1 | Agregar `ReferralCode` + `ReferralTracking` a `social.py` | social.py | P0 |
| 2.2 | Migración para tablas de referidos | Nuevo | P0 |
| 2.3 | `referral_service.py`: generate code, claim, process rewards | Nuevo | P0 |
| 2.4 | Endpoints de referidos en `backend/app/api/v1/endpoints/referrals.py` | Nuevo | P0 |
| 2.5 | Job nocturno: detectar churn, calcular métricas de referidos | Nuevo | P1 |
| 2.6 | Anti-fraud: detección de multi-cuenta (misma IP/wallet/device) | referral_service.py | P1 |
| 2.7 | Hook `useReferrals.ts` | Nuevo | P0 |
| 2.8 | `ReferralDashboard.tsx`: dashboard en pantalla de Amigos | Nuevo | P0 |
| 2.9 | `ShareCodeSheet.tsx`: sheet nativa de compartir | Nuevo | P0 |
| 2.10 | Landing page ligera `axolot.to/join/{code}` | NUEVO (frontend/landing?) | P1 |
| 2.11 | Auto-friend: al reclamar código → crear FriendRelation con referidor | Modificar social_service | P0 |
| 2.12 | "Momentos de compartir": botón post-ganar, post-eclosión legendaria, etc. | Modificar varios | P2 |

**Verificación Fase 2:**
- [ ] Cada usuario tiene un código único generado
- [ ] Share sheet nativo funciona con link pre-escrito
- [ ] Link de referido abre landing page con info del referidor
- [ ] Al registrarse con código, ambos reciben rewards iniciales
- [ ] Dashboard muestra mis referidos y rewards acumulados
- [ ] Referidor se vuelve amigo automáticamente del referido

### Fase 3: Social Deepening — 2 semanas

**Objetivo**: Gifting, mejores amigos, rankings sociales, notificaciones.

| # | Tarea | Prioridad |
|---|-------|-----------|
| 3.1 | Gifting: `GiftPanel.tsx` + `POST /social/gift` | P1 |
| 3.2 | Sistema de "Mejor Amigo" (30d + 10 interacciones) | P2 |
| 3.3 | Rankings entre amigos (leaderboard semanal) | P2 |
| 3.4 | `SocialNotifications.tsx` (campanita en HUD) | P1 |
| 3.5 | Cueva destacada (boost de visibilidad pago) | P2 |
| 3.6 | Integración con chat (`docs/plan_chat_integration.md`) para DMs entre amigos | P2 |

---

## 10. KPIs & Métricas de Éxito

### North Star Metric

> **Amigos activos semanales**: número de jugadores que tuvieron ≥1 interacción social (like, visita, gift, juego juntos) en los últimos 7 días.

### KPIs Primarios

| KPI | Baseline (sin capa social) | Meta D30 | Meta D90 |
|-----|---------------------------|----------|----------|
| Amigos por usuario activo | 0 | 8 | 15 |
| % nuevos usuarios vía referido | 0% | 15% | 30% |
| Retención D7 | ~25%* | 35% | 45% |
| Retención D30 | ~10%* | 18% | 25% |
| DAU/MAU | ~20%* | 30% | 40% |
| Interacciones sociales diarias por DAU | 0 | 5 | 10 |

*\*Baselines estimados — necesito datos reales del analytics actual.*

### KPIs Secundarios

| KPI | Descripción |
|-----|-------------|
| Tasa de aceptación de solicitudes | % solicitudes aceptadas / enviadas |
| Tasa de conversión de referido | % registrados que llegan a D7 |
| ARPU social | Ingreso promedio de usuarios con ≥1 amigo vs sin amigos |
| Coeficiente viral K | Ver fórmula en sección 7.2 |
| Gifts enviados por DAU | Promedio diario de regalos enviados |
| Tasa de reciprocidad | % gifts que reciben un gift de vuelta en 48h |

### Dashboard de Social Health (a construir en Fase 1)

```
┌─────────────────────────────────────────────────┐
│  SOCIAL HEALTH DASHBOARD                         │
│                                                  │
│  👥 Total amigos: 12,450                         │
│  🔗 Conexiones nuevas hoy: 234                   │
│  ❤️ Likes hoy: 1,890                             │
│  🎁 Gifts hoy: 456                               │
│  💌 Referidos nuevos esta semana: 89             │
│  📊 K viral (7d): 0.68                           │
└─────────────────────────────────────────────────┘
```

---

## Apéndice A: Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| Baja adopción (pocos agregan amigos) | Media | Alto | Momentos de "Agregar amigo" post-partida. Sugerir automáticamente jugadores recientes. |
| Abuso de multi-cuenta para referidos | Alta | Medio | Detección IP/wallet/device fingerprint. Delay de 24h en rewards D7+. Requiere actividad real. |
| Spam / acoso entre jugadores | Media | Alto | Bloqueo unilateral. Rate-limiting. Reportes con revisión manual. No chat sin confirmación de amistad. |
| Complejidad técnica del social graph | Media | Medio | Empezar simple: solo amigos directos. Sin grafo de "amigos de amigos" inicialmente. |
| Canibalización de paid acquisition | Baja | Bajo | Los referidos alcanzan audiencias que paid no toca (círculos de confianza). Son complementarios. |

## Apéndice B: Decisiones Pendientes

1. **¿Landing page separada o integrada en el frontend principal?** — Si es separada, puede ser más ligera y cargar más rápido para nuevos usuarios. Si es integrada, menos infraestructura.
2. **¿Los códigos de referido deben ser on-chain (contrato) u off-chain (DB)?** — Off-chain inicialmente por simplicidad y costo de gas. Si el programa crece, migrar a on-chain para transparencia.
3. **¿Chat entre amigos inmediato o diferido a Fase 3?** — Recomiendo diferir. El chat tiene su propio plan (`docs/plan_chat_integration.md`). La capa social debe funcionar sin chat (interacción asimétrica).
4. **¿Integración con X (Twitter) para "Iniciar sesión y encontrar amigos"?** — Posible en Fase 3+. Privy ya soporta social login. Buscar amigos por contactos de Twitter podría acelerar la adopción.
5. **¿Gifting con AXF o solo ítems?** — Solo ítems y FRJ inicialmente. AXF tiene valor de compra directa y podría generar exploits. Revisar en Fase 3.

## Apéndice C: Referencias

- `docs/GDD.md` — Game Design Document general
- `docs/santuario_ux_plan.md` — Layout 9:16, ZonaInferior social
- `docs/plan_santuario_mobile_layout.md` — Implementación del santuario mobile
- `docs/plan_chat_integration.md` — Plan de chat (complementario, Fase 3+)
- `docs/completed/vip_club_design.md` — VIP con idea de referidos (sección 13.2)
- `docs/completed/AXOLOTTO_BIBLE.md` — Fase 10: ecosistema y comunidad
- `docs/completed/crypto_purchase_plan.md` — Bonus de referido en crypto purchases
- `wiki/CHANGELOG.md` — Historial de cambios del proyecto
