# Rediseño Gashapon: Eliminación de Fichas + Sistema de Cápsulas

> Análisis y recomendación de game design.
> Junio 2026

## Decisión del usuario

- ✅ **AXF** (Axoficha) = premium currency
- ✅ **FRJ** (Frijolito) = game currency
- ✅ Tiers renombrados: **bronce**, **plata**, **oro**
- ✅ Eliminar "Ficha de Gashapon" como ítem/ticket
- ❓ Si acaso te ganas algo para gashapon, van a ser las cápsulas mismas
- ❓ Preocupación: con fichas podías usar diferentes cantidades según tier (1/2/4/6) — se pierde esa flexibilidad

---

## 1. Diagnóstico del sistema actual

### 1.1 ¿Qué es "Ficha de Gashapon" hoy?

Ítem consumible (ERC-1155) con `is_gashapon_ticket: True`. **No se compra** (`price_gal=0, price_axg=0`). Solo se obtiene como recompensa.

**Fuentes de obtención:**

| Fuente | Cantidad | Frecuencia |
|--------|----------|------------|
| VIP Coral | 1/mes | Mensual |
| VIP Dorado | 3/mes | Mensual |
| VIP Axolite | 5/mes | Mensual |
| Racha diaria día 7 | 1 | Semanal |

**Uso como pago alternativo:**

| Roll | Costo FRJ | Costo en Fichas |
|------|-----------|-----------------|
| Gashapon común | 1000 FRJ | 1 ficha |
| Gashapon premium | 2500 FRJ | 1 ficha |
| Cápsula Bronce | 1500 FRJ | 1 ficha |
| Cápsula Plata | 5000 FRJ | 2 fichas |
| Cápsula Oro | 20000 FRJ | 4 fichas |
| Triple Suerte | 22500 FRJ | 6 fichas |

**Problema de diseño:** La ficha vale 1500 FRJ en bronce pero 5000 FRJ en premium (1 ficha = 2500 FRJ). No tiene valor consistente. Es un "comodín" que el jugador optimiza según el tier más caro.

### 1.2 ¿Qué decisión toma el jugador hoy?

Con fichas, el jugador enfrenta un mini-puzzle:
- "¿Gasto 1 ficha en bronce (valor 1500) o ahorro 4 para oro (valor 5000 c/u)?"
- La respuesta óptima es **siempre oro** (5000 FRJ/ficha vs 1500 FRJ/ficha en bronce)

Esto no es una decisión interesante — es un cálculo de eficiencia con una sola respuesta correcta. La flexibilidad es **ilusoria**: el sistema empuja a acumular para oro.

### 1.3 Conclusión

Las fichas no crean decisiones estratégicas reales. Solo añaden:
- Un ítem extra en inventario
- Una ruta de pago paralela que confunde
- Un cálculo de eficiencia trivial (siempre gastar en el tier más caro)

**Eliminarlas es la decisión correcta.**

---

## 2. Sistema propuesto: Cápsulas como ítems

### 2.1 Inventario de cápsulas

Cada cápsula es un ítem independiente en inventario (ERC-1155):

| Ítem | Ícono | Rareza | Efecto |
|------|-------|--------|--------|
| Cápsula Bronce | 🟤 | Común | 1 roll gratuito tier bronce |
| Cápsula Plata | ⚪ | Raro | 1 roll gratuito tier plata |
| Cápsula Oro | 🟡 | Épico | 1 roll gratuito tier oro |

**No son convertibles entre sí.** Una Cápsula Bronce siempre da roll bronce. Simple, directo, sin cálculos.

### 2.2 Fuentes de obtención (reemplazan a las fichas)

| Fuente | Antes (fichas) | Ahora (cápsulas) | Nota |
|--------|---------------|-------------------|------|
| VIP Coral | 1 ficha/mes | 2 Cápsula Bronce/mes | Más rolls, menor valor c/u |
| VIP Dorado | 3 fichas/mes | 2 Bronce + 1 Plata/mes | Mix de tiers |
| VIP Axolite | 5 fichas/mes | 3 Bronce + 2 Plata + 1 Oro/mes | Premium feel |
| Racha día 7 | 1 ficha | 1 Cápsula Plata | Más emocionante que bronce |

**¿Por qué más cápsulas que fichas?**
- 1 ficha se podía optimizar para valer ~5000 FRJ (usándola en oro)
- 2 Cápsula Bronce = 2 × 1500 = 3000 FRJ de valor. Menos valor, pero más rolls = más dopamina.
- El valor total es menor pero la **frecuencia de uso** es mayor → más engagement.

### 2.3 ¿Se pierde flexibilidad? Sí. ¿Es malo? No.

Lo que se pierde:
- No puedes juntar 2 bronce para hacer 1 plata
- No puedes "ahorrar" para optimizar valor

Lo que se gana:
- Claridad: cada cápsula hace exactamente lo que dice
- Emoción: recibir una Cápsula Oro es un momento especial
- Colección: ver tus cápsulas en inventario es tangible
- Sin cálculos: el jugador solo abre la cápsula y ya

### 2.4 Opción futura: Fusión de cápsulas (si hace falta flexibilidad)

Si en el futuro los jugadores piden flexibilidad, se puede agregar:

```
2 Cápsula Bronce → 1 Cápsula Plata  (Fusión)
1 Cápsula Plata  → 2 Cápsula Bronce (Des fusión)
```

Esto recupera la flexibilidad sin volver a las fichas. Pero **no incluirlo en V1** — validar primero si los jugadores realmente lo necesitan.

---

## 3. Gashapon clásico (máquina de accesorios)

El gashapon clásico es una máquina SEPARADA de las cápsulas. Actualmente tiene dos modos:

| Modo | Costo FRJ | Drop pool |
|------|-----------|-----------|
| Común | 1000 FRJ | 70% Común, 25% Raro, 5% Épico |
| Premium | 2500 FRJ | 45% Raro, 45% Épico, 10% Legendario |

**Recomendación:** Este gashapon clásico se paga **solo con FRJ**. Sin tickets, sin cápsulas. Es el "sumidero de FRJ" básico para jugadores que quieren accesorios rápido.

Las cápsulas (bronce/plata/oro) son un sistema separado con su propio loop:

```
Jugar → Ganar FRJ → Comprar Cápsula → Abrir → Recibir premio (carta, accesorio, egg, etc.)
                         ↑
       VIP / Racha diaria ───→ Cápsulas gratis
```

---

## 4. Cambios requeridos

### 4.1 Backend — Modelos

**Eliminar:**
- `ItemCatalog.item_metadata.is_gashapon_ticket` — ya no se usa
- `_get_or_create_gashapon_token()` en `shop.py:170-187`
- Campo `use_ticket` en `GashaponRollRequest` y `CapsuleRollRequest`

**Agregar ítems al catálogo (`seed_catalog.py`):**
```python
# Cápsulas como ítems consumibles
ItemCatalog(
    item_type=ItemType.CONSUMABLE,
    name="Cápsula Bronce",
    description="Contiene un premio aleatorio. Tier bronce.",
    price_gal=1500,   # se puede comprar con FRJ
    price_axg=0,
    item_metadata={"slot": "consumable", "capsule_tier": "bronce"},
)
ItemCatalog(
    item_type=ItemType.CONSUMABLE,
    name="Cápsula Plata",
    price_gal=5000,
    price_axg=0,
    item_metadata={"slot": "consumable", "capsule_tier": "plata"},
)
ItemCatalog(
    item_type=ItemType.CONSUMABLE,
    name="Cápsula Oro",
    price_gal=20000,
    price_axg=0,
    item_metadata={"slot": "consumable", "capsule_tier": "oro"},
)
```

**Actualizar esquema de request:**
```python
class CapsuleRollRequest(BaseModel):
    tier: Literal["bronce", "plata", "oro"]
    use_capsule: bool = False  # True = usa cápsula del inventario, False = paga con FRJ
```

### 4.2 Backend — Endpoints

**`POST /shop/capsule/roll`** — Modificar `roll_capsule`:
- Si `use_capsule=True`: buscar `Capsula [tier]` en inventario, consumir 1
- Si `use_capsule=False`: cobrar FRJ según `TIER_COSTS[tier]`
- Eliminar lógica de ticket mapping (1/2/4/6 → línea 867)

**`POST /shop/gashapon/roll`** — Simplificar `roll_gashapon`:
- Solo pago con FRJ. Eliminar `use_ticket`.

**`POST /shop/capsule/daily-claim`** — `claim_daily_capsule`:
- Día 7: en lugar de `_add_item("Ficha de Gashapon")`, hacer `_add_item("Cápsula Plata")`

**`POST /shop/capsule/triple-suerte`:**
- Solo FRJ. Sin opción de tickets.

### 4.3 Backend — VIP monthly

**`shop_service.py:448-463`** — `_grant_vip_monthly_benefits`:

```python
# Antes: grant gashapon tickets
# Ahora:
capsule_rewards = {
    "coral": {"bronce": 2},
    "dorado": {"bronce": 2, "plata": 1},
    "axolite": {"bronce": 3, "plata": 2, "oro": 1},
}
```

**`config.py`** — Actualizar VIP config:
```python
"capsulas_mensuales": {"bronce": 2}  # Coral
"capsulas_mensuales": {"bronce": 2, "plata": 1}  # Dorado
"capsulas_mensuales": {"bronce": 3, "plata": 2, "oro": 1}  # Axolite
```

### 4.4 Frontend

**`Gashapon.tsx`:**
- Renombrar tiers en `TIER_CONFIG`: `cobre` → `bronce`, emoji 🟤 → 🟠
- Actualizar costs display (150/500/2000/2250 → mantener, son display scaling)
- Mostrar cantidad de cápsulas en inventario por tier
- Botón "Usar Cápsula" si el jugador tiene una de ese tier

**`Store.tsx`:**
- Sección de compra de cápsulas individuales (precio en FRJ)
- Eliminar referencias a "Ficha de Gashapon"

**`VipModal.tsx`:**
- Actualizar beneficios mensuales: mostrar cápsulas en lugar de fichas

**`Inventory.tsx`:**
- Agrupar cápsulas como categoría en inventario

### 4.5 Simulación

**`phase_05_gashapon.py`:** Actualizar para usar cápsulas, no tickets.

### 4.6 Tests

**`test_gashapon_rates.py`:** Eliminar tests de ticket, agregar tests de `use_capsule`.

---

## 5. Resumen de la recomendación

| Elemento | Antes | Después |
|----------|-------|---------|
| Pago bronce | 1500 FRJ o 1 ficha | 1500 FRJ o 1 Cápsula Bronce |
| Pago plata | 5000 FRJ o 2 fichas | 5000 FRJ o 1 Cápsula Plata |
| Pago oro | 20000 FRJ o 4 fichas | 20000 FRJ o 1 Cápsula Oro |
| Pago triple | 22500 FRJ o 6 fichas | 22500 FRJ (solo) |
| VIP reward | 1-5 fichas/mes | 2-6 cápsulas/mes (mix tiers) |
| Racha día 7 | 1 ficha | 1 Cápsula Plata |
| Decisión jugador | Optimizar fichas para oro | Usar o guardar cada cápsula |
| Complejidad | Media (cálculo de eficiencia) | Baja (directo) |

**Principio de diseño:** Una cápsula = un roll de su tier. Sin conversiones, sin optimizaciones. La emoción viene de **ganar** la cápsula correcta, no de **calcular** su uso.

---

## 6. Implementación

Ver PR separado. Este documento es la especificación de diseño.

**Archivos a modificar (~12 archivos):**
- `backend/app/api/v1/endpoints/shop.py` — eliminar ticket logic, agregar capsule logic
- `backend/app/core/config.py` — actualizar VIP capsulas_mensuales
- `backend/app/core/prices.py` — renombrar tiers cobre→bronce
- `backend/app/services/shop_service.py` — VIP mensual con cápsulas
- `backend/app/models/items.py` — limpiar metadata
- `backend/app/scripts/seed_catalog.py` — agregar 3 ítems cápsula
- `frontend/components/Gashapon.tsx` — tiers, use_capsule, mostrar inventario
- `frontend/components/Store.tsx` — limpiar referencias
- `frontend/components/VipModal.tsx` — actualizar beneficios
- `backend/app/scripts/simulation/phase_05_gashapon.py` — quitar tickets
- `backend/tests/unit/test_gashapon_rates.py` — actualizar tests
