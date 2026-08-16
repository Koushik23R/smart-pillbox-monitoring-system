from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.v1.devices.schemas import (
    DeviceCreateRequest,
    DeviceHeartbeatRequest,
    DeviceListResponse,
    DeviceResponse,
    DeviceUpdateRequest,
)
from app.api.v1.devices.service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


def _serialize_device(device: Any) -> dict[str, Any]:
    return {
        "id": str(device.id),
        "patient_id": str(device.patient_id) if device.patient_id else None,
        "name": device.name,
        "device_type": device.device_type.value,
        "serial_number": device.serial_number,
        "firmware_version": device.firmware_version,
        "status": device.status.value,
        "connectivity_mode": device.connectivity_mode.value,
        "room_name": device.room_name,
        "battery_level": device.battery_level,
        "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
        "is_active": device.is_active,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Register a new device")
def create_device(
    payload: DeviceCreateRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Register a new smart pill box device. Requires authentication."""
    try:
        device = DeviceService(db).create(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _serialize_device(device)


@router.get("", response_model=DeviceListResponse, summary="List devices with optional filters")
def list_devices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, pattern=r"^(online|offline|error|maintenance)$", description="Filter by status"),
    device_type: str | None = Query(None, pattern=r"^(esp32|simulator|future)$", description="Filter by device type"),
    is_active: bool | None = Query(None, description="Filter by active state"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List all devices with pagination and optional filtering by status, type, or active state."""
    result = DeviceService(db).list(
        page=page,
        page_size=page_size,
        status=status,
        device_type=device_type,
        is_active=is_active,
    )
    return {
        "items": [_serialize_device(item) for item in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.get("/{device_id}", response_model=DeviceResponse, summary="Get device details")
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full details of a specific device by ID."""
    try:
        device = DeviceService(db).get(device_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _serialize_device(device)


@router.put("/{device_id}", response_model=DeviceResponse, summary="Update device attributes")
def update_device(
    device_id: str,
    payload: DeviceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Update editable attributes of a device (name, firmware, room, etc.)."""
    try:
        device = DeviceService(db).update(device_id, payload.model_dump(exclude_unset=True))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _serialize_device(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a device")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Permanently remove a device from the system."""
    try:
        DeviceService(db).delete(device_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return None


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse, summary="Record device heartbeat")
def device_heartbeat(
    device_id: str,
    payload: DeviceHeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Report device heartbeat. Updates status to online, last_seen_at, battery level, and firmware version."""
    try:
        device = DeviceService(db).heartbeat(device_id, payload.model_dump(exclude_unset=True))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _serialize_device(device)


@router.get("/{device_id}/status", summary="Get device status")
def get_device_status(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve the current operational status of a device including battery, firmware, and connectivity."""
    try:
        return DeviceService(db).get_status(device_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
