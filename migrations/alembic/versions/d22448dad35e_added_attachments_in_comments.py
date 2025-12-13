"""added_attachments_in_comments

Revision ID: d22448dad35e
Revises: c3d4e5f6a7b8
Create Date: 2025-12-13 16:40:24.646758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd22448dad35e'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add attachments column to comments table
    op.add_column('comments', sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove attachments column from comments table
    op.drop_column('comments', 'attachments')
