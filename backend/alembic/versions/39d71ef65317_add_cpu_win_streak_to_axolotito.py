"""add_cpu_win_streak_to_axolotito

Revision ID: 39d71ef65317
Revises: c3d4e5f6a7b8
Create Date: 2026-05-28 01:40:16.760951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39d71ef65317'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('axolotito', sa.Column('cpu_win_streak', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('axolotito', 'cpu_win_streak')
