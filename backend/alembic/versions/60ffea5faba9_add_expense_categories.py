"""add expense categories

Revision ID: 60ffea5faba9
Revises: 70f29fdb45ad
Create Date: 2026-02-11 19:32:17.799530
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "60ffea5faba9"
down_revision: Union[str, None] = "70f29fdb45ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ ONLY expense_categories table + indexes
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_expense_categories_id", "expense_categories", ["id"], unique=False)
    op.create_index("ix_expense_categories_name", "expense_categories", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_expense_categories_name", table_name="expense_categories")
    op.drop_index("ix_expense_categories_id", table_name="expense_categories")
    op.drop_table("expense_categories")
