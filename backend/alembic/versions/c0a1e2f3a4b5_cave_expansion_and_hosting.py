"""cave_expansion_and_hosting

Revision ID: c0a1e2f3a4b5
Revises: ff01aa23bb45
Create Date: 2026-06-03

Adds to User:
  - cave_level (int, default 1) — replaces webito_slots_unlocked
  - cave_name (varchar, nullable)
  - cave_decorations (JSON, default '{}')
  - cave_expansion_started_at (timestamp, nullable)
  - cave_expansion_target_level (int, nullable)

Migrates webito_slots_unlocked → cave_level for existing users.

Adds to GameRoom:
  - host_id (varchar FK → user.privy_did, nullable)
  - room_config (JSON, nullable)
  - visibility (varchar, default 'public')
  - password_hash (varchar, nullable)
  - host_reputation_earned (int, default 0)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c0a1e2f3a4b5'
down_revision: Union[str, Sequence[str], None] = 'ff01aa23bb45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # User — cave_expansion columns
    op.add_column('user', sa.Column('cave_level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('user', sa.Column('cave_name', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('cave_decorations', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('user', sa.Column('cave_expansion_started_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('cave_expansion_target_level', sa.Integer(), nullable=True))

    # Migrate webito_slots_unlocked → cave_level for existing users
    op.execute("""
        UPDATE "user"
        SET cave_level = webito_slots_unlocked
        WHERE cave_level = 1 AND webito_slots_unlocked > 1
    """)

    # GameRoom — hosting columns
    op.add_column('gameroom', sa.Column('host_id', sa.String(length=255), nullable=True))
    op.add_column('gameroom', sa.Column('room_config', sa.JSON(), nullable=True))
    op.add_column('gameroom', sa.Column('visibility', sa.String(length=20), nullable=False, server_default='public'))
    op.add_column('gameroom', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('gameroom', sa.Column('host_reputation_earned', sa.Integer(), nullable=False, server_default='0'))

    # FK for host_id → user.privy_did
    op.create_foreign_key(
        'fk_gameroom_host_id_user',
        'gameroom', 'user',
        ['host_id'], ['privy_did'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_gameroom_host_id_user', 'gameroom', type_='foreignkey')
    op.drop_column('gameroom', 'host_reputation_earned')
    op.drop_column('gameroom', 'password_hash')
    op.drop_column('gameroom', 'visibility')
    op.drop_column('gameroom', 'room_config')
    op.drop_column('gameroom', 'host_id')
    op.drop_column('user', 'cave_expansion_target_level')
    op.drop_column('user', 'cave_expansion_started_at')
    op.drop_column('user', 'cave_decorations')
    op.drop_column('user', 'cave_name')
    op.drop_column('user', 'cave_level')
    # Note: webito_slots_unlocked is NOT restored in downgrade.
    # Data migration is one-way.
