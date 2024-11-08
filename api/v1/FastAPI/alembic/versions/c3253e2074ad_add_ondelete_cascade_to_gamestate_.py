"""Add ondelete cascade to GameState foreign key

Revision ID: c3253e2074ad
Revises: d1579c4b8616
Create Date: 2024-11-08 20:47:39.295807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3253e2074ad'
down_revision: Union[str, None] = 'd1579c4b8616'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add `ondelete="CASCADE"` constraint to `game_id` foreign key in `game_states` table
    op.drop_constraint('game_states_game_id_fkey', 'game_states', type_='foreignkey')
    op.create_foreign_key(
        None, 'game_states', 'game_configurations', ['game_id'], ['game_id'], ondelete='CASCADE'
    )

    # Add `ondelete="CASCADE"` constraint to `game_id` foreign key in `game_summary` table
    op.drop_constraint('game_summary_game_id_fkey', 'game_summary', type_='foreignkey')
    op.create_foreign_key(
        None, 'game_summary', 'game_configurations', ['game_id'], ['game_id'], ondelete='CASCADE'
    )

    # Add `ondelete="CASCADE"` constraint to `user_id` foreign key in `game_configurations` table
    op.drop_constraint('game_configurations_user_id_fkey', 'game_configurations', type_='foreignkey')
    op.create_foreign_key(
        None, 'game_configurations', 'users', ['user_id'], ['user_id'], ondelete='CASCADE'
    )

def downgrade():
    # Remove `ondelete="CASCADE"` from `game_states` table
    op.drop_constraint(None, 'game_states', type_='foreignkey')
    op.create_foreign_key(
        'game_states_game_id_fkey', 'game_states', 'game_configurations', ['game_id'], ['game_id']
    )

    # Remove `ondelete="CASCADE"` from `game_summary` table
    op.drop_constraint(None, 'game_summary', type_='foreignkey')
    op.create_foreign_key(
        'game_summary_game_id_fkey', 'game_summary', 'game_configurations', ['game_id'], ['game_id']
    )

    # Remove `ondelete="CASCADE"` from `game_configurations` table
    op.drop_constraint(None, 'game_configurations', type_='foreignkey')
    op.create_foreign_key(
        'game_configurations_user_id_fkey', 'game_configurations', 'users', ['user_id'], ['user_id']
    )