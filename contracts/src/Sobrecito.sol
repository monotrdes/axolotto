// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Sobrecito
 * @notice Sobrecitos de cartas de lotería (ERC-1155).
 *         Token IDs: 1=Fase1 (Clásica), 2=Fase2 (De la Suerte), 3=Fase3 (Pro de Plasma).
 *         Al abrir un sobrecito se quema este token y el backend mintea 7 cartas aleatorias.
 */
contract Sobrecito is ERC1155, Ownable {
    address public gameController;

    // Supply acuñado por fase
    mapping(uint256 => uint256) public mintedByFase;
    // Supply máximo por fase
    mapping(uint256 => uint256) public maxSupplyByFase;

    event SobrecitoMint(address indexed to, uint256 fase, uint256 amount);
    event SobrecitoAbierto(address indexed by, uint256 fase, uint256 sobrecitoId);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Sobrecito: No autorizado");
        _;
    }

    constructor(address initialOwner, string memory uri_)
        ERC1155(uri_)
        Ownable(initialOwner)
    {
        // Limites de supply por fase (en sobrecitos, no en cartas)
        maxSupplyByFase[1] = 50000;  // Fase 1 — sin límite estricto para simulaciones
        maxSupplyByFase[2] = 50000;
        maxSupplyByFase[3] = 50000;
    }

    function setGameController(address _controller) external onlyOwner {
        gameController = _controller;
    }

    /// @notice Acuña sobrecitos para un jugador (compra en tienda)
    function mintSobrecito(address to, uint256 fase, uint256 amount) external onlyController {
        require(fase >= 1 && fase <= 3, "Sobrecito: Fase invalida");
        mintedByFase[fase] += amount;
        _mint(to, fase, amount, "");
        emit SobrecitoMint(to, fase, amount);
    }

    /**
     * @notice Abre un sobrecito vía GameController (único camino autorizado).
     *         onlyController previene que un jugador queme su sobre directamente
     *         en la red sin pasar por el backend, lo que dejaría las cartas sin mintear.
     * @param fase  ID del tipo de sobrecito (1, 2 o 3)
     */
    function abrirSobrecito(uint256 fase) external onlyController returns (uint256 sobrecitoId) {
        require(balanceOf(msg.sender, fase) >= 1, "Sobrecito: No tienes este sobrecito");
        _burn(msg.sender, fase, 1);
        sobrecitoId = fase; // El backend usa el fase como ID de referencia
        emit SobrecitoAbierto(msg.sender, fase, sobrecitoId);
        return sobrecitoId;
    }

    /// @notice Quema sobrecitos desde una dirección (usado por GameController)
    function burnSobrecito(address from, uint256 fase, uint256 amount) external onlyController {
        _burn(from, fase, amount);
    }

    /// @notice Transfiere sobrecitos de una dirección a otra (usado por GameController)
    function transferirSobrecito(address from, address to, uint256 fase, uint256 amount) external onlyController {
        _safeTransferFrom(from, to, fase, amount, "");
    }
}
