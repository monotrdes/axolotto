# Plan de Implementación – Sistema de Retiro (DevEx / Cash‑Out)

## 1. Resumen del objetivo
Desarrollar y poner en producción el flujo completo de **retiro de fondos** para usuarios que han adquirido AXG mediante fiat o cripto. El sistema debe:
- Permitir al usuario solicitar la conversión de AXG a MXN y transferir el monto neto a su cuenta bancaria.
- Aplicar retenciones fiscales automáticas (7 % para Régimen de Premios).
- Garantizar la **seguridad anti‑fraude** evitando retiros repetidos en un corto período (n días) y gestionando tarjetas sospechosas.
- Integrarse con la **tesorería** del proyecto para reflejar correctamente el flujo de fondos y la reserva del 80 %.

## 2. Estado actual
- Compra de AXG con cripto está implementada (backend `web3_service.py`).
- La tesorería está configurada con el fondo y transferencias de comisiones a la wallet del tesoro.
- Falta el **módulo de retiro**: modelo, endpoint, lógica fiscal, panel de aprobación y notificaciones.

## 3. Requerimientos funcionales
| # | Requerimiento | Detalle |
|---|---------------|---------|
| 1 | Modelo `WithdrawalRequest` | Campos: `user_id`, `amount_axg`, `status` (pending/approved/rejected), `tax_withheld`, `net_amount_mxn`, `created_at`, `processed_at`, `last_withdrawal_at` |
| 2 | Endpoint `POST /bank/withdraw` | Validaciones: mínimo 100 AXG, saldo suficiente, límite de n días desde último retiro, verificación de tarjeta (si aplica). |
| 3 | Retención fiscal automática | 7 % del monto bruto si el usuario está bajo **Régimen de Premios**; registrar en `tax_withheld`. |
| 4 | Panel admin `/admin/withdrawals` | Listado, filtro por estado, acciones `approve`/`reject`. Al aprobar, generar transferencia y registrar `processed_at`. |
| 5 | Notificación al usuario | Email / in‑app con detalle del **monto neto** a recibir y confirmación de envío. |
| 6 | Integración con tesorería | Transferir el neto a la cuenta bancaria del usuario mediante API de pagos (ej. Stripe, Mercado Pago) y registrar la salida en `TreasuryLedger`. |
| 7 | Anti‑fraude – período de espera | Configurable `WITHDRAWAL_COOLDOWN_DAYS` (ej. 7 días). Bloquear nuevas solicitudes antes de que pase el periodo. |
| 8 | Prevención de tarjetas robadas | Verificar hash de tarjeta/banco contra lista negra; rechazar si coincide. Mantener tabla `BlacklistedCards`. |
| 9 | CFDI de retenciones | Generar documento fiscal (CFDI) al aprobar retiro y adjuntarlo al registro `WithdrawalRequest`. |

## 4. Consideraciones de seguridad y cumplimiento
- **AML/KYC**: Verificar identidad del usuario antes de permitir retiros superiores a $10 000 MXN.
- **Limitación de n días**: Evita depósitos que rebotan por uso de tarjetas robadas; permite a la plataforma monitorizar patrones sospechosos.
- **Auditoría**: Guardar logs de todas las solicitudes y acciones admin en `audit_logs`.
- **Respaldo de fondos**: Mantener una reserva del **80 %** del total vendido en la cuenta de Mercado Pago como garantía de recompra.
- **Cumplimiento SAT**: Emitir CFDI automáticamente y proporcionar descargas al usuario.

## 5. Arquitectura y flujo de datos
```mermaid
flowchart TD
    User-->API: POST /bank/withdraw
    API-->|Validaciones|DB[DB WithdrawalRequest]
    DB-->|Crear registro|API
    API-->|Check cooldown & blacklist|SecurityService
    SecurityService-->|Aprobado|API
    API-->|Notificar admin|AdminPanel
    AdminPanel-->|Approve/Reject|API
    API-->|Generate CFDI|CFDIService
    API-->|Transferencia|TreasuryService
    TreasuryService-->|Update ledger|LedgerDB
    API-->|Notify user|NotificationService
```

## 6. Pasos de implementación
1. **Diseño de BD**
   - Añadir tabla `withdrawal_requests` con los campos descritos.
   - Añadir tabla `blacklisted_cards` y columna `last_withdrawal_at` en `users`.
2. **Servicios backend**
   - Implementar `withdrawal_service.py` con lógica de creación, validación y cálculo de retenciones.
   - Extender `admin_panel.py` para gestión de retiros.
3. **Integración de pagos**
   - Configurar cliente API (Stripe/Mercado Pago) para envíos bancarios.
   - Implementar función `transfer_to_user(account, amount)`.
4. **Generación de CFDI**
   - Integrar librería Facturapi (o similar) y crear endpoint `/bank/withdrawals/{id}/cfdi`.
5. **Seguridad**
   - Implementar verificación contra `blacklisted_cards` y lógica de `WITHDRAWAL_COOLDOWN_DAYS`.
   - Añadir auditoría de eventos.
6. **Frontend**
   - Crear pantalla “Retiro” en la sección de wallet.
   - Mostrar estimado neto y confirmación antes de enviar.
   - Notificaciones de estado (pendiente, aprobado, rechazado).
7. **Pruebas**
   - Unit tests para cálculo de impuestos y cooldown.
   - Integration tests con mock API de pagos.
   - Test de carga para validar concurrencia en aprobación admin.
8. **Despliegue**
   - Migraciones DB.
   - Deploy a entorno staging, ejecutar pruebas end‑to‑end.
   - Monitoreo de transferencias y alertas de fallos.

## 7. Verificación y métricas post‑lanzamiento
- **KPIs**: Tiempo promedio de aprobación, tasa de éxito de transferencias, número de retiros bloqueados por fraude.
- **Auditoría**: Revisión semanal de logs y conciliación con extractos de la cuenta de tesorería.
- **Feedback**: Encuesta a usuarios tras el primer retiro para detectar fricciones.

---
*Este plan está abierto a revisión. Por favor, indique si hay ajustes o prioridades adicionales que desee incluir.*
