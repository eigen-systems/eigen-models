"""
Project group member model for the Eigen platform.

This module contains the ProjectGroupMember model for tracking membership
in project groups with role-based access control.
"""

import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectGroupMember(Base):
    """
    Project group member model representing membership in project groups.

    Each member has a role that determines their permissions within the group.
    Roles: admin, member.

    Note: Project owners/admins automatically have admin rights in all groups.

    Attributes:
        id: Primary key integer field
        group_id: Foreign key to project_groups table
        user_id: Foreign key to users table
        role: Member role ('admin', 'member')
        joined_via: How they joined ('auto', 'direct', 'request')
        notifications_enabled: Whether member receives group notifications
        last_read_at: Last time user read messages in this group
        created_at: When the membership was created
        updated_at: When the membership was last updated
    """

    __tablename__ = "project_group_members"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for group member"
    )

    # Group reference
    group_id = Column(
        Integer,
        ForeignKey("project_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to project_groups table"
    )

    # User reference
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )

    # Role: 'admin', 'member'
    role = Column(
        String(20),
        nullable=False,
        default="member",
        comment="Member role: 'admin', 'member'"
    )

    # How they joined: 'auto', 'direct', 'request'
    joined_via = Column(
        String(30),
        nullable=False,
        default="direct",
        comment="How the member joined: 'auto', 'direct', 'request'"
    )

    # Member-specific settings
    notifications_enabled = Column(
        Boolean,
        default=True,
        comment="Whether member receives group notifications"
    )

    # Last read timestamp for unread tracking
    last_read_at = Column(
        DateTime,
        nullable=True,
        comment="Last time user read messages in this group"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the membership was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the membership was last updated"
    )

    # Relationships
    group = relationship(
        "ProjectGroup",
        back_populates="members"
    )
    user = relationship(
        "User",
        back_populates="group_memberships",
        foreign_keys=[user_id]
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'member')",
            name="ck_group_member_role"
        ),
        CheckConstraint(
            "joined_via IN ('auto', 'direct', 'request')",
            name="ck_group_member_joined_via"
        ),
        UniqueConstraint(
            "group_id", "user_id",
            name="uq_group_member"
        ),
        Index("idx_group_member_group", "group_id"),
        Index("idx_group_member_user", "user_id"),
        Index("idx_group_member_role", "role"),
        {"comment": "Project group membership"},
    )

    def __repr__(self) -> str:
        return f"<ProjectGroupMember(id={self.id}, group_id={self.group_id}, user_id='{self.user_id}', role='{self.role}')>"

    def to_dict(self) -> dict:
        """Convert group member to dictionary for API responses."""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_via": self.joined_via,
            "notifications_enabled": self.notifications_enabled,
            "last_read_at": self.last_read_at.isoformat() if self.last_read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
