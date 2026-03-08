from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    oauth_provider: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
