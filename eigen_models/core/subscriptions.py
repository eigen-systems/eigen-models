"""
User subscription model for the Eigen platform.
"""

import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from ..base import Base


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False,
    )
    status = Column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    polar_subscription_id = Column(String(255), unique=True, nullable=True)
    polar_customer_id = Column(String(255), nullable=True)
    polar_product_id = Column(String(255), nullable=True)
    billing_interval = Column(String(20), nullable=True)  # "month" or "year"
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", backref="subscription")

    __table_args__ = (
        Index("idx_subscription_polar_id", "polar_subscription_id"),
        Index("idx_subscription_tier_status", "tier", "status"),
        {"comment": "User subscription tracking for Polar.sh integration"},
    )

    def __repr__(self) -> str:
        return f"<UserSubscription(user_id='{self.user_id}', tier='{self.tier}', status='{self.status}')>"

    @property
    def is_pro(self) -> bool:
        return self.tier == SubscriptionTier.PRO and self.status in (
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier.value if self.tier else None,
            "status": self.status.value if self.status else None,
            "polar_subscription_id": self.polar_subscription_id,
            "polar_customer_id": self.polar_customer_id,
            "polar_product_id": self.polar_product_id,
            "billing_interval": self.billing_interval,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
