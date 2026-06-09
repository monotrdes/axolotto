"""Add BURN and VIP_GAL_EXPIRED to transactiontype enum

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a1
Create Date: 2026-05-27
"""
from alembic import op

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'BURN'")
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'VIP_GAL_EXPIRED'")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de un enum; se deja como no-op
    pass
