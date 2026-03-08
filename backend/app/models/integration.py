from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Integration(Base):
    __tablename__ = "integrations"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_integration_user_provider"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # gmail, slack, notion
    access_token = Column(Text, nullable=True)      # encrypted
    refresh_token = Column(Text, nullable=True)     # encrypted
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="integrations")
    sync_logs = relationship("SyncLog", back_populates="integration", cascade="all, delete-orphan")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    items_imported = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    status = Column(String(20), default="success", nullable=False)  # success, error
    error_message = Column(Text, nullable=True)

    # Relationships
    integration = relationship("Integration", back_populates="sync_logs")
