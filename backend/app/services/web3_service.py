from __future__ import annotations
"""
web3_service.py — Servicio Web3 de Axolotto

Soporta dos modos:
  - "polygon_amoy" : Polygon Amoy Testnet (Chain ID 80002) — staging
  - "local"        : Anvil local (Chain ID 31337) — simulaciones/desarrollo

El modo se configura via BLOCKCHAIN_MODE en el .env.
Los ABIs se cargan desde los artifacts de Foundry en contracts/out/
"""
from web3 import Web3
from app.core.config import settings, AXF_BACKEND_TO_WEI_FACTOR, FRJ_BACKEND_TO_WEI_FACTOR
import json
import threading
import os
import re
from pathlib import Path

# ── Ruta base de los artifacts de Foundry ─────────────────────────────────────
# Funciona tanto desde Docker (./contracts/) como desde host (backend/../contracts/)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # raíz del proyecto
_CONTRACTS_OUT = _BASE_DIR / "contracts" / "out"

def _load_abi(contract_name: str) -> list:
    """Carga el ABI desde los artifacts compilados de Foundry."""
    artifact_path = _CONTRACTS_OUT / f"{contract_name}.sol" / f"{contract_name}.json"
    if artifact_path.exists():
        with open(artifact_path) as f:
            return json.load(f)["abi"]
    # Fallback: ABI mínimo inline para compatibilidad
    print(f"⚠️ Artifact no encontrado: {artifact_path}. Usando ABI mínimo.")
    return []

# ── ABIs mínimos inline como fallback ─────────────────────────────────────────
_ERC20_TRANSFER_ABI = json.loads('[{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]')

_ERC20_MINT_ABI = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"from","type":"address"},{"name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')

_WEBITOS_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"fase","type":"uint8"}],"name":"mintWebito","outputs":[{"name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tokenId","type":"uint256"}],"name":"burnWebito","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')

_AXOLOTITOS_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"dna","type":"uint256"},{"name":"stats","type":"tuple","components":[{"name":"salinity","type":"uint8"},{"name":"luck","type":"uint8"},{"name":"focus","type":"uint8"},{"name":"stamina","type":"uint8"},{"name":"charisma","type":"uint8"},{"name":"agility","type":"uint8"},{"name":"wisdom","type":"uint8"},{"name":"strength","type":"uint8"}]},{"name":"traits","type":"tuple","components":[{"name":"skinColor","type":"uint8"},{"name":"gillType","type":"uint8"},{"name":"eyeType","type":"uint8"},{"name":"mouthType","type":"uint8"},{"name":"tailType","type":"uint8"},{"name":"foreheadType","type":"uint8"},{"name":"limbType","type":"uint8"}]}],"name":"mintAxolotito","outputs":[{"name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tokenId","type":"uint256"},{"name":"stats","type":"tuple","components":[{"name":"salinity","type":"uint8"},{"name":"luck","type":"uint8"},{"name":"focus","type":"uint8"},{"name":"stamina","type":"uint8"},{"name":"charisma","type":"uint8"},{"name":"agility","type":"uint8"},{"name":"wisdom","type":"uint8"},{"name":"strength","type":"uint8"}]}],"name":"updateStats","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tokenId","type":"uint256"}],"name":"getStats","outputs":[{"name":"","type":"tuple","components":[{"name":"salinity","type":"uint8"},{"name":"luck","type":"uint8"},{"name":"focus","type":"uint8"},{"name":"stamina","type":"uint8"},{"name":"charisma","type":"uint8"},{"name":"agility","type":"uint8"},{"name":"wisdom","type":"uint8"},{"name":"strength","type":"uint8"}]}],"stateMutability":"view","type":"function"},
  {"inputs":[{"name":"tokenId","type":"uint256"}],"name":"dnaOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
]''')

_CARTAS_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"ids","type":"uint256[]"},{"name":"amounts","type":"uint256[]"}],"name":"mintCards","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"account","type":"address"},{"name":"id","type":"uint256"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"name":"owner","type":"address"},{"name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"name":"","type":"bool"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"name":"operator","type":"address"},{"name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"owner","type":"address"},{"name":"approved","type":"bool"}],"name":"setApprovalForTablas","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"id","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"transferCard","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')

_SOBRECITO_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"fase","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"mintSobrecito","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"from","type":"address"},{"name":"fase","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"burnSobrecito","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"fase","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"transferirSobrecito","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')

_TABLAS_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"cardIds","type":"uint256[16]"}],"name":"createBoard","outputs":[{"name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"to","type":"address"},{"name":"cardIds","type":"uint256[16]"}],"name":"createNPCBoard","outputs":[{"name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tableId","type":"uint256"},{"name":"destroyCardIndex","type":"uint256"}],"name":"dissolveBoard","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tableId","type":"uint256"}],"name":"dissolveBoardSafe","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"tableId","type":"uint256"}],"name":"getLayout","outputs":[{"name":"","type":"uint256[16]"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"name":"tableId","type":"uint256"},{"name":"won","type":"bool"},{"name":"xpGained","type":"uint256"}],"name":"updateTableStats","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')

_CONSUMABLES_ABI_MINIMAL = json.loads('''[
  {"inputs":[{"name":"to","type":"address"},{"name":"id","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"mintConsumable","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"name":"from","type":"address"},{"name":"id","type":"uint256"},{"name":"amount","type":"uint256"}],"name":"burnConsumable","outputs":[],"stateMutability":"nonpayable","type":"function"}
]''')


class Web3Service:
    """
    Servicio centralizado de interacciones con la blockchain de Axolotto.
    
    Soporta modo "polygon_amoy" (Polygon Amoy Testnet) y "local" (Anvil).
    """
    # Mutex para serializar transacciones y evitar conflictos de nonce
    _tx_lock = threading.Lock()

    # ── Conexión ──────────────────────────────────────────────────────────────
    w3 = Web3(Web3.HTTPProvider(settings.rpc_url))

    @staticmethod
    def _get_w3() -> Web3:
        """Devuelve instancia Web3 con la URL RPC correcta según el modo."""
        return Web3(Web3.HTTPProvider(settings.rpc_url))

    @staticmethod
    def _get_admin():
        """Recupera la cuenta del Treasury/Admin desde la clave privada."""
        w3 = Web3Service._get_w3()
        return w3, w3.eth.account.from_key(settings.TREASURY_PRIVATE_KEY)

    @staticmethod
    def _send_tx(function_call, w3: Web3 = None) -> str:
        """Firma y envía una transacción. Serializada con lock para evitar nonce conflicts."""
        with Web3Service._tx_lock:
            if w3 is None:
                w3 = Web3Service._get_w3()
            admin_account = w3.eth.account.from_key(settings.TREASURY_PRIVATE_KEY)
            nonce = w3.eth.get_transaction_count(admin_account.address, 'pending')

            try:
                gas_estimado = function_call.estimate_gas({'from': admin_account.address})
                gas_limit = int(gas_estimado * 1.3)
            except Exception as e:
                print(f"⚠️ No se pudo estimar gas: {e}. Usando 3M.")
                gas_limit = 3_000_000

            tx = function_call.build_transaction({
                'chainId': settings.chain_id,
                'gas': gas_limit,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            signed = w3.eth.account.sign_transaction(tx, settings.TREASURY_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            return w3.to_hex(tx_hash)

    # ── FRJ (Frijolito — ERC-20) ──────────────────────────────────────────────

    @staticmethod
    def mint_frj(to_address: str, amount: int) -> str:
        """Acuña FRJ para un jugador (recompensa, depósito admin).

        Args:
            amount: Monto en unidad mínima entera de backend (4 decimales).
        """
        w3 = Web3Service._get_w3()
        to = Web3.to_checksum_address(to_address)
        amount_wei = amount * FRJ_BACKEND_TO_WEI_FACTOR
        abi = _load_abi("Frijolito") or _ERC20_MINT_ABI
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.GEMA_ALGA_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mint(to, amount_wei), w3)

    @staticmethod
    def burn_frj(from_address: str, amount: int) -> str:
        """Quema FRJ de un jugador (cuota de entrada, compra en tienda).

        Args:
            amount: Monto en unidad mínima entera de backend (4 decimales).
        """
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        amount_wei = amount * FRJ_BACKEND_TO_WEI_FACTOR
        abi = _load_abi("Frijolito") or _ERC20_MINT_ABI
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.GEMA_ALGA_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.burn(from_addr, amount_wei), w3)

    @staticmethod
    def transferir_axofichas(to_address: str, amount: int) -> str:
        """Envía AXF desde el Treasury a un jugador.

        Args:
            amount: Monto en unidad mínima entera de backend (6 decimales).
        """
        w3 = Web3Service._get_w3()
        to = Web3.to_checksum_address(to_address)
        amount_wei = amount * AXF_BACKEND_TO_WEI_FACTOR
        abi = _load_abi("Axoficha") or _ERC20_MINT_ABI
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.AXOGEMA_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mint(to, amount_wei), w3)

    @staticmethod
    def burn_axofichas(from_address: str, amount: int) -> str:
        """Quema AXF de un jugador.

        Args:
            amount: Monto en unidad mínima entera de backend (6 decimales).
        """
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        amount_wei = amount * AXF_BACKEND_TO_WEI_FACTOR
        abi = _load_abi("Axoficha") or _ERC20_MINT_ABI
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.AXOGEMA_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.burn(from_addr, amount_wei), w3)

    # ── Webitos (ERC-721) ─────────────────────────────────────────────────────

    @staticmethod
    def mint_webito_onchain(player_address: str, fase: int = 1) -> str:
        """Acuña un Webito NFT para el jugador."""
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        abi = _load_abi("Webitos") or _WEBITOS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.WEBITOS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mintWebito(player, fase), w3)

    # ── Axolotitos (ERC-721 con stats on-chain) ───────────────────────────────

    @staticmethod
    def mint_axolotito_onchain(player_address: str, dna: str, stats: tuple = None, traits: tuple = None) -> str:
        """Acuña un Axolotito NFT para el jugador con opcionalmente sus stats/traits."""
        if stats is None:
            stats = (5, 10, 50, 100, 10, 10, 10, 10)   # salinity,luck,focus,stamina,charisma,agility,wisdom,strength
        if traits is None:
            traits = (0, 1, 0, 1, 0, 0, 0)              # skinColor,gillType,eyeType,mouthType,tailType,foreheadType,limbType
        return Web3Service.mint_axolotito_with_stats(player_address, dna, stats, traits)

    @staticmethod
    def mint_axolotito_with_stats(
        player_address: str,
        dna: str,
        stats: tuple,   # (salinity, luck, focus, stamina, charisma, agility, wisdom, strength)
        traits: tuple,  # (skinColor, gillType, eyeType, mouthType, tailType, foreheadType, limbType)
    ) -> str:
        """
        Acuña un Axolotito con DNA, stats y traits almacenados on-chain.
        
        Args:
            player_address: Wallet del jugador
            dna:    DNA como string numérico (se convierte a uint256)
            stats:  Tupla de 8 ints (0-100 cada uno, stamina 50-200)
            traits: Tupla de 7 ints (índices de rasgos visuales)
        """
        if not settings.AXOLOTITOS_ADDRESS:
            import secrets
            mock = f"0x_mock_axo_{secrets.token_hex(16)}"
            print(f"ℹ️ AXOLOTITOS_ADDRESS no configurado. Mock hash: {mock}")
            return mock

        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        dna_uint = int(dna) if dna.isdigit() else int(dna, 0)

        # Asegurar que los stats están en rango uint8
        s = tuple(min(255, max(0, int(x))) for x in stats)
        
        # Mapeo de rasgos visuales de string a uint8 indices
        trait_mappings = {
            # skinColor
            "pink": 0, "gray_light": 1, "gray_light_pink": 1, "gray_dark": 2, "gray_dead_sea": 2, "gold": 3, "astral": 4,
            # gillType
            "short": 0, "normal": 1, "feathery": 2, "crown": 3, "phoenix": 4,
            # eyeType
            "cute": 0, "derp": 1, "dreamer": 2, "cool": 3, "intellectual": 3, "zen": 4,
            # mouthType
            "flat": 0, "smile": 1, "fang": 2, "rockstar": 3, "divine": 4,
            # tailType
            "standard": 0, "wavy": 1, "betta": 2, "plasma": 3,
            # foreheadType
            "none": 0, "stripes": 1, "gem": 2, "halo": 3,
            # limbType
            "soft": 0, "claws": 1, "scales": 2, "coral": 3
        }
        
        mapped_traits = []
        for i, val in enumerate(traits):
            if isinstance(val, str):
                mapped_traits.append(trait_mappings.get(val, 0))
            else:
                mapped_traits.append(int(val))
        t = tuple(min(255, max(0, x)) for x in mapped_traits)

        abi = _load_abi("Axolotitos") or _AXOLOTITOS_ABI_MINIMAL
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.AXOLOTITOS_ADDRESS), abi=abi
        )
        return Web3Service._send_tx(
            contract.functions.mintAxolotito(player, dna_uint, s, t), w3
        )

    @staticmethod
    def get_axolotito_stats(token_id: int) -> dict | None:
        """Lee los stats on-chain de un Axolotito."""
        if not settings.AXOLOTITOS_ADDRESS:
            return None
        w3 = Web3Service._get_w3()
        abi = _load_abi("Axolotitos") or _AXOLOTITOS_ABI_MINIMAL
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.AXOLOTITOS_ADDRESS), abi=abi
        )
        raw = contract.functions.getStats(token_id).call()
        return {
            "salinity": raw[0], "luck": raw[1], "focus": raw[2], "stamina": raw[3],
            "charisma": raw[4], "agility": raw[5], "wisdom": raw[6], "strength": raw[7],
        }

    @staticmethod
    def update_axolotito_stats_onchain(token_id: int, stats: tuple) -> str:
        """Actualiza los stats on-chain de un Axolotito."""
        if not settings.AXOLOTITOS_ADDRESS:
            return "0x_mock_update_stats"
        w3 = Web3Service._get_w3()
        s = tuple(min(255, max(0, int(x))) for x in stats)
        abi = _load_abi("Axolotitos") or _AXOLOTITOS_ABI_MINIMAL
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.AXOLOTITOS_ADDRESS), abi=abi
        )
        return Web3Service._send_tx(contract.functions.updateStats(token_id, s), w3)

    # ── Cartas Lotería (ERC-1155) ─────────────────────────────────────────────

    @staticmethod
    def mint_cards_onchain(player_address: str, card_ids: list[int], amounts: list[int]) -> str:
        """Acuña múltiples cartas (al abrir un sobre)."""
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        # Convertir IDs del catálogo (12-65) a IDs del contrato (1-54)
        contract_ids = [cid - 11 for cid in card_ids]
        abi = _load_abi("CartasLoteria") or _CARTAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CARDS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mintCards(player, contract_ids, amounts), w3)

    @staticmethod
    def approve_tablas_for_player(player_address: str) -> str:
        """Aprueba al contrato de Tablas para mover las cartas del jugador (escrow)."""
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        abi = _load_abi("CartasLoteria") or _CARTAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CARDS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.setApprovalForTablas(player, True), w3)

    @staticmethod
    def transfer_card_onchain(from_address: str, to_address: str, card_id: int, amount: int = 1) -> str:
        """Transfiere cartas de un jugador a otro on-chain (convierte ID catálogo a ID contrato)."""
        if settings.IS_MOCK_WEB3 or not settings.CARDS_ADDRESS:
            return "0x_mock_transfer_card"
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        contract_id = card_id - 11  # catálogo 12-65 → contrato 1-54
        abi = _load_abi("CartasLoteria") or _CARTAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CARDS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferCard(from_addr, to_addr, contract_id, amount), w3)

    # ── Sobrecitos (ERC-1155) ──────────────────────────────────────────────────

    @staticmethod
    def mint_sobrecito_onchain(player_address: str, sobrecito_id: int, amount: int = 1) -> str:
        """Acuña sobrecitos (al comprar en tienda)."""
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        abi = _load_abi("Sobrecito") or _SOBRECITO_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.BOOSTERS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mintSobrecito(player, sobrecito_id, amount), w3)

    @staticmethod
    def burn_sobrecito_onchain(player_address: str, sobrecito_id: int, amount: int = 1) -> str:
        """Quema sobrecitos (al abrirlos)."""
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        abi = _load_abi("Sobrecito") or _SOBRECITO_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.BOOSTERS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.burnSobrecito(player, sobrecito_id, amount), w3)

    @staticmethod
    def transferir_sobrecito_onchain(from_address: str, to_address: str, sobrecito_id: int, amount: int = 1) -> str:
        """Transfiere sobrecitos de un jugador a otro on-chain."""
        if settings.IS_MOCK_WEB3 or not settings.BOOSTERS_ADDRESS:
            return "0x_mock_transfer_sobrecito"
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        abi = _load_abi("Sobrecito") or _SOBRECITO_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.BOOSTERS_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferirSobrecito(from_addr, to_addr, sobrecito_id, amount), w3)

    # ── Tablas (ERC-721 con escrow) ───────────────────────────────────────────

    @staticmethod
    def create_board_onchain(player_address: str, card_ids: list[int]) -> str:
        """
        Crea una tabla on-chain transfiriendo las 16 cartas al contrato (escrow).
        IMPORTANTE: El jugador debe haber aprobado al contrato de Tablas previamente.
        """
        if not settings.TABLAS_ADDRESS:
            import secrets
            return f"0x_mock_tabla_{secrets.token_hex(16)}"

        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        assert len(card_ids) == 16, "Se necesitan exactamente 16 cartas"
        
        # Convertir IDs del catálogo (12-65) a IDs del contrato (1-54)
        contract_ids = [cid - 11 for cid in card_ids]
        abi = _load_abi("TablasLoteria") or _TABLAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.TABLAS_ADDRESS), abi=abi)
        # Convertir lista de 16 a tuple para Solidity uint256[16]
        card_tuple = tuple(contract_ids[:16])
        return Web3Service._send_tx(
            contract.functions.createBoard(player, card_tuple), w3
        )

    @staticmethod
    def dissolve_board_onchain(board_token_id: int, destroy_card_index: int) -> str:
        """
        Disuelve una tabla on-chain, devolviendo 15 cartas y destruyendo la del índice especificado.
        """
        if not settings.TABLAS_ADDRESS:
            return "0x_mock_dissolve_board"
        w3 = Web3Service._get_w3()
        abi = _load_abi("TablasLoteria") or _TABLAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.TABLAS_ADDRESS), abi=abi)
        return Web3Service._send_tx(
            contract.functions.dissolveBoard(board_token_id, destroy_card_index), w3
        )

    @staticmethod
    def dissolve_board_safe_onchain(board_token_id: int) -> str:
        """
        Disuelve una tabla on-chain de manera segura, devolviendo las 16 cartas al dueño.
        """
        if not settings.TABLAS_ADDRESS:
            return "0x_mock_dissolve_board_safe"
        w3 = Web3Service._get_w3()
        abi = _load_abi("TablasLoteria") or _TABLAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.TABLAS_ADDRESS), abi=abi)
        return Web3Service._send_tx(
            contract.functions.dissolveBoardSafe(board_token_id), w3
        )

    @staticmethod
    def update_table_stats_onchain(board_token_id: int, won: bool, xp_gained: int) -> str:
        """
        Actualiza los stats de una tabla on-chain.
        """
        if not settings.TABLAS_ADDRESS:
            return "0x_mock_update_table_stats"
        w3 = Web3Service._get_w3()
        abi = _load_abi("TablasLoteria") or _TABLAS_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.TABLAS_ADDRESS), abi=abi)
        return Web3Service._send_tx(
            contract.functions.updateTableStats(board_token_id, won, xp_gained), w3
        )

    @staticmethod
    def create_npc_board(card_ids: list[int]) -> int:
        """
        Mints an NPC board on-chain using the owner/deployer wallet.

        Calls TablasLoteria.createNPCBoard(NPC_WALLET_ADDRESS, card_ids).
        Unlike create_board_onchain, no ERC-1155 card escrow is required.

        Args:
            card_ids: List of exactly 16 catalog card IDs (12-65).
                      Converted to contract IDs (1-54) via cid - 11.

        Returns:
            The blockchain token ID (uint256) of the minted NPC table NFT.

        Raises:
            AssertionError: If card_ids does not contain exactly 16 entries.
            Exception: Any web3/chain error is propagated to the caller.
        """
        assert len(card_ids) == 16, "Se necesitan exactamente 16 cartas"

        if not settings.TABLAS_ADDRESS:
            import random
            mock_id = random.randint(1_000_000_000, 2_000_000_000)
            print(f"  TABLAS_ADDRESS no configurado. Mock token_id: {mock_id}")
            return mock_id

        w3 = Web3Service._get_w3()
        npc_wallet = Web3.to_checksum_address(settings.NPC_WALLET_ADDRESS)

        # Convert catalog IDs (12-65) to contract IDs (1-54)
        contract_ids = tuple(cid - 11 for cid in card_ids[:16])

        abi = _load_abi("TablasLoteria") or _TABLAS_ABI_MINIMAL
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.TABLAS_ADDRESS), abi=abi
        )
        tx_hash = Web3Service._send_tx(
            contract.functions.createNPCBoard(npc_wallet, contract_ids), w3
        )
        token_id = Web3Service._wait_and_get_token_id(tx_hash, w3)
        if token_id is None:
            raise RuntimeError(f"No se pudo extraer token_id del receipt. tx_hash={tx_hash}")
        return token_id

    # ── Consumibles (ERC-1155) ────────────────────────────────────────────────

    @staticmethod
    def mint_consumable(player_address: str, consumable_id: int, amount: int = 1) -> str:
        """Acuña un consumible para el jugador."""
        if not settings.CONSUMABLES_ADDRESS:
            return f"0x_mock_consumable"
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        contract_id = consumable_id - 6 if consumable_id >= 7 else consumable_id
        abi = _load_abi("Consumables") or _CONSUMABLES_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CONSUMABLES_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.mintConsumable(player, contract_id, amount), w3)

    @staticmethod
    def burn_consumable(player_address: str, consumable_id: int, amount: int = 1) -> str:
        """Quema un consumible al usarlo."""
        if not settings.CONSUMABLES_ADDRESS:
            return f"0x_mock_burn_consumable"
        w3 = Web3Service._get_w3()
        player = Web3.to_checksum_address(player_address)
        contract_id = consumable_id - 6 if consumable_id >= 7 else consumable_id
        abi = _load_abi("Consumables") or _CONSUMABLES_ABI_MINIMAL
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.CONSUMABLES_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.burnConsumable(player, contract_id, amount), w3)

    # ── Utilidades ────────────────────────────────────────────────────────────

    @staticmethod
    def _wait_and_get_token_id(tx_hash: str, w3: Web3 = None) -> int | None:
        """Espera la transacción y extrae el tokenId del evento Transfer (ERC-721)."""
        if w3 is None:
            w3 = Web3Service._get_w3()
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)
            for log in receipt.get('logs', []):
                if log.get('topics') and w3.to_hex(log['topics'][0]) == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    if len(log['topics']) == 4:
                        return int(w3.to_hex(log['topics'][3]), 16)
        except Exception as e:
            print(f"⚠️ Error al esperar recibo o parsear tokenId: {e}")
        return None

    @staticmethod
    def get_token_id_from_tx(tx_hash: str) -> int | None:
        """Espera la transacción y extrae el tokenId de la transferencia."""
        if not tx_hash or tx_hash.startswith("0x_mock") or tx_hash.startswith("0x_error"):
            import random
            return random.randint(1_000_000_000, 2_000_000_000)
        w3 = Web3Service._get_w3()
        return Web3Service._wait_and_get_token_id(tx_hash, w3)

    @staticmethod
    def transfer_board_onchain(from_address: str, to_address: str, board_token_id: int) -> str:
        """Transfiere un NFT de Tabla on-chain usando el GameController."""
        if not settings.GAME_CONTROLLER_ADDRESS or not settings.TABLAS_ADDRESS:
            return "0x_mock_transfer_board"
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        abi = _load_abi("GameController")
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.GAME_CONTROLLER_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferirTabla(from_addr, to_addr, board_token_id), w3)

    @staticmethod
    def transfer_axolotito_onchain(from_address: str, to_address: str, axolotito_token_id: int) -> str:
        """Transfiere un NFT de Axolotito on-chain usando el GameController."""
        if not settings.GAME_CONTROLLER_ADDRESS or not settings.AXOLOTITOS_ADDRESS:
            return "0x_mock_transfer_axolotito"
        w3 = Web3Service._get_w3()
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)
        abi = _load_abi("GameController")
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.GAME_CONTROLLER_ADDRESS), abi=abi)
        return Web3Service._send_tx(contract.functions.transferirAxolotito(from_addr, to_addr, axolotito_token_id), w3)

    @staticmethod
    def verify_usdc_payment(
        tx_hash: str,
        expected_recipient: str,
        min_usdc: float,
        expected_sender: str | None = None,  # wallet del usuario — anti tx-hash theft
    ) -> bool:
        """
        Verifica que tx_hash sea una Transfer USDC válida:
          - al treasury (expected_recipient)
          - por >= min_usdc (tolerancia 1%)
          - desde expected_sender si se provee (previene que otro reclame el mismo tx)
        En modo dev (mock hashes) siempre devuelve True.
        """
        if not tx_hash:
            if settings.ALLOW_DEV_PAYMENTS:
                return True
            return False

        if tx_hash.startswith("0x_mock"):
            if settings.ALLOW_DEV_PAYMENTS:
                return True
            return False

        if not re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash):
            return False

        if not settings.USDC_ADDRESS:
            if settings.ALLOW_DEV_PAYMENTS:
                print("⚠️ USDC_ADDRESS no configurado. Asumiendo pago válido (ALLOW_DEV_PAYMENTS=True).")
                return True
            else:
                print("🚨 ERROR: USDC_ADDRESS no configurado en producción/testnet.")
                return False

        try:
            w3 = Web3Service._get_w3()
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if not receipt or receipt.get("status") != 1:
                return False

            TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
            usdc_addr      = Web3.to_checksum_address(settings.USDC_ADDRESS)
            recipient_addr = Web3.to_checksum_address(expected_recipient)
            sender_addr    = Web3.to_checksum_address(expected_sender) if expected_sender else None
            min_amount     = int(min_usdc * 1_000_000 * 0.99)  # USDC 6 decimales, 1% tolerancia

            for log in receipt.get("logs", []):
                topics = log.get("topics", [])
                if len(topics) < 3:
                    continue
                if w3.to_hex(topics[0]) != TRANSFER_TOPIC:
                    continue
                if log.get("address", "").lower() != usdc_addr.lower():
                    continue
                # topic[1] = from (indexed), topic[2] = to (indexed) — 32 bytes padded
                from_addr = Web3.to_checksum_address("0x" + w3.to_hex(topics[1])[26:])
                to_addr   = Web3.to_checksum_address("0x" + w3.to_hex(topics[2])[26:])
                if to_addr.lower() != recipient_addr.lower():
                    continue
                # Verificar remitente si se proporcionó (clave de seguridad anti-theft)
                if sender_addr and from_addr.lower() != sender_addr.lower():
                    print(f"⚠️ tx {tx_hash}: from={from_addr} no coincide con sender esperado {sender_addr}")
                    continue
                amount = int(w3.to_hex(log.get("data", "0x0")), 16)
                if amount >= min_amount:
                    return True

            return False
        except Exception as e:
            print(f"⚠️ Error verificando pago USDC: {e}")
            return False

    @staticmethod
    def get_treasury_address() -> str:
        """Devuelve la dirección pública del Treasury derivada del private key."""
        w3 = Web3Service._get_w3()
        account = w3.eth.account.from_key(settings.TREASURY_PRIVATE_KEY)
        return account.address

    @staticmethod
    def is_connected() -> bool:
        """Verifica si hay conexión con la blockchain."""
        try:
            w3 = Web3Service._get_w3()
            return w3.is_connected()
        except Exception:
            return False

    @staticmethod
    def get_mode() -> str:
        """Devuelve el modo de blockchain activo."""
        return settings.BLOCKCHAIN_MODE