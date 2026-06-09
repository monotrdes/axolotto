# 🦎 MAESTRO DE PENDIENTES — Ecosistema Axolotto

Este documento consolida y organiza todas las especificaciones, características y planes de desarrollo descritos en los 31 archivos de planificación del proyecto (ahora alojados en la carpeta `docs/`), incluyendo los planes de UX y del PlayMode del frontend. Muestra el estado actual del codebase (backend y frontend) y traza la hoja de ruta en fases lógicas y prioridades, completada con checklists detallados.

---

## 📊 Estado Actual del Proyecto

Al analizar el código del backend, los contratos y la interfaz de usuario en el frontend, identificamos el siguiente estado de implementación:

### ✅ Completado y Sólido en Código
*   **Club VIP (Fase 4 completada)**: Modelos de datos para Axolotito principal (`is_main`), guards de congelamiento por VIP expirado, descuentos y bonus en multijugador (`multiplayer_service.py`) e integración visual completa con marcos VIP CSS y Badges de Corner en el frontend (`VipModal.tsx`).
*   **Utilidad de Estadísticas del Axolotito (Stats)**:
    *   **Focus**: Reduce fallos en marcado de casillas de lotería.
    *   **Charisma**: Aplica hasta un 10% de descuento en la compra de consumibles en la tienda.
    *   **Agility**: Reduce a la mitad el tiempo de enfriamiento (`sleep_expires_at`).
    *   **Wisdom**: Otorga hasta un +10% de rendimiento de staking pasivo de los tableros.
    *   **Strength**: Asegura estadísticas base élite al eclosionar Webitos Astrales.
    *   **Salinity**: Añade costo adicional de energía por partida.
*   **Gashapón y Drop Rates**: Sorteo balanceado con pre-check de legendario, drops de Webitos Astrales (0.1%) y Foil Boosters (0.5%) y animaciones de unboxing neón en frontend (`Gashapon.tsx`).
*   **Tableros NPC (Bots)**: Implementación de bots con tableros reales que gradúan al pool de Gashapón de acuerdo a su experiencia acumulada (`NPC_BOARDS_PLAN.md`).
*   **Seguridad y Robustez**: Mitigaciones para dobles gastos con `SELECT FOR UPDATE`, tabla `ProcessedTransactions` anti-replay, CSPRNG en aleatoriedades, límites anti-sybil para jackpots y cálculo de rachas diarias con base en la zona horaria de Xochimilco (UTC-6).
*   **Estructura Base PlayMode v2 y UI**: Componentes `WizardDots`, `AxoStatusBar` e interfaces de selección de modo, selección de tabla, budget y salas de espera multijugador implementados.
*   **Simplificación de UI en PlayMode**: Selección inline de Axolotitos con despliegue de estadísticas, eliminación de hovers complejos y portales externos flotantes redundantes.

### ❌ Pendiente / Inexistente en Código
*   **Sistema de Retiros (DevEx / Cash-out)**: No hay modelos ni endpoints en backend, ni página en frontend.
*   **Pasarela de Pago Fiat (Mercado Pago)**: Falta la integración del SDK, webhooks de acreditación y botones de pago.
*   **Migración a Base Sepolia**: El juego sigue configurado para correr localmente sobre Anvil (`chainId: 31337`).
*   **Mercado P2P de Cartas y Sobres**: El marketplace secundario solo soporta Axolotitos y Tablas; falta comercio de boosters y cartas individuales.
*   **El Nido Cenote 2.5D**: La vista del criadero e incubadoras sigue siendo una cuadrícula plana; falta el fondo subacuático dinámico y los Axolotitos nadadores 2.5D.
*   **Oponentes Múltiples en el Simulador CPU**: El modo Champion es de 1v5 contra bots, pero la pantalla `CpuSimScreen.tsx` solo renderiza 1 tablero bot. Falta mostrar las 4 tablas CPU adicionales de fondo.
*   **Fichas de Gashapón**: El frontend no lee el conteo de fichas de gashapón del inventario ni permite tirar gratis consumiéndolas.
*   **Automatización de Pruebas y CI/CD**: Falta la configuración de GitHub Actions y tests de interfaz Playwright.

---

## 🗺️ Hoja de Ruta Consolidada por Fases

> [!IMPORTANT]
> Las prioridades se definen como:
> - **🔴 PRIORIDAD ALTA**: Core financiero, Web3 de producción y flujos transaccionales críticos.
> - **🟠 PRIORIDAD MEDIA**: Experiencia de juego, mecánicas de retención e integraciones de interfaz dinámicas.
> - **🟡 PRIORIDAD BAJA**: Sistemas secundarios de progresión y expansiones futuras de gamificación.

---

### 🔴 FASE 1: Migración a Base Sepolia Testnet (Web3 en Staging)
*El ecosistema requiere salir de Anvil local a Base Sepolia para probar integraciones reales como MoonPay sandbox y oráculos de precios.*

- [ ] **Despliegue de Smart Contracts**
    - [ ] Desplegar la suite de los 9 contratos inteligentes a Base Sepolia usando Foundry.
    - [ ] Configurar el archivo `contracts/foundry.toml` agregando el endpoint `base_sepolia`.
- [ ] **Configuraciones de Entorno y Conexión (Backend)**
    - [ ] Configurar `BLOCKCHAIN_MODE = "base_sepolia"` en `.env`.
    - [ ] Configurar la constante `USDC_ADDRESS` para apuntar a la dirección oficial de USDC en Base Sepolia: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`.
    - [ ] Actualizar `rpc_url` y `chain_id` dinámicos en `backend/app/core/config.py` para soportar Base Sepolia (Chain ID `84532`).
- [ ] **Configuraciones de Entorno y Frontend**
    - [ ] Configurar `NEXT_PUBLIC_CHAIN_ID = 84532` y `NEXT_PUBLIC_RPC_URL = "https://sepolia.base.org"` en `frontend/.env.local`.
    - [ ] Modificar `frontend/lib/blockchain.ts` para importar y usar la cadena `baseSepolia` de Viem de manera dinámica.
    - [ ] Actualizar `PrivyProviderWrapper.tsx` configurando `defaultChain: baseSepolia` y `supportedChains: [baseSepolia]`.
- [ ] **Ajustes de UI para Base Sepolia**
    - [ ] Actualizar textos e íconos de la interfaz reemplazando "Plasma" por "Base Sepolia" en `CryptoCheckout.tsx`, `Store.tsx`, `Santuario.tsx`, `Inventory.tsx` y `Criadero.tsx`.
    - [ ] Cambiar enlaces de exploradores de bloques a `https://sepolia.basescan.org/tx/{tx_hash}`.

---

### 🔴 FASE 2: Pasarela de Entrada Fíat (Mercado Pago)
*Es la vía principal para que los jugadores tradicionales sin conocimientos de criptomonedas ingresen fondos (comprando AXG) a través de SPEI, tarjetas de crédito o tiendas OXXO.*

- [ ] **Servicio del SDK de Mercado Pago (Backend)**
    - [ ] Crear el módulo `backend/app/services/mercadopago_service.py` para instanciar el cliente oficial de Mercado Pago.
    - [ ] Definir la tabla de conversión fija MXN ↔ AXG en la configuración (10 AXG = $20 MXN / $1.00 USD).
- [ ] **Endpoints de Compra y Notificación**
    - [ ] Crear `POST /bank/checkout/mercadopago` que genere un link de preferencia de pago dinámico (Checkout Pro de Mercado Pago).
    - [ ] Crear el webhook `POST /bank/webhook/mercadopago` para escuchar eventos del estado de la transacción de Mercado Pago.
    - [ ] Implementar la lógica para acreditar de manera segura e inmediata los AXG al saldo de la cuenta (`Wallet`) del usuario cuando se apruebe el webhook, registrando el movimiento en `TransactionLedger`.
- [ ] **Integración en la Interfaz (Frontend)**
    - [ ] Añadir en `Store.tsx` la opción de pago "Pagar con SPEI / Tarjeta / OXXO" llamando al endpoint de Mercado Pago.
    - [ ] Renderizar el botón con estilos premium integrando la estética de la pasarela y manejando de forma limpia los estados de carga.

---

### 🔴 FASE 3: Sistema de Retiros (DevEx / Cash-out)
*Permite a los jugadores convertir sus ganancias de GAL a AXG y posteriormente a dinero real en sus cuentas bancarias o wallets cripto, reteniendo los impuestos correspondientes.*

- [ ] **Base de Datos y Modelos**
    - [ ] Crear el modelo `WithdrawalRequest` (`user_id`, `amount_axg`, `status`, `net_amount_mxn`, `tax_withheld`, `destination_type`, `destination_address`, `cfdi_uuid`).
    - [ ] Crear la tabla `swap_ledger` para auditar conversiones de saldo entre saldos de juego (GAL) y saldos premium de retiro (AXG).
    - [ ] Crear la tabla `blacklisted_cards` para registrar e inmovilizar cuentas bancarias de usuarios reportados por contracargos o fraude.
    - [ ] Definir balances segregados en tesorería (`crypto_fund_balance` y `fiat_fund_balance`).
- [ ] **Lógica de Retención Fiscal e Integraciones**
    - [ ] Diseñar `backend/app/services/withdrawal_service.py` para procesar las solicitudes.
    - [ ] Implementar retención fiscal del **7% (Régimen de Retención de Premios en México)** del monto bruto antes del desembolso.
    - [ ] Integrar el servicio con Facturapi para emitir el CFDI de Retenciones automáticamente al aprobarse un retiro bancario.
    - [ ] Añadir oráculo Uniswap o fallback manual para conversiones en tiempo real de stablecoins de retiro a moneda local.
    - [ ] Incorporar guard de KYC obligatorio para retiros superiores a $10,000 MXN o cuando los holdings del usuario excedan cierto límite.
- [ ] **Endpoints de Gestión y Panel de Administración**
    - [ ] Crear el endpoint de solicitud `POST /bank/withdraw` (validando cooldown de 7 días entre retiros y un saldo mínimo de retiro de 100 AXG).
    - [ ] Desarrollar rutas de control de administrador `GET/PATCH /admin/withdrawals` para auditar, aprobar o rechazar de manera manual o automatizada las solicitudes de retiro.
- [ ] **Pantalla de Retiro en Frontend (`WithdrawalPage`)**
    - [ ] Diseñar una nueva vista o modal premium de retiros (soporte de cuenta CLABE y de wallet criptográfica).
    - [ ] Mostrar información clara y transparente del 7% de impuestos retenidos, el cobro por swap, y enlaces para descargar los CFDIs PDF/XML una vez completados.

---

### 🟠 FASE 4: Mercado Secundario P2P Completo y Control de Tienda — ✅ COMPLETADO
*Desbloquea el comercio libre entre usuarios de cartas sueltas y boosters sellados (mochila), ampliando las oportunidades de especulación y recolección de regalías.*

- [x] **Actualización de Base de Datos y Endpoints P2P**
    - [x] Extender el modelo `PlayerInventory` y las rutas de mercado para permitir que cartas individuales (`PlayerCard`) y boosters sellados sean listados.
    - [x] Crear endpoints `POST /market/inventory/list` and `POST /market/inventory/buy` que manejen de forma atómica la compra-venta en GAL.
    - [x] Aplicar retención automática del **5% de regalías (casa)** en la compra-venta de boosters y cartas, depositándose directamente a la wallet del Tesoro.
- [x] **Ajustes de UI en Inventario y Tienda**
    - [x] Actualizar `Inventory.tsx` y `MarketP2P.tsx` para listar las cartas y boosters con filtros de rareza, brillantes (Foil) e históricos de transacciones.
    - [x] Reemplazar el stock fijo dummy de `999999` en la tienda del frontend para el Booster Foil, mostrando dinámicamente el límite real de la temporada mensual (`Quedan {100 - vendidos_mes} / 100`).

---

### 🟠 FASE 5: El Nido Cenote 2.5D e Interfaz del Simulador
*Transforma la actual cuadrícula plana del Criadero en un cenote subacuático 2.5D interactivo y pule la visualización competitiva en el simulador de partidas contra bots.*

- [ ] **Estructura del Canvas y Capas Visuales (Criadero)**
    - [ ] Modificar `Criadero.tsx` y `Santuario.tsx` implementando un canvas estructurado en capas CSS (rayos de luz difuminados, burbujas dinámicas ascendentes y cuevas como habitaciones).
    - [ ] Desarrollar keyframes CSS de nado para que los Axolotitos eclosionados naveguen de forma orgánica por el canvas subacuático, con hovers y tooltips informativos.
    - [ ] Agregar capas de renderizado térmico en las incubadoras: halo animado naranja (nido activo) y bloque de hielo traslúcido azul (congelado por expiración VIP).
- [ ] **Oponentes Múltiples en el Simulador CPU**
    - [ ] En `CpuSimScreen.tsx` para partidas Champion (1v5), renderizar las 5 tablas CPU del oponente flotando al fondo en escala reducida y con efecto blur para dar la sensación visual de "estar rodeado" por la mesa.
- [ ] **Micro-detalles y Ajustes del Simulador**
    - [ ] Incrementar el delay del frame de carta cantada (`CalledCard`) en el simulador CPU a 1.2s para una lectura más cómoda (actualmente corre a 800ms).
    - [ ] Implementar la advertencia flotante `"⚠️ CPU cerca..."` en `CpuSimScreen.tsx` cuando un bot alcance el 70% de llenado de su tabla.
    - [ ] Agregar el listener `popstate` de Window en el frontend para sincronizar la navegación con el botón físico/atrás del sistema y evitar perder el estado del wizard del PlayMode.

---

### 🟠 FASE 6: Pruebas, Cobertura y CI/CD
*Configurar el marco técnico que garantice la robustez de la economía y la estabilidad de la interfaz responsive.*

- [ ] **QA Visual y Responsivo de la Interfaz (Viewports)**
    - [ ] Verificar el comportamiento visual del wizard y todas las pantallas de juego en viewports de móvil (375px) y escritorio (1280px).
    - [ ] Asegurar que ningún popup, modal o componente unificado de `BottomSheet.tsx` y `ToastContext.tsx` desborde, requiera scroll horizontal o rompa el layout.
- [ ] **Configuración del Pipeline de Integración Continua (CI)**
    - [ ] Crear el directorio `.github/workflows/` y configurar el archivo de pipeline `ci.yml`.
    - [ ] Configurar el job del backend para correr la suite de pruebas unitarias (`pytest`) sobre SQLite y testear contratos con Foundry (`forge test`).
    - [ ] Añadir bandera de cobertura de código (`pytest-cov`) con fallo si cae por debajo del **70%** en servicios clave (`shop_service`, `bank_service`, `multiplayer_service`).
- [ ] **Automatización de Pruebas E2E de Frontend**
    - [ ] Instalar Playwright en `frontend/` y diseñar `playwright.config.ts`.
    - [ ] Escribir tests automatizados para validar la robustez ante latencias elevadas, clicks rápidos repetitivos (double-submit) y tolerancia ante caídas de la API (error 500).

---

### 🟡 FASE 7: Mecánicas de Retención y Gamificación Futura (Ver [00_PLAN_GAMIFICACION.md](file:///home/monotr/axolotto/docs/00_PLAN_GAMIFICACION.md))
*Mecánicas secundarias e incentivos del GDD que profundizan la economía y mejoran la retención diaria a mediano plazo.*

- [ ] **Implementación Completa de Fichas de Gashapón**
    - [ ] Leer del inventario del usuario las `"Ficha de Gashapón"` poseídas.
    - [ ] Mostrar un contador destacado `🎟️ Fichas: X` en el header de Gashapón en el frontend.
    - [ ] Habilitar botones de acción en `Gashapon.tsx` para realizar tiradas gratuitas consumiendo 1 Ficha de Gashapón en lugar de GAL.
- [ ] **Personalidades y Genes de Comportamiento**
    - [ ] Modificar la lógica de eclosión de huevos (`incubation.py`) para inyectar naturalezas del Axolotito (*Metódico*, *Hiperactivo*, *Suertudo*) que aplican modificadores ligeros a sus estadísticas base.
- [ ] **Sistema de Crafteo y Fundición de Cartas (Card Melter)**
    - [ ] Crear el endpoint en backend para fusionar 5 cartas comunes duplicadas más una cuota en GAL para fabricar 1 carta rara aleatoria (actuando como sumidero inflacionario de cartas en la economía).
- [x] **Desarmado Seguro de Tablas (Solvente de Pegamento)**
    - [x] Implementar la función de desarmado seguro (recuperación 16/16 cartas) cobrando 120 GAL en backend y actualizando frontend/smart-contracts.
- [ ] **Clima Dinámico e Inclemencias en el Criadero**
    - [ ] Diseñar tareas programadas (Crons) que modifiquen el clima del servidor (heladas/tormentas), obligando a los usuarios a aplicar Lámparas Infrarrojas o Gotas Anti-Escarcha a sus nidos.
- [ ] **Misiones Diarias (Daily Bounties)**
    - [ ] Diseñar el panel de misiones diarias (retos simples como alimentar 2 veces o jugar 3 partidas) recompensando con fragmentos cosméticos y GAL extras.

---

## 💡 Propuestas de Diseño del Experto Game Designer

A continuación se listan mecánicas altamente interactivas sugeridas en los reportes de diseño para consolidar a Axolotto como un referente del sector:

1.  **El Mercado de Cascarones Cósmicos (Cosmic Shell Auction)**
    *   *Mecánica*: Al eclosionar un *Webito Astral*, el jugador obtiene un **Cosmic Shell**. Juntando 5 e incinerándolos en el altar, el servidor activa una *Lluvia de Meteoros* por 1 hora, elevando en +5% la pureza genética mínima de todos los huevos que nazcan globalmente en ese intervalo. Fomenta el cooperativismo y la especulación de alto nivel.
2.  **Nesting Guilds (Beca / Scholarship)**
    *   *Mecánica*: Jugadores avanzados pueden depositar sus Axolotitos y Tablas de nivel alto en una "Bóveda de Gremio". Jugadores F2P (nuevos) los toman prestados gratis para competir, y el contrato inteligente reparte automáticamente el **30% de los GAL ganados al dueño / gremio y el 70% al becado**. Remueve barreras de entrada Web3.
3.  **Ink Stamping (Holografía Temporal Foil)**
    *   *Mecánica*: Un consumible llamado **Tinta Holográfica** (obtenible en el Gashapón) aplica un efecto brillante (Foil) temporal por 7 días a cualquier carta común. Durante este lapso, el tablero que contenga la carta recibe un **+2.5% de boost a su tasa de staking pasivo**, permitiendo probar la estética premium.
4.  **Invasión de Predadores (PvE Cooperativo)**
    *   *Mecánica*: Evento aleatorio global donde garzas o carpas invaden los canales de Xochimilco. El juego detiene el PvP tradicional para abrir el lobby "Defensa del Nido", donde se inscriben los Axolotitos y se unen fuerzas en una lotería PvE cooperativa. Las estadísticas de *Strength* y *Wisdom* mitigan ataques de los predadores.
