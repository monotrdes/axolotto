"""tutorial_f2p_webito_slots_fields

Revision ID: fa91b3c2d7e0
Revises: e5f6a7b8c9d0
Create Date: 2026-05-30

Adds to User:
  - tutorial_completed (bool)
  - webito_slots_unlocked (int)
  - f2p_astral_fragments (int)
  - f2p_daily_gal_earned (float)
  - f2p_daily_gal_reset_at (timestamp)

Adds to WebitoIncubation:
  - tutorial_phase (int)
  - tutorial_karma (varchar)

Adds to transactiontype enum:
  - tutorial_bonus
  - webito_unlock
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'fa91b3c2d7e0'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend transactiontype enum with new values (PostgreSQL-safe)
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'tutorial_bonus'")
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'webito_unlock'")

    # User — tutorial & f2p columns
    op.add_column('user', sa.Column('tutorial_completed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('webito_slots_unlocked', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('user', sa.Column('f2p_astral_fragments', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('f2p_daily_gal_earned', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('user', sa.Column('f2p_daily_gal_reset_at', sa.DateTime(), nullable=True))

    # WebitoIncubation — tutorial columns
    op.add_column('webitoincubation', sa.Column('tutorial_phase', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('webitoincubation', sa.Column('tutorial_karma', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('webitoincubation', 'tutorial_karma')
    op.drop_column('webitoincubation', 'tutorial_phase')
    op.drop_column('user', 'f2p_daily_gal_reset_at')
    op.drop_column('user', 'f2p_daily_gal_earned')
    op.drop_column('user', 'f2p_astral_fragments')
    op.drop_column('user', 'webito_slots_unlocked')
    op.drop_column('user', 'tutorial_completed')
    # Note: PostgreSQL does not support removing enum values; downgrade leaves enum extended.
