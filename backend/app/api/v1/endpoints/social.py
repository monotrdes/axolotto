"""Social API endpoints — friends, likes, cave visits.

Phase 1 (task-1780974961-58): Friend CRUD + likes + search + cave visits.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Optional

from sqlmodel import Session, select

from app.database import get_session
from app.core.auth import get_verified_user_id
from app.core.limiter import limiter
from app.services.social_service import SocialService

router = APIRouter()


# ── Request Schemas ─────────────────────────────────────────────────────────

class FriendRequest(BaseModel):
    target_user_id: str


class BlockRequest(BaseModel):
    user_id: str


# ── Friend CRUD ─────────────────────────────────────────────────────────────

@router.get("/friends")
def list_friends(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """List all friends with online status, sorted by relevance."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    return SocialService.get_friends_list(session, verified_user_id)


@router.get("/friends/top")
def top_friends(
    limit: int = Query(default=4, ge=1, le=10),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Top N friends for ZonaInferior shortcut bar."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    return SocialService.get_top_active_friends(session, verified_user_id, limit)


@router.post("/friends/request", status_code=201)
def send_friend_request(
    req: FriendRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Send a friend request."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    relation = SocialService.send_friend_request(session, verified_user_id, req.target_user_id)
    return {
        "message": "Solicitud enviada.",
        "relation_id": relation.id,
        "status": relation.status.value,
    }


@router.post("/friends/accept/{request_id}")
def accept_friend_request(
    request_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Accept a pending friend request."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    relation = SocialService.accept_friend_request(session, verified_user_id, request_id)
    return {
        "message": "¡Ahora son amigos! 🦎",
        "relation_id": relation.id,
        "friend_id": relation.user_a,
        "friends_since": relation.friends_since.isoformat() if relation.friends_since else None,
    }


@router.post("/friends/reject/{request_id}")
def reject_friend_request(
    request_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Reject a pending friend request."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    SocialService.reject_friend_request(session, verified_user_id, request_id)
    return {"message": "Solicitud rechazada."}


@router.delete("/friends/{relation_id}")
def remove_friend(
    relation_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Remove a friend."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    SocialService.remove_friend(session, verified_user_id, relation_id)
    return {"message": "Amigo eliminado."}


@router.post("/friends/block")
def block_user(
    req: BlockRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Block a user."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    SocialService.block_user(session, verified_user_id, req.user_id)
    return {"message": "Usuario bloqueado."}


@router.get("/friends/pending")
def pending_requests(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Get incoming pending friend requests."""
    return SocialService.get_pending_requests(session, verified_user_id)


@router.get("/friends/sent")
def sent_requests(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Get sent friend requests still pending."""
    return SocialService.get_sent_requests(session, verified_user_id)


# ── Search & Discovery ──────────────────────────────────────────────────────

@router.get("/friends/search")
def search_players(
    q: str = Query(..., min_length=2, description="Nickname search query"),
    limit: int = Query(default=20, ge=1, le=50),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Search players by nickname."""
    return SocialService.search_players(session, q, verified_user_id, limit)


@router.get("/friends/recent-players")
def recent_players(
    limit: int = Query(default=10, ge=1, le=30),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Players from recent public rooms (not yet friends)."""
    return SocialService.get_recent_players(session, verified_user_id, limit)


@router.get("/friends/suggestions")
def friend_suggestions(
    limit: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> list[dict]:
    """Suggested players: friends of friends (mutual connections)."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    return SocialService.get_suggestions(session, verified_user_id, limit)


# ── Social Actions ──────────────────────────────────────────────────────────

@router.post("/like/{target_user_id}")
def like_friend(
    target_user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Give a like to a friend. +1 FRJ for both."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    return SocialService.process_like(session, verified_user_id, target_user_id)


@router.post("/visit/{friend_id}")
def visit_friend_cave(
    friend_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Visit a friend's cave. Returns public cave data."""
    from app.models.user import User
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)
    return SocialService.visit_cave(session, verified_user_id, friend_id)


@router.get("/friends/{friend_id}/cave")
def get_friend_cave(
    friend_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
) -> dict:
    """Get friend's cave data without counting a visit (read-only)."""
    from app.models.user import User
    from app.services.social_service import SocialService
    from app.core.auth import require_tutorial
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if user: require_tutorial(user)

    # Verify friendship
    if not SocialService.are_friends(session, verified_user_id, friend_id):
        raise HTTPException(status_code=403, detail="Solo puedes ver la cueva de tus amigos.")

    friend = session.exec(select(User).where(User.privy_did == friend_id)).first()
    if not friend:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return {
        "friend_id": friend_id,
        "nickname": friend.nickname,
        "cave_name": friend.cave_name,
        "cave_level": friend.cave_level,
        "cave_decorations": friend.cave_decorations,
        "vip_tier": friend.vip_tier,
        "avatar_url": friend.avatar_url or "",
    }
