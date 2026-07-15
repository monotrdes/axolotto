// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Frijolito (FRJ)
 * @notice Crédito cerrado de utilidad de Axolotto. No es transferible entre
 *         jugadores ni redimible. El sistema sólo puede emitirlo o consumirlo
 *         mediante mint/burn autorizados.
 */
contract Frijolito is ERC20, Ownable {
    address public gameController;
    error PlayerTransfersDisabled();

    event GameControllerUpdated(address indexed oldController, address indexed newController);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Frijolito: No autorizado");
        _;
    }

    constructor(address initialOwner) ERC20("Frijolito", "FRJ") Ownable(initialOwner) {}

    /// @notice Asigna el GameController que tiene permisos de mint/burn
    function setGameController(address _controller) external onlyOwner {
        emit GameControllerUpdated(gameController, _controller);
        gameController = _controller;
    }

    /// @notice Acuña FRJ para una dirección (usado por el Treasury al recompensar jugadores)
    function mint(address to, uint256 amount) external onlyController {
        _mint(to, amount);
    }

    /// @notice Quema FRJ desde una dirección (usado al gastar en la tienda/cuotas)
    function burn(address from, uint256 amount) external onlyController {
        _burn(from, amount);
    }

    function _update(address from, address to, uint256 amount) internal override {
        if (from != address(0) && to != address(0)) {
            revert PlayerTransfersDisabled();
        }
        super._update(from, to, amount);
    }
}
