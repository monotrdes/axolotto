"""Social graph models: friends, actions, referrals.

Phase 1 (task-1780974961-58): FriendRelation + SocialActionLog
Phase 2 (task-1780974969-59): ReferralCode + ReferralTracking
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index


# ── Friend Graph ────────────────────────────────────────────────────────────

class FriendStatus(str, Enum):
    PENDING = "pending"        # Solicitud enviada, no aceptada aún
    ACTIVE = "active"          # Amigos confirmados
    BLOCKED = "blocked"        # Bloqueado (unilateral)
    REMOVED = "removed"        # Eliminado (soft-delete)


class FriendRelation(SQLModel, table=True):
    __tablename__ = "friend_relations"
    __table_args__ = (
        UniqueConstraint("user_a", "user_b", name="uq_friend_pair"),
        Index("idx_friend_status", "status"),
        Index("idx_friend_user_b_status", "user_b", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_a: str = Field(foreign_key="user.privy_did", index=True)  # quien envió solicitud
    user_b: str = Field(foreign_key="user.privy_did", index=True)  # quien recibe
    status: FriendStatus = Field(default=FriendStatus.PENDING)
    friends_since: Optional[datetime] = Field(default=None)
    interaction_count: int = Field(default=0)         # total: likes + gifts + visits + games
    last_interaction_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        return self.status == FriendStatus.ACTIVE


# ── Social Actions Log (analytics + anti-abuse) ──────────────────────────────

class SocialActionType(str, Enum):
    LIKE_GIVEN = "like_given"
    GIFT_SENT = "gift_sent"
    CAVE_VISITED = "cave_visited"
    GAME_INVITE_SENT = "game_invite_sent"
    FRIEND_REQUEST_SENT = "friend_request_sent"
    FRIEND_REQUEST_ACCEPTED = "friend_request_accepted"


class SocialActionLog(SQLModel, table=True):
    __tablename__ = "social_action_logs"
    __table_args__ = (
        Index("idx_social_actor_time", "actor_id", "created_at"),
        Index("idx_social_target_time", "target_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: str = Field(foreign_key="user.privy_did", index=True)
    target_id: str = Field(foreign_key="user.privy_did", index=True)
    action_type: SocialActionType
    metadata_json: str = Field(default="{}")  # item_id, quantity, room_id, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Referral System (Phase 2) ───────────────────────────────────────────────

class ReferralStatus(str, Enum):
    REGISTERED = "registered"        # Creó cuenta con el código
    TUTORIAL_DONE = "tutorial_done"  # Completó tutorial
    D7_RETAINED = "d7_retained"      # Jugó en D7 (primer partida + actividad)
    CONVERTED = "converted"          # Hizo primera compra crypto
    CHURNED = "churned"              # 30 días sin jugar


class ReferralCode(SQLModel, table=True):
    __tablename__ = "referral_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", unique=True, index=True)
    code: str = Field(unique=True, index=True, max_length=30)
    total_uses: int = Field(default=0)
    active_referrals: int = Field(default=0)       # no churned
    rewards_earned_frj: int = Field(default=0)     # unidad mínima
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralTracking(SQLModel, table=True):
    __tablename__ = "referral_tracking"

    id: Optional[int] = Field(default=None, primary_key=True)
    referrer_id: str = Field(foreign_key="user.privy_did", index=True)
    referred_id: str = Field(foreign_key="user.privy_did", unique=True, index=True)
    code_used: str = Field(index=True)
    status: ReferralStatus = Field(default=ReferralStatus.REGISTERED)
    rewards_given_to_referrer: str = Field(default="{}")  # JSON: {"tutorial":true,"d7":false,...}
    rewards_given_to_referred: str = Field(default="{}")
    referred_at: datetime = Field(default_factory=datetime.utcnow)
    converted_at: Optional[datetime] = Field(default=None)
    churned_at: Optional[datetime] = Field(default=None)
