from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.v1.auth.schemas import TokenRefreshRequest, TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.api.v1.auth.service import AuthService
from app.core.exceptions import AppException
from app.infrastructure.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        return service.register(payload.email, payload.password, payload.full_name, payload.role)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/login", response_model=dict)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        return service.login(payload.email, payload.password)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/refresh", response_model=dict)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        return service.refresh(payload.refresh_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }
