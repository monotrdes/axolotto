# Plan: Remediar VULN-02 — Centralización extrema de la Treasury Key

**Parent Task**: `task-1781055512-64`
**Subtask**: `task-1781055512-64-VULN-02`
**Auditoría**: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md`
**Fecha**: 2026-06-09
**Estado**: Planning
**Severidad**: 🔴 Crítica
**Prioridad**: Inmediato (bloqueante de producción)

## Resumen

Una sola `TREASURY_PRIVATE_KEY` en el `.env` del backend es owner de TODOS los contratos del sistema. Con esa clave se puede hacer mint ilimitado de AXF y FRJ, burn de cualquier wallet, y transferencia de cualquier NFT. No hay multisig, timelock, límites de tasa on-chain, ni separación de roles. Una filtración de esa clave = colapso económico total e irreversible.

## Ubicación del problema

| Archivo | Líneas | Problema |
|---------|--------|----------|
| `contracts/src/GameController.sol` | todas `onlyOwner` | Owner puede `depositarFRJ`/`depositarAXF` (mint arbitrario), `cobrarFRJ`/`cobrarAXF` (burn de cualquier wallet), transferir NFTs |
| `contracts/src/Axoficha.sol` | `mint()` con `onlyController` | `onlyController` incluye `owner()` → mint ilimitado de AXF |
| `contracts/src/Frijolito.sol` | `mint()` con `onlyController` | `onlyController` incluye `owner()` → mint ilimitado de FRJ |
| `backend/app/services/web3_service.py` | 102-132 | `TREASURY_PRIVATE_KEY` en texto plano, firma cada tx |
| `backend/app/core/config.py` | settings | `TREASURY_PRIVATE_KEY` cargada de `.env` sin protección |

---

## Plan de remediación

### Fase 1: Separación de roles on-chain (contratos)

#### 1.1 Migrar a `AccessControl` de OpenZeppelin

Reemplazar el modelo `Ownable` + `onlyController` por `AccessControl` con roles granulares:

```solidity
// Roles definidos
bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
bytes32 public constant CONTROLLER_ROLE = keccak256("CONTROLLER_ROLE");
bytes32 public constant DEFAULT_ADMIN_ROLE = 0x00; // multisig fría
```

**Contratos a modificar:**
- [ ] `Axoficha.sol` — migrar de `Ownable` a `AccessControl`
- [ ] `Frijolito.sol` — migrar de `Ownable` a `AccessControl`
- [ ] `GameController.sol` — migrar de `Ownable` a `AccessControl`
- [ ] `Webitos.sol` — migrar a `AccessControl`
- [ ] `Axolotitos.sol` — migrar a `AccessControl`
- [ ] `CartasLoteria.sol` — migrar a `AccessControl`
- [ ] `TablasLoteria.sol` — migrar a `AccessControl`
- [ ] `Sobrecito.sol` — migrar a `AccessControl`
- [ ] `Consumables.sol` — migrar a `AccessControl`

#### 1.2 Añadir `Pausable` a los tokens

- [ ] `Axoficha.sol` — heredar `Pausable`, gatear `mint`/`burn`/`transfer` con `whenNotPaused`
- [ ] `Frijolito.sol` — heredar `Pausable`, gatear `mint`/`burn`/`transfer` con `whenNotPaused`

#### 1.3 Circuit breaker: cap de mint por ventana

- [ ] Añadir en `Axoficha.sol` y `Frijolito.sol`:
  ```solidity
  uint256 public constant MINT_CAP_PER_WINDOW = 1_000_000 * 10**18;
  uint256 public constant MINT_WINDOW = 1 days;
  uint256 public mintedThisWindow;
  uint256 public windowStart;
  ```
- [ ] Validar en cada `mint()` que `mintedThisWindow + amount <= MINT_CAP_PER_WINDOW`
- [ ] Resetear el contador al iniciar nueva ventana

#### 1.4 Timelock para acciones administrativas

- [ ] Desplegar `TimelockController` de OpenZeppelin (o equivalente minimalista)
- [ ] Las funciones sensibles (`grantRole`, `revokeRole`, `setController`) pasan por timelock de 48h
- [ ] Las funciones operativas (`mint` con cap, `burn`) las ejecuta directamente la hot wallet

### Fase 2: Infraestructura de claves (backend)

#### 2.1 Hot Wallet operativa

- [ ] Generar nueva wallet operativa (la "hot wallet") con solo `MINTER_ROLE` + `CONTROLLER_ROLE`
- [ ] La hot wallet NO tiene `DEFAULT_ADMIN_ROLE`
- [ ] Fondos ETH mínimos para gas (rotación semanal automática desde la multisig)

#### 2.2 KMS / HSM para la clave operativa

- [ ] Evaluar opciones: AWS KMS, GCP KMS, Azure Key Vault, o HashiCorp Vault
- [ ] Migrar `TREASURY_PRIVATE_KEY` → firma vía KMS (nunca exponer la clave en memoria)
- [ ] Implementar helper `sign_transaction_via_kms(tx)` en `web3_service.py`
- [ ] Eliminar `TREASURY_PRIVATE_KEY` del `.env` y de `config.py`

#### 2.3 Multisig fría (Gnosis Safe)

- [ ] Desplegar Gnosis Safe en la chain objetivo (mínimo 2/3 o 3/5 firmantes)
- [ ] Transferir `DEFAULT_ADMIN_ROLE` de todos los contratos al Gnosis Safe
- [ ] La multisig es la única que puede `grantRole`/`revokeRole`/`pause`/`unpause`
- [ ] Documentar el procedimiento de recovery de emergencia

### Fase 3: Monitoreo on-chain

#### 3.1 Eventos de alerta

- [ ] Emitir evento `LargeMint(address indexed to, uint256 amount)` en Axoficha/Frijolito cuando amount > umbral
- [ ] Backend: worker que escucha eventos `LargeMint` y dispara alerta (Discord/Telegram/email)

#### 3.2 Dashboard / health-check

- [ ] Health-check periódico: comparar `totalSupply()` on-chain vs suma de wallets en DB
- [ ] Script de reconciliación diaria: detectar divergencias y alertar
- [ ] Registrar métricas de mint diario y comparar contra el cap

### Fase 4: Configuración de entorno

#### 4.1 Validación al arranque

- [ ] `config.py`: añadir `@model_validator` que **falle el arranque** si:
  - `BLOCKCHAIN_MODE != "local"` y `TREASURY_PRIVATE_KEY` está presente en texto plano (forzar migración a KMS)
  - `BLOCKCHAIN_MODE == "production"` y no hay `KMS_KEY_ID` o `HOT_WALLET_ADDRESS`

#### 4.2 Rotación de claves

- [ ] Script de rotación programada de la hot wallet (cada 90 días)
- [ ] Procedimiento documentado para compromiso de clave

---

## Riesgos y consideraciones

1. **Despliegue de nuevos contratos**: migrar a `AccessControl` rompe la ABI actual → requiere redeploy coordinado con migración de estado on-chain (balances, NFTs, allowances).
2. **Coordinación backend ↔ contratos**: el backend debe actualizar todas las referencias de ABI y direcciones de contrato (`settings.py` + `NEXT_PUBLIC_*`).
3. **Timelock vs velocidad de juego**: las acciones de juego (mint de premios, burn de cuotas) las ejecuta la hot wallet sin timelock. Solo acciones administrativas pasan por timelock.
4. **Costo de KMS**: evaluar costos de AWS KMS (~$1/mes por clave + ~$0.03 por 10k firmas) vs volumen esperado de transacciones.

## Criterios de aceptación

- [ ] Ningún contrato tiene un solo owner con poder de mint ilimitado
- [ ] La hot wallet operativa NO puede cambiar roles ni pausar
- [ ] Existe un cap diario de mint on-chain en ambos tokens
- [ ] Los tokens son `Pausable` y solo la multisig fría puede pausar
- [ ] `TREASURY_PRIVATE_KEY` no aparece en texto plano en `.env`, `config.py`, logs, ni backups
- [ ] Las firmas operativas pasan por KMS
- [ ] Hay monitoreo activo de mints anómalos con alertas
- [ ] El backend arranca sin errores con la nueva configuración de contratos
- [ ] Tests de integración pasan con los nuevos contratos

---

## Referencias

- Auditoría completa: `docs/AUDITORIA_SEGURIDAD_2026-06-09.md`
- OpenZeppelin AccessControl: https://docs.openzeppelin.com/contracts/5.x/access-control
- OpenZeppelin Pausable: https://docs.openzeppelin.com/contracts/5.x/api/utils#Pausable
- Gnosis Safe: https://safe.global/
- AWS KMS signing: https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html
