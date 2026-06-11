"""
Admin service — business logic for admin endpoints.

Moved from backend/app/api/v1/endpoints/admin.py during modular code guard
refactoring (Fase 3.4). No logic was changed.
"""

import os
import json
import pathlib
import re
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Session, select, func
from sqlalchemy import text, case as sa_case

from app.core.config import settings
from app.models.user import User
from app.models.economy import (
    Wallet,
    TransactionLedger,
    TransactionType,
    AxgPurchaseRecord,
    AxfPurchaseRecord,
)
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.models.promo import PromoCode, PendingReward
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.lobby_models import TreasuryVault, JackpotVault, MultiplayerGameLog, GameRoom
from app.models.manual_mode_event import ManualModeEvent
from app.services.rarity_service import get_card_dynamic_rarities

NPC_DID = "npc_axolotto_system"

logger = logging.getLogger("admin")

# ── In-memory simulation state ────────────────────────────────────────────────
_sim_state: dict = {"running": False, "started_at": None, "error": None}
_sim_lock = threading.Lock()


class SimRunParams(BaseModel):
    players: int = 4
    games: int = 5
    incubation: int = 45
    multi_wait: int = 35
    skip_reset: bool = False
    max_boosters: Optional[int] = None
    max_boards: Optional[int] = None
    max_webitos: Optional[int] = None
    include_user: Optional[str] = None
    skip_imprinting: bool = False
    create_test_event: bool = False
    initial_axf: float = 0.0
    initial_frj: float = 0.0


STEP_MAP = {
    "1": 3.0,
    "2": 8.0,
    "2b": 12.0,
    "2c": 16.0,
    "3": 20.0,
    "3b": 24.0,
    "3c": 28.0,
    "4": 32.0,
    "4b": 36.0,
    "5": 40.0,
    "5b": 48.0,
    "6": 52.0,
    "6b": 56.0,
    "7": 60.0,
    "7b": 64.0,
    "7c": 68.0,
    "7d": 72.0,
    "9": 78.0,
    "9b": 84.0,
    "9c": 90.0,
    "9d": 94.0,
    "10": 97.0,
}


def get_sim_progress(progress_path: str) -> dict:
    if not os.path.exists(progress_path):
        return {"progress": 0.0, "current_step": "Iniciando...", "live_details": ""}

    try:
        with open(progress_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return {"progress": 0.0, "current_step": "Error leyendo progreso", "live_details": ""}

    raw_lines = [line.strip() for line in content.replace("\r", "\n").split("\n") if line.strip()]

    current_step = "Iniciando..."
    step_key = "1"
    live_details = ""
    progress_val = 0.0

    step_pattern = re.compile(r"⏳\s*\[(\d+[a-z]?)/10\]\s*(.*)")
    pct_pattern = re.compile(r"(\d+(?:\.\d+)?)%")

    for line in raw_lines:
        match = step_pattern.search(line)
        if match:
            step_key = match.group(1)
            step_desc = match.group(2)
            current_step = f"[{step_key}/10] {step_desc}"
            progress_val = STEP_MAP.get(step_key, progress_val)
            live_details = ""
        else:
            if any(
                line.startswith(prefix)
                for prefix in ("⏳", "💰", "👤", "🥚", "  ", "💎", "🃏", "✨", "🎯", "🎴", "👑", "🌿", "🎮", "⚔️")
            ):
                live_details = line
            elif len(line) < 120 and "simulando" in line.lower():
                live_details = line

            if step_key == "5":
                pct_match = pct_pattern.search(line)
                if pct_match:
                    try:
                        inc_pct = float(pct_match.group(1))
                        progress_val = 35.0 + (inc_pct / 100.0) * 10.0
                    except ValueError:
                        pass

    return {
        "progress": round(progress_val, 1),
        "current_step": current_step,
        "live_details": live_details,
    }


def _run_sim_task(params: SimRunParams) -> None:
    global _sim_state
    cmd = [
        "python", "-u", "app/scripts/simulation/runner.py",
        "--players", str(params.players),
        "--games", str(params.games),
        "--incubation", str(params.incubation),
        "--multi-wait", str(params.multi_wait),
        "--db-url", settings.DATABASE_URL,
    ]
    if params.skip_reset:
        cmd.append("--skip-reset")
    if params.skip_imprinting:
        cmd.append("--skip-imprinting")
    if params.create_test_event:
        cmd.append("--create-test-event")
    for flag, val in [
        ("--max-boosters", params.max_boosters),
        ("--max-boards", params.max_boards),
        ("--max-webitos", params.max_webitos),
        ("--include-user", params.include_user),
    ]:
        if val is not None:
            cmd.extend([flag, str(val)])
    if params.initial_axf > 0:
        cmd.extend(["--initial-axf", str(params.initial_axf)])
    if params.initial_frj > 0:
        cmd.extend(["--initial-frj", str(params.initial_frj)])
    try:
        progress_path = settings.SIMULATION_REPORT_PATH.replace("report.txt", "progress.log")
        if os.path.exists(progress_path):
            try:
                os.remove(progress_path)
            except Exception:
                pass
        with open(progress_path, "w", encoding="utf-8") as f:
            process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd="/app")
            process.wait(timeout=900)
            if process.returncode != 0:
                # Leer últimas líneas del log para diagnóstico
                try:
                    with open(progress_path, "r", encoding="utf-8", errors="ignore") as rf:
                        tail = rf.read()[-2000:] if os.path.getsize(progress_path) > 0 else ""
                except Exception:
                    tail = ""
                error_msg = f"Simulación terminó con código {process.returncode}"
                logger.error(error_msg)
                with _sim_lock:
                    _sim_state["error"] = error_msg + ("\n" + tail[-500:] if tail else "")
    except Exception as e:
        logger.error("Simulation task failed: %s", e, exc_info=True)
        with _sim_lock:
            _sim_state["error"] = str(e)[:500]
    finally:
        with _sim_lock:
            _sim_state.update({"running": False, "started_at": None})


# ── Service functions ─────────────────────────────────────────────────────────


def check_admin_status(user_id: str) -> dict:
    """Check if user is an admin and return status."""
    admin_dids = settings.admin_dids
    is_admin = user_id in admin_dids

    if is_admin:
        logger.info(f"Admin access granted for user_id={user_id}")
    else:
        logger.warning(
            f"Admin access denied for user_id={user_id}. "
            f"ADMIN_PRIVY_DIDS={'set' if settings.ADMIN_PRIVY_DIDS else 'empty'}, "
            f"ADMIN_PRIVY_DID={'set' if settings.ADMIN_PRIVY_DID else 'empty'}"
        )

    return {
        "is_admin": is_admin,
        "configured_did": (admin_dids[0] if admin_dids else None) if is_admin else None,
    }


def get_overview(session: Session) -> dict:
    """Gather admin overview / dashboard metrics."""
    now = datetime.utcnow()

    total_users = session.exec(
        select(func.count(User.id)).where(User.privy_did != NPC_DID)
    ).one()

    total_gal = session.exec(
        select(func.sum(Wallet.frijolitos)).where(Wallet.user_id != NPC_DID)
    ).one() or 0.0

    total_axg = session.exec(
        select(func.sum(Wallet.axofichas)).where(Wallet.user_id != NPC_DID)
    ).one() or 0.0

    vip_rows = session.exec(
        select(User.vip_tier, func.count(User.id))
        .where(User.privy_did != NPC_DID)
        .where(User.vip_expires_at > now)
        .where(User.vip_tier.isnot(None))
        .group_by(User.vip_tier)
    ).all()
    vip_counts = {tier: count for tier, count in vip_rows}

    treasury = session.exec(select(TreasuryVault)).first()
    jackpot = session.exec(select(JackpotVault)).first()

    total_boards = session.exec(
        select(func.count(PlayerBoard.id))
        .where(PlayerBoard.is_npc_pool == False)
        .where(PlayerBoard.is_dead == False)
    ).one()

    total_axos = session.exec(
        select(func.count(Axolotito.id)).where(Axolotito.user_id != NPC_DID)
    ).one()

    loteria_agg = session.exec(
        select(func.sum(PlayerBoard.games_played), func.sum(PlayerBoard.games_won))
        .where(PlayerBoard.is_npc_pool == False)
    ).one()
    total_loteria_games = int(loteria_agg[0] or 0)
    total_loteria_wins = int(loteria_agg[1] or 0)
    global_loteria_win_rate = round(
        (total_loteria_wins / total_loteria_games * 100) if total_loteria_games > 0 else 0.0, 1
    )

    total_mp_games = session.exec(
        select(func.count(MultiplayerGameLog.id)).where(MultiplayerGameLog.user_id != NPC_DID)
    ).one()

    active_rooms = session.exec(
        select(func.count(GameRoom.id)).where(GameRoom.status == "waiting")
    ).one()

    # --- CORCHOLATAS / PROMOS ---
    corcholata_rows = session.execute(
        select(
            func.count(PendingReward.id).label("total_claimed"),
            func.coalesce(func.sum(PendingReward.reward_axf), 0).label("total_axf"),
            func.coalesce(func.sum(PendingReward.reward_frj), 0).label("total_frj"),
        ).where(PendingReward.claimed == True)
    ).one()
    corcholata_stats = {
        "total_claimed": int(corcholata_rows.total_claimed),
        "total_axf_gifted": round(float(corcholata_rows.total_axf), 2),
        "total_frj_gifted": round(float(corcholata_rows.total_frj), 2),
    }

    # --- COMPRAS CRYPTO (USDC on-chain) ---
    crypto_row = session.execute(
        text("""SELECT COUNT(id) AS total_orders,
                       COALESCE(SUM(axg_amount), 0) AS total_axf,
                       COALESCE(SUM(usd_amount), 0)  AS total_usd
                FROM cryptopurchaseorder
               WHERE status = 'COMPLETED'""")
    ).one()
    crypto_stats = {
        "completed_orders": int(crypto_row.total_orders),
        "total_axf_sold": round(float(crypto_row.total_axf), 2),
        "total_usd_received": round(float(crypto_row.total_usd), 2),
    }

    # --- CÁLCULO DE GANANCIAS EN PESOS (MXN) ---
    total_purchased_mxn = session.exec(
        select(func.sum(AxgPurchaseRecord.mxn_amount))
    ).one() or 0.0

    total_iva_mxn = total_purchased_mxn * 0.16 / 1.16
    total_gateway_fees_mxn = total_purchased_mxn * 0.045
    total_net_revenue_mxn = total_purchased_mxn - total_iva_mxn - total_gateway_fees_mxn

    # Tasa del 70% del bruto (1 AXF = $1.40 MXN payout)
    required_reserve_mxn_70_gross = total_axg * 1.40
    unlocked_profit_mxn_70_gross = max(0.0, total_net_revenue_mxn - required_reserve_mxn_70_gross)

    # Tasa del 70% del neto (1 AXF = $1.14 MXN payout)
    required_reserve_mxn_70_net = total_axg * 1.14
    unlocked_profit_mxn_70_net = max(0.0, total_net_revenue_mxn - required_reserve_mxn_70_net)

    # Tasa del 50% del bruto (DevEx base: 1 AXF = $1.00 MXN payout)
    required_reserve_mxn_50_gross = total_axg * 1.00
    unlocked_profit_mxn_50_gross = max(0.0, total_net_revenue_mxn - required_reserve_mxn_50_gross)

    # Calcular promedio de compra de AXF e histórico
    total_purchased_axg = session.exec(
        select(func.sum(AxfPurchaseRecord.axf_amount))
    ).one() or 0.0

    if total_purchased_axg > 0:
        avg_price_per_axg = total_purchased_mxn / total_purchased_axg
    else:
        avg_price_per_axg = 0.15

    total_axg_in_circulation_mxn = total_axg * avg_price_per_axg
    avg_price_per_gal = avg_price_per_axg / 10.0
    total_gal_in_circulation_mxn = total_gal * avg_price_per_gal

    # Count active manual mode events
    active_events = session.exec(
        select(func.count(ManualModeEvent.id))
        .where(ManualModeEvent.is_active == True)
        .where(ManualModeEvent.end_date >= datetime.utcnow().date())
    ).one()
    upcoming_events = session.exec(
        select(func.count(ManualModeEvent.id))
        .where(ManualModeEvent.is_active == True)
        .where(ManualModeEvent.start_date > datetime.utcnow().date())
    ).one()

    return {
        "total_users": total_users,
        "total_frj_in_circulation": round(float(total_gal), 2),
        "total_frj_in_circulation_mxn": round(float(total_gal_in_circulation_mxn), 2),
        "total_axf_in_circulation": round(float(total_axg), 2),
        "total_axf_in_circulation_mxn": round(float(total_axg_in_circulation_mxn), 2),
        "treasury_balance": round(float(treasury.balance) if treasury else 0.0, 2),
        "jackpot_current": round(float(jackpot.current_amount) if jackpot else 0.0, 2),
        "vip_counts": vip_counts,
        "total_loteria_games": total_loteria_games,
        "global_loteria_win_rate_pct": global_loteria_win_rate,
        "total_multiplayer_games": total_mp_games,
        "active_rooms": active_rooms,
        "total_boards": total_boards,
        "total_axolotitos": total_axos,
        "active_manual_events": active_events,
        "upcoming_manual_events": upcoming_events,
        "financials": {
            "total_purchased_mxn": round(total_purchased_mxn, 2),
            "total_iva_mxn": round(total_iva_mxn, 2),
            "total_gateway_fees_mxn": round(total_gateway_fees_mxn, 2),
            "total_net_revenue_mxn": round(total_net_revenue_mxn, 2),
            "devex_70_gross": {
                "payout_per_axf": 1.40,
                "required_reserve_mxn": round(required_reserve_mxn_70_gross, 2),
                "unlocked_profit_mxn": round(unlocked_profit_mxn_70_gross, 2),
            },
            "devex_70_net": {
                "payout_per_axf": 1.14,
                "required_reserve_mxn": round(required_reserve_mxn_70_net, 2),
                "unlocked_profit_mxn": round(unlocked_profit_mxn_70_net, 2),
            },
            "devex_50_gross": {
                "payout_per_axf": 1.00,
                "required_reserve_mxn": round(required_reserve_mxn_50_gross, 2),
                "unlocked_profit_mxn": round(unlocked_profit_mxn_50_gross, 2),
            },
        },
        "corcholatas": corcholata_stats,
        "crypto_purchases": crypto_stats,
    }


def get_players(
    session: Session,
    search: Optional[str] = None,
    sort: str = "created_at_desc",
    page: int = 1,
    limit: int = 50,
) -> dict:
    """List all real players with aggregated stats."""
    now = datetime.utcnow()

    axo_sq = (
        select(Axolotito.user_id, func.count(Axolotito.id).label("axo_count"))
        .where(Axolotito.user_id != NPC_DID)
        .group_by(Axolotito.user_id)
        .subquery()
    )
    board_sq = (
        select(
            PlayerBoard.user_id,
            func.count(PlayerBoard.id).label("board_count"),
            func.sum(PlayerBoard.games_played).label("total_games"),
            func.sum(PlayerBoard.games_won).label("total_wins"),
        )
        .where(PlayerBoard.is_npc_pool == False)
        .group_by(PlayerBoard.user_id)
        .subquery()
    )

    stmt = (
        select(
            User.privy_did,
            User.nickname,
            User.email,
            User.vip_tier,
            User.vip_expires_at,
            User.created_at,
            Wallet.frijolitos,
            Wallet.axofichas,
            func.coalesce(axo_sq.c.axo_count, 0).label("axo_count"),
            func.coalesce(board_sq.c.board_count, 0).label("board_count"),
            func.coalesce(board_sq.c.total_games, 0).label("total_games"),
            func.coalesce(board_sq.c.total_wins, 0).label("total_wins"),
        )
        .where(User.privy_did != NPC_DID)
        .outerjoin(Wallet, Wallet.user_id == User.privy_did)
        .outerjoin(axo_sq, axo_sq.c.user_id == User.privy_did)
        .outerjoin(board_sq, board_sq.c.user_id == User.privy_did)
    )

    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (User.nickname.ilike(like)) | (User.email.ilike(like)) | (User.privy_did.ilike(like))
        )

    win_rate_expr = sa_case(
        (board_sq.c.total_games > 0, board_sq.c.total_wins * 100.0 / board_sq.c.total_games),
        else_=0.0,
    )
    sort_map = {
        "nickname_asc":       User.nickname.asc(),
        "nickname_desc":      User.nickname.desc(),
        "email_asc":          User.email.asc(),
        "email_desc":         User.email.desc(),
        "frj_asc":            Wallet.frijolitos.asc(),
        "frj_desc":           Wallet.frijolitos.desc(),
        "axf_asc":            Wallet.axofichas.asc(),
        "axf_desc":           Wallet.axofichas.desc(),
        "axo_count_asc":      func.coalesce(axo_sq.c.axo_count, 0).asc(),
        "axo_count_desc":     func.coalesce(axo_sq.c.axo_count, 0).desc(),
        "board_count_asc":    func.coalesce(board_sq.c.board_count, 0).asc(),
        "board_count_desc":   func.coalesce(board_sq.c.board_count, 0).desc(),
        "total_games_asc":    func.coalesce(board_sq.c.total_games, 0).asc(),
        "total_games_desc":   func.coalesce(board_sq.c.total_games, 0).desc(),
        "win_rate_asc":       win_rate_expr.asc(),
        "win_rate_desc":      win_rate_expr.desc(),
        "created_at_asc":     User.created_at.asc(),
        "created_at_desc":    User.created_at.desc(),
        # legacy aliases kept for backwards compat
        "gal_desc":           Wallet.frijolitos.desc(),
        "axg_desc":           Wallet.axofichas.desc(),
    }
    stmt = stmt.order_by(sort_map.get(sort, User.created_at.desc()))
    stmt = stmt.offset((page - 1) * limit).limit(limit)

    rows = session.execute(stmt).all()
    results = []
    for row in rows:
        total_games = int(row.total_games or 0)
        total_wins = int(row.total_wins or 0)
        is_vip_active = row.vip_expires_at and row.vip_expires_at > now
        results.append({
            "privy_did": row.privy_did,
            "nickname": row.nickname,
            "email": row.email,
            "vip_tier": row.vip_tier if is_vip_active else None,
            "frj": round(float(row.frijolitos or 0.0), 2),
            "axf": round(float(row.axofichas or 0.0), 2),
            "axo_count": int(row.axo_count),
            "board_count": int(row.board_count),
            "total_games": total_games,
            "win_rate": round((total_wins / total_games * 100) if total_games > 0 else 0.0, 1),
            "created_at": row.created_at.isoformat() if row.created_at else None,
        })
    return {"players": results, "page": page, "limit": limit}


def get_player_detail(session: Session, player_did: str) -> dict:
    """Get full details for a single player."""
    from fastapi import HTTPException

    now = datetime.utcnow()
    user = session.exec(select(User).where(User.privy_did == player_did)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    wallet = session.exec(select(Wallet).where(Wallet.user_id == player_did)).first()

    axolotitos = session.exec(
        select(Axolotito).where(Axolotito.user_id == player_did)
    ).all()

    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == player_did)
        .where(PlayerBoard.is_npc_pool == False)
    ).all()

    recent_txs = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.user_id == player_did)
        .order_by(TransactionLedger.created_at.desc())
        .limit(50)
    ).all()

    mp_history = session.exec(
        select(MultiplayerGameLog)
        .where(MultiplayerGameLog.user_id == player_did)
        .order_by(MultiplayerGameLog.created_at.desc())
        .limit(20)
    ).all()

    return {
        "user": {
            "privy_did": user.privy_did,
            "nickname": user.nickname,
            "email": user.email,
            "wallet_address": user.wallet_address,
            "vip_tier": user.vip_tier if user.is_vip else None,
            "vip_expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None,
            "vip_streak_months": user.vip_streak_months,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "unlocked_board_slots": user.unlocked_board_slots,
        },
        "wallet": {
            "frj": round(float(wallet.frijolitos), 2),
            "axf": round(float(wallet.axofichas), 2),
            "frag_comun": wallet.frag_comun,
            "frag_raro": wallet.frag_raro,
            "frag_epico": wallet.frag_epico,
            "frag_legendario": wallet.frag_legendario,
        }
        if wallet
        else None,
        "axolotitos": [
            {
                "id": a.id,
                "name": a.name,
                "level": a.level,
                "experience": a.experience,
                "status": a.status,
                "energy_current": a.energy_current,
                "cpu_win_streak": a.cpu_win_streak,
                "escrow_balance_gal": float(a.escrow_balance_gal),
                "stats": {
                    "salinity": a.stat_salinity,
                    "luck": a.stat_luck,
                    "focus": a.stat_focus,
                    "stamina": a.stat_stamina,
                    "charisma": a.stat_charisma,
                    "agility": a.stat_agility,
                    "wisdom": a.stat_wisdom,
                    "strength": a.stat_strength,
                    "suerte": a.stat_luck,
                    "ojo": a.stat_focus,
                    "pila": a.stat_stamina,
                    "sal": a.stat_salinity,
                },
                "skin_color": a.skin_color,
                "is_frozen_by_vip": a.is_frozen_by_vip,
            }
            for a in axolotitos
        ],
        "boards": [
            {
                "id": b.id,
                "name": b.name,
                "level": b.level,
                "xp": b.xp,
                "card_count": len(b.card_ids) if b.card_ids else 0,
                "games_played": b.games_played,
                "games_won": b.games_won,
                "win_rate": round(
                    (b.games_won / b.games_played * 100) if b.games_played > 0 else 0.0, 1
                ),
                "is_dead": b.is_dead,
                "is_frozen_by_vip": b.is_frozen_by_vip,
            }
            for b in boards
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "tx_type": t.tx_type.value if hasattr(t.tx_type, "value") else str(t.tx_type),
                "currency": t.currency.value if hasattr(t.currency, "value") else str(t.currency),
                "amount": float(t.amount),
                "description": t.description,
            }
            for t in recent_txs
        ],
        "multiplayer_history": [
            {
                "id": g.id,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "room_name": g.room_name,
                "axo_name": g.axo_name,
                "outcome": g.outcome,
                "net_gal": float(g.net_gal),
                "xp_gained": g.xp_gained,
            }
            for g in mp_history
        ],
    }


def get_economy_charts(session: Session) -> dict:
    """Get economy chart data for the admin dashboard."""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    gal_rows = session.execute(
        text("""
            SELECT DATE(created_at) as day, SUM(ABS(amount)) as volume
            FROM transactionledger
            WHERE currency::text = 'frijolito'
              AND user_id != :npc
              AND created_at >= :cutoff
            GROUP BY day
            ORDER BY day ASC
        """),
        {"npc": NPC_DID, "cutoff": thirty_days_ago},
    ).all()

    games_rows = session.execute(
        text("""
            SELECT DATE(created_at) as day, COUNT(*) as games
            FROM multiplayergamelog
            WHERE user_id != :npc
              AND created_at >= :cutoff
            GROUP BY day
            ORDER BY day ASC
        """),
        {"npc": NPC_DID, "cutoff": thirty_days_ago},
    ).all()

    tx_rows = session.exec(
        select(TransactionLedger.tx_type, func.count(TransactionLedger.id))
        .where(TransactionLedger.user_id != NPC_DID)
        .group_by(TransactionLedger.tx_type)
    ).all()

    vip_rows = session.exec(
        select(User.vip_tier, func.count(User.id))
        .where(User.privy_did != NPC_DID)
        .where(User.vip_expires_at > now)
        .where(User.vip_tier.isnot(None))
        .group_by(User.vip_tier)
    ).all()

    total_real_users = session.exec(
        select(func.count(User.id)).where(User.privy_did != NPC_DID)
    ).one()
    active_vip_total = sum(count for _, count in vip_rows)

    # ── DETAILED BREAKDOWN OF THE LAST 30 DAYS ──
    tx_records = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.user_id != NPC_DID)
        .where(
            TransactionLedger.tx_type.in_(
                [TransactionType.MARKET_BUY, TransactionType.BOOSTER_PURCHASE]
            )
        )
    ).all()

    catalog_items = session.exec(select(ItemCatalog)).all()
    name_to_type = {item.name: item.item_type for item in catalog_items}

    webitos_dict = {}
    boosters_dict = {}
    gashapon_dict = {
        "common_gal": {"count": 0, "volume": 0.0},
        "common_ticket": {"count": 0, "volume": 0.0},
        "premium_gal": {"count": 0, "volume": 0.0},
        "premium_ticket": {"count": 0, "volume": 0.0},
    }
    capsulas_dict = {
        "bronce": {"count": 0, "volume": 0.0},
        "plata": {"count": 0, "volume": 0.0},
        "oro": {"count": 0, "volume": 0.0},
        "diaria": {"count": 0, "volume": 0.0},
    }
    vip_dict = {}
    other_dict = {}
    exchange_dict = {"count": 0, "axf_spent": 0.0, "frj_received": 0.0}

    for tx in tx_records:
        desc = tx.description or ""
        amount = abs(float(tx.amount))
        currency = tx.currency.value if hasattr(tx.currency, "value") else str(tx.currency)
        currency = currency.lower()

        if desc.startswith("Compra de sobre sellado de "):
            item_name = desc.replace("Compra de sobre sellado de ", "")
            if item_name not in boosters_dict:
                boosters_dict[item_name] = {
                    "name": item_name, "count": 0, "axf_vol": 0.0, "frj_vol": 0.0,
                }
            boosters_dict[item_name]["count"] += 1
            if currency == "axoficha":
                boosters_dict[item_name]["axf_vol"] += amount
            else:
                boosters_dict[item_name]["frj_vol"] += amount

        elif desc.startswith("Compra de "):
            item_name = desc.replace("Compra de ", "")
            item_type = name_to_type.get(item_name)
            if item_type == ItemType.EGG:
                if item_name not in webitos_dict:
                    webitos_dict[item_name] = {
                        "name": item_name, "count": 0, "axf_vol": 0.0, "frj_vol": 0.0,
                    }
                webitos_dict[item_name]["count"] += 1
                if currency == "axoficha":
                    webitos_dict[item_name]["axf_vol"] += amount
                else:
                    webitos_dict[item_name]["frj_vol"] += amount
            else:
                if item_name not in other_dict:
                    other_dict[item_name] = {
                        "name": item_name,
                        "count": 0,
                        "axf_vol": 0.0,
                        "frj_vol": 0.0,
                        "type": (
                            item_type.value
                            if hasattr(item_type, "value")
                            else str(item_type)
                            if item_type
                            else "OTHER"
                        ),
                    }
                other_dict[item_name]["count"] += 1
                if currency == "axoficha":
                    other_dict[item_name]["axf_vol"] += amount
                else:
                    other_dict[item_name]["frj_vol"] += amount

        elif desc.startswith("Activación Pase VIP "):
            tier = desc.replace("Activación Pase VIP ", "").split(" ")[0]
            if tier not in vip_dict:
                vip_dict[tier] = {"tier": tier, "count": 0, "axf_vol": 0.0}
            vip_dict[tier]["count"] += 1
            vip_dict[tier]["axf_vol"] += amount

        elif desc.startswith("Gashapón ("):
            is_premium = "PREMIUM" in desc.upper()
            is_ticket = "usando Ficha" in desc or "usando ticket" in desc.lower()
            roll_tier = "premium" if is_premium else "common"
            roll_type = "ticket" if is_ticket else "frj"
            key = f"{roll_tier}_{roll_type}"
            if key in gashapon_dict:
                gashapon_dict[key]["count"] += 1
                if not is_ticket:
                    gashapon_dict[key]["volume"] += amount

        elif desc.startswith("Cápsula "):
            parts = desc.split(" ")
            if len(parts) > 1:
                raw_tier = (
                    parts[1]
                    .replace("★LEGENDARIO★", "")
                    .replace("★TABLA FORJADA★", "")
                    .lower()
                )
                if raw_tier in capsulas_dict:
                    capsulas_dict[raw_tier]["count"] += 1
                    capsulas_dict[raw_tier]["volume"] += amount
                elif "diaria" in desc.lower() or "free" in desc.lower():
                    capsulas_dict["diaria"]["count"] += 1
                    capsulas_dict["diaria"]["volume"] += amount

        elif desc.startswith("Intercambio de AXF por "):
            exchange_dict["count"] += 1
            if currency == "axoficha":
                exchange_dict["axf_spent"] += amount
            try:
                frj_part = desc.split(" por ")[1].split(" ")[0]
                exchange_dict["frj_received"] += float(frj_part)
            except Exception:
                pass

    # Count Phase 1 webitos distributed via promo codes
    promo_rows = session.exec(
        select(ItemCatalog.name, func.count(PromoCode.id))
        .join(PromoCode, PromoCode.reward_item_id == ItemCatalog.id)
        .where(PromoCode.redeemed_by.isnot(None))
        .where(ItemCatalog.item_type == ItemType.EGG)
        .group_by(ItemCatalog.name)
    ).all()
    for item_name, count in promo_rows:
        if item_name not in webitos_dict:
            webitos_dict[item_name] = {
                "name": item_name, "count": 0, "axg_vol": 0.0, "gal_vol": 0.0,
            }
        webitos_dict[item_name]["count"] += count

    return {
        "daily_gal_volume": [
            {"day": str(r[0]), "volume": round(float(r[1]), 2)} for r in gal_rows
        ],
        "daily_mp_games": [
            {"day": str(r[0]), "games": int(r[1])} for r in games_rows
        ],
        "tx_type_breakdown": [
            {"tx_type": str(r[0]), "count": int(r[1])} for r in tx_rows
        ],
        "vip_distribution": [
            {"tier": r[0], "count": r[1]} for r in vip_rows
        ]
        + [
            {
                "tier": "sin_vip",
                "count": max(0, total_real_users - active_vip_total),
            }
        ],
        "detailed_breakdown": {
            "webitos": list(webitos_dict.values()),
            "boosters": list(boosters_dict.values()),
            "gashapon": gashapon_dict,
            "capsulas": capsulas_dict,
            "vip": list(vip_dict.values()),
            "other_items": list(other_dict.values()),
            "currency_exchange": exchange_dict,
        },
    }


def get_simulation_report() -> dict:
    """Read and return the simulation report file."""
    from fastapi import HTTPException

    path = settings.SIMULATION_REPORT_PATH
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Reporte no encontrado en: {path}")
    resolved = pathlib.Path(path).resolve()
    if not resolved.is_relative_to(pathlib.Path("/app")):
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    modified_at = datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()
    return {"content": content, "modified_at": modified_at}


def get_simulation_status() -> dict:
    """Return current simulation run status."""
    progress_path = settings.SIMULATION_REPORT_PATH.replace("report.txt", "progress.log")
    if _sim_state["running"]:
        prog_data = get_sim_progress(progress_path)
        return {
            "running": True,
            "started_at": _sim_state["started_at"],
            "progress": prog_data["progress"],
            "current_step": prog_data["current_step"],
            "live_details": prog_data["live_details"],
        }
    else:
        error = _sim_state.get("error")
        if error:
            return {
                "running": False,
                "started_at": None,
                "progress": 0.0,
                "current_step": f"Error: {error[:200]}",
                "live_details": "",
            }
        report_exists = os.path.exists(settings.SIMULATION_REPORT_PATH)
        return {
            "running": False,
            "started_at": None,
            "progress": 100.0 if report_exists else 0.0,
            "current_step": "Completada" if report_exists else "No iniciada",
            "live_details": "",
        }


def run_simulation(params: SimRunParams, background_tasks) -> dict:
    """Start a new simulation in the background."""
    from fastapi import HTTPException

    if params.include_user:
        if not re.fullmatch(r"did:privy:[a-zA-Z0-9_-]+", params.include_user):
            raise HTTPException(
                status_code=400,
                detail="Formato de include_user inválido. Debe ser un Privy DID.",
            )

    with _sim_lock:
        if _sim_state["running"]:
            raise HTTPException(
                status_code=409,
                detail="Simulación ya en ejecución. Espera a que termine.",
            )
        _sim_state.update({"running": True, "started_at": datetime.utcnow().isoformat(), "error": None})
    background_tasks.add_task(_run_sim_task, params)
    return {"status": "started"}


# ── Chaos & Security Simulator v2 ────────────────────────────────────────────────

class ChaosRunParams(BaseModel):
    """Parameters for the Chaos & Security Simulator v2."""
    total_players: int = 100
    duration: int = 120
    skip_reset: bool = False
    enable_replay_attack: bool = True
    enable_id_spoofing: bool = True
    enable_race_condition: bool = True
    enable_double_booking: bool = True
    enable_boundary_injection: bool = True
    enable_cooldown_bypass: bool = True


# ── In-memory chaos simulation state ──────────────────────────────────────────
_chaos_sim_state: dict = {"running": False, "started_at": None, "error": None}
_chaos_sim_lock = threading.Lock()

CHAOS_PROGRESS_PATH = "/app/chaos_simulation_progress.log"
CHAOS_REPORT_PATH = "/app/chaos_simulation_report.txt"
CHAOS_ACTIVITIES_PATH = "/app/chaos_activities.json"


def _parse_chaos_progress(progress_path: str) -> dict:
    """Parse the chaos runner's stdout log for progress info."""
    if not os.path.exists(progress_path):
        return {"progress": 0.0, "current_phase": "Iniciando...", "live_details": ""}

    try:
        with open(progress_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return {"progress": 0.0, "current_phase": "Error leyendo progreso", "live_details": ""}

    lines = content.replace("\r", "\n").split("\n")

    current_phase = "Iniciando..."
    progress_val = 0.0
    live_details = ""

    setup_markers = {
        "[SETUP/0]": 2.0, "[SETUP/1]": 5.0, "[SETUP/2]": 10.0,
        "[SETUP/3]": 15.0, "[SETUP/4]": 22.0, "[SETUP/5]": 28.0,
        "[SETUP/6]": 33.0, "[SETUP/7]": 37.0, "[SETUP/8]": 41.0,
        "[SETUP/9]": 44.0, "[SETUP/10]": 47.0,
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check setup phase markers
        for marker, pct in setup_markers.items():
            if marker in line:
                current_phase = f"Setup: {line.split(']', 1)[-1].strip() if ']' in line else line}"
                progress_val = pct
                break

        if "[CONCURRENT]" in line:
            progress_val = 50.0
            current_phase = "Fase Concurrente"

        if "Ejecutando fase concurrente" in line:
            progress_val = 55.0

        # Parse elapsed time in concurrent phase
        if "elapsed" not in line.lower() and "⏱️" in line:
            try:
                # Format: "⏱️  30s / 120s | ..."
                parts = line.split("/")
                if len(parts) >= 2:
                    elapsed_str = parts[0].strip().rstrip("s").split()[-1]
                    elapsed = float(elapsed_str)
                    # 55% to 90% during concurrent phase
                    progress_val = 55.0 + (elapsed / 120.0) * 35.0
                    live_details = line
            except (ValueError, IndexError):
                pass

        if "[VALIDATION]" in line:
            progress_val = 90.0
            current_phase = "Validación"

        if "[REPORT]" in line:
            progress_val = 95.0
            current_phase = "Generando Reporte"

        if "completada" in line.lower() and "simulación" in line.lower():
            progress_val = 100.0
            current_phase = "Completada"

    return {
        "progress": round(min(progress_val, 100.0), 1),
        "current_phase": current_phase,
        "live_details": live_details[-200:] if live_details else "",
    }


def _read_chaos_activities() -> dict:
    """Read live activities JSON file written by the chaos runner."""
    if not os.path.exists(CHAOS_ACTIVITIES_PATH):
        return {}
    try:
        with open(CHAOS_ACTIVITIES_PATH, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except Exception:
        return {}


def get_chaos_simulation_status() -> dict:
    """Return current chaos simulation run status."""
    if _chaos_sim_state["running"]:
        prog = _parse_chaos_progress(CHAOS_PROGRESS_PATH)
        activities = _read_chaos_activities()
        return {
            "running": True,
            "started_at": _chaos_sim_state["started_at"],
            "progress": prog["progress"],
            "current_phase": prog["current_phase"],
            "live_details": prog["live_details"],
            "activities": activities.get("activities", {}),
            "counters": activities.get("counters", {}),
            "stats": activities.get("stats", {}),
        }
    else:
        error = _chaos_sim_state.get("error")
        if error:
            return {
                "running": False,
                "started_at": None,
                "progress": 0.0,
                "current_phase": f"Error: {error[:200]}",
                "live_details": "",
                "activities": {},
                "counters": {},
                "stats": {},
            }
        report_exists = os.path.exists(CHAOS_REPORT_PATH)
        # Read last activities even when stopped (for final snapshot)
        activities = _read_chaos_activities()
        return {
            "running": False,
            "started_at": None,
            "progress": 100.0 if report_exists else 0.0,
            "current_phase": "Completada" if report_exists else "No iniciada",
            "live_details": "",
            "activities": activities.get("activities", {}),
            "counters": activities.get("counters", {}),
            "stats": activities.get("stats", {}),
        }


def get_chaos_simulation_report() -> dict:
    """Read and return the chaos simulation report file."""
    from fastapi import HTTPException

    path = CHAOS_REPORT_PATH
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Reporte de caos no encontrado.")
    resolved = pathlib.Path(path).resolve()
    try:
        if not resolved.is_relative_to(pathlib.Path("/app")):
            raise HTTPException(status_code=403, detail="Acceso denegado.")
    except AttributeError:
        # Python < 3.9 fallback
        if not str(resolved).startswith("/app"):
            raise HTTPException(status_code=403, detail="Acceso denegado.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    modified_at = datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()
    return {"content": content, "modified_at": modified_at}


def run_chaos_simulation(params: ChaosRunParams, background_tasks) -> dict:
    """Start a new chaos simulation in the background."""
    from fastapi import HTTPException

    # Validate
    if params.total_players < 1 or params.total_players > 500:
        raise HTTPException(
            status_code=400,
            detail="total_players debe estar entre 1 y 500.",
        )
    if params.duration < 10 or params.duration > 600:
        raise HTTPException(
            status_code=400,
            detail="duration debe estar entre 10 y 600 segundos.",
        )

    with _chaos_sim_lock:
        if _chaos_sim_state["running"]:
            raise HTTPException(
                status_code=409,
                detail="Simulación caótica ya en ejecución. Espera a que termine.",
            )
        _chaos_sim_state.update({
            "running": True,
            "started_at": datetime.utcnow().isoformat(),
            "error": None,
        })
    background_tasks.add_task(_run_chaos_sim_task, params)
    return {"status": "started"}


def _run_chaos_sim_task(params: ChaosRunParams) -> None:
    """Background task that spawns chaos_runner.py as a subprocess."""
    cmd = [
        "python", "-u", "app/scripts/simulation_chaos/chaos_runner.py",
        "--total-players", str(params.total_players),
        "--duration", str(params.duration),
        "--db-url", settings.DATABASE_URL,
    ]
    if params.skip_reset:
        cmd.append("--skip-reset")
    if not params.enable_replay_attack:
        cmd.append("--no-replay")
    if not params.enable_id_spoofing:
        cmd.append("--no-spoof")
    if not params.enable_race_condition:
        cmd.append("--no-race")
    if not params.enable_double_booking:
        cmd.append("--no-booking")
    if not params.enable_boundary_injection:
        cmd.append("--no-injection")
    if not params.enable_cooldown_bypass:
        cmd.append("--no-cooldown")

    try:
        # Clear old progress
        if os.path.exists(CHAOS_PROGRESS_PATH):
            try:
                os.remove(CHAOS_PROGRESS_PATH)
            except Exception:
                pass

        with open(CHAOS_PROGRESS_PATH, "w", encoding="utf-8") as f:
            process = subprocess.Popen(
                cmd, stdout=f, stderr=subprocess.STDOUT, cwd="/app"
            )
            process.wait(timeout=900)  # 15 min max
            if process.returncode != 0:
                try:
                    with open(CHAOS_PROGRESS_PATH, "r", encoding="utf-8", errors="ignore") as rf:
                        tail = rf.read()[-2000:] if os.path.getsize(CHAOS_PROGRESS_PATH) > 0 else ""
                except Exception:
                    tail = ""
                error_msg = f"Chaos sim terminó con código {process.returncode}"
                logger.error(error_msg)
                with _chaos_sim_lock:
                    _chaos_sim_state["error"] = error_msg + ("\n" + tail[-500:] if tail else "")
    except Exception as e:
        logger.error("Chaos simulation task failed: %s", e, exc_info=True)
        with _chaos_sim_lock:
            _chaos_sim_state["error"] = str(e)[:500]
    finally:
        with _chaos_sim_lock:
            _chaos_sim_state.update({"running": False, "started_at": None})


def get_card_distribution(session: Session) -> dict:
    """Get card distribution statistics for the catalog."""
    # 1. Get dynamic rarities map from the database
    dynamic_rarities = get_card_dynamic_rarities(session)

    # 2. Get master list of cards from catalog
    cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
    ).all()

    # 3. Get total circulation, shiny, and first edition for all cards
    circ_stmt = (
        select(
            PlayerInventory.item_id,
            func.sum(PlayerInventory.quantity).label("total_qty"),
            func.sum(
                sa_case(
                    (PlayerInventory.is_shiny == True, PlayerInventory.quantity), else_=0
                )
            ).label("shiny_qty"),
            func.sum(
                sa_case(
                    (PlayerInventory.is_first_edition == True, PlayerInventory.quantity),
                    else_=0,
                )
            ).label("first_ed_qty"),
        )
        .join(ItemCatalog, ItemCatalog.id == PlayerInventory.item_id)
        .where(ItemCatalog.item_type == ItemType.CARD)
        .where(PlayerInventory.user_id != NPC_DID)
        .where(PlayerInventory.quantity > 0)
        .group_by(PlayerInventory.item_id)
    )
    circ_results = session.execute(circ_stmt).all()

    circ_map = {
        row.item_id: {
            "total_qty": int(row.total_qty or 0),
            "shiny_qty": int(row.shiny_qty or 0),
            "first_ed_qty": int(row.first_ed_qty or 0),
        }
        for row in circ_results
    }

    cards_list = []
    total_copies_in_circulation = 0
    total_shiny_in_circulation = 0
    total_first_ed_in_circulation = 0

    catalog_rarity_counts = {
        "Legendaria": 0,
        "Épica": 0,
        "Rara": 0,
        "Poco Común": 0,
        "Común": 0,
    }
    circulation_rarity_counts = {
        "Legendaria": 0,
        "Épica": 0,
        "Rara": 0,
        "Poco Común": 0,
        "Común": 0,
    }

    for c in cards:
        r_info = dynamic_rarities.get(c.id, {"dynamic_rarity": "Común", "circulation": 0})
        dyn_rarity = r_info["dynamic_rarity"]

        stats = circ_map.get(c.id, {"total_qty": 0, "shiny_qty": 0, "first_ed_qty": 0})

        total_copies_in_circulation += stats["total_qty"]
        total_shiny_in_circulation += stats["shiny_qty"]
        total_first_ed_in_circulation += stats["first_ed_qty"]

        catalog_rarity_counts[dyn_rarity] += 1
        circulation_rarity_counts[dyn_rarity] += stats["total_qty"]

        cards_list.append({
            "id": c.id,
            "name": c.name,
            "numero_loteria": (
                c.item_metadata.get("numero_loteria") if c.item_metadata else None
            ),
            "dynamic_rarity": dyn_rarity,
            "total_circulation": stats["total_qty"],
            "shiny_circulation": stats["shiny_qty"],
            "first_edition_circulation": stats["first_ed_qty"],
        })

    # Sort cards by lottery number
    cards_list.sort(key=lambda x: int(x["numero_loteria"] or 999))

    return {
        "total_unique_cards": len(cards),
        "total_copies_in_circulation": total_copies_in_circulation,
        "total_shiny_in_circulation": total_shiny_in_circulation,
        "total_first_edition_in_circulation": total_first_ed_in_circulation,
        "catalog_rarity_distribution": catalog_rarity_counts,
        "circulation_rarity_distribution": circulation_rarity_counts,
        "cards": cards_list,
    }
