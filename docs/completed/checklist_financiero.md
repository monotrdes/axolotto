# Axolotto — Checklist Financiero/Operativo en el Juego

> Derivado de todo lo discutido: precios, impuestos, Mercado Pago, cripto, P2P, VIP, reservas, comisiones de renta, retiros y demás. Ordenado por prioridad real.

---

## 🔴 CRÍTICO — Sin esto hay dinero que se pierde o el sistema no funciona

### Compras con Fiat (Mercado Pago)
- [ ] Integrar el SDK de Mercado Pago en el backend (crear `mercadopago_service.py`)
- [ ] Endpoint `POST /bank/checkout/mercadopago` — genera un link de pago con el monto en MXN correspondiente a los AXG que el usuario quiere comprar
- [ ] Webhook `POST /bank/webhook/mercadopago` — Mercado Pago notifica cuando el pago se aprueba, el backend acredita los AXG automáticamente
- [ ] Tabla de equivalencia MXN → AXG fijada por admin (10 AXG = $20 MXN, ya documentado en el plan)

### Compras con Cripto (Smart Contract)
- [ ] Integrar el contrato inteligente existente en `web3_service.py` para el flujo de compra de AXG con USDC/USDT
- [ ] Endpoint `POST /bank/checkout/crypto` — el usuario paga al contrato, el contrato notifica al backend via event listener o webhook, el backend acredita AXG
- [ ] Verificación on-chain del pago antes de acreditar (evitar doble-gasto)

### Sistema de Retiro (DevEx / Cash-Out)
- [ ] Modelo `WithdrawalRequest` en la BD: `user_id`, `amount_axg`, `status` (pending/approved/rejected), `tax_withheld`, `net_amount_mxn`, `created_at`, `processed_at`
- [ ] Endpoint `POST /bank/withdraw` — el usuario solicita retiro de AXG (mínimo 100 AXG = $200 MXN)
- [ ] Lógica de retención fiscal automática: **7% si es Régimen de Premios**, descontado del monto bruto antes de pagar
- [ ] Panel de admin para aprobar/rechazar solicitudes de retiro (`GET/PATCH /admin/withdrawals`)
- [ ] Notificación al usuario con el monto neto que recibirá antes de confirmar

---

## 🟠 IMPORTANTE — La economía está incompleta sin esto

### Comisión de la Casa en Rentas de Tablas (5% burn de GAL)
- [x] En `board.py` → endpoint `POST /{board_id}/rent` (línea ~835), la transferencia de GAL va 100% al dueño. **Comisión del 5% quemada** (el dueño recibe el 95% del `rent_fee_gal`)
- [x] Registrar esa comisión en el ledger como `TransactionType.BURN` con descripción `"Comisión de plataforma por renta de tabla"`

### Comisión de la Casa en Ventas P2P de Tablas y Axolotitos (5% en AXG)
- [x] En `board.py` → endpoint de compra P2P de tablas, el pago en AXG va 100% al vendedor. **5% retenido como comisión de Tridyland**
- [x] Lo mismo para la compra P2P de Axolotitos en `incubation.py`
- [x] AXG retenidos van a la wallet del tesoro (`TREASURY_WALLET_ID` en config)

### Comisión de Partidas Multijugador (10% del jackpot)
- [ ] En `multiplayer_service.py`, cuando se cobra la cuota de entrada y se reparte el jackpot, **falta retener el 10%** antes de pagar al ganador
- [ ] Ese 10% se acredita en la wallet del tesoro, no desaparece

### Sistema VIP Club — Pase ya se vende, pero no hace nada
- [ ] Campo `vip_expires_at: Optional[datetime]` en el modelo `User` (migración de BD)
- [ ] En `shop_service.py`, cuando se compra `Pase VIP Club (30 días)`, setear `user.vip_expires_at = now + 30 días`
- [ ] Scheduler (APScheduler o Celery) que cada 24h reparte **+10 GAL** a todos los usuarios con `vip_expires_at > now`
- [ ] Endpoint `GET /user/vip-status` — devuelve si el usuario es VIP y cuándo expira
- [ ] El frontend muestra el marco dorado/corona cuando `is_vip = true`

### Upgrade de Board Slots — Se vende pero no modifica nada
- [ ] Campo `board_slots: int = 2` en el modelo `User` (o en el wallet)
- [ ] En `shop_service.py`, cuando se compra `Upgrade de Board Slots`, incrementar `user.board_slots += 1`
- [ ] En `board.py` → `POST /boards/build`, validar que el usuario no tenga más tablas activas que `user.board_slots`

### Límite Anual del Webito Astral (100 unidades)
- [ ] Campo `supply_sold: int = 0` en `ItemCatalog` (o usar la columna `max_supply` que ya existe y verificar contra ella)
- [ ] En `shop_service.py`, antes de vender el Webito Astral, verificar `supply_sold < 100`. Si se agota, marcar `is_active = False` automáticamente
- [ ] Cron job que cada 1 de enero resetea `supply_sold = 0` y reactiva `is_active = True`

---

## 🟡 MEJORAS — No bloquean, pero completan la experiencia

### Wallet del Tesoro / Contabilidad Interna
- [ ] Definir un usuario sistema `TRIDYLAND_TREASURY` en la BD (o una tabla separada `TreasuryLedger`)
- [ ] Todas las comisiones (5% P2P, 10% jackpot, etc.) se registran en ese ledger separado, no en wallets de usuario
- [ ] Vista de admin `GET /admin/treasury/balance` para monitorear ingresos en tiempo real

### CFDI de Retenciones (para retiros de usuarios)
- [ ] Integración básica con el SAT/PAC (ej. Facturapi) para emitir el CFDI de Retenciones automáticamente al momento de aprobar un retiro
- [ ] Guardar el UUID del CFDI en el registro del `WithdrawalRequest`
- [ ] El usuario puede descargar su comprobante desde `GET /bank/withdrawals/{id}/cfdi`

### Reserva del 80% — Tracking contable
- [ ] No necesita código nuevo urgente, pero se debe documentar que el 80% del AXG vendido debe ser **inmovilizado** en la cuenta de Mercado Pago como fondo de recompra
- [ ] Vista admin `GET /admin/financial/reserve-health` que calcula: `(AXG en circulación × precio DevEx) vs saldo real en MP`

### Foil Booster — Feedback visual al usuario
- [ ] El endpoint de apertura de Booster ya regresa las cartas con `is_shiny: true/false`. El **frontend** debe mostrar una animación diferente cuando viene una carta shiny del Foil Booster (actualmente el campo existe pero no se usa)

### Gashapón (Ficha de Gashapón)
- [ ] El ítem existe en el catálogo (`price_axg = 0`, se da como reward), pero **no hay endpoint** que use una Ficha de Gashapón para obtener un reward aleatorio
- [ ] Endpoint `POST /shop/gashapon/spin` — consume 1 Ficha del inventario y entrega un premio (carta rara, GAL, fragmentos, etc.) con tabla de probabilidades

---

## 📋 Resumen de Prioridades

| Bloque | Items faltantes | Impacto |
|---|---|---|
| 🔴 Pagos fiat/cripto | 3 bloques completos | Sin esto no hay ingresos reales |
| 🔴 Sistema de retiro | 1 bloque completo | Sin esto los usuarios no pueden cobrar |
| 🟠 Comisión de rentas | 2 líneas de código | Pérdida directa del 5% por cada renta |
| 🟠 Comisión P2P | ~20 líneas por endpoint | Pérdida del 5% en cada venta P2P |
| 🟠 Comisión jackpot | ~10 líneas en multiplayer | Pérdida del 10% de cada partida |
| 🟠 VIP Club funcional | Migración BD + scheduler | El pase ya se vende pero no hace nada |
| 🟠 Board Slots funcional | Migración BD + validación | El upgrade ya se vende pero no hace nada |
| 🟠 Webito Astral — límite | Verificación + cron | Sin límite se pueden vender infinitos |
| 🟡 Tesoro/contabilidad | Tabla nueva | Visibilidad de ingresos |
| 🟡 CFDI automático | Integración PAC | Cumplimiento SAT en retiros |
| 🟡 Gashapón | 1 endpoint nuevo | Experiencia del jugador |
