"""
Push Token models for the Eigen platform.

This module contains models for storing Expo push notification tokens
for mobile devices.
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
)
from sqlalchemy.orm import relationship

from ..base import Base


class PushToken(Base):
    """
    PushToken model for storing Expo push notification tokens.

    Supports multiple devices per user, allowing notifications to be sent
    to all of a user's devices.

    Attributes:
        id: Primary key
        user_id: The user this token belongs to
        token: The Expo push token (ExponentPushToken[...])
        device_type: Device platform (ios, android)
        device_name: Human-readable device name
        is_active: Whether this token is currently active
        created_at: When the token was registered
        updated_at: When the token was last updated
        last_used_at: When the token was last used to send a notification
    """

    __tablename__ = "push_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this push token"
    )

    token = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Expo push token (ExponentPushToken[...])"
    )

    device_type = Column(
        String(50),
        nullable=True,
        comment="Device platform (ios, android)"
    )

    device_name = Column(
        String(255),
        nullable=True,
        comment="Human-readable device name"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether this token is currently active"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

    last_used_at = Column(
        DateTime,
        nullable=True,
        comment="When the token was last used to send a notification"
    )

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref="push_tokens"
    )

    __table_args__ = (
        Index("idx_push_token_user_active", "user_id", "is_active"),
        {"comment": "Expo push notification tokens for mobile devices"},
    )

    def __repr__(self) -> str:
        return f"<PushToken(id={self.id}, user_id='{self.user_id}', device='{self.device_type}')>"

    def to_dict(self) -> dict:
        """Convert push token to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "device_type": self.device_type,
            "device_name": self.device_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }
