from __future__ import annotations

from datetime import datetime, time
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import MedicationSchedule, User


class MedicationService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _as_uuid(value: str | UUID | None) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

    def create(self, payload: dict[str, Any]) -> MedicationSchedule:
        patient_id = payload.get("patient_id")
        if patient_id:
            patient = self.db.execute(select(User).where(User.id == self._as_uuid(patient_id))).scalar_one_or_none()
            if patient is None:
                raise ValueError("patient_id does not exist")

        schedule = MedicationSchedule(
            patient_id=patient_id or self._get_default_patient_id(),
            medication_name=payload["medication_name"],
            dosage=float(payload["dosage"]),
            dosage_unit=payload["dosage_unit"],
            scheduled_time=time.fromisoformat(payload["scheduled_time"]),
            frequency=payload["frequency"],
            start_date=datetime.fromisoformat(payload["start_date"]),
            end_date=(datetime.fromisoformat(payload["end_date"]) if payload.get("end_date") else None),
            timezone=payload.get("timezone", "UTC"),
            is_active=bool(payload.get("is_active", True)),
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def list(self, *, page: int, page_size: int, medication_name: str | None = None, is_active: bool | None = None) -> dict[str, Any]:
        query = select(MedicationSchedule)

        if medication_name:
            query = query.where(MedicationSchedule.medication_name.ilike(f"%{medication_name}%"))
        if is_active is not None:
            query = query.where(MedicationSchedule.is_active.is_(is_active))

        total_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_query).scalar_one()

        ordered = query.order_by(MedicationSchedule.scheduled_time.asc(), MedicationSchedule.created_at.desc())
        paginated = ordered.offset((page - 1) * page_size).limit(page_size)
        items = self.db.execute(paginated).scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get(self, schedule_id: str) -> MedicationSchedule:
        schedule = self.db.execute(select(MedicationSchedule).where(MedicationSchedule.id == self._as_uuid(schedule_id))).scalar_one_or_none()
        if schedule is None:
            raise LookupError("Medication schedule not found")
        return schedule

    def update(self, schedule_id: str, payload: dict[str, Any]) -> MedicationSchedule:
        schedule = self.get(schedule_id)

        for field, value in payload.items():
            if field == "patient_id" and value is not None:
                patient_uuid = self._as_uuid(value)
                patient = self.db.execute(select(User).where(User.id == patient_uuid)).scalar_one_or_none()
                if patient is None:
                    raise ValueError("patient_id does not exist")
                schedule.patient_id = patient_uuid
                continue
            if field == "scheduled_time":
                schedule.scheduled_time = time.fromisoformat(value)
                continue
            if field == "start_date":
                schedule.start_date = datetime.fromisoformat(value)
                continue
            if field == "end_date":
                schedule.end_date = datetime.fromisoformat(value) if value else None
                continue
            if field == "dosage":
                schedule.dosage = float(value)
                continue
            if field == "is_active":
                schedule.is_active = bool(value)
                continue
            if field == "frequency":
                schedule.frequency = value
                continue
            if field == "patient_id" and value is None:
                schedule.patient_id = self._get_default_patient_id()
                continue
            setattr(schedule, field, value)

        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete(self, schedule_id: str) -> None:
        schedule = self.get(schedule_id)
        self.db.delete(schedule)
        self.db.commit()

    def _get_default_patient_id(self) -> str:
        patient = self.db.execute(select(User).where(User.role == "patient")).scalars().first()
        if patient is None:
            raise ValueError("No patient user found")
        return patient.id
