"""merge heads and add last_play_date daily_play_streak

Revision ID: ff01aa23bb45
Revises: bc1a3e9f0d2c, 53f16c5d5b0f
Create Date: 2026-06-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ff01aa23bb45'
down_revision: Union[str, Sequence[str], None] = ('bc1a3e9f0d2c', '53f16c5d5b0f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_play_date TIMESTAMP')
    op.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS daily_play_streak INTEGER NOT NULL DEFAULT 0')


def downgrade() -> None:
    op.drop_column('user', 'daily_play_streak')
    op.drop_column('user', 'last_play_date')
