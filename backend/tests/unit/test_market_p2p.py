"""
test_market_p2p.py — Unit tests for the player-to-peer (P2P) inventory market.
Tests listing items, canceling listings, buying listings, checking VIP commission rates,
and mock web3 transfers on-chain.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import select, Session
from fastapi import HTTPException
from app.core.config import frj_to_internal, frj_to_display

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity, InventoryMarketListing
from app.models.user import User
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
from app.models.lobby_models import TreasuryVault

from app.api.v1.endpoints.market import (
    list_inventory_item,
    cancel_inventory_listing,
    buy_inventory_listing,
    get_inventory_listings,
    ListInventoryItemRequest,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet, make_item


@pytest.fixture(autouse=True)
def mock_web3_transfers(monkeypatch):
    """Mock Web3Service transfer methods to prevent blockchain connection errors."""
    mock_transfer_booster = MagicMock(return_value="0xfake_booster_tx")
    mock_transfer_card = MagicMock(return_value="0xfake_card_tx")
    monkeypatch.setattr("app.services.web3_service.Web3Service.transferir_sobrecito_onchain", mock_transfer_booster)
    monkeypatch.setattr("app.services.web3_service.Web3Service.transfer_card_onchain", mock_transfer_card)
    return {
        "transfer_booster": mock_transfer_booster,
        "transfer_card": mock_transfer_card,
    }


# ===========================================================================
# 1. Tests for listing inventory items (list_inventory_item)
# ===========================================================================

class TestListInventoryItem:
    def test_list_success_depletes_inventory(self, session: Session):
        """Listing an item reduces inventory quantity."""
        user = make_user(session, privy_did="did:privy:seller1")
        item = make_item(session, name="Sobre Fase 1", item_type=ItemType.BOOSTER, is_active=True)
        item.is_sellable = True
        session.add(item)
        session.commit()

        # Add 3 packs to inventory
        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=3, is_first_edition=False, is_shiny=False)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        req = ListInventoryItemRequest(inventory_id=inv.id, quantity=2, price_gal=50.0)
        res = list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)

        assert "éxito" in res["mensaje"] or "exito" in res["mensaje"].lower()
        
        # Check that inventory quantity went down to 1
        session.refresh(inv)
        assert inv.quantity == 1

        # Check listing was created
        listing = session.exec(select(InventoryMarketListing).where(InventoryMarketListing.seller_id == user.privy_did)).first()
        assert listing is not None
        assert listing.item_id == item.id
        assert listing.quantity == 2
        assert listing.price_gal == 50.0
        assert listing.is_active is True

    def test_list_success_deletes_inventory_row_when_zero(self, session: Session):
        """Listing the total quantity of an item removes it from active inventory."""
        user = make_user(session, privy_did="did:privy:seller2")
        item = make_item(session, name="Carta Común", item_type=ItemType.CARD, is_active=True)
        item.is_sellable = True
        session.add(item)
        session.commit()

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=1, is_first_edition=True, is_shiny=True)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        req = ListInventoryItemRequest(inventory_id=inv.id, quantity=1, price_gal=120.0)
        list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)

        # Inventory row should be deleted
        inv_check = session.get(PlayerInventory, inv.id)
        assert inv_check is None

        # Listing should exist
        listing = session.exec(select(InventoryMarketListing).where(InventoryMarketListing.seller_id == user.privy_did)).first()
        assert listing is not None
        assert listing.is_first_edition is True
        assert listing.is_shiny is True
        assert listing.price_gal == 120.0

    def test_list_invalid_parameters(self, session: Session):
        """Invalid quantity or price raises 400."""
        user = make_user(session, privy_did="did:privy:seller_bad")
        
        # 1. Invalid quantity
        req = ListInventoryItemRequest(inventory_id=1, quantity=0, price_gal=10.0)
        with pytest.raises(HTTPException) as exc:
            list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "cantidad" in exc.value.detail

        # 2. Invalid price
        req = ListInventoryItemRequest(inventory_id=1, quantity=2, price_gal=-5.0)
        with pytest.raises(HTTPException) as exc:
            list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "precio" in exc.value.detail

    def test_list_not_owned_or_insufficient_quantity(self, session: Session):
        """Listing an item not owned or listing more than owned raises 400."""
        user = make_user(session, privy_did="did:privy:seller_owner")
        item = make_item(session, name="Carta Rara", item_type=ItemType.CARD)
        
        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=1)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        # Try to list 2 (only have 1)
        req = ListInventoryItemRequest(inventory_id=inv.id, quantity=2, price_gal=10.0)
        with pytest.raises(HTTPException) as exc:
            list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "No posees" in exc.value.detail or "cantidad" in exc.value.detail

        # Try listing with another user's verified_user_id
        with pytest.raises(HTTPException) as exc_other:
            list_inventory_item(request=req, session=session, verified_user_id="did:privy:hacker")
        assert exc_other.value.status_code == 400

    def test_list_non_sellable_item(self, session: Session):
        """Items configured with is_sellable=False cannot be listed."""
        user = make_user(session, privy_did="did:privy:seller_unsellable")
        item = make_item(session, name="Legacy Item", item_type=ItemType.CARD)
        item.is_sellable = False
        session.add(item)
        session.commit()

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=2)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        req = ListInventoryItemRequest(inventory_id=inv.id, quantity=1, price_gal=100.0)
        with pytest.raises(HTTPException) as exc:
            list_inventory_item(request=req, session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "no se puede vender" in exc.value.detail


# ===========================================================================
# 2. Tests for canceling listings (cancel_inventory_listing)
# ===========================================================================

class TestCancelInventoryListing:
    def test_cancel_success_merges_inventory(self, session: Session):
        """Canceling a listing merges items back into existing inventory row."""
        user = make_user(session, privy_did="did:privy:canceller1")
        item = make_item(session, name="Carta Brillante", item_type=ItemType.CARD)
        
        # Existing inventory with 1 card
        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=1, is_first_edition=True, is_shiny=True)
        session.add(inv)
        
        # Listing of 2 cards (same attributes)
        listing = InventoryMarketListing(
            seller_id=user.privy_did, item_id=item.id, quantity=2,
            is_first_edition=True, is_shiny=True, price_gal=80.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        cancel_inventory_listing(listing_id=listing.id, session=session, verified_user_id=user.privy_did)

        # Inventory quantity should be 1 + 2 = 3
        session.refresh(inv)
        assert inv.quantity == 3

        # Listing should be deleted
        check_listing = session.get(InventoryMarketListing, listing.id)
        assert check_listing is None

    def test_cancel_success_creates_new_inventory_row(self, session: Session):
        """Canceling a listing creates a new inventory row if the player no longer has any."""
        user = make_user(session, privy_did="did:privy:canceller2")
        item = make_item(session, name="Sobre Rare", item_type=ItemType.BOOSTER)
        
        listing = InventoryMarketListing(
            seller_id=user.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=40.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        cancel_inventory_listing(listing_id=listing.id, session=session, verified_user_id=user.privy_did)

        # Check new PlayerInventory row exists
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is not None
        assert inv.quantity == 1

        # Check listing deleted
        assert session.get(InventoryMarketListing, listing.id) is None

    def test_cancel_non_owner_raises_404(self, session: Session):
        """A user cannot cancel another user's listing."""
        user1 = make_user(session, privy_did="did:privy:canceller_owner")
        user2 = make_user(session, privy_did="did:privy:canceller_hacker")
        item = make_item(session, name="Item Test", item_type=ItemType.CARD)
        
        listing = InventoryMarketListing(
            seller_id=user1.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=5.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        with pytest.raises(HTTPException) as exc:
            cancel_inventory_listing(listing_id=listing.id, session=session, verified_user_id=user2.privy_did)
        assert exc.value.status_code == 404
        assert "no encontrada" in exc.value.detail or "inactiva" in exc.value.detail


# ===========================================================================
# 3. Tests for buying listings (buy_inventory_listing)
# ===========================================================================

class TestBuyInventoryListing:
    def test_buy_cannot_buy_own_listing(self, session: Session):
        """Seller cannot purchase their own active listing."""
        user = make_user(session, privy_did="did:privy:self_buyer")
        item = make_item(session, name="Item", item_type=ItemType.CARD)
        listing = InventoryMarketListing(
            seller_id=user.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=10.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        with pytest.raises(HTTPException) as exc:
            buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "propia" in exc.value.detail

    def test_buy_insufficient_gal(self, session: Session):
        """Purchase fails if buyer does not have enough GAL."""
        seller = make_user(session, privy_did="did:privy:seller_gal")
        buyer = make_user(session, privy_did="did:privy:buyer_gal")
        make_wallet(session, buyer.privy_did, gemas_alga=10.0) # only has 10 GAL
        
        item = make_item(session, name="Item Raro", item_type=ItemType.CARD)
        listing = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=50.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        with pytest.raises(HTTPException) as exc:
            buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=buyer.privy_did)
        assert exc.value.status_code == 400
        assert "insuficiente" in exc.value.detail

    def test_buy_success_standard_user_5percent_fee(self, session: Session):
        """Buying with standard user accounts levies a 5% commission fee to Treasury."""
        seller = make_user(session, privy_did="did:privy:s_std")
        buyer = make_user(session, privy_did="did:privy:b_std") # standard (not VIP)
        
        seller_w = make_wallet(session, seller.privy_did, gemas_alga=0.0)
        buyer_w = make_wallet(session, buyer.privy_did, gemas_alga=100.0)
        
        item = make_item(session, name="Carta Standard", item_type=ItemType.CARD)
        listing = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=item.id, quantity=1,
            is_first_edition=True, is_shiny=False, price_gal=100.0, is_active=True
        )
        session.add(listing)
        
        treasury = TreasuryVault(balance=frj_to_internal(10.0))
        session.add(treasury)
        session.commit()
        session.refresh(listing)

        res = buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=buyer.privy_did)
        assert "éxito" in res["mensaje"] or "success" in res["mensaje"].lower()

        # Check balances:
        # Price = 100.0 GAL. Standard fee = 5% (5.0 GAL)
        # Buyer: 100.0 - 100.0 = 0.0 GAL
        # Seller: 0.0 + 95.0 = 95.0 GAL
        # Treasury: 10.0 + 5.0 = 15.0 GAL
        session.refresh(buyer_w)
        session.refresh(seller_w)
        session.refresh(treasury)

        assert buyer_w.gemas_alga == 0.0
        assert frj_to_display(seller_w.gemas_alga) == 95.0
        assert frj_to_display(treasury.balance) == 15.0

        # Check buyer has the item now
        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == buyer.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is not None
        assert inv.quantity == 1
        assert inv.is_first_edition is True
        assert inv.is_shiny is False

        # Check listing was deleted
        assert session.get(InventoryMarketListing, listing.id) is None

        # Check Transaction Ledger records
        ledgers = session.exec(select(TransactionLedger).order_by(TransactionLedger.id.desc())).all()
        # Should have 3 entries (buyer, seller, treasury)
        assert len(ledgers) >= 3
        buyer_tx = [l for l in ledgers if l.user_id == buyer.privy_did][0]
        seller_tx = [l for l in ledgers if l.user_id == seller.privy_did][0]
        treasury_tx = [l for l in ledgers if l.user_id == "treasury"][0]

        assert frj_to_display(buyer_tx.amount) == 100.0
        assert buyer_tx.tx_type == TransactionType.MARKET_BUY
        assert frj_to_display(seller_tx.amount) == 95.0
        assert seller_tx.tx_type == TransactionType.REWARD
        assert frj_to_display(treasury_tx.amount) == 5.0
        assert treasury_tx.tx_type == TransactionType.BURN

    @pytest.mark.parametrize("vip_tier, expected_rate", [
        ("coral", 0.04),
        ("dorado", 0.03),
        ("axolite", 0.02),
    ])
    def test_buy_success_vip_tiers(self, session: Session, vip_tier, expected_rate):
        """Buying with a VIP user account applies the correct discounted commission fee."""
        seller = make_user(session, privy_did=f"did:privy:s_vip_{vip_tier}")
        buyer = make_user(session, privy_did=f"did:privy:b_vip_{vip_tier}", is_vip=True, vip_tier=vip_tier)
        
        seller_w = make_wallet(session, seller.privy_did, gemas_alga=0.0)
        buyer_w = make_wallet(session, buyer.privy_did, gemas_alga=200.0)
        
        item = make_item(session, name=f"Card VIP {vip_tier}", item_type=ItemType.CARD)
        listing = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=True, price_gal=200.0, is_active=True
        )
        session.add(listing)
        
        treasury = TreasuryVault(balance=frj_to_internal(5.0))
        session.add(treasury)
        session.commit()
        session.refresh(listing)

        buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=buyer.privy_did)

        # Calculations:
        # Price = 200.0
        # Commission = Price * expected_rate (e.g. 200 * 0.015 = 3.0)
        # Seller share = Price - Commission (e.g. 197.0)
        commission = round(200.0 * expected_rate, 2)
        seller_share = 200.0 - commission

        session.refresh(buyer_w)
        session.refresh(seller_w)
        session.refresh(treasury)

        assert buyer_w.gemas_alga == 0.0
        assert frj_to_display(seller_w.gemas_alga) == seller_share
        assert frj_to_display(treasury.balance) == 5.0 + commission

    def test_buy_triggers_onchain_web3_transfers_for_booster(self, session: Session, mock_web3_transfers):
        """P2P purchase of a booster pack triggers Web3Service.transfer_booster_onchain if users have wallets."""
        seller = make_user(session, privy_did="did:privy:s_web3_b", wallet_address="0xSellerBoosterWalletAddress")
        buyer = make_user(session, privy_did="did:privy:b_web3_b", wallet_address="0xBuyerBoosterWalletAddress")
        
        make_wallet(session, seller.privy_did, gemas_alga=0.0)
        make_wallet(session, buyer.privy_did, gemas_alga=50.0)
        
        # Booster pack in catalog with phase = 2
        item = make_item(
            session, name="Sobre Test Onchain", item_type=ItemType.BOOSTER,
            item_metadata={"fase": 2}
        )
        listing = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=item.id, quantity=3,
            is_first_edition=False, is_shiny=False, price_gal=50.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=buyer.privy_did)

        # Verify mock Web3 transfer booster was called
        # transfer_booster_onchain(from, to, fase, quantity)
        mock_web3_transfers["transfer_booster"].assert_called_once_with(
            "0xSellerBoosterWalletAddress",
            "0xBuyerBoosterWalletAddress",
            2,
            3
        )
        mock_web3_transfers["transfer_card"].assert_not_called()

    def test_buy_triggers_onchain_web3_transfers_for_card(self, session: Session, mock_web3_transfers):
        """P2P purchase of a card triggers Web3Service.transfer_card_onchain if users have wallets."""
        seller = make_user(session, privy_did="did:privy:s_web3_c", wallet_address="0xSellerCardWalletAddress")
        buyer = make_user(session, privy_did="did:privy:b_web3_c", wallet_address="0xBuyerCardWalletAddress")
        
        make_wallet(session, seller.privy_did, gemas_alga=0.0)
        make_wallet(session, buyer.privy_did, gemas_alga=75.0)
        
        # Card item catalog id = 15
        item = make_item(session, name="Carta Test Onchain", item_type=ItemType.CARD)
        listing = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=item.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=75.0, is_active=True
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

        buy_inventory_listing(listing_id=listing.id, session=session, verified_user_id=buyer.privy_did)

        # Verify mock Web3 transfer card was called
        # transfer_card_onchain(from, to, card_id, quantity)
        mock_web3_transfers["transfer_card"].assert_called_once_with(
            "0xSellerCardWalletAddress",
            "0xBuyerCardWalletAddress",
            item.id,
            1
        )
        mock_web3_transfers["transfer_booster"].assert_not_called()


# ===========================================================================
# 4. Tests for listing queries (get_inventory_listings)
# ===========================================================================

class TestGetInventoryListings:
    def test_get_listings_filter_and_sort(self, session: Session):
        """Listings query successfully filters by item type and sorts by price ascending/descending."""
        # Setup catalog items
        booster = make_item(session, name="Sobre Súper", item_type=ItemType.BOOSTER)
        card_a = make_item(session, name="Carta Alfa", item_type=ItemType.CARD)
        card_b = make_item(session, name="Carta Beta", item_type=ItemType.CARD)
        
        seller = make_user(session, privy_did="did:privy:bulk_seller")

        # Create listings
        list_booster = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=booster.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=50.0, is_active=True
        )
        list_card_a = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=card_a.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=30.0, is_active=True
        )
        list_card_b = InventoryMarketListing(
            seller_id=seller.privy_did, item_id=card_b.id, quantity=1,
            is_first_edition=False, is_shiny=False, price_gal=100.0, is_active=True
        )
        session.add_all([list_booster, list_card_a, list_card_b])
        session.commit()

        # 1. Query all, sort by price_asc
        listings_asc = get_inventory_listings(item_type=None, sort="price_asc", session=session)
        assert len(listings_asc) == 3
        # Should be ordered: card_a (30), booster (50), card_b (100)
        assert listings_asc[0]["id"] == list_card_a.id
        assert listings_asc[1]["id"] == list_booster.id
        assert listings_asc[2]["id"] == list_card_b.id

        # 2. Query only CARDS, sort by price_desc
        listings_cards_desc = get_inventory_listings(item_type=ItemType.CARD, sort="price_desc", session=session)
        assert len(listings_cards_desc) == 2
        # Should be ordered: card_b (100), card_a (30)
        assert listings_cards_desc[0]["id"] == list_card_b.id
        assert listings_cards_desc[1]["id"] == list_card_a.id

        # 3. Query only BOOSTERS
        listings_boosters = get_inventory_listings(item_type=ItemType.BOOSTER, session=session)
        assert len(listings_boosters) == 1
        assert listings_boosters[0]["id"] == list_booster.id
