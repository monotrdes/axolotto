# Plan de Implementación – Compras con Cripto (AXG)

> Versión 2 — rediseñado con base en el codebase real (contratos, web3_service, bank_service, Privy).  
> El plan anterior tenía supuestos incorrectos sobre MINTER_ROLE y transfer_erc20_from_user. Ver correcciones abajo.

---

## 🎯 Objetivo

Que cualquier jugador pueda recargar **AXG (Axogemas)** en minutos, desde el celular, sin salir de la app. El jugador paga USDC en Plasma, el backend verifica on-chain y mintea AXG automáticamente. Claro que el jugador debe saber de cripto — pero el flujo tiene que sentirse simple: elige un pack, escanea el QR o toca "Pagar con mi wallet", y listo.

---

## 🏗️ Arquitectura del flujo

```
[Frontend]                    [Backend]                     [Chain Plasma]
    │                             │                               │
    │  POST /bank/checkout/crypto │                               │
    │  { pack_id }                │                               │
    ├────────────────────────────►│                               │
    │                             │ Crea CryptoPurchaseOrder      │
    │                             │ status=AWAITING_PAYMENT       │
    │◄────────────────────────────┤                               │
    │  { order_id,                │                               │
    │    pay_to: TREASURY_ADDR,   │                               │
    │    usdc_amount: "5.05",     │                               │
    │    expires_at }             │                               │
    │                             │                               │
    │  [Usuario envía USDC]       │                               │
    │  Privy sendTransaction()    │                               │
    ├──────────────────────────────────────────────────────────►  │
    │                             │              tx confirmada    │
    │                             │                               │
    │  POST /checkout/{id}/confirm│                               │
    │  { tx_hash }                │                               │
    ├────────────────────────────►│                               │
    │                             │ verify_usdc_payment(tx_hash) │
    │                             │ admin_deposit(axg_amount)    │
    │                             ├──────────────────────────────►│
    │                             │              AXG minted       │
    │◄────────────────────────────┤ status=COMPLETED             │
    │  Balance actualizado 🎉     │                               │
```

### Estados de la orden
```
AWAITING_PAYMENT → CONFIRMING → COMPLETED
AWAITING_PAYMENT → EXPIRED     (30 min sin pago)
CONFIRMING       → FAILED      (tx inválida o monto incorrecto)
```

---

## ✅ Lo que ya existe (no reinventar)

| Pieza | Archivo | Qué hace |
|---|---|---|
| `web3_service.transferir_axogemas(to, amount)` | `backend/app/services/web3_service.py` | Mintea AXG on-chain al wallet del jugador |
| `bank_service.admin_deposit(session, user_id, amount, currency, desc)` | `backend/app/services/bank_service.py` | Actualiza wallet off-chain + llama transferir_axogemas + registra en TransactionLedger |
| `GET /bank/wallet/{user_id}` | `backend/app/api/v1/endpoints/bank.py` | Devuelve saldos actuales |
| `User.wallet_address` | `backend/app/models/user.py` | Wallet Privy ya guardada en DB |
| `useBlockchainEvents.ts` | `frontend/hooks/useBlockchainEvents.ts` | Escucha Transfer de AXG/GAL, refresca HUD automáticamente |
| Contratos AXG/GAL | `contracts/src/Axogema.sol`, `GemaAlga.sol` | Mint via `onlyGameController` (Treasury address) |

### Correcciones al plan v1
- **MINTER_ROLE no existe** — los contratos usan `onlyGameController`/`onlyOwner`. No hay que modificar los contratos Solidity.
- **`transfer_erc20_from_user` no aplica** — el jugador no transfiere tokens a un contrato intermedio. Paga USDC directamente a la wallet del Treasury. El backend mintea AXG después de confirmar el pago on-chain.
- **El backend ya puede mintear** con `transferir_axogemas()` y `admin_deposit()`. Solo hay que agregar la capa de checkout encima.

---

## 🎁 Catálogo de Packs AXG

| Pack | Precio | AXG Base | Bonus | AXG Total | Badge |
|------|--------|----------|-------|-----------|-------|
| 🐣 Huevito | $2 USD | 200 | — | 200 | — |
| 🦎 Axolotito | $5 USD | 500 | +10% | 550 | POPULAR |
| 🌿 Cenote | $15 USD | 1,500 | +15% | 1,725 | VALOR |
| 🏆 Jackpot | $50 USD | 5,000 | +20% | 6,000 | MEJOR DEAL |

**Bonuses especiales:**
- **Primera compra**: +10% AXG automático en cualquier pack (campo `first_crypto_purchase_at` en User)
- **Oferta flash**: 1 pack aleatorio con +25% AXG, rota cada 24h
- **Código de referido**: ambos reciben +5% AXG en su próxima compra

Los precios en MXN se calculan en tiempo real desde `GET /bank/exchange-rate`.

---

## 📦 Cambios de código necesarios

### 1. Modelo — `CryptoPurchaseOrder`
**Archivo:** `backend/app/models/economy.py` — agregar al final

```python
class OrderStatus(str, Enum):
    AWAITING_PAYMENT = "awaiting_payment"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"

class CryptoPurchaseOrder(SQLModel, table=True):
    id: str                           # UUID, primary key
    user_id: str                      # FK user.privy_did
    pack_id: str                      # "huevito" | "axolotito" | "cenote" | "jackpot"
    usd_amount: float
    usdc_amount: float                # usd_amount + 1% slippage buffer
    axg_amount: float                 # AXG a mintear (base + bonus)
    payment_token: str = "USDC"
    treasury_address: str             # dirección donde el jugador debe enviar
    tx_hash_payment: Optional[str]    # UNIQUE — previene double-mint
    tx_hash_mint: Optional[str]
    status: OrderStatus = OrderStatus.AWAITING_PAYMENT
    bonus_applied: Optional[str]      # "first_purchase" | "flash_sale" | "referral"
    bonus_pct: float = 0.0
    created_at: datetime
    expires_at: datetime              # created_at + 30 min
    completed_at: Optional[datetime]
```

### 2. `CheckoutService`
**Archivo:** `backend/app/services/checkout_service.py` (nuevo)

```python
AXG_PACKS = {
    "huevito":   {"usd": 2,  "axg_base": 200,  "bonus_pct": 0.00},
    "axolotito": {"usd": 5,  "axg_base": 500,  "bonus_pct": 0.10},
    "cenote":    {"usd": 15, "axg_base": 1500, "bonus_pct": 0.15},
    "jackpot":   {"usd": 50, "axg_base": 5000, "bonus_pct": 0.20},
}

class CheckoutService:
    @staticmethod
    def create_order(session, user_id, pack_id) → CryptoPurchaseOrder:
        # Valida: user tiene wallet_address registrado
        # Valida: usuario tiene < 3 órdenes activas (rate limit)
        # Aplica bonuses: primera compra (+10%), flash sale, referido (+5%)
        # Crea orden con expires_at = now + 30min
        # Devuelve la orden (con pay_to = settings.TREASURY_ADDRESS)

    @staticmethod
    def confirm_payment(session, order_id, tx_hash) → CryptoPurchaseOrder:
        # Valida: orden existe y está en AWAITING_PAYMENT
        # Valida: orden no expirada
        # Valida: tx_hash no usado antes en ninguna otra orden (anti double-mint)
        # Llama: web3_service.verify_usdc_payment(tx_hash, treasury, min_amount)
        # Llama: bank_service.admin_deposit(session, user_id, axg_amount, "axogema", desc)
        # Actualiza: status=COMPLETED, tx_hash_payment, tx_hash_mint, completed_at

    @staticmethod
    def expire_stale_orders(session) → int:
        # Marca EXPIRED las órdenes AWAITING_PAYMENT con expires_at < now
        # Llamar periódicamente (cron o on-demand al hacer GET status)
```

### 3. Endpoints
**Archivo:** `backend/app/api/v1/endpoints/checkout.py` (nuevo)

```python
# Router prefix: /bank/checkout
GET  /bank/checkout/packs
     → Lista de packs con precio USD/MXN, AXG total, badge, y oferta flash activa

POST /bank/checkout/crypto
     Body: { pack_id: str, referral_code?: str }
     Auth: get_verified_user_id()
     → { order_id, pay_to, usdc_amount, axg_amount, bonus_pct, expires_at }

GET  /bank/checkout/crypto/{order_id}
     Auth: usuario debe ser el dueño de la orden
     → { status, tx_hash_payment?, tx_hash_mint?, completed_at? }

POST /bank/checkout/crypto/{order_id}/confirm
     Body: { tx_hash: str }
     Auth: usuario debe ser el dueño de la orden
     → { status: "completed", axg_amount, new_balance }

GET  /bank/exchange-rate
     → { usd_mxn: float, updated_at }  ← fetch externo con TTL de 1h
```

Agregar en `backend/app/api/v1/router.py`:
```python
from app.api.v1.endpoints import checkout
api_router.include_router(checkout.router, tags=["checkout"])
```

### 4. `web3_service.verify_usdc_payment`
**Archivo:** `backend/app/services/web3_service.py`

```python
def verify_usdc_payment(
    self, tx_hash: str, expected_recipient: str, min_usdc: float
) -> bool:
    """Verifica que tx_hash sea Transfer de USDC al treasury por al menos min_usdc."""
    receipt = self.w3.eth.get_transaction_receipt(tx_hash)
    if not receipt or receipt.status != 1:
        return False
    # Parsear Transfer(address indexed from, address indexed to, uint256 value)
    # del contrato USDC (settings.USDC_ADDRESS)
    # Validar: to == expected_recipient (case-insensitive)
    # Validar: value >= int(min_usdc * 1e6) * 0.99  ← tolerancia 1%
    ...
```

Agregar en `backend/app/core/config.py`:
```python
USDC_ADDRESS: str = ""  # Dirección del contrato USDC en Plasma
```

### 5. Frontend — `CryptoCheckout.tsx`
**Archivo:** `frontend/components/CryptoCheckout.tsx` (nuevo)

Bottom sheet animado con state machine de 5 pantallas:

```
'packs' → 'method' → 'paying' → 'confirming' → 'success'
```

**Pantalla 1 — Elige tu pack:**
Grid 2×2 de pack cards. Cada card muestra emoji, nombre, precio en USD y MXN,
AXG total y badge (POPULAR / VALOR / MEJOR DEAL). La oferta flash tiene borde
dorado parpadeante. Botón "Continuar →".

**Pantalla 2 — Método de pago:**
Radio selector: USDC en Plasma (único por ahora). Muestra total en USD y MXN.
Botón "Iniciar compra →" → llama `POST /bank/checkout/crypto`.

**Pantalla 3 — Pago (pantalla más importante):**
```
┌─────────────────────────────────┐
│  Envía exactamente:             │
│                                 │
│  5.05 USDC                      │
│  a esta dirección:              │
│                                 │
│  [   QR CODE grande   ]         │
│                                 │
│  0x7f3a…b9c2   [📋 Copiar]     │
│                                 │
│  ⏳ Expira en 28:43             │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 💜 Pagar con mi wallet  │   │  ← Privy sendTransaction, 1-tap
│  └─────────────────────────┘   │
│                                 │
│  ¿Ya pagaste desde otra app?   │
│  [Pegar hash de tx manualmente] │
└─────────────────────────────────┘
```

Hooks usados:
```typescript
const { sendTransaction } = usePrivy();

// Al tocar "Pagar con mi wallet":
const { hash } = await sendTransaction({
  to: order.pay_to,
  data: encodeUSDCTransfer(order.pay_to, parseUnits(order.usdc_amount, 6)),
});
// Inmediatamente llama confirm con el hash
await axios.post(`/bank/checkout/crypto/${order.order_id}/confirm`, { tx_hash: hash });
```

**Pantalla 4 — Confirmando:**
Spinner + polling a `GET /bank/checkout/crypto/{order_id}` cada 4s.
Muestra tx hash con link al explorador de Plasma (`https://plasma-explorer.to/tx/...`).

**Pantalla 5 — Éxito:**
Animación de confetti/glow (igual que ResultCard del Gashapon).
Muestra AXG recibidos con desglose (base + bonus %). Nuevo saldo.
Botón "¡A jugar!".

**Integración en Store.tsx:**
En el tab "El Banco" (tabla de conversión AXG→GAL), agregar una card encima:
```tsx
<button onClick={() => setCryptoCheckoutOpen(true)}
  className="w-full rounded-2xl border border-purple-500/30 bg-purple-950/20 p-4
             flex items-center justify-between">
  <div>
    <div className="font-black text-white text-sm">💎 Recargar AXG</div>
    <div className="text-[10px] text-slate-400">Paga con USDC · Recibe Axogemas al instante</div>
  </div>
  <span className="text-purple-400 text-lg">→</span>
</button>
{cryptoCheckoutOpen && (
  <CryptoCheckout userId={userId} token={token}
    onClose={() => setCryptoCheckoutOpen(false)}
    onSuccess={recargarSaldos} />
)}
```

**Integración en `PrivyProviderWrapper.tsx`:**
```typescript
// Agregar al config de Privy:
defaultChain: plasmaTestnet,   // definir en lib/blockchain.ts
supportedChains: [plasmaTestnet],
```

---

## 💳 Opciones de Recarga — Rutas para el jugador

### Ruta A — Privy 1-tap (ya implementado ✅)
El jugador tiene USDC en su wallet de Privy (el embedded wallet que Privy crea automáticamente al iniciar sesión). Hace clic en **"Pagar con mi wallet (Privy)"** y Privy muestra una pantalla de confirmación nativa. El backend verifica el `from` de la transacción contra `user.wallet_address`.

### Ruta B — Desde Binance / CEX (guía en la UI ✅)
Binance soporta retiros de **USDT** a la red **Plasma** desde septiembre 2025, con comisiones ≈$0.01 USD.

**Flujo correcto:**
1. En Binance: Portafolio → Retirar → USDT → Red: **Plasma**
2. Destino: **la wallet de Privy del usuario** (NO la dirección del treasury directamente)
3. Una vez recibido en la wallet de Privy, usar el botón "Pagar con mi wallet (Privy)"

> ⚠️ **Por qué no se puede pagar directo al treasury desde Binance:**  
> La verificación on-chain (`verify_usdc_payment`) comprueba que el campo `from` de la transacción coincida con el `wallet_address` del usuario en la BD. Cuando el usuario retira desde Binance, el `from` es la hot wallet de Binance, no la wallet del usuario — la verificación fallaría.  
> Solución: cargar la wallet de Privy primero, luego pagar desde ahí.

**Nota sobre Bitso:** Bitso **NO soporta la red Plasma** (solo ETH, TRON, Polygon, Solana). No es una opción válida para este flujo.

---

## 🪙 Privy Fiat On-Ramp — Plan de Integración

> Estado: **planificado** (post-MVP). Requiere cuenta en MoonPay/Ramp y configuración de Privy.

### ¿Qué es?

Privy expone el hook `useFundWallet()` que abre un modal nativo para que el jugador compre cripto con tarjeta de crédito/débito o transferencia bancaria, sin salir de la app. El proveedor (MoonPay, Meld, Ramp, Coinbase) procesa el pago fiat y deposita directamente en la wallet de Privy del usuario.

### Proveedores disponibles

| Proveedor | Monedas soportadas | MXN → USDC? | Plasma? | Notas |
|---|---|---|---|---|
| **MoonPay** | USDC, USDT, ETH | Sí (tarjeta) | No directo — usa EVM bridging | Mayor adopción en LATAM |
| **Meld** | USDC, USDT | Sí | Investigating | Integración más nueva |
| **Ramp** | USDT | Sí (SPEI/OXXO) | ✅ **USDT en Plasma** (abril 2026) | Mejor opción para MX |
| **Coinbase Pay** | USDC | No MXN | No — solo ETH mainnet | Solo usuarios con cuenta Coinbase |

**Recomendación:** Integrar **Ramp** como proveedor prioritario. Anunció soporte de USDT en Plasma en abril 2026, acepta SPEI y OXXO, y tiene bajas comisiones para México.

### API de Privy — `useFundWallet`

```typescript
import { useFundWallet } from '@privy-io/react-auth';

const { fundWallet } = useFundWallet();

// Al tocar "Comprar USDC con tarjeta / SPEI / OXXO":
await fundWallet(userWalletAddress, {
  chain: plasmaTestnet,     // o plasmaMainnet cuando se lance
  amount: '5.05',           // en USD
  asset: 'USDC',            // o 'USDT'
});
// El modal de Ramp/MoonPay se abre. Al cerrar, el wallet del usuario
// ya tiene los fondos. Desde ahí pueden pagar con el botón de Privy.
```

### Configuración en `PrivyProviderWrapper.tsx`

```typescript
import { PrivyProvider } from '@privy-io/react-auth';

<PrivyProvider
  appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID!}
  config={{
    defaultChain: plasmaTestnet,
    supportedChains: [plasmaTestnet],
    fundingMethodConfig: {
      moonpay: {
        useSandbox: process.env.NODE_ENV !== 'production',
      },
      // Ramp — configurar API key cuando esté disponible
    },
    // embeddedWallets: { createOnLogin: 'all-users' },  // ya configurado?
  }}
>
```

### Definición de la red Plasma en `lib/blockchain.ts`

```typescript
import { defineChain } from 'viem';

export const plasmaTestnet = defineChain({
  id: 31337,              // verificar el chainId real de Plasma testnet
  name: 'Plasma Testnet',
  nativeCurrency: { name: 'Plasma ETH', symbol: 'ETH', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://rpc.plasma-testnet.to'] },  // verificar URL
  },
  blockExplorers: {
    default: { name: 'PlasmaScan', url: 'https://testnet.plasmascan.to' },
  },
});

// Dirección del contrato USDC en Plasma — obtener del equipo de Plasma o docs
export const USDC_PLASMA_ADDRESS = process.env.NEXT_PUBLIC_USDC_ADDRESS as `0x${string}`;
```

### Flujo completo con on-ramp

```
[Usuario] → Elige pack → "Comprar con tarjeta/SPEI"
    ↓
[Privy fundWallet] → Modal Ramp/MoonPay → Pago fiat
    ↓
[USDC/USDT llega a wallet Privy del usuario]
    ↓
[Usuario toca "Pagar con mi wallet (Privy)"] → eth_sendTransaction
    ↓
[Backend verifica + mintea AXG]
```

### Pasos para implementar

1. **Registrar cuenta en Ramp** (ramp.network/business) y obtener API key
2. **Agregar `fundingMethodConfig`** con Ramp/MoonPay en `PrivyProviderWrapper.tsx`
3. **Definir chain Plasma** en `lib/blockchain.ts` con chainId y RPC correctos
4. **Agregar botón** "Comprar con tarjeta / SPEI / OXXO" en la pantalla `paying` de `CryptoCheckout.tsx`:
   ```tsx
   <button onClick={() => fundWallet(embeddedWallet.address, { chain: plasmaTestnet, amount: order.usdc_amount.toFixed(2), asset: 'USDC' })}>
     💳 Comprar USDC con tarjeta / SPEI / OXXO
   </button>
   ```
5. **Verificar chainId** real de Plasma con el equipo antes de lanzar

### Pendientes de verificar

- [ ] ChainId real de Plasma mainnet/testnet
- [ ] URL del RPC de Plasma  
- [ ] Dirección del contrato USDC en Plasma (de Plasma team o bridge oficial)
- [ ] Si Ramp ya tiene producción en Plasma (anuncio abril 2026 fue de testnet)
- [ ] Si `useFundWallet` de Privy acepta Ramp como proveedor custom o solo MoonPay/Meld/Coinbase

---

## 🔐 Seguridad

| Riesgo | Mitigación |
|---|---|
| Double-mint (mismo tx_hash 2 veces) | `tx_hash_payment` tiene `unique=True` en DB + constraint |
| Orden expirada pagada tarde | `confirm_payment` rechaza si `expires_at < now` |
| Monto incorrecto enviado | `verify_usdc_payment` exige ≥99% del monto esperado |
| TX-hash theft (alguien reclama la tx de otro) | `verify_usdc_payment` verifica que `from` == `user.wallet_address` |
| Spam de órdenes | Máx 3 órdenes activas por usuario (`MAX_ACTIVE_ORDERS = 3`) |
| Private key expuesta | `TREASURY_PRIVATE_KEY` solo en backend `.env`, nunca al frontend |
| Pago directo desde CEX al treasury | UX informa al usuario: primero cargar wallet de Privy, luego pagar desde ahí |

---

## 💡 Ideas post-MVP (roadmap)

| Idea | Complejidad | Impacto |
|---|---|---|
| **SPEI/OXXO Pay** vía Conekta | Media | Alto para México |
| **Recibo por email** (Privy tiene el email) | Baja | Medio |
| **Gifting** — comprar AXG para un amigo | Media | Alto |
| **Límite mensual anti-whale** ($500 USD) | Baja | Seguridad |
| **Códigos de referido** con tabla propia | Media | Crecimiento |
| **Oferta flash dinámica** en tabla de settings | Baja | Engagement |

SPEI funciona con exactamente el mismo `CryptoPurchaseOrder`: el webhook de Conekta llama a `confirm_payment` internamente. Cero cambios en contratos.

---

## 📋 Archivos a crear/modificar

| Estado | Archivo |
|---|---|
| ✅ Hecho | `backend/app/models/economy.py` — `CryptoPurchaseOrder`, `OrderStatus` |
| ✅ Hecho | `backend/app/services/checkout_service.py` |
| ✅ Hecho | `backend/app/api/v1/endpoints/checkout.py` |
| ✅ Hecho | `backend/app/main.py` — router incluido + migración startup |
| ✅ Hecho | `backend/app/services/web3_service.py` — `verify_usdc_payment` con sender check |
| ✅ Hecho | `backend/app/core/config.py` — `USDC_ADDRESS` |
| ✅ Hecho | `backend/requirements.txt` — httpx |
| ✅ Hecho | `frontend/components/CryptoCheckout.tsx` — 5 pantallas + guía Binance |
| ✅ Hecho | `frontend/components/Store.tsx` — botón "Recargar AXG con cripto" |
| 📋 Pendiente | `frontend/components/PrivyProviderWrapper.tsx` — `defaultChain` Plasma + Ramp config |
| 📋 Pendiente | `frontend/lib/blockchain.ts` — definir `plasmaTestnet` (verificar chainId real) |
| 📋 Pendiente | `.env` — `USDC_ADDRESS` con la dirección real del contrato USDC en Plasma |

---

## ✅ Verificación E2E

```bash
# Backend
cd /home/monotr/axolotto/backend
# 1. Crear orden: POST /bank/checkout/crypto {pack_id: "axolotito"}
# 2. Verificar BD: CryptoPurchaseOrder status=AWAITING_PAYMENT
# 3. Confirmar: POST /checkout/{id}/confirm {tx_hash: "0x_mock_usdc_123"}
# 4. Verificar: wallet.axogemas += 550, TransactionLedger tiene entrada tipo DEPOSIT
# 5. Repetir confirm con mismo tx_hash → debe rechazar 409 Conflict

# Frontend (DevTools → viewport iPhone 14)
cd /home/monotr/axolotto/frontend && npm run dev
# Store → El Banco → Recargar AXG → pack Axolotito
# → "Pagar con mi wallet" → Privy sendTransaction
# → polling status → éxito → HUD muestra nuevo saldo AXG
```

---

*Última actualización: 2026-05-26. Diseñado con base en codebase real — sin cambios a contratos Solidity, reutiliza web3_service.transferir_axogemas y bank_service.admin_deposit.*
