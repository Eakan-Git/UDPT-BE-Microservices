from odmantic import Model, Field
from typing import Optional
from datetime import datetime
from enums import ActivityType

class Activity(Model):
    id: int = Field(primary_field=True)
    type: Optional[str]
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)