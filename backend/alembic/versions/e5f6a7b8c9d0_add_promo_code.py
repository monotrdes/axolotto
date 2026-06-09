"""add promo_code table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'promocode',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('batch', sa.String(), nullable=False),
        sa.Column('reward_type', sa.String(), nullable=False, server_default='booster_pack'),
        sa.Column('reward_item_id', sa.Integer(), nullable=False),
        sa.Column('redeemed_by', sa.String(), nullable=True),
        sa.Column('redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reward_item_id'], ['itemcatalog.id']),
        sa.ForeignKeyConstraint(['redeemed_by'], ['user.privy_did']),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_promocode_code', 'promocode', ['code'])
    op.create_index('ix_promocode_redeemed_by', 'promocode', ['redeemed_by'])


def downgrade() -> None:
    op.drop_index('ix_promocode_redeemed_by', table_name='promocode')
    op.drop_index('ix_promocode_code', table_name='promocode')
    op.drop_table('promocode')
