"""add max_per_user and whitelist

Revision ID: d4e5f6a7b8c9
Revises: c52a220cb024
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c52a220cb024'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('itemcatalog', sa.Column('max_per_user', sa.Integer(), nullable=True))
    op.create_table(
        'whitelistentry',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('registered_at', sa.DateTime(), nullable=False),
        sa.Column('phase_access', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source', sa.String(), nullable=False, server_default='microsite'),
        sa.ForeignKeyConstraint(['user_id'], ['user.privy_did']),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_whitelistentry_user_id', 'whitelistentry', ['user_id'])
    op.create_index('ix_whitelistentry_email', 'whitelistentry', ['email'])


def downgrade() -> None:
    op.drop_index('ix_whitelistentry_email', table_name='whitelistentry')
    op.drop_index('ix_whitelistentry_user_id', table_name='whitelistentry')
    op.drop_table('whitelistentry')
    op.drop_column('itemcatalog', 'max_per_user')
