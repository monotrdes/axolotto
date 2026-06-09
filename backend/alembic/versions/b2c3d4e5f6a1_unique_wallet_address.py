"""unique_wallet_address

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_user_wallet_address",
        "user",
        ["wallet_address"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_wallet_address", "user", type_="unique")
