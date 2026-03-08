from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class IntegrationResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    is_active: bool
    last_synced_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncLogResponse(BaseModel):
    id: int
    integration_id: int
    synced_at: datetime
    items_imported: int
    items_updated: int
    status: str
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class SyncResult(BaseModel):
    integration_id: int
    provider: str
    items_imported: int
    items_updated: int
    status: str
    error_message: Optional[str] = None
