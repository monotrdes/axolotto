"""fix CAVE_ITEM enum value case

Revision ID: cc99dd88ee77
Revises: ff01aa23bb45
Create Date: 2026-06-03

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'cc99dd88ee77'
down_revision: Union[str, Sequence[str], None] = 'ff01aa23bb45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE itemtype RENAME VALUE 'cave_item' TO 'CAVE_ITEM'")


def downgrade() -> None:
    op.execute("ALTER TYPE itemtype RENAME VALUE 'CAVE_ITEM' TO 'cave_item'")
