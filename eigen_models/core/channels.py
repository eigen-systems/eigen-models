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
from sqlalchemy.orm import relationship

from ..base import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for channel"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to projects table"
    )
    name = Column(
        String(100),
        nullable=False,
        comment="Channel name"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Channel description"
    )
    channel_type = Column(
        String(20),
        nullable=False,
        default="text",
        comment="Channel type: 'text', 'voice', 'announcement'"
    )
    visibility = Column(
        String(20),
        nullable=False,
        default="public",
        comment="Channel visibility: 'public' or 'private'"
    )
    created_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the channel"
    )
    is_archived = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether channel is archived"
    )
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is the default channel for the project"
    )
    member_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of members in the channel"
    )
    last_message_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last message in channel"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the channel was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the channel was last updated"
    )

    project = relationship(
        "Project",
        back_populates="channels"
    )
    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )
    members = relationship(
        "ChannelMember",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "ChannelMessage",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    threads = relationship(
        "ChannelThread",
        back_populates="channel",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "channel_type IN ('text', 'voice', 'announcement')",
            name="ck_channel_type"
        ),
        CheckConstraint(
            "visibility IN ('public', 'private')",
            name="ck_channel_visibility"
        ),
        Index("idx_channel_project", "project_id"),
        Index("idx_channel_created_by", "created_by"),
        Index("idx_channel_type", "channel_type"),
        Index("idx_channel_visibility", "visibility"),
        Index("idx_channel_is_default", "is_default"),
        {"comment": "Channels for project communication"},
    )

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, name='{self.name}', project_id={self.project_id})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "channel_type": self.channel_type,
            "visibility": self.visibility,
            "created_by": self.created_by,
            "is_archived": self.is_archived,
            "is_default": self.is_default,
            "member_count": self.member_count,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
