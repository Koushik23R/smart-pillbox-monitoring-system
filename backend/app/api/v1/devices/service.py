from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Device, DeviceStatus, DeviceType, ConnectivityMode, User


class DeviceService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _as_uuid(value: str | UUID | None) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

    def create(self, payload: dict[str, Any]) -> Device:
        serial_number = payload.get("serial_number")
        if serial_number:
            existing = self.db.execute(
                select(Device).where(Device.serial_number == serial_number)
            ).scalar_one_or_none()
            if existing:
                raise ValueError("serial_number already registered")

        patient_id = payload.get("patient_id")
        if patient_id:
            patient = self.db.execute(
                select(User).where(User.id == self._as_uuid(patient_id))
            ).scalar_one_or_none()
            if patient is None:
                raise ValueError("patient_id does not exist")

        device = Device(
            name=payload["name"],
            device_type=DeviceType(payload.get("device_type", "simulator")),
            serial_number=serial_number,
            firmware_version=payload.get("firmware_version"),
            connectivity_mode=ConnectivityMode(payload.get("connectivity_mode", "simulated")),
            room_name=payload.get("room_name"),
            patient_id=self._as_uuid(patient_id) if patient_id else None,
            status=DeviceStatus.OFFLINE,
            is_active=bool(payload.get("is_active", True)),
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def list(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        device_type: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        query = select(Device)

        if status:
            query = query.where(Device.status == DeviceStatus(status))
        if device_type:
            query = query.where(Device.device_type == DeviceType(device_type))
        if is_active is not None:
            query = query.where(Device.is_active.is_(is_active))

        total_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_query).scalar_one()

        ordered = query.order_by(Device.created_at.desc())
        paginated = ordered.offset((page - 1) * page_size).limit(page_size)
        items = self.db.execute(paginated).scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get(self, device_id: str) -> Device:
        device = self.db.execute(
            select(Device).where(Device.id == self._as_uuid(device_id))
        ).scalar_one_or_none()
        if device is None:
            raise LookupError("Device not found")
        return device

    def update(self, device_id: str, payload: dict[str, Any]) -> Device:
        device = self.get(device_id)

        for field, value in payload.items():
            if value is None:
                continue
            if field == "patient_id":
                if value:
                    patient_uuid = self._as_uuid(value)
                    patient = self.db.execute(
                        select(User).where(User.id == patient_uuid)
                    ).scalar_one_or_none()
                    if patient is None:
                        raise ValueError("patient_id does not exist")
                    device.patient_id = patient_uuid
                else:
                    device.patient_id = None
                continue
            if field == "device_type":
                device.device_type = DeviceType(value)
                continue
            if field == "connectivity_mode":
                device.connectivity_mode = ConnectivityMode(value)
                continue
            if field == "is_active":
                device.is_active = bool(value)
                continue
            if field == "serial_number":
                if value:
                    existing = self.db.execute(
                        select(Device).where(
                            Device.serial_number == value,
                            Device.id != device.id,
                        )
                    ).scalar_one_or_none()
                    if existing:
                        raise ValueError("serial_number already registered")
                device.serial_number = value
                continue
            setattr(device, field, value)

        self.db.commit()
        self.db.refresh(device)
        return device

    def delete(self, device_id: str) -> None:
        device = self.get(device_id)
        self.db.delete(device)
        self.db.commit()

    def heartbeat(self, device_id: str, payload: dict[str, Any]) -> Device:
        device = self.get(device_id)
        device.status = DeviceStatus.ONLINE
        device.last_seen_at = datetime.now(timezone.utc)

        if payload.get("battery_level") is not None:
            device.battery_level = float(payload["battery_level"])
        if payload.get("firmware_version"):
            device.firmware_version = payload["firmware_version"]

        self.db.commit()
        self.db.refresh(device)
        return device

    def get_status(self, device_id: str) -> dict[str, Any]:
        device = self.get(device_id)
        return {
            "device_id": str(device.id),
            "status": device.status.value,
            "battery_level": device.battery_level,
            "firmware_version": device.firmware_version,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            "is_online": device.status == DeviceStatus.ONLINE,
        }
