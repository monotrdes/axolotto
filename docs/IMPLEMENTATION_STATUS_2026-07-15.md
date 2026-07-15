# Estado de implementación — transición a producto sin apuestas

**Fecha:** 15 de julio de 2026  
**Alcance:** primera intervención P0 posterior a la auditoría integral  
**Dictamen:** apto para continuar desarrollo gratuito y cerrado; no apto para monetización o mainnet.

## Decisión adoptada

Axolotto se rediseña como videojuego gratuito y plataforma futura de artículos digitales:

- ninguna partida requiere una entrada o pone valor en riesgo;
- jugar o ganar no produce dinero, saldo retirable ni objetos revendibles;
- no hay jackpot, fondo de premios ni reparto de depósitos de otros jugadores;
- las compras futuras entregarán contenido conocido a precio fijo;
- sólo una venta concreta de una creación puede generar saldo fiat para su creador;
- AXF, FRJ, artículos y Creator Earnings son unidades distintas;
- la cadena es la autoridad objetivo sobre activos on-chain; PostgreSQL conserva identidad, compliance, órdenes, progresión no monetaria y contabilidad fiat. La implementación actual aún es híbrida y no puede declararse chain-authoritative hasta completar finality y reconciliación.

La especificación normativa está en `ADR-001-NON_GAMBLING_PRODUCT_MODEL.md`.

## Cambios implementados

### Contención económica

- Configuración pública `non_gambling` y flags económicos apagados por defecto.
- Partida CPU gratuita implementada: consume energía y conserva progresión, pero no consulta/modifica wallet, no cobra entrada, no crea ledger, no entrega premio y no mintea tokens.
- El modo gratuito rechaza multiplicadores, autoplay y presupuestos/límites económicos.
- La aplicación no monta rutas completas de pagos, checkout P2P ni marketplace cuando sus capacidades están apagadas.
- Guards defensivos en juego pagado, multiplayer, jackpot, mint administrativo, transferencias P2P, promociones, referidos, VIP, tienda aleatoria, marketplace, hatching, Reciclón y mutaciones de assets.
- El gateway simulado y los fallbacks Web3 sólo pueden existir en simulación local explícita.
- Los nuevos flujos de activos se rechazan si falla chain en las rutas contenidas; receipt/finality, indexador y reconciliación completos siguen pendientes y por eso la economía pública permanece apagada.
- Feed, expansión/aceleración de cueva y megáfono con saldo quedan apagados hasta reemplazar sus dual-writes legados.

### Cuentas, menores y comercio

- Nuevas bandas de edad: `unknown`, `under_13`, `teen_13_17`, `adult_18_plus`.
- Estados independientes de comercio, creador, KYC y aceptación de documentos.
- Política fail-closed: una cuenta desconocida puede completar el tutorial y jugar gratis, pero no comprar, vender, usar marketplace, vincular wallet ni retirar.
- El tutorial gratuito entrega sólo un Axo y una tabla de práctica DB-only, marcados como no transferibles y sin token/NFT; no simula propiedad on-chain.
- La vinculación de wallets desde `/auth/sync` está cerrada incluso para adultos hasta implementar challenge firmado y procedencia de la wallet.
- Menores no pueden vender ni retirar en el MVP; compras de menores quedan desactivadas hasta diseñar cuenta parental y obtener revisión jurídica.
- Hay campos, constraints y guards iniciales de edad/consentimiento; todavía no existe un sistema completo de age assurance, onboarding parental o KYC.

### Frontend y promesas públicas

- Hook de política pública que falla cerrado si la API no responde.
- Accesos CPU, paid/multiplayer, staking, VIP, tienda, P2P y recompensas usan capacidades explícitas; el cliente omite wallet y parámetros económicos en modo público.
- Tienda, Reciclón y marketplace muestran estado no disponible y no disparan flujos apagados.
- Landing reescrita alrededor de juego gratuito, colección y creación; sin afirmaciones de premio, yield, inversión, cashout o ingreso por jugar.

### Smart contracts

- Disolver una tabla quema realmente la carta elegida, devuelve las demás y limpia su estado.
- `ReciclonVault` sólo acepta el contrato de cartas configurado y deriva su contabilidad de transferencias ERC-1155 recibidas.
- Se eliminó el registro de recibos falsificable y el burn arbitrario; se agregaron invariants, fuzz y wiring de despliegue.
- `CartasLoteria` fija el vault una sola vez y sólo permite que éste queme sus propias cartas custodiadas.
- AXF y FRJ ya rechazan transferencias entre direcciones: son créditos cerrados de mint/burn. Una gobernanza futura deberá usar un instrumento separado.
- El burn del vault queda bajo un único owner rotatable; el deploy local exporta su dirección y la propiedad deberá transferirse a un Safe antes de producción.
- NFTs/cartas conservan transferibilidad estándar en los contratos actuales; sus rutas API están apagadas, pero esto sigue siendo un bloqueo de testnet pública/mainnet.

### Legal y operación

- Guía mexicana con ruta de constitución, menores, privacidad, propiedad intelectual, consumo, fiscalidad y preguntas para autoridades/proveedores.
- Matriz de capacidades por edad y propuesta de Safe 2-de-3, hardware wallets, roles separados, timelock, caps y alertas.
- Compose liga PostgreSQL, Anvil, backend y taskboard a loopback; esto reduce exposición local, pero no convierte por sí solo un despliegue en entorno privado.

## Evidencia de verificación de este corte

- Backend focal de política, cuenta, guards económicos, chain assets, tutorial/free play, staking, promo, social y crafting: **120 passed**.
- `compileall`: correcto.
- Foundry: **39/39 passed**, incluidos 256 casos fuzz del invariant de Reciclón y fuzz de no-transferibilidad AXF/FRJ.
- Simulación de `Deploy.s.sol`: correcta; incluye y reporta `ReciclonVault`.
- TypeScript: `tsc --noEmit --incremental false`, correcto.
- ESLint focal de archivos cambiados: 0 errores y 9 warnings heredados; el lint estricto amplio todavía falla por deuda legacy (`any`, imports/variables e imágenes).
- `docker compose config --quiet`: correcto; puertos sensibles ligados a `127.0.0.1`.
- Alembic reporta un solo head (`d5e6f7a8b9c0`) y la migración nueva fue validada desde el head anterior. El bootstrap desde base vacía sigue bloqueado por una migración histórica anterior.

Estos resultados son suites focales reproducibles, no una afirmación de que toda la suite histórica esté verde.

## Lo que deliberadamente sigue apagado

- cobros fiat o cripto;
- venta o retiro de AXF/FRJ;
- Creator Earnings y payouts;
- marketplace primario/secundario entre usuarios;
- P2P y wallets externas para menores;
- VIP con yield, staking económico, rentas y jackpot;
- loot boxes, cápsulas o huevos pagados;
- Reciclón, hatching y otras mutaciones de activos que aún no completan finality/reconciliación;
- DAO y gobernanza tokenizada.
- vinculación de wallet pública sin prueba criptográfica de control.

## Bloqueos antes de una prueba monetizada

1. Constituir la entidad y definir contabilidad/impuestos con abogado mercantil-fiscal y contador.
2. Obtener opinión escrita de abogado mexicano en videojuegos/plataformas/fintech y consulta preventiva ante SEGOB sobre la mecánica temática.
3. Elegir PSP de marketplace que soporte onboarding/KYC de vendedores, split o payouts, refunds y chargebacks en México.
4. Implementar ledger fiat doble-entry, reserva, conciliación y payout sólo después de ventana de riesgo.
5. Reparar el historial Alembic: hoy una base PostgreSQL vacía falla en `37751e240bf6` porque `playerboard` no existe.
6. Llevar la suite completa a verde. Hay fallos observados en subconjuntos históricos (unidades raw/display, fixtures lunares, gashapon/jackpot); no existe aún un baseline reproducible y verde del repositorio completo.
7. Completar chain finality, indexador, reconciliación y pausa automática por divergencia.
8. Restringir transferencias de NFTs/cartas, separar roles, usar Safe/timelock/caps y realizar auditoría externa. AXF/FRJ ya son no transferibles, pero sus permisos administrativos aún requieren ese hardening.
9. Implementar términos, privacidad, cookies, UGC/IP, moderación, reembolsos y aceptación versionada.
10. Ejecutar pentest, pruebas de carga, restauración de backups e incident drill antes de mainnet.
11. Implementar un launch manifest firmado/versionado; la aprobación de dos personas hoy es una regla documental, no un control técnico.
12. Construir una ruta comercial nueva para catálogo fijo y Creator Earnings MXN; no se deben reactivar los flags de tienda/marketplace legacy.
13. Añadir idempotency keys persistentes a juego/tutorial y pruebas concurrentes PostgreSQL; los locks actuales evitan lost updates, pero no sustituyen deduplicación de intención.
14. Antes de habilitar comercio, hacer que el frontend combine capacidades globales con `account_capabilities` (edad, consentimiento, KYC/creator), manteniendo al backend como autoridad.

## Contactos iniciales

En este orden:

1. abogado mexicano con experiencia conjunta en videojuegos/plataformas digitales, juegos y sorteos, fintech/activos virtuales, privacidad e IP;
2. contador fiscal con experiencia en marketplaces, pagos a creadores e IVA/ISR;
3. Secretaría de Economía y SAT para constitución/RFC/e.firma;
4. Dirección General de Juegos y Sorteos de SEGOB para obtener criterio por escrito antes de monetizar;
5. PSP de marketplace y proveedor KYC que operen formalmente en México;
6. IMPI/INDAUTOR para marca, licencias y registro de activos relevantes;
7. PROFECO y autoridad mexicana de privacidad para verificar obligaciones de consumo y datos.

Datos oficiales, enlaces y guion de preguntas: `STARTUP_LEGAL_MX.md`.

## Siguiente tramo recomendado

El siguiente tramo no debe reactivar funciones económicas. Debe:

1. reparar bootstrap de base de datos y baseline de pruebas;
2. diseñar el ledger de órdenes/Creator Earnings sin conectarlo todavía a dinero real;
3. implementar finality, indexación y reconciliación on-chain;
4. restringir NFTs/cartas y migrar administración de AXF/FRJ a multisig/roles/caps;
5. construir onboarding parental/adulto y aceptación legal versionada;
6. preparar un sandbox de catálogo fijo con creadores adultos invitados.

La habilitación futura debe requerir evidencia técnica, legal y operativa; no sólo el cambio de una variable de entorno.
