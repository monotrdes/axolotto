"""
test_tutorial_service.py — Tests del servicio de tutorial de Axolotto.

Usa SQLite en memoria para velocidad. Cubre:
  - start_tutorial: fase 0 → 1
  - advance_phase: fases 1→2, 2→3, 3→4, 4→5
  - complete_tutorial: aplicación de karma + User.tutorial_completed
  - _evaluate_karma: lucky vs salty
  - _apply_karma_bonus: GAL para lucky, consumible/fallback para salty
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

# Hacer importables los módulos de app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Importar todos los modelos para que SQLModel.metadata los conozca
from app.models.user import User  # noqa: F401
from app.models.economy import (  # noqa: F401
    Wallet, TransactionLedger, TransactionType, CurrencyType,
    CryptoPurchaseOrder, ProcessedTransaction,
)
from app.models.items import (  # noqa: F401
    ItemCatalog, PlayerInventory, WebitoIncubation,
    CapsulaDailyFree, CapsulaPity, LegacyBacker,
    ItemType, Rarity,
)
from app.models.axolotito import Axolotito  # noqa: F401
from app.models.board import PlayerBoard  # noqa: F401
from app.models.promo import PromoCode, PendingReward  # noqa: F401

from app.services.tutorial_service import TutorialService, LUCKY_GAL_BONUS

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def engine():
    import app.database
    old_engine = app.database.engine

    _engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(_engine)

    # Patch the app database engine so BankService uses our test engine
    app.database.engine = _engine

    yield _engine
    _engine.dispose()
    app.database.engine = old_engine


@pytest.fixture
def session(engine):
    with Session(engine) as sess:
        yield sess
        sess.rollback()
    # Cleanup
    from sqlalchemy import text
    with engine.connect() as conn:
        from sqlalchemy import text as _text
        conn.execute(_text("PRAGMA foreign_keys = OFF;"))
        for table in reversed(SQLModel.metadata.sorted_tables):
            conn.execute(_text(f'DELETE FROM "{table.name}";'))
        conn.execute(_text("PRAGMA foreign_keys = ON;"))
        conn.commit()


def _make_user(session: Session, privy_did: str = "did:privy:tutorial_test") -> User:
    user = User(privy_did=privy_did, email="test@axolot.to")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_incubation(
    session: Session,
    user_id: str,
    tutorial_phase: int = 0,
    bonus_luck: float = 10.0,
    bonus_focus: float = 10.0,
    bonus_stamina: float = 10.0,
) -> WebitoIncubation:
    incubation = WebitoIncubation(
        user_id=user_id,
        item_id=1,
        fecha_eclosion_estimada=datetime.utcnow() + timedelta(hours=48),
        tutorial_phase=tutorial_phase,
        bonus_luck=bonus_luck,
        bonus_focus=bonus_focus,
        bonus_stamina=bonus_stamina,
    )
    session.add(incubation)
    session.commit()
    session.refresh(incubation)
    return incubation





# ---------------------------------------------------------------------------
# start_tutorial
# ---------------------------------------------------------------------------

class TestStartTutorial:
    def test_start_from_phase_0_sets_phase_1(self, session):
        user = _make_user(session, "did:privy:start_1")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=0)

        result = TutorialService.start_tutorial(session, user.privy_did, inc)

        assert result["phase"] == 1
        assert isinstance(result["dialogue"], str)
        assert len(result["dialogue"]) > 0
        assert isinstance(result["egg_intro_dialogue"], str)

        session.refresh(inc)
        assert inc.tutorial_phase == 1

    def test_start_again_raises_400(self, session):
        user = _make_user(session, "did:privy:start_2")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=1)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            TutorialService.start_tutorial(session, user.privy_did, inc)
        assert exc.value.status_code == 400

    def test_start_returns_egg_intro_dialogue(self, session):
        user = _make_user(session, "did:privy:start_3")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=0)
        result = TutorialService.start_tutorial(session, user.privy_did, inc)
        assert "Cenote" in result["egg_intro_dialogue"] or len(result["egg_intro_dialogue"]) > 10


# ---------------------------------------------------------------------------
# advance_phase
# ---------------------------------------------------------------------------

class TestAdvancePhase:
    def test_phase_not_started_raises_400(self, session):
        user = _make_user(session, "did:privy:adv_0")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=0)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            TutorialService.advance_phase(session, user.privy_did, inc)
        assert exc.value.status_code == 400

    def test_phase_1_to_2(self, session):
        user = _make_user(session, "did:privy:adv_1")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=1)

        result = TutorialService.advance_phase(session, user.privy_did, inc)

        assert result["phase"] == 2
        assert "mini_wins" in result
        assert "mini_total" in result
        assert isinstance(result["dialogue"], str)

        session.refresh(inc)
        assert inc.tutorial_phase == 2

    def test_phase_2_to_3(self, session):
        user = _make_user(session, "did:privy:adv_2")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=2)

        result = TutorialService.advance_phase(session, user.privy_did, inc)

        assert result["phase"] == 3
        assert "focus_moment_dialogue" in result
        assert "agility_moment_dialogue" in result
        assert isinstance(result["focus_moment_dialogue"], str)

        session.refresh(inc)
        assert inc.tutorial_phase == 3

    def test_phase_3_to_4_sets_karma(self, session):
        user = _make_user(session, "did:privy:adv_3")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=3)

        result = TutorialService.advance_phase(session, user.privy_did, inc)

        assert result["phase"] == 4
        assert result["karma"] in ("lucky", "salty")
        assert "karma_dialogue" in result
        assert isinstance(result["karma_dialogue"], str)

        session.refresh(inc)
        assert inc.tutorial_phase == 4
        assert inc.tutorial_karma in ("lucky", "salty")

    def test_phase_3_lucky_karma_when_high_bonus_luck(self, session):
        user = _make_user(session, "did:privy:adv_3_lucky")
        inc = _make_incubation(
            session, user.privy_did, tutorial_phase=3,
            bonus_luck=80.0, bonus_focus=5.0, bonus_stamina=5.0
        )
        result = TutorialService.advance_phase(session, user.privy_did, inc)
        # bonus_luck=80 > 60 → siempre lucky
        assert result["karma"] == "lucky"

    def test_phase_4_to_5_applies_bonus_gal(self, session):
        user = _make_user(session, "did:privy:adv_4_lucky")
        inc = _make_incubation(
            session, user.privy_did, tutorial_phase=4,
            bonus_luck=80.0
        )
        inc.tutorial_karma = "lucky"
        session.add(inc)
        session.commit()

        result = TutorialService.advance_phase(session, user.privy_did, inc)

        assert result["phase"] == 5
        assert result["karma"] == "lucky"
        assert result["karma_bonus"]["type"] == "frj"
        assert result["karma_bonus"]["amount"] == LUCKY_GAL_BONUS

        # Verificar wallet
        from app.services.bank_service import BankService
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.gemas_alga >= LUCKY_GAL_BONUS

    def test_phase_4_to_5_salty_gives_gal(self, session):
        user = _make_user(session, "did:privy:adv_4_salty")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=4)
        inc.tutorial_karma = "salty"
        session.add(inc)
        session.commit()

        result = TutorialService.advance_phase(session, user.privy_did, inc)

        assert result["karma"] == "salty"
        assert result["karma_bonus"]["type"] == "frj"
        assert result["karma_bonus"]["amount"] == 15.0

        # Verificar wallet
        from app.services.bank_service import BankService
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.frijolitos == 15.0

    def test_phase_already_completed_raises_400(self, session):
        user = _make_user(session, "did:privy:adv_done")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=5)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            TutorialService.advance_phase(session, user.privy_did, inc)
        assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# complete_tutorial
# ---------------------------------------------------------------------------

class TestCompleteTutorial:
    def test_complete_from_phase_4_marks_user_done(self, session):
        user = _make_user(session, "did:privy:complete_1")
        inc = _make_incubation(
            session, user.privy_did, tutorial_phase=4, bonus_luck=80.0
        )
        inc.tutorial_karma = "lucky"
        session.add(inc)
        session.commit()

        result = TutorialService.complete_tutorial(session, user.privy_did, inc)

        assert result["completed"] is True
        assert result["karma"] == "lucky"
        assert result["next_step"] == "hatch"
        assert isinstance(result["dialogue"], str)

        session.refresh(user)
        assert user.tutorial_completed is True

    def test_complete_from_phase_5_does_not_double_apply_bonus(self, session):
        user = _make_user(session, "did:privy:complete_2")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=5)
        inc.tutorial_karma = "salty"
        session.add(inc)
        session.commit()

        result = TutorialService.complete_tutorial(session, user.privy_did, inc)

        assert result["completed"] is True
        # bonus debe ser None porque ya estaba en phase 5
        assert result["bonus"] is None

    def test_complete_before_phase_4_raises_400(self, session):
        user = _make_user(session, "did:privy:complete_3")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=2)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            TutorialService.complete_tutorial(session, user.privy_did, inc)
        assert exc.value.status_code == 400

    def test_complete_tutorial_completed_flag_not_set_twice(self, session):
        """Llamar dos veces a complete no debe fallar aunque user.tutorial_completed ya sea True."""
        user = _make_user(session, "did:privy:complete_4")
        user.tutorial_completed = True
        session.add(user)
        session.commit()

        inc = _make_incubation(session, user.privy_did, tutorial_phase=5)
        inc.tutorial_karma = "salty"
        session.add(inc)
        session.commit()

        result = TutorialService.complete_tutorial(session, user.privy_did, inc)
        assert result["completed"] is True


# ---------------------------------------------------------------------------
# _evaluate_karma internamente
# ---------------------------------------------------------------------------

class TestEvaluateKarma:
    def test_lucky_when_bonus_luck_over_60(self, session):
        inc = _make_incubation(
            session, "did:privy:karma_eval_1", tutorial_phase=3, bonus_luck=65.0
        )
        karma = TutorialService._evaluate_karma(inc, phase_wins=1)
        assert karma == "lucky"

    def test_lucky_when_majority_wins(self, session):
        inc = _make_incubation(
            session, "did:privy:karma_eval_2", tutorial_phase=3, bonus_luck=5.0
        )
        # PHASE_ROUNDS=5, mayoría = >2.5 → 3+ wins
        karma = TutorialService._evaluate_karma(inc, phase_wins=4)
        assert karma == "lucky"

    def test_salty_as_default(self, session):
        inc = _make_incubation(
            session, "did:privy:karma_eval_3", tutorial_phase=3, bonus_luck=5.0
        )
        karma = TutorialService._evaluate_karma(inc, phase_wins=1)
        assert karma == "salty"

    def test_lucky_overrides_when_both_luck_and_wins(self, session):
        inc = _make_incubation(
            session, "did:privy:karma_eval_4", tutorial_phase=3, bonus_luck=80.0
        )
        karma = TutorialService._evaluate_karma(inc, phase_wins=5)
        assert karma == "lucky"


# ---------------------------------------------------------------------------
# _apply_karma_bonus — ledger entries
# ---------------------------------------------------------------------------

class TestApplyKarmaBonus:
    def test_lucky_bonus_writes_ledger(self, session):
        user = _make_user(session, "did:privy:bonus_lucky_1")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=4)

        TutorialService._apply_karma_bonus(session, user.privy_did, inc, "lucky")

        ledger_entries = session.exec(
            select(TransactionLedger)
            .where(TransactionLedger.user_id == user.privy_did)
            .where(TransactionLedger.tx_type == TransactionType.TUTORIAL_BONUS)
        ).all()
        assert len(ledger_entries) >= 1
        assert any(e.amount == LUCKY_GAL_BONUS for e in ledger_entries)

    def test_salty_bonus_gives_gal(self, session):
        user = _make_user(session, "did:privy:bonus_salty_gal")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=4)

        result = TutorialService._apply_karma_bonus(session, user.privy_did, inc, "salty")

        assert result["type"] == "frj"
        assert result["amount"] == 15.0


# ---------------------------------------------------------------------------
# TestTutorialLocks
# ---------------------------------------------------------------------------

class TestTutorialLocks:
    def test_complete_tutorial_sets_tutorial_flags(self, session):
        user = _make_user(session, "did:privy:locks_1")
        inc = _make_incubation(session, user.privy_did, tutorial_phase=4)
        inc.tutorial_karma = "lucky"
        inc.tutorial_board_card_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        session.add(inc)
        session.commit()

        result = TutorialService.complete_tutorial(session, user.privy_did, inc)
        assert result["completed"] is True

        # Verificar que el Axolotito creado tenga is_tutorial=True e is_main=True
        axo_db = session.exec(select(Axolotito).where(Axolotito.user_id == user.privy_did)).first()
        assert axo_db is not None
        assert axo_db.is_tutorial is True
        assert axo_db.is_main is True

        # Verificar que la Tabla Tutorial tenga is_tutorial=True
        board_db = session.exec(select(PlayerBoard).where(PlayerBoard.user_id == user.privy_did)).first()
        assert board_db is not None
        assert board_db.is_tutorial is True
        assert board_db.name == "Tabla Tutorial"
        assert axo_db.assigned_board_id == board_db.id

    def test_cannot_list_tutorial_axolotito_for_sale_or_rent(self, session):
        from app.api.v1.endpoints.user import list_axolotito_for_sale, list_axolotito_for_rent, ListAxoSaleRequest, ListAxoRentRequest
        from fastapi import HTTPException

        user = _make_user(session, "did:privy:locks_2")
        axo = Axolotito(
            user_id=user.privy_did,
            name="Axolotito Tutorial",
            is_tutorial=True,
            is_main=True,
            status="idle"
        )
        session.add(axo)
        session.commit()

        # Intento de venta
        with pytest.raises(HTTPException) as exc:
            list_axolotito_for_sale(
                axolotito_id=axo.id,
                payload=ListAxoSaleRequest(sale_price_gal=100.0),
                session=session,
                verified_user_id=user.privy_did
            )
        assert exc.value.status_code == 400
        assert "no se puede vender" in exc.value.detail

        # Intento de renta
        with pytest.raises(HTTPException) as exc:
            list_axolotito_for_rent(
                axolotito_id=axo.id,
                payload=ListAxoRentRequest(rent_fee_gal=10.0, rent_share_owner_pct=50),
                session=session,
                verified_user_id=user.privy_did
            )
        assert exc.value.status_code == 400
        assert "no se puede rentar" in exc.value.detail

    def test_cannot_list_or_delete_tutorial_board(self, session):
        from app.api.v1.endpoints.board import list_board_for_sale, list_board_for_rent, delete_board, ListSaleRequest, ListRentRequest
        from fastapi import HTTPException

        user = _make_user(session, "did:privy:locks_3")
        board = PlayerBoard(
            user_id=user.privy_did,
            name="Tabla Tutorial",
            card_ids=[1] * 16,
            card_first_editions=[False] * 16,
            is_tutorial=True
        )
        session.add(board)
        session.commit()

        # Intento de venta
        with pytest.raises(HTTPException) as exc:
            list_board_for_sale(
                board_id=board.id,
                payload=ListSaleRequest(sale_price_gal=150.0),
                session=session,
                verified_user_id=user.privy_did
            )
        assert exc.value.status_code == 400
        assert "no se puede vender" in exc.value.detail

        # Intento de renta
        with pytest.raises(HTTPException) as exc:
            list_board_for_rent(
                board_id=board.id,
                payload=ListRentRequest(rent_fee_gal=15.0, rent_share_owner_pct=40),
                session=session,
                verified_user_id=user.privy_did
            )
        assert exc.value.status_code == 400
        assert "no se puede rentar" in exc.value.detail

        # Intento de desarmar (delete)
        with pytest.raises(HTTPException) as exc:
            delete_board(
                board_id=board.id,
                session=session,
                verified_user_id=user.privy_did
            )
        assert exc.value.status_code == 400
        assert "no se puede desarmar" in exc.value.detail

