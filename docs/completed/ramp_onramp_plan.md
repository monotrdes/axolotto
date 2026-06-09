# Plan: On-Ramp USDT0 en Plasma → Wallet Privy

> Documento técnico. Objetivo: que el jugador pueda comprar USDT0 con tarjeta, SPEI u OXXO,
> y recibirlo directamente en su wallet de Privy, para luego pagar AXG con un clic.
>
> Versión: 2026-05-26 | Privy v3.19.0 | Stack: Next.js · viem · @privy-io/react-auth

---

## TL;DR — Qué falta y qué necesito de ti

Antes de escribir una sola línea de código, necesito que me proporciones:

| # | Dato | ¿Dónde encontrarlo? | Estado |
|---|------|---------------------|--------|
| 1 | **Plasma mainnet Chain ID** (número) | Docs oficiales Plasma / plasmascan.to | ❌ Falta |
| 2 | **Plasma mainnet RPC URL** | Docs Plasma | ❌ Falta |
| 3 | **Dirección contrato USDT0 en Plasma** | Docs Plasma / explorers | ❌ Falta |
| 4 | **Dirección contrato USDC en Plasma** (si existe) | Docs Plasma | ❌ Falta |
| 5 | **Ramp API key** | [app.ramp.network](https://app.ramp.network) → API Keys | ⏳ En proceso (7 días) |
| 6 | **MoonPay publishable key sandbox** (`pk_test_...`) | dashboard.moonpay.com → API Keys | ✅ Tienes — pegar en `.env.local` |
| 7 | **MoonPay secret key sandbox** (`sk_test_...`) | dashboard.moonpay.com → API Keys | 🔲 Solo para prod (firma URL) |
| 8 | **Privy App ID** | ya en `.env.local` ✅ | ✅ Listo |

Con esos 5 datos obligatorios (1-3-4-5) la implementación completa toma ~3h.

---

## Contexto: codebase actual

```
frontend/
  lib/blockchain.ts          → define publicClient, usa anvil (chainId 31337)
  components/PrivyProviderWrapper.tsx  → Privy con loginMethods=[google,email], sin chain config
  components/CryptoCheckout.tsx        → checkout AXG, tiene botón Privy pay y guía Binance

backend/
  .env  → BLOCKCHAIN_MODE=local, USDC_ADDRESS vacío
  app/services/web3_service.py  → verify_usdc_payment usa settings.USDC_ADDRESS
```

**Hoy la app corre contra Anvil local (chainId 31337).** Para producción necesitamos migrar al Chain ID real de Plasma.

---

## Arquitectura: 3 capas de funding

```
                     ┌────────────────────────────────────┐
                     │     Jugador quiere recargar AXG    │
                     └────────────┬───────────────────────┘
                                  │
              ┌───────────────────┼──────────────────────┐
              ▼                   ▼                       ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │  Ruta A (ya hecho)│ │   Ruta B (ya hecho│ │  Ruta C ← ESTO  │
    │  Wallet Privy     │ │   Guía Binance    │ │  Comprar cripto  │
    │  tiene USDT0      │ │   CEX → Privy     │ │  con tarjeta /   │
    │  → paga 1-tap     │ │   → paga 1-tap    │ │  SPEI / OXXO     │
    └──────────────────┘ └──────────────────┘ └────────┬─────────┘
                                                        │
                                    ┌───────────────────┴───────┐
                                    │ Ramp SDK  (recomendado)   │
                                    │ MoonPay via Privy         │
                                    └───────────────────────────┘
                                    Deposita USDT0 en wallet Privy
                                    → jugador usa botón Pagar ✅
```

---

## Opción A — Ramp Network (recomendada para MX)

### Por qué Ramp

- Acepta **SPEI y OXXO** (pagos en MXN sin tarjeta de crédito)
- Anunció soporte de USDT en Plasma en abril 2026
- Comisiones ~1-2% (vs MoonPay ~4%)
- KYC light: email + selfie, sin documentos para montos bajos
- SDK sencillo: 5 líneas de código

### Cómo funciona

```
[Jugador] → toca "Comprar USDT con SPEI/tarjeta"
    ↓
[Ramp modal] → jugador paga MXN con OXXO, SPEI, o tarjeta
    ↓
[Ramp deposita USDT0] → wallet Privy del jugador (directo on-chain)
    ↓
[Jugador vuelve a Axolotto] → toca "Pagar con mi wallet" → AXG acreditados
```

### Instalación

```bash
cd /home/monotr/axolotto/frontend
npm install @ramp-network/ramp-instant-sdk
```

### Código — Hook `useRampFunding`

Crear `frontend/hooks/useRampFunding.ts`:

```typescript
'use client';
import { RampInstantSDK } from '@ramp-network/ramp-instant-sdk';
import { useWallets } from '@privy-io/react-auth';

const RAMP_API_KEY = process.env.NEXT_PUBLIC_RAMP_API_KEY ?? '';

// ❗ Completar con los datos reales de Plasma
const PLASMA_CHAIN_ID  = Number(process.env.NEXT_PUBLIC_CHAIN_ID);   // ej. 12345
const USDT0_ADDRESS    = process.env.NEXT_PUBLIC_USDT0_ADDRESS ?? ''; // contrato USDT0 en Plasma
// Ramp asset code para USDT0 en Plasma — verificar en docs.ramp.network/assets
// Formato típico: "PLASMA_USDT0" o similar
const RAMP_ASSET_CODE  = process.env.NEXT_PUBLIC_RAMP_ASSET_CODE ?? 'PLASMA_USDT0';

interface UseRampFundingOptions {
  amountUsd?: number;
}

export function useRampFunding() {
  const { wallets } = useWallets();

  const openRamp = ({ amountUsd }: UseRampFundingOptions = {}) => {
    const embeddedWallet = wallets.find(w => w.walletClientType === 'privy');
    if (!embeddedWallet) {
      console.error('No embedded Privy wallet found');
      return;
    }

    new RampInstantSDK({
      hostApiKey:     RAMP_API_KEY,
      hostAppName:    'Axolotto',
      hostLogoUrl:    'https://axolot.to/logo.png',
      swapAsset:      RAMP_ASSET_CODE,      // USDT0 en Plasma
      userAddress:    embeddedWallet.address, // wallet Privy del jugador
      swapAmount:     amountUsd ? String(amountUsd * 1_000_000) : undefined, // micro-USDT
      fiatCurrency:   'MXN',               // moneda default
      fiatValue:      amountUsd ? String(amountUsd * 17.5) : undefined, // MXN estimado
      // Sandbox/prod se controla con el API key — sandbox keys tienen "_test_"
    }).show();
  };

  return { openRamp };
}
```

### Integrar en `CryptoCheckout.tsx` (pantalla `method`)

```tsx
import { useRampFunding } from '@/hooks/useRampFunding';

// Dentro del componente:
const { openRamp } = useRampFunding();

// En renderMethod(), después del resumen de precios:
<div className="flex items-center gap-3 my-2">
  <div className="flex-1 h-px bg-white/8" />
  <span className="text-[9px] text-slate-600 uppercase font-bold">o compra USDT primero</span>
  <div className="flex-1 h-px bg-white/8" />
</div>

<button
  onClick={() => openRamp({ amountUsd: selectedPack?.usd })}
  className="w-full py-3 rounded-2xl border border-yellow-500/30 bg-yellow-950/20 flex items-center justify-between px-4 transition-all hover:bg-yellow-950/40 active:scale-95"
>
  <div className="flex items-center gap-2">
    <span className="text-lg">💳</span>
    <div className="text-left">
      <div className="text-[11px] font-black text-yellow-400 uppercase">Comprar con SPEI / OXXO / Tarjeta</div>
      <div className="text-[9px] text-slate-500">Ramp Network · USDT en Plasma · ~1% comisión</div>
    </div>
  </div>
  <span className="text-yellow-400 text-xs">→</span>
</button>

<p className="text-[9px] text-slate-600 text-center mt-1">
  Ramp deposita USDT en tu wallet. Después regresa y presiona "Iniciar compra".
</p>
```

---

## Opción B — MoonPay Widget standalone (implementado ✅, funciona en sandbox hoy)

### Por qué NO usar `useFundWallet` de Privy con MoonPay

Analisis del bundle compilado de Privy v3.19.0 reveló que:
- Privy tiene sus propias API keys de MoonPay hardcodeadas internamente
- Internamente hace `isSupportedChainIdForMoonpay(chainId)` con lista fija:
  ethereum, base, optimism, polygon, arbitrum, avalanche, monad
- **Plasma no está en la lista** → `useFundWallet` con MoonPay no muestra el botón para Plasma
- La API key del dashboard de Privy se usa en su backend para firmar URLs — no hay forma de inyectar una chain custom

### Solución: Widget standalone con publishable key

Usamos el widget de MoonPay directamente (popup) con nuestra propia publishable key.
En sandbox no se requiere firma de URL (entorno permisivo).

**Archivos implementados:**
- `frontend/hooks/useMoonPayWidget.ts` — hook que abre el popup
- `frontend/components/CryptoCheckout.tsx` — botón "Comprar con tarjeta / SPEI"
- `frontend/.env.local` — variables `NEXT_PUBLIC_MOONPAY_PK`, `NEXT_PUBLIC_MOONPAY_SANDBOX`, `NEXT_PUBLIC_MOONPAY_CURRENCY`

### Para activar en sandbox HOY

```bash
# frontend/.env.local — agregar:
NEXT_PUBLIC_MOONPAY_PK=pk_test_TU_PUBLISHABLE_KEY_AQUI
NEXT_PUBLIC_MOONPAY_SANDBOX=true
NEXT_PUBLIC_MOONPAY_CURRENCY=usdc_base   # para probar el widget; Plasma: cambiar cuando MoonPay lo soporte
```

El botón "Comprar con tarjeta / SPEI" en la pantalla de método de pago aparece automáticamente cuando `NEXT_PUBLIC_MOONPAY_PK` está configurado.

### Para producción — firma de URL en el backend

En producción, MoonPay requiere que la URL sea firmada con HMAC-SHA256 usando la secret key.
Agregar endpoint en FastAPI:

```python
# backend/app/api/v1/endpoints/checkout.py — agregar al final
import hmac, hashlib, base64
from urllib.parse import urlparse

@router.get("/moonpay-sign")
async def sign_moonpay_url(
    url: str,
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Firma una URL de MoonPay con la secret key (solo para llamadas autenticadas)."""
    secret = settings.MOONPAY_SECRET_KEY  # sk_live_... en backend .env
    parsed = urlparse(url)
    query = parsed.query
    signature = base64.b64encode(
        hmac.new(secret.encode(), query.encode(), hashlib.sha256).digest()
    ).decode()
    return {"signed_url": f"{url}&signature={signature}"}
```

```python
# backend/app/core/config.py — agregar
MOONPAY_SECRET_KEY: str = ""  # sk_live_... NUNCA exponer al frontend
```

Y en el hook frontend, antes de abrir el popup en modo producción:
```typescript
if (!IS_SANDBOX) {
  const { data } = await axios.get(`${API}/bank/checkout/moonpay-sign`, {
    params: { url },
    headers,
  });
  url = data.signed_url;
}
```

### Limitación actual

MoonPay no lista Plasma como chain soportada todavía. Para testing se usa `usdc_base` (USDC en Base).
Cuando MoonPay soporte Plasma: cambiar `NEXT_PUBLIC_MOONPAY_CURRENCY` al asset code correcto
(buscar en [docs.moonpay.com/moonpay/onramp/currencies](https://docs.moonpay.com/moonpay/onramp/currencies)).

### Flujo de pago con MoonPay standalone

```
[Usuario toca "Comprar con tarjeta / SPEI"]
    ↓
[Popup MoonPay sandbox] → usuario "paga" con tarjeta de prueba
    ↓
[En sandbox: confirmación simulada, no hay transferencia real on-chain]
    ↓
[Usuario cierra popup]
    ↓
[Para probar el checkout completo: usar hash 0x_mock_usdc_123 en el campo manual]
```

---

## Opción C — `useFiatOnramp` experimental (MXN nativo)

Privy v3.19.0 incluye `useFiatOnramp` marcado como `@experimental`. Soporta MXN como moneda de entrada.

```typescript
import { useFiatOnramp } from '@privy-io/react-auth';

const { fund } = useFiatOnramp();

await fund({
  source: {
    assets: ['mxn'],       // moneda fiat de entrada
    defaultAsset: 'mxn',
  },
  destination: {
    asset: 'USDT',         // activo cripto de salida (verificar código exacto)
    chain: `eip155:${PLASMA_CHAIN_ID}`,  // CAIP-2 format — necesita chainId real
    address: wallet.address,
  },
  environment: process.env.NODE_ENV === 'production' ? 'production' : 'sandbox',
  defaultAmount: '100',    // MXN
});
```

> ⚠️ Experimental. El proveedor que se usa internamente depende de la configuración del dashboard de Privy.
> No hay garantía de que soporte USDT0 en Plasma todavía.

---

## Variables de entorno necesarias

### Frontend `.env.local`

```bash
# — YA EXISTE —
NEXT_PUBLIC_PRIVY_APP_ID=cmnmsvcj500v00dl2zof7g50t
NEXT_PUBLIC_CHAIN_ID=31337          # ❗ Cambiar al Chain ID real de Plasma para producción

# — AGREGAR —
NEXT_PUBLIC_PLASMA_RPC_URL=         # ❗ URL del RPC de Plasma mainnet
NEXT_PUBLIC_USDT0_ADDRESS=          # ❗ Dirección del contrato USDT0 en Plasma
NEXT_PUBLIC_USDC_ADDRESS=           # ❗ Dirección del contrato USDC en Plasma (si existe)
NEXT_PUBLIC_RAMP_API_KEY=           # ❗ API key de Ramp Network
NEXT_PUBLIC_RAMP_ASSET_CODE=        # ❗ Código del asset en Ramp (ej. "PLASMA_USDT0")
```

### Backend `.env`

```bash
# — YA EXISTE —
PLASMA_RPC_URL=http://anvil_axolotto:8545  # ❗ Cambiar a RPC real para producción

# — AGREGAR —
USDC_ADDRESS=           # ❗ Dirección del contrato USDC o USDT0 en Plasma
                        # (el que se usará para verificar pagos on-chain)
```

---

## Actualización de `lib/blockchain.ts`

Una vez que tengas el Chain ID y RPC de Plasma:

```typescript
import { createPublicClient, http, defineChain } from 'viem';

const PLASMA_RPC_URL  = process.env.NEXT_PUBLIC_PLASMA_RPC_URL ?? 'http://127.0.0.1:8545';
const PLASMA_CHAIN_ID = Number(process.env.NEXT_PUBLIC_CHAIN_ID ?? 31337);

// ❗ Completar con datos reales
export const plasmaChain = defineChain({
  id:   PLASMA_CHAIN_ID,
  name: 'Plasma',
  nativeCurrency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
  rpcUrls: {
    default: { http: [PLASMA_RPC_URL] },
    public:  { http: [PLASMA_RPC_URL] },
  },
  blockExplorers: {
    default: { name: 'PlasmaScan', url: 'https://plasmascan.to' },
  },
});

export const publicClient = createPublicClient({
  chain: PLASMA_CHAIN_ID === 31337 ? anvil : plasmaChain,
  transport: http(PLASMA_RPC_URL),
});

export const CONTRACT_ADDRESSES = {
  GEMA_ALGA:       process.env.NEXT_PUBLIC_GEMA_ALGA_ADDRESS       as `0x${string}`,
  AXOGEMA:         process.env.NEXT_PUBLIC_AXOGEMA_ADDRESS          as `0x${string}`,
  WEBITOS:         process.env.NEXT_PUBLIC_WEBITOS_ADDRESS          as `0x${string}`,
  GAME_CONTROLLER: process.env.NEXT_PUBLIC_GAME_CONTROLLER_ADDRESS  as `0x${string}`,
  USDT0:           (process.env.NEXT_PUBLIC_USDT0_ADDRESS ?? '')    as `0x${string}`,
  USDC:            (process.env.NEXT_PUBLIC_USDC_ADDRESS  ?? '')    as `0x${string}`,
};
```

---

## Actualización de `PrivyProviderWrapper.tsx`

```typescript
"use client";
import { PrivyProvider } from "@privy-io/react-auth";
import { plasmaChain } from "@/lib/blockchain";

export default function PrivyProviderWrapper({ children }: { children: React.ReactNode }) {
  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID as string}
      config={{
        loginMethods: ["google", "email"],
        // Configurar la red por default
        defaultChain: plasmaChain,
        supportedChains: [plasmaChain],
        appearance: {
          theme: "dark",
          accentColor: "#E4007C",
        },
        embeddedWallets: {
          createOnLogin: 'all-users',  // asegura que todos tengan wallet
        },
        // Habilitar funding nativo de Privy (activar también en dashboard.privy.io)
        funding: {
          enabled: true,
        },
      }}
    >
      {children}
    </PrivyProvider>
  );
}
```

---

## Actualización de `verify_usdc_payment` en el backend

Hoy la función verifica específicamente el contrato de `USDC_ADDRESS`. Si el jugador paga con **USDT0** (contrato diferente), la verificación fallará.

Opciones:
1. **Aceptar tanto USDC como USDT0**: pasar lista de contratos aceptados y verificar cualquiera de los dos.
2. **Aceptar solo USDT0**: cambiar `USDC_ADDRESS` en `.env` a la dirección de USDT0.

Recomendación: **opción 2 por ahora** (menos código). Si en el futuro se aceptan ambos, refactorizar.

```python
# backend/app/core/config.py — renombrar para reflejar el token real
ACCEPTED_PAYMENT_TOKEN_ADDRESS: str = ""  # USDT0 o USDC en Plasma
```

```python
# backend/app/services/web3_service.py — actualizar
if log.get("address", "").lower() != settings.ACCEPTED_PAYMENT_TOKEN_ADDRESS.lower():
    continue
```

> Si cambias el nombre de la variable, actualizar también `checkout_service.py` que pasa `min_usdc`.
> En realidad el monto puede ser USDT0 (6 decimales, misma escala que USDC) — no hay cambio numérico.

---

## Pasos de implementación — orden exacto

> Marcar ✅ conforme se completen.

### Fase 1 — Obtener datos (blocker)
- [ ] **1.1** Confirmar Chain ID real de Plasma mainnet (ej. `2804` o el que sea)
- [ ] **1.2** Confirmar RPC URL de Plasma mainnet
- [ ] **1.3** Obtener dirección del contrato USDT0 en Plasma
- [ ] **1.4** Verificar si USDC existe en Plasma; si no, usar USDT0 como token de pago
- [ ] **1.5** Registrar cuenta en [app.ramp.network](https://app.ramp.network) → obtener API key
- [ ] **1.6** Verificar que Ramp soporte USDT0 en Plasma ([docs.ramp.network/assets](https://docs.ramp.network/assets)) y obtener el asset code exacto

### Fase 2 — Variables de entorno
- [ ] **2.1** Agregar a `frontend/.env.local`: `NEXT_PUBLIC_PLASMA_RPC_URL`, `NEXT_PUBLIC_USDT0_ADDRESS`, `NEXT_PUBLIC_RAMP_API_KEY`, `NEXT_PUBLIC_RAMP_ASSET_CODE`
- [ ] **2.2** Actualizar `NEXT_PUBLIC_CHAIN_ID` a Chain ID real de Plasma (para producción, en staging dejar 31337)
- [ ] **2.3** Agregar a `backend/.env`: `USDC_ADDRESS` con la dirección de USDT0 (o USDC si existe)
- [ ] **2.4** Agregar variables al servidor de producción (mismas que en .env.local pero con valores prod)

### Fase 3 — Frontend
- [ ] **3.1** Instalar Ramp SDK: `npm install @ramp-network/ramp-instant-sdk`
- [ ] **3.2** Actualizar `lib/blockchain.ts` → agregar `plasmaChain`, exportar `USDT0` address
- [ ] **3.3** Actualizar `PrivyProviderWrapper.tsx` → `defaultChain`, `supportedChains`, `embeddedWallets`
- [ ] **3.4** Crear `hooks/useRampFunding.ts` (ver código arriba)
- [ ] **3.5** Integrar botón Ramp en `CryptoCheckout.tsx` pantalla `method`
- [ ] **3.6** Actualizar `CryptoCheckout.tsx` → reemplazar `USDC_ADDRESS` por `USDT0_ADDRESS` o hacer dinámico
- [ ] **3.7** Probar en localhost: flujo Ramp sandbox → wallet Privy recibe USDT0

### Fase 4 — Backend
- [ ] **4.1** Actualizar `verify_usdc_payment` → aceptar USDT0 address además de (o en lugar de) USDC
- [ ] **4.2** Verificar que `verify_usdc_payment` funcione con transacción USDT0 real de Plasma
- [ ] **4.3** Probar E2E: Ramp sandbox → USDT0 en wallet → pago checkout → AXG acreditados

### Fase 5 — Privy Dashboard
- [ ] **5.1** Ir a [dashboard.privy.io](https://dashboard.privy.io) → tu app
- [ ] **5.2** Settings → Funding → Enable
- [ ] **5.3** Agregar Plasma como red soportada (si el dashboard lo permite)
- [ ] **5.4** (Opcional) Activar MoonPay si se quiere tarjeta adicional a Ramp

### Fase 6 — Testing & lanzamiento
- [ ] **6.1** Testing con Ramp sandbox (API key `_test_` genera flows de prueba sin pago real)
- [ ] **6.2** Probar en mobile (flujo crítico — Ramp es principalmente mobile)
- [ ] **6.3** Cambiar Ramp key a producción en `.env` de servidor
- [ ] **6.4** Smoke test real con $1 USD

---

## Qué hace cada proveedor (resumen rápido)

| | Ramp | MoonPay via Privy | `useFiatOnramp` |
|---|---|---|---|
| **SPEI / OXXO** | ✅ | ❌ | Depende del proveedor |
| **Tarjeta MX** | ✅ | ✅ | Depende |
| **MXN nativo** | ✅ | ✅ | ✅ (confirmado en tipos) |
| **USDT0 en Plasma** | ✅ (verificar asset code) | ❓ (depende de MoonPay) | ❓ (experimental) |
| **Comisión** | ~1-2% | ~3-4% | ~1-3% |
| **Integración** | SDK propio | Privy hook nativo | Privy hook experimental |
| **KYC** | Light (email + selfie) | Completo | Depende |

**Recomendación MVP**: Ramp + Privy embeddedWallet. SPEI/OXXO cubre al 70% de usuarios en México sin tarjeta de crédito internacional.

---

## Preguntas frecuentes

**¿USDT0 tiene 6 decimales como USDC?**
Sí, USDT estándar usa 6 decimales. El código en `verify_usdc_payment` (`int(min_usdc * 1_000_000)`) no necesita cambiar.

**¿Privy crea una wallet automáticamente al iniciar sesión?**
Solo si se configura `embeddedWallets: { createOnLogin: 'all-users' }` en el PrivyProvider. Sin eso, la wallet puede no existir para usuarios que iniciaron sesión antes de esta config. Agregar la config NO rompe wallets existentes.

**¿El jugador necesita entender de cripto?**
Con Ramp: no. El modal de Ramp es fiat-first: el usuario ve "Paga $100 MXN con OXXO, recibes X USDT en tu wallet". La parte cripto es invisible.

**¿Qué pasa si Ramp no soporta USDT0 en Plasma todavía?**
Dos opciones: (a) esperar (Ramp está activamente expandiendo Plasma según el anuncio de abril 2026), o (b) usar Ramp para depositar USDT en otra red y bridgear — más fricción, no recomendado para MVP.

---

*Creado: 2026-05-26 | Basado en tipos reales de @privy-io/react-auth v3.19.0*
