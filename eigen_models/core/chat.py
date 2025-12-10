"""
Chat models for the Eigen platform.

This module contains models for chat conversations between users,
supporting both one-on-one and group chats.
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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from ..base import Base
from .users import User


class Chat(Base):
    """
    Chat model representing conversations between users.
    
    This model stores chat information for both one-on-one conversations
    and group chats, tracking participants and conversation metadata.
    
    Attributes:
        id: Primary key integer field
        chat_type: Type of chat - either 'direct' (1-on-1) or 'group'
        name: Name of the chat (optional, mainly for group chats)
        created_by: Foreign key to the users table (user who created the chat)
        created_at: When the chat was created
        updated_at: When the chat was last modified
        last_message_at: Timestamp of the last message in the chat
    """
    
    __tablename__ = "chats"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for chat"
    )
    
    # Chat type and metadata
    chat_type = Column(
        String(20),
        nullable=False,
        comment="Chat type: 'direct' (1-on-1) or 'group'"
    )
    name = Column(
        String(255),
        nullable=True,
        comment="Name of the chat (optional, mainly for group chats)"
    )
    
    # Foreign key to users table (user who created the chat)
    created_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the chat"
    )
    
    # Participants stored as array of user IDs
    # For direct chats, this will contain 2 user IDs
    # For group chats, this can contain multiple user IDs
    participant_ids = Column(
        ARRAY(String),
        nullable=False,
        comment="Array of participant user IDs (clerk_user_id values)"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the chat was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the chat was last modified"
    )
    last_message_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of the last message in the chat"
    )
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "chat_type IN ('direct', 'group')",
            name="ck_chat_type"
        ),
        Index("idx_chat_type", "chat_type"),
        Index("idx_chat_created_by", "created_by"),
        Index("idx_chat_last_message_at", "last_message_at"),
        {"comment": "Chat conversations between users"},
    )
    
    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, chat_type='{self.chat_type}', name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert chat to dictionary for API responses."""
        return {
            "id": self.id,
            "chat_type": self.chat_type,
            "name": self.name,
            "created_by": self.created_by,
            "participant_ids": self.participant_ids if self.participant_ids else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }

