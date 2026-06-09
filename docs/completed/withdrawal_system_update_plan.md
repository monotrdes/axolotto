# Implementation Plan – Actualización del Sistema de Retiro (Dual Fund y KYC)

## Goal Description
Actualizar el flujo de retiro existente para:
1. **Evitar KYC** al limitar los retiros a < 10 000 MXN por usuario sin verificación.
2. **Manejar dos fondos** separados:
   - **Fondo Crypto (USDT/USDC)**: corresponde a la cantidad de gemas compradas con cripto.
   - **Fondo Pesos (MXN)**: corresponde a la cantidad de gemas compradas con fiat (Mercado Pago).
3. **Soportar retiros mixtos** cuando un usuario haya aportado en cripto y quiera retirar en pesos, incluyendo conversiones automáticas y gestión de liquidez.

## User Review Required
> [!IMPORTANT]
> Revisa los siguientes puntos críticos antes de aprobar:
> - **Umbral KYC**: ¿10 000 MXN es el límite correcto o deseas otro valor?
> - **Política de conversión automática**: ¿Convertir siempre todo el monto solicitado a la moneda del fondo disponible o permitir retiros parciales?
> - **Tarifas de conversión**: ¿Aplicar alguna comisión adicional por conversión cripto‑> pesos?
> - **Impacto en la tesorería**: Asegurarse de que haya suficiente liquidez en la wallet de USDT/USDC para cubrir conversiones.

## Open Questions
> [!WARNING]
> - ¿Qué prioridad tiene la conversión automática frente a rechazar el retiro si la liquidez crypto es insuficiente?
> - ¿Se requiere un proceso de “swap” interno (ej. vía Uniswap) o se delegará a un exchange externo?
> - ¿Cómo se manejará el registro de fondos en el `TreasuryLedger` para distinguir entre crypto y pesos?

## Proposed Changes
---
### Database
#### [MODIFY] [withdrawal_requests](file:///home/monotr/axolotto/models/withdrawal_requests.py)
- Añadir campo `source_fund: Enum('CRYPTO','FIAT')`.
- Añadir campo `requested_currency: Enum('MXN','USDT','USDC')`.
- Añadir campo `kyc_exempt: bool` (true si monto < KYC_LIMIT).

#### [NEW] [crypto_fund_balance.sql](file:///home/monotr/axolotto/migrations/crypto_fund_balance.sql)
- Tabla `crypto_fund_balance` con columnas `user_id`, `usdt_amount`, `usdc_amount`.

#### [NEW] [fiat_fund_balance.sql](file:///home/monotr/axolotto/migrations/fiat_fund_balance.sql)
- Tabla `fiat_fund_balance` con columnas `user_id`, `mxn_amount`.
---
### Backend Services
#### [NEW] [withdrawal_service.py](file:///home/monotr/axolotto/services/withdrawal_service.py)
- Función `process_withdrawal(request: WithdrawalRequest)` que:
  1. Verifica `amount_mxn` contra `KYC_LIMIT` (10 000 MXN). Si supera, marca `kyc_exempt=False` y requiere KYC.
  2. Determina el fondo origen según cómo el usuario compró sus gemas (crypto vs fiat).
  3. Si `requested_currency` difiere del fondo origen, realiza **conversión automática**:
     - Si retira MXN pero sólo tiene crypto balance, consulta tasa spot (via API de exchange) y convierte la cantidad necesaria.
     - Si la liquidez crypto es insuficiente, **fallback** a rechazar o a una cola de espera.
  4. Aplica retención fiscal del 7 % (si aplica) y registra en `TreasuryLedger` con tipo `WITHDRAWAL_CRYPTO` o `WITHDRAWAL_FIAT`.
  5. Actualiza balances en `crypto_fund_balance` o `fiat_fund_balance`.

#### [MODIFY] [admin_panel.py](file:///home/monotr/axolotto/admin/admin_panel.py)
- Añadir columna `source_fund` y `requested_currency` en listado de retiros.
- Botón “Aprobar” debe llamar a `withdrawal_service.process_withdrawal`.
---
### Integration with Payments
#### [NEW] [payment_gateway.py](file:///home/monotr/axolotto/integrations/payment_gateway.py)
- Wrapper que soporta:
  - Transferencias bancarias (MXN) vía Stripe/Mercado Pago.
  - Transferencias de USDT/USDC a wallets externas vía API de exchange.
- Función `transfer_funds(user_wallet, amount, currency)` que delega al proveedor adecuado.
---
### Frontend
#### [NEW] [withdrawal_page.html](file:///home/monotr/axolotto/frontend/withdrawal_page.html)
- Formulario con selección de **Moneda de destino** (MXN, USDT, USDC).
- Indicador de **KYC requerido** si el cálculo supera 10 000 MXN.
- Mensaje explicativo de posible conversión y comisión.
---
### Configuración
#### [MODIFY] [config.py](file:///home/monotr/axolotto/config.py)
- `KYC_LIMIT_MXN = 10000`
- `WITHDRAWAL_COOLDOWN_DAYS = 7`
- `CONVERSION_FEE_PERCENT = 0.5`  # opcional
---
## Verification Plan
### Automated Tests
- Unit test para `process_withdrawal` con escenarios:
  1. Retiro < KYC_LIMIT usando mismo fondo → aprobado.
  2. Retiro > KYC_LIMIT → marcado `kyc_exempt=False`.
  3. Retiro MXN con solo crypto balance → conversión correcta y balance actualizado.
  4. Retiro con liquidez crypto insuficiente → rechazo.
- Integration test que simula webhook de exchange para obtener tasa de conversión.

### Manual Verification
- Simular usuario que compró 5 000 AXG con USDT y 3 000 AXG con fiat. Solicitar retiro de 8 000 MXN y validar que se convierta parcialmente de crypto y el resto se tome del fondo fiat.
- Revisar que el registro en `TreasuryLedger` refleje correctamente los movimientos y comisiones.

---
*Este plan está abierto a revisión. Por favor, indique si hay ajustes o prioridades adicionales que desee incluir antes de proceder con la implementación.*
