from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Points_TransferBase(BaseModel):
    points: int = Field(..., description="Points to transfer, must be greater than 100")

class Points_TransferCreate(Points_TransferBase):
    to_user_id: int = Field(..., description="User ID to transfer points to")
    description: Optional[str] = Field(None, description="Description of the points transfer")

class Points_TransferRead(Points_TransferBase):
    id: int = Field(..., description="Points transfer ID")
    from_user_id: int = Field(..., description="User ID to transfer points from")
    to_user_id: int = Field(..., description="User ID to transfer points to")
    description: Optional[str] = Field(None, description="Description of the points transfer")
    created_at: datetime = Field(..., description="Points transfer created date")
    updated_at: datetime = Field(..., description="Points transfer modified date")