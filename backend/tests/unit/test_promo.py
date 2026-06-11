import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from app.core.config import axf_to_display, frj_to_display

from app.models.user import User
from app.models.promo import PromoCode
from app.models.items import ItemCatalog, PlayerInventory, WhitelistEntry
from app.models.economy import Wallet, TransactionLedger
from app.services.promo_service import redeem_promo_code


def _setup_promo_data(session: Session):
    # Crear un item de prueba
    item = ItemCatalog(
        id=999,
        name="Item Especial Lanzamiento",
        item_type="ACCESSORY",
        rarity="epic",
        price_axg=0.0,
        price_gal=0,
        is_active=True
    )
    session.add(item)

    # Crear códigos promocionales de prueba
    promo_valid = PromoCode(
        id=1,
        code="AXOL-VALID-12",
        batch="Lote de Lanzamiento",
        reward_type="ACCESSORY",
        reward_item_id=999,
        reward_frijolitos=1000.0,
        reward_axofichas=139.0,
        created_at=datetime.utcnow()
    )
    promo_redeemed = PromoCode(
        id=2,
        code="AXOL-USED-99",
        batch="Lote de Lanzamiento",
        reward_type="ACCESSORY",
        reward_item_id=999,
        reward_frijolitos=500.0,
        reward_axofichas=50.0,
        redeemed_by="some_other_user",
        redeemed_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    session.add_all([promo_valid, promo_redeemed])
    session.commit()
    return item, promo_valid, promo_redeemed


def test_redeem_promo_code_success(session: Session):
    item, promo_valid, _ = _setup_promo_data(session)

    # Crear usuario nuevo
    user = User(
        privy_did="user_new_promo",
        email="new_promo@axolotto.com",
        tutorial_completed=False
    )
    session.add(user)
    session.commit()

    # Canjear
    res = redeem_promo_code(session, user_id=user.privy_did, code="AXOL-VALID-12", email=user.email)
    
    assert res["status"] == "pending_tutorial"
    assert "Código verificado!" in res["mensaje"]
    assert res["frijolitos_rewarded"] == 1000.0
    assert res["axofichas_rewarded"] == 139.0
    assert res["item_id"] == 999
    assert res["item_name"] == "Item Especial Lanzamiento"

    # Reclamar premio
    from app.api.v1.endpoints.rewards import claim_pending_reward
    from fastapi import Request
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/rewards/claim",
        "headers": [],
    }
    dummy_request = Request(scope=scope)
    claim_res = claim_pending_reward(request=dummy_request, session=session, verified_user_id=user.privy_did)
    assert claim_res["status"] == "claimed"

    # Verificar balances en Wallet
    wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
    assert wallet is not None
    assert frj_to_display(wallet.frijolitos) == 1000.0
    assert axf_to_display(wallet.axofichas) == 139.0

    # Verificar inventario
    inv = session.exec(select(PlayerInventory).where(PlayerInventory.user_id == user.privy_did)).first()
    assert inv is not None
    assert inv.item_id == 999
    assert inv.quantity == 1

    # Verificar que el código quedó marcado como canjeado
    session.refresh(promo_valid)
    assert promo_valid.redeemed_by == user.privy_did
    assert promo_valid.redeemed_at is not None

    # Verificar Whitelist
    wl = session.exec(select(WhitelistEntry).where(WhitelistEntry.user_id == user.privy_did)).first()
    assert wl is not None
    assert wl.source == "souvenir"


def test_redeem_promo_code_already_redeemed_by_other(session: Session):
    _setup_promo_data(session)
    user = User(
        privy_did="user_promo_other",
        email="promo_other@axolotto.com",
        tutorial_completed=False
    )
    session.add(user)
    session.commit()

    # Intentar canjear un código ya usado
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-USED-99", email=user.email)

    assert exc.value.status_code == 409
    assert "ya fue canjeado" in exc.value.detail

    # Debe contar como intento fallido
    session.refresh(user)
    assert user.promo_code_attempts == 1


def test_redeem_promo_code_existing_user_blocked(session: Session):
    _setup_promo_data(session)
    # Crear usuario que YA completó el tutorial (usuario existente)
    user = User(
        privy_did="user_existing",
        email="existing@axolotto.com",
        tutorial_completed=True
    )
    session.add(user)
    session.commit()

    # Intentar canjear
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-VALID-12", email=user.email)

    assert exc.value.status_code == 403
    assert "solo es válido para cuentas nuevas" in exc.value.detail


def test_redeem_promo_code_max_attempts_rate_limit(session: Session):
    _setup_promo_data(session)
    user = User(
        privy_did="user_hacking_attempts",
        email="hacker@axolotto.com",
        tutorial_completed=False
    )
    session.add(user)
    session.commit()

    # 1er intento fallido
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-INVALID-1", email=user.email)
    assert exc.value.status_code == 404
    assert "Intentos restantes: 2" in exc.value.detail

    # 2do intento fallido
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-INVALID-2", email=user.email)
    assert exc.value.status_code == 404
    assert "Intentos restantes: 1" in exc.value.detail

    # 3er intento fallido
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-INVALID-3", email=user.email)
    assert exc.value.status_code == 404
    assert "Intentos restantes: 0" in exc.value.detail

    # 4to intento fallido — bloqueado por rate limit a nivel de DB
    with pytest.raises(HTTPException) as exc:
        redeem_promo_code(session, user_id=user.privy_did, code="AXOL-VALID-12", email=user.email)
    assert exc.value.status_code == 429
    assert "límite de 3 intentos fallidos" in exc.value.detail
