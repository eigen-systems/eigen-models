"""
Project join request model for the Eigen platform.

This module contains the ProjectJoinRequest model for handling requests
from users who want to join public projects.
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


class ProjectJoinRequest(Base):
    """
    Project join request model for public project membership requests.

    Users can request to join public projects. Project admins can approve
    or reject these requests.

    Attributes:
        id: Primary key integer field
        project_id: Foreign key to projects table
        user_id: Foreign key to users table (requester)
        message: Optional message from the requester
        status: Request status ('pending', 'approved', 'rejected', 'cancelled')
        requested_role: Role the user is requesting (default: viewer)
        reviewed_by: Admin who reviewed the request
        reviewed_at: When the request was reviewed
        rejection_reason: Reason for rejection (if rejected)
        created_at: When the request was created
        updated_at: When the request was last updated
    """

    __tablename__ = "project_join_requests"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for join request"
    )

    # Project reference
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )

    # User reference (requester)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table (requester)"
    )

    # Request message from user
    message = Column(
        Text,
        nullable=True,
        comment="Optional message from the requester"
    )

    # Status: 'pending', 'approved', 'rejected', 'cancelled'
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Request status: 'pending', 'approved', 'rejected', 'cancelled'"
    )

    # Requested role (optional, default is 'viewer')
    requested_role = Column(
        String(20),
        nullable=True,
        default="viewer",
        comment="Role the user is requesting"
    )

    # Response details
    reviewed_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        comment="Admin who reviewed the request"
    )
    reviewed_at = Column(
        DateTime,
        nullable=True,
        comment="When the request was reviewed"
    )
    rejection_reason = Column(
        Text,
        nullable=True,
        comment="Reason for rejection (if rejected)"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the request was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the request was last updated"
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="join_requests"
    )
    user = relationship(
        "User",
        back_populates="project_join_requests",
        foreign_keys=[user_id]
    )
    reviewer = relationship(
        "User",
        foreign_keys=[reviewed_by]
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'cancelled')",
            name="ck_request_status"
        ),
        CheckConstraint(
            "requested_role IN ('admin', 'editor', 'viewer')",
            name="ck_requested_role"
        ),
        Index("idx_request_project", "project_id"),
        Index("idx_request_user", "user_id"),
        Index("idx_request_status", "status"),
        Index("idx_request_pending", "project_id", "status"),
        {"comment": "Join requests for public projects"},
    )

    def __repr__(self) -> str:
        return f"<ProjectJoinRequest(id={self.id}, project_id={self.project_id}, user_id='{self.user_id}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert join request to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "message": self.message,
            "status": self.status,
            "requested_role": self.requested_role,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
