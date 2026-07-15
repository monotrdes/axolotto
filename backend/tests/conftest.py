from __future__ import annotations
"""
conftest.py — Fixtures compartidos para todos los tests de Axolotto.

Usa PostgreSQL de prueba (axolotto_test) para soportar SELECT FOR UPDATE.
Cada test corre en su propia sesión; al terminar se hace TRUNCATE CASCADE
sobre todas las tablas para dejar la BD limpia.
"""
import os
import sys
import pytest
from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

# The existing suite exercises the legacy value-bearing economy deliberately.
# Production/default settings remain fail-closed; tests must opt in explicitly.
os.environ.setdefault("PRODUCT_MODE", "legacy_simulation")
os.environ.setdefault("ENABLE_FIAT_PAYMENTS", "true")
os.environ.setdefault("ENABLE_CRYPTO_CHECKOUT", "true")
os.environ.setdefault("ENABLE_PLAYER_MARKETPLACE", "true")
os.environ.setdefault("ENABLE_CREATOR_PAYOUTS", "false")
os.environ.setdefault("ENABLE_VIP_SALES", "true")
os.environ.setdefault("ENABLE_FREE_GAMEPLAY", "true")
os.environ.setdefault("ENABLE_PAID_GAMEPLAY", "true")
os.environ.setdefault("ENABLE_GAMEPLAY_TOKEN_REWARDS", "true")
os.environ.setdefault("ENABLE_JACKPOT", "true")
os.environ.setdefault("ENABLE_PURCHASED_RANDOM_REWARDS", "true")
os.environ.setdefault("ENABLE_PLAYER_TOKEN_TRANSFERS", "true")
os.environ.setdefault("ENABLE_CLIENT_REPORTED_REWARDS", "true")
os.environ.setdefault("ENABLE_PROMOTIONAL_TOKEN_REWARDS", "true")
os.environ.setdefault("ENABLE_ADMIN_TOKEN_MINTS", "true")
os.environ.setdefault("ENABLE_ADMIN_BALANCE_ADJUSTMENTS", "true")
os.environ.setdefault("ENABLE_PASSIVE_TOKEN_REWARDS", "true")
os.environ.setdefault("ENABLE_LEGACY_ASSET_CLAIMS", "true")
os.environ.setdefault("ENABLE_FIXED_ITEM_SHOP", "true")
os.environ.setdefault("ENABLE_FIXED_GAMEPLAY_SPENDING", "true")
os.environ.setdefault("ENABLE_CARD_CRAFTING", "true")
os.environ.setdefault("ENABLE_BOARD_ASSET_MUTATIONS", "true")
os.environ.setdefault("ENABLE_HATCHING", "true")
os.environ.setdefault("ENABLE_RECICLON", "true")
os.environ.setdefault("ALLOW_DEV_PAYMENTS", "true")

# Asegurar que los módulos de app sean importables desde tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Importar TODOS los modelos para que se registren en SQLModel.metadata
# antes de llamar a create_all.
from app.models.user import User  # noqa: F401
from app.models.economy import (  # noqa: F401
    Wallet, TransactionLedger, CryptoPurchaseOrder, ProcessedTransaction, CryptoPaymentAttempt,
)
from app.models.items import (  # noqa: F401
    ItemCatalog, PlayerInventory, WebitoIncubation,
    CapsulaDailyFree, CapsulaPity, LegacyBacker,
)
from app.models.axolotito import Axolotito  # noqa: F401
from app.models.market_escrow import (  # noqa: F401
    EscrowListing, FiatPaymentIntent, EarnedBalanceLock,
)
from app.models.manual_mode_event import ManualModeEvent  # noqa: F401
from app.models.board import PlayerBoard  # noqa: F401
from app.models.lobby_models import (  # noqa: F401
    GameRoom, RoomRegistration, TreasuryVault,
    JackpotVault, JackpotWin, MultiplayerGameLog,
)
from app.models.social import (  # noqa: F401
    FriendRelation, FriendStatus, SocialActionLog, SocialActionType,
    ReferralCode, ReferralTracking, ReferralStatus,
)
from app.models.economy import CurrencyType
from app.models.items import ItemType, Rarity

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")

# ---------------------------------------------------------------------------
# Engine — session-scoped: se crea una sola vez y se destruye al final.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine():
    if TEST_DB_URL == "sqlite://" or "sqlite" in TEST_DB_URL:
        from sqlalchemy.pool import StaticPool
        _engine = create_engine(
            TEST_DB_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(TEST_DB_URL)
        
    SQLModel.metadata.create_all(_engine)
    
    # Sobrescribir el engine global de la aplicación para que apunte al de pruebas
    import app.database
    app.database.engine = _engine
    
    # También parchear en módulos que importan 'engine' directamente
    try:
        import app.services.multiplayer_service
        app.services.multiplayer_service.engine = _engine
    except ImportError:
        pass
    try:
        import app.services.vip_scheduler
        app.services.vip_scheduler.engine = _engine
    except ImportError:
        pass
    
    yield _engine
    _engine.dispose()


# ---------------------------------------------------------------------------
# Session — function-scoped: una sesión nueva por test, limpieza post-test.
# ---------------------------------------------------------------------------

@pytest.fixture
def session(engine):
    with Session(engine) as sess:
        yield sess
        # Rollback de cualquier cosa no commiteada antes de cerrar la sesión.
        sess.rollback()

    # Limpieza: TRUNCATE en PostgreSQL o DELETE en SQLite
    if "sqlite" in str(engine.url):
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            for table in reversed(SQLModel.metadata.sorted_tables):
                conn.execute(text(f'DELETE FROM "{table.name}";'))
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            conn.commit()
    else:
        with engine.connect() as conn:
            table_names = ", ".join(
                f'"{t.name}"' for t in SQLModel.metadata.sorted_tables
            )
            conn.execute(
                text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
            )
            conn.commit()


# ---------------------------------------------------------------------------
# Helpers de construcción de datos de prueba
# ---------------------------------------------------------------------------

def make_user(
    session: Session,
    privy_did: str = "did:privy:test_user",
    wallet_address: str | None = "GENERATE_UNIQUE",
    is_vip: bool = False,
    vip_tier: str | None = None,
    tutorial_completed: bool = True,
) -> User:
    from datetime import datetime, timedelta
    import uuid

    if wallet_address == "GENERATE_UNIQUE":
        wallet_address = f"0x{uuid.uuid4().hex.zfill(40)}"

    vip_expires_at = None
    if is_vip and vip_tier:
        vip_expires_at = datetime.utcnow() + timedelta(days=30)

    user = User(
        privy_did=privy_did,
        wallet_address=wallet_address,
        vip_tier=vip_tier if is_vip else None,
        vip_expires_at=vip_expires_at,
        tutorial_completed=tutorial_completed,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def make_wallet(
    session: Session,
    user_id: str,
    axogemas: float = 0.0,
    gemas_alga: float = 0.0,
) -> Wallet:
    from app.core.config import axf_to_internal, frj_to_internal
    axf_int = axf_to_internal(axogemas)
    frj_int = frj_to_internal(gemas_alga)
    wallet = Wallet(user_id=user_id, axofichas=axf_int, frijolitos=frj_int)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return wallet


def make_item(
    session: Session,
    name: str,
    item_type: ItemType,
    price_axg: float | None = None,
    price_gal: float | None = None,
    is_active: bool = True,
    max_supply: int | None = None,
    item_metadata: dict | None = None,
    rarity: Rarity = Rarity.COMMON,
) -> ItemCatalog:
    from app.core.config import axf_to_internal, frj_to_internal
    axf_int = axf_to_internal(price_axg) if price_axg is not None else None
    frj_int = frj_to_internal(price_gal) if price_gal is not None else None
    item = ItemCatalog(
        name=name,
        item_type=item_type,
        price_axg=axf_int,
        price_gal=frj_int,
        is_active=is_active,
        max_supply=max_supply,
        item_metadata=item_metadata or {},
        rarity=rarity,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def make_card_pool(session: Session, count: int = 10) -> list[ItemCatalog]:
    """Crea N cartas en el catálogo para que el booster tenga de dónde elegir."""
    cards = []
    for i in range(count):
        card = make_item(
            session,
            name=f"Carta Test {i + 1}",
            item_type=ItemType.CARD,
            rarity=Rarity.COMMON,
        )
        cards.append(card)
    return cards
