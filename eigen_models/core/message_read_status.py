"""
Message read status model for the Eigen platform.

This module contains the MessageReadStatus model for tracking read receipts
on group messages.
"""

import datetime
from sqlalchemy import (
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


class MessageReadStatus(Base):
    """
    Message read status model for tracking read receipts.

    Each record indicates that a specific user has read a specific message.
    Used for showing read receipts and calculating unread counts.

    Attributes:
        id: Primary key integer field
        message_id: Foreign key to group_messages table
        user_id: Foreign key to users table
        read_at: When the message was read
    """

    __tablename__ = "message_read_status"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for read status"
    )

    # Message reference
    message_id = Column(
        Integer,
        ForeignKey("group_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to group_messages table"
    )

    # User reference
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )

    # When read
    read_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the message was read"
    )

    # Relationships
    message = relationship(
        "GroupMessage",
        back_populates="read_statuses"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "message_id", "user_id",
            name="uq_message_read_status"
        ),
        Index("idx_read_status_message", "message_id"),
        Index("idx_read_status_user", "user_id"),
        Index("idx_read_status_read_at", "read_at"),
        {"comment": "Read receipts for group messages"},
    )

    def __repr__(self) -> str:
        return f"<MessageReadStatus(id={self.id}, message_id={self.message_id}, user_id='{self.user_id}')>"

    def to_dict(self) -> dict:
        """Convert read status to dictionary for API responses."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
