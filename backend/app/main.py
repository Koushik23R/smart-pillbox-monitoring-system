from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth.router import router as auth_router
from app.api.v1.devices.router import router as devices_router
from app.api.v1.medications.router import router as medications_router
from app.core.config import get_settings
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Smart Pill Box Monitoring System - Device Management API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


Base.metadata.create_all(bind=engine)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(medications_router, prefix="/api/v1")
app.include_router(devices_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
