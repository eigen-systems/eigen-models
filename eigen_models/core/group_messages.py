"""
Group message model for the Eigen platform.

This module contains the GroupMessage model for chat messages within project groups.
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class GroupMessage(Base):
    """
    Group message model representing chat messages in project groups.

    Messages support text, images, files, and system messages.
    Features include replies, editing, soft deletion, and attachments.

    Attributes:
        id: Primary key integer field
        group_id: Foreign key to project_groups table
        sender_id: Foreign key to users table
        content: Message text content
        message_type: Type of message ('text', 'image', 'file', 'system')
        attachments: JSONB array of file attachments
        reply_to_id: Reference to parent message (for threading)
        is_edited: Whether message has been edited
        edited_at: When message was last edited
        is_deleted: Whether message has been soft deleted
        deleted_at: When message was deleted
        created_at: When the message was created
    """

    __tablename__ = "group_messages"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for group message"
    )

    # Group reference
    group_id = Column(
        Integer,
        ForeignKey("project_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to project_groups table"
    )

    # Sender reference
    sender_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to users table (sender)"
    )

    # Message content
    content = Column(
        Text,
        nullable=True,
        comment="Message text content"
    )

    # Message type: 'text', 'image', 'file', 'system'
    message_type = Column(
        String(20),
        nullable=False,
        default="text",
        comment="Type of message: 'text', 'image', 'file', 'system'"
    )

    # Attachments: [{url, filename, type, size}]
    attachments = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Array of file attachments with metadata"
    )

    # Reply/thread reference
    reply_to_id = Column(
        Integer,
        ForeignKey("group_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to parent message for threading"
    )

    # Edit tracking
    is_edited = Column(
        Boolean,
        default=False,
        comment="Whether message has been edited"
    )
    edited_at = Column(
        DateTime,
        nullable=True,
        comment="When message was last edited"
    )

    # Soft delete
    is_deleted = Column(
        Boolean,
        default=False,
        comment="Whether message has been soft deleted"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="When message was deleted"
    )

    # Timestamp (no updated_at for messages - use edited_at instead)
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the message was created"
    )

    # Relationships
    group = relationship(
        "ProjectGroup",
        back_populates="messages"
    )
    sender = relationship(
        "User",
        foreign_keys=[sender_id]
    )
    reply_to = relationship(
        "GroupMessage",
        remote_side=[id],
        foreign_keys=[reply_to_id]
    )
    reactions = relationship(
        "MessageReaction",
        back_populates="message",
        cascade="all, delete-orphan"
    )
    read_statuses = relationship(
        "MessageReadStatus",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'file', 'system')",
            name="ck_group_message_type"
        ),
        Index("idx_group_message_group", "group_id"),
        Index("idx_group_message_sender", "sender_id"),
        Index("idx_group_message_created", "created_at"),
        Index("idx_group_message_reply", "reply_to_id"),
        Index("idx_group_message_group_created", "group_id", "created_at"),
        {"comment": "Chat messages in project groups"},
    )

    def __repr__(self) -> str:
        content_preview = self.content[:30] + "..." if self.content and len(self.content) > 30 else self.content
        return f"<GroupMessage(id={self.id}, group_id={self.group_id}, sender_id='{self.sender_id}', content='{content_preview}')>"

    def to_dict(self) -> dict:
        """Convert group message to dictionary for API responses."""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "sender_id": self.sender_id,
            "content": self.content if not self.is_deleted else None,
            "message_type": self.message_type,
            "attachments": self.attachments if self.attachments and not self.is_deleted else [],
            "reply_to_id": self.reply_to_id,
            "is_edited": self.is_edited,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
