# Plan: Remediar VULN-03 — Endpoints `/dev/*` sin autenticación + auto-reward gigante

**Parent Task**: `task-1781055512-64`
**Subtask**: `task-1781055512-64-VULN-03`
**Auditoría**: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md`
**Fecha**: 2026-06-09
**Estado**: Planning
**Severidad**: 🟠 Alta
**Prioridad**: Inmediato (bloqueante de producción)

## Resumen

Dos endpoints bajo `/dev/*` presentan riesgos graves si el backend se despliega accidentalmente con `BLOCKCHAIN_MODE=local`:

1. **`POST /dev/reset-tutorial`** — aunque pide identidad (`get_verified_user_id`), crea un `PendingReward` con `DEV_AUTO_REWARD_AXF = 50_000` y `DEV_AUTO_REWARD_FRJ = 500_000`. Encadenado con VULN-01, un atacante puede invocarlo con `?user_id=<su_did>` y recibir 50k AXF + 500k FRJ.
2. **`POST /dev/fill-multiplayer-rooms`** — **no tiene ningún dependency de autenticación** (`Depends(get_verified_user_id)` ausente). Su única protección es `_check_dev_mode()`, que solo verifica `BLOCKCHAIN_MODE == "local"`. Un atacante puede envenenar el matchmaking con miles de jugadores mock.

El patrón de riesgo es: si VULN-01 no está mitigado y el modo local llega a producción, estos endpoints se vuelven armas de inflación masiva.

## Ubicación del problema

| Archivo | Líneas | Problema |
|---------|--------|----------|
| `backend/app/api/v1/endpoints/dev.py` | 42 | `reset_tutorial` pide `user_id` vía `get_verified_user_id` — vulnerable al bypass de VULN-01 |
| `backend/app/api/v1/endpoints/dev.py` | 108-128 | `reset_tutorial` crea `PendingReward` con `DEV_AUTO_REWARD_AXF`/`DEV_AUTO_REWARD_FRJ` |
| `backend/app/api/v1/endpoints/dev.py` | 150 | `fill_multiplayer_rooms` **sin `Depends(get_verified_user_id)`** — solo `_check_dev_mode()` |
| `backend/app/core/config.py` | 127-128 | `DEV_AUTO_REWARD_AXF = 50000.0`, `DEV_AUTO_REWARD_FRJ = 500000.0` — montos excesivos incluso para dev |
| `backend/app/main.py` | (router include) | El router `dev` se monta **siempre**, sin importar `BLOCKCHAIN_MODE` |

---

## Plan de remediación

### Fase 1: Blindar el router `/dev` completo

#### 1.1 Añadir `Depends(get_verified_user_id)` a `fill_multiplayer_rooms`

El endpoint `fill_multiplayer_rooms` actualmente no pide identidad. Añadir el dependency:

```python
@router.post("/fill-multiplayer-rooms")
def fill_multiplayer_rooms(
    room_type: str = Query(...),
    count: int = Query(...),
    axf_amount: float = Query(...),
    frj_amount: float = Query(...),
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),  # ← AÑADIR
):
```

- [ ] Añadir `user_id: str = Depends(get_verified_user_id)` como parámetro
- [ ] No es necesario usar `user_id` en la lógica, pero fuerza la autenticación

#### 1.2 Añadir `Depends(require_admin)` a TODOS los endpoints `/dev/*`

Incluso con identidad, cualquier usuario autenticado podría abusar de `/dev/*`. Gatear con `require_admin`:

- [ ] `reset_tutorial` — añadir `_admin: bool = Depends(require_admin)` (además del `get_verified_user_id` existente)
- [ ] `fill_multiplayer_rooms` — añadir `_admin: bool = Depends(require_admin)` (además del nuevo `get_verified_user_id`)

```python
from app.core.auth import get_verified_user_id, require_admin

@router.post("/reset-tutorial")
def reset_tutorial(
    delete_axolotito: bool = False,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
    _admin: bool = Depends(require_admin),  # ← AÑADIR
):
    _check_dev_mode()
    # ...

@router.post("/fill-multiplayer-rooms")
def fill_multiplayer_rooms(
    room_type: str = Query(...),
    count: int = Query(...),
    axf_amount: float = Query(...),
    frj_amount: float = Query(...),
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),  # ← AÑADIR
    _admin: bool = Depends(require_admin),          # ← AÑADIR
):
    _check_dev_mode()
    # ...
```

#### 1.3 No montar el router `dev` en producción

La defensa más fuerte: si `BLOCKCHAIN_MODE != "local"`, el router ni siquiera existe en la app.

- [ ] Localizar el `include_router` del router `dev` en `backend/app/main.py`
- [ ] Envolverlo en un condicional:

```python
if settings.BLOCKCHAIN_MODE == "local":
    from app.api.v1.endpoints import dev
    api_router.include_router(dev.router, prefix="/dev")
```

Esto garantiza que en producción los endpoints `/dev/*` devuelvan 404, no 403 — no revelan siquiera que existen.

### Fase 2: Reducir y aislar los auto-rewards

#### 2.1 Reducir `DEV_AUTO_REWARD_AXF` y `DEV_AUTO_REWARD_FRJ`

Los valores actuales (50k AXF, 500k FRJ) son desproporcionados. Para testing local, 500-1000 de cada moneda es más que suficiente.

- [ ] Cambiar en `config.py`:
  ```python
  DEV_AUTO_REWARD_AXF: float = 1000.0   # antes 50000.0
  DEV_AUTO_REWARD_FRJ: float = 5000.0   # antes 500000.0
  ```

#### 2.2 Mover las constantes `DEV_AUTO_REWARD_*` fuera del config global

Las constantes de dev no pertenecen al archivo de configuración principal. Deberían vivir en el propio `dev.py` o en un `dev_config.py` separado que solo se importa en modo local.

- [ ] Mover `DEV_AUTO_REWARD_AXF` y `DEV_AUTO_REWARD_FRJ` a `dev.py` como constantes del módulo
- [ ] Eliminarlas de `config.py`
- [ ] Actualizar la referencia en `dev.py:reset_tutorial` de `settings.DEV_AUTO_REWARD_AXF` a la constante local

### Fase 3: Defensa en profundidad con `_check_dev_mode`

#### 3.1 Ejecutar `_check_dev_mode()` como dependency de router

En lugar de llamar `_check_dev_mode()` dentro de cada handler, convertirlo en un dependency a nivel de router:

```python
router = APIRouter(dependencies=[Depends(_check_dev_mode_dep)])

def _check_dev_mode_dep():
    if settings.BLOCKCHAIN_MODE != "local":
        raise HTTPException(status_code=404)  # 404, no 403 — no revelar que el endpoint existe
```

- [ ] Crear `_check_dev_mode_dep()` como dependency
- [ ] Pasar `dependencies=[Depends(_check_dev_mode_dep)]` al `APIRouter()`
- [ ] Eliminar las llamadas individuales a `_check_dev_mode()` dentro de cada handler
- [ ] Cambiar el status code de 403 a 404 (no revelar existencia del endpoint)

---

## Riesgos y consideraciones

1. **Tests existentes**: los tests de integración que usan `/dev/*` deben actualizarse para incluir autenticación de admin (o usar `X-Dev-User` con un DID admin si se implementa VULN-01 primero).
2. **Taskboard / scripts**: verificar si algún script de simulación (`phase_*.py`) llama a `/dev/*` sin auth — deberán actualizarse.
3. **Orden de implementación**: VULN-01 (auth bypass) y VULN-03 (dev endpoints) son independientes pero complementarios. Idealmente implementar VULN-01 primero para que `get_verified_user_id` sea robusto, y luego VULN-03 para gatear los endpoints dev.

## Criterios de aceptación

- [ ] `POST /dev/fill-multiplayer-rooms` sin token → 401 Unauthorized
- [ ] `POST /dev/reset-tutorial` con token de usuario no-admin → 403 Forbidden
- [ ] `POST /dev/fill-multiplayer-rooms` con token de usuario no-admin → 403 Forbidden
- [ ] Ambos endpoints requieren token de admin para funcionar
- [ ] En producción (`BLOCKCHAIN_MODE != "local"`), los endpoints `/dev/*` devuelven 404 (no existen)
- [ ] `DEV_AUTO_REWARD_AXF` ≤ 1000 y `DEV_AUTO_REWARD_FRJ` ≤ 5000
- [ ] Las constantes `DEV_AUTO_REWARD_*` no están en `config.py`
- [ ] Tests de integración actualizados para usar auth de admin en `/dev/*`
- [ ] Scripts de simulación (`phase_*.py`) funcionan correctamente con los cambios

---

## Referencias

- Auditoría completa: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md` (VULN-03, líneas 104-123)
- Plan VULN-01 (auth bypass): `docs/plan_vuln01_auth_bypass.md`
- Plan VULN-02 (treasury multisig): `docs/plan_task-1781055512-64-VULN-02_remediacion-centralizacion-treasury-multisig.md`
- Archivo afectado: `backend/app/api/v1/endpoints/dev.py` (líneas 42, 108-128, 150-157)
- Config afectada: `backend/app/core/config.py` (líneas 127-128)
- Auth: `backend/app/core/auth.py` (`get_verified_user_id`, `require_admin`)
