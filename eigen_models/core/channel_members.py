import datetime
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base


class ChannelMember(Base):
    __tablename__ = "channel_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for channel member"
    )
    channel_id = Column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to channels table"
    )
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )
    role = Column(
        String(20),
        nullable=False,
        default="member",
        comment="Member role: 'admin' or 'member'"
    )
    notifications = Column(
        String(20),
        nullable=False,
        default="all",
        comment="Notification preference: 'all', 'mentions', 'none'"
    )
    last_read_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last read message"
    )
    last_seen_message_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="UUID of last seen message"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When member joined the channel"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When member record was last updated"
    )

    channel = relationship(
        "Channel",
        back_populates="members"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    __table_args__ = (
        UniqueConstraint("channel_id", "user_id", name="uq_channel_member"),
        CheckConstraint(
            "role IN ('admin', 'member')",
            name="ck_channel_member_role"
        ),
        CheckConstraint(
            "notifications IN ('all', 'mentions', 'none')",
            name="ck_channel_member_notifications"
        ),
        Index("idx_channel_member_channel", "channel_id"),
        Index("idx_channel_member_user", "user_id"),
        Index("idx_channel_member_role", "role"),
        {"comment": "Channel membership records"},
    )

    def __repr__(self) -> str:
        return f"<ChannelMember(id={self.id}, channel_id={self.channel_id}, user_id='{self.user_id}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "role": self.role,
            "notifications": self.notifications,
            "last_read_at": self.last_read_at.isoformat() if self.last_read_at else None,
            "last_seen_message_id": str(self.last_seen_message_id) if self.last_seen_message_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
