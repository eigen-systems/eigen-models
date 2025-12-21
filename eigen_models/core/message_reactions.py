"""
Message reaction model for the Eigen platform.

This module contains the MessageReaction model for emoji reactions on group messages.
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


class MessageReaction(Base):
    """
    Message reaction model for emoji reactions on group messages.

    Users can add multiple different emoji reactions to a message,
    but only one of each type per message.

    Attributes:
        id: Primary key integer field
        message_id: Foreign key to group_messages table
        user_id: Foreign key to users table
        emoji: Emoji character or shortcode
        created_at: When the reaction was added
    """

    __tablename__ = "message_reactions"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for message reaction"
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

    # Emoji (character or shortcode like :thumbsup:)
    emoji = Column(
        String(32),
        nullable=False,
        comment="Emoji character or shortcode"
    )

    # Timestamp
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the reaction was added"
    )

    # Relationships
    message = relationship(
        "GroupMessage",
        back_populates="reactions"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "message_id", "user_id", "emoji",
            name="uq_message_reaction"
        ),
        Index("idx_reaction_message", "message_id"),
        Index("idx_reaction_user", "user_id"),
        Index("idx_reaction_emoji", "emoji"),
        {"comment": "Emoji reactions on group messages"},
    )

    def __repr__(self) -> str:
        return f"<MessageReaction(id={self.id}, message_id={self.message_id}, user_id='{self.user_id}', emoji='{self.emoji}')>"

    def to_dict(self) -> dict:
        """Convert message reaction to dictionary for API responses."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "emoji": self.emoji,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
