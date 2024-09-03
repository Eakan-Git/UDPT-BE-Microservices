from odmantic import Model, Field
from typing import Optional
from datetime import datetime

class Points_Transfer(Model):
    id: int = Field(primary_field=True)
    from_user_id: int = Field(index=True)
    to_user_id: int = Field(index=True)
    points: int = Field(gt=99, description="Points to transfer, must be >= 100")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)