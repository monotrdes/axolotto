import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlmodel import select

from app.models.economy import CurrencyType, TransactionLedger, Wallet
from app.models.items import ItemCatalog, ItemType, PlayerInventory, Rarity
from app.api.v1.endpoints.shop import (
    melt_card_endpoint as melt_card, forge_card_endpoint as forge_card, MeltCardRequest, ForgeCardRequest,
    roll_capsule, roll_triple_suerte, CapsuleRollRequest, TripleSuerteRequest
)
from tests.conftest import make_user, make_wallet, make_item


@pytest.fixture(autouse=True)
def mock_web3(monkeypatch):
    """Mock Web3Service to prevent real blockchain calls during tests."""
    monkeypatch.setattr(
        "app.services.web3_service.Web3Service.burn_frj",
        MagicMock(return_value=None),
    )


def test_melt_card_success(session):
    # 1. Setup user, wallet and items
    user = make_user(session, privy_did="did:privy:melt_user")
    wallet = make_wallet(session, user.privy_did, gemas_alga=1000.0)

    # Make common card to melt
    common_card = make_item(
        session, name="Carta Comun A", item_type=ItemType.CARD, rarity=Rarity.COMMON
    )
    # Seed 5 copies in player inventory
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=5, is_first_edition=False, is_shiny=False
    ))

    # Make rare card (next rarity) that will be chosen randomly
    rare_card = make_item(
        session, name="Carta Rara B", item_type=ItemType.CARD, rarity=Rarity.RARE
    )
    session.commit()

    # 2. Invoke melt endpoint
    req = MeltCardRequest(card_id=common_card.id, is_first_edition=False)
    res = melt_card(request=req, session=session, verified_user_id=user.privy_did)

    # 3. Assertions
    assert res["success"] is True
    assert res["new_card"]["id"] == rare_card.id
    assert res["new_card"]["rarity"] == "rare"

    # Wallet fee deducted: 1000.0 - 100.0 = 900.0
    assert res["balance_gal"] == 900.0
    # 10 common fragments added
    assert res["fragments"]["frag_comun"] == 10

    # Verify inventory card count
    inv_common = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == common_card.id)
    ).first()
    assert inv_common is None  # all 5 copias were consumed

    inv_rare = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == rare_card.id)
    ).first()
    assert inv_rare is not None
    assert inv_rare.quantity == 1


def test_melt_card_insufficient_copies(session):
    user = make_user(session, privy_did="did:privy:melt_user2")
    wallet = make_wallet(session, user.privy_did, gemas_alga=1000.0)

    common_card = make_item(
        session, name="Carta Comun A", item_type=ItemType.CARD, rarity=Rarity.COMMON
    )
    # Seed only 4 copies
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=4, is_first_edition=False, is_shiny=False
    ))
    session.commit()

    req = MeltCardRequest(card_id=common_card.id, is_first_edition=False)
    with pytest.raises(HTTPException) as exc:
        melt_card(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "No tienes suficientes copias" in exc.value.detail


def test_melt_card_insufficient_gal(session):
    user = make_user(session, privy_did="did:privy:melt_user3")
    wallet = make_wallet(session, user.privy_did, gemas_alga=50.0)  # Cuesta 100 GAL

    common_card = make_item(
        session, name="Carta Comun A", item_type=ItemType.CARD, rarity=Rarity.COMMON
    )
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=common_card.id, quantity=5, is_first_edition=False, is_shiny=False
    ))
    session.commit()

    req = MeltCardRequest(card_id=common_card.id, is_first_edition=False)
    with pytest.raises(HTTPException) as exc:
        melt_card(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "Frijolitos insuficientes" in exc.value.detail


def test_forge_card_success(session):
    user = make_user(session, privy_did="did:privy:forge_user")
    wallet = make_wallet(session, user.privy_did, gemas_alga=1000.0)
    
    # Give user fragments: 250 epic fragments
    wallet.frag_epico = 250
    session.add(wallet)

    # Card to forge: Epic card (requires 250 epic frags + 1000 GAL)
    epic_card = make_item(
        session, name="Carta Epica B", item_type=ItemType.CARD, rarity=Rarity.EPIC
    )
    session.commit()

    # Invoke forge endpoint
    req = ForgeCardRequest(target_card_id=epic_card.id)
    res = forge_card(request=req, session=session, verified_user_id=user.privy_did)

    assert res["success"] is True
    assert res["forged_card"]["id"] == epic_card.id
    assert res["balance_gal"] == 0.0
    assert res["fragments"]["frag_epico"] == 0

    # Verify inventory
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user.privy_did)
        .where(PlayerInventory.item_id == epic_card.id)
    ).first()
    assert inv is not None
    assert inv.quantity == 1


def test_forge_card_insufficient_fragments(session):
    user = make_user(session, privy_did="did:privy:forge_user2")
    wallet = make_wallet(session, user.privy_did, gemas_alga=1000.0)
    
    # Give only 249 epic fragments
    wallet.frag_epico = 249
    session.add(wallet)

    epic_card = make_item(
        session, name="Carta Epica B", item_type=ItemType.CARD, rarity=Rarity.EPIC
    )
    session.commit()

    req = ForgeCardRequest(target_card_id=epic_card.id)
    with pytest.raises(HTTPException) as exc:
        forge_card(request=req, session=session, verified_user_id=user.privy_did)

    assert exc.value.status_code == 400
    assert "Fragmentos insuficientes" in exc.value.detail


def _seed_capsule_catalog(session):
    for r in (Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY):
        make_item(session, f"Carta {r.value}", ItemType.CARD, rarity=r)
        make_item(session, f"Acc {r.value}", ItemType.ACCESSORY, rarity=r)
    make_item(session, "Booster Cápsula", ItemType.BOOSTER,
              item_metadata={"pack_theme": "pure", "fase": 1})
    make_item(session, "Webito Cápsula", ItemType.EGG, price_gal=200.0)
    session.commit()


def test_capsule_roll_with_capsule_item(session):
    user = make_user(session, privy_did="did:privy:capsule_user")
    wallet = make_wallet(session, user.privy_did, gemas_alga=100.0)
    _seed_capsule_catalog(session)

    # Create capsule items in catalog
    for tier_name in ("bronce", "plata", "oro"):
        existing = session.exec(
            select(ItemCatalog).where(ItemCatalog.name == f"Cápsula {tier_name.capitalize()}")
        ).first()
        if not existing:
            make_item(session, f"Cápsula {tier_name.capitalize()}", ItemType.CONSUMABLE,
                      item_metadata={"capsule_tier": tier_name})
    session.commit()

    # 1. Bronce roll using capsule item
    capsula_bronce = session.exec(
        select(ItemCatalog).where(ItemCatalog.name == "Cápsula Bronce")
    ).first()
    assert capsula_bronce is not None
    session.add(PlayerInventory(
        user_id=user.privy_did, item_id=capsula_bronce.id, quantity=1,
        is_first_edition=False, is_shiny=False
    ))
    session.commit()

    req = CapsuleRollRequest(tier="bronce", use_capsule=True)
    from unittest.mock import patch
    with patch("app.services.capsule_service._rng.random", return_value=0.99):
        res = roll_capsule(request=req, session=session, verified_user_id=user.privy_did)
    assert res is not None
    # Capsule consumed
    inv = session.exec(select(PlayerInventory).where(PlayerInventory.user_id == user.privy_did).where(PlayerInventory.item_id == capsula_bronce.id)).first()
    assert inv is None
    # No FRJ was charged
    assert res["balance_after"] == pytest.approx(100.0)

    # 2. Test insufficient capsule raises error
    # capsule was already consumed, should have 0 now
    req = CapsuleRollRequest(tier="bronce", use_capsule=True)
    with pytest.raises(HTTPException) as exc:
        roll_capsule(request=req, session=session, verified_user_id=user.privy_did)
    assert exc.value.status_code == 400
    assert "Cápsula" in exc.value.detail


def test_triple_suerte_charges_frj(session):
    user = make_user(session, privy_did="did:privy:triple_user")
    wallet = make_wallet(session, user.privy_did, gemas_alga=25000.0)
    _seed_capsule_catalog(session)
    from unittest.mock import patch

    with patch("app.services.capsule_service._rng.random", return_value=0.99):
        res = roll_triple_suerte(request=TripleSuerteRequest(), session=session, verified_user_id=user.privy_did)
    assert len(res["results"]) == 3
    assert res["total_cost"] == 22500.0
    assert res["balance_after"] == pytest.approx(25000.0 - 22500.0)
