from odmantic import Model, Field
from typing import Optional
from datetime import datetime

class Activity_Participation(Model):
    id: int = Field(primary_field=True)
    activity_id: int
    user_id: int = Field(index=True)
    activity_points: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)