"""
Comment model for the Eigen platform.
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
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, nullable=True, default=None)  # List of attachment URLs
    is_edited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", backref="comments")
    post = relationship("Post", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    __table_args__ = (
        Index("idx_comment_post", "post_id"),
        Index("idx_comment_user", "user_id"),
        Index("idx_comment_parent", "parent_id"),
        Index("idx_comment_created", "created_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "parent_id": self.parent_id,
            "content": self.content,
            "attachments": self.attachments,
            "is_edited": self.is_edited,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
