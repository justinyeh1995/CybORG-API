"""Add createAt in game_configurations

Revision ID: 97c6165b9ff0
Revises: 2e999cfc4108
Create Date: 2024-10-28 20:24:48.684656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97c6165b9ff0'
down_revision: Union[str, None] = '2e999cfc4108'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column(
        'game_configurations',
        sa.Column(
            'createdAt',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )
    
def downgrade() -> None:
    op.drop_column('game_configurations', 'createdAt')
    
