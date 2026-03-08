from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    impact: Optional[int] = None
    urgency: Optional[int] = None
    energy_required: Optional[int] = None

    @field_validator("impact", "urgency", "energy_required", mode="before")
    @classmethod
    def validate_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Value must be between 1 and 5")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[int] = None
    urgency: Optional[int] = None
    energy_required: Optional[int] = None

    @field_validator("impact", "urgency", "energy_required", mode="before")
    @classmethod
    def validate_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Value must be between 1 and 5")
        return v


class SnoozeRequest(BaseModel):
    snooze_until: datetime


class SubStepsUpdate(BaseModel):
    sub_steps: List[str]


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    source: str
    source_id: Optional[str] = None
    impact: int
    urgency: int
    energy_required: int
    priority_score: float
    status: str
    is_big_rock: bool
    sub_steps: Optional[List[str]] = None
    snooze_until: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
