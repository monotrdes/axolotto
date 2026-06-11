#!/usr/bin/env python3
"""
chaos_runner.py — Chaos & Security Simulator v2 entrypoint.

Orchestrates: setup (reuse existing phases) → concurrent bots + attack agents →
validation tests → security audit report.

Supports up to 500 concurrent players as a PostgreSQL stress test.

Usage:
    cd D:\\Axolotto_2026\\axolotto
    python backend/app/scripts/simulation_chaos/chaos_runner.py
    python backend/app/scripts/simulation_chaos/chaos_runner.py --total-players 100 --duration 120
"""
import sys
import os
import argparse
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait as fut_wait
from datetime import datetime, timezone

# ── Path setup ────────────────────────────────────────────────────────────────
# chaos_runner.py is at: backend/app/scripts/simulation_chaos/chaos_runner.py
_this_file = os.path.abspath(__file__)
_sim_chaos_dir = os.path.dirname(_this_file)          # .../scripts/simulation_chaos/
_scripts_dir = os.path.dirname(_sim_chaos_dir)         # .../scripts/
_sim_dir = os.path.join(_scripts_dir, "simulation")    # .../scripts/simulation/
_app_dir = os.path.dirname(_scripts_dir)               # .../app/
backend_dir = os.path.dirname(_app_dir)                # .../backend/

sys.path.insert(0, backend_dir)
sys.path.insert(0, _sim_chaos_dir)   # chaos modules
sys.path.insert(0, _sim_dir)         # original simulation phases

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# ── Override DB pool for high concurrency BEFORE importing app.database ──────
# 100+ concurrent bots need a large connection pool
os.environ.setdefault("SQLALCHEMY_POOL_SIZE", "120")
os.environ.setdefault("SQLALCHEMY_MAX_OVERFLOW", "50")

# ── Early arg parsing: --db-url must be set BEFORE app.database is imported ──
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--db-url", default=None)
_pre_args, _ = _pre.parse_known_args()
if _pre_args.db_url:
    os.environ["DATABASE_URL"] = _pre_args.db_url
elif not os.path.exists("/.dockerenv"):
    # Remap Docker hostnames for host-machine execution
    if "DATABASE_URL" in os.environ:
        _dbu = os.environ["DATABASE_URL"]
        if "@db_axolotto:5432" in _dbu:
            os.environ["DATABASE_URL"] = _dbu.replace("@db_axolotto:5432", "@127.0.0.1:5433")
    for _key in ("WEB3_PROVIDER_URL", "ANVIL_RPC_URL", "RPC_URL"):
        if _key in os.environ and "anvil_axolotto" in os.environ[_key]:
            os.environ[_key] = os.environ[_key].replace("anvil_axolotto", "127.0.0.1")

# ── Import app modules (after env is set) ─────────────────────────────────────
from sqlmodel import Session, create_engine as _create_engine
from app.core.config import settings
from sim_types import SimConfig, _rng, PERSONALITY_POOL
from chaos_types import ChaosConfig, CHAOS_PERSONALITY_MAP, build_personality_list
from runtime_state import (
    init_db_semaphore, reset_all_state,
    record_incident, get_incidents,
    increment_counter, get_counters,
    increment_stat, get_stats,
)
from chaos_report import generate_chaos_report, save_chaos_report, generate_setup_summary


# ═══════════════════════════════════════════════════════════════════════════════
# Web3 Mock installation (duplicated from runner.py for isolation)
# ═══════════════════════════════════════════════════════════════════════════════

def _install_web3_mocks():
    """Patch all Web3Service on-chain methods to return fake tx hashes.

    Duplicated from runner.py lines 138-171. When the chaos simulator becomes
    the primary simulator, this will be extracted to a shared utility.
    """
    from app.services import web3_service as _w3mod
    _mock_counter = [0]  # list for mutable closure

    def _mock_tx(*a, **kw):
        _mock_counter[0] += 1
        return f"0x_chaos_mock_{_mock_counter[0]:06d}"

    _w3mod.Web3Service.mint_webito_onchain       = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_axolotito_onchain    = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_axolotito_with_stats = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_sobrecito_onchain    = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.burn_sobrecito_onchain    = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.transferir_sobrecito_onchain = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.burn_axofichas            = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.transferir_axofichas      = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.burn_frj                  = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_frj                  = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_cards_onchain        = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.transfer_card_onchain     = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.create_board_onchain      = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.dissolve_board_onchain    = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.dissolve_board_safe_onchain = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.transfer_board_onchain    = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.transfer_axolotito_onchain = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.update_table_stats_onchain = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.burn_consumable           = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.mint_consumable           = staticmethod(lambda *a, **kw: _mock_tx())
    _w3mod.Web3Service.create_npc_board          = staticmethod(lambda *a, **kw: _rng.randint(1000, 9999))
    settings.IS_MOCK_WEB3 = True


# ═══════════════════════════════════════════════════════════════════════════════
# Main Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_admin_users_ok(session, progress) -> None:
    """Después del reset, asegura que los admin users tengan sus campos básicos
    restaurados (cave, slots). El tutorial_completed NO se toca aquí — el flujo
    de incubación/tutorial se encargará de ponerlo a True cuando corresponda."""
    admin_dids = getattr(settings, 'admin_dids', [])
    if not admin_dids:
        return

    from sqlmodel import select as _sel
    from app.models.user import User
    try:
        for admin_did in admin_dids:
            user = session.exec(
                _sel(User).where(User.privy_did == admin_did)
            ).first()
            if not user:
                continue

            fixed = []
            # NOTA: NO tocamos tutorial_completed — el tutorial lo pondrá a True
            if not user.cave_level or user.cave_level < 1:
                user.cave_level = 1
                fixed.append("cave_level")
            if not user.unlocked_board_slots or user.unlocked_board_slots < 3:
                user.unlocked_board_slots = 3
                fixed.append("unlocked_board_slots")
            if user.webito_slots_unlocked is None or user.webito_slots_unlocked < 1:
                user.webito_slots_unlocked = 1
                fixed.append("webito_slots_unlocked")

            if fixed:
                session.add(user)
                session.commit()
                progress(f"  🛡️  Admin {admin_did[-20:]}: {', '.join(fixed)} restaurados post-reset")
    except Exception as e:
        session.rollback()
        progress(f"  ⚠️  _ensure_admin_users_ok falló: {e}")


# Removed _verify_all_players_have_axolotitos to allow bots to complete tutorial naturally


def run_chaos_simulation(config: ChaosConfig):
    """Main orchestrator: setup → concurrent bots+agents → validation → report."""
    t_start = time.monotonic()

    # ── Suppress noisy logs ──────────────────────────────────────────────────
    import warnings
    import logging
    warnings.filterwarnings("ignore")
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    # ── Install Web3 mocks ───────────────────────────────────────────────────
    _install_web3_mocks()

    # ── Override engine with large pool ─────────────────────────────────────
    from app import database as _dbmod
    pool_size = int(os.environ.get("SQLALCHEMY_POOL_SIZE", "120"))
    max_overflow = int(os.environ.get("SQLALCHEMY_MAX_OVERFLOW", "50"))
    _chaos_engine = _create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,       # Verify connections before use
        pool_recycle=300,         # Recycle connections every 5 min
    )
    _dbmod.engine = _chaos_engine
    engine = _chaos_engine

    # Also patch the engine reference in bot_actions module
    import bot_actions as _ba
    _ba.engine = _chaos_engine

    # Also patch the engine reference in chaos_agents module
    import chaos_agents as _ca
    _ca.engine = _chaos_engine

    engine.echo = False

    # ── Initialize DB semaphore ──────────────────────────────────────────────
    # Allow up to (pool_size - 20) concurrent sessions to leave headroom
    init_db_semaphore(max(pool_size - 20, 10))
    reset_all_state()

    print(f"🔧 Engine pool: size={pool_size}, overflow={max_overflow}")
    print(f"🔒 DB semaphore: {max(pool_size - 20, 10)} concurrent sessions")

    # ── Phase 1: Sequential Setup (reuse existing phases) ────────────────────
    print("\n" + "=" * 70)
    print("⚡  CHAOS & SECURITY SIMULATOR V2")
    print("=" * 70)
    print(f"👥 Total bots: {config.total_bots}  |  ⏱️  Duración: {config.duration_seconds}s")
    print(f"   🐋 Whales: {config.whale_count}  |  📦 Collectors: {config.collector_count}  |  🆓 Free2Play: {config.free2play_count}")
    print("=" * 70)

    progress = lambda msg: print(msg, flush=True)

    progress("⏳ [SETUP] Importando fases del simulador original...")

    # Import all setup phases from the original simulation
    from phase_00_reset import phase_reset, phase_migrations
    from phase_01_users import phase_create_users
    from phase_01b_corcholata import phase_redeem_corcholata
    from phase_01c_daily_rewards import phase_daily_rewards
    from phase_02_wallets import phase_fund_wallets
    from phase_02b_tickets import phase_seed_tickets
    from phase_03_boosters import phase_buy_boosters, phase_open_boosters
    from phase_04_incubation import phase_incubation
    from phase_05_gashapon import phase_gashapon
    from phase_06_boards import phase_boards
    from phase_06c_crafting import phase_card_melter
    from phase_06d_deconstruct import phase_board_deconstruction
    from phase_06e_market import phase_p2p_market
    from phase_07_vip import phase_vip
    from phase_07e_cave_expansion import phase_cave_expansion
    from phase_07f_cave_decor import phase_cave_decor
    from phase_09e_social import phase_social_simulation

    # Build a SimConfig for the setup phases — use minimal times for speed
    player_count = config.total_bots
    sim_cfg = SimConfig(
        players=player_count,
        incubation=2,         # minimal incubation for 100 players
        games=1,              # minimal games
        multi_wait=3,         # minimal multiplayer wait
        skip_reset=config.skip_reset,
        db_url=config.db_url,
        skip_imprinting=True, # skip imprinting for speed
        create_test_event=False,
    )

    state: dict = {}

    with Session(engine) as session:
        state = {
            "session": session,
            "progress": progress,
            "live_progress": lambda m: print(m, flush=True),
            "stats": {},
            "errors": [],
        }

        try:
            # Phase 0: Migrations
            progress("⏳ [SETUP/0] Migraciones...")
            state.update(phase_migrations(engine, sim_cfg, **state) or {})

            # Phase 0b: Reset
            if not config.skip_reset:
                progress("⏳ [SETUP/1] Reset de base de datos...")
                state.update(phase_reset(engine, sim_cfg, **state) or {})

            # Phase 1: Users
            progress(f"⏳ [SETUP/2] Creando {player_count} usuarios...")
            state.update(phase_create_users(engine, sim_cfg, **state) or {})

            # ── Asegurar que los admin users sobrevivan el reset ──────────────
            # Después del reset, TODOS los usuarios tienen tutorial_completed=FALSE.
            # phase_01_users solo restaura el PRO_USER_DID hardcodeado, pero el admin
            # real (con su Privy DID de producción) queda en estado tutorial.
            # Corregimos todos los admin DIDs configurados AHORA, antes del tutorial.
            _ensure_admin_users_ok(session, progress)

            # Assign chaos personalities to players
            players = state.get("players", [])
            chaos_personalities = build_personality_list(
                config.whale_count, config.collector_count, config.free2play_count
            )
            for i, p in enumerate(players):
                if i < len(chaos_personalities):
                    p["chaos_personality"] = chaos_personalities[i]

            # ── Incluir admin users como jugadores completos ──────────────────
            # El admin DEBE participar en TODO el flujo: corcholata, tutorial,
            # wallet, VIP, boosters, y fase concurrente.  No basta con solo
            # arreglar tutorial_completed — necesitan ser parte de 'players'.
            from sqlmodel import select as _sel2
            admin_dids = getattr(settings, 'admin_dids', [])
            for admin_did in admin_dids:
                if admin_did in [p["user_id"] for p in players]:
                    continue  # ya fue creado por phase_01_users (ej. PRO_USER_DID)
                admin_user = session.exec(
                    _sel2(User).where(User.privy_did == admin_did)
                ).first()
                if admin_user:
                    players.append({
                        "user_id": admin_did,
                        "wallet_addr": admin_user.wallet_address or "0x" + "0" * 40,
                        "personality": PERSONALITY_POOL[1],  # whale
                        "chaos_personality": dict(CHAOS_PERSONALITY_MAP["whale"]),
                    })
                    progress(f"  🛡️  Admin {admin_did[-20:]}: incluido como jugador completo (whale)")
            # ──────────────────────────────────────────────────────────────────

            # Phase 2-X: Economy setup — Tutorial FIRST, then VIP, then the rest
            progress("⏳ [SETUP/3] Corcholatas + Daily Rewards (fondos iniciales)...")
            state.update(phase_redeem_corcholata(engine, sim_cfg, **state) or {})
            state.update(phase_daily_rewards(engine, sim_cfg, **state) or {})

            progress(f"⏳ [SETUP/4] 🎓 TUTORIAL + Incubación ({sim_cfg.incubation}s)...")
            state.update(phase_incubation(engine, sim_cfg, **state) or {})

            progress("⏳ [SETUP/5] 💰 Fondos + Tickets...")
            state.update(phase_fund_wallets(engine, sim_cfg, **state) or {})
            state.update(phase_seed_tickets(engine, sim_cfg, **state) or {})

            progress("⏳ [SETUP/6] 👑 VIP Club (activación, descuento para compras)...")
            state.update(phase_vip(engine, sim_cfg, **state) or {})

            progress("⏳ [SETUP/7] 🃏 Boosters (compra con descuento VIP)...")
            state.update(phase_buy_boosters(engine, sim_cfg, **state) or {})
            # Open all boosters now (tutorial is done)
            state.update(phase_open_boosters(engine, sim_cfg, strategy="immediate", **state) or {})
            state.update(phase_open_boosters(engine, sim_cfg, strategy="selective", **state) or {})
            state.update(phase_open_boosters(engine, sim_cfg, strategy="final", **state) or {})

            progress("⏳ [SETUP/8] 🎰 Gashapon...")
            state.update(phase_gashapon(engine, sim_cfg, **state) or {})

            progress("⏳ [SETUP/9] 📋 Tableros + Mercado...")
            state.update(phase_boards(engine, sim_cfg, **state) or {})
            state.update(phase_card_melter(engine, sim_cfg, **state) or {})
            state.update(phase_board_deconstruction(engine, sim_cfg, **state) or {})
            state.update(phase_p2p_market(engine, sim_cfg, **state) or {})

            progress("⏳ [SETUP/10] 🏠 Cueva + Social...")
            state.update(phase_cave_expansion(engine, sim_cfg, **state) or {})
            state.update(phase_cave_decor(engine, sim_cfg, **state) or {})
            state.update(phase_social_simulation(engine, sim_cfg, **state) or {})

            progress("✅ [SETUP] Completado.\n")
            setup_summary = generate_setup_summary(state.get("stats", {}))
            progress(setup_summary)

        except Exception as e:
            progress(f"❌ [SETUP] Error: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()

    # ── Phase 2: Concurrent Chaos ────────────────────────────────────────────
    progress("=" * 70)
    progress("⚡ [CONCURRENT] Iniciando fase caótica...")
    attack_agent_count = sum(1 for v in [
        config.enable_replay_attack, config.enable_id_spoofing,
        config.enable_race_condition, config.enable_double_booking,
        config.enable_boundary_injection, config.enable_cooldown_bypass,
    ] if v)
    progress(f"   {len(players)} bots + {attack_agent_count} chaos agents en paralelo")
    progress("=" * 70)

    stop_event = threading.Event()

    # ── Activity writer daemon thread ────────────────────────────────────────
    ACTIVITIES_PATH = os.environ.get(
        "CHAOS_ACTIVITIES_PATH",
        os.path.join(backend_dir, "chaos_activities.json"),
    )

    def _activity_writer():
        """Write live activities to JSON every 1.5s for the visual dashboard."""
        from runtime_state import get_live_activities, get_counters, get_stats
        writes = 0
        while not stop_event.is_set():
            try:
                data = {
                    "activities": get_live_activities(),
                    "counters": get_counters(),
                    "stats": get_stats(),
                }
                with open(ACTIVITIES_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, default=str)
                writes += 1
                if writes == 1:
                    progress(f"   📡 Activity writer activo ({len(data['activities'])} actividades iniciales)")
            except Exception as e:
                if writes == 0:
                    progress(f"   ⚠️  Activity writer error: {e}")
            stop_event.wait(1.5)
        progress(f"   📡 Activity writer terminado ({writes} writes)")

    activity_thread = threading.Thread(target=_activity_writer, daemon=True)
    activity_thread.start()
    progress(f"   📡 Activity writer → {ACTIVITIES_PATH}")

    # Collect player data for bot threads
    from sqlmodel import select as _sel
    from app.models.axolotito import Axolotito as _Axo
    from app.models.board import PlayerBoard as _PB

    player_data_list = []
    with Session(engine) as session:
        for p in players:
            uid = p["user_id"]
            axo_ids = list(session.exec(
                _sel(_Axo.id).where(_Axo.user_id == uid)
            ).all())
            board_ids = list(session.exec(
                _sel(_PB.id).where(_PB.user_id == uid, _PB.is_dead == False)
            ).all())
            player_data_list.append({
                "user_id": uid,
                "chaos_personality": p.get("chaos_personality", chaos_personalities[0]),
                "axolotito_ids": axo_ids,
                "board_ids": board_ids,
            })

    all_user_ids = [p["user_id"] for p in players]
    all_axo_ids = [axo for pd in player_data_list for axo in pd["axolotito_ids"]]

    # Removed forced tutorial bypass pre-flight check to let bots play tutorial live

    # Spawn all bot threads and chaos agents
    from bot_state_machine import PlayerBot

    total_workers = min(len(player_data_list) + 6, 150)
    progress(f"   ThreadPoolExecutor: max_workers={total_workers}")

    with ThreadPoolExecutor(max_workers=total_workers) as executor:
        # Submit all bots
        bot_futures = []
        for i, pd in enumerate(player_data_list):
            pname = pd["chaos_personality"]["name"]
            bot = PlayerBot(
                thread_id=f"{pname}_{i:03d}",
                user_id=pd["user_id"],
                personality=pd["chaos_personality"],
                duration_seconds=config.duration_seconds,
                stop_event=stop_event,
            )
            fut = executor.submit(bot.run)
            bot_futures.append(fut)

        progress(f"   ✅ {len(bot_futures)} bots lanzados")

        # Submit chaos agents
        chaos_futures = []
        if config.enable_replay_attack:
            from chaos_agents import chaos_replay_attack
            chaos_futures.append(executor.submit(
                chaos_replay_attack, config, all_user_ids, all_axo_ids, stop_event))
            progress("   🔄 Replay Attack agent lanzado")

        if config.enable_id_spoofing:
            from chaos_agents import chaos_id_spoofing
            chaos_futures.append(executor.submit(
                chaos_id_spoofing, config, all_user_ids, all_axo_ids, stop_event))
            progress("   👤 ID Spoofing agent lanzado")

        if config.enable_race_condition:
            from chaos_agents import chaos_race_condition
            chaos_futures.append(executor.submit(
                chaos_race_condition, config, all_user_ids, all_axo_ids, stop_event))
            progress("   ⚡ Race Condition agent lanzado")

        if config.enable_double_booking:
            from chaos_agents import chaos_double_booking
            chaos_futures.append(executor.submit(
                chaos_double_booking, config, all_user_ids, all_axo_ids, stop_event))
            progress("   🎯 Double Booking agent lanzado")

        if config.enable_boundary_injection:
            from chaos_agents import chaos_boundary_injection
            chaos_futures.append(executor.submit(
                chaos_boundary_injection, config, all_user_ids, all_axo_ids, stop_event))
            progress("   💉 Boundary Injection agent lanzado")

        if config.enable_cooldown_bypass:
            from chaos_agents import chaos_cooldown_bypass
            chaos_futures.append(executor.submit(
                chaos_cooldown_bypass, config, all_user_ids, all_axo_ids, stop_event))
            progress("   ⏱️  Cooldown Bypass agent lanzado")

        progress(f"\n⏳ Ejecutando fase concurrente por {config.duration_seconds}s...\n")

        # Wait for the configured duration
        for elapsed in range(config.duration_seconds):
            # Dynamically refresh the shared all_axo_ids list from the database
            try:
                from sqlmodel import Session as _Sess, select as _sel_ids
                from app.models.axolotito import Axolotito as _Axo3
                with _Sess(engine) as session:
                    new_ids = list(session.exec(_sel_ids(_Axo3.id)).all())
                    all_axo_ids.clear()
                    all_axo_ids.extend(new_ids)
            except Exception:
                pass

            if elapsed % 15 == 0 and elapsed > 0:
                # Progress update every 15s
                stats = get_stats()
                counters = get_counters()
                progress(
                    f"   ⏱️  {elapsed}s / {config.duration_seconds}s | "
                    f"Acciones: {stats.get('bot_actions', 0)} | "
                    f"Ataques: {sum(counters.get(f'{k}_launched', 0) for k in ('replay','spoof','race','booking','injection','cooldown'))} | "
                    f"500s: {stats.get('bot_500s', 0)}"
                )
            time.sleep(1)

        progress("\n🛑 Señal de parada enviada a todos los hilos...")
        stop_event.set()

        # Wait for all futures to complete
        all_futures = bot_futures + chaos_futures
        done, not_done = fut_wait(all_futures, timeout=60)
        if not_done:
            progress(f"   ⚠️  {len(not_done)} hilos no terminaron en 60s")

        # Collect bot stats
        total_bot_actions = 0
        for fut in bot_futures:
            try:
                result = fut.result(timeout=5)
                if isinstance(result, dict):
                    total_bot_actions += result.get("actions_taken", 0)
            except Exception:
                pass

        increment_stat("bot_actions", total_bot_actions)

        # Collect agent counters
        for fut in chaos_futures:
            try:
                fut.result(timeout=5)
            except Exception:
                pass

    progress("✅ [CONCURRENT] Fase caótica completada.\n")

    # ── Phase 3: Validation Tests ────────────────────────────────────────────
    progress("=" * 70)
    progress("🛡️  [VALIDATION] Ejecutando tests de errores (phase_10)...")
    progress("=" * 70)

    with Session(engine) as session:
        state["session"] = session
        try:
            from phase_10_errors import phase_error_tests
            state.update(phase_error_tests(engine, sim_cfg, **state) or {})
        except Exception as e:
            progress(f"   ⚠️  Error en validación: {e}")

    # ── Phase 4: Report Generation ───────────────────────────────────────────
    progress("\n📊 [REPORT] Generando reporte de auditoría...")

    incidents = get_incidents()
    counters = get_counters()
    stats = get_stats()
    runtime = time.monotonic() - t_start

    report = generate_chaos_report(incidents, counters, stats, config, runtime)
    print(report)

    # Save to file
    report_path = os.environ.get(
        "CHAOS_REPORT_PATH",
        os.path.join(backend_dir, "chaos_simulation_report.txt"),
    )
    try:
        path = save_chaos_report(report, report_path)
        print(f"\n💾 Reporte guardado en: {path}")
    except Exception as e:
        print(f"\n⚠️  No se pudo guardar el reporte: {e}")

    # ── Cleanup ──────────────────────────────────────────────────────────────
    try:
        with Session(engine) as session:
            # Free stuck axolotitos
            from sqlmodel import select as _sel2
            stuck_axos = session.exec(
                _sel2(_Axo).where(_Axo.status == "playing")
            ).all()
            for a in stuck_axos:
                a.status = "idle"
                session.add(a)
            if stuck_axos:
                session.commit()
                print(f"  🧹 {len(stuck_axos)} axolotito(s) liberados.")
    except Exception:
        pass

    # Print final summary
    criticals = [i for i in incidents if i.severity.value == "CRITICAL"]
    warnings_list = [i for i in incidents if i.severity.value == "WARNING"]
    print(f"\n🎉 ¡Simulación Caótica v2 completada en {runtime:.1f}s!")
    print(f"   🔴 {len(criticals)} críticos | 🟡 {len(warnings_list)} warnings | "
          f"🟢 {len(incidents) - len(criticals) - len(warnings_list)} info")
    print(f"   ⚡ {stats.get('bot_actions', 0)} acciones de bots "
          f"({stats.get('bot_actions', 0) / max(1, runtime):.1f}/s)")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Entrypoint
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Chaos & Security Simulator v2 — Axolotto Stress Test"
    )
    parser.add_argument("--total-players", type=int, default=100,
                        help="Total de bots simultáneos (default: 100, max: 500)")
    parser.add_argument("--duration", type=int, default=120,
                        help="Duración de la fase concurrente en segundos (default: 120)")
    parser.add_argument("--skip-reset", action="store_true",
                        help="No resetear BD al inicio")
    parser.add_argument("--db-url", type=str, default=None,
                        help="Database URL directa")

    # Attack toggles
    parser.add_argument("--no-replay", action="store_true",
                        help="Deshabilitar Replay Attack")
    parser.add_argument("--no-spoof", action="store_true",
                        help="Deshabilitar ID Spoofing")
    parser.add_argument("--no-race", action="store_true",
                        help="Deshabilitar Race Condition (Double Spend)")
    parser.add_argument("--no-booking", action="store_true",
                        help="Deshabilitar Double Booking")
    parser.add_argument("--no-injection", action="store_true",
                        help="Deshabilitar Boundary Injection")
    parser.add_argument("--no-cooldown", action="store_true",
                        help="Deshabilitar Cooldown Bypass")

    args = parser.parse_args()

    # Clamp player count
    total = max(1, min(args.total_players, 500))

    config = ChaosConfig(
        total_players=total,
        duration_seconds=args.duration,
        skip_reset=args.skip_reset,
        db_url=args.db_url,
        enable_replay_attack=not args.no_replay,
        enable_id_spoofing=not args.no_spoof,
        enable_race_condition=not args.no_race,
        enable_double_booking=not args.no_booking,
        enable_boundary_injection=not args.no_injection,
        enable_cooldown_bypass=not args.no_cooldown,
    )

    run_chaos_simulation(config)


if __name__ == "__main__":
    main()
