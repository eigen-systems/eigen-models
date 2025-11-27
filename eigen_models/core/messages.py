"""
Message models for the Eigen platform.

This module contains models for chat messages, storing message content,
metadata, and read receipts for conversations.
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
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base
from .users import User


class Message(Base):
    """
    Message model representing individual messages in a chat conversation.
    
    This model stores message content, sender information, read receipts,
    and attachments for chat messages.
    
    Attributes:
        id: Primary key integer field
        chat_id: Foreign key to the chats table
        sender_id: Foreign key to the users table (message sender)
        content: Message content/text
        message_type: Type of message - 'text', 'image', 'file', 'system'
        attachments: JSONB field for message attachments
        read_at: Timestamp when the message was read (for read receipts)
        created_at: When the message was created
    """
    
    __tablename__ = "messages"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for message"
    )
    
    # Foreign keys
    chat_id = Column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to chats table"
    )
    sender_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to users table (message sender)"
    )
    
    # Message content
    content = Column(Text, nullable=True, comment="Message content/text")
    message_type = Column(
        String(20),
        nullable=False,
        default="text",
        comment="Message type: 'text', 'image', 'file', 'system'"
    )
    
    # Attachments and metadata
    attachments = Column(
        JSONB,
        nullable=True,
        comment="Message attachments (JSON structure with file URLs, types, etc.)"
    )
    
    # Read receipt tracking
    read_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when the message was read (for read receipts)"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        index=True,
        comment="When the message was created"
    )
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", backref="messages")
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'file', 'system')",
            name="ck_message_type"
        ),
        Index("idx_message_chat_id", "chat_id"),
        Index("idx_message_sender_id", "sender_id"),
        Index("idx_message_created_at", "created_at"),
        Index("idx_message_chat_created_at", "chat_id", "created_at"),
        {"comment": "Messages in chat conversations"},
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, sender_id='{self.sender_id}', message_type='{self.message_type}')>"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary for API responses."""
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "message_type": self.message_type,
            "attachments": self.attachments,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

