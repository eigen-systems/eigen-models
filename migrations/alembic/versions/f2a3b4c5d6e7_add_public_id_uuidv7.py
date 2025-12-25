"""add_public_id_uuidv7

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2025-12-25 12:00:00.000000

Phase 1: Adds public_id (nullable) to group_messages and last_seen_public_id to project_group_members.
UUIDv7 is used for client-side message identification and cursor-based sync.

IMPORTANT: After running this migration, run the data migration script:
    python db_models/scripts/migrate_public_ids_to_uuidv7.py

Then run the follow-up migration (g3b4c5d6e7f8) to make the column non-nullable.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add public_id column as nullable (for existing data migration)
    op.add_column('group_messages',
        sa.Column('public_id', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='Public UUIDv7 identifier for client-side operations'))

    # Step 2: Add last_seen_public_id to project_group_members
    op.add_column('project_group_members',
        sa.Column('last_seen_public_id', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='Last message public_id seen by user for sync cursor'))

    # NOTE: After this migration:
    # 1. Run: python db_models/scripts/migrate_public_ids_to_uuidv7.py
    # 2. Then run: alembic upgrade head (for g3b4c5d6e7f8 migration)


def downgrade() -> None:
    # Remove last_seen_public_id from project_group_members
    op.drop_column('project_group_members', 'last_seen_public_id')

    # Remove public_id column from group_messages
    op.drop_column('group_messages', 'public_id')
