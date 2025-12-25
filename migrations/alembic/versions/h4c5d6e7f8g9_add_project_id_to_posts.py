"""add_project_id_to_posts

Revision ID: h4c5d6e7f8g9
Revises: g3b4c5d6e7f8
Create Date: 2025-12-25 14:00:00.000000

Adds project_id foreign key to posts table for linking posts to projects.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h4c5d6e7f8g9'
down_revision: Union[str, None] = 'g3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add project_id column to posts table
    op.add_column('posts',
        sa.Column('project_id', sa.Integer(), nullable=True,
                  comment='Linked project for the post'))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_post_project_id',
        'posts',
        'projects',
        ['project_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Add index for project_id lookups
    op.create_index('idx_post_project_id', 'posts', ['project_id'])


def downgrade() -> None:
    # Remove index
    op.drop_index('idx_post_project_id', table_name='posts')

    # Remove foreign key constraint
    op.drop_constraint('fk_post_project_id', 'posts', type_='foreignkey')

    # Remove column
    op.drop_column('posts', 'project_id')
