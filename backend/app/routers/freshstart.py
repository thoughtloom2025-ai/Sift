import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.freshstart import FreshStartLog
from app.schemas.freshstart import FreshStartCheck, FreshStartReset, FreshStartLogResponse
from app.schemas.task import TaskResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/freshstart", tags=["freshstart"])


@router.get("/check", response_model=FreshStartCheck)
async def check_fresh_start(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    threshold = settings.FRESH_START_THRESHOLD_HOURS
    last_login = current_user.last_login_at

    if not last_login:
        return FreshStartCheck(
            should_trigger=False,
            hours_since_last_login=0.0,
            threshold_hours=threshold,
        )

    now = datetime.now(timezone.utc)
    if last_login.tzinfo is None:
        last_login = last_login.replace(tzinfo=timezone.utc)

    hours_elapsed = (now - last_login).total_seconds() / 3600
    should_trigger = hours_elapsed >= threshold

    return FreshStartCheck(
        should_trigger=should_trigger,
        hours_since_last_login=round(hours_elapsed, 2),
        threshold_hours=threshold,
    )


@router.post("/reset", response_model=FreshStartReset)
async def fresh_start_reset(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    threshold = settings.FRESH_START_THRESHOLD_HOURS
    cutoff = datetime.now(timezone.utc) - timedelta(hours=threshold)

    # Archive all stale active tasks
    result = await db.execute(
        select(Task).where(
            Task.user_id == current_user.id,
            Task.status == "active",
            Task.created_at <= cutoff,
        )
    )
    stale_tasks = result.scalars().all()

    archived_count = 0
    for task in stale_tasks:
        task.status = "archived"
        task.archived_at = datetime.now(timezone.utc)
        archived_count += 1

    await db.flush()

    # Find the single best next action (lowest energy, highest impact)
    result = await db.execute(
        select(Task).where(
            Task.user_id == current_user.id,
            Task.status == "active",
        ).order_by(Task.energy_required.asc(), Task.impact.desc()).limit(1)
    )
    next_task = result.scalar_one_or_none()

    # Log the fresh start
    log = FreshStartLog(
        user_id=current_user.id,
        tasks_archived_count=archived_count,
        next_action_task_id=next_task.id if next_task else None,
    )
    db.add(log)
    await db.commit()

    return FreshStartReset(
        tasks_archived=archived_count,
        next_action_task=next_task,
        message="Welcome back. Everything's been cleared. Let's start fresh.",
    )


@router.get("/history", response_model=List[FreshStartLogResponse])
async def get_fresh_start_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FreshStartLog)
        .where(FreshStartLog.user_id == current_user.id)
        .order_by(FreshStartLog.triggered_at.desc())
        .limit(20)
    )
    return result.scalars().all()
