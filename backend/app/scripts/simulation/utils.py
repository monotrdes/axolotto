"""
Utility helpers shared across simulation phases.
"""
from datetime import datetime
from sqlmodel import Session, select

from app.models.axolotito import Axolotito
from app.models.lobby_models import GameRoom, RoomRegistration, MultiplayerGameLog, JackpotVault, JackpotWin
from app.models.items import WebitoIncubation
from app.services.multiplayer_service import MultiplayerService
from app.core.config import frj_to_display
from fastapi import HTTPException

import time
from datetime import timedelta


def _make_bar(pct: float, width: int = 22) -> str:
    """Barra de progreso ASCII: [████████░░░░░░░░] 42%"""
    filled = int(width * min(pct, 100) / 100)
    return "█" * filled + "░" * (width - filled)


def _interact_eggs(session: Session, user_id: str, incubation_time_s: int) -> None:
    """
    Espera a que los huevos estén listos para eclosionar.
    El sistema de calor/congelado/cuidado fue retirado: los huevos eclosionan
    únicamente por tiempo (imprinting), así que solo esperamos el período.
    """
    wait_s = max(1, incubation_time_s)
    print(f"    ⏳ Esperando {wait_s}s mientras incuban los huevos...")
    time.sleep(wait_s)


def _trigger_waiting_rooms(session: Session, stats: dict, errors: list, round_num: int) -> None:
    """Arranca todas las salas 'waiting' con inscripciones. El scheduler de
    producción (cada 10s) puede haber arrancado algunas — no pasa nada,
    _read_new_logs recolecta los resultados de cualquier sala ya procesada."""
    session.expire_all()
    waiting_rooms = session.exec(
        select(GameRoom).where(GameRoom.status == "waiting")
    ).all()
    for room in waiting_rooms:
        regs = session.exec(
            select(RoomRegistration).where(RoomRegistration.room_id == room.id)
        ).all()
        if not regs:
            continue
        room.status = "playing"
        session.add(room)
        session.commit()
        n_boards = sum(1 for r in regs)
        print(f"  🎮 Ronda {round_num} — '{room.name}' ({n_boards} axo(s)) ▶️ iniciando...")
        try:
            MultiplayerService.simulate_multiplayer_match(room.id)
            session.expire_all()
            stats["multi_rooms_simulated"] = stats.get("multi_rooms_simulated", 0) + 1
        except Exception as e:
            session.rollback()
            errors.append(f"multi_simulate room {room.id} ronda {round_num}: {e}")


def _read_new_logs(
    session: Session,
    registered: dict,
    all_logs: list,
) -> None:
    """Lee MultiplayerGameLog no notificados. Primero por user_id de los axos
    registrados vía el sim, luego un barrido de cualquier log huérfano (salas
    que arrancó el scheduler antes de que el sim las tocara)."""
    seen_ids: set[int] = set()

    # Pass 1: logs de los axolotitos que el sim registró
    for axo_id, info in registered.items():
        user_id = info["user_id"]
        new_logs = session.exec(
            select(MultiplayerGameLog)
            .where(MultiplayerGameLog.user_id == user_id)
            .where(MultiplayerGameLog.notified == False)  # noqa: E712
            .order_by(MultiplayerGameLog.created_at.asc())
        ).all()
        for log in new_logs:
            seen_ids.add(log.id)
            icon = "🏆" if log.outcome == "Victoria" else "💔"
            net_display = frj_to_display(log.net_gal)
            print(f"    {icon} {log.axo_name:<22} │ {log.room_name:<26} │ "
                  f"Neto: {net_display:+7.1f} FRJ │ XP: +{log.xp_gained}")
            all_logs.append({
                "user_id": user_id,
                "axo_name": log.axo_name,
                "room_name": log.room_name,
                "outcome": log.outcome,
                "net_gal": net_display,
                "xp_gained": log.xp_gained,
            })
            log.notified = True
            session.add(log)
        session.commit()

    # Pass 2: cualquier log huérfano (salas arrancadas por el scheduler)
    orphan_logs = session.exec(
        select(MultiplayerGameLog)
        .where(MultiplayerGameLog.notified == False)  # noqa: E712
        .order_by(MultiplayerGameLog.created_at.asc())
    ).all()
    for log in orphan_logs:
        if log.id in seen_ids:
            continue
        icon = "🏆" if log.outcome == "Victoria" else "💔"
        net_display = frj_to_display(log.net_gal)
        print(f"    {icon} {log.axo_name:<22} │ {log.room_name:<26} │ "
              f"Neto: {net_display:+7.1f} FRJ │ XP: +{log.xp_gained}")
        all_logs.append({
            "user_id": log.user_id,
            "axo_name": log.axo_name,
            "room_name": log.room_name,
            "outcome": log.outcome,
            "net_gal": net_display,
            "xp_gained": log.xp_gained,
        })
        log.notified = True
        session.add(log)
    if orphan_logs:
        session.commit()


def expect_error(label: str, expected_code: int, fn, session: Session, errors_log: list, counter: dict) -> None:
    """
    Ejecuta fn() esperando un HTTPException con el código dado.
    counter debe tener keys "passed" y "failed" (int).
    """
    try:
        fn()
        # Si llegamos aquí, no hubo error — FALLO
        print(f"  ❌ ERROR TEST '{label}': esperaba {expected_code}, pero NO lanzó excepción")
        errors_log.append(f"error_test_missing_{label}")
        counter["failed"] += 1
    except HTTPException as e:
        if e.status_code == expected_code:
            print(f"  ✅ [{expected_code}] {label}: '{e.detail[:60]}'")
            counter["passed"] += 1
        else:
            print(f"  ⚠️  ERROR TEST '{label}': esperaba {expected_code}, obtuvo {e.status_code}")
            errors_log.append(f"error_test_wrong_code_{label}_{e.status_code}")
            counter["failed"] += 1
    except Exception as e:
        # Error inesperado (no HTTP) — contar como fallo de test pero no de servidor
        print(f"  ⚠️  ERROR TEST '{label}': excepción no-HTTP: {type(e).__name__}: {str(e)[:60]}")
        counter["failed"] += 1
    finally:
        try:
            session.rollback()
        except Exception:
            pass
