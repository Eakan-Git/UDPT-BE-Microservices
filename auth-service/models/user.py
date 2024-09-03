from odmantic import Model, Field
from typing import Optional
from datetime import datetime
from enums import Role
from config import config
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Model):
    id: int = Field(primary_field=True)
    username: Optional[str] = Field(unique=True, index=True)
    is_channged_default_password: Optional[bool] = False
    hashed_password: Optional[str] = pwd_context.hash(config.get("DEFAULT_USER_PASSWORD"))
    avatar: Optional[str] = config.get("DEFAULT_AVATAR")
    email: Optional[str] = None
    role: Optional[str] = Role.EMPLOYEE.value
    is_locked: Optional[bool] = False
    full_name: Optional[str] = None
    address: Optional[str] = None
    citizen_id: Optional[str] = None
    tax_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_number: Optional[str] = None
    bonus_point: Optional[int] = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)