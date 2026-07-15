"""add age assurance and commerce controls

Revision ID: d5e6f7a8b9c0
Revises: c72e0f3576ed
Create Date: 2026-07-15 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c72e0f3576ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("age_band", sa.String(length=16), nullable=False, server_default="unknown"),
    )
    op.add_column("user", sa.Column("age_assured_at", sa.DateTime(), nullable=True))
    op.add_column("user", sa.Column("guardian_consent_at", sa.DateTime(), nullable=True))
    op.add_column(
        "user", sa.Column("guardian_consent_version", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("commerce_status", sa.String(length=24), nullable=False, server_default="disabled"),
    )
    op.add_column(
        "user",
        sa.Column("creator_status", sa.String(length=24), nullable=False, server_default="ineligible"),
    )
    op.add_column(
        "user",
        sa.Column("kyc_status", sa.String(length=24), nullable=False, server_default="not_started"),
    )
    op.add_column(
        "user", sa.Column("terms_accepted_version", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "user", sa.Column("privacy_accepted_version", sa.String(length=64), nullable=True)
    )

    op.create_check_constraint(
        "ck_user_age_band",
        "user",
        "age_band IN ('unknown', 'under_13', 'teen_13_17', 'adult_18_plus')",
    )
    op.create_check_constraint(
        "ck_user_commerce_status",
        "user",
        "commerce_status IN ('disabled', 'pending_guardian', 'eligible', 'suspended')",
    )
    op.create_check_constraint(
        "ck_user_creator_status",
        "user",
        "creator_status IN ('ineligible', 'pending_review', 'approved', 'suspended')",
    )
    op.create_check_constraint(
        "ck_user_kyc_status",
        "user",
        "kyc_status IN ('not_started', 'pending', 'verified', 'rejected')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_kyc_status", "user", type_="check")
    op.drop_constraint("ck_user_creator_status", "user", type_="check")
    op.drop_constraint("ck_user_commerce_status", "user", type_="check")
    op.drop_constraint("ck_user_age_band", "user", type_="check")
    op.drop_column("user", "privacy_accepted_version")
    op.drop_column("user", "terms_accepted_version")
    op.drop_column("user", "kyc_status")
    op.drop_column("user", "creator_status")
    op.drop_column("user", "commerce_status")
    op.drop_column("user", "guardian_consent_version")
    op.drop_column("user", "guardian_consent_at")
    op.drop_column("user", "age_assured_at")
    op.drop_column("user", "age_band")
