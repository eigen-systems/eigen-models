"""
Cofounder match model for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from enum import Enum

from ..base import Base


class MatchStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class CofounderMatch(Base):
    __tablename__ = "cofounder_matches"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        SQLEnum(MatchStatus),
        default=MatchStatus.PENDING,
        nullable=False,
        index=True,
    )
    message = Column(Text, nullable=True)
    compatibility_score = Column(Float, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    sender = relationship("User", back_populates="sent_matches", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_matches", foreign_keys=[receiver_id])

    __table_args__ = (
        UniqueConstraint("sender_id", "receiver_id", name="uq_cofounder_match"),
        Index("idx_match_sender_status", "sender_id", "status"),
        Index("idx_match_receiver_status", "receiver_id", "status"),
        Index("idx_match_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CofounderMatch(id={self.id}, sender='{self.sender_id}', receiver='{self.receiver_id}', status='{self.status}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "status": self.status.value if self.status else None,
            "message": self.message,
            "compatibility_score": self.compatibility_score,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
