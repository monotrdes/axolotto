"""add_user_vip_fields

Revision ID: 37751e240bf6
Revises: 919663c1bc6e
Create Date: 2026-05-26 10:57:49.529535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '37751e240bf6'
down_revision: Union[str, Sequence[str], None] = '919663c1bc6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to user
    op.add_column('user', sa.Column('vip_tier', sa.String(), nullable=True))
    op.add_column('user', sa.Column('vip_expires_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('vip_streak_months', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('vip_streak_last_renewed', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('vip_pending_gal', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('user', sa.Column('vip_pending_gal_expires_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('vip_tiers_activated', sa.String(), nullable=True, server_default='[]'))

    # Add columns to axolotito and playerboard
    op.add_column('axolotito', sa.Column('is_frozen_by_vip', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('playerboard', sa.Column('is_frozen_by_vip', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('playerboard', 'is_frozen_by_vip')
    op.drop_column('axolotito', 'is_frozen_by_vip')
    
    op.drop_column('user', 'vip_tiers_activated')
    op.drop_column('user', 'vip_pending_gal_expires_at')
    op.drop_column('user', 'vip_pending_gal')
    op.drop_column('user', 'vip_streak_last_renewed')
    op.drop_column('user', 'vip_streak_months')
    op.drop_column('user', 'vip_expires_at')
    op.drop_column('user', 'vip_tier')
