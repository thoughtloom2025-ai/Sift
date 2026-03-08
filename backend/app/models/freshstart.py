from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FreshStartLog(Base):
    __tablename__ = "fresh_start_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tasks_archived_count = Column(Integer, default=0)
    next_action_task_id = Column(Integer, nullable=True)  # no FK — task may be archived

    # Relationships
    user = relationship("User", back_populates="fresh_start_logs")
