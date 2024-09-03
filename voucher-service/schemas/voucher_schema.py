from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VoucherBase(BaseModel):
    pass

class VoucherRead(VoucherBase):
    id: int = Field(..., description="ID of the voucher")
    provider: Optional[str] = Field(None, description="Provider of the voucher")
    url : Optional[str] = Field(None, description="URL of the voucher")
    require_point: int = Field(..., gt=0, description="Point required to redeem the voucher")
    title: str = Field(..., min_length=1, description="Title of the voucher")
    description: Optional[str] = Field(None, description="Description of the voucher")
    created_at: datetime = Field(..., description="Created date of the voucher")
    updated_at: datetime = Field(..., description="Updated date of the voucher")

class VoucherCreate(VoucherBase):
    require_point: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, description="Title of the voucher")
    description: Optional[str] = Field(None, description="Description of the voucher")
    provider: Optional[str] = Field(None, description="Provider of the voucher")
    url: Optional[str] = Field(None, description="URL of the voucher")

class VoucherUpdate(VoucherBase):
    require_point: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, min_length=1, description="Title of the voucher")
    description: Optional[str] = Field(None, description="Description of the voucher")
    provider: Optional[str] = Field(None, description="Provider of the voucher")
    url: Optional[str] = Field(None, description="URL of the voucher")