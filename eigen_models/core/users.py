"""
User model for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    String,
)
from sqlalchemy.orm import relationship

from ..base import Base


class User(Base):
    __tablename__ = "users"

    clerk_user_id = Column(String(255), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
    mobile_number = Column(String(255), nullable=True)
    image_url = Column(String(512), nullable=True)

    # Cofounder relationships
    cofounder_profile = relationship(
        "CofounderProfile", back_populates="user", uselist=False
    )
    sent_matches = relationship(
        "CofounderMatch",
        back_populates="sender",
        foreign_keys="CofounderMatch.sender_id",
    )
    received_matches = relationship(
        "CofounderMatch",
        back_populates="receiver",
        foreign_keys="CofounderMatch.receiver_id",
    )

    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        {"comment": "System users with Clerk authentication integration"},
    )

    def __repr__(self) -> str:
        return f"<User(clerk_user_id='{self.clerk_user_id}', email='{self.email}')>"

    def to_dict(self) -> dict:
        return {
            "clerk_user_id": self.clerk_user_id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "mobile_number": self.mobile_number,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
