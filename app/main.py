from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes.user_routes import router as user_router

# ──────────────────────────────────────────────
# Instancia principal de la aplicación
# ──────────────────────────────────────────────
app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestión de usuarios del sistema **device_systems**. "
        "Permite listar, consultar, filtrar y registrar usuarios con validaciones "
        "robustas usando **FastAPI** y **Pydantic v2**."
    ),
    version="1.0.0",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@devicesystems.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# Registro de routers
# ──────────────────────────────────────────────
app.include_router(user_router)


# ──────────────────────────────────────────────
# Endpoint raíz
# ──────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Bienvenida")
def root():
    return {
        "app": "device_systems",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
    }


# ──────────────────────────────────────────────
# Manejador global de errores 404
# ──────────────────────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Recurso no encontrado",
            "path": str(request.url),
        },
    )