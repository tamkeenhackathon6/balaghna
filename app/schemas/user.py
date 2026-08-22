from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "citizen"


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
