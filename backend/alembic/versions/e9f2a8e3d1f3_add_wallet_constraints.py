"""add wallet constraints

Revision ID: e9f2a8e3d1f3
Revises: da23a8e9d1e3
Create Date: 2026-06-01 09:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9f2a8e3d1f3'
down_revision: Union[str, Sequence[str], None] = 'da23a8e9d1e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear restricciones CHECK en la tabla wallet
    op.create_check_constraint(
        "axogemas_non_negative",
        "wallet",
        "axogemas >= 0"
    )
    op.create_check_constraint(
        "gemas_alga_non_negative",
        "wallet",
        "gemas_alga >= 0"
    )


def downgrade() -> None:
    # Eliminar restricciones CHECK
    op.drop_constraint("axogemas_non_negative", "wallet", type_="check")
    op.drop_constraint("gemas_alga_non_negative", "wallet", type_="check")
