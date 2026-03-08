import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_admin
from app.models.user import User
from app.models.task import Task
from app.models.integration import Integration, SyncLog
from app.schemas.auth import UserResponse
from app.schemas.analytics import AdminStats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all()


@router.put("/users/{user_id}")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    await db.commit()
    return {"message": f"User {user_id} {'activated' if is_active else 'deactivated'}"}


@router.get("/stats", response_model=AdminStats)
async def get_platform_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0

    total_tasks_result = await db.execute(select(func.count(Task.id)))
    total_tasks = total_tasks_result.scalar() or 0

    total_integrations_result = await db.execute(
        select(func.count(Integration.id)).where(Integration.is_active == True)
    )
    total_integrations = total_integrations_result.scalar() or 0

    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    syncs_result = await db.execute(
        select(func.count(SyncLog.id)).where(SyncLog.synced_at >= last_24h)
    )
    syncs_last_24h = syncs_result.scalar() or 0

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_tasks=total_tasks,
        total_integrations=total_integrations,
        syncs_last_24h=syncs_last_24h,
    )


@router.get("/integrations")
async def get_integration_health(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Integration).order_by(Integration.last_synced_at.desc()).limit(100)
    )
    integrations = result.scalars().all()
    return [
        {
            "id": i.id,
            "user_id": i.user_id,
            "provider": i.provider,
            "is_active": i.is_active,
            "last_synced_at": i.last_synced_at,
        }
        for i in integrations
    ]


@router.get("/sync-logs")
async def get_sync_logs(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SyncLog).order_by(SyncLog.synced_at.desc()).limit(100)
    )
    logs = result.scalars().all()
    return [
        {
            "id": l.id,
            "integration_id": l.integration_id,
            "synced_at": l.synced_at,
            "items_imported": l.items_imported,
            "status": l.status,
            "error_message": l.error_message,
        }
        for l in logs
    ]
