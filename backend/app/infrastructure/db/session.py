import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.base import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smart_pillbox.db" if os.getenv("APP_ENV") == "test" else "postgresql+psycopg://postgres:postgres@db:5432/pillbox",
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

__all__ = ["Base", "engine", "SessionLocal", "DATABASE_URL"]
