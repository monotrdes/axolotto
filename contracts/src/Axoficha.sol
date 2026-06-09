// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Axoficha (AXF)
 * @notice Moneda premium de Axolotto. Se adquiere con dinero real (SPEI/crypto).
 *         Se usa para comprar Webitos y Boosters en la tienda.
 *         Solo el GameController puede hacer mint/burn.
 */
contract Axoficha is ERC20, Ownable {
    address public gameController;

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Axoficha: No autorizado");
        _;
    }

    constructor(address initialOwner) ERC20("Axoficha", "AXF") Ownable(initialOwner) {}

    function setGameController(address _controller) external onlyOwner {
        gameController = _controller;
    }

    function mint(address to, uint256 amount) external onlyController {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external onlyController {
        _burn(from, amount);
    }
}
