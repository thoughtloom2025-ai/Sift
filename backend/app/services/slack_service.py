import logging
from app.models.integration import Integration
from app.auth.encryption import decrypt_token

logger = logging.getLogger(__name__)


async def fetch_slack_tasks(integration: Integration) -> list[dict]:
    """Fetch unresolved DMs and mentions from Slack."""
    access_token = decrypt_token(integration.access_token or "")
    if not access_token:
        logger.warning(f"No access token for Slack integration {integration.id}")
        return []

    try:
        from slack_sdk.web.async_client import AsyncWebClient
        client = AsyncWebClient(token=access_token)

        tasks = []

        # Fetch DMs
        conversations = await client.conversations_list(types="im", limit=10)
        channels = conversations.get("channels", [])

        for channel in channels[:5]:
            history = await client.conversations_history(
                channel=channel["id"],
                limit=10,
            )
            messages = history.get("messages", [])
            for msg in messages:
                if msg.get("text") and not msg.get("bot_id"):
                    tasks.append({
                        "source_id": f"{channel['id']}_{msg['ts']}",
                        "raw_content": f"Slack DM: {msg['text'][:500]}",
                    })

        return tasks[:20]
    except Exception as e:
        logger.error(f"Slack fetch failed for integration {integration.id}: {e}")
        return []
