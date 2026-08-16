from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password


def test_password_hash_and_verify_round_trip():
    password = "StrongPass123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_tokens_include_expected_types():
    access = create_access_token("user@example.com", "patient")
    refresh = create_refresh_token("user@example.com", "patient")

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert access != refresh
