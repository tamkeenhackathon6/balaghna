from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="citizen", nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    national_id_hash: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    national_id_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    complaints: Mapped[list["Complaint"]] = relationship(back_populates="user", foreign_keys="Complaint.user_id")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    complaint_updates: Mapped[list["ComplaintUpdate"]] = relationship(back_populates="user")
    department: Mapped["Department | None"] = relationship(foreign_keys=[department_id])
    assigned_tasks: Mapped[list["Complaint"]] = relationship(back_populates="assigned_employee", foreign_keys="Complaint.assigned_employee_id")
