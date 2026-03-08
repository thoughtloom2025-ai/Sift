import logging
from app.models.integration import Integration
from app.auth.encryption import decrypt_token

logger = logging.getLogger(__name__)


async def fetch_notion_tasks(integration: Integration) -> list[dict]:
    """Fetch unchecked tasks and pages from Notion."""
    access_token = decrypt_token(integration.access_token or "")
    if not access_token:
        logger.warning(f"No access token for Notion integration {integration.id}")
        return []

    try:
        from notion_client import AsyncClient
        client = AsyncClient(auth=access_token)

        tasks = []

        # Search for pages with unchecked to-dos
        search_result = await client.search(
            filter={"value": "page", "property": "object"},
            page_size=20,
        )

        pages = search_result.get("results", [])
        for page in pages[:15]:
            title = ""
            props = page.get("properties", {})

            # Extract title from various property types
            for prop_name, prop_value in props.items():
                if prop_value.get("type") == "title":
                    title_parts = prop_value.get("title", [])
                    title = "".join(p.get("plain_text", "") for p in title_parts)
                    break

            if not title:
                title = "Notion page"

            tasks.append({
                "source_id": page["id"],
                "raw_content": f"Notion: {title}",
            })

        return tasks
    except Exception as e:
        logger.error(f"Notion fetch failed for integration {integration.id}: {e}")
        return []
