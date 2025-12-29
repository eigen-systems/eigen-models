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
    request_details = Column(
        JSONB,
        nullable=True,
        comment="Request post details: {compensation_type, stipend_amount, stipend_currency, duration_type, duration_value, work_type, location, application_deadline, positions_available}"
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

    # Location coordinates
    latitude = Column(
        Float,
        nullable=True,
        comment="Latitude coordinate"
    )
    longitude = Column(
        Float,
        nullable=True,
        comment="Longitude coordinate"
    )

    # Linked project (optional)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Linked project for the post"
    )

    # Relationships
    author = relationship("User", backref="posts")
    project = relationship("Project", back_populates="linked_posts")
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "post_type IN ('general', 'request')",
            name="ck_post_type"
        ),
        Index("idx_post_author_id", "author_id"),
        Index("idx_post_type", "post_type"),
        Index("idx_post_created_at", "created_at"),
        Index("idx_post_project_id", "project_id"),
        # GIN indexes for efficient array containment queries
        Index("idx_post_tags_gin", "tags", postgresql_using="gin"),
        Index("idx_post_skills_gin", "skills", postgresql_using="gin"),
        # Composite index for author + created_at (common feed query pattern)
        Index("idx_post_author_created", "author_id", "created_at"),
        {"comment": "User posts including general posts and request posts"},
    )
    
    def __repr__(self) -> str:
        return f"<Post(id={self.id}, author_id='{self.author_id}', post_type='{self.post_type}')>"
    
    def to_dict(self) -> dict:
        """Convert post to dictionary for API responses."""
        result = {
            "id": self.id,
            "author_id": self.author_id,
            "post_type": self.post_type,
            "content": self.content,
            "attachments": self.attachments,
            "requirements": self.requirements,
            "request_details": self.request_details,
            "skills": self.skills if self.skills else [],
            "tags": self.tags if self.tags else [],
            "github_repo_fullname": self.github_repo_fullname,
            "github_repo_url": self.github_repo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "project_id": self.project_id,
        }
        # Include project info if relationship is loaded
        if self.project_id and self.project:
            result["project"] = {
                "id": self.project.id,
                "title": self.project.title,
                "description": self.project.description,
                "visibility": self.project.visibility,
                "owner_id": self.project.owner_id,
                "member_count": self.project.member_count,
            }
        return result

