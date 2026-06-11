import pytest
import threading
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity
from app.models.economy import Wallet
from app.services.shop_service import ShopService
from tests.conftest import make_user, make_wallet, make_item, make_card_pool

# Parchear Web3Service para evitar llamadas reales on-chain en los hilos
@pytest.fixture(autouse=True)
def mock_web3_concurrency(monkeypatch):
    from unittest.mock import MagicMock
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.burn_sobrecito_onchain",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.mint_cards_onchain",
        MagicMock(return_value=["0xfake1", "0xfake2"]),
    )

def test_concurrent_booster_opening(engine, session):
    if engine.dialect.name == "sqlite":
        pytest.skip("SQLite no soporta bloqueo a nivel de fila (SELECT FOR UPDATE) requerido para esta prueba de concurrencia.")
        
    # 1. Setup
    user = make_user(session, privy_did="concurrency_user")
    make_wallet(session, user_id="concurrency_user", gemas_alga=100.0)
    
    # Crear cartas en catálogo
    make_card_pool(session, count=10)
    
    # Crear booster en catálogo
    booster_item = make_item(
        session,
        name="Booster Concurrency",
        item_type=ItemType.BOOSTER,
        price_axg=50.0,
        item_metadata={"pack_theme": "pure", "fase": 1}
    )
    
    # Dar exactamente 1 sobre en inventario
    inv = PlayerInventory(user_id="concurrency_user", item_id=booster_item.id, quantity=1)
    session.add(inv)
    session.commit()
    
    # 2. Hilos concurrentes
    results = []
    errors = []
    
    def worker():
        # Cada hilo debe usar su propia sesión para simular conexiones de red concurrentes
        with Session(engine) as local_session:
            try:
                res = ShopService.open_booster(
                    session=local_session,
                    user_id="concurrency_user",
                    item_id=booster_item.id
                )
                results.append(res)
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    # 3. Validar resultados
    # Exactamente una petición debe haber tenido éxito, la otra debe haber fallado
    assert len(results) == 1, f"Se esperada exactamente 1 éxito, se obtuvieron {len(results)}. Errores: {[str(e) for e in errors]}"
    assert len(errors) == 1, f"Se esperaba exactamente 1 error, se obtuvieron {len(errors)}"
    
    # El error debe ser una excepción HTTP 400 por falta de sobres en inventario
    err = errors[0]
    assert isinstance(err, HTTPException)
    assert err.status_code == 400
    assert "No tienes este booster en tu inventario." in err.detail or "No tienes este sobre" in err.detail
    
    # Validar que el inventario final en BD está vacío
    with Session(engine) as local_session:
        final_inv = local_session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == "concurrency_user")
            .where(PlayerInventory.item_id == booster_item.id)
        ).first()
        # Debe haberse eliminado o su cantidad ser <= 0
        assert final_inv is None or final_inv.quantity <= 0
