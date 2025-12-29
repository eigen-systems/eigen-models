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


class ChannelMessageReaction(Base):
    __tablename__ = "channel_message_reactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for reaction"
    )
    message_id = Column(
        Integer,
        ForeignKey("channel_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to channel_messages table"
    )
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )
    emoji = Column(
        String(50),
        nullable=False,
        comment="Emoji reaction (emoji character or shortcode)"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the reaction was added"
    )

    message = relationship(
        "ChannelMessage",
        back_populates="reactions"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "emoji", name="uq_channel_message_reaction"),
        Index("idx_channel_reaction_message", "message_id"),
        Index("idx_channel_reaction_user", "user_id"),
        Index("idx_channel_reaction_emoji", "emoji"),
        {"comment": "Reactions on channel messages"},
    )

    def __repr__(self) -> str:
        return f"<ChannelMessageReaction(id={self.id}, message_id={self.message_id}, emoji='{self.emoji}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "emoji": self.emoji,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
