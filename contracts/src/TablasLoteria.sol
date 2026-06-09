// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TablasLoteria
 * @notice Tablas de juego como NFTs ERC-721 con las 16 cartas en ESCROW.
 *
 * Al crear una tabla:
 *   1. Se transfieren las 16 cartas ERC-1155 del jugador a este contrato (escrow).
 *   2. Se acuña un NFT de Tabla para el jugador.
 *   3. El layout de 16 card IDs se almacena on-chain.
 *
 * Las cartas en escrow siguen contando para el staking pasivo (el backend las contabiliza).
 *
 * Al disolver una tabla (desarmar):
 *   1. Se quema el NFT de Tabla.
 *   2. Se devuelven 15 cartas al dueño (1 se destruye aleatoriamente según la lógica off-chain).
 */
contract TablasLoteria is ERC721, ERC1155Holder, Ownable {
    address public gameController;
    IERC1155 public cartasContract;
    uint256 private _nextTableId;

    // El layout de 16 card IDs (carta de lotería ID 1-54) por tabla
    mapping(uint256 => uint256[16]) public layoutOf;
    // Cuántos juegos ha jugado cada tabla
    mapping(uint256 => uint256) public gamesPlayed;
    mapping(uint256 => uint256) public gamesWon;
    // XP de cada tabla
    mapping(uint256 => uint256) public xpOf;

    string private _baseTokenURI;

    event TablaCreada(uint256 indexed tableId, address indexed owner, uint256[16] cardLayout);
    event TableDisuelta(uint256 indexed tableId, address indexed owner, uint256 cardDestroyedIndex);
    event StatsTablaActualizados(uint256 indexed tableId, uint256 gamesPlayed, uint256 gamesWon, uint256 xp);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "TablasLoteria: No autorizado");
        _;
    }

    constructor(address initialOwner, address _cartas, string memory baseURI)
        ERC721("Axolotto Tablas", "TABLA")
        Ownable(initialOwner)
    {
        cartasContract = IERC1155(_cartas);
        _baseTokenURI = baseURI;
        _nextTableId = 1;
    }

    function setGameController(address _controller) external onlyOwner {
        gameController = _controller;
    }

    function setBaseURI(string memory baseURI) external onlyOwner {
        _baseTokenURI = baseURI;
    }

    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    /**
     * @notice Crea una nueva tabla transfiriendo las 16 cartas al contrato (escrow).
     * @param to        Dirección del jugador dueño de la tabla
     * @param cardIds   Array de 16 IDs de cartas de lotería (valores 1-54)
     *
     * IMPORTANTE: El jugador debe haber aprobado a este contrato previamente con
     *             setApprovalForAll en el contrato CartasLoteria.
     */
    function createBoard(address to, uint256[16] calldata cardIds)
        external
        onlyController
        returns (uint256)
    {
        // Validar que haya exactamente 16 cartas válidas
        for (uint256 i = 0; i < 16; i++) {
            require(cardIds[i] >= 1 && cardIds[i] <= 54, "TablasLoteria: Carta invalida");
        }

        // Preparar arrays para transferencia batch
        uint256[] memory ids     = new uint256[](16);
        uint256[] memory amounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) {
            ids[i]     = cardIds[i];
            amounts[i] = 1;
        }

        // Transferir las 16 cartas del jugador a este contrato (escrow)
        cartasContract.safeBatchTransferFrom(to, address(this), ids, amounts, "");

        // Acuñar el NFT de Tabla
        uint256 tableId = _nextTableId++;
        _safeMint(to, tableId);
        layoutOf[tableId] = cardIds;

        emit TablaCreada(tableId, to, cardIds);
        return tableId;
    }

    /**
     * @notice Disuelve una tabla, devolviendo 15 cartas y destruyendo 1.
     * @param tableId           NFT de la tabla a disolver
     * @param destroyCardIndex  Índice (0-15) de la carta que se destruye (decidido por el backend)
     */
    function dissolveBoard(uint256 tableId, uint256 destroyCardIndex)
        external
        onlyController
    {
        address tableOwner = ownerOf(tableId);
        require(destroyCardIndex < 16, "TablasLoteria: Indice invalido");

        uint256[16] memory cards = layoutOf[tableId];

        // Construir arrays de devolución (15 cartas)
        uint256[] memory returnIds     = new uint256[](15);
        uint256[] memory returnAmounts = new uint256[](15);
        uint256 j = 0;
        for (uint256 i = 0; i < 16; i++) {
            if (i != destroyCardIndex) {
                returnIds[j]     = cards[i];
                returnAmounts[j] = 1;
                j++;
            }
        }

        // Quemar el NFT de tabla
        _burn(tableId);

        // Devolver 15 cartas al dueño
        cartasContract.safeBatchTransferFrom(address(this), tableOwner, returnIds, returnAmounts, "");

        emit TableDisuelta(tableId, tableOwner, destroyCardIndex);
    }

    /**
     * @notice Disuelve una tabla de manera segura, devolviendo las 16 cartas al dueño.
     * @param tableId           NFT de la tabla a disolver
     */
    function dissolveBoardSafe(uint256 tableId)
        external
        onlyController
    {
        address tableOwner = ownerOf(tableId);
        uint256[16] memory layoutCards = layoutOf[tableId];

        uint256[] memory returnIds     = new uint256[](16);
        uint256[] memory returnAmounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) {
            returnIds[i]     = layoutCards[i];
            returnAmounts[i] = 1;
        }

        // Quemar el NFT de tabla
        _burn(tableId);

        // Devolver 16 cartas al dueño
        cartasContract.safeBatchTransferFrom(address(this), tableOwner, returnIds, returnAmounts, "");

        emit TableDisuelta(tableId, tableOwner, 999); // 999 indica desarmado seguro sin pérdida
    }


    /**
     * @notice Crea una tabla NPC sin requerir transferencia de cartas ERC-1155.
     *         El sistema no tiene cartas reales en escrow para los bots; esta función
     *         acuña el NFT de Tabla directamente, registrando el layout on-chain.
     * @param to      Dirección que recibirá el NFT (wallet NPC)
     * @param cardIds Array de 16 IDs de cartas (valores 1-54)
     * @dev  Solo puede llamarse por el owner del contrato (deployer / system wallet).
     *       NO transfiere ni bloquea cartas ERC-1155.
     */
    function createNPCBoard(address to, uint256[16] calldata cardIds)
        external
        onlyOwner
        returns (uint256 tableId)
    {
        for (uint256 i = 0; i < 16; i++) {
            require(cardIds[i] >= 1 && cardIds[i] <= 54, "TablasLoteria: Carta invalida");
        }
        tableId = _nextTableId++;
        layoutOf[tableId] = cardIds;
        _safeMint(to, tableId);
        emit TablaCreada(tableId, to, cardIds);
    }

    /// @notice Actualiza stats de la tabla después de un juego
    function updateTableStats(uint256 tableId, bool won, uint256 xpGained) external onlyController {
        gamesPlayed[tableId]++;
        if (won) gamesWon[tableId]++;
        xpOf[tableId] += xpGained;
        emit StatsTablaActualizados(tableId, gamesPlayed[tableId], gamesWon[tableId], xpOf[tableId]);
    }

    function transferBoard(address from, address to, uint256 tableId) external onlyController {
        require(ownerOf(tableId) == from, "TablasLoteria: No es el dueno");
        _transfer(from, to, tableId);
    }

    function getLayout(uint256 tableId) external view returns (uint256[16] memory) {
        return layoutOf[tableId];
    }

    function totalMinted() external view returns (uint256) {
        return _nextTableId - 1;
    }

    // Necesario para que el contrato pueda recibir ERC1155 (escrow)
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC1155Holder)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
