---
tags: [ai-context, bugs, gotchas]
description: "Trampas conocidas que han causado problemas — leer antes de tocar las áreas afectadas"
last_modified: "2026-06-07"
source_files: ["memory/project_gotchas.md", "HANDOFF_ANTIGRAVITY.md"]
---

# Gotchas — Trampas Conocidas

## Base de Datos / Alembic

### Columnas renombradas fuera de Alembic
**Problema**: Hubo renombrados manuales de columnas en producción que Alembic no registró. Las migraciones estándar fallan porque intentan renombrar columnas que ya tienen el nombre nuevo (o crear columnas que ya existen).

**Solución**: Escribir siempre migraciones idempotentes con bloques `DO $$ ... $$`:
```sql
DO $$ BEGIN
    ALTER TABLE axf_purchase_record RENAME COLUMN axg_amount TO axf_amount;
EXCEPTION
    WHEN undefined_column THEN NULL;
    WHEN duplicate_column THEN NULL;
END $$;
```

### Dos Alembic heads — ya resuelto, no recrear
**Problema**: Existieron dos ramas paralelas de migración que causaban errores 502 al iniciar el backend.

**Resolución**: Se creó `backend/alembic/versions/bb01d2e3f4a5_merge_heads.py` para unirlas.

**Regla**: Antes de crear una nueva migración, verificar que solo hay un head:
```bash
alembic heads
# Debe mostrar exactamente 1 head. Si hay 2, crear merge migration primero.
```

### Startup migrations en main.py
El backend aplica migraciones de schema al iniciar vía `main.py`. Al agregar columnas nuevas, verificar si el cambio ya está en la lógica de startup antes de crear una migración Alembic separada para evitar conflictos.

---

## Monedas / Aliases

### AXF vs AXG, FRJ vs GAL
Las monedas fueron renombradas en junio 2026. El código legacy usa los nombres viejos:

| Nombre nuevo | Símbolo nuevo | Alias viejo en código | Contrato |
|-------------|--------------|----------------------|---------|
| Axofichas | AXF | `axg`, `AXG`, `axogema` | `Axogema.sol` |
| Frijolitos | FRJ | `gal`, `GAL`, `gema_alga` | `GemaAlga.sol` |

**En modelos Python**: `AxgPurchaseRecord = AxfPurchaseRecord` — ambos nombres funcionan. Usar `AxfPurchaseRecord` en código nuevo.

**En agente economy-analyst**: Los archivos del agente aún usan `GAL`/`AXG` internamente (son los mismos alias). No hay bug — es nomenclatura interna del agente.

**Trampas frecuentes**:
- El frontend `.env.local` puede tener `NEXT_PUBLIC_AXOGEMA_ADDRESS` (nombre de contrato, no de moneda) — esto es correcto
- Variables de entorno de contratos no cambiaron nombre porque los contratos Solidity siguen llamándose `GemaAlga.sol` y `Axogema.sol`

---

## Multijugador

### Moneda obligatoria: FRJ
El multiplayer solo acepta FRJ (Frijolitos). AXF está explícitamente prohibido en escrow de salas. Si se intenta usar AXF en una sala multijugador, la lógica debe rechazarlo. Verificar `MULTIPLAYER_CURRENCY = "frijolito"` en `config.py`.

### Mock players y auto-start
Existe un sistema de mock player injection para desarrollo. Las salas con solo mock players NO deben auto-iniciar. Un bug previo causaba que rooms con solo mocks arrancaran automáticamente, lo que distorsionaba las métricas de economía.

---

## MCP Servers — usar antes de leer archivos

### axolotto-kb registrado en .claude/settings.json
El MCP server `axolotto-kb` está registrado y provee tools: `get_architecture`, `get_module`, `get_economy`, `get_conventions`, `search_knowledge`, `get_live_status`.

**Por qué importa**: Los agentes que no usan estas tools pueden desperdiciar 20-50K tokens explorando archivos manualmente. Llamar `get_live_status` al inicio de sesión es una buena práctica.

---

## Taskboard

### Aislamiento estricto
El taskboard (`tools/taskboard/`) es completamente autónomo. Los cambios en el taskboard NUNCA deben afectar backend/frontend/contracts. Si una descripción de tarea del taskboard menciona cambios en el juego, eso significa que el agente de la tarea debe actuar sobre el juego — el taskboard en sí no toca esos archivos.

### Worktrees huérfanos
Los agentes que trabajaron en worktrees bajo `../.axolotto_worktrees/` pueden dejar worktrees sin rama activa. Verificar periódicamente con:
```bash
git worktree list
git worktree prune
```

### Context cache con TTL de 24h
Los archivos `tools/taskboard/.context_cache/axolotto.txt` y `taskboard.txt` tienen TTL de 24h. Si un agente ve información desactualizada del taskboard, refrescar con `POST /api/refresh-context` en el servidor del taskboard.

---

## Issues del HANDOFF (estado al 2026-06-01)

### Backend 502 — resuelto
El 502 que afectaba `api.axolot.to` fue causado por los dos Alembic heads + columnas renombradas. Ya resuelto con:
1. Merge migration `bb01d2e3f4a5_merge_heads.py`
2. Migración idempotente `fa92a8e3d1f4_rename_tokens_and_add_promo_rewards.py`
3. Clase renombrada a `AxfPurchaseRecord` con alias `AxgPurchaseRecord`

### Feature Flujo Corcholata — en planificación
Sistema de códigos promocionales para onboarding físico (corcholatas/tapas). Estado:
- Schema DB diseñado (`promo_codes`, `promo_batches`)
- Endpoint `POST /api/v1/codes/redeem` pendiente de implementación completa
- Archivos backend relevantes: `backend/app/api/v1/endpoints/codes.py`, `backend/app/models/promo.py`, `backend/app/services/promo_service.py`
- Frontend pendiente: componente `CodeEntryPanel` con dos variantes (foco login vs foco código)

### Kit de bienvenida configurado en /admin
```
axf_amount = 139   # intencional: deja 9 AXF tras ~13 partidas fáciles, creando retención
frj_amount = 1000
code_expires_days = 365
```

### Rate limit en códigos
3 intentos por `user_id` para validar código de corcholata. El contador se decrementa por intento fallido, no se resetea.

→ Ver [[critical_rules]] para las reglas de seguridad relacionadas con checkout y replay protection
→ Ver [[agent_routing]] para qué agente manejar cada issue pendiente
