from odmantic import Model, Field
from typing import Optional
from datetime import datetime

class Voucher(Model):
    id: int = Field(primary_field=True)
    provider: Optional[str] = None
    url : Optional[str] = None
    require_point: int
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)