# Plan: Remediar VULN-04 — Desincronización DB ↔ Blockchain por errores tragados

**Parent Task**: `task-1781055512-64`
**Subtask**: `task-1781055512-64-VULN-04`
**Auditoría**: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md`
**Fecha**: 2026-06-09
**Estado**: Planning
**Severidad**: 🟠 Alta
**Prioridad**: Corto plazo

## Resumen

El backend muta el estado en PostgreSQL y **después** intenta replicar la operación on-chain dentro de un `try/except` que solo hace `print(...)`. Si la operación on-chain falla (congestión de RPC, gas insuficiente, nonce collision, timeout), el error se traga silenciosamente y la DB ya fue mutada. Resultado: **divergencia permanente entre la DB (fuente de verdad para el juego) y la blockchain (libro mayor de auditoría).**

No existe outbox transaccional, no hay reintentos, no hay reconciliación periódica, y las operaciones no son atómicas con el `session.commit()`.

## Ubicación del problema

| Archivo | Líneas | Operación DB | Operación on-chain | Error tragado |
|---------|--------|-------------|-------------------|---------------|
| `game_service.py` | 107-113 | `wallet.frijolitos -= entry_fee` | `Web3Service.burn_frj(...)` | `print(...)` |
| `game_service.py` | 356-360 | (premio ya calculado en DB) | `Web3Service.mint_frj(...)` | `print(...)` |
| `game_service.py` | 362-367 | (stats ya actualizados) | `Web3Service.update_table_stats_onchain(...)` | `print(...)` |
| `game_service.py` | 500-506 | `wallet.frijolitos -= cost` | `Web3Service.burn_frj(...)` | `print(...)` |
| `market.py` | 200-209 | (transfer ya hecha en DB) | `transfer_card_onchain(...)` | `print(...)` |
| `bank_service.py` | 66-74 | `wallet.axofichas += amount` **después** del try | `Web3Service.transferir_axofichas(...)` | `raise HTTPException` (mejor, pero el orden DB vs chain es inconsistente) |
| `board_service.py` | 413, 504, 660, 1449 | mutaciones DB | varias operaciones on-chain | `print(...)` / `pass` |
| `multiplayer_service.py` | ~155 | operaciones de sala | on-chain | `print(...)` |
| `admin_service.py` | ~191 | mutaciones admin | on-chain | `print(...)` |

---

## Plan de remediación

### Fase 1: Patrón Outbox Transaccional

En lugar de disparar la tx on-chain inline, escribir la **intención** en una tabla dentro de la misma transacción DB, y procesarla con un worker externo.

#### 1.1 Crear tabla `ChainOutbox`

```python
class ChainOutbox(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True)
    operation: str          # "mint_frj", "burn_frj", "mint_axf", "transfer_card", etc.
    payload_json: str       # argumentos de la operación (JSON)
    status: str = "pending" # pending → processing → confirmed | failed
    tx_hash: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 5
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
```

- [ ] Definir modelo `ChainOutbox` en `backend/app/models/economy.py`
- [ ] Ejecutar migración (o usar `SQLModel.metadata.create_all`)

#### 1.2 Refactorizar operaciones on-chain → escribir en outbox + commit atómico

Patrón actual (roto):
```python
wallet.frijolitos -= fee          # DB
session.commit()                  # DB committed
try:
    Web3Service.burn_frj(...)     # chain — si falla, DB ya está committed
except Exception as e:
    print(...)                     # error tragado
```

Patrón nuevo:
```python
wallet.frijolitos -= fee          # DB
outbox_entry = ChainOutbox(
    user_id=user_id,
    operation="burn_frj",
    payload_json=json.dumps({"to_address": addr, "amount": fee}),
    status="pending",
)
session.add(outbox_entry)
session.commit()                  # DB + outbox atómico — la intención persiste
# El worker procesa la outbox de forma asíncrona
```

- [ ] `game_service.py`: refactorizar 4 sitios (entry_fee burn, prize mint, board stats, food burn)
- [ ] `market.py`: refactorizar P2P transfer
- [ ] `board_service.py`: refactorizar 4+ sitios
- [ ] `multiplayer_service.py`: refactorizar operaciones on-chain
- [ ] `admin_service.py`: refactorizar

#### 1.3 Worker de procesamiento de outbox

- [ ] Crear `backend/app/services/chain_outbox_worker.py`
- [ ] Worker con loop: `SELECT FOR UPDATE ... WHERE status='pending' ORDER BY created_at LIMIT 1`
- [ ] Idempotencia: verificar `ProcessedTransaction` antes de enviar tx on-chain
- [ ] Reintentos con backoff exponencial (1s → 2s → 4s → 8s → 16s, max 5)
- [ ] Marcar `status='failed'` y enviar alerta cuando se agotan reintentos

```python
async def process_outbox(session: Session):
    entry = session.exec(
        select(ChainOutbox)
        .where(ChainOutbox.status == "pending")
        .order_by(ChainOutbox.created_at.asc())
        .with_for_update(skip_locked=True)
    ).first()
    if not entry:
        return
    entry.status = "processing"
    session.commit()
    try:
        tx_hash = dispatch_onchain(entry)
        entry.tx_hash = tx_hash
        entry.status = "confirmed"
        # Registrar en ProcessedTransaction (anti-replay)
        session.add(ProcessedTransaction(tx_hash=tx_hash, user_id=entry.user_id, purpose=entry.operation))
    except Exception as e:
        entry.retry_count += 1
        entry.last_error = str(e)
        if entry.retry_count >= entry.max_retries:
            entry.status = "failed"
            # ALERTA: enviar a logs estructurados + monitor
        else:
            entry.status = "pending"  # reintentar
    session.commit()
```

### Fase 2: Reconciliación periódica DB ↔ Blockchain

#### 2.1 Script de reconciliación

- [ ] Crear `backend/app/scripts/reconcile_db_chain.py`
- [ ] Comparar periódicamente (cron cada 1h o 24h según criticidad):
  - `totalSupply()` on-chain vs `SUM(wallet.frijolitos + wallet.axofichas)` en DB
  - NFTs en wallets on-chain vs `PlayerInventory` + `PlayerBoard`
- [ ] Generar reporte de divergencias y alertar

#### 2.2 Health-check endpoint

- [ ] Endpoint `GET /api/v1/admin/chain-health` (protegido con `require_admin`)
- [ ] Devuelve: contador de outbox pendientes, contador de fallos, última tx confirmada, divergencia DB vs chain

### Fase 3: Structured logging + alertas

#### 3.1 Reemplazar `print()` por logging estructurado

- [ ] Reemplazar todos los `print(f"⚠️ Error...")` en servicios por `logger.error()` o `logger.warning()` con contexto (user_id, operation, amount)
- [ ] Añadir handler que envíe a archivo + consola con formato JSON (facilita monitoreo)

#### 3.2 Métricas y alertas

- [ ] Contador de outbox pendientes (`gauge`)
- [ ] Contador de outbox fallidos (`counter`)
- [ ] Alerta si `failed_count > 0` o `pending_count > N` (Discord/Telegram webhook)

### Fase 4: Garantía de atomicidad en operaciones críticas

#### 4.1 Orden consistente DB ↔ Chain

- [ ] Para **créditos** (mint): primero registrar intención en outbox → commit DB → worker mintea
- [ ] Para **débitos** (burn): deducir de DB + escribir outbox en mismo commit
- [ ] Para **transferencias**: usar patrón "2-phase" con outbox

#### 4.2 `bank_service.py` — unificar orden

Actualmente en `bank_service.py:66-74`, el mint on-chain va **antes** del crédito DB (línea 74). Esto es correcto (fail-fast on-chain aborta antes de tocar DB), pero inconsistente con el resto del sistema donde la DB va primero.

- [ ] Estandarizar: usar siempre outbox para todas las operaciones on-chain
- [ ] O alternativamente: para mints (bajo riesgo), mantener fail-fast on-chain → DB. Para burns (alto riesgo de divergencia), usar outbox.

---

## Riesgos y consideraciones

1. **Latencia**: el outbox worker introduce un delay entre la operación DB y la confirmación on-chain. Para operaciones de juego (burn de cuota), esto es aceptable. Para retiros (mint a wallet del usuario), podría ser problemático para UX.
2. **Ordenamiento**: el worker debe procesar en orden FIFO por usuario para evitar nonce collisions on-chain.
3. **Idempotencia**: crítico verificar `ProcessedTransaction` antes de cada tx para no hacer double-spend en reintentos.
4. **Idempotencia de mints/burns**: si el worker hace `mint_frj` exitosamente pero crashea antes de marcar `confirmed`, el reintento haría un segundo mint. El `ProcessedTransaction` UNIQUE constraint previene esto, pero hay que registrar la tx hash **inmediatamente** después de enviar la tx (no después de confirmarla).
5. **Compatibilidad con simulación**: en modo `IS_MOCK_WEB3`, el outbox debe procesarse inline o con un worker mock que "confirma" instantáneamente.

---

## Criterios de aceptación

- [ ] Existe la tabla `ChainOutbox` y el modelo SQLModel
- [ ] Todas las operaciones on-chain pasan por el outbox (no hay llamadas directas a `Web3Service` desde servicios de negocio)
- [ ] Worker de outbox procesa entradas con reintentos y backoff
- [ ] `ProcessedTransaction` se registra para cada tx confirmada (anti-replay)
- [ ] Si una operación on-chain falla definitivamente, se registra en `ChainOutbox.failed` y se alerta
- [ ] No quedan `print(f"⚠️ Error...")` que traguen fallos on-chain — todos usan `logger.error()`
- [ ] Script de reconciliación DB ↔ Chain existe y puede ejecutarse manualmente
- [ ] Health-check endpoint `/admin/chain-health` devuelve métricas de outbox
- [ ] Tests unitarios del worker: idempotencia, reintentos, fallo definitivo
- [ ] Tests de integración: operación de juego → entrada en outbox → worker procesa → tx confirmada
- [ ] Modo mock (`IS_MOCK_WEB3=true`) procesa outbox inline sin worker real

---

## Referencias

- Auditoría completa: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md` (VULN-04, líneas 126-146)
- Modelo existente: `ProcessedTransaction` en `backend/app/models/economy.py:135`
- Patrón Outbox: https://microservices.io/patterns/data/transactional-outbox.html
