"""
GitHub account models for the Eigen platform.

This module contains models for GitHub account integration, storing GitHub user
information and OAuth tokens for authenticated GitHub access.
"""

import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..base import Base
from .users import User


class GitHubAccount(Base):
    """
    GitHub account model representing linked GitHub accounts for users.
    
    This model stores GitHub user information, OAuth tokens, and statistics
    for users who have connected their GitHub accounts to the Eigen platform.
    
    Attributes:
        id: Primary key integer field
        user_id: Foreign key to the users table (references clerk_user_id)
        github_user_id: Unique GitHub user identifier
        username: GitHub username
        avatar_url: URL to user's GitHub avatar
        html_url: URL to user's GitHub profile
        access_token: Encrypted GitHub OAuth access token (encrypted at app layer)
        token_scope: OAuth token scope/permissions
        follower_count: Number of GitHub followers
        following_count: Number of GitHub users being followed
        public_repos: Number of public repositories
        public_gists: Number of public gists
        bio: User's GitHub bio
        company: User's company/organization
        blog_url: User's blog URL
        location: User's location
        last_synced: Timestamp of last sync with GitHub API
        created_at: When the GitHub account was linked
    """
    
    __tablename__ = "github_accounts"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for GitHub account"
    )
    
    # Foreign key to users table
    # Note: User model uses clerk_user_id (String) as PK, so this references that
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )
    
    # GitHub user information
    github_user_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="Unique GitHub user identifier"
    )
    username = Column(Text, nullable=True, comment="GitHub username")
  
    
    # OAuth token information (encrypted at app layer)
    access_token = Column(Text, nullable=True, comment="Encrypted GitHub OAuth access token")
    token_scope = Column(Text, nullable=True, comment="OAuth token scope/permissions")
    
    # GitHub statistics
    follower_count = Column(Integer, nullable=True, comment="Number of GitHub followers")
    following_count = Column(Integer, nullable=True, comment="Number of GitHub users being followed")
    public_repos = Column(Integer, nullable=True, comment="Number of public repositories")

   
    
    # Sync tracking
    last_synced = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="Timestamp of last sync with GitHub API"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the GitHub account was linked"
    )
    
    # Relationship
    user = relationship("User", backref="github_accounts")
    
    # Table constraints and indexes
    __table_args__ = (
        Index("idx_github_account_user_id", "user_id"),
        Index("idx_github_account_github_user_id", "github_user_id"),
        {"comment": "GitHub account integration for users"},
    )
    
    def __repr__(self) -> str:
        return f"<GitHubAccount(id={self.id}, user_id='{self.user_id}', username='{self.username}')>"
    
    def to_dict(self) -> dict:
        """Convert GitHub account to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "github_user_id": self.github_user_id,
            "username": self.username,
            "token_scope": self.token_scope,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "public_repos": self.public_repos,
            "last_synced": self.last_synced.isoformat() if self.last_synced else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

