from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    user_id: int
    category_id: int | None = None
    department_id: int | None = None
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    address: str | None = None
    area: str | None = None
    governorate: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_path: str | None = None
    priority: str = "medium"
    status: str = "new"
    routing_reason: str | None = None
    routing_confidence: float | None = None


class ComplaintRead(BaseModel):
    id: int
    user_id: int
    category_id: int | None = None
    department_id: int | None = None
    title: str
    description: str
    address: str | None = None
    area: str | None = None
    governorate: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_path: str | None = None
    priority: str
    status: str
    routing_reason: str | None = None
    routing_confidence: float | None = None
    assigned_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
