"""added_user_interaction

Revision ID: 68771abc7470
Revises: 26b1992eb766
Create Date: 2025-12-16 20:34:18.982908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '68771abc7470'
down_revision: Union[str, None] = '26b1992eb766'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_interactions table for user-to-user interactions (mute, block, etc.)
    op.create_table('user_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('target_user_id', sa.String(length=255), nullable=False),
        sa.Column('interaction_type', sa.String(length=30), nullable=False),
        sa.Column('interaction_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.clerk_user_id'], name='user_interactions_target_user_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name='user_interactions_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_user_interactions'),
        sa.UniqueConstraint('user_id', 'target_user_id', 'interaction_type', name='uq_user_interaction')
    )
    op.create_index('idx_user_interaction_target', 'user_interactions', ['target_user_id'], unique=False)
    op.create_index('idx_user_interaction_type', 'user_interactions', ['interaction_type'], unique=False)
    op.create_index('idx_user_interaction_user', 'user_interactions', ['user_id'], unique=False)
    op.create_index('ix_user_interactions_id', 'user_interactions', ['id'], unique=False)


def downgrade() -> None:
    # Drop user_interactions table
    op.drop_index('ix_user_interactions_id', table_name='user_interactions')
    op.drop_index('idx_user_interaction_user', table_name='user_interactions')
    op.drop_index('idx_user_interaction_type', table_name='user_interactions')
    op.drop_index('idx_user_interaction_target', table_name='user_interactions')
    op.drop_table('user_interactions')
