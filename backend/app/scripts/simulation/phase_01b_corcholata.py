"""
phase_01b_corcholata.py — Cada jugador canjea un código promocional (corcholata).

Flujo real:
  1. Jugador ingresa código PromoCode (simulado aquí)
  2. Se crea PendingReward (hold hasta completar tutorial)
  3. Después del tutorial, se llama POST /rewards/claim
  4. Se entregan axofichas + frijolitos al wallet

Esta fase crea un PromoCode ÚNICO por jugador y lo canjea inmediatamente.
Pasos 3-4 ocurren en phase_04_incubation.py después de completar el tutorial.
"""
import secrets

from sqlmodel import Session
from fastapi import HTTPException

from app.models.promo import PromoCode
from app.core.config import settings
from app.services.promo_service import redeem_promo_code


def _create_unique_code(session: Session, player_index: int) -> PromoCode:
    """Crea un PromoCode único para un jugador simulado."""
    suffix = secrets.token_hex(4).upper()
    code = f"SIM-{player_index:03d}-{suffix}"

    promo = PromoCode(
        code=code,
        batch="simulation",
        reward_type="starter_pack",
        reward_axofichas=settings.DEV_AUTO_REWARD_AXF,
        reward_frijolitos=settings.DEV_AUTO_REWARD_FRJ,
        reward_item_id=None,
    )
    session.add(promo)
    session.commit()
    return promo


def phase_redeem_corcholata(engine, config, **state) -> dict:
    """
    Para cada jugador, crea un PromoCode único y lo canjea.
    Esto crea un PendingReward por jugador (NO entrega recursos inmediatos).
    """
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🎟️  Creando y canjeando corcholata única para cada jugador...")

    redeemed = 0
    for i, p in enumerate(players):
        user_id = p["user_id"]
        email = p.get("email", f"sim_{user_id.split(':')[-1]}@example.com")

        try:
            # Crear código único para este jugador
            promo = _create_unique_code(session, i + 1)

            # Canjearlo
            result = redeem_promo_code(
                session=session,
                user_id=user_id,
                code=promo.code,
                email=email,
            )
            redeemed += 1
            preview = result.get("reward_preview", {})
            progress(
                f"    🎟️  {user_id}: código {promo.code} → PendingReward "
                f"(AXF:{preview.get('axofichas', 0):.0f} FRJ:{preview.get('frijolitos', 0):.0f})"
            )
        except HTTPException as e:
            if "Ya canjeaste" in str(e.detail) or "ya fue canjeado" in str(e.detail):
                progress(f"    ℹ️  {user_id}: Ya tenía corcholata canjeada (run previa)")
            elif "superado" in str(e.detail).lower():
                errors.append(f"corcholata_attempts_exceeded {user_id}: {e.detail}")
            elif "correo" in str(e.detail).lower():
                errors.append(f"corcholata_no_email {user_id}: {e.detail}")
            else:
                errors.append(f"corcholata {user_id}: {e.detail}")
        except Exception as e:
            errors.append(f"corcholata_unexpected {user_id}: {e}")
            session.rollback()

    stats["corcholatas_redeemed"] = redeemed
    progress(f"  ✅ Corcholatas canjeadas: {redeemed}/{len(players)}")
    return {}
