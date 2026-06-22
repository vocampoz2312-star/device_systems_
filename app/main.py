from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database.connection import create_tables
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router

# Crear tablas al iniciar (únicamente si no se usan migraciones)
# create_tables()

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestión de **usuarios**, **dispositivos** y **préstamos** "
        "del sistema **device_systems**.\n\n"
        "### Características\n"
        "- CRUD completo de usuarios, dispositivos y préstamos\n"
        "- Persistencia en **SQLite** via **SQLAlchemy**\n"
        "- Migraciones de base de datos con **Alembic**\n"
        "- Asociaciones entre modelos (One-to-Many / Many-to-One)\n"
        "- Consultas con **joins** y filtros avanzados\n"
        "- Validación de datos con **Pydantic v2**\n"
        "- Manejo de errores con **HTTPException**\n"
        "- **Dependency Injection** con `Depends()`\n"
        "- Cabeceras HTTP personalizadas\n"
        "- Documentación interactiva con **Swagger/OpenAPI**"
    ),
    version="4.0.0",
    contact={"name": "Equipo device_systems", "email": "soporte@devicesystems.com"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


@app.get("/", tags=["Root"], summary="Bienvenida")
def root():
    return {
        "app": "device_systems",
        "version": "3.0.0",
        "database": "SQLite — device_systems.db",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": True, "message": "Recurso no encontrado", "status_code": 404},
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Error interno del servidor", "status_code": 500},
    )