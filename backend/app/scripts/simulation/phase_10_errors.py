from sqlmodel import Session, select
from sqlalchemy import delete
from fastapi import HTTPException

from app.models.axolotito import Axolotito
from app.models.items import ItemCatalog
from app.models.lobby_models import RoomRegistration
from app.models.economy import CurrencyType
from app.services.bank_service import BankService
from app.services.shop_service import ShopService
from app.api.v1.endpoints.game import PlayRequest, FeedRequest
from app.services.game_service import GameService
from app.api.v1.endpoints.incubation import hatch_webito
from app.api.v1.endpoints.multiplayer import (
    register_axolotito, recall_axolotito, RegisterRequest,
)
from app.api.v1.endpoints.user import sync_user
from app.api.v1.endpoints.user import SyncUserRequest as SyncRequest

from utils import expect_error


def phase_error_tests(engine, config, **state) -> dict:
    """
    Intenta realizar acciones prohibidas para verificar que el backend las rechaza correctamente.
    Cada test DEBE lanzar HTTPException con el código esperado; si no lo hace, se reporta como FALLO.
    """
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    boards_by_user: dict = state["boards_by_user"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🚫 Ejecutando tests de rutas negativas...")

    user_a = players[0]["user_id"]
    user_b = players[1]["user_id"] if len(players) > 1 else players[0]["user_id"]

    axos_a = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_a)
    ).all()
    axos_b = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_b)
    ).all()

    counter = {"passed": 0, "failed": 0}

    # Test 1: Comprar item con saldo insuficiente → 400
    item = session.exec(
        select(ItemCatalog).where(ItemCatalog.is_active == True, ItemCatalog.price_axg > 0)
    ).first()
    if item:
        wallet = BankService.get_or_create_wallet(session, user_a)
        old_axg = wallet.axofichas
        wallet.axofichas = 0.01
        session.add(wallet)
        session.commit()
        expect_error(
            "compra_sin_saldo",
            400,
            lambda: ShopService.buy_item(session, user_a, item.id, CurrencyType.AXOGEMA),
            session=session,
            errors_log=errors,
            counter=counter,
        )
        wallet.axofichas = old_axg
        session.add(wallet)
        session.commit()

    # Test 2: Interactuar con axolotito de otro usuario → 403
    if axos_a and axos_b:
        axo_b = axos_b[0]
        expect_error(
            "axo_ajeno_feed",
            403,
            lambda: GameService.feed_axolotito(
                axo_id=axo_b.id,
                food_type="shrimp",
                session=session,
                verified_user_id=user_a,
            ),
            session=session,
            errors_log=errors,
            counter=counter,
        )

    # Test 3: Jugar sin energía → 400
    if axos_a:
        axo = axos_a[0]
        session.refresh(axo)
        old_energy = axo.energy_current
        old_status = axo.status
        axo.energy_current = 0
        axo.status = "idle"
        boards_ids = boards_by_user.get(user_a, [])
        if boards_ids:
            axo.assigned_board_id = boards_ids[0]
        session.add(axo)
        session.commit()
        expect_error(
            "jugar_sin_energia",
            400,
            lambda: GameService.play_match(
                axolotito_id=axo.id,
                room_name="rookie",
                multiplier=1,
                bot_enabled=False,
                bot_budget_gal=0,
                bot_loss_limit_pct=30.0,
                bot_profit_limit_pct=50.0,
                session=session,
                verified_user_id=user_a,
            ),
            session=session,
            errors_log=errors,
            counter=counter,
        )
        axo.energy_current = old_energy
        axo.status = old_status
        session.add(axo)
        session.commit()

    # Test 4: Inscribir axolotito ya inscrito → 400
    if axos_a and boards_by_user.get(user_a):
        axo = axos_a[0]
        session.refresh(axo)
        if axo.status == "idle":
            bids = boards_by_user[user_a][:1]
            wallet = BankService.get_or_create_wallet(session, user_a)
            wallet.frijolitos = max(wallet.frijolitos, 500)
            session.add(wallet)
            session.commit()
            try:
                register_axolotito(
                    req=RegisterRequest(
                        axolotito_id=axo.id,
                        room_type="rookie",
                        boards=bids,
                        budget_gal=100.0,
                        loss_limit_pct=30.0,
                        profit_limit_pct=50.0,
                    ),
                    session=session,
                    verified_user_id=user_a,
                )
            except HTTPException:
                pass

            session.refresh(axo)
            if axo.status == "playing":
                expect_error(
                    "inscripcion_doble",
                    400,
                    lambda: register_axolotito(
                        req=RegisterRequest(
                            axolotito_id=axo.id,
                            room_type="rookie",
                            boards=bids,
                            budget_gal=100.0,
                            loss_limit_pct=30.0,
                            profit_limit_pct=50.0,
                        ),
                        session=session,
                        verified_user_id=user_a,
                    ),
                    session=session,
                    errors_log=errors,
                    counter=counter,
                )
                # Limpiar
                axo.status = "idle"
                axo.escrow_balance_gal = 0.0
                session.add(axo)
                try:
                    session.exec(
                        delete(RoomRegistration).where(RoomRegistration.axolotito_id == axo.id)
                    )
                    session.commit()
                except Exception:
                    session.rollback()

    # Test 5: Eclosionar huevo inexistente → 404
    expect_error(
        "hatch_inexistente",
        404,
        lambda: hatch_webito(
            incubation_id=999999,
            session=session,
            verified_user_id=user_a,
        ),
        session=session,
        errors_log=errors,
        counter=counter,
    )

    # Test 6: Cambiar wallet por una ya registrada → 409
    if len(players) >= 2:
        wallet_b = players[1]["wallet_addr"]
        expect_error(
            "wallet_duplicada",
            409,
            lambda: sync_user(
                req=SyncRequest(
                    privy_did=user_a,
                    wallet_address=wallet_b,
                    email=None,
                ),
                session=session,
                verified_user_id=user_a,
            ),
            session=session,
            errors_log=errors,
            counter=counter,
        )

    # Test 7: Recall de axolotito que no está en sala → 400
    if axos_a:
        axo = axos_a[0]
        session.refresh(axo)
        if axo.status == "idle":
            expect_error(
                "recall_sin_sala",
                400,
                lambda: recall_axolotito(
                    axolotito_id=axo.id,
                    session=session,
                    verified_user_id=user_a,
                ),
                session=session,
                errors_log=errors,
                counter=counter,
            )

    stats["error_tests_passed"] = counter["passed"]
    stats["error_tests_failed"] = counter["failed"]
    progress(f"  ✅ Tests de errores: {counter['passed']} pasaron, {counter['failed']} fallaron.")
    return {}
