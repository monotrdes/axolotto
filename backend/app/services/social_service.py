"""Social service — friend graph, actions, and cave visits.

Phase 1 (task-1780974961-58): Core friend management + likes + search.
Phase 2 (task-1780974969-59): Referral codes and tracking (to be added).
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select, or_, and_
from fastapi import HTTPException

from app.core.config import settings
from app.models.social import (
    FriendRelation,
    FriendStatus,
    SocialActionLog,
    SocialActionType,
)
from app.models.user import User

# ── Limits ──────────────────────────────────────────────────────────────────

MAX_FRIENDS = 100
MAX_PENDING_SENT = 20
MAX_PENDING_REQUESTS_PER_HOUR = 10
MAX_LIKES_PER_FRIEND_PER_DAY = 1
MAX_DAILY_SOCIAL_REWARD = 5  # FRJ per social action (likes)


class SocialService:

    # ── Friend Requests ──────────────────────────────────────────────────

    @staticmethod
    def send_friend_request(
        session: Session, sender_id: str, target_id: str
    ) -> FriendRelation:
        """Send a friend request from sender to target."""
        if sender_id == target_id:
            raise HTTPException(status_code=400, detail="No puedes agregarte a ti mismo.")

        # Verify target exists
        target = session.exec(select(User).where(User.privy_did == target_id)).first()
        if not target:
            raise HTTPException(status_code=404, detail="Jugador no encontrado.")

        # Check current friend count
        active_friends = SocialService._count_active_friends(session, sender_id)
        if active_friends >= MAX_FRIENDS:
            raise HTTPException(
                status_code=400,
                detail=f"Has alcanzado el límite de {MAX_FRIENDS} amigos.",
            )

        # Check pending sent count
        pending_sent = SocialService._count_pending_sent(session, sender_id)
        if pending_sent >= MAX_PENDING_SENT:
            raise HTTPException(
                status_code=400,
                detail=f"Tienes {MAX_PENDING_SENT} solicitudes pendientes. Espera a que respondan.",
            )

        # Check if relation already exists
        existing = SocialService._find_relation(session, sender_id, target_id)
        if existing:
            if existing.status == FriendStatus.ACTIVE:
                raise HTTPException(status_code=400, detail="Ya son amigos.")
            if existing.status == FriendStatus.PENDING:
                if existing.user_a == sender_id:
                    raise HTTPException(
                        status_code=400, detail="Ya enviaste una solicitud a este jugador."
                    )
                else:
                    # The other user already sent a request — auto-accept
                    existing.status = FriendStatus.ACTIVE
                    existing.friends_since = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                    session.add(existing)
                    session.commit()
                    session.refresh(existing)
                    return existing
            if existing.status == FriendStatus.BLOCKED:
                raise HTTPException(status_code=400, detail="No puedes agregar a este jugador.")

        # Rate-limit by hour
        SocialService._check_hourly_rate_limit(session, sender_id)

        relation = FriendRelation(
            user_a=sender_id,
            user_b=target_id,
            status=FriendStatus.PENDING,
        )
        session.add(relation)

        # Log the action
        SocialService._log_action(session, sender_id, target_id, SocialActionType.FRIEND_REQUEST_SENT)

        session.commit()
        session.refresh(relation)
        return relation

    @staticmethod
    def accept_friend_request(
        session: Session, user_id: str, request_id: int
    ) -> FriendRelation:
        """Accept a pending friend request."""
        relation = session.exec(
            select(FriendRelation).where(
                FriendRelation.id == request_id,
                FriendRelation.user_b == user_id,
                FriendRelation.status == FriendStatus.PENDING,
            )
        ).first()
        if not relation:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya procesada.")

        relation.status = FriendStatus.ACTIVE
        relation.friends_since = datetime.utcnow()
        relation.updated_at = datetime.utcnow()

        SocialService._log_action(session, user_id, relation.user_a, SocialActionType.FRIEND_REQUEST_ACCEPTED)

        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation

    @staticmethod
    def reject_friend_request(
        session: Session, user_id: str, request_id: int
    ) -> None:
        """Reject a pending friend request."""
        relation = session.exec(
            select(FriendRelation).where(
                FriendRelation.id == request_id,
                FriendRelation.user_b == user_id,
                FriendRelation.status == FriendStatus.PENDING,
            )
        ).first()
        if not relation:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya procesada.")

        relation.status = FriendStatus.REMOVED
        relation.updated_at = datetime.utcnow()
        session.add(relation)
        session.commit()

    @staticmethod
    def remove_friend(session: Session, user_id: str, friend_rel_id: int) -> None:
        """Remove a friend (soft-delete the relation)."""
        relation = session.exec(
            select(FriendRelation).where(
                FriendRelation.id == friend_rel_id,
                FriendRelation.status == FriendStatus.ACTIVE,
                or_(
                    FriendRelation.user_a == user_id,
                    FriendRelation.user_b == user_id,
                ),
            )
        ).first()
        if not relation:
            raise HTTPException(status_code=404, detail="Relación de amistad no encontrada.")

        relation.status = FriendStatus.REMOVED
        relation.updated_at = datetime.utcnow()
        session.add(relation)
        session.commit()

    @staticmethod
    def block_user(session: Session, user_id: str, target_id: str) -> None:
        """Block a user. Creates or updates relation to BLOCKED."""
        existing = SocialService._find_relation(session, user_id, target_id)
        if existing:
            existing.status = FriendStatus.BLOCKED
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            relation = FriendRelation(
                user_a=user_id,
                user_b=target_id,
                status=FriendStatus.BLOCKED,
            )
            session.add(relation)
        session.commit()

    # ── Friend List ───────────────────────────────────────────────────────

    @staticmethod
    def get_friends_list(
        session: Session, user_id: str
    ) -> list[dict]:
        """Get all active friends with online status and basic info."""
        relations = session.exec(
            select(FriendRelation).where(
                and_(
                    FriendRelation.status == FriendStatus.ACTIVE,
                    or_(
                        FriendRelation.user_a == user_id,
                        FriendRelation.user_b == user_id,
                    ),
                )
            ).order_by(FriendRelation.last_interaction_at.desc())
        ).all()

        friend_ids = set()
        result = []
        for rel in relations:
            friend_id = rel.user_b if rel.user_a == user_id else rel.user_a
            if friend_id in friend_ids:
                continue
            friend_ids.add(friend_id)

            friend_user = session.exec(
                select(User).where(User.privy_did == friend_id)
            ).first()
            if not friend_user:
                continue

            result.append({
                "relation_id": rel.id,
                "friend_id": friend_id,
                "nickname": friend_user.nickname,
                "avatar_url": friend_user.avatar_url or "",
                "vip_tier": friend_user.vip_tier,
                "is_online": SocialService._is_online(friend_user),
                "is_best_friend": SocialService._is_best_friend(rel, user_id),
                "interaction_count": rel.interaction_count,
                "friends_since": rel.friends_since.isoformat() if rel.friends_since else None,
            })

        # Sort: best friends (pinned) first, then online, then by interaction count
        result.sort(key=lambda f: (
            not f["is_best_friend"],
            not f["is_online"],
            -f["interaction_count"],
        ))
        return result

    @staticmethod
    def get_top_active_friends(
        session: Session, user_id: str, limit: int = 4
    ) -> list[dict]:
        """Get top N friends for ZonaInferior (sorted by relevance)."""
        all_friends = SocialService.get_friends_list(session, user_id)
        return all_friends[:limit]

    @staticmethod
    def get_pending_requests(
        session: Session, user_id: str
    ) -> list[dict]:
        """Get incoming pending friend requests."""
        relations = session.exec(
            select(FriendRelation).where(
                FriendRelation.user_b == user_id,
                FriendRelation.status == FriendStatus.PENDING,
            )
        ).all()

        result = []
        for rel in relations:
            sender = session.exec(
                select(User).where(User.privy_did == rel.user_a)
            ).first()
            if sender:
                result.append({
                    "id": rel.id,
                    "from_user_id": rel.user_a,
                    "from_nickname": sender.nickname,
                    "from_avatar_url": sender.avatar_url or "",
                    "created_at": rel.created_at.isoformat(),
                })
        return result

    @staticmethod
    def get_sent_requests(
        session: Session, user_id: str
    ) -> list[dict]:
        """Get sent friend requests still pending."""
        relations = session.exec(
            select(FriendRelation).where(
                FriendRelation.user_a == user_id,
                FriendRelation.status == FriendStatus.PENDING,
            )
        ).all()

        result = []
        for rel in relations:
            target = session.exec(
                select(User).where(User.privy_did == rel.user_b)
            ).first()
            if target:
                result.append({
                    "id": rel.id,
                    "to_user_id": rel.user_b,
                    "to_nickname": target.nickname,
                    "to_avatar_url": target.avatar_url or "",
                    "created_at": rel.created_at.isoformat(),
                })
        return result

    # ── Search & Discovery ───────────────────────────────────────────────

    @staticmethod
    def search_players(
        session: Session, query: str, searcher_id: str, limit: int = 20
    ) -> list[dict]:
        """Search players by nickname. Excludes blocked users."""
        if len(query) < 2:
            raise HTTPException(status_code=400, detail="Busca al menos 2 caracteres.")

        users = session.exec(
            select(User).where(
                User.nickname.ilike(f"%{query}%"),
                User.privy_did != searcher_id,
            ).limit(limit)
        ).all()

        # Fetch existing relationships for all found users at once
        results = []
        for user in users:
            rel = SocialService._find_relation(session, searcher_id, user.privy_did)
            if rel and rel.status == FriendStatus.BLOCKED:
                continue

            results.append({
                "user_id": user.privy_did,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url or "",
                "vip_tier": user.vip_tier,
                "cave_level": user.cave_level,
                "friendship_status": rel.status.value if rel else "none",
            })
        return results

    @staticmethod
    def get_recent_players(
        session: Session, user_id: str, limit: int = 10
    ) -> list[dict]:
        """Get players from recent public rooms, excluding current friends."""
        from app.models.lobby_models import MultiplayerGameLog

        # Find recent game logs for the user
        logs = session.exec(
            select(MultiplayerGameLog).where(
                MultiplayerGameLog.user_id == user_id
            ).order_by(MultiplayerGameLog.created_at.desc()).limit(20)
        ).all()

        # Get room names to find other players in same rooms
        room_names = list(set(log.room_name for log in logs if log.room_name))
        if not room_names:
            return []

        recent_player_ids = set()
        for room_name in room_names:
            co_players = session.exec(
                select(MultiplayerGameLog.user_id).where(
                    MultiplayerGameLog.room_name == room_name,
                    MultiplayerGameLog.user_id != user_id,
                )
            ).all()
            for cp in co_players:
                recent_player_ids.add(cp)

        # Filter out existing friends/blocked and map to user info
        results = []
        for pid in recent_player_ids:
            rel = SocialService._find_relation(session, user_id, pid)
            if rel and rel.status in (FriendStatus.ACTIVE, FriendStatus.BLOCKED):
                continue

            player = session.exec(select(User).where(User.privy_did == pid)).first()
            if player:
                results.append({
                    "user_id": player.privy_did,
                    "nickname": player.nickname,
                    "avatar_url": player.avatar_url or "",
                    "vip_tier": player.vip_tier,
                })

        return results[:limit]

    @staticmethod
    def get_suggestions(
        session: Session, user_id: str, limit: int = 5
    ) -> list[dict]:
        """Suggest players: friends of friends (mutual connections)."""
        # Get my friends
        my_friend_ids = SocialService._get_friend_ids(session, user_id)
        if not my_friend_ids:
            return []

        # Get friends of my friends
        suggestions = {}
        for fid in my_friend_ids:
            their_friends = SocialService._get_friend_ids(session, fid)
            for tf in their_friends:
                if tf == user_id or tf in my_friend_ids:
                    continue
                if tf not in suggestions:
                    suggestions[tf] = {"mutual_count": 0, "mutual_friends": []}
                suggestions[tf]["mutual_count"] += 1
                suggestions[tf]["mutual_friends"].append(fid)

        # Sort by mutual count desc
        sorted_suggestions = sorted(
            suggestions.items(), key=lambda x: -x[1]["mutual_count"]
        )

        results = []
        for uid, data in sorted_suggestions[:limit]:
            # Skip blocked
            rel = SocialService._find_relation(session, user_id, uid)
            if rel and rel.status == FriendStatus.BLOCKED:
                continue

            user = session.exec(select(User).where(User.privy_did == uid)).first()
            if user:
                results.append({
                    "user_id": uid,
                    "nickname": user.nickname,
                    "avatar_url": user.avatar_url or "",
                    "mutual_friends": data["mutual_count"],
                })

        return results

    # ── Social Actions ───────────────────────────────────────────────────

    @staticmethod
    def process_like(
        session: Session, actor_id: str, target_id: str
    ) -> dict:
        """Give a like to a friend. Mutually rewards +1 FRJ (unidad mínima)."""
        if actor_id == target_id:
            raise HTTPException(status_code=400, detail="No puedes darte like a ti mismo.")

        # Verify they are friends
        rel = SocialService._find_active_friendship(session, actor_id, target_id)
        if not rel:
            raise HTTPException(status_code=403, detail="Solo puedes dar like a tus amigos.")

        # Check daily limit
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        liked_today = session.exec(
            select(SocialActionLog).where(
                SocialActionLog.actor_id == actor_id,
                SocialActionLog.target_id == target_id,
                SocialActionLog.action_type == SocialActionType.LIKE_GIVEN,
                SocialActionLog.created_at >= today,
            )
        ).all()
        if len(liked_today) >= MAX_LIKES_PER_FRIEND_PER_DAY:
            raise HTTPException(status_code=400, detail="Ya le diste like hoy a este amigo.")

        # Log the like
        SocialService._log_action(session, actor_id, target_id, SocialActionType.LIKE_GIVEN)

        # Update interaction counter
        rel.interaction_count += 1
        rel.last_interaction_at = datetime.utcnow()
        rel.updated_at = datetime.utcnow()
        session.add(rel)

        actor_frj = None
        target_frj = None
        rewarded = settings.ENABLE_GAMEPLAY_TOKEN_REWARDS
        if rewarded:
            # Legacy reward path. Public non-gambling mode keeps the social
            # interaction but never creates wallets or changes token balances.
            from app.services.bank_service import BankService

            actor_wallet = BankService.get_or_create_wallet(session, actor_id)
            target_wallet = BankService.get_or_create_wallet(session, target_id)
            actor_wallet.frijolitos += 1
            target_wallet.frijolitos += 1
            actor_frj = actor_wallet.frijolitos
            target_frj = target_wallet.frijolitos
            session.add(actor_wallet)
            session.add(target_wallet)
        session.commit()

        return {
            "message": (
                "Like enviado. +1 FRJ para ambos."
                if rewarded
                else "Like enviado."
            ),
            "rewarded": rewarded,
            "actor_frj": actor_frj,
            "target_frj": target_frj,
        }

    @staticmethod
    def get_friend_cave(
        session: Session, visitor_id: str, friend_id: str
    ) -> dict:
        """Get friend's public cave data for visiting."""
        # Verify friendship
        rel = SocialService._find_active_friendship(session, visitor_id, friend_id)
        if not rel:
            raise HTTPException(status_code=403, detail="Solo puedes visitar la cueva de tus amigos.")

        friend = session.exec(select(User).where(User.privy_did == friend_id)).first()
        if not friend:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Log the visit
        SocialService._log_action(
            session, visitor_id, friend_id, SocialActionType.CAVE_VISITED,
            metadata='{"type": "visit"}'
        )

        # Update interaction
        rel.interaction_count += 1
        rel.last_interaction_at = datetime.utcnow()
        rel.updated_at = datetime.utcnow()
        session.add(rel)
        session.commit()

        return {
            "friend_id": friend_id,
            "nickname": friend.nickname,
            "cave_name": friend.cave_name,
            "cave_level": friend.cave_level,
            "cave_decorations": friend.cave_decorations,
            "vip_tier": friend.vip_tier,
            "avatar_url": friend.avatar_url or "",
            "is_online": SocialService._is_online(friend),
        }

    @staticmethod
    def visit_cave(
        session: Session, visitor_id: str, friend_id: str
    ) -> dict:
        """Register a cave visit (legacy-compatible wrapper)."""
        return SocialService.get_friend_cave(session, visitor_id, friend_id)

    # ── Visibility Helpers ──────────────────────────────────────────────

    @staticmethod
    def are_friends(session: Session, user_a: str, user_b: str) -> bool:
        """Check if two users are friends."""
        return SocialService._find_active_friendship(session, user_a, user_b) is not None

    @staticmethod
    def validate_room_access(
        session: Session, room_visibility: str, host_id: str, visitor_id: str
    ) -> bool:
        """Validate that a visitor can join a room based on visibility."""
        if room_visibility == "public":
            return True
        if room_visibility == "private":
            return False  # Private rooms use password; access handled by endpoint
        if room_visibility == "friends":
            if visitor_id == host_id:
                return True
            return SocialService.are_friends(session, host_id, visitor_id)
        return False

    # ═══════════════════════════════════════════════════════════════════════
    # Private helpers
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _find_relation(
        session: Session, user_a: str, user_b: str
    ) -> Optional[FriendRelation]:
        """Find any relation between two users (regardless of direction)."""
        return session.exec(
            select(FriendRelation).where(
                or_(
                    and_(FriendRelation.user_a == user_a, FriendRelation.user_b == user_b),
                    and_(FriendRelation.user_a == user_b, FriendRelation.user_b == user_a),
                )
            )
        ).first()

    @staticmethod
    def _find_active_friendship(
        session: Session, user_a: str, user_b: str
    ) -> Optional[FriendRelation]:
        """Find an active friendship relation between two users."""
        return session.exec(
            select(FriendRelation).where(
                FriendRelation.status == FriendStatus.ACTIVE,
                or_(
                    and_(FriendRelation.user_a == user_a, FriendRelation.user_b == user_b),
                    and_(FriendRelation.user_a == user_b, FriendRelation.user_b == user_a),
                ),
            )
        ).first()

    @staticmethod
    def _count_active_friends(session: Session, user_id: str) -> int:
        return len(session.exec(
            select(FriendRelation).where(
                FriendRelation.status == FriendStatus.ACTIVE,
                or_(
                    FriendRelation.user_a == user_id,
                    FriendRelation.user_b == user_id,
                ),
            )
        ).all())

    @staticmethod
    def _count_pending_sent(session: Session, user_id: str) -> int:
        return len(session.exec(
            select(FriendRelation).where(
                FriendRelation.user_a == user_id,
                FriendRelation.status == FriendStatus.PENDING,
            )
        ).all())

    @staticmethod
    def _check_hourly_rate_limit(session: Session, user_id: str) -> None:
        """Check that user hasn't exceeded MAX_PENDING_REQUESTS_PER_HOUR."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        count = len(session.exec(
            select(SocialActionLog).where(
                SocialActionLog.actor_id == user_id,
                SocialActionLog.action_type == SocialActionType.FRIEND_REQUEST_SENT,
                SocialActionLog.created_at >= one_hour_ago,
            )
        ).all())
        if count >= MAX_PENDING_REQUESTS_PER_HOUR:
            raise HTTPException(
                status_code=429,
                detail=f"Has enviado demasiadas solicitudes. Espera una hora.",
            )

    @staticmethod
    def _log_action(
        session: Session,
        actor_id: str,
        target_id: str,
        action_type: SocialActionType,
        metadata: str = "{}",
    ) -> SocialActionLog:
        log_entry = SocialActionLog(
            actor_id=actor_id,
            target_id=target_id,
            action_type=action_type,
            metadata_json=metadata,
        )
        session.add(log_entry)
        return log_entry

    @staticmethod
    def _get_friend_ids(session: Session, user_id: str) -> list[str]:
        """Get all active friend IDs for a user."""
        relations = session.exec(
            select(FriendRelation).where(
                FriendRelation.status == FriendStatus.ACTIVE,
                or_(
                    FriendRelation.user_a == user_id,
                    FriendRelation.user_b == user_id,
                ),
            )
        ).all()
        return [
            rel.user_b if rel.user_a == user_id else rel.user_a
            for rel in relations
        ]

    @staticmethod
    def _is_online(user: User) -> bool:
        """Heuristic: online if last_play_date within last 5 minutes."""
        if not user.last_play_date:
            return False
        return (datetime.utcnow() - user.last_play_date) < timedelta(minutes=5)

    @staticmethod
    def _is_best_friend(relation: FriendRelation, user_id: str) -> bool:
        """Best friend (pinned/compadre) status for user_id."""
        if relation.user_a == user_id:
            return relation.pinned_by_a
        else:
            return relation.pinned_by_b

    @staticmethod
    def toggle_pin_friend(
        session: Session, user_id: str, friend_id: str, pinned: bool
    ) -> FriendRelation:
        """Pin or unpin a friend (compadre)."""
        relation = SocialService._find_relation(session, user_id, friend_id)
        if not relation or relation.status != FriendStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="No existe una relación de amistad activa.")

        if relation.user_a == user_id:
            relation.pinned_by_a = pinned
        else:
            relation.pinned_by_b = pinned

        relation.updated_at = datetime.utcnow()
        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation
