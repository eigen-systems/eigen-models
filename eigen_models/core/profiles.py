"""
Profile models for the Eigen platform.

This module contains models for user profiles, storing extended user information
including professional details, skills, GitHub integration status, and resume information.
"""

import datetime
from sqlalchemy import (
    Boolean,
    BigInteger,
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


class Profile(Base):
    """
    Profile model representing extended user profile information.
    
    This model stores professional profile data including headline, bio, skills,
    location, timezone, GitHub connection status, and resume information.
    
    Attributes:
        id: Primary key integer field
        user_id: Foreign key to the users table (references clerk_user_id)
        headline: Professional headline or title
        bio: User's biography or description
        skills: Array of canonical skills
        timezone: User's timezone
        location_geog: Geographic point (latitude, longitude) using WGS84 (SRID 4326)
        location: User's location/city (text description)
        state: User's state/province
        country: User's country
        pin: Postal/ZIP code
        district: User's district/region
        github_connected: Whether GitHub account is connected
        github_username: GitHub username if connected
        github_user_id: GitHub user ID if connected
        github_last_synced: Timestamp of last GitHub sync
        resume_uploaded: Whether resume has been uploaded
        resume_file_url: URL to uploaded resume file
        resume_text: Extracted text content from resume
        resume_json: Structured JSON data from resume parsing
        created_at: When the profile was created
        updated_at: When the profile was last modified
    """
    
    __tablename__ = "profiles"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Primary key for profile"
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
    
    # Profile information
    headline = Column(Text, nullable=True, comment="Professional headline or title")
    bio = Column(Text, nullable=True, comment="User's biography or description")
    skills = Column(
        ARRAY(Text),
        nullable=True,
        comment="Canonical list of skills"
    )
    timezone = Column(String(255), nullable=True, comment="User's timezone")
    
    # Geographic location
    location_geog = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        comment="Geographic point (latitude, longitude) using WGS84 (SRID 4326)"
    )
    location = Column(String(255), nullable=True, comment="User's location/city")
    state = Column(String(255), nullable=True, comment="User's state/province")
    country = Column(String(255), nullable=True, comment="User's country")
    pin = Column(String(50), nullable=True, comment="Postal/ZIP code")
    district = Column(String(255), nullable=True, comment="User's district/region")
    
    # GitHub integration status
    github_connected = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether GitHub account is connected"
    )
    github_username = Column(Text, nullable=True, comment="GitHub username if connected")
    github_user_id = Column(
        BigInteger,
        nullable=True,
        comment="GitHub user ID if connected"
    )
    github_last_synced = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last GitHub sync"
    )
    
    # Resume information
    resume_uploaded = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether resume has been uploaded"
    )
    resume_file_url = Column(Text, nullable=True, comment="URL to uploaded resume file")
    resume_text = Column(Text, nullable=True, comment="Extracted text content from resume")
    resume_json = Column(JSONB, nullable=True, comment="Structured JSON data from resume parsing")
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="When the profile was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="When the profile was last modified"
    )
    
    # Relationship
    user = relationship("User", backref="profile")
    
    # Table constraints and indexes
    __table_args__ = (
        Index("idx_profile_user_id", "user_id"),
        Index("idx_profile_github_user_id", "github_user_id"),
        # Spatial index for geographic queries (PostGIS will create GIST index)
        {"comment": "User profile information and professional details"},
    )
    
    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, user_id='{self.user_id}', headline='{self.headline}')>"
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary for API responses."""
        # Handle Geography POINT serialization
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
            "user_id": self.user_id,
            "headline": self.headline,
            "bio": self.bio,
            "skills": self.skills if self.skills else [],
            "timezone": self.timezone,
            "location_geog": location_geog_dict,
            "location": self.location,
            "state": self.state,
            "country": self.country,
            "pin": self.pin,
            "district": self.district,
            "github_connected": self.github_connected,
            "github_username": self.github_username,
            "github_user_id": self.github_user_id,
            "github_last_synced": self.github_last_synced.isoformat() if self.github_last_synced else None,
            "resume_uploaded": self.resume_uploaded,
            "resume_file_url": self.resume_file_url,
            "resume_text": self.resume_text,
            "resume_json": self.resume_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

