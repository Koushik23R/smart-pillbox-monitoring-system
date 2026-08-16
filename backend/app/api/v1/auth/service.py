from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, UserAlreadyExistsError, UserNotFoundError
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.infrastructure.db.models import User, UserRole


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, email: str, password: str, full_name: str, role: str) -> dict:
        existing = self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            raise UserAlreadyExistsError("User already exists")

        normalized_role = UserRole(role)
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=normalized_role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        access_token = create_access_token(subject=user.email, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.email, role=user.role.value)

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def login(self, email: str, password: str) -> dict:
        user = self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        access_token = create_access_token(subject=user.email, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.email, role=user.role.value)

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        from app.core.security import decode_token

        try:
            payload = decode_token(refresh_token)
        except Exception as exc:  # pragma: no cover
            raise AuthenticationError("Invalid refresh token") from exc

        if payload.get("token_type") != "refresh":
            raise AuthenticationError("Token type is invalid")

        user = self.db.execute(select(User).where(User.email == payload["sub"])).scalar_one_or_none()
        if not user:
            raise UserNotFoundError("User not found")

        access_token = create_access_token(subject=user.email, role=user.role.value)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
