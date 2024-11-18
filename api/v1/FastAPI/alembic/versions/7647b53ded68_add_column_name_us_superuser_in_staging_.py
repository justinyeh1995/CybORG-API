"""Add column name us_superuser in staging db

Revision ID: 7647b53ded68
Revises: 5940fde1da7e
Create Date: 2024-11-18 22:12:18.106251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7647b53ded68'
down_revision: Union[str, None] = '5940fde1da7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(table_name='users', column=sa.Column('is_superuser', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column(table_name='users', column_name='is_superuser')
