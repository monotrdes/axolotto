# Auditoría y Medidas de Seguridad de Axolotto

Este documento describe detalladamente el diseño defensivo y las medidas de mitigación de vulnerabilidades implementadas en el backend y los contratos inteligentes de Axolotto. El objetivo es garantizar un entorno de juego "irrompible", libre de dobles gastos, ataques de replay, manipulación de azar o abusos en la economía interna.

---

## 1. Concurrencia y Prevención de Dobles Gastos (§4.1)

### Vulnerabilidad potencial
Un usuario malintencionado podría realizar peticiones paralelas masivas (ej. 10 peticiones simultáneas) para consumir un mismo recurso (como abrir un único sobre booster o gastar un saldo que no tiene).

### Mitigación
- **Bloqueo Pesimista (`SELECT FOR UPDATE`):** Antes de procesar cualquier transacción que afecte el inventario (`PlayerInventory`) o el saldo (`Wallet`), el servicio de backend realiza una consulta bloqueante usando `with_for_update()`.
- **Lógica Transaccional Atómica:** Las operaciones se ejecutan dentro de bloques transaccionales cerrados. Si una petición adquiere el bloqueo, reduce la cantidad de stock a 0 o descuenta el saldo antes de liberar la fila. Las peticiones concurrentes restantes leen el nuevo estado (`quantity=0` o saldo insuficiente) y son rechazadas con HTTP 400/402.
- **Áreas Protegidas:**
  - Apertura de boosters en la tienda (`open_booster`).
  - Uso de consumibles en incubaciones (`buy_and_use_consumable`).
  - Interacciones pagadas con el huevo (`interact_with_egg`).
  - Creación de tableros aleatorios y manuales.
  - Compras y arriendos en el mercado secundario.
  - Desbloqueo de ranuras de tableros y registros en multijugador (`join_lobby`).
  - Giros del Gashapón y cápsulas de la suerte.

---

## 2. Prevención de Ataques de Replay de Blockchain (§4.2)

### Vulnerabilidad potencial
Un atacante podría interceptar un hash de transacción (`tx_hash`) válido de USDC en la red y reenviarlo al endpoint `/shop/buy` propio o de otro usuario para reclamar gemas gratis de forma ilimitada (Double-Spending / Replay).

### Mitigación
1. **Modelo `ProcessedTransaction`:** Tabla dedicada en la base de datos con un índice único y estricto (`UNIQUE`) a nivel de base de datos en la columna `tx_hash`.
2. **Defensa Multicapa en el Backend (`checkout_service.py`):**
   - **Capa 1 (Lookup rápido):** Antes de interactuar con la blockchain, el backend comprueba si el `tx_hash` existe en `ProcessedTransaction`. Si existe, se aborta inmediatamente con un código HTTP 409.
   - **Capa 2 (Integridad de la Orden):** Comprobación en `CryptoPurchaseOrder` para asegurar que el hash no esté asociado a órdenes previas.
   - **Capa 3 (Atomicidad en BD):** El registro en `ProcessedTransaction` y el cambio de estado de la orden a `CONFIRMING` se realizan en la misma transacción atómica. Si ocurriese una carrera concurrente extrema que supere los lookups previos, el constraint `UNIQUE` de la BD generará una violación de unicidad, abortando el segundo intento con HTTP 409.
3. **Validación del Emisor On-chain:** El servicio verifica on-chain que el `from` (remitente) de la transacción del token USDC coincida exactamente con la dirección de la billetera (`wallet_address`) del usuario autenticado en Axolotto. Si el sender es diferente o inválido, la orden se marca como `FAILED` y se responde con HTTP 422.

---

## 3. Aleatoriedad Criptográficamente Segura (§4.3)

### Vulnerabilidad potencial
Si la aleatoriedad es generada en el frontend o utiliza generadores de números pseudoaleatorios (PRNG) predecibles en el backend (sembrados con marcas de tiempo simples), los atacantes podrían adivinar qué cartas obtendrán o manipular el resultado del juego.

### Mitigación
- **Azar 100% en Backend:** Toda la lógica de probabilidad se calcula en servidores de confianza. El cliente solo recibe y renderiza los resultados.
- **Uso de CSPRNG:** Se utiliza la clase `random.SystemRandom` (y `secrets.SystemRandom`) en todos los puntos críticos del código. Esta implementación obtiene entropía segura directamente del sistema operativo (`/dev/urandom`), impidiendo cualquier predicción de semillas.
- **Casos de Uso:**
  - Selección de cartas y estados *shiny* al abrir boosters (`shop_service.py`).
  - Drops y premios de Gashapón y giros de cápsulas (`shop.py`).
  - Generación de estadísticas base de axolotitos al eclosionar (`incubation.py`).
  - Efectos del clima sobre los huevos y consumo de energía.
  - Sorteo de cartas y barajas en partidas multijugador (`multiplayer_service.py`).

---

## 4. Invariabilidad del Tiempo y Cooldowns del Servidor (§4.4 y §4.7)

### Vulnerabilidad potencial
Adelantar el reloj del sistema operativo local en el cliente para saltar los tiempos de espera (cooldowns) de alimentación, canto del huevo o reclamos VIP.

### Mitigación
- **Validación del Lado del Servidor:** Los cooldowns de interacciones con el huevo y recuperación de energía de axolotitos se calculan usando `datetime.utcnow()` del servidor. El backend nunca confía en marcas de tiempo enviadas por el frontend.
- **Huso Horario Controlado:** Para evitar que los usuarios cambien su cabecera de lenguaje o su IP para simular un cambio de zona horaria y reiniciar rachas diarias antes de tiempo, los reclamos VIP y la cápsula gratuita calculan el cambio de día en la zona horaria del santuario: **Xochimilco (`America/Mexico_City`, UTC-6)**.
- **Registro Persistente:** Se utiliza el campo `vip_last_daily_gal_at` en el registro del usuario para bloquear múltiples reclamos en un mismo día del huso horario de referencia.

---

## 5. Escrow de Partidas y Retiros Controlados (§4.5)

### Vulnerabilidad potencial
Un jugador ingresa a una partida multijugador apostando su Axolotito y fondos, y al ver que está perdiendo, intenta retirar de inmediato el Axolotito o los fondos de la plataforma (Bypass de Escrow).

### Mitigación
- **Restricción por Estado del Lobby:** El endpoint `/recall` (retiro/recuperación) del axolotito inspecciona el estado de la sala (`GameRoom`).
- **Retiro Permitido:** Solo se procesa el retiro inmediato si la sala está en estado de espera (`waiting`). El Axolotito se desvincula de inmediato y el escrow es reembolsado de forma segura.
- **Bloqueo en Juego:** Si la sala ha cambiado a estado de juego (`in_progress` o `finished`), el retiro inmediato se rechaza. En su lugar, el sistema marca `wants_to_stop = True`.
- **Liquidación en Settle:** El scheduler del backend (`simulate_multiplayer_match`) lee el estado y, tras resolver y liquidar la partida de manera atómica, procesa el retiro del Axolotito de forma justa según el resultado.

---

## 6. Lucha contra Ataques Sybil e Inflado de Jackpot (§4.6)

### Vulnerabilidad potencial
Un atacante crea decenas de cuentas fantasmas controladas por él mismo y las registra en una partida multijugador usando la misma wallet o wallets secundarias. Esto le permitiría "inflar" artificialmente la cuota acumulada del Jackpot de la sala de espera y asegurar una victoria para su cuenta principal.

### Mitigación
1. **Unicidad de Billeteras:** La columna `wallet_address` en la tabla `User` posee una restricción `UNIQUE` estricta. Ningún usuario puede vincular una billetera que ya esté asociada a otra cuenta (`privy_did`).
2. **Límite de Registros Concurrentes:** El backend limita a **1 Axolotito** por `user_id` en salas del mismo tipo en espera, evitando el autollenado.
3. **Límite por Dirección de Wallet:** Búsqueda cruzada durante el registro para evitar que múltiples usuarios que de alguna forma compartan o controlen la misma billetera física puedan registrar más de un Axolotito.
4. **Límite de Tablas por Wallet:** Máximo de 5 tablas por billetera en una misma sala.
5. **Cómputo Seguro de Elegibilidad de Jackpot (`jackpot_eligible`):**
   - El jackpot solo se activa si hay **al menos 2 billeteras humanas distintas** registradas en la partida.
   - Las billeteras se guardan y comparan aplicando `.lower()` (insensibilidad a mayúsculas/minúsculas).
   - Usuarios sin billetera definida (`None`) se omiten del conteo para evitar bypasses de elegibilidad.

---

## 7. Control del Programador (Scheduler) Multijugador (§4.8)

### Vulnerabilidad potencial
Un usuario intenta predecir o sesgar la secuencia de cartas sorteadas en la lotería al inundar el scheduler.

### Mitigación
- **Validación del Flujo de Registro:** Prevención de colisiones por billetera.
- **Barajado Seguro:** El scheduler baraja las cartas del sorteo usando exclusivamente `random.SystemRandom()`. Cada carta se extrae con una distribución probabilística independiente no manipulable.

---

## 8. Seguridad en Contratos Inteligentes (Foundry)

Para mitigar riesgos on-chain en Plasma/Anvil:
- **GameController como Única Puerta de Entrada:** Los tokens ERC-20 (`GemaAlga` y `Axogema`) restringen sus funciones `mint` y `burn` al GameController mediante el modificador `onlyController`. El jugador no puede acuñarse tokens directamente.
- **Pruebas de Fuzzing Automatizadas:** Se ejecutan pruebas de fuzzing (`testFuzz_TransferGAL` y `testFuzz_TransferAXG`) en Foundry enviando transacciones con direcciones aleatorias y montos arbitrarios (hasta 1,000,000,000 tokens) para asegurar que no ocurran subdesbordamientos (*underflows*) ni desbordamientos (*overflows*) de balance y que las restricciones de seguridad del contrato se mantengan robustas bajo cualquier escenario.
