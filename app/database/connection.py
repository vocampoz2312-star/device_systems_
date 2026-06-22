from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ──────────────────────────────────────────────
# Configuración de la base de datos SQLite
# ──────────────────────────────────────────────
DATABASE_URL = "sqlite:///./device_systems.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # requerido para SQLite con FastAPI
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def create_tables():
    """Crea todas las tablas definidas en los modelos."""
    from app.models import user_model, device_model, loan_model  # noqa: F401
    Base.metadata.create_all(bind=engine)