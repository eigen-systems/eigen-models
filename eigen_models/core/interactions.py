"""
User interaction models for the Eigen platform.
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
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base


class UserInteraction(Base):
    """User-to-user interactions like mute, block, etc."""
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    target_user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    interaction_type = Column(String(30), nullable=False)  # mute, block, report
    interaction_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "target_user_id", "interaction_type", name="uq_user_interaction"
        ),
        Index("idx_user_interaction_user", "user_id"),
        Index("idx_user_interaction_target", "target_user_id"),
        Index("idx_user_interaction_type", "interaction_type"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "interaction_type": self.interaction_type,
            "interaction_metadata": self.interaction_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    following_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
        Index("idx_follower", "follower_id"),
        Index("idx_following", "following_id"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "following_id": self.following_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
