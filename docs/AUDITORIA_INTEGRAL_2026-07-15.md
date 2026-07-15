# Auditoría integral 360° de Axolotto

**Fecha de corte:** 15 de julio de 2026  
**Repositorio/branch:** `dev`  
**Commit auditado:** `e12f5b1`  
**Estado del árbol al iniciar:** limpio; branch local 39 commits por delante de `origin/dev`  
**Áreas:** producto, frontend, UX/accesibilidad, backend, seguridad, Web3, smart contracts, economía/jugabilidad, DevOps/QA, privacidad y marco legal mexicano.

> **Aviso importante:** este documento es una auditoría técnica y de riesgos, no una opinión jurídica, fiscal, contable ni regulatoria. Las conclusiones legales son señales de riesgo que deben validarse por escrito con abogados mexicanos especializados en juegos y sorteos, prevención de lavado, fintech/activos virtuales, consumo, privacidad y fiscalidad antes de recibir dinero real o habilitar premios con valor.

---

## 1. Dictamen ejecutivo

### Veredicto

**NO-GO para lanzar públicamente con dinero real, tokens con valor, marketplace/DevEx o contratos en mainnet.**  
**GO condicionado para continuar como entorno cerrado de desarrollo**, sin dinero real, sin promesas de retiro/valor y con infraestructura de desarrollo limitada a loopback/VPN.

Axolotto ya tiene una base considerable y varias remediaciones de seguridad bien encaminadas, pero el producto que describe la documentación no coincide todavía con el que ejecuta el código. Hay cinco clases de bloqueadores:

1. **Clasificación legal no resuelta.** Se cobra una moneda adquirible, interviene el azar, existen premios/jackpot y se contempla una ruta de monetización o retiro indirecto. Llamar a FRJ “soft currency” o separar el DevEx no elimina por sí solo el riesgo de juego con apuesta, actividad vulnerable, protección al consumidor o activo virtual.
2. **Flujos Web3/económicos no atómicos.** Varias operaciones consideran “éxito” la mera difusión de una transacción, el worker de outbox no se arranca desde la aplicación y hay emisiones/recompensas que confían en señales del cliente.
3. **Integración de juego incompleta.** El modo manual no recibe su tablero, puede reconectar en bucle; el modo automático puede generar polling agresivo; patrones, precios, payout y replay difieren entre cliente y servidor.
4. **Contratos aún no desplegables como sistema seguro.** Hay control administrativo total en una sola cuenta, rutas funcionalmente rotas en Reciclón/disolución, confianza excesiva en parámetros del backend y un script que omite contratos necesarios.
5. **Sin baseline de release.** El build y el typecheck del frontend pasan, pero lint arroja 542 errores; la suite backend queda en 746 aprobadas/73 fallidas/1 omitida; no hay CI; dependencias y artefactos no son reproducibles desde un clon limpio.

### Madurez estimada

| Dimensión | Estado | Comentario ejecutivo |
|---|---:|---|
| Visión y profundidad de producto | **Alta** | Mundo, colección, crianza, economía y modos de juego tienen amplitud real. |
| Arquitectura de prototipo | **Media-alta** | Separación frontend/backend/contratos y servicios de dominio razonable. |
| Coherencia funcional end-to-end | **Baja-media** | Contratos HTTP/WS, precios, patrones y settlements divergen. |
| Seguridad de aplicación | **Media** | Hay buenas defensas recientes, pero permanecen rutas críticas y carreras. |
| Seguridad/operación Web3 | **Baja** | Hot key, broadcast sin finality, outbox incompleto y despliegue incongruente. |
| UX/accesibilidad | **Media-baja** | Identidad rica, pero modos críticos y navegación asistiva no están listos. |
| QA/entrega reproducible | **Baja** | Suites amplias pero rojas, casi sin E2E frontend y sin CI. |
| Preparación regulatoria | **Muy baja** | Sin opinión jurídica externa ni criterio/resolución de autoridad, KYC/AML completo o superficies legales reales. |

### Fortalezas que conviene preservar

- Autenticación Privy de producción valida ES256, audiencia e issuer; el bypass de desarrollo está bloqueado fuera de modo local (`backend/app/core/auth.py:37-76`, `backend/app/core/config.py:218-241`).
- CORS está limitado a orígenes explícitos (`backend/app/main.py:492-499`).
- Wallet y transacciones sensibles han migrado en buena parte a unidades mínimas enteras, restricciones no-negativas, claves únicas y bloqueos transaccionales (`backend/app/models/economy.py:43-57,132-171`).
- Ya existen `ProcessedTransaction`, HMAC con comparación constante, outbox transaccional y código de reconciliación: la dirección arquitectónica es correcta, aunque su operación aún no lo sea.
- En CPU, el resultado económico nace en backend; el cliente debería limitarse a reproducir el trace autoritativo (`frontend/hooks/useCpuGame.ts:228-273`).
- La lógica manual comprueba que las marcas correspondan a cartas cantadas (`backend/app/services/game_logic.py:380-386`).
- El motor 3D limita pixel ratio, pausa por visibilidad y contempla calidad/movimiento reducido (`frontend/components/world3d/ThreeWorldEngine.ts:102-105,225-240`).
- El tutorial persiste checkpoint en backend y permite reanudación (`frontend/components/tutorial/TutorialFlow.tsx:167-180,216-251`).
- Los 29 tests Foundry disponibles pasan. Esto da una base útil, aunque no cubre varios flujos rotos ni sustituye una auditoría externa.
- El repositorio no contiene secretos de entorno trackeados en el árbol actual; los `.env` inspeccionados están ignorados. Esto no confirma que nunca hayan estado en imágenes, historial o registros.

---

## 2. Alcance, método y límites

### Qué se revisó

- Aproximadamente 964 archivos: backend FastAPI/SQLModel/Web3.py, frontend Next/React/Three.js/PWA, contratos Solidity/Foundry, Docker/scripts, documentación, wiki, tests y herramientas internas.
- Arquitectura y flujos de autenticación, wallet, pagos, checkout, marketplace, escrow, referrals, multijugador, WebSocket, tienda, VIP, jackpot, tutorial, PWA y despliegue.
- Contratos, permisos, custodia, supply, despliegue y correspondencia con el backend.
- GDD/Biblia, economía, incentivos, antifraude, claridad comercial y claims públicos.
- Fuentes oficiales mexicanas vigentes sobre juegos/sorteos, AML, consumo, privacidad, impuestos, activos virtuales y propiedad intelectual.

### Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| `npm run build` | **Pasa** |
| `npx tsc --noEmit` | **Pasa** |
| `npm run lint` | **Falla:** 753 problemas; 542 errores y 211 warnings |
| `npm audit --omit=dev` | **36 vulnerabilidades:** 7 altas y 29 moderadas |
| Foundry en imagen Docker | **29/29 pasan** (17 GameContracts, 12 MarketEscrow) |
| Backend en contenedor efímero | **746 pasan, 73 fallan, 1 omitida** |
| Playwright/E2E | No ejecutado: la configuración espera servidor externo y el proyecto prohíbe levantarlo durante esta auditoría |

Las 73 fallas backend no equivalen automáticamente a 73 defectos productivos. Se agrupan en: migración incompleta AXG/GAL→AXF/FRJ; expectativas incompatibles entre unidades humanas y mínimas; artefactos de contratos ausentes en el contenedor declarado; rutas de simulación calculadas contra otro layout; y posibles regresiones funcionales. La conclusión relevante para release es que **no existe una baseline verde y reproducible**.

### Límites

- Revisión estática y pruebas locales; no hubo acceso a producción, balances reales, wallets, bytecode desplegado, configuración de firewall, nube, logs, métricas, backups ni KYC.
- No se realizó auditoría criptográfica formal, fuzzing/invariants exhaustivos, pentest activo, carga, caos, Lighthouse ni QA visual en navegadores/dispositivos.
- No se verificó el historial completo de secretos, capas de imágenes ya publicadas ni registros externos.
- `fog-context`, requerido por las instrucciones del repositorio, no estaba disponible en esta sesión. Se compensó con inspección directa y revisión paralela, pero no se pudo consultar impacto semántico ni registrar decisiones allí.
- Parte de la documentación canónica referenciada no existe en su ruta actual: `docs/GDD.md` y `docs/vip_club_design.md`; se usaron versiones archivadas, Biblia, wiki y código real.

### Escala de prioridad

- **P0 — Bloqueador:** pérdida/creación de valor, incumplimiento probable, exploit sencillo o modo principal inoperable. Impide release.
- **P1 — Alto:** daño serio, inconsistencia económica, carrera, engaño comercial o deuda que vuelve insegura la operación.
- **P2 — Medio:** resiliencia, accesibilidad, mantenimiento o calidad que debe resolverse antes de escalar.
- **P3 — Bajo/deuda:** mejora estructural sin impacto inmediato demostrable.

---

## 3. Mapa consolidado de hallazgos

| ID | P | Área | Hallazgo | Estado recomendado |
|---|:---:|---|---|---|
| REG-01 | P0 | Legal/producto | Alta exposición a regulación de juegos con apuesta/sorteos | Opinión escrita + vía SEGOB/permiso si aplica, o rediseño |
| LEG-01 | P0 | Menores | Sin age gate/juego responsable; alcance regulatorio por precisar | Controles 18+ y criterio legal/autoridad |
| LEG-02 | P0 | AML/fintech | “Firewall FRJ” no elimina valor/conversión; KYC/AML incompleto | Pausar dinero/retiros; análisis LFPIORPI/LRITF |
| LEG-03 | P0 | Consumo | Sin T&C, cancelación ni precios/claims coherentes | Implementar y revisar antes de captación |
| LEG-04 | P1 | Privacidad | Sin aviso/ARCO/retención/respuesta a incidentes visibles | Programa de privacidad y seguridad |
| LEG-05 | P1 | Fiscal/financiero | IEPS/IVA/ISR/retenciones y clasificación financiera sin memo | Análisis firmado por flujo/entidad |
| LEG-06 | P1 | Marketing/IP | Claims falsos y activos IA/culturales sin expediente de derechos | Corregir copy y crear chain-of-title |
| SEC-01 | P0* | Pagos | Gateway siempre mock; endpoint de pago simulado puede acreditar gratis si queda accesible | Desmontar fuera de dev y crear gateway real |
| SEC-02 | P0 | Economía | Referral/F2P confían en hitos o resultado suministrados por cliente | Eventos server-side, prueba e idempotencia |
| W3-01 | P0 | Web3 | Broadcast se trata como éxito; no hay receipt/finality en ruta general | Máquina de estados y reconciliación |
| W3-02 | P1 | Web3 | Outbox no se inicia; crash deja `processing` y la ruta sync no hace claim seguro | Supervisor, lease/reaper y claim único |
| DATA-01 | P0 | Datos/economía | Checkout mezcla floats humanos con columnas/unidades mínimas | `int` end-to-end, migración y tests frontera |
| ECON-01 | P1 | Economía | Timeout hosted suma fee al escrow y deja estado/saldo inconsistente | Deshabilitar/corregir; invariant de conservación |
| ECON-02 | P1 | Balance | Parámetros sugieren EV CPU inflacionario; falta simulación vigente | Pausar multiplicadores y resimular |
| SC-01 | P0 | Contratos | ReciclonVault no puede recibir ERC-1155 ni quemar con permisos actuales | Rediseñar/reprobar flujo completo |
| SC-02 | P1 | Contratos | Disolver tabla no quema la carta ni reduce supply | Burn/backing e invariants |
| SC-03 | P0 | Contratos | Autoridad total concentrada en owner/hot key, sin roles/timelock/caps | Multisig, roles, pausa, caps, timelock |
| SC-04 | P0* | Custodia | Dirección ausente puede degradar escrow a hash mock fuera de tests | Fail-fast; cero fallback mock |
| SC-05 | P1 | Deploy | Script omite contratos y red documentada difiere de config | Pipeline único + manifest verificable |
| SC-06 | P1 | Supply | Caps comerciales prometidos no se aplican on-chain | Codificar caps o retirar promesa |
| FE-01 | P0 | Juego manual | Cliente nunca recibe su tablero; modo no puede operar correctamente | Payload privado + integración WS |
| FE-02 | P1 | Tiempo real | Riesgo de reconexión/polling continuo por identidades inestables | Reproducir, estabilizar y single-flight |
| GAME-01 | P0 | Economía/UX | UI CPU muestra cuotas/premios 4–10× distintos al backend | Fuente canónica, prueba contractual |
| GAME-02 | P0 | Reglas | Patrones manuales habilitados y validados no coinciden | Motor único de patrones |
| QA-01 | P1 | Release | 73 tests backend fallan; lint falla; sin CI | Baseline verde obligatoria |
| OPS-01 | P0* | Infra | Taskboard y Anvil permiten alto impacto si son accesibles fuera del host | Loopback/VPN/perfiles; rotar secretos |
| GOV-01 | P1 | Gobierno | GDD, Biblia, landing, precios y nombres AXG/GAL/AXF/FRJ divergen | Una fuente versionada y contratos generados |
| FE-03 | P1 | Integración | Chat WS, dos pestañas, salas hosted y settlement no cierran end-to-end | Esquema versionado + E2E multiusuario |
| GAME-03 | P1 | Confianza | Replay/XP/payout visual se estima o vuelve a sortear en cliente | Trace/settlement autoritativo |
| UX-01 | P1 | Accesibilidad | Tableros, mundo, hold button y modales no son operables por teclado/lector | WCAG 2.2 AA y alternativa DOM |
| BE-01 | P1 | Datos/ops | DDL dinámico y doble `create_all` compiten con Alembic | Migración única predeploy |
| BE-02 | P1 | Concurrencia | Schedulers, claims, inventario y locks no están listos para réplicas | Leader/locks/constraints/idempotencia |
| SEC-03 | P1 | Secretos | Docker `COPY . .` sin `.dockerignore`; el `.env` local puede entrar en capas | Rotar, BuildKit, usuario no-root |
| DEP-01 | P1 | Supply chain | 7 altas/29 moderadas; locks ignorados, requirements sin pins | Actualizar, fijar, SBOM y escaneo CI |
| UX-02 | P2 | Resiliencia | Auth/tutorial/store/lobby tienen estados eternos o silenciosos | Error/retry/timeouts observables |
| OPS-02 | P2 | Operación | Health superficial; sin readiness, métricas, PITR probado ni runbooks | SLO/alertas/backups/DR |
| PERF-01 | P2 | Frontend | `/play` monolítico; bundle/FPS no medidos; PWA no es offline | Split/lazy/budgets/matriz dispositivos |

`P0*` indica riesgo condicionado a exposición de red/configuración. Debe tratarse como P0 hasta demostrar controles externos.

---

## 4. Gobierno técnico y coherencia documental

### GOV-01 — No existe una fuente de verdad operativa (P1)

**Evidencia**

- `CLAUDE.md` enlaza `docs/GDD.md` y `docs/vip_club_design.md`, pero esas rutas no existen; las versiones disponibles están bajo `docs/completed/` y conservan AXG/GAL.
- La Biblia dice Plasma chain ID 9746 (`docs/AXOLOTTO_MASTER_BIBLE.md:242,420-424`), mientras `contracts/foundry.toml:12-17` configura Polygon Amoy.
- Backend VIP cobra 50/120/300 AXF y entrega 20/50/130 FRJ diarios (`backend/app/core/config.py:10-53`); wiki y documentos archivados publican otros importes.
- Landing anuncia 100/250/500 AXF, cashback, multiplicadores de XP y “ventajas fiscales” (`frontend/app/page.tsx:521-566`), contradictorios con backend.
- Frontend usa todavía una tasa hardcodeada `FRJ_PER_AXF = 4` con TODO (`frontend/lib/vip.ts:205-210`).
- Hay contratos legacy duplicados AXG/GAL junto a AXF/FRJ.

**Riesgo**

Errores de precio, publicidad engañosa, tests obsoletos, decisiones incompatibles y auditorías que revisan un producto distinto al desplegado.

**Corrección**

1. Declarar un único `PRODUCT_SPEC.md`/GDD vigente, con propietario y fecha.
2. Mantener precios, patrones, tiers, decimales, redes y direcciones en configuración canónica versionada.
3. Generar tipos/esquemas para Python, TypeScript y Solidity/deploy manifests; no duplicar valores monetarios en UI.
4. Marcar documentos históricos como archivados y no normativos; corregir enlaces del índice.
5. Añadir ADR para: fuente de verdad DB/on-chain, modelo de custodia, rol de AXF/FRJ, red destino y frontera regulatoria.

### GOV-02 — Documentos legales previos contienen supuestos no confiables (P1)

`docs/plan_economia_devex_fintech.md` y `docs/completed/AUDITORIA_LEGAL_FINANCIERA.md` no deben operar como autorización. Entre otros problemas, describen FRJ como off-chain/sin valor aunque existe como ERC-20, usan umbrales monetarios estáticos o antiguos, atribuyen retenciones automáticas a proveedores de pago y sugieren que una entidad offshore cambia por sí sola la sustancia regulatoria.

**Corrección:** conservarlos como antecedentes, encabezarlos “NO VIGENTE / NO ES OPINIÓN LEGAL” y reemplazarlos por memorandos firmados que describan exactamente los flujos actuales.

### Arquitectura entendida

El sistema combina:

- **Cliente Next/React/Three.js:** landing, autenticación Privy, mundo 3D, onboarding, tienda, CPU, auto multijugador y manual WS.
- **FastAPI/SQLModel/PostgreSQL:** fuente económica operativa, inventario, juego, marketplace, pagos, schedulers, reconciliación y puente Web3.
- **Solidity/Foundry:** AXF/FRJ ERC-20, NFTs/1155 de mascotas/cartas/consumibles, tablas, GameController, escrow y Reciclón.
- **Modelo híbrido:** una parte de propiedad/moneda pretende vivir on-chain, pero la resolución, jackpot, estados y muchos movimientos viven en DB.

La arquitectura híbrida es viable si se define qué sistema es autoritativo para cada activo y existe reconciliación. Hoy esa frontera es implícita y cambia por endpoint.

---

## 5. Backend, seguridad y datos

### SEC-01 — Pago simulado utilizable como pago real si queda montado (P0 condicionado)

**Hecho:** la factory siempre retorna `MockPaymentGateway` (`backend/app/services/payment_gateway/__init__.py:5-11`). `POST /api/v1/payments/mock/{gateway_ref}/pay` no exige autenticación y construye un webhook válido (`backend/app/api/v1/endpoints/payments.py:42-65`). Fuera de local se bloquea salvo `ALLOW_DEV_PAYMENTS=true`, pero `BLOCKCHAIN_MODE` tiene default local.

**Impacto:** quien conozca/obtenga un `gateway_ref` podría completar sin pago una compra o escrow en cualquier despliegue mal configurado. No se afirma que el endpoint esté expuesto actualmente en producción; el control depende de configuración.

**Corrección:** no registrar el router mock en artefactos de producción; protegerlo con identidad administrativa y red local aun en desarrollo; implementar gateway real con allowlist estricta de eventos; hacer fallar startup si se habilita fiat con factory mock.

### SEC-02 — Recompensas premium confiadas al cliente (P0)

- Referral acepta un `milestone` aportado por el cliente y recompensa `tutorial_done` sin prueba server-side (`backend/app/api/v1/endpoints/referrals.py:56-70`, `backend/app/services/referral_service.py:175-250`). El crédito no usa lock, ledger, outbox ni prueba on-chain (`backend/app/services/referral_service.py:288-300`).
- F2P recibe `won` desde el cliente; el límite diario reduce volumen, pero no prueba el resultado (`backend/app/api/v1/endpoints/f2p.py:63-158`).

**Impacto:** Sybil, emisión de AXF/FRJ, desincronización DB-chain y abuso automatizado.

**Corrección:** solo eventos de dominio internos e idempotentes (`event_id` único); el servidor deriva tutorial/partida/resultado; rewards mediante un ledger/outbox común; rate limits, device/risk scoring y pruebas de abuso.

### W3-01 — “Enviado” se confunde con “confirmado” (P0)

`web3_service._send_tx` retorna después de `send_raw_transaction`, sin esperar receipt, `status == 1` ni confirmaciones (`backend/app/services/web3_service.py:165-231`). Hay rutas que después confirman DB/outbox. Una transacción revertida, reemplazada, caída o reorganizada puede producir un activo fantasma o un doble estado.

**Corrección:** estados `created → signed → broadcast → mined → finalized` y `reverted/dropped`; persistir nonce/hash; confirmar receipt y número mínimo de bloques; reconciliar; nunca liberar custodia o acreditar valor final con solo un hash.

### W3-02 — Outbox conceptualmente correcto, operacionalmente incompleto (P1)

- Startup inicia schedulers multiplayer y VIP, no el worker de outbox (`backend/app/main.py:483-490`).
- La ruta normal sí selecciona con `FOR UPDATE SKIP LOCKED`, pero confirma `processing` antes del envío y no tiene lease/reaper (`backend/app/services/chain_outbox_worker.py:126-164`). Un crash puede dejar la fila atascada.
- La ruta `process_outbox_sync` consulta pendientes sin ese claim/lock (`backend/app/services/chain_outbox_worker.py:210-256`); si se invoca concurrentemente, no ofrece la misma exclusión.
- Ambas rutas marcan `confirmed` después de recibir un hash, no después de finality; ese defecto económico crítico queda cubierto por W3-01.

**Corrección:** worker separado y supervisado; un solo mecanismo de claim con lease/heartbeat y `SKIP LOCKED`; reaper; DLQ; clave idempotente de operación; estados mined/finalized; métricas de lag, reintentos y drift.

### DATA-01 — Unidades monetarias incompatibles en checkout (P0)

Packs y servicio usan cantidades humanas/float (`backend/app/services/checkout_service.py:29-33,133-146`), mientras el modelo declara `BigInteger` en unidades mínimas (`backend/app/models/economy.py:132-153`). La acreditación usa el valor raw (`backend/app/services/checkout_service.py:267-270`) y la verificación USDC vuelve a aplicar decimales en otra capa (`backend/app/services/web3_service.py:706-776`).

**Impacto:** truncamiento, rechazo o crédito por un factor de 10^decimales. Ejemplo observado: un pack rotulado 220 AXF puede persistir `220` unidades mínimas (= 0.000220 AXF si son 6 decimales).

**Corrección:** `int` desde request normalizado hasta DB/cadena; `Decimal` solo en la frontera de presentación; helpers únicos por token; constraints; migración auditada; tests para 0, mínimo, decimales, máximos y redondeo.

### ECON-01 — Timeout hosted corrompe el escrow y bloquea recuperación (P1)

El registro descuenta presupuesto a wallet y lo pone en escrow (`backend/app/api/v1/endpoints/multiplayer.py:193-203,616-623`). Cuando expira una sala hosted, el scheduler **suma** `fee × tablas` al escrow, aunque esa fee debía salir del presupuesto, elimina registros y finaliza la sala (`backend/app/services/multiplayer_service.py:223-244`). Sin embargo, `/settle` exige `waiting_settlement` (`backend/app/api/v1/endpoints/multiplayer.py:715-730`) y el timeout no establece ese estado.

**Impacto demostrado:** saldo de escrow inflado y fondos/axolotito potencialmente atrapados en un estado que el settlement normal rechaza. Ese crédito latente podría convertirse en emisión si una ruta de recuperación futura lo devuelve sin distinguir principal/fee, pero no se demostró un faucet cobrable repetible en el flujo actual.

**Corrección inmediata:** deshabilitar hosted rooms; reembolsar únicamente principal efectivamente cobrado; nunca incrementar escrow al cancelar; transicionar explícitamente a estado reembolsable; invariant `wallets + escrow + pools + treasury + jackpot = supply contable`; regression test de timeout, retry y concurrencia.

### DATA-02 — Operaciones económicas fuera del patrón atómico (P1)

- Admin deposit difunde AXF antes de actualizar DB y ledger, sin receipt/outbox (`backend/app/services/bank_service.py:52-97`).
- P2P mueve DB pero puede dejar tokens on-chain intactos; fee no tiene destino on-chain explícito (`backend/app/services/bank_service.py:113-183`).
- Mercado FRJ legacy entrega inventario DB antes de finalidad de cadena y solo crea ciertas operaciones si ambas wallets existen (`backend/app/api/v1/endpoints/market.py:154-261`).
- Pago USDC válido seguido de fallo de mint queda `FAILED` sin proceso robusto de retry/refund (`backend/app/services/checkout_service.py:267-285`).

**Corrección:** una máquina de estados económica común; source of truth explícito por activo; reserve/commit/release; idempotency; outbox; reversa/refund; reconciliación DB↔chain y doble-entry ledger.

### BE-01 — Migraciones en runtime compiten con Alembic (P1)

`backend/app/main.py:17-481` ejecuta dos `SQLModel.metadata.create_all` y decenas de `ALTER TABLE`, drops y updates en startup, incluidos campos monetarios `DOUBLE PRECISION`. Docker también ejecuta `alembic upgrade head`.

**Riesgo:** drift, locks al arrancar, carreras entre réplicas, fallos parciales y esquemas distintos según historia de despliegue.

**Corrección:** Alembic como único mecanismo; job predeploy con lock; migraciones forward/backward compatibles; startup read-only respecto al esquema.

### BE-02 — Concurrencia y ejecución multiproceso incompletas (P1)

- Schedulers se crean con `asyncio.create_task` sin handle, supervisión, shutdown ni leader election (`backend/app/main.py:483-490`). Cada réplica ejecutaría el mismo cron.
- Claims de staking/VIP/board no bloquean consistentemente todo el estado; inventario carece de `UNIQUE(user,item,...)` y `CHECK quantity >= 0` (`backend/app/models/items.py:54-60`).
- Locks de P2P por rol y no por ID canónico pueden deadlockear en transferencias opuestas.
- Primer claim de staking puede regalar una ventana anterior; hay rutas que suman floats a balances enteros y no exigen con rigor el estado activo (`backend/app/services/staking_service.py:192-290`, `backend/app/services/board/staking_service.py:165-267`).

**Corrección:** constraints DB, orden de locks determinista, timestamps al entrar, `SELECT FOR UPDATE`, idempotency keys, scheduler singleton o cola distribuida y tests concurrentes reales sobre PostgreSQL.

### AUTH-01 — WebSocket y bans no comparten exactamente el modelo HTTP (P1)

En modo local, WS decodifica JWT sin firma sin respetar toda la misma ruta `ALLOW_DEV_AUTH` (`backend/app/api/v1/ws/game_ws.py:40-51`); token viaja en query (`:79-84`). Los bans viven en un JSON, se leen por request y fallan abierto ante error (`backend/app/core/auth.py:91-103`); WS no aplica necesariamente el mismo control.

**Corrección:** autenticador común HTTP/WS; token por subprotocolo/header o cookie segura; bans en DB/Redis con auditoría; límites de origen/tamaño/tasa y mensajes de error no sensibles.

### SEC-03 — Secretos e infraestructura de desarrollo (P0 condicionado/P1)

- `backend/Dockerfile:7` hace `COPY . .`; existe un `.env` local y no hay `.dockerignore`. Aunque no esté en Git, podría quedar en una capa de imagen.
- Taskboard escucha globalmente, permite CORS `*`, recibe POST sin auth y ejecuta subprocess; Compose publica 8181, monta el repo RW y entrega claves API (`tools/taskboard/routes.py:214,241,272-283,411-412`; `docker-compose.yaml:65-78`).
- Anvil publica 8545 con cuentas conocidas/desbloqueadas (`docker-compose.yaml:17-35`).
- Treasury usa una hot key y el nonce lock/cache solo protege un proceso (`backend/app/services/web3_service.py:92-207`).

**Corrección 72 h:** comprobar exposición; bind a `127.0.0.1` o VPN; perfiles Compose; auth/CSRF/allowlist; repo RO; separar claves; `.dockerignore`; limpiar/rotar secretos y revisar imágenes/registry. Para valor real: KMS/HSM, roles separados y multisig.

### Observaciones P2/P3 backend/operación

- WebSocket mantiene estado singleton por proceso, no limpia todas las sesiones finalizadas y un fallo de settlement puede quedar solo en log (`backend/app/services/ws_manager.py:91-94,644-731`). Para HA necesita Redis/DB, CAS y retries.
- Reconciliación debe aceptar solo eventos de éxito exactos; validar antes de consumir el replay key y ofrecer recovery/refund cuando el comprador no tenga wallet.
- Leonardo webhook es opcional si no hay secret; descarga URL controlable con redirects y sin límites claros: SSRF/memoria/disco (`backend/app/api/v1/endpoints/leonardo.py:46-54,87-102,145-208`).
- Health solo declara proceso vivo (`backend/app/main.py:501-504`); falta readiness DB/RPC/outbox, métricas, tracing, alertas, backup/PITR y restore drill.
- `requirements.txt` no fija versiones/hashes; Docker corre como root y Python 3.11 contradice documentación 3.12.

---

## 6. Smart contracts y operación on-chain

### SC-01 — ReciclonVault no es funcional con el diseño actual (P0)

`ReciclonVault` hereda solo `Ownable`, no implementa `IERC1155Receiver`/`ERC1155Holder` (`contracts/src/ReciclonVault.sol:18`). Una transferencia segura ERC-1155 hacia el vault revierte. Además, `batchBurn` llama `CartasLoteria.burnCard` desde la dirección del vault (`contracts/src/ReciclonVault.sol:59-87`), pero `burnCard` es `onlyController` (`contracts/src/CartasLoteria.sol:65-67`). El script de despliegue ni siquiera crea el vault.

Hay además una llamada “de verificación” con id/amount 0 cuyo resultado se ignora; no aporta seguridad.

**Corrección:** heredar receiver correcto; otorgar un rol de burner limitado al vault o hacer que GameController orqueste; eliminar low-level calls; validar balances y accounting; desplegar/configurar en el mismo script; tests de recepción, batch, rechazo, supply y reentradas.

### SC-02 — Disolver tabla no destruye la carta (P1 funcional/económico)

`dissolveBoard` quema el NFT de tabla y devuelve 15 cartas, pero nunca llama `burnCard` para la carta elegida (`contracts/src/TablasLoteria.sol:112-140`). La carta queda retenida en el pool del contrato y `totalSupplyOf` no baja. El test existente solo comprueba que el jugador recibe cero de la carta destruida, por eso no detecta el error (`contracts/test/GameContracts.t.sol:253-263`).

`createNPCBoard` no deposita backing (`contracts/src/TablasLoteria.sol:179-189`), por lo que no es una tabla normalmente disoluble. Si el pool compartido no tiene las cartas, la transferencia revierte atómicamente; si las tiene por backing de otras tablas, la ausencia de accounting por `tableId` no impide consumir ese backing. Es un riesgo de invariant, no un exploit reproducido.

**Corrección:** accounting de backing por `tableId`; quemar explícitamente la unidad; separar de forma imposible de confundir tablas NPC; limpiar `layoutOf`; invariants pool = suma de backing y supply después de crear/disolver.

### SC-03 — Backend/owner puede decidir cualquier economía on-chain (P0 para mainnet)

Los tokens y NFTs permiten al controller **o al owner** operaciones privilegiadas; el deployer conserva ownership. GameController expone casi todo como `onlyOwner`: mint/burn, precios, premio, usuario, stats, transferencias y eventos (`contracts/src/GameController.sol:71-323`). No verifica de forma suficiente propiedad de axolotito/tabla, precio canónico, estado terminal de sala ni replay por `roomId`. `onlyFRJ` solo exige `msg.value == 0`.

**Impacto:** compromiso/error del hot key puede mintear, quemar o mover toda la economía; un backend comprometido puede registrar la misma finalización o parámetros arbitrarios. Esto también contradice cualquier claim de trustlessness.

**Corrección:**

- Roles separados (`MINTER`, `BURNER`, `SETTLER`, `PAUSER`) con mínimo privilegio.
- Multisig como admin, timelock para cambios no urgentes y pausa de emergencia.
- Caps/velocidades de emisión, nonces e IDs de operación consumidos una vez.
- Validaciones de ownership, estado y límites on-chain; o documentar honestamente un modelo custodial centralizado y reducir superficie on-chain.
- Transferir/renunciar ownerships solo después de un runbook probado; nunca a EOA única.

### SC-04 — Escrow ausente puede degradar silenciosamente a mock (P0 condicionado)

`web3_service` puede devolver hashes simulados cuando falta la dirección de escrow (`backend/app/services/web3_service.py:825-857`), y reconciliación puede interpretar la presencia del hash como custodia (`backend/app/services/reconciliation_service.py:216-223`).

**Impacto:** en un ambiente monetizado mal configurado, un comprador puede pagar sin que exista custodia/release real.

**Corrección:** fail-fast no-test ante dirección cero/bytecode ausente/chain ID incorrecto; verificar receipt de depósito/release; cero fallbacks mock fuera de tests.

### SC-05 — Script, red y manifest de despliegue están incompletos (P1)

`contracts/script/Deploy.s.sol:41-83` despliega tokens, assets, tablas y GameController, pero omite MarketEscrow y ReciclonVault. `foundry.toml` configura Amoy mientras el producto declara Plasma.

**Corrección:** una sola red objetivo por ambiente; deploy determinista completo; manifest firmado con direcciones, bytecode hashes, admin/roles y bloque; verificación explorer; smoke test pago→custodia→release→earnings.

### SC-06 — Supply/caps prometidos no están aplicados (P1)

Documentos prometen límites de Webitos y Sobrecitos, pero `Webitos.mintWebito` no aplica cap (`contracts/src/Webitos.sol:50-54`) y `Sobrecito` registra `mintedByFase` sin limitarlo (`contracts/src/Sobrecito.sol:34-47`).

**Corrección:** decidir si el límite es compromiso comercial. Si lo es, codificar cap inmutable o gobernado con demora/transparencia, evento de cambio y tests. Si no, retirar la promesa.

### Cobertura de contratos

Las suites cubren happy paths principales y MarketEscrow, pero no existen invariants ni tests específicos para Reciclón, caps, replay de sala, controller cero, backing tabla/pool, script de producción, reorg/revert/finality o consistencia DB-chain. Los dos fuzz tests de transferencia no cubren economía.

Antes de mainnet se requiere:

1. Invariants Foundry: conservación, caps, ownership/backing, estados terminales, no replay.
2. Fuzz de arrays, IDs, cantidades, permisos y secuencias cancel/deposit/release.
3. Slither/Mythril y revisión manual independiente.
4. Auditoría externa del commit final; congelar bytecode después.
5. Testnet canary, límites bajos, pausa, monitoreo y programa de disclosure/bug bounty.

---

## 7. Economía y jugabilidad

### ECON-02 — La configuración sugiere EV CPU inflacionario (P1 hasta medir)

Código actual Rookie: fee 10, premio 40 y consolación 5 FRJ (`backend/app/core/prices.py:123-150`). Un comentario de una simulación anterior reporta 55.4% de win rate para focus 50 (`backend/app/services/game_logic.py:30-35`), pero conserva premios antiguos y no es una medición del commit actual. Como estimación de riesgo, si esa tasa siguiera vigente, aplicarla a los premios actuales produciría:

`EV neto ≈ 0.554 × (40−10) + 0.446 × (5−10) = +14.39 FRJ/juego` antes de otros bonos.

El multiplicador 10 escala linealmente fee y payout (`backend/app/services/game_service.py:117-125`). Cada juego consume 10 energía y el descanso base dura solo un minuto (`backend/app/services/game_service.py:156,618-622`). Esto no demuestra el EV real actual, pero sí justifica simularlo antes de release: si la tasa permanece cerca de la documentada, el modo sería una fuente importante de FRJ.

**Corrección:** pausar multiplicadores altos; recalcular tasas mediante Monte Carlo sobre el mismo motor productivo; bankroll/house-edge por cohorte de stats; límites diarios y antifarm; telemetría de source/sink; prueba de conservación; no usar comentarios desactualizados como balance.

### GAME-01 — Lo que el jugador acepta no es lo que el servidor cobra/paga (P0)

UI CPU muestra Rookie `100 → +160` y Champion `500 → +2900` (`frontend/components/screens/BoardSelectScreen.tsx:36-38,303-330`); backend cobra/paga `10/40` y `50/200` (`backend/app/core/prices.py:123-163`). Sala Rookie adicional muestra 35 en otra pantalla (`frontend/components/screens/SalaSelectScreen.tsx:198-220`).

**Impacto:** consentimiento económico inválido, tickets de soporte, potencial engaño y métricas imposibles de interpretar.

**Corrección:** endpoint público versionado `/rules/economy`; pantalla de confirmación recibe quote con expiración/idempotency; settlement devuelve fee, bruto, neto, XP, saldo y ledger ID; contract tests cliente-servidor.

### GAME-02 — Tres motores de patrones producen ganadores distintos (P0)

Las salas admiten patrones configurables (`backend/app/api/v1/endpoints/multiplayer.py:434-457`), pero el grito manual llama un validador sin pasar patrones activos (`backend/app/services/ws_manager.py:481-500`). Ese validador acepta un conjunto fijo y omite cruz/L/Z (`backend/app/services/game_logic.py:361-408`). CPU anuncia línea+cuadrito, pero evalúa línea en la ruta auditada (`backend/app/services/game_logic.py:50-107`, `backend/app/services/game_service.py:255-273`).

**Corrección:** un solo `PatternEngine`, puro y versionado, utilizado por CPU/auto/manual; devolver patrón ganador y celdas; property tests por rotación/reflejo y E2E por cada patrón.

### GAME-03 — Replay y recompensas visuales no son autoritativos (P1)

Backend devuelve `bot_marked_indices`, pero frontend vuelve a decidir fallos con `Math.random()` (`frontend/hooks/useCpuGame.ts:412-443`). Manual termina sin payout detallado; wrappers inventan/estiman payout o XP (`frontend/hooks/useManualGame.ts:202-208`, `frontend/components/multiplayer/ManualGameWrapper.tsx:48-60`, `frontend/components/multiplayer/AutoGameWrapper.tsx:120-135`).

**Impacto:** el usuario ve una partida que no explica la liquidación real; disputas y percepción de manipulación.

**Corrección:** un `game_trace` firmado/versionado con semilla/commit-reveal si aplica, cartas cantadas, marcas, fallos, patrón, ganador y settlement; cliente reproduce, nunca resortea.

### GAME-04 — Incentivos manipulativos y antifraude insuficiente (P1 legal/producto)

La Biblia indica que el kit entrega 139 AXF para dejar al jugador deliberadamente a 1 AXF de otra partida e inducir microtransacción (`docs/AXOLOTTO_MASTER_BIBLE.md:408`). También reconoce farming pasivo con bots (`:405`). Esto es una señal de dark pattern, especialmente sensible si acceden menores o personas vulnerables.

**Corrección:** retirar diseño “quedarse a uno”; ofrecer costos claros y presupuesto; límites de sesión/gasto/pérdida; cooldown; exclusión; antifraude basado en riesgo; prohibir auto-play con valor hasta resolver clasificación y controles.

### ECON-03 — Tipo de cambio y paquetes no son coherentes (P1)

Config nominaliza 1 AXF ≈ 2 MXN, mientras algunos packs en USD entregan cantidades que implican descuentos superiores a 10× según tipo de cambio; frontend además usa `FRJ_PER_AXF=4`, Biblia otros ratios y VIP otros precios. No puede calcularse emisión, LTV, liability ni impuestos con varias unidades de cuenta.

**Corrección:** tabla canónica por SKU/moneda/país, FX y vigencia; separar precio comercial de valor contable; registrar promociones como descuento explícito; modelar liabilities de balances; simulación de fuentes/sinks por percentil y stress test.

### Recomendaciones de diseño de juego

- Definir si Axolotto es principalmente **colección/crianza** o **juego de azar con premios**; hoy el loop monetario está dominado por lotería automática.
- Para una versión de bajo riesgo, hacer que partidas no requieran moneda comprada y que premios no sean transferibles/canjeables; monetizar cosméticos/expansión con valor fijo. Aun así, obtener opinión jurídica.
- Separar modos de habilidad y azar; publicar reglas, probabilidades, comisiones y fuentes de aleatoriedad.
- Añadir límites de bankroll por sala, pérdida, ganancia, día y dispositivo; detección multi-account y colusión; cooldowns reales.
- Simular economía con usuarios heterogéneos, no solo promedios: whales, veteranos, Sybil, AFK, bots, alta suerte/focus, múltiples axolotitos y VIP.
- Mantener un dashboard de emisión/burn por causa, supply DB/on-chain, Gini, sink coverage, jackpot liability, ARPDAU y fraude.

---

## 8. Frontend, UX y accesibilidad

### FE-01 — El modo manual no recibe el tablero del jugador (P0)

El hook inicia con 16 ceros y `boardId=null` y ningún handler los sustituye (`frontend/hooks/useManualGame.ts:112-113,161-231`). El wrapper entrega esos ceros al juego (`frontend/components/multiplayer/ManualGameWrapper.tsx:70-80`). Backend conoce las cartas, pero conexión, `game_start` y sync no envían un payload privado con el tablero (`backend/app/services/ws_manager.py:127-153,239-254,283-293`).

**Impacto:** el jugador no sabe qué cartas marcar; el modo manual no es liberable.

**Corrección:** mensaje privado/autenticado `player_state` con `board_id`, 16 posiciones/números y versión; reenviar en reconnect/sync; nunca broadcast a oponentes; validación schema y E2E con dos usuarios.

### FE-02 — Riesgo de loops de red por identidades React inestables (P1)

- Manual crea handlers, cierre de URL y `onOpen` por render; `connect` depende de ellos y el effect reconecta (`frontend/hooks/useManualGame.ts:138-272`, `frontend/hooks/useWebSocket.ts:155-172`). Cada mensaje puede provocar otra conexión.
- Auto recibe `onGameEnd` inline; `fetchGameState` depende de él y el effect hace fetch inmediato (`frontend/components/multiplayer/AutoGameWrapper.tsx:35-41`, `frontend/hooks/useAutoGame.ts:72-157`). Cada respuesta puede reiniciar polling.

**Impacto potencial:** exceso de conexiones/peticiones, estados duplicados, batería/CPU y servicio inestable. La revisión fue estática; falta reproducir y medir conteo de conexiones/requests para cuantificarlo.

**Corrección:** callbacks en refs o memoizados, endpoint string estable, effect dependiente solo de configuración estable; `setTimeout` recursivo single-flight; `AbortController`; backoff+jitter; test con fake timers que cuente conexiones/peticiones.

### FE-03 — Contratos WS incompletos o incompatibles (P1)

- Chat envía `{action: "chat_message"}` y backend enruta por `type` (`frontend/components/chat/ChatFeed.tsx:77-78`, `backend/app/api/v1/ws/game_ws.py:190-217`).
- Backend cierra una pestaña reemplazada con evento/4008, pero frontend reconecta cierres no intencionales (`backend/app/services/ws_manager.py:113-124`, `frontend/hooks/useWebSocket.ts:133-149`), generando guerra entre pestañas.
- Salas hosted se muestran pero no son seleccionables; el tipo seleccionado solo representa salas oficiales (`frontend/components/screens/SalaSelectScreen.tsx:59-70,280-337`, `frontend/components/PlayMode.tsx:371-393`).

**Corrección:** JSON Schema/TypeBox/Pydantic generado y versionado; 4008 terminal con UX “sesión activa en otra pestaña”; state machine de `roomId/password`; tests contractuales bidireccionales.

### FE-04 — Claims públicos no corresponden al producto (P0 consumo/P1 técnico)

- Landing dice jackpot “24/7 On-Chain” (`frontend/app/page.tsx:500-509`), pero vault y reparto auditados viven en SQL (`backend/app/models/lobby_models.py:29-35`, `backend/app/services/multiplayer_service.py:486-507,586-666`).
- Tiers/precios/beneficios VIP de landing contradicen backend; “ventajas fiscales” carece de sustento individualizado.
- La nota llamada “legal” en VIP solo explica acumulación de días/slots, no renovación, cancelación, precio, impuestos ni términos (`frontend/components/vip/ModeA.tsx:186-194`).

**Corrección inmediata:** retirar “on-chain”, “ventajas fiscales”, cashback y beneficios no implementados; usar datos backend; todo claim verificable debe enlazar reglas/explorer/condiciones.

### UX-01 — Operaciones esenciales no son accesibles (P1)

- Celdas y tablas seleccionables usan `div` sin rol, `tabIndex` ni teclas (`frontend/components/ui/BoardCardGrid.tsx:427-438`, `frontend/components/screens/BoardSelectScreen.tsx:224-238`).
- Hold-to-confirm es pointer-only (`frontend/components/ui/HoldButton.tsx:109-154`).
- Canvas del mundo está `aria-hidden` y solo registra pointer; no existe alternativa DOM equivalente (`frontend/components/world/GameCanvas.tsx:245-248`, `frontend/components/world3d/ThreeWorldEngine.ts:118-142,326-329`).
- `BottomSheet` y Settings carecen de dialog semantics, focus trap/return y Escape (`frontend/components/ui/BottomSheet.tsx:14-44`, `frontend/components/SettingsModal.tsx:75-100`).
- Reduced motion está contemplado en 3D pero no en varias animaciones infinitas del tutorial.

**Corrección:** WCAG 2.2 AA como criterio de aceptación; botones nativos, grid roving, labels/estado, foco visible, alternativa HTML para hotspots, diálogos correctos, `prefers-reduced-motion`, axe + teclado + lector de pantalla en CI.

### UX-02 — Estados de error pueden dejar al usuario atrapado (P1/P2)

- `/auth/sync` no verifica `response.ok`; catch puede mantener fase `loading` para siempre (`frontend/app/play/page.tsx:593-658`).
- “Reintentar” tutorial cambia refs/estado que no reejecutan el effect de inicialización (`frontend/components/tutorial/TutorialFlow.tsx:139-208,305-315`).
- Store/lobby degradan a vacío y continúan mostrando acciones, ocultando la diferencia entre “sin datos” y “falló”.
- Cerrar panel desmonta una partida CPU ya liquidada en backend (`frontend/app/play/page.tsx:1045-1118`).

**Corrección:** state machines explícitas `idle/loading/success/empty/error/stale`; timeout, retry real, logout/recuperación; persistir/rehidratar partida; no desmontar una transacción activa.

### UX-03 — Compra accidental/doble y consentimiento insuficiente (P1)

Hold-to-confirm es una buena intención, pero `comprarItem` no bloquea una compra in-flight ni envía idempotency key; otros controles permanecen activos (`frontend/hooks/useStore.ts:254-265`, `frontend/components/store/OfficialTab.tsx:332-340`).

**Corrección:** quote server-side, resumen total/impuestos/moneda/beneficio, botón bloqueado por operación, key idempotente, recibo, reversa; historial accesible. Para suscripción: consentimiento separado y cancelación inmediata.

### PERF-01 — Monolito `/play`, polling duplicado y PWA ambigua (P2)

`frontend/app/play/page.tsx` tiene ~1,195 líneas e importa gran parte de paneles/3D. Página y `PlayMode` consultan estado activo cada 5 s; el provider realtime está ubicado después de un consumidor. El service worker solo hace network pass-through y responde 503 offline (`frontend/public/sw.js:14-27`), pero la UI ofrece instalación.

**Corrección:** separar route/orchestrator/state machines; lazy load del 3D/paneles; caché de datos única; budgets de JS/FPS/memoria; decidir PWA online-only honesta o shell offline versionado.

### Calidad de experiencia todavía no medida

No se confirmó contraste efectivo, responsive, Safe Areas, FPS, memoria, tamaño real de bundle, gestos, Safari/iOS, Android económico ni lector de pantalla en ejecución. La revisión visual fue estática; el informe no debe interpretarse como certificación UX.

---

## 9. Legalidad y cumplimiento en México

### REG-01 — Clasificación regulatoria preliminar (P0)

La sustancia descrita combina:

- pago/compra de AXF y conversión o adquisición de FRJ;
- cuota para partidas;
- resultado materialmente influido por azar;
- premios, jackpot, NFTs/activos transferibles;
- marketplace y una ruta DevEx/cashout contemplada.

La Dirección General de Juegos y Sorteos señala que los juegos con apuestas y sorteos, en todas sus modalidades, requieren permiso expreso de SEGOB. El Reglamento define apuesta en términos de una cantidad apreciable en moneda nacional arriesgada para obtener un premio mayor; además contempla registros electrónicos y centros de apuestas remotas. Esto no clasifica automáticamente esta implementación, pero sí crea **riesgo alto** de que la operación real sea tratada por su sustancia, no por llamar a FRJ “soft currency” ni por mover el retiro a otro módulo.

**Decisión antes de desarrollo comercial:**

1. Entregar a counsel un diagrama exacto de cada flujo de fondos/activos y obtener opinión firmada.
2. Definir con counsel la vía de consulta o trámite ante SEGOB y, si el modelo encuadra, obtener el permiso antes de abrir la mecánica.
3. Hasta entonces: geofence, 18+, cero dinero real, cero retiro/transferencia de premios y cero publicidad de jackpot con valor.
4. Si se busca un diseño fuera de apuesta, rediseñar sustancialmente consideración, premios/valor/transferibilidad y azar; no confiar en etiquetas.

Fuentes: [SEGOB — Juegos y Sorteos](https://juegosysorteos.segob.gob.mx/es/Juegos_y_Sorteos/home), [prohibiciones y menores](https://juegosysorteos.segob.gob.mx/es/Juegos_y_Sorteos/Prohibiciones), [Reglamento de la LFJS](https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LFJS.pdf), [Ley Federal de Juegos y Sorteos](https://www.diputados.gob.mx/LeyesBiblio/pdf/109.pdf).

### LEG-01 — Menores y juego responsable inexistentes en producto (P0)

El Reglamento prohíbe a menores participar en el cruce de apuestas y exige advertencias en publicidad de juegos/sorteos; la aplicación precisa al producto digital debe confirmarse con counsel y SEGOB. En frontend no se encontraron age gate real, verificación 18+, autoexclusión, límites de depósito/pérdida/tiempo, enfriamiento, historial de juego, advertencias de probabilidad ni soporte de juego problemático.

**Controles recomendados, sujetos al criterio/permiso aplicable:** bloquear onboarding monetario hasta verificar mayoría de edad e identidad según riesgo; geolocalización/jurisdicción; autoexclusión por periodo, límites configurables, reality checks, no crédito, no auto-play monetario, enlaces de ayuda y monitoreo de patrones de riesgo. No se afirma que cada control sea por sí solo una obligación legal general; el paquete exacto debe acordarse con counsel/autoridad.

### LEG-02 — AML/KYC y activos virtuales (P0)

SAT identifica como actividades vulnerables juegos/sorteos y, cuando AXF/FRJ encajen en la definición legal de activo virtual, el ofrecimiento habitual/profesional mediante plataformas que faciliten intercambio o provean custodia/transferencia. Las obligaciones dependen del rol y de umbrales vigentes en UMA. LFPIORPI reformada requiere información precisa del originante, receptor y, en su caso, beneficiario controlador para ciertos flujos cuando resulte aplicable.

El plan actual no demuestra un programa completo de alta, identificación/verificación, beneficiario controlador, perfil transaccional, screening, conservación, avisos, manual interno, capacitación, auditoría, información de originante/receptor cuando aplique y reportes. Umbrales históricos en dólares dentro de docs no son control válido.

**Corrección:** análisis de sujeto/actividad por cada flujo; responsable de cumplimiento; matriz UMA actualizable; KYC/KYB escalonado antes de compra/transferencia/retiro; sanciones/PEP/adverse media según riesgo; monitoreo Sybil/structuring; expedientes y avisos; políticas de rechazo, retención o reembolso solo con base contractual, obligación legal u orden competente.

Fuentes: [LFPIORPI vigente](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPIORPI.pdf), [SAT — Actividades Vulnerables](https://wwwnp.sat.gob.mx/minisitio/ActividadesVulnerables/), [SAT — obligaciones generales](https://www.sat.gob.mx/minisitio/ActividadesVulnerables/informacion_general.html).

### LEG-03 — Consumidor, precios, publicidad y suscripciones (P0/P1)

No se encontraron rutas funcionales de Términos, Privacidad, reembolsos/cancelación ni contacto legal; el footer usa spans inertes (`frontend/app/page.tsx:633-642`). A la vez, precios/premios y claims VIP/jackpot son contradictorios. La LFPC exige información clara, seguridad/confidencialidad, domicilio/contacto, costos totales, términos y ausencia de prácticas engañosas; la regulación actual incorpora claridad, consentimiento y cancelación en cobros recurrentes.

**Corrección antes de cobrar:**

- Razón social, domicilio/contacto, jurisdicción y atención.
- Precio total en MXN, impuestos/comisiones/red/gas, vigencia del quote y tipo de cambio.
- Características, probabilidades/reglas, entrega, custodia, reversa, reembolso y activos perdidos.
- Suscripción VIP con información clara, consentimiento expreso, aviso al menos cinco días naturales antes de renovación automática, cancelación sin penalización y mecanismo de cancelación inmediata.
- Historial/recibo descargable; procedimiento de queja; lenguaje simple y registro de versión aceptada.
- Revisión de cada claim; retirar “on-chain” o “ventaja fiscal” si no es demostrable.

Fuentes: [Ley Federal de Protección al Consumidor](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf), [PROFECO — Monitoreo de Tiendas Virtuales](https://www.profeco.gob.mx/tiendasvirtuales/).

### LEG-04 — Privacidad y seguridad de datos (P1; gate antes de captar datos sensibles)

Privy, wallets, email, IP/dispositivo, transacciones, KYC y analítica forman un perfil identificable. No se encontró aviso integral/simplificado operativo, centro ARCO, inventario de encargados/transferencias, plazos de retención, consentimiento diferenciado ni proceso visible de incidente.

La ley vigente exige informar desde la recolección electrónica, mantener medidas de seguridad y notificar vulneraciones materiales. Deben definirse roles responsable/encargado y transferencias internacionales con Privy, proveedor KYC, pagos, analítica, nube y soporte.

**Corrección:** cumplir aviso, ARCO, seguridad y notificación inmediata de vulneraciones significativas; además, como buenas prácticas, mantener data map/registro de tratamientos, minimización, retención/borrado, contratos/cláusulas de transferencia, cifrado, respuesta a incidentes y evaluación de impacto para KYC/fraude/perfilado. Estas últimas herramientas no se presentan como obligaciones generales expresas de la ley mexicana.

Fuente: [Ley Federal de Protección de Datos Personales en Posesión de los Particulares](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf).

### LEG-05 — Fiscalidad, pagos y clasificación financiera (P1 alto)

Juegos/sorteos pueden generar IEPS y obligaciones técnicas/de reporte; ventas digitales, comisiones, premios, tokens y marketplace implican IVA/ISR/retenciones/facturación según el modelo. No debe suponerse que Stripe u otra pasarela “retiene todo”.

Custodia, transmisión, intercambio o venta habitual de activos virtuales requiere análisis separado bajo LFPIORPI y, según estructura/servicios, LRITF y disposiciones de Banxico. Circular 4/2019 regula a determinadas entidades financieras; no es una autorización general para Axolotto.

**Corrección:** memo fiscal por flujo y entidad; CFDI/contabilidad; tratamiento de balances no consumidos, premios y fees; nexus/usuarios extranjeros; conciliación gateway-bank-ledger-chain; análisis financiero firmado antes de wallet custodial/cashout.

Fuentes: [SAT — Juegos con apuestas y sorteos](https://wwwmat.sat.gob.mx/consultas/39264/juegos-con-apuestas-y-sorteos-), [SAT — retenciones de plataformas](https://wwwmat.sat.gob.mx/declaracion/39311/presenta-tu-declaracion-de-entero-de-retenciones), [Banxico — Circular 4/2019](https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-4-2019/circular-4-2019.html).

### LEG-06 — Propiedad intelectual, IA y patrimonio cultural (P1)

El repo incluye assets nombrados como generados con Gemini y no contiene un expediente de licencias/cesiones ni LICENSE general. En su comunicado del 28 de agosto de 2025, INDAUTOR explicó el criterio de la SCJN sobre obras generadas autónomamente por IA: no son registrables como derecho de autor. Debe distinguirse una salida autónoma de una obra con aportación humana original y demostrable. Esto no impide necesariamente el uso, pero puede reducir exclusividad y exige revisar inputs, términos del proveedor y contribución humana.

También deben despejarse marcas/nombres, cartas de lotería, música, tipografías, librerías, imágenes de Xochimilco/ajolote y contribuciones. Si se incorporan expresiones culturales específicas de pueblos/comunidades, analizar consentimiento y la ley de patrimonio cultural; no se debe asumir que toda estética mexicana es apropiable ni que toda referencia genérica está prohibida.

**Corrección:** asset register con autor, fuente, licencia, modelo/versión/prompt, inputs, edición humana, territorio y cesión; búsquedas de marca; CLA de colaboradores; política de takedown; SBOM/licencias; counsel cultural cuando aplique.

Fuentes: [INDAUTOR — comunicado de 28 de agosto de 2025 sobre IA y registro](https://www.indautor.gob.mx/comunicados.php), [Ley Federal del Derecho de Autor](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFDA.pdf), [Ley de protección del patrimonio cultural de pueblos y comunidades](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPPCPCIA.pdf).

### Documentos/pantallas mínimas antes de beta monetizada

1. Términos de servicio y reglas oficiales/versionadas.
2. Aviso de privacidad corto e integral; cookies/SDKs; ARCO.
3. Política de compra, entrega, cancelación, reembolso y chargebacks.
4. Términos VIP/renovación y confirmación de consentimiento.
5. Política KYC/AML y sanciones; restricciones geográficas/edad.
6. Juego responsable, autoexclusión, límites y ayuda.
7. Riesgos Web3: volatilidad, gas, custodia, claves, irreversibilidad, smart-contract risk.
8. Propiedad/licencia de NFTs: qué compra el usuario y qué derechos no recibe.
9. Reglas de marketplace/DevEx, comisiones, impuestos, disputas y retiro.
10. Evidencia del permiso/criterio aplicable y contacto del operador autorizado.

---

## 10. QA, dependencias, DevOps y observabilidad

### QA-01 — No hay una rama liberable reproducible (P1 de proceso; gate obligatorio)

**Frontend**

- Build y typecheck pasan.
- ESLint falla con 542 errores y 211 warnings. Hay uso amplio de `any`, imports/variables sin usar, dependencias de hooks y supresiones. Entre señales funcionales: `frontend/hooks/useWebSocket.ts:147` referencia `connect` antes de su declaración y `frontend/app/page.tsx:67,77` hace `setState` sincrónico dentro de effects.
- Solo existe un spec Playwright (`frontend/tests/degraded_network.spec.ts`), Chromium desktop, con TODO/selectores que no representan el flujo autenticado. No hay E2E CPU/manual/auto, dos usuarios, dos pestañas, reconnect, compra, settlement, mobile, WebKit/Firefox, axe o visual regression.

**Backend**

- La imagen declarada no incluye pytest; fue necesario instalarlo en un contenedor efímero.
- Resultado: 746 pass, 73 fail, 1 skip. Varias fallas prueban que tests/código no terminaron la migración de nombres/unidades; otras dependen de rutas/artefactos ausentes en la imagen. También fallan suites de banco, outbox/desync, gashapon, jackpot, mercado, VIP y staking, por lo que no deben descartarse todas como “tests viejos”.

**Contratos**

- 29/29 pasan, pero las omisiones permiten que bugs como la carta retenida al disolver sigan verdes.

**Gate recomendado:** ningún merge a release si build/type/lint/test/invariants/security scan no están verdes; una excepción requiere waiver con dueño, expiración y riesgo aceptado.

### DEP-01 — Supply chain no reproducible y vulnerable (P1)

- `npm audit --omit=dev` reportó 7 vulnerabilidades altas y 29 moderadas en el árbol de producción, incluidas dependencias de Next y transitivas. Esto es exposición de versión, no prueba por sí sola de explotación en Axolotto.
- `backend/requirements.txt` no fija versiones/hashes ni incluye las herramientas de test.
- `.gitignore` ignora locks (`package-lock.json`, yarn/poetry); existe un lock frontend local pero no está versionado.
- `axios` y `lucide-react` se importan directamente sin declararse como dependencias directas; llegan transitivamente.
- `.gitmodules` referencia OpenZeppelin, pero el árbol Git no contiene el gitlink de `contracts/lib`; un clon limpio no puede reproducir el build Foundry sin pasos externos no documentados.
- No hay workflow CI versionado ni SBOM/licence scan.

**Corrección:**

1. Versionar locks y usar `npm ci`; pin con rangos conscientes y Renovate/Dependabot.
2. Fijar Python con lock/hashes (`uv.lock`/Poetry/pip-tools) y separar deps dev.
3. Registrar correctamente submódulo o usar Foundry dependency reproducible; fijar commit de OpenZeppelin.
4. Actualizar advisories, priorizando rutas alcanzables; SCA en cada PR y escaneo de imagen.
5. Generar SBOM CycloneDX/SPDX, firmas/provenance y política de licencias.

### OPS-01 — Compose es laboratorio, no baseline de producción (P0 condicionado/P1)

`docker-compose.yaml` usa Foundry `latest`, publica backend/Anvil/taskboard, monta código/repo, carece de healthchecks y límites; Anvil trae cuentas conocidas. Docker backend corre root y copia todo el contexto. Taskboard comparte red/secretos y tiene capacidad de ejecutar procesos.

**Corrección:** perfiles `dev/test`; puertos loopback; red/credenciales separadas; imágenes por digest, non-root, read-only filesystem, capabilities mínimas, health/readiness, recursos, secrets manager, TLS/reverse proxy, WAF/rate limit y artefactos inmutables.

### OPS-02 — Deploy y recuperación no están demostrados (P1/P2)

El script de producción revisado reconstruye/reinicia principalmente frontend, usa `npm install`, puede auto-stage/commit y una composición con `; pm2 start` puede ocultar un build fallido. No demuestra despliegue coordinado de backend/migraciones/contratos, health gates ni rollback.

No se encontró evidencia versionada suficiente de:

- SLO/SLI y alertas para pagos, outbox, chain lag, ledger drift, WS y jackpot.
- logs estructurados con correlation/operation ID y redacción de PII.
- backup PostgreSQL con PITR y restore drill.
- runbooks de llave comprometida, pausa, reorg, doble mint, pago sin release, chargeback y data breach.
- DR multi-zona, RTO/RPO, capacity/load tests o incident ownership.

**Corrección:** CI/CD de artefactos inmutables; migrate once; canary; smoke tests; rollback automático; readiness profunda; OpenTelemetry; dashboards; PITR y simulacros trimestrales.

### P2/P3 de mantenimiento

- `frontend/README.md` continúa como plantilla Create Next App; `contracts/README.md` es boilerplate Foundry y no documenta red, direcciones, permisos ni verificación.
- Hay componentes legacy/desconectados y contratos duplicados, aumentando superficie y drift.
- El repo trackea varios PNG/HTML generados de varios MB y assets duplicados; conviene optimizar/LFS/CDN y documentar procedencia/licencia.
- No hay `LICENSE` del proyecto.

---

## 11. Plan de remediación priorizado

### Fase 0 — Contención (0–72 horas)

**Objetivo:** impedir pérdida/emisión de valor mientras se decide el producto.

- [ ] Poner dinero real, retiro/DevEx, marketplace con valor, hosted rooms y multiplicador CPU >1 detrás de feature flags apagadas.
- [ ] Desmontar router de pago mock y endpoints de reward confiados al cliente fuera de entorno local autenticado.
- [ ] Corregir la inflación/bloqueo del escrow en timeout; añadir invariant de conservación y test repetido/concurrente.
- [ ] Revisar exposición de 8001/8181/8545; bind loopback/VPN y bloquear en firewall.
- [ ] Rotar treasury, webhook y API keys potencialmente incluidas en capas/servicios; revisar registry/historial/logs.
- [ ] Retirar landing claims falsos: precios/premios VIP, “on-chain”, cashback, “ventajas fiscales”.
- [ ] Congelar manual/auto para usuarios hasta corregir tablero y loops de red.
- [ ] Nombrar responsables de incidente, economía, seguridad y legal; preservar logs/evidencia.

**Evidencia de salida:** flags verificadas, scan de puertos, claves rotadas, tests exploit rojos→verdes y publicación corregida.

### Fase 1 — Integridad mínima (días 4–14)

- [ ] Convertir todo checkout/ledger/outbox a `int` mínimo; migración reconciliada.
- [ ] Worker outbox supervisado con claim atómico, lease/reaper/DLQ y receipt/finality.
- [ ] Fail-fast si faltan direcciones/bytecode/chain ID; nunca hash mock en no-test.
- [ ] Endpoint canónico de precios/reglas/tiers + schemas compartidos HTTP/WS.
- [ ] Reparar tablero manual, reconexión, polling auto, chat y 4008; settlement/trace autoritativo.
- [ ] Unificar PatternEngine; tests por modo/patrón.
- [ ] Alembic único; eliminar DDL de startup.
- [ ] Constraints/locks/idempotencia en inventario, rewards, compras y claims.
- [ ] Cerrar suite backend/lint y añadir CI básica: build, type, lint, pytest, forge, SCA, secret scan.
- [ ] Simular economía actual y fijar límites temporales conservadores.

**Evidencia de salida:** pipeline verde desde clon limpio, reconciliación sin drift, pruebas multiusuario y reporte de Monte Carlo versionado.

### Fase 2 — Producto seguro y operable (semanas 3–6)

- [ ] Rediseñar permisos de contratos; multisig/roles/pause/caps/nonces/timelock.
- [ ] Reparar Reciclón/backing de tablas; invariants/fuzz y deploy completo.
- [ ] Gateway real, refunds/chargebacks, KYC gates y ledger doble-entry.
- [ ] Estado WS distribuido, schedulers con líder y observabilidad completa.
- [ ] Accesibilidad WCAG 2.2 AA, estados de error, mobile/browser matrix y visual QA.
- [ ] Split `/play`, budgets de bundle/FPS/memoria y decisión PWA.
- [ ] Backups/PITR restore, incident drills, rate/load/chaos tests.
- [ ] GDD/ADR/manifest de redes como fuente única; retirar legacy.

### Fase 3 — Autorización y lanzamiento (6–12+ semanas, depende de terceros)

- [ ] Opiniones legales firmadas y resolución/permiso aplicable de SEGOB.
- [ ] Programa KYC/AML, fiscal, privacidad y consumo implementado y auditado.
- [ ] Términos/políticas/reglas oficiales en UI con versionado de aceptación.
- [ ] Auditoría externa de smart contracts y pentest de app/API/infra; remediación verificada.
- [ ] Testnet canary con límites bajos, bug bounty/disclosure y simulacro de pausa.
- [ ] Revisión go/no-go por seguridad, legal, economía, producto y operaciones; aceptación formal de riesgos residuales.

---

## 12. Gates objetivos para permitir un lanzamiento monetizado

No lanzar hasta que **todos** sean demostrables:

| Gate | Evidencia mínima |
|---|---|
| Legal | Opinión firmada, permiso/criterio, entidad operadora y jurisdicciones autorizadas |
| Edad/AML | 18+, KYC/KYB, screening, monitoreo, avisos, self-exclusion y límites probados |
| Economía | Sin faucets; source/sink y liabilities bajo stress; invariants de conservación verdes |
| Pagos | Gateway real; idempotencia; recibo; refund/chargeback; conciliación bancaria/ledger |
| Web3 | Receipt/finality, reconciliación, multisig/roles/pause, deploy manifest y explorer |
| Contratos | Auditoría externa cerrada, invariants/fuzz, bytecode congelado y runbook de incidentes |
| Juego | CPU/auto/manual E2E; patrones/precios/trace/settlement autoritativos |
| UX | Teclado/lector/mobile; error/retry; términos y costos antes del consentimiento |
| QA | Clon limpio; CI verde; cero P0/P1 abiertos; SCA/secret/image scans dentro de política |
| Operación | Readiness, SLO/alertas, backups restaurados, rollback y simulacros de incidentes |

### Dos rutas realistas de producto

> **Decisión posterior:** el fundador descartó la ruta de juego monetizado/regulado. Desde el 15 de julio de 2026 rige `ADR-001-NON_GAMBLING_PRODUCT_MODEL.md`; la Ruta B se conserva únicamente como contexto histórico de la auditoría original.

**Ruta A — Demo cerrada de bajo riesgo:** sin compra, retiro, transferibilidad ni premios con valor; monedas de prueba reseteables; acceso limitado; copy claro. Permite validar diversión/UX mientras se repara arquitectura. Requiere aun privacidad, consumo e IP.

**Ruta B — Producto monetizado/regulado:** mantener apuesta/jackpot/mercado solo con permiso, controles 18+/AML/fiscal, capital operativo, auditorías, transparencia de reglas y operación madura. Es materialmente más costosa y lenta.

Intentar una ruta intermedia basada solo en “FRJ no tiene valor” es la opción de mayor riesgo: el código, la convertibilidad, los premios y el marketplace contradicen esa narrativa.

---

## 13. Preguntas que el equipo directivo debe resolver

1. ¿Qué entidad jurídica recibe dinero y en qué jurisdicciones se ofrecerá?
2. ¿AXF/FRJ son custodiales, transferibles y redimibles? ¿Quién asume su liability?
3. ¿Qué activo es autoritativo en DB y cuál on-chain? ¿Cómo se resuelve una divergencia?
4. ¿Se quiere operar un juego regulado o rediseñar hacia colección/cosméticos sin premio de valor?
5. ¿Qué permiso/criterio escrito existe hoy? Si ninguno, ¿quién lidera la consulta?
6. ¿Menores pueden entrar a la parte no monetaria? ¿Cómo se separan datos, marketing y gasto?
7. ¿Quién controla treasury/admin/pausa y cuál es el procedimiento de emergencia?
8. ¿Qué garantías comerciales se hacen sobre supply, ownership, “on-chain”, precio y retiro?
9. ¿Cuál es el bankroll/liability máximo ante jackpot, fraude, chargebacks y balances no consumidos?
10. ¿Qué métricas y umbrales disparan una pausa automática?

---

## 14. Cierre

Axolotto no necesita una reescritura total: necesita **reducir ambigüedad y cerrar ciclos críticos**. La mejor inversión inmediata no es añadir contenido, sino hacer que una sola definición de precio/regla/activo atraviese UI, backend, ledger y cadena; que ninguna operación cree valor sin prueba; y que el modelo legal coincida con la experiencia que realmente se vende.

El orden correcto es:

1. contener valor y exposición;
2. restaurar invariantes y baseline verde;
3. cerrar los tres modos end-to-end;
4. decidir y documentar el modelo regulatorio;
5. endurecer contratos/operación;
6. recién entonces monetizar y escalar.

Mientras permanezcan abiertos los P0 REG-01, LEG-01/02/03, SEC-01/02, W3-01, DATA-01, SC-01/03/04, FE-01, GAME-01/02 y OPS-01 —y mientras los P1 económicos/operativos no tengan baseline verde—, el dictamen se mantiene **NO-GO**.

---

## 15. Actualización verificada tras decidir el modelo sin apuestas

Esta sección es un addendum de implementación posterior al snapshot `e12f5b1` auditado originalmente. Su base documental fue comprometida en `e69f02c`; las correcciones descritas debajo pertenecen al worktree de remediación posterior y deben evaluarse con su commit final, no atribuirse al snapshot inicial.

La decisión del fundador del 15 de julio de 2026 elimina como objetivo de producto las entradas pagadas, premios financiados por jugadores, jackpot, cashout de recompensas, P2P libre y artículos aleatorios comprados con valor de reventa. El modelo objetivo pasa a ser juego gratuito, venta de contenido digital conocido y un futuro programa de creadores adultos con saldo fiat separado. La decisión completa se registra en `ADR-001-NON_GAMBLING_PRODUCT_MODEL.md`.

Se implementó una primera contención P0:

- política de producto fail-closed y endpoint público de capacidades;
- CPU gratuito sin entrada, premio, wallet, ledger ni mint; multiplicadores/autoplay/presupuestos rechazados;
- tutorial gratuito con starter DB-only no transferible y sin token/NFT, para cerrar onboarding sin fingir propiedad on-chain;
- pagos, marketplace, payouts, VIP, jackpot, juego pagado, recompensas reportadas por cliente, transferencias y mutaciones de activos riesgosas desactivados por defecto;
- bandas de edad y estados separados de comercio, creador y KYC;
- vinculación de wallet cerrada hasta implementar challenge firmado; menores sin comercio/payout/wallet en el MVP;
- UI y landing sin promesas de premios, rendimiento, retiro o ingresos por jugar;
- correcciones a la disolución de tablas y a la custodia/contabilidad de `ReciclonVault`;
- AXF/FRJ no transferibles por contrato; NFTs/cartas todavía requieren restricción on-chain;
- puertos de Anvil, backend y taskboard ligados a loopback en Compose;
- guía legal mexicana y separación de menores/adultos.

Evidencia del corte de remediación: 120 pruebas backend focales pasan; Foundry pasa 39/39 (incluido fuzz); la simulación de despliegue pasa; TypeScript y `docker compose config` pasan. Esto no sustituye el baseline histórico completo ni las auditorías externas. El detalle reproducible se conserva en `IMPLEMENTATION_STATUS_2026-07-15.md`.

### Hallazgos de verificación que siguen bloqueando producción

1. **Migraciones desde cero:** `alembic upgrade head` sobre PostgreSQL vacío falla en la migración histórica `37751e240bf6`, que intenta alterar `playerboard` antes de que el historial de Alembic haya creado esa tabla. La migración nueva de edad/comercio sí fue probada desde el head anterior, pero eso no corrige el bootstrap limpio. Se requiere consolidar o reparar la historia y validarla desde una base vacía antes de cualquier despliegue.
2. **Baseline de pruebas:** los grupos focales afectados por esta intervención pasan, pero distintos subconjuntos históricos todavía exhiben fallos en unidades raw/display, fixtures lunares, gashapon y jackpot. Los conteos observados pertenecen a comandos parciales, no a un baseline global reproducible. Debe guardarse comando, imagen/runtime y JUnit por commit hasta lograr una suite completa verde.
3. **Economía pública:** las funciones anteriores permanecen en el repositorio para migración/desmantelamiento, pero no constituyen un producto monetizable seguro. Cambiar un flag no sustituye entidad, opinión legal, PSP real, KYC/fiscal, ledger fiat, reconciliación, contratos restringidos y aprobación de lanzamiento.
4. **Autoridad de cadena:** `CHAIN_ECONOMY_AUTHORITATIVE` expresa el objetivo, no el estado conseguido. Se cerraron fallbacks peligrosos en rutas de activos, pero wallets DB/outbox siguen siendo legado y aún falta el ciclo completo `intent → broadcast → mined → finalized`, indexador reproducible, reconciliación y modo económico read-only automatizado.
5. **Compliance de edad:** existen campos y guards, no un sistema completo. Faltan proveedor/método de age assurance, consentimiento parental verificable, KYC, procedencia de wallet y flujos de soporte/borrado.
6. **Comercio objetivo:** la tienda y marketplace actuales son legacy y permanecen prohibidos en `non_gambling`. El catálogo fijo, ledger MXN de creadores, reservas, refunds y payouts se deben construir como una ruta nueva.

Por tanto, el dictamen actualizado es: **GO para desarrollo y pruebas gratuitas cerradas; NO-GO para cobrar, pagar a creadores, ofrecer mercado público, mainnet o habilitar cualquier mecánica de valor.**
