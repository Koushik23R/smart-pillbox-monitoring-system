import uuid
from datetime import datetime, time
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True
    )
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[float] = mapped_column(nullable=False)
    dosage_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    scheduled_time: Mapped[time] = mapped_column(Time, nullable=False)
    frequency: Mapped[ScheduleFrequency] = mapped_column(
        SAEnum(ScheduleFrequency, native_enum=False), default=ScheduleFrequency.DAILY, nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    patient: Mapped["User"] = relationship("User", back_populates="schedules")
    device: Mapped["Device | None"] = relationship("Device", back_populates="schedules")
    events: Mapped[list["MedicationEvent"]] = relationship(
        "MedicationEvent", back_populates="schedule"
    )

    def __repr__(self) -> str:
        return (
            f"MedicationSchedule(id={self.id}, medication_name={self.medication_name}, "
            f"scheduled_time={self.scheduled_time})"
        )
