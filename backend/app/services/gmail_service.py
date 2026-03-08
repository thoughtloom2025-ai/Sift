import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import Integration
from app.auth.encryption import decrypt_token, encrypt_token
from app.config import settings

logger = logging.getLogger(__name__)


def _fetch_gmail_sync(access_token: str, refresh_token: str | None) -> tuple[list[dict], str | None]:
    """
    Synchronous Gmail fetch — run via asyncio.to_thread to avoid blocking the event loop.
    Returns (tasks, new_access_token_if_refreshed).
    """
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    client_id = settings.GMAIL_CLIENT_ID or settings.GOOGLE_CLIENT_ID
    client_secret = settings.GMAIL_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    new_token: str | None = None
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        new_token = creds.token

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    result = service.users().messages().list(
        userId="me",
        q="is:unread in:inbox",
        maxResults=50,
    ).execute()

    messages = result.get("messages", [])
    tasks = []

    for msg in messages[:20]:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "No Subject")
        from_addr = headers.get("From", "")
        snippet = msg_data.get("snippet", "")

        tasks.append({
            "source_id": msg["id"],
            "raw_content": f"Email from {from_addr}: {subject}\n{snippet}",
        })

    return tasks, new_token


async def fetch_gmail_tasks(integration: Integration, db: AsyncSession | None = None) -> list[dict]:
    """Fetch unread emails from Gmail and return as raw task items."""
    access_token = decrypt_token(integration.access_token or "")
    refresh_token = decrypt_token(integration.refresh_token or "") if integration.refresh_token else None

    if not access_token:
        logger.warning(f"No access token for Gmail integration {integration.id}")
        return []

    try:
        tasks, new_token = await asyncio.to_thread(_fetch_gmail_sync, access_token, refresh_token)

        # Persist refreshed token so next sync doesn't fail
        if new_token and db:
            integration.access_token = encrypt_token(new_token)
            await db.commit()

        return tasks
    except Exception as e:
        logger.error(f"Gmail fetch failed for integration {integration.id}: {e}")
        return []
