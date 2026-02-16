"""
Profile models for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    Boolean,
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from ..base import Base
from .users import User


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    headline = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(ARRAY(Text), nullable=True)
    timezone = Column(String(255), nullable=True)

    # Geographic location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    pin = Column(String(50), nullable=True)
    district = Column(String(255), nullable=True)

    # GitHub integration
    github_connected = Column(Boolean, default=False, nullable=False)
    github_username = Column(Text, nullable=True)
    github_user_id = Column(BigInteger, nullable=True)
    github_last_synced = Column(DateTime, nullable=True)

    # Resume
    resume_uploaded = Column(Boolean, default=False, nullable=False)
    resume_file_url = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_json = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", backref="profile")

    __table_args__ = (
        Index("idx_profile_user_id", "user_id"),
        Index("idx_profile_github_user_id", "github_user_id"),
    )

    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, user_id='{self.user_id}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "headline": self.headline,
            "bio": self.bio,
            "skills": self.skills if self.skills else [],
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location": self.location,
            "state": self.state,
            "country": self.country,
            "pin": self.pin,
            "district": self.district,
            "github_connected": self.github_connected,
            "github_username": self.github_username,
            "github_user_id": self.github_user_id,
            "github_last_synced": self.github_last_synced.isoformat() if self.github_last_synced else None,
            "resume_uploaded": self.resume_uploaded,
            "resume_file_url": self.resume_file_url,
            "resume_text": self.resume_text,
            "resume_json": self.resume_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
