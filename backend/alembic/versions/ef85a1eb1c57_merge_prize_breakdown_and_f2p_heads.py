"""merge_prize_breakdown_and_f2p_heads

Revision ID: ef85a1eb1c57
Revises: a1b2c3d4e5f7, d1e2f3a4b5c6
Create Date: 2026-06-08 00:07:28.473152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef85a1eb1c57'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f7', 'd1e2f3a4b5c6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
