from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    from_date: datetime = Field(..., description="Ticket for date")
    to_date: datetime = Field(..., description="Ticket to date")
    
class TicketCreate(BaseModel):
    type: Optional[str] = Field(None, description="Ticket type")
    description: Optional[str] = Field(None, description="Ticket description")
    from_date: datetime = Field(..., description="Ticket for date")
    to_date: datetime = Field(..., description="Ticket to date")

class TicketRead(TicketBase):
    id: int = Field(..., description="Ticket ID")
    type: str = Field(..., description="Ticket type")
    status: str = Field(..., description="Ticket status")
    description: Optional[str] = Field(None, description="Ticket description")
    created_at: datetime = Field(..., description="Ticket created date")
    updated_at: datetime = Field(..., description="Ticket modified date")

class TicketUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Ticket type")
    status: Optional[str] = Field(None, description="Ticket status")
    description: Optional[str] = Field(None, description="Ticket description")
    from_date: Optional[datetime] = Field(None, description="Ticket for date")
    to_date: Optional[datetime] = Field(None, description="Ticket to date")