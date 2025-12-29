import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class ProjectCompletion(Base):
    __tablename__ = "project_completions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for project completion"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Foreign key to projects table"
    )
    completed_by = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who marked the project as complete"
    )
    completion_text = Column(
        Text,
        nullable=True,
        comment="Summary text describing the project completion"
    )
    completion_attachments = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Attachments: {images: [], files: [], links: []}"
    )
    achievements = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of achievements/milestones completed"
    )
    testimonials = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Testimonials from team members: [{user_id, text, rating, created_at}]"
    )
    metrics = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Project metrics: {duration_days, team_size, commits, etc.}"
    )
    is_featured = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this completion is featured in success stories"
    )
    featured_at = Column(
        DateTime,
        nullable=True,
        comment="When the completion was featured"
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the project was marked complete"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the completion was last updated"
    )

    project = relationship(
        "Project",
        back_populates="completion"
    )
    completed_by_user = relationship(
        "User",
        foreign_keys=[completed_by]
    )

    __table_args__ = (
        Index("idx_project_completion_project", "project_id"),
        Index("idx_project_completion_completed_by", "completed_by"),
        Index("idx_project_completion_featured", "is_featured"),
        Index("idx_project_completion_created", "created_at"),
        {"comment": "Project completion records for success stories"},
    )

    def __repr__(self) -> str:
        return f"<ProjectCompletion(id={self.id}, project_id={self.project_id})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "completed_by": self.completed_by,
            "completion_text": self.completion_text,
            "completion_attachments": self.completion_attachments if self.completion_attachments else {"images": [], "files": [], "links": []},
            "achievements": self.achievements if self.achievements else [],
            "testimonials": self.testimonials if self.testimonials else [],
            "metrics": self.metrics if self.metrics else {},
            "is_featured": self.is_featured,
            "featured_at": self.featured_at.isoformat() if self.featured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
