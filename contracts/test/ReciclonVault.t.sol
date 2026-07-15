// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "../src/CartasLoteria.sol";
import "../src/ReciclonVault.sol";

contract ForeignCards is ERC1155 {
    constructor() ERC1155("") {}

    function mint(address to, uint256 id, uint256 amount) external {
        _mint(to, id, amount, "");
    }
}

contract ReciclonVaultTest is Test {
    CartasLoteria internal cartas;
    ReciclonVault internal vault;
    ForeignCards internal foreignCards;

    address internal admin = makeAddr("admin");
    address internal controller = makeAddr("controller");
    address internal player = makeAddr("player");

    function setUp() public {
        vm.startPrank(admin);
        cartas = new CartasLoteria(admin, "http://localhost/carta/{id}");
        vault = new ReciclonVault(address(cartas));
        cartas.setGameController(controller);
        cartas.setReciclonVault(address(vault));
        vm.stopPrank();

        foreignCards = new ForeignCards();
    }

    function test_receiveSingleCard_tracksRealCustody() public {
        _mintCards(player, _single(1), _single(3));

        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, 2, "");

        assertEq(cartas.balanceOf(address(vault), 1), 2);
        assertEq(vault.totalCardsReceived(), 2);
        assertEq(vault.totalCardsBurned(), 0);
        assertEq(vault.totalCardsHeld(), 2);
        _assertAccountingInvariant();
    }

    function test_wiringConfiguresVaultExactlyOnce() public {
        assertEq(cartas.reciclonVault(), address(vault));
        assertEq(vault.cartasLoteria(), address(cartas));
        assertEq(vault.owner(), admin);

        vm.expectRevert("CartasLoteria: vault ya configurado");
        vm.prank(admin);
        cartas.setReciclonVault(address(vault));
    }

    function test_receiveBatchCards_tracksRealCustody() public {
        uint256[] memory ids = new uint256[](2);
        uint256[] memory amounts = new uint256[](2);
        ids[0] = 1;
        ids[1] = 2;
        amounts[0] = 2;
        amounts[1] = 3;
        _mintCards(player, ids, amounts);

        vm.prank(player);
        cartas.safeBatchTransferFrom(player, address(vault), ids, amounts, "");

        assertEq(cartas.balanceOf(address(vault), 1), 2);
        assertEq(cartas.balanceOf(address(vault), 2), 3);
        assertEq(vault.totalCardsReceived(), 5);
        assertEq(vault.totalCardsBurned(), 0);
        assertEq(vault.totalCardsHeld(), 5);
        _assertAccountingInvariant();
    }

    function test_rejectsForeignERC1155() public {
        foreignCards.mint(player, 1, 1);

        vm.expectRevert(abi.encodeWithSelector(ReciclonVault.UnauthorizedToken.selector, address(foreignCards)));
        vm.prank(player);
        foreignCards.safeTransferFrom(player, address(vault), 1, 1, "");

        assertEq(vault.totalCardsReceived(), 0);
        assertEq(vault.totalCardsBurned(), 0);
        assertEq(vault.totalCardsHeld(), 0);
    }

    function test_batchBurn_reducesVaultBalanceAndSupply() public {
        _mintCards(player, _single(1), _single(3));
        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, 2, "");

        vm.prank(admin);
        vault.batchBurn(_single(1), _single(1));

        assertEq(cartas.balanceOf(player, 1), 1);
        assertEq(cartas.balanceOf(address(vault), 1), 1);
        assertEq(cartas.totalSupplyOf(1), 2);
        assertEq(vault.totalCardsReceived(), 2);
        assertEq(vault.totalCardsBurned(), 1);
        assertEq(vault.totalCardsHeld(), 1);
        _assertAccountingInvariant();
    }

    function test_batchBurn_rejectsNonOwnerOperator() public {
        _mintCards(player, _single(1), _single(1));
        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, 1, "");

        vm.expectRevert(abi.encodeWithSignature("OwnableUnauthorizedAccount(address)", controller));
        vm.prank(controller);
        vault.batchBurn(_single(1), _single(1));

        assertEq(cartas.balanceOf(address(vault), 1), 1);
        assertEq(vault.totalCardsHeld(), 1);
        _assertAccountingInvariant();
    }

    function test_batchBurn_cannotBurnAnotherAccountBalance() public {
        _mintCards(player, _single(1), _single(2));
        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, 1, "");

        vm.expectRevert("ReciclonVault: saldo insuficiente");
        vm.prank(admin);
        vault.batchBurn(_single(1), _single(2));

        assertEq(cartas.balanceOf(player, 1), 1);
        assertEq(cartas.balanceOf(address(vault), 1), 1);
        assertEq(cartas.totalSupplyOf(1), 2);
        assertEq(vault.totalCardsReceived(), 1);
        assertEq(vault.totalCardsBurned(), 0);
        assertEq(vault.totalCardsHeld(), 1);
        _assertAccountingInvariant();
    }

    function test_genericControllerPathsCannotMutateVaultCustody() public {
        _mintCards(player, _single(1), _single(1));
        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, 1, "");

        vm.expectRevert("CartasLoteria: usar burnVaultCards");
        vm.prank(controller);
        cartas.burnCard(address(vault), 1, 1);

        vm.expectRevert("CartasLoteria: vault no transferible");
        vm.prank(controller);
        cartas.transferCard(address(vault), player, 1, 1);

        assertEq(cartas.balanceOf(address(vault), 1), 1);
        assertEq(vault.totalCardsHeld(), 1);
        _assertAccountingInvariant();
    }

    function test_registerReceiptIsNeutralized() public {
        vm.expectRevert(ReciclonVault.DeclarativeAccountingDisabled.selector);
        vm.prank(controller);
        vault.registerReceipt(_single(1), _single(1));

        assertEq(vault.totalCardsReceived(), 0);
        assertEq(vault.totalCardsBurned(), 0);
        assertEq(vault.totalCardsHeld(), 0);
    }

    function testFuzz_receivedEqualsBurnedPlusHeld(uint8 receivedSeed, uint8 burnedSeed) public {
        uint256 received = bound(uint256(receivedSeed), 1, 100);
        uint256 burned = bound(uint256(burnedSeed), 0, received);
        _mintCards(player, _single(1), _single(received));

        vm.prank(player);
        cartas.safeTransferFrom(player, address(vault), 1, received, "");

        if (burned > 0) {
            vm.prank(admin);
            vault.batchBurn(_single(1), _single(burned));
        }

        assertEq(cartas.balanceOf(address(vault), 1), received - burned);
        _assertAccountingInvariant();
    }

    function _mintCards(address to, uint256[] memory ids, uint256[] memory amounts) internal {
        vm.prank(controller);
        cartas.mintCards(to, ids, amounts);
    }

    function _single(uint256 value) internal pure returns (uint256[] memory values) {
        values = new uint256[](1);
        values[0] = value;
    }

    function _assertAccountingInvariant() internal view {
        assertEq(vault.totalCardsReceived(), vault.totalCardsBurned() + vault.totalCardsHeld());
    }
}
