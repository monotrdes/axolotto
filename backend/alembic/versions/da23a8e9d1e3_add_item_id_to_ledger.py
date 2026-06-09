"""add item_id to ledger

Revision ID: da23a8e9d1e3
Revises: f4bede193f3f
Create Date: 2026-06-01 08:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'da23a8e9d1e3'
down_revision: Union[str, Sequence[str], None] = 'f4bede193f3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add column
    op.add_column('transactionledger', sa.Column('item_id', sa.Integer(), nullable=True))
    
    # 2. Create foreign key constraint
    op.create_foreign_key(
        'fk_transactionledger_item_id_itemcatalog',
        'transactionledger', 'itemcatalog',
        ['item_id'], ['id']
    )
    
    # 3. Create index
    op.create_index(
        op.f('ix_transactionledger_item_id'),
        'transactionledger', ['item_id'],
        unique=False
    )
    
    # 4. Backfill historical entries
    bind = op.get_bind()
    try:
        items = bind.execute(sa.text("SELECT id, name FROM itemcatalog")).fetchall()
        for item_id, name in items:
            bind.execute(
                sa.text(
                    "UPDATE transactionledger "
                    "SET item_id = :item_id "
                    "WHERE item_id IS NULL AND description LIKE :pattern"
                ),
                {"item_id": item_id, "pattern": f"%{name}%"}
            )
    except Exception as e:
        print(f"⚠️ Error during backfill: {e}")


def downgrade() -> None:
    op.drop_index(op.f('ix_transactionledger_item_id'), table_name='transactionledger')
    op.drop_constraint('fk_transactionledger_item_id_itemcatalog', 'transactionledger', type_='foreignkey')
    op.drop_column('transactionledger', 'item_id')
