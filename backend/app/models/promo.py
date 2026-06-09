from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class PromoCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    batch: str
    reward_type: str = Field(default="booster_pack")
    reward_item_id: Optional[int] = Field(default=None, foreign_key="itemcatalog.id", nullable=True)
    reward_frijolitos: float = Field(default=0.0)
    reward_axofichas: float = Field(default=0.0)
    redeemed_by: Optional[str] = Field(default=None, foreign_key="user.privy_did")
    redeemed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PendingReward(SQLModel, table=True):
    """Premio de código promocional pendiente de reclamar (se entrega al final del tutorial)."""
    __tablename__ = "pending_rewards"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.privy_did", index=True, unique=True)
    promo_code_id: int = Field(foreign_key="promocode.id")
    reward_axf: float = Field(default=0.0)
    reward_frj: float = Field(default=0.0)
    reward_item_id: Optional[int] = Field(default=None, nullable=True)
    claimed: bool = Field(default=False)
    claimed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
