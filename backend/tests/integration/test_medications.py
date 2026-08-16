from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _get_auth_token(email: str = "medication-user@example.com", password: str = "StrongPass123!"):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Medication User",
            "role": "patient",
        },
    )
    if register.status_code == 201:
        return register.json()["access_token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login.json()["access_token"]


def test_medication_crud_with_filter_and_pagination():
    token = _get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "patient_id": None,
        "medication_name": "Paracetamol",
        "dosage": 1.5,
        "dosage_unit": "tablet",
        "scheduled_time": "08:00:00",
        "frequency": "daily",
        "start_date": "2026-08-16T08:00:00",
        "end_date": "2026-08-30T08:00:00",
        "timezone": "UTC",
        "is_active": True,
    }

    create_response = client.post(
        "/api/v1/medications",
        json=payload,
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["medication_name"] == "Paracetamol"
    assert created["dosage"] == 1.5
    medication_id = created["id"]

    list_response = client.get(
        "/api/v1/medications?page=1&page_size=10&medication_name=Paracetamol&is_active=true",
        headers=headers,
    )
    assert list_response.status_code == 200, list_response.text
    body = list_response.json()
    assert body["items"]
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["total"] >= 1

    detail_response = client.get(f"/api/v1/medications/{medication_id}", headers=headers)
    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == medication_id

    update_response = client.put(
        f"/api/v1/medications/{medication_id}",
        json={
            **payload,
            "medication_name": "Paracetamol Plus",
            "dosage": 2.0,
        },
        headers=headers,
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["medication_name"] == "Paracetamol Plus"
    assert update_response.json()["dosage"] == 2.0

    delete_response = client.delete(f"/api/v1/medications/{medication_id}", headers=headers)
    assert delete_response.status_code == 204

    post_delete = client.get(f"/api/v1/medications/{medication_id}", headers=headers)
    assert post_delete.status_code == 404


def test_medication_validation_rejects_invalid_payload():
    token = _get_auth_token(email="validation-user@example.com", password="StrongPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    invalid_response = client.post(
        "/api/v1/medications",
        json={
            "patient_id": None,
            "medication_name": "",
            "dosage": 0,
            "dosage_unit": "",
            "scheduled_time": "bad-time",
            "frequency": "invalid-frequency",
            "start_date": "not-a-date",
            "timezone": "UTC",
        },
        headers=headers,
    )

    assert invalid_response.status_code in {422, 400}
