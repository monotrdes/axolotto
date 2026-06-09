// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/Frijolito.sol";
import "../src/Axoficha.sol";
import "../src/Webitos.sol";
import "../src/Axolotitos.sol";
import "../src/CartasLoteria.sol";
import "../src/Sobrecito.sol";
import "../src/TablasLoteria.sol";
import "../src/Consumables.sol";
import "../src/GameController.sol";

contract GameContractsTest is Test {
    Frijolito     frj;
    Axoficha      axf;
    Webitos       webitosC;
    Axolotitos    axolotitoC;
    CartasLoteria cartasC;
    Sobrecito     sobrecitosC;
    TablasLoteria tablasC;
    Consumables   consumablesC;
    GameController controller;

    address treasury = address(0x1);  // Wallet del admin/backend
    address player   = address(0x2);  // Jugador de prueba

    function setUp() public {
        vm.startPrank(treasury);

        frj            = new Frijolito(treasury);
        axf            = new Axoficha(treasury);
        webitosC       = new Webitos(treasury, "http://localhost/webito/");
        axolotitoC     = new Axolotitos(treasury, "http://localhost/axolotito/");
        cartasC        = new CartasLoteria(treasury, "http://localhost/carta/{id}");
        sobrecitosC    = new Sobrecito(treasury, "http://localhost/sobrecito/{id}");
        consumablesC   = new Consumables(treasury, "http://localhost/consumable/{id}");
        tablasC        = new TablasLoteria(treasury, address(cartasC), "http://localhost/tabla/");
        controller     = new GameController(treasury);

        controller.configurar(
            address(frj), address(axf), address(webitosC), address(axolotitoC),
            address(cartasC), address(sobrecitosC), address(tablasC), address(consumablesC)
        );

        frj.setGameController(address(controller));
        axf.setGameController(address(controller));
        webitosC.setGameController(address(controller));
        axolotitoC.setGameController(address(controller));
        cartasC.setGameController(address(controller));
        cartasC.setTablasContract(address(tablasC));
        sobrecitosC.setGameController(address(controller));
        tablasC.setGameController(address(controller));
        consumablesC.setGameController(address(controller));

        vm.stopPrank();
    }

    // ── Tests de tokens ERC-20 ────────────────────────────────────────────────

    function test_DepositarGAL() public {
        vm.prank(treasury);
        controller.depositarFRJ(player, 1000 ether);
        assertEq(frj.balanceOf(player), 1000 ether);
    }

    function test_CobrarGAL() public {
        vm.startPrank(treasury);
        controller.depositarFRJ(player, 1000 ether);
        controller.cobrarFRJ(player, 100 ether);
        vm.stopPrank();
        assertEq(frj.balanceOf(player), 900 ether);
    }

    function test_SoloControllerPuedeMintearGAL() public {
        vm.expectRevert();
        vm.prank(player); // player intenta mintear directamente
        frj.mint(player, 1000 ether);
    }

    function testFuzz_TransferGAL(address to, uint256 amount) public {
        vm.assume(to != address(0));
        vm.assume(to != address(frj));
        vm.assume(to != address(controller));
        vm.assume(to != player);
        vm.assume(to != treasury);
        
        // Limitar amount para evitar desbordamiento del total supply en pruebas de stress
        amount = bound(amount, 1, 1000000000 ether);

        vm.prank(treasury);
        controller.depositarFRJ(player, amount);
        
        assertEq(frj.balanceOf(player), amount);
        
        vm.prank(player);
        frj.transfer(to, amount);
        
        assertEq(frj.balanceOf(to), amount);
        assertEq(frj.balanceOf(player), 0);
    }

    function testFuzz_TransferAXG(address to, uint256 amount) public {
        vm.assume(to != address(0));
        vm.assume(to != address(axf));
        vm.assume(to != address(controller));
        vm.assume(to != player);
        vm.assume(to != treasury);
        
        amount = bound(amount, 1, 1000000000 ether);

        vm.prank(treasury);
        controller.depositarAXF(player, amount);
        
        assertEq(axf.balanceOf(player), amount);
        
        vm.prank(player);
        axf.transfer(to, amount);
        
        assertEq(axf.balanceOf(to), amount);
        assertEq(axf.balanceOf(player), 0);
    }

    // ── Tests de Webitos ──────────────────────────────────────────────────────

    function test_ComprarWebito() public {
        vm.startPrank(treasury);
        controller.depositarAXF(player, 500 ether);
        uint256 tokenId = controller.comprarWebito(player, 1, 50 ether); // 50 AXF
        vm.stopPrank();

        assertEq(webitosC.ownerOf(tokenId), player);
        assertEq(axf.balanceOf(player), 450 ether);
        assertEq(webitosC.webitoFase(tokenId), 1);
    }

    // ── Tests de Sobrecitos y apertura ──────────────────────────────────────────

    function test_ComprarYAbrirBooster() public {
        vm.startPrank(treasury);
        controller.depositarAXF(player, 500 ether);
        controller.comprarSobrecito(player, 1, 1, 50 ether); // 1 booster fase 1

        assertEq(sobrecitosC.balanceOf(player, 1), 1);

        uint256[] memory ids = new uint256[](7);
        ids[0] = 1; ids[1] = 5; ids[2] = 10; ids[3] = 15;
        ids[4] = 20; ids[5] = 25; ids[6] = 30;
        controller.abrirSobrecito(player, 1, ids);
        vm.stopPrank();

        // El sobre se quemó
        assertEq(sobrecitosC.balanceOf(player, 1), 0);
        // Las cartas llegaron
        assertEq(cartasC.balanceOf(player, 1), 1);
        assertEq(cartasC.balanceOf(player, 5), 1);
    }

    // ── Tests de Eclosión ─────────────────────────────────────────────────────

    function test_EclosionarWebito() public {
        vm.startPrank(treasury);
        controller.depositarAXF(player, 500 ether);
        uint256 webitoId = controller.comprarWebito(player, 1, 50 ether);

        Axolotitos.Stats memory stats = Axolotitos.Stats({
            salinity: 5, luck: 50, focus: 70, stamina: 100,
            charisma: 20, agility: 30, wisdom: 40, strength: 60
        });
        Axolotitos.Traits memory traits = Axolotitos.Traits({
            skinColor: 0, gillType: 1, eyeType: 2, mouthType: 1,
            tailType: 0, foreheadType: 0, limbType: 0
        });

        uint256 axolotitoId = controller.eclosionar(player, webitoId, 123456789, stats, traits);
        vm.stopPrank();

        // Webito quemado
        vm.expectRevert();
        webitosC.ownerOf(webitoId);

        // Axolotito creado con stats on-chain
        assertEq(axolotitoC.ownerOf(axolotitoId), player);
        assertEq(axolotitoC.dnaOf(axolotitoId), 123456789);
        Axolotitos.Stats memory s = axolotitoC.getStats(axolotitoId);
        assertEq(s.focus, 70);
        assertEq(s.luck, 50);
    }

    // ── Tests de Tabla con Escrow ─────────────────────────────────────────────

    function test_CrearTablaConEscrow() public {
        vm.startPrank(treasury);
        controller.depositarFRJ(player, 10000 ether);

        // Mint 16 cartas únicas para el jugador
        uint256[] memory cardIds = new uint256[](16);
        uint256[] memory amounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) {
            cardIds[i] = i + 1; // cartas 1-16
            amounts[i] = 1;
        }
        controller.mintCartas(player, cardIds, amounts);

        // El jugador aprueba al contrato de Tablas para mover sus cartas (escrow)
        vm.stopPrank();
        vm.prank(player);
        cartasC.setApprovalForAll(address(tablasC), true);

        vm.startPrank(treasury);
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;

        uint256 tableId = controller.crearTabla(player, layout, 25 ether); // 25 FRJ
        vm.stopPrank();

        // Las cartas están en el contrato de Tablas (escrow)
        for (uint256 i = 0; i < 16; i++) {
            assertEq(cartasC.balanceOf(address(tablasC), i + 1), 1);
            assertEq(cartasC.balanceOf(player, i + 1), 0);
        }

        // La tabla es un NFT del jugador
        assertEq(tablasC.ownerOf(tableId), player);

        // El layout está guardado on-chain
        uint256[16] memory savedLayout = tablasC.getLayout(tableId);
        assertEq(savedLayout[0], 1);
        assertEq(savedLayout[15], 16);
    }

    function test_DisolverTabla() public {
        vm.startPrank(treasury);
        controller.depositarFRJ(player, 10000 ether);

        // Mint cartas y crear tabla
        uint256[] memory cardIds = new uint256[](16);
        uint256[] memory amounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) { cardIds[i] = i + 1; amounts[i] = 1; }
        controller.mintCartas(player, cardIds, amounts);
        vm.stopPrank();

        vm.prank(player);
        cartasC.setApprovalForAll(address(tablasC), true);

        vm.startPrank(treasury);
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;
        uint256 tableId = controller.crearTabla(player, layout, 25 ether);

        // Disolver tabla — destruir carta índice 0 (carta ID 1)
        tablasC.dissolveBoard(tableId, 0);
        vm.stopPrank();

        // La tabla fue quemada
        vm.expectRevert();
        tablasC.ownerOf(tableId);

        // 15 cartas devueltas (carta 1 destruida, cartas 2-16 devueltas)
        assertEq(cartasC.balanceOf(player, 1), 0); // destruida
        assertEq(cartasC.balanceOf(player, 2), 1); // devuelta
        assertEq(cartasC.balanceOf(player, 16), 1); // devuelta
    }

    function test_DisolverTablaSegura() public {
        vm.startPrank(treasury);
        controller.depositarFRJ(player, 10000 ether);

        // Mint cartas y crear tabla
        uint256[] memory cardIds = new uint256[](16);
        uint256[] memory amounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) { cardIds[i] = i + 1; amounts[i] = 1; }
        controller.mintCartas(player, cardIds, amounts);
        vm.stopPrank();

        vm.prank(player);
        cartasC.setApprovalForAll(address(tablasC), true);

        vm.startPrank(treasury);
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;
        uint256 tableId = controller.crearTabla(player, layout, 25 ether);

        // Disolver tabla de manera segura (con solvente) — todas las 16 cartas devueltas
        tablasC.dissolveBoardSafe(tableId);
        vm.stopPrank();

        // La tabla fue quemada
        vm.expectRevert();
        tablasC.ownerOf(tableId);

        // Las 16 cartas devueltas intactas
        for (uint256 i = 0; i < 16; i++) {
            assertEq(cartasC.balanceOf(player, i + 1), 1);
        }
    }


    // ── Test de flujo completo de partida ─────────────────────────────────────

    function test_PartidaCompleta() public {
        vm.startPrank(treasury);
        controller.depositarFRJ(player, 10000 ether);
        controller.depositarAXF(player, 500 ether);

        // Comprar y abrir booster
        controller.comprarSobrecito(player, 1, 2, 100 ether);
        uint256[] memory cards1 = new uint256[](7);
        cards1[0]=1; cards1[1]=2; cards1[2]=3; cards1[3]=4; cards1[4]=5; cards1[5]=6; cards1[6]=7;
        controller.abrirSobrecito(player, 1, cards1);
        uint256[] memory cards2 = new uint256[](7);
        cards2[0]=8; cards2[1]=9; cards2[2]=10; cards2[3]=11; cards2[4]=12; cards2[5]=13; cards2[6]=14;
        controller.abrirSobrecito(player, 1, cards2);

        // Mint 2 cartas extra para completar 16
        uint256[] memory extra = new uint256[](2);
        extra[0] = 15; extra[1] = 16;
        uint256[] memory extraAmt = new uint256[](2);
        extraAmt[0] = 1; extraAmt[1] = 1;
        controller.mintCartas(player, extra, extraAmt);
        vm.stopPrank();

        // Aprobar escrow
        vm.prank(player);
        cartasC.setApprovalForAll(address(tablasC), true);

        // Crear tabla
        vm.startPrank(treasury);
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;
        uint256 tableId = controller.crearTabla(player, layout, 25 ether);

        // Comprar webito y eclosionar
        uint256 webitoId = controller.comprarWebito(player, 1, 50 ether);
        Axolotitos.Stats memory stats = Axolotitos.Stats({
            salinity: 5, luck: 60, focus: 75, stamina: 100,
            charisma: 25, agility: 35, wisdom: 45, strength: 55
        });
        Axolotitos.Traits memory traits = Axolotitos.Traits({
            skinColor: 2, gillType: 1, eyeType: 0, mouthType: 1,
            tailType: 0, foreheadType: 1, limbType: 0
        });
        uint256 axolotitoId = controller.eclosionar(player, webitoId, 987654321, stats, traits);

        // Jugar partida — el jugador gana 35 FRJ
        uint256 balanceAntes = frj.balanceOf(player);
        Axolotitos.Stats memory statsActualizados = Axolotitos.Stats({
            salinity: 5, luck: 60, focus: 75, stamina: 90, // stamina bajó de 100 a 90
            charisma: 25, agility: 35, wisdom: 45, strength: 55
        });
        controller.registrarPartida(
            player,
            axolotitoId,
            tableId,
            10 ether,   // cuota 10 FRJ
            35 ether,   // premio 35 FRJ (victoria)
            true,       // ganó
            statsActualizados,
            15          // 15 XP a la tabla
        );
        vm.stopPrank();

        // Premio neto = 35 - 10 = +25 FRJ
        assertEq(frj.balanceOf(player), balanceAntes + 25 ether);

        // Stats del axolotito actualizados
        Axolotitos.Stats memory sActual = axolotitoC.getStats(axolotitoId);
        assertEq(sActual.stamina, 90);

        // Stats de la tabla actualizados
        assertEq(tablasC.gamesPlayed(tableId), 1);
        assertEq(tablasC.gamesWon(tableId), 1);
        assertEq(tablasC.xpOf(tableId), 15);
    }

    // ── Tests de Tabla NPC (sin escrow) ──────────────────────────────────────

    function test_CrearTablaNPC() public {
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1; // IDs 1-16

        // Solo el owner del contrato (treasury) puede llamar createNPCBoard
        vm.prank(treasury);
        uint256 tableId = tablasC.createNPCBoard(player, layout);

        // El NFT pertenece al player
        assertEq(tablasC.ownerOf(tableId), player);

        // El layout quedó guardado on-chain
        uint256[16] memory savedLayout = tablasC.getLayout(tableId);
        for (uint256 i = 0; i < 16; i++) {
            assertEq(savedLayout[i], i + 1);
        }

        // No se transfirió ninguna carta al contrato (balance de cartas = 0)
        for (uint256 i = 1; i <= 16; i++) {
            assertEq(cartasC.balanceOf(address(tablasC), i), 0);
        }
    }

    function test_CrearTablaNPC_SoloOwner() public {
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;

        // Un jugador no autorizado no puede llamar createNPCBoard
        vm.expectRevert();
        vm.prank(player);
        tablasC.createNPCBoard(player, layout);
    }

    function test_CrearTablaNPC_CartaInvalida() public {
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;
        layout[0] = 0; // ID 0 es inválido (rango válido: 1-54)

        vm.expectRevert();
        vm.prank(treasury);
        tablasC.createNPCBoard(player, layout);
    }

    function test_TransferenciaAdministrativaTabla() public {
        address playerB = address(0x3);

        vm.startPrank(treasury);
        controller.depositarFRJ(player, 10000 ether);

        // Mint 16 cartas para player
        uint256[] memory cardIds = new uint256[](16);
        uint256[] memory amounts = new uint256[](16);
        for (uint256 i = 0; i < 16; i++) {
            cardIds[i] = i + 1;
            amounts[i] = 1;
        }
        controller.mintCartas(player, cardIds, amounts);
        vm.stopPrank();

        // El jugador aprueba
        vm.prank(player);
        cartasC.setApprovalForAll(address(tablasC), true);

        // Crear tabla
        vm.startPrank(treasury);
        uint256[16] memory layout;
        for (uint256 i = 0; i < 16; i++) layout[i] = i + 1;
        uint256 tableId = controller.crearTabla(player, layout, 25 ether);

        // Transferencia administrativa por el owner (treasury) del GameController
        controller.transferirTabla(player, playerB, tableId);
        vm.stopPrank();

        // Verificar que el dueño ahora es playerB
        assertEq(tablasC.ownerOf(tableId), playerB);
    }

    function test_TransferenciaAdministrativaAxolotito() public {
        address playerB = address(0x3);

        vm.startPrank(treasury);
        controller.depositarAXF(player, 500 ether);
        uint256 webitoId = controller.comprarWebito(player, 1, 50 ether);

        Axolotitos.Stats memory stats = Axolotitos.Stats({
            salinity: 5, luck: 50, focus: 70, stamina: 100,
            charisma: 20, agility: 30, wisdom: 40, strength: 60
        });
        Axolotitos.Traits memory traits = Axolotitos.Traits({
            skinColor: 0, gillType: 1, eyeType: 2, mouthType: 1,
            tailType: 0, foreheadType: 0, limbType: 0
        });

        uint256 axolotitoId = controller.eclosionar(player, webitoId, 123456789, stats, traits);

        // Transferencia administrativa por el owner (treasury) del GameController
        controller.transferirAxolotito(player, playerB, axolotitoId);
        vm.stopPrank();

        // Verificar que el dueño ahora es playerB
        assertEq(axolotitoC.ownerOf(axolotitoId), playerB);
    }
}
