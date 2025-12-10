"""
Embedding sync status models for the Eigen platform.
"""

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from ..base import Base


class EmbeddingSyncStatus(Base):
    __tablename__ = "embedding_sync_status"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(255), nullable=False)
    qdrant_synced = Column(Boolean, default=False, nullable=False)
    qdrant_collection = Column(String(100), nullable=True)
    neo4j_synced = Column(Boolean, default=False, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_sync_entity"),
        Index("idx_sync_pending", "qdrant_synced", "neo4j_synced"),
        Index("idx_sync_entity_type", "entity_type"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "qdrant_synced": self.qdrant_synced,
            "qdrant_collection": self.qdrant_collection,
            "neo4j_synced": self.neo4j_synced,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "last_error": self.last_error,
            "retry_count": self.retry_count,
        }
