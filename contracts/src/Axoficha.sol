// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Axoficha (AXF)
 * @notice Crédito premium cerrado de Axolotto. No es transferible entre
 *         jugadores ni redimible. El sistema sólo puede emitirlo o consumirlo
 *         mediante mint/burn autorizados.
 */
contract Axoficha is ERC20, Ownable {
    address public gameController;
    error PlayerTransfersDisabled();

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

    function _update(address from, address to, uint256 amount) internal override {
        if (from != address(0) && to != address(0)) {
            revert PlayerTransfersDisabled();
        }
        super._update(from, to, amount);
    }
}
