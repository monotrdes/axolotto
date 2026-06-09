"""
test_shop_service.py — Pruebas unitarias de ShopService.buy_item

Cubre los flujos críticos:
  - Guards de validación (usuario, ítem, wallet)
  - Verificaciones de saldo (soft y hard check)
  - Límites anti-whale (boosters, webitos)
  - Stock y transiciones de fase
  - Compras exitosas (booster, egg, currency_pack)
  - Mecánicas VIP (descuento por tier)
  - Tolerancia a fallos Web3 (errores de burn se swallowean)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.economy import (
    CurrencyType, TransactionLedger, TransactionType, Wallet,
)
from app.models.items import ItemCatalog, ItemType, PlayerInventory, Rarity
from app.models.axolotito import Axolotito
from app.services.shop_service import ShopService

from tests.conftest import make_user, make_wallet, make_item, make_card_pool

# ---------------------------------------------------------------------------
# Fixture local: booster pure sin metadata de fase
# ---------------------------------------------------------------------------

def _make_booster(session, price_axg=50.0, price_gal=None, max_supply=None,
                  pack_theme="pure", fase=1):
    return make_item(
        session,
        name="Booster Test",
        item_type=ItemType.BOOSTER,
        price_axg=price_axg,
        price_gal=price_gal,
        max_supply=max_supply,
        item_metadata={"pack_theme": pack_theme, "fase": fase},
    )


def _make_egg(session, price_gal=200.0, max_supply=None):
    return make_item(
        session,
        name="Webito Test",
        item_type=ItemType.EGG,
        price_gal=price_gal,
        max_supply=max_supply,
    )


# ---------------------------------------------------------------------------
# Parche global: Web3Service siempre mockeado en este módulo para no
# necesitar nodo blockchain ni contrato desplegado.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_web3(monkeypatch):
    """Reemplaza todos los métodos externos de Web3Service por no-ops."""
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.burn_axogemas",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.burn_gal",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.mint_gal",
        MagicMock(return_value=None),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.mint_cards_onchain",
        MagicMock(return_value="0xfaketxhash"),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.mint_webito_onchain",
        MagicMock(return_value="0xfaketxhash"),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.mint_booster_onchain",
        MagicMock(return_value="0xfaketxhash"),
    )
    monkeypatch.setattr(
        "app.services.shop_service.Web3Service.burn_booster_onchain",
        MagicMock(return_value="0xburnhash"),
    )


# ===========================================================================
# 1. Guards de validación
# ===========================================================================

class TestBuyItemGuards:

    def test_user_not_found_raises_400(self, session):
        item = _make_booster(session)
        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, "did:privy:no_existe", item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 400
        assert "Usuario no encontrado" in exc.value.detail

    def test_item_not_found_raises_404(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=1000)
        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, 999999, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 404

    def test_inactive_item_raises_404(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=1000)
        item = _make_booster(session)
        item.is_active = False
        session.add(item)
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 404

    def test_missing_wallet_address_for_nft_raises_400(self, session):
        """Un usuario sin wallet Web3 no puede comprar NFTs (boosters, eggs)."""
        user = make_user(session, wallet_address=None)
        make_wallet(session, user.privy_did, axogemas=1000)
        item = _make_booster(session)

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 400
        assert "wallet Web3" in exc.value.detail

    def test_no_price_for_currency_raises_400(self, session):
        """Si el ítem no tiene precio en la moneda elegida, se rechaza."""
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        # price_gal=None → no se puede comprar con GAL
        item = make_item(
            session, "Item sin GAL", ItemType.BOOSTER,
            price_axg=50.0, price_gal=None,
            item_metadata={"pack_theme": "pure", "fase": 1},
        )

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code == 400
        assert "no se puede comprar" in exc.value.detail


# ===========================================================================
# 2. Verificaciones de saldo
# ===========================================================================

class TestBalanceChecks:

    def test_insufficient_axg_balance_raises_400(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=10.0)  # necesita 50
        item = _make_booster(session, price_axg=50.0)
        make_card_pool(session)

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code in (400, 402)
        assert "Saldo insuficiente" in exc.value.detail

    def test_insufficient_gal_balance_raises_400(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=50.0)  # necesita 200
        item = _make_egg(session, price_gal=200.0)

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code in (400, 402)
        assert "Saldo insuficiente" in exc.value.detail

    def test_exact_balance_succeeds(self, session):
        """Compra con saldo exactamente igual al precio — debe funcionar."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=50.0)
        item = _make_booster(session, price_axg=50.0)
        make_card_pool(session)

        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert result is not None


# ===========================================================================
# 3. Límites anti-whale
# ===========================================================================

class TestAntiWhaleLimits:

    def test_booster_limit_100_per_user(self, session):
        """Un usuario no puede comprar más de 100 boosters en total."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=9999)
        item = _make_booster(session, price_axg=50.0)

        # Insertar 100 entradas de compra de booster en el ledger
        for _ in range(100):
            session.add(TransactionLedger(
                user_id=user.privy_did,
                amount=50.0,
                currency=CurrencyType.AXOGEMA,
                tx_type=TransactionType.BOOSTER_PURCHASE,
                item_id=item.id,
                description="Booster Test",
            ))
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 400
        assert "Límite de preventa" in exc.value.detail

    def test_egg_limit_at_7_raises_400(self, session):
        """Un usuario no puede tener más de 7 webitos/axolotitos (sin VIP, con cueva nivel 7)."""
        user = make_user(session)
        user.cave_level = 7
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        # Crear 7 webitos en inventario
        egg_catalog = _make_egg(session, price_gal=200.0)
        session.add(PlayerInventory(
            user_id=user.privy_did, item_id=egg_catalog.id, quantity=7,
        ))
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code == 400
        assert "Límite alcanzado" in exc.value.detail

    def test_egg_limit_counts_hatched_axolotitos(self, session):
        """El límite de webitos cuenta también los axolotitos ya eclosionados."""
        user = make_user(session)
        user.cave_level = 7
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        egg_catalog = _make_egg(session, price_gal=200.0)

        # 4 webitos en inventario + 3 axolotitos eclosionados = 7 → límite
        session.add(PlayerInventory(
            user_id=user.privy_did, item_id=egg_catalog.id, quantity=4,
        ))
        for i in range(3):
            session.add(Axolotito(
                user_id=user.privy_did,
                name=f"Axo {i}",
                dna=f"DNA_{i}",
            ))
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code == 400
        assert "Límite alcanzado" in exc.value.detail

    def test_egg_limit_higher_for_axolite_vip(self, session):
        """Un usuario VIP Axolite tiene límite de 8 webitos (7 + 1 bonus slot, con cueva nivel 7)."""
        user = make_user(session, is_vip=True, vip_tier="axolite")
        user.cave_level = 7
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        egg_catalog = _make_egg(session, price_gal=200.0)

        # 7 webitos: debería poder comprar 1 más (límite = 8)
        session.add(PlayerInventory(
            user_id=user.privy_did, item_id=egg_catalog.id, quantity=7,
        ))
        session.commit()

        # No debe lanzar excepción
        result = ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert result is not None

    def test_egg_purchase_fails_when_no_nest_available(self, session):
        """No se puede comprar un huevo si no se tienen nidos disponibles (ej. cave_level=1, ya tiene 1 huevo)."""
        user = make_user(session)
        user.cave_level = 1
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        egg_catalog = _make_egg(session, price_gal=200.0)

        # Crear 1 huevo en el inventario, lo que llena el único nido disponible para nivel 1 (1 + 0 = 1 slot)
        session.add(PlayerInventory(
            user_id=user.privy_did, item_id=egg_catalog.id, quantity=1,
        ))
        session.commit()

        # Intentar comprar otro huevo debería fallar
        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code == 400
        assert "No tienes nidos disponibles" in exc.value.detail

    def test_egg_purchase_fails_when_axolotito_occupies_only_nest(self, session):
        """Un axolotito eclosionado ocupa su nido/dormitorio — no hay espacio para un webito."""
        user = make_user(session)
        user.cave_level = 1
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        egg_catalog = _make_egg(session, price_gal=200.0)

        # El axolotito del tutorial ocupa el único nido (cave_level=1 → 1 nido)
        session.add(Axolotito(user_id=user.privy_did, name="Axo Tutorial"))
        session.commit()

        # No hay huevos en inventario, pero el nido está ocupado por el axolotito
        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert exc.value.status_code == 400
        assert "No tienes nidos disponibles" in exc.value.detail

    def test_egg_purchase_allowed_after_cave_expansion(self, session):
        """Al expandir el cenote a nivel 2 (2 nidos) con 1 axolotito, se puede comprar un webito."""
        user = make_user(session)
        user.cave_level = 2
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=9999)
        egg_catalog = _make_egg(session, price_gal=200.0)

        # 1 axolotito ocupa 1 de los 2 nidos del nivel 2
        session.add(Axolotito(user_id=user.privy_did, name="Axo Tutorial"))
        session.commit()

        # Debería poder comprar el webito en el nido libre
        result = ShopService.buy_item(session, user.privy_did, egg_catalog.id, CurrencyType.GEMA_ALGA)
        assert result is not None


# ===========================================================================
# 4. Stock y transiciones de fase
# ===========================================================================

class TestStockAndPhaseTransition:

    def test_sold_out_item_raises_400(self, session):
        """Un ítem con max_supply ya alcanzado devuelve 400 Sold Out."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=9999)
        item = _make_booster(session, max_supply=1)

        # Simular que ya se vendió 1 booster (max_supply alcanzado)
        session.add(TransactionLedger(
            user_id=user.privy_did,
            amount=50.0,
            currency=CurrencyType.AXOGEMA,
            tx_type=TransactionType.BOOSTER_PURCHASE,
            item_id=item.id,
            description=f"Apertura instantánea de {item.name}",
        ))
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 400
        assert "Sold Out" in exc.value.detail

    def test_sold_out_deactivates_item(self, session):
        """Al alcanzar max_supply, el ítem queda is_active=False."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=9999)
        item = _make_booster(session, max_supply=1)

        session.add(TransactionLedger(
            user_id=user.privy_did,
            amount=50.0,
            currency=CurrencyType.AXOGEMA,
            tx_type=TransactionType.BOOSTER_PURCHASE,
            item_id=item.id,
            description=f"Apertura instantánea de {item.name}",
        ))
        session.commit()

        try:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        except HTTPException:
            pass

        session.refresh(item)
        assert item.is_active is False

    def test_phase_transition_activates_fase2_when_fase1_sold_out(self, session):
        """Al agotarse un ítem de fase=1, debe activarse automáticamente el de fase=2."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=9999)

        fase1 = make_item(
            session, "Booster Fase 1", ItemType.BOOSTER,
            price_axg=50.0, max_supply=1,
            item_metadata={"pack_theme": "pure", "fase": 1},
        )
        fase2 = make_item(
            session, "Booster Fase 2", ItemType.BOOSTER,
            price_axg=50.0, is_active=False,
            item_metadata={"pack_theme": "pure", "fase": 2},
        )

        # Simular sold out de fase 1
        session.add(TransactionLedger(
            user_id=user.privy_did,
            amount=50.0,
            currency=CurrencyType.AXOGEMA,
            tx_type=TransactionType.BOOSTER_PURCHASE,
            item_id=fase1.id,
            description=f"Apertura instantánea de {fase1.name}",
        ))
        session.commit()

        try:
            ShopService.buy_item(session, user.privy_did, fase1.id, CurrencyType.AXOGEMA)
        except HTTPException:
            pass

        session.refresh(fase2)
        assert fase2.is_active is True, "La Fase 2 debe activarse automáticamente al agotarse Fase 1"


# ===========================================================================
# 5. Booster sellado (buy_item) + apertura (open_booster)
# ===========================================================================

class TestBoosterPurchase:

    # ---- buy_item: compra el sobre sellado ----------------------------------

    def test_buy_booster_returns_sealed_booster(self, session):
        """buy_item devuelve un sobre sellado; las cartas se revelan en open_booster."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        assert result["tipo"] == "sealed_booster"
        assert result["item_id"] == item.id
        assert "cards" not in result

    def test_buy_booster_increments_inventory(self, session):
        """Comprar un booster agrega 1 sobre sellado al inventario."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is not None
        assert inv.quantity == 1

    def test_buy_booster_increments_existing_inventory(self, session):
        """Comprar un segundo booster del mismo tipo suma quantity, no crea duplicado."""
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=1000.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        entries = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).all()
        assert len(entries) == 1
        assert entries[0].quantity == 2

    def test_buy_booster_decrements_wallet_axg(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.axogemas == pytest.approx(450.0)

    def test_buy_booster_creates_ledger_entry(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        ledger = session.exec(
            select(TransactionLedger)
            .where(TransactionLedger.user_id == user.privy_did)
            .where(TransactionLedger.tx_type == TransactionType.BOOSTER_PURCHASE)
        ).first()
        assert ledger is not None
        assert ledger.amount == pytest.approx(50.0)

    def test_buy_booster_tx_hash_returned(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        assert "tx_hash" in result

    def test_foil_monthly_limit_raises_400(self, session):
        """El Booster Brillante tiene un límite de 100 ventas mensuales globales."""
        buyer = make_user(session, privy_did="did:privy:foil_buyer")
        make_wallet(session, buyer.privy_did, axogemas=9999.0)
        item = make_item(
            session, "Booster Brillante (Foil)", ItemType.BOOSTER,
            price_axg=50.0,
            item_metadata={"pack_theme": "foil", "fase": 1},
        )

        # Simular 100 ventas globales de este mes bajo otro usuario para no
        # activar el límite per-user de 100 boosters del comprador.
        other = make_user(
            session, privy_did="did:privy:other_foil",
            wallet_address="0x0000000000000000000000000000000000000001",
        )
        make_wallet(session, other.privy_did)
        for _ in range(100):
            session.add(TransactionLedger(
                user_id=other.privy_did,
                amount=50.0,
                currency=CurrencyType.AXOGEMA,
                tx_type=TransactionType.MARKET_BUY,
                item_id=item.id,
                description=f"Compra de sobre sellado de {item.name}",
            ))
        session.commit()

        with pytest.raises(HTTPException) as exc:
            ShopService.buy_item(session, buyer.privy_did, item.id, CurrencyType.AXOGEMA)
        assert exc.value.status_code == 400
        assert "Límite mensual" in exc.value.detail

    # ---- open_booster: revela las 7 cartas ----------------------------------

    def _seed_booster_in_inventory(self, session, user, item):
        """Helper: coloca 1 sobre sellado en el inventario del usuario."""
        session.add(PlayerInventory(
            user_id=user.privy_did,
            item_id=item.id,
            quantity=1,
            is_first_edition=True,
            is_shiny=False,
        ))
        session.commit()

    def test_open_booster_gives_exactly_7_cards(self, session):
        user = make_user(session)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)
        self._seed_booster_in_inventory(session, user, item)

        result = ShopService.open_booster(session, user.privy_did, item.id)

        assert len(result["cards"]) == 7

    def test_open_booster_cards_are_unique(self, session):
        """SystemRandom.sample garantiza que no hay cartas repetidas en un sobre."""
        user = make_user(session)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)
        self._seed_booster_in_inventory(session, user, item)

        result = ShopService.open_booster(session, user.privy_did, item.id)

        card_ids = [c["id"] for c in result["cards"]]
        assert len(card_ids) == len(set(card_ids)), "Las 7 cartas deben ser únicas"

    def test_open_booster_shiny_flags_length_matches_cards(self, session):
        user = make_user(session)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)
        self._seed_booster_in_inventory(session, user, item)

        result = ShopService.open_booster(session, user.privy_did, item.id)

        assert len(result["shiny_flags"]) == 7

    def test_open_foil_booster_has_exactly_5_shiny_cards(self, session):
        """El Booster Brillante (foil) siempre entrega exactamente 5 cartas shiny."""
        user = make_user(session)
        make_card_pool(session, count=10)
        item = make_item(
            session, "Booster Brillante (Foil)", ItemType.BOOSTER,
            price_axg=50.0,
            item_metadata={"pack_theme": "foil", "fase": 1},
        )
        self._seed_booster_in_inventory(session, user, item)

        result = ShopService.open_booster(session, user.privy_did, item.id)

        assert sum(result["shiny_flags"]) == 5

    def test_open_booster_respects_theme_filter(self, session):
        """Un sobre de tema 'fiesta' solo entrega cartas del set FIESTA_CARDS."""
        from app.services.shop_service import FIESTA_CARDS

        user = make_user(session)
        for name in FIESTA_CARDS:
            make_item(session, name, ItemType.CARD)

        item = make_item(
            session, "Booster Fiesta", ItemType.BOOSTER,
            price_axg=50.0,
            item_metadata={"pack_theme": "fiesta", "fase": 1},
        )
        self._seed_booster_in_inventory(session, user, item)

        result = ShopService.open_booster(session, user.privy_did, item.id)

        card_names = {c["name"] for c in result["cards"]}
        assert card_names.issubset(FIESTA_CARDS), (
            f"Cartas fuera del set fiesta: {card_names - FIESTA_CARDS}"
        )

    def test_open_booster_consumes_inventory(self, session):
        """Abrir un sobre reduce su quantity en 1 (o lo elimina si queda en 0)."""
        user = make_user(session)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)
        self._seed_booster_in_inventory(session, user, item)

        ShopService.open_booster(session, user.privy_did, item.id)

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is None or inv.quantity == 0


# ===========================================================================
# 6. Compra de webito (EGG)
# ===========================================================================

class TestEggPurchase:

    def test_egg_purchase_success(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = _make_egg(session, price_gal=200.0)

        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        assert result["tipo"] == "normal"

    def test_egg_decrements_gal_wallet(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = _make_egg(session, price_gal=200.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.gemas_alga == pytest.approx(300.0)

    def test_egg_creates_inventory_entry(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = _make_egg(session, price_gal=200.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is not None
        assert inv.quantity == 1

    def test_egg_increments_existing_inventory(self, session):
        """Si ya hay un webito en inventario, quantity debe sumar 1, no crear duplicado."""
        user = make_user(session)
        user.cave_level = 5
        session.add(user)
        make_wallet(session, user.privy_did, gemas_alga=1000.0)
        item = _make_egg(session, price_gal=200.0)

        session.add(PlayerInventory(
            user_id=user.privy_did, item_id=item.id, quantity=1,
        ))
        session.commit()

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        entries = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).all()
        assert len(entries) == 1, "No debe haber filas duplicadas en PlayerInventory"
        assert entries[0].quantity == 2

    def test_egg_creates_ledger_entry(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = _make_egg(session, price_gal=200.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        ledger = session.exec(
            select(TransactionLedger)
            .where(TransactionLedger.user_id == user.privy_did)
            .where(TransactionLedger.tx_type == TransactionType.MARKET_BUY)
        ).first()
        assert ledger is not None
        assert ledger.amount == pytest.approx(200.0)


# ===========================================================================
# 7. Currency Pack (intercambio AXG → GAL)
# ===========================================================================

class TestCurrencyPack:

    def test_currency_pack_purchase_is_forbidden(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=200.0, gemas_alga=0.0)
        item = make_item(
            session, "Pack GAL 1000", ItemType.CURRENCY_PACK,
            price_axg=100.0,
            item_metadata={"gal_amount": 1000},
        )

        with pytest.raises(HTTPException) as excinfo:
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        
        assert excinfo.value.status_code == 403
        assert "deshabilitada" in excinfo.value.detail


# ===========================================================================
# 8. Mecánicas VIP
# ===========================================================================

class TestVIPMechanics:

    @pytest.mark.parametrize("tier,discount", [
        ("coral",    0.05),
        ("dorado",   0.12),
        ("axolite",  0.20),
    ])
    def test_vip_discount_applied_by_tier(self, session, tier, discount):
        """Cada tier VIP aplica el descuento correcto al precio en AXG."""
        user = make_user(session, is_vip=True, vip_tier=tier)
        base_price = 100.0
        make_wallet(session, user.privy_did, axogemas=base_price)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=base_price)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        expected_spent = round(base_price * (1 - discount), 2)
        expected_remaining = round(base_price - expected_spent, 2)
        assert wallet.axogemas == pytest.approx(expected_remaining, abs=0.01)

    def test_vip_discount_not_applied_to_eggs(self, session):
        """Los webitos (EGG) están excluidos del descuento VIP."""
        user = make_user(session, is_vip=True, vip_tier="axolite")  # 20% discount
        price_gal = 200.0
        make_wallet(session, user.privy_did, gemas_alga=price_gal)
        item = _make_egg(session, price_gal=price_gal)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        # Sin descuento: debe haber gastado exactamente 200 GAL
        assert wallet.gemas_alga == pytest.approx(0.0)

    def test_vip_discount_not_applied_to_gal_payments(self, session):
        """El descuento VIP solo aplica a pagos con AXG, no con GAL."""
        user = make_user(session, is_vip=True, vip_tier="axolite")
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = make_item(
            session, "Booster GAL", ItemType.BOOSTER,
            price_gal=200.0,
            item_metadata={"pack_theme": "pure", "fase": 1},
        )
        make_card_pool(session, count=10)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.gemas_alga == pytest.approx(300.0)


# ===========================================================================
# 9. Tolerancia a fallos Web3
# ===========================================================================

class TestWeb3ErrorHandling:

    def test_burn_axg_failure_does_not_block_purchase(self, session, monkeypatch):
        """Si burn_axogemas falla, la compra igual debe completarse (swallowed)."""
        monkeypatch.setattr(
            "app.services.shop_service.Web3Service.burn_axogemas",
            MagicMock(side_effect=Exception("RPC timeout")),
        )
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        # No debe lanzar excepción — el error de burn se traga con un print
        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
        assert result is not None

    def test_burn_axg_failure_still_decrements_wallet(self, session, monkeypatch):
        """Aunque el burn on-chain falle, el saldo interno sí debe decrementarse."""
        monkeypatch.setattr(
            "app.services.shop_service.Web3Service.burn_axogemas",
            MagicMock(side_effect=Exception("nodo caído")),
        )
        user = make_user(session)
        make_wallet(session, user.privy_did, axogemas=500.0)
        make_card_pool(session, count=10)
        item = _make_booster(session, price_axg=50.0)

        ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.axogemas == pytest.approx(450.0)

    def test_burn_gal_failure_does_not_block_purchase(self, session, monkeypatch):
        monkeypatch.setattr(
            "app.services.shop_service.Web3Service.burn_gal",
            MagicMock(side_effect=Exception("timeout")),
        )
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)
        item = _make_egg(session, price_gal=200.0)

        result = ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.GEMA_ALGA)
        assert result is not None
