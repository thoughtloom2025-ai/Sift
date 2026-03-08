from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Sift"
    DATABASE_URL: str = "postgresql+asyncpg://sift:siftpass@localhost:5432/sift"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    NOTION_CLIENT_ID: str = ""
    NOTION_CLIENT_SECRET: str = ""

    GEMINI_API_KEY: str = ""
    ENCRYPTION_KEY: str = ""

    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    FRESH_START_THRESHOLD_HOURS: int = 18
    SYNC_INTERVAL_MINUTES: int = 30

    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
