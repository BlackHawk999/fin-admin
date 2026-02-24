"""split cashbox entry fields

Revision ID: db30a3cac8c1
Revises: 3d1483baa3c0
Create Date: 2026-02-24 13:30:13.481665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db30a3cac8c1'
down_revision: Union[str, None] = '3d1483baa3c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
