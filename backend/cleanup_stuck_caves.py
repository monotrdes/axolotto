"""
cleanup_stuck_caves.py — Limpia expansiones de Cenote atrapadas.

Ejecutar desde la carpeta backend/:
    python cleanup_stuck_caves.py

Si usas SQLite (local):    python cleanup_stuck_caves.py
Si usas PostgreSQL (Docker): python cleanup_stuck_caves.py --pg
"""
import sys
from sqlmodel import Session, select, text
from app.database import engine
from app.models.user import User
from app.models.economy import Wallet

def main():
    dry_run = "--dry-run" in sys.argv
    use_pg = "--pg" in sys.argv

    # Si se fuerza PostgreSQL, reemplazar engine temporalmente
    if use_pg:
        from sqlmodel import create_engine
        pg_url = "postgresql://axolotto_admin:una_contraseña_super_perrona_y_larga@127.0.0.1:5433/axolotto_app_db"
        eng = create_engine(pg_url, echo=False)
    else:
        eng = engine

    with Session(eng) as session:
        # ── 1. Encontrar usuarios atrapados ──
        stuck = session.exec(
            select(User).where(
                User.cave_expansion_target_level.is_not(None),
                User.cave_expansion_started_at.is_not(None),
            )
        ).all()

        if not stuck:
            print("✅ No hay usuarios con excavaciones atrapadas.")
            return

        print(f"🔍 {len(stuck)} usuario(s) con excavación atrapada:\n")
        for u in stuck:
            target = u.cave_expansion_target_level
            started = u.cave_expansion_started_at
            current = u.cave_level
            nickname = u.nickname or u.privy_did[:20]
            print(f"  🧑 {nickname}")
            print(f"     Nivel actual: {current} → Target atrapado: {target}")
            print(f"     Iniciado: {started}")

            if dry_run:
                continue

            # ── 2. Reembolsar FRJ ──
            from app.api.v1.endpoints.cave_expansion import CAVE_LEVEL_DEFINITIONS
            level_def = CAVE_LEVEL_DEFINITIONS.get(target, {})
            frj_cost = level_def.get("cost_frj", 0)
            is_vip = u.is_vip
            frj_refund = int(frj_cost * 0.5) if is_vip else frj_cost

            wallet = session.exec(
                select(Wallet).where(Wallet.user_id == u.privy_did)
            ).first()
            if wallet and frj_refund > 0:
                wallet.frijolitos = (wallet.frijolitos or 0) + frj_refund
                session.add(wallet)
                print(f"     💧 Reembolsado: {frj_refund} FRJ{' (VIP -50%)' if is_vip else ''}")

            # ── 3. Avanzar el nivel (la excavación ya terminó su timer) ──
            # Si el timer ya expiró, completamos la expansión
            from datetime import datetime, timedelta
            elapsed = datetime.utcnow() - started
            total_hours = level_def.get("excavation_hours", 24)
            if elapsed >= timedelta(hours=total_hours):
                u.cave_level = target
                u.webito_slots_unlocked = target
                print(f"     ⛏️  Nivel avanzado a {target} (timer expirado: {elapsed.total_seconds()/3600:.1f}h ≥ {total_hours}h)")

            # ── 4. Limpiar estado de expansión ──
            u.cave_expansion_target_level = None
            u.cave_expansion_started_at = None
            session.add(u)

        if not dry_run:
            session.commit()
            print(f"\n✅ {len(stuck)} usuario(s) limpiados.")
        else:
            print(f"\n🔍 Modo dry-run. Usa sin --dry-run para aplicar los cambios.")

if __name__ == "__main__":
    main()
