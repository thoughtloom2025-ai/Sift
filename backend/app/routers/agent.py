import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskResponse, SubStepsUpdate
from app.services.ranking_service import rank_tasks_for_user
from app.services.gemini_service import extract_task_entities, generate_task_breakdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    title: str
    impact: int
    urgency: int
    energy_required: int
    is_big_rock: bool


class RankResponse(BaseModel):
    tasks: List[TaskResponse]
    energy_level: int
    total_active: int
    suppressed: int


@router.post("/rank", response_model=RankResponse)
async def rank_tasks(
    energy_level: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not 1 <= energy_level <= 5:
        raise HTTPException(status_code=400, detail="energy_level must be 1-5")

    from sqlalchemy import select as sa_select
    all_result = await db.execute(
        sa_select(Task).where(Task.user_id == current_user.id, Task.status == "active")
    )
    total_active = len(all_result.scalars().all())

    ranked = await rank_tasks_for_user(db, current_user.id, energy_level)
    suppressed = total_active - len(ranked)

    return RankResponse(
        tasks=ranked,
        energy_level=energy_level,
        total_active=total_active,
        suppressed=suppressed,
    )


@router.post("/extract", response_model=ExtractResponse)
async def extract_entities(
    req: ExtractRequest,
    current_user: User = Depends(get_current_user),
):
    entities = await extract_task_entities(req.text)
    return ExtractResponse(**entities)


@router.post("/breakdown/{task_id}", response_model=SubStepsUpdate)
async def breakdown_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    steps = await generate_task_breakdown(task.title, task.description)
    task.sub_steps = steps
    await db.commit()
    return SubStepsUpdate(sub_steps=steps)
