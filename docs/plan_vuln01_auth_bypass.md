# Plan: VULN-01 — Eliminar bypass de autenticación vía `?user_id=`

**Severidad:** 🔴 Crítica  
**Parent task:** task-1781055512-64  
**Archivos afectados:**
- `backend/app/core/auth.py` (líneas 35-47)
- `backend/app/core/config.py` (líneas 63, 102)

---

## Descripción del problema

`get_verified_user_id` activa una rama "modo dev" cuando `BLOCKCHAIN_MODE == "local"` **y** `PRIVY_APP_ID` está vacío. El problema es que **ambos son los valores por defecto** — cualquier despliegue que olvide fijar esas variables en el `.env` queda con autenticación desactivada.

Dos vectores:

1. **Sin credentials:** el backend acepta `?user_id=<cualquier_did>` como identidad válida → suplantación total.
2. **Con token pero sin `PRIVY_APP_ID`:** el JWT se decodifica con `verify_signature: False` → un atacante forja un JWT con cualquier `sub`.

---

## Cambios requeridos

### 1. `backend/app/core/config.py`

Cambiar el default de `BLOCKCHAIN_MODE` de `"local"` a `None` (campo requerido) **o** agregar un `@model_validator` que bloquee el arranque si la configuración es insegura:

```python
@model_validator(mode="after")
def _enforce_auth(self):
    if self.BLOCKCHAIN_MODE != "local" and not self.PRIVY_APP_ID:
        raise ValueError(
            "PRIVY_APP_ID es obligatorio cuando BLOCKCHAIN_MODE != 'local'. "
            "Configura el .env antes de arrancar en producción."
        )
    return self
```

### 2. `backend/app/core/auth.py`

Reemplazar el bypass via query param por un mecanismo explícito con header dedicado:

**Antes (eliminar):**
```python
if not credentials:
    if settings.BLOCKCHAIN_MODE == "local" and not settings.PRIVY_APP_ID:
        user_id = request.query_params.get("user_id") or request.query_params.get("privy_did")
        if user_id:
            return user_id
```

**Después:**
```python
if not credentials:
    # Dev bypass: solo si ALLOW_DEV_AUTH=true (nunca en prod) y via header explícito
    if settings.ALLOW_DEV_AUTH and settings.BLOCKCHAIN_MODE == "local":
        user_id = request.headers.get("X-Dev-User")
        if user_id:
            return user_id
    raise HTTPException(status_code=401, detail="Token de autenticación requerido")
```

Agregar a `config.py`:
```python
ALLOW_DEV_AUTH: bool = False  # NUNCA true en producción
```

### 3. Verificación JWT — siempre con firma

Eliminar la rama que decodifica sin verificar firma:

**Antes (eliminar):**
```python
if not settings.PRIVY_APP_ID:
    payload = jwt.decode(token, options={"verify_signature": False})
    return payload.get("sub")
```

**Después:** Si no hay `PRIVY_APP_ID`, el `@model_validator` ya habrá bloqueado el arranque. Nunca llegar a este punto en producción.

---

## Guía de verificación

- [ ] El servidor **no arranca** si `BLOCKCHAIN_MODE != "local"` y `PRIVY_APP_ID` está vacío (error claro al inicio).
- [ ] `GET /api/v1/bank/balance?user_id=did:privy:atacante` → 401 Unauthorized (sin token).
- [ ] Con `ALLOW_DEV_AUTH=false` (default), el header `X-Dev-User` es ignorado.
- [ ] Con `ALLOW_DEV_AUTH=true` y `BLOCKCHAIN_MODE=local`, el header `X-Dev-User: did:privy:test` funciona para tests locales.
- [ ] JWT forjado con firma inválida → 401 (no se acepta).
- [ ] Tests unitarios de `get_verified_user_id` cubren los 4 casos anteriores.

---

## Notas de implementación

- No romper los tests existentes que usan `?user_id=` — migrarlos a `X-Dev-User` header en el mismo PR.
- Revisar si algún test en CI setea `BLOCKCHAIN_MODE=local` implícitamente; añadir `ALLOW_DEV_AUTH=true` en el `.env.test` de CI.
- Verificar que `require_admin` en `auth.py` también pase por `get_verified_user_id` (no tenga su propio bypass).
