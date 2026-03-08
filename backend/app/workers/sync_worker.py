import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def run_sync_job() -> None:
    """Periodic sync job — syncs all active integrations for all users."""
    logger.info("Running periodic integration sync...")
    try:
        from app.database import AsyncSessionLocal
        from app.services.sync_service import sync_all_users
        async with AsyncSessionLocal() as db:
            await sync_all_users(db)
    except Exception as e:
        logger.error(f"Sync job failed: {e}")


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(
            run_sync_job,
            "interval",
            minutes=settings.SYNC_INTERVAL_MINUTES,
            id="sync_job",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Sync scheduler started (interval: {settings.SYNC_INTERVAL_MINUTES}m)")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Sync scheduler stopped")
