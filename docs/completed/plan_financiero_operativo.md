# Axolotto & Tridyland: Plan Financiero, Operativo y Fiscal Unificado

> [!IMPORTANT]
> **ESTE DOCUMENTO CONTIENE PROYECCIONES HISTÓRICAS Y DE DISEÑO INICIAL.**
> Para consultar los precios, tipos de cambio, comisiones y límites oficiales vigentes de Axolotto, dirígete a la [Biblia de Procesamiento de Precios y Tokens (token_prices_bible.md)](file:///home/monotr/axolotto/docs/token_prices_bible.md), la cual centraliza y unifica toda la configuración económica del sistema.

Este documento consolida la arquitectura económica, de precios, proyecciones financieras por fases de venta, estrategias fiscales ante el SAT y lineamientos de custodia de tesorería para **Axolotto** y **Tridyland**.

---

## 1. Modelo Económico de Reserva 80/20 y Recompra Solvente

Para que la plataforma sea económicamente viable y no corra riesgo de insolvencia (*bank run*) ni de asfixia de flujo por impuestos, el modelo de reserva y recompra se calcula sobre **ingresos netos de impuestos y comisiones**:

```
[Usuario paga $200.00 MXN ($10.00 USD) Bruto]
        │
        ├──> IVA (16% al SAT): $27.60 MXN ($1.38 USD)
        ├──> MP Fee (4.5% Pasarela): $9.00 MXN ($0.45 USD)
        └──> Neto Recibido por Tridyland: $163.40 MXN ($8.17 USD)
                  │
                  ├──> 80% ($130.80 MXN / $6.54 USD) ──> [Reserva Líquida de Respaldo]
                  │                                            │
                  │                                            └─── (Cash-Out / DevEx) ──> Paga $100.00 MXN ($5.00 USD)
                  │                                                                        └── Excedente: $30.80 MXN ($1.54 USD)
                  └──> 20% ($32.60 MXN / $1.63 USD) ──> [Tesorería Operativa (Gastos/Desarrollo)]
```

### Dinámica Financiera
1.  **Aportación Inicial:** Por cada compra de **100 AXG (equivalente a $200.00 MXN / $10.00 USD bruto)**, se deducen $27.60 MXN de IVA y $9.00 MXN de comisión de Mercado Pago. Del neto de **$163.40 MXN**, el **80% ($130.80 MXN)** va a la reserva de recompra y el **20% ($32.60 MXN)** va a la tesorería de desarrollo.
2.  **Tasa de Recompra Solvente (DevEx):** La plataforma garantiza la recompra de gemas legítimas obtenidas en el juego a una tasa de **$100.00 MXN ($5.00 USD)** por cada 100 AXG (spread de recompra del 50% sobre el precio de venta bruto).
3.  **Solvencia Matemática del 100%:** Como la reserva activa contiene $130.80 MXN por cada 100 AXG emitidas y la obligación máxima de recompra es de $100.00 MXN, el sistema cuenta con un respaldo del **130% sobre el pasivo de recompra**. Ante un pánico de retiros, el sistema liquida al 100% de los usuarios y conserva ganancias.
4.  **Distribución del Excedente de $30.80 MXN ($1.54 USD):**
    *   **50% ($15.40 MXN):** Destinado al **Fondo de Crecimiento y Jackpots** para recomprar GAL directamente del mercado y alimentar los pozos acumulados de la lotería activa.
    *   **50% ($15.40 MXN):** Destinado al **Fondo de Prevención de Fraude** para cubrir el costo de disputas y contracargos de Mercado Pago.
5.  **Emisión Cero de AXG por Gameplay:** La gema premium (AXG) jamás se otorga gratis. Las recompensas de juego se pagan únicamente en la moneda blanda **GAL** (Algas), la cual no tiene respaldo en la reserva de dinero real.

### B. Dinámica de Regalías P2P
*   **Comisión del 5% en el Marketplace P2P (Mercado Secundario):** En cada venta de Axolotitos, tablas o accesorios P2P (entre usuarios), la plataforma cobra un fee del **5% en AXG**. Si el Jugador A vende a Jugador B por 100 AXG, Tridyland recibe **5 AXG**.
*   **Margen Neto Libre de Pasivos (100% Utilidad):** A diferencia de las AXG compradas directamente, estas 5 AXG de comisión **ya están completamente respaldadas por la reserva** (por el dinero que el comprador depositó para adquirirlas inicialmente). Tridyland puede retirarlas de su cuenta y cambiarlas por dinero real en la reserva a la tasa DevEx ($5.00 USD por cada 100 AXG), quedándose con **$0.25 USD netos de ganancia pura (100% margen)** sin incurrir en nuevas deudas, o usarlas para fondear torneos.
*   **Rentas P2P (Comisiones en GAL):** Las transacciones de renta de tablas se liquidan en GAL. La plataforma cobra una comisión del **5% en GAL** en cada renta. **El 100% de este fee en GAL se quema (se destruye de circulación)** para regular la oferta, combatir la inflación de algas y asegurar que los activos en manos de los jugadores retengan su valor comercial a largo plazo.

### C. El Mecanismo de "Desbloqueo de Reservas" (Reserve Unlocking)
*   **Cómo funciona:** Cuando un jugador gasta sus gemas (AXG) en la tienda oficial para comprar Webitos primarios, boosters de cartas o upgrades permanentes, esas gemas **se queman y salen de circulación permanentemente**.
*   **Liberación de la Reserva:** Al quemarse el token, la obligación de recompra o pasivo del creador desaparece (ya no hay AXG circulantes que el usuario pueda canjear por $5.00 USD). Por ende, el **80% del valor neto ($6.54 USD por cada 100 AXG gastadas) que estaba bloqueado en la reserva se libera y pasa a ser 100% utilidad neta para Tridyland**.
*   **Alineación de Incentivos:** Esto hace que la ganancia del creador no dependa de bloquear capital a perpetuidad. Si los usuarios se divierten y compran activos virtuales en la tienda, el 100% del dinero ingresado (neto de impuestos y procesador) se desbloquea de la reserva convirtiéndose en ganancia del desarrollador.

---

## 2. Catálogo de Productos y Matriz de Precios

Para asegurar que cualquier persona pueda entrar a jugar y a la vez generar utilidades constantes, se definen los precios del catálogo maestro:

### A. Matriz de Precios Base y Reservas (Equivalencia: 1 AXG = $2 MXN / $0.10 USD)

| Producto | Categoría | Precio AXG | Precio Fíat (Bruto) | Margen Neto Operativo | Reserva de Respaldo (80% Neto) | Tasa de Recompra (50% Bruto) | Límite de Suministro (Supply) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Webito Génesis** | Huevo (Fase 1) | 50 AXG | **$100 MXN** ($5 USD) | $16.30 MXN | $65.40 MXN | **$50 MXN** ($2.5 USD) | 420 unidades |
| **Webito Expansión** | Huevo (Fase 2) | 100 AXG | **$200 MXN** ($10 USD) | $32.60 MXN | $130.80 MXN | **$100 MXN** ($5 USD) | 1,260 unidades |
| **Webito Retail** | Huevo (Fase 3) | 150 AXG | **$300 MXN** ($15 USD) | $48.90 MXN | $196.20 MXN | **$150 MXN** ($7.5 USD) | 2,520 unidades |
| **Booster Fiesta** | Booster (Fase 1) | 25 AXG | **$50 MXN** ($2.5 USD) | $8.15 MXN | $32.70 MXN | No aplica (Consumible) | 3,000 unidades |
| **Booster Nido** | Booster (Fase 1) | 25 AXG | **$50 MXN** ($2.5 USD) | $8.15 MXN | $32.70 MXN | No aplica (Consumible) | 3,000 unidades |
| **Booster Cosmos** | Booster (Fase 1) | 25 AXG | **$50 MXN** ($2.5 USD) | $8.15 MXN | $32.70 MXN | No aplica (Consumible) | 3,000 unidades |
| **Booster Mezclado** | Booster (Fase 1) | 15 AXG | **$30 MXN** ($1.5 USD) | $4.89 MXN | $19.62 MXN | No aplica (Consumible) | 5,000 unidades |
| **Tabla Clásica** | Tablero NFT | 10 AXG | **$20 MXN** ($1 USD) | $1.63 MXN | $6.54 MXN | **$10 MXN** ($0.5 USD) | Ilimitado |
| **Tabla de la Suerte** | Tablero NFT | 50 AXG | **$100 MXN** ($5 USD) | $8.15 MXN | $32.70 MXN | **$50 MXN** ($2.5 USD) | Ilimitado |
| **Tabla Pro Plasma** | Tablero NFT | 150 AXG | **$300 MXN** ($15 USD) | $24.45 MXN | $98.10 MXN | **$150 MXN** ($7.5 USD) | Ilimitado |
| **Lámpara Infrarroja Pro** | Consumible | 25 AXG | **$50 MXN** ($2.5 USD) | $8.15 MXN | $32.70 MXN | No aplica (Consumible) | Ilimitado |
| **Upgrade de Board Slots** | Slot Permanente | 50 AXG | **$100 MXN** ($5 USD) | $8.15 MXN | $32.70 MXN | No aplica (Utility) | Ilimitado |

### B. Paquetes de Divisas (AXG a GAL)

| Paquete de Algas | Costo AXG | Costo Fíat (Equivalente) | Cantidad de GAL otorgada | Valor Unitario por GAL | Bono Promocional |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Paquete Alga Común** | 10 AXG | **$20 MXN** ($1 USD) | 100 GAL | $0.20 MXN | Precio Base |
| **Paquete Alga Abundante** | 50 AXG | **$100 MXN** ($5 USD) | 550 GAL | $0.18 MXN | +10% GAL extra |
| **Paquete Alga Imperial** | 100 AXG | **$200 MXN** ($10 USD) | 1,200 GAL | $0.16 MXN | +20% GAL extra |
| **Súper Carga de Alga** | 500 AXG | **$1,000 MXN** ($50 USD) | 6,500 GAL | $0.15 MXN | +30% GAL extra |

### C. Recálculo del Costo Real de Entrada al Juego
Para que un jugador comience a competir de forma real en los lobbies multijugador, requiere:
1.  **1 Webito** (para incubar su primer Axolotito).
2.  **16 cartas únicas** (para poder fabricar su primer tablero de lotería). Como cada sobre/booster contiene 7 cartas, el usuario debe adquirir un mínimo de **3 boosters** (21 cartas en total) para armar su colección básica libre de repetidas.
3.  **1 Paquete de Algas (GAL)** para pagar la tarifa de fabricación del tablero y tener fondos para las tarifas de entrada (match fees).
    *   *Fabricación al azar:* Cuesta **25 GAL** (usa cartas del inventario aleatoriamente).
    *   *Diseño manual (Editor personalizado):* Cuesta **50 GAL** (permite elegir la posición exacta de cada carta para mejor estrategia).

A continuación se proyectan los costos reales según la fase y la estrategia de entrada (Económica vs. Premium):

#### Camino 1: Entrada Económica (Webito + 3 Boosters Mezclados + 1 Paquete Alga Común + Tablero al Azar o Manual)
*   **Webito:**
    - Fase 1: 50 AXG ($100 MXN / $5 USD)
    - Fase 2: 100 AXG ($200 MXN / $10 USD)
    - Fase 3: 150 AXG ($300 MXN / $15 USD)
*   **Cartas:** 3 Boosters Mezclados (3 * 15 AXG) = 45 AXG ($90 MXN / $4.50 USD).
*   **Algas:** 1 Paquete de Alga Común (100 GAL) = 10 AXG ($20 MXN / $1.00 USD).
    - *Fabricación:* El jugador fabrica su tablero al azar (25 GAL) o usando el editor manual (50 GAL) de su saldo de 100 GAL, conservando el excedente para las match fees iniciales.
*   **Costo de Entrada Total por Fases:**
    - **Fase 1 (Fundadores):** 105 AXG ➔ **$210.00 MXN** (~$10.50 USD)
    - **Fase 2 (Expansión):** 155 AXG ➔ **$310.00 MXN** (~$15.50 USD)
    - **Fase 3 (Retail/Lanzamiento):** 205 AXG ➔ **$410.00 MXN** (~$20.50 USD)

#### Camino 2: Entrada Premium Temática (Webito + 3 Boosters Temáticos + 1 Paquete Alga Común + Editor Manual)
*   **Webito:**
    - Fase 1: 50 AXG ($100 MXN)
    - Fase 2: 100 AXG ($200 MXN)
    - Fase 3: 150 AXG ($300 MXN)
*   **Cartas:** 3 Boosters Temáticos (Fiesta, Nido, Cosmos) (3 * 25 AXG) = 75 AXG ($150 MXN / $7.50 USD).
*   **Algas:** 1 Paquete de Alga Común (100 GAL) = 10 AXG ($20 MXN / $1.00 USD).
    - *Fabricación:* Fabricación premium en editor manual (50 GAL).
*   **Costo de Entrada Total por Fases:**
    - **Fase 1 (Fundadores):** 135 AXG ➔ **$270.00 MXN** (~$13.50 USD)
    - **Fase 2 (Expansión):** 185 AXG ➔ **$370.00 MXN** (~$18.50 USD)
    - **Fase 3 (Retail/Lanzamiento):** 235 AXG ➔ **$470.00 MXN** (~$23.50 USD)

*   *Análisis de Viabilidad:* Mantener el costo de entrada de fundadores en un rango de **$210 MXN a $270 MXN** garantiza una tasa de conversión de jugadores extremadamente alta. Es un precio sumamente competitivo para la economía mexicana y de América Latina.

---

## 3. Proyecciones Financieras por Fases de Agotamiento (Con Desbloqueo de Reservas)

A continuación, calculamos los ingresos brutos, netos y las utilidades finales reales de Tridyland conforme se agotan los suministros primarios limitados del juego. 

> [!IMPORTANT]
> **El Ciclo de Desbloqueo en Venta de Items:** 
> Cuando calculamos el agotamiento de una fase, asumimos que los jugadores compran las gemas AXG y **las gastan en la tienda oficial** para adquirir los Webitos y Boosters.
> Al gastarse en la tienda, las gemas se queman (se destruyen de circulación).
> Esto elimina el pasivo de recompra y **desbloquea el 80% de la reserva de forma inmediata**, haciendo que Tridyland capture el **100% del ingreso neto (81.7% del ingreso bruto)** como utilidad final para el desarrollador.
> La reserva solo retiene fondos para las gemas que los jugadores decidan conservar en su balance sin gastar, o para aquellas que estén activas en la economía secundaria P2P.

### Fase 1: Lanzamiento de Fundadores (Límites Agotados)
*   **Suministro Agotado:** 420 Webitos Génesis (50 AXG c/u) + 14,000 Boosters Temáticos (25/15 AXG c/u).
*   **Gemas Totales Gastadas y Quemadas:** $321,000$ AXG.
*   **Ingreso Bruto Fíat (Cobrado):** **$642,000.00 MXN** ($32,100.00 USD).
*   **IVA (16% al SAT):** $88,552.00 MXN ($4,427.60 USD).
*   **Comisión Pasarela Mercado Pago (4.5%):** $28,890.00 MXN ($1,444.50 USD).
*   **Ingreso Neto Recibido (Caja Operativa):** $524,558.00 MXN ($26,227.90 USD).
*   **Distribución inicial durante la compra:**
    - Reserva Temporal (80% del neto): $419,646.40 MXN.
    - Margen Operativo Inmediato (20% del neto): $104,911.60 MXN.
*   **Liberación de Reserva al comprar los items (Gemas quemadas):** **$419,646.40 MXN** se transfieren de la reserva a utilidades.
*   **Ganancia Neta Final del Desarrollador en Fase 1:** **$524,558.00 MXN** ($26,227.90 USD) – *100% del neto*.

---

### Fase 2: Expansión de Jugabilidad (Límites Agotados)
*   **Suministro Agotado:** 1,260 Webitos Expansión (100 AXG c/u).
*   **Gemas Totales Gastadas y Quemadas:** $126,000$ AXG.
*   **Ingreso Bruto Fíat (Cobrado):** **$252,000.00 MXN** ($12,600.00 USD).
*   **IVA (16% al SAT):** $34,758.00 MXN ($1,737.90 USD).
*   **Comisión Pasarela Mercado Pago (4.5%):** $11,340.00 MXN ($567.00 USD).
*   **Ingreso Neto Recibido (Caja Operativa):** $205,902.00 MXN ($10,295.10 USD).
*   **Liberación de Reserva al comprar los items (Gemas quemadas):** **$164,721.60 MXN** se liberan a utilidades.
*   **Ganancia Neta Final del Desarrollador en Fase 2:** **$205,902.00 MXN** ($10,295.10 USD) – *100% del neto*.

---

### Fase 3: Lanzamiento Minorista/Retail (Límites Agotados)
*   **Suministro Agotado:** 2,520 Webitos Retail (150 AXG c/u).
*   **Gemas Totales Gastadas y Quemadas:** $378,000$ AXG.
*   **Ingreso Bruto Fíat (Cobrado):** **$756,000.00 MXN** ($37,800.00 USD).
*   **IVA (16% al SAT):** $104,276.00 MXN ($5,213.80 USD).
*   **Comisión Pasarela Mercado Pago (4.5%):** $34,020.00 MXN ($1,701.00 USD).
*   **Ingreso Neto Recibido (Caja Operativa):** $617,704.00 MXN ($30,885.20 USD).
*   **Liberación de Reserva al comprar los items (Gemas quemadas):** **$494,163.20 MXN** se liberan a utilidades.
*   **Ganancia Neta Final del Desarrollador en Fase 3:** **$617,704.00 MXN** ($30,885.20 USD) – *100% del neto*.

---

### Totales Acumulados de Venta Primaria Limitada (Fases 1, 2 y 3 Agotadas)

| Métrica Financiera | Monto en Pesos (MXN) | Monto en Dólares (USD) | Tipo de Flujo de Efectivo |
| :--- | :--- | :--- | :--- |
| **Ingreso Bruto Acumulado** | **$1,650,000.00 MXN** | **$82,500.00 USD** | Cobro Total de Pasarelas |
| **IVA (16% enterado al SAT)** | $227,586.00 MXN | $11,379.30 USD | Impuesto trasladado (Egreso) |
| **Comisiones de Pasarela (4.5%)** | $74,250.00 MXN | $3,712.50 USD | Costo de Procesamiento (Egreso) |
| **Neto Recibido en Caja (Caja)** | **$1,348,164.00 MXN** | **$67,408.20 USD** | Ingreso Corporativo Neto (81.7%) |
| **Fondo de Reserva de Respaldo** | $0.00 MXN | $0.00 USD | **$1,078,531.20 MXN Liberado de Reserva** |
| **Ganancia Neta Final (Tridyland)** | **$1,348,164.00 MXN** | **$67,408.20 USD** | **100% del Neto es Utilidad Corporativa** |

*   *El Rendimiento a Largo Plazo:* Al agotarse la venta de activos primarios, Tridyland conserva el **100% de la caja neta ($1,348,164.00 MXN)**. A partir de ese momento, la fuente de ingresos del desarrollador pasa a ser de forma exclusiva las **regalías recurrentes del 5% en AXG** en el Marketplace P2P sobre todas las reventas de Axolotitos y cartas raras de la comunidad, las cuales se capitalizan directamente de la reserva y representan utilidades netas directas y pasivas a perpetuidad.

## 4. Estrategias Legales contra la Fricción del CFDI de Retiro

En México, exigirle a un videojugador o creador casual que emita una factura electrónica (CFDI) para poder retirar su dinero destruiría la experiencia de usuario y el volumen de juego. Para evitar esto, Tridyland puede optar por tres esquemas de estructuración legal:

### Opción A: Régimen de Retención por Premios y Sorteos (Recomendado)
*   **Definición Legal:** El juego y sus lobbies multijugador se registran en los Términos de Servicio (ToS) como un **Concurso Deportivo y de Destreza**. El Cash-Out de AXG se clasifica fiscalmente como el pago de un **Premio**.
*   **Tasas de Impuestos Bajas:** En México, la Ley del ISR fija una retención federal del **1%** por premios, y los estados aplican un impuesto local (promedio del **6%** en la mayoría del país). La retención total automatizada es de solo **~7%**.
*   **Fricción Cero:** El jugador solicita retirar $1,000 MXN. El sistema calcula y retiene de forma automática $70 MXN de impuestos, transfiriéndole al jugador $930 MXN a su cuenta bancaria.
*   **Autofacturación Corporativa:** Tridyland emite mensualmente un **CFDI de Retenciones y Pagos Efectuados** a favor del RFC del jugador (o al RFC genérico público si el jugador no está registrado). Este CFDI emitido por la empresa es el soporte fiscal completo que exige el SAT para deducir el 100% de los egresos por retiros, liberando por completo al usuario de emitir facturas.

### Opción B: Régimen de Plataformas Tecnológicas de Intermediación
*   **Definición Legal:** Tridyland se registra ante el SAT como plataforma digital intermediaria de comercio electrónico (como Uber o Mercado Libre) para el Marketplace P2P de Axolotto.
*   **Retención Directa:** La plataforma realiza una retención mensual fija del impuesto del usuario (generalmente 1% a 2.1% de ISR en servicios y 8% de IVA) y la paga directamente al SAT.
*   **Soporte Fiscal:** La plataforma emite de forma mensual una **Constancia de Retenciones** al usuario. Tridyland deduce los gastos de su base impositiva con este documento interno, evitando requerir facturas de los jugadores.

### Opción C: Estructura Holding Offshore (Web3 Cripto)
*   **Definición Legal:** Se crea una empresa controladora (holding) en una jurisdicción con leyes fiscales favorables para activos digitales (e.g. Delaware, Panamá o Islas Vírgenes Británicas). Esta empresa es la dueña del smart contract y las reservas de stablecoins.
*   **Flujo de Retiro Cripto:** Los retiros de dinero real se solicitan y se pagan exclusivamente en stablecoins (USDC/USDT) desde la entidad offshore directamente a la wallet del usuario.
*   **Sin SAT en el Retiro:** Al ser una transacción de activos virtuales realizada fuera del territorio mexicano por una entidad extranjera, Tridyland México no tiene obligaciones de retención ni CFDI locales. El usuario es responsable de declarar y pagar sus impuestos por ganancias cripto de forma individual.

---

## 5. Estructura Corporativa y Unificación Comercial (Tridyland)

Para realizar ventas físicas (TikTok Shop, Shopify, Amazon Seller, Mercado Libre) y digitales (Axolotto) de manera formal en México, se implementará la constitución de una **Persona Moral** bajo el **Régimen General de Ley**:

### A. Ventajas en E-commerce de la Persona Moral vs. Persona Física
1.  **Exención de Retenciones Directas en Canales de Venta:** Plataformas como Amazon, Mercado Libre o TikTok Shop están obligadas a retener el **1% de ISR** y el **8% de IVA** sobre cada venta a las personas físicas. A las Personas Morales, al presentar su RFC corporativo y Constancia de Situación Fiscal, **no se les retiene ningún impuesto**. Recibes el 100% del dinero cobrado y declaras sobre utilidades netas a final de mes.
2.  **Unificación de Deducibles:** Todos los gastos de infraestructura digital (servidores AWS/Vercel, APIs de pago, software de diseño, contabilidad) incurridos para el juego Axolotto se pueden deducir del ISR generado por las ventas físicas del e-commerce, reduciendo drásticamente la carga de impuestos global.

### B. Trámites y Papelería Requerida para Constituir la Empresa
1.  **Autorización de Nombre:** Solicitud del nombre corporativo (ej. *Tridyland S.A. de C.V.*) en el portal de la Secretaría de Economía (Gratuito, 2-5 días).
2.  **Redacción de Estatutos y Firma ante Notario o Corredor Público:**
    *   **Objeto Social Amplio:** Es indispensable incluir el desarrollo de videojuegos, licenciamiento de marcas, pasarelas de pago, bases de datos de activos virtuales, así como la comercialización, importación y exportación de productos de consumo general por medios electrónicos (e-commerce).
3.  **Inscripción al SAT y e.firma:** Obtención del RFC corporativo y firma electrónica de la empresa en oficinas del SAT.
4.  **Cuentas Bancarias y Agregadores Corporativos:** Apertura de cuentas de banco comerciales (BBVA, Clara, etc.) y cuentas de negocio en Mercado Pago y Stripe.

### C. Desglose de Costos de Inicio y Operación Mensual (MXN)
*   **Honorarios del Notario (Acta Constitutiva):** **$12,000 MXN a $18,000 MXN** (Pago único).
*   **Domicilio Fiscal (Oficina Virtual):** **$500 MXN a $1,200 MXN mensuales** (Para notificaciones del SAT).
*   **Contador Mensual Corporativo:** **$2,500 MXN a $4,500 MXN mensuales** (Encargado de la contabilidad, IVA, ISR y retenciones de premios).
*   **Inversión Inicial Total de Apertura Legal:** **$15,000 MXN a $22,000 MXN** (~$750 - $1,100 USD).

---

## 6. Custodia Cripto y Rendimientos Pasivos de Reservas

Para los fondos de reserva en criptomonedas (USDC/USDT) recolectados por compras directas Web3:

### A. Custodia Multifirma (Multisig Wallet)
*   **Billetera Gnosis Safe:** Los tokens se almacenan en un contrato multifirma con esquema de firmas **3-de-5** o **2-de-3**.
*   **Dispositivos de Hardware:** Los firmantes autorizados utilizarán billeteras frías físicas (**Ledger** o **Trezor**). Las frases semilla se graban en tarjetas de metal y se guardan bajo llave en cajas de seguridad de diferentes sucursales bancarias.

### B. Rendimientos Pasivos en DeFi (Ratio de Seguridad 50/50)
1.  **50% Líquido en Multisig:** Permanece en balance sin invertir para procesar con rapidez los retiros de los usuarios y evitar pagar altos gas fees de desinversión constantes.
2.  **50% en Lending de Aave v3:** Se deposita en los pools de préstamo de **Aave v3** en una red L2 o Plasma Chain de bajo coste para generar un rendimiento anual flotante del **4% al 10%** en stablecoins.
3.  **Prohibición de Colaterales Volátiles:** Queda estrictamente prohibido hacer staking o proveer liquidez con activos de precio volátil (e.g. ETH, MATIC, AXG) para evitar pérdidas impermanentes (*impermanent loss*) que comprometan el respaldo total de recompra.
4.  **Monitoreo de Paridad:** La tesorería cripto se diversifica en un **50% USDC** y **50% USDT** para mitigar el riesgo de pérdida de paridad (depeg) de una sola stablecoin.

---

## 7. Análisis Comparativo de Mercado (Roblox, Web3 y TCG) y Estrategia de Precios

Para determinar si los precios propuestos para **Axolotto** son adecuados o si el juego se está vendiendo por debajo de su valor real, se ha realizado un desglose profundo de los competidores más exitosos en Roblox (economías cerradas de alto volumen) y en la Web3/TCG (economías abiertas y competitivas).

### A. Benchmarks del Mercado de Videojuegos (Robux, USD y Cripto)

#### 1. Ecosistema Roblox: Gacha, Mascotas y Power-ups Permanentes
En Roblox, los jugadores compran Robux a un tipo de cambio estándar de **$0.0125 USD por 1 Robux** (o 100 Robux = $1.25 USD / $25.00 MXN). Los juegos más rentables monetizan de la siguiente forma:

*   **Pet Simulator 99 (Gacha de Mascotas y Consumibles):**
    *   *Exclusive Eggs (Huevos de Gacha):* Cuestan **400 Robux (~$5.00 USD / $100.00 MXN)** por un hatch de mascota exclusiva aleatorio. Los paquetes de 8 huevos cuestan **3,200 Robux (~$40.00 USD / $800.00 MXN)**.
    *   *Exclusive Card Packs (Sobres de Cartas Digitales):* Cuestan **99 Robux (~$1.25 USD / $25.00 MXN)** por sobre individual, y **2,699 Robux (~$33.75 USD / $675.00 MXN)** por un paquete de 30 sobres.
    *   *Gamepasses Permanentes (Utility Boosts):* Cuestan desde **175 Robux (~$2.20 USD)** hasta **3,250 Robux (~$40.60 USD / $810.00 MXN)** (el pase de "Huge Hunter" que solo aumenta la probabilidad de obtener mascotas de tipo "Huge").
*   **Adopt Me! (Mascotas y Coleccionismo de Rol):**
    *   *Mascotas de la Tienda de Robux:* Mascotas icónicas como el *Axolotl* o *Cerberus* costaban de **500 a 600 Robux (~$6.25 a $7.50 USD / $125.00 a $150.00 MXN)** de forma unitaria cuando estaban en la tienda oficial.
*   **Blox Fruits (Poderes y Habilidades Permanentes):**
    *   *Frutas Permanentes de Alto Rango (Kitsune, Dragon):* Cuestan de **4,000 a 5,000 Robux (~$40.00 a $50.00 USD / $800.00 a $1,000.00 MXN)** por una sola habilidad permanente.
    *   *Frutas Permanentes de Rango Medio (Buddha, Portal):* Cuestan de **1,650 a 2,000 Robux (~$20.60 a $25.00 USD / $410.00 a $500.00 MXN)**.

> [!NOTE]
> **Lección de Roblox:** Los usuarios de Roblox están plenamente habituados a pagar de **$5.00 a $50.00 USD** por activos 100% digitales y cerrados, sin posibilidad de reventa legal, alquiler o retiro de dinero real (el jugador no recibe rendimiento alguno).

#### 2. Ecosistema Web3 y Juegos de Cartas Coleccionables (TCG)
En los juegos con propiedad digital real (NFTs o criptomonedas), la monetización es más alta debido al valor especulativo y a la utilidad financiera:

*   **Splinterlands (TCG de Batalla Rápida):**
    *   *Ticket de Entrada (Summoner's Spellbook):* Obligatorio para jugar y ganar recompensas, cuesta **$10.00 USD ($200.00 MXN)**.
    *   *Booster Packs (Sobres de 5 Cartas):* Cuestan **$4.00 USD ($80.00 MXN)** c/u.
*   **Gods Unchained (TGC Tradicional Competitivo):**
    *   *Booster Packs (Sobres de 5 Cartas):* Cuestan desde **$2.49 USD** (Rare Pack) hasta **$149.99 USD** (Shiny Legendary Pack) para coleccionistas de cartas brillantes.
*   **Axie Infinity (Combate de Mascotas/Cartas NFT):**
    *   *Entrada Competitiva:* Aunque es gratis para probar, jugar de forma competitiva para ganar tokens requiere comprar un equipo de 3 Axies NFT en el mercado secundario. El precio mínimo (floor price) en 2026 oscila entre **$5.00 y $20.00 USD por mascota**, sumando un ticket de entrada real de **$15.00 a $60.00 USD ($300.00 a $1,200.00 MXN)**.

---

### B. La Gran Ventaja Económica de Axolotto: Economía Abierta con Respaldo

La diferencia clave entre Axolotto y Roblox es la **Soberanía y Respaldo Financiero**:
1.  **Roblox (Economía Cerrada):** Si un jugador gasta $20.00 USD en Robux, ese dinero se evapora para él. El valor de reventa es $0.00 USD (está prohibido por los ToS).
2.  **Axolotto (Economía Abierta 80/20):** Si un jugador gasta **200 AXG ($20.00 USD / $400.00 MXN)** en el juego:
    *   Tiene un **valor de salida (DevEx) garantizado por contrato de $10.00 USD** (50% del valor de compra).
    *   Los activos (Axolotitos, Tablas, Cartas) son suyos. Puede rentarlos en el marketplace para generar ingresos pasivos (GAL) o revenderlos a otros usuarios en AXG.
    *   Debido a este "piso de valor" (floor price), los jugadores de Axolotto son **significativamente menos sensibles al precio**. Saben que están comprando un activo con valor de rescate, lo que justifica precios de venta primarios más elevados que en los juegos tradicionales.

---

### C. Estrategia de Captura de Valor: Mantener Entrada Accesible + Añadir "Whale Tiers" (Monetización para Ballenas)

Si subimos demasiado el precio de entrada base (el costo mínimo para jugar), limitaremos el crecimiento de la base de usuarios en México y América Latina, afectando la liquidez del mercado P2P. 
La estrategia óptima no es hacer el juego inaccesible para los jugadores comunes, sino **crear productos premium de alto costo dirigidos a coleccionistas, creadores de contenido y jugadores de alto presupuesto (ballenas)**.

#### Propuesta de Nuevos Productos Premium y Alta Monetización

1.  **Booster Packs Brillantes (Foil Boosters):**
    *   *Mecánica:* Sobres premium de 7 cartas que garantizan al menos una carta **Shiny/Foil** (brillante) con efectos visuales especiales on-chain.
    *   *Precio:* **100 AXG ($200.00 MXN / $10.00 USD)** (un incremento de 4x sobre el booster mezclado).
2.  **Webitos de Temporada / Edición Especial (Limited Eggs):**
    *   *Mecánica:* Huevos temáticos de disponibilidad ultra-limitada (ej. 100 unidades al año) con skins exclusivas o variantes visuales raras.
    *   *Precio:* **500 AXG ($1,000.00 MXN / $50.00 USD)**.
3.  **Pase de Club VIP (Suscripción Mensual):**
    *   *Mecánica:* Suscripción de 30 días que otorga un marco cosmético dorado, un bono diario de +10 GAL por log-in y acceso a torneos VIP exclusivos.
    *   *Precio:* **50 AXG/mes ($100.00 MXN / $5.00 USD)**.
4.  **Tablas de Lujo Animadas (Custom Board Skins):**
    *   *Mecánica:* Tablas cosméticas con animaciones de fondo, efectos de sonido al marcar casillas y diseño personalizado.
    *   *Precio:* **250 AXG ($500.00 MXN / $25.00 USD)**.

---

### D. Matriz de Precios Optimizada Final (Incluyendo Tiers Premium)

Esta matriz mantiene la base competitiva propuesta anteriormente (que ya duplicaba o triplicaba el margen del juego original) y añade los nuevos productos de alta monetización para exprimir el valor de los usuarios de alto poder adquisitivo:

| Ítem del Juego | Tipo de Ítem | Precio AXG | Precio Fíat (Bruto) | Margen Neto Operativo (20%) | Reserva Respaldada (80% Neto) | Tasa de Recompra (50% Bruto) | Objetivo de Mercado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Webito Génesis (Fase 1)** | Huevo Fundador | 250 AXG | **$500 MXN** ($25 USD) | $81.50 MXN | $327.00 MXN | **$250 MXN** ($12.5 USD) | Coleccionistas / Hype Inicial |
| **Webito Expansión (Fase 2)** | Huevo Estándar | 150 AXG | **$300 MXN** ($15 USD) | $48.90 MXN | $196.20 MXN | **$150 MXN** ($7.5 USD) | Jugador Promedio (Early) |
| **Webito Retail (Fase 3)** | Huevo Comercial | 200 AXG | **$400 MXN** ($20 USD) | $65.20 MXN | $261.60 MXN | **$200 MXN** ($10.0 USD) | Jugador Promedio (Lanzamiento) |
| **Booster Temático (7 c)** | Cartas Comunes | 35 AXG | **$70 MXN** ($3.5 USD) | $11.41 MXN | $45.78 MXN | No aplica (Consumible) | Progresión Básica |
| **Booster Mezclado (7 c)** | Cartas Económicas| 20 AXG | **$40 MXN** ($2.0 USD) | $6.52 MXN | $26.16 MXN | No aplica (Consumible) | Entrada Accesible |
| **Tabla de la Suerte (+10%)** | Tablero NFT Raro | 50 AXG | **$100 MXN** ($5.0 USD) | $8.15 MXN | $32.70 MXN | **$50 MXN** ($2.5 USD) | Jugador Frecuente |
| **Tabla Pro de Plasma (+20%)** | Tablero NFT Épico | 150 AXG | **$300 MXN** ($15 USD) | $24.45 MXN | $98.10 MXN | **$150 MXN** ($7.5 USD) | Jugador Competitivo |
| **Gotas Anti-Escarcha** | Consumible Base | 0 AXG | **150 GAL** (Gratis) | No aplica | No aplica | No aplica | Retención de Jugador F2P |
| **Lámpara Infrarroja Pro** | Consumible Premium| 25 AXG | **$50 MXN** ($2.5 USD) | $4.08 MXN | $16.35 MXN | No aplica (Consumible) | Comodidad y Protección |
| **Upgrade de Board Slots** | Utilidad Slot | 50 AXG | **$100 MXN** ($5.0 USD) | $8.15 MXN | $32.70 MXN | No aplica (Utility) | Jugadores Activos |
| **Pase VIP Club (30 días)** | Suscripción / Pase | 50 AXG | **$100 MXN** ($5.0 USD) | $16.30 MXN (100% Neto)* | No aplica | No aplica | Recurrencia Mensual |
| **Booster Brillante (Foil)** | Sobres Colección | 100 AXG | **$200 MXN** ($10 USD) | $32.60 MXN | $130.80 MXN | No aplica (Consumible) | Whales / Coleccionistas |
| **Webito Astral (Limitado)** | Huevo Ultra-Raro | 500 AXG | **$1000 MXN** ($50 USD) | $163.40 MXN | $654.00 MXN | **$500 MXN** ($25.0 USD) | Whales / Especuladores |
| **Tabla Cósmica Animada** | Skin Animada | 250 AXG | **$500 MXN** ($25 USD) | $81.70 MXN (100% Neto)* | No aplica | No aplica | Cosmético de Prestigio |

*\*Nota: Los cosméticos puros (como la Tabla Cósmica) y los pases de servicio (VIP Club) que no tienen valor de recompra líquida ni DevEx no cargan pasivos sobre la reserva, por lo que el 100% de su ingreso neto se libera de forma directa a la tesorería de desarrollo.*

### E. Costo de Entrada y Jugabilidad Balanceada (Fase 2)
Al mantener la estructura base con los nuevos precios optimizados, el costo para entrar a jugar de forma real y competitiva se mantiene en un rango balanceado:
*   **Entrada Económica:** 1 Webito Expansión ($300 MXN) + 3 Boosters Mezclados ($120 MXN) + 1 Paquete Alga Común ($20 MXN) = **$440.00 MXN (~$22.00 USD)**.
*   **Entrada Premium Temática:** 1 Webito Expansión ($300 MXN) + 3 Boosters Temáticos ($210 MXN) + 1 Paquete Alga Común ($20 MXN) = **$530.00 MXN (~$26.50 USD)**.

Este balance permite que **cualquier persona en México y Latinoamérica acceda por menos de $500 MXN**, pero abre la puerta para que aquellos usuarios dispuestos a gastar más (comprando Boosters Brillantes, Webito Astral, y la Tabla Cósmica Animada) puedan gastar **más de $2,000.00 MXN ($100.00 USD) en su primer día**, disparando la rentabilidad neta del proyecto.
