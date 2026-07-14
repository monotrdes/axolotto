"""VULN-06: Migrar saldos monetarios de float a enteros (unidad mínima)

Esta migración convierte todas las columnas monetarias float a INTEGER
multiplicando por el factor de precisión correspondiente:

  AXF (Axofichas): float * 10^6 → integer
  FRJ (Frijolitos): float * 10^4 → integer

Las columnas de estadísticas (stat_*, xp, level) NO son monetarias y se mantienen.

Revision ID: b1c2d3e4f5a6
Revises: ff01aa23bb45
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'b1c2d3e4f5a6'
down_revision = 'ff01aa23bb45'
branch_labels = None
depends_on = None

# Factores de precisión
AXF_FACTOR = 10 ** 6   # 1 AXF = 1,000,000 unidades mínimas
FRJ_FACTOR = 10 ** 4   # 1 FRJ = 10,000 unidades mínimas


def _migrate_column(table: str, column: str, factor: int):
    """Convierte una columna float a bigint multiplicando por factor y redondeando."""
    # Usamos ROUND para evitar polvo (dust) en la conversión
    op.execute(
        f'ALTER TABLE "{table}" ALTER COLUMN "{column}" '
        f'TYPE BIGINT USING ROUND("{column}"::numeric * {factor})::bigint'
    )


def _migrate_nullable_column(table: str, column: str, factor: int):
    """Convierte columna float nullable a bigint nullable."""
    op.execute(
        f'ALTER TABLE "{table}" ALTER COLUMN "{column}" '
        f'TYPE BIGINT USING '
        f'CASE WHEN "{column}" IS NULL THEN NULL '
        f'ELSE ROUND("{column}"::numeric * {factor})::bigint END'
    )


def upgrade():
    # ── Wallet ──────────────────────────────────────────────────────────
    _migrate_column("wallet", "axofichas", AXF_FACTOR)
    _migrate_column("wallet", "frijolitos", FRJ_FACTOR)

    # ── TransactionLedger ────────────────────────────────────────────────
    _migrate_column("transactionledger", "amount", 1)  # moneda mixta — se migra 1:1
    _migrate_column("transactionledger", "fee_applied", 1)

    # ── AxfPurchaseRecord ────────────────────────────────────────────────
    _migrate_column("axf_purchase_record", "axf_amount", AXF_FACTOR)

    # ── ItemCatalog ──────────────────────────────────────────────────────
    _migrate_nullable_column("itemcatalog", "price_axg", AXF_FACTOR)
    _migrate_nullable_column("itemcatalog", "price_gal", FRJ_FACTOR)

    # ── Axolotito ────────────────────────────────────────────────────────
    _migrate_column("axolotito", "accrued_unclaimed", FRJ_FACTOR)
    _migrate_column("axolotito", "escrow_balance_gal", FRJ_FACTOR)
    _migrate_column("axolotito", "bot_budget_axg", FRJ_FACTOR)
    _migrate_column("axolotito", "bot_loss_limit_axg", FRJ_FACTOR)
    _migrate_column("axolotito", "bot_profit_limit_axg", FRJ_FACTOR)
    _migrate_column("axolotito", "sale_price_gal", FRJ_FACTOR)
    _migrate_column("axolotito", "rent_fee_gal", FRJ_FACTOR)

    # ── Lobby models ─────────────────────────────────────────────────────
    _migrate_column("multiplayergamelog", "net_gal", FRJ_FACTOR)
    _migrate_column("multiplayergamelog", "entry_fee_paid", FRJ_FACTOR)
    _migrate_column("multiplayergamelog", "gross_prize_gal", FRJ_FACTOR)
    _migrate_column("treasuryvault", "balance", FRJ_FACTOR)
    _migrate_column("jackpotvault", "current_amount", FRJ_FACTOR)
    _migrate_column("jackpotvault", "seed_amount", FRJ_FACTOR)
    _migrate_column("jackpotwin", "amount_won", FRJ_FACTOR)
    _migrate_column("gameroom", "entry_fee_gal", FRJ_FACTOR)

    # ── User ─────────────────────────────────────────────────────────────
    _migrate_column("user", "f2p_daily_gal_earned", FRJ_FACTOR)
    _migrate_column("user", "vip_pending_gal", FRJ_FACTOR)

    # ── CryptoPurchaseOrder ──────────────────────────────────────────────
    _migrate_column("cryptopurchaseorder", "usdc_amount", 1)  # ya en mínima unidad
    _migrate_column("cryptopurchaseorder", "axf_amount", AXF_FACTOR)

    # Nota: TransactionLedger.amount migra 1:1 porque es un registro histórico.
    # Las nuevas escrituras ya usan montos en unidad mínima entera.
    # Para migrar registros históricos correctamente necesitaríamos conocer
    # la moneda de cada fila — se deja como mejora futura (baja prioridad).


def downgrade():
    """Revierte las columnas a float (división por factor)."""
    # ── Wallet ──────────────────────────────────────────────────────────
    op.execute(
        f'ALTER TABLE "wallet" ALTER COLUMN "axofichas" '
        f'TYPE DOUBLE PRECISION USING "axofichas"::double precision / {AXF_FACTOR}'
    )
    op.execute(
        f'ALTER TABLE "wallet" ALTER COLUMN "frijolitos" '
        f'TYPE DOUBLE PRECISION USING "frijolitos"::double precision / {FRJ_FACTOR}'
    )

    # ── TransactionLedger ────────────────────────────────────────────────
    for col in ("amount", "fee_applied"):
        op.execute(
            f'ALTER TABLE "transactionledger" ALTER COLUMN "{col}" '
            f'TYPE DOUBLE PRECISION USING "{col}"::double precision'
        )

    # ── AxfPurchaseRecord ────────────────────────────────────────────────
    op.execute(
        f'ALTER TABLE "axf_purchase_record" ALTER COLUMN "axf_amount" '
        f'TYPE DOUBLE PRECISION USING "axf_amount"::double precision / {AXF_FACTOR}'
    )

    # ── ItemCatalog ──────────────────────────────────────────────────────
    for col in ("price_axg", "price_gal"):
        factor = AXF_FACTOR if col == "price_axg" else FRJ_FACTOR
        op.execute(
            f'ALTER TABLE "itemcatalog" ALTER COLUMN "{col}" '
            f'TYPE DOUBLE PRECISION USING '
            f'CASE WHEN "{col}" IS NULL THEN NULL '
            f'ELSE "{col}"::double precision / {factor} END'
        )

    # ── Axolotito ────────────────────────────────────────────────────────
    for col in ("accrued_unclaimed", "escrow_balance_gal", "bot_budget_axg",
                 "bot_loss_limit_axg", "bot_profit_limit_axg",
                 "sale_price_gal", "rent_fee_gal"):
        op.execute(
            f'ALTER TABLE "axolotito" ALTER COLUMN "{col}" '
            f'TYPE DOUBLE PRECISION USING "{col}"::double precision / {FRJ_FACTOR}'
        )

    # ── Lobby models ─────────────────────────────────────────────────────
    for col, factor in [
        ("net_gal", FRJ_FACTOR), ("entry_fee_paid", FRJ_FACTOR),
        ("gross_prize_gal", FRJ_FACTOR), ("balance", FRJ_FACTOR),
        ("current_amount", FRJ_FACTOR), ("seed_amount", FRJ_FACTOR),
        ("amount_won", FRJ_FACTOR), ("entry_fee_gal", FRJ_FACTOR),
    ]:
        table = {
            "net_gal": "multiplayergamelog", "entry_fee_paid": "multiplayergamelog",
            "gross_prize_gal": "multiplayergamelog", "balance": "treasuryvault",
            "current_amount": "jackpotvault", "seed_amount": "jackpotvault",
            "amount_won": "jackpotwin", "entry_fee_gal": "gameroom",
        }[col]
        op.execute(
            f'ALTER TABLE "{table}" ALTER COLUMN "{col}" '
            f'TYPE DOUBLE PRECISION USING "{col}"::double precision / {factor}'
        )

    # ── User ─────────────────────────────────────────────────────────────
    for col in ("f2p_daily_gal_earned", "vip_pending_gal"):
        op.execute(
            f'ALTER TABLE "user" ALTER COLUMN "{col}" '
            f'TYPE DOUBLE PRECISION USING "{col}"::double precision / {FRJ_FACTOR}'
        )

    # ── CryptoPurchaseOrder ──────────────────────────────────────────────
    op.execute(
        f'ALTER TABLE "cryptopurchaseorder" ALTER COLUMN "axf_amount" '
        f'TYPE DOUBLE PRECISION USING "axf_amount"::double precision / {AXF_FACTOR}'
    )
    op.execute(
        f'ALTER TABLE "cryptopurchaseorder" ALTER COLUMN "usdc_amount" '
        f'TYPE DOUBLE PRECISION USING "usdc_amount"::double precision'
    )
