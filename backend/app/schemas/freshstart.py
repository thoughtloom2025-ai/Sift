from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.task import TaskResponse


class FreshStartCheck(BaseModel):
    should_trigger: bool
    hours_since_last_login: float
    threshold_hours: int


class FreshStartReset(BaseModel):
    tasks_archived: int
    next_action_task: Optional[TaskResponse] = None
    message: str


class FreshStartLogResponse(BaseModel):
    id: int
    user_id: int
    triggered_at: datetime
    tasks_archived_count: int
    next_action_task_id: Optional[int] = None

    model_config = {"from_attributes": True}
