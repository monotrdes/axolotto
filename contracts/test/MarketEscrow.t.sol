// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "../src/MarketEscrow.sol";

contract MockNFT is ERC721 {
    constructor() ERC721("Mock", "MOCK") {}
    function mint(address to, uint256 tokenId) external { _mint(to, tokenId); }
}

contract MarketEscrowTest is Test {
    MarketEscrow escrow;
    MockNFT nft;

    address owner    = makeAddr("owner");
    address operator = makeAddr("operator");
    address seller   = makeAddr("seller");
    address buyer    = makeAddr("buyer");
    address attacker = makeAddr("attacker");

    bytes32 constant LISTING_ID  = keccak256("listing-1");
    bytes32 constant PAYMENT_REF = keccak256("mock_payment_ref");
    uint256 constant TOKEN_ID = 7;
    uint256 constant PRICE_AXF = 500 * 1e6;

    event Released(bytes32 indexed listingId, address indexed buyer, bytes32 paymentRef);

    function setUp() public {
        escrow = new MarketEscrow(owner, operator);
        nft = new MockNFT();
        nft.mint(seller, TOKEN_ID);
        // El backend firma esta aprobación vía la embedded wallet del vendedor
        vm.prank(seller);
        nft.setApprovalForAll(address(escrow), true);
    }

    function _deposit() internal {
        vm.prank(operator);
        escrow.depositAndList(LISTING_ID, seller, address(nft), TOKEN_ID, PRICE_AXF);
    }

    // ── Depósito ────────────────────────────────────────────────────────

    function test_depositAndList_custodiesNft() public {
        _deposit();
        assertEq(nft.ownerOf(TOKEN_ID), address(escrow));
        MarketEscrow.Listing memory l = escrow.getListing(LISTING_ID);
        assertEq(l.seller, seller);
        assertEq(uint8(l.status), uint8(MarketEscrow.Status.Listed));
        assertEq(l.priceAxf, PRICE_AXF);
    }

    function test_depositAndList_revertsForNonOperator() public {
        vm.prank(attacker);
        vm.expectRevert(MarketEscrow.NotOperator.selector);
        escrow.depositAndList(LISTING_ID, seller, address(nft), TOKEN_ID, PRICE_AXF);
    }

    // Invariante 1: un listingId jamás se reutiliza (estado terminal)
    function test_listingId_neverReused_afterRelease() public {
        _deposit();
        vm.prank(operator);
        escrow.release(LISTING_ID, buyer, PAYMENT_REF);

        // El buyer devuelve el NFT al seller para intentar relistear con el mismo id
        vm.prank(buyer);
        nft.transferFrom(buyer, seller, TOKEN_ID);

        vm.prank(operator);
        vm.expectRevert(abi.encodeWithSelector(MarketEscrow.ListingIdAlreadyUsed.selector, LISTING_ID));
        escrow.depositAndList(LISTING_ID, seller, address(nft), TOKEN_ID, PRICE_AXF);
    }

    // ── Liberación ──────────────────────────────────────────────────────

    function test_release_transfersToBuyer_andEmitsPaymentRef() public {
        _deposit();
        vm.expectEmit(true, true, false, true);
        emit Released(LISTING_ID, buyer, PAYMENT_REF);
        vm.prank(operator);
        escrow.release(LISTING_ID, buyer, PAYMENT_REF);
        assertEq(nft.ownerOf(TOKEN_ID), buyer);
    }

    function test_release_revertsForNonOperator() public {
        _deposit();
        vm.prank(attacker);
        vm.expectRevert(MarketEscrow.NotOperator.selector);
        escrow.release(LISTING_ID, attacker, PAYMENT_REF);
    }

    // Invariante 2: release y refund son mutuamente excluyentes
    function test_refund_revertsAfterRelease() public {
        _deposit();
        vm.startPrank(operator);
        escrow.release(LISTING_ID, buyer, PAYMENT_REF);
        vm.expectRevert(abi.encodeWithSelector(MarketEscrow.ListingNotActive.selector, LISTING_ID));
        escrow.refund(LISTING_ID);
        vm.stopPrank();
    }

    function test_release_revertsAfterRefund() public {
        _deposit();
        vm.startPrank(operator);
        escrow.refund(LISTING_ID);
        vm.expectRevert(abi.encodeWithSelector(MarketEscrow.ListingNotActive.selector, LISTING_ID));
        escrow.release(LISTING_ID, buyer, PAYMENT_REF);
        vm.stopPrank();
    }

    // ── Refund ──────────────────────────────────────────────────────────

    function test_refund_returnsToOriginalSeller() public {
        _deposit();
        vm.prank(operator);
        escrow.refund(LISTING_ID);
        assertEq(nft.ownerOf(TOKEN_ID), seller);
        assertEq(uint8(escrow.getListing(LISTING_ID).status), uint8(MarketEscrow.Status.Refunded));
    }

    // ── Pausa / emergencia ──────────────────────────────────────────────

    function test_paused_blocksDepositAndRelease() public {
        _deposit();
        vm.prank(owner);
        escrow.pause();

        vm.startPrank(operator);
        vm.expectRevert(Pausable.EnforcedPause.selector);
        escrow.depositAndList(keccak256("listing-2"), seller, address(nft), TOKEN_ID, PRICE_AXF);
        vm.expectRevert(Pausable.EnforcedPause.selector);
        escrow.release(LISTING_ID, buyer, PAYMENT_REF);
        vm.stopPrank();
    }

    // Invariante 3: el NFT nunca puede salir hacia owner/operator —
    // emergencyWithdraw solo devuelve al seller registrado.
    function test_emergencyWithdraw_onlyWhenPaused_returnsToSeller() public {
        _deposit();

        vm.prank(owner);
        vm.expectRevert(Pausable.ExpectedPause.selector);
        escrow.emergencyWithdraw(LISTING_ID);

        vm.prank(owner);
        escrow.pause();
        vm.prank(owner);
        escrow.emergencyWithdraw(LISTING_ID);
        assertEq(nft.ownerOf(TOKEN_ID), seller);
    }

    function test_emergencyWithdraw_revertsForNonOwner() public {
        _deposit();
        vm.prank(owner);
        escrow.pause();
        vm.prank(operator);
        vm.expectRevert(abi.encodeWithSelector(Ownable.OwnableUnauthorizedAccount.selector, operator));
        escrow.emergencyWithdraw(LISTING_ID);
    }

    // ── Operator admin ──────────────────────────────────────────────────

    function test_setOperator_onlyOwner() public {
        vm.prank(attacker);
        vm.expectRevert(abi.encodeWithSelector(Ownable.OwnableUnauthorizedAccount.selector, attacker));
        escrow.setOperator(attacker);

        vm.prank(owner);
        escrow.setOperator(buyer);
        assertEq(escrow.operator(), buyer);
    }
}
