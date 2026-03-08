import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task

logger = logging.getLogger(__name__)


def calculate_priority_score(task: Task, energy_level: int) -> float:
    """
    Score = (Impact × Urgency) / Energy Required.
    Tasks with energy_required > energy_level are suppressed (score = 0).
    """
    if task.energy_required > energy_level:
        return 0.0
    if task.energy_required == 0:
        return 0.0
    return (task.impact * task.urgency) / task.energy_required


def is_big_rock(task: Task) -> bool:
    return task.energy_required >= 4 and task.impact >= 4


async def rank_tasks_for_user(
    db: AsyncSession,
    user_id: int,
    energy_level: int,
) -> List[Task]:
    """Return ranked active tasks for the user, filtered by energy level."""
    result = await db.execute(
        select(Task).where(
            Task.user_id == user_id,
            Task.status == "active",
        )
    )
    tasks = result.scalars().all()

    # Update big_rock flags and scores
    for task in tasks:
        task.is_big_rock = is_big_rock(task)
        task.priority_score = calculate_priority_score(task, energy_level)

    await db.commit()

    # Filter suppressed tasks and sort by score descending
    ranked = sorted(
        [t for t in tasks if t.priority_score > 0],
        key=lambda t: t.priority_score,
        reverse=True,
    )
    return ranked


async def get_next_task(
    db: AsyncSession,
    user_id: int,
    energy_level: int,
) -> Optional[Task]:
    """Get the single best task for the user's current energy level."""
    ranked = await rank_tasks_for_user(db, user_id, energy_level)
    if not ranked:
        return None
    task = ranked[0]
    await db.refresh(task)
    return task
