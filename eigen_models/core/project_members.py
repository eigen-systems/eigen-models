"""
Project member model for the Eigen platform.

This module contains the ProjectMember model for tracking project membership
with role-based access control.
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


class ProjectMember(Base):
    """
    Project member model representing membership in projects.

    Each member has a role that determines their permissions within the project.
    Roles: owner, admin, editor, viewer.

    Attributes:
        id: Primary key integer field
        project_id: Foreign key to projects table
        user_id: Foreign key to users table
        role: Member role ('owner', 'admin', 'editor', 'viewer')
        joined_via: How they joined ('invitation', 'request', 'direct')
        invited_by: Who invited/approved them
        notifications_enabled: Whether member receives project notifications
        created_at: When the membership was created
        updated_at: When the membership was last updated
    """

    __tablename__ = "project_members"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for project member"
    )

    # Project reference
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )

    # User reference
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )

    # Role: 'owner', 'admin', 'editor', 'viewer'
    role = Column(
        String(20),
        nullable=False,
        default="viewer",
        comment="Member role: 'owner', 'admin', 'editor', 'viewer'"
    )

    # How they joined: 'invitation', 'request', 'direct'
    joined_via = Column(
        String(30),
        nullable=True,
        comment="How the member joined: 'invitation', 'request', 'direct'"
    )

    # Who invited/approved them
    invited_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User who invited or approved this member"
    )

    # Member-specific settings
    notifications_enabled = Column(
        Boolean,
        default=True,
        comment="Whether member receives project notifications"
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
    project = relationship(
        "Project",
        back_populates="members"
    )
    user = relationship(
        "User",
        back_populates="project_memberships",
        foreign_keys=[user_id]
    )
    inviter = relationship(
        "User",
        foreign_keys=[invited_by]
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'admin', 'editor', 'viewer')",
            name="ck_member_role"
        ),
        UniqueConstraint(
            "project_id", "user_id",
            name="uq_project_member"
        ),
        Index("idx_member_project", "project_id"),
        Index("idx_member_user", "user_id"),
        Index("idx_member_role", "role"),
        {"comment": "Project membership with roles"},
    )

    def __repr__(self) -> str:
        return f"<ProjectMember(id={self.id}, project_id={self.project_id}, user_id='{self.user_id}', role='{self.role}')>"

    def to_dict(self) -> dict:
        """Convert project member to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_via": self.joined_via,
            "invited_by": self.invited_by,
            "notifications_enabled": self.notifications_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
