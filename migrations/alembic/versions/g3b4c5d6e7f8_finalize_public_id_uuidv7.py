"""finalize_public_id_uuidv7

Revision ID: g3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2025-12-25 12:30:00.000000

Phase 2: Makes public_id non-nullable and adds unique constraint and indexes.

PREREQUISITE: Before running this migration, ensure you have:
1. Run the first migration (f2a3b4c5d6e7)
2. Run the data migration script: python db_models/scripts/migrate_public_ids_to_uuidv7.py
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g3b4c5d6e7f8'
down_revision: Union[str, None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verify all messages have public_id before proceeding
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM group_messages WHERE public_id IS NULL"))
    null_count = result.scalar()

    if null_count > 0:
        raise Exception(
            f"Cannot finalize migration: {null_count} messages still have NULL public_id. "
            "Please run the data migration script first: "
            "python db_models/scripts/migrate_public_ids_to_uuidv7.py"
        )

    # Step 1: Make column non-nullable
    op.alter_column('group_messages', 'public_id', nullable=False)

    # Step 2: Add unique constraint
    op.create_unique_constraint('uq_group_message_public_id', 'group_messages', ['public_id'])

    # Step 3: Add indexes
    op.create_index('idx_group_message_public_id', 'group_messages', ['public_id'], unique=True)
    op.create_index('idx_group_message_group_public', 'group_messages', ['group_id', 'public_id'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('idx_group_message_group_public', table_name='group_messages')
    op.drop_index('idx_group_message_public_id', table_name='group_messages')

    # Remove unique constraint
    op.drop_constraint('uq_group_message_public_id', 'group_messages', type_='unique')

    # Make column nullable again
    op.alter_column('group_messages', 'public_id', nullable=True)
