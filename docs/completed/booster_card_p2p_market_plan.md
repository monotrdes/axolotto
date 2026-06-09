# Plan de Implementación: Venta P2P de Sobres Sellados y Cartas Sueltas

Este plan detalla los cambios requeridos en contratos inteligentes, backend y frontend para permitir que los sobres (boosters) y cartas de lotería en el inventario (`PlayerInventory`) del jugador sean comercializados en el mercado secundario P2P usando la moneda del juego (`GAL`). Además, asegura la integración de la mochila del jugador para visualizar y abrir sobres a demanda.

---

## 🎯 Objetivos de la Implementación
1. **Visualización y Apertura Diferida**: Permitir que los sobres comprados o ganados se guarden sellados en el inventario del jugador y se abran a discreción de este.
2. **Mercado P2P de Ítems del Inventario**: Crear un modelo y endpoints para listar y comprar sobres y cartas en el mercado secundario.
3. **Consistencia On-chain**: Actualizar los contratos ERC-1155 de sobres (`Boosters.sol`) y cartas (`CartasLoteria.sol`) para permitir transferencias P2P iniciadas por el backend (controlador), manteniendo la concordancia entre base de datos y blockchain.
4. **Interfaz de Usuario Premium**:
   - Extender `Inventory.tsx` para mostrar sobres, botón de apertura instantánea y botón de enlistar para venta P2P.
   - Extender `MarketP2P.tsx` con filtros de "Sobres" y "Cartas", visualizando los listings y permitiendo su compra directa.

---

## 🔍 Hallazgos de la Investigación

### Estado Actual en el Backend
- **Apertura y Quema**: El backend ya implementa `ShopService.open_booster` y la ruta `/shop/booster/open`. Al comprar un booster en `ShopService.buy_item`, este se añade a `PlayerInventory` y se acuña on-chain (ERC-1155). Al abrirse, se quema on-chain y se acuñan las 7 cartas correspondientes.
- **Mercado P2P Existente**: Axolotitos y Tablas se listan y venden directamente modificando flags en sus propias tablas (`is_listed_for_sale`, `sale_price_gal`). Dado que las cartas y sobres se guardan agrupados por cantidad en `PlayerInventory`, no podemos usar flags directos y requerimos una tabla de listings independiente.
- **Web3 / Blockchain**: `Web3Service` posee métodos para transferir Axolotitos (`transfer_axolotito_onchain`) y Tablas (`transfer_board_onchain`), pero carece de soporte para transferir sobres (`Boosters`) y cartas (`CartasLoteria`) entre cuentas.

### Estado Actual en Contratos Inteligentes
- `Boosters.sol` y `CartasLoteria.sol` heredan de ERC-1155 de OpenZeppelin y definen roles de `onlyController` para acuñación y quema. Sin embargo, no proveen una función de transferencia delegada que solo el controlador pueda invocar (como sí lo hacen `Axolotitos.sol` y `TablasLoteria.sol` con `transferAxolotito` y `transferirTabla` respectivamente).

---

## 🛠️ Cambios Propuestos

### 1. Smart Contracts
Modificar los contratos ERC-1155 para añadir funciones de transferencia controladas por el backend (GameController).

#### [MODIFY] [Boosters.sol](file:///home/monotr/axolotto/contracts/src/Boosters.sol)
Añadir una función `transferBooster` protegida por el modifier `onlyController`:
```solidity
function transferBooster(address from, address to, uint256 fase, uint256 amount) external onlyController {
    _safeTransferFrom(from, to, fase, amount, "");
}
```

#### [MODIFY] [CartasLoteria.sol](file:///home/monotr/axolotto/contracts/src/CartasLoteria.sol)
Añadir una función `transferCard` protegida por el modifier `onlyController`:
```solidity
function transferCard(address from, address to, uint256 id, uint256 amount) external onlyController {
    _safeTransferFrom(from, to, id, amount, "");
}
```

---

### 2. Backend Modelos
Definir un nuevo modelo para registrar los listings activos del mercado P2P para ítems del inventario.

#### [MODIFY] [items.py](file:///home/monotr/axolotto/backend/app/models/items.py)
Añadir la clase `InventoryMarketListing` usando SQLModel:
```python
from datetime import datetime

class InventoryMarketListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(foreign_key="user.privy_did", index=True)
    item_id: int = Field(foreign_key="itemcatalog.id")
    quantity: int = Field(default=1)
    is_first_edition: bool = Field(default=False)
    is_shiny: bool = Field(default=False)
    price_gal: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 3. Backend Servicios (Web3)
Agregar soporte en el servicio de blockchain para transferir los tokens ERC-1155 correspondientes.

#### [MODIFY] [web3_service.py](file:///home/monotr/axolotto/backend/app/services/web3_service.py)
Añadir métodos para invocar las nuevas funciones de los contratos:
```python
    @staticmethod
    def transfer_booster_onchain(from_address: str, to_address: str, booster_fase: int, amount: int = 1) -> str:
        if settings.IS_MOCK_WEB3:
            return "0x_mock_transfer_booster"
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        abi = _load_abi("Boosters") or _BOOSTERS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.BOOSTERS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferBooster(from_addr, to_addr, booster_fase, amount), w3)

    @staticmethod
    def transfer_card_onchain(from_address: str, to_address: str, card_id: int, amount: int = 1) -> str:
        if settings.IS_MOCK_WEB3:
            return "0x_mock_transfer_card"
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        abi = _load_abi("CartasLoteria")
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CARTAS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferCard(from_addr, to_addr, card_id, amount), w3)
```

---

### 4. Endpoints del Backend
Crear un nuevo router `/api/v1/market` para el comercio de inventario, implementando validaciones de cantidad, saldos, comisión P2P (con soporte para descuento de VIP) y actualización de inventarios.

#### [NEW] [market.py](file:///home/monotr/axolotto/backend/app/api/v1/endpoints/market.py)
Crear endpoints:
- `POST /market/inventory/list`:
  - Valida que el usuario tenga el ítem en `PlayerInventory` y en cantidad suficiente.
  - Reduce la cantidad en `PlayerInventory` (elimina la fila si llega a 0) para "bloquear" el ítem de aperturas o fusiones mientras está listado.
  - Crea una fila en `InventoryMarketListing`.
- `POST /market/inventory/{listing_id}/cancel`:
  - Valida propiedad de la publicación.
  - Elimina la publicación y reembolsa la cantidad original al inventario del usuario (`PlayerInventory`), sumándola a una fila existente o creando una nueva.
- `POST /market/inventory/{listing_id}/buy`:
  - Valida que la publicación exista y que el comprador no sea el vendedor.
  - Obtiene las wallets del comprador y vendedor.
  - Aplica comisión de servicio de 5% (reducida según tier de membresía VIP del comprador: Coral=4%, Dorado=3%, Axolite=1.5%).
  - Deduce el costo total en `gemas_alga` (GAL) del comprador, transfiere el remanente al vendedor y deposita la comisión en el `TreasuryVault`.
  - Registra las transacciones en `TransactionLedger`.
  - Transfiere el NFT on-chain utilizando `transfer_booster_onchain` (para sobres) o `transfer_card_onchain` (para cartas).
  - Añade la cantidad adquirida al inventario `PlayerInventory` del comprador.
  - Elimina la publicación.
- `GET /market/inventory/listings`:
  - Devuelve todos los listings de inventario activos uniéndolos con el `ItemCatalog` para retornar metadatos (nombre, descripción, imagen, tipo, rareza). Permite filtrar por tipo de ítem (`item_type`) y ordenar por precio.

#### [MODIFY] [main.py](file:///home/monotr/axolotto/backend/app/main.py)
- Importar `InventoryMarketListing` para registro del modelo.
- Importar y registrar el router `/api/v1/market`:
```python
from app.api.v1.endpoints import market
app.include_router(market.router, prefix="/api/v1/market", tags=["Marketplace P2P Inventario"])
```

---

### 5. Frontend: Visualización de Sobres y Venta P2P

#### [MODIFY] [Inventory.tsx](file:///home/monotr/axolotto/frontend/components/Inventory.tsx)
- **Visualización de Sobres**:
  - En la pestaña de cartas, listar al inicio cualquier ítem de tipo `BOOSTER` presente en `ownedItems`.
  - Mostrar tarjetas de sobres con diseños y colores atractivos (según su fase o temática).
- **Apertura de Sobres**:
  - Agregar el botón "Abrir Sobre" para boosters. Al pulsarlo, consume el booster invocando `/api/v1/shop/booster/open` y dispara el modal premium de unboxing 3D existente en la tienda.
- **P2P Listing**:
  - Para sobres y cartas poseídas, añadir un botón de "Vender P2P".
  - Al pulsarlo, abrir un modal flotante para seleccionar la cantidad a vender (hasta el máximo poseído) y el precio en GAL. Al confirmar, envía una petición `POST /api/v1/market/inventory/list`.

#### [MODIFY] [MarketP2P.tsx](file:///home/monotr/axolotto/frontend/components/MarketP2P.tsx)
- **Filtros Adicionales**:
  - Añadir chips/botones de filtro para `Sobres` y `Cartas` en la barra de tipos de activos.
- **Carga de Datos**:
  - Extender la función `loadMarket` para hacer una petición `axios.get` a `/api/v1/market/inventory/listings` y mezclar sus resultados con los de Tablas y Axolotitos.
- **Visualización de Ítems**:
  - Si el listado es un sobre (`itemType === 'BOOSTER'`), pintar un sobre 3D con colores específicos de su Fase y su badge de cantidad.
  - Si es una carta (`itemType === 'CARD'`), renderizar la carta con sus badges dinámicos (`✨ Brillante`, `⭐ 1st Ed` y su marco animado según rareza).
- **Acciones**:
  - Si es un listing propio, la acción "Retirar" ejecutará la llamada a `/api/v1/market/inventory/{id}/cancel`.
  - Si es ajeno, el botón "Comprar" abrirá la confirmación de compra y llamará a `/api/v1/market/inventory/{id}/buy`.

---

## 🧪 Plan de Verificación

### Pruebas Automatizadas
1. **Pruebas Unitarias del Backend**:
   - Crear un test unitario `test_market_p2p.py` en `backend/tests/unit`.
   - Validar listado exitoso, errores por cantidad insuficiente o precio <= 0.
   - Validar cancelación exitosa y devolución del item al inventario.
   - Validar compra exitosa: descuento de saldo GAL en comprador, abono con descuento de comisión en vendedor, incremento del TreasuryVault, y transferencia en el inventario.
   - Validar límites y cobro correcto de comisiones según membresía VIP del comprador.
2. **Pruebas de Simulación de Red Degradada/Concurrencia**:
   - Verificar comportamiento transaccional (rollback en base de datos si falla la transferencia Web3 on-chain).

### Pruebas Manuales
1. Comprar un booster sellado en la tienda, verificar que se añade al inventario sin auto-abrirse.
2. Ir a la pestaña "Cartas" en el inventario y verificar que el booster aparece ahí.
3. Hacer click en "Abrir Sobre" en el inventario, confirmar que la animación de apertura 3D ocurre y que se generan las 7 cartas en el inventario.
4. Con un booster sellado, presionar "Vender P2P", listar 1 booster por 100 GAL. Verificar que se descuenta 1 booster del inventario personal.
5. Iniciar sesión con otra cuenta de prueba (o simularla en Postman/frontend) y comprar el booster listado. Verificar saldos, comisiones de tesorería y transferencia del booster en el inventario de la segunda cuenta.
