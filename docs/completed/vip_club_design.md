# Axolotto VIP Club — Diseño Completo del Sistema

> Documento de diseño y plan de implementación.
> Decisiones confirmadas: días se apilan; upgrade aplica crédito proporcional; slots extra se congelan al expirar; GAL diario se reclama o expira (acumula hasta 2 días); el marco VIP vive en el Axolotito Principal, no en un perfil de usuario.

---

## 1. Filosofía del Sistema

El VIP Club no es un "pass cosmético con propina de monedas". Es la razón por la que un jugador comprometido prefiere Axolotto sobre cualquier otra alternativa.

**Principios de diseño:**
- El ROI en moneda sola ya debe ser positivo en todos los niveles
- Los exclusivos no deben poder comprarse de ninguna otra forma
- El sistema recompensa lealtad acumulada, no solo la primera compra
- La expiración nunca se siente como castigo — activos congelados, no perdidos
- El GAL diario requiere acción del jugador para crear hábito de login diario

**Filosofía de representación visual:**
No existe un "perfil de usuario" clásico. El **Axolotito** es el avatar del jugador. Por tanto, el estatus VIP se expresa a través del Axolotito Principal del jugador — no de un nombre de usuario ni de un avatar de perfil. Cuando otros jugadores ven tu axolotito en el lobby de multijugador, en los leaderboards o en el marketplace, ven tu rango VIP en él.

---

## 2. Los Tres Niveles

### 🪸 Pase Coral — 100 AXG/mes ($200 MXN)
*El punto de entrada sin culpa.*

| Beneficio | Detalle |
|---|---|
| **+40 GAL/día** (hasta 1,200 GAL/mes si reclamas todos los días) | ≈ 120 AXG de valor — ROI positivo solo en GAL |
| **5% descuento en tienda** | Todos los items AXG excepto Webitos |
| **1 tirada de Gashapón/mes** | Acreditada al activar/renovar |
| **Bono de bienvenida (primer mes):** +200 GAL inmediatos | Solo al activar por primera vez |
| **Marco Coral** en el Axolotito Principal | Borde coral/turquesa animado |
| **Badge "🪸" en tablas** del jugador (leaderboards/marketplace) | Indicador de esquina sutil |

---

### ✨ Pase Dorado — 250 AXG/mes ($500 MXN)
*El sweet spot. Para quienes rentan, venden y juegan multijugador.*

| Beneficio | Detalle |
|---|---|
| **+100 GAL/día** (hasta 3,000 GAL/mes) | ≈ 300 AXG de valor |
| **12% descuento en tienda** | |
| **3 tiradas de Gashapón/mes** | |
| **+1 slot de tabla** mientras dure la suscripción | Rentas esa tabla extra y el pase se paga solo |
| **Caja mensual:** 1 Booster aleatorio | Al activar o renovar |
| **Bono de bienvenida (primer mes):** +500 GAL + 1 Booster extra | |
| **Comisión P2P reducida: 3%** | vs. 5% estándar |
| **Marco Dorado + corona animada** en el Axolotito Principal | Borde dorado con shimmer |
| **Acceso anticipado 24h** a nuevas fases de contenido | |

---

### 🌟 Pase Axolite — 500 AXG/mes ($1,000 MXN)
*Para los que viven Axolotto.*

| Beneficio | Detalle |
|---|---|
| **+200 GAL/día** (hasta 6,000 GAL/mes) | ≈ 600 AXG de valor |
| **20% descuento en tienda** | |
| **5 tiradas de Gashapón/mes** | |
| **+2 slots de tabla** | |
| **+1 slot de Axolotito** (límite 7 → 8) | |
| **Caja premium mensual:** 1 Booster Foil + 1 Booster normal | |
| **Bono de bienvenida (primer mes):** +1,000 GAL + 1 Booster Foil extra | |
| **Comisión P2P: 1.5%** | |
| **Entrada a multijugador -15%** | |
| **+5% sobre jackpots ganados** | |
| **Marco Axolite animado** en el Axolotito Principal | Gradiente oro→rosa→morado con partículas |
| **Badge "🌟" en tablas** | |
| **Nombre en color dorado** en rankings y leaderboards | |
| **Botón "Compartir rango"** | Genera card con tu axolotito + marco para redes sociales |

---

## 3. El Marco VIP — Todos los Axolotitos

### Concepto
No existe un "Axolotito Principal". Si el jugador es VIP, **todos sus axolotitos** llevan el marco del tier, porque el estatus es del jugador, no del axolotito.

Esto es correcto porque en multijugador puedes mandar varios axolotitos al mismo tiempo — todos deberían verse como VIP porque lo eres.

Para tablas en leaderboards y marketplace, el badge de tier es del dueño: si el dueño es VIP, la tabla tiene el badge. La identidad del comprador/vendedor en el marketplace no se expone públicamente — la plataforma maneja la transacción y tiene el `user_id` para el registro interno. No se necesita sistema de reputación.

### Marco visual por tier

| Tier | Marco en cada Axolotito del usuario | Badge en sus Tablas |
|---|---|---|
| Sin VIP | Ninguno | Ninguno |
| 🪸 Coral | Borde turquesa con pulso suave | Cinta "🪸" en esquina |
| ✨ Dorado | Borde dorado con shimmer animado + corona | Cinta "✨" en esquina |
| 🌟 Axolite | Gradiente oro→rosa→morado rotando + partículas | Cinta "🌟" + brillo |

**Implementación frontend:** el componente de Axolotito recibe `vip_tier` del propietario y aplica el CSS correspondiente. No requiere ningún campo nuevo en el modelo — se usa `user.vip_tier` del owner.

---

## 4. El Ícono VIP — Siempre Visible en la UI

### Posición
Encima de los paneles de monedas (AXG / GAL), en la barra superior de la app. No enterrado en el shop.

### Estado 1: Sin VIP (modo invitación)
```
╔══════════════════════════════╗
║  [✨ VIP CLUB  ▸]            ║  ← chip con shimmer/pulse animado
║  AXG: 1,234   GAL: 5,678    ║
╚══════════════════════════════╝
```
- El chip tiene una animación de shimmer (como efecto foil) que lo hace irresistible
- Color: gradiente oscuro con destellos dorados
- Texto: "VIP CLUB" + flecha que indica "clic para saber más"
- Al hover/tap: tooltip "Beneficios exclusivos para miembros VIP 👑"

### Estado 2: VIP Activo
```
╔══════════════════════════════╗
║  [🪸 CORAL · 28d]            ║  ← compact badge con días restantes
║  AXG: 1,234   GAL: 5,678    ║
╚══════════════════════════════╝
```
- Color del badge coincide con el tier (coral/dorado/gradiente Axolite)
- Si quedan ≤ 5 días: badge en ámbar con ⚠️ y parpadeo suave
- Si quedan ≤ 1 día: badge en rojo, urgencia visible

### Estado 3: GAL pendiente de reclamar
```
╔══════════════════════════════╗
║  [✨ DORADO · 💎 80 GAL]     ║  ← badge + indicador de claim disponible
║  AXG: 1,234   GAL: 5,678    ║
╚══════════════════════════════╝
```
- Cuando hay `vip_pending_gal > 0`, el badge muestra el GAL disponible
- El badge tiene un pulso de color que invita a clickear y reclamar
- Al reclamar desde el modal: animación de monedas que vuelan desde el modal al contador de GAL

---

## 5. El Modal VIP — Dos Modos

### Modo A: Sin VIP (Sales Experience)

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   👑  VIP CLUB DE AXOLOTTO                      │
│   Únete a la élite de jugadores.                │
│                                                 │
│   ┌─────────────────────────────────────────┐   │
│   │  🎁 REGALO DE BIENVENIDA                │   │
│   │  Al activar hoy recibes al instante:    │   │
│   │  • 200 GAL (Coral)                      │   │
│   │  • 500 GAL + 1 Booster (Dorado)         │   │
│   │  • 1,000 GAL + 1 Foil (Axolite)         │   │
│   └─────────────────────────────────────────┘   │
│                                                 │
│   ELIGE TU NIVEL                                │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │ 🪸 CORAL │  │✨ DORADO │  │🌟AXOLITE │    │
│   │ 100 AXG  │  │ 250 AXG  │  │ 500 AXG  │    │
│   │ /mes     │  │ /mes     │  │ /mes     │    │
│   │          │  │ ★ POPULAR│  │          │    │
│   │ +40GAL/d │  │+100GAL/d │  │+200GAL/d │    │
│   │ 5% desc  │  │ 12% desc │  │ 20% desc │    │
│   │          │  │ +1 tabla │  │ +2 tablas│    │
│   │          │  │ 3% P2P   │  │ 1.5% P2P │    │
│   │          │  │          │  │ +5% jckpt│    │
│   │[Unirme]  │  │[Unirme]  │  │[Unirme]  │    │
│   └──────────┘  └──────────┘  └──────────┘    │
│                                                 │
│   "342 jugadores VIP activos ahora mismo" 🔥   │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Detalles UX:**
- Las 3 tarjetas tienen animación de hover (se elevan ligeramente)
- La tarjeta "Dorado" tiene un badge "⭐ POPULAR" y es ligeramente más grande
- Al pulsar "Unirme", el botón se convierte en el total con impuesto: "Confirmar — 100 AXG"
- Segundo clic ejecuta la compra
- Después de comprar: la tarjeta "explota" en confeti y el modal transiciona al Modo B

### Modo B: VIP Activo (Dashboard)

```
┌─────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────┐   │
│  │  [Axolotito Principal con marco VIP]      │   │
│  │          ✨ DORADO                        │   │
│  │     Hola, Chispas 🎉                      │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  Suscripción activa — vence el 25 jun 2026      │
│  [████████████████░░░░░░░░] 28 días restantes   │
│                                                 │
│  ╔═══════════════════════════════════════════╗  │
│  ║  💎 BONO DIARIO                           ║  │
│  ║                                           ║  │
│  ║      80 GAL disponibles 🟢               ║  │
│  ║  2 días acumulados · expiran en 18h 23m   ║  │
│  ║                                           ║  │
│  ║          [ RECLAMAR 80 GAL → ]            ║  │
│  ╚═══════════════════════════════════════════╝  │
│                                                 │
│  — — o si no hay pending — —                    │
│                                                 │
│  ╔═══════════════════════════════════════════╗  │
│  ║  💎 BONO DIARIO                           ║  │
│  ║                                           ║  │
│  ║      Ya reclamaste hoy ✅                 ║  │
│  ║      Próximo bono en  11h 30m             ║  │
│  ╚═══════════════════════════════════════════╝  │
│                                                 │
│  RACHA  🔥 4 meses consecutivos                │
│  ●─●─●─●─○─○─○─○ ←──── 6m para Veterano       │
│                                                 │
│  BENEFICIOS ACTIVOS                             │
│  ✓ 100 GAL/día      ✓ 12% desc. tienda         │
│  ✓ +1 slot tabla    ✓ 3% comisión P2P          │
│  ✓ Gashapón ×3/mes                              │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  ↑ Sube a AXOLITE — paga solo 375 AXG    │  │
│  │  (crédito: 125 AXG por 15 días restantes)│  │
│  │                  [ Ver Axolite → ]        │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  HISTORIAL DE MEMBRESÍA                         │
│  ENE  FEB  MAR  ABR  MAY  JUN                  │
│   —    —   🪸   🪸   ✨   ✨    activo          │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Detalles UX:**
- El Axolotito Principal aparece animado (idle animation) con su marco VIP en el header del modal
- Si no tiene Axolotito Principal designado: muestra un placeholder con prompt "Designa tu Axolotito Principal"
- El botón "Reclamar" tiene un glow pulsante verde cuando hay GAL disponible
- Al reclamar: animación de monedas que vuelan hacia el contador de GAL en la barra superior, el contador sube con contador animado
- Si quedan ≤ 5 días: encima del header aparece banner "⚠️ Tu suscripción vence pronto — Renovar"
- El "upgrade banner" solo aparece si el usuario NO es Axolite
- El historial muestra los últimos 6-12 meses con ícono del tier activo ese mes (o "—" si no tenía VIP)

---

## 6. Mecánica de Claim Diario

- Cada medianoche UTC el scheduler genera GAL en `vip_pending_gal`
- El jugador debe abrir el modal y pulsar "Reclamar"
- **Acumulación máxima: 2 días** — si no reclamas el día 1, el día 2 tienes el doble disponible
- Al llegar el día 3 sin reclamar: el lote más antiguo **expira**, registrado en ledger como `VIP_GAL_EXPIRED`
- Ejemplo Dorado (100 GAL/día):
  - Día 1 sin reclamar → pending = 100 GAL, timer = 48h
  - Día 2 sin reclamar → pending = 200 GAL, timer baja a 24h
  - Día 3 sin reclamar → 100 GAL del día 1 expiran, pending = 100 GAL del día 2, timer reinicia a 48h

**Por qué 2 días y no 1:**
Un solo día de gracia se siente punitivo para un suscriptor de pago. Dos días permite ausentarse un día sin perder todo. Tres días elimina el incentivo de engagement diario.

---

## 7. Mecánica de Upgrade (Crédito Proporcional)

```
crédito = (precio_plan_actual / 30) × días_restantes
precio_final = precio_plan_nuevo - crédito
```

**Ejemplo:** Coral con 15 días restantes → Dorado
- Crédito: (100 / 30) × 15 = **50 AXG**
- Precio final: 250 − 50 = **200 AXG**
- El nuevo periodo de 30 días arranca desde hoy

**Reglas:**
- Crédito con floor en 1 AXG (nunca gratis)
- Solo aplica para **subir** de nivel. Para bajar, el cambio ocurre al vencimiento
- Mismo tier: simplemente suma 30 días sin crédito
- `vip_pending_gal` no se pierde al hacer upgrade

---

## 8. Mecánica de Congelación al Expirar

Cuando el VIP expira y el usuario tenía slots extra:

### Boards
- Las tablas que excedan `unlocked_board_slots` base (3) se marcan `is_frozen_by_vip = True`
- Criterio: las adquiridas más recientemente (`ORDER BY created_at DESC`)
- HTTP 423 Locked en endpoints de rentar, vender, jugar
- Auto-descongelación al renovar el mismo tier o superior

### Axolotitos (solo Axolite)
- El Axolotito más reciente queda frozen si el usuario tenía 8
- Si el Axolotito Principal queda frozen: auto-asignar el siguiente más antiguo como Principal
- 7 días de gracia con notificaciones en días 7, 3 y 1 antes del vencimiento

---

## 9. Sistema de Racha

- `vip_streak_months` incrementa si la renovación ocurre dentro de los 3 días tras el vencimiento
- Se resetea si lapsa más de 3 días
- La racha no se rompe al cambiar de tier

### Recompensas permanentes (se quedan aunque el VIP expire):

| Racha | Recompensa |
|---|---|
| 3 meses | Badge "Constante 🔥" permanente en perfil |
| 6 meses | Marco "Veterano" cosmético exclusivo |
| 12 meses | Título "Axolotto Original" + 1 Webito Astral gratis |
| 24 meses | Marco legendario "Leyenda del Nido" — el más raro del juego |

---

## 10. Bono de Bienvenida (Primera Activación)

Solo se otorga la primera vez que el jugador activa ese tier.

| Tier | GAL inmediatos | Items extra |
|---|---|---|
| 🪸 Coral | +200 GAL | — |
| ✨ Dorado | +500 GAL | 1 Booster normal |
| 🌟 Axolite | +1,000 GAL | 1 Booster Foil |

El bono es atómico con la compra (mismo commit de BD). Se rastrea con `vip_tiers_activated: JSON array`.

---

## 11. Configuración Centralizada (`config.py`)

```python
VIP_CONFIG = {
    "coral": {
        "price_axg": 100,
        "gal_daily": 40,
        "discount": 0.05,
        "gashapon_monthly": 1,
        "table_bonus_slots": 0,
        "axolotito_bonus_slots": 0,
        "p2p_commission": 0.04,
        "jackpot_bonus": 0.0,
        "multiplayer_discount": 0.0,
        "welcome_gal": 200,
        "welcome_boosters": [],
    },
    "dorado": {
        "price_axg": 250,
        "gal_daily": 100,
        "discount": 0.12,
        "gashapon_monthly": 3,
        "table_bonus_slots": 1,
        "axolotito_bonus_slots": 0,
        "p2p_commission": 0.03,
        "jackpot_bonus": 0.0,
        "multiplayer_discount": 0.0,
        "welcome_gal": 500,
        "welcome_boosters": ["normal"],
    },
    "axolite": {
        "price_axg": 500,
        "gal_daily": 200,
        "discount": 0.20,
        "gashapon_monthly": 5,
        "table_bonus_slots": 2,
        "axolotito_bonus_slots": 1,
        "p2p_commission": 0.015,
        "jackpot_bonus": 0.05,
        "multiplayer_discount": 0.15,
        "welcome_gal": 1000,
        "welcome_boosters": ["foil"],
    },
}
```

---

## 12. Estado de Implementación

### Backend ✅ Completado

| Tarea | Archivo | Estado |
|---|---|---|
| Campos VIP en `User` | `models/user.py` | ✅ |
| `is_frozen_by_vip` en `Board` | `models/board.py` | ✅ |
| `is_frozen_by_vip` en `Axolotito` | `models/axolotito.py` | ✅ |
| `BURN` + `VIP_GAL_EXPIRED` en `TransactionType` | `models/economy.py` | ✅ |
| `VIP_CONFIG` centralizado | `core/config.py` | ✅ |
| Detección VIP en `buy_item` | `services/shop_service.py` | ✅ |
| `_handle_vip_purchase` con crédito + racha + bono bienvenida | `services/shop_service.py` | ✅ |
| `get_vip_upgrade_preview` | `services/shop_service.py` | ✅ |
| Descuento VIP en precio de tienda | `services/shop_service.py` | ✅ |
| Límite axolotito respeta bonus VIP | `services/shop_service.py` | ✅ |
| Scheduler asyncio (GAL diario + congelación) | `services/vip_scheduler.py` | ✅ |
| Migraciones dinámicas en startup | `main.py` | ✅ |
| `GET /auth/vip-status` | `endpoints/user.py` | ✅ |
| `POST /auth/vip/claim-daily-gal` | `endpoints/user.py` | ✅ |
| `GET /shop/vip/upgrade-preview` | `endpoints/shop.py` | ✅ |
| Guard HTTP 423 en rentar/vender tabla | `endpoints/board.py` | ✅ |
| Seed: 3 ítems VIP reemplazando el antiguo | `scripts/seed_catalog.py` | ✅ |

### Backend ✅ Completado (segunda ronda)

| Tarea | Archivo | Estado |
|---|---|---|
| Frozen guards en `list-sale` y `list-rent` de Axolotito | `endpoints/user.py` | ✅ HTTP 423 |
| Filtrar `is_frozen_by_vip` del marketplace de axolotitos | `endpoints/user.py` | ✅ |
| Comisión P2P con descuento VIP en `buy_axolotito` | `endpoints/user.py` | ✅ 5%→4%→3%→1.5% según tier |
| +5% jackpot bonus Axolite en Premio 1, Premio 2 y Jackpot de Oro | `services/multiplayer_service.py` | ✅ |
| Entrada multijugador -15% para Axolite | `services/multiplayer_service.py` | ✅ |

### Backend 🔲 Pendiente

| Tarea | Archivo | Notas |
|---|---|---|
| Notificaciones 7d/3d/1d antes del vencimiento | `services/vip_scheduler.py` | Requiere sistema de notificaciones push/email — depende de infra |

### Frontend 🔲 Pendiente (toda la sección)

#### Ícono VIP (barra superior, siempre visible)
- [ ] Chip "VIP CLUB" con shimmer cuando no es VIP — invita a clickear
- [ ] Badge de tier compacto cuando es VIP (ej. "🪸 CORAL · 28d")
- [ ] Badge con indicador de GAL disponible cuando `vip_pending_gal > 0` (ej. "✨ DORADO · 💎 80")
- [ ] Badge ámbar + ⚠️ cuando quedan ≤ 5 días
- [ ] Badge rojo cuando queda ≤ 1 día
- [ ] Al click: abre el Modal VIP

#### Modal VIP — Modo A (sin VIP)
- [ ] Header con título y subtítulo
- [ ] Banner "🎁 Regalo de Bienvenida" mostrando bonos por tier
- [ ] 3 tarjetas de tier en fila (Coral / Dorado / Axolite) con badge "⭐ POPULAR" en Dorado
- [ ] Hover: tarjeta se eleva, muestra beneficios completos
- [ ] Botón "Unirme" → confirmación → compra → confeti + transición a Modo B
- [ ] Pie: contador "X jugadores VIP activos ahora mismo"

#### Modal VIP — Modo B (dashboard VIP)
- [ ] Header: Axolotito Principal animado con marco del tier + "Hola, [nombre] 🎉"
- [ ] Si no hay Axolotito Principal designado: placeholder + botón "Designar"
- [ ] Barra de progreso de días restantes (color del tier)
- [ ] Banner de renovación urgente si ≤ 5 días
- [ ] **Claim card:**
  - Con pending: botón "Reclamar X GAL →" con glow verde + timer de expiración
  - Sin pending: "Ya reclamaste hoy ✅ · Próximo en Xh Ym"
  - Al reclamar: animación de monedas volando al contador de GAL
- [ ] Racha: fila de puntos ● por cada mes, destacando milestones (3/6/12/24)
- [ ] Lista de beneficios activos del tier actual
- [ ] Upgrade banner (oculto si es Axolite): precio con crédito (llamar a `/shop/vip/upgrade-preview`)
- [ ] Historial de membresía: últimos 6 meses con ícono del tier de cada mes (o "—")

#### Axolotito Principal y Marcos
- [ ] Campo `is_main` en el modelo Axolotito (frontend)
- [ ] UI para designar un Axolotito como Principal (en la pantalla de gestión de axolotitos)
- [ ] Renderizar marco/borde por tier en la vista del Axolotito Principal
  - Coral: borde turquesa con CSS `box-shadow` pulsante
  - Dorado: borde dorado con CSS `@keyframes shimmer`
  - Axolite: borde con gradiente rotante (`conic-gradient`) + partículas (canvas o CSS)
- [ ] Mostrar Axolotito Principal con marco en:
  - Lobby de multijugador
  - Leaderboards (ranking de jugadores)
  - Marketplace P2P (tarjeta del vendedor/arrendador)
  - Header del modal VIP (Modo B)

#### Tablas con Badge de Tier
- [ ] Badge de esquina en tarjetas de tabla cuando el dueño es VIP
  - Cinta pequeña "🪸" / "✨" / "🌟" en esquina superior derecha
  - Solo en: leaderboards y marketplace; NO en la vista de juego
- [ ] Overlay candado 🔒 + texto "Renueva tu VIP" en boards congeladas
- [ ] Filtrar `is_frozen_by_vip = true` de los listings públicos del marketplace

---

## 13. Ideas para Después

Estas ideas fueron evaluadas y aprobadas conceptualmente pero no se implementan ahora:

### 13.1 VIP Shop Exclusivo
Sección de tienda solo visible para VIPs con items rotativos mensuales: skins de carta exclusivos (borde de carta diferente), avatares de axolotito únicos, cosméticos limitados por tier.

### 13.2 Referidos VIP
Referido activa VIP → ambos reciben días extra. Límite 10 referidos activos por mes.

### 13.3 Torneo VIP Mensual
Lotería exclusiva VIPs cada último domingo. Sin cuota o mínima en GAL. Axolite tiene +10% en puntos.

### 13.4 Multiplicador de Login Diario
El bono de login base ×1.5 / ×2 / ×3 según tier. Requiere implementar sistema de login diario primero.

### 13.5 Card para Redes Sociales (Axolite)
Botón "Compartir mi rango" que genera una imagen con el Axolotito Principal + marco Axolite + stats del jugador. Para Instagram / X / WhatsApp.

---

## 14. Notas de Economía

**Emisión real de GAL con claim obligatorio:**
Suponiendo 85% de claim rate, 100 VIPs distribuidos:
- 50 Coral: 50 × 40 × 0.85 = **1,700 GAL/día**
- 35 Dorado: 35 × 100 × 0.85 = **2,975 GAL/día**
- 15 Axolite: 15 × 200 × 0.85 = **2,550 GAL/día**
- **Total real: ~7,225 GAL/día** (vs 8,500 si fuera auto-crédito)

El GAL tiene sinks naturales (rentas, partidas, consumibles) — monitorear el ratio si la adopción escala.

**Sobre el crédito proporcional:**
No hay vector de abuso: el crédito tiene floor en 1 AXG, solo aplica en upgrade, y cada compra requiere pagar la diferencia real. Nunca hay ganancia en el loop comprar→upgradar→comprar.
