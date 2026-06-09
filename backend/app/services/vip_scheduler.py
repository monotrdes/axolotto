"""
Scheduler VIP: corre en background (asyncio loop), cada hora.
- Expira GAL pendiente que no se reclamó antes de la media noche UTC (use-it-or-lose-it).
- Genera nuevo GAL pendiente para VIPs activos (una vez por día MX, reemplaza el lote anterior).
- Congela slots de Board/Axolotito cuando el VIP expira.
"""
import asyncio
import json
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.core.config import VIP_CONFIG
from app.database import engine
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.economy import CurrencyType, TransactionLedger, TransactionType, Wallet
from app.models.user import User


async def vip_scheduler_loop():
    while True:
        await asyncio.sleep(3600)  # cada hora
        try:
            _run_vip_jobs()
        except Exception as e:
            print(f"[VIP Scheduler] Error: {e}")


def _run_vip_jobs():
    mx_tz = timezone(timedelta(hours=-6))
    now_mx = datetime.now(timezone.utc).astimezone(mx_tz)
    now = datetime.utcnow()

    # --- Secciones 1-3: GAL generation, expiry, freeze (bulk, sin movimiento de dinero) ---
    with Session(engine) as session:
        all_users = session.exec(select(User)).all()

        for user in all_users:
            changed = False

            # --- 1. Congelar boards/axolotitos si el VIP expiró ---
            if user.vip_tier and not user.is_vip:
                _apply_slot_freeze(session, user)
                user.vip_tier = None
                changed = True

            # Solo procesar GAL para VIPs activos
            if not user.is_vip or not user.vip_tier:
                if changed:
                    session.add(user)
                continue

            config = VIP_CONFIG.get(user.vip_tier)
            if not config:
                continue

            gal_amount = float(config["gal_daily"])

            # --- 2. Expirar lote de GAL si ha pasado la fecha de expiración (final del día UTC) ---
            if user.vip_pending_gal > 0 and user.vip_pending_gal_expires_at and now >= user.vip_pending_gal_expires_at:
                expired_amount = user.vip_pending_gal
                user.vip_pending_gal = 0.0
                user.vip_pending_gal_expires_at = None
                ledger_exp = TransactionLedger(
                    user_id=user.privy_did,
                    amount=expired_amount,
                    currency=CurrencyType.GEMA_ALGA,
                    tx_type=TransactionType.VIP_GAL_EXPIRED,
                    description=f"GAL VIP expirado sin reclamar ({user.vip_tier})"
                )
                session.add(ledger_exp)
                changed = True

            # --- 3. Generar nuevo GAL pendiente (USE IT OR LOSE IT) ---
            # Se genera una sola vez por día en horario de Xochimilco.
            # Si el usuario no reclama antes de la media noche UTC, el GAL expira.
            already_generated_today = False
            if user.vip_last_daily_gal_at:
                last_gal_mx = user.vip_last_daily_gal_at.replace(tzinfo=timezone.utc).astimezone(mx_tz)
                if last_gal_mx.date() == now_mx.date():
                    already_generated_today = True

            if not already_generated_today:
                # Si aún hay GAL pendiente (el scheduler no corrió justo a media noche),
                # expirarlo antes de generar el nuevo día.
                if user.vip_pending_gal > 0:
                    expired_amount = user.vip_pending_gal
                    user.vip_pending_gal = 0.0
                    user.vip_pending_gal_expires_at = None
                    ledger_exp = TransactionLedger(
                        user_id=user.privy_did,
                        amount=expired_amount,
                        currency=CurrencyType.GEMA_ALGA,
                        tx_type=TransactionType.VIP_GAL_EXPIRED,
                        description=f"GAL VIP expirado sin reclamar ({user.vip_tier})"
                    )
                    session.add(ledger_exp)

                # Asignar nuevo GAL del día (reemplazar, NO acumular)
                user.vip_pending_gal = gal_amount
                user.vip_pending_gal_expires_at = datetime(now.year, now.month, now.day, 23, 59, 59)
                user.vip_last_daily_gal_at = now
                changed = True

            if changed:
                session.add(user)

        session.commit()

    # --- Sección 4: Auto-renovación — sesión individual por usuario para atomicidad ---
    # Obtener candidatos (lectura ligera, sin lock)
    with Session(engine) as session:
        candidate_ids = list(session.exec(
            select(User.privy_did)
            .where(User.vip_auto_renew == True)
            .where(User.vip_expires_at != None)
        ).all())

    for privy_did in candidate_ids:
        _auto_renew_user(privy_did, now)

    print(f"[VIP Scheduler] Ciclo completado. {now.strftime('%Y-%m-%d %H:%M')} UTC")


def _auto_renew_user(privy_did: str, now: datetime) -> None:
    """Renueva VIP de un usuario en su propia sesión con row locks en User y Wallet.
    Si falla a mitad, el rollback automático garantiza que no se descuente AXG sin extender el VIP."""
    try:
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.privy_did == privy_did).with_for_update()
            ).first()
            if not user or not user.vip_auto_renew or not user.is_vip or not user.vip_tier:
                return
            days_left = (user.vip_expires_at - now).days
            if not (1 <= days_left <= 3):
                return
            price = VIP_CONFIG.get(user.vip_tier, {}).get("price_axg", 0)
            wallet = session.exec(
                select(Wallet).where(Wallet.user_id == privy_did).with_for_update()
            ).first()
            if wallet and wallet.axofichas >= price:
                wallet.axofichas -= price
                user.vip_expires_at += timedelta(days=30)
                user.vip_streak_months += 1
                user.vip_streak_last_renewed = now
                ledger = TransactionLedger(
                    user_id=privy_did, amount=price,
                    currency=CurrencyType.AXOGEMA, tx_type=TransactionType.MARKET_BUY,
                    description=f"Auto-renovación VIP {user.vip_tier} (30 días)"
                )
                session.add_all([wallet, user, ledger])
                session.commit()
                print(f"[VIP Scheduler] Auto-renovación OK: {privy_did[-8:]} tier={user.vip_tier}")
            else:
                user.vip_auto_renew = False
                session.add(user)
                session.commit()
                print(f"[VIP Scheduler] Auto-renovación fallida (saldo insuficiente): {privy_did[-8:]}")
    except Exception as e:
        print(f"[VIP Scheduler] Auto-renovación error para {privy_did[-8:]}: {e}")


def _apply_slot_freeze(session: Session, user: User):
    base_table_slots = user.unlocked_board_slots  # slots base sin VIP
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.user_id == user.privy_did)
        .where(PlayerBoard.is_dead == False)
        .order_by(PlayerBoard.created_at.desc())
    ).all()

    for i, board in enumerate(boards):
        should_freeze = i >= base_table_slots
        if board.is_frozen_by_vip != should_freeze:
            board.is_frozen_by_vip = should_freeze
            session.add(board)

    # Axolotitos — solo aplica si era Axolite (slot extra = 1)
    if user.vip_tier == "axolite":
        base_axo_limit = user.cave_level
        axolotitos = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user.privy_did)
            .order_by(Axolotito.created_at.desc())
        ).all()
        
        main_frozen = False
        for i, axo in enumerate(axolotitos):
            should_freeze = i >= base_axo_limit
            if axo.is_frozen_by_vip != should_freeze:
                axo.is_frozen_by_vip = should_freeze
                if should_freeze and axo.is_main:
                    axo.is_main = False
                    main_frozen = True
                session.add(axo)

        # Lógica de auto-reemplazo: Si el Axolotito Principal se congeló,
        # auto-asignar el siguiente axolotito más antiguo y activo (descongelado) como principal.
        if main_frozen:
            next_main = session.exec(
                select(Axolotito)
                .where(Axolotito.user_id == user.privy_did)
                .where(Axolotito.is_frozen_by_vip == False)
                .order_by(Axolotito.created_at.asc())
            ).first()
            if next_main:
                next_main.is_main = True
                session.add(next_main)
