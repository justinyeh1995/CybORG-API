"""Add steps in gamesummary

Revision ID: 2e999cfc4108
Revises: bca9d3dc72a0
Create Date: 2024-10-25 22:51:38.455189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e999cfc4108'
down_revision: Union[str, None] = 'bca9d3dc72a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass