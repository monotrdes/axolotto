// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Consumables
 * @notice Artículos consumibles del juego (ERC-1155).
 *
 * Token IDs:
 *   1 = Algae Pellet     (Pellet de Algas)   - Restaura 15 energía, cuesta 2 GAL
 *   2 = Brine Shrimp     (Camarón de Salmuera) - Restaura 60 energía, cuesta 10 GAL
 *   3 = Gotas Anti-Escarcha - Protege huevo de congelación
 *   4 = Lámpara Infrarroja  - Acelera incubación
 */
contract Consumables is ERC1155, Ownable {
    address public gameController;

    // Nombres de los consumibles para referencia
    mapping(uint256 => string) public consumableName;
    // Supply total acuñado por tipo
    mapping(uint256 => uint256) public totalMintedOf;

    event ConsumableMinted(address indexed to, uint256 id, uint256 amount);
    event ConsumableUsed(address indexed by, uint256 id);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Consumables: No autorizado");
        _;
    }

    constructor(address initialOwner, string memory uri_)
        ERC1155(uri_)
        Ownable(initialOwner)
    {
        consumableName[1] = "Algae Pellet";
        consumableName[2] = "Brine Shrimp";
        consumableName[3] = "Gotas Anti-Escarcha";
        consumableName[4] = "Lampara Infrarroja";
    }

    function setGameController(address _controller) external onlyOwner {
        gameController = _controller;
    }

    /// @notice Acuña consumibles para un jugador
    function mintConsumable(address to, uint256 id, uint256 amount) external onlyController {
        require(id >= 1 && id <= 4, "Consumables: ID invalido");
        totalMintedOf[id] += amount;
        _mint(to, id, amount, "");
        emit ConsumableMinted(to, id, amount);
    }

    /// @notice Quema un consumible al usarlo (GameController llama esto al alimentar un Axolotito)
    function burnConsumable(address from, uint256 id, uint256 amount) external onlyController {
        _burn(from, id, amount);
        emit ConsumableUsed(from, id);
    }
}
