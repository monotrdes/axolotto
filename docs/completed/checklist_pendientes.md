# Checklist Consolidador de Pendientes — Ecosistema Axolotto

Este documento consolida y prioriza todas las tareas y especificaciones descritas en los archivos de diseño (`.md`) del proyecto, comparándolas con el estado actual de la programación en el backend y el frontend. Además, incluye nuevas propuestas de gamificación y monetización.

---

## 🔴 PRIORIDAD ALTA (Crítico — Núcleo Económico, Finanzas y Web3)

### 1. Sistema de Retiro (DevEx / Cash-Out)
*El flujo que permite a los jugadores convertir sus ganancias en dinero real. Actualmente no existe código de retiro en el backend ni en el frontend.*
- [ ] **Modelo de Datos (`WithdrawalRequest`)**: Crear el modelo con soporte para fondos duales (Crypto vs Fiat), moneda solicitada (MXN, USDT, USDC), retención de impuestos (tax_withheld), neto a pagar (net_amount_mxn) y estatus KYC.
- [ ] **Tablas de Base de Datos Adicionales**:
  - Tabla `swap_ledger` para registrar swaps de balance cuando hay retiros mixtos (ej. balance crypto -> fiat).
  - Tabla `blacklisted_cards` para registrar tarjetas/bancos sospechosos y evitar contracargos.
  - Balances de fondos segregados (`crypto_fund_balance` y `fiat_fund_balance`).
- [ ] **Endpoints del Backend**:
  - `POST /bank/withdraw`: Solicitar retiro (mínimo 100 AXG, validación de cooldown de 7 días, saldo e identidad).
  - `GET/PATCH /admin/withdrawals` (Panel de Admin): Listar, aprobar o rechazar solicitudes de retiro.
- [ ] **Servicios y Lógica de Negocio (`withdrawal_service.py`)**:
  - Lógica fiscal: Retener automáticamente el **7% (Régimen de Premios)** y generar autofacturación (CFDI de retención a través de Facturapi).
  - Lógica de Swap: Integrar oracle de precios y DEX interna (Uniswap) o fallback externo para swaps de USDT/USDC a MXN.
  - Validación KYC automática para retiros mayores a $10,000 MXN o según el porcentaje de holdings.
- [ ] **Integración en Frontend (`WithdrawalPage`)**:
  - Interfaz de retiro: Selección de moneda destino, estimación de comisiones, aviso dinámico de requerimiento de KYC y listado de historial.

### 2. Compras Fíat con Mercado Pago
*El riel de entrada principal para jugadores tradicionales. Actualmente el backend solo soporta compras en cripto.*
- [ ] **Servicio de Pasarela (`mercadopago_service.py`)**: Integrar el SDK oficial de Mercado Pago.
- [ ] **Endpoint `POST /bank/checkout/mercadopago`**: Generar preferencia de pago y retornar link con monto en MXN (basado en catálogo: 10 AXG = $20 MXN).
- [ ] **Webhook `POST /bank/webhook/mercadopago`**: Procesar notificaciones de aprobación de pago en background para acreditar AXG al usuario de forma automática.
- [ ] **Integración en Frontend (`Store.tsx`)**:
  - Agregar botón "Pagar con SPEI / Tarjeta / OXXO" usando la pasarela de Mercado Pago.

### 3. Mecánica de Sobres Sellados y Especulación P2P
*Actualmente los boosters se abren instantáneamente al ser comprados o ganados en sorteos de cápsulas. Se rediseñará el flujo para permitir guardarlos en la mochila (PlayerInventory) o venderlos en el mercado secundario P2P ante la escasez física.*

#### **Análisis de Impacto en Sistemas del Juego:**
*   **Contratos Inteligentes (`Boosters.sol`)**: La funcionalidad on-chain ya existe (mint de sobres de Fase 1-3). Al comprar un sobre, el backend minteará el sobre on-chain a la wallet del usuario en vez de las cartas individuales de inmediato.
*   **Mercado P2P (Backend)**: Actualmente solo se pueden vender Axolotitos y Tablas. Se requiere crear un endpoint genérico (o modelo `MarketListing`) para listar ítems del `PlayerInventory` (sobres y cartas) en GAL/AXG.
*   **Inventario del Jugador (`PlayerInventory`)**: Los sobres comprados se guardarán como filas con el `item_id` del booster correspondiente en el catálogo de la tienda.
*   **Sorteos del Gashapón y Cápsulas**: Al ganar un sobre en la ruleta o cápsulas, el booster se añadirá sellado directamente al inventario (usando `_add_to_inventory` en `shop.py`), sin abrirse en el acto.
*   **Economía de Especulación**: Al agotarse los sobres primarios de Fase 1 en la tienda oficial, los jugadores solo podrán conseguirlos a través de la reventa P2P, lo que incrementará las regalías de Tridyland (comisión del 5% del Marketplace).

#### **Tareas Pendientes (En Desarrollo):**
- [x] **Implementar Quema y Apertura de Sobres (Backend)**:
  - [x] Agregar `Web3Service.burn_booster_onchain` para soportar quema del NFT de sobre on-chain.
  - [x] Modificar `ShopService.buy_item` en `shop_service.py` para guardar sobres de cartas sellados por defecto en `PlayerInventory` y realizar acuñación Web3 on-chain.
  - [x] Implementar `ShopService.open_booster` y la ruta `/shop/booster/open` para consumir 1 sobre, realizar quema on-chain, generar 7 cartas aleatorias con su respectivo procesamiento de duplicados y brillantes, guardarlas y acuñarlas.
  - [x] Retornar el `inventory_id` de cada ítem en el endpoint `/inventory/{user_id}`.
- [x] **Visualización e Integración de Apertura (Frontend)**:
  - [x] Mostrar sobres sellados (`item_type === 'BOOSTER'`) al inicio de la sección de **Cartas** en `Inventory.tsx`.
  - [x] Integrar el modal interactivo de unboxing 3D y partículas animadas en `Inventory.tsx` al pulsar "Abrir Sobre".
  - [x] Actualizar el flujo de éxito de compra en `Store.tsx` para ofrecer apertura instantánea o ir al inventario.
- [ ] **Soporte de Especulación P2P**:
  - [ ] Crear endpoints `POST /market/inventory/list` y `POST /market/inventory/buy` para comercio P2P de sobres sellados y cartas sueltas.
  - [ ] Implementar soporte visual en el Marketplace P2P del frontend para enlistar y comprar estos ítems.

### 4. Finalización del Sistema VIP Club
*Backend y Frontend completados.*
- [x] **Campos y Lógica de Axolotito Principal**:
  - [x] Campo `is_main: bool` en modelo `Axolotito` + migración en `main.py` (`ALTER TABLE axolotito ADD COLUMN is_main`).
  - [x] Endpoint `POST /auth/axolotitos/{id}/set-main` — desactiva `is_main` en todos los demás y lo activa en el seleccionado.
  - [x] Lógica de auto-reemplazo en `vip_scheduler.py`: si el VIP expira y el principal se congela, se asigna automáticamente el siguiente Axolotito más antiguo como principal.
- [x] **Guards de Congelamiento**:
  - [x] HTTP 423 en renta/venta/expedición de Axolotitos (`user.py`) y tablas (`board.py`).
  - [x] Marketplaces de Axolotitos (`/axolotitos/market/sale` y `/rent`) filtran `is_frozen_by_vip == False`.
  - [x] Marketplace de tablas (`/rent/market` y `/sale/market`) filtran `is_frozen_by_vip == False` ← *corregido ahora*.
- [x] **Beneficios VIP en Partidas** (`multiplayer_service.py`):
  - [x] Axolite: -15% descuento en entrada multijugador (vía `VIP_CONFIG["axolite"]["multiplayer_discount"]`).
  - [x] Axolite: +5% bonus sobre jackpots ganados (vía `VIP_CONFIG["axolite"]["jackpot_bonus"]`).
- [x] **Integración en Frontend**:
  - [x] **Ícono VIP en cabecera**: `VipChip` en `page.tsx` — shimmer animado para no-VIP, chip con emoji/tier/días/GAL-pendiente pulsante para VIP activo, estado urgente en rojo (≤5 días).
  - [x] **Modal VIP**:
    - *Modo A (Ventas)*: Tabla comparativa de Coral, Dorado, Axolite con precios, beneficios, bono de bienvenida y botón de compra con confirmación doble. Implementado en `VipModal.tsx`.
    - *Modo B (Dashboard)*: Muestra Axolotito Principal con marco animado VIP, barra de progreso temporal, botón "Reclamar GAL" con glow pulsante, contador de racha, toggle auto-renovación y banner de upgrade. Implementado en `VipModal.tsx`.
  - [x] **Marcos Visuales y Badges**:
    - Marcos CSS en `globals.css`: `.vip-frame-coral` (turquesa pulsante), `.vip-frame-dorado` (oro shimmer), `.vip-frame-axolite` (degradado gold→pink→purple ciclando). Usados en `VipModal.tsx` sobre el avatar del Axolotito Principal.
    - Cintas de esquina (🪸 / ✨ / 🌟) implementadas en `RentalMarket.tsx`, `MarketP2P.tsx` y `Rankings.tsx` con colores por tier.

### 5. Migración a Red Base Sepolia Testnet
*El juego sigue corriendo sobre Anvil local en chainId 31337. Para probar MoonPay sandbox en staging es necesario migrar a Base Sepolia L2.*
- [ ] **Deploy de Contratos**: Desplegar los 9 contratos en Base Sepolia usando Foundry.
- [ ] **Actualización de Backend**:
  - Agregar variables de RPC (`https://sepolia.base.org`) y address oficial de USDC (`0x036CbD53842c5426634e7929541eC2318f3dCF7e`) en `config.py` y `.env`.
- [ ] **Actualización de Frontend**:
  - Configurar PrivyProviderWrapper para usar Base Sepolia por default.
  - Modificar client viem y links de exploradores en `Store.tsx` y `CryptoCheckout.tsx` a BaseScan.

---

## 🟠 PRIORIDAD MEDIA (Mecánicas de Juego, Ajustes de Diseño y Bugs)

### 1. Ajustes en Probabilidades de Gashapón y Cápsulas
- [x] **Webito Astral (0.1%) y Booster Foil (0.5%) en Sorteos**:
  - [x] Modificar `roll_gashapon` y `_roll_capsule` en `shop.py` — pre-check legendario antes del pool normal.
  - [x] Al ganarse, van SELLADOS al inventario (`_add_to_inventory`). `is_legendary=True` en respuesta.
  - [x] Gashapón Premium: Legendaria rebajada 15% → 10% (más equilibrado para 250 GAL).
  - [x] Cápsulas: prob. escala por tier (Cobre 0.05%/0.2% → Oro 0.2%/1.0% Astral/Foil).
  - [x] "Sobre" en cápsulas: check secundario de Foil (5% cobre / 12% plata / 22% oro).
  - [x] Axolotitos normales del pool excluyen Astrales (solo se ganan por legendary drop).
  - [x] El frontend muestra efectos visuales de celebración masiva: `LegendaryOverlay` con 60 partículas flotantes (temáticas: cósmicas para Astral, doradas para Foil), ring burst, flash blanco inicial, banner "¡PREMIO MÍTICO!" y `ResultCard` especializado por tipo (fondo cósmico violeta / dorado). Implementado en `Gashapon.tsx`.

### 2. Definición y Uso de las Estadísticas (Stats) del Axolotito
*Se requiere dar utilidad formal a cada estadística en las mecánicas para consolidar el diseño del juego. Actualmente, solo Focus, Luck y Stamina tienen impacto real.*

**Estado actual en el código:**
*   **Focus**: Reduce la probabilidad de fallar el marcado de casillas en lotería (`miss_chance = (100 - Focus) * 0.003` en `multiplayer_service.py`).
*   **Luck**: Aumenta el premio de GAL recibido al ganar una línea o tabla en lotería (`luck_bonus = (Luck / 1000) * win_prize` en `multiplayer_service.py`).
*   **Stamina**: Define la energía máxima del Axolotito (por defecto 100, configurable dinámicamente).

**Tareas pendientes para implementar las demás stats:**
- [x] **Charisma (Descuentos en Tienda)**:
  - `shop_service.py`: al comprar `CONSUMABLE`, aplica descuento = `min(10%, stat_charisma * 0.1%)` usando el Axolotito Principal del usuario.
- [x] **Agility (Optimización de Tiempos)**:
  - `game.py` y `multiplayer.py`: `sleep_expires_at` reducido con `agility_factor = max(0.5, 1.0 - stat_agility/200)` (hasta -50% tiempo).
- [x] **Wisdom (Yield de Staking / Sinergia)**:
  - `board.py:get_board_hourly_rate`: multiplica la tasa horaria por `1 + stat_wisdom/1000` del Axolotito Principal del dueño (hasta +10% con wisdom=100).
- [x] **Strength (Resistencia al Criadero)**:
  - `incubation.py`: stat distributions mejoradas al eclosionar; Webito Astral obtiene baseline elite (45-85 en todas las stats, salinity 0-5).
- [x] **Salinity (Factor de Riesgo / Mala Suerte)**:
  - `multiplayer_service.py`: `extra_energy_loss = round(stat_salinity * 0.2)` se resta tras cada partida (0-20 pts extra según salinity).

### 3. Correcciones de UI en Unboxing de Sobres
- [x] **Bug de Badges Cortados**: Añadido `pt-4` al contenedor de grid en `Store.tsx` e `Inventory.tsx` para que los badges `-top-2.5` no queden cortados por `overflow-hidden` del modal exterior.
- [x] **Flujo del Booster Brillante (Foil)**:
  - Modal de compra exitosa detecta `item_type === 'booster'` y muestra UI específica: sobre dorado animado, partículas flotantes, info box y dos botones ("Abrir Ahora" / "Ir al Inventario").
  - Foil tiene degradado amber→fuchsia→purple con `pack-pulse` y doble glow de sombra.
- [x] **Animación de Apertura Foil**: Keyframes `foil-explode` (más dramático) + `golden-ring` (anillo dorado burst). Foil usa 100 partículas con 18 símbolos vs 30 normal. Cartas reveladas usan `card-land` con stagger por índice.

### 4. Mostrar Límite Real en Booster Foil
- [ ] **Stock dinámico**: Actualmente muestra un supply restante absurdo de `999999` debido al placeholder de base de datos.
- [ ] **Implementación**: Modificar endpoints de catálogo para retornar las ventas del mes en curso de Booster Foil, y pintar en la tarjeta de la tienda la leyenda `Quedan: {100 - vendidos_mes} / 100`.

### 5. Expansión del Simulador del Universo (`simulate_universe.py`)
- [ ] **Cobertura del Marketplace P2P**: Agregar simulación de transacciones secundarias en el script de prueba para validar que las transferencias on-chain ERC-721 en Anvil local funcionen coordinadas con la base de datos al listar, rentar y vender tablas y Axolotitos.

### 6. Rediseño Cenote Subacuático 2.5D (El Nido)
*La incubadora sigue pintándose como una cuadrícula plana.*
- [ ] **Canvas de Cenote**: Implementar el fondo de capas superpuestas (rayos de luz, burbujas ascendentes, rocas y cuevas de anidación).
- [ ] **Axolotitos Nadadores**: Renderizar sprites de Axolotitos eclosionados nadando de forma libre en la columna de agua con oscilaciones aleatorias (Keyframes CSS individuales) y tooltips flotantes al hacer hover.
- [ ] **Efectos Térmicos**: Añadir los estados visuales en los nidos (halo naranja cálido para nidos activos, bloque azul gélido para nidos congelados que requieren clicks para descongelar).

---

## 🟡 PRIORIDAD BAJA (Expansiones del GDD y Sistemas de Retención)

### 1. Personalidades de Axolotitos (Genes de Comportamiento)
- [ ] **Lógica en Eclosión**: Asignar al nacer naturalezas como *Metódico* (+Focus, -Stamina), *Suertudo* (+Luck, -Agility) e *Hiperactivo* (recuperación veloz, -Focus) que modifiquen levemente las estadísticas del Axolotito.

### 2. Sistema de Crafteo y Fusión (Card Melter)
- [ ] **Fusión de Duplicados**: Crear endpoint para fundir 5 cartas duplicadas comunes + GAL para obtener 1 carta rara aleatoria, actuando como sumidero inflacionario de cartas y monedas.

### 3. Clima Dinámico y Eventos del Criadero
- [ ] **Inclemencias Climáticas**: Añadir eventos aleatorios en el servidor (como tormentas o heladas) que afecten temporalmente el calor de todos los nidos activos, incentivando el uso de Gotas Anti-Escarcha o Lámparas Infrarrojas.

### 4. Misiones Diarias (Daily Bounties)
- [ ] **Quests Cortas**: Implementar un panel de 3 retos diarios simples (ej. alimentar 2 veces, jugar 3 partidas) para otorgar bonos de GAL y fragmentos cosméticos.

---

## 💡 PROPUESTAS CREATIVAS (Experto Game Designer)

### 1. El Mercado de Cascarones Cósmicos (Cosmic Shell Auction)
- **Concepto**: Al eclosionar un *Webito Astral*, el jugador recibe un ítem coleccionable llamado **Cascarón Cósmico (Cosmic Shell)**.
- **Mecánica**: Los jugadores pueden acumular 5 cascarones y quemarlos en un "Altar del Cenote" para desatar una *Lluvia de Meteoros* global de 1 hora. Durante este evento, la pureza genética mínima de todos los huevos del servidor que eclosionen se eleva en +5%. Esto crea una economía cooperativa muy atractiva para los especuladores.

### 2. Nesting Guilds (El Sistema de Becas Cooperativo)
- **Concepto**: Permitir a los jugadores fundar "Nidos" (Gremios) dentro del juego.
- **Mecánica**: Los jugadores experimentados con tableros y Axolotitos de alto nivel pueden depositarlos en la "Bóveda del Gremio". Los jugadores nuevos pueden tomarlos prestados de forma gratuita para jugar en salas comunes, y el contrato inteligente distribuye de forma automática el 30% de los GAL ganados al gremio y el 70% al becado. Excelente para atraer volumen de usuarios sin fricción de entrada.

### 3. Ink stamping (Cosmética Temporal Foil)
- **Concepto**: Introducir un consumible extremadamente raro en el Gashapón llamado **Tinta Holográfica**.
- **Mecánica**: Permite aplicar un efecto brillante (Foil) temporal de 7 días a cualquier carta común. Durante ese periodo, el tablero que contenga la carta estampada recibe un **+2.5% de boost a su tasa de staking pasivo**. Permite a los F2P probar los beneficios de coleccionismo premium.

### 4. Invasión de Predadores (Climatic Co-op PVE)
- **Concepto**: Eventos de servidor temporales donde "Garzas" o "Carpas" invaden los canales de Xochimilco.
- **Mecánica**: El juego desactiva temporalmente el multijugador PvP convencional por unas horas y abre una sala de "Defensa del Nido". Los jugadores inscribe a sus Axolotitos y unen fuerzas en una lotería cooperativa donde los stats de *Fuerza* y *Sabiduría* mitigan ataques de los predadores. Las recompensas incluyen fragmentos de accesorios exclusivos de supervivencia.
