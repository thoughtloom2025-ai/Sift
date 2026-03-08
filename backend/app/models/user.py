from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True, unique=True, index=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    energy_logs = relationship("EnergyLog", back_populates="user", cascade="all, delete-orphan")
    fresh_start_logs = relationship("FreshStartLog", back_populates="user", cascade="all, delete-orphan")
    daily_stats = relationship("DailyStats", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    # Relationship
    user = relationship("User", back_populates="refresh_tokens")
