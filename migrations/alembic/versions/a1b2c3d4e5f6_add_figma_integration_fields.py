"""add_figma_integration_fields

Revision ID: a1b2c3d4e5f6
Revises: 68771abc7470
Create Date: 2025-12-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '68771abc7470'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Figma integration fields to profiles table
    op.add_column('profiles', sa.Column('figma_connected', sa.Boolean(), nullable=False, server_default='false', comment='Whether Figma account is connected'))
    op.add_column('profiles', sa.Column('figma_username', sa.Text(), nullable=True, comment='Figma username/handle if connected'))
    op.add_column('profiles', sa.Column('figma_user_id', sa.Text(), nullable=True, comment='Figma user ID if connected'))
    op.add_column('profiles', sa.Column('figma_email', sa.Text(), nullable=True, comment='Figma email if connected'))
    op.add_column('profiles', sa.Column('figma_access_token', sa.Text(), nullable=True, comment='Figma OAuth access token'))
    op.add_column('profiles', sa.Column('figma_refresh_token', sa.Text(), nullable=True, comment='Figma OAuth refresh token'))
    op.add_column('profiles', sa.Column('figma_token_expires_at', sa.DateTime(), nullable=True, comment='When Figma access token expires'))
    op.add_column('profiles', sa.Column('figma_last_synced', sa.DateTime(), nullable=True, comment='Timestamp of last Figma sync'))

    # Add index for Figma user ID
    op.create_index('idx_profile_figma_user_id', 'profiles', ['figma_user_id'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index('idx_profile_figma_user_id', table_name='profiles')

    # Remove Figma columns
    op.drop_column('profiles', 'figma_last_synced')
    op.drop_column('profiles', 'figma_token_expires_at')
    op.drop_column('profiles', 'figma_refresh_token')
    op.drop_column('profiles', 'figma_access_token')
    op.drop_column('profiles', 'figma_email')
    op.drop_column('profiles', 'figma_user_id')
    op.drop_column('profiles', 'figma_username')
    op.drop_column('profiles', 'figma_connected')
