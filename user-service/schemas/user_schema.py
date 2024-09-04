from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name of the user")

class UserCreate(UserBase):
    username: str = Field(..., description="Username of the user")

class UserRead(UserBase):
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username of the user")
    is_locked: bool = Field(..., description="Whether the user is locked")
    is_channged_default_password: bool = Field(..., description="Whether the user has changed the default password")
    role: str = Field(..., description="User role")
    avatar: Optional[str] = Field(None, description="Avatar of the user")
    email: Optional[str] = Field(None, description="Email of the user")
    address: Optional[str] = Field(None, description="User address")
    citizen_id: Optional[str] = Field(None, description="Citizen ID")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    bank_name: Optional[str] = Field(None, description="Bank name")
    bank_number: Optional[str] = Field(None, description="Bank account number")
    bonus_point: int = Field(..., description="Bonus points of the user")
    created_at: datetime = Field(..., description="User created date")
    updated_at: datetime = Field(..., description="User modified date")

class UserUpdate(BaseModel):
    avatar: Optional[str] = Field(None, description="Avatar of the user")
    email: Optional[str] = Field(None, description="Email of the user")
    role: Optional[str] = Field(None, description="User role")
    is_locked: Optional[bool] = Field(False, description="Whether the user is locked")
    address: Optional[str] = Field(None, description="User address")
    citizen_id: Optional[str] = Field(None, description="Citizen ID")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    bank_name: Optional[str] = Field(None, description="Bank name")
    bank_number: Optional[str] = Field(None, description="Bank account number")
    bonus_point: Optional[int] = Field(None, description="Bonus points of the user")

class UserChangePassword(BaseModel):
    old_password: str = Field(..., description="Old password of the user")
    new_password: str = Field(..., description="New password of the user")

class VerifyPassword(BaseModel):
    username: str = Field(..., description="Username of the user")
    password: str = Field(..., description="Password of the user")