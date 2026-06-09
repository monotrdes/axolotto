# Plan de Implementación: Pruebas, Simulación y Robustez (Irrompible)

Este plan detalla la estrategia de pruebas, simulación con volumen/ruido y mitigación de vulnerabilidades para hacer el sistema "irrompible". Está alineado con el stack real del proyecto: **FastAPI + SQLModel + PostgreSQL + Web3 (Plasma/Anvil) + Next.js**.

---

## 0. Setup del Entorno de Pruebas

### 0.1. Estructura de Directorios
```
backend/tests/
├── conftest.py              # fixtures globales: DB en memoria, cliente HTTP, usuarios mock
├── unit/
│   ├── test_shop_service.py
│   ├── test_gashapon_rates.py
│   ├── test_inventory.py
│   ├── test_bank_service.py
│   ├── test_vip_system.py
│   └── test_multiplayer_service.py
├── integration/
│   ├── test_concurrency_race_conditions.py
│   ├── test_replay_attacks.py
│   ├── test_blockchain_desync.py
│   ├── test_escrow_integrity.py
│   └── test_jackpot_vault.py
└── simulation/
    ├── simulate_high_volume_traffic.py
    ├── generate_noise_data.py
    └── simulate_degraded_network.py
```

### 0.2. Dependencias Necesarias
- **Checklist de Cambios (Completado):**
  - [x] Instalar dependencias de pruebas unitarias (`pytest`, `pytest-asyncio`, `pytest-xdist`, `httpx`).
  - [x] Instalar dependencias de simulación y stress (`locust`, `faker`).
  - [x] Agregar las librerías al entorno virtual local `.venv`.

### 0.3. Base de Datos de Prueba
- Usar SQLite en memoria para unit tests (rápidos, sin estado).
- Usar PostgreSQL con transacciones que hacen rollback al finalizar cada test de integración (sin contaminar datos).
- Nunca usar la BD de producción ni la testnet Plasma en tests automáticos.

---

## 1. Pruebas Unitarias de Flujos Críticos

### 1.1. `test_shop_service.py`
- Compra de booster/webito con saldo insuficiente → debe lanzar `HTTPException 402`.
- Compra exitosa: verificar descuento correcto de USDC en `TransactionLedger` y adición al inventario.
- Compra de ítem inactivo (`is_active=False`) → debe rechazarse.
- Verificar que el campo `total_sold` en `/shop/items` es consistente con las entradas en `TransactionLedger`.

### 1.2. `test_gashapon_rates.py`
- Simular 100,000 tiradas y validar estadísticamente que:
  - Webito Astral (0.1%) cae entre 80–120 veces (IC 95%).
  - Booster Brillante (0.5%) cae entre 450–550 veces (IC 95%).
- Verificar que la entropía viene de `secrets` del servidor, no de `random` (buscar en código).
- Validar que el sistema de **pity** (`CapsulaPity`) reseta correctamente tras un drop épico/legendario.

### 1.3. `test_inventory.py`
- Intentar abrir un booster con `quantity=0` → rechazo.
- Apertura simultánea del mismo booster: solo una debe decrementar a 1 y la segunda ver `quantity=0`.
- Verificar que no se generan entradas duplicadas en `PlayerInventory` para el mismo `(user_id, item_id)`.

### 1.4. `test_bank_service.py`
- `get_or_create_wallet`: creación idempotente — llamarlo dos veces para el mismo `user_id` no duplica wallets.
- Transferencia con saldo insuficiente → rollback completo, ninguna wallet queda modificada.
- Transferencia exitosa → verificar exactitud numérica (sin pérdida de centavos por floating point).
- Depósito negativo o cero → rechazo antes de tocar la BD.

### 1.5. `test_vip_system.py` *(nuevo — cubre commits recientes)*
- **Welcome gift**: activar VIP por primera vez genera exactamente un toast/notificación de regalo, no más.
- **Auto-renovación**: simular que el VIP expira y verificar que el scheduler lo renueva solo si hay saldo suficiente; si no hay, marca como expirado sin cobrar.
- **Racha (streak)**: días consecutivos sin romper la racha incrementan correctamente; un día de salto la resetea.
- **Filtro de upgrade**: verificar que el endpoint de tienda filtra correctamente ítems según nivel VIP del usuario.

### 1.6. `test_multiplayer_service.py`
- `get_or_create_waiting_room`: dos usuarios con `boards_count` que sumen ≤30 van a la misma sala.
- Verificar que `WINNING_LINES` y `WINNING_CUADRITOS` no tienen duplicados y cubren todos los patrones esperados.
- `check_line` / `check_cuadrito`: casos borde — tablero vacío, tablero lleno, exactamente una línea.

---

## 2. Pruebas de Integración y Stress (Resiliencia a Exploits)

### 2.1. `test_concurrency_race_conditions.py`
**Apertura de booster duplicado:**
```python
# 10 requests simultáneos al mismo booster con quantity=1
# Solo 1 debe retornar 200; los demás deben retornar 409 o 400
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(client.post, "/shop/booster/open", ...) for _ in range(10)]
results = [f.result() for f in futures]
assert sum(1 for r in results if r.status_code == 200) == 1
```
- Requiere `SELECT FOR UPDATE` en el registro de `PlayerInventory`.

**Registro simultáneo al mismo lobby:**
- Dos usuarios intentan ocupar el último hueco de una sala al mismo tiempo.
- Verificar que la capacidad de 30 tablas nunca se excede.
- **Checklist de Cambios (Completado):**
  - [x] Agregar `with_for_update()` en la consulta de salas activas en `get_or_create_waiting_room` para bloquear los registros de salas durante la asignación/creación concurrente.
  - [x] Garantizar que peticiones simultáneas esperen la finalización de la transacción actual para evitar que la capacidad de 30 tablas sea superada.

**Double-spend de Gal/Axogemas:**
- Enviar dos transferencias simultáneas que juntas excedan el saldo disponible.
- Solo una debe completarse; la otra debe fallar con 402 o 400.
- **Checklist de Cambios (Completado):**
  - [x] Agregar `for_update=True` a todos los flujos de consumo de saldo (GAL/AXG) en `BankService.get_or_create_wallet`.
  - [x] Proteger el flujo de compra y uso de consumibles en incubaciones (`buy_and_use_consumable`).
  - [x] Proteger las interacciones pagadas con el huevo (`interact_with_egg`).
  - [x] Proteger la creación de tableros aleatoria (`create_random_board`) y manual (`build_board`).
  - [x] Proteger las compras (`buy_board`) y arriendos (`rent_board`) en el mercado secundario bloqueando de forma pesimista tanto la cartera del comprador/arrendatario como la del vendedor/propietario.
  - [x] Proteger el desbloqueo de slots de tablero adicionales (`unlock_board_slot`).
  - [x] Proteger la entrada a partidas multijugador (`join_lobby`) y la alimentación/recuperación de energía de axolotitos (`feed_axolotito`).
  - [x] Proteger los lanzamientos comunes y premium del Gashapón (`roll_gashapon`).
  - [x] Proteger los giros de cápsulas individuales (`roll_capsule`) y de triple suerte (`roll_triple_suerte`).
  - [x] Proteger las compras de pases VIP directas (`buy_item` -> `_handle_vip_purchase`) y las auto-renovaciones en segundo plano (`vip_scheduler.py`).

### 2.2. `test_replay_attacks.py`
- Reutilizar un `tx_hash` ya procesado en `/shop/buy` → debe retornar error inmediato.
- Usar el `tx_hash` de otro usuario para reclamar fondos propios → debe fallar validación de `sender`.
- Tabla `ProcessedTransactions` debe tener índice único en `tx_hash` a nivel de BD (no solo lógica de aplicación).

### 2.3. `test_blockchain_desync.py`
- Mockear `Web3Service` para que falle **después** de registrar la transacción en BD pero **antes** de confirmarla on-chain.
- Verificar que el estado queda en "pending" o se hace rollback — nunca en estado inconsistente.
- Simular timeout de nodo RPC: la operación debe reintentar con backoff exponencial o devolver error limpio al usuario.
- Verificar que cambiar `BLOCKCHAIN_MODE` de `local` a `plasma` en `.env` no rompe ningún test de integración (el mock debe ser agnóstico al modo).

### 2.4. `test_escrow_integrity.py` *(nuevo)*
- Registrar un axolotito en partida → verificar que el escrow se retiene en `TreasuryVault`.
- Intentar retirar el axolotito mientras la partida está `in_progress` → debe rechazarse.
- Simular cancelación de sala → verificar que todos los escrows se devuelven sin pérdida.
- Simular victoria: el ganador recibe el premio y el `JackpotVault` se actualiza correctamente.

### 2.5. `test_jackpot_vault.py` *(nuevo)*
- Verificar que el jackpot acumula el porcentaje correcto de cada entrada (no más, no menos).
- Simular múltiples partidas consecutivas: el jackpot no se resetea entre partidas normales, solo al pagarlo.
- Intento de doble-pago del jackpot: solo un ganador puede reclamarlo por ciclo.

---

## 3. Simulación y Generación de Ruido (Robustez)

### 3.1. `simulate_high_volume_traffic.py`
- Simular miles de usuarios concurrentes con **Locust** (más robusto que scripts manuales):
  ```python
  class AxolottoUser(HttpUser):
      wait_time = between(0.1, 2)
      tasks = [BuyBooster, OpenBooster, SpinGashapon, RegisterToLobby]
  ```
- Métricas a capturar: p50/p95/p99 de latencia, tasa de errores, conexiones activas a PostgreSQL.
- Umbral de aceptación: p95 < 500ms bajo 500 usuarios concurrentes.
- **Checklist de Cambios (Completado):**
  - [x] Crear directorio `tests/simulation/` con `__init__.py`.
  - [x] Implementar `AxolottoReadUser` (peso 2, 0.5–3 s): tareas `GET /shop/items`, `GET /multiplayer/jackpot`, `GET /shop/activity`, `GET /capsule/daily-status`. Sin autenticación.
  - [x] Implementar `AxolottoUser` (peso 3, 0.1–2 s): mezcla 2:3 de lectura y escritura; `on_start` hace `POST /auth/sync` para crear wallet; tareas cubren `buy`, `open_booster`, `gashapon/roll`, `capsule/daily-claim`, `multiplayer/lobby`.
  - [x] Implementar `AxolottoHeavyUser` (peso 1, 0.05–0.5 s): whale/VIP con ráfagas de escritura intensiva.
  - [x] Auth en modo dev vía query param `?user_id=` (compatible con `PRIVY_APP_ID` no configurado).
  - [x] Hook `@events.quitting`: imprime resumen p50/p95/p99, tasa de error; devuelve exit code 1 si `p95 > 500 ms` o `error_rate > 5%`.
  - [x] Códigos 400/402/404/409/422 tratados como éxitos de lógica de negocio, no fallos de infraestructura.
  - [x] Instrucciones de ejecución documentadas en docstring del archivo.

### 3.2. `generate_noise_data.py`
Enviar datos inesperados a todos los endpoints críticos:
- Payloads incompletos o malformados (campos faltantes, tipos incorrectos).
- IDs de usuario/carta/ítem inexistentes (`user_id="' OR 1=1 --"`).
- Valores fuera de rango: cantidad negativa, booster `item_id=0`, `budget_gal=-999`.
- Firmas Web3 corruptas o `tx_hash` con formato inválido (`"0xZZZZ"`).
- Peticiones sin token de autenticación, con token expirado, con token de otro usuario.
- Caracteres Unicode extremos en campos de texto (`\x00`, emojis de 4 bytes, strings de 10,000 chars).

### 3.3. `simulate_degraded_network.py`
- Agregar latencia simulada (100ms–5s) y desconexiones aleatorias a nivel de mock de `Web3Service`.
- Verificar que el cliente frontend maneja correctamente los estados: loader activo → timeout → mensaje de error.
- Comprobar que no se generan peticiones duplicadas por doble-click o doble-submit en botones del frontend.
- Verificar que los botones de acción se deshabilitan mientras hay una petición en vuelo (`isLoading` state).
- **Checklist de Implementación y Simulación (Completado — 8/8 ✅):**
  - [x] **[A]** Latencia de red baja (100ms) manejada de forma consistente en la base de datos tras la quema de boosters.
  - [x] **[B]** Latencia extrema (2s) y fallos en RPC tolerados de forma segura durante la quema on-chain.
  - [x] **[C]** Reversión/Rollback limpio de saldos ante excepciones de timeout en depósitos de AXG.
  - [x] **[D]** Sin estados parciales inconsistentes ante desconexiones RPC aleatorias en compras de ítems.
  - [x] **[E]** Mitigación de doble-submit concurrente para apertura de boosters (1 unidad, 10 hilos).
  - [x] **[F]** Control de race conditions con latencia en blockchain para solicitudes concurrentes.
  - [x] **[G]** Recuperación y persistencia de saldo tras una caída del nodo RPC seguida de un intento exitoso.
  - [x] **[H]** Comportamiento correcto en cascada (compra lenta y apertura) bajo latencia acumulada.
- **Checklist de Cambios (Completado):**
  - [x] **[A] Latencia baja (100 ms)**: `open_booster` completa correctamente y consume exactamente 1 booster del inventario.
  - [x] **[B] Latencia alta (2 s) en burn onchain**: `open_booster` tolera el retraso gracias a `try/except`; entrega cartas igualmente.
  - [x] **[B2] Fallo total en burn**: excepción en `burn_booster_onchain` no impide la apertura del sobre.
  - [x] **[C] Timeout en llamada crítica** (`transferir_axogemas`): `admin_deposit` retorna HTTP 500 y la BD queda intacta (saldo = 0).
  - [x] **[D] Desconexión intermitente (80% fallo)**: `buy_item` nunca deja estado parcial; saldo final coincide exactamente con operaciones exitosas × precio.
  - [x] **[E/F] Double-submit concurrente**: 10 hilos sobre 1 booster con `quantity=1` → exactamente 1 éxito (requiere PostgreSQL; `SKIP` en SQLite con mensaje claro).
  - [x] **[G] Recuperación**: fallo blockchain → HTTP 500 sin tocar BD; siguiente intento exitoso → saldo actualizado correctamente.
  - [x] **[H] Cascada buy → open con latencia 200 ms**: saldo debitado correcto (-10 AXG), inventario consumido, cartas entregadas.
  - [x] Checks de frontend documentados en docstring del archivo (manuales — requieren Playwright para automatización).

---

## 4. Puntos de Vulnerabilidad y Cómo Evitar "Chamaqueos"

### 4.1. Duplicación de Aperturas (Race Conditions)
- **Ataque**: El usuario envía 10 peticiones `/shop/booster/open` simultáneas con un solo sobre.
- **Solución**: `SELECT FOR UPDATE` en `PlayerInventory` antes de cualquier decremento. Nivel de aislamiento `SERIALIZABLE` en transacciones críticas.
- **Checklist de Cambios (Completado):**
  - [x] Implementar el endpoint diferido `POST /shop/booster/open` en `app/api/v1/endpoints/shop.py`.
  - [x] Bloquear de forma pesimista el registro del inventario (`PlayerInventory`) del booster en `ShopService.open_booster` mediante `with_for_update()`.
  - [x] Reducir correctamente el stock de sobres y eliminar el registro si llega a cero para evitar dobles aperturas simultáneas.
  - [x] Crear el método de quema de boosters `burn_booster_onchain` en `Web3Service` y realizar el acuñado de cartas on-chain correspondientes.

### 4.2. Robo o Reuso de Hash de Transacción
- **Ataque**: Tomar un `tx_hash` de USDC exitoso de otro jugador y enviarlo al propio endpoint.
- **Solución**: Verificar que `sender` de la transacción USDC coincide exactamente con el address del `user_id` solicitante. Tabla `ProcessedTransactions` con índice `UNIQUE` en `tx_hash`.
- **Checklist de Implementación (Completado):**
  - [x] **Modelo `ProcessedTransaction`** (`app/models/economy.py`): tabla con campos `tx_hash` (UNIQUE + índice), `user_id`, `purpose` y `created_at`. Sirve como registro de auditoría y barrera de replay.
  - [x] **Migración Alembic** (`alembic/versions/a1b2c3d4e5f6_add_processed_transactions.py`): crea la tabla y el índice `UNIQUE` en `tx_hash` en la BD.
  - [x] **Capa 1 – Lookup rápido** (`checkout_service.py` → `confirm_payment`): antes de tocar la blockchain, buscar en `ProcessedTransaction` si el `tx_hash` ya fue procesado. Retorna HTTP 409 de inmediato sin consumir RPC call.
  - [x] **Capa 2 – Guard en `CryptoPurchaseOrder`** (`checkout_service.py`): verificar si el `tx_hash_payment` ya está asignado en alguna orden previa (cubre el caso de crash entre el commit de la orden y el de `ProcessedTransaction`). Retorna HTTP 409.
  - [x] **Registro atómico con barrera de BD** (`checkout_service.py`): insertar `ProcessedTransaction` y actualizar la orden a `CONFIRMING` en el mismo commit. Si dos requests concurrentes superan ambos lookups, el `UNIQUE` constraint de PostgreSQL rechaza el segundo con excepción capturada → HTTP 409.
  - [x] **Verificación on-chain de remitente** (`web3_service.py` → `verify_usdc_payment`): inspecciona los logs de la transacción USDC. Si `from_addr != expected_sender` (wallet del usuario en BD), el log se descarta. Si ningún log válido supera el monto mínimo, retorna `False` → la orden pasa a `FAILED` y responde HTTP 422.
  - [x] **Campo `purpose` en `ProcessedTransaction`**: se almacena como `"checkout_usdc"`, dejando la tabla extensible para otros flujos (e.g. retiros, bridges) sin colisiones.
- **Checklist de Pruebas en `test_replay_attacks.py` (Completado — 15/15 ✅):**
  - [x] **[A]** Replay mismo usuario: reutilizar `tx_hash` en segunda orden propia → HTTP 409.
  - [x] **[B]** Replay cruzado: User B intenta usar el hash que User A ya confirmó → HTTP 409.
  - [x] **[C]** Robo de hash: `from` on-chain no coincide con el wallet del reclamante → orden queda `FAILED`, HTTP 422.
  - [x] **[D]** Race condition concurrente: `ProcessedTransaction` ya existe antes del commit → Capa 1 la detecta, HTTP 409.
  - [x] **[E]** Orden ya `COMPLETED`: re-confirmar una orden terminada → HTTP 409 inmediato.
  - [x] **[F]** Orden expirada: `confirm_payment` después de `expires_at` → HTTP 410; sin registro en `ProcessedTransaction`.
  - [x] **[G]** Orden de otro usuario: User B intenta confirmar orden de User A → HTTP 403 antes de cualquier verificación.
  - [x] **[H]** `tx_hash` inválido (prefijo `0x_bad`): verificación on-chain falla → HTTP 422.
  - [x] **[H2]** `tx_hash` inválido con estado de BD consistente: orden queda `FAILED`, no `CONFIRMING`.
  - [x] **[I]** Modo dev (`0x_mock`): `verify_usdc_payment` retorna `True` sin RPC → orden completa correctamente.
  - [x] **[J]** Integridad de `ProcessedTransaction`: exactamente 1 registro creado con `user_id`, `purpose="checkout_usdc"` y `created_at` dentro del rango temporal.
  - [x] **[K]** Orden en estado `CONFIRMING`: no se puede re-confirmar → Capa 1 detecta el hash existente, HTTP 409.
  - [x] **[L]** Campo `purpose` siempre es `"checkout_usdc"` para confirmaciones de checkout (extensibilidad futura garantizada).
  - [x] **[M]** Sender dirección cero (`0x000...`): mock de tx inválida → HTTP 422.
  - [x] **[N]** Dos hashes distintos para dos usuarios distintos: procesan sin interferencia; exactamente 2 registros independientes en `ProcessedTransaction`.

### 4.3. Manipulación de Probabilidades desde el Cliente
- **Ataque**: Alterar el payload para indicar qué carta quiere obtener en el booster o predecir drops manipulando semillas locales de números aleatorios.
- **Solución**: Drops y eventos aleatorios generados enteramente en el backend utilizando generadores de números aleatorios seguros criptográficamente (CSPRNG) a través de `secrets.SystemRandom()` / `random.SystemRandom()`. El cliente solo recibe el resultado final.
- **Checklist de Cambios (Completado):**
  - [x] Migrar el generador de Gashapón (`roll_gashapon`) a `random.SystemRandom` en `shop.py`.
  - [x] Migrar el generador de cápsulas sorpresa (`_roll_capsule`) a `random.SystemRandom` en `shop.py`.
  - [x] Migrar la apertura de sobres boosters en `shop_service.py` para usar `random.SystemRandom` al seleccionar cartas y estados shiny.
  - [x] Asegurar la generación de estadísticas al nacer (eclosión de webito) en `incubation.py` usando `secrets.SystemRandom()`.
  - [x] Migrar las probabilidades de congelación de huevo por clima a `random.SystemRandom` en `incubation.py`.
  - [x] Asegurar la selección aleatoria de cartas al crear tableros y al destruir cartas en disoluciones de tableros en `board.py` usando `random.SystemRandom`.
  - [x] Confirmar que las barajas y sorteos multijugador en `multiplayer_service.py` usan exclusivamente `random.SystemRandom`.

### 4.4. Bypass de Cooldowns via Reloj del Cliente
- **Ataque**: Adelantar el reloj del OS para saltarse cooldowns de cuidado del webito o gashapón gratis.
- **Solución**: Todos los timestamps se calculan con `datetime.utcnow()` del servidor. Los campos `last_petting`, `last_singing`, `last_feeding` nunca se toman del request del cliente.
- **Checklist de Cambios (Completado):**
  - [x] Validar que todas las interacciones de cuidado de huevos (`interact_with_egg` en `incubation.py`) utilicen `datetime.utcnow()` del servidor.
  - [x] Validar que el cálculo de la cápsula diaria gratuita (`_daily_can_claim` en `shop.py`) y las rachas utilicen la hora del servidor en la zona horaria de Xochimilco (`America/Mexico_City`).
  - [x] Validar que el estado de sueño de los Axolotitos (`game.py`) verifique los tiempos de espera usando la hora del servidor.
  - [x] Confirmar que ningún endpoint del backend acepte o parsee timestamps provenientes de payloads del cliente para validar cooldowns.

### 4.5. Manipulación del Escrow de Partidas y Retiro de Axolotito *(nuevo)*
- **Ataque**: Registrarse en una partida, esperar a que empiece, y luego intentar retirar el axolotito/fondos mientras la partida corre.
- **Solución**: El endpoint de retiro verifica que `GameRoom.status == "waiting"`. Si está `in_progress` o `finished`, el retiro es rechazado.
- **Checklist de Cambios (Completado):**
  - [x] Evitar la liquidación de fondos (`/settle`) mientras el Axolotito tenga el estado `'playing'` (que indica partida o registro activo).
  - [x] Modificar `/recall` para comprobar si la sala está en estado de espera (`waiting`). Si es así, se le remueve de inmediato y se le cambia de estado a `'waiting_settlement'` para permitir el reembolso de fondos inmediato.
  - [x] Si la sala ya comenzó la partida (`status != "waiting"`), el retiro inmediato se rechaza, y se marca `wants_to_stop = True`.
  - [x] Corregir el bug del scheduler en `simulate_multiplayer_match` agregando `session.refresh(axo_obj)` para detectar de forma en tiempo real la señal `wants_to_stop` guardada por `/recall` desde la otra transacción de la API.

### 4.6. Inflado de Jackpot *(nuevo)*
- **Ataque**: Registrarse con wallets múltiples para aportar más al jackpot y luego ganar con una cuenta "principal".
- **Solución**: Un mismo `user_id` no puede tener más de N registros simultáneos. Vincular `user_id` a un único wallet verificado (no se puede cambiar de wallet sin proceso de verificación).
- **Checklist de Implementación (Completado):**
  - [x] **UNIQUE en `wallet_address`** (`app/models/user.py`): El modelo `User` tiene `wallet_address` con `unique=True` a nivel de BD, impidiendo que dos cuentas distintas (`privy_did`) compartan la misma billetera Web3.
  - [x] **Límite de 1 Axolotito por `user_id` por sala de tipo** (`multiplayer.py` → `register_axolotito`): Antes de registrar, busca si el `user_id` ya tiene un `RoomRegistration` activo en una sala del mismo `room_type` con estado `waiting`. Retorna HTTP 400 si lo encuentra.
  - [x] **Límite de 1 registro por `wallet_address` por sala de tipo** (`multiplayer.py`): Consulta cruzada `User → Axolotito → RoomRegistration → GameRoom` para detectar si la `wallet_address` del solicitante ya tiene un slot activo en la sala. Retorna HTTP 400 con la wallet en el mensaje de error.
  - [x] **Límite de 5 tablas por `user_id`/`wallet_address` en la sala concreta** (`multiplayer.py`): Cuenta las tablas ya registradas en la sala específica por la misma billetera y rechaza si el nuevo lote haría el total > 5.
  - [x] **Anti-sybil en `jackpot_eligible`** (`multiplayer_service.py` → `simulate_multiplayer_match`): Cambiado de `len(human_players) >= 2` (user_ids) a **`len(human_wallets) >= 2`** (wallets únicas normalizadas con `.lower()`). Aunque las barreras de registro prevengan el escenario, esta defensa en profundidad garantiza la invariante incluso ante futuros cambios en el flujo de registro.
  - [x] **Normalización case-insensitive de wallets** (`multiplayer_service.py`): El set `human_wallets` usa `.lower()` para que `0xWallet` y `0xWALLET` sean tratadas como la misma dirección.
  - [x] **Usuario sin `wallet_address` no cuenta para elegibilidad** (`multiplayer_service.py`): Si `owner_for_wallet.wallet_address` es `None`, no se agrega al set `human_wallets`, evitando que cuentas sin billetera ayuden a pasar el threshold.
- **Checklist de Pruebas en `test_jackpot_inflation.py` (Completado — 11/11 ✅):**
  - [x] **[A]** Mismo user_id, dos Axolotitos en sala de mismo tipo → HTTP 400 ("Ya tienes un Axolotito en sala de espera").
  - [x] **[B]** Misma wallet, segundo Axolotito del mismo user mientras el primero está en espera → HTTP 400 (límite por user_id).
  - [x] **[C]** Caso positivo: dos jugadores con wallets distintas → ambos registrados con éxito.
  - [x] **[D]** 5 tablas de 1 sola wallet → `jackpot_eligible = False`, sin `JackpotWin`.
  - [x] **[E]** Defensa en profundidad: la invariante de `lower()` colapsa wallets idénticas de distinta capitalización en 1 entrada del set; las wallets únicas del servicio se calculan correctamente.
  - [x] **[F]** 5 tablas de 2 wallets distintas → `jackpot_eligible = True`, estado del jackpot consistente.
  - [x] **[G]** 4 tablas de 2 wallets distintas → `jackpot_eligible = False` (faltan tablas mínimas), sin `JackpotWin`.
  - [x] **[H]** En partidas no elegibles, el jackpot acumula exactamente el 5% del total de cuotas cobradas (sin pagar ni resetear).
  - [x] **[I]** `JackpotWin` apunta al `user_id` correcto del ganador; `amount_won > 0`.
  - [x] **[J]** Usuario sin `wallet_address` (`None`) no contribuye al conteo de wallets únicas → no ayuda a activar el jackpot.
  - [x] **[K]** Tras ganar el jackpot, el vault se reinicia a saldo `> 0`; `last_won_at` y `last_winner_axo_id` quedan registrados.

### 4.7. Explotación del Sistema de Racha VIP y Reclamos Diarios *(nuevo)*
- **Ataque**: Hacer login desde zona horaria diferente o manipular `Accept-Language` para confundir el cálculo del día de reclamo o racha.
- **Solución**: El cálculo de racha y día de reclamos usa la zona horaria de Xochimilco (UTC-6) a nivel de servidor, ignorando cualquier dato de zona horaria del cliente.
- **Checklist de Cambios (Completado):**
  - [x] Crear el campo `vip_last_daily_gal_at` en el modelo `User` en `app/models/user.py` para registrar de manera persistente la fecha de última generación.
  - [x] Agregar `vip_last_daily_gal_at` a la migración automática en `app/main.py`.
  - [x] Ajustar la lógica del cron de recompensas en `app/services/vip_scheduler.py` para procesar el día en base a la zona horaria de Xochimilco (UTC-6).
  - [x] Adaptar el cálculo de racha diaria de la cápsula gratis (`_daily_can_claim`) en `app/api/v1/endpoints/shop.py` para comparar días bajo el huso horario de Xochimilco (UTC-6).
  - [x] Asegurar la consistencia del acumulador de renovación VIP (`shop_service.py`) usando la zona horaria de Xochimilco (UTC-6).

### 4.8. Abuso del Scheduler de Multiplayer *(nuevo)*
- **Ataque**: Llenar una sala con 30 tablas propias para controlar el inicio de la partida y manipular el timing de los números sorteados.
- **Solución**: Límite de tablas por `user_id` por sala (ej. máximo 5). Verificar que la semilla de aleatoriedad del sorteo no es predecible.
- **Checklist de Cambios (Completado):**
  - [x] Restringir registros en `register_axolotito` para que usuarios diferentes que compartan la misma dirección de billetera Web3 (`wallet_address`) no puedan inscribirse en la misma sala de espera.
  - [x] Limitar a un máximo de 5 tablas por usuario/billetera en total en la misma sala de espera.
  - [x] Modificar `get_or_create_waiting_room` para recibir el `user_id` y omitir la asignación a salas que ya contengan registros vinculados a la misma cuenta o billetera (evitando el bypass en auto-re-registro).
  - [x] Auditar que el scheduler utiliza `random.SystemRandom` para mezclar la baraja de cartas, garantizando aleatoriedad criptográficamente segura (CSPRNG basada en `/dev/urandom`) no predecible ni manipulable.
  - [x] Escribir el suite de pruebas unitarias en `test_multiplayer_limits.py` cubriendo todas las restricciones y verificaciones de aleatoriedad.

---

## 5. Pruebas de Contratos Inteligentes (Foundry/Forge)

### 5.1. Tests en Anvil Local
- Correr `forge test` con el suite existente antes de cualquier deploy a Plasma.
- Añadir fuzz tests para las funciones de transferencia de tokens:
  ```solidity
  function testFuzz_transfer(address to, uint256 amount) public { ... }
  ```
- **Checklist de Implementación de Fuzz Tests en Foundry (Completado — 2/2 ✅):**
  - [x] Agregar `testFuzz_TransferGAL(address to, uint256 amount)` en `GameContracts.t.sol` excluyendo direcciones nulas o especiales y limitando montos razonables (`bound`).
  - [x] Agregar `testFuzz_TransferAXG(address to, uint256 amount)` en `GameContracts.t.sol` para validar la robustez de las transferencias de AXG.

### 5.2. Simulación de Deploy
- `forge script Deploy.s.sol --fork-url http://localhost:8545` como smoke test post-build.
- Verificar que los ABIs exportados en `contracts/out/` son los que usa `web3_service.py` (no versiones stale).
- **Checklist de Verificación de Sincronización de ABIs (Completado — 9/9 ✅):**
  - [x] Crear suite de pruebas de sincronización de ABIs `test_abi_sync.py` que compruebe la existencia y carga física de los archivos de artefactos JSON de Foundry en `contracts/out/`.
  - [x] Validar que las firmas y parámetros de los métodos clave de `GemaAlga`, `Axogema`, `Webitos`, `Axolotitos`, `CartasLoteria`, `Boosters`, `TablasLoteria` y `Consumables` coinciden exactamente con lo esperado en el backend.

---

## 6. Integración Continua (CI)

### 6.1. Pipeline Mínimo (GitHub Actions / similar)
```yaml
- name: Run unit tests
  run: pytest backend/tests/unit/ -x -q

- name: Run integration tests
  run: pytest backend/tests/integration/ -x -q --tb=short

- name: Run forge tests
  run: forge test --root contracts/
```

### 6.2. Umbrales de Calidad
- Cobertura de código: mínimo 70% en servicios críticos (`shop_service`, `bank_service`, `multiplayer_service`).
- Cero tests de integración fallando en `main` — los fallos en CI bloquean el merge.
- Los tests de simulación (`simulation/`) corren manualmente o en schedule nocturno, no en cada PR.

---

## 7. Prioridades y Checklist

### 🔴 Prioridad Alta (P0) — Críticos de Seguridad
- [x] Implementar `SELECT FOR UPDATE` en decremento de inventario (`PlayerInventory`).
- [x] Crear tabla `ProcessedTransactions` con índice `UNIQUE` en `tx_hash` + validación de `sender`.
- [x] Escribir `test_concurrency_race_conditions.py` y `test_replay_attacks.py`.
- [x] Verificar que el scheduler de multiplayer no puede ser inundado para controlar el timing del sorteo.
- [x] Añadir límite de registros por `user_id` y `wallet_address` por sala en `multiplayer.py`. *(§4.8)*
- [x] Migrar todos los generadores de números aleatorios en endpoints y servicios a `random.SystemRandom` (CSPRNG). *(§4.3)*
- [x] Escribir `test_secure_randomness.py` como guardia de regresión de CSPRNG en CI. *(§4.3)*

### 🟡 Prioridad Media (P1) — Pruebas Unitarias e Integración
- [x] Configurar `conftest.py` con fixtures de BD en memoria y cliente HTTP. *(§0.3)*
- [x] Escribir `test_shop_service.py` cubriendo compras, descuentos VIP, límite mensual Foil y anti-whale. *(§1.1)*
- [x] Pruebas estadísticas de tasas de drop del Gashapón (100k tiradas) — `test_gashapon_rates.py`. *(§1.2)*
- [x] Escribir `test_vip_system.py` cubriendo welcome gift, auto-renovación y rachas. *(§1.5)*
- [x] Escribir `test_escrow_integrity.py` y `test_jackpot_vault.py`. *(§2.4, §2.5)*
- [x] Desarrollar `generate_noise_data.py` con payloads corruptos para todos los endpoints. *(§3.2)*
- [x] Escribir `test_inventory.py`: apertura con `quantity=0`, race condition de doble apertura, sin duplicados en `PlayerInventory`. *(§1.3)*
- [x] Escribir `test_bank_service.py`: idempotencia de wallet, rollback por saldo insuficiente, exactitud numérica, rechazo de depósitos ≤0. *(§1.4)*
- [x] Escribir `test_multiplayer_service.py`: asignación de sala, unicidad de `WINNING_LINES`, casos borde de `check_line`/`check_cuadrito`. *(§1.6)*
- [x] Escribir `test_blockchain_desync.py`: mock de `Web3Service` con fallo post-BD, estado nunca inconsistente, timeout con backoff. *(§2.3)*
- [x] Migrar scripts de simulación de volumen a Locust (`simulate_high_volume_traffic.py`). *(§3.1)*
- [x] Crear `simulate_degraded_network.py`: latencia simulada, doble-submit prevenido, `isLoading` correcto en frontend. *(§3.3)*

### 🟠 Prioridad Media-Baja (P1.5) — Vulnerabilidades con Checklist Pendiente
- [x] §4.1 Race conditions en apertura de booster — `SELECT FOR UPDATE` + endpoint diferido `POST /shop/booster/open`.
- [x] §4.2 Replay attacks / reuso de `tx_hash` — tabla `ProcessedTransactions` + validación de `sender`.
- [x] §4.3 Manipulación de probabilidades — CSPRNG en todos los endpoints de drops y sorteos.
- [x] §4.4 Bypass de cooldowns via reloj del cliente — timestamps 100% del servidor (UTC).
- [x] §4.5 Manipulación del escrow de partidas — guard en `/recall` y `/settle`.
- [x] §4.6 Inflado de Jackpot — `UNIQUE` en `wallet_address` + límites por `user_id`/`wallet` en registro + `jackpot_eligible` basado en wallets únicas (`.lower()`) + `test_jackpot_inflation.py` (11 tests).
- [x] §4.7 Explotación de rachas VIP — cálculo de día en UTC-6 (Xochimilco) con campo `vip_last_daily_gal_at`.
- [x] §4.8 Abuso del scheduler de multiplayer — límite de 5 tablas/sala por wallet + `test_multiplayer_limits.py`.

### 🟢 Prioridad Baja (P2) — Calidad, Documentación e Infraestructura
- [x] Crear `SECURITY.md` documentando todas las mitigaciones §4.1–§4.8.
- [ ] Configurar pipeline CI mínimo (GitHub Actions): `pytest unit/`, `pytest integration/`, `forge test`. *(§6.1)*
- [ ] Configurar umbral de cobertura de código en CI (mínimo 70% en `shop_service`, `bank_service`, `multiplayer_service`). *(§6.2)*
- [x] Añadir fuzz tests en Foundry para contratos de token (`testFuzz_transfer`). *(§5.1)*
- [x] Simular latencia de red en el frontend: verificar estados de loading y botones deshabilitados. *(§3.3)*
- [x] Verificar que los ABIs exportados en `contracts/out/` estén sincronizados con los que usa `web3_service.py`. *(§5.2)*

---

## 8. Auditoría Final — Estado Real del Plan (2026-05-26)

**Suite de pruebas: 224 tests recolectados → 223 ✅ passed, 1 ⏭ skipped (SQLite/FOR UPDATE).**

### ✅ Completado y Verificado en Código

| Área | Evidencia |
|------|-----------|
| P0 — Race conditions, replay attacks, CSPRNG, escrow, VIP, multiplayer limits | Código + 16 archivos de test en `tests/unit/` |
| P1 — Todos los test suites unitarios (shop, bank, gashapon, inventory, VIP, multiplayer, blockchain, escrow, jackpot) | 99 tests en servicios críticos |
| P1.5 §4.6 — Wallet única + bloqueo de cambio | `user.py` `unique=True`, migración `b2c3d4e5f6a1`, `test_wallet_uniqueness.py` (6 tests), `test_jackpot_inflation.py` (11 tests) |
| §3.1 Locust — `simulate_high_volume_traffic.py` | 3 clases de usuario, hook SLA, auth dev, en `tests/simulation/` |
| §3.2 — `generate_noise_data.py` | `backend/app/scripts/generate_noise_data.py` |
| §3.3 — `simulate_degraded_network.py` | 8 passed + checks frontend documentados |
| §5.1 — Foundry fuzz tests | `testFuzz_TransferGAL`, `testFuzz_TransferAXG` en `contracts/test/GameContracts.t.sol` |
| §5.2 — ABI sync | `test_abi_sync.py` (9 tests, por Gemini/Antigravity) |
| SECURITY.md | `/SECURITY.md` (115 líneas, §4.1–§4.8) |

### ❌ Pendiente de Implementar

- [ ] **§6.1 — Pipeline CI (GitHub Actions)**: crear `.github/workflows/ci.yml` con jobs `pytest unit/`, `pytest integration/`, `forge test --root contracts/`. No existe el directorio `.github/workflows/`.
- [ ] **§6.2 — Umbral de cobertura**: configurar `pytest-cov` + `--cov-fail-under=70` en el job de CI para `shop_service`, `bank_service`, `multiplayer_service`. Depende de §6.1.
- [ ] **Frontend Playwright (opcional)**: automatizar los checks manuales de `simulate_degraded_network.py` (isLoading, doble-click, botón disabled). Actualmente son solo checks documentados; `tests/simulation/` no tiene archivo Playwright.

---

## 9. Resumen de Pendientes y Hoja de Ruta de Pruebas

A continuación se detalla la hoja de ruta para completar las tareas pendientes de aseguramiento de calidad, agrupadas por fases y con listas de verificación claras.

### Fase 1: Automatización e Integración Continua (CI)
El objetivo de esta fase es automatizar la ejecución de las suites de prueba existentes en cada pull request y push a la rama principal.
- **[ ] Configuración de GitHub Actions Workflow:**
  - [ ] Crear el directorio `.github/workflows/`.
  - [ ] Crear el archivo `.github/workflows/ci.yml`.
  - [ ] Configurar un job para el backend (Python, Poetry/pip, base de datos SQLite mockeada, dependencias de `requirements.txt`).
  - [ ] Configurar un job para Foundry (instalación de Foundry, compilación y ejecución de `forge test --root contracts/`).
- **[ ] Umbrales de Cobertura de Código:**
  - [ ] Integrar `pytest-cov` en el entorno de pruebas del backend.
  - [ ] Configurar la ejecución de `pytest --cov=app --cov-fail-under=70 backend/tests/` en el pipeline de CI para asegurar que los cambios futuros mantengan la calidad.
  - [ ] Excluir carpetas no críticas (como migraciones o scripts de datos) para enfocar el reporte en `shop_service`, `bank_service`, `multiplayer_service` e `incubation_service`.

### Fase 2: Automatización de Pruebas de Interfaz (E2E Frontend)
El objetivo de esta fase es transformar los criterios de verificación manual de red degradada y de interfaz en pruebas automatizadas robustas.
- **[ ] Setup de Playwright en el Frontend:**
  - [ ] Instalar Playwright en la carpeta `frontend/` (`npm install --save-dev @playwright/test`).
  - [ ] Crear el archivo de configuración `playwright.config.ts`.
- **[ ] Implementación de Casos de Prueba Críticos:**
  - [ ] **Simulación de Latencia:** Escribir un test E2E que intercepte llamadas a la API, inyecte retrasos artificiales de 2s y verifique que los botones de compra e incubación muestran loaders y bloquean el clic simultáneo (`disabled`).
  - [ ] **Verificación de Red Caída:** Escribir un test que simule desconexión (interceptar llamadas API y retornar error 500) y valide que el cliente Next.js maneja la respuesta mediante alertas/toasts de error sin provocar fallos en cascada.
  - [ ] **Idempotencia en UI:** Validar que realizar múltiples clicks rápidos (double-submit) en el botón de abrir booster o comprar no genera solicitudes repetidas en el tráfico de red.

### Fase 3: Reorganización Estructural y Smoke Tests de Contratos
Mejorar la estructura física de los archivos de prueba para alinearlos con el plan original y automatizar las simulaciones en entornos locales.
- **[ ] Separación Física de Pruebas de Integración:**
  - [ ] Crear el directorio `backend/tests/integration/` e instalar el archivo `__init__.py`.
  - [ ] Mover los archivos `test_concurrency_race_conditions.py`, `test_replay_attacks.py`, `test_blockchain_desync.py`, `test_escrow_integrity.py` y `test_jackpot_vault.py` de `backend/tests/unit/` a `backend/tests/integration/`.
  - [ ] Actualizar los imports y configuraciones locales necesarios en `conftest.py`.
- **[ ] Smoke Tests de Scripts de Deploy:**
  - [ ] Crear una tarea o script para correr localmente `forge script Deploy.s.sol --fork-url http://localhost:8545` levantando un contenedor efímero de Anvil.
  - [ ] Validar que las direcciones obtenidas se escriban correctamente en la configuración de entorno temporal de las pruebas de integración.
