from app.api.v1.auth.router import router as auth_router
from app.api.v1.medications.router import router as medications_router

__all__ = ["auth_router", "medications_router"]
