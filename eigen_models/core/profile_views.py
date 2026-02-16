"""
Profile view tracking model for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)

from ..base import Base


class ProfileView(Base):
    __tablename__ = "profile_views"

    id = Column(Integer, primary_key=True, index=True)
    viewer_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    viewed_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    viewed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_profile_view_viewed", "viewed_id", "viewed_at"),
        Index("idx_profile_view_viewer", "viewer_id", "viewed_at"),
        {"comment": "Tracks which users have viewed which profiles"},
    )

    def __repr__(self) -> str:
        return f"<ProfileView(viewer='{self.viewer_id}', viewed='{self.viewed_id}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "viewer_id": self.viewer_id,
            "viewed_id": self.viewed_id,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
        }
