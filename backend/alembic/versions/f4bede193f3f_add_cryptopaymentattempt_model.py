"""Add CryptoPaymentAttempt model

Revision ID: f4bede193f3f
Revises: fa91b3c2d7e0
Create Date: 2026-06-01 08:27:14.243041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f4bede193f3f'
down_revision: Union[str, Sequence[str], None] = 'fa91b3c2d7e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('cryptopaymentattempt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.String(), nullable=False),
    sa.Column('tx_hash', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('error_detail', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['cryptopurchaseorder.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.privy_did'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cryptopaymentattempt_order_id'), 'cryptopaymentattempt', ['order_id'], unique=False)
    op.create_index(op.f('ix_cryptopaymentattempt_tx_hash'), 'cryptopaymentattempt', ['tx_hash'], unique=False)
    op.create_index(op.f('ix_cryptopaymentattempt_user_id'), 'cryptopaymentattempt', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_cryptopaymentattempt_user_id'), table_name='cryptopaymentattempt')
    op.drop_index(op.f('ix_cryptopaymentattempt_tx_hash'), table_name='cryptopaymentattempt')
    op.drop_index(op.f('ix_cryptopaymentattempt_order_id'), table_name='cryptopaymentattempt')
    op.drop_table('cryptopaymentattempt')
    # ### end Alembic commands ###
