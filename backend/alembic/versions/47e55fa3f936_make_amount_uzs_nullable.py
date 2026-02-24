"""make amount_uzs nullable

Revision ID: 47e55fa3f936
Revises: db30a3cac8c1
Create Date: 2026-02-24 15:37:36.970294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47e55fa3f936'
down_revision: Union[str, None] = 'db30a3cac8c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
