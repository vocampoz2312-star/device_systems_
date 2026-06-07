from fastapi import APIRouter, Query, Response, Depends, status
from typing import Optional

from app.schemas.user_schema import (
    UserCreate, UserUpdate, UserPatch,
    UserResponse, UserListResponse, MessageResponse,
)
from app.services import user_service
from app.dependencies.user_dependencies import get_user_or_404
from app.data import users_db

router = APIRouter(prefix="/users", tags=["Usuarios"])

CUSTOM_HEADERS = {"X-App-Name": "device_systems", "X-API-Version": "2.0"}


def _headers(response: Response):
    for k, v in CUSTOM_HEADERS.items():
        response.headers[k] = v


# ── GET /users ─────────────────────────────────
@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Retorna todos los usuarios. Permite filtrar por **rol** y/o **estado**.",
    response_description="Lista de usuarios encontrados",
    status_code=status.HTTP_200_OK,
)
def get_users(
    response: Response,
    role: Optional[str] = Query(default=None, description="Filtrar por rol: admin, support, user"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo"),
):
    _headers(response)
    users = user_service.list_users(role=role, is_active=is_active)
    return {"total": len(users), "users": users}


# ── GET /users/{user_id} ────────────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Retorna un usuario específico usando su **ID** como path parameter.",
    response_description="Usuario encontrado",
    status_code=status.HTTP_200_OK,
)
def get_user(response: Response, user=Depends(get_user_or_404)):
    _headers(response)
    return user


# ── POST /users ─────────────────────────────────
@router.post(
    "",
    response_model=UserResponse,
    summary="Crear usuario",
    description="Registra un nuevo usuario. Valida datos con Pydantic y evita correos duplicados.",
    response_description="Usuario creado exitosamente",
    status_code=status.HTTP_201_CREATED,
)
def create_user(user_in: UserCreate, response: Response):
    _headers(response)
    return user_service.create_user(user_in)


# ── PUT /users/{user_id} ────────────────────────
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo (PUT)",
    description="Reemplaza **todos** los campos de un usuario existente.",
    response_description="Usuario actualizado",
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_in: UserUpdate,
    response: Response,
    user=Depends(get_user_or_404),
):
    _headers(response)
    return user_service.update_user(user["id"], user_in)


# ── PATCH /users/{user_id} ──────────────────────
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcial (PATCH)",
    description="Modifica **solo los campos enviados** del usuario. Mínimo un campo requerido.",
    response_description="Usuario actualizado parcialmente",
    status_code=status.HTTP_200_OK,
)
def patch_user(
    user_in: UserPatch,
    response: Response,
    user=Depends(get_user_or_404),
):
    _headers(response)
    return user_service.patch_user(user["id"], user_in)


# ── DELETE /users/{user_id} ─────────────────────
@router.delete(
    "/{user_id}",
    summary="Eliminar usuario",
    description="Elimina permanentemente un usuario del sistema.",
    response_description="Usuario eliminado",
    status_code=status.HTTP_200_OK,
)
def delete_user(response: Response, user=Depends(get_user_or_404)):
    _headers(response)
    user_service.delete_user(user["id"])
    return {"message": f"Usuario '{user['name']}' eliminado correctamente."}