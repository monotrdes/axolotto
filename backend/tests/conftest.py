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
from app.models.manual_mode_event import ManualModeEvent  # noqa: F401
from app.models.board import PlayerBoard  # noqa: F401
from app.models.lobby_models import (  # noqa: F401
    GameRoom, RoomRegistration, TreasuryVault,
    JackpotVault, JackpotWin, MultiplayerGameLog,
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
    wallet = Wallet(user_id=user_id, axogemas=axogemas, gemas_alga=gemas_alga)
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
    item = ItemCatalog(
        name=name,
        item_type=item_type,
        price_axg=price_axg,
        price_gal=price_gal,
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
