"""
GitHub repository models for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
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

from ..base import Base


class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_repo_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    html_url = Column(String(512), nullable=False)
    clone_url = Column(String(512), nullable=True)
    languages = Column(ARRAY(Text), nullable=True)
    primary_language = Column(String(100), nullable=True)
    topics = Column(ARRAY(Text), nullable=True)
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)
    is_fork = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    default_branch = Column(String(100), default="main")
    size_kb = Column(Integer, nullable=True)
    license_name = Column(String(100), nullable=True)
    readme_content = Column(Text, nullable=True)
    llm_summary = Column(Text, nullable=True)
    frameworks_detected = Column(ARRAY(Text), nullable=True)
    dependencies = Column(JSONB, nullable=True)
    last_push_at = Column(DateTime, nullable=True)
    repo_created_at = Column(DateTime, nullable=True)
    last_synced_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", backref="repositories")

    __table_args__ = (
        Index("idx_github_repo_user_id", "user_id"),
        Index("idx_github_repo_languages", "languages", postgresql_using="gin"),
        Index("idx_github_repo_topics", "topics", postgresql_using="gin"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "github_repo_id": self.github_repo_id,
            "full_name": self.full_name,
            "name": self.name,
            "description": self.description,
            "html_url": self.html_url,
            "languages": self.languages or [],
            "primary_language": self.primary_language,
            "topics": self.topics or [],
            "stars_count": self.stars_count,
            "forks_count": self.forks_count,
            "is_fork": self.is_fork,
            "is_private": self.is_private,
            "llm_summary": self.llm_summary,
            "frameworks_detected": self.frameworks_detected or [],
            "last_push_at": self.last_push_at.isoformat() if self.last_push_at else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
        }
