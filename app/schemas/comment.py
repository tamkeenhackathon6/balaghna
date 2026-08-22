from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    complaint_id: int
    user_id: int
    body: str


class CommentRead(BaseModel):
    id: int
    complaint_id: int
    user_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
