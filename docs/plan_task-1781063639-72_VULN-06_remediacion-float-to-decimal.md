# Plan de Remediacion: VULN-06 — Migrar saldos monetarios de `float` a `Decimal`/enteros

**Severidad:** 🟡 Media
**Ubicacion:** `models/economy.py:49-50`, `bank_service.py`, `market_service.py`, `game_service.py`, `multiplayer_service.py`, `shop_service.py`
**Auditoria:** docs/AUDITORIA_SEGURIDAD_2026-06-09.md#L169-L177
**Task:** task-1781063639-72

---

## 1. Descripcion del Problema

Todos los saldos y montos en la capa economica son `float` (IEEE-754). Las comisiones (`amount * 0.05`), bonuses y conversiones acumulan errores de redondeo. Operaciones repetidas pueden crear o destruir "polvo" de FRJ, y comparaciones `saldo < precio` pueden fallar en los bordes. Esto permite "dust farming": estructurar miles de micro-transacciones donde el redondeo favorece al atacante.

## 2. Impacto

- Fugas economicas lentas pero acumulables
- Contabilidad no determinista entre DB y logica de juego
- Inconsistencia con on-chain que ya usa `to_wei` (enteros)

## 3. Estrategia de Remediacion

### Opcion A (Recomendada): Enteros con unidad minima (wei)

Migrar todos los saldos a enteros en la unidad mas pequena (centavos de FRJ / satoshis de AXF). Alineado con on-chain.

**Cambios necesarios:**

1. **models/economy.py** — Cambiar `axofichas: float` y `frijolitos: float` a `axofichas: int` y `frijolitos: int`.
   - Migracion: `UPDATE wallet SET axofichas = axofichas * 10**6` (o el factor que se defina, ej. 10^4 para FRJ, 10^18 para AXF).
   - Añadir columnas `precision_axf: int = 6` y `precision_frj: int = 4` por si se necesita variable.

2. **core/config.py** — Definir constantes:
   ```python
   AXF_DECIMALS_BACKEND: int = 6   # 1 AXF = 1_000_000 unidades minimas
   FRJ_DECIMALS_BACKEND: int = 4   # 1 FRJ = 10_000 unidades minimas
   ```

3. **services/bank_service.py** — Reemplazar toda aritmetica float por int.
   - `amount * 0.05` → `amount * 5 // 100`
   - Validar que todas las operaciones usen `//` (division entera) para truncar hacia el usuario de forma predecible.

4. **services/game_logic.py, game_service.py** — Premios, fees, multipliers con aritmetica entera.

5. **services/multiplayer_service.py** — Pool calculations, loot distribution, luck_bonus con enteros.

6. **services/shop_service.py, market_service.py** — Precios, descuentos, fees en enteros.

7. **web3_service.py** — Eliminar conversion float-to-wei intermedia. Usar enteros directamente.

8. **Validadores Pydantic** — Crear tipos `AxfAmount = Annotated[int, Field(ge=0)]` y `FrjAmount = Annotated[int, Field(ge=0)]`.

9. **Alembic migration** — Script que transforma columnas y recalcula.

### Opcion B: `Decimal` con contexto fijo

Si se prefiere legibilidad (no recomiendo por tener que convertir a int para on-chain igualmente):
- Usar `DECIMAL(18, 6)` en DB + `Decimal` en Python con `getcontext().prec = 28`.
- Convertir a int solo en la frontera con web3_service.

## 4. Mitigacion de Dust Farming

- Truncar siempre hacia el usuario en fees (floor).
- Usar `amount // divisor` no `amount / divisor`.
- Añadir un `assert total_distributed <= total_collected` (o `==` segun invariante).
- Log de acumulacion de dust para monitoreo.

## 5. Tareas

- [ ] `models/economy.py` — Schema y migracion
- [ ] `core/config.py` — Constantes de precision
- [ ] `services/bank_service.py` — Aritmetica entera
- [ ] `services/game_service.py`, `game_logic.py` — Premios/fees enteros
- [ ] `services/multiplayer_service.py` — Pool entero
- [ ] `services/shop_service.py`, `market_service.py` — Precios enteros
- [ ] `web3_service.py` — Sin float intermedio
- [ ] Validadores Pydantic — Tipos `AxfAmount`, `FrjAmount`
- [ ] Alembic migration — Conversion de columnas
- [ ] Tests de invariante: `sum(debits) == sum(credits)` en operaciones atomicas

## 6. Pruebas

- Property-based testing con Hypothesis: generar operaciones aleatorias y verificar invariante de suma cero.
- Test de dust: 10,000 micro-transacciones de 0.01 FRJ, verificar que el total reconciliado <= 0.01 FRJ de desvio.

## 7. Dependencias

- Ejecutar despues de o en paralelo con VULN-04 (outbox) para no conflictuar migraciones de tabla.
