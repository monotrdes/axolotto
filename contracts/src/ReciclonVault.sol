// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ReciclonVault
 * @notice Custodia de cartas recicladas de El Reciclon.
 *         Las cartas ERC-1155 se transfieren aqui via CartasLoteria.transferCard()
 *         y quedan en custodia permanente. El controller puede ejecutar batchBurn
 *         para destruirlas definitivamente en lote.
 *
 *         Flujo:
 *         1. Jugador recicla → backend llama CartasLoteria.transferCard(jugador, vault, id, amount)
 *         2. Cartas quedan en este contrato
 *         3. (Opcional) Controller llama batchBurn(ids, amounts) → CartasLoteria.burnCard(vault, id, amount)
 */
contract ReciclonVault is Ownable {
    /// @notice Contrato CartasLoteria (ERC-1155) autorizado para burn
    address public cartasLoteria;

    /// @notice Direccion del GameController autorizada para operar
    address public controller;

    /// @notice Total de cartas recibidas (acumulativo, solo lectura)
    uint256 public totalCardsReceived;

    event CardsReceived(address indexed from, uint256[] ids, uint256[] amounts);
    event CardsBurned(uint256[] ids, uint256[] amounts);

    modifier onlyController() {
        require(
            msg.sender == controller || msg.sender == owner(),
            "ReciclonVault: No autorizado"
        );
        _;
    }

    constructor(address _cartasLoteria, address _controller) Ownable(msg.sender) {
        require(_cartasLoteria != address(0), "ReciclonVault: cartasLoteria es cero");
        require(_controller != address(0), "ReciclonVault: controller es cero");
        cartasLoteria = _cartasLoteria;
        controller = _controller;
    }

    function setController(address _controller) external onlyOwner {
        require(_controller != address(0), "ReciclonVault: controller es cero");
        controller = _controller;
    }

    function setCartasLoteria(address _cartasLoteria) external onlyOwner {
        require(_cartasLoteria != address(0), "ReciclonVault: cartasLoteria es cero");
        cartasLoteria = _cartasLoteria;
    }

    /// @notice Quema en lote las cartas custodiadas en este contrato.
    ///         Llama a CartasLoteria.burnCard(vault, id, amount) por cada entrada.
    ///         Solo el controller o el owner pueden ejecutarlo.
    function batchBurn(uint256[] calldata ids, uint256[] calldata amounts) external onlyController {
        require(ids.length == amounts.length, "ReciclonVault: arrays no coinciden");
        require(ids.length > 0, "ReciclonVault: arrays vacios");

        // Interface minima para burnCard
        (bool success, ) = cartasLoteria.call(
            abi.encodeWithSignature(
                "burnCard(address,uint256,uint256)",
                address(this),
                0,  // placeholder, se itera abajo
                0
            )
        );
        // Nota: el call de arriba es solo para verificacion temprana.
        // Hacemos las llamadas reales en el loop.

        for (uint256 i = 0; i < ids.length; i++) {
            require(ids[i] >= 1 && ids[i] <= 54, "ReciclonVault: ID invalido");
            require(amounts[i] > 0, "ReciclonVault: amount cero");

            (bool ok, bytes memory data) = cartasLoteria.call(
                abi.encodeWithSignature(
                    "burnCard(address,uint256,uint256)",
                    address(this),
                    ids[i],
                    amounts[i]
                )
            );
            require(ok, string(abi.encodePacked("ReciclonVault: burnCard fallo para id=", toString(ids[i]))));
        }

        totalCardsReceived -= _sum(amounts);
        emit CardsBurned(ids, amounts);
    }

    /// @notice Registra recepcion de cartas (llamado externamente o via evento).
    ///         Como las cartas llegan via CartasLoteria.transferCard(), el backend
    ///         debe llamar esta funcion para mantener el contador actualizado.
    function registerReceipt(uint256[] calldata ids, uint256[] calldata amounts) external onlyController {
        require(ids.length == amounts.length, "ReciclonVault: arrays no coinciden");
        uint256 total = _sum(amounts);
        totalCardsReceived += total;
        emit CardsReceived(msg.sender, ids, amounts);
    }

    // ── Helpers ──

    function _sum(uint256[] memory arr) internal pure returns (uint256) {
        uint256 s = 0;
        for (uint256 i = 0; i < arr.length; i++) {
            s += arr[i];
        }
        return s;
    }

    function toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
