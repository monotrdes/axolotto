// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GemaAlga (GAL)
 * @notice Moneda principal del juego Axolotto.
 *         Se gana jugando, se gasta en la tienda, tablas, comida y cuotas de entrada.
 *         Solo el GameController puede hacer mint/burn.
 */
contract GemaAlga is ERC20, Ownable {
    address public gameController;

    event GameControllerUpdated(address indexed oldController, address indexed newController);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "GemaAlga: No autorizado");
        _;
    }

    constructor(address initialOwner) ERC20("Gema Alga", "GAL") Ownable(initialOwner) {}

    /// @notice Asigna el GameController que tiene permisos de mint/burn
    function setGameController(address _controller) external onlyOwner {
        emit GameControllerUpdated(gameController, _controller);
        gameController = _controller;
    }

    /// @notice Acuña GAL para una dirección (usado por el Treasury al recompensar jugadores)
    function mint(address to, uint256 amount) external onlyController {
        _mint(to, amount);
    }

    /// @notice Quema GAL desde una dirección (usado al gastar en la tienda/cuotas)
    function burn(address from, uint256 amount) external onlyController {
        _burn(from, amount);
    }
}
