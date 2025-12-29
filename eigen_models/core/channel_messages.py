import datetime
import uuid
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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base


def generate_uuid7():
    return uuid.uuid4()


class ChannelMessage(Base):
    __tablename__ = "channel_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for channel message"
    )
    public_id = Column(
        UUID(as_uuid=True),
        default=generate_uuid7,
        nullable=False,
        unique=True,
        index=True,
        comment="Public UUID for message (used in real-time)"
    )
    channel_id = Column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to channels table"
    )
    sender_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to users table (message sender)"
    )
    content = Column(
        Text,
        nullable=True,
        comment="Message content"
    )
    message_type = Column(
        String(30),
        nullable=False,
        default="text",
        comment="Message type: 'text', 'image', 'file', 'system', 'reply'"
    )
    attachments = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Message attachments: [{type, url, name, size, mime_type}]"
    )
    thread_id = Column(
        Integer,
        ForeignKey("channel_threads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key to thread if this is a reply"
    )
    reply_to_message_id = Column(
        Integer,
        ForeignKey("channel_messages.id", ondelete="SET NULL"),
        nullable=True,
        comment="Foreign key to parent message if this is a reply"
    )
    reply_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of replies to this message"
    )
    reaction_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of reactions"
    )
    mentions = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of mentioned user IDs"
    )
    is_edited = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether message has been edited"
    )
    edited_at = Column(
        DateTime,
        nullable=True,
        comment="When message was last edited"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether message has been soft deleted"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="When message was deleted"
    )
    is_pinned = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether message is pinned"
    )
    pinned_at = Column(
        DateTime,
        nullable=True,
        comment="When message was pinned"
    )
    pinned_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User who pinned the message"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        index=True,
        comment="When message was sent"
    )

    channel = relationship(
        "Channel",
        back_populates="messages"
    )
    sender = relationship(
        "User",
        foreign_keys=[sender_id]
    )
    pinner = relationship(
        "User",
        foreign_keys=[pinned_by]
    )
    thread = relationship(
        "ChannelThread",
        back_populates="messages",
        foreign_keys=[thread_id]
    )
    reply_to = relationship(
        "ChannelMessage",
        remote_side=[id],
        foreign_keys=[reply_to_message_id]
    )
    reactions = relationship(
        "ChannelMessageReaction",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'file', 'system', 'reply')",
            name="ck_channel_message_type"
        ),
        Index("idx_channel_message_channel", "channel_id"),
        Index("idx_channel_message_sender", "sender_id"),
        Index("idx_channel_message_thread", "thread_id"),
        Index("idx_channel_message_created", "created_at"),
        Index("idx_channel_message_pinned", "is_pinned"),
        {"comment": "Channel messages for real-time communication"},
    )

    def __repr__(self) -> str:
        return f"<ChannelMessage(id={self.id}, channel_id={self.channel_id}, sender_id='{self.sender_id}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "public_id": str(self.public_id) if self.public_id else None,
            "channel_id": self.channel_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "message_type": self.message_type,
            "attachments": self.attachments if self.attachments else [],
            "thread_id": self.thread_id,
            "reply_to_message_id": self.reply_to_message_id,
            "reply_count": self.reply_count,
            "reaction_count": self.reaction_count,
            "mentions": self.mentions if self.mentions else [],
            "is_edited": self.is_edited,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "is_pinned": self.is_pinned,
            "pinned_at": self.pinned_at.isoformat() if self.pinned_at else None,
            "pinned_by": self.pinned_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
