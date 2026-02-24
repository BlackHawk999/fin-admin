"""cashbox entry split by payment types and expenses

Revision ID: 3d1483baa3c0
Revises: 60ffea5faba9
Create Date: 2026-02-24 13:18:29.807664
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3d1483baa3c0"
down_revision: Union[str, None] = "60ffea5faba9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("cash_in_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("card_in_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("click_payme_in_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("bonus_spent_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("cash_exp_company_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.add_column(
        "daily_cashbox_entries",
        sa.Column("cash_exp_other_uzs", sa.Numeric(15, 0), nullable=False, server_default="0"),
    )
    op.alter_column(
        "daily_cashbox_entries",
        "amount_uzs",
        existing_type=sa.Numeric(15, 0),
        nullable=True,
    )

    # если раньше amount_uzs был общей суммой (обычно наличные) — переносим в cash_in_uzs
    op.execute("UPDATE daily_cashbox_entries SET cash_in_uzs = COALESCE(amount_uzs, 0)")


def downgrade() -> None:
    # откат: удаляем новые колонки (amount_uzs НЕ трогаем)
    op.drop_column("daily_cashbox_entries", "cash_exp_other_uzs")
    op.drop_column("daily_cashbox_entries", "cash_exp_company_uzs")
    op.drop_column("daily_cashbox_entries", "bonus_spent_uzs")
    op.drop_column("daily_cashbox_entries", "click_payme_in_uzs")
    op.drop_column("daily_cashbox_entries", "card_in_uzs")
    op.drop_column("daily_cashbox_entries", "cash_in_uzs")