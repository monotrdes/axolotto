# Plan: Unificación Sistema de Recompensas Diarias — Ciclo Lunar

**Estado**: Planning  
**Categoría**: Game Design / Frontend / Backend  
**Prioridad**: Media  
**Última actualización**: 2026-06-07

---

## 1. Diagnóstico — El problema actual

Existen **dos mecánicas independientes** de recompensa diaria que compiten entre sí:

### Mecánica A — Daily FRJ (header)
- **Ubicación**: Pastilla siempre visible en el encabezado de la app
- **Recompensa**: 50–110 FRJ según racha (día 1 = 50, +10 FRJ/día, máx. día 7 = 110 FRJ)
- **Naturaleza**: Moneda pura, predecible, sin sorpresa
- **Lógica de racha**: Se rompe si faltas 1 día — reinicia a 50 FRJ
- **Backend**: `DailyRewardService` / `daily_reward_service.py`
- **Frontend**: `DailyClaim.tsx` (badge en header, bottom sheet con grid 7 días)

### Mecánica B — Cápsula Diaria gratis (sección Gashapon)
- **Ubicación**: Tab Gashapon — requiere navegación activa
- **Recompensa**: Roll de cápsula bronce: 45% FRJ (50–150), 30% carta, 10% accesorio, 10% booster, 5% axolotito
- **Naturaleza**: Gacha, variable, con emoción
- **Lógica de racha**: `consecutive_days` en `CapsulaDailyFree` — pero no se muestra como UI de racha
- **Backend**: `capsule_service._daily_can_claim` / `CapsulaDailyFree` model
- **Frontend**: `Gashapon.tsx` (`handleDaily`, `dailyStatus`)

### Por qué es un problema de game design

| Problema | Impacto |
|----------|---------|
| **Solapamiento de FRJ**: la cápsula bronce da 50–150 FRJ en el 45% de los rolls → a veces ambas mecánicas premian lo mismo | Dilución narrativa y económica |
| **Asimetría de visibilidad**: la A está en el header (siempre visible), la B requiere ir a Gashapon | La B tiene discovery friction — muchos jugadores no la ven |
| **Confusión narrativa**: ¿por qué Axolotto te da dos regalos distintos sin relación? | Incoherencia en la propuesta de valor F2P |
| **Racha invisible**: la B tiene racha pero no la comunica — la A la muestra prominentemente | La B no genera engagement de retención |
| **Emisión descontrolada**: hasta ~260 FRJ/día si se reclaman ambas | Presión inflacionaria en el ecosistema FRJ |

---

## 2. Solución Propuesta — Sistema de Ciclo Lunar

Reemplazar ambas mecánicas con un **sistema de tres loops anidados** inspirado en los ciclos lunares: el axolotl, animal de Xochimilco, vive en el agua y se rige por los ciclos de la luna.

```
LOOP DIARIO (Días 1–7)
   └─ completar → avanza la LUNA (loop semanal)
         └─ completar 6 Lunas → completa el CICLO LUNAR (loop mensual)
                  └─ celebración + reset a Luna 1
```

### Loop 1 — La Semana (7 días)

Cada día tiene una recompensa fija. El día 7 siempre es una cápsula.

```
┌──────────────────────────────────────────────────────┐
│  🌙 LUNA 1 de 6   •   Día 4 de 7                    │
├──────────────────────────────────────────────────────┤
│  D1    D2    D3    D4    D5    D6    D7               │
│ [50]  [65]  [80]  [★]  [110] [130]  [🎰]            │
│  ✓     ✓     ✓    HOY                BRONCE          │
├──────────────────────────────────────────────────────┤
│  Hoy reclamas: +95 FRJ                              │
│  El día 7 te espera: Cápsula Bronce 🎰              │
│                                                      │
│       [ 🎁 RECLAMAR +95 FRJ ]                       │
└──────────────────────────────────────────────────────┘
```

FRJ diarios (días 1–6): `50 → 65 → 80 → 95 → 110 → 130 FRJ`  
Total FRJ semana: **530 FRJ + cápsula del día 7**

### Loop 2 — Las Lunas (6 semanas)

Cada vez que completas los 7 días, avanzas una Luna. La cápsula del Día 7 depende de en qué Luna estás:

| Luna | Día 7 — Premio | Valor tienda |
|------|---------------|-------------|
| 🌑 **Luna 1** | 1× Cápsula Bronce | 150 FRJ |
| 🌒 **Luna 2** | 2× Cápsulas Bronce | 300 FRJ |
| 🌓 **Luna 3** | 1× Cápsula Plata | 500 FRJ |
| 🌔 **Luna 4** | 1× Cápsula Plata + 1× Bronce | 650 FRJ |
| 🌕 **Luna 5** | 2× Cápsulas Plata | 1,000 FRJ |
| 🌟 **Luna 6** | 1× Cápsula Oro ✨ | 2,000 FRJ |

Completar las 6 Lunas = **Ciclo Lunar completo** → celebración + reset a Luna 1.

### Loop 3 — El Ciclo Lunar (42 días perfectos)

Completar un ciclo entero es un logro difícil y merecedor. Al completar la Luna 6:

1. El jugador recibe su Cápsula Oro (Luna 6)
2. Aparece una pantalla de celebración: **"¡Ciclo Lunar Completado!"**
3. Se otorga un **badge de temporada** cosmético (no monetario): "Axolotl Lunar — Ciclo I"
4. El contador regresa a Luna 1, Día 1

Los badges acumulan: quien completa 3 ciclos tiene "Axolotl Lunar — Ciclo III". Esto funciona como sistema de prestige visual sin inflación.

---

## 3. Reglas del Sistema — Qué rompe qué

Este es el diseño más delicado: la severidad del reset define si los jugadores se re-enganchan o abandonan.

### Regla de la racha diaria

- Debes reclamar cada día dentro de las **24 horas siguientes** al reclamo anterior (midnight México City)
- Si fallas un día: **la racha semanal reinicia a Día 1** de la Luna actual
- **La Luna NO retrocede** — solo reinicia la semana
- Ejemplo: Estás en Luna 3, Día 5 → fallas un día → vuelves a Luna 3, Día 1 (no a Luna 1)

**Por qué**: resetear TODO por fallar un día causa abandono. Resetear solo la semana genera re-engagement ("tengo que rehacerla pero no perdí semanas").

### Regla de la Luna

- Una Luna solo avanza cuando completas los 7 días consecutivos
- Si llevas 10 días sin reclamar nada (inactividad total), la Luna también retrocede a 1
- El umbral de 10 días (vs. 1 día) da margen de vida real sin destruir el progreso acumulado

### Regla del Ciclo

- Si completas Luna 6 y hay un badge de ese ciclo, el número del badge es permanente aunque pierdas rachas después

---

## 4. Análisis Económico

### Antes (sistema actual, racha perfecta 7 días × 6 semanas)

| Mecánica | Total |
|----------|-------|
| Daily FRJ: 560 FRJ/semana × 6 | 3,360 FRJ |
| Cápsula Bronce diaria × 42 (valor tienda) | 6,300 FRJ |
| **Total valor en tienda / 42 días** | **9,660 FRJ** |
| FRJ/día efectivo | ~230 FRJ/día |

### Después (Ciclo Lunar perfecto, 42 días)

| Mecánica | Total |
|----------|-------|
| FRJ días 1–6: 530 FRJ/semana × 6 | 3,180 FRJ |
| Cápsulas del día 7 (valor tienda): 150+300+500+650+1000+2000 | 4,600 FRJ |
| **Total valor en tienda / 42 días** | **7,780 FRJ** |
| FRJ/día efectivo | ~185 FRJ/día |

**Reducción para el jugador perfecto**: ~19% menos valor total, pero concentrado en items de mayor tier (plata, oro) con mejor percepción de valor y más emoción.

**Para el jugador promedio** (que rompe rachas):
- Antes: podía reclamar cada cápsula bronce aunque no tuviera racha diaria → emisión constante
- Después: si no termina la semana, el día 7 nunca llega → emisión se frena naturalmente en los malos weeks

### Curva de recompensa a lo largo del ciclo

```
Valor día 7 (FRJ equiv):
2000 ┤                                              ●
     │
1000 ┤                                    ●●
     │
 650 ┤                          ●
     │
 500 ┤              ●
     │
 300 ┤    ●
     │
 150 ┤●
     └──────────────────────────────────────────
     Luna1  Luna2  Luna3  Luna4  Luna5  Luna6
```

La curva creciente crea anticipación. Los jugadores que están en Luna 4-5 tienen un FOMO real de llegar a la Oro.

---

## 5. Integración con VIP

El sistema de Lunas puede diferenciarse para VIP sin romper el balance:

| Beneficio VIP | Descripción |
|---------------|-------------|
| **Escudo Lunar** (1×/mes) | Una vez al mes, si fallas un día, la racha NO se rompe. Consumible automático. |
| **Arranque rápido** | VIP empieza cada ciclo en Luna 2 (se salta la primera) |
| **Multiplicador día 7** | VIP recibe +1 cápsula de un tier inferior extra (ej: Luna 3 = 1 Plata + 1 Bronce de regalo) |

El Escudo Lunar es especialmente valioso: un viaje o un día ocupado no destruye el progreso. Esto es un argumento de venta directo para VIP.

---

## 6. UX — Puntos de entrada y flujo visual

### Header badge

```
Antes:  🔥 4/7
Después: 🌔 L4 · D3/7       (Luna 4, Día 3 de 7, puede reclamarse → pulsa)
         🌔 L4 · D3 ✓       (ya reclamado hoy)
```

El badge muestra Luna + Día, los dos loops en un vistazo.

### Bottom sheet unificado (reemplaza DailyClaim.tsx)

```
┌──────────────────────────────────────────────────────┐
│  🌔 CICLO LUNAR · Luna 4 de 6                       │
│  ○○○● · ○○ (Lunas completadas / total)              │
├──────────────────────────────────────────────────────┤
│  ESTA SEMANA:                                        │
│  [50] [65] [80] [95] [110] [130]  [🎰 P+B]         │
│   ✓    ✓    ✓    ★                  día 7: Plata     │
│                                     + Bronce gratis  │
├──────────────────────────────────────────────────────┤
│  Hoy: +95 FRJ       Día 7: 🎰 Plata + Bronce       │
│                                                      │
│       [ 🎁 RECLAMAR +95 FRJ ]                       │
├──────────────────────────────────────────────────────┤
│  PRÓXIMAS LUNAS:                                     │
│  L5: 2× Plata   L6: 🏆 Oro                         │
└──────────────────────────────────────────────────────┘
```

### En Gashapon

Eliminar el botón de "cápsula diaria gratis" independiente. En su lugar:

```
╔══════════════════════════════════════╗
║  🌔 Tu Ciclo Lunar — Luna 4, Día 3  ║
║  Día 7 te espera: 🎰 Plata + Bronce ║
║  [ Ver mi progreso → ]               ║
╚══════════════════════════════════════╝
```

Este banner vive en la parte superior de Gashapon y abre el mismo bottom sheet del header. Gashapon se convierte en el punto de aspiración ("aquí puedes comprar más cápsulas, y la Luna te regala una también").

---

## 7. Plan de Implementación

### Backend

**Archivos a modificar / crear:**

| Archivo | Cambio |
|---------|--------|
| `backend/app/services/lunar_streak_service.py` | **CREAR** — lógica central: `LunarStreakService` |
| `backend/app/models/user.py` | Añadir `lunar_streak_day` (0–7), `lunar_week` (1–6), `lunar_last_claim_at`, `lunar_cycles_completed` |
| `backend/app/api/v1/endpoints/bank.py` | Añadir `GET /rewards/lunar` y `POST /rewards/lunar/claim` |
| `backend/app/services/daily_reward_service.py` | **DEPRECAR** — endpoint legacy retorna 410 Gone |
| `backend/app/services/capsule_service.py` | Eliminar `_daily_can_claim` — ya no se usa desde aquí |

**Esquema del `LunarStreakService`:**

```python
DAILY_FRJ = [50, 65, 80, 95, 110, 130]  # días 1-6

LUNA_REWARDS: dict[int, list[dict]] = {
    1: [{"type": "capsule", "tier": "bronce", "qty": 1}],
    2: [{"type": "capsule", "tier": "bronce", "qty": 2}],
    3: [{"type": "capsule", "tier": "plata",  "qty": 1}],
    4: [{"type": "capsule", "tier": "plata",  "qty": 1},
        {"type": "capsule", "tier": "bronce", "qty": 1}],
    5: [{"type": "capsule", "tier": "plata",  "qty": 2}],
    6: [{"type": "capsule", "tier": "oro",    "qty": 1}],
}

class LunarStreakService:
    def get_status(user: User) -> LunarStatus:
        # Retorna: lunar_week, streak_day, can_claim,
        #          today_reward_preview, day7_reward_preview,
        #          next_claim_at, inactivity_warning

    def claim(db: Session, user: User) -> ClaimResult:
        # Días 1-6: acredita FRJ, avanza streak_day
        # Día 7: ejecuta rolls de cápsula según LUNA_REWARDS[lunar_week]
        #         luego avanza lunar_week (o cierra ciclo si era 6)
        #         reinicia streak_day a 0

    def _check_inactivity(user: User) -> bool:
        # Si last_claim > 10 días: resetea lunar_week a 1
```

**Alembic migration**: nuevas columnas en tabla `users`.

### Frontend

**Archivos a modificar:**

| Archivo | Cambio |
|---------|--------|
| `frontend/components/DailyClaim.tsx` | Rediseñar completamente: badge L#·D#/7 + bottom sheet con grid semanal + track de 6 Lunas + preview día 7 |
| `frontend/components/Gashapon.tsx` | Eliminar sección `handleDaily` — reemplazar con banner que enlaza al sheet unificado |
| `frontend/services/rewardsService.ts` | Nuevas funciones `fetchLunarStatus()` y `claimLunarDay()` |
| `frontend/types/economy.ts` | Nueva interfaz `LunarStatus` con `lunar_week`, `streak_day`, `day7_preview`, `luna_track[]` |

### Migración de datos existentes

- Mapear `f2p_daily_claim_streak` (1–7) → `lunar_streak_day`
- Inicializar todos los usuarios existentes a `lunar_week = 1`
- `CapsulaDailyFree` table: mantener como log histórico, no eliminar

---

## 8. Criterios de Verificación

**Flujo diario:**
- [x] `GET /rewards/lunar/status` retorna estado correcto sin racha, con racha activa, racha rota, inactividad >7d
- [x] `POST /rewards/lunar/claim` días 1–6: acredita FRJ correcto, avanza `streak_day`
- [x] `POST /rewards/lunar/claim` día 7: ejecuta los rolls de `LUNA_REWARDS[lunar_week]`, avanza `lunar_week`
- [x] No se puede reclamar 2 veces el mismo día (429)
- [x] Racha diaria se rompe correctamente si gap > 1 día; `lunar_week` no retrocede

**Progresión de Lunas:**
- [x] Luna 1 día 7 → 1 Bronce; Luna 2 día 7 → 2 Bronce; ... Luna 6 día 7 → 1 Oro
- [x] Al completar Luna 6: `lunar_cycles_completed` incrementa, `lunar_week` vuelve a 1
- [x] Inactividad >7d: `lunar_week` resetea a 1 correctamente

**Frontend:**
- [x] Badge muestra "🌙 L2·D5/7" con punto de notificación si `can_claim`
- [x] Bottom sheet muestra grid 7 días con FRJ correcto por día + ícono de cápsula en día 7
- [x] Track de 6 Lunas (iconos lunares) refleja progreso actual
- [x] Preview "Próximas Lunas" muestra correctamente L+1 y L+2
- [x] Gashapon ya no tiene sección de cápsula diaria independiente
- [x] Endpoints legacy (`/rewards/daily-claim`, `/shop/capsule/daily-claim`) retornan 410 Gone

---

## 9. Decisiones cerradas (2026-06-07)

| Pregunta | Decisión |
|----------|----------|
| Umbral de inactividad para resetear Luna | **7 días** sin ningún reclamo → Luna vuelve a 1 |
| VIP tiene Escudo Lunar | **No** — VIP tiene sus propios premios separados |
| Badges de ciclo | **Solo cosmética** — sin efecto de gameplay |
| Luna 6 recompensa extra | **No** — 1× Cápsula Oro es suficiente; el badge cosmético es el diferenciador |
| Nombre oficial del sistema | **"Ciclo Lunar"** en-game; código usa `LunarStreakService` |

---

## 10. Archivos de referencia

- `backend/app/services/daily_reward_service.py` — lógica actual de racha FRJ
- `backend/app/services/capsule_service.py` — `_roll_capsule` y `_daily_can_claim`
- `frontend/components/DailyClaim.tsx` — UI actual del badge y bottom sheet
- `frontend/components/Gashapon.tsx` — sección `handleDaily` de la máquina
- `backend/app/models/user.py` — campos `f2p_daily_claim_streak`, `last_f2p_daily_claim_at`
- `backend/app/core/config.py` — VIP tiers (si se añade Escudo Lunar)
