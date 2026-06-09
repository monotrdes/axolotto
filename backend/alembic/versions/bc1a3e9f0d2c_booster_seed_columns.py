"""booster_seed_columns

Revision ID: bc1a3e9f0d2c
Revises: fa92a8e3d1f4
Create Date: 2026-06-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'bc1a3e9f0d2c'
down_revision: Union[str, Sequence[str], None] = 'fa92a8e3d1f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE playerinventory ADD COLUMN IF NOT EXISTS seed VARCHAR")
    op.execute("ALTER TABLE inventorymarketlisting ADD COLUMN IF NOT EXISTS seed VARCHAR")


def downgrade() -> None:
    op.drop_column('inventorymarketlisting', 'seed')
    op.drop_column('playerinventory', 'seed')
