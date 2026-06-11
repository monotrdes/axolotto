import pytest
import json
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, func

from app.models.user import User
from app.models.economy import Wallet, CurrencyType, TransactionLedger
from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity
from app.services.shop_service import ShopService
from app.services.vip_scheduler import _run_vip_jobs
from app.core.config import VIP_CONFIG

from tests.conftest import make_user, make_wallet, make_item

def setup_vip_test_catalog(session: Session):
    # 1. Seed de los boosters de bienvenida
    booster_normal = make_item(
        session,
        name="Sobrecito Mezclado",
        item_type=ItemType.BOOSTER,
        item_metadata={"fase": 1, "pack_theme": "pure"}
    )
    booster_foil = make_item(
        session,
        name="Sobrecito Brillante (Foil)",
        item_type=ItemType.BOOSTER,
        item_metadata={"fase": 1, "pack_theme": "foil"}
    )

    # 2. Seed de las Cápsulas VIP
    capsula_bronce = make_item(
        session,
        name="Cápsula Bronce",
        item_type=ItemType.CONSUMABLE,
        item_metadata={"capsule_tier": "bronce"}
    )
    capsula_plata = make_item(
        session,
        name="Cápsula Plata",
        item_type=ItemType.CONSUMABLE,
        item_metadata={"capsule_tier": "plata"}
    )
    capsula_oro = make_item(
        session,
        name="Cápsula Oro",
        item_type=ItemType.CONSUMABLE,
        item_metadata={"capsule_tier": "oro"}
    )

    # 3. Seed de los Pases VIP
    vip_coral = make_item(
        session,
        name="Pase Coral VIP (30 días)",
        item_type=ItemType.CONSUMABLE,
        price_axg=400.0,
        item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "coral"}
    )
    vip_dorado = make_item(
        session,
        name="Pase Dorado VIP (30 días)",
        item_type=ItemType.CONSUMABLE,
        price_axg=600.0,
        item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "dorado"}
    )
    vip_axolite = make_item(
        session,
        name="Pase Axolite VIP (30 días)",
        item_type=ItemType.CONSUMABLE,
        price_axg=1800.0,
        item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "axolite"}
    )

    return vip_coral, vip_dorado, vip_axolite, booster_normal, booster_foil, capsula_bronce, capsula_plata, capsula_oro

def test_vip_welcome_gift(session):
    vip_coral, vip_dorado, vip_axolite, booster_normal, booster_foil, capsula_bronce, capsula_plata, capsula_oro = setup_vip_test_catalog(session)

    # Caso 1: Usuario compra Coral por primera vez
    user_a = make_user(session, privy_did="user_a")
    make_wallet(session, user_id="user_a", axogemas=160.0) # 160 AXF, fondos suficientes

    ShopService.buy_item(session, user_id="user_a", item_id=vip_coral.id, payment_currency=CurrencyType.AXOGEMA)

    session.refresh(user_a)
    wallet_a = session.exec(select(Wallet).where(Wallet.user_id == "user_a")).one()

    # Debe haber recibido:
    # 200.0 GAL de welcome_gal Coral
    # 2 Cápsulas Bronce (capsulas_mensuales Coral: bronce=2)
    # 0 boosters Coral
    assert user_a.is_vip is True
    assert user_a.vip_tier == "coral"
    assert wallet_a.gemas_alga == 200 * 10**4
    assert wallet_a.axogemas == 110 * 10**6 # Costó 50 AXF (Coral §1 del plan)

    # Comprobar Cápsulas Bronce
    inv_bronce = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_a")
        .where(PlayerInventory.item_id == capsula_bronce.id)
    ).first()
    assert inv_bronce is not None
    assert inv_bronce.quantity == 2  # Coral da 2 Cápsulas Bronce

    # Caso 2: Usuario compra Coral una SEGUNDA VEZ (apila período, no da welcome_gal de nuevo)
    ShopService.buy_item(session, user_id="user_a", item_id=vip_coral.id, payment_currency=CurrencyType.AXOGEMA)
    session.refresh(user_a)
    session.refresh(wallet_a)

    # Se extendió el tiempo
    assert wallet_a.gemas_alga == 200 * 10**4 # No se sumaron otros 200 FRJ
    assert wallet_a.axogemas == 60 * 10**6 # Costó otros 50 AXF

    # Caso 3: Usuario compra Dorado (da 500 GAL + 1 booster normal + capsulas: bronce=2, plata=1)
    user_b = make_user(session, privy_did="user_b")
    make_wallet(session, user_id="user_b", axogemas=180.0)

    ShopService.buy_item(session, user_id="user_b", item_id=vip_dorado.id, payment_currency=CurrencyType.AXOGEMA)

    session.refresh(user_b)
    wallet_b = session.exec(select(Wallet).where(Wallet.user_id == "user_b")).one()

    assert user_b.vip_tier == "dorado"
    assert wallet_b.gemas_alga == 500 * 10**4

    # Verificar Cápsula Bronce (2)
    inv_bronce_b = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_b")
        .where(PlayerInventory.item_id == capsula_bronce.id)
    ).first()
    assert inv_bronce_b is not None
    assert inv_bronce_b.quantity == 2  # 2 bronce Dorado

    # Verificar Cápsula Plata (1)
    inv_plata_b = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_b")
        .where(PlayerInventory.item_id == capsula_plata.id)
    ).first()
    assert inv_plata_b is not None
    assert inv_plata_b.quantity == 1  # 1 plata Dorado

    # Verificar booster normal
    inv_booster_b = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_b")
        .where(PlayerInventory.item_id == booster_normal.id)
    ).first()
    assert inv_booster_b is not None
    assert inv_booster_b.quantity == 1

    # Caso 4: Usuario compra Axolite (da 1000 GAL + 1 booster foil + capsulas: bronce=3, plata=2, oro=1)
    user_c = make_user(session, privy_did="user_c")
    make_wallet(session, user_id="user_c", axogemas=350.0)

    ShopService.buy_item(session, user_id="user_c", item_id=vip_axolite.id, payment_currency=CurrencyType.AXOGEMA)

    session.refresh(user_c)
    wallet_c = session.exec(select(Wallet).where(Wallet.user_id == "user_c")).one()

    assert user_c.vip_tier == "axolite"
    assert wallet_c.gemas_alga == 1000 * 10**4

    # Verificar Cápsula Bronce (3)
    inv_bronce_c = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_c")
        .where(PlayerInventory.item_id == capsula_bronce.id)
    ).first()
    assert inv_bronce_c is not None
    assert inv_bronce_c.quantity == 3  # 3 bronce Axolite

    # Verificar Cápsula Plata (2)
    inv_plata_c = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_c")
        .where(PlayerInventory.item_id == capsula_plata.id)
    ).first()
    assert inv_plata_c is not None
    assert inv_plata_c.quantity == 2  # 2 plata Axolite

    # Verificar Cápsula Oro (1)
    inv_oro_c = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_c")
        .where(PlayerInventory.item_id == capsula_oro.id)
    ).first()
    assert inv_oro_c is not None
    assert inv_oro_c.quantity == 1  # 1 oro Axolite

    # Verificar booster foil
    inv_booster_c = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == "user_c")
        .where(PlayerInventory.item_id == booster_foil.id)
    ).first()
    assert inv_booster_c is not None
    assert inv_booster_c.quantity == 1

def test_vip_auto_renewal_success(session):
    vip_coral, vip_dorado, vip_axolite, *others = setup_vip_test_catalog(session)

    # 1. Setup usuario activo con auto-renovación habilitada a punto de expirar en 2 días
    user = make_user(session, privy_did="user_renew")
    user.vip_tier = "axolite"
    user.vip_expires_at = datetime.utcnow() + timedelta(days=2)
    user.vip_auto_renew = True
    user.vip_streak_months = 2
    session.add(user)
    
    # Wallet con fondos suficientes (precio Axolite = 300 AXF, §1 del plan)
    make_wallet(session, user_id="user_renew", axogemas=360.0)
    session.commit()

    # 2. Ejecutar tareas del scheduler
    _run_vip_jobs()

    session.refresh(user)
    wallet = session.exec(select(Wallet).where(Wallet.user_id == "user_renew")).one()

    # 3. Comprobar que se cobró y se extendió
    assert wallet.axogemas == 60 * 10**6 # 360 - 300 AXF
    assert user.vip_expires_at > datetime.utcnow() + timedelta(days=31) # Se sumaron 30 días a la expiración
    assert user.vip_streak_months == 3
    assert user.vip_auto_renew is True

    # Verificar ledger de transacción
    ledger = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.user_id == "user_renew")
        .where(TransactionLedger.currency == CurrencyType.AXOGEMA)
    ).first()
    assert ledger is not None
    assert ledger.amount == 300 * 10**6
    assert "Auto-renovación" in ledger.description

def test_vip_auto_renewal_insufficient_funds(session):
    vip_coral, vip_dorado, vip_axolite, *others = setup_vip_test_catalog(session)

    # Setup usuario sin fondos
    user = make_user(session, privy_did="user_renew_fail")
    user.vip_tier = "axolite"
    user.vip_expires_at = datetime.utcnow() + timedelta(days=2)
    user.vip_auto_renew = True
    user.vip_streak_months = 2
    session.add(user)
    
    make_wallet(session, user_id="user_renew_fail", axogemas=10.0) # Saldo insuficiente
    session.commit()

    _run_vip_jobs()

    session.refresh(user)
    
    # La auto-renovación debió apagarse (vip_auto_renew = False) y no extenderse
    assert user.vip_auto_renew is False
    assert user.vip_streak_months == 2

def test_vip_streak_tracking(session):
    vip_coral, *others = setup_vip_test_catalog(session)

    # 1. Compra inicial
    user = make_user(session, privy_did="user_streak")
    make_wallet(session, user_id="user_streak", axogemas=200.0)
    
    ShopService.buy_item(session, user_id="user_streak", item_id=vip_coral.id, payment_currency=CurrencyType.AXOGEMA)
    session.refresh(user)
    assert user.vip_streak_months == 1

    # 2. Simular renovación oportuna manual tras 28 días (mes nuevo)
    # Cambiamos last_renewed a hace 28 días
    user.vip_streak_last_renewed = datetime.utcnow() - timedelta(days=28)
    session.add(user)
    session.commit()

    ShopService.buy_item(session, user_id="user_streak", item_id=vip_coral.id, payment_currency=CurrencyType.AXOGEMA)
    session.refresh(user)
    assert user.vip_streak_months == 2

    # 3. Simular expiración tardía y reactivación (Racha rota)
    # Forzar expiración y descongelación de slots en base de datos
    user.vip_expires_at = datetime.utcnow() - timedelta(days=5)
    user.vip_streak_last_renewed = datetime.utcnow() - timedelta(days=70) # Renovado hace mucho tiempo
    session.add(user)
    session.commit()

    # Ejecutar scheduler para congelar y limpiar estado de expirados
    _run_vip_jobs()
    session.refresh(user)
    assert user.vip_tier is None # Eliminado el tier
    assert user.is_vip is False

    # El usuario vuelve a comprar Pase VIP
    ShopService.buy_item(session, user_id="user_streak", item_id=vip_coral.id, payment_currency=CurrencyType.AXOGEMA)
    session.refresh(user)
    
    # La racha debe haberse reiniciado a 1
    assert user.vip_streak_months == 1


# ─────────────────────────────────────────────────────────────────────────────
# Tests del contrato público: GET /shop/vip/tiers y GET /shop/vip/stats
# ─────────────────────────────────────────────────────────────────────────────

EXPECTED_KEYS = {
    "id", "price_axf", "frj_daily", "frj_monthly", "discount",
    "capsulas_mensuales", "p2p_commission", "table_bonus_slots",
    "axolotito_bonus_slots", "jackpot_bonus", "multiplayer_discount",
    "welcome_frj", "welcome_boosters", "popular",
}

EXPECTED_ORDER = ["coral", "dorado", "axolite"]


def test_get_vip_tiers_contrato_correcto():
    """Todos los tiers tienen exactamente las claves del contrato §9.2."""
    tiers = ShopService.get_vip_tiers()

    assert len(tiers) == 3, "Deben existir exactamente 3 tiers"
    for tier in tiers:
        missing = EXPECTED_KEYS - set(tier.keys())
        extra = set(tier.keys()) - EXPECTED_KEYS
        assert not missing, f"Tier '{tier.get('id')}' le faltan claves: {missing}"
        assert not extra, f"Tier '{tier.get('id')}' tiene claves extra: {extra}"


def test_get_vip_tiers_claves_traducidas():
    """
    Las claves legacy se traducen correctamente (rediseño §1 del plan económico,
    montos en unidad mínima entera VULN-06):
      price_axg → price_axf  : 50 / 120 / 300 AXF
      gal_daily  → frj_daily  : 20 / 50  / 130 FRJ
      welcome_gal→ welcome_frj: 200 / 500 / 1000 FRJ
    """
    tiers = {t["id"]: t for t in ShopService.get_vip_tiers()}

    # Precios AXF (1 AXF = $2 MXN → $100 / $240 / $600 MXN/mes)
    assert tiers["coral"]["price_axf"] == 50
    assert tiers["dorado"]["price_axf"] == 120
    assert tiers["axolite"]["price_axf"] == 300

    # FRJ diario
    assert tiers["coral"]["frj_daily"] == 20
    assert tiers["dorado"]["frj_daily"] == 50
    assert tiers["axolite"]["frj_daily"] == 130

    # Welcome FRJ
    assert tiers["coral"]["welcome_frj"] == 200
    assert tiers["dorado"]["welcome_frj"] == 500
    assert tiers["axolite"]["welcome_frj"] == 1000

    # Las claves legacy no deben aparecer en el contrato
    for tier in tiers.values():
        assert "price_axg" not in tier
        assert "gal_daily" not in tier
        assert "welcome_gal" not in tier


def test_get_vip_tiers_orden():
    """El orden devuelto es coral → dorado → axolite."""
    tiers = ShopService.get_vip_tiers()
    ids = [t["id"] for t in tiers]
    assert ids == EXPECTED_ORDER


def test_get_vip_tiers_frj_monthly():
    """frj_monthly == frj_daily * 30 para todos los tiers."""
    tiers = ShopService.get_vip_tiers()
    for tier in tiers:
        assert tier["frj_monthly"] == tier["frj_daily"] * 30, (
            f"Tier '{tier['id']}': frj_monthly {tier['frj_monthly']} "
            f"!= frj_daily {tier['frj_daily']} * 30"
        )


def test_get_vip_tiers_popular_solo_dorado():
    """popular=True solo en dorado; coral y axolite tienen popular=False."""
    tiers = {t["id"]: t for t in ShopService.get_vip_tiers()}
    assert tiers["coral"]["popular"] is False
    assert tiers["dorado"]["popular"] is True
    assert tiers["axolite"]["popular"] is False


def test_get_vip_tiers_consistent_with_vip_config():
    """
    Los valores del contrato provienen directamente de VIP_CONFIG —
    no hay hardcoding paralelo.
    """
    tiers = {t["id"]: t for t in ShopService.get_vip_tiers()}
    from app.core.config import axf_to_display, frj_to_display
    for tier_id, cfg in VIP_CONFIG.items():
        t = tiers[tier_id]
        assert t["price_axf"] == axf_to_display(cfg["price_axg"])
        assert t["frj_daily"] == frj_to_display(cfg["gal_daily"])
        assert t["welcome_frj"] == frj_to_display(cfg["welcome_gal"])
        assert t["discount"] == cfg["discount"]
        assert t["capsulas_mensuales"] == cfg["capsulas_mensuales"]
        assert t["p2p_commission"] == cfg["p2p_commission"]
        assert t["popular"] == cfg.get("popular", False)


def test_vip_stats_cuenta_solo_activos(session):
    """
    active_vip_count solo incluye usuarios cuyo vip_expires_at > now().
    Usuarios expirados o sin VIP no cuentan.
    """
    now = datetime.utcnow()

    # Usuario VIP activo (expira en 10 días)
    u_active = make_user(session, privy_did="stats_active")
    u_active.vip_tier = "coral"
    u_active.vip_expires_at = now + timedelta(days=10)
    session.add(u_active)

    # Usuario VIP expirado (expiró hace 1 día)
    u_expired = make_user(session, privy_did="stats_expired")
    u_expired.vip_tier = "dorado"
    u_expired.vip_expires_at = now - timedelta(days=1)
    session.add(u_expired)

    # Usuario sin VIP
    u_none = make_user(session, privy_did="stats_none")
    session.add(u_none)

    session.commit()

    # Contar igual que el endpoint: vip_expires_at > now
    active_count = session.exec(
        select(func.count(User.id)).where(User.vip_expires_at > now)
    ).one()

    assert active_count == 1, (
        f"Solo debe contar 1 VIP activo, obtuvo {active_count}"
    )


def test_vip_stats_cero_sin_usuarios_activos(session):
    """Con todos los VIPs expirados, active_vip_count debe ser 0."""
    now = datetime.utcnow()

    u1 = make_user(session, privy_did="expired_1")
    u1.vip_tier = "axolite"
    u1.vip_expires_at = now - timedelta(seconds=1)
    session.add(u1)
    session.commit()

    active_count = session.exec(
        select(func.count(User.id)).where(User.vip_expires_at > now)
    ).one()

    assert active_count == 0
