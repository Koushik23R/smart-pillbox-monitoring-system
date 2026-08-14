import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class MedicationEventType(str, Enum):
    REMINDER = "reminder"
    TAKEN = "taken"
    MISSED = "missed"
    NOT_TAKEN = "not_taken"
    CONFIRMED = "confirmed"


class MedicationEventStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    MISSED = "missed"
    VERIFIED = "verified"


class MedicationEvent(Base):
    __tablename__ = "medication_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True
    )
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medication_schedules.id"), nullable=True
    )
    event_type: Mapped[MedicationEventType] = mapped_column(
        SAEnum(MedicationEventType, native_enum=False), nullable=False
    )
    status: Mapped[MedicationEventStatus] = mapped_column(
        SAEnum(MedicationEventStatus, native_enum=False),
        default=MedicationEventStatus.PENDING,
        nullable=False,
    )
    observed_weight_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    observed_weight_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    measured_delta: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="simulator", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    verified_by_caregiver: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    patient: Mapped["User"] = relationship("User", back_populates="events")
    device: Mapped["Device | None"] = relationship("Device", back_populates="events")
    schedule: Mapped["MedicationSchedule | None"] = relationship(
        "MedicationSchedule", back_populates="events"
    )
    verification_records: Mapped[list["VerificationRecord"]] = relationship(
        "VerificationRecord", back_populates="event"
    )

    def __repr__(self) -> str:
        return (
            f"MedicationEvent(id={self.id}, type={self.event_type.value}, "
            f"status={self.status.value}, timestamp={self.timestamp})"
        )
