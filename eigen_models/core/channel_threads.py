import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from ..base import Base


class ChannelThread(Base):
    __tablename__ = "channel_threads"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for thread"
    )
    channel_id = Column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to channels table"
    )
    root_message_id = Column(
        Integer,
        ForeignKey("channel_messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Foreign key to the root message that started the thread"
    )
    reply_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of replies in the thread"
    )
    last_reply_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last reply in thread"
    )
    participant_ids = Column(
        ARRAY(Integer),
        nullable=True,
        default=list,
        comment="List of user IDs who participated in the thread"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the thread was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the thread was last updated"
    )

    channel = relationship(
        "Channel",
        back_populates="threads"
    )
    root_message = relationship(
        "ChannelMessage",
        foreign_keys=[root_message_id]
    )
    messages = relationship(
        "ChannelMessage",
        back_populates="thread",
        foreign_keys="ChannelMessage.thread_id"
    )

    __table_args__ = (
        Index("idx_channel_thread_channel", "channel_id"),
        Index("idx_channel_thread_root_message", "root_message_id"),
        Index("idx_channel_thread_last_reply", "last_reply_at"),
        {"comment": "Threads for channel message replies"},
    )

    def __repr__(self) -> str:
        return f"<ChannelThread(id={self.id}, channel_id={self.channel_id}, root_message_id={self.root_message_id})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "root_message_id": self.root_message_id,
            "reply_count": self.reply_count,
            "last_reply_at": self.last_reply_at.isoformat() if self.last_reply_at else None,
            "participant_ids": self.participant_ids if self.participant_ids else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
