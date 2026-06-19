from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database.connection import create_tables
from app.routes.user_routes import router as user_router

# Crear tablas al iniciar
create_tables()

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestión de usuarios del sistema **device_systems**.\n\n"
        "### Características\n"
        "- CRUD completo con persistencia en **SQLite** via **SQLAlchemy**\n"
        "- Validación de datos con **Pydantic v2**\n"
        "- Manejo de errores con **HTTPException**\n"
        "- **Dependency Injection** con `Depends()`\n"
        "- Sesión de base de datos por request\n"
        "- Filtros por rol, estado y ordenamiento\n"
        "- Cabeceras HTTP personalizadas"
    ),
    version="3.0.0",
    contact={"name": "Equipo device_systems", "email": "soporte@devicesystems.com"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(user_router)


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