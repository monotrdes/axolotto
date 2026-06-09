// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/Frijolito.sol";
import "../src/Axoficha.sol";
import "../src/Webitos.sol";
import "../src/Axolotitos.sol";
import "../src/CartasLoteria.sol";
import "../src/Sobrecito.sol";
import "../src/TablasLoteria.sol";
import "../src/Consumables.sol";
import "../src/GameController.sol";

/**
 * @title Deploy
 * @notice Script de Foundry para desplegar todo el ecosistema Axolotto.
 *
 * USO:
 *   forge script script/Deploy.s.sol --rpc-url http://127.0.0.1:8545 --broadcast --private-key $DEPLOYER_KEY
 *
 * Las direcciones se imprimen al stdout en el formato:
 *   DEPLOYED_FRJ=0x...
 *   DEPLOYED_AXF=0x...
 *   ... (etc.)
 *
 * El script deploy_local.sh captura este output y lo escribe al .env del backend.
 */
contract Deploy is Script {
    function run() external {
        // La clave privada del deployer (Treasury/Admin) se pasa como env var
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address deployer = vm.addr(deployerKey);

        // URL base del backend para metadata NFT
        string memory baseURI = vm.envOr("METADATA_BASE_URL", string("http://localhost:8001/api/v1/metadata/"));

        vm.startBroadcast(deployerKey);

        // ── 1. Tokens ERC-20 ──────────────────────────────────────────────────
        Frijolito frj = new Frijolito(deployer);
        Axoficha  axf = new Axoficha(deployer);

        // ── 2. NFTs ERC-721 (sin tablas aún, necesitan dirección de cartas) ──
        Webitos     webitosContract    = new Webitos(deployer, string(abi.encodePacked(baseURI, "webito/")));
        Axolotitos  axolotitoContract  = new Axolotitos(deployer, string(abi.encodePacked(baseURI, "axolotito/")));

        // ── 3. Tokens ERC-1155 ────────────────────────────────────────────────
        CartasLoteria cartasContract       = new CartasLoteria(deployer, string(abi.encodePacked(baseURI, "carta/{id}")));
        Sobrecito     sobrecitosContract   = new Sobrecito(deployer, string(abi.encodePacked(baseURI, "sobrecito/{id}")));
        Consumables   consumablesContract  = new Consumables(deployer, string(abi.encodePacked(baseURI, "consumable/{id}")));

        // ── 4. Tablas (necesita la dirección de cartas para escrow) ───────────
        TablasLoteria tablasContract = new TablasLoteria(
            deployer,
            address(cartasContract),
            string(abi.encodePacked(baseURI, "tabla/"))
        );

        // ── 5. GameController ─────────────────────────────────────────────────
        GameController controller = new GameController(deployer);

        controller.configurar(
            address(frj),
            address(axf),
            address(webitosContract),
            address(axolotitoContract),
            address(cartasContract),
            address(sobrecitosContract),
            address(tablasContract),
            address(consumablesContract)
        );

        // ── 6. Asignar GameController en todos los contratos ──────────────────
        frj.setGameController(address(controller));
        axf.setGameController(address(controller));
        webitosContract.setGameController(address(controller));
        axolotitoContract.setGameController(address(controller));
        cartasContract.setGameController(address(controller));
        cartasContract.setTablasContract(address(tablasContract));
        sobrecitosContract.setGameController(address(controller));
        tablasContract.setGameController(address(controller));
        consumablesContract.setGameController(address(controller));

        vm.stopBroadcast();

        // ── 7. Imprimir direcciones en formato que deploy_local.sh puede parsear ──
        console.log("DEPLOYED_FRJ=%s", address(frj));
        console.log("DEPLOYED_AXF=%s", address(axf));
        console.log("DEPLOYED_WEBITOS=%s", address(webitosContract));
        console.log("DEPLOYED_AXOLOTITOS=%s", address(axolotitoContract));
        console.log("DEPLOYED_CARTAS=%s", address(cartasContract));
        console.log("DEPLOYED_SOBRECITOS=%s", address(sobrecitosContract));
        console.log("DEPLOYED_TABLAS=%s", address(tablasContract));
        console.log("DEPLOYED_CONSUMABLES=%s", address(consumablesContract));
        console.log("DEPLOYED_GAME_CONTROLLER=%s", address(controller));
        console.log("DEPLOYER_ADDRESS=%s", deployer);
    }
}
