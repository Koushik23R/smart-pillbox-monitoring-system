from __future__ import annotations

from pydantic import BaseModel, Field


class DeviceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    device_type: str = Field("simulator", pattern=r"^(esp32|simulator|future)$")
    serial_number: str | None = Field(None, max_length=255)
    firmware_version: str | None = Field(None, max_length=50)
    connectivity_mode: str = Field("simulated", pattern=r"^(wifi|bluetooth|usb|simulated)$")
    room_name: str | None = Field(None, max_length=255)
    patient_id: str | None = None
    is_active: bool = True


class DeviceUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    device_type: str | None = Field(None, pattern=r"^(esp32|simulator|future)$")
    serial_number: str | None = Field(None, max_length=255)
    firmware_version: str | None = Field(None, max_length=50)
    connectivity_mode: str | None = Field(None, pattern=r"^(wifi|bluetooth|usb|simulated)$")
    room_name: str | None = Field(None, max_length=255)
    patient_id: str | None = None
    is_active: bool | None = None


class DeviceHeartbeatRequest(BaseModel):
    battery_level: float | None = Field(None, ge=0, le=100)
    firmware_version: str | None = Field(None, max_length=50)


class DeviceResponse(BaseModel):
    id: str
    patient_id: str | None
    name: str
    device_type: str
    serial_number: str | None
    firmware_version: str | None
    status: str
    connectivity_mode: str
    room_name: str | None
    battery_level: float | None
    last_seen_at: str | None
    is_active: bool
    created_at: str
    updated_at: str


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse]
    total: int
    page: int
    page_size: int
