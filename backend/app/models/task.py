from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(20), nullable=False, index=True)   # gmail, slack, notion, manual
    source_id = Column(String(500), nullable=True)             # external reference ID
    impact = Column(Integer, default=3, nullable=False)        # 1-5
    urgency = Column(Integer, default=3, nullable=False)       # 1-5
    energy_required = Column(Integer, default=3, nullable=False)  # 1-5
    priority_score = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="active", nullable=False, index=True)  # active, completed, archived, snoozed
    is_big_rock = Column(Boolean, default=False, nullable=False)
    sub_steps = Column(JSON, nullable=True)       # list of strings
    snooze_until = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    metadata_record = relationship("TaskMetadata", back_populates="task", uselist=False, cascade="all, delete-orphan")


class TaskMetadata(Base):
    __tablename__ = "task_metadata"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    raw_content = Column(Text, nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    llm_model_used = Column(String(100), nullable=True)
    extraction_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="metadata_record")
