import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class VerificationMethod(str, Enum):
    MANUAL = "manual"
    WEIGHT = "weight"
    CAMERA = "camera"
    HYBRID = "hybrid"


class VerificationResult(str, Enum):
    TAKEN = "taken"
    NOT_TAKEN = "not_taken"
    UNKNOWN = "unknown"


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medication_events.id"), nullable=False
    )
    verification_method: Mapped[VerificationMethod] = mapped_column(
        SAEnum(VerificationMethod, native_enum=False), nullable=False
    )
    result: Mapped[VerificationResult] = mapped_column(
        SAEnum(VerificationResult, native_enum=False), nullable=False
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    camera_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    event: Mapped["MedicationEvent"] = relationship(
        "MedicationEvent", back_populates="verification_records"
    )

    def __repr__(self) -> str:
        return (
            f"VerificationRecord(id={self.id}, event_id={self.event_id}, "
            f"result={self.result.value})"
        )
