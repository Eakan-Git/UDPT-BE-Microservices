from odmantic import Model, Field
from typing import Optional
from datetime import datetime
from enums import TimeSheet, TimeSheetStatus

class Time_Sheet(Model):
    id: int = Field(primary_field=True)
    user_id: int = Field(index=True)
    previous_value: dict = Field(default=TimeSheet.get_default())
    current_value: dict = Field(default=TimeSheet.get_default())
    status: str = Field(default=TimeSheetStatus.APPROVED.value)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)