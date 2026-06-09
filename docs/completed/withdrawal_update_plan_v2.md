# Implementation Plan – Actualización del Sistema de Retiro (KYC % Límite, Retiros Parciales & Swaps)

## Goal Description
Refinar el flujo de retiro para:
1. **KYC basado en porcentaje** en lugar de un límite absoluto fijo. Permitir retiros sin verificación siempre que el monto sea ≤ **X %** del total de fondos del usuario (configurable, p.ej. 20 %).
2. **Retiros parciales**: el usuario puede elegir retirar una parte de sus fondos en la moneda original (USDT/USDC) y/o en pesos, sin necesidad de convertir todo.
3. **Opciones de conversión**:
    - **Swap interno** (ej. vía DEX integrado) para convertir crypto → MXN cuando la liquidez fiat sea insuficiente.
    - **Swap externo** (exchange regulado) como fallback.
4. **Tarifas y compliance**: aplicar una comisión por swap interno (p.ej. 0.5 % + posible tarifa de red) y registrar la operación en el `TreasuryLedger` con tipo `SWAP_CRYPTO_TO_FIAT`.

## User Review Required
> [!IMPORTANT]
> - **Porcentaje KYC**: confirmar el valor recomendado (ej. 20 %).
> - **Política de swaps**: ¿permitimos swaps internos automáticos o requerimos aprobación manual?
> - **Comisión de swap**: definir si la tarifa se absorbe o se pasa al usuario.
> - **Límites de retiro parcial**: ¿existe un mínimo por transacción?

## Open Questions
> [!WARNING]
> - ¿Cuál es la tolerancia regulatoria para swaps internos en México? (AML/CTF requieren trazabilidad completa.)
> - ¿Se necesita un proveedor de precios (oracle) certificado para la tasa spot?
> - ¿Cómo se reportarán los swaps a la UIF (Financial Intelligence Unit) – como conversiones o como retiros?

## Proposed Changes
---
### Configuración
#### [MODIFY] [config.py](file:///home/monotr/axolotto/config.py)
- `KYC_PERCENT_LIMIT = 0.20  # 20 % del total holdings puede retirarse sin KYC`
- `SWAP_INTERNAL_ENABLED = True`
- `SWAP_FEE_PERCENT = 0.5`
- `MIN_WITHDRAWAL_AMOUNT = 50  # MXN o equivalente en USDT/USDC`

### Database
#### [MODIFY] [withdrawal_requests](file:///home/monotr/axolotto/models/withdrawal_requests.py)
- Añadir campo `partial_amount_axg: Decimal` (cantidad AXG a retirar sin conversión).
- Añadir campo `swap_used: bool` y `swap_fee: Decimal`.

#### [NEW] [swap_ledger.sql](file:///home/monotr/axolotto/migrations/swap_ledger.sql)
- Tabla `swap_ledger` con `id`, `user_id`, `from_currency`, `to_currency`, `amount_from`, `amount_to`, `fee`, `timestamp`.

### Backend Services
#### [MODIFY] [withdrawal_service.py](file:///home/monotr/axolotto/services/withdrawal_service.py)
- **Cálculo KYC**: `kyc_exempt = (requested_mxn <= user.total_holdings_mxn * KYC_PERCENT_LIMIT)`.
- **Retiros parciales**: aceptar `partial_amount_axg` y descontar directamente del balance crypto sin swap.
- **Swap interno**:
  1. Verificar `SWAP_INTERNAL_ENABLED`.
  2. Obtener tasa spot mediante oracle confiable.
  3. Aplicar `SWAP_FEE_PERCENT`.
  4. Registrar en `swap_ledger` y en `TreasuryLedger` con movimiento `SWAP_CRYPTO_TO_FIAT`.
- **Fallback externo**: si liquidez o tasa no disponible, marcar solicitud como `pending_swap` y notificar al admin.

#### [MODIFY] [admin_panel.py](file:///home/monotr/axolotto/admin/admin_panel.py)
- Mostrar columnas `partial_amount_axg`, `swap_used`, `swap_fee`.
- Botón “Aprobar” llama a `process_withdrawal` con posibilidad de aprobar swap interno.

### Integration with Payments
#### [MODIFY] [payment_gateway.py](file:///home/monotr/axolotto/integrations/payment_gateway.py)
- Añadir método `perform_internal_swap(user_id, amount_usdt, target_mxn)` que usa el oracle y actualiza balances.
- Mantener compatibilidad con transferencias externas como antes.

### Frontend
#### [MODIFY] [withdrawal_page.html](file:///home/monotr/axolotto/frontend/withdrawal_page.html)
- Campo “Retiro parcial en crypto” para indicar AXG/USDT/USDC a retirar sin conversión.
- Selector de “Convertir a MXN” con checkbox – si se marca, se muestra estimado de tasa y comisión.
- Mensaje dinámico que indica si el retiro está bajo el **% KYC limit** o requerirá verificación.

### Verification Plan
#### Automated Tests
- Test KYC‑percentage: usuario con 100 000 MXN total holdings solicita 15 000 MXN → `kyc_exempt=False`.
- Test retiro parcial crypto: solicita 200 USDT sin conversión → balance actualizado y sin registro de swap.
- Test swap interno exitoso: solicita 5 000 MXN, solo tiene 3 000 MXN fiat y 2 000 USDT crypto → swap interno calcula conversión, aplica fee, registra en `swap_ledger`.
- Test swap fallback cuando liquidez insuficiente → solicitud queda en estado `pending_swap`.

#### Manual Verification
- Simular usuario con fondos mixtos, ejecutar retiro parcial + swap y validar registros en `TreasuryLedger` y `swap_ledger`.
- Verificar que el reporte de auditoría incluye la tasa usada y la comisión aplicada.

---
*Este plan está abierto a revisión. Por favor, confirme los valores de porcentaje KYC, tarifas de swap y si se permite el swap interno antes de proceder con la implementación.*
