from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class EnergyLogCreate(BaseModel):
    level: int
    session_id: Optional[str] = None

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Energy level must be between 1 and 5")
        return v


class EnergyLogResponse(BaseModel):
    id: int
    user_id: int
    level: int
    logged_at: datetime
    session_id: Optional[str] = None

    model_config = {"from_attributes": True}


class EnergyHistoryResponse(BaseModel):
    logs: List[EnergyLogResponse]
    avg_level: float
    days_tracked: int
