import logging
import secrets
import urllib.parse
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.encryption import encrypt_token
from app.models.integration import Integration, SyncLog
from app.models.user import User
from app.schemas.integration import IntegrationResponse, SyncLogResponse, SyncResult
from app.services.sync_service import sync_integration
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    return result.scalars().all()


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    integration.is_active = False
    integration.access_token = None
    integration.refresh_token = None
    await db.commit()
    return {"message": f"{integration.provider} disconnected"}


@router.post("/sync", response_model=List[SyncResult])
async def sync_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.is_active == True,
        )
    )
    integrations = result.scalars().all()
    results = []
    for integration in integrations:
        log = await sync_integration(db, integration)
        results.append(SyncResult(
            integration_id=integration.id,
            provider=integration.provider,
            items_imported=log.items_imported,
            items_updated=log.items_updated,
            status=log.status,
            error_message=log.error_message,
        ))
    return results


@router.post("/sync/{integration_id}", response_model=SyncResult)
async def sync_one(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    log = await sync_integration(db, integration)
    return SyncResult(
        integration_id=integration.id,
        provider=integration.provider,
        items_imported=log.items_imported,
        items_updated=log.items_updated,
        status=log.status,
        error_message=log.error_message,
    )


@router.get("/sync-logs", response_model=List[SyncLogResponse])
async def get_sync_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SyncLog)
        .join(Integration, SyncLog.integration_id == Integration.id)
        .where(Integration.user_id == current_user.id)
        .order_by(SyncLog.synced_at.desc())
        .limit(50)
    )
    return result.scalars().all()


# --- OAuth flows for each provider ---

def _make_state(user_id: int) -> str:
    """Encode user_id into the state token for stateless OAuth callbacks."""
    token = secrets.token_urlsafe(24)
    return f"{user_id}.{token}"


def _parse_state_user_id(state: str) -> int | None:
    """Extract user_id from state token. Returns None if malformed."""
    try:
        user_id_str, _ = state.split(".", 1)
        return int(user_id_str)
    except (ValueError, AttributeError):
        return None


@router.get("/auth/gmail")
async def gmail_oauth_start(current_user: User = Depends(get_current_user)):
    state = _make_state(current_user.id)
    params = {
        "client_id": settings.GMAIL_CLIENT_ID or settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/gmail/callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {"url": url}


@router.get("/auth/gmail/callback")
async def gmail_oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    user_id = _parse_state_user_id(state)
    if not user_id:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=invalid_state")

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GMAIL_CLIENT_ID or settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/gmail/callback",
                },
            )
            token_data = token_response.json()

        if "error" in token_data:
            logger.error(f"Gmail token exchange failed: {token_data['error']}")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=gmail_auth_failed")

        result = await db.execute(
            select(Integration).where(
                Integration.user_id == user_id,
                Integration.provider == "gmail",
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            integration.access_token = encrypt_token(token_data["access_token"])
            if token_data.get("refresh_token"):
                integration.refresh_token = encrypt_token(token_data["refresh_token"])
            integration.is_active = True
        else:
            integration = Integration(
                user_id=user_id,
                provider="gmail",
                access_token=encrypt_token(token_data["access_token"]),
                refresh_token=encrypt_token(token_data["refresh_token"]) if token_data.get("refresh_token") else None,
                is_active=True,
            )
            db.add(integration)

        await db.commit()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?connected=gmail")
    except Exception as e:
        logger.error(f"Gmail OAuth callback failed: {e}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=gmail_auth_failed")


@router.get("/auth/slack")
async def slack_oauth_start(current_user: User = Depends(get_current_user)):
    state = _make_state(current_user.id)
    params = {
        "client_id": settings.SLACK_CLIENT_ID,
        "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/slack/callback",
        "scope": "channels:history,im:history,users:read",
        "state": state,
    }
    url = "https://slack.com/oauth/v2/authorize?" + urllib.parse.urlencode(params)
    return {"url": url}


@router.get("/auth/slack/callback")
async def slack_oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    user_id = _parse_state_user_id(state)
    if not user_id:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=invalid_state")

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.SLACK_CLIENT_ID,
                    "client_secret": settings.SLACK_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/slack/callback",
                },
            )
            token_data = token_response.json()

        if not token_data.get("ok"):
            logger.error(f"Slack token exchange failed: {token_data.get('error')}")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=slack_auth_failed")

        access_token = token_data["access_token"]

        result = await db.execute(
            select(Integration).where(
                Integration.user_id == user_id,
                Integration.provider == "slack",
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            integration.access_token = encrypt_token(access_token)
            integration.is_active = True
        else:
            integration = Integration(
                user_id=user_id,
                provider="slack",
                access_token=encrypt_token(access_token),
                is_active=True,
            )
            db.add(integration)

        await db.commit()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?connected=slack")
    except Exception as e:
        logger.error(f"Slack OAuth callback failed: {e}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=slack_auth_failed")


@router.get("/auth/notion")
async def notion_oauth_start(current_user: User = Depends(get_current_user)):
    state = _make_state(current_user.id)
    params = {
        "client_id": settings.NOTION_CLIENT_ID,
        "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/notion/callback",
        "response_type": "code",
        "state": state,
    }
    url = "https://api.notion.com/v1/oauth/authorize?" + urllib.parse.urlencode(params)
    return {"url": url}


@router.get("/auth/notion/callback")
async def notion_oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    user_id = _parse_state_user_id(state)
    if not user_id:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=invalid_state")

    try:
        import httpx
        import base64
        credentials = base64.b64encode(
            f"{settings.NOTION_CLIENT_ID}:{settings.NOTION_CLIENT_SECRET}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://api.notion.com/v1/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": f"{settings.BACKEND_URL}/api/v1/integrations/auth/notion/callback",
                },
                headers={"Authorization": f"Basic {credentials}"},
            )
            token_data = token_response.json()

        if "error" in token_data:
            logger.error(f"Notion token exchange failed: {token_data['error']}")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=notion_auth_failed")

        access_token = token_data["access_token"]

        result = await db.execute(
            select(Integration).where(
                Integration.user_id == user_id,
                Integration.provider == "notion",
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            integration.access_token = encrypt_token(access_token)
            integration.is_active = True
        else:
            integration = Integration(
                user_id=user_id,
                provider="notion",
                access_token=encrypt_token(access_token),
                is_active=True,
            )
            db.add(integration)

        await db.commit()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?connected=notion")
    except Exception as e:
        logger.error(f"Notion OAuth callback failed: {e}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings/integrations?error=notion_auth_failed")
