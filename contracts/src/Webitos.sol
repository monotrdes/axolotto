// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Webitos
 * @notice Huevos NFT únicos (ERC-721). Cada Webito tiene un ID único.
 *         Se incuban haciendo "cariñitos" en el frontend para nacer como Axolotito.
 *         Fases 1-3 con oferta limitada (420 / 1260 / 2520 por fase).
 */
contract Webitos is ERC721, Ownable {
    address public gameController;
    uint256 private _nextTokenId;

    // Fase del webito por tokenId (1, 2 o 3)
    mapping(uint256 => uint8) public webitoFase;

    string private _baseTokenURI;

    event WebitoMinted(uint256 indexed tokenId, address indexed to, uint8 fase);

    modifier onlyController() {
        require(msg.sender == gameController || msg.sender == owner(), "Webitos: No autorizado");
        _;
    }

    constructor(address initialOwner, string memory baseURI)
        ERC721("Axolotto Webitos", "WEBITO")
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

    /// @notice Acuña un nuevo Webito para un jugador
    function mintWebito(address to, uint8 fase) external onlyController returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        webitoFase[tokenId] = fase;
        _safeMint(to, tokenId);
        emit WebitoMinted(tokenId, to, fase);
        return tokenId;
    }

    /// @notice Quema el Webito al eclosionar (se convierte en Axolotito)
    function burnWebito(uint256 tokenId) external onlyController {
        _burn(tokenId);
    }

    function totalMinted() external view returns (uint256) {
        return _nextTokenId - 1;
    }
}
