from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.v1.medications.schemas import (
    MedicationCreateRequest,
    MedicationListResponse,
    MedicationResponse,
    MedicationUpdateRequest,
)
from app.api.v1.medications.service import MedicationService

router = APIRouter(prefix="/medications", tags=["medications"])


@router.post("", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        schedule = MedicationService(db).create(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "id": str(schedule.id),
        "patient_id": str(schedule.patient_id) if schedule.patient_id else None,
        "medication_name": schedule.medication_name,
        "dosage": schedule.dosage,
        "dosage_unit": schedule.dosage_unit,
        "scheduled_time": schedule.scheduled_time.isoformat(),
        "frequency": schedule.frequency,
        "start_date": schedule.start_date.isoformat(),
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active,
    }


@router.get("", response_model=MedicationListResponse)
def list_medications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    medication_name: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    result = MedicationService(db).list(
        page=page,
        page_size=page_size,
        medication_name=medication_name,
        is_active=is_active,
    )
    return {
        "items": [
            {
                "id": str(item.id),
                "patient_id": str(item.patient_id) if item.patient_id else None,
                "medication_name": item.medication_name,
                "dosage": item.dosage,
                "dosage_unit": item.dosage_unit,
                "scheduled_time": item.scheduled_time.isoformat(),
                "frequency": item.frequency,
                "start_date": item.start_date.isoformat(),
                "end_date": item.end_date.isoformat() if item.end_date else None,
                "timezone": item.timezone,
                "is_active": item.is_active,
            }
            for item in result["items"]
        ],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.get("/{schedule_id}", response_model=MedicationResponse)
def get_medication(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        schedule = MedicationService(db).get(schedule_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {
        "id": str(schedule.id),
        "patient_id": str(schedule.patient_id) if schedule.patient_id else None,
        "medication_name": schedule.medication_name,
        "dosage": schedule.dosage,
        "dosage_unit": schedule.dosage_unit,
        "scheduled_time": schedule.scheduled_time.isoformat(),
        "frequency": schedule.frequency,
        "start_date": schedule.start_date.isoformat(),
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active,
    }


@router.put("/{schedule_id}", response_model=MedicationResponse)
def update_medication(
    schedule_id: str,
    payload: MedicationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        schedule = MedicationService(db).update(schedule_id, payload.model_dump(exclude_unset=True))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "id": str(schedule.id),
        "patient_id": str(schedule.patient_id) if schedule.patient_id else None,
        "medication_name": schedule.medication_name,
        "dosage": schedule.dosage,
        "dosage_unit": schedule.dosage_unit,
        "scheduled_time": schedule.scheduled_time.isoformat(),
        "frequency": schedule.frequency,
        "start_date": schedule.start_date.isoformat(),
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active,
    }


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        MedicationService(db).delete(schedule_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return None
