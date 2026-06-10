"""merge_vuln06_and_main

Revision ID: e13048ae5137
Revises: b1c2d3e4f5a6, ef85a1eb1c57
Create Date: 2026-06-10 01:09:33.219672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e13048ae5137'
down_revision: Union[str, Sequence[str], None] = ('b1c2d3e4f5a6', 'ef85a1eb1c57')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
