from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    assigned_employee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    area: Mapped[str | None] = mapped_column(String(255), nullable=True)
    governorate: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    routing_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    routing_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    employee_assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    work_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    work_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="complaints", foreign_keys=[user_id])
    category: Mapped["Category"] = relationship(back_populates="complaints")
    department: Mapped["Department"] = relationship(back_populates="complaints")
    comments: Mapped[list["Comment"]] = relationship(back_populates="complaint")
    updates: Mapped[list["ComplaintUpdate"]] = relationship(back_populates="complaint")
    assigned_employee: Mapped["User | None"] = relationship(back_populates="assigned_tasks", foreign_keys=[assigned_employee_id])
