"""
Project model for the Eigen platform.

This module contains the Project model for collaborative workspaces where users
can create projects, add documentation, links, and collaborate with team members.
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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class Project(Base):
    """
    Project model representing collaborative workspaces in the Eigen platform.

    Projects can be public (anyone can request to join) or private (invite-only).
    Each project has an owner and can have multiple members with different roles.

    Attributes:
        id: Primary key integer field
        title: Project title (required)
        description: Project description
        owner_id: Foreign key to users table (project creator)
        visibility: 'public' or 'private'
        status: 'active', 'archived', or 'deleted'
        attachments: JSONB array of file URLs/metadata
        links: JSONB array of link objects {title, url, type}
        tags: Array of tags for categorization
        skills: Array of skills required/related to the project
        allow_join_requests: Whether public projects accept join requests
        require_approval: Whether join requests need admin approval
        max_members: Optional maximum member limit
        member_count: Current number of members (including owner)
        is_featured: Whether project is featured
        created_at: When the project was created
        updated_at: When the project was last updated
    """

    __tablename__ = "projects"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for project"
    )

    # Basic Info
    title = Column(
        String(255),
        nullable=False,
        comment="Project title"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Project description"
    )

    # Owner
    owner_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table (project owner)"
    )

    # Visibility: 'public' or 'private'
    visibility = Column(
        String(20),
        nullable=False,
        default="public",
        comment="Project visibility: 'public' or 'private'"
    )

    # Status: 'active', 'archived', 'deleted'
    status = Column(
        String(20),
        nullable=False,
        default="active",
        comment="Project status: 'active', 'archived', or 'deleted'"
    )

    # Content - Attachments (file URLs/metadata)
    attachments = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Array of file attachments (URLs and metadata)"
    )

    # Content - Links (external resources)
    links = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Array of link objects: {title, url, type}"
    )

    # Tags/Categories
    tags = Column(
        ARRAY(Text),
        nullable=True,
        default=list,
        comment="Array of tags for project categorization"
    )
    skills = Column(
        ARRAY(Text),
        nullable=True,
        default=list,
        comment="Array of skills related to the project"
    )

    # Settings
    allow_join_requests = Column(
        Boolean,
        default=True,
        comment="Whether public projects accept join requests"
    )
    require_approval = Column(
        Boolean,
        default=True,
        comment="Whether join requests require admin approval"
    )
    max_members = Column(
        Integer,
        nullable=True,
        comment="Optional maximum number of members"
    )

    # Metadata
    member_count = Column(
        Integer,
        default=1,
        comment="Current number of members (including owner)"
    )
    is_featured = Column(
        Boolean,
        default=False,
        comment="Whether project is featured"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the project was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the project was last updated"
    )

    # Relationships
    owner = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id]
    )
    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    join_requests = relationship(
        "ProjectJoinRequest",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    invitations = relationship(
        "ProjectInvitation",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    activities = relationship(
        "ProjectActivity",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "visibility IN ('public', 'private')",
            name="ck_project_visibility"
        ),
        CheckConstraint(
            "status IN ('active', 'archived', 'deleted')",
            name="ck_project_status"
        ),
        Index("idx_project_owner", "owner_id"),
        Index("idx_project_visibility", "visibility"),
        Index("idx_project_status", "status"),
        Index("idx_project_created", "created_at"),
        Index("idx_project_skills", "skills", postgresql_using="gin"),
        Index("idx_project_tags", "tags", postgresql_using="gin"),
        {"comment": "Projects for collaborative workspaces"},
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title='{self.title}', owner_id='{self.owner_id}')>"

    def to_dict(self) -> dict:
        """Convert project to dictionary for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "owner_id": self.owner_id,
            "visibility": self.visibility,
            "status": self.status,
            "attachments": self.attachments if self.attachments else [],
            "links": self.links if self.links else [],
            "tags": self.tags if self.tags else [],
            "skills": self.skills if self.skills else [],
            "allow_join_requests": self.allow_join_requests,
            "require_approval": self.require_approval,
            "max_members": self.max_members,
            "member_count": self.member_count,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
