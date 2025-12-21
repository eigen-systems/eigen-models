"""
Project group join request model for the Eigen platform.

This module contains the ProjectGroupJoinRequest model for handling
join requests to private groups within projects.
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
)
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectGroupJoinRequest(Base):
    """
    Project group join request model for private group access requests.

    When a project member wants to join a private group, they submit a request
    that can be approved or rejected by group admins.

    Attributes:
        id: Primary key integer field
        group_id: Foreign key to project_groups table
        user_id: Foreign key to users table (requester)
        message: Optional message from requester
        status: Request status ('pending', 'approved', 'rejected', 'cancelled')
        reviewed_by: Who reviewed the request
        reviewed_at: When the request was reviewed
        rejection_reason: Reason for rejection (if rejected)
        created_at: When the request was created
        updated_at: When the request was last updated
    """

    __tablename__ = "project_group_join_requests"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for group join request"
    )

    # Group reference
    group_id = Column(
        Integer,
        ForeignKey("project_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to project_groups table"
    )

    # Requester reference
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table (requester)"
    )

    # Request message
    message = Column(
        Text,
        nullable=True,
        comment="Optional message from requester"
    )

    # Status: 'pending', 'approved', 'rejected', 'cancelled'
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Request status: 'pending', 'approved', 'rejected', 'cancelled'"
    )

    # Reviewer reference
    reviewed_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User who reviewed the request"
    )

    # When reviewed
    reviewed_at = Column(
        DateTime,
        nullable=True,
        comment="When the request was reviewed"
    )

    # Rejection reason
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
    group = relationship(
        "ProjectGroup",
        back_populates="join_requests"
    )
    user = relationship(
        "User",
        back_populates="group_join_requests",
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
            name="ck_group_join_request_status"
        ),
        Index("idx_group_join_request_group", "group_id"),
        Index("idx_group_join_request_user", "user_id"),
        Index("idx_group_join_request_status", "status"),
        Index("idx_group_join_request_pending", "group_id", "status"),
        {"comment": "Join requests for private groups"},
    )

    def __repr__(self) -> str:
        return f"<ProjectGroupJoinRequest(id={self.id}, group_id={self.group_id}, user_id='{self.user_id}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert group join request to dictionary for API responses."""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "user_id": self.user_id,
            "message": self.message,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
