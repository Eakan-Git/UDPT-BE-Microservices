from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VoucherExchangeBase(BaseModel):
    voucher_title: str = Field(..., description="Voucher title")
    voucher_description: str = Field(..., description="Voucher description")

class VoucherExchangeCreate(BaseModel):
    voucher_id: int = Field(..., description="Voucher ID")

class VoucherExchangeRead(VoucherExchangeBase):
    id: int = Field(..., description="Voucher ID")
    user_id: int = Field(..., description="User ID")
    code: Optional[str] = Field(None, description="Voucher code")
    point_used: int = Field(..., description="Point used")
    created_at: datetime = Field(..., description="Voucher created at")
    updated_at: datetime = Field(..., description="Voucher updated at")
    is_used: bool = Field(..., description="Is this voucher used?")