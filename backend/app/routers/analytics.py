import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.analytics import DailyStats
from app.models.freshstart import FreshStartLog
from app.schemas.analytics import AnalyticsSummary, DailyTrend, CompletionRate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Tasks completed in last 7 days
    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.completed_at >= seven_days_ago,
        )
    )
    total_completed = completed_result.scalar() or 0

    big_rocks_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.is_big_rock == True,
            Task.completed_at >= seven_days_ago,
        )
    )
    big_rocks = big_rocks_result.scalar() or 0

    easy_wins_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.energy_required <= 2,
            Task.completed_at >= seven_days_ago,
        )
    )
    easy_wins = easy_wins_result.scalar() or 0

    fresh_starts_result = await db.execute(
        select(func.count(FreshStartLog.id)).where(
            FreshStartLog.user_id == current_user.id,
            FreshStartLog.triggered_at >= seven_days_ago,
        )
    )
    fresh_starts = fresh_starts_result.scalar() or 0

    # Average energy from DailyStats
    stats_result = await db.execute(
        select(func.avg(DailyStats.avg_energy_level)).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= seven_days_ago.date(),
        )
    )
    avg_energy = stats_result.scalar() or 3.0

    days_result = await db.execute(
        select(func.count(DailyStats.id)).where(DailyStats.user_id == current_user.id)
    )
    days_tracked = days_result.scalar() or 0

    return AnalyticsSummary(
        total_tasks_completed=total_completed,
        avg_energy_level=round(float(avg_energy), 2),
        big_rocks_completed=big_rocks,
        easy_wins_completed=easy_wins,
        fresh_starts_triggered=fresh_starts,
        days_tracked=days_tracked,
    )


@router.get("/trends", response_model=List[DailyTrend])
async def get_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyStats)
        .where(DailyStats.user_id == current_user.id)
        .order_by(DailyStats.date.desc())
        .limit(30)
    )
    return result.scalars().all()


@router.get("/completion-rate", response_model=CompletionRate)
async def get_completion_rate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        select(func.count(Task.id)).where(Task.user_id == current_user.id)
    )
    total = total_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
        )
    )
    completed = completed_result.scalar() or 0

    big_rock_total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.is_big_rock == True,
        )
    )
    big_rock_total = big_rock_total_result.scalar() or 0

    big_rock_completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.is_big_rock == True,
            Task.status == "completed",
        )
    )
    big_rock_completed = big_rock_completed_result.scalar() or 0

    return CompletionRate(
        total_tasks=total,
        completed_tasks=completed,
        completion_rate=round(completed / total * 100, 1) if total > 0 else 0.0,
        big_rock_completion_rate=round(big_rock_completed / big_rock_total * 100, 1) if big_rock_total > 0 else 0.0,
    )
