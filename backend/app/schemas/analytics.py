from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class DailyTrend(BaseModel):
    date: date
    avg_energy_level: Optional[float] = None
    tasks_completed: int
    big_rocks_completed: int
    easy_wins_completed: int
    fresh_starts_triggered: int

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_tasks_completed: int
    avg_energy_level: float
    big_rocks_completed: int
    easy_wins_completed: int
    fresh_starts_triggered: int
    days_tracked: int


class CompletionRate(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    big_rock_completion_rate: float


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_tasks: int
    total_integrations: int
    syncs_last_24h: int
