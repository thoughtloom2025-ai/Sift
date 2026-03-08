import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth.jwt import verify_password, hash_password, create_access_token, create_refresh_token
from app.auth.dependencies import get_current_user
from app.models.user import User, RefreshToken
from app.schemas.auth import RegisterRequest, Token, RefreshRequest, UserResponse, UserUpdate
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username, User.is_active == True))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token_str)


@router.post("/refresh", response_model=Token)
async def refresh_token(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    from app.auth.jwt import decode_token
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id), User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return Token(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if update.full_name is not None:
        current_user.full_name = update.full_name
    if update.avatar_url is not None:
        current_user.avatar_url = update.avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/google")
async def google_login():
    """Initiate Google OAuth flow."""
    import secrets
    import urllib.parse
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BACKEND_URL}/api/v1/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {"url": url, "state": state}


@router.get("/google/callback")
async def google_callback(code: str, state: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.BACKEND_URL}/api/v1/auth/google/callback",
                },
            )
            token_data = token_response.json()

            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            google_user = user_response.json()

        # Find or create user
        result = await db.execute(select(User).where(User.oauth_id == google_user["id"]))
        user = result.scalar_one_or_none()

        if not user:
            result = await db.execute(select(User).where(User.email == google_user["email"]))
            user = result.scalar_one_or_none()

        if user:
            user.oauth_id = google_user["id"]
            user.oauth_provider = "google"
            user.last_login_at = datetime.now(timezone.utc)
            if google_user.get("picture"):
                user.avatar_url = google_user["picture"]
        else:
            user = User(
                email=google_user["email"],
                full_name=google_user.get("name"),
                avatar_url=google_user.get("picture"),
                oauth_provider="google",
                oauth_id=google_user["id"],
                is_verified=True,
                last_login_at=datetime.now(timezone.utc),
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token_str = create_refresh_token({"sub": str(user.id)})

        redirect_url = (
            f"{settings.FRONTEND_URL}/auth/callback"
            f"?access_token={access_token}&refresh_token={refresh_token_str}"
        )
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}")
        raise HTTPException(status_code=400, detail="OAuth authentication failed")


@router.post("/forgot-password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    # In a real app, send an email. For now, just acknowledge.
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    # In a real app, validate the reset token. For now, stub.
    return {"message": "Password reset successfully"}
