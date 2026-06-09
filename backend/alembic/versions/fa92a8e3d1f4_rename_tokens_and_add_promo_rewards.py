"""rename_tokens_and_add_promo_rewards

Revision ID: fa92a8e3d1f4
Revises: fa91b3c2d7e0
Create Date: 2026-06-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'fa92a8e3d1f4'
down_revision: Union[str, Sequence[str], None] = 'fa91b3c2d7e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("ALTER TYPE currencytype ADD VALUE IF NOT EXISTS 'axoficha'")
    op.execute("ALTER TYPE currencytype ADD VALUE IF NOT EXISTS 'frijolito'")
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='wallet' AND column_name='axogemas') THEN
                ALTER TABLE wallet RENAME COLUMN axogemas TO axofichas;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='wallet' AND column_name='gemas_alga') THEN
                ALTER TABLE wallet RENAME COLUMN gemas_alga TO frijolitos;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='axogemas_non_negative' AND table_name='wallet') THEN
                ALTER TABLE wallet DROP CONSTRAINT axogemas_non_negative;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='gemas_alga_non_negative' AND table_name='wallet') THEN
                ALTER TABLE wallet DROP CONSTRAINT gemas_alga_non_negative;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='axofichas_non_negative' AND table_name='wallet') THEN
                ALTER TABLE wallet ADD CONSTRAINT axofichas_non_negative CHECK (axofichas >= 0);
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='frijolitos_non_negative' AND table_name='wallet') THEN
                ALTER TABLE wallet ADD CONSTRAINT frijolitos_non_negative CHECK (frijolitos >= 0);
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='promocode' AND column_name='reward_frijolitos') THEN
                ALTER TABLE promocode ADD COLUMN reward_frijolitos FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='promocode' AND column_name='reward_axofichas') THEN
                ALTER TABLE promocode ADD COLUMN reward_axofichas FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='promocode' AND column_name='reward_item_id' AND is_nullable='NO') THEN
                ALTER TABLE promocode ALTER COLUMN reward_item_id DROP NOT NULL;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='cryptopurchaseorder' AND column_name='axg_amount') THEN
                ALTER TABLE cryptopurchaseorder RENAME COLUMN axg_amount TO axf_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='axg_purchase_record')
               AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='axf_purchase_record') THEN
                ALTER TABLE axg_purchase_record RENAME TO axf_purchase_record;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='axf_purchase_record' AND column_name='axg_amount') THEN
                ALTER TABLE axf_purchase_record RENAME COLUMN axg_amount TO axf_amount;
            END IF;
        END $$;
    """)

def downgrade() -> None:
    pass
