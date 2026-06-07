from fastapi import Header, HTTPException, Path, status
from app.data import users_db


# ──────────────────────────────────────────────
# Dependencias reutilizables con Depends()
# ──────────────────────────────────────────────

def get_user_or_404(user_id: int = Path(..., ge=1, description="ID del usuario")):
    """
    Dependencia que busca un usuario por ID.
    Si no existe, lanza automáticamente un 404.
    Se reutiliza en GET, PUT, PATCH y DELETE.
    """
    user = users_db.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={user_id} no encontrado.",
        )
    return user


def check_email_not_duplicate(email: str, exclude_id: int | None = None):
    """
    Dependencia que valida si un correo ya existe en la base de datos.
    Lanza 409 Conflict si está duplicado.
    """
    if users_db.email_exists(email, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo '{email}' ya está registrado.",
        )


def get_api_info():
    """
    Dependencia que retorna metadatos de la API.
    Puede usarse para inyectar configuración global en cualquier endpoint.
    """
    return {
        "app": "device_systems",
        "version": "2.0.0",
        "author": "Equipo device_systems",
    }


def verify_api_key(x_api_key: str = Header(default=None, alias="X-API-Key")):
    """
    Dependencia que simula autenticación básica mediante cabecera HTTP.
    Uso: incluir cabecera 'X-API-Key: device2024' en la petición.
    """
    VALID_KEY = "device2024"
    if x_api_key != VALID_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada. Incluye la cabecera X-API-Key.",
        )
    return x_api_key