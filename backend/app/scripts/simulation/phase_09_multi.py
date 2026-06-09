import time

from sqlmodel import Session, select
from sqlalchemy import delete
from fastapi import HTTPException

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.lobby_models import GameRoom, RoomRegistration, JackpotVault, JackpotWin
from app.services.bank_service import BankService
from app.api.v1.endpoints.multiplayer import (
    register_axolotito, recall_axolotito,
    settle_axolotito_escrow, RegisterRequest,
)

from sim_types import _rng
from utils import _trigger_waiting_rooms, _read_new_logs


def phase_multiplayer(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    boards_by_user: dict = state["boards_by_user"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    wait_secs = config.multi_wait

    progress("  ⚔️  Simulando multijugador (con test de recall y espera real)...")

    # ── Construir lista de jugadores elegibles ─────────────────────────────────
    eligible: list[tuple] = []  # (player_dict, axo, [boards])
    for p in players:
        user_id = p["user_id"]
        axos = session.exec(
            select(Axolotito).where(
                Axolotito.user_id == user_id,
                Axolotito.status == "idle",
            )
        ).all()
        bids = boards_by_user.get(user_id, [])
        boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.id.in_(bids),
                PlayerBoard.is_dead == False,
            )
        ).all() if bids else []
        if axos and boards:
            eligible.append((p, axos[0], boards))

    if len(eligible) < 2:
        progress("  ⚠️  Pocos elegibles para multijugador (necesita al menos 2). Saltando.")
        return {}

    # ── TEST DE RECALL ────────────────────────────────────────────────────────
    recall_p, recall_axo, recall_boards = eligible[0]
    recall_user = recall_p["user_id"]

    wallet_r = BankService.get_or_create_wallet(session, recall_user)
    wallet_r.frijolitos = max(wallet_r.frijolitos, 500.0)
    session.add(wallet_r)
    recall_axo.energy_current = max(recall_axo.energy_current, 20)
    session.add(recall_axo)
    session.commit()

    recall_board_ids = [b.id for b in recall_boards[:2]]
    try:
        register_axolotito(
            req=RegisterRequest(
                axolotito_id=recall_axo.id,
                room_type="rookie",
                boards=recall_board_ids,
                budget_gal=200.0,
                loss_limit_pct=30.0,
                profit_limit_pct=50.0,
            ),
            session=session,
            verified_user_id=recall_user,
        )
        session.refresh(recall_axo)
        print(f"  📝 RECALL TEST: '{recall_axo.name}' inscrito (status={recall_axo.status})")

        recall_res = recall_axolotito(
            axolotito_id=recall_axo.id,
            session=session,
            verified_user_id=recall_user,
        )
        session.refresh(recall_axo)
        if recall_res.get("immediate"):
            print(f"  ✅ RECALL: '{recall_axo.name}' retirado en espera → status={recall_axo.status}")
            stats["recall_tests_passed"] = stats.get("recall_tests_passed", 0) + 1
            settle_axolotito_escrow(
                axolotito_id=recall_axo.id,
                session=session,
                verified_user_id=recall_user,
            )
            session.refresh(recall_axo)
            print(f"  💰 RECALL: fondos recuperados, status={recall_axo.status}")
        else:
            print(f"  ⚠️  RECALL no inmediato: {recall_res.get('mensaje')}")
    except HTTPException as e:
        errors.append(f"recall_test: {e.detail}")

    # ── REGISTRAR TODOS LOS JUGADORES ────────────────────────────────────────
    # registered: axo_id -> {user_id, budget, board_ids, room_type}
    registered: dict[int, dict] = {}

    for p, axo, boards in eligible:
        user_id = p["user_id"]
        personality = p["personality"]

        # Elegir sala según personalidad
        room_type = "champion" if personality.get("play_style") == "champion" else "rookie"
        fee = 50.0 if room_type == "champion" else 10.0

        # 1-3 tablas aleatorias
        n_boards = _rng.randint(1, min(3, len(boards)))
        chosen_boards = _rng.sample(boards, n_boards)
        chosen_ids = [b.id for b in chosen_boards]

        # Presupuesto para 4-8 rondas
        rounds_target = _rng.randint(4, 8)
        budget = round(fee * n_boards * rounds_target, 2)

        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.frijolitos < budget:
            wallet.frijolitos = budget + 200.0
            session.add(wallet)

        # Forzar idle + energía suficiente
        session.refresh(axo)
        if axo.status != "idle":
            axo.status = "idle"
            session.add(axo)
        if axo.energy_current < 10:
            axo.energy_current = axo.stat_stamina or 100
            session.add(axo)
        session.commit()

        loss_pct = _rng.choice([20.0, 30.0, 40.0])
        profit_pct = _rng.choice([40.0, 60.0, 80.0, 100.0])

        try:
            register_axolotito(
                req=RegisterRequest(
                    axolotito_id=axo.id,
                    room_type=room_type,
                    boards=chosen_ids,
                    budget_gal=budget,
                    loss_limit_pct=loss_pct,
                    profit_limit_pct=profit_pct,
                ),
                session=session,
                verified_user_id=user_id,
            )
            session.refresh(axo)
            room_reg = session.exec(
                select(RoomRegistration).where(RoomRegistration.axolotito_id == axo.id)
            ).first()
            if room_reg:
                registered[axo.id] = {
                    "user_id": user_id,
                    "budget": budget,
                    "board_ids": chosen_ids,
                    "room_type": room_type,
                    "room_id": room_reg.room_id,
                }
                print(f"  📋 '{axo.name}' [{personality['name']}] → sala {room_type} "
                      f"| {n_boards} tabla(s) | presupuesto {budget:.0f} GAL "
                      f"| SL={loss_pct:.0f}% TP={profit_pct:.0f}%")
        except HTTPException as e:
            errors.append(f"multi_register {user_id}: {e.detail}")

    if not registered:
        progress("  ⚠️  Ningún axolotito pudo registrarse. Saltando.")
        return {}

    # Acumular todos los resultados de todas las rondas
    all_match_logs: list[dict] = []

    # ── CICLO DE RONDAS ──────────────────────────────────────────────────────
    MAX_ROUNDS = 3
    for round_num in range(1, MAX_ROUNDS + 1):

        # Espera real simulando el lobby timer (30 s del scheduler)
        progress(f"  ⏳ Ronda {round_num}: esperando {wait_secs}s "
                 f"(como el scheduler en producción)...")
        for tick in range(wait_secs, 0, -1):
            time.sleep(1)
            if tick % 10 == 0 or tick <= 3:
                progress(f"    🕐 {tick}s...")

        # Disparar simulación de todas las salas en espera
        _trigger_waiting_rooms(session, stats, errors, round_num)

        # Leer y mostrar resultados de esta ronda
        print(f"\n  📊 Resultados ronda {round_num}:")
        _read_new_logs(session, registered, all_match_logs)

        # Liquidar los que terminaron (waiting_settlement)
        for axo_id, info in registered.items():
            axo = session.get(Axolotito, axo_id)
            if axo and axo.status == "waiting_settlement":
                try:
                    res = settle_axolotito_escrow(
                        axolotito_id=axo_id,
                        session=session,
                        verified_user_id=info["user_id"],
                    )
                    stats["multi_axos_settled"] = stats.get("multi_axos_settled", 0) + 1
                    print(f"  💵 '{axo.name}' liquidado → "
                          f"{res['refunded_gal']:.1f} GAL devueltos "
                          f"(neto: {res['net_performance']:+.1f} GAL)")
                except HTTPException as e:
                    errors.append(f"multi_settle {info['user_id']}: {e.detail}")

        # Revisar si queda alguien aún en juego (auto-re-inscrito)
        still_playing = [
            axo_id for axo_id in registered
            if (lambda a: a and a.status == "playing")(session.get(Axolotito, axo_id))
        ]
        if not still_playing:
            print(f"  🎉 Todos los axolotitos terminaron tras ronda {round_num}.")
            break
        if round_num < MAX_ROUNDS:
            print(f"  🔄 {len(still_playing)} axo(s) re-inscrito(s) automáticamente → ronda {round_num + 1}")

    # Recall + settle cualquier axo que siga en juego tras MAX_ROUNDS
    for axo_id, info in registered.items():
        axo = session.get(Axolotito, axo_id)
        if axo and axo.status == "playing":
            try:
                recall_axolotito(axolotito_id=axo_id, session=session, verified_user_id=info["user_id"])
                session.refresh(axo)
            except HTTPException:
                pass
            if axo.status == "waiting_settlement":
                try:
                    res = settle_axolotito_escrow(
                        axolotito_id=axo_id, session=session, verified_user_id=info["user_id"]
                    )
                    stats["multi_axos_settled"] = stats.get("multi_axos_settled", 0) + 1
                    print(f"  💵 '{axo.name}' (forzado) → {res['refunded_gal']:.1f} GAL")
                except HTTPException as e:
                    errors.append(f"multi_settle_forced {info['user_id']}: {e.detail}")

    # ── ESTADO DEL JACKPOT ───────────────────────────────────────────────────
    jackpot = session.exec(select(JackpotVault)).first()
    if jackpot:
        print(f"\n  💰 Jackpot actual: {jackpot.current_amount:.2f} GAL")
        recent_wins = session.exec(
            select(JackpotWin).order_by(JackpotWin.won_at.desc()).limit(5)
        ).all()
        if recent_wins:
            stats["multi_jackpot_won"] = stats.get("multi_jackpot_won", 0) + len(recent_wins)
            for jw in recent_wins:
                jp_axo = session.get(Axolotito, jw.axo_id)
                print(f"  🎰 JACKPOT: {jp_axo.name if jp_axo else '?'} "
                      f"ganó {jw.amount_won:.0f} GAL en turno #{jw.cards_drawn_count}")

    stats["multi_match_logs"] = all_match_logs

    victories = sum(1 for l in all_match_logs if l["outcome"] == "Victoria")
    total_net  = sum(l["net_gal"] for l in all_match_logs)

    progress(
        f"  ✅ Multi: {stats.get('multi_rooms_simulated', 0)} salas │ "
        f"{len(all_match_logs)} partidas │ "
        f"{victories} victorias │ "
        f"Neto total: {total_net:+.1f} GAL │ "
        f"{stats.get('recall_tests_passed', 0)} recall(s) pasaron │ "
        f"{stats.get('multi_axos_settled', 0)} liquidados."
    )
    return {}
