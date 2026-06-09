"""
phase_01c_daily_rewards.py — Simulación del Ciclo Lunar (recompensas diarias F2P).

Flujo:
  1. Cada bot inicia con streak 0.
  2. Realiza una petición de claim diaria (lunar_streak_service.claim).
  3. Retrocede `user.lunar_last_claim_at` por 25 horas.
  4. Repite claim + retroceso consecutivamente:
     - Bots normales: 3 días (prueba básica de racha)
     - Whales: 7 días (prueba de ciclo completo con cápsulas)
  5. Registra estadísticas de FRJ acumulados y ciclos lunares completados.
"""
import random
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models.user import User
from app.models.economy import Wallet
from app.services.lunar_streak_service import claim as lunar_claim

_rng = random.SystemRandom()


def phase_daily_rewards(engine, config, **state) -> dict:
    """Simula el Ciclo Lunar para todos los bots."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🌙 Simulando Ciclo Lunar (recompensas diarias)...")

    total_frj_earned = 0.0
    total_capsules = 0
    max_luna_reached = 0
    max_streak_reached = 0

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        p_name = personality.get("name", "casual")

        # Determinar cuántos días simular según personalidad
        if p_name in ("whale", "aggressive"):
            n_days = 7  # Ciclo completo: 6 días FRJ + día 7 cápsulas
        elif p_name == "collector":
            n_days = 5  # 5 días de FRJ
        elif p_name == "free2play":
            n_days = 7  # F2P depende de esto — ciclo completo
        else:
            n_days = 3  # Casual: solo 3 días

        user = session.exec(
            select(User).where(User.privy_did == user_id).with_for_update()
        ).first()
        if not user:
            errors.append(f"daily_rewards: user {user_id} not found")
            continue

        frj_earned = 0.0
        capsules_won = 0
        streak_days = 0

        for day in range(1, n_days + 1):
            try:
                # Reset lunar_last_claim_at if not the first day → simulate "yesterday"
                if day > 1:
                    user.lunar_last_claim_at = (
                        user.lunar_last_claim_at - timedelta(hours=25)
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)

                # Claim the daily reward
                res = lunar_claim(db=session, user=user)

                if res.get("type") == "frj":
                    amount = res.get("amount", 0)
                    frj_earned += amount
                    total_frj_earned += amount
                    streak_days = res.get("streak_day", day)
                    print(
                        f"  🌙 {user_id} ({p_name}): Día {streak_days}/{res.get('lunar_week', '?')} "
                        f"— +{amount:.0f} FRJ"
                    )
                elif res.get("type") == "capsule":
                    rolls = res.get("rolls", [])
                    capsules_won += len(rolls)
                    total_capsules += len(rolls)
                    streak_days = 0  # Se resetea tras día 7
                    luna = res.get("lunar_week", "?")
                    print(
                        f"  💊 {user_id} ({p_name}): Día 7 — Luna {luna} "
                        f"— {len(rolls)} cápsula(s) recibida(s)"
                    )
                    if res.get("cycle_complete"):
                        print(f"  🌟 {user_id}: ¡Ciclo Lunar completo!")

                max_luna_reached = max(max_luna_reached, res.get("lunar_week", 0))
                max_streak_reached = max(max_streak_reached, streak_days)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "ya reclamaste" in error_msg.lower():
                    # Ya reclamó hoy — normal en simulación, forzar retroceso y reintentar
                    try:
                        user.lunar_last_claim_at = (
                            user.lunar_last_claim_at - timedelta(hours=25)
                        )
                        session.add(user)
                        session.commit()
                        session.refresh(user)
                        res = lunar_claim(db=session, user=user)
                        if res.get("type") == "frj":
                            frj_earned += res.get("amount", 0)
                            total_frj_earned += res.get("amount", 0)
                            streak_days = res.get("streak_day", 0)
                        elif res.get("type") == "capsule":
                            capsules_won += len(res.get("rolls", []))
                            total_capsules += len(res.get("rolls", []))
                        print(f"  🌙 {user_id} ({p_name}): Reintento exitoso tras retroceso")
                    except Exception as e2:
                        session.rollback()
                        errors.append(f"daily_claim {user_id} day {day}: {e2}")
                else:
                    session.rollback()
                    errors.append(f"daily_claim {user_id} day {day}: {e}")

        print(
            f"  📊 {user_id} ({p_name}): {frj_earned:.0f} FRJ acumulados, "
            f"{capsules_won} cápsulas en {n_days} días simulados"
        )

    stats["daily_claims_total"] = stats.get("daily_claims_total", 0) + n_days * len(players)
    stats["max_lunar_week_reached"] = max_luna_reached
    stats["max_daily_streak_reached"] = max_streak_reached
    stats["daily_frj_earned"] = total_frj_earned
    stats["daily_capsules_won"] = total_capsules

    progress(
        f"  ✅ Ciclo Lunar: {total_frj_earned:.0f} FRJ acumulados, "
        f"{total_capsules} cápsulas, máx Luna {max_luna_reached}"
    )
    return {}
