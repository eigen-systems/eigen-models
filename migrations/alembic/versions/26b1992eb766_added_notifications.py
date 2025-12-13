"""added_notifications

Revision ID: 26b1992eb766
Revises: d22448dad35e
Create Date: 2025-12-13 18:35:26.771286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '26b1992eb766'
down_revision: Union[str, None] = 'd22448dad35e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.String(length=255), nullable=False, comment='User who receives the notification'),
    sa.Column('actor_id', sa.String(length=255), nullable=True, comment='User who triggered the notification'),
    sa.Column('notification_type', sa.Enum('FOLLOW', 'LIKE', 'COMMENT', 'MENTION', 'REPLY', 'INVITE', 'MESSAGE', 'SYSTEM', 'APPLICATION', name='notificationtype'), nullable=False, comment='Type of notification'),
    sa.Column('title', sa.String(length=255), nullable=True, comment='Short title for the notification'),
    sa.Column('content', sa.Text(), nullable=False, comment='Notification message content'),
    sa.Column('entity_type', sa.String(length=50), nullable=True, comment='Type of related entity (post, comment, user, etc.)'),
    sa.Column('entity_id', sa.String(length=255), nullable=True, comment='ID of the related entity'),
    sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional notification data'),
    sa.Column('is_read', sa.Boolean(), nullable=False, comment='Whether the notification has been read'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('read_at', sa.DateTime(), nullable=True, comment='When the notification was read'),
    sa.ForeignKeyConstraint(['actor_id'], ['users.clerk_user_id'], name=op.f('notifications_actor_id_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.clerk_user_id'], name=op.f('notifications_recipient_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications')),
    comment='User notifications for various platform events'
    )
    op.create_index('idx_notification_recipient_created', 'notifications', ['recipient_id', 'created_at'], unique=False)
    op.create_index('idx_notification_recipient_unread', 'notifications', ['recipient_id', 'is_read'], unique=False)
    op.create_index('idx_notification_type_created', 'notifications', ['notification_type', 'created_at'], unique=False)
    op.create_index(op.f('ix_notifications_actor_id'), 'notifications', ['actor_id'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_notification_type'), 'notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notifications_recipient_id'), 'notifications', ['recipient_id'], unique=False)


def downgrade() -> None:
    # Drop notifications table and its indexes
    op.drop_index(op.f('ix_notifications_recipient_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_notification_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_actor_id'), table_name='notifications')
    op.drop_index('idx_notification_type_created', table_name='notifications')
    op.drop_index('idx_notification_recipient_unread', table_name='notifications')
    op.drop_index('idx_notification_recipient_created', table_name='notifications')
    op.drop_table('notifications')

    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS notificationtype')
