from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import User
from app.infrastructure.db.session import SessionLocal, engine

security = HTTPBearer()


def get_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        token_data = decode_token(credentials.credentials)
    except Exception as exc:  # pragma: no cover - runtime validation path
        raise AuthenticationError("Invalid or expired token") from exc

    if token_data.get("token_type") != "access":
        raise AuthenticationError("Token type is invalid")

    statement = select(User).where(User.email == token_data["sub"])
    user = db.execute(statement).scalar_one_or_none()
    if user is None:
        raise AuthenticationError("User not found")

    return user


def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise AuthorizationError("Insufficient permissions")
        return current_user

    return role_checker


__all__ = ["get_current_user", "get_db", "require_role", "security"]
