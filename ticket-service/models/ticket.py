from odmantic import Model, Field
from typing import Optional
from datetime import datetime
from enums import TicketStatus

class Ticket(Model):
    id: int = Field(primary_field=True)
    user_id: int
    from_date: datetime
    to_date: datetime
    description: str
    type: Optional[str]
    status: str = TicketStatus.PENDING.value
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)