from sqlmodel import Session, select
from fastapi import HTTPException

from app.api.v1.endpoints.shop import (
    roll_gashapon, claim_daily_capsule, roll_capsule, roll_triple_suerte,
    GashaponRollRequest, CapsuleRollRequest, TripleSuerteRequest,
)


def phase_gashapon(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🎰 Jugando gashapon y cápsulas...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]

        # — Gashapon estándar —
        for roll_i in range(personality.get("gashapon_rolls", 1)):
            try:
                res = roll_gashapon(
                    request=GashaponRollRequest(user_id=user_id),
                    session=session,
                    verified_user_id=user_id,
                )
                prize = res.get("item_name") or res.get("prize") or res.get("resultado", "?")
                print(f"  🎰 {user_id} roll #{roll_i+1}: {prize}")
                stats["gashapon_rolls"] = stats.get("gashapon_rolls", 0) + 1
            except HTTPException as e:
                errors.append(f"gashapon {user_id}: {e.detail}")

        # — Cápsula diaria —
        try:
            res = claim_daily_capsule(session=session, verified_user_id=user_id)
            prize = res.get("item_name") or res.get("resultado", "?")
            print(f"  💊 {user_id}: cápsula diaria → {prize}")
            stats["capsule_claims"] = stats.get("capsule_claims", 0) + 1
        except HTTPException as e:
            if e.status_code in (400, 409):
                print(f"  ℹ️  {user_id}: cápsula diaria ya reclamada hoy ({e.detail})")
            else:
                errors.append(f"capsule {user_id}: {e.detail}")

        # — Cápsulas de Tier extra (Bronce=1, etc. — todas cuestan FRJ ahora) —
        tier = "bronce"
        try:
            res = roll_capsule(
                request=CapsuleRollRequest(tier=tier),
                session=session,
                verified_user_id=user_id,
            )
            print(f"  💊 {user_id}: cápsula {tier} → {res.get('item_name', '?')}")
        except HTTPException as e:
            errors.append(f"capsule_roll {user_id}: {e.detail}")

        # — Triple Suerte (solo personalidades que la tienen) —
        if personality.get("does_triple_suerte"):
            try:
                res = roll_triple_suerte(
                    request=TripleSuerteRequest(),
                    session=session,
                    verified_user_id=user_id
                )
                prizes = [r.get("item_name", "?") for r in res.get("results", [])]
                print(f"  🌟 {user_id}: Triple Suerte → {prizes}")
                stats["triple_suerte"] = stats.get("triple_suerte", 0) + 1
            except HTTPException as e:
                errors.append(f"triple_suerte {user_id}: {e.detail}")

    progress(f"  ✅ Gashapon: {stats.get('gashapon_rolls', 0)} rolls, "
             f"{stats.get('capsule_claims', 0)} cápsulas.")
    return {}
