"""
Base model class for all eigen models.

This module provides the foundational SQLAlchemy declarative base and common functionality
shared across all database models in the Eigen platform.
"""

import datetime
from sqlalchemy import Column, Integer, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Define naming conventions for constraints to ensure consistency
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",  # Match PostgreSQL default
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create the declarative base that all models will inherit from
Base = declarative_base(metadata=metadata)


class BaseModel(Base):
    """
    Abstract base model with common fields and functionality.
    
    This class provides standard timestamp fields that are common across
    most models in the Eigen platform. Models can inherit from this class
    to get automatic created_at and updated_at tracking.
    
    Attributes:
        id: Primary key integer field
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime, 
        default=datetime.datetime.utcnow, 
        nullable=False,
        comment="Timestamp when the record was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="Timestamp when the record was last updated"
    )
    
    def __repr__(self) -> str:
        """
        String representation of the model instance.
        
        Returns:
            String showing the class name and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dictionary representation of the model with basic fields
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }