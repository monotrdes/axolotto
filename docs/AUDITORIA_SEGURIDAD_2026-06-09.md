# 🛡️ Auditoría de Seguridad Web3 — Axolotto

**Fecha:** 2026-06-09
**Auditor:** Claude (Senior Web3 Security Auditor / Full-Stack QA)
**Alcance:** Smart Contracts (`contracts/src/`), Backend (`backend/app/`), integración Web3, capa de autenticación y economía dual AXF/FRJ.
**Metodología:** Revisión adversa de sombrero blanco, análisis estático y trazado de flujos de fondos.

---

## 0. Resumen Ejecutivo

Axolotto usa una arquitectura **"backend-autoritativo"**: el resultado de la lotería se calcula **off-chain** con `random.SystemRandom()` y la blockchain actúa como un libro mayor espejo controlado por una única wallet Treasury. Esto **elimina** las clases clásicas de vulnerabilidad on-chain (manipulación de aleatoriedad por validadores, reentrancy, front-running/MEV del sorteo), pero **traslada todo el riesgo al backend y a la gestión de claves**.

Los contratos están razonablemente blindados (todo gateado por `onlyOwner`/`onlyController`). El riesgo real y crítico vive en el backend.

### Tabla de hallazgos

| ID | Severidad | Título |
|----|-----------|--------|
| VULN-01 | 🔴 **Crítica** | Bypass total de autenticación vía `?user_id=` cuando el modo por defecto (`local`) llega a producción |
| VULN-02 | 🔴 **Crítica** | Centralización extrema: una sola `TREASURY_PRIVATE_KEY` es owner de TODOS los contratos (mint infinito) |
| VULN-03 | 🟠 **Alta** | Endpoints `/dev/*` sin auth + auto-reward gigante (50k AXF / 500k FRJ) explotables si `BLOCKCHAIN_MODE=local` |
| VULN-04 | 🟠 **Alta** | Desincronización DB ↔ Blockchain: fallos de mint/burn on-chain se tragan silenciosamente |
| VULN-05 | 🟠 **Alta** | Inflación de premios no respaldada en multijugador (luck_bonus / vip_bonus se acuñan de la nada) |
| VULN-06 | 🟡 **Media** | Uso de `float` para saldos monetarios (errores de redondeo acumulables / "dust farming") |
| VULN-07 | 🟡 **Media** | `verify_usdc_payment` devuelve `True` incondicional en modo local (free AXF si se filtra a prod) |
| VULN-08 | 🟡 **Media** | Sobrecito.abrirSobrecito on-chain desacoplado del minteo de cartas (el backend decide las cartas) |
| VULN-09 | 🟡 **Media** | Staking sin enforcement de slots: se puede stakear Axolotitos ilimitados |
| VULN-10 | 🟢 **Baja** | `dissolveBoard`: índice de carta a destruir lo decide el backend (no verificable por el jugador) |
| VULN-11 | 🟢 **Baja** | Web3Service relee `w3.eth.gas_price`/nonce bajo lock global → cuello de botella y DoS de throughput |
| VULN-12 | 🔵 **Opt.** | Código muerto, `return` duplicado, queries N+1 en endpoints de lobby/tienda |

---

## 1. Arquitectura general

```
Cliente (Privy JWT)  ──HTTP──►  FastAPI Backend  ──Treasury PK──►  GameController (owner)
       │                              │                                   │
   wallet self-custodial         PostgreSQL (fuente de verdad)      14 contratos (espejo)
```

**Observación clave:** La DB es la fuente de verdad para el juego. La cadena es un espejo "best-effort". Toda mutación de fondos pasa por `get_verified_user_id`. Por tanto, **la seguridad del juego = la seguridad de ese único dependency de auth + la protección de la Treasury key.** Ambos tienen problemas (VULN-01, VULN-02).

---

## 2. Hallazgos detallados

### [VULN-01] Bypass total de autenticación vía parámetro `user_id`
- **Severidad:** 🔴 Crítica
- **Ubicación:** `backend/app/core/auth.py:35-47` + `backend/app/core/config.py:63,102`
- **Descripción del Problema:**
  `get_verified_user_id` contiene una rama de "modo desarrollo":
  ```python
  if not credentials:
      if settings.BLOCKCHAIN_MODE == "local" and not settings.PRIVY_APP_ID:
          user_id = request.query_params.get("user_id") or request.query_params.get("privy_did")
          if user_id:
              return user_id     # ← suplanta a CUALQUIER usuario sin token
  ```
  El problema es que **los valores por defecto activan esta rama**: `BLOCKCHAIN_MODE` por defecto es `"local"` (config.py:63) y `PRIVY_APP_ID` por defecto es `None` (config.py:102). Si el `.env` de producción olvida fijar `PRIVY_APP_ID` o `BLOCKCHAIN_MODE`, **todo el sistema de identidad se desactiva**.
  Incluso con `PRIVY_APP_ID` ausente pero token presente (Caso 1, líneas 52-66), el backend **decodifica el JWT sin verificar la firma** (`verify_signature: False`) y confía en el claim `sub` → un atacante forja un JWT con cualquier `sub`.
- **Escenario de Ataque (PoC conceptual):**
  1. El atacante detecta que `api.axolot.to` corre con `BLOCKCHAIN_MODE=local` (o sin `PRIVY_APP_ID`).
  2. Llama `POST /api/v1/bank/...` o `/game/play?user_id=did:privy:VICTIMA`.
  3. El backend devuelve `did:privy:VICTIMA` como identidad verificada → el atacante drena la wallet de la víctima, reclama sus premios, vende su inventario en el market, etc.
  4. Como `admin_dids` se compara contra el `sub`, si conoce un DID admin puede pasar `?user_id=<DID_ADMIN>` y golpear endpoints `require_admin`.
- **Impacto:** Robo total de fondos de cualquier cuenta, suplantación de admin, colapso de la economía. Pérdida de fondos de todos los usuarios.
- **Remediación:**
  - **Eliminar el default permisivo.** `BLOCKCHAIN_MODE` no debe tener default `"local"`; debe ser un campo requerido o defaultear a `"production"`.
  - Añadir un `@model_validator` que **falle el arranque** si `BLOCKCHAIN_MODE != "local"` y `PRIVY_APP_ID` está vacío.
  - Nunca aceptar `user_id` por query param. Para tests locales usar un header explícito `X-Dev-User` gateado por una env var separada `ALLOW_DEV_AUTH=true` que **jamás** se setee en prod.
  - Eliminar la decodificación sin verificar firma; usar siempre JWKS.
  ```python
  @model_validator(mode="after")
  def _enforce_auth(self):
      if self.BLOCKCHAIN_MODE != "local" and not self.PRIVY_APP_ID:
          raise ValueError("PRIVY_APP_ID es obligatorio fuera de modo local")
      return self
  ```
- 📋 **Plan de remediación:** `docs/plan_vuln01_auth_bypass.md`

---

### [VULN-02] Centralización extrema — una sola clave acuña todo
- **Severidad:** 🔴 Crítica
- **Ubicación:** `contracts/src/GameController.sol` (todas las funciones `onlyOwner`), `web3_service.py:102-132` (`TREASURY_PRIVATE_KEY`)
- **Descripción del Problema:**
  El `GameController` es `Ownable` y su owner (la Treasury) puede `depositarFRJ`/`depositarAXF` (mint arbitrario), `cobrarFRJ`/`cobrarAXF` (burn de cualquier wallet), transferir Tablas/Axolotitos de cualquiera, etc. La misma `TREASURY_PRIVATE_KEY` vive en el `.env` del backend y firma **cada** transacción. No hay multisig, ni timelock, ni límites de tasa on-chain, ni separación de roles.
  Además `Frijolito.mint`/`Axoficha.mint` aceptan al `owner()` directamente (`onlyController` incluye `owner()`), así que una filtración de la clave = **mint ilimitado de ambas monedas** y burn del saldo de cualquier jugador.
- **Escenario de Ataque (PoC conceptual):**
  1. Un atacante compromete el host del backend (RCE, fuga de `.env`, backup expuesto, log con la clave).
  2. Con la clave: `axf.mint(atacante, 10**30)` y la vende, o `frj.burn(victima, balance)` para sabotear, o transfiere todos los NFT.
  3. No hay forma on-chain de revertirlo ni de pausar.
- **Impacto:** Pérdida total e irreversible de la integridad económica. Single point of failure absoluto.
- **Remediación:**
  - Mover la propiedad de los contratos a un **multisig (Gnosis Safe)** + **timelock** para funciones administrativas sensibles (cambiar controller, configurar direcciones).
  - Separar roles: una "hot wallet" operativa con permisos *acotados* (solo `mint` hasta un cap diario por bloque) y owner frío en multisig. Usar `AccessControl` de OZ con roles `MINTER_ROLE`, `PAUSER_ROLE`.
  - Añadir `Pausable` a los tokens y un circuit breaker (cap de mint por ventana).
  - Guardar la clave operativa en un KMS/HSM (AWS KMS, GCP KMS), nunca en `.env` plano.
  - Monitoreo on-chain de mints anómalos con alertas.
- 📋 **Plan de remediación:** `docs/plan_task-1781055512-64-VULN-02_remediacion-centralizacion-treasury-multisig.md`

---

### [VULN-03] Endpoints `/dev/*` sin autenticación + auto-reward gigante
- **Severidad:** 🟠 Alta
- **Ubicación:** `backend/app/api/v1/endpoints/dev.py:42,150` y `config.py:123-124`
- **Descripción del Problema:**
  `fill_multiplayer_rooms` (dev.py:150) **no tiene `Depends(get_verified_user_id)`** — su única protección es `_check_dev_mode()` (que solo verifica `BLOCKCHAIN_MODE == "local"`). `reset_tutorial` sí pide identidad, pero crea un `PendingReward` con `DEV_AUTO_REWARD_AXF = 50_000` y `DEV_AUTO_REWARD_FRJ = 500_000` (config.py:123-124).
  Encadenado con **VULN-01**, en un despliegue accidentalmente en modo local:
- **Escenario de Ataque (PoC conceptual):**
  1. `POST /api/v1/dev/reset-tutorial?user_id=did:privy:atacante` → genera premio pendiente de 50k AXF + 500k FRJ.
  2. Completar el tutorial (o disparar el claim) → fondos reales acreditados.
  3. Repetir con miles de DIDs autogenerados → minado infinito; o spamear `fill-multiplayer-rooms` para envenenar el matchmaking.
- **Impacto:** Inflación masiva de la economía, envenenamiento de salas, DoS de matchmaking.
- **Remediación:**
  - Añadir `Depends(require_admin)` a **todos** los endpoints `/dev/*`, además del check de modo.
  - Registrar el router `dev` **solo** si `settings.BLOCKCHAIN_MODE == "local"` (no montarlo siquiera en prod):
    ```python
    if settings.BLOCKCHAIN_MODE == "local":
        api_router.include_router(dev.router, prefix="/dev")
    ```
  - Reducir/condicionar `DEV_AUTO_REWARD_*` y nunca leerlos fuera del router dev.
- 📋 **Plan de remediación:** `docs/plan_task-1781055512-64-VULN-03_remediacion-dev-endpoints-auth.md`

---

### [VULN-04] Desincronización DB ↔ Blockchain por errores tragados
- **Severidad:** 🟠 Alta
- **Ubicación:** `game_service.py:111-113, 356-360, 502-506`; `market.py:208-209`; patrón general en `web3_service`
- **Descripción del Problema:**
  El backend muta el saldo en la DB y *después* intenta replicar on-chain dentro de un `try/except` que solo hace `print(...)`:
  ```python
  wallet.frijolitos -= entry_fee          # DB
  try:
      Web3Service.burn_frj(...)            # chain
  except Exception as e:
      print(f"⚠️ Error al quemar ...: {e}")   # se traga el error
  ```
  El premio se mintea on-chain por el monto completo en otra llamada independiente. Si una de las dos (burn de cuota / mint de premio) falla y la otra no, **la cadena y la DB divergen permanentemente**. No hay outbox, reintentos, ni reconciliación. Tampoco son atómicas con el `session.commit()`.
- **Escenario de Ataque / Impacto:**
  - Un atacante que provoque fallos intermitentes del RPC (o simplemente la congestión de red) puede inducir estados donde la DB le acredita premios que nunca se acuñaron, o donde su saldo on-chain queda inflado respecto al DB. Al ser la DB la fuente de verdad para el market y el retiro, la divergencia es explotable según qué capa se consulte en cada operación.
  - A escala, la contabilidad on-chain pierde todo valor de auditoría.
- **Remediación:**
  - Implementar un **patrón outbox transaccional**: escribir la intención on-chain en una tabla dentro del mismo commit que la mutación DB, y procesarla con un worker idempotente con reintentos y backoff.
  - Registrar cada tx on-chain confirmada en `ProcessedTransaction` y reconciliar periódicamente DB vs cadena.
  - Nunca usar `print` para tragar fallos financieros: emitir a un log estructurado + métrica + alerta, y marcar la fila como `pending_chain_sync`.
- 📋 **Plan de remediación:** `docs/plan_task-1781055512-64-VULN-04_remediacion-db-chain-outbox.md`

---

### [VULN-05] Inflación de premios no respaldada en multijugador
- **Severidad:** 🟠 Alta
- **Ubicación:** `multiplayer_service.py:300-353, 480-522`
- **Descripción del Problema:**
  La bolsa se calcula como `total_collected_gal = human_boards_count * room.entry_fee_gal` y se reparte 35% + 55% + 5% tesorería + 5% jackpot. Pero a los ganadores se les suma **además** un `luck_bonus = (luck/1000) * share` (hasta +10%) y un `vip_bonus` (hasta +5%) que **no se debitan de ninguna bolsa ni vault** — se crean directamente en `escrow_balance_gal`. Encima, la cuota real cobrada a VIPs es descontada (`effective_fee`, líneas 244-247), pero la bolsa se computa con el `entry_fee_gal` completo: la bolsa está **sobre-financiada** respecto a lo realmente recolectado.
- **Escenario de Ataque (PoC conceptual):**
  1. Un jugador con `stat_luck` alto y VIP Axolite entra a tantas partidas como pueda.
  2. Cada victoria mintea ~15% extra de FRJ que nadie pagó; al hacer `/settle`, ese excedente pasa a su wallet real.
  3. Bucle de farmeo sostenido → inflación neta de FRJ en cada ronda ganada.
- **Impacto:** Inflación monetaria sistemática, devaluación del FRJ, ventaja económica desbalanceada.
- **Remediación:**
  - Financiar `luck_bonus`/`vip_bonus` desde una bolsa explícita (p. ej., una fracción reservada de la bolsa o de la tesorería) y **garantizar la invariante**: `Σ pagos == Σ recolectado`. Añadir un assert/reconciliación al cierre de cada partida.
  - Usar `effective_fee` también en `total_collected_gal`.

---

### [VULN-06] Saldos monetarios en `float`
- **Severidad:** 🟡 Media
- **Ubicación:** `models/economy.py:49-50` (`axofichas: float`, `frijolitos: float`); aritmética en bank/market/game services.
- **Descripción del Problema:**
  Todos los saldos y montos son `float` (IEEE-754). Las comisiones (`amount * 0.05`), bonuses y conversiones acumulan errores de redondeo. Operaciones repetidas pueden crear o destruir "polvo" de FRJ, y comparaciones `saldo < precio` pueden fallar en los bordes.
- **Escenario de Ataque:** "Dust farming": estructurar miles de micro-transacciones donde el redondeo favorece consistentemente al atacante (p. ej., comisiones que redondean a la baja vs. créditos que redondean al alza).
- **Impacto:** Fugas económicas lentas pero acumulables; contabilidad no determinista.
- **Remediación:** Migrar a enteros (unidades mínimas / wei) o `Decimal` con contexto fijo en toda la capa económica. On-chain ya usa `to_wei`; alinear la DB a la misma granularidad entera.

---

### [VULN-07] `verify_usdc_payment` confía ciegamente en modo local
- **Severidad:** 🟡 Media
- **Ubicación:** `web3_service.py:560-580` y `checkout_service.py:168-173`
- **Descripción del Problema:**
  En modo local (o con `tx_hash` mock, o sin `USDC_ADDRESS`) la verificación de pago devuelve `True` sin comprobar nada. La validación de formato del hash en `confirm_payment` también se salta en local. Encadenado con un despliegue accidental en modo local (VULN-01), el checkout de AXF con cripto se vuelve gratis.
- **Escenario de Ataque (PoC conceptual):** Con backend en local, `confirm_payment(order, tx_hash="0x_mock_loquesea")` → mintea el pack de AXF sin pago real.
- **Impacto:** Acuñación gratuita de moneda premium (la que se compra con dinero real).
- **Remediación:** Igual que VULN-01: impedir el arranque en modo no-local sin `USDC_ADDRESS` (ya existe el validador para esto, reforzarlo) y separar el "modo dev de pagos" en una bandera explícita distinta de `BLOCKCHAIN_MODE`. La verificación on-chain real (recipient + sender + monto) está **bien implementada** — el riesgo es solo el bypass por configuración.

---

### [VULN-08] Apertura de sobrecito on-chain desacoplada del minteo de cartas
- **Severidad:** 🟡 Media
- **Ubicación:** `contracts/src/Sobrecito.sol:56-62` (`abrirSobrecito`) vs. `GameController.abrirSobrecito` (líneas 148-158)
- **Descripción del Problema:**
  `Sobrecito.abrirSobrecito(fase)` es **público**: cualquier holder puede quemar su sobrecito on-chain y emitir el evento `SobrecitoAbierto`. Pero las 7 cartas se acuñan en una transacción **separada** del backend (`GameController.abrirSobrecito`, que el backend dispara al escuchar el evento). Si el jugador llama directamente al contrato `Sobrecito` (sin pasar por el backend), **quema su sobre y nunca recibe cartas** (el backend no necesariamente está escuchando, o el flujo oficial usa `burnSobrecito` desde el controller). Inversamente, el contenido de las cartas lo decide el backend off-chain → confianza total en el servidor para la "aleatoriedad" del sobre.
- **Impacto:** Pérdida de activos del jugador (sobre quemado sin contraparte); además, la equidad del drop no es verificable.
- **Remediación:**
  - Quitar `abrirSobrecito` público del contrato `Sobrecito` o hacerlo `onlyController`, de modo que el único camino de apertura sea el atómico vía `GameController.abrirSobrecito` (que quema y mintea en la misma tx).
  - Para equidad verificable del drop, usar un commit-reveal con semilla firmada por el backend, o VRF si se quiere drop on-chain.

---

### [VULN-09] Staking sin límite de slots
- **Severidad:** 🟡 Media
- **Ubicación:** `staking_service.py:118-122` (`get_staking_slots`) vs `claim_all_staking:301-329`
- **Descripción del Problema:**
  `get_staking_slots` calcula `cave_level + 1` slots, pero `claim_all_staking` itera **todos** los Axolotitos del usuario y reclama por cada uno, sin respetar el número de slots. El cap diseñado (slots limitados) no se aplica al pago.
- **Impacto:** Un usuario con N Axolotitos cobra staking de los N, ignorando la mecánica de slots → rendimiento pasivo desbalanceado.
- **Remediación:** En `claim_all_staking` y en el accrual, restringir a los primeros `get_staking_slots(user)` Axolotitos (p. ej., los marcados explícitamente como "en staking"), y validar el estado del slot al acreditar.

---

### [VULN-10] Destrucción de carta en `dissolveBoard` decidida por el backend
- **Severidad:** 🟢 Baja
- **Ubicación:** `contracts/src/TablasLoteria.sol:112-140` + `web3_service.dissolve_board_onchain`
- **Descripción del Problema:**
  `dissolveBoard(tableId, destroyCardIndex)` recibe el índice a destruir como parámetro del controller. El jugador no tiene garantía verificable de qué carta se destruye ni de que el proceso sea aleatorio/justo (es una decisión off-chain del backend).
- **Impacto:** Posible favoritismo/abuso por parte de un operador malicioso; falta de transparencia. Existe `dissolveBoardSafe` que devuelve las 16 — la asimetría puede confundir.
- **Remediación:** Si la destrucción debe ser aleatoria, derivarla de un commit-reveal o de una semilla auditable, y emitir prueba en el evento. Documentar claramente cuándo se usa `dissolveBoard` vs `dissolveBoardSafe`.

---

### [VULN-11] Lock global de transacciones Web3 → cuello de botella / DoS de throughput
- **Severidad:** 🟢 Baja
- **Ubicación:** `web3_service.py:91-132` (`_tx_lock` global + `estimate_gas` por cada tx)
- **Descripción del Problema:**
  Todas las transacciones on-chain se serializan con un único `threading.Lock` de clase, y cada una hace `estimate_gas` y `get_transaction_count(..., 'pending')` síncronos. Bajo carga (muchos jugadores ganando a la vez) esto crea una cola global; un atacante que genere muchas acciones on-chain puede degradar el throughput de todo el sistema. Además el manejo de nonce con `'pending'` bajo lock no protege ante múltiples instancias/procesos del backend (PM2 cluster).
- **Impacto:** Degradación de servicio; con varios workers, colisiones de nonce y txs perdidas.
- **Remediación:** Externalizar el envío on-chain a una **cola dedicada** (un solo "relayer" worker) con gestión de nonce centralizada y reintentos. Evitar `estimate_gas` por tx (cachear límites por tipo de operación).

---

### [VULN-12] Optimización: código muerto, N+1 y duplicados
- **Severidad:** 🔵 Optimización
- **Ubicaciones:**
  - `web3_service.py:617-618`: `return False` duplicado (código muerto tras el `except`).
  - `multiplayer_service.py` y `multiplayer.py`: múltiples `session.get`/`select(User)` dentro de bucles por jugador → **N+1**. Precargar con un solo query e indexar por `privy_did`.
  - `shop.py:get_store_items`: varias subconsultas `func.sum/count` por ítem dentro del bucle.
  - `Counter.sol`: contrato de ejemplo sin uso productivo; eliminar del set desplegado.
- **Remediación:** Limpiar código muerto, batch de queries (eager loading), y eliminar contratos no usados del pipeline de despliegue.

---

## 3. Lo que está BIEN hecho (para no romperlo)

- ✅ **Aleatoriedad:** uso consistente de `random.SystemRandom()` (CSPRNG) en todo el juego; el sorteo se calcula off-chain, no depende de `block.timestamp`/`blockhash` → inmune a manipulación de validadores y MEV del sorteo.
- ✅ **Replay protection del checkout:** doble capa (`ProcessedTransaction` UNIQUE + chequeo en `CryptoPurchaseOrder.tx_hash_payment` UNIQUE) y commit atómico que delega la carrera al constraint de BD. Sólido.
- ✅ **Anti tx-hash theft:** `verify_usdc_payment` compara `from_addr` con el `wallet_address` del usuario.
- ✅ **`SELECT FOR UPDATE`** correcto en `get_or_create_wallet(for_update=True)`, market, capsule, settle → previene double-spend concurrente.
- ✅ **Anti-sybil del jackpot:** exige ≥2 `wallet_address` únicas, no solo user_ids (multiplayer_service.py:266-278).
- ✅ **Contratos:** sin reentrancy real (Solidity 0.8 con checked math, gating estricto `onlyController`, sin `.call` a contratos arbitrarios con estado mutable después).
- ✅ **Validación de inputs** del juego (multiplier en {1,2,5,10}, cartas 1-54, boards 1-3, buy-in 10-1000).

---

## 4. Priorización recomendada

1. **Inmediato (bloqueante de prod):** VULN-01, VULN-02, VULN-03, VULN-07 — todo lo que dependa de que el `.env` esté perfecto. Hacer que el sistema **falle ruidosamente** al arrancar mal configurado.
2. **Corto plazo:** VULN-04 (outbox/reconciliación), VULN-05 (invariante de bolsa), VULN-06 (Decimal/enteros).
3. **Medio plazo:** VULN-08, VULN-09, VULN-10, VULN-11.
4. **Continuo:** VULN-12 y monitoreo on-chain.

---

*Fin del reporte. Generado en revisión estática; se recomienda complementar con pruebas dinámicas (fuzzing de endpoints, tests de invariantes económicas con Foundry/property-based) antes de mainnet.*
