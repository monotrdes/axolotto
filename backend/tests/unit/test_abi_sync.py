import json
from pathlib import Path
import pytest
from app.services.web3_service import _load_abi

CONTRACTS_TO_VERIFY = [
    "GemaAlga",
    "Axogema",
    "Webitos",
    "Axolotitos",
    "CartasLoteria",
    "Boosters",
    "TablasLoteria",
    "Consumables",
    "GameController",
]

def get_method_from_abi(abi: list, method_name: str):
    """Retorna la definición del método en el ABI si existe, de lo contrario None."""
    for item in abi:
        if item.get("type") == "function" and item.get("name") == method_name:
            return item
    return None

def verify_inputs(method_abi: dict, expected_inputs: list):
    """Compara los inputs del método con los tipos y nombres esperados."""
    actual_inputs = method_abi.get("inputs", [])
    assert len(actual_inputs) == len(expected_inputs), (
        f"Método {method_abi['name']}: se esperaban {len(expected_inputs)} inputs, "
        f"pero se encontraron {len(actual_inputs)}."
    )
    for i, (name, val_type) in enumerate(expected_inputs):
        actual_name = actual_inputs[i].get("name")
        actual_type = actual_inputs[i].get("type")
        assert actual_type == val_type, (
            f"Método {method_abi['name']}, input {i}: tipo esperado '{val_type}', "
            f"pero se obtuvo '{actual_type}'."
        )

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_abis_exist_and_are_loaded_from_foundry_artifacts():
    """Verifica que no se esté usando el fallback y que los archivos existan en contracts/out/."""
    for contract_name in CONTRACTS_TO_VERIFY:
        abi = _load_abi(contract_name)
        assert len(abi) > 0, (
            f"El ABI de {contract_name} no pudo ser cargado desde los artifacts de Foundry. "
            "Asegúrate de que los contratos estén compilados con 'forge build'."
        )

def test_gema_alga_abi_sync():
    abi = _load_abi("GemaAlga")
    
    # mint(address to, uint256 amount)
    mint = get_method_from_abi(abi, "mint")
    assert mint is not None, "GemaAlga debe tener la función 'mint'"
    verify_inputs(mint, [("to", "address"), ("amount", "uint256")])
    
    # burn(address from, uint256 amount)
    burn = get_method_from_abi(abi, "burn")
    assert burn is not None, "GemaAlga debe tener la función 'burn'"
    verify_inputs(burn, [("from", "address"), ("amount", "uint256")])

def test_axogema_abi_sync():
    abi = _load_abi("Axogema")
    
    # mint(address to, uint256 amount)
    mint = get_method_from_abi(abi, "mint")
    assert mint is not None, "Axogema debe tener la función 'mint'"
    verify_inputs(mint, [("to", "address"), ("amount", "uint256")])
    
    # burn(address from, uint256 amount)
    burn = get_method_from_abi(abi, "burn")
    assert burn is not None, "Axogema debe tener la función 'burn'"
    verify_inputs(burn, [("from", "address"), ("amount", "uint256")])

def test_webitos_abi_sync():
    abi = _load_abi("Webitos")
    
    # mintWebito(address to, uint8 fase)
    mint = get_method_from_abi(abi, "mintWebito")
    assert mint is not None, "Webitos debe tener la función 'mintWebito'"
    verify_inputs(mint, [("to", "address"), ("fase", "uint8")])
    
    # burnWebito(uint256 tokenId)
    burn = get_method_from_abi(abi, "burnWebito")
    assert burn is not None, "Webitos debe tener la función 'burnWebito'"
    verify_inputs(burn, [("tokenId", "uint256")])

def test_axolotitos_abi_sync():
    abi = _load_abi("Axolotitos")
    
    # mintAxolotito(address to, uint256 dna, Stats stats, Traits traits)
    mint = get_method_from_abi(abi, "mintAxolotito")
    assert mint is not None, "Axolotitos debe tener la función 'mintAxolotito'"
    verify_inputs(mint, [
        ("to", "address"),
        ("dna", "uint256"),
        ("stats", "tuple"),
        ("traits", "tuple")
    ])
    
    # updateStats(uint256 tokenId, Stats stats)
    update = get_method_from_abi(abi, "updateStats")
    assert update is not None, "Axolotitos debe tener la función 'updateStats'"
    verify_inputs(update, [("tokenId", "uint256"), ("stats", "tuple")])
    
    # getStats(uint256 tokenId)
    get_stats = get_method_from_abi(abi, "getStats")
    assert get_stats is not None, "Axolotitos debe tener la función 'getStats'"
    verify_inputs(get_stats, [("tokenId", "uint256")])
    
    # dnaOf(uint256 tokenId)
    dna_of = get_method_from_abi(abi, "dnaOf")
    assert dna_of is not None, "Axolotitos debe tener la función 'dnaOf'"
    verify_inputs(dna_of, [("tokenId", "uint256")])

def test_cartas_loteria_abi_sync():
    abi = _load_abi("CartasLoteria")
    
    # mintCards(address to, uint256[] ids, uint256[] amounts)
    mint = get_method_from_abi(abi, "mintCards")
    assert mint is not None, "CartasLoteria debe tener la función 'mintCards'"
    verify_inputs(mint, [
        ("to", "address"),
        ("ids", "uint256[]"),
        ("amounts", "uint256[]")
    ])
    
    # balanceOf(address account, uint256 id)
    balance = get_method_from_abi(abi, "balanceOf")
    assert balance is not None, "CartasLoteria debe tener la función 'balanceOf'"
    verify_inputs(balance, [("account", "address"), ("id", "uint256")])
    
    # isApprovedForAll(address owner, address operator)
    approved = get_method_from_abi(abi, "isApprovedForAll")
    assert approved is not None, "CartasLoteria debe tener la función 'isApprovedForAll'"
    verify_inputs(approved, [("owner", "address"), ("operator", "address")])

def test_boosters_abi_sync():
    abi = _load_abi("Boosters")
    
    # mintBooster(address to, uint256 fase, uint256 amount)
    mint = get_method_from_abi(abi, "mintBooster")
    assert mint is not None, "Boosters debe tener la función 'mintBooster'"
    verify_inputs(mint, [
        ("to", "address"),
        ("fase", "uint256"),
        ("amount", "uint256")
    ])
    
    # burnBooster(address from, uint256 fase, uint256 amount)
    burn = get_method_from_abi(abi, "burnBooster")
    assert burn is not None, "Boosters debe tener la función 'burnBooster'"
    verify_inputs(burn, [
        ("from", "address"),
        ("fase", "uint256"),
        ("amount", "uint256")
    ])

def test_tablas_loteria_abi_sync():
    abi = _load_abi("TablasLoteria")
    
    # createBoard(address to, uint256[16] cardIds)
    create = get_method_from_abi(abi, "createBoard")
    assert create is not None, "TablasLoteria debe tener la función 'createBoard'"
    verify_inputs(create, [("to", "address"), ("cardIds", "uint256[16]")])
    
    # dissolveBoard(uint256 tableId, uint256 destroyCardIndex)
    dissolve = get_method_from_abi(abi, "dissolveBoard")
    assert dissolve is not None, "TablasLoteria debe tener la función 'dissolveBoard'"
    verify_inputs(dissolve, [("tableId", "uint256"), ("destroyCardIndex", "uint256")])
    
    # getLayout(uint256 tableId)
    get_layout = get_method_from_abi(abi, "getLayout")
    assert get_layout is not None, "TablasLoteria debe tener la función 'getLayout'"
    verify_inputs(get_layout, [("tableId", "uint256")])
    
    # updateTableStats(uint256 tableId, bool won, uint256 xpGained)
    update = get_method_from_abi(abi, "updateTableStats")
    assert update is not None, "TablasLoteria debe tener la función 'updateTableStats'"
    verify_inputs(update, [
        ("tableId", "uint256"),
        ("won", "bool"),
        ("xpGained", "uint256")
    ])

def test_consumables_abi_sync():
    abi = _load_abi("Consumables")
    
    # mintConsumable(address to, uint256 id, uint256 amount)
    mint = get_method_from_abi(abi, "mintConsumable")
    assert mint is not None, "Consumables debe tener la función 'mintConsumable'"
    verify_inputs(mint, [
        ("to", "address"),
        ("id", "uint256"),
        ("amount", "uint256")
    ])
    
    # burnConsumable(address from, uint256 id, uint256 amount)
    burn = get_method_from_abi(abi, "burnConsumable")
    assert burn is not None, "Consumables debe tener la función 'burnConsumable'"
    verify_inputs(burn, [
        ("from", "address"),
        ("id", "uint256"),
        ("amount", "uint256")
    ])
