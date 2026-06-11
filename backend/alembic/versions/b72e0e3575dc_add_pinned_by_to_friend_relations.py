"""add pinned_by to friend_relations

Revision ID: b72e0e3575dc
Revises: de45f7199b37
Create Date: 2026-06-11 20:32:31.266599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b72e0e3575dc'
down_revision: Union[str, Sequence[str], None] = 'de45f7199b37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add pinned_by columns to friend_relations."""
    op.add_column(
        'friend_relations',
        sa.Column('pinned_by_a', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.add_column(
        'friend_relations',
        sa.Column('pinned_by_b', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )


def downgrade() -> None:
    """Downgrade schema - Remove pinned_by columns from friend_relations."""
    op.drop_column('friend_relations', 'pinned_by_a')
    op.drop_column('friend_relations', 'pinned_by_b')
