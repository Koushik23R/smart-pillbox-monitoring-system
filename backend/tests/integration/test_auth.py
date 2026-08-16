from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login_flow():
    payload = {
        "email": "user.auth@example.com",
        "password": "StrongPass123!",
        "full_name": "Auth User",
        "role": "caregiver",
    }

    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201, register_response.text
    register_body = register_response.json()
    assert register_body["user"]["email"] == payload["email"]
    assert "access_token" in register_body
    assert "refresh_token" in register_body

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_body = login_response.json()
    assert login_body["user"]["email"] == payload["email"]
    assert "access_token" in login_body
    assert "refresh_token" in login_body

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["email"] == payload["email"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_body["refresh_token"]},
    )
    assert refresh_response.status_code == 200, refresh_response.text
    assert "access_token" in refresh_response.json()


def test_login_rejects_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
