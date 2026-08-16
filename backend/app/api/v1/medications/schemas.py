from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel, Field, field_validator


class MedicationCreateRequest(BaseModel):
    patient_id: str | None = None
    medication_name: str = Field(..., min_length=2, max_length=255)
    dosage: float = Field(..., gt=0)
    dosage_unit: str = Field(..., min_length=1, max_length=50)
    scheduled_time: str = Field(..., min_length=5)
    frequency: str = Field(..., pattern=r"^(daily|weekly|custom)$")
    start_date: str
    end_date: str | None = None
    timezone: str = "UTC"
    is_active: bool = True

    @field_validator("scheduled_time")
    @classmethod
    def validate_scheduled_time(cls, value: str) -> str:
        try:
            time.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover
            raise ValueError("scheduled_time must be in HH:MM:SS or HH:MM format") from exc
        return value

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover
            raise ValueError("start_date must be a valid ISO datetime string") from exc
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover
            raise ValueError("end_date must be a valid ISO datetime string") from exc
        return value


class MedicationUpdateRequest(MedicationCreateRequest):
    pass


class MedicationResponse(BaseModel):
    id: str
    patient_id: str | None
    medication_name: str
    dosage: float
    dosage_unit: str
    scheduled_time: str
    frequency: str
    start_date: str
    end_date: str | None
    timezone: str
    is_active: bool


class MedicationListResponse(BaseModel):
    items: list[MedicationResponse]
    total: int
    page: int
    page_size: int
