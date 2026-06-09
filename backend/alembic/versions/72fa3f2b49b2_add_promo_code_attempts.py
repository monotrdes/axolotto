"""add_promo_code_attempts

Revision ID: 72fa3f2b49b2
Revises: bb01d2e3f4a5
Create Date: 2026-06-02 01:13:21.091483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '72fa3f2b49b2'
down_revision: Union[str, Sequence[str], None] = 'bb01d2e3f4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('promo_code_attempts', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('user', 'promo_code_attempts')
