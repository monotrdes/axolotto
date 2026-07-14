"""add_prize_breakdown_to_multigamelog

Revision ID: a1b2c3d4e5f7
Revises: ce47b3f1
Create Date: 2026-06-07

Add prize breakdown fields to MultiplayerGameLog to support clear
prize display in multiplayer game results:
  - prize_breakdown_json (Text, nullable) — JSON breakdown of prizes won
  - won_premio_1 (bool) — won first pattern prize
  - won_premio_2 (bool) — won full board prize
  - won_jackpot (bool) — won global jackpot
  - entry_fee_paid (float) — total buy-in paid for the match
  - gross_prize_gal (float) — gross prize amount before fees
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, Sequence[str], None] = 'ce47b3f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('multiplayergamelog', sa.Column(
        'prize_breakdown_json', sa.Text(), nullable=True
    ))
    op.add_column('multiplayergamelog', sa.Column(
        'won_premio_1', sa.Boolean(), nullable=False, server_default=sa.text('false')
    ))
    op.add_column('multiplayergamelog', sa.Column(
        'won_premio_2', sa.Boolean(), nullable=False, server_default=sa.text('false')
    ))
    op.add_column('multiplayergamelog', sa.Column(
        'won_jackpot', sa.Boolean(), nullable=False, server_default=sa.text('false')
    ))
    op.add_column('multiplayergamelog', sa.Column(
        'entry_fee_paid', sa.Float(), nullable=False, server_default=sa.text('0')
    ))
    op.add_column('multiplayergamelog', sa.Column(
        'gross_prize_gal', sa.Float(), nullable=False, server_default=sa.text('0')
    ))


def downgrade() -> None:
    op.drop_column('multiplayergamelog', 'gross_prize_gal')
    op.drop_column('multiplayergamelog', 'entry_fee_paid')
    op.drop_column('multiplayergamelog', 'won_jackpot')
    op.drop_column('multiplayergamelog', 'won_premio_2')
    op.drop_column('multiplayergamelog', 'won_premio_1')
    op.drop_column('multiplayergamelog', 'prize_breakdown_json')
