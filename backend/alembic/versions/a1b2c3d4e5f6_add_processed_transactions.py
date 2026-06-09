"""add_processed_transactions

Revision ID: a1b2c3d4e5f6
Revises: 37751e240bf6
Create Date: 2026-05-26 00:00:00.000000

"""
import sqlmodel
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '37751e240bf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'processedtransaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tx_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('purpose', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.privy_did']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tx_hash', name='uq_processedtransaction_tx_hash'),
    )
    op.create_index('ix_processedtransaction_tx_hash', 'processedtransaction', ['tx_hash'], unique=True)
    op.create_index('ix_processedtransaction_user_id', 'processedtransaction', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_processedtransaction_user_id', 'processedtransaction')
    op.drop_index('ix_processedtransaction_tx_hash', 'processedtransaction')
    op.drop_table('processedtransaction')
