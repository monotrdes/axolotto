# 🎁 Plan: Flujo Corcholata → Tutorial → Premio + Bug Fix Eclosión

> **Estado**: ✅ COMPLETADO — Todas las tareas implementadas y verificadas en código (2026-06-02).
> 1. ✅ El axolotito eclosiona correctamente (bugs de `res.ok` arreglados)
> 2. ✅ El premio se guarda y se revela al final del tutorial (flujo Corcholata → Tutorial → Cofre)

---

---

# 🔴 PARTE A — Arreglar Bug de Eclosión (CRÍTICO)

## Diagnóstico

El frontend NUNCA verifica `res.ok` en las llamadas al backend del tutorial. Cuando el backend falla (401, 400, 500), el `catch(() => ({}))` traga el error y el frontend avanza como si nada. 

**Efecto dominó:**
1. `ActKarmaReveal.handleContinue` → `POST /tutorial/next-step` falla → fase no avanza en backend
2. `ActGame.handleAdvance` → mismo problema con `/next-step`
3. `ActHatching` → `POST /tutorial/complete/{id}` → backend responde `400 "Fase actual: 1"`
4. `axolotito_name` es `undefined`, axolotito NUNCA se crea en BD
5. El huevo sigue apareciendo en el Santuario, sin nombre ni nada

---

## Fix #1: `ActGame.tsx` — Verificar res.ok en handleAdvance

**Archivo**: `frontend/components/tutorial/acts/ActGame.tsx`
**Línea**: ~132 (dentro de `handleAdvance`)

### ANTES (código actual):
```tsx
const handleAdvance = useCallback(async () => {
  if (advancing || !gameCompleted || !webito?.tutorialId) return;
  setAdvancing(true);
  try {
    const res = await fetch(`${API_BASE}/tutorial/next-step/${webito.tutorialId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json',
        ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
      },
    });
    await res.json().catch(() => ({}));
    onComplete();
  } catch (e) {
    console.error('Error al avanzar fase del tutorial:', e);
    onComplete(); // <-- ¡AVANZA IGUAL aunque haya fallado!
  } finally {
    setAdvancing(false);
  }
}, [advancing, gameCompleted, webito?.tutorialId, authenticated, token, onComplete]);
```

### DESPUÉS (código corregido):
```tsx
const handleAdvance = useCallback(async () => {
  if (advancing || !gameCompleted || !webito?.tutorialId) return;
  setAdvancing(true);
  try {
    const res = await fetch(`${API_BASE}/tutorial/next-step/${webito.tutorialId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json',
        ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
      },
    });

    // ✅ NUEVO: Verificar respuesta del backend
    if (!res.ok) {
      const errText = await res.text().catch(() => 'Unknown error');
      console.error(`❌ Tutorial next-step falló (${res.status}): ${errText}`);
      setAdvancing(false);
      return; // ⛔ NO avanzar si falló
    }

    const data = await res.json();
    console.log('✅ Tutorial next-step OK — fase:', data?.current_step);
    onComplete();
  } catch (e) {
    console.error('❌ Error de red al avanzar fase del tutorial:', e);
    // ⛔ NO llamar onComplete() en el catch
  } finally {
    setAdvancing(false);
  }
}, [advancing, gameCompleted, webito?.tutorialId, authenticated, token, onComplete]);
```

---

## Fix #2: `ActHatching.tsx` — Verificar res.ok + loguear nombre

**Archivo**: `frontend/components/tutorial/acts/ActHatching.tsx`
**Línea**: ~42 (useEffect que llama `/complete`)

### ANTES (código actual):
```tsx
useEffect(() => {
  let cancelled = false;
  const doComplete = async () => {
    try {
      const res = await fetch(`${API_BASE}/tutorial/complete/${webito.tutorialId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
          ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      });
      const data = await res.json().catch(() => ({}));
      // ❌ Si el backend devuelve 400, data = {"detail":"..."} y axolotito_name es undefined
      if (!cancelled && data?.axolotito_name) {
        axoNameRef.current = data.axolotito_name;
        setAxolotitoName(data.axolotito_name);
      }
      if (!cancelled) {
        setReady(true);
      }
    } catch (e) {
      console.error(e);
      if (!cancelled) setReady(true); // <-- avanza igual
    }
  };
  // ...
}, []);
```

### DESPUÉS (código corregido):
```tsx
useEffect(() => {
  let cancelled = false;
  const doComplete = async () => {
    try {
      console.log('🥚 ActHatching: llamando POST /tutorial/complete/', webito.tutorialId);
      const res = await fetch(`${API_BASE}/tutorial/complete/${webito.tutorialId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
          ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      });

      // ✅ NUEVO: Verificar respuesta
      if (!res.ok) {
        const errText = await res.text().catch(() => 'Unknown error');
        console.error(`❌ Tutorial complete falló (${res.status}): ${errText}`);
        if (!cancelled) setReady(true); // mostrar algo aunque falle
        return;
      }

      const data = await res.json();
      console.log('✅ Tutorial complete respuesta:', JSON.stringify(data));

      if (!cancelled && data?.axolotito_name) {
        axoNameRef.current = data.axolotito_name;
        setAxolotitoName(data.axolotito_name);
        console.log('🐣 Axolotito eclosionado:', data.axolotito_name);
      } else if (!cancelled) {
        console.warn('⚠️ complete no devolvió axolotito_name. Data:', data);
      }
      if (!cancelled) {
        setReady(true);
      }
    } catch (e) {
      console.error('❌ Error de red en tutorial complete:', e);
      if (!cancelled) setReady(true);
    }
  };
  // ...
}, []);
```

---

## Fix #3: `ActKarmaReveal.tsx` — Verificar res.ok

**Archivo**: `frontend/components/tutorial/acts/ActKarmaReveal.tsx`
**Línea**: ~72 (handleContinue)

### ANTES:
```tsx
const handleContinue = async () => {
  if (transitioning) return;
  setTransitioning(true);
  try {
    if (webito?.tutorialId) {
      await fetch(`${API_BASE}/tutorial/next-step/${webito.tutorialId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
          ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      });
    }
    onComplete();
  } catch {
    onComplete();
  } finally {
    setTransitioning(false);
  }
};
```

### DESPUÉS:
```tsx
const handleContinue = async () => {
  if (transitioning) return;
  setTransitioning(true);
  try {
    if (webito?.tutorialId) {
      const res = await fetch(`${API_BASE}/tutorial/next-step/${webito.tutorialId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
          ...(authenticated ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      });

      // ✅ NUEVO: Verificar respuesta
      if (!res.ok) {
        const errText = await res.text().catch(() => 'Unknown error');
        console.error(`❌ KarmaReveal next-step falló (${res.status}): ${errText}`);
        setTransitioning(false);
        return; // ⛔ NO avanzar
      }

      console.log('✅ KarmaReveal next-step OK');
    }
    onComplete();
  } catch (e) {
    console.error('❌ Error de red en KarmaReveal handleContinue:', e);
    // ⛔ NO llamar onComplete()
  } finally {
    setTransitioning(false);
  }
};
```

---

## Fix #4: Backend — Logs en `complete_tutorial()`

**Archivo**: `backend/app/services/tutorial_service.py`
**Línea**: ~200 (función `complete_tutorial`)

Agregar logs al inicio de la función para diagnosticar qué llega:

```python
async def complete_tutorial(
    db: AsyncSession, tutorial_id: str, user_id: str
) -> dict:
    """Completar el tutorial y eclosionar el axolotito."""
    print(f"🐣 complete_tutorial llamado: tutorial_id={tutorial_id}, user_id={user_id}", flush=True)

    webito = await db.execute(
        select(TutorialWebito).where(
            TutorialWebito.id == tutorial_id,
            TutorialWebito.user_id == user_id
        )
    )
    webito = webito.scalar_one_or_none()

    if not webito:
        print(f"❌ TutorialWebito no encontrado para id={tutorial_id}", flush=True)
        raise HTTPException(status_code=404, detail="Tutorial no encontrado")

    print(f"📊 webito: current_step={webito.current_step}, completed={webito.completed}", flush=True)

    if webito.current_step < 8:
        print(f"❌ Tutorial incompleto: paso {webito.current_step}/8", flush=True)
        raise HTTPException(
            status_code=400,
            detail=f"Debes completar todas las fases antes. Fase actual: {webito.current_step}."
        )

    # ... resto de la función (llamar _perform_hatch, etc.)
    print(f"🐣 Llamando _perform_hatch para webito={webito.id}", flush=True)
    axolotito = await _perform_hatch(db, webito)
    print(f"✅ Hatch exitoso: {axolotito.name} (id={axolotito.id})", flush=True)
    # ...
```

---

## Fix #5: Backend — `imprinting_service.py` resiliente a base_stats = 0

**Archivo**: `backend/app/services/imprinting_service.py`
**Línea**: ~85 (función `final_stats`)

### Problema
Cuando no hay padrino (sin `imprinting_session`), los `base_stat_focus`, `base_stat_wisdom`, etc. son `0.0`. Esto genera stats finales muy bajos.

### Solución
Si no hay imprinting, usar defaults balanceados:

```python
def final_stats(
    base_stat_focus: float,
    base_stat_wisdom: float,
    base_stat_strength: float,
    base_stat_agility: float,
    bonus_focus: float = 0.0,
    bonus_wisdom: float = 0.0,
    bonus_strength: float = 0.0,
    bonus_agility: float = 0.0,
    bonus_salinity: float = 0.0,
) -> dict:
    """Calcular stats finales combinando base + bonus."""
    # Si los base_stats son 0 (sin imprinting), usar defaults
    if base_stat_focus == 0.0 and base_stat_wisdom == 0.0 and base_stat_strength == 0.0 and base_stat_agility == 0.0:
        base_stat_focus = 50.0
        base_stat_wisdom = 50.0
        base_stat_strength = 50.0
        base_stat_agility = 50.0

    return {
        "focus": base_stat_focus + bonus_focus,
        "wisdom": base_stat_wisdom + bonus_wisdom,
        "strength": base_stat_strength + bonus_strength,
        "agility": base_stat_agility + bonus_agility,
        "salinity": bonus_salinity,
    }
```

---

---

# 🟠 PARTE B — Flujo Corcholata: Premio al Final del Tutorial

## Objetivo

> El premio NO debe entregarse en el momento del canjeo. Debe **guardarse y revelarse al final del tutorial** dentro de un cofre animado.

---

## Diagrama del Nuevo Flujo

```
LANDING PAGE
  └→ "Canjear mi Corcholata"
       └→ CodeEntryPanel (input)
            └→ POST /codes/redeem
                 ├─ ❌ Inválido → error + intentos
                 └─ ✅ Válido
                      └→ PendingReward guardado (NO se entrega todavía)
                      └→ Panel: "🔒 Tu premio te espera al final del tutorial"
                      └→ Redirige a /play

/play
  └→ POST /auth/sync → has_pending_corcholata_reward = true
  └→ WebitoIntroAnimation
  └→ TutorialFlow
       ├─ Acto 1-7 (normal)
       ├─ Banner sutil flotante: "🎁 Premio al final"
       ├─ Acto 8: ActKarmaReveal
       ├─ Acto 9: ActHatching (eclosión del axolotito)
       └─ Acto 10: ActTreasureChest 🆕
            ├─ Animación de cofre abriéndose
            ├─ POST /rewards/claim
            │    ├─ Entrega 139 AXF + 1000 FRJ + ítem exclusivo
            │    └─ Marca PendingReward.claimed = true
            └─ Muestra recompensas
       └→ PostTutorialBranch
       └→ Juego normal
```

---

## B1 — Nuevo Modelo: `PendingReward`

**Archivo**: `backend/app/models/promo.py` (agregar al final)

```python
class PendingReward(Base):
    """Premio de código promocional pendiente de reclamar (se entrega al final del tutorial)."""
    __tablename__ = "pending_rewards"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, unique=True)
    promo_code_id = Column(String(64), ForeignKey("promo_codes.id"), nullable=False)
    reward_axf = Column(Integer, nullable=False, default=0)
    reward_frj = Column(Integer, nullable=False, default=0)
    reward_item_id = Column(String(64), nullable=True)
    claimed = Column(Boolean, default=False, nullable=False)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="pending_reward")
    promo_code = relationship("PromoCode", backref="pending_reward")
```

**Migración:**
```bash
cd backend
alembic revision --autogenerate -m "add_pending_rewards_table"
alembic upgrade head
```

---

## B2 — Modificar `promo_service.py`: NO entregar, guardar

**Archivo**: `backend/app/services/promo_service.py`
**Función**: `redeem_promo_code()`

Donde actualmente hace:
```python
# ❌ ACTUAL: entrega inmediata
wallet = await bank_service.get_or_create_wallet(db, user_id)
wallet.axofichas += 139
wallet.frijolitos += 1000
```

Reemplazar por:
```python
# ✅ NUEVO: guardar para después
from app.models.promo import PendingReward

pending = PendingReward(
    user_id=user_id,
    promo_code_id=promo_code.id,
    reward_axf=139,
    reward_frj=1000,
    reward_item_id=None,
    expires_at=datetime.utcnow() + timedelta(days=7),
)
db.add(pending)
await db.flush()
```

Y cambiar respuesta de:
```python
return {"status": "success", "reward": {"axofichas": 139, "frijolitos": 1000}}
```
A:
```python
return {
    "status": "pending_tutorial",
    "message": "Código verificado! Tu premio se revelará al terminar el tutorial.",
    "reward_preview": {"axofichas": 139, "frijolitos": 1000, "item": "Item exclusivo de lanzamiento"}
}
```

---

## B3 — Endpoint `POST /codes/redeem` — respuesta diferenciada

El endpoint ya redirige a `promo_service.redeem_promo_code()`. Solo asegurar que el frontend pueda distinguir:

| `status` | Significado |
|---|---|
| `"success"` | Canjeado y entregado (usuario sin tutorial pendiente) |
| `"pending_tutorial"` | Código válido, premio guardado, esperando tutorial |
| `"error"` | Código inválido/expirado/ya usado |

---

## B4 — Nuevo Endpoint: `POST /rewards/claim`

**Archivo NUEVO**: `backend/app/api/v1/endpoints/rewards.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.promo import PendingReward
from app.services.bank_service import BankService

router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.post("/claim")
async def claim_pending_reward(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reclama el premio Corcholata pendiente después del tutorial."""
    
    result = await db.execute(
        select(PendingReward).where(
            PendingReward.user_id == current_user.id,
            PendingReward.claimed == False,
        )
    )
    pending = result.scalar_one_or_none()

    if not pending:
        raise HTTPException(status_code=404, detail="No tienes premios pendientes")

    if pending.expires_at and pending.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Tu premio ha expirado")

    # ENTREGAR
    bank_service = BankService()
    wallet = await bank_service.get_or_create_wallet(db, current_user.id)

    wallet.axofichas = (wallet.axofichas or 0) + pending.reward_axf
    wallet.frijolitos = (wallet.frijolitos or 0) + pending.reward_frj

    # Marcar como reclamado
    pending.claimed = True
    pending.claimed_at = datetime.utcnow()

    await db.commit()

    return {
        "status": "claimed",
        "reward": {
            "axofichas": pending.reward_axf,
            "frijolitos": pending.reward_frj,
            "item": pending.reward_item_id,
        },
        "wallet": {
            "axofichas": wallet.axofichas,
            "frijolitos": wallet.frijolitos,
        }
    }
```

**Registrar router** en `backend/app/api/v1/__init__.py`:
```python
from app.api.v1.endpoints import rewards
app.include_router(rewards.router, prefix="/api/v1")
```

---

## B5 — `POST /auth/sync` devuelve `has_pending_corcholata_reward`

**Archivo**: `backend/app/api/v1/endpoints/auth.py`
**Función**: `sync_user()`

Agregar al response:
```python
pending_result = await db.execute(
    select(PendingReward).where(
        PendingReward.user_id == current_user.id,
        PendingReward.claimed == False,
    )
)
has_pending = pending_result.scalar_one_or_none() is not None

return {
    # ... campos existentes ...
    "has_pending_corcholata_reward": has_pending,
}
```

---

## B6 — `POST /tutorial/complete` devuelve `has_pending_reward`

**Archivo**: `backend/app/services/tutorial_service.py`
**Función**: `complete_tutorial()`

Agregar al dict de respuesta:
```python
pending_result = await db.execute(
    select(PendingReward).where(
        PendingReward.user_id == user_id,
        PendingReward.claimed == False,
    )
)
has_pending = pending_result.scalar_one_or_none() is not None

return {
    "status": "ok",
    "axolotito_name": axolotito.name,
    "axolotito_id": axolotito.id,
    "has_pending_reward": has_pending,
}
```

---

## B7 — Frontend: Nuevo Estado en `CodeEntryPanel.tsx`

En `handleRedeem`:
```tsx
if (data.status === 'pending_tutorial') {
  setPanelState('pending_tutorial');
  return;
}
```

Nuevo bloque UI:
```tsx
{panelState === 'pending_tutorial' && (
  <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
    className="text-center space-y-6 py-6">
    <div className="text-7xl animate-bounce">🔒</div>
    <h3 className="text-2xl font-black text-yellow-400">¡Código Verificado!</h3>
    <p className="text-gray-300 text-sm">Tu Kit de Bienvenida está guardado. Se revelará al terminar el tutorial.</p>
    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-xs text-yellow-300 space-y-1">
      <div>🪙 +139 Axofichas</div>
      <div>🌿 +1,000 Frijolitos</div>
      <div>🎁 Ítem exclusivo de lanzamiento</div>
    </div>
    <button onClick={() => window.location.href = '/play'}
      className="px-8 py-3 bg-gradient-to-r from-yellow-500 to-amber-500 text-black font-bold rounded-full">
      Comenzar Tutorial →
    </button>
  </motion.div>
)}
```

---

## B8 — Banner Flotante Durante el Tutorial

**Archivo**: `frontend/components/tutorial/TutorialFlow.tsx`

Prop nueva: `hasPendingReward?: boolean`

```tsx
{hasPendingReward && (
  <motion.div
    initial={{ y: 100, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    transition={{ delay: 2 }}
    className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50
               bg-yellow-500/10 border border-yellow-500/30 backdrop-blur-md
               rounded-full px-6 py-2.5 shadow-lg">
    <p className="text-yellow-400 text-xs font-bold animate-pulse flex items-center gap-2">
      <span>🎁</span> Tu premio Corcholata te espera al final del tutorial
    </p>
  </motion.div>
)}
```

---

## B9 — Nuevo Componente: `ActTreasureChest.tsx`

Ver código completo en el documento del editor.

Fases de animación: `chest_closed` → `chest_opening` → `rewards_revealed`
- Auto-claim al montar (si `hasPendingReward`)
- Partículas doradas durante apertura
- Revelación escalonada: AXF → FRJ → Ítem
- Si `hasPendingReward` es false, salta automáticamente con `onComplete()`

---

## B10 — Agregar `treasure-chest` al `TUTORIAL_SCRIPT`

**Archivo**: `frontend/components/tutorial/TutorialScript.ts`

Después de `acto-9-hatching`:
```ts
{
  id: "acto-10-cofre",
  type: "treasure-chest",
  title: "Cofre del Tesoro",
  condition: (ctx: TutorialContext) => ctx.hasPendingReward === true,
},
```

---

## B11 — Pasar `hasPendingReward` desde `syncData` a `TutorialFlow`

**Archivo**: `frontend/app/play/page.tsx`

```tsx
const [hasPendingReward, setHasPendingReward] = useState(false);

// En sync:
if (data.has_pending_corcholata_reward) {
  setHasPendingReward(true);
}

// Pasar a TutorialFlow:
<TutorialFlow
  hasPendingReward={hasPendingReward}
  ...
/>
```

Y en `TutorialFlow.tsx`, pasar al `TutorialContext` para que los actos lo lean.

---

# ✅ Checklist de Implementación

## Fase A — Bug Fixes (CRÍTICO)
- [x] A1: `ActGame.tsx` — verificar `res.ok` en `handleAdvance`
- [x] A2: `ActHatching.tsx` — verificar `res.ok` en `useEffect` + loguear nombre
- [x] A3: `ActKarmaReveal.tsx` — verificar `res.ok` en `handleContinue` *(N/A: karma se resuelve server-side en fase 3, no hay fetch)*
- [x] A4: `tutorial_service.py` — agregar `print()` logs en `complete_tutorial()`
- [x] A5: `imprinting_service.py` — defaults si `base_stat_* == 0.0` *(usa `initial_base_stats()` con rangos por stat — mejora sobre flat 50.0)*

## Fase B — Corcholata → Tutorial → Premio
- [x] B1: `models/promo.py` — modelo `PendingReward` + migración Alembic
- [x] B2: `promo_service.py` — guardar en `PendingReward` en vez de entregar
- [x] B3: `codes.py` — respuesta `status: "pending_tutorial"`
- [x] B4: `rewards.py` (NUEVO) — endpoint `POST /rewards/claim`
- [x] B5: `auth.py` — sync devuelve `has_pending_corcholata_reward`
- [x] B6: `tutorial_service.py` — complete devuelve `has_pending_reward`
- [x] B7: `CodeEntryPanel.tsx` — nuevo estado `pending_tutorial`
- [x] B8: `TutorialFlow.tsx` — banner flotante "🎁 Premio al final"
- [x] B9: `ActTreasureChest.tsx` (NUEVO) — cofre con animación y claim
- [x] B10: `TutorialScript.ts` — agregar `acto-10-cofre`
- [x] B11: `app/play/page.tsx` — pasar `hasPendingReward` a `TutorialFlow`

---

# 🧪 Cómo Probar el Flujo Completo

1. **Canjear código** en landing → debe mostrar "🔒 Premio guardado"
2. **Ir a /play** → debe arrancar tutorial normalmente
3. **Banner** amarillo abajo durante todo el tutorial
4. **ActHatching** → debe mostrar nombre del axolotito eclosionado
5. **ActTreasureChest** → cofre se abre, muestra +139 AXF, +1000 FRJ, ítem
6. **Santuario** → el axolotito aparece con su nombre y stats
7. **Wallet** → axofichas y frijolitos acreditados
