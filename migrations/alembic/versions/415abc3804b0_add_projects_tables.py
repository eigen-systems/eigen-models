"""add_projects_tables

Revision ID: 415abc3804b0
Revises: a1b2c3d4e5f6
Create Date: 2025-12-19 16:58:33.774490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '415abc3804b0'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for project'),
    sa.Column('title', sa.String(length=255), nullable=False, comment='Project title'),
    sa.Column('description', sa.Text(), nullable=True, comment='Project description'),
    sa.Column('owner_id', sa.String(length=255), nullable=False, comment='Foreign key to users table (project owner)'),
    sa.Column('visibility', sa.String(length=20), nullable=False, comment="Project visibility: 'public' or 'private'"),
    sa.Column('status', sa.String(length=20), nullable=False, comment="Project status: 'active', 'archived', or 'deleted'"),
    sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of file attachments (URLs and metadata)'),
    sa.Column('links', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of link objects: {title, url, type}'),
    sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True, comment='Array of tags for project categorization'),
    sa.Column('skills', postgresql.ARRAY(sa.Text()), nullable=True, comment='Array of skills related to the project'),
    sa.Column('allow_join_requests', sa.Boolean(), nullable=True, comment='Whether public projects accept join requests'),
    sa.Column('require_approval', sa.Boolean(), nullable=True, comment='Whether join requests require admin approval'),
    sa.Column('max_members', sa.Integer(), nullable=True, comment='Optional maximum number of members'),
    sa.Column('member_count', sa.Integer(), nullable=True, comment='Current number of members (including owner)'),
    sa.Column('is_featured', sa.Boolean(), nullable=True, comment='Whether project is featured'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the project was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the project was last updated'),
    sa.CheckConstraint("status IN ('active', 'archived', 'deleted')", name=op.f('ck_projects_ck_project_status')),
    sa.CheckConstraint("visibility IN ('public', 'private')", name=op.f('ck_projects_ck_project_visibility')),
    sa.ForeignKeyConstraint(['owner_id'], ['users.clerk_user_id'], name=op.f('projects_owner_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_projects')),
    comment='Projects for collaborative workspaces'
    )
    op.create_index('idx_project_created', 'projects', ['created_at'], unique=False)
    op.create_index('idx_project_owner', 'projects', ['owner_id'], unique=False)
    op.create_index('idx_project_skills', 'projects', ['skills'], unique=False, postgresql_using='gin')
    op.create_index('idx_project_status', 'projects', ['status'], unique=False)
    op.create_index('idx_project_tags', 'projects', ['tags'], unique=False, postgresql_using='gin')
    op.create_index('idx_project_visibility', 'projects', ['visibility'], unique=False)
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)

    # Create project_activities table
    op.create_table('project_activities',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for activity'),
    sa.Column('project_id', sa.Integer(), nullable=False, comment='Foreign key to projects table'),
    sa.Column('user_id', sa.String(length=255), nullable=True, comment='Foreign key to users table (action performer)'),
    sa.Column('activity_type', sa.String(length=50), nullable=False, comment="Type of activity (e.g., 'member_joined', 'updated')"),
    sa.Column('description', sa.Text(), nullable=True, comment='Human-readable description of the activity'),
    sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional data/context for the activity'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the activity occurred'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_activities_project_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_activities_user_id_fkey'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_activities')),
    comment='Activity log for project events'
    )
    op.create_index('idx_activity_created', 'project_activities', ['created_at'], unique=False)
    op.create_index('idx_activity_project', 'project_activities', ['project_id'], unique=False)
    op.create_index('idx_activity_project_created', 'project_activities', ['project_id', 'created_at'], unique=False)
    op.create_index('idx_activity_type', 'project_activities', ['activity_type'], unique=False)
    op.create_index('idx_activity_user', 'project_activities', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_activities_id'), 'project_activities', ['id'], unique=False)
    op.create_index(op.f('ix_project_activities_project_id'), 'project_activities', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_activities_user_id'), 'project_activities', ['user_id'], unique=False)

    # Create project_invitations table
    op.create_table('project_invitations',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for invitation'),
    sa.Column('project_id', sa.Integer(), nullable=False, comment='Foreign key to projects table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table (invitee)'),
    sa.Column('invited_by', sa.String(length=255), nullable=True, comment='Foreign key to users table (inviter)'),
    sa.Column('role', sa.String(length=20), nullable=False, comment="Role being offered: 'admin', 'editor', 'viewer'"),
    sa.Column('message', sa.Text(), nullable=True, comment='Personal message from the inviter'),
    sa.Column('status', sa.String(length=20), nullable=False, comment="Invitation status: 'pending', 'accepted', 'declined', 'expired', 'cancelled'"),
    sa.Column('expires_at', sa.DateTime(), nullable=True, comment='When the invitation expires'),
    sa.Column('responded_at', sa.DateTime(), nullable=True, comment='When the invitee responded'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the invitation was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the invitation was last updated'),
    sa.CheckConstraint("role IN ('admin', 'editor', 'viewer')", name=op.f('ck_project_invitations_ck_invitation_role')),
    sa.CheckConstraint("status IN ('pending', 'accepted', 'declined', 'expired', 'cancelled')", name=op.f('ck_project_invitations_ck_invitation_status')),
    sa.ForeignKeyConstraint(['invited_by'], ['users.clerk_user_id'], name=op.f('project_invitations_invited_by_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_invitations_project_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_invitations_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_invitations')),
    comment='Invitations to join projects'
    )
    op.create_index('idx_invitation_pending', 'project_invitations', ['user_id', 'status'], unique=False)
    op.create_index('idx_invitation_project', 'project_invitations', ['project_id'], unique=False)
    op.create_index('idx_invitation_status', 'project_invitations', ['status'], unique=False)
    op.create_index('idx_invitation_user', 'project_invitations', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_invitations_id'), 'project_invitations', ['id'], unique=False)
    op.create_index(op.f('ix_project_invitations_invited_by'), 'project_invitations', ['invited_by'], unique=False)
    op.create_index(op.f('ix_project_invitations_project_id'), 'project_invitations', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_invitations_user_id'), 'project_invitations', ['user_id'], unique=False)

    # Create project_join_requests table
    op.create_table('project_join_requests',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for join request'),
    sa.Column('project_id', sa.Integer(), nullable=False, comment='Foreign key to projects table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table (requester)'),
    sa.Column('message', sa.Text(), nullable=True, comment='Optional message from the requester'),
    sa.Column('status', sa.String(length=20), nullable=False, comment="Request status: 'pending', 'approved', 'rejected', 'cancelled'"),
    sa.Column('requested_role', sa.String(length=20), nullable=True, comment='Role the user is requesting'),
    sa.Column('reviewed_by', sa.String(length=255), nullable=True, comment='Admin who reviewed the request'),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True, comment='When the request was reviewed'),
    sa.Column('rejection_reason', sa.Text(), nullable=True, comment='Reason for rejection (if rejected)'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the request was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the request was last updated'),
    sa.CheckConstraint("requested_role IN ('admin', 'editor', 'viewer')", name=op.f('ck_project_join_requests_ck_requested_role')),
    sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'cancelled')", name=op.f('ck_project_join_requests_ck_request_status')),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_join_requests_project_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.clerk_user_id'], name=op.f('project_join_requests_reviewed_by_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_join_requests_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_join_requests')),
    comment='Join requests for public projects'
    )
    op.create_index('idx_request_pending', 'project_join_requests', ['project_id', 'status'], unique=False)
    op.create_index('idx_request_project', 'project_join_requests', ['project_id'], unique=False)
    op.create_index('idx_request_status', 'project_join_requests', ['status'], unique=False)
    op.create_index('idx_request_user', 'project_join_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_join_requests_id'), 'project_join_requests', ['id'], unique=False)
    op.create_index(op.f('ix_project_join_requests_project_id'), 'project_join_requests', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_join_requests_user_id'), 'project_join_requests', ['user_id'], unique=False)

    # Create project_members table
    op.create_table('project_members',
    sa.Column('id', sa.Integer(), nullable=False, comment='Primary key for project member'),
    sa.Column('project_id', sa.Integer(), nullable=False, comment='Foreign key to projects table'),
    sa.Column('user_id', sa.String(length=255), nullable=False, comment='Foreign key to users table'),
    sa.Column('role', sa.String(length=20), nullable=False, comment="Member role: 'owner', 'admin', 'editor', 'viewer'"),
    sa.Column('joined_via', sa.String(length=30), nullable=True, comment="How the member joined: 'invitation', 'request', 'direct'"),
    sa.Column('invited_by', sa.String(length=255), nullable=True, comment='User who invited or approved this member'),
    sa.Column('notifications_enabled', sa.Boolean(), nullable=True, comment='Whether member receives project notifications'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the membership was created'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the membership was last updated'),
    sa.CheckConstraint("role IN ('owner', 'admin', 'editor', 'viewer')", name=op.f('ck_project_members_ck_member_role')),
    sa.ForeignKeyConstraint(['invited_by'], ['users.clerk_user_id'], name=op.f('project_members_invited_by_fkey'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_members_project_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.clerk_user_id'], name=op.f('project_members_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_members')),
    sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member'),
    comment='Project membership with roles'
    )
    op.create_index('idx_member_project', 'project_members', ['project_id'], unique=False)
    op.create_index('idx_member_role', 'project_members', ['role'], unique=False)
    op.create_index('idx_member_user', 'project_members', ['user_id'], unique=False)
    op.create_index(op.f('ix_project_members_id'), 'project_members', ['id'], unique=False)
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop project_members table
    op.drop_index(op.f('ix_project_members_user_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_project_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_id'), table_name='project_members')
    op.drop_index('idx_member_user', table_name='project_members')
    op.drop_index('idx_member_role', table_name='project_members')
    op.drop_index('idx_member_project', table_name='project_members')
    op.drop_table('project_members')

    # Drop project_join_requests table
    op.drop_index(op.f('ix_project_join_requests_user_id'), table_name='project_join_requests')
    op.drop_index(op.f('ix_project_join_requests_project_id'), table_name='project_join_requests')
    op.drop_index(op.f('ix_project_join_requests_id'), table_name='project_join_requests')
    op.drop_index('idx_request_user', table_name='project_join_requests')
    op.drop_index('idx_request_status', table_name='project_join_requests')
    op.drop_index('idx_request_project', table_name='project_join_requests')
    op.drop_index('idx_request_pending', table_name='project_join_requests')
    op.drop_table('project_join_requests')

    # Drop project_invitations table
    op.drop_index(op.f('ix_project_invitations_user_id'), table_name='project_invitations')
    op.drop_index(op.f('ix_project_invitations_project_id'), table_name='project_invitations')
    op.drop_index(op.f('ix_project_invitations_invited_by'), table_name='project_invitations')
    op.drop_index(op.f('ix_project_invitations_id'), table_name='project_invitations')
    op.drop_index('idx_invitation_user', table_name='project_invitations')
    op.drop_index('idx_invitation_status', table_name='project_invitations')
    op.drop_index('idx_invitation_project', table_name='project_invitations')
    op.drop_index('idx_invitation_pending', table_name='project_invitations')
    op.drop_table('project_invitations')

    # Drop project_activities table
    op.drop_index(op.f('ix_project_activities_user_id'), table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_project_id'), table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_id'), table_name='project_activities')
    op.drop_index('idx_activity_user', table_name='project_activities')
    op.drop_index('idx_activity_type', table_name='project_activities')
    op.drop_index('idx_activity_project_created', table_name='project_activities')
    op.drop_index('idx_activity_project', table_name='project_activities')
    op.drop_index('idx_activity_created', table_name='project_activities')
    op.drop_table('project_activities')

    # Drop projects table
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index('idx_project_visibility', table_name='projects')
    op.drop_index('idx_project_tags', table_name='projects', postgresql_using='gin')
    op.drop_index('idx_project_status', table_name='projects')
    op.drop_index('idx_project_skills', table_name='projects', postgresql_using='gin')
    op.drop_index('idx_project_owner', table_name='projects')
    op.drop_index('idx_project_created', table_name='projects')
    op.drop_table('projects')
