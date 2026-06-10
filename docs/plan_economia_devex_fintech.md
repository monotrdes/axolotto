# Plan: Saneamiento Económico, Mercado P2P y DevEx Fintech

> Documento de diseño — rediseño completo de la infraestructura de monetización, el mercado P2P (Tianguis) y el sistema de retiro para desarrolladores/creadores (DevEx) de Axolotto.

## Resumen ejecutivo

Erradicar la "esquizofrenia financiera" actual mediante cuatro pilares:

1. **Valor nominal fijo** del AXF anclado a fiat (1 AXF = $2.00 MXN).
2. **Cortafuegos legal** que separa el azar (FRJ, sin valor de retiro) del comercio de destreza (NFTs artesanales por AXF).
3. **Marketplace P2P con escrow on-chain + pagos fiat** (Stripe Connect / Mercado Pago) con split payout automático, ocultando la blockchain al usuario final.
4. **Compliance automatizado**: AML, KYC, retenciones fiscales (SAT/México, Régimen de Plataformas Tecnológicas).

---

## 1. Constantes económicas de referencia (base inmutable)

**Ley económica: 1 AXF (Axoficha) = $2.00 MXN (fijo).** Relación lineal estricta para evitar arbitrajes.

### Paquetes en la Tienda Oficial

| Paquete | AXF | Precio MXN | Valor efectivo |
|---------|-----|-----------|----------------|
| Chico | 25 | $50 | $2.00/AXF |
| Mediano | 60 | $110 | ~$1.83/AXF |
| Grande | 160 | $280 | ~$1.75/AXF |
| Ballena | 600 | $980 | ~$1.63/AXF |

### Club VIP (suscripciones de 30 días)

Se elimina cualquier bono que multiplique ganancias o pozos de azar (jackpots) con moneda premium. El valor es de **conveniencia y estatus estético**.

| Nivel | Costo | Reclamo diario | Comisión P2P |
|-------|-------|----------------|--------------|
| Coral (Casual) | 50 AXF ($100 MXN/mes) | 20 FRJ | 4% |
| Dorado (Frecuente) | 120 AXF ($240 MXN/mes) | 50 FRJ | 3% |
| Axolite (Hardcore) | 300 AXF ($600 MXN/mes) | 130 FRJ | 2% especial |

---

## 2. Cortafuegos legal: separación de azar y comercio

Doctrina de la "Realidad Económica" para evitar catalogación como casino/juego de apuestas regulado:

1. **Bucle de azar** (Salas de Lotería Multijugador): se alimenta y premia **exclusivamente con FRJ** (Frijolitos), moneda off-chain centralizada **sin valor de conversión a dinero real**. El FRJ ganado por suerte solo sirve para jugar más, comprar comida base o expansiones cosméticas intransferibles de la cueva. *El azar divierte, pero no genera flujo financiero saliente.*
2. **Bucle de destreza/artesanal** (Crianza/Breeding con imprinting estratégico de Webitos y Forja de Tablas por rendimiento CSR): genera **activos NFT (ERC-721/1155) únicos**. Solo estos activos artesanales, con valor determinado por el mercado libre, pueden listarse y venderse por AXF en el Tianguis P2P.

---

## 3. Arquitectura fintech: DevEx P2P Escrow automatizado

Modelo de "Marketplace de Creadores" (estilo Roblox) mediado por pasarelas tradicionales, con la blockchain oculta en el backend.

### Saldos duales en base de datos

La cartera embebida del usuario traza invisiblemente dos tipos de AXF:

- **`AXF_Purchased`**: comprado con tarjeta/SPEI en la tienda oficial. **No elegible** para retiro DevEx.
- **`AXF_Earned`**: obtenido vendiendo un NFT artesanal a otro jugador en el Tianguis P2P. **Activa el disparador de retiro DevEx.**

### Ledger en Smart Contract + flujo fiduciario (método Counter-Strike)

La cola de órdenes de compra/venta y el inventario del mercado P2P corren sobre un **Smart Contract de Escrow**, para auditoría inmutable. Flujo:

1. **PUBLICACIÓN**: el Vendedor (Usuario A) lista un Axolotito Épico por 500 AXF ($1,000 MXN). El backend transfiere automáticamente el NFT de la Embedded Wallet del Usuario A al Smart Contract de Escrow ("limbo de garantía"). El activo queda congelado.
2. **INTENCIÓN DE COMPRA**: el Comprador (Usuario B) selecciona el ítem en la app móvil. El juego despliega el Checkout SDK de Mercado Pago o Stripe Connect por $1,000 MXN.
3. **DIVISIÓN DINÁMICA (SPLIT PAYOUT)**: la pasarela procesa el pago fiat y ejecuta un split 1:1 en la nube:
   - El **2%** ($20 MXN, o la comisión según nivel VIP del vendedor) va a la cuenta bancaria corporativa del estudio.
   - El **98%** ($980 MXN) va a la sub-cuenta fiduciaria (Stripe Express / Mercado Pago) vinculada del Usuario A.
4. **LIBERACIÓN BLOCKCHAIN**: al completarse la liquidación fiduciaria, la pasarela dispara un webhook seguro (`payment.completed`) al servidor. El backend firma una transacción on-chain instruyendo al Escrow que libere el NFT y lo asigne a la billetera embebida del Usuario B. El saldo `AXF_Earned` del vendedor se actualiza.

---

## 4. Barreras de cumplimiento, AML y seguridad antifraude

- **Cuarentena obligatoria (holding period)**: todo AXF ganado en una transacción P2P entra en un bloqueo de seguridad de **72 horas** antes de poder liquidarse al banco del vendedor (resolución de alertas de fraude / tarjetas robadas).
- **KYC y registro fiscal automatizado**: integración con Stripe Connect Express. Si un usuario acumula retiros **> $500 USD anuales**, se bloquean los pagos entrantes hasta completar verificación de identidad (INE/Pasaporte) y RFC.
- **Retención en la fuente**: Stripe actúa como agente retenedor bajo el **Régimen de Plataformas Tecnológicas** (aplicando automáticamente las tasas correspondientes de ISR e IVA sobre el flujo del vendedor y emitiendo la constancia fiscal digital).

---

## 5. Entregables esperados

1. **Propuesta de arquitectura técnica**: diagrama de flujo o pseudocódigo de los componentes — frontend móvil, servidor/API, pasarela fiat con split, y Smart Contract de Escrow.
2. **Diseño del Smart Contract de Escrow (Solidity)**: funciones clave para el manejo seguro del limbo de los NFTs durante el proceso de pago fiat.
3. **Algoritmo de conciliación en el backend**: validar que el webhook de la pasarela coincida exactamente con el ID del ítem en custodia del contrato antes de liberar el activo.

---

## Notas de implementación (contexto del repo)

- Toca: `backend/app/services/checkout_service.py`, `backend/app/api/v1/endpoints/market.py`, `backend/app/api/v1/endpoints/checkout.py`, `backend/app/models/economy.py`, `backend/app/core/config.py` (VIP tiers), y nuevo contrato de escrow en `contracts/src/`.
- Reglas críticas vigentes: `SELECT FOR UPDATE` antes de mutar Wallet/Inventory, `ProcessedTransaction` para replay protection, direcciones de contratos solo desde env/settings.

---
---

# PARTE II — ENTREGABLES

> Desarrollo de los tres entregables del §5. **Decisión de alcance**: la pasarela fiat (Mercado Pago / Stripe Connect) NO se integra en esta fase — se implementa un `MockPaymentGateway` que replica su contrato (checkout, split, webhook firmado), de modo que la pasarela real sea un swap de adaptador después.

## E1. Arquitectura técnica

### E1.1 Componentes

```
┌─────────────────────┐        ┌──────────────────────────────────────────┐
│  FRONTEND MÓVIL     │        │  BACKEND (FastAPI, puerto 8001)          │
│  (Next.js / app)    │        │                                          │
│                     │ HTTPS  │  market.py ──► escrow_market_service.py  │
│  Tianguis P2P UI    │───────►│  payments.py ─► payment_gateway/         │
│  Checkout simulado  │        │       │            ├─ base.py (ABC)      │
│  (modal fake-pay)   │        │       │            └─ mock_gateway.py    │
└─────────────────────┘        │       ▼                                  │
                               │  reconciliation_service.py               │
                               │       │                                  │
                               │       ▼                                  │
                               │  ChainOutbox worker ──► web3_service.py  │
                               └───────────┬──────────────────────────────┘
                                           │ JSON-RPC (Anvil / Plasma)
                                           ▼
                               ┌──────────────────────┐
                               │  MarketEscrow.sol    │◄── custodia NFTs
                               │  (nuevo contrato)    │    (Axolotitos,
                               └──────────────────────┘     TablasLoteria…)
```

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Servicio de mercado escrow | `backend/app/services/escrow_market_service.py` (nuevo) | Listar/cancelar/comprar: orquesta DB + outbox + gateway |
| Gateway de pagos (interfaz) | `backend/app/services/payment_gateway/base.py` (nuevo) | ABC: `create_checkout()`, `verify_webhook()`, `get_payment()` |
| Gateway simulado | `backend/app/services/payment_gateway/mock_gateway.py` (nuevo) | Simula checkout, split 98/2 y dispara webhook firmado (HMAC) tras N segundos |
| Conciliación | `backend/app/services/reconciliation_service.py` (nuevo) | Algoritmo E3: valida webhook ↔ custodia on-chain antes de liberar |
| Endpoints | `backend/app/api/v1/endpoints/market.py` (extender) + `payments.py` (nuevo: webhook) | API pública + receptor de webhooks |
| Worker on-chain | reutiliza patrón `ChainOutbox` existente (`models/economy.py`) | Nuevas operaciones: `escrow_deposit`, `escrow_release`, `escrow_refund` |
| Contrato | `contracts/src/MarketEscrow.sol` (nuevo) | Custodia y liberación de NFTs (E2) |

### E1.2 Modelos de datos nuevos (`backend/app/models/market_escrow.py`)

```python
class EscrowListing(SQLModel, table=True):
    id: str                      # uuid — se usa también como listingId on-chain (bytes32)
    seller_id: str               # privy_did
    nft_contract: str            # dirección (desde settings, nunca hardcode)
    token_id: int
    price_axf: int               # unidad mínima 10**6 (1 AXF = $2 MXN fijo)
    price_mxn_cents: int         # derivado: price_axf/10**6 * 200  (centavos)
    fee_pct: int                 # bps según VIP del vendedor: 400/300/200
    status: str                  # draft → escrowed → pending_payment → paid → released
                                 #   | cancelled | refunded
    escrow_tx_hash: str | None   # tx del depósito al contrato
    release_tx_hash: str | None
    buyer_id: str | None
    created_at / updated_at

class FiatPaymentIntent(SQLModel, table=True):
    id: str                      # uuid interno
    listing_id: str              # FK EscrowListing — UNIQUE parcial sobre intents activos
    buyer_id: str
    gateway: str                 # "mock" | "mercadopago" | "stripe"
    gateway_ref: str             # id del checkout en la pasarela (unique)
    amount_mxn_cents: int
    split_fee_cents: int         # comisión casa
    split_seller_cents: int      # 96-98% al vendedor
    status: str                  # created → succeeded | failed | expired
    expires_at: datetime         # TTL 30 min (mismo patrón que CryptoPurchaseOrder)

class EarnedBalanceLock(SQLModel, table=True):
    """Cuarentena 72h del AXF_Earned (§4)."""
    id: int
    seller_id: str
    listing_id: str
    axf_amount: int              # unidad mínima
    unlocks_at: datetime         # created_at + 72h
    status: str                  # locked → available | clawed_back
```

**Saldos duales (§3)**: NO se parte `Wallet.axofichas` en dos columnas. `AXF_Earned` disponible = `SUM(EarnedBalanceLock.axf_amount WHERE status='available')`; todo lo demás es `AXF_Purchased`. Así el saldo jugable sigue siendo uno solo y el elegible a retiro se deriva del ledger (auditable, sin migración destructiva).

### E1.3 Flujo end-to-end (pseudocódigo)

```
# 1. PUBLICACIÓN  — POST /market/escrow/list
with session.begin():
    inventario = SELECT ... FOR UPDATE          # regla crítica #3
    validar: NFT es artesanal (Axolotitos/TablasLoteria), sin listing activo
    listing = EscrowListing(status="draft", fee_pct=vip_fee(seller))
    outbox.add("escrow_deposit", {listing_id, nft_contract, token_id})
# worker → MarketEscrow.depositAndList(...) → status="escrowed"

# 2. INTENCIÓN DE COMPRA  — POST /market/escrow/{id}/checkout
validar: listing.status == "escrowed", buyer != seller, sin intent activo
intent = gateway.create_checkout(
    amount   = listing.price_mxn_cents,
    split    = {house: fee, seller: resto},
    metadata = {listing_id, buyer_id})           # ← clave de conciliación
return {checkout_url}                            # mock: modal de pago fake

# 3. SPLIT (SIMULADO)  — MockPaymentGateway
# al "pagar" en el modal fake, el mock registra el split en
# FiatPaymentIntent y dispara POST /api/v1/payments/webhook
# con firma HMAC-SHA256(secret_de_settings, body)

# 4. LIBERACIÓN  — webhook → reconciliation_service (algoritmo E3)
# si concilia OK: outbox.add("escrow_release", {listing_id, buyer_wallet})
#                 EarnedBalanceLock(locked, 72h) para el vendedor
# worker → MarketEscrow.release(...) → NFT a wallet del comprador
```

## E2. Smart Contract de Escrow — `contracts/src/MarketEscrow.sol`

### Decisiones de diseño

- **Operator-driven**: el usuario nunca firma; el backend (wallet operadora, misma usada por `web3_service`) ejecuta depósito y liberación. El contrato es el **ledger auditable**, no la UX.
- `listingId` = `bytes32` derivado del uuid del backend → conciliación 1:1 DB↔chain.
- El pago es fiat off-chain ⇒ el contrato **no toca dinero**; solo custodia NFTs y registra el `paymentRef` al liberar (auditoría inmutable del "método Counter-Strike").

```solidity
contract MarketEscrow is IERC721Receiver, ReentrancyGuard, Pausable, Ownable {

    enum Status { None, Listed, Released, Refunded }

    struct Listing {
        address seller;          // embedded wallet del vendedor
        address nftContract;
        uint256 tokenId;
        uint256 priceAxf;        // informativo (unidad mínima), para auditoría
        Status  status;
        uint64  listedAt;
    }

    mapping(bytes32 => Listing) public listings;
    address public operator;     // backend signer

    // ── núcleo ────────────────────────────────────────────────
    function depositAndList(bytes32 listingId, address seller,
        address nftContract, uint256 tokenId, uint256 priceAxf)
        external onlyOperator whenNotPaused;
        // safeTransferFrom(seller→escrow); requiere aprobación previa
        // de la embedded wallet (la firma el backend vía Privy).
        // revert si listings[listingId].status != None  (anti-reuso de id)

    function release(bytes32 listingId, address buyer, bytes32 paymentRef)
        external onlyOperator nonReentrant whenNotPaused;
        // require status == Listed; transfiere NFT al buyer;
        // status = Released; emit Released(listingId, buyer, paymentRef)

    function refund(bytes32 listingId)
        external onlyOperator nonReentrant;
        // require status == Listed; NFT de vuelta al seller (cancelación
        // o fallo de pago); status = Refunded

    // ── seguridad / vistas ────────────────────────────────────
    function setOperator(address) external onlyOwner;
    function pause() / unpause() external onlyOwner;
    function getListing(bytes32) external view returns (Listing memory);
    function emergencyWithdraw(bytes32 listingId) external onlyOwner;
        // solo si paused: devuelve al seller registrado (nunca a owner)

    event Deposited(bytes32 indexed listingId, address indexed seller, address nft, uint256 tokenId);
    event Released (bytes32 indexed listingId, address indexed buyer, bytes32 paymentRef);
    event Refunded (bytes32 indexed listingId, address indexed seller);
}
```

**Invariantes a testear en Foundry** (`contracts/test/MarketEscrow.t.sol`):
1. Un `listingId` jamás se reutiliza (None→Listed→Released/Refunded es terminal).
2. `release` y `refund` solo desde `operator`; nunca ambos para el mismo id.
3. El NFT solo puede salir hacia `buyer` (release) o `seller` original (refund/emergency) — nunca hacia `owner`/`operator`.
4. `paymentRef` queda en el evento `Released` → auditoría cruzada con `FiatPaymentIntent.gateway_ref`.

## E3. Algoritmo de conciliación (webhook → liberación)

`POST /api/v1/payments/webhook` → `reconciliation_service.reconcile(payload, signature)`:

```
1. AUTENTICIDAD
   firma_esperada = HMAC_SHA256(settings.PAYMENT_WEBHOOK_SECRET, raw_body)
   if not constant_time_compare(firma, firma_esperada): → 401  (sin detalle)

2. IDEMPOTENCIA  (regla crítica #4)
   INSERT ProcessedTransaction(tx_hash=f"webhook:{gateway_ref}",
                               purpose="p2p_fiat_payment")
   on UNIQUE violation → 200 "already processed"   # replay benigno, no error

3. MATCHING DB  (todo bajo una transacción con SELECT FOR UPDATE)
   intent  = FiatPaymentIntent WHERE gateway_ref = payload.ref FOR UPDATE
   listing = EscrowListing WHERE id = intent.listing_id FOR UPDATE
   verificar TODOS, si alguno falla → status="failed" + alerta, NO liberar:
     a) intent.status == "created" y no expirado
     b) listing.status == "escrowed" | "pending_payment"
     c) payload.amount_cents == intent.amount_mxn_cents      # monto exacto
     d) payload.metadata.listing_id == listing.id            # ítem exacto
     e) payload.split == (intent.split_fee_cents, intent.split_seller_cents)

4. MATCHING ON-CHAIN  (la pasarela NO es fuente de verdad del activo)
   onchain = MarketEscrow.getListing(bytes32(listing.id))
   verificar:
     f) onchain.status == Listed
     g) onchain.nftContract == listing.nft_contract
        y onchain.tokenId == listing.token_id
     h) ownerOf(tokenId) == address(MarketEscrow)            # custodia real
   discrepancia ⇒ status="reconciliation_mismatch" + alerta crítica
   (pago recibido pero activo inconsistente → reembolso manual/mock)

5. EJECUCIÓN  (misma transacción DB — patrón outbox garantiza atomicidad)
   intent.status  = "succeeded"
   listing.status = "paid";  listing.buyer_id = intent.buyer_id
   ChainOutbox.add("escrow_release",
       {listing_id, buyer_wallet, payment_ref: gateway_ref})
   EarnedBalanceLock(seller, axf_amount=listing.price_axf,
       unlocks_at=now+72h, status="locked")                  # §4 cuarentena
   TransactionLedger(MARKET_SELL para seller, MARKET_BUY para buyer,
       fee_applied=comisión VIP)
   COMMIT

6. POST-COMMIT  (worker ChainOutbox, con reintentos)
   release() on-chain → listing.status = "released"
   si el worker agota reintentos → alerta; el NFT sigue seguro en escrow
```

**Propiedad clave**: el dinero (paso 3) y el activo (paso 4) se validan de forma independiente y la liberación solo ocurre si ambos concilian con el **mismo `listing_id`**. Un webhook válido de la pasarela jamás puede liberar un NFT distinto al pagado.

## Simulación (fase actual, sin MP/Stripe)

- `MockPaymentGateway`: genera `gateway_ref = "mock_" + uuid`, expone un endpoint dev `POST /payments/mock/{ref}/pay` (o auto-paga tras 5 s) que construye el payload del webhook **firmado con el mismo HMAC** que usaría la pasarela real — el flujo de conciliación se ejerce completo.
- También simula fallos para tests: `?outcome=failed|wrong_amount|wrong_listing|replay` → cubren los pasos 1-4 del algoritmo.
- KYC/retenciones (§4): en mock, solo se registra el split y la cuarentena 72h; la integración Stripe Express/retención SAT queda para la fase de pasarela real (la interfaz `base.py` ya reserva `create_seller_account()` y `get_kyc_status()`).

## Orden de implementación sugerido

1. `MarketEscrow.sol` + tests Foundry (invariantes E2).
2. Modelos `market_escrow.py` + migración Alembic.
3. `payment_gateway/` (base + mock) y `reconciliation_service.py` con tests unitarios (replay, mismatch, monto incorrecto).
4. `escrow_market_service.py` + endpoints + operaciones nuevas del worker ChainOutbox.
5. UI Tianguis: listado escrow + modal de checkout simulado.
