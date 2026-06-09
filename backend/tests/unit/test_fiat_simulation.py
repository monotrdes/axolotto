import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.models.user import User
from app.models.economy import Wallet, CurrencyType, AxgPurchaseRecord
from app.models.items import ItemCatalog, ItemType, Rarity
from app.services.shop_service import ShopService
from tests.conftest import make_user, make_wallet, make_item

def test_axg_purchase_record_creation(session: Session):
    # Crear un usuario de prueba
    user = make_user(session, privy_did="did:privy:sim_purchase_test")
    
    # Crear un registro de compra de AXG en pesos
    record = AxgPurchaseRecord(
        user_id=user.privy_did,
        axg_amount=7250.0,
        mxn_amount=875.0,
        pack_name="7250x$875",
        created_at=datetime.utcnow()
    )
    session.add(record)
    session.commit()
    
    # Verificar que se guardó correctamente en la base de datos
    db_record = session.exec(
        select(AxgPurchaseRecord).where(AxgPurchaseRecord.user_id == user.privy_did)
    ).first()
    
    assert db_record is not None
    assert db_record.axg_amount == 7250.0
    assert db_record.mxn_amount == 875.0
    assert db_record.pack_name == "7250x$875"


def test_axg_purchase_greedy_simulation(session: Session):
    # Simular la lógica que usamos en phase_fund_wallets
    user = make_user(session, privy_did="did:privy:sim_purchase_greedy")
    wallet = make_wallet(session, user_id=user.privy_did, axogemas=0.0)
    
    # Supongamos que el jugador necesita 8500 AXG para sus compras planificadas
    total_needed_axg = 8500.0
    
    AXG_PACKS = [
        {"axg": 7250, "price_mxn": 875.0, "name": "7250x$875"},
        {"axg": 1725, "price_mxn": 263.0, "name": "1725x$263"},
        {"axg": 550,  "price_mxn": 88.0,  "name": "550x$88"},
        {"axg": 200,  "price_mxn": 35.0,  "name": "200x$35"},
    ]

    current_obtained = 0.0
    mxn_spent = 0.0
    purchased_packs_counts = {}

    while current_obtained < total_needed_axg:
        remaining = total_needed_axg - current_obtained
        chosen_pack = None
        for pack in AXG_PACKS:
            if pack["axg"] <= remaining:
                chosen_pack = pack
                break
        if not chosen_pack:
            chosen_pack = AXG_PACKS[-1]

        # Registrar compra en la DB
        record = AxgPurchaseRecord(
            user_id=user.privy_did,
            axg_amount=chosen_pack["axg"],
            mxn_amount=chosen_pack["price_mxn"],
            pack_name=chosen_pack["name"],
            created_at=datetime.utcnow()
        )
        session.add(record)
        
        current_obtained += chosen_pack["axg"]
        mxn_spent += chosen_pack["price_mxn"]
        purchased_packs_counts[chosen_pack["name"]] = purchased_packs_counts.get(chosen_pack["name"], 0) + 1

    session.commit()
    wallet.axogemas = current_obtained
    session.add(wallet)
    session.commit()
    
    # 8500 AXG debería comprar: 1x 7250, 1x 550, 1x 550 (ya van 8350), y 1x 200 (total 8550)
    assert current_obtained == 8550.0
    assert mxn_spent == 875.0 + 88.0 + 88.0 + 35.0 # $1086 MXN
    
    # Contar registros en BD
    records = session.exec(
        select(AxgPurchaseRecord).where(AxgPurchaseRecord.user_id == user.privy_did)
    ).all()
    assert len(records) == 4
    
    # Validar sumas en BD
    total_db_mxn = sum(r.mxn_amount for r in records)
    total_db_axg = sum(r.axg_amount for r in records)
    assert total_db_mxn == 1086.0
    assert total_db_axg == 8550.0
