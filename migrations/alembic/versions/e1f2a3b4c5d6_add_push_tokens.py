"""add_push_tokens

Revision ID: e1f2a3b4c5d6
Revises: b1c2d3e4f5a6
Create Date: 2025-12-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create push_tokens table
    op.create_table('push_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False, comment='User who owns this push token'),
        sa.Column('token', sa.String(length=255), nullable=False, comment='Expo push token (ExponentPushToken[...])'),
        sa.Column('device_type', sa.String(length=50), nullable=True, comment='Device platform (ios, android)'),
        sa.Column('device_name', sa.String(length=255), nullable=True, comment='Human-readable device name'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, comment='Whether this token is currently active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True, comment='When the token was last used to send a notification'),
        sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('push_tokens_user_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_push_tokens')),
        sa.UniqueConstraint('token', name=op.f('uq_push_tokens_token')),
        comment='Expo push notification tokens for mobile devices'
    )
    # Create indexes
    op.create_index('idx_push_token_user_active', 'push_tokens', ['user_id', 'is_active'], unique=False)
    op.create_index(op.f('ix_push_tokens_id'), 'push_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_push_tokens_user_id'), 'push_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_push_tokens_token'), 'push_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_push_tokens_is_active'), 'push_tokens', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop push_tokens table and its indexes
    op.drop_index(op.f('ix_push_tokens_is_active'), table_name='push_tokens')
    op.drop_index(op.f('ix_push_tokens_token'), table_name='push_tokens')
    op.drop_index(op.f('ix_push_tokens_user_id'), table_name='push_tokens')
    op.drop_index(op.f('ix_push_tokens_id'), table_name='push_tokens')
    op.drop_index('idx_push_token_user_active', table_name='push_tokens')
    op.drop_table('push_tokens')
