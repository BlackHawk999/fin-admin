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
    bind = op.get_bind()
    dialect = bind.dialect.name  # "sqlite", "postgresql", ...

    # --- expense_categories ---
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expense_categories_id"), "expense_categories", ["id"], unique=False)
    op.create_index(op.f("ix_expense_categories_name"), "expense_categories", ["name"], unique=True)

    # --- cashbox_entry_audits ---
    # SQLite не сможет: NOT NULL + без default на существующих строках.
    # Postgres сможет, поэтому на Postgres делаем как надо.
    if dialect != "sqlite":
        # created_at NOT NULL: безопаснее дать default сейчас/или fixed, а потом снять server_default (не обязательно)
        op.add_column(
            "cashbox_entry_audits",
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        )
    else:
        # На SQLite добавим nullable=True чтобы не падало (если таблица уже есть и в ней строки)
        op.add_column("cashbox_entry_audits", sa.Column("created_at", sa.DateTime(), nullable=True))

    # Дальше все опасные ALTER COLUMN — только для НЕ sqlite
    if dialect != "sqlite":
        op.alter_column(
            "cashbox_entry_audits",
            "old_date",
            existing_type=sa.DATE(),
            nullable=False,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "old_amount_uzs",
            existing_type=sa.INTEGER(),
            type_=sa.Numeric(precision=15, scale=0),
            nullable=False,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "old_comment",
            existing_type=sa.TEXT(),
            type_=sa.String(length=500),
            existing_nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "new_date",
            existing_type=sa.DATE(),
            nullable=False,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "new_amount_uzs",
            existing_type=sa.INTEGER(),
            type_=sa.Numeric(precision=15, scale=0),
            nullable=False,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "new_comment",
            existing_type=sa.TEXT(),
            type_=sa.String(length=500),
            existing_nullable=True,
        )

    # drop edited_at (SQLite обычно умеет drop_column только в новых версиях, но alembic на sqlite часто падает)
    if dialect != "sqlite":
        op.drop_column("cashbox_entry_audits", "edited_at")

        # unique + индексы (это у тебя автоген накидал — на Postgres норм)
        op.create_unique_constraint(None, "cashboxes", ["name"])
        op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
        op.create_index(op.f("ix_company_transactions_id"), "company_transactions", ["id"], unique=False)
        op.create_index(op.f("ix_daily_cashbox_entries_id"), "daily_cashbox_entries", ["id"], unique=False)
        op.create_index(op.f("ix_employees_id"), "employees", ["id"], unique=False)
        op.create_index(op.f("ix_expenses_id"), "expenses", ["id"], unique=False)
        op.create_index(op.f("ix_owners_id"), "owners", ["id"], unique=False)
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

        # (не обязательно) можно убрать server_default после добавления created_at
        op.alter_column("cashbox_entry_audits", "created_at", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # На Postgres откатываем полноценно, на SQLite — минимально без падений
    if dialect != "sqlite":
        op.drop_index(op.f("ix_users_id"), table_name="users")
        op.drop_index(op.f("ix_owners_id"), table_name="owners")
        op.drop_index(op.f("ix_expenses_id"), table_name="expenses")
        op.drop_index(op.f("ix_employees_id"), table_name="employees")
        op.drop_index(op.f("ix_daily_cashbox_entries_id"), table_name="daily_cashbox_entries")
        op.drop_index(op.f("ix_company_transactions_id"), table_name="company_transactions")
        op.drop_index(op.f("ix_companies_id"), table_name="companies")
        op.drop_constraint(None, "cashboxes", type_="unique")

        op.add_column("cashbox_entry_audits", sa.Column("edited_at", sa.DateTime(), nullable=False))
        op.alter_column(
            "cashbox_entry_audits",
            "new_comment",
            existing_type=sa.String(length=500),
            type_=sa.TEXT(),
            existing_nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "new_amount_uzs",
            existing_type=sa.Numeric(precision=15, scale=0),
            type_=sa.INTEGER(),
            nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "new_date",
            existing_type=sa.DATE(),
            nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "old_comment",
            existing_type=sa.String(length=500),
            type_=sa.TEXT(),
            existing_nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "old_amount_uzs",
            existing_type=sa.Numeric(precision=15, scale=0),
            type_=sa.INTEGER(),
            nullable=True,
        )
        op.alter_column(
            "cashbox_entry_audits",
            "old_date",
            existing_type=sa.DATE(),
            nullable=True,
        )
        op.drop_column("cashbox_entry_audits", "created_at")
    else:
        # SQLite: максимально безопасный откат
        # created_at попробуем удалить, если не получится — просто оставим (лучше чем падать)
        try:
            op.drop_column("cashbox_entry_audits", "created_at")
        except Exception:
            pass

    op.drop_index(op.f("ix_expense_categories_name"), table_name="expense_categories")
    op.drop_index(op.f("ix_expense_categories_id"), table_name="expense_categories")
    op.drop_table("expense_categories")
