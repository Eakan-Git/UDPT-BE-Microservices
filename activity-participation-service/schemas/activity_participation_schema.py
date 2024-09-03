from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Activity_ParticipationBase(BaseModel):
    activity_id: int = Field(..., description="Activity ID")
    user_id: int = Field(..., description="User ID")

class Activity_ParticipationCreate(BaseModel):
    activity_id: int = Field(..., description="Activity ID")

class Activity_ParticipationRead(Activity_ParticipationBase):
    id: int = Field(..., description="Activity Participation ID")
    activity_points: int = Field(..., description="Activity points")
    created_at: datetime = Field(..., description="Activity participation created date")
    updated_at: datetime = Field(..., description="Activity participation modified date")

class Activity_ParticipationUpdate(BaseModel):
    activity_points: Optional[int] = Field(None, description="Activity points")
    activity_id: Optional[int] = Field(None, description="Activity ID")
    user_id: Optional[int] = Field(None, description="User ID")

class Activity_Participation_Update_Points(BaseModel):
    id: int = Field(..., description="Activity Participation ID")
    activity_points: int = Field(..., description="Activity points")