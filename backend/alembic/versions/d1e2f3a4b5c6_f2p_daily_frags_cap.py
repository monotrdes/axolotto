"""f2p_daily_frags_cap

Revision ID: d1e2f3a4b5c6
Revises: cc99dd88ee77, c0a1e2f3a4b5
Create Date: 2026-06-04

Adds to User:
  - f2p_daily_frags_earned (int, default 0) — daily fragment cap tracking
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = ('cc99dd88ee77', 'c0a1e2f3a4b5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column('f2p_daily_frags_earned', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('user', 'f2p_daily_frags_earned')
