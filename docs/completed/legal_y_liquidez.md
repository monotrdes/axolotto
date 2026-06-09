# Axolotto: Legalidad, Casas de Cambio y Retiros (Cash-Out)

Este documento analiza los riesgos legales, la viabilidad financiera del modelo de "Casa de Cambio" (Buyback/Spread) y las mejores prácticas de la industria (ej. Roblox DevEx) para evitar problemas regulatorios (CNBV, SEC, Lavado de Dinero).

---

## 1. El Concepto de Casa de Cambio (Spread, Reserva y Liquidez)

Vender Axogemas a un precio (ej. $10.00) y comprarlas a otro menor (ej. $7.00) es lo que en finanzas se llama **Spread (Diferencial)** de recompra. 

En teoría, esto es financieramente muy sano para ti porque:
1.  **Amortigua las salidas:** Evita la especulación rápida. Si alguien quiere meter dinero y sacarlo inmediatamente, asume un costo (spread del 30%).
2.  **Genera ingresos pasivos residuales:** Capturas el 30% del valor en cada ciclo de retiro de gemas.
3.  **Suelo de Valor:** Ofrece un precio piso claro a tus usuarios, aumentando la confianza y el volumen de adquisición.

### Resolución del Riesgo de Pánico Bancario (Bank Run)
Si tú eres la contraparte de recompra de las gemas con dinero real, corres el riesgo de que todos los jugadores retiren sus fondos a la vez (un Bank Run). 

Para resolver esto sin riesgo de quiebra, Axolotto implementa el **Modelo de Reserva 80/20**:
*   De cada venta de gemas a $10 USD, **$8 USD (80%)** se van a una reserva líquida intocable, y **$2 USD (20%)** se van a gastos operativos.
*   Al recomprar a **$7 USD (70%)**, la reserva siempre tiene un colchón de $1 USD extra (excedente) por cada gema emitida.
*   **Matemáticamente solvente:** Si todos los jugadores deciden retirar todo su dinero al mismo tiempo, la reserva puede liquidar al 100% de los usuarios a $7 USD y aún sobrará un excedente de $1 USD por gema retirada.

> [!IMPORTANT]
> **Regla de Oro:** Para que este modelo sea solvente, **nunca se deben emitir Axogemas (AXG) gratis ni a través de gameplay**. Si los jugadores pueden generar AXG de la nada jugando e intentar cobrarlas a $7 USD en dinero real, vaciarán la reserva. AXG es estrictamente un utility token de compra primaria. Su emisión por gameplay es de cero. Los premios son únicamente en GAL.

---

## 2. Implicaciones Legales: ¿Es Legal?

**Sí, pero con condiciones estrictas.** Si lo haces mal, puedes ser acusado de operar una captadora de dinero ilegal o un casino sin licencia.

### A. El Riesgo de ser Clasificado como "Security" (Valor Financiero)
Si tú vendes un token y prometes recomprarlo garantizando un valor de retorno o ganancias, la SEC (EE. UU.) o la CNBV (México) considerarán que estás vendiendo un **contrato de inversión**.
*   **Consecuencia:** Multas millonarias y bloqueo de la plataforma por vender valores no registrados.
*   **Cómo evitarlo:** 
    *   AXG debe definirse siempre como un **Utility Token** (Token de Utilidad) sin expectativa de ganancias.
    *   Tus Términos de Servicio (ToS) deben dejar en claro que las gemas no son depósitos bancarios ni instrumentos financieros, sino monedas de juego digital de entretenimiento.

### B. Leyes de Prevención de Lavado de Dinero (PLD/AML)
Si permites que los usuarios depositen dinero y retiren dinero real (Cash-Out) de forma directa:
*   Te conviertes ante la ley en un **MSB (Money Services Business)** o una entidad FinTech.
*   **Obligación legal:** Debes implementar **KYC (Know Your Customer)**. Esto significa pedir identificación oficial (INE/Pasaporte) y comprobante de domicilio a cualquier usuario antes de permitirle retirar dinero real. De lo contrario, los criminales podrían usar tu juego para blanquear dinero (tarjetas clonadas -> compran AXG -> retiran dinero limpio).

---

## 3. El Modelo Roblox: DevEx (Developer Exchange)

El modelo más seguro, legal y probado del mundo es el de **Roblox**:

```
[Usuario compra Robux] --> Tasa: 100 Robux = $1.00 USD (Venta primaria)
[Usuario gasta Robux en creadores] --> Roblox cobra 30% a 70% de Fee
[Creador solicita Cash-Out] --> Tasa DevEx: 100,000 Robux = $350.00 USD (Recompra)
```

### ¿Por qué el modelo de Roblox es 100% legal y no requiere licencia de banco?
1.  **No hay libre convertibilidad:** Un jugador normal no puede comprar Robux y luego "retirarlos" al banco al día siguiente. El Cash-Out (DevEx) está **exclusivamente reservado para creadores** que han aportado valor al juego (creando mapas, skins o tablas).
2.  **Tasa de Recompra Castigada (Spread Masivo):** Roblox recompra los Robux a una fracción de lo que los vende. Esto absorbe la inflación y les permite financiar la operación.
3.  **KYC y Verificación Obligatoria:** Para pasar por DevEx, el creador debe enviar sus documentos de identificación y formularios fiscales (W-8BEN / IRS).

---

## 4. Solución Propuesta para Axolotto

Para operar de forma 100% legal y sin riesgos de contracargos P2P o regulaciones complejas de custodia de divisas, se propone la siguiente arquitectura:

```
[Dinero Fíat/Cripto del Usuario] (Vía Mercado Pago / Stripe / Smart Contract)
              │
              ▼ (100% de la compra de AXG)
       ┌──────────────┐
       │ Emisión AXG  │ ──> [80% Reserva / 20% Tesorería]
       └──────────────┘
              │
              ▼ (Jugador compra AXG y las usa en el juego)
 ┌──────────┐      Compra P2P      ┌──────────┐
 │ JugadorA │ ───────────────────> │ JugadorB │ (Vende Carta Rara / Renta Tabla en AXG)
 └──────────┘                      └──────────┘
                                         │
                                         ▼ (AXG recibidas por JugadorB)
                                   [Retiro/Cash-Out (DevEx)]
                                         │ (Tasa de Recompra $7 por gema vendida a $10)
                                         │ (Requiere KYC / 14 días de retención anti-fraude)
                                         ▼
                                   [Pesos Fíat / USDT]
```

### Las 3 Reglas del Cash-Out (DevEx) en Axolotto:
1.  **Exclusión de Mercado Pago en el P2P:** Los jugadores no pueden utilizar Mercado Pago ni transferencias bancarias directas para realizar compras entre ellos en el Marketplace P2P. Toda transacción secundaria se liquida únicamente en AXG o GAL. Mercado Pago se reserva exclusivamente para la compra primaria de AXG del juego.
2.  **Periodo de Retención Anti-Fraude (14 Días):** Para mitigar los contracargos de tarjetas robadas o clonadas de Mercado Pago, cualquier cantidad de AXG recibida por un vendedor a través de transacciones P2P tendrá un periodo de bloqueo o retención de 14 días naturales antes de ser elegible para retiro/Cash-Out. Esto da tiempo suficiente para detectar y revertir fraudes de pago primarios.
3.  **Proceso de Retiro Regulado (DevEx con KYC):** El retiro de dinero real no es un derecho inmediato de retractación de compra. Solo se permite a creadores y jugadores que hayan acumulado AXG de forma legítima en el Marketplace P2P. La solicitud de retiro se procesa bajo los siguientes términos:
    *   **Tasa de Recompra fija:** Se paga a razón de $7 USD por cada gema (o equivalente en MXN) restando el spread del 30%, financiado directamente por la reserva del 80%.
    *   **Verificación obligatoria de KYC:** Integración con proveedores externos de verificación de identidad para cumplir con regulaciones anti-lavado de dinero (PLD/AML).

---

## 5. Estructura Bancaria, Custodia y Seguridad de Reservas

Para operar la plataforma de forma profesional, mitigar el congelamiento de cuentas y garantizar la seguridad de los activos de **Tridyland**, se establecen las siguientes directrices de infraestructura financiera:

### A. Estructura de Cuentas Fíat
1.  **Constitución Obligatoria de Persona Moral:** Se debe constituir una sociedad mercantil en México (sugerido: S.A.P.I. de C.V. o S.A. de C.V.) bajo la denominación de **Tridyland** o similar, con su respectivo Registro Federal de Contribuyentes (RFC).
2.  **Cuenta de Mercado Pago Empresa (Business):**
    *   **Prohibición de Cuentas Personales:** No se deben procesar los pagos del juego en una cuenta a nombre de Persona Física (cuenta personal). El algoritmo de Mercado Pago detectará un patrón inusual de depósitos recurrentes por venta de tokens digitales, marcando la cuenta bajo sospecha de lavado de dinero o captación ilegal y congelará el 100% de los fondos de forma automática e indefinida.
    *   **Apertura Corporativa:** Registrar la cuenta con el RFC de la Persona Moral, actas constitutivas, identificación del representante legal e información bancaria corporativa. Esto permite acceso a APIs avanzadas sin límites de transaccionalidad y soporte directo para disputas y contracargos.
3.  **Separación de Cuentas Operativas y de Reserva:**
    *   **Cuenta de Tesorería Operativa (20%):** Cuenta bancaria o de Mercado Pago de uso diario para pagar proveedores, marketing y sueldos.
    *   **Cuenta de Reserva Custodiada (80%):** Una cuenta de inversión separada (e.g. GBM Corporativo o CETES Directo Corporativo). Los fondos de esta cuenta son intocables y se dedican en su totalidad a garantizar la recompra del programa DevEx.

### B. Seguridad de Activos Criptográficos (Web3)
1.  **Custodia Multifirma (Multisig Wallet):**
    *   Los fondos criptográficos acumulados por compras con stablecoins en el smart contract de venta no deben almacenarse en hot wallets ordinarias (como cuentas individuales de MetaMask del equipo fundador).
    *   Se requiere implementar una billetera multifirma **Gnosis Safe** en la red Plasma o Mainnet.
    *   **Configuración del Umbral (Threshold):** Se recomienda un esquema de firmas **3-de-5** (mínimo 3 firmas de 5 llaves físicas autorizadas) o **2-de-3** en etapas iniciales.
2.  **Uso de Hard Wallets (Billeteras Frías):**
    *   Las llaves que controlan la multisig deben ser estrictamente dispositivos de hardware físicos (**Ledger** o **Trezor**).
    *   Las frases semilla de recuperación (*seed phrases*) de cada dispositivo deben estar respaldadas físicamente en metal y almacenadas en cajas de seguridad bancarias separadas físicamente.
3.  **Procedimientos de Emergencia (Planes de Contingencia):**
    *   **Pérdida de Llave:** Configurar la multisig con un esquema de recuperación social o un time-lock que permita agregar una nueva firma autorizada si una de las wallets físicas del equipo falla o se extravía, evitando el bloqueo perpetuo de fondos.
    *   **Monitoreo en Tiempo Real:** Configurar bots de alerta (e.g. OpenZeppelin Defender o Tenderly) en canales internos de comunicación para notificar al equipo al instante sobre cualquier transacción propuesta, firmada o ejecutada desde la multisig.

---

## 6. Régimen Fiscal ante el SAT (México)

Operar un juego Web3 con pasarelas fíat en México implica obligaciones fiscales estrictas ante el Servicio de Administración Tributaria (SAT).

### A. Impuesto al Valor Agregado (IVA - 16%)
1.  **Venta de Axogemas (AXG) como Servicio Digital:**
    *   Bajo la Ley del IVA mexicana, la enajenación de tokens de utilidad dentro de un juego digital se clasifica como la prestación de un **servicio digital de entretenimiento**.
    *   **Desglose Obligatorio:** Tridyland debe cobrar y desglosar el **16% de IVA** sobre cada compra de AXG. Si un usuario compra un paquete de 100 AXG a $10 USD, el desglose en su factura o comprobante debe indicar: $8.62 USD (Precio base de AXG) + $1.38 USD (IVA 16%) = $10.00 USD totales.
    *   El IVA recaudado no forma parte de los ingresos del juego; debe enterarse (pagarse) mensualmente al SAT, restándole el IVA acreditable de los gastos operativos (como servidores, APIs o publicidad).

### B. Impuesto Sobre la Renta (ISR) y la Reserva 80/20
1.  **Acumulación del Ingreso:**
    *   Para el SAT, el 100% de la venta base de la gema ($8.62 USD netos de IVA) representa un **ingreso acumulable** al momento de cobrarse, sin importar que Tridyland guarde el 80% en reserva.
    *   **Compensación de Ejercicio:** Al cierre fiscal, los ingresos acumulados por ventas se netean con los egresos deducibles pagados en el DevEx, reduciendo el pago final de ISR corporativo al margen de ganancia real obtenido.
2.  **Estrategia de Deducción sin Fricción (Esquema de Retención por Premios):**
    *   **El Reto:** La mayoría de los usuarios son estudiantes o videojugadores casuales sin RFC activo o e-firma, por lo que exigirles que emitan una factura CFDI para retirar sus fondos es inviable.
    *   **Solución (Régimen de Premios y Sorteos):** Tridyland estructura legalmente la dinámica de Axolotto como un **Concurso de Destreza** (torneo deportivo digital). Los retiros (DevEx) de los jugadores se liquidan fiscalmente bajo el régimen de **Premios**.
    *   **Retención Automatizada:** Tridyland realiza la retención de impuestos directamente de la solicitud de Cash-Out (1% federal de ISR + ~6% de impuesto local estatal, sumando un **~7% de impuesto retenido**). El jugador recibe el 93% restante directo en pesos a su cuenta bancaria.
    *   **Emisión de CFDI por la Empresa:** Tridyland emite un **CFDI de Retenciones y Pagos Efectuados** a favor del RFC del jugador (o al RFC genérico público si el jugador no cuenta con RFC individual). Este comprobante, emitido por la plataforma, es 100% deducible para Tridyland, evitando exigirle facturas electrónicas al usuario.
3.  **Alternativa Web3 Offshore (Fuera de la Jurisdicción del SAT):**
    *   Si los retiros se realizan en stablecoins (USDC/USDT) mediante una entidad holding constituida fuera de México (offshore en Panamá o Delaware), la transacción ocurre internacionalmente. La empresa extranjera compra de vuelta las gemas sin requerimientos de CFDIs locales, trasladando al usuario la responsabilidad individual de declarar sus ingresos por activos virtuales.

### C. Emisión de CFDIs Automatizados (Facturación)
1.  **CFDI Público General:** El backend debe generar de forma automática un CFDI global diario o mensual con el RFC genérico del SAT (`XAXX010101000`) para todas las compras de AXG realizadas por jugadores que no solicitaron factura individual.
2.  **CFDI Nominativo:** Si un usuario solicita factura de su compra de gemas, la plataforma debe permitirle ingresar su RFC y régimen fiscal en su perfil para emitirle el CFDI correspondiente por concepto de "Servicios de comercio electrónico".

---

## 7. Unificación Operativa: E-commerce y Juegos bajo una Persona Moral

Si estás considerando expandir tus operaciones comerciales hacia ventas en línea, Shopify, Amazon Seller, Mercado Libre o TikTok Shop, constituir una **Persona Moral** (empresa) bajo el **Régimen General de Ley** es la estrategia óptima para unificar la contabilidad y maximizar el flujo de efectivo.

### A. Ventajas de Operar E-commerce como Persona Moral vs. Persona Física
En México, el SAT clasifica las actividades comerciales de forma distinta según el tipo de contribuyente:
1.  **Si vendes como Persona Física (Plataformas Tecnológicas):**
    *   Plataformas como Amazon, Mercado Libre o TikTok Shop están obligadas a retenerte impuestos en cada venta realizada: **1% de ISR** y **8% de IVA**.
    *   Esta retención es automática y directa sobre tus ingresos brutos, lo cual disminuye tu capital de trabajo (flujo de caja) para comprar inventario.
2.  **Si vendes como Persona Moral (Régimen General):**
    *   **Exención de Retenciones:** Al registrar el RFC de tu empresa (Persona Moral) y subir tu Constancia de Situación Fiscal a Amazon, Mercado Libre o TikTok Shop, las plataformas **no te retendrán un solo peso**.
    *   Recibes el 100% del dinero cobrado por las ventas y declaras los impuestos sobre tu utilidad contable neta en tu contabilidad mensual regular.

### B. Trámites, Notarios y Papelería Requerida en México
Para constituir e iniciar la operación unificada de Tridyland, requieres realizar los siguientes pasos legales:
1.  **Autorización de Denominación Social:** Tramitado en la Secretaría de Economía. Sirve para reservar el nombre corporativo (ej. *Tridyland S.A. de C.V.*). (Sin costo, tarda 2-5 días).
2.  **Acta Constitutiva ante Notario o Corredor Público:**
    *   Se definen los estatutos, socios, porcentajes de acciones y el "Objeto Social".
    *   **Objeto Social Amplio:** Es vital redactar el objeto social para abarcar el desarrollo de videojuegos, pasarelas de pago, administración de activos virtuales, así como la comercialización, importación, exportación y distribución de de bienes de consumo a través de internet (e-commerce). Esto te permite facturar y operar tanto el juego como tus tiendas en línea bajo la misma empresa.
    *   *Costo:* De **$12,000 MXN a $18,000 MXN** ($600 - $900 USD) en promedio, dependiendo de la notaría.
3.  **Inscripción en el SAT y Firma Electrónica (e.firma):** Registro formal de la empresa para obtener su RFC corporativo y firma digital de la persona moral (esencial para emitir y recibir facturas CFDI). (Sin costo, requiere cita presencial).
4.  **Domicilio Fiscal (Oficina Virtual):** Si no cuentas con oficina física, puedes rentar un servicio de oficina virtual para recibir notificaciones del SAT. (*Costo:* **$500 MXN a $1,200 MXN mensuales**).
5.  **Contabilidad Mensual Corporativa:** Contratación de un despacho contable que gestione las declaraciones de impuestos (ISR, IVA, retenciones por premios). (*Costo:* **$2,500 MXN a $4,500 MXN mensuales** para operaciones iniciales).
