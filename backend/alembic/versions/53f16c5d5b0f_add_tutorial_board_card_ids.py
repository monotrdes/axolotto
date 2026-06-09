"""add_tutorial_board_card_ids

Revision ID: 53f16c5d5b0f
Revises: fa92a8e3d1f4
Create Date: 2026-06-02 10:04:57
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '53f16c5d5b0f'
down_revision: Union[str, Sequence[str], None] = '72fa3f2b49b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('webitoincubation',
                  sa.Column('tutorial_board_card_ids', postgresql.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('webitoincubation', 'tutorial_board_card_ids')
