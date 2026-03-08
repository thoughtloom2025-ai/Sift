from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EnergyLog(Base):
    __tablename__ = "energy_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 1-5
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    session_id = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="energy_logs")
