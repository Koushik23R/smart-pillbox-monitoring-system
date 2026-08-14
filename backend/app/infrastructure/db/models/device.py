import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class DeviceType(str, Enum):
    ESP32 = "esp32"
    SIMULATOR = "simulator"
    FUTURE = "future"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ConnectivityMode(str, Enum):
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    USB = "usb"
    SIMULATED = "simulated"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(
        SAEnum(DeviceType, native_enum=False), default=DeviceType.SIMULATOR, nullable=False
    )
    serial_number: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(
        SAEnum(DeviceStatus, native_enum=False), default=DeviceStatus.OFFLINE, nullable=False
    )
    connectivity_mode: Mapped[ConnectivityMode] = mapped_column(
        SAEnum(ConnectivityMode, native_enum=False),
        default=ConnectivityMode.SIMULATED,
        nullable=False,
    )
    room_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    battery_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    patient: Mapped["User | None"] = relationship("User", back_populates="devices")
    schedules: Mapped[list["MedicationSchedule"]] = relationship(
        "MedicationSchedule", back_populates="device"
    )
    sensor_readings: Mapped[list["SensorReading"]] = relationship(
        "SensorReading", back_populates="device"
    )
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="device")
    events: Mapped[list["MedicationEvent"]] = relationship(
        "MedicationEvent", back_populates="device"
    )

    def __repr__(self) -> str:
        return f"Device(id={self.id}, name={self.name}, status={self.status.value})"
