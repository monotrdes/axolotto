# Axolotto Security Audit Report — Segunda Auditoría
**Fecha:** 2026-06-04  
**Auditor:** Claude Sonnet (claude-sonnet-4-6), segundo auditor  
**Scope:** Re-audit completo contra hallazgos previos (2026-05-31) + features nuevos  
**Auditoría anterior:** `docs/completed/SECURITY_AUDIT.md`

---

## Resumen Ejecutivo

**Nivel de riesgo: HIGH — No lanzar con dinero real hasta resolver NEW-3 y NEW-4.**

Los 13 SEVs críticos/altos/medios del audit anterior están mayoritariamente corregidos. Sin embargo, se encontraron **4 vulnerabilidades HIGH nuevas** en features agregados después del audit (cave expansion, F2P, incubación, rewards). Dos de ellos permiten farmear Axolotitos Astrales gratis (el asset de mayor valor del juego) sin gastar nada.

**Top 4 issues críticos a resolver antes de lanzar:**
1. `GET /cave/status` muta estado y otorga huevos gratis sin autenticación (NEW-3)
2. F2P `/watch-reward` permite acumular fragmentos ilimitados → Axolotitos Astrales gratis (NEW-4)
3. Race condition en `hatch_webito` puede duplicar NFTs on-chain (NEW-2)
4. Race condition en `rewards/claim` permite double-claim del reward de lanzamiento (NEW-1)

---

## Parte 1 — Verificación de Hallazgos Anteriores

### SEV-1: Admin Deposit sin autenticación
**Estado: CORREGIDO**

`backend/app/api/v1/endpoints/bank.py:55-77` ahora tiene `_: str = Depends(require_admin)`. El endpoint ya no es accesible sin JWT de admin válido.

---

### SEV-2: Payment Bypass — verify_usdc_payment early returns
**Estado: CORREGIDO**

`backend/app/services/web3_service.py:559-578`: ambos early-return `True` (`0x_mock` prefix y `USDC_ADDRESS` vacío) están gateados en `settings.BLOCKCHAIN_MODE == "local"`. En producción retornan `False`. `config.py:121-124` agrega un `model_validator` que falla en startup si `USDC_ADDRESS` está vacío en modo no-local.

---

### SEV-3: Privy JWT Auth Bypass
**Estado: CORREGIDO**

`backend/app/core/auth.py:35-66`: el fallback `?user_id=` ahora requiere `BLOCKCHAIN_MODE == "local" and not PRIVY_APP_ID`. Con `PRIVY_APP_ID` seteado, sigue el path de verificación completo ES256/JWKS.

---

### SEV-4: settle_axolotito_escrow Race Condition
**Estado: CORREGIDO**

`backend/app/api/v1/endpoints/multiplayer.py:637-641`: Axolotito se obtiene con `.with_for_update()`. Status check ocurre después del lock. Wallet con `for_update=True` en línea 662.

---

### SEV-5: Market Buy — wallets sin lock
**Estado: CORREGIDO**

`backend/app/api/v1/endpoints/market.py:145-146`: `buyer_wallet` y `seller_wallet` se obtienen con `for_update=True`.

---

### SEV-6: CORS Wildcard Origin Regex
**Estado: CORREGIDO**

`backend/app/main.py:426-432`: `allow_origin_regex` eliminado. Solo lista explícita de `allow_origins`.

---

### SEV-7: RNG inseguro en _try_legendary_drop
**Estado: AÚN VULNERABLE**

`backend/app/api/v1/endpoints/shop.py:417`: `_try_legendary_drop()` todavía usa `rand = random.random()` (Mersenne Twister) en vez del `_rng = random.SystemRandom()` definido en línea 19. La función migró de la línea reportada previamente (477) pero el bug sobrevivió.

**Fix (1 línea):** Cambiar `rand = random.random()` → `rand = _rng.random()` en `shop.py:417`.

---

### SEV-8: Secrets en .env en git
**Estado: CORREGIDO**

`.env` removido del tracking de git. `.gitignore` actualizado.

---

### SEV-9: Checkout failure path — orden stranded
**Estado: CORREGIDO**

`backend/app/services/checkout_service.py:239-263`: en fallo de verificación, se llama `session.delete(processed_entry)` y `order.status` regresa a `AWAITING_PAYMENT` con `order.tx_hash_payment = None`.

---

### SEV-10: Simulation include_user — inyección subprocess
**Estado: CORREGIDO**

`backend/app/api/v1/endpoints/admin.py:828-830`: `include_user` validado con `re.fullmatch(r"did:privy:[a-zA-Z0-9_-]+", ...)`. Estado usa `threading.Lock`.

---

### SEV-11: BuyRequest.user_id mass assignment
**Estado: CORREGIDO**

`backend/app/api/v1/endpoints/shop.py:21-23`: `BuyRequest` y `GashaponRollRequest` ya no exponen `user_id`. Se usa `verified_user_id` del dependency injection.

---

### SEV-12: Stock count via description.contains()
**Estado: CORREGIDO**

`backend/app/services/shop_service.py:67-88`: Stock usa `TransactionLedger.item_id == item.id`. Las queries `LIKE` eliminadas.

---

### SEV-13: Promo code — email del cliente
**Estado: CORREGIDO**

`backend/app/services/promo_service.py:103-108`: usa `email=user.email` del objeto `User`. Rechaza si email no está verificado.

---

### SEV-14: Simulation report — path traversal
**Estado: PARCIALMENTE CORREGIDO**

`backend/app/api/v1/endpoints/admin.py:787-793`: el fix actual valida `os.path.basename(path) != "simulation_report.txt"`. Esto previene archivos con nombre diferente pero **no valida que el archivo esté dentro de `/app/`**. Un atacante que controle `SIMULATION_REPORT_PATH` puede apuntar a `/secrets/simulation_report.txt` y la validación pasa.

**Fix completo:**
```python
import pathlib
resolved = pathlib.Path(path).resolve()
if not resolved.is_relative_to(pathlib.Path("/app")):
    raise HTTPException(status_code=403, detail="Acceso denegado.")
```

---

## Parte 2 — Hallazgos Nuevos

---

### [HIGH] NEW-1: Double-Claim Race Condition en rewards/claim

**Ubicación:** `backend/app/api/v1/endpoints/rewards.py:25-30`

**Descripción:** El endpoint `POST /api/v1/rewards/claim` obtiene la fila `PendingReward` sin row lock. El wallet sí tiene `for_update=True` (línea 39), pero `PendingReward` nunca se re-lee después del wallet lock. Dos requests concurrentes del mismo usuario leen `claimed == False`, pasan el check, ambas serializan en el wallet lock y ambas acreditan el reward.

**Impacto:** Un jugador puede reclamar su reward de lanzamiento dos o más veces, duplicando los AXF/FRJ iniciales.

**PoC:** Enviar dos POST simultáneos a `/api/v1/rewards/claim` desde la misma sesión autenticada.

**Fix:**
```python
pending = session.exec(
    select(PendingReward).where(
        PendingReward.user_id == verified_user_id,
        PendingReward.claimed == False,
    ).with_for_update()
).first()
```

---

### [HIGH] NEW-2: Double-Hatch Race Condition — Duplicación de NFT

**Ubicación:** `backend/app/api/v1/endpoints/incubation.py:214`

**Descripción:** `hatch_webito` obtiene `WebitoIncubation` con `session.get()` — sin pessimistic lock. Dos requests concurrentes a `POST /api/v1/incubation/hatch/{id}` cargan el mismo registro, pasan todos los guards (límite axo, tiempo, imprinting), y ambos llaman `_perform_hatch` que hace mint on-chain de un Axolotito nuevo (línea 383). Compárese con `start_imprinting` (línea 499) que correctamente usa `.with_for_update()`.

**Impacto:** Un solo huevo produce dos Axolotito NFTs on-chain. El segundo puede carecer de registro DB válido pero el token blockchain ya existe, creando un asset on-chain huérfano y distorsión económica.

**Fix:** Reemplazar `session.get(WebitoIncubation, incubation_id)` con:
```python
incubation = session.exec(
    select(WebitoIncubation)
    .where(WebitoIncubation.id == incubation_id)
    .with_for_update()
).first()
```
Y re-verificar el límite de axos después del lock.

---

### [HIGH] NEW-3: GET /cave/status — Muta Estado Sin Autenticación + Leak de Wallet

**Ubicación:** `backend/app/api/v1/endpoints/cave_expansion.py:378-404`

**Descripción:** `GET /api/v1/cave/status` acepta `user_id` como query param abierto sin dependency de autenticación. Cuando el timer de excavación ha transcurrido (líneas 391-404), este endpoint **de lectura** llama `_grant_egg_reward()`, incrementa `user.cave_level`, hace commit a la DB y retorna balances del wallet (`wallet.axogemas`, `wallet.frijolitos`).

**Impacto (mutación de estado):** Cualquier persona sin autenticación puede completar expansiones de cueva para cualquier usuario, saltándose el timer de espera y la opción de acelerar con AXG. En niveles 7-8 esto otorga huevos Webito Astral gratuitamente.

**Impacto (filtración de datos):** El objeto `wallet` en línea 478 expone balances de activos con valor monetario real a cualquier solicitante no autenticado.

**Fix:**
1. Agregar `verified_user_id: str = Depends(get_verified_user_id)` a `get_cave_status`
2. Mover la lógica de auto-resolve (otorgar huevo/subir nivel) a `POST /cave/expand/complete` o al endpoint de aceleración
3. Separar datos públicos de la cueva de datos sensibles del wallet

---

### [HIGH] NEW-4: F2P Fragment Farm — Axolotitos Astrales Ilimitados Gratis

**Ubicación:** `backend/app/api/v1/endpoints/f2p.py:62-155`

**Descripción:** Tres problemas combinados:

1. **`won` es parámetro del cliente sin prueba:** El booleano `won` en línea 62 es un query param del cliente. No hay verificación server-side de que el jugador realmente jugó o vio algo.

2. **Fragmentos sin límite:** GAL tiene cap de 10/día (`DAILY_CAP_GAL`), pero los fragmentos se incrementan sin condición en línea 146 (`user.f2p_astral_fragments += frags`). No hay cap diario ni total. Con suficientes calls, `FRAGMENTS_TO_HATCH` fragmentos = un huevo Astral Webito gratis.

3. **Race condition en cap de GAL diario:** El `User` row se obtiene sin `for_update` (línea 79), permitiendo que dos calls concurrentes lean `earned_today = 0` y ambas acrediten GAL, bypaseando el límite de 10 GAL/día.

**Impacto:** Un atacante puede acumular Axolotitos Astrales (asset de mayor valor) de forma ilimitada vía calls automatizados a la API. El bypass de GAL diario es un exploit económico secundario.

**Fix:**
- Agregar `@limiter.limit("20/hour")` (o más restrictivo) al endpoint
- Agregar cap diario de fragmentos (no solo GAL): `max_frags_per_day`
- Agregar cooldown entre calls (ej: mínimo 3 minutos entre rewards)
- Lock `User` row con `for_update=True` antes de actualizar contadores diarios

---

### [MEDIUM] NEW-5: NameError en Cave Expand Logro Path — DoS

**Ubicación:** `backend/app/api/v1/endpoints/cave_expansion.py:599`

**Descripción:** Dentro de `start_expansion` (rama `path == "logro"`), línea 599 llama `_get_user_stats(session, user_id)`. La función tiene como parámetro `verified_user_id` — no existe variable `user_id` en scope. Esto levanta `NameError: name 'user_id' is not defined` en runtime.

**Impacto:** Cualquier usuario autenticado que intente expandir su cueva por el path de logro recibe 500 Internal Server Error. DoS contra el feature de expansión por logros para todos los usuarios.

**Fix (1 línea):** `stats = _get_user_stats(session, verified_user_id)` en `cave_expansion.py:599`.

---

### [MEDIUM] NEW-6: Win-Streak + Luck Bonus — Extracción Ilimitada de GAL

**Ubicación:** `backend/app/api/v1/endpoints/game.py:463-468`

**Descripción:** El bonus de win-streak (`min(50, streak * 15)%` cap en +50%) se combina multiplicativamente con el luck bonus (`stat_luck / 1000.0 * win_prize`). Un Axolotito de stat_luck=100 en racha de 3 victorias recibe `win_prize * 1.01 * 1.45`. En la sala champion (premio 290 GAL, fee 50 GAL), el payout neto es ~+374 GAL por victoria. Un jugador hábil en sala champion con Axolotito de alta suerte puede extraer GAL ilimitadamente si mantiene racha.

**Nota:** Esto puede ser diseño intencional (el GDD menciona "negative house edge at high focus como feature"). No es un bug de código per se, pero es riesgo económico real a escala.

**Recomendación:** Documentar el payout máximo teórico por partida. Evaluar si luck bonus y streak bonus deben ser mutuamente excluyentes o si streak solo aplica sobre prize base.

---

### [MEDIUM] NEW-7: Cave Expansion — Double Reward via GET Concurrente

**Ubicación:** `backend/app/api/v1/endpoints/cave_expansion.py:391-404`

**Descripción:** Incluso para usuarios autenticados, la lógica de auto-resolve dentro de `GET /status` no está protegida contra calls concurrentes. Dos GETs simultáneos (ej: dos tabs abiertas) ambos leen `elapsed >= timedelta(hours=total_hours)`, ambos llaman `_grant_egg_reward()` y hacen commit. El `cave_expansion_target_level = None` se setea solo después de que ambas sesiones lo leyeron como no-null.

**Impacto:** Un usuario puede recibir dos huevos de una sola expansión completada.

**Fix:** Mover el bloque de auto-resolve a endpoints POST, o usar `with_for_update()` al obtener el `User` row en el check de auto-resolve. Alternativamente, update condicional: `UPDATE ... WHERE cave_expansion_target_level = X AND cave_level = X-1`.

---

### [MEDIUM] NEW-8: VIP Scheduler — Renovación Sin Lock Atómico en User

**Ubicación:** `backend/app/services/vip_scheduler.py:37-122`

**Descripción:** El loop de auto-renovación VIP procesa todos los usuarios sin row lock en `User`. El `wallet` tiene `for_update=True` (línea 104), pero `user` viene del list `all_users` obtenido sin lock en línea 37. Si un request API modifica `user.vip_expires_at` o `wallet.axogemas` durante el loop, el scheduler puede sobrescribir esos cambios. Si el scheduler crashea entre deducir el wallet y extender `vip_expires_at`, el usuario pierde AXG sin recibir la extensión VIP.

**Recomendación:** Usar sesiones individuales por renovación de usuario, con row locks en User y Wallet, y cada renovación en su propio try/except con rollback.

---

### [MEDIUM] NEW-9: Simulation Report — Validación de Path Incompleta (residual SEV-14)

Ver descripción en SEV-14 arriba. La validación actual (`os.path.basename`) no es suficiente. Implementar `pathlib.Path.resolve().is_relative_to("/app/")`.

---

### [LOW] NEW-10: hatch_webito — user_id como Query Param (Mass Assignment Residual)

**Ubicación:** `backend/app/api/v1/endpoints/incubation.py:204-212`

**Descripción:** `POST /incubation/hatch/{incubation_id}` acepta `user_id: str` como query param plano. El check `if user_id != verified_user_id` es correcto pero perpetúa el patrón frágil de SEV-11. Si el check se elimina por accidente en un refactor, cualquier usuario puede hatchear el huevo de otro.

**Fix:** Eliminar el `user_id` query parameter. El check de ownership `incubation.user_id != verified_user_id` en línea 215 ya provee la verificación correcta usando la identidad del JWT.

---

### [LOW] NEW-11: Frontend — USDC Address Fallback a Treasury

**Ubicación:** `frontend/components/CryptoCheckout.tsx:218`

**Descripción:**
```typescript
params: [{ from, to: USDC_ADDRESS || order.pay_to, data, value: '0x0' }],
```
Cuando `NEXT_PUBLIC_USDC_ADDRESS` no está seteado, el target cae a `order.pay_to` (address del treasury). Esto enviaría el monto como native transfer al treasury en vez de llamar `transfer()` en el contrato ERC-20 de USDC. La transacción revierte o no mueve USDC real. La verificación server-side fallará correctamente, pero la UX es confusa y el usuario puede pensar que pagó.

**Fix:** Validar explícitamente que `USDC_ADDRESS` es un address válido antes de renderizar la opción de pago con wallet Privy. Mostrar error visible si falta.

---

### [LOW] NEW-12: Player-Hosted Room — Host No Paga Entry Fee

**Ubicación:** `backend/app/api/v1/endpoints/multiplayer.py:351-424`

**Descripción:** `POST /multiplayer/create-room` crea sala sin cobrarle stake al host. Los jugadores que se unen vía `join_player_room` pagan GAL en escrow (línea 549), pero el host crea la sala gratis. El host controla cuándo inicia el juego; si la lógica de juego no está completamente implementada, los joiners tienen GAL en riesgo sin reciprocidad del host.

**Recomendación:** Requerir que el host pague el mismo entry fee que los joiners (stake simétrico), o deshabilitar el join endpoint hasta que la lógica de juego para salas de jugador esté implementada.

---

### [LOW] NEW-13: SHA-256 para Room Passwords

**Ubicación:** `backend/app/api/v1/endpoints/multiplayer.py:52-53`

**Descripción:**
```python
def _hash_password(pw: str) -> str:
    return hashlib.sha256(f"axolotto_salt_{pw}".encode()).hexdigest()
```
SHA-256 con salt estático es trivialmente bruteforceable para passwords cortos. Si alguien obtiene el hash (backup leak, SQL injection), puede revertir passwords cortos en segundos.

**Fix:** Usar `bcrypt` o `argon2`. O documentar que room passwords son de baja criticidad (salas efímeras) y aceptar el riesgo.

---

### [INFO] NEW-14: Smart Contracts — Sin Vulnerabilidades Nuevas

Los contratos nuevos (`Axoficha.sol`, `Frijolito.sol`, `Consumables.sol`) siguen el mismo patrón seguro: `^0.8.24` (aritmética checked), `onlyController` en mint/burn, `onlyOwner` en configuración, sin external calls que puedan re-entrar. No se identificaron reentrancy, integer overflow, ni problemas de access control nuevos.

**Nota persistente de SEV-15:** Toda la seguridad on-chain está delegada a la treasury private key del backend. Rotar a hardware wallet o KMS antes de mainnet.

---

### [INFO] NEW-15: Frontend — Sin Issues Críticos de Client-Side Trust

`CryptoCheckout.tsx` usa correctamente `order.pay_to` (address del treasury desde el backend). Precios y cantidades de AXG son server-authoritative. `tx_hash` viene del blockchain provider (Privy), no del cliente. El único riesgo es NEW-11. No se identificaron vectores de manipulación de balance o bypass de precio en el cliente.

---

## Tabla Resumen

| ID | Severity | Estado | Descripción | Archivo |
|----|----------|--------|-------------|---------|
| SEV-1 | CRITICAL | ✅ CORREGIDO | Admin deposit sin auth | bank.py:55 |
| SEV-2 | CRITICAL | ✅ CORREGIDO | USDC payment bypass | web3_service.py:559 |
| SEV-3 | CRITICAL | ✅ CORREGIDO | Privy JWT auth bypass | auth.py:35 |
| SEV-4 | HIGH | ✅ CORREGIDO | settle escrow race | multiplayer.py:637 |
| SEV-5 | HIGH | ✅ CORREGIDO | Market buy wallet race | market.py:145 |
| SEV-6 | HIGH | ✅ CORREGIDO | CORS wildcard regex | main.py |
| SEV-7 | MEDIUM | ✅ CORREGIDO | `random.random()` en legendary drop | shop.py:417 |
| SEV-8 | HIGH | ✅ CORREGIDO | Secrets en .env git | .env |
| SEV-9 | MEDIUM | ✅ CORREGIDO | Checkout stranded order | checkout_service.py |
| SEV-10 | MEDIUM | ✅ CORREGIDO | Simulation include_user injection | admin.py:828 |
| SEV-11 | MEDIUM | ✅ CORREGIDO | BuyRequest.user_id mass assignment | shop.py |
| SEV-12 | MEDIUM | ✅ CORREGIDO | Stock count via LIKE query | shop_service.py |
| SEV-13 | LOW | ✅ CORREGIDO | Promo code email del cliente | promo_service.py |
| SEV-14 | LOW | ✅ CORREGIDO | Simulation report path traversal | admin.py:787 |
| NEW-1 | HIGH | ✅ CORREGIDO | Double-claim en rewards/claim | rewards.py:25 |
| NEW-2 | HIGH | ✅ CORREGIDO | Double-hatch duplica NFT on-chain | incubation.py:214 |
| NEW-3 | HIGH | ✅ CORREGIDO | GET /cave/status muta estado sin auth + leak wallet | cave_expansion.py:378 |
| NEW-4 | HIGH | ✅ CORREGIDO | F2P fragments ilimitados → Astrales gratis | f2p.py:62 |
| NEW-5 | MEDIUM | ✅ CORREGIDO | NameError en cave logro path (DoS) | cave_expansion.py:599 |
| NEW-6 | MEDIUM | ✅ CORREGIDO | Win-streak + luck bonus extracción ilimitada GAL | game.py:463 |
| NEW-7 | MEDIUM | ✅ CORREGIDO | Double cave reward via GET concurrente | cave_expansion.py:391 |
| NEW-8 | MEDIUM | ✅ CORREGIDO | VIP scheduler sin lock atómico en User | vip_scheduler.py:37 |
| NEW-9 | MEDIUM | ✅ CORREGIDO | Simulation report path validación incompleta | admin.py:790 |
| NEW-10 | LOW | 🆕 NUEVO | hatch_webito user_id query param residual | incubation.py:204 |
| NEW-11 | LOW | 🆕 NUEVO | Frontend USDC address fallback a treasury | CryptoCheckout.tsx:218 |
| NEW-12 | LOW | 🆕 NUEVO | Host no paga entry fee en player-hosted rooms | multiplayer.py:351 |
| NEW-13 | LOW | 🆕 NUEVO | SHA-256 para room passwords | multiplayer.py:52 |
| NEW-14 | INFO | ✅ REVISADO | Contratos — sin vulnerabilidades nuevas | contracts/src/ |
| NEW-15 | INFO | ✅ REVISADO | Frontend — sin issues client-side críticos | CryptoCheckout.tsx |

---

## Ruta Crítica Antes de Lanzar

### Inmediato (antes de cualquier USDC real) — COMPLETADO 2026-06-04

1. ✅ **NEW-3 (HIGH)** — `GET /cave/status` ahora requiere `Depends(get_verified_user_id)` + `with_for_update()` en User. Commit `2f49b40`.

2. ✅ **NEW-4 (HIGH)** — F2P watch-reward: User bloqueado con `for_update`, cap diario de fragmentos `DAILY_CAP_FRAGS=10`, migración `d1e2f3a4b5c6`. Commit `2f49b40`.

3. ✅ **SEV-7 (MEDIUM)** — `rand = _rng.random()` en `shop.py:417`. Commit `2f49b40`.

4. ✅ **NEW-1 (HIGH)** — `PendingReward` con `.with_for_update()` en `rewards/claim`. Commit `2f49b40`.

5. ✅ **NEW-2 (HIGH)** — `WebitoIncubation` con `select().with_for_update()` en `hatch_webito`. Commit `2f49b40`.

6. ✅ **NEW-5 (MEDIUM)** — `user_id` → `verified_user_id` en `cave_expansion.py` rama logro. Commit `2f49b40`.

### Sprint siguiente — COMPLETADO 2026-06-04

7. ✅ **SEV-14/NEW-9 (MEDIUM)** — `pathlib.Path.resolve().is_relative_to("/app/")` en `admin.py:791`. Commit `fix-security-sprint2`.

8. ✅ **NEW-7 (MEDIUM)** — Ya corregido por fix de NEW-3: `with_for_update()` en User dentro de `GET /cave/status` garantiza que requests concurrentes serialicen y solo uno otorgue el huevo. Commit `2f49b40`.

9. ✅ **NEW-8 (MEDIUM)** — VIP auto-renovación en `_auto_renew_user()` separada: sesión individual por usuario, `with_for_update()` en User y Wallet, rollback automático si falla entre deducir AXG y extender VIP. Commit `fix-security-sprint2`.

10. ✅ **NEW-6 (MEDIUM)** — `MAX_WIN_MULTIPLIER = 1.65` en `game.py`: luck (+10%) × streak (+50%) = 1.65x payout máximo documentado y aplicado como hard cap. Champion: max 478.5 GAL bruto por victoria. Commit `fix-security-sprint2`.

### Pre-mainnet (antes de USDC real en circulación)

- Rotar `TREASURY_PRIVATE_KEY` a hardware wallet o KMS; nunca usar key de Anvil en prod
- ✅ **Rate limiting (`slowapi`) en endpoints de pago y auth** — Completado el 2026-06-04
- Constraints DB: `CHECK (gemas_alga >= 0)`, `CHECK (axogema >= 0)` en `Wallet`
- Monitoreo/alertas en: balances negativos, calls de admin deposit, mint transactions en bulk, intentos de auth fallidos
- Audit de terceros en contratos antes de manejar fondos reales en mainnet

---

## Actividades Propuestas (Puntos de Bajo Impacto / "Low-Hanging Fruits")

A continuación se detallan las actividades no tan pesadas identificadas en esta auditoría, junto con sus pasos accionables correspondientes:

### Actividad 1: Implementar Rate Limiting (`slowapi`) en endpoints de pago y auth (COMPLETADA)
- **Descripción:** Proteger endpoints críticos contra ataques de denegación de servicio (DoS) o fuerza bruta mediante límites por IP.
- **Pasos:**
  1. [x] Identificar todos los endpoints de pago y autenticación en el backend:
     - `POST /api/v1/bank/checkout/crypto` (creación de orden de compra)
     - `POST /api/v1/bank/transfer` (transferencia P2P de fondos)
     - `POST /api/v1/rewards/claim` (reclamo de recompensas de lanzamiento)
  2. [x] Modificar la firma de estos endpoints en `backend/app/api/v1/endpoints/checkout.py`, `bank.py` y `rewards.py` para que acepten el parámetro `request: Request`.
  3. [x] Aplicar el decorador `@limiter.limit("X/minute")` importando `limiter` desde `app.core.limiter`. Valores propuestos:
     - `/bank/checkout/crypto`: `10/minute`
     - `/bank/transfer`: `5/minute`
     - `/rewards/claim`: `5/minute`
  4. [x] Agregar pruebas unitarias en `backend/tests/unit/test_security_hardening.py` que simulen peticiones concurrentes y verifiquen la respuesta `429 Too Many Requests`.

### Actividad 2: Resolver NEW-10 (user_id residual query parameter en hatch_webito)
- **Descripción:** Eliminar el parámetro residual `user_id` en el endpoint de incubación que abre la puerta a inconsistencias si se modifica por error.
- **Pasos:**
  1. Modificar la firma del endpoint `hatch_webito` en `backend/app/api/v1/endpoints/incubation.py:204` para eliminar `user_id: str`.
  2. Eliminar el check `if user_id != verified_user_id:` de las líneas 211-212.
  3. En la línea 229, cambiar la búsqueda del usuario para que use directamente `verified_user_id`:
     `user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()`
  4. Actualizar las pruebas unitarias que simulan llamadas a este endpoint para que no envíen el parámetro de consulta `user_id`.

### Actividad 3: Resolver NEW-11 (Validación preventiva de USDC_ADDRESS en frontend)
- **Descripción:** Validar que la dirección de USDC esté configurada en el cliente y mostrar un error explícito si falta, previniendo fallbacks incorrectos.
- **Pasos:**
  1. En `frontend/components/CryptoCheckout.tsx`, validar que `USDC_ADDRESS` (línea 25) tenga el formato de dirección Ethereum correcto (hexadecimal de 40 caracteres con prefijo `0x`).
  2. En el método `handlePrivyPay` (línea 199), comprobar que `USDC_ADDRESS` existe y es válida. Si no es así, lanzar un error descriptivo en la UI como *"La dirección de contrato USDC no está configurada"*.
  3. Modificar la línea 218 (`to: USDC_ADDRESS || order.pay_to`) para evitar el fallback a la dirección del tesoro (`order.pay_to`), asegurando que solo se envíen transacciones al contrato ERC-20 real.

### Actividad 4: Resolver NEW-13 (Mejorar seguridad de contraseñas de salas o documentar riesgo)
- **Descripción:** SHA-256 con salt estático es vulnerable a ataques de fuerza bruta rápidos si se expone la base de datos.
- **Pasos:**
  1. Opción recomendada: Actualizar la función `_hash_password` en `backend/app/api/v1/endpoints/multiplayer.py` para usar `bcrypt` o `argon2` para hashes seguros de contraseñas.
  2. Alternativa: Si las contraseñas de las salas son de baja criticidad (efímeras), agregar un comentario explícito en el código documentando la aceptación del riesgo técnico de usar SHA-256 para esta funcionalidad específica.
