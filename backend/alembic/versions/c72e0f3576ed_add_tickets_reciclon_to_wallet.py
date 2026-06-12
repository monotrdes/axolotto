"""add tickets_reciclon to wallet

Revision ID: c72e0f3576ed
Revises: b72e0e3575dc
Create Date: 2026-06-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c72e0f3576ed'
down_revision: Union[str, Sequence[str], None] = 'b72e0e3575dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add tickets_reciclon column to wallet."""
    op.add_column(
        'wallet',
        sa.Column('tickets_reciclon', sa.Integer(), nullable=False, server_default=sa.text('0'))
    )


def downgrade() -> None:
    """Downgrade schema - Remove tickets_reciclon column from wallet."""
    op.drop_column('wallet', 'tickets_reciclon')
