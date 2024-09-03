from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ActivityBase(BaseModel):
    title: str = Field(..., description="Title of the activity")

class ActivityCreate(ActivityBase):
    type: str = Field(..., description="Type of the activity")
    from_date: datetime = Field(..., description="Start date of the activity")
    to_date: datetime = Field(..., description="End date of the activity")
    description: Optional[str] = Field(None, description="Description of the activity")

class ActivityRead(ActivityBase):
    id: int = Field(..., description="Activity ID")
    type: str = Field(..., description="Type of the activity")
    from_date: datetime = Field(..., description="Start date of the activity")
    to_date: datetime = Field(..., description="End date of the activity")
    description: Optional[str] = Field(None, description="Description of the activity")
    created_at: datetime = Field(..., description="Activity created date")
    updated_at: datetime = Field(..., description="Activity modified date")

class ActivityUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Type of the activity")
    from_date: Optional[datetime] = Field(None, description="Start date of the activity")
    to_date: Optional[datetime] = Field(None, description="End date of the activity")
    title: Optional[str] = Field(None, description="Title of the activity")
    description: Optional[str] = Field(None, description="Description of the activity")