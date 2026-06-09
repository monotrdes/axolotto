// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Axolotitos
 * @notice Personajes NFT únicos (ERC-721) con DNA y stats almacenados on-chain.
 *         La blockchain es la fuente de verdad para ownership y stats al momento
 *         de compra/venta. El backend sincroniza la DB desde el contrato.
 *
 * Stats (escala 0-100 en puntos enteros, excepto stamina 50-200):
 *   salinity, luck, focus, stamina, charisma, agility, wisdom, strength
 *
 * DNA: uint256 generado por el backend al eclosionar el Webito.
 */
contract Axolotitos is ERC721, Ownable {
    address public gameController;
    uint256 private _nextTokenId;

    struct Stats {
        uint8 salinity;   // 0-100 mala suerte
        uint8 luck;       // 0-100 drops/críticos
        uint8 focus;      // 0-100 precisión de cartas
        uint8 stamina;    // 50-200 (se guarda como uint8 pero puede ir hasta 200 → usamos uint16)
        uint8 charisma;   // 0-100 descuentos
        uint8 agility;    // 0-100 velocidad
        uint8 wisdom;     // 0-100 sinergia de tabla
        uint8 strength;   // 0-100 resistencia
    }

    // Stats almacenados on-chain por tokenId
    mapping(uint256 => uint256) public dnaOf;
    mapping(uint256 => Stats)   public statsOf;

    // Traits visuales (codificados como índices para ahorrar gas)
    struct Traits {
        uint8 skinColor;    // 0=pink, 1=gray_light, 2=gray_dark, 3=gold, 4=astral
        uint8 gillType;     // 0=short, 1=normal, 2=feathery, 3=crown, 4=phoenix
        uint8 eyeType;      // 0=cute, 1=derp, 2=dreamer, 3=cool, 4=zen
        uint8 mouthType;    // 0=flat, 1=smile, 2=fang, 3=rockstar, 4=divine
        uint8 tailType;     // 0=standard, 1=wavy, 2=betta, 3=plasma
        uint8 foreheadType; // 0=none, 1=stripes, 2=gem, 3=halo
        uint8 limbType;     // 0=soft, 1=claws, 2=scales, 3=coral
    }
    mapping(uint256 => Traits) public traitsOf;

    string private _baseTokenURI;

    event AxolotitoNacido(uint256 indexed tokenId, address indexed owner, uint256 dna);
    event StatsActualizados(uint256 indexed tokenId);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Axolotitos: No autorizado");
        _;
    }

    constructor(address initialOwner, string memory baseURI)
        ERC721("Axolotto Axolotitos", "AXOLOTO")
        Ownable(initialOwner)
    {
        _baseTokenURI = baseURI;
        _nextTokenId = 1;
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
     * @notice Acuña un nuevo Axolotito con DNA, stats y traits on-chain.
     * @param to          Dirección del jugador
     * @param dna         Uint256 único representando la secuencia genética
     * @param stats       Struct con los 8 stats del personaje
     * @param traits      Struct con los 7 rasgos visuales
     * @return tokenId    ID del NFT acuñado
     */
    function mintAxolotito(
        address to,
        uint256 dna,
        Stats calldata stats,
        Traits calldata traits
    ) external onlyController returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        dnaOf[tokenId]    = dna;
        statsOf[tokenId]  = stats;
        traitsOf[tokenId] = traits;
        emit AxolotitoNacido(tokenId, to, dna);
        return tokenId;
    }

    /**
     * @notice Actualiza los stats de un Axolotito (nivel, XP, energía, etc.)
     *         Solo el GameController puede actualizar para evitar trampas.
     */
    function updateStats(uint256 tokenId, Stats calldata stats) external onlyController {
        require(_ownerOf(tokenId) != address(0), "Axolotitos: Token no existe");
        statsOf[tokenId] = stats;
        emit StatsActualizados(tokenId);
    }

    function transferAxolotito(address from, address to, uint256 tokenId) external onlyController {
        require(ownerOf(tokenId) == from, "Axolotitos: No es el dueno");
        _transfer(from, to, tokenId);
    }

    function totalMinted() external view returns (uint256) {
        return _nextTokenId - 1;
    }

    /// @notice Getter explícito para los stats (evita problema de deserialización de structs en Solidity)
    function getStats(uint256 tokenId) external view returns (Stats memory) {
        return statsOf[tokenId];
    }

    /// @notice Getter explícito para los traits visuales
    function getTraits(uint256 tokenId) external view returns (Traits memory) {
        return traitsOf[tokenId];
    }
}
