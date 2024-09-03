from odmantic import Model, Field
from typing import Optional
from datetime import datetime

class WorkLog(Model):
    id: int = Field(primary_field=True)
    user_id: int
    check_in: Optional[datetime] = Field(default_factory=datetime.utcnow)
    check_out: Optional[datetime] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)