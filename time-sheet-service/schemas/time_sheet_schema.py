from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enums import TimeSheet

class TimeSheetBase(BaseModel):
    id: int = Field(..., description="Time sheet ID")
    user_id: int = Field(..., description="User ID")

class TimeSheetCreate(BaseModel):
    current_value: Optional[dict] = Field(TimeSheet.DEFAULT, description="Current time sheet value")

class TimeSheetRead(TimeSheetBase):
    previous_value: dict = Field(..., description="Previous time sheet value")
    current_value: dict = Field(..., description="Current time sheet value")
    status: str = Field(..., description="Time sheet status")
    created_at: datetime = Field(..., description="Time sheet created date")
    updated_at: datetime = Field(..., description="Time sheet modified date")

class TimeSheetUpdate(BaseModel):
    current_value: Optional[dict] = Field(TimeSheet.DEFAULT, description="Current time sheet value")

class TimeSheetManage(BaseModel):
    id: int = Field(..., description="Time sheet ID")
    status: str = Field(..., description="Time sheet status")