from fastapi import APIRouter, Query, Response, Depends, status
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.user_schema import (
    UserCreate, UserUpdate, UserPatch,
    UserResponse, UserListResponse,
)
from app.schemas.loan_schema import LoanDetailResponse
from app.services import user_service, loan_service
from app.dependencies.database_dependency import get_db

router = APIRouter(prefix="/users", tags=["Usuarios"])

CUSTOM_HEADERS = {"X-App-Name": "device_systems", "X-API-Version": "3.0"}


def _headers(response: Response):
    for k, v in CUSTOM_HEADERS.items():
        response.headers[k] = v


# ── GET /users ─────────────────────────────────
@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description=(
        "Retorna todos los usuarios registrados en la base de datos. "
        "Permite filtrar por **rol** y/o **estado activo**, "
        "y ordenar por `id`, `name` o `created_at`."
    ),
    response_description="Lista paginada de usuarios",
    status_code=status.HTTP_200_OK,
)
def get_users(
    response: Response,
    db: Session = Depends(get_db),
    role: Optional[str] = Query(default=None, description="Filtrar por rol: admin, support, user"),
    is_active: Optional[bool] = Query(default=None, description="true = activos, false = inactivos"),
    order_by: str = Query(default="id", description="Ordenar por: id, name, created_at"),
):
    _headers(response)
    users = user_service.list_users(db, role=role, is_active=is_active, order_by=order_by)
    return {"total": len(users), "users": users}


# ── GET /users/{user_id} ────────────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Retorna un usuario específico desde la base de datos usando su **ID**.",
    response_description="Usuario encontrado",
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return user_service.get_user(db, user_id)


# ── POST /users ─────────────────────────────────
@router.post(
    "",
    response_model=UserResponse,
    summary="Crear usuario",
    description="Registra un nuevo usuario en la base de datos. Evita correos duplicados.",
    response_description="Usuario creado exitosamente",
    status_code=status.HTTP_201_CREATED,
)
def create_user(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return user_service.create_user(db, user_in)


# ── PUT /users/{user_id} ────────────────────────
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo (PUT)",
    description="Reemplaza **todos** los campos de un usuario existente en la base de datos.",
    response_description="Usuario actualizado",
    status_code=status.HTTP_200_OK,
)
def update_user(user_id: int, user_in: UserUpdate, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return user_service.update_user(db, user_id, user_in)


# ── PATCH /users/{user_id} ──────────────────────
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcial (PATCH)",
    description="Modifica **solo los campos enviados**. Mínimo un campo requerido.",
    response_description="Usuario actualizado parcialmente",
    status_code=status.HTTP_200_OK,
)
def patch_user(user_id: int, user_in: UserPatch, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return user_service.patch_user(db, user_id, user_in)


# ── GET /users/{user_id}/loans ───────────────────
@router.get(
    "/{user_id}/loans",
    response_model=dict,
    summary="Préstamos de un usuario",
    description="Retorna todos los préstamos asociados a un usuario específico.",
    response_description="Lista de préstamos del usuario",
    status_code=status.HTTP_200_OK,
)
def get_user_loans(user_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    loans = loan_service.get_user_loans(db, user_id)
    return {"total": len(loans), "loans": loans}


# ── DELETE /users/{user_id} ─────────────────────
@router.delete(
    "/{user_id}",
    summary="Eliminar usuario",
    description="Elimina permanentemente un usuario de la base de datos.",
    response_description="Confirmación de eliminación",
    status_code=status.HTTP_200_OK,
)
def delete_user(user_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    user = user_service.delete_user(db, user_id)
    return {"message": f"Usuario '{user.name}' eliminado correctamente."}