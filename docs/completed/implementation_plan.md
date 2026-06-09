# Plan de Implementación: Ajuste de Proyecciones y Flujo de Desbloqueo de Reservas (SAT / Tienda)

Este plan detalla los ajustes propuestos en [plan_financiero_operativo.md](file:///home/monotr/axolotto/plan_financiero_operativo.md) y [monetizacion_tokenomics.md](file:///home/monotr/axolotto/monetizacion_tokenomics.md) para reflejar con precisión el flujo de ingresos cuando los usuarios compran y gastan gemas en la tienda oficial (compra de Webitos y Boosters).

---

## 1. El Flujo de Ingresos: ¿Cuándo es Ganancia Real?

El usuario tiene toda la razón: cuando los jugadores gastan sus gemas (AXG) en la tienda oficial (comprando Webitos o Boosters), esas gemas se queman o regresan al creador, lo que **desbloquea el 80% de la reserva de forma inmediata**.

El ciclo financiero funciona de la siguiente manera:
1.  **El jugador compra 100 AXG por $200 MXN:**
    *   Tridyland paga $27.60 MXN de IVA y $9 MXN de comisión a Mercado Pago.
    *   Quedan **$163.40 MXN** netos en caja.
    *   Por política, $130.80 MXN (80%) se guardan en la reserva y $32.60 MXN (20%) en la tesorería de operaciones.
    *   *Estado:* El usuario tiene 100 AXG en su wallet. Tridyland tiene la obligación de respaldar esos 100 AXG (en caso de que el usuario los use en el P2P y otro usuario los retire a $100 MXN).
2.  **El jugador gasta los 100 AXG en la Tienda Oficial (compra un Webito):**
    *   El jugador entrega sus 100 AXG a Tridyland a cambio del activo digital.
    *   Estas 100 AXG se queman (se destruyen).
    *   **Consecuencia:** Como las AXG ya no existen en circulación, la obligación de recompra (el pasivo) desaparece por completo.
    *   **Desbloqueo de Reserva:** Los **$130.80 MXN** que estaban congelados en la cuenta de reservas de respaldo se liberan de inmediato y se transfieren a la cuenta de utilidades operativas de Tridyland.
3.  **Resultado Final:** Al gastarse las gemas en la tienda, Tridyland se queda con el **100% del ingreso neto ($163.40 MXN)** de esa venta original.

---

## 2. Ajuste en las Proyecciones Financieras por Fases

Bajo esta aclaración, las proyecciones financieras en **Section 3** de `plan_financiero_operativo.md` deben ser ajustadas para mostrar que cuando una fase se agota (es decir, todos los Webitos y Boosters de esa fase son comprados por los jugadores en la tienda oficial), **toda la reserva de esa fase se desbloquea**, resultando en que Tridyland se queda con el **100% del ingreso neto**:

### Recálculo de Ganancias Netas al Agotar Fases:
*   **Fase 1 (Fundadores agotada):**
    - Ingreso Bruto: $642,000.00 MXN.
    - Neto en Caja (Ganancia Final de Tridyland): **$524,558.00 MXN** ($26,228.00 USD).
*   **Fase 2 (Expansión agotada):**
    - Ingreso Bruto: $252,000.00 MXN.
    - Neto en Caja (Ganancia Final de Tridyland): **$205,902.00 MXN** ($10,295.00 USD).
*   **Fase 3 (Retail agotada):**
    - Ingreso Bruto: $756,000.00 MXN.
    - Neto en Caja (Ganancia Final de Tridyland): **$617,704.00 MXN** ($30,885.00 USD).
*   **Total Acumulado:**
    - Ingreso Bruto: $1,650,000.00 MXN.
    - **Ganancia Neta Final de Tridyland:** **$1,348,164.00 MXN** (~$67,408.00 USD).

La única parte que permanece custodiada en la reserva es la gema que el usuario conserve en su balance y decida no gastar en la tienda oficial, o aquella que se esté comerciando en el Marketplace P2P entre usuarios.

---

## Cambios Propuestos en los Documentos

### 1. [plan_financiero_operativo.md](file:///home/monotr/axolotto/plan_financiero_operativo.md)
*   Reescribir la **Sección 3** para detallar la distinción entre ingreso temporal (con reserva bloqueada) e ingreso final (reserva desbloqueada al comprar ítems en la tienda oficial).
*   Actualizar las tablas de proyecciones por fases de agotamiento para reflejar la ganancia neta final real.

### 2. [monetizacion_tokenomics.md](file:///home/monotr/axolotto/monetizacion_tokenomics.md)
*   Clarificar en la Sección 3 el ciclo de desbloqueo de reservas al quemarse gemas gastadas en la tienda oficial.

---

## Plan de Verificación

1.  **Consistencia Matemática:** Validar que los montos brutos, impuestos (IVA 16%), comisiones (MP 4.5%) y neto en caja sumen exactamente las cifras proyectadas.
2.  **Aprobación del Usuario:** Confirmar si la explicación financiera del desbloqueo de reservas disipa sus dudas y le parece la forma adecuada de presentar las utilidades del proyecto.
