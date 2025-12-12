"""add_comments_table

Revision ID: c3d4e5f6a7b8
Revises: 2421de911768
Create Date: 2025-12-12 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = '2421de911768'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create comments table only - don't touch other tables
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='comments_post_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name='comments_user_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], name='comments_parent_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_comments')
    )
    op.create_index('idx_comment_post', 'comments', ['post_id'], unique=False)
    op.create_index('idx_comment_user', 'comments', ['user_id'], unique=False)
    op.create_index('idx_comment_parent', 'comments', ['parent_id'], unique=False)
    op.create_index('idx_comment_created', 'comments', ['created_at'], unique=False)
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_comments_id', table_name='comments')
    op.drop_index('idx_comment_created', table_name='comments')
    op.drop_index('idx_comment_parent', table_name='comments')
    op.drop_index('idx_comment_user', table_name='comments')
    op.drop_index('idx_comment_post', table_name='comments')
    op.drop_table('comments')
