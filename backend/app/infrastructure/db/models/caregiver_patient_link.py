import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class CaregiverPatientLink(Base):
    __tablename__ = "caregiver_patient_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    caregiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    caregiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[caregiver_id],
        back_populates="caregiver_links",
    )
    patient: Mapped["User"] = relationship(
        "User",
        foreign_keys=[patient_id],
        back_populates="patient_links",
    )

    def __repr__(self) -> str:
        return f"CaregiverPatientLink(caregiver_id={self.caregiver_id}, patient_id={self.patient_id})"
