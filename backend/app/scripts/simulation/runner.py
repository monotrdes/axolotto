#!/usr/bin/env python3
"""
runner.py — Modular entrypoint for the Axolotto Universe Simulator v3.

Usage:
    cd D:\Axolotto_2026\axolotto
    python backend/app/scripts/simulation/runner.py
    python backend/app/scripts/simulation/runner.py --players 4 --incubation 45 --games 5
"""

import sys
import os
import argparse

# ── Path setup ────────────────────────────────────────────────────────────────
# runner.py is at: backend/app/scripts/simulation/runner.py
# backend_dir is:  backend/
_this_file = os.path.abspath(__file__)
_sim_dir    = os.path.dirname(_this_file)           # .../scripts/simulation/
_scripts_dir = os.path.dirname(_sim_dir)            # .../scripts/
_app_dir    = os.path.dirname(_scripts_dir)         # .../app/
backend_dir = os.path.dirname(_app_dir)             # .../backend/
sys.path.insert(0, backend_dir)
sys.path.insert(0, _sim_dir)   # allows sibling phase files to import each other

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# ── Early arg parsing: --db-url must be set BEFORE app.database is imported ──
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--db-url", default=None)
_pre_args, _ = _pre.parse_known_args()
if _pre_args.db_url:
    os.environ["DATABASE_URL"] = _pre_args.db_url
elif not os.path.exists("/.dockerenv"):
    # Remap Docker hostnames when running on the host machine
    if "DATABASE_URL" in os.environ:
        _dbu = os.environ["DATABASE_URL"]
        if "@db_axolotto:5432" in _dbu:
            os.environ["DATABASE_URL"] = _dbu.replace("@db_axolotto:5432", "@127.0.0.1:5433")
    for _key in ("WEB3_PROVIDER_URL", "ANVIL_RPC_URL", "RPC_URL"):
        if _key in os.environ and "anvil_axolotto" in os.environ[_key]:
            os.environ[_key] = os.environ[_key].replace("anvil_axolotto", "127.0.0.1")

# ── App imports (after env is set) ───────────────────────────────────────────
from sqlmodel import Session

from app.database import engine  # single shared engine instance
from app.core.config import settings

from sim_types import SimConfig, _rng
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
from phase_08_solo import phase_individual_play
from phase_09_multi import phase_multiplayer
from phase_09e_social import phase_social_simulation
from phase_10_errors import phase_error_tests


def main():
    parser = argparse.ArgumentParser(description="Simulador v3 — Universo Axolotto")
    parser.add_argument("--players",      type=int,   default=4,  help="Jugadores simulados (exc. Pro)")
    parser.add_argument("--incubation",   type=int,   default=45, help="Segundos de incubación real")
    parser.add_argument("--games",        type=int,   default=5,  help="Partidas manuales por axolotito")
    parser.add_argument("--multi-wait",   type=int,   default=35, help="Segundos de espera de lobby por ronda multijugador")
    parser.add_argument("--skip-reset",   action="store_true",    help="No resetear BD al inicio")
    parser.add_argument("--max-boosters", type=int,   default=None, help="Boosters por jugador (sobreescribe personalidad)")
    parser.add_argument("--max-boards",   type=int,   default=None, help="Tableros por jugador (sobreescribe personalidad)")
    parser.add_argument("--max-webitos",  type=int,   default=None, help="Webitos por jugador (sobreescribe personalidad)")
    parser.add_argument("--db-url",       type=str,   default=None, help="Database URL directa (ej: postgresql://user:pass@127.0.0.1:5433/db)")
    parser.add_argument("--include-user", type=str,   default=None, help="privy_did de un usuario real para incluirlo como bot extra (su data se resetea)")
    parser.add_argument("--skip-imprinting", action="store_true", help="Salta la simulación de partidas de imprinting (más rápido)")
    parser.add_argument("--create-test-event", action="store_true", help="Crea un ManualModeEvent de prueba durante la simulación")
    parser.add_argument("--initial-axf", type=float, default=0.0, help="AXF inicial por jugador (0 = auto-calcular según personalidad)")
    parser.add_argument("--initial-frj", type=float, default=0.0, help="FRJ inicial por jugador (0 = auto-calcular según personalidad)")
    args = parser.parse_args()

    config = SimConfig(
        players=args.players,
        incubation=args.incubation,
        games=args.games,
        multi_wait=args.multi_wait,
        skip_reset=args.skip_reset,
        max_boosters=args.max_boosters,
        max_boards=args.max_boards,
        max_webitos=args.max_webitos,
        include_user=args.include_user,
        db_url=args.db_url,
        skip_imprinting=args.skip_imprinting,
        create_test_event=args.create_test_event,
        initial_axf=args.initial_axf,
        initial_frj=args.initial_frj,
    )

    print("\n" + "=" * 70)
    print("🚀  SIMULADOR DE UNIVERSO AXOLOTTO v3")
    print("=" * 70)
    print(f"👥 Jugadores: {args.players}  |  ⏱️  Incubación: {args.incubation}s  "
          f"|  🎮 Partidas: {args.games}  |  ⚔️  Multi-wait: {args.multi_wait}s")
    print("=" * 70)

    import warnings
    import logging
    warnings.filterwarnings("ignore")
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    engine.echo = False

    log_file = open("simulation.log", "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    def progress(msg: str) -> None:
        """Escribe una línea normal al terminal (va al stdout real, no al log)."""
        original_stdout.write(msg + "\n")
        original_stdout.flush()

    def live_progress(msg: str) -> None:
        """Sobreescribe la línea actual en terminal con \r (para contadores en vivo)."""
        # Padding a 90 chars para borrar residuos de líneas anteriores más largas
        original_stdout.write(f"\r{msg:<90}")
        original_stdout.flush()

    # ── Mock Web3Service for sim: skip real blockchain calls ─────────────────
    # Sim wallets are fake addresses without ETH. Patch all on-chain calls to
    # return mock hashes so phases don't fail on gas/funds errors.
    # Use a counter to generate unique tx hashes — ProcessedTransaction has a
    # UNIQUE constraint on tx_hash, so identical hashes cause integrity errors.
    from app.services import web3_service as _w3mod
    _mock_counter = [0]  # list for mutable closure in nonlocal-less lambdas
    def _mock_tx(*a, **kw):
        _mock_counter[0] += 1
        return f"0x_sim_mock_{_mock_counter[0]:06d}"
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
    # Force mock mode in outbox worker — avoids _dispatch_onchain entirely,
    # generates tx_hash from entry.id guaranteeing uniqueness per entry.
    settings.IS_MOCK_WEB3 = True

    stats: dict = {}
    errors: list = []

    session = Session(engine)

    # Build initial state: session, callbacks, stats, errors all travel in state
    state = {
        "session": session,
        "progress": progress,
        "live_progress": live_progress,
        "stats": stats,
        "errors": errors,
    }

    try:
        # Phase 0: Migrations (uses engine directly, not session)
        state.update(phase_migrations(engine, config, **state) or {})

        progress("⏳ [1/10] Reset...")
        if not config.skip_reset:
            state.update(phase_reset(engine, config, **state) or {})

        progress("⏳ [2/10] Usuarios...")
        state.update(phase_create_users(engine, config, **state) or {})

        # Apply --max-* overrides to each player's personality
        players = state["players"]
        if config.max_boosters is not None or config.max_boards is not None or config.max_webitos is not None:
            for p in players:
                pers = p["personality"]
                if config.max_boosters is not None:
                    # Override: set exactly N boosters (ignore personality default)
                    pers["boosters_normal"] = config.max_boosters
                    pers["boosters_foil"]   = 0
                if config.max_boards is not None:
                    pers["boards_random"] = config.max_boards
                if config.max_webitos is not None:
                    pers["eggs"] = config.max_webitos

        # ── Add real user as extra bot player ─────────────────────────────────
        if config.include_user:
            from sqlmodel import select
            from app.models.user import User
            real_user = session.exec(
                select(User).where(User.privy_did == config.include_user)
            ).first()
            if real_user:
                from sim_types import PERSONALITY_POOL
                # Assign personality (cycle through pool)
                real_personality = _rng.choice(PERSONALITY_POOL).copy()
                if config.max_boosters is not None:
                    real_personality["boosters_normal"] = config.max_boosters
                    real_personality["boosters_foil"]   = 0
                if config.max_boards is not None:
                    real_personality["boards_random"] = config.max_boards
                if config.max_webitos is not None:
                    real_personality["eggs"] = config.max_webitos
                players.append({
                    "user_id":      real_user.privy_did,
                    "wallet_addr":  real_user.wallet_address or f"0x{'cafe' + '0' * 36}",
                    "personality":  real_personality,
                })
                progress(f"  👤 Usuario real incluido como bot: {config.include_user}")
            else:
                progress(f"  ⚠️  Usuario {config.include_user} no encontrado en DB. Saltando.")

        # Crear evento de modo manual de prueba si se solicitó
        if config.create_test_event:
            from datetime import date, timedelta as td
            from app.models.manual_mode_event import ManualModeEvent
            from datetime import time as dtime
            test_event = ManualModeEvent(
                name="Evento de Prueba Simulación 🧪",
                start_date=date.today(),
                end_date=date.today() + td(days=7),
                daily_open_time=dtime(15, 0),
                daily_close_time=dtime(23, 0),
                tabla_cost_gal=10.0,
                bonus_gal_on_win=50.0,
                drop_multiplier=2.0,
                griton_delay_ms=2000,
                win_condition="tabla_llena",
                max_players_per_room=10,
                min_players_to_start=2,
                broadcast_message="🧪 Evento de prueba de simulación",
                created_by=players[0]["user_id"] if players else "sim_runner",
            )
            session.add(test_event)
            session.commit()
            progress("  ✅ ManualModeEvent de prueba creado")
            stats["test_event_created"] = True

        progress("⏳ [2b/10] Corcholatas — canjeando código promocional...")
        state.update(phase_redeem_corcholata(engine, config, **state) or {})

        progress("⏳ [2c/10] Ciclo Lunar — simulando recompensas diarias...")
        state.update(phase_daily_rewards(engine, config, **state) or {})

        progress("⏳ [3/10] Fondos + paquetes FRJ...")
        state.update(phase_fund_wallets(engine, config, **state) or {})

        progress("⏳ [3b/10] Cápsulas iniciales — sembrando saldo inicial...")
        state.update(phase_seed_tickets(engine, config, **state) or {})

        progress("⏳ [3c/10] VIP Club — suscripciones antes de compras...")
        state.update(phase_vip(engine, config, **state) or {})

        progress("⏳ [4/10] Boosters — compra (sellados, con descuento VIP si aplica)...")
        state.update(phase_buy_boosters(engine, config, **state) or {})

        # Apertura INMEDIATA: solo los jugadores con estrategia "immediate"
        progress("⏳ [4b/10] Boosters — apertura inmediata (whale)...")
        state.update(phase_open_boosters(engine, config, strategy="immediate", **state) or {})

        progress(f"⏳ [5/10] Incubación — tutorial + imprinting ({config.incubation}s max)...")
        state.update(phase_incubation(engine, config, **state) or {})

        # Apertura POST-INCUBACIÓN: selective (foils ya comprados) + random
        progress("⏳ [5b/10] Boosters — apertura post-incubación (selective + random)...")
        state.update(phase_open_boosters(engine, config, strategy="selective", **state) or {})

        progress("⏳ [6/10] Gashapon + cápsulas...")
        state.update(phase_gashapon(engine, config, **state) or {})

        # Apertura FINAL antes de crear tableros: hoarders abren sus sobres
        # (necesitan cartas para armar tableros manuales)
        progress("⏳ [6b/10] Boosters — apertura final (hoarder + restantes)...")
        state.update(phase_open_boosters(engine, config, strategy="final", **state) or {})

        progress("⏳ [7/10] Tableros...")
        state.update(phase_boards(engine, config, **state) or {})

        progress("⏳ [7b/10] Cenote Místico (Card Melter: Melt & Forge)...")
        state.update(phase_card_melter(engine, config, **state) or {})

        progress("⏳ [7c/10] Desarme Seguro (Solvente de Pegamento)...")
        state.update(phase_board_deconstruction(engine, config, **state) or {})

        progress("⏳ [7d/10] Mercado Secundario P2P...")
        state.update(phase_p2p_market(engine, config, **state) or {})

        progress(f"⏳ [9/10] Partidas individuales ({config.games} × jugador)...")
        # Apply --games override to each player's personality
        for p in players:
            p["personality"] = {**p["personality"], "solo_games": config.games}
        state.update(phase_individual_play(engine, config, **state) or {})

        progress("⏳ [9b/10] Multijugador + Recall...")
        state.update(phase_multiplayer(engine, config, **state) or {})

        progress("⏳ [9c/10] Expansión del Cenote (niveles 2-8)...")
        state.update(phase_cave_expansion(engine, config, **state) or {})

        progress("⏳ [9d/10] Decoración del Cenote (CAVE_ITEMs)...")
        state.update(phase_cave_decor(engine, config, **state) or {})

        progress("⏳ [9e/10] Capa Social — Amigos y Referidos...")
        state.update(phase_social_simulation(engine, config, **state) or {})

        progress("⏳ [10/10] Tests de errores...")
        state.update(phase_error_tests(engine, config, **state) or {})

    finally:
        # ── Cleanup: liberar axolotitos stuck en salas multiplayer ──────────
        try:
            from sqlmodel import select
            from app.models.axolotito import Axolotito as _Axo
            from app.models.lobby_models import GameRoom as _GR, RoomRegistration as _RR
            stuck_axos = session.exec(
                select(_Axo).where(_Axo.status == "playing")
            ).all()
            for a in stuck_axos:
                a.status = "idle"
                session.add(a)
            if stuck_axos:
                session.commit()
                progress(f"  🧹 {len(stuck_axos)} axolotito(s) liberados de estado 'playing'.")
            # Limpiar registros de salas activas
            active_regs = session.exec(select(_RR)).all()
            for r in active_regs:
                session.delete(r)
            empty_rooms = session.exec(select(_GR).where(_GR.status == "waiting")).all()
            for gr in empty_rooms:
                session.delete(gr)
            if active_regs or empty_rooms:
                session.commit()
        except Exception:
            session.rollback()
        session.close()
        sys.stdout = original_stdout
        log_file.close()

    # ── Reporte ──────────────────────────────────────────────────────────────
    gp = stats.get("games_played", 0)
    win_rate = (stats.get("wins", 0) / gp * 100) if gp > 0 else 0.0

    report = f"""
{'='*70}
📊  REPORTE FINAL — SIMULADOR AXOLOTTO v3
{'='*70}
👥  Usuarios creados:          {stats.get('users_created', 0)}
🎟️  Corcholatas canjeadas:     {stats.get('corcholatas_redeemed', 0)}
🎁  Corcholatas reclamadas:    {stats.get('corcholatas_claimed', 0)}
💸  AXF comprados (Sim.):      {stats.get('axg_purchased_qty', 0.0):.0f} AXF (Pesos: ${stats.get('axg_purchased_mxn', 0.0):.2f} MXN)
💎  Paquetes FRJ comprados:    {stats.get('frj_packs_bought', 0)}
🃏  Boosters normales:         {stats.get('boosters_bought', 0)}
✨  Boosters foil:             {stats.get('boosters_foil_bought', 0)}
🎯  Boosters extra (abiertos): {stats.get('boosters_extra_bought', 0)}
🎴  Cartas abiertas total:     {stats.get('cards_opened', 0)}
🥚  Webitos adoptados:         {stats.get('eggs_bought', 0)}
🐣  Axolotitos eclosionados:   {stats.get('eggs_hatched', 0)}
🎓  Tutoriales completados:    {stats.get('tutorial_boards', 0)} (Tabla Tutorial creada)
🧬  Naturalezas obtenidas:     {", ".join(f"{k}: {v}" for k, v in stats.get('natures', {}).items()) if stats.get('natures') else "Ninguna"}
😇  Karma Lucky:               {stats.get('karma_lucky', 0)}
🧂  Karma Salty:               {stats.get('karma_salty', 0)}
💧  Recompensas Salty (FRJ):   {stats.get('salty_rewards_received', 0)}
🌤️  Clima incubación:          {stats.get('weather_logged', '?')}
🎉  Evento de prueba creado:   {"Sí" if stats.get('test_event_created') else "No"}
{'-'*70}
🎰  Gashapon rolls:            {stats.get('gashapon_rolls', 0)}
💊  Cápsulas reclamadas:       {stats.get('capsule_claims', 0)}
🌟  Triple Suerte:             {stats.get('triple_suerte', 0)}
📋  Tableros creados:          {stats.get('boards_created', 0)}  ({stats.get('manual_boards', 0)} manuales)
🏪  Tableros en venta P2P:     {stats.get('boards_listed_sale', 0)}
🏠  Tableros en renta:         {stats.get('boards_listed_rent', 0)}
📈  Slots desbloqueados:       {stats.get('slot_upgrades', 0)}
🦎  Axos en venta P2P:         {stats.get('axos_listed_sale', 0)}
{'-'*70}
👑  VIP activados:             {stats.get('vip_activations', 0)}
🔄  VIP Auto-Renovación:       {stats.get('vip_auto_renew', 0)}
🌿  FRJ VIP reclamados:        {stats.get('vip_gal_claimed', 0)}
💸  Ahorro jugadores (VIP):    {stats.get('vip_savings_axg', 0.0):.2f} AXF  ← ingresos perdidos por la casa
{'-'*70}
🎮  Partidas individuales:     {gp}
  🏆 Victorias:               {stats.get('wins', 0)}  ({win_rate:.1f}%)
  💔 Derrotas:                {stats.get('losses', 0)}
  🤖 Autojuego:               {stats.get('autogames', 0)} partidas
  💰 FRJ obtenidas:           {stats.get('total_prize_gal', 0.0):.2f}
  🍽️  Alimentaciones:          {stats.get('feedings', 0)}
  😴 Ciclos sueño:            {stats.get('sleeps', 0)}
  🔧 Cave items equipados:    {stats.get('cave_equips', 0)}
  💍 Accesorios equipados:    {stats.get('accessory_equips', 0)}
{'-'*70}
⚔️  Salas multijugador:        {stats.get('multi_rooms_simulated', 0)}
  📞 Recall pasó:             {stats.get('recall_tests_passed', 0)}
  💵 Axos liquidados:         {stats.get('multi_axos_settled', 0)}
  💰 Jackpots ganados:        {stats.get('multi_jackpot_won', 0)}
{'-'*70}"""

    # Detalle de resultados multijugador por partida
    match_logs = stats.get("multi_match_logs", [])
    if match_logs:
        multi_victories = sum(1 for l in match_logs if l["outcome"] == "Victoria")
        multi_net = sum(l["net_gal"] for l in match_logs)
        report += f"""
  📊 Partidas jugadas:         {len(match_logs)}
  🏆 Victorias:               {multi_victories}  ({multi_victories/len(match_logs)*100:.0f}%)
  💸 FRJ neto total:          {multi_net:+.1f}
  Detalle:
"""
        for log in match_logs:
            icon = "🏆" if log["outcome"] == "Victoria" else "💔"
            axo_name = log["axo_name"][:20]
            room_name = log["room_name"][:24]
            report += (f"    {icon} {axo_name:<20} │ {room_name:<24} │ "
                       f"Neto: {log['net_gal']:+7.1f} FRJ │ XP: +{log['xp_gained']}\n")

    report += f"""
{'-'*70}
🌙  Ciclo Lunar (Daily):
  💰 FRJ acumulados:          {stats.get('daily_frj_earned', 0.0):.0f} FRJ
  💊 Cápsulas ganadas:        {stats.get('daily_capsules_won', 0)}
  🌕 Máx Luna alcanzada:      {stats.get('max_lunar_week_reached', 0)}
  📅 Máx racha diaria:        {stats.get('max_daily_streak_reached', 0)}
{'-'*70}
⛏️  Expansión del Cenote:
  🏗️  Expansiones totales:     {stats.get('cave_expansions_total', 0)}
  💸 AXF gastados (aceler.):  {stats.get('cave_expansion_axf_spent', 0.0):.0f}
  🏆 Máx nivel alcanzado:     {stats.get('max_cave_level_reached', 1)}
{'-'*70}
🖼️  Decoración del Cenote:
  🎨 Items equipados:         {stats.get('cave_items_equipped', 0)}
  🔒 Tests seguridad slot:    {stats.get('cave_decor_slot_mismatch_checked', 0)}
  🧬 Tests límite mentoría:   {stats.get('padrino_mentorship_errors_checked', 0)}
{'-'*70}
👥  Capa Social — Amigos:
  📨 Solicitudes enviadas:     {stats.get('social_friend_requests_sent', 0)}
  ✅ Solicitudes aceptadas:    {stats.get('social_friend_requests_accepted', 0)}
  ❌ Solicitudes rechazadas:   {stats.get('social_friend_requests_rejected', 0)}
  🤝 Amistades activas total:  {stats.get('social_total_active_friendships', 0)}
  ❤️  Likes dados:             {stats.get('social_likes_given', 0)} (total BD: {stats.get('social_total_likes_logged', 0)})
  🏠 Cuevas visitadas:         {stats.get('social_cave_visits', 0)} (total BD: {stats.get('social_total_visits_logged', 0)})
  🚫 Bloqueos:                 {stats.get('social_blocks_created', 0)}
  💔 Amistades eliminadas:     {stats.get('social_friends_removed', 0)}
  🔍 Sugerencias encontradas:  {stats.get('social_suggestions_checked', 0)}
{'-'*70}
🔗  Capa Social — Referidos:
  🏷️  Códigos generados:       {stats.get('social_codes_generated', 0)} (total BD: {stats.get('social_total_codes', 0)})
  📥 Códigos canjeados:        {stats.get('social_codes_claimed', 0)}
  🎯 Milestones procesados:    {stats.get('social_milestones_processed', 0)}
  👶 Referidos totales:        {stats.get('social_total_referrals', 0)}
{'-'*70}
🛡️  Capa Social — Anti-Abuso:
  🔒 Anti-fraud bloqueos:      {stats.get('social_anti_fraud_blocks', 0)}
  ⏱️  Rate-limit hits:         {stats.get('social_rate_limit_hits', 0)}
{'-'*70}
🚫  Tests de errores:
  ✅ Pasaron:                 {stats.get('error_tests_passed', 0)}
  ❌ Fallaron:                {stats.get('error_tests_failed', 0)}
{'='*70}
"""

    if errors:
        report += f"\n⚠️  ERRORES ({len(errors)}):\n"
        from collections import Counter
        for err, cnt in Counter(errors).most_common():
            report += f"  x{cnt}  {err}\n"
    else:
        report += "✅  Sin errores durante la simulación.\n"

    report += "=" * 70 + "\n"

    progress(report)

    try:
        with open("simulation_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("💾 Reporte guardado en simulation_report.txt")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el reporte: {e}")

    print("🎉 ¡Simulación v2 completada!")


if __name__ == "__main__":
    main()
