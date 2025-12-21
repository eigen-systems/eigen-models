"""
Project group model for the Eigen platform.

This module contains the ProjectGroup model for group chats within projects.
Each project can have multiple groups (public/private) for team communication.
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
    Text,
)
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectGroup(Base):
    """
    Project group model representing chat groups within projects.

    Each project has at least one default group (auto-created).
    Groups can be public (any project member can join) or private (requires request).
    Private groups can optionally be hidden from non-members.

    Attributes:
        id: Primary key integer field
        project_id: Foreign key to projects table
        name: Group name
        description: Group description
        visibility: 'public' or 'private' (within project)
        show_to_non_members: Whether private groups appear in list for non-members
        is_default: Whether this is the auto-created default group
        created_by: Who created the group
        member_count: Current number of members
        created_at: When the group was created
        updated_at: When the group was last updated
    """

    __tablename__ = "project_groups"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for project group"
    )

    # Project reference
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )

    # Basic Info
    name = Column(
        String(255),
        nullable=False,
        comment="Group name"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Group description"
    )

    # Visibility within project: 'public' or 'private'
    visibility = Column(
        String(20),
        nullable=False,
        default="public",
        comment="Group visibility within project: 'public' or 'private'"
    )

    # Whether private groups are shown to non-members (if False, completely hidden)
    show_to_non_members = Column(
        Boolean,
        default=True,
        comment="Whether private groups appear in list for non-members"
    )

    # Default group flag
    is_default = Column(
        Boolean,
        default=False,
        comment="Whether this is the auto-created default group"
    )

    # Creator
    created_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this group"
    )

    # Member count
    member_count = Column(
        Integer,
        default=0,
        comment="Current number of members in the group"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the group was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the group was last updated"
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="groups"
    )
    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )
    members = relationship(
        "ProjectGroupMember",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    join_requests = relationship(
        "ProjectGroupJoinRequest",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "GroupMessage",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "visibility IN ('public', 'private')",
            name="ck_group_visibility"
        ),
        Index("idx_group_project", "project_id"),
        Index("idx_group_visibility", "visibility"),
        Index("idx_group_is_default", "is_default"),
        Index("idx_group_created", "created_at"),
        {"comment": "Project groups for team communication"},
    )

    def __repr__(self) -> str:
        return f"<ProjectGroup(id={self.id}, name='{self.name}', project_id={self.project_id})>"

    def to_dict(self) -> dict:
        """Convert project group to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "visibility": self.visibility,
            "show_to_non_members": self.show_to_non_members,
            "is_default": self.is_default,
            "created_by": self.created_by,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
