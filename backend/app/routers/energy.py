import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.energy import EnergyLog
from app.models.user import User
from app.schemas.energy import EnergyLogCreate, EnergyLogResponse, EnergyHistoryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/energy", tags=["energy"])


@router.post("", response_model=EnergyLogResponse, status_code=201)
async def log_energy(
    data: EnergyLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = EnergyLog(
        user_id=current_user.id,
        level=data.level,
        session_id=data.session_id,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/today", response_model=List[EnergyLogResponse])
async def get_today_energy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(EnergyLog).where(
            EnergyLog.user_id == current_user.id,
            func.date(EnergyLog.logged_at) == today,
        ).order_by(EnergyLog.logged_at.desc())
    )
    return result.scalars().all()


@router.get("/history", response_model=EnergyHistoryResponse)
async def get_energy_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(EnergyLog).where(
            EnergyLog.user_id == current_user.id,
            EnergyLog.logged_at >= thirty_days_ago,
        ).order_by(EnergyLog.logged_at.desc())
    )
    logs = result.scalars().all()

    avg = sum(l.level for l in logs) / len(logs) if logs else 0.0
    unique_days = len(set(l.logged_at.date() for l in logs))

    return EnergyHistoryResponse(
        logs=logs,
        avg_level=round(avg, 2),
        days_tracked=unique_days,
    )
