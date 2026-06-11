// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MarketEscrow
 * @notice Custodia de NFTs artesanales (Axolotitos, Tablas) durante ventas P2P
 *         pagadas en fiat off-chain (Tianguis P2P).
 *
 * El contrato NO maneja dinero: el pago ocurre en una pasarela fiat
 * (Mercado Pago / Stripe, o simulada) y el backend —único `operator`—
 * ordena la liberación tras conciliar el webhook de pago con esta custodia.
 * El contrato es el ledger auditable: cada liberación registra el
 * `paymentRef` de la pasarela en el evento Released.
 *
 * Ciclo de vida de un listing (terminal, sin reuso de id):
 *   None → Listed → Released | Refunded
 */
contract MarketEscrow is ERC721Holder, ReentrancyGuard, Pausable, Ownable {

    enum Status { None, Listed, Released, Refunded }

    struct Listing {
        address seller;       // embedded wallet del vendedor
        address nftContract;
        uint256 tokenId;
        uint256 priceAxf;     // unidad mínima (6 decimales), informativo para auditoría
        Status  status;
        uint64  listedAt;
    }

    mapping(bytes32 => Listing) private _listings;
    address public operator;  // backend signer

    event Deposited(bytes32 indexed listingId, address indexed seller, address nftContract, uint256 tokenId, uint256 priceAxf);
    event Released(bytes32 indexed listingId, address indexed buyer, bytes32 paymentRef);
    event Refunded(bytes32 indexed listingId, address indexed seller);
    event OperatorChanged(address indexed previousOperator, address indexed newOperator);

    error NotOperator();
    error ListingIdAlreadyUsed(bytes32 listingId);
    error ListingNotActive(bytes32 listingId);
    error ZeroAddress();

    modifier onlyOperator() {
        if (msg.sender != operator) revert NotOperator();
        _;
    }

    constructor(address initialOwner, address initialOperator) Ownable(initialOwner) {
        if (initialOperator == address(0)) revert ZeroAddress();
        operator = initialOperator;
    }

    // ── Núcleo ──────────────────────────────────────────────────────────

    /// @notice Deposita el NFT del vendedor en custodia y abre el listing.
    /// @dev Requiere aprobación previa del NFT hacia este contrato
    ///      (la firma el backend vía la embedded wallet del vendedor).
    function depositAndList(
        bytes32 listingId,
        address seller,
        address nftContract,
        uint256 tokenId,
        uint256 priceAxf
    ) external onlyOperator whenNotPaused nonReentrant {
        if (seller == address(0) || nftContract == address(0)) revert ZeroAddress();
        if (_listings[listingId].status != Status.None) revert ListingIdAlreadyUsed(listingId);

        _listings[listingId] = Listing({
            seller: seller,
            nftContract: nftContract,
            tokenId: tokenId,
            priceAxf: priceAxf,
            status: Status.Listed,
            listedAt: uint64(block.timestamp)
        });

        IERC721(nftContract).safeTransferFrom(seller, address(this), tokenId);
        emit Deposited(listingId, seller, nftContract, tokenId, priceAxf);
    }

    /// @notice Libera el NFT al comprador tras conciliar el pago fiat.
    /// @param paymentRef Referencia del pago en la pasarela (auditoría cruzada).
    function release(bytes32 listingId, address buyer, bytes32 paymentRef)
        external onlyOperator whenNotPaused nonReentrant
    {
        if (buyer == address(0)) revert ZeroAddress();
        Listing storage l = _listings[listingId];
        if (l.status != Status.Listed) revert ListingNotActive(listingId);

        l.status = Status.Released;
        IERC721(l.nftContract).safeTransferFrom(address(this), buyer, l.tokenId);
        emit Released(listingId, buyer, paymentRef);
    }

    /// @notice Devuelve el NFT al vendedor original (cancelación o pago fallido).
    function refund(bytes32 listingId) external onlyOperator nonReentrant {
        Listing storage l = _listings[listingId];
        if (l.status != Status.Listed) revert ListingNotActive(listingId);

        l.status = Status.Refunded;
        IERC721(l.nftContract).safeTransferFrom(address(this), l.seller, l.tokenId);
        emit Refunded(listingId, l.seller);
    }

    // ── Administración / emergencia ─────────────────────────────────────

    function setOperator(address newOperator) external onlyOwner {
        if (newOperator == address(0)) revert ZeroAddress();
        emit OperatorChanged(operator, newOperator);
        operator = newOperator;
    }

    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    /// @notice Solo en pausa: devuelve el NFT al vendedor registrado.
    ///         Nunca puede enviarse a owner/operator — invariante de custodia.
    function emergencyWithdraw(bytes32 listingId) external onlyOwner whenPaused nonReentrant {
        Listing storage l = _listings[listingId];
        if (l.status != Status.Listed) revert ListingNotActive(listingId);

        l.status = Status.Refunded;
        IERC721(l.nftContract).safeTransferFrom(address(this), l.seller, l.tokenId);
        emit Refunded(listingId, l.seller);
    }

    // ── Vistas ──────────────────────────────────────────────────────────

    function getListing(bytes32 listingId) external view returns (Listing memory) {
        return _listings[listingId];
    }
}
