"""
Notification models for the Eigen platform.

This module contains models for user notifications including follows, likes,
comments, mentions, and system notifications.
"""

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from enum import Enum

from ..base import Base


class NotificationType(str, Enum):
    """Enumeration of notification types."""
    FOLLOW = "follow"
    LIKE = "like"
    COMMENT = "comment"
    MENTION = "mention"
    REPLY = "reply"
    INVITE = "invite"
    MESSAGE = "message"
    SYSTEM = "system"
    APPLICATION = "application"  # For job/project applications


class Notification(Base):
    """
    Notification model for user notifications.

    Attributes:
        id: Primary key
        recipient_id: User who receives the notification
        actor_id: User who triggered the notification (optional for system notifications)
        notification_type: Type of notification (follow, like, comment, etc.)
        title: Short title for the notification
        content: Notification message content
        entity_type: Type of related entity (post, comment, user, etc.)
        entity_id: ID of the related entity
        metadata: Additional JSON metadata
        is_read: Whether the notification has been read
        created_at: When the notification was created
        read_at: When the notification was read
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    recipient_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who receives the notification"
    )

    actor_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who triggered the notification"
    )

    notification_type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
        comment="Type of notification"
    )

    title = Column(
        String(255),
        nullable=True,
        comment="Short title for the notification"
    )

    content = Column(
        Text,
        nullable=False,
        comment="Notification message content"
    )

    # Related entity information
    entity_type = Column(
        String(50),
        nullable=True,
        comment="Type of related entity (post, comment, user, etc.)"
    )

    entity_id = Column(
        String(255),
        nullable=True,
        comment="ID of the related entity"
    )

    # Additional data as JSON
    extra_data = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional notification data"
    )

    # Read status
    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether the notification has been read"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        index=True
    )

    read_at = Column(
        DateTime,
        nullable=True,
        comment="When the notification was read"
    )

    # Relationships
    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        backref="notifications_received"
    )
    actor = relationship(
        "User",
        foreign_keys=[actor_id],
        backref="notifications_triggered"
    )

    __table_args__ = (
        Index("idx_notification_recipient_unread", "recipient_id", "is_read"),
        Index("idx_notification_recipient_created", "recipient_id", "created_at"),
        Index("idx_notification_type_created", "notification_type", "created_at"),
        {"comment": "User notifications for various platform events"},
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.notification_type}', recipient='{self.recipient_id}')>"

    def to_dict(self) -> dict:
        """Convert notification to dictionary for API responses."""
        return {
            "id": self.id,
            "recipient_id": self.recipient_id,
            "actor_id": self.actor_id,
            "notification_type": self.notification_type.value if self.notification_type else None,
            "title": self.title,
            "content": self.content,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "metadata": self.extra_data,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
