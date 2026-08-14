import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class UserRole(str, Enum):
    PATIENT = "patient"
    CAREGIVER = "caregiver"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False), default=UserRole.PATIENT, nullable=False
    )
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

    patient_links: Mapped[list["CaregiverPatientLink"]] = relationship(
        "CaregiverPatientLink",
        foreign_keys="CaregiverPatientLink.patient_id",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    caregiver_links: Mapped[list["CaregiverPatientLink"]] = relationship(
        "CaregiverPatientLink",
        foreign_keys="CaregiverPatientLink.caregiver_id",
        back_populates="caregiver",
        cascade="all, delete-orphan",
    )
    schedules: Mapped[list["MedicationSchedule"]] = relationship(
        "MedicationSchedule", back_populates="patient"
    )
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="patient")
    events: Mapped[list["MedicationEvent"]] = relationship(
        "MedicationEvent", back_populates="patient"
    )
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="patient")
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="actor"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, role={self.role.value})"
