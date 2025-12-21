"""add_project_groups

Revision ID: b1c2d3e4f5a6
Revises: 415abc3804b0
Create Date: 2025-12-21

This migration adds:
- project_groups: Chat groups within projects
- project_group_members: Group membership with roles
- project_group_join_requests: Join requests for private groups
- group_messages: Chat messages in groups
- message_reactions: Emoji reactions on messages
- message_read_status: Read receipts for messages
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = '415abc3804b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create project_groups table
    op.create_table('project_groups',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for project group'),
    sa.Column('project_id', sa.Integer(), nullable=False, comment='Foreign key to projects table'),
    sa.Column('name', sa.String(length=255), nullable=False, comment='Group name'),
    sa.Column('description', sa.Text(), nullable=True, comment='Group description'),
    sa.Column('visibility', sa.String(length=20), nullable=False, comment="Group visibility within project: 'public' or 'private'"),
    sa.Column('show_to_non_members', sa.Boolean(), nullable=True, default=True, comment='Whether private groups appear in list for non-members'),
    sa.Column('is_default', sa.Boolean(), nullable=True, default=False, comment='Whether this is the auto-created default group'),
    sa.Column('created_by', sa.String(length=255), nullable=True, comment='User who created this group'),
    sa.Column('member_count', sa.Integer(), nullable=True, default=0, comment='Current number of members in the group'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the group was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the group was last updated'),
    sa.CheckConstraint("visibility IN ('public', 'private')", name=op.f('ck_project_groups_ck_group_visibility')),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_groups_project_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['created_by'], ['users.clerk_user_id'], name=op.f('project_groups_created_by_fkey'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_groups')),
    comment='Project groups for team communication'
    )
    op.create_index('idx_group_project', 'project_groups', ['project_id'], unique=False)
    op.create_index('idx_group_visibility', 'project_groups', ['visibility'], unique=False)
    op.create_index('idx_group_is_default', 'project_groups', ['is_default'], unique=False)
    op.create_index('idx_group_created', 'project_groups', ['created_at'], unique=False)
    op.create_index(op.f('ix_project_groups_id'), 'project_groups', ['id'], unique=False)
    op.create_index(op.f('ix_project_groups_project_id'), 'project_groups', ['project_id'], unique=False)

    # Create project_group_members table
    op.create_table('project_group_members',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for group member'),
    sa.Column('group_id', sa.Integer(), nullable=False, comment='Foreign key to project_groups table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table'),
    sa.Column('role', sa.String(length=20), nullable=False, comment="Member role: 'admin', 'member'"),
    sa.Column('joined_via', sa.String(length=30), nullable=False, comment="How the member joined: 'auto', 'direct', 'request'"),
    sa.Column('notifications_enabled', sa.Boolean(), nullable=True, default=True, comment='Whether member receives group notifications'),
    sa.Column('last_read_at', sa.DateTime(), nullable=True, comment='Last time user read messages in this group'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the membership was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the membership was last updated'),
    sa.CheckConstraint("role IN ('admin', 'member')", name=op.f('ck_project_group_members_ck_group_member_role')),
    sa.CheckConstraint("joined_via IN ('auto', 'direct', 'request')", name=op.f('ck_project_group_members_ck_group_member_joined_via')),
    sa.ForeignKeyConstraint(['group_id'], ['project_groups.id'], name=op.f('project_group_members_group_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_group_members_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_group_members')),
    sa.UniqueConstraint('group_id', 'user_id', name='uq_group_member'),
    comment='Project group membership'
    )
    op.create_index('idx_group_member_group', 'project_group_members', ['group_id'], unique=False)
    op.create_index('idx_group_member_user', 'project_group_members', ['user_id'], unique=False)
    op.create_index('idx_group_member_role', 'project_group_members', ['role'], unique=False)
    op.create_index(op.f('ix_project_group_members_id'), 'project_group_members', ['id'], unique=False)
    op.create_index(op.f('ix_project_group_members_group_id'), 'project_group_members', ['group_id'], unique=False)
    op.create_index(op.f('ix_project_group_members_user_id'), 'project_group_members', ['user_id'], unique=False)

    # Create project_group_join_requests table
    op.create_table('project_group_join_requests',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for group join request'),
    sa.Column('group_id', sa.Integer(), nullable=False, comment='Foreign key to project_groups table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table (requester)'),
    sa.Column('message', sa.Text(), nullable=True, comment='Optional message from requester'),
    sa.Column('status', sa.String(length=20), nullable=False, comment="Request status: 'pending', 'approved', 'rejected', 'cancelled'"),
    sa.Column('reviewed_by', sa.String(length=255), nullable=True, comment='User who reviewed the request'),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True, comment='When the request was reviewed'),
    sa.Column('rejection_reason', sa.Text(), nullable=True, comment='Reason for rejection (if rejected)'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the request was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the request was last updated'),
    sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'cancelled')", name=op.f('ck_project_group_join_requests_ck_group_join_request_status')),
    sa.ForeignKeyConstraint(['group_id'], ['project_groups.id'], name=op.f('project_group_join_requests_group_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_group_join_requests_user_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.clerk_user_id'], name=op.f('project_group_join_requests_reviewed_by_fkey'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_group_join_requests')),
    comment='Join requests for private groups'
    )
    op.create_index('idx_group_join_request_group', 'project_group_join_requests', ['group_id'], unique=False)
    op.create_index('idx_group_join_request_user', 'project_group_join_requests', ['user_id'], unique=False)
    op.create_index('idx_group_join_request_status', 'project_group_join_requests', ['status'], unique=False)
    op.create_index('idx_group_join_request_pending', 'project_group_join_requests', ['group_id', 'status'], unique=False)
    op.create_index(op.f('ix_project_group_join_requests_id'), 'project_group_join_requests', ['id'], unique=False)
    op.create_index(op.f('ix_project_group_join_requests_group_id'), 'project_group_join_requests', ['group_id'], unique=False)
    op.create_index(op.f('ix_project_group_join_requests_user_id'), 'project_group_join_requests', ['user_id'], unique=False)

    # Create group_messages table
    op.create_table('group_messages',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for group message'),
    sa.Column('group_id', sa.Integer(), nullable=False, comment='Foreign key to project_groups table'),
    sa.Column('sender_id', sa.String(length=255), nullable=True, comment='Foreign key to users table (sender)'),
    sa.Column('content', sa.Text(), nullable=True, comment='Message text content'),
    sa.Column('message_type', sa.String(length=20), nullable=False, comment="Type of message: 'text', 'image', 'file', 'system'"),
    sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of file attachments with metadata'),
    sa.Column('reply_to_id', sa.Integer(), nullable=True, comment='Reference to parent message for threading'),
    sa.Column('is_edited', sa.Boolean(), nullable=True, default=False, comment='Whether message has been edited'),
    sa.Column('edited_at', sa.DateTime(), nullable=True, comment='When message was last edited'),
    sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False, comment='Whether message has been soft deleted'),
    sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='When message was deleted'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the message was created'),
    sa.CheckConstraint("message_type IN ('text', 'image', 'file', 'system')", name=op.f('ck_group_messages_ck_group_message_type')),
    sa.ForeignKeyConstraint(['group_id'], ['project_groups.id'], name=op.f('group_messages_group_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.clerk_user_id'], name=op.f('group_messages_sender_id_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reply_to_id'], ['group_messages.id'], name=op.f('group_messages_reply_to_id_fkey'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_group_messages')),
    comment='Chat messages in project groups'
    )
    op.create_index('idx_group_message_group', 'group_messages', ['group_id'], unique=False)
    op.create_index('idx_group_message_sender', 'group_messages', ['sender_id'], unique=False)
    op.create_index('idx_group_message_created', 'group_messages', ['created_at'], unique=False)
    op.create_index('idx_group_message_reply', 'group_messages', ['reply_to_id'], unique=False)
    op.create_index('idx_group_message_group_created', 'group_messages', ['group_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_group_messages_id'), 'group_messages', ['id'], unique=False)
    op.create_index(op.f('ix_group_messages_group_id'), 'group_messages', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_messages_sender_id'), 'group_messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_group_messages_reply_to_id'), 'group_messages', ['reply_to_id'], unique=False)

    # Create message_reactions table
    op.create_table('message_reactions',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for message reaction'),
    sa.Column('message_id', sa.Integer(), nullable=False, comment='Foreign key to group_messages table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table'),
    sa.Column('emoji', sa.String(length=32), nullable=False, comment='Emoji character or shortcode'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the reaction was added'),
    sa.ForeignKeyConstraint(['message_id'], ['group_messages.id'], name=op.f('message_reactions_message_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('message_reactions_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_message_reactions')),
    sa.UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_message_reaction'),
    comment='Emoji reactions on group messages'
    )
    op.create_index('idx_reaction_message', 'message_reactions', ['message_id'], unique=False)
    op.create_index('idx_reaction_user', 'message_reactions', ['user_id'], unique=False)
    op.create_index('idx_reaction_emoji', 'message_reactions', ['emoji'], unique=False)
    op.create_index(op.f('ix_message_reactions_id'), 'message_reactions', ['id'], unique=False)
    op.create_index(op.f('ix_message_reactions_message_id'), 'message_reactions', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_reactions_user_id'), 'message_reactions', ['user_id'], unique=False)

    # Create message_read_status table
    op.create_table('message_read_status',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for read status'),
    sa.Column('message_id', sa.Integer(), nullable=False, comment='Foreign key to group_messages table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table'),
    sa.Column('read_at', sa.DateTime(), nullable=False, comment='When the message was read'),
    sa.ForeignKeyConstraint(['message_id'], ['group_messages.id'], name=op.f('message_read_status_message_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('message_read_status_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_message_read_status')),
    sa.UniqueConstraint('message_id', 'user_id', name='uq_message_read_status'),
    comment='Read receipts for group messages'
    )
    op.create_index('idx_read_status_message', 'message_read_status', ['message_id'], unique=False)
    op.create_index('idx_read_status_user', 'message_read_status', ['user_id'], unique=False)
    op.create_index('idx_read_status_read_at', 'message_read_status', ['read_at'], unique=False)
    op.create_index(op.f('ix_message_read_status_id'), 'message_read_status', ['id'], unique=False)
    op.create_index(op.f('ix_message_read_status_message_id'), 'message_read_status', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_read_status_user_id'), 'message_read_status', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop message_read_status table
    op.drop_index(op.f('ix_message_read_status_user_id'), table_name='message_read_status')
    op.drop_index(op.f('ix_message_read_status_message_id'), table_name='message_read_status')
    op.drop_index(op.f('ix_message_read_status_id'), table_name='message_read_status')
    op.drop_index('idx_read_status_read_at', table_name='message_read_status')
    op.drop_index('idx_read_status_user', table_name='message_read_status')
    op.drop_index('idx_read_status_message', table_name='message_read_status')
    op.drop_table('message_read_status')

    # Drop message_reactions table
    op.drop_index(op.f('ix_message_reactions_user_id'), table_name='message_reactions')
    op.drop_index(op.f('ix_message_reactions_message_id'), table_name='message_reactions')
    op.drop_index(op.f('ix_message_reactions_id'), table_name='message_reactions')
    op.drop_index('idx_reaction_emoji', table_name='message_reactions')
    op.drop_index('idx_reaction_user', table_name='message_reactions')
    op.drop_index('idx_reaction_message', table_name='message_reactions')
    op.drop_table('message_reactions')

    # Drop group_messages table
    op.drop_index(op.f('ix_group_messages_reply_to_id'), table_name='group_messages')
    op.drop_index(op.f('ix_group_messages_sender_id'), table_name='group_messages')
    op.drop_index(op.f('ix_group_messages_group_id'), table_name='group_messages')
    op.drop_index(op.f('ix_group_messages_id'), table_name='group_messages')
    op.drop_index('idx_group_message_group_created', table_name='group_messages')
    op.drop_index('idx_group_message_reply', table_name='group_messages')
    op.drop_index('idx_group_message_created', table_name='group_messages')
    op.drop_index('idx_group_message_sender', table_name='group_messages')
    op.drop_index('idx_group_message_group', table_name='group_messages')
    op.drop_table('group_messages')

    # Drop project_group_join_requests table
    op.drop_index(op.f('ix_project_group_join_requests_user_id'), table_name='project_group_join_requests')
    op.drop_index(op.f('ix_project_group_join_requests_group_id'), table_name='project_group_join_requests')
    op.drop_index(op.f('ix_project_group_join_requests_id'), table_name='project_group_join_requests')
    op.drop_index('idx_group_join_request_pending', table_name='project_group_join_requests')
    op.drop_index('idx_group_join_request_status', table_name='project_group_join_requests')
    op.drop_index('idx_group_join_request_user', table_name='project_group_join_requests')
    op.drop_index('idx_group_join_request_group', table_name='project_group_join_requests')
    op.drop_table('project_group_join_requests')

    # Drop project_group_members table
    op.drop_index(op.f('ix_project_group_members_user_id'), table_name='project_group_members')
    op.drop_index(op.f('ix_project_group_members_group_id'), table_name='project_group_members')
    op.drop_index(op.f('ix_project_group_members_id'), table_name='project_group_members')
    op.drop_index('idx_group_member_role', table_name='project_group_members')
    op.drop_index('idx_group_member_user', table_name='project_group_members')
    op.drop_index('idx_group_member_group', table_name='project_group_members')
    op.drop_table('project_group_members')

    # Drop project_groups table
    op.drop_index(op.f('ix_project_groups_project_id'), table_name='project_groups')
    op.drop_index(op.f('ix_project_groups_id'), table_name='project_groups')
    op.drop_index('idx_group_created', table_name='project_groups')
    op.drop_index('idx_group_is_default', table_name='project_groups')
    op.drop_index('idx_group_visibility', table_name='project_groups')
    op.drop_index('idx_group_project', table_name='project_groups')
    op.drop_table('project_groups')
