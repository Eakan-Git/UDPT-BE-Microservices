from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WorkLogBase(BaseModel):
    user_id: int = Field(..., description="User ID")

class WorkLogCreate(WorkLogBase):
    pass

class WorkLogRead(WorkLogBase):
    id: int = Field(..., description="Work log ID")
    check_in: datetime = Field(..., description="Check in time")
    check_out: Optional[datetime] = Field(None, description="Check out time")
    note: Optional[str] = Field(None, description="Note")
    created_at: datetime = Field(..., description="Work log created date")
    updated_at: datetime = Field(..., description="Work log modified date")

class WorkLogUpdateNote(BaseModel):
    note: str = Field(..., description="Note")