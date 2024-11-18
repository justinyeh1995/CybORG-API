"""Alter column name username -> full_name in staging db

Revision ID: 5940fde1da7e
Revises: da3b7120165e
Create Date: 2024-11-18 22:03:33.287997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5940fde1da7e'
down_revision: Union[str, None] = 'da3b7120165e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(table_name='users', column_name="username", new_column_name="full_name")


def downgrade() -> None:
    op.alter_column(table_name='users', column_name="full_name", new_column_name="username")
