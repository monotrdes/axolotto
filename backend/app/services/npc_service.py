"""
npc_service.py — NPC board pool management for CPU game rooms.

Handles seeding and replacement of NPC boards used as opponents in CPU matches.
"""
from sqlmodel import Session, select
from sqlalchemy import func

from app.models.board import PlayerBoard
from app.models.user import User


def _ensure_npc_pool(session: Session, room: str, all_card_ids: list, rng) -> None:
    """Seeds 20 NPC boards for a room if the pool is empty. Uses flush (no commit)."""
    print(f"[NPC] Auto-seeding {room} pool with 20 boards (first game trigger)")
    npc_user = session.exec(select(User).where(User.privy_did == "npc_axolotto_system")).first()
    if not npc_user:
        npc_user = User(privy_did="npc_axolotto_system", nickname="NPC System")
        session.add(npc_user)
        session.flush()
    for i in range(1, 21):
        session.add(PlayerBoard(
            user_id="npc_axolotto_system",
            name=f"Bot {room.capitalize()} #{i}",
            card_ids=rng.sample(all_card_ids, 16),
            card_first_editions=[False] * 16,
            is_npc_pool=True,
            npc_room=room,
            npc_retired=False,
        ))
    session.flush()


def _spawn_npc_replacement(session: Session, room: str, all_card_ids: list, rng) -> None:
    """Creates a replacement NPC board when one graduates to the gashapon pool."""
    print(f"[NPC] Board graduated to gashapon pool. Spawning replacement for {room}")
    npc_user = session.exec(
        select(User).where(User.privy_did == "npc_axolotto_system")
    ).first()
    if not npc_user:
        return
    idx = session.exec(
        select(func.count(PlayerBoard.id))
        .where(PlayerBoard.user_id == npc_user.privy_did)
    ).one()
    new_board = PlayerBoard(
        user_id=npc_user.privy_did,
        name=f"Bot {room.capitalize()} #{idx + 1}",
        card_ids=rng.sample(all_card_ids, 16),
        card_first_editions=[False] * 16,
        is_npc_pool=True,
        npc_room=room,
        npc_retired=False,
    )
    session.add(new_board)
