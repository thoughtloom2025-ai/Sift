import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, SnoozeRequest, SubStepsUpdate
from app.services.ranking_service import get_next_task, rank_tasks_for_user
from app.services.gemini_service import generate_task_breakdown, extract_task_entities

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.user_id == current_user.id)
    if status:
        query = query.where(Task.status == status)
    if source:
        query = query.where(Task.source == source)
    query = query.order_by(Task.priority_score.desc(), Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.ranking_service import is_big_rock, calculate_priority_score

    impact = task_data.impact
    urgency = task_data.urgency
    energy_required = task_data.energy_required

    # If any ratings are missing, ask Gemini to infer them
    if impact is None or urgency is None or energy_required is None:
        combined = task_data.title
        if task_data.description:
            combined += f"\n{task_data.description}"
        entities = await extract_task_entities(combined)
        impact = impact if impact is not None else entities["impact"]
        urgency = urgency if urgency is not None else entities["urgency"]
        energy_required = energy_required if energy_required is not None else entities["energy_required"]

    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        source="manual",
        impact=impact,
        urgency=urgency,
        energy_required=energy_required,
    )
    task.is_big_rock = is_big_rock(task)
    task.priority_score = calculate_priority_score(task, energy_level=3)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/next", response_model=Optional[TaskResponse])
async def get_next(
    energy_level: int = Query(3, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_next_task(db, current_user.id, energy_level)
    return task


@router.get("/eligible", response_model=List[TaskResponse])
async def get_eligible(
    energy_level: int = Query(3, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tasks = await rank_tasks_for_user(db, current_user.id, energy_level)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
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
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.ranking_service import is_big_rock, calculate_priority_score
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update.title is not None:
        task.title = update.title
    if update.description is not None:
        task.description = update.description
    if update.impact is not None:
        task.impact = update.impact
    if update.urgency is not None:
        task.urgency = update.urgency
    if update.energy_required is not None:
        task.energy_required = update.energy_required

    task.is_big_rock = is_big_rock(task)
    task.priority_score = calculate_priority_score(task, energy_level=3)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(
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
    task.status = "archived"
    task.archived_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Task archived"}


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
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
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/snooze", response_model=TaskResponse)
async def snooze_task(
    task_id: int,
    snooze: SnoozeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "snoozed"
    task.snooze_until = snooze.snooze_until
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/archive", response_model=TaskResponse)
async def archive_task(
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
    task.status = "archived"
    task.archived_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/breakdown", response_model=SubStepsUpdate)
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


@router.put("/{task_id}/substeps", response_model=TaskResponse)
async def update_substeps(
    task_id: int,
    update: SubStepsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.sub_steps = update.sub_steps
    await db.commit()
    await db.refresh(task)
    return task
