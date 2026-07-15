// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";

interface ICartasLoteriaVaultBurn {
    function burnVaultCards(uint256 id, uint256 amount) external;
}

/**
 * @title ReciclonVault
 * @notice Custodia de cartas recicladas de El Reciclon.
 *         Solo acepta el ERC-1155 CartasLoteria configurado. Los callbacks del
 *         estandar registran cada recepcion real y el owner puede ejecutar
 *         batchBurn para destruir definitivamente cartas de este mismo vault.
 *
 *         Flujo:
 *         1. Jugador recicla y transfiere CartasLoteria al vault
 *         2. Cartas quedan en este contrato
 *         3. El owner operativo llama batchBurn(ids, amounts)
 *
 *         La propiedad debe transferirse a un Safe antes de produccion. No se
 *         conserva un operador fijo adicional: Ownable ya permite rotar el
 *         control sin redeploy y evita una segunda llave privilegiada.
 */
contract ReciclonVault is ERC1155Holder, Ownable {
    /// @notice Contrato CartasLoteria (ERC-1155) autorizado para burn
    address public immutable cartasLoteria;

    /// @notice Totales acumulativos y saldo actualmente custodiado.
    uint256 public totalCardsReceived;
    uint256 public totalCardsBurned;
    uint256 public totalCardsHeld;

    event CardsReceived(address indexed from, uint256[] ids, uint256[] amounts);
    event CardsBurned(uint256[] ids, uint256[] amounts);

    error UnauthorizedToken(address token);
    error DeclarativeAccountingDisabled();

    constructor(address _cartasLoteria) Ownable(msg.sender) {
        require(_cartasLoteria != address(0), "ReciclonVault: cartasLoteria es cero");
        cartasLoteria = _cartasLoteria;
    }

    /// @dev Registra una recepcion simple confirmada por el callback ERC-1155.
    function onERC1155Received(address, address from, uint256 id, uint256 amount, bytes memory)
        public
        override
        returns (bytes4)
    {
        if (msg.sender != cartasLoteria) revert UnauthorizedToken(msg.sender);

        uint256[] memory ids = new uint256[](1);
        uint256[] memory amounts = new uint256[](1);
        ids[0] = id;
        amounts[0] = amount;
        _recordReceipt(from, ids, amounts);

        return this.onERC1155Received.selector;
    }

    /// @dev Registra una recepcion batch confirmada por el callback ERC-1155.
    function onERC1155BatchReceived(address, address from, uint256[] memory ids, uint256[] memory amounts, bytes memory)
        public
        override
        returns (bytes4)
    {
        if (msg.sender != cartasLoteria) revert UnauthorizedToken(msg.sender);
        _recordReceipt(from, ids, amounts);
        return this.onERC1155BatchReceived.selector;
    }

    /// @notice Quema en lote las cartas custodiadas en este contrato.
    ///         Llama a CartasLoteria.burnVaultCards(id, amount) por cada entrada.
    ///         Solo el owner rotatable puede ejecutarlo.
    function batchBurn(uint256[] calldata ids, uint256[] calldata amounts) external onlyOwner {
        require(ids.length == amounts.length, "ReciclonVault: arrays no coinciden");
        require(ids.length > 0, "ReciclonVault: arrays vacios");

        uint256 totalToBurn = 0;
        for (uint256 i = 0; i < ids.length; i++) {
            require(ids[i] >= 1 && ids[i] <= 54, "ReciclonVault: ID invalido");
            require(amounts[i] > 0, "ReciclonVault: amount cero");
            require(
                IERC1155(cartasLoteria).balanceOf(address(this), ids[i]) >= amounts[i],
                "ReciclonVault: saldo insuficiente"
            );
            totalToBurn += amounts[i];
        }

        require(totalToBurn <= totalCardsHeld, "ReciclonVault: custodia insuficiente");
        totalCardsHeld -= totalToBurn;
        totalCardsBurned += totalToBurn;

        for (uint256 i = 0; i < ids.length; i++) {
            ICartasLoteriaVaultBurn(cartasLoteria).burnVaultCards(ids[i], amounts[i]);
        }

        _assertAccounting();
        emit CardsBurned(ids, amounts);
    }

    /// @notice ABI legacy neutralizada: la contabilidad solo cambia por callbacks reales.
    function registerReceipt(uint256[] calldata, uint256[] calldata) external pure {
        revert DeclarativeAccountingDisabled();
    }

    function _recordReceipt(address from, uint256[] memory ids, uint256[] memory amounts) internal {
        require(ids.length == amounts.length, "ReciclonVault: arrays no coinciden");
        require(ids.length > 0, "ReciclonVault: arrays vacios");

        uint256 totalReceived = 0;
        for (uint256 i = 0; i < ids.length; i++) {
            require(ids[i] >= 1 && ids[i] <= 54, "ReciclonVault: ID invalido");
            require(amounts[i] > 0, "ReciclonVault: amount cero");
            totalReceived += amounts[i];
        }

        totalCardsReceived += totalReceived;
        totalCardsHeld += totalReceived;
        _assertAccounting();
        emit CardsReceived(from, ids, amounts);
    }

    function _assertAccounting() internal view {
        assert(totalCardsReceived == totalCardsBurned + totalCardsHeld);
    }
}
