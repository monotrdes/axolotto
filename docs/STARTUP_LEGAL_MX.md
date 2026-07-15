# Guía de arranque legal y de producto para Axolotto en México

**Fecha de revisión:** 15 de julio de 2026  
**Estado del proyecto considerado:** etapa temprana, sin sociedad constituida, permisos ni operación comercial pública  
**Alcance:** ruta práctica para diseñar Axolotto como videojuego y mercado de artículos digitales, reduciendo el riesgo de que sea considerado juego con apuesta, sorteo, captación o servicio financiero.

> **Aviso importante:** este documento es una guía de preparación y diseño basada en fuentes oficiales vigentes a la fecha indicada. No es un dictamen legal, fiscal, financiero ni regulatorio. La clasificación depende de la operación real, no del nombre comercial utilizado. Antes de cobrar, permitir retiros o lanzar en mainnet se requiere una opinión escrita de profesionales mexicanos que conozcan la mecánica completa.

---

## 1. Decisión de producto recomendada

Axolotto debería presentarse y operar como:

> **Videojuego de entretenimiento y creación digital con un marketplace curado donde creadores adultos venden artículos digitales de contenido conocido.**

No debería operar como:

- una plataforma en la que se paga para participar en una mecánica aleatoria con posibilidad de obtener algo canjeable por dinero;
- un sistema de premios financiado con entradas o depósitos de otros jugadores;
- una inversión, producto de rendimiento, fondo común o mecanismo para ganar dinero sólo por jugar;
- una casa de cambio, custodio o mercado abierto de tokens;
- una DAO, plataforma descentralizada o economía autónoma mientras una sola persona conserve el control administrativo.

### 1.1 Regla de oro contra la clasificación como apuesta

La combinación que debe evitarse es:

`pago o cosa de valor + azar + premio con valor económico`

Por diseño, Axolotto debe separar estos elementos:

- El azar puede existir como entretenimiento dentro de una partida, pero no debe repartir dinero, saldo retirable ni objetos comercializables.
- Una compra debe entregar contenido fijo, visible y descrito antes de pagar.
- Las ganancias de un creador deben surgir de una venta identificable de una obra o artículo que ese creador produjo, no de ganar partidas.
- Los puntos obtenidos por jugar no deben convertirse en dinero, activos comercializables ni saldo de creador.

La Dirección General de Juegos y Sorteos de SEGOB indica que los juegos con apuestas y los sorteos, en sus distintas modalidades, requieren permiso expreso. Incluso existen trámites para sorteos sin venta de boletos; por ello, **la ausencia de una cuota de entrada no basta por sí sola para descartar la competencia de SEGOB**. La mecánica de lotería de símbolos debe consultarse por escrito antes de un lanzamiento público monetizado.

### 1.2 Mecánicas aceptables para el diseño objetivo

- Partidas gratuitas o incluidas en una suscripción de precio fijo.
- Progresión, experiencia, logros y puntos ligados a la cuenta.
- Recompensas cosméticas no transferibles y sin valor de retiro.
- Venta directa de skins, mapas, animaciones, música, accesorios o experiencias cuyo contenido se conoce antes de pagar.
- Suscripción que entrega beneficios fijos y claramente enumerados.
- Concurso creativo o de habilidad con bases revisadas previamente por abogado y, cuando corresponda, SEGOB.
- Marketplace de contenido creado por usuarios, con revisión de propiedad intelectual y moderación.

### 1.3 Mecánicas que no deben lanzarse

- Sobres, cofres o loot boxes comprados que contengan objetos con valor de reventa.
- Jackpot, bote, pozo, bolsa o premio financiado por pagos de jugadores.
- Entrada pagada a una partida que pueda entregar un premio de valor.
- Retiro de recompensas ganadas por azar o por jugar partidas.
- Conversión de FRJ, AXF o premios de juego a MXN, cripto u otro activo transferible.
- P2P libre fuera del marketplace controlado.
- Referidos en los que el participante gane por incorporar nuevos pagadores.
- Promesas de apreciación, rentabilidad, ingreso pasivo o futura participación en utilidades.
- Venta anticipada de un token de DAO.

---

## 2. Arquitectura económica recomendada

La separación contable y técnica debe ser real, no sólo nominal.

| Unidad | Cómo se obtiene | Transferencia | Retiro | Uso permitido |
|---|---|---:|---:|---|
| **FRJ — puntos de juego** | Sólo por actividad gratuita o incluida | No | No | Progresión y consumibles ligados a cuenta |
| **AXF — créditos cerrados** | Compra directa o promoción claramente descrita | No | No | Comprar contenido fijo dentro de Axolotto |
| **Artículo digital** | Compra directa o creación aprobada | Sólo dentro del marketplace y cuando se autorice | No es dinero | Licencia de uso o propiedad digital según sus términos |
| **Saldo del creador en MXN** | Venta completada de una creación propia | No entre usuarios | Sí, sólo 18+, KYC y fiscal | Pago al creador después de devoluciones y reservas |

### 2.1 Consecuencias técnicas

- Los contratos actuales de FRJ y AXF ya bloquean transferencias entre direcciones y sólo permiten mint/burn autorizado. Antes de desplegarlos aún faltan caps, roles separados, Safe/timelock y auditoría externa.
- Una futura DAO debe usar un instrumento y análisis jurídico separados; no se debe volver transferible FRJ/AXF para improvisar gobernanza.
- La interfaz debe llamarlos **puntos** o **créditos**, no inversión, moneda o activo con respaldo.
- No debe existir un par AXF/MXN, AXF/FRJ o FRJ/MXN utilizable por usuarios para retiro.
- El saldo del creador debe ser un pasivo contable en MXN separado de ambos tokens.
- Las compras, devoluciones, impuestos, comisión, reserva y saldo pagable deben registrarse por separado.
- La contabilidad debe poder explicar qué comprador financió qué venta y a qué creador corresponde.

### 2.2 La blockchain como fuente de verdad

La cadena puede ser la fuente técnica de verdad para:

- identidad del contrato;
- emisión, propiedad y transferencia autorizada de artículos;
- historial de operaciones;
- reglas de escasez previamente publicadas;
- eventos que alimentan una proyección de lectura en la base de datos.

No puede ser la autoridad final sobre:

- obligaciones fiscales;
- devoluciones y bonificaciones legalmente procedentes;
- protección de datos;
- derechos de menores;
- titularidad de propiedad intelectual no adquirida válidamente;
- órdenes administrativas o judiciales.

Cuando una operación on-chain no pueda revertirse, los términos deben explicar el mecanismo compensatorio: devolución de dinero, bloqueo, recompra, reemisión o transferencia correctiva autorizada. No debe afirmarse que la irreversibilidad elimina derechos del consumidor.

### 2.3 Cómo pagar a jugadores sin crear un fondo de premios

El flujo recomendable es:

`comprador → pago de artículo concreto → impuestos/comisión/reserva → saldo del creador`  

Cada pago debe estar ligado a una creación y a un vendedor. El creador aporta trabajo, propiedad intelectual y valor comercial. No se paga por haber depositado dinero, reclutado personas o ganado una partida aleatoria.

Aunque no exista un fondo de premios, el marketplace necesita cubrir:

- contracargos;
- devoluciones y bonificaciones;
- fraude y cuentas comprometidas;
- obligaciones fiscales;
- saldos negativos del vendedor;
- costos de moderación y soporte.

La solución preferida es usar un proveedor de pagos autorizado con soporte real para marketplace, KYC de vendedores y pagos diferidos. Una reserva contractual o una ventana de maduración del saldo seguirá siendo necesaria.

---

## 3. Referencias de otros videojuegos

No debe copiarse una marca o mecánica concreta; los siguientes patrones sirven para comprender la separación económica:

- **Roblox:** distingue saldo comprado de `Earned Robux`; su programa DevEx permite retirar únicamente Robux elegibles obtenidos por creadores y aplica verificación, requisitos y revisión. [Developer Exchange](https://en.help.roblox.com/hc/en-us/articles/203314100-Developer-Exchange-DevEx-Overview-How-to-Submit-Requirements).
- **Minecraft:** su Partner Program permite vender mapas, skins, texturas y contenido original sujeto a revisión de calidad y aptitud. [Minecraft Partner Program](https://www.minecraft.net/en-us/partner).
- **Fortnite:** remunera a desarrolladores de islas por aportación al ecosistema y exige aceptación de términos, perfil fiscal y plataforma de pagos. [Engagement Payouts](https://dev.epicgames.com/documentation/fortnite/engagement-payout-in-fortnite-creative).
- **Steam/Counter-Strike:** es una referencia de riesgo, no el modelo recomendado. El mercado oficial usa Steam Wallet y no permite retirar ni transferir sus fondos a bancos o terceros. [Community Market FAQ](https://help.steampowered.com/en/faqs/view/61F0-72B7-9A18-C70B).

El patrón aconsejado para Axolotto combina contenido fijo y curado al estilo Minecraft con una separación estricta entre créditos comprados, puntos ganados y saldo pagable a creadores.

---

## 4. Separación de menores y personas adultas

No es ilegal por sí mismo que una persona menor juegue un videojuego no apostado, apropiado para su edad. El Reglamento de la Ley Federal de Juegos y Sorteos sí prohíbe que menores participen en apuestas. Además, la legislación infantil reconoce su derecho a la intimidad, protección de datos y uso seguro de Internet.

### 4.1 Matriz de permisos recomendada para el MVP

| Función | Menor de 13 | 13 a 17 | 18 o más |
|---|---:|---:|---:|
| Jugar contenido apropiado | Con subcuenta de tutor | Sí, con controles | Sí |
| Chat libre | No | No; sólo canales moderados | Según reglas |
| Perfil público | No por defecto | Privado por defecto | Opcional |
| Compra directa | Sólo por tutor | Tutor o límites verificables | Sí |
| P2P o transferencia | No | No | Sólo marketplace controlado |
| Wallet externa | No | No | Sólo después de controles de riesgo |
| Publicar para venta | No | No en el MVP | Sí, con revisión |
| Recibir retiros | No | No | Sí, con KYC y fiscal |

### 4.2 Controles mínimos de infancia

- Fecha de nacimiento declarada al registro y señalización clara de por qué se solicita.
- Cuenta parental y consentimiento verificable para menores, sin recopilar identificación oficial del niño.
- Compra protegida con PIN, topes, confirmación del adulto y recibos al tutor.
- Perfiles privados, mínima información pública y ausencia de geolocalización precisa.
- Chat predefinido o moderado, filtros, bloqueo, reporte y conservación controlada de evidencia.
- Prohibición de contacto comercial directo de adultos con menores.
- Sin publicidad conductual ni técnicas de presión, escasez falsa o recompensas por insistir al tutor.
- Controles de tiempo, avisos de descanso y autoexclusión de compras.
- Procedimiento urgente de abuso, grooming, amenazas, fraude y material ilícito.
- Moderadores capacitados y canal de escalamiento humano.
- Clasificación mexicana A, B, B15, C o D visible según corresponda.

Para la primera versión monetizada, la regla sencilla y defendible es: **los menores pueden jugar; únicamente adultos verificados pueden vender y retirar**.

---

## 5. Ruta de constitución y monetización

### 5.1 Lo que puede hacerse antes de constituir una empresa

- Programar y probar localmente.
- Ejecutar pruebas cerradas gratuitas sin pagos, retiros ni promesas comerciales.
- Documentar propiedad intelectual y conservar evidencia de autoría.
- Solicitar búsqueda y registro de marca como persona física.
- Consultar autoridades y profesionales.

El fundador puede realizar actividades empresariales como persona física si se registra fiscalmente. Sin embargo, por responsabilidad, propiedad intelectual, contratos con PSP, tratamiento de datos y pagos a terceros, **Axolotto debería constituir una persona moral antes de una beta pública monetizada**.

### 5.2 Formas societarias a evaluar

| Alternativa | Ventaja | Limitación a revisar |
|---|---|---|
| **SAS** | Constitución electrónica gratuita; admite una persona accionista física | Límite anual de ingresos, sólo personas físicas como accionistas y menor flexibilidad para inversión futura |
| **S. de R.L. de C.V.** | Control cerrado y estructura común para pocos socios | Entrada de inversionistas y derechos especiales deben diseñarse bien |
| **S.A.P.I. de C.V.** | Mayor flexibilidad para inversión, clases y pactos de accionistas | Más costo, formalidad y asesoría corporativa |

Por la intención futura de inversión o DAO, debe pedirse al abogado una comparación escrita entre S. de R.L. y S.A.P.I. La DAO no debe ser el motivo para emitir un token ahora.

### 5.3 Orden recomendado

1. Inventariar código, arte, música, dominio, marca, contratos y cuentas técnicas.
2. Obtener opinión preliminar de abogado de juegos/sorteos y fintech sobre el diseño objetivo.
3. Obtener e.firma y RFC personal actualizados.
4. Elegir sociedad con abogado corporativo y contador.
5. Constituir la sociedad y registrar beneficiario controlador, socios y representante.
6. Inscribir RFC de la sociedad y obtener e.firma.
7. Ceder formalmente a la sociedad la marca, código, arte, dominio y demás propiedad intelectual.
8. Abrir cuenta bancaria empresarial; no recibir ventas en cuentas personales.
9. Contratar PSP/adquirente con soporte documentado para marketplace y payouts.
10. Definir tratamiento fiscal de ventas, créditos, comisiones y pagos a creadores.
11. Publicar términos, privacidad, devoluciones, reglas de menores y marketplace.
12. Completar revisión SEGOB y de clasificación de videojuegos.
13. Ejecutar beta gratuita y luego beta monetizada sólo con artículos fijos.
14. Habilitar ventas de creadores adultos después de KYC, moderación y conciliación contable.
15. Considerar mainnet únicamente tras auditoría técnica, legal y operativa.

---

## 6. Checklist por fases

### Fase 0 — Desarrollo gratuito y cerrado

- [ ] Desactivar pagos, retiros, venta P2P, jackpots y premios con valor.
- [ ] Documentar la mecánica completa y todos los flujos de valor.
- [ ] Separar FRJ, AXF y saldo de creador en especificación y código.
- [ ] Crear inventario de propiedad intelectual y dependencias/licencias.
- [ ] Evitar claims de inversión, descentralización, rendimiento o DAO.
- [ ] Diseñar controles de llaves, roles y recuperación.

### Fase 1 — Constitución y criterio profesional

- [ ] Contratar abogado corporativo y abogado regulatorio.
- [ ] Contratar contador con experiencia en plataformas tecnológicas.
- [ ] Seleccionar SAS, S. de R.L. o S.A.P.I.
- [ ] Constituir, obtener RFC y e.firma.
- [ ] Formalizar cesiones de propiedad intelectual a la sociedad.
- [ ] Registrar o solicitar marca Axolotto y marcas relacionadas.
- [ ] Enviar consulta escrita a SEGOB y conservar acuse/respuesta.
- [ ] Obtener memorando sobre activos virtuales, AML y modelo de pagos.

### Fase 2 — Producto apto para menores

- [ ] Clasificación de edad y descriptores de contenido.
- [ ] Age gate, cuenta parental y matriz de permisos por edad.
- [ ] Privacidad por diseño y minimización de datos.
- [ ] Moderación, reporte, bloqueo y protocolo de emergencia.
- [ ] PIN, límites y recibos parentales para compras.
- [ ] No permitir wallets, P2P, venta ni retiro a menores.
- [ ] Realizar evaluación de impacto de privacidad infantil.

### Fase 3 — Ventas propias de contenido fijo

- [ ] Cuenta bancaria y PSP a nombre de la sociedad.
- [ ] Mostrar razón social, RFC, domicilio y soporte.
- [ ] Precios totales en MXN, impuestos y contenido exacto.
- [ ] CFDI, recibos, cancelaciones, devoluciones y bonificaciones.
- [ ] Inventario de bienes digitales y licencias consistente.
- [ ] Conciliación diaria entre PSP, contabilidad, base y cadena.
- [ ] Reserva y proceso de chargebacks.

### Fase 4 — Marketplace de creadores

- [ ] Sólo vendedores de 18+ durante el MVP.
- [ ] KYC, RFC/datos fiscales, CLABE y beneficiario real.
- [ ] Contrato de creador y licencia/cesión necesaria.
- [ ] Revisión humana de originalidad, contenido y derechos.
- [ ] Trazabilidad comprador-artículo-vendedor.
- [ ] Comisión, impuestos y reserva visibles antes de publicar.
- [ ] Retenciones, CFDI e informes configurados con el contador.
- [ ] Saldo en MXN madurado antes de retiro.
- [ ] Política de contracargos, fraude y saldo negativo.

### Fase 5 — Blockchain pública y administración segura

- [ ] Auditoría externa de contratos.
- [ ] Multifirma para tesorería, emisión y upgrades.
- [ ] Timelock para cambios sensibles y pausa de emergencia separada.
- [ ] Caps, rate limits y allowlists.
- [ ] Monitoreo on-chain y alertas 24/7.
- [ ] Plan probado de incidente, comunicación y recuperación.
- [ ] Divulgación clara de control centralizado y facultades administrativas.
- [ ] No habilitar transferibilidad pública ni cashout de tokens.

### Fase 6 — DAO futura

- [ ] Nuevo dictamen corporativo, fiscal, valores y fintech.
- [ ] Definir si la gobernanza es contractual, corporativa o sólo consultiva.
- [ ] No vincular token con utilidades, rendimiento o apreciación sin autorización aplicable.
- [ ] Resolver derechos de voto, conflictos, sanciones, tesorería y responsabilidad.
- [ ] Auditoría independiente y votación con timelock.

---

## 7. Documentos y políticas a preparar

### 7.1 Corporativos y fiscales

- Acta constitutiva y estatutos.
- Libro o registro de socios/accionistas y beneficiario controlador.
- Poderes del representante legal.
- RFC, e.firma, constancia de situación fiscal y domicilio fiscal.
- Contratos de cesión de código, arte, música, diseño, dominio y marcas.
- Contratos de trabajo o prestación de servicios con cláusulas de propiedad intelectual y confidencialidad.
- Cuenta bancaria empresarial y contratos con PSP.
- Matriz de impuestos, CFDI, retenciones e informes.

### 7.2 Producto y consumidores

- Términos de servicio.
- Contrato/licencia de usuario final para artículos digitales.
- Aviso de privacidad integral y aviso simplificado en cada punto de captura.
- Política de cookies, analítica y SDK de terceros.
- Política de precios, facturación, cancelación, devolución y bonificación.
- Información visible de razón social, RFC, domicilio y canales de soporte.
- Divulgación de blockchain, finality y mecanismo compensatorio.
- Política contra prácticas manipulativas y compras accidentales.
- Procedimiento de quejas y atención PROFECO.

### 7.3 Marketplace y creadores

- Acuerdo de vendedor/creador.
- Reglas de contenido y moderación.
- Garantía de autoría, licencias y ausencia de infracción.
- Licencia otorgada a Axolotto y al comprador.
- Procedimiento de denuncia y retiro de contenido infractor.
- Tabla de comisión, impuestos, reserva y calendario de pago.
- Política de KYC, sanciones, fraude, contracargos y saldo negativo.
- Reglas de contenido generado con IA y evidencia de procedencia.
- Expediente fiscal y de identidad del creador.

### 7.4 Menores y seguridad

- Términos para menores y consentimiento parental.
- Política de seguridad infantil y conducta de adultos.
- Política de chat, moderación, reportes, bloqueo y escalamiento.
- Evaluación de impacto de privacidad.
- Plan de respuesta a incidentes y notificación de vulneraciones.
- Política de retención y eliminación de datos.
- Gobierno de llaves, accesos privilegiados y logs administrativos.

---

## 8. Preguntas que deben responderse por escrito

### 8.1 Para SEGOB — Juegos y Sorteos

Adjuntar diagramas, pantallas y ejemplos numéricos. Evitar una descripción incompleta.

1. ¿Una partida digital inspirada en lotería de símbolos, sin pago de entrada y sin premio canjeable, constituye un juego o sorteo sujeto a permiso?
2. ¿Cambia la respuesta si el jugador recibe únicamente puntos no transferibles y sin valor monetario?
3. ¿La venta de cosméticos de contenido fijo y ajenos al resultado de la partida crea una apuesta o condición de participación?
4. ¿Un artículo aleatorio gratuito, no transferible y sin valor de retiro se considera sorteo?
5. ¿La existencia de un marketplace separado para obras creadas por usuarios cambia la clasificación de la partida?
6. ¿Qué tratamiento tendría un concurso exclusivamente de habilidad con premio patrocinado y sin pago de entrada?
7. ¿Qué frases, disclosures o restricciones exige SEGOB para la publicidad de la mecánica?
8. ¿Se requiere un permiso o consulta diferente por operar en Internet y aceptar usuarios de distintos estados?
9. ¿Puede SEGOB confirmar su criterio en oficio o respuesta escrita identificable?

### 8.2 Para el abogado regulatorio/corporativo

1. ¿La forma recomendada es SAS, S. de R.L. o S.A.P.I. considerando fundador único, inversión futura y propiedad intelectual?
2. ¿Qué aspectos exactos de la mecánica podrían considerarse sorteo de símbolos, concurso o juego con apuesta?
3. ¿La separación FRJ/AXF/saldo MXN es suficiente si los dos primeros están on-chain pero no son transferibles?
4. ¿Axolotto ofrece intercambio, custodia o transferencia de activos virtuales bajo la LFPIORPI?
5. ¿La empresa realiza una actividad financiera reservada si recibe al comprador y paga al creador después?
6. ¿Debe operar como comisionista, intermediario, licenciante, merchant of record u otra figura?
7. ¿Qué contratos puede aceptar directamente un menor y cuáles requieren al tutor?
8. ¿Qué sistema de consentimiento parental es proporcional y defendible?
9. ¿Qué derechos adquiere realmente el comprador de un NFT o artículo digital?
10. ¿Cómo se ejecuta legalmente un reembolso cuando la transacción on-chain no es reversible?
11. ¿Qué obligaciones adicionales aplican a usuarios o creadores extranjeros?
12. ¿Qué cambios exigiría una futura DAO o token de gobernanza?

### 8.3 Para el contador fiscalista

1. ¿Qué actividades económicas y regímenes deben registrarse en el RFC de la sociedad?
2. ¿La venta de AXF/créditos causa IVA al comprar el crédito o al consumirlo?
3. ¿Cómo se factura una venta de artículo digital y cómo se documenta una devolución?
4. ¿Axolotto es una plataforma tecnológica de intermediación entre terceros para ISR e IVA?
5. ¿Qué ISR/IVA debe retener a creadores personas físicas y qué CFDI debe emitir o recibir?
6. ¿Cómo se trata fiscalmente la comisión, la reserva de contracargos y el saldo pendiente del creador?
7. ¿Qué declaraciones informativas o reportes mensuales aplican?
8. ¿Cómo se tratan creadores sin RFC, residentes en el extranjero o menores representados por tutores?
9. ¿Cómo deben valorarse contablemente créditos no consumidos y pasivos de marketplace?
10. ¿Qué evidencia debe conciliarse entre PSP, banco, base de datos y cadena?

### 8.4 Para el PSP/adquirente/payout provider

1. ¿Está autorizado y aparece vigente en los registros oficiales aplicables?
2. ¿Su contrato permite marketplaces de artículos digitales, videojuegos y tecnología blockchain?
3. ¿Puede separar cobro del comprador, comisión de Axolotto, reserva y pago al vendedor?
4. ¿Quién es merchant of record y quién responde frente al consumidor?
5. ¿Quién ejecuta KYC, listas de sanciones y validación de cuenta bancaria del creador?
6. ¿Permite impedir vendedores y beneficiarios menores de edad?
7. ¿Cuál es la ventana de contracargos y qué reserva exige?
8. ¿Cómo maneja devoluciones parciales, saldo negativo y cuenta de vendedor cerrada?
9. ¿Qué reportes entrega para CFDI, retenciones, conciliación e investigación de fraude?
10. ¿Usa 3-D Secure, tokenización, device risk y límites configurables?
11. ¿Qué datos personales recibe cada parte y bajo qué contrato de encargado/transferencia?
12. ¿Puede operar sin que Axolotto custodie fondos o saldos retirables de los usuarios?

---

## 9. Contactos oficiales

Los canales siguientes sirven para orientación y trámites. Una respuesta telefónica no sustituye una opinión legal ni un criterio escrito.

| Tema | Autoridad/canal | Contacto oficial | Tipo de acción |
|---|---|---|---|
| Constitución SAS y sociedades | Secretaría de Economía | [Portal SAS](https://www.gob.mx/tuempresa/articulos/crea-tu-sociedad-por-acciones); `sascontacto@economia.gob.mx`; [Centro de Contacto Ciudadano](https://www.gob.mx/se/acciones-y-programas/centro-de-contacto-ciudadano); `contacto.ciudadano@economia.gob.mx` | Constitución obligatoria si se elige persona moral; orientación previa recomendada |
| RFC de la empresa | SAT | [Inscribe tu empresa en el RFC](https://wwwmat.sat.gob.mx/tramites/33804/inscribe-tu-empresa-en-el-rfc); MarcaSAT `55 627 22 728` | Obligatorio para operar como sociedad |
| e.firma | SAT | [e.firma para empresa](https://wwwmat.sat.gob.mx/tramites/17074/obten-el-certificado-de-e.firma-para-tu-empresa) | Obligatoria para trámites y cumplimiento de la sociedad |
| Juegos, apuestas y sorteos | Dirección General de Juegos y Sorteos, SEGOB | [Centro de Atención a Usuarios](https://www.juegosysorteos.gob.mx/es/Juegos_y_Sorteos/centro_de_atencion_a_usuarios); `tramitescau@segob.gob.mx`; `55 5209 8800`, opción 5, ext. 30000, 30014, 30040, 30051 y 30071; Versalles 49, piso 2, Col. Juárez, CDMX | Consulta escrita imprescindible; permiso sólo si la actividad resulta regulada |
| Requisitos de sorteos | SEGOB | [Requisitos para sorteos](https://juegosysorteos.gob.mx/es/Juegos_y_Sorteos/Requisitos_para_Sorteos) | Referencia; no iniciar solicitud sin criterio previo |
| Actividades vulnerables/AML | SAT | [Minisitio de Actividades Vulnerables](https://www.sat.gob.mx/minisitio/ActividadesVulnerables/informacion_general.html); `centraldeactividadesvulnerables@sat.gob.mx`; MarcaSAT `55 627 22 728`, opción de Actividades Vulnerables; [SPPLD](https://sppld.sat.gob.mx/pld/index.html) | Alta y avisos obligatorios sólo si Axolotto encuadra como sujeto obligado |
| Interpretación UIF | Unidad de Inteligencia Financiera | [Funciones y contacto](https://www.gob.mx/uif/que-hacemos); `contacto_uif@hacienda.gob.mx` | Orientación complementaria; acudir primero con abogado/SAT |
| Actividad fintech reservada | CNBV | [Sector Fintech](https://www.gob.mx/cnbv/acciones-y-programas/sector-fintech); [normatividad vigente](https://www.cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/Paginas/NORMATIVIDAD-FINTECH.aspx) | Consultar si se custodiarán o transferirán fondos; preferir proveedor autorizado |
| Verificar proveedor financiero | CONDUSEF | [SIPRES](https://www.gob.mx/condusef/articulos/vas-a-contratar-un-servicio-financiero?idiom=es) | Verificación obligatoria de diligencia antes de contratar PSP financiero |
| Protección del consumidor | PROFECO | [Canales de atención vigentes](https://www.gob.mx/profeco/prensa/profeco-orienta-sobre-terminos-y-condiciones-abusivos-al-comprar-por-internet?idiom=es); `asesoria@profeco.gob.mx`; `55 5568 8722`; `800 468 8722` | Cumplimiento de LFPC obligatorio; orientación recomendada |
| Comercio electrónico | PROFECO | [Código de Ética de Comercio Electrónico](https://www.gob.mx/profeco/articulos/codigo-de-etica-en-materia-de-comercio-electronico?idiom=es); [Monitoreo de tiendas virtuales](https://www.profeco.gob.mx/tiendasvirtuales/) | Código/Distintivo voluntarios; información y derechos de LFPC obligatorios |
| Privacidad de particulares | Secretaría Anticorrupción y Buen Gobierno, Unidad de Protección de Datos Personales | [Autoridad garante actual](https://www.gob.mx/buengobierno/prensa/inician-trabajos-autoridades-garantes-federales-de-acceso-a-la-informacion-y-proteccion-de-datos-personales); `proteccion.datos@buengobierno.gob.mx`; conmutador `55 2000 3000` | Cumplimiento de LFPDPPP obligatorio; confirmar canal vigente del sector privado |
| Marca | IMPI | [Cuenta PASE/Marca en Línea](https://eservicios.impi.gob.mx/); [preguntas de marcas](https://www.gob.mx/impi/acciones-y-programas/temas-de-interes-preguntas-frecuentes-marcas); `buzon@impi.gob.mx`; `55 5334 0700` | Registro no obligatorio para crear, pero prioritario antes de difusión amplia |
| Código, arte, música y contratos | INDAUTOR | [Registro de obra](https://www.gob.mx/public/tramites/detalleTramite.xhtml?homoclave=INDAUTOR-01-001); `registro.obras@cultura.gob.mx`; Puebla 143, Roma Norte, CDMX; `55 3601 8210`, `55 3601 8216`, `800 228 3400` | Derecho nace con la creación; registro probatorio recomendado |
| Estado de INDARELIN | INDAUTOR/DOF | [Acuerdo del 6 de marzo de 2026](https://indautor.gob.mx/documentos/informacion-general/DOF%20-%20Diario%20Oficial%20de%20la%20Federacion.pdf) | INDARELIN suspendido desde el 18-02-2026; usar modalidad de correo o presencial mientras siga suspendido |
| Protección infantil digital | SIPINNA | [Sitio y contacto](https://www.gob.mx/sipinna); `atencionciudadana@segob.gob.mx`; `55 5728 7300`; [directorio nacional y estatal](https://www.gob.mx/sipinna/documentos/directorio-de-secretarias-ejecutivas-de-sipinna-estatales-y-de-secretarias-ejecutivas-municipales-por-estado) | Consulta voluntaria recomendada para política infantil |
| Clasificación de videojuegos | Dirección General de Radio, Televisión y Cinematografía, SEGOB | [Lineamientos de clasificación](https://www.dof.gob.mx/nota_detalle_popup.php?codigo=5606047); [DGRTC](https://dgrtc.segob.gob.mx/es/DGRTC/Historia); `55 5128 0000` o `55 5209 8800`, ext. 15600 | Clasificación/advertencias aplicables al distribuir o comercializar; confirmar modalidad concreta |

---

## 10. Seguridad cuando el fundador conserva el control

Control central no debe significar una sola llave o una sola cuenta.

- Multifirma 2-de-3 o 3-de-5 para tesorería, emisión, upgrades y cambios de roles.
- Firmantes separados físicamente y al menos uno de recuperación fuera de la operación diaria.
- Hardware wallets; ninguna llave de tesorería o administración en `.env`, servidor web o equipo de desarrollo cotidiano.
- Rol de pausa separado del rol de emisión y del rol de retiro.
- Timelock público para upgrades y cambios económicos; pausa de emergencia inmediata pero limitada.
- Caps de emisión, límites diarios, rate limits y destinos allowlisted.
- Separación de ambientes y llaves para local, testnet y mainnet.
- Logs administrativos inmutables y alertas para mint, burn, pause, upgrade, cambios de precio y retiros.
- Reconciliación automática de eventos confirmados contra la proyección de base de datos.
- Número explícito de confirmaciones y manejo de reorganizaciones de cadena.
- Plan de respuesta: congelar, investigar, notificar, compensar, rotar llaves y recuperar.
- Auditoría externa de contratos antes de mainnet y programa posterior de divulgación de vulnerabilidades.
- Publicación honesta de quién controla los contratos y qué facultades conserva.

No debe anunciarse que Axolotto está descentralizado mientras el fundador pueda emitir, pausar, actualizar o mover activos unilateralmente.

---

## 11. Gates de salida

### Se puede abrir una beta gratuita cuando

- no existan pagos, retiros ni premios con valor;
- la seguridad básica, privacidad y moderación estén operativas;
- el contenido tenga clasificación y audiencia definida;
- se explique que es una prueba sin economía real.

### Se puede vender contenido propio cuando

- exista persona física correctamente registrada o, preferentemente, sociedad con RFC/e.firma;
- banco, PSP, CFDI, impuestos, términos, privacidad y devoluciones estén operativos;
- SEGOB y el abogado hayan evaluado la mecánica documentada;
- no haya azar pagado ni recompensas comercializables de partidas.

### Se puede abrir el marketplace cuando

- sólo vendan adultos verificados;
- el PSP soporte marketplace y payouts contractualmente;
- propiedad intelectual, moderación, KYC, impuestos y contracargos estén resueltos;
- cada saldo sea atribuible a ventas reales y conciliado;
- ninguna unidad ganada en gameplay pueda retirarse.

### No se debe abrir mainnet cuando

- una sola llave controle todo;
- no exista auditoría independiente;
- los contratos no tengan caps, pausa y monitoreo;
- exista discrepancia entre cadena, base de datos y contabilidad;
- quede sin resolver la clasificación legal de tokens o mecánicas.

---

## 12. Fuentes jurídicas principales

- [Ley Federal de Juegos y Sorteos](https://www.diputados.gob.mx/LeyesBiblio/pdf/109.pdf).
- [Reglamento de la Ley Federal de Juegos y Sorteos](https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LFJS.pdf).
- [Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPIORPI.pdf).
- [Ley Federal de Protección al Consumidor](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf).
- [Ley Federal de Protección de Datos Personales en Posesión de los Particulares](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf).
- [Ley General de los Derechos de Niñas, Niños y Adolescentes](https://www.diputados.gob.mx/LeyesBiblio/pdf/LGDNNA.pdf).
- [SAT: retenciones por plataformas tecnológicas](https://wwwmat.sat.gob.mx/declaracion/39311/presenta-tu-declaracion-de-entero-de-retenciones).
- [Banco de México: Circular 4/2019 sobre activos virtuales de instituciones sujetas](https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-4-2019/circular-4-2019.html).

---

## 13. Próximos cinco pasos

1. Congelar por escrito el modelo económico recomendado de este documento y eliminar del discurso `jackpot`, `premio`, `apuesta`, `rendimiento`, `inversión` y `cashout por jugar`.
2. Preparar un dossier de diez páginas con mecánica, diagramas de dinero/tokens, edades, screenshots y ejemplos numéricos.
3. Enviar ese mismo dossier al abogado regulatorio, contador y SEGOB para evitar respuestas basadas en versiones diferentes.
4. Constituir la sociedad y formalizar la propiedad intelectual antes de aceptar dinero público.
5. Lanzar en orden: beta gratuita → ventas propias fijas → marketplace de adultos → mainnet; no lanzar las cuatro capas simultáneamente.
