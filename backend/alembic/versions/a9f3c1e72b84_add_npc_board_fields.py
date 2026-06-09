"""add_npc_board_fields

Revision ID: a9f3c1e72b84
Revises: 39d71ef65317
Create Date: 2026-05-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9f3c1e72b84'
down_revision: Union[str, Sequence[str], None] = '39d71ef65317'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('playerboard', sa.Column('is_npc_pool', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('playerboard', sa.Column('npc_room', sa.String(), nullable=True))
    op.add_column('playerboard', sa.Column('npc_retired', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('playerboard', sa.Column('origin_story', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('playerboard', 'origin_story')
    op.drop_column('playerboard', 'npc_retired')
    op.drop_column('playerboard', 'npc_room')
    op.drop_column('playerboard', 'is_npc_pool')
