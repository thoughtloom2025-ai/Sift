from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    avg_energy_level = Column(Float, nullable=True)
    tasks_completed = Column(Integer, default=0)
    tasks_archived = Column(Integer, default=0)
    big_rocks_completed = Column(Integer, default=0)
    easy_wins_completed = Column(Integer, default=0)
    fresh_starts_triggered = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="daily_stats")
