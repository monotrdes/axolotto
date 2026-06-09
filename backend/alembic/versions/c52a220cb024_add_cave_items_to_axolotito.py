"""add_cave_items_to_axolotito

Revision ID: c52a220cb024
Revises: 39d71ef65317
Create Date: 2026-05-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c52a220cb024'
down_revision: Union[str, Sequence[str], None] = 'a9f3c1e72b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('axolotito', sa.Column('cave_items', sa.JSON(), nullable=True, server_default='[]'))


def downgrade() -> None:
    op.drop_column('axolotito', 'cave_items')
