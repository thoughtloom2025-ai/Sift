import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.integration import Integration, SyncLog
from app.models.task import Task, TaskMetadata
from app.auth.encryption import decrypt_token
from app.services.gemini_service import extract_task_entities

logger = logging.getLogger(__name__)


async def sync_integration(db: AsyncSession, integration: Integration) -> SyncLog:
    """Sync a single integration and return the sync log."""
    log = SyncLog(
        integration_id=integration.id,
        items_imported=0,
        items_updated=0,
        status="success",
    )
    try:
        if integration.provider == "gmail":
            from app.services.gmail_service import fetch_gmail_tasks
            items = await fetch_gmail_tasks(integration, db)
        elif integration.provider == "slack":
            from app.services.slack_service import fetch_slack_tasks
            items = await fetch_slack_tasks(integration)
        elif integration.provider == "notion":
            from app.services.notion_service import fetch_notion_tasks
            items = await fetch_notion_tasks(integration)
        else:
            logger.warning(f"Unknown provider: {integration.provider}")
            items = []

        imported, updated = await _upsert_tasks(db, integration, items)
        log.items_imported = imported
        log.items_updated = updated
        integration.last_synced_at = datetime.now(timezone.utc)

    except Exception as e:
        logger.error(f"Sync failed for integration {integration.id} ({integration.provider}): {e}")
        log.status = "error"
        log.error_message = str(e)

    db.add(log)
    await db.commit()
    return log


async def _upsert_tasks(
    db: AsyncSession,
    integration: Integration,
    raw_items: list[dict],
) -> tuple[int, int]:
    """Import raw items as tasks, using LLM extraction. Returns (imported, updated)."""
    imported = 0
    updated = 0

    for item in raw_items:
        source_id = item.get("source_id")
        raw_content = item.get("raw_content", "")

        # Check for existing task (deduplication)
        existing = None
        if source_id:
            result = await db.execute(
                select(Task).where(
                    Task.user_id == integration.user_id,
                    Task.source == integration.provider,
                    Task.source_id == source_id,
                )
            )
            existing = result.scalar_one_or_none()

        if existing and existing.status != "active":
            continue  # Don't update archived/completed tasks

        # Run LLM extraction
        entities = await extract_task_entities(raw_content)

        if existing:
            existing.title = entities["title"]
            existing.impact = entities["impact"]
            existing.urgency = entities["urgency"]
            existing.energy_required = entities["energy_required"]
            existing.is_big_rock = entities["is_big_rock"]
            updated += 1
        else:
            task = Task(
                user_id=integration.user_id,
                title=entities["title"],
                description=raw_content[:1000] if raw_content else None,
                source=integration.provider,
                source_id=source_id,
                impact=entities["impact"],
                urgency=entities["urgency"],
                energy_required=entities["energy_required"],
                is_big_rock=entities["is_big_rock"],
            )
            db.add(task)
            await db.flush()

            meta = TaskMetadata(
                task_id=task.id,
                raw_content=raw_content,
                extracted_entities=entities,
                llm_model_used="gemini-1.5-flash",
            )
            db.add(meta)
            imported += 1

    await db.commit()
    return imported, updated


async def sync_all_users(db: AsyncSession) -> None:
    """Sync all active integrations across all users."""
    result = await db.execute(
        select(Integration).where(Integration.is_active == True)
    )
    integrations = result.scalars().all()

    for integration in integrations:
        try:
            await sync_integration(db, integration)
        except Exception as e:
            logger.error(f"Failed to sync integration {integration.id}: {e}")
