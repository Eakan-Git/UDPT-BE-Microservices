from odmantic import Model, Field
from typing import Optional
from datetime import datetime

class Voucher_Exchange(Model):
    id: int = Field(primary_field=True)
    user_id: int = Field(index=True)

    code : Optional[str] = None
    voucher_title: Optional[str] = None
    voucher_description: Optional[str] = None
    point_used: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: Optional[bool] = False