from app.api.v1.auth.router import router as auth_router
from app.api.v1.devices.router import router as devices_router
from app.api.v1.medications.router import router as medications_router

__all__ = ["auth_router", "devices_router", "medications_router"]
