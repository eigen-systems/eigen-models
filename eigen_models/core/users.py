"""
User-related models for the Eigen platform.

This module contains models for user management, authentication, and user profile data.
Uses Clerk for authentication integration.
"""

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from enum import Enum
from sqlalchemy.orm import relationship

from ..base import Base




class User(Base):
    """
    User model representing system users with Clerk authentication.
    
    This model stores core user information and integrates with Clerk for
    authentication and user management. The clerk_user_id serves as the
    primary key to maintain consistency with Clerk's user identification.
    
    Attributes:
        clerk_user_id: Primary key from Clerk authentication service
        name: Full name of the user
        email: Unique email address for authentication
        is_active: Whether the user account is active
        last_login_at: Timestamp of last successful login
        created_at: When the user account was created
        updated_at: When the user account was last modified
    
    Relationships:
        mobile_numbers: Associated mobile phone numbers
        subscriptions: User's payment subscriptions
    """
    
    __tablename__ = "users"
    
    # Override Base id field with Clerk user ID
    clerk_user_id = Column(
        String(255),
        primary_key=True,
        nullable=False,
        comment="Unique Clerk user identifier"
    )
    
    # Core user information
    name = Column(String(255), nullable=False, comment="User's full name")
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address"
    )
    
    # Account status and tracking
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    last_login_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last successful login"
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
    
    mobile_number = Column(String(255), nullable=True, comment="User's mobile number")
    image_url = Column(String(512), nullable=True, comment="User's image URL")

    # Project relationships
    owned_projects = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id"
    )
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        foreign_keys="ProjectMember.user_id"
    )
    project_join_requests = relationship(
        "ProjectJoinRequest",
        back_populates="user",
        foreign_keys="ProjectJoinRequest.user_id"
    )
    project_invitations = relationship(
        "ProjectInvitation",
        back_populates="user",
        foreign_keys="ProjectInvitation.user_id"
    )

    # Table constraints and indexes
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        {"comment": "System users with Clerk authentication integration"},
    )
    
    def __repr__(self) -> str:
        return f"<User(clerk_user_id='{self.clerk_user_id}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses."""
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

   