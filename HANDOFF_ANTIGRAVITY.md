# Handoff para Antigravity — 2026-06-01

## Estado actual del servidor

El backend en `api.axolot.to` estaba caído (502). Se resolvió así:

1. **Migraciones alembic** tenían dos heads paralelos (rama tuya + rama nuestra). Se creó merge migration `bb01d2e3f4a5_merge_heads.py` para unirlas.
2. **Columnas renombradas en DB** sin que alembic lo supiera — se usó `stamp` + migraciones idempotentes con `DO $$ ... $$`.
3. **`AxgPurchaseRecord` → `AxfPurchaseRecord`** — el modelo Python no había sido actualizado. Ya está corregido con alias de compatibilidad.

### Archivos modificados hoy (sin commit aún)
- `backend/app/models/economy.py` — clase renombrada a `AxfPurchaseRecord`, tablename `axf_purchase_record`, campo `axf_amount`. Alias `AxgPurchaseRecord = AxfPurchaseRecord` para compatibilidad con scripts viejos.
- `backend/alembic/env.py` — import actualizado a `AxfPurchaseRecord`
- `backend/app/main.py` — import actualizado a `AxfPurchaseRecord`
- `backend/alembic/versions/fa92a8e3d1f4_rename_tokens_and_add_promo_rewards.py` — reescrita como idempotente con DO $$ blocks
- `backend/alembic/versions/bb01d2e3f4a5_merge_heads.py` — nueva, merge de las dos ramas

### Estado del servidor después del fix
```bash
docker compose up -d --build backend_axolotto
# Si aún no está corriendo, verificar:
docker logs axolotto_backend --tail 30
```

---

## Feature en planificación: Flujo Corcholata (landing page)

Se estaba diseñando el UX del landing. Aquí el estado de decisiones tomadas:

### Decisiones confirmadas
- **Login**: botón único "Iniciar sesión" que abre el selector de Privy (Google/Apple/Email). No listar opciones manualmente.
- **"Únete ahora"**: abre panel con Privy login prominente + campo de código opcional abajo.
- **"Canjear mi corcholata"**: abre el mismo panel pero con el campo de código prominente arriba + login abajo.
- **Si ya tiene sesión activa**: ambos botones redirigen directo a `juega.axolot.to`.
- **Códigos únicos por corcholata física** (1 código = 1 cuenta, evita abuso multi-cuenta).
- **Rate limit**: 3 intentos por `user_id` para validar código.
- **Expiración**: configurable por lote desde /admin, default 365 días desde creación.

### Kit de bienvenida (variables en /admin)
```
axf_amount        = 139   # Axofichas (moneda principal)
frj_amount        = 1000  # Frijolitos (moneda secundaria)
special_item_id   = ?     # Item especial de lanzamiento (pendiente definir)
special_item_qty  = 1
code_expires_days = 365
```
El 139 AXF es intencional: después de ~13 partidas fáciles (10 AXF) quedan 9 AXF — justo 1 corto para otra partida, creando retención.

### Flujo lógico del panel
```
Click botón (cualquiera de los 2)
  └─ ¿Sesión activa? → redirect juega.axolot.to

  └─ Abre CodeEntryPanel
      ├─ Pre-fill código desde localStorage si existe
      ├─ Input código + botón Privy login
      └─ Post-auth:
          ├─ Usuario nuevo + código válido → grant kit → success screen → redirect
          ├─ Usuario nuevo sin código → onboarding normal → redirect
          ├─ Usuario existente → redirect (sin kit, sin importar si tiene código)
          └─ Código inválido → error inline, decrementar intentos (máx 3)
```

### Schema DB para los códigos
```sql
promo_codes
├─ id           UUID
├─ code         VARCHAR(12) UNIQUE   -- ej. AXOL-K7M3
├─ batch_id     FK → promo_batches
├─ redeemed_by  FK → users (nullable)
├─ redeemed_at  TIMESTAMP (nullable)
└─ expires_at   TIMESTAMP

promo_batches
├─ id
├─ name         -- "Lanzamiento Verano 2026"
├─ kit_config   JSONB  -- snapshot del kit al momento de generar
└─ expires_days INT
```
El `kit_config` es JSONB snapshot para que cambios futuros en /admin no afecten lotes anteriores.

### Endpoint a implementar
`POST /api/v1/codes/redeem`
- Requiere auth (Privy JWT)
- Body: `{ "code": "AXOL-XXXX" }`
- Checks: código existe, no expirado, no canjeado, usuario es nuevo, intentos < 3
- Respuesta éxito: kit contents para mostrar en success screen antes del redirect

### Archivos relevantes ya existentes
- `backend/app/api/v1/endpoints/codes.py` — endpoint de códigos (revisar estado)
- `backend/app/models/promo.py` — modelo PromoCode (revisar si tiene los campos nuevos)
- `backend/app/services/promo_service.py` — lógica de promo
- `backend/alembic/versions/e5f6a7b8c9d0_add_promo_code.py` — migración existente

### Frontend pendiente
- Componente `CodeEntryPanel` (modal/drawer) en el landing
- Dos variantes: foco en Privy login (Únete) vs foco en código (Canjear)
- Persistencia del código en `localStorage` key: `corcholata_code_draft`
- Success screen mostrando el kit antes de redirigir (no redirigir automático)
- Indicador visual de intentos restantes (ej. ●●● → ●●○ → ●○○)

---

## Precios de referencia (economy.py)
- Partida fácil (clásica): 10 AXF
- Partida difícil / 5 tablas (suerte): 50 AXF
- Booster pure (más barato): 60 AXF + 800 FRJ
- Booster regular: 100 AXF + 1300 FRJ

## Notas técnicas
- Monedas: **AXF = Axofichas** (antes AXG/axogemas), **FRJ = Frijolitos** (antes GAL/gemas_alga)
- El servidor corre en `tridyland`, backend en Docker, frontend en PM2
- DB en Docker port 5433, backend en Docker port 8001, frontend PM2 port 3000
- Nginx hace reverse proxy de `api.axolot.to` → localhost:8001
- Para reiniciar todo: `bash reiniciar.sh` desde `~/axolotto`
