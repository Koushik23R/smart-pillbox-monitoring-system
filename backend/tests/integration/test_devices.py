from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _get_auth_token(email: str = "device-user@example.com", password: str = "StrongPass123!"):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Device User",
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


def test_device_crud_with_filters_and_pagination():
    token = _get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/devices",
        json={
            "name": "Living Room Pill Box",
            "device_type": "esp32",
            "serial_number": "ESP-001",
            "firmware_version": "1.2.0",
            "connectivity_mode": "wifi",
            "room_name": "Living Room",
            "is_active": True,
        },
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["name"] == "Living Room Pill Box"
    assert created["device_type"] == "esp32"
    assert created["status"] == "offline"
    assert created["serial_number"] == "ESP-001"
    device_id = created["id"]

    list_response = client.get(
        "/api/v1/devices?page=1&page_size=10&device_type=esp32&is_active=true",
        headers=headers,
    )
    assert list_response.status_code == 200, list_response.text
    body = list_response.json()
    assert body["items"]
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["total"] >= 1

    detail_response = client.get(f"/api/v1/devices/{device_id}", headers=headers)
    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == device_id

    update_response = client.put(
        f"/api/v1/devices/{device_id}",
        json={
            "name": "Bedroom Pill Box",
            "room_name": "Bedroom",
            "firmware_version": "1.3.0",
        },
        headers=headers,
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["name"] == "Bedroom Pill Box"
    assert updated["room_name"] == "Bedroom"
    assert updated["firmware_version"] == "1.3.0"

    delete_response = client.delete(f"/api/v1/devices/{device_id}", headers=headers)
    assert delete_response.status_code == 204

    post_delete = client.get(f"/api/v1/devices/{device_id}", headers=headers)
    assert post_delete.status_code == 404


def test_device_heartbeat_updates_status_and_battery():
    token = _get_auth_token(email="heartbeat-user@example.com", password="StrongPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/devices",
        json={
            "name": "Heartbeat Device",
            "device_type": "simulator",
            "serial_number": "SIM-HB-001",
        },
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    device_id = create_response.json()["id"]
    assert create_response.json()["status"] == "offline"

    heartbeat_response = client.post(
        f"/api/v1/devices/{device_id}/heartbeat",
        json={"battery_level": 85.5, "firmware_version": "2.0.0"},
        headers=headers,
    )
    assert heartbeat_response.status_code == 200, heartbeat_response.text
    hb = heartbeat_response.json()
    assert hb["status"] == "online"
    assert hb["battery_level"] == 85.5
    assert hb["firmware_version"] == "2.0.0"
    assert hb["last_seen_at"] is not None

    status_response = client.get(f"/api/v1/devices/{device_id}/status", headers=headers)
    assert status_response.status_code == 200, status_response.text
    status_body = status_response.json()
    assert status_body["status"] == "online"
    assert status_body["battery_level"] == 85.5
    assert status_body["is_online"] is True
    assert status_body["last_seen_at"] is not None


def test_device_duplicate_serial_rejected():
    token = _get_auth_token(email="dup-serial@example.com", password="StrongPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(
        "/api/v1/devices",
        json={"name": "Device A", "serial_number": "DUP-001"},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/devices",
        json={"name": "Device B", "serial_number": "DUP-001"},
        headers=headers,
    )
    assert second.status_code == 400
    assert "already registered" in second.json()["detail"]


def test_device_validation_rejects_invalid_payload():
    token = _get_auth_token(email="device-validation@example.com", password="StrongPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    invalid_response = client.post(
        "/api/v1/devices",
        json={
            "name": "",
            "device_type": "invalid-type",
            "connectivity_mode": "invalid-mode",
        },
        headers=headers,
    )
    assert invalid_response.status_code in {422, 400}
