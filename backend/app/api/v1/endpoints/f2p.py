"""
f2p.py — Endpoints de economía F2P: huevo durmiente y micro-recompensas.

Routes:
  GET  /api/v1/f2p/egg-status        → Estado actual del huevo durmiente
  POST /api/v1/f2p/watch-reward      → Acredita GAL y fragmentos por ver una partida
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
    Wallet,
)
from app.models.user import User
from app.services.bank_service import BankService
from app.core.config import frj_to_internal, frj_to_display, settings
from app.core.product_policy import require_feature
from app.services.f2p_service import F2PService

router = APIRouter()
_f2p = F2PService()


# ---------------------------------------------------------------------------
# GET /egg-status
# ---------------------------------------------------------------------------

@router.get("/egg-status")
def get_egg_status(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Devuelve el estado actual del huevo durmiente del jugador F2P."""
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Leer fragmentos desde el modelo User (añadido por Agente A)
    fragments: int = getattr(user, "f2p_astral_fragments", 0) or 0
    stage = _f2p.egg_reaction_stage(fragments)
    bubble = _f2p.get_dream_bubble(fragments)

    return {
        "fragments": fragments,
        "fragments_needed": _f2p.FRAGMENTS_TO_HATCH,
        "reaction_stage": stage,
        "dream_bubble": bubble,
        "ready_to_hatch": fragments >= _f2p.FRAGMENTS_TO_HATCH,
    }


# ---------------------------------------------------------------------------
# POST /watch-reward
# ---------------------------------------------------------------------------

@router.post("/watch-reward")
def watch_reward(
    won: bool = False,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Acredita FRJ y Fragmentos Astrales al jugador F2P por ver una partida.

    Query param:
      won (bool, default False) — True si el jugador ganó la tabla espejo.

    Aplica el tope diario de FRJ (10 FRJ/día). Los fragmentos siempre se acumulan.
    Resetea el contador diario cada 24 h a partir del último reset.
    """
    require_feature(
        settings.ENABLE_CLIENT_REPORTED_REWARDS,
        "client_reported_rewards",
    )

    # --- Cargar usuario con lock pesimista para evitar race en contadores diarios ---
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id).with_for_update()
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # --- Verificar / resetear cap diario ---
    reset_at: datetime | None = getattr(user, "f2p_daily_gal_reset_at", None)
    earned_today: float = frj_to_display(getattr(user, "f2p_daily_gal_earned", 0) or 0)
    frags_earned_today: int = getattr(user, "f2p_daily_frags_earned", 0) or 0

    now = datetime.utcnow()
    if reset_at is None or now >= reset_at:
        # Nuevo ciclo de 24 h
        earned_today = 0.0
        frags_earned_today = 0
        try:
            user.f2p_daily_gal_reset_at = now + timedelta(hours=24)
            user.f2p_daily_gal_earned = 0
            user.f2p_daily_frags_earned = 0
        except AttributeError:
            pass

    # --- Calcular recompensas base ---
    reward = _f2p.watch_game_reward(won)
    raw_frj: float = reward["frj"]
    frags: int = reward["fragments"]

    # --- Aplicar tope diario ---
    capped = False
    frj_to_credit: float = raw_frj

    if not _f2p.under_daily_cap(earned_today):
        # Ya superó el límite — fragmentos sí se acreditan, FRJ no
        frj_to_credit = 0.0
        capped = True
    else:
        # Puede quedar poco espacio
        remaining = _f2p.DAILY_CAP_FRJ - earned_today
        if frj_to_credit > remaining:
            frj_to_credit = remaining
            capped = True

    # --- Acreditar FRJ en wallet ---
    if frj_to_credit > 0:
        wallet: Wallet = BankService.get_or_create_wallet(
            session, verified_user_id, for_update=True
        )
        wallet.frijolitos += frj_to_internal(frj_to_credit)
        wallet.last_updated = now
        session.add(wallet)

        # Ledger
        ledger_entry = TransactionLedger(
            user_id=verified_user_id,
            amount=frj_to_internal(frj_to_credit),
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.F2P_REWARD,
            description=f"Recompensa F2P por ver partida ({'ganó' if won else 'observó'})",
        )
        session.add(ledger_entry)

        # Actualizar contador diario
        try:
            user.f2p_daily_gal_earned = frj_to_internal(earned_today + frj_to_credit)
        except AttributeError:
            pass

    # --- Acreditar fragmentos (cap diario) ---
    fragments_before: int = getattr(user, "f2p_astral_fragments", 0) or 0
    frags_remaining_today = max(0, _f2p.DAILY_CAP_FRAGS - frags_earned_today)
    frags_to_credit = min(frags, frags_remaining_today)
    try:
        user.f2p_astral_fragments = fragments_before + frags_to_credit
        user.f2p_daily_frags_earned = frags_earned_today + frags_to_credit
    except AttributeError:
        frags_to_credit = frags

    session.add(user)
    session.commit()

    # --- Calcular estado final del huevo ---
    total_fragments: int = getattr(user, "f2p_astral_fragments", fragments_before + frags_to_credit) or 0
    stage = _f2p.egg_reaction_stage(total_fragments)
    bubble = _f2p.get_dream_bubble(total_fragments)

    frags_cap_reached = frags_to_credit < frags

    response: dict = {
        "capped": capped,
        "frags_capped": frags_cap_reached,
        "gal_earned": round(frj_to_credit, 4),
        "frj_earned": round(frj_to_credit, 4),
        "fragments_added": frags_to_credit,
        "total_fragments": total_fragments,
        "egg_reaction_stage": stage,
        "dream_bubble": bubble,
    }

    if capped:
        response["message"] = (
            "Tu pozo de Frijolitos diario se ha agotado. "
            "¡Adopta tu Webito para ganancias ilimitadas!"
        )
    if frags_cap_reached and not capped:
        response["message"] = (
            "Has alcanzado el límite diario de Fragmentos Astrales. "
            "¡Vuelve mañana para seguir acumulando!"
        )

    return response
