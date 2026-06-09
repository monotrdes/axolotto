"""merge_heads

Revision ID: bb01d2e3f4a5
Revises: e9f2a8e3d1f3, fa92a8e3d1f4
Create Date: 2026-06-01

"""
from typing import Sequence, Union


revision: str = 'bb01d2e3f4a5'
down_revision: Union[str, Sequence[str]] = ('e9f2a8e3d1f3', 'fa92a8e3d1f4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
