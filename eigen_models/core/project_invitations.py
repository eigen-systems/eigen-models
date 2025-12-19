"""
Project invitation model for the Eigen platform.

This module contains the ProjectInvitation model for handling invitations
to join projects (primarily used for private projects).
"""

import datetime
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectInvitation(Base):
    """
    Project invitation model for inviting users to join projects.

    Owners and admins can invite users to join projects. Invitations can
    have expiration dates and specific role assignments.

    Attributes:
        id: Primary key integer field
        project_id: Foreign key to projects table
        user_id: Foreign key to users table (invitee)
        invited_by: Foreign key to users table (inviter)
        role: Role being offered to the invitee
        message: Personal message from inviter
        status: Invitation status ('pending', 'accepted', 'declined', 'expired', 'cancelled')
        expires_at: When the invitation expires
        responded_at: When the invitee responded
        created_at: When the invitation was created
        updated_at: When the invitation was last updated
    """

    __tablename__ = "project_invitations"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for invitation"
    )

    # Project reference
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )

    # Invitee
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table (invitee)"
    )

    # Inviter (must be owner or admin)
    invited_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to users table (inviter)"
    )

    # Role being offered
    role = Column(
        String(20),
        nullable=False,
        default="viewer",
        comment="Role being offered: 'admin', 'editor', 'viewer'"
    )

    # Personal message from inviter
    message = Column(
        Text,
        nullable=True,
        comment="Personal message from the inviter"
    )

    # Status: 'pending', 'accepted', 'declined', 'expired', 'cancelled'
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Invitation status: 'pending', 'accepted', 'declined', 'expired', 'cancelled'"
    )

    # Expiration
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="When the invitation expires"
    )

    # Response tracking
    responded_at = Column(
        DateTime,
        nullable=True,
        comment="When the invitee responded"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the invitation was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the invitation was last updated"
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="invitations"
    )
    user = relationship(
        "User",
        back_populates="project_invitations",
        foreign_keys=[user_id]
    )
    inviter = relationship(
        "User",
        foreign_keys=[invited_by]
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'declined', 'expired', 'cancelled')",
            name="ck_invitation_status"
        ),
        CheckConstraint(
            "role IN ('admin', 'editor', 'viewer')",
            name="ck_invitation_role"
        ),
        Index("idx_invitation_project", "project_id"),
        Index("idx_invitation_user", "user_id"),
        Index("idx_invitation_status", "status"),
        Index("idx_invitation_pending", "user_id", "status"),
        {"comment": "Invitations to join projects"},
    )

    def __repr__(self) -> str:
        return f"<ProjectInvitation(id={self.id}, project_id={self.project_id}, user_id='{self.user_id}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert invitation to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "invited_by": self.invited_by,
            "role": self.role,
            "message": self.message,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
