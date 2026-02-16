"""
Cofounder profile model for the Eigen platform.
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
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from enum import Enum

from ..base import Base


class TechnicalLevel(str, Enum):
    NON_TECHNICAL = "non_technical"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    STUDENT = "student"
    BETWEEN_JOBS = "between_jobs"


class CommitmentTimeline(str, Enum):
    ALREADY_FULLTIME = "already_fulltime"
    READY_NOW = "ready_now"
    WITHIN_6_MONTHS = "within_6_months"
    WITHIN_1_YEAR = "within_1_year"
    EXPLORING = "exploring"


class IdeaStatus(str, Enum):
    COMMITTED_TO_IDEA = "committed_to_idea"
    HAVE_IDEAS_OPEN_TO_OTHERS = "have_ideas_open_to_others"
    OPEN_TO_EXPLORE = "open_to_explore"


class RemotePreference(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    IN_PERSON = "in_person"
    FLEXIBLE = "flexible"


class CofounderProfile(Base):
    __tablename__ = "cofounder_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255),
        ForeignKey("users.clerk_user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # About yourself
    elevator_pitch = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    impressive_accomplishment = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    professional_experience = Column(Text, nullable=True)
    technical_level = Column(SQLEnum(TechnicalLevel), nullable=True)
    primary_roles = Column(ARRAY(Text), nullable=True)
    industries = Column(ARRAY(Text), nullable=True)
    employment_status = Column(SQLEnum(EmploymentStatus), nullable=True)
    commitment_timeline = Column(SQLEnum(CommitmentTimeline), nullable=True)
    idea_status = Column(SQLEnum(IdeaStatus), nullable=True)
    ideas_description = Column(Text, nullable=True)
    has_cofounder = Column(Boolean, default=False, nullable=False)
    responsibility_areas = Column(ARRAY(Text), nullable=True)
    equity_expectations = Column(Text, nullable=True)
    remote_preference = Column(SQLEnum(RemotePreference), nullable=True)
    free_time = Column(Text, nullable=True)
    life_story = Column(Text, nullable=True)
    anything_else = Column(Text, nullable=True)

    # Preferences
    looking_for_description = Column(Text, nullable=True)
    preferences = Column(JSONB, nullable=True, default=dict)

    # Meta
    is_complete = Column(Boolean, default=False, nullable=False)
    completion_score = Column(Integer, default=0, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="cofounder_profile")

    __table_args__ = (
        Index("idx_cofounder_profile_user_id", "user_id"),
        Index("idx_cofounder_profile_visible", "is_visible"),
        Index("idx_cofounder_profile_complete", "is_complete"),
    )

    def __repr__(self) -> str:
        return f"<CofounderProfile(id={self.id}, user_id='{self.user_id}')>"

    def compute_completion_score(self) -> int:
        """Compute profile completion score (0-100)."""
        fields_weights = {
            "elevator_pitch": 15,
            "technical_level": 10,
            "primary_roles": 10,
            "industries": 10,
            "commitment_timeline": 10,
            "idea_status": 10,
            "looking_for_description": 15,
            "professional_experience": 5,
            "impressive_accomplishment": 5,
            "education": 5,
            "responsibility_areas": 5,
        }
        score = 0
        for field, weight in fields_weights.items():
            value = getattr(self, field, None)
            if value is not None and value != "" and value != []:
                score += weight
        return min(score, 100)

    def update_completion(self):
        """Update completion score and is_complete flag."""
        self.completion_score = self.compute_completion_score()
        self.is_complete = self.completion_score >= 60

    def get_embedding_text(self) -> str:
        """Build text for vector embedding."""
        parts = []
        if self.elevator_pitch:
            parts.append(f"About me: {self.elevator_pitch}")
        if self.professional_experience:
            parts.append(f"Experience: {self.professional_experience}")
        if self.impressive_accomplishment:
            parts.append(f"Accomplishment: {self.impressive_accomplishment}")
        if self.education:
            parts.append(f"Education: {self.education}")
        if self.ideas_description:
            parts.append(f"Ideas: {self.ideas_description}")
        if self.primary_roles:
            parts.append(f"Roles: {', '.join(self.primary_roles)}")
        if self.industries:
            parts.append(f"Industries: {', '.join(self.industries)}")
        if self.technical_level:
            parts.append(f"Technical level: {self.technical_level.value}")
        if self.looking_for_description:
            parts.append(f"Looking for: {self.looking_for_description}")
        if self.responsibility_areas:
            parts.append(f"Responsibilities: {', '.join(self.responsibility_areas)}")
        if self.commitment_timeline:
            parts.append(f"Commitment: {self.commitment_timeline.value}")
        if self.remote_preference:
            parts.append(f"Work style: {self.remote_preference.value}")
        return ". ".join(parts)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "elevator_pitch": self.elevator_pitch,
            "video_url": self.video_url,
            "impressive_accomplishment": self.impressive_accomplishment,
            "education": self.education,
            "professional_experience": self.professional_experience,
            "technical_level": self.technical_level.value if self.technical_level else None,
            "primary_roles": self.primary_roles or [],
            "industries": self.industries or [],
            "employment_status": self.employment_status.value if self.employment_status else None,
            "commitment_timeline": self.commitment_timeline.value if self.commitment_timeline else None,
            "idea_status": self.idea_status.value if self.idea_status else None,
            "ideas_description": self.ideas_description,
            "has_cofounder": self.has_cofounder,
            "responsibility_areas": self.responsibility_areas or [],
            "equity_expectations": self.equity_expectations,
            "remote_preference": self.remote_preference.value if self.remote_preference else None,
            "free_time": self.free_time,
            "life_story": self.life_story,
            "anything_else": self.anything_else,
            "looking_for_description": self.looking_for_description,
            "preferences": self.preferences or {},
            "is_complete": self.is_complete,
            "completion_score": self.completion_score,
            "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
