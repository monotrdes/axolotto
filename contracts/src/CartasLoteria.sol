// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CartasLoteria
 * @notice 54 cartas de lotería como tokens ERC-1155 semi-fungibles.
 *         Token IDs: 1-54 (cada ID = una carta del mazo de lotería).
 *         Las cartas pueden estar en el inventario del jugador O en escrow
 *         dentro del contrato TablasLoteria mientras la tabla está activa.
 */
contract CartasLoteria is ERC1155, Ownable {
    address public gameController;
    address public tablasContract; // Contrato de tablas autorizado para escrow
    address public reciclonVault; // Vault autorizado para quemar solo su propia custodia

    // Supply actual por carta
    mapping(uint256 => uint256) public totalSupplyOf;

    event CartasMinted(address indexed to, uint256[] ids, uint256[] amounts);
    event ReciclonVaultConfigured(address indexed vault);

    modifier onlyController() {
        require(
            msg.sender == gameController ||
            msg.sender == tablasContract ||
            msg.sender == owner(),
            "CartasLoteria: No autorizado"
        );
        _;
    }

    constructor(address initialOwner, string memory uri_)
        ERC1155(uri_)
        Ownable(initialOwner)
    {}

    function setGameController(address _controller) external onlyOwner {
        gameController = _controller;
    }

    function setTablasContract(address _tablas) external onlyOwner {
        tablasContract = _tablas;
    }

    /// @notice Configura una sola vez el vault de reciclaje.
    function setReciclonVault(address _vault) external onlyOwner {
        require(_vault != address(0), "CartasLoteria: vault es cero");
        require(reciclonVault == address(0), "CartasLoteria: vault ya configurado");
        reciclonVault = _vault;
        emit ReciclonVaultConfigured(_vault);
    }

    function setURI(string memory uri_) external onlyOwner {
        _setURI(uri_);
    }

    /// @notice Acuña múltiples cartas a un jugador (al abrir un sobre)
    function mintCards(
        address to,
        uint256[] calldata ids,
        uint256[] calldata amounts
    ) external onlyController {
        for (uint256 i = 0; i < ids.length; i++) {
            require(ids[i] >= 1 && ids[i] <= 54, "CartasLoteria: ID de carta invalido");
            totalSupplyOf[ids[i]] += amounts[i];
        }
        _mintBatch(to, ids, amounts, "");
        emit CartasMinted(to, ids, amounts);
    }

    /// @notice Quema cartas (al destruir una carta en el desmontaje de tabla)
    function burnCard(address from, uint256 id, uint256 amount) external onlyController {
        require(from != reciclonVault, "CartasLoteria: usar burnVaultCards");
        totalSupplyOf[id] -= amount;
        _burn(from, id, amount);
    }

    /// @notice Permite al ReciclonVault quemar exclusivamente cartas de su propio saldo.
    function burnVaultCards(uint256 id, uint256 amount) external {
        require(msg.sender == reciclonVault && reciclonVault != address(0), "CartasLoteria: vault no autorizado");
        require(id >= 1 && id <= 54, "CartasLoteria: ID de carta invalido");
        require(amount > 0, "CartasLoteria: amount cero");
        totalSupplyOf[id] -= amount;
        _burn(msg.sender, id, amount);
    }

    /// @notice Aprueba al contrato de Tablas para mover cartas (para escrow)
    function setApprovalForTablas(address owner_, bool approved) external onlyController {
        require(owner_ != reciclonVault, "CartasLoteria: vault no aprobable");
        _setApprovalForAll(owner_, tablasContract, approved);
    }

    /// @notice Transfiere cartas de una dirección a otra (usado por GameController)
    function transferCard(address from, address to, uint256 id, uint256 amount) external onlyController {
        require(from != reciclonVault, "CartasLoteria: vault no transferible");
        _safeTransferFrom(from, to, id, amount, "");
    }
}
