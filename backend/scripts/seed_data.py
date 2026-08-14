"""Seed sample data for the smart pillbox database.

This is intentionally a data-only bootstrap script for development and testing.
It does not implement application logic.
"""

from __future__ import annotations

import uuid
from datetime import datetime, time, timedelta

from sqlalchemy import select

from app.infrastructure.db.base import Base
from app.infrastructure.db.models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertType,
    CaregiverPatientLink,
    Device,
    DeviceStatus,
    DeviceType,
    MedicationEvent,
    MedicationEventStatus,
    MedicationEventType,
    MedicationSchedule,
    ScheduleFrequency,
    SensorReading,
    User,
    UserRole,
    VerificationMethod,
    VerificationRecord,
    VerificationResult,
)
from app.infrastructure.db.session import SessionLocal


def seed() -> None:
    session = SessionLocal()
    try:
        if session.execute(select(User.id).limit(1)).first():
            return

        patient_user = User(
            id=uuid.uuid4(),
            email="patient@example.com",
            password_hash="hashed_password_placeholder",
            full_name="Alice Patient",
            role=UserRole.PATIENT,
            is_active=True,
        )
        caregiver_user = User(
            id=uuid.uuid4(),
            email="caregiver@example.com",
            password_hash="hashed_password_placeholder",
            full_name="Bob Caregiver",
            role=UserRole.CAREGIVER,
            is_active=True,
        )

        session.add_all([patient_user, caregiver_user])
        session.flush()

        device = Device(
            id=uuid.uuid4(),
            patient_id=patient_user.id,
            name="Smart Pill Box",
            device_type=DeviceType.SIMULATOR,
            serial_number="SIM-001",
            firmware_version="1.0.0",
            status=DeviceStatus.ONLINE,
            room_name="Bedroom",
            battery_level=98.5,
            last_seen_at=datetime.utcnow(),
        )
        session.add(device)
        session.flush()

        schedule = MedicationSchedule(
            id=uuid.uuid4(),
            patient_id=patient_user.id,
            device_id=device.id,
            medication_name="Vitamin D",
            dosage=1.0,
            dosage_unit="tablet",
            scheduled_time=time(8, 0),
            frequency=ScheduleFrequency.DAILY,
            start_date=datetime.utcnow() - timedelta(days=7),
            timezone="UTC",
            is_active=True,
        )
        session.add(schedule)
        session.flush()

        link = CaregiverPatientLink(
            id=uuid.uuid4(),
            caregiver_id=caregiver_user.id,
            patient_id=patient_user.id,
        )
        session.add(link)

        medication_event = MedicationEvent(
            id=uuid.uuid4(),
            patient_id=patient_user.id,
            device_id=device.id,
            schedule_id=schedule.id,
            event_type=MedicationEventType.REMINDER,
            status=MedicationEventStatus.RESOLVED,
            observed_weight_before=120.0,
            observed_weight_after=118.5,
            threshold_value=1.5,
            measured_delta=1.5,
            source="simulator",
            verified_by_caregiver=False,
        )
        session.add(medication_event)
        session.flush()

        alert = Alert(
            id=uuid.uuid4(),
            patient_id=patient_user.id,
            device_id=device.id,
            alert_type=AlertType.REMINDER,
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.RESOLVED,
            message="Medication reminder triggered for Vitamin D.",
        )
        session.add(alert)

        sensor_reading = SensorReading(
            id=uuid.uuid4(),
            device_id=device.id,
            weight_value=118.5,
            raw_reading=118.5,
            calibration_offset=0.0,
            signal_quality="good",
        )
        session.add(sensor_reading)

        verification = VerificationRecord(
            id=uuid.uuid4(),
            event_id=medication_event.id,
            verification_method=VerificationMethod.WEIGHT,
            result=VerificationResult.TAKEN,
            confidence_score=0.94,
            notes="Medication taken based on weight delta.",
        )
        session.add(verification)

        session.commit()
        print("Seed data inserted successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
