"""
Project activity model for the Eigen platform.

This module contains the ProjectActivity model for logging project events
and maintaining an activity history.
"""

import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectActivity(Base):
    """
    Project activity model for logging project events.

    Records all significant events in a project such as creation, updates,
    member changes, and other collaborative activities.

    Activity types include:
    - 'created': Project was created
    - 'updated': Project details were updated
    - 'member_joined': A new member joined
    - 'member_left': A member left the project
    - 'member_removed': A member was removed
    - 'member_role_changed': A member's role was changed
    - 'invitation_sent': An invitation was sent
    - 'invitation_accepted': An invitation was accepted
    - 'invitation_declined': An invitation was declined
    - 'request_received': A join request was received
    - 'request_approved': A join request was approved
    - 'request_rejected': A join request was rejected
    - 'link_added': A link was added
    - 'link_removed': A link was removed
    - 'attachment_added': An attachment was added
    - 'attachment_removed': An attachment was removed
    - 'visibility_changed': Project visibility was changed
    - 'archived': Project was archived
    - 'restored': Project was restored from archive

    Attributes:
        id: Primary key integer field
        project_id: Foreign key to projects table
        user_id: Foreign key to users table (who performed the action)
        activity_type: Type of activity (e.g., 'member_joined', 'updated')
        description: Human-readable description
        extra_data: Additional data/context in JSON format
        created_at: When the activity occurred
    """

    __tablename__ = "project_activities"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for activity"
    )

    # Project reference
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )

    # User who performed the action (nullable for system actions)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to users table (action performer)"
    )

    # Activity type
    activity_type = Column(
        String(50),
        nullable=False,
        comment="Type of activity (e.g., 'member_joined', 'updated')"
    )

    # Human-readable description
    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of the activity"
    )

    # Additional data/context for the activity
    extra_data = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional data/context for the activity"
    )

    # Timestamp
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the activity occurred"
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="activities"
    )
    user = relationship("User")

    # Table constraints and indexes
    __table_args__ = (
        Index("idx_activity_project", "project_id"),
        Index("idx_activity_user", "user_id"),
        Index("idx_activity_type", "activity_type"),
        Index("idx_activity_created", "created_at"),
        Index("idx_activity_project_created", "project_id", "created_at"),
        {"comment": "Activity log for project events"},
    )

    def __repr__(self) -> str:
        return f"<ProjectActivity(id={self.id}, project_id={self.project_id}, activity_type='{self.activity_type}')>"

    def to_dict(self) -> dict:
        """Convert activity to dictionary for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "extra_data": self.extra_data if self.extra_data else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
