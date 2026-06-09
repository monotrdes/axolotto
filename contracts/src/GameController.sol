// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./Frijolito.sol";
import "./Axoficha.sol";
import "./Webitos.sol";
import "./Axolotitos.sol";
import "./CartasLoteria.sol";
import "./Sobrecito.sol";
import "./TablasLoteria.sol";
import "./Consumables.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GameController
 * @notice Orquestador central de Axolotto. Tiene permisos de mint/burn en
 *         todos los contratos del juego. El Treasury wallet del backend llama
 *         estas funciones para ejecutar acciones del juego.
 *
 *  ┌─────────────────────────────────────────────────────────┐
 *  │  Backend (Treasury Wallet)                              │
 *  │       ↓                                                 │
 *  │  GameController ──→ Frijolito / Axoficha (ERC-20)       │
 *  │                 ──→ Webitos / Axolotitos / Tablas (721) │
 *  │                 ──→ Cartas / Sobrecito / Consumables(1155)│
 *  └─────────────────────────────────────────────────────────┘
 */
contract GameController is Ownable {

    // Referencias a todos los contratos del ecosistema
    Frijolito     public frj;
    Axoficha      public axf;
    Webitos       public webitos;
    Axolotitos    public axolotitos;
    CartasLoteria public cartas;
    Sobrecito     public sobrecitos;
    TablasLoteria public tablas;
    Consumables   public consumables;

    // Eventos de alto nivel para auditoria
    event TiendaCompra(address indexed jugador, string itemType, uint256 itemId, uint256 precio, string moneda);
    event PartidaJugada(address indexed jugador, uint256 axolotitoId, uint256 tablaId, bool gano, uint256 premio);
    event AxolotitoNutrido(address indexed jugador, uint256 axolotitoId, uint256 consumableId);

    // Eventos multijugador — modo manual (tiempo real)
    event ManualGameStarted(uint256 indexed roomId, uint256 timestamp);
    event CardCalled(uint256 indexed roomId, uint8 cardNumber, uint256 timestamp);
    event LoteriaShouted(uint256 indexed roomId, address indexed player, uint256 axolotitoId, bool valid);
    event ManualGameEnded(uint256 indexed roomId, address indexed winner, uint256 payout);

    /// @notice Bloquea el envío de moneda nativa (ETH) en operaciones multijugador.
    ///         El multijugador solo acepta Frijolitos (FRJ / Frijolito).
    modifier onlyFRJ() {
        require(msg.value == 0, "GameController: AXF no aceptado en multijugador");
        _;
    }

    constructor(address initialOwner) Ownable(initialOwner) {}

    // ─── Configuración ───────────────────────────────────────────────────────

    function configurar(
        address _frj,
        address _axf,
        address _webitos,
        address _axolotitos,
        address _cartas,
        address _sobrecitos,
        address _tablas,
        address _consumables
    ) external onlyOwner {
        frj         = Frijolito(_frj);
        axf         = Axoficha(_axf);
        webitos     = Webitos(_webitos);
        axolotitos  = Axolotitos(_axolotitos);
        cartas      = CartasLoteria(_cartas);
        sobrecitos  = Sobrecito(_sobrecitos);
        tablas      = TablasLoteria(_tablas);
        consumables = Consumables(_consumables);
    }

    // ─── Economía: Monedas ────────────────────────────────────────────────────

    /// @notice Deposita FRJ a un jugador (Premio de partida, admin deposit)
    function depositarFRJ(address jugador, uint256 cantidad) external onlyOwner {
        frj.mint(jugador, cantidad);
    }

    /// @notice Deposita AXF a un jugador (compra con SPEI)
    function depositarAXF(address jugador, uint256 cantidad) external onlyOwner {
        axf.mint(jugador, cantidad);
    }

    /// @notice Cobra FRJ a un jugador (cuota de entrada, compra en tienda)
    function cobrarFRJ(address jugador, uint256 cantidad) external onlyOwner {
        frj.burn(jugador, cantidad);
    }

    /// @notice Cobra AXF a un jugador
    function cobrarAXF(address jugador, uint256 cantidad) external onlyOwner {
        axf.burn(jugador, cantidad);
    }

    // ─── Tienda: Webitos ──────────────────────────────────────────────────────

    /**
     * @notice Compra un Webito pagando en AXF. Acuña el NFT y cobra la moneda.
     * @param jugador   Wallet del comprador
     * @param fase      Fase del Webito (1, 2 o 3)
     * @param precioAXF Precio en wei (18 decimales)
     */
    function comprarWebito(address jugador, uint8 fase, uint256 precioAXF)
        external
        onlyOwner
        returns (uint256 tokenId)
    {
        axf.burn(jugador, precioAXF);
        tokenId = webitos.mintWebito(jugador, fase);
        emit TiendaCompra(jugador, "WEBITO", fase, precioAXF, "AXF");
    }

    // ─── Tienda: Sobrecitos ───────────────────────────────────────────────────

    /**
     * @notice Compra un sobrecito pagando en AXF. El sobrecito es un token ERC-1155.
     * @param jugador   Wallet del comprador
     * @param fase      Fase del sobrecito (1, 2 o 3)
     * @param cantidad  Cantidad de sobrecitos
     * @param precioAXF Precio total en wei
     */
    function comprarSobrecito(address jugador, uint8 fase, uint256 cantidad, uint256 precioAXF)
        external
        onlyOwner
    {
        axf.burn(jugador, precioAXF);
        sobrecitos.mintSobrecito(jugador, fase, cantidad);
        emit TiendaCompra(jugador, "SOBRECITO", fase, precioAXF, "AXF");
    }

    // ─── Apertura de Sobrecitos ───────────────────────────────────────────────

    /**
     * @notice Abre un sobrecito: quema el token y mintea las 7 cartas obtenidas.
     * @param jugador  Wallet del jugador
     * @param fase     Fase del sobrecito (1, 2 o 3)
     * @param cardIds  IDs de las 7 cartas a acuñar (elegidas aleatoriamente por el backend)
     */
    function abrirSobrecito(
        address jugador,
        uint8 fase,
        uint256[] calldata cardIds
    ) external onlyOwner {
        require(cardIds.length == 7, "GameController: Debe haber 7 cartas");
        sobrecitos.burnSobrecito(jugador, fase, 1);
        uint256[] memory amounts = new uint256[](7);
        for (uint256 i = 0; i < 7; i++) amounts[i] = 1;
        cartas.mintCards(jugador, cardIds, amounts);
    }

    // ─── Eclosión de Axolotito ────────────────────────────────────────────────

    /**
     * @notice Eclosiona un Webito: lo quema y acuña un Axolotito con stats + traits.
     * @param jugador       Wallet del jugador
     * @param webitoTokenId Token del Webito a eclosionar
     * @param dna           DNA único del Axolotito (uint256)
     * @param stats         Stats del Axolotito on-chain
     * @param traits        Rasgos visuales del Axolotito
     */
    function eclosionar(
        address jugador,
        uint256 webitoTokenId,
        uint256 dna,
        Axolotitos.Stats calldata stats,
        Axolotitos.Traits calldata traits
    ) external onlyOwner returns (uint256 axolotitoId) {
        webitos.burnWebito(webitoTokenId);
        axolotitoId = axolotitos.mintAxolotito(jugador, dna, stats, traits);
    }

    // ─── Creación de Tabla ────────────────────────────────────────────────────

    /**
     * @notice Crea una tabla de juego, poniendo las cartas en escrow.
     * @param jugador   Wallet del jugador
     * @param cardIds   16 IDs de cartas que formarán la tabla
     * @param precioFRJ Precio de creación de la tabla en FRJ
     */
    function crearTabla(
        address jugador,
        uint256[16] calldata cardIds,
        uint256 precioFRJ
    ) external onlyOwner returns (uint256 tableId) {
        frj.burn(jugador, precioFRJ);
        tableId = tablas.createBoard(jugador, cardIds);
        emit TiendaCompra(jugador, "TABLA", tableId, precioFRJ, "FRJ");
    }

    // ─── Alimentar Axolotito ──────────────────────────────────────────────────

    /**
     * @notice Alimenta un Axolotito usando un consumible. Cobra FRJ y quema el item.
     * @param jugador       Wallet del jugador
     * @param consumableId  1=Algae Pellet, 2=Brine Shrimp
     * @param precioFRJ     Precio en FRJ
     */
    function alimentarAxolotito(
        address jugador,
        uint256 axolotitoId,
        uint256 consumableId,
        uint256 precioFRJ
    ) external onlyOwner {
        frj.burn(jugador, precioFRJ);
        consumables.burnConsumable(jugador, consumableId, 1);
        emit AxolotitoNutrido(jugador, axolotitoId, consumableId);
    }

    // ─── Resultado de Partida ─────────────────────────────────────────────────

    /**
     * @notice Registra el resultado de una partida y distribuye el premio.
     * @param jugador       Wallet del jugador
     * @param axolotitoId   Token del Axolotito que jugó
     * @param tablaId       Token de la tabla usada
     * @param cuotaFRJ      Cuota de entrada cobrada
     * @param premioFRJ     Premio en FRJ para el jugador (0 si perdió)
     * @param gano          true si el jugador ganó
     * @param statsActualizados  Stats actualizados del Axolotito (energía, nivel, etc.)
     * @param xpTabla       XP ganado por la tabla
     */
    function registrarPartida(
        address jugador,
        uint256 axolotitoId,
        uint256 tablaId,
        uint256 cuotaFRJ,
        uint256 premioFRJ,
        bool gano,
        Axolotitos.Stats calldata statsActualizados,
        uint256 xpTabla
    ) external onlyOwner {
        // Cobrar cuota de entrada
        frj.burn(jugador, cuotaFRJ);

        // Pagar premio
        if (premioFRJ > 0) {
            frj.mint(jugador, premioFRJ);
        }

        // Actualizar stats del Axolotito on-chain
        axolotitos.updateStats(axolotitoId, statsActualizados);

        // Actualizar stats de la tabla on-chain
        tablas.updateTableStats(tablaId, gano, xpTabla);

        emit PartidaJugada(jugador, axolotitoId, tablaId, gano, premioFRJ);
    }

    // ─── Mint directo de Cartas (para simulación/seed) ────────────────────────

    function mintCartas(
        address jugador,
        uint256[] calldata ids,
        uint256[] calldata amounts
    ) external onlyOwner {
        cartas.mintCards(jugador, ids, amounts);
    }

    /// @notice Acuña consumibles directamente (para simulación)
    function mintConsumible(address jugador, uint256 id, uint256 cantidad) external onlyOwner {
        consumables.mintConsumable(jugador, id, cantidad);
    }

    function transferirTabla(address from, address to, uint256 tableId) external onlyOwner {
        tablas.transferBoard(from, to, tableId);
    }

    function transferirAxolotito(address from, address to, uint256 axolotitoId) external onlyOwner {
        axolotitos.transferAxolotito(from, to, axolotitoId);
    }

    // ─── Multijugador Manual (FRJ-only) ──────────────────────────────────────

    /// @notice Inicia una partida multijugador manual. Solo FRJ, sin AXF nativo.
    /// @param roomId    ID de la sala en el backend
    function iniciarPartidaManual(uint256 roomId) external payable onlyOwner onlyFRJ {
        emit ManualGameStarted(roomId, block.timestamp);
    }

    /// @notice El Gritón canta una carta durante la partida manual.
    /// @param roomId     ID de la sala
    /// @param cardNumber Número de lotería de la carta cantada (1-54)
    function cantarCarta(uint256 roomId, uint8 cardNumber) external payable onlyOwner onlyFRJ {
        require(cardNumber >= 1 && cardNumber <= 54, "GameController: Numero de carta invalido");
        emit CardCalled(roomId, cardNumber, block.timestamp);
    }

    /// @notice Un jugador grita ¡Lotería! — se registra si fue válido o no.
    /// @param roomId       ID de la sala
    /// @param player       Wallet del jugador
    /// @param axolotitoId  Token del Axolotito
    /// @param valid        true si el grito fue válido (línea completa)
    function gritarLoteria(
        uint256 roomId,
        address player,
        uint256 axolotitoId,
        bool valid
    ) external payable onlyOwner onlyFRJ {
        emit LoteriaShouted(roomId, player, axolotitoId, valid);
    }

    /// @notice Finaliza una partida multijugador manual y paga al ganador en FRJ.
    /// @param roomId       ID de la sala
    /// @param winner       Wallet del ganador
    /// @param payout       Premio en FRJ (Frijolito) para el ganador
    function finalizarPartidaManual(
        uint256 roomId,
        address winner,
        uint256 payout
    ) external payable onlyOwner onlyFRJ {
        if (payout > 0) {
            frj.mint(winner, payout);
        }
        emit ManualGameEnded(roomId, winner, payout);
    }
}
