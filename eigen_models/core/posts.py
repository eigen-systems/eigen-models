"""
Post models for the Eigen platform.

This module contains models for user posts, including general posts and request posts
with content, attachments, requirements, skills, tags, and GitHub repository information.
"""

import datetime
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from ..base import Base
from .users import User


class Post(Base):
    """
    Post model representing user posts in the Eigen platform.
    
    This model stores posts that can be either general posts or request posts,
    with support for content, attachments, requirements, skills, tags, and
    GitHub repository information.
    
    Attributes:
        id: Primary key integer field
        author_id: Foreign key to the users table (references clerk_user_id)
        type: Post type - either 'general' or 'request'
        content: Post content/text
        attachments: JSONB field for post attachments
        requirements: JSONB field for post requirements (for request posts)
        skills: Array of skills related to the post
        tags: Array of tags for categorization
        github_repo_fullname: Full name of associated GitHub repository (e.g., "vercel/next.js")
        github_repo_url: URL to the GitHub repository
        created_at: When the post was created
    """
    
    __tablename__ = "posts"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for post"
    )
    
    # Foreign key to users table
    # Note: User model uses clerk_user_id (String) as PK, so this references that
    author_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users table (post author)"
    )
    
    # Post type and content
    post_type = Column(
        String(30),
        nullable=False,
        comment="Post type: 'general' or 'request'"
    )
    content = Column(Text, nullable=True, comment="Post content/text")
    
    # Structured data
    attachments = Column(
        JSONB,
        nullable=True,
        comment="Post attachments (JSON structure)"
    )
    requirements = Column(
        JSONB,
        nullable=True,
        comment="Post requirements (JSON structure, typically for request posts)"
    )
    
    # Arrays
    skills = Column(
        ARRAY(Text),
        nullable=True,
        comment="Array of skills related to the post"
    )
    tags = Column(
        ARRAY(Text),
        nullable=True,
        comment="Array of tags for post categorization"
    )
    
    # GitHub repository information
    github_repo_fullname = Column(
        Text,
        nullable=True,
        comment="Full name of associated GitHub repository (e.g., 'vercel/next.js')"
    )
    github_repo_url = Column(
        Text,
        nullable=True,
        comment="URL to the GitHub repository"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the post was created"
    )
    location_geog = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        comment="Geographic point (latitude, longitude) using WGS84 (SRID 4326)"
    )
    # Relationship
    author = relationship("User", backref="posts")
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "post_type IN ('general', 'request')",
            name="ck_post_type"
        ),
        Index("idx_post_author_id", "author_id"),
        Index("idx_post_type", "post_type"),
        Index("idx_post_created_at", "created_at"),
        {"comment": "User posts including general posts and request posts"},
    )
    
    def __repr__(self) -> str:
        return f"<Post(id={self.id}, author_id='{self.author_id}', post_type='{self.post_type}')>"
    
    def to_dict(self) -> dict:
        """Convert post to dictionary for API responses."""
        location_geog_dict = None
        if self.location_geog:
            try:
                # For Geography POINT, coordinates are typically accessed via .x (longitude) and .y (latitude)
                # or through the geometry object
                if hasattr(self.location_geog, 'x') and hasattr(self.location_geog, 'y'):
                    location_geog_dict = {
                        "latitude": float(self.location_geog.y),
                        "longitude": float(self.location_geog.x),
                    }
                elif hasattr(self.location_geog, 'data'):
                    # If it's a WKBElement, we might need to use ST_X/ST_Y functions
                    # For now, return WKT representation
                    location_geog_dict = {"wkt": str(self.location_geog)}
            except (AttributeError, ValueError):
                # Fallback to string representation
                location_geog_dict = {"wkt": str(self.location_geog)}
        return {
            "id": self.id,
            "author_id": self.author_id,
            "post_type": self.post_type,
            "content": self.content,
            "attachments": self.attachments,
            "requirements": self.requirements,
            "skills": self.skills if self.skills else [],
            "tags": self.tags if self.tags else [],
            "github_repo_fullname": self.github_repo_fullname,
            "github_repo_url": self.github_repo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "location_geog": location_geog_dict,
        }

