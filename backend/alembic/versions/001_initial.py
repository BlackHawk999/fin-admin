"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("monthly_salary_uzs", sa.Numeric(15, 0), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "advances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount_uzs", sa.Numeric(15, 0), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "company_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount_uzs", sa.Numeric(15, 0), nullable=False),
        sa.Column("direction", sa.Enum("OUT", "IN", name="transactiondirection"), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cashboxes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cashboxes_name", "cashboxes", ["name"], unique=True)

    op.create_table(
        "daily_cashbox_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cashbox_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount_uzs", sa.Numeric(15, 0), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(["cashbox_id"], ["cashboxes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "owners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("color_hex", sa.String(7), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount_uzs", sa.Numeric(15, 0), nullable=False),
        sa.Column("category", sa.String(255), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.Column("payer_type", sa.Enum("owner", "other", name="payertype"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["owners.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("expenses")
    op.drop_table("owners")
    op.drop_table("daily_cashbox_entries")
    op.drop_table("cashboxes")
    op.drop_table("company_transactions")
    op.drop_table("companies")
    op.drop_table("advances")
    op.drop_table("employees")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS payertype")
    op.execute("DROP TYPE IF EXISTS transactiondirection")
