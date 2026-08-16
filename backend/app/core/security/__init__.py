from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    salt = hashlib.sha256(settings.secret_key.encode("utf-8")).hexdigest()[:16]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("pbkdf2_sha256$"):
        return False
    _, salt, digest_hex = hashed_password.split("$", 2)
    expected = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hmac.compare_digest(expected, digest_hex)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "token_type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "token_type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
