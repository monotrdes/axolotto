# Onboarding Completo: Landing → Tutorial → Branch F2P/Premium Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conectar el landing page con el flujo completo de onboarding: login → animación de primer contacto con el Webito → tutorial híbrido → branch de monetización (paga y juega / gratis y especta con tu Axolotito despierto), más una herramienta de reset para pruebas.

**Architecture:** Cuatro capas en secuencia: (1) landing con auth integrada, (2) `/play` detecta primer uso y orquesta la experiencia, (3) el tutorial ya construido (TutorialFlow) se engancha al flujo, (4) post-tutorial branching decide entre modo premium y modo F2P con Axolotito despierto. El endpoint `auth/sync` actúa como fuente de verdad para `tutorial_completed` e `is_new_user`. El reset de dev es un endpoint protegido por `ENVIRONMENT=development`.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, Privy (Google + Apple OAuth), FastAPI, SQLModel

---

## Contexto del Codebase

### Archivos clave ya existentes

| Archivo | Estado actual |
|---------|---------------|
| `frontend/app/page.tsx` | Landing estático (161 líneas). Sin auth. Link a `/play`. |
| `frontend/app/play/page.tsx` | App principal con tabs. `auth/sync` al entrar. Sin detección de primer uso. |
| `frontend/components/PrivyProviderWrapper.tsx` | Privy con solo `["google", "email"]`. Sin Apple. |
| `backend/app/api/v1/endpoints/user.py` | `POST /auth/sync` — NO devuelve `tutorial_completed`. |
| `frontend/components/tutorial/TutorialFlow.tsx` | Tutorial completo ya construido (3 partidas + karma + eclosión). |
| `frontend/components/criadero/SleepingEgg.tsx` | Huevo durmiente F2P (para usuarios pre-tutorial). |

### Flujo actual vs. flujo objetivo

```
ACTUAL:
  landing → "Únirme" → /play → tabs (sin onboarding)

OBJETIVO:
  landing → login → /play → [si is_new_user] → WebitoIntroAnimation
            → TutorialFlow (3 partidas) → PostTutorialBranch
            → [paga] → modo premium con todas las tabs
            → [no paga] → F2P: Axolotito despierto especta + "Armar el Webito"
```

### El cambio narrativo F2P post-tutorial

**Antes del tutorial:** Usuario sin Axolotito → `SleepingEgg` (huevo durmiente acumula fragmentos).
**Después del tutorial:** Usuario CON Axolotito nacido pero sin GAL → **Axolotito despierto frustrado**. Ya no es un huevo dormido. Es tu Axolotito vivo que *quiere* jugar pero no puede. Especta partidas y comenta con `DialogueEngine`. Su meta es motivarte a comprar GAL.

---

## Mapa de archivos

| Archivo | Tipo | Responsabilidad |
|---------|------|----------------|
| `backend/app/api/v1/endpoints/user.py` | Modificar | `sync` devuelve `tutorial_completed`, `is_new_user`, `webito_slots_unlocked` |
| `backend/app/api/v1/endpoints/dev_tools.py` | Crear | `POST /dev/reset-tutorial` — solo en `ENVIRONMENT=development` |
| `frontend/components/PrivyProviderWrapper.tsx` | Modificar | Agregar `apple_oauth` a `loginMethods` |
| `frontend/app/page.tsx` | Modificar | Integrar botones de login directo + redirect post-auth |
| `frontend/app/play/page.tsx` | Modificar | Detectar `is_new_user`/`tutorial_completed`, orquestar flujo |
| `frontend/components/onboarding/WebitoIntroAnimation.tsx` | Crear | Animación de primer contacto: Webito cae del cielo |
| `frontend/components/onboarding/PostTutorialBranch.tsx` | Crear | Pantalla de decisión: pagar vs. F2P |
| `frontend/components/f2p/AwakeAxoSpectator.tsx` | Crear | Axolotito despierto especta + comentarios + CTA |
| `frontend/components/dev/TutorialResetButton.tsx` | Crear | Botón de reset solo en `NODE_ENV=development` |

---

## FASE 1 — Backend: sync devuelve estado de tutorial + dev reset

### Task 1: Ampliar `auth/sync` para devolver estado de onboarding

**Files:**
- Modify: `backend/app/api/v1/endpoints/user.py`

- [ ] **Step 1: Leer el archivo completo antes de editar**

```bash
cat backend/app/api/v1/endpoints/user.py | head -120
```

- [ ] **Step 2: Modificar el return de `sync_user`**

Localiza el bloque `return` al final de `sync_user` (línea ~95) y reemplázalo:

```python
    # Detectar si es usuario nuevo (recién creado en esta llamada)
    is_new_user = mensaje.startswith("¡Bienvenido!")

    # Leer campos de tutorial con getattr para compatibilidad con usuarios pre-migración
    tutorial_completed = getattr(db_user, "tutorial_completed", False)
    webito_slots = getattr(db_user, "webito_slots_unlocked", 1)

    return {
        "mensaje": mensaje,
        "is_new_user": is_new_user,
        "tutorial_completed": tutorial_completed,
        "webito_slots_unlocked": webito_slots,
        "wallet": {
            "axogemas": wallet.axogemas,
            "gemas_alga": wallet.gemas_alga,
            "vip_tier": db_user.vip_tier if db_user.is_vip else None,
            "vip_expires_at": db_user.vip_expires_at.isoformat() if db_user.vip_expires_at else None,
            "vip_days_remaining": days_remaining,
            "vip_pending_gal": db_user.vip_pending_gal if db_user.is_vip else 0.0,
        }
    }
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/user.py
git commit -m "feat(sync): return tutorial_completed, is_new_user, webito_slots_unlocked"
```

---

### Task 2: Endpoint de reset para pruebas de desarrollo

**Files:**
- Create: `backend/app/api/v1/endpoints/dev_tools.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Verificar variable de entorno en `.env`**

```bash
grep "ENVIRONMENT\|ENV=" backend/.env | head -5
```

Si no existe `ENVIRONMENT`, agrégala manualmente al `.env`:
```
ENVIRONMENT=development
```

- [ ] **Step 2: Crear el endpoint de reset**

```python
# backend/app/api/v1/endpoints/dev_tools.py
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.core.auth import get_verified_user_id
from app.models.user import User
from app.models.items import WebitoIncubation
from app.models.axolotito import Axolotito

router = APIRouter()

def _require_dev_env():
    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(
            status_code=403,
            detail="Este endpoint solo está disponible en entorno de desarrollo."
        )

@router.post("/reset-tutorial")
def reset_tutorial(
    delete_axolotito: bool = False,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    """
    Resetea el estado de tutorial del usuario autenticado.
    Solo disponible cuando ENVIRONMENT=development.
    
    Params:
      delete_axolotito: Si True, elimina el Axolotito nacido del tutorial
                        para poder ver la animación de eclosión de nuevo.
    """
    _require_dev_env()

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado.")

    # Reset campos del usuario
    user.tutorial_completed = False
    user.webito_slots_unlocked = 1
    user.f2p_astral_fragments = 0
    user.f2p_daily_gal_earned = 0.0
    user.f2p_daily_gal_reset_at = None
    session.add(user)

    # Reset tutorial_phase de todas las incubaciones activas
    incubations = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
    ).all()
    reset_incubations = 0
    for inc in incubations:
        inc.tutorial_phase = 0
        inc.tutorial_karma = None
        session.add(inc)
        reset_incubations += 1

    # Opcionalmente eliminar el Axolotito nacido del tutorial
    deleted_axo = None
    if delete_axolotito:
        tutorial_axos = session.exec(
            select(Axolotito).where(Axolotito.user_id == user_id)
        ).all()
        for axo in tutorial_axos:
            deleted_axo = axo.name
            session.delete(axo)

    session.commit()

    return {
        "reset": True,
        "user_id": user_id,
        "tutorial_completed": False,
        "webito_slots_unlocked": 1,
        "incubations_reset": reset_incubations,
        "axolotito_deleted": deleted_axo,
        "message": "Tutorial reseteado. Recarga la app para ver el flujo desde el inicio.",
    }

@router.get("/onboarding-state")
def get_onboarding_state(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_verified_user_id),
):
    """Inspecciona el estado actual de onboarding. Solo en development."""
    _require_dev_env()

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado.")

    incubations = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
    ).all()
    axolotitos = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_id)
    ).all()

    return {
        "tutorial_completed": getattr(user, "tutorial_completed", False),
        "webito_slots_unlocked": getattr(user, "webito_slots_unlocked", 1),
        "f2p_fragments": getattr(user, "f2p_astral_fragments", 0),
        "incubations": [
            {
                "id": inc.id,
                "tutorial_phase": getattr(inc, "tutorial_phase", 0),
                "tutorial_karma": getattr(inc, "tutorial_karma", None),
                "calor_actual": inc.calor_actual,
            }
            for inc in incubations
        ],
        "axolotitos": [
            {"id": axo.id, "name": axo.name, "nature": axo.nature}
            for axo in axolotitos
        ],
    }
```

- [ ] **Step 3: Registrar el router en `main.py`**

Lee `backend/app/main.py` y agrega al final del bloque de `include_router`:

```python
# backend/app/main.py — agregar solo si ENVIRONMENT=development
import os as _os
if _os.getenv("ENVIRONMENT", "production") == "development":
    from app.api.v1.endpoints import dev_tools
    app.include_router(dev_tools.router, prefix="/api/v1/dev", tags=["Dev Tools"])
```

- [ ] **Step 4: Probar el endpoint manualmente**

```bash
# Dentro del contenedor con ENVIRONMENT=development
curl -X POST http://localhost:8000/api/v1/dev/reset-tutorial \
  -H "Authorization: Bearer TOKEN"
# Expected: {"reset": true, "tutorial_completed": false, ...}

# Con ENVIRONMENT=production (default)
curl -X POST http://localhost:8000/api/v1/dev/reset-tutorial \
  -H "Authorization: Bearer TOKEN"
# Expected: 403 "Este endpoint solo está disponible en entorno de desarrollo."
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/dev_tools.py backend/app/main.py backend/.env
git commit -m "feat(dev): tutorial reset endpoint gated by ENVIRONMENT=development"
```

---

## FASE 2 — Frontend: Auth en landing + Apple login

### Task 3: Agregar Apple OAuth a Privy

**Files:**
- Modify: `frontend/components/PrivyProviderWrapper.tsx`

- [ ] **Step 1: Leer el archivo**

```bash
cat frontend/components/PrivyProviderWrapper.tsx
```

- [ ] **Step 2: Agregar `apple_oauth` a loginMethods**

```tsx
// frontend/components/PrivyProviderWrapper.tsx
"use client";

import { PrivyProvider } from "@privy-io/react-auth";
import { ToastProvider } from "@/context/ToastContext";

export default function PrivyProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID as string}
      config={{
        loginMethods: ["google", "apple", "email"],
        appearance: {
          theme: "dark",
          accentColor: "#E4007C",
          logo: undefined,
          landingHeader: "Entra a Axolotto",
          loginMessage: "Tu Axolotito te está esperando 🦎",
        },
      }}
    >
      <ToastProvider>
        {children}
      </ToastProvider>
    </PrivyProvider>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/PrivyProviderWrapper.tsx
git commit -m "feat(auth): add Apple OAuth to Privy login methods"
```

---

### Task 4: Login directo en el landing page

**Files:**
- Modify: `frontend/app/page.tsx`

El landing actual termina en un formulario de código. Necesita una sección de login antes del código, y un redirect automático a `/play` tras autenticarse.

- [ ] **Step 1: Leer `page.tsx` completo**

```bash
cat frontend/app/page.tsx
```

- [ ] **Step 2: Agregar lógica de auth + redirect**

Reemplaza `JoinPageInner` para detectar si el usuario ya está autenticado y redirigir:

```tsx
// frontend/app/page.tsx — al inicio del componente JoinPageInner, después de los imports
"use client";

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect } from 'react';
import { usePrivy } from '@privy-io/react-auth';
import CodeRedemption from '@/components/CodeRedemption';

// ... mantener CARDS igual

function JoinPageInner() {
  const searchParams = useSearchParams();
  const codeFromUrl = searchParams.get('code') ?? '';
  const router = useRouter();
  const { ready, authenticated, login } = usePrivy();

  // Si ya está autenticado, ir directo a /play
  useEffect(() => {
    if (ready && authenticated) {
      router.push('/play');
    }
  }, [ready, authenticated, router]);

  // ... resto del JSX igual, pero agrega esta sección ANTES del "Code Redemption CTA":
```

- [ ] **Step 3: Agregar sección de login al JSX**

Inserta esta sección después del bloque `{/* Colecciones Preview */}` y antes de `{/* Code Redemption CTA */}`:

```tsx
      {/* LOGIN CTA */}
      <section className="py-16 px-6 max-w-md mx-auto text-center">
        <div className="bg-gradient-to-br from-[#E4007C]/10 to-purple-900/10 border border-[#E4007C]/30 rounded-3xl p-8">
          <div className="text-6xl mb-4">🦎</div>
          <h2 className="text-3xl font-black mb-2">¿Listo para jugar?</h2>
          <p className="text-gray-400 text-sm mb-6">
            Entra con tu cuenta y te asignamos un Webito. El tutorial es gratis — solo pagas cuando quieras jugar de verdad.
          </p>
          <button
            onClick={login}
            disabled={!ready}
            className="w-full py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-lg shadow-[0_0_40px_rgba(228,0,124,0.4)] transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {ready ? '¡Jugar gratis! →' : 'Cargando...'}
          </button>
          <p className="text-gray-600 text-xs mt-4">
            Google · Apple · Email — sin wallet requerida
          </p>
        </div>
      </section>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat(landing): add direct login CTA + redirect to /play when authenticated"
```

---

## FASE 3 — Frontend: Animación de primer contacto

### Task 5: `WebitoIntroAnimation` — El Webito cae del cielo

**Files:**
- Create: `frontend/components/onboarding/WebitoIntroAnimation.tsx`
- Modify: `frontend/app/globals.css`

Esta animación ocurre UNA sola vez en la vida del jugador, justo después de autenticarse por primera vez. El Webito "cae" desde arriba de la pantalla, rebota, y luego habla.

- [ ] **Step 1: Agregar keyframes en globals.css**

```css
/* frontend/app/globals.css — agregar al final */

/* Webito cae del cielo */
@keyframes webito-fall {
  0%   { transform: translateY(-200px) rotate(-15deg); opacity: 0; }
  60%  { transform: translateY(20px)   rotate(5deg);   opacity: 1; }
  75%  { transform: translateY(-10px)  rotate(-3deg);  }
  85%  { transform: translateY(8px)    rotate(2deg);   }
  100% { transform: translateY(0px)    rotate(0deg);   opacity: 1; }
}
.animate-webito-fall {
  animation: webito-fall 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

/* Polvo de impacto */
@keyframes dust-burst {
  0%   { transform: scale(0); opacity: 0.7; }
  100% { transform: scale(2.5); opacity: 0; }
}
.animate-dust-burst {
  animation: dust-burst 0.5s ease-out forwards;
}

/* Webito flota suavemente */
@keyframes webito-float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-8px); }
}
.animate-webito-float {
  animation: webito-float 2.5s ease-in-out infinite;
}
```

- [ ] **Step 2: Crear el componente**

```tsx
// frontend/components/onboarding/WebitoIntroAnimation.tsx
"use client"
import { useState, useEffect } from "react"
import WebitoDialogue from "@/components/tutorial/WebitoDialogue"

interface Props {
  onComplete: () => void
}

const INTRO_SEQUENCE = [
  {
    text: "¡AY! ¡Me caí! Perdón perdón... llevo semanas dentro de este cascarón y finalmente escuché que tú llegaste.",
    delay: 1200,
  },
  {
    text: "Soy un Webito. Un axolotito que todavía no nace. Y te elegí a ti para que seas mi jugador.",
    delay: 0,
  },
  {
    text: "Aquí afuera hay un juego llamado Lotería. ¡Y yo NECESITO jugar! ¿Me ayudas? ¿Me llevas a una mesa?",
    delay: 0,
  },
]

type AnimPhase = "falling" | "landing" | "floating" | "talking" | "done"

export default function WebitoIntroAnimation({ onComplete }: Props) {
  const [phase, setPhase] = useState<AnimPhase>("falling")
  const [dialogueIndex, setDialogueIndex] = useState(-1)
  const [showDust, setShowDust] = useState(false)

  // Secuencia de animación
  useEffect(() => {
    const t1 = setTimeout(() => {
      setPhase("landing")
      setShowDust(true)
    }, 900)
    const t2 = setTimeout(() => {
      setShowDust(false)
      setPhase("floating")
    }, 1400)
    const t3 = setTimeout(() => {
      setPhase("talking")
      setDialogueIndex(0)
    }, 1800)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [])

  const handleDialogueDismiss = () => {
    const next = dialogueIndex + 1
    if (next < INTRO_SEQUENCE.length) {
      setDialogueIndex(next)
    } else {
      setPhase("done")
      onComplete()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ background: "radial-gradient(ellipse at center, #0d1b2a 0%, #020408 100%)" }}
    >
      {/* Estrellas de fondo — puntos estáticos */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {Array.from({ length: 40 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              width: Math.random() * 2 + 1 + "px",
              height: Math.random() * 2 + 1 + "px",
              top: Math.random() * 100 + "%",
              left: Math.random() * 100 + "%",
              opacity: Math.random() * 0.5 + 0.1,
            }}
          />
        ))}
      </div>

      {/* El Webito */}
      <div className="relative flex flex-col items-center" style={{ marginTop: "-80px" }}>
        <div
          className={
            phase === "falling"
              ? "animate-webito-fall"
              : phase === "floating" || phase === "talking" || phase === "done"
              ? "animate-webito-float"
              : ""
          }
          style={{ fontSize: "96px", lineHeight: 1, userSelect: "none" }}
        >
          🥚
        </div>

        {/* Nube de polvo al aterrizar */}
        {showDust && (
          <div
            className="absolute bottom-0 animate-dust-burst"
            style={{
              width: "80px",
              height: "20px",
              background: "radial-gradient(ellipse, rgba(255,255,255,0.3) 0%, transparent 70%)",
              borderRadius: "50%",
            }}
          />
        )}
      </div>

      {/* Texto de fase antes del diálogo */}
      {phase === "falling" && (
        <p className="mt-8 text-gray-500 text-sm animate-pulse">
          algo viene del cielo...
        </p>
      )}

      {/* Diálogos */}
      {phase === "talking" && dialogueIndex >= 0 && dialogueIndex < INTRO_SEQUENCE.length && (
        <WebitoDialogue
          text={INTRO_SEQUENCE[dialogueIndex].text}
          speaker="webito"
          onDismiss={handleDialogueDismiss}
          autoHideMs={INTRO_SEQUENCE[dialogueIndex].delay || undefined}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/onboarding/WebitoIntroAnimation.tsx frontend/app/globals.css
git commit -m "feat(onboarding): WebitoIntroAnimation — webito falls from sky on first login"
```

---

## FASE 4 — Post-Tutorial Branch

### Task 6: `PostTutorialBranch` — La decisión de monetización

**Files:**
- Create: `frontend/components/onboarding/PostTutorialBranch.tsx`

Esta pantalla aparece exactamente una vez: justo después de que el tutorial termina (eclosión completa). Presenta la división premium / F2P de forma narrativa, no como un paywall frío.

El Axolotito recién nacido habla. No dice "compra tokens". Dice que tiene hambre de competir.

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/onboarding/PostTutorialBranch.tsx
"use client"
import { useState } from "react"

interface Props {
  axoName: string
  karma: "lucky" | "salty"
  onPayAndPlay: () => void   // → ir a la tienda/banco
  onPlayFree: () => void     // → modo F2P espectador
}

const AXO_DIALOGUE_BY_KARMA = {
  lucky: "¡Estoy listo para las ligas mayores! Siento la suerte corriendo por mis branquias. ¡Necesito entrar a una sala real AHORA!",
  salty: "Okay, el agua estuvo salada en el tutorial... pero eso fue entrenamiento. En una partida real voy a demostrar quién soy.",
}

export default function PostTutorialBranch({ axoName, karma, onPayAndPlay, onPlayFree }: Props) {
  const [chosen, setChosen] = useState<"premium" | "free" | null>(null)

  const handlePremium = () => {
    setChosen("premium")
    setTimeout(onPayAndPlay, 600)
  }
  const handleFree = () => {
    setChosen("free")
    setTimeout(onPlayFree, 600)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center px-6"
      style={{ background: "radial-gradient(ellipse at center, #0a0f1a 0%, #020408 100%)" }}
    >
      {/* Axolotito */}
      <div className="text-8xl mb-2 animate-webito-float">🦎</div>
      <p
        className="text-sm font-black tracking-widest mb-1"
        style={{ color: karma === "lucky" ? "#FBBF24" : "#60A5FA" }}
      >
        {axoName.toUpperCase()}
      </p>

      {/* Diálogo del Axo */}
      <div className="max-w-sm w-full bg-black/60 border border-cyan-500/30 rounded-2xl p-5 mb-8 text-center">
        <p className="text-sm text-cyan-100 italic leading-relaxed">
          "{AXO_DIALOGUE_BY_KARMA[karma]}"
        </p>
      </div>

      {/* Las dos opciones */}
      <div className="max-w-sm w-full space-y-4">
        {/* Opción premium */}
        <button
          onClick={handlePremium}
          disabled={chosen !== null}
          className="w-full py-5 rounded-2xl font-black text-lg transition-all transform hover:scale-105 active:scale-95 disabled:opacity-60"
          style={{
            background: chosen === "premium"
              ? "linear-gradient(135deg, #FBBF24, #F59E0B)"
              : "linear-gradient(135deg, #E4007C, #B30062)",
            boxShadow: "0 0 30px rgba(228,0,124,0.4)",
          }}
        >
          💎 ¡Que juegue de verdad!
          <span className="block text-xs font-normal opacity-80 mt-0.5">
            Compra GAL → acceso completo al juego
          </span>
        </button>

        {/* Opción F2P */}
        <button
          onClick={handleFree}
          disabled={chosen !== null}
          className="w-full py-4 rounded-2xl font-black text-base border border-white/10 hover:border-white/30 transition-all transform hover:scale-102 active:scale-98 disabled:opacity-60"
          style={{ background: "rgba(255,255,255,0.04)" }}
        >
          👁️ Primero quiero ver cómo se juega
          <span className="block text-xs font-normal text-gray-400 mt-0.5">
            Entra gratis · tu Axolotito especta partidas reales
          </span>
        </button>
      </div>

      <p className="text-gray-600 text-xs mt-6 text-center max-w-xs">
        Puedes cambiar de modo cuando quieras desde el menú principal.
      </p>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/onboarding/PostTutorialBranch.tsx
git commit -m "feat(onboarding): PostTutorialBranch — pay vs F2P decision screen with axo dialogue"
```

---

## FASE 5 — F2P con Axolotito Despierto

### Task 7: `AwakeAxoSpectator` — El Axolotito vivo que no puede jugar (aún)

**Files:**
- Create: `frontend/components/f2p/AwakeAxoSpectator.tsx`

Este componente reemplaza al `SleepingEgg` para usuarios que **ya completaron el tutorial** pero no tienen GAL. Su Axolotito está vivo, los acompaña mientras espectan, y comenta las partidas usando el `DialogueEngine`.

La narrativa: tu Axolotito está frustrado/emocionado viendo partidas desde las gradas. Cada partida que espéctas le genera micro-recompensas y fragmentos hacia el modo "Armar el Webito" (cosmetics ganados F2P).

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/f2p/AwakeAxoSpectator.tsx
"use client"
import { useState, useEffect, useCallback } from "react"
import { usePrivy } from "@privy-io/react-auth"
import WebitoDialogue from "@/components/tutorial/WebitoDialogue"

interface Axolotito {
  id: number
  name: string
  nature?: string
  stat_luck?: number
  stat_salinity?: number
}

interface Props {
  axolotito: Axolotito
  isWatchingGame: boolean        // true mientras el usuario está en la vista espectador
  gameResult?: "win" | "lose" | null
  onBuyGal: () => void            // → redirige a tienda/banco
}

// Comentarios del Axo mientras especta (no necesita API, hardcoded para F2P)
const SPECTATOR_COMMENTS: Record<string, string[]> = {
  watching: [
    "Yo podría hacer eso. Fácil. Denme una mesa.",
    "¿Ves esa tabla? Yo la llenaría en la mitad de tiempo.",
    "¡¡El Gritón cantó EL AXOLOTITO!! ¡Esa carta me pertenece a mí!",
    "Si tuviera GAL ahorita mismo, estaría ganando. Te lo juro.",
    "Las cartas de ese jugador son de las buenas. Yo merezco esas cartas.",
    "¡Anda, canta La Sirena! ¡La Sirena! ¡LA SIRENA!",
  ],
  win_witnessed: [
    "¡YO SABÍA QUE IBA A GANAR! Bueno, no, no sabía. Pero me alegra.",
    "¡Lotería! ¡Lotería! ...ojalá fuera yo.",
    "Ese jugador ganó bien chido. Yo también quiero ganar chido.",
  ],
  lose_witnessed: [
    "Le faltó un poco de suerte. A mí no me faltaría, yo tengo aura.",
    "Pobre. Hubiera necesitado menos salinidad. Yo ya sé cómo funciona.",
    "La sal. Siempre la sal. Ya sé por qué perdió.",
  ],
  idle: [
    "¿Cuándo jugamos de verdad?",
    "Tengo las branquias listas. Y los reflejos también.",
    "Sigo aquí. Por si me necesitas. Para jugar. Eso.",
  ],
}

const getRandom = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)]

export default function AwakeAxoSpectator({ axolotito, isWatchingGame, gameResult, onBuyGal }: Props) {
  const { getAccessToken } = usePrivy()
  const [currentComment, setCurrentComment] = useState("")
  const [fragmentsToday, setFragmentsToday] = useState(0)
  const [galToday, setGalToday] = useState(0)
  const [capped, setCapped] = useState(false)
  const [showComment, setShowComment] = useState(false)

  // Comentario aleatorio cada vez que el estado cambia
  useEffect(() => {
    let comment = ""
    if (gameResult === "win") comment = getRandom(SPECTATOR_COMMENTS.win_witnessed)
    else if (gameResult === "lose") comment = getRandom(SPECTATOR_COMMENTS.lose_witnessed)
    else if (isWatchingGame) comment = getRandom(SPECTATOR_COMMENTS.watching)
    else comment = getRandom(SPECTATOR_COMMENTS.idle)

    if (comment) {
      setCurrentComment(comment)
      setShowComment(true)
    }
  }, [isWatchingGame, gameResult])

  // Acreditar recompensa F2P cuando termina una partida espectada
  const claimWatchReward = useCallback(async (won: boolean) => {
    try {
      const token = await getAccessToken()
      const res = await fetch(`/api/v1/f2p/watch-reward?won=${won}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return
      const data = await res.json()
      if (data.capped) {
        setCapped(true)
      } else {
        setFragmentsToday(prev => prev + (data.fragments_added ?? 0))
        setGalToday(prev => prev + (data.gal_earned ?? 0))
      }
    } catch (e) {
      console.error("watch-reward failed", e)
    }
  }, [getAccessToken])

  useEffect(() => {
    if (gameResult === "win") claimWatchReward(true)
    else if (gameResult === "lose") claimWatchReward(false)
  }, [gameResult, claimWatchReward])

  return (
    <div className="relative">
      {/* Card del Axolotito */}
      <div
        className="bg-black/40 border border-cyan-500/20 rounded-2xl p-4 text-center"
        style={{ boxShadow: "0 0 20px rgba(0,229,255,0.05)" }}
      >
        <div className="text-5xl mb-2 animate-webito-float">🦎</div>
        <p className="font-black text-sm text-cyan-300">{axolotito.name}</p>
        {axolotito.nature && (
          <p className="text-xs text-gray-500 mt-0.5 capitalize">{axolotito.nature}</p>
        )}

        {/* Micro-stats del día */}
        <div className="flex justify-center gap-4 mt-3">
          <div className="text-center">
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">GAL hoy</p>
            <p className="text-sm font-black text-emerald-400">+{galToday.toFixed(1)}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Fragmentos</p>
            <p className="text-sm font-black text-purple-400">+{fragmentsToday}</p>
          </div>
        </div>

        {/* Cap alcanzado */}
        {capped && (
          <p className="text-[10px] text-yellow-500 mt-2 px-2">
            Límite diario alcanzado. Vuelve mañana o compra GAL para jugar sin límite.
          </p>
        )}

        {/* CTA */}
        <button
          onClick={onBuyGal}
          className="mt-4 w-full py-3 rounded-xl font-black text-sm transition-all hover:scale-105 active:scale-95"
          style={{
            background: "linear-gradient(135deg, #E4007C22, #B3006222)",
            border: "1px solid #E4007C44",
            color: "#FF8DA1",
          }}
        >
          💎 Comprar GAL — que juegue de verdad
        </button>
      </div>

      {/* Comentario del Axo */}
      {showComment && currentComment && (
        <WebitoDialogue
          text={currentComment}
          speaker="axo"
          onDismiss={() => setShowComment(false)}
          autoHideMs={5000}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/f2p/AwakeAxoSpectator.tsx
git commit -m "feat(f2p): AwakeAxoSpectator — born axolotito spectates games and earns micro-rewards"
```

---

## FASE 6 — Orquestación en `/play`

### Task 8: Integrar todo el flujo en `play/page.tsx`

**Files:**
- Modify: `frontend/app/play/page.tsx`

Este es el cambio más delicado porque toca la página principal. Lee el archivo completo antes de modificar.

- [ ] **Step 1: Leer el archivo**

```bash
wc -l frontend/app/play/page.tsx
cat frontend/app/play/page.tsx
```

- [ ] **Step 2: Agregar estado de onboarding al componente principal**

Dentro del componente principal (la función que tiene los `usePrivy()` hooks), agrega:

```tsx
// Tipos
type OnboardingPhase =
  | "loading"        // esperando sync
  | "intro"          // WebitoIntroAnimation (primera vez)
  | "tutorial"       // TutorialFlow activo
  | "branch"         // PostTutorialBranch (decisión)
  | "done"           // flujo completo, mostrar tabs normales

// Estado
const [onboardingPhase, setOnboardingPhase] = useState<OnboardingPhase>("loading")
const [syncData, setSyncData] = useState<{
  is_new_user: boolean
  tutorial_completed: boolean
  webito_slots_unlocked: number
} | null>(null)
const [tutorialKarma, setTutorialKarma] = useState<"lucky" | "salty">("lucky")
const [tutorialAxoName, setTutorialAxoName] = useState("Axolotito Bebé")
```

- [ ] **Step 3: Modificar `sincronizarConBackend` para leer el nuevo campo**

En el efecto existente que llama a `auth/sync`, después de `setDatosBanco(datos.wallet)`, agregar:

```tsx
// Guardar datos de onboarding
const newSyncData = {
  is_new_user: datos.is_new_user ?? false,
  tutorial_completed: datos.tutorial_completed ?? false,
  webito_slots_unlocked: datos.webito_slots_unlocked ?? 1,
}
setSyncData(newSyncData)

// Decidir fase de onboarding
if (newSyncData.is_new_user) {
  setOnboardingPhase("intro")
} else if (!newSyncData.tutorial_completed) {
  setOnboardingPhase("tutorial")
} else {
  setOnboardingPhase("done")
}
```

- [ ] **Step 4: Agregar renders condicionales antes del `return` principal de tabs**

Justo antes del bloque que renderiza las tabs (donde está `tabActiva`), agregar:

```tsx
// ─── Onboarding flow ─────────────────────────────────────────────────────────
if (!ready) {
  // ya existía el loader
}

if (authenticated && onboardingPhase === "loading") {
  return (
    <div className="world-bg flex h-screen items-center justify-center">
      <div className="text-gray-500 animate-pulse text-sm">Sincronizando...</div>
    </div>
  )
}

if (authenticated && onboardingPhase === "intro") {
  return (
    <WebitoIntroAnimation
      onComplete={() => setOnboardingPhase("tutorial")}
    />
  )
}

if (authenticated && onboardingPhase === "tutorial") {
  // Para el tutorial necesitamos los datos del juego.
  // Reutilizamos los mismos datos que el modo de juego ya carga.
  // Por ahora redirigimos a la tab santuario con el tutorial activo.
  // La integración completa del TutorialFlow requiere
  // que Santuario/Criadero lo detecte (ver nota de integración abajo).
  return (
    <div className="world-bg min-h-screen">
      <TutorialFlow
        userId={user?.id ?? ""}
        token={accessToken}
        bonusFocus={50}
        bonusLuck={50}
        bonusAgility={50}
        bonusStamina={100}
        bonusSalinity={30}
        inferredNature="lucky"
        selectedAxo={{ id: 0, name: "Webito", cpu_win_streak: 0 }}
        selectedBoardId={0}
        playerBoards={[]}
        allCards={[]}
        onComplete={() => {
          setOnboardingPhase("branch")
        }}
      />
    </div>
  )
}

if (authenticated && onboardingPhase === "branch") {
  return (
    <PostTutorialBranch
      axoName={tutorialAxoName}
      karma={tutorialKarma}
      onPayAndPlay={() => {
        setOnboardingPhase("done")
        setTabActiva("tienda")
      }}
      onPlayFree={() => {
        setOnboardingPhase("done")
        setTabActiva("jugar")
      }}
    />
  )
}
// ─────────────────────────────────────────────────────────────────────────────
```

- [ ] **Step 5: Agregar imports en la parte superior del archivo**

```tsx
import WebitoIntroAnimation from "@/components/onboarding/WebitoIntroAnimation"
import PostTutorialBranch from "@/components/onboarding/PostTutorialBranch"
import { TutorialFlow } from "@/components/tutorial/TutorialFlow"
```

- [ ] **Step 6: Commit**

```bash
git add frontend/app/play/page.tsx
git commit -m "feat(play): orchestrate onboarding phases — intro → tutorial → branch → game"
```

---

## FASE 7 — Dev Reset Button en la UI

### Task 9: Botón de reset visible solo en desarrollo

**Files:**
- Create: `frontend/components/dev/TutorialResetButton.tsx`

- [ ] **Step 1: Crear el componente**

```tsx
// frontend/components/dev/TutorialResetButton.tsx
"use client"
import { useState } from "react"
import { usePrivy } from "@privy-io/react-auth"

interface Props {
  onReset: () => void   // padre recarga el estado de onboarding
}

export default function TutorialResetButton({ onReset }: Props) {
  // Solo render en development
  if (process.env.NODE_ENV !== "development") return null

  const { getAccessToken } = usePrivy()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [deleteAxo, setDeleteAxo] = useState(false)

  const handleReset = async () => {
    setLoading(true)
    setResult(null)
    try {
      const token = await getAccessToken()
      const res = await fetch(
        `https://api.axolot.to/api/v1/dev/reset-tutorial?delete_axolotito=${deleteAxo}`,
        { method: "POST", headers: { Authorization: `Bearer ${token}` } }
      )
      const data = await res.json()
      if (res.ok) {
        setResult(`✅ ${data.message}`)
        setTimeout(() => {
          onReset()   // el padre fuerza re-sync
        }, 1500)
      } else {
        setResult(`❌ ${data.detail}`)
      }
    } catch (e) {
      setResult("❌ Error de red")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        position: "fixed",
        bottom: "80px",
        right: "16px",
        zIndex: 9999,
        background: "#1a0a0a",
        border: "1px solid #7f1d1d",
        borderRadius: "12px",
        padding: "10px 14px",
        fontSize: "11px",
        color: "#fca5a5",
        maxWidth: "220px",
      }}
    >
      <p className="font-black text-xs mb-2 text-red-400">🛠️ DEV — Reset Tutorial</p>

      <label style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px", cursor: "pointer" }}>
        <input
          type="checkbox"
          checked={deleteAxo}
          onChange={e => setDeleteAxo(e.target.checked)}
        />
        <span>Eliminar Axolotito nacido</span>
      </label>

      <button
        onClick={handleReset}
        disabled={loading}
        style={{
          width: "100%",
          padding: "6px",
          background: loading ? "#450a0a" : "#7f1d1d",
          border: "none",
          borderRadius: "6px",
          color: "#fca5a5",
          fontWeight: "bold",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Reseteando..." : "🔄 Resetear"}
      </button>

      {result && (
        <p style={{ marginTop: "6px", fontSize: "10px", lineHeight: 1.4 }}>{result}</p>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Agregar en `play/page.tsx` al final del JSX principal**

Después del cierre del tab de juego, antes del `</div>` raíz:

```tsx
{/* Dev tools — solo en development */}
{process.env.NODE_ENV === "development" && (
  <TutorialResetButton
    onReset={() => {
      // Fuerza re-sincronización y vuelve al estado loading
      setOnboardingPhase("loading")
      setSyncData(null)
      // El useEffect de auth detectará el cambio y re-sincronizará
    }}
  />
)}
```

- [ ] **Step 3: Agregar import**

```tsx
import TutorialResetButton from "@/components/dev/TutorialResetButton"
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/dev/TutorialResetButton.tsx frontend/app/play/page.tsx
git commit -m "feat(dev): TutorialResetButton — one-click tutorial reset visible only in NODE_ENV=development"
```

---

## Self-Review

### Spec coverage

| Requerimiento | Task |
|--------------|------|
| Landing con código promocional | Ya existe `CodeRedemption`. Task 4 agrega login directo |
| Login con Google | Ya existe en Privy |
| Login con Apple | Task 3 |
| Otro método común (email) | Ya existe en Privy |
| Animación primer contacto con Webito | Task 5 (`WebitoIntroAnimation`) |
| Historia del Webito que quiere jugar | Task 5 (diálogos de intro) |
| Tutorial (3 partidas) | Ya construido en `TutorialFlow` |
| Branch al final: paga / F2P | Task 6 (`PostTutorialBranch`) |
| F2P: modo espectador con Axolotito despierto | Task 7 (`AwakeAxoSpectator`) |
| F2P: narrative shift post-tutorial | Task 7 (Axolotito vivo comenta partidas, no huevo dormido) |
| Resetear estado para testing | Task 2 (backend) + Task 9 (frontend button) |
| `auth/sync` devuelve `tutorial_completed` | Task 1 |
| Orquestación completa en `/play` | Task 8 |

### Notas de integración pendientes

**TutorialFlow en Task 8 usa datos dummy por ahora** — los props `selectedAxo`, `playerBoards`, `allCards` necesitan datos reales del backend para que `CpuSimScreen` funcione dentro del tutorial. La integración completa requiere que `/play` cargue los datos del juego antes de mostrar `TutorialFlow`. Ese fetch ya ocurre en los componentes hijos (`PlayMode`, `Santuario`) pero no a nivel de `page.tsx`. Opciones:

1. Hacer el fetch en `page.tsx` antes de mostrar el tutorial (recomendado a largo plazo)
2. Que `TutorialFlow` haga sus propios fetches internamente (más simple a corto plazo)

La Task 8 implementa la opción 2 con datos dummy como punto de partida. La integración con datos reales es el siguiente paso una vez que el flujo esté visible.

**`AwakeAxoSpectator` necesita ser colocado** dentro de la tab de juego (`PlayMode` o `Santuario`) para los usuarios F2P post-tutorial. El componente existe pero el padre aún no lo detecta.

---

## Orden de ejecución recomendado

```
Agente A (backend):  Task 1 → Task 2
Agente B (frontend): Task 3 → Task 4 → Task 5 → Task 6 → Task 7
Agente C (frontend): Task 8 → Task 9 (depende de Tasks 5, 6, 7)
```

Agente B y Agente A pueden trabajar en paralelo desde el inicio.
Agente C espera que Agente B termine Tasks 5, 6 y 7 para tener los componentes disponibles.
