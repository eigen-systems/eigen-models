"""
Notification models for the Eigen platform.
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
    FOLLOW = "follow"
    MESSAGE = "message"
    SYSTEM = "system"
    MATCH_REQUEST = "match_request"
    MATCH_ACCEPTED = "match_accepted"
    MATCH_DECLINED = "match_declined"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(255), nullable=True)
    extra_data = Column(JSONB, nullable=True, default=dict)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    recipient = relationship("User", foreign_keys=[recipient_id], backref="notifications_received")
    actor = relationship("User", foreign_keys=[actor_id], backref="notifications_triggered")

    __table_args__ = (
        Index("idx_notification_recipient_unread", "recipient_id", "is_read"),
        Index("idx_notification_recipient_created", "recipient_id", "created_at"),
        Index("idx_notification_type_created", "notification_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.notification_type}', recipient='{self.recipient_id}')>"

    def to_dict(self) -> dict:
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
