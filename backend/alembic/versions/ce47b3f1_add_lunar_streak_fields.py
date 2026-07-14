"""add lunar streak fields to users

Revision ID: ce47b3f1
Revises: ff01aa23bb45
Create Date: 2026-06-07

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ce47b3f1'
down_revision: Union[str, None] = 'ff01aa23bb45'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('lunar_streak_day', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('lunar_week', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('user', sa.Column('lunar_last_claim_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('lunar_cycles_completed', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('user', 'lunar_cycles_completed')
    op.drop_column('user', 'lunar_last_claim_at')
    op.drop_column('user', 'lunar_week')
    op.drop_column('user', 'lunar_streak_day')
