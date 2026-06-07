from fastapi import APIRouter, HTTPException, Query, Path, Response, status
from typing import Optional
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, RoleEnum

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"],
)

# ──────────────────────────────────────────────
# Base de datos simulada en memoria
# ──────────────────────────────────────────────
_users_db = [
    {"id": 1, "name": "Ana Martínez",  "email": "ana.martinez@devicesystems.com",  "role": "admin",   "is_active": True},
    {"id": 2, "name": "Carlos Ruiz",   "email": "carlos.ruiz@devicesystems.com",   "role": "support", "is_active": True},
    {"id": 3, "name": "Laura Gómez",   "email": "laura.gomez@devicesystems.com",   "role": "user",    "is_active": False},
    {"id": 4, "name": "Pedro Sánchez", "email": "pedro.sanchez@devicesystems.com", "role": "user",    "is_active": True},
]

_id_counter = len(_users_db)

CUSTOM_HEADERS = {
    "X-App-Name": "device_systems",
    "X-API-Version": "1.0",
}


def _add_headers(response: Response):
    for key, value in CUSTOM_HEADERS.items():
        response.headers[key] = value


# GET /users
@router.get("", response_model=UserListResponse, summary="Listar usuarios", status_code=200)
def get_users(
    response: Response,
    role: Optional[RoleEnum] = Query(default=None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo"),
):
    _add_headers(response)
    result = _users_db.copy()
    if role is not None:
        result = [u for u in result if u["role"] == role.value]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return {"total": len(result), "users": result}


# GET /users/{user_id}
@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID", status_code=200)
def get_user_by_id(
    response: Response,
    user_id: int = Path(..., ge=1, description="ID del usuario"),
):
    _add_headers(response)
    user = next((u for u in _users_db if u["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Usuario con id={user_id} no encontrado.")
    return user


# POST /users
@router.post("", response_model=UserResponse, summary="Crear usuario", status_code=201)
def create_user(user_in: UserCreate, response: Response):
    global _id_counter
    _add_headers(response)

    if any(u["email"].lower() == user_in.email.lower() for u in _users_db):
        raise HTTPException(status_code=409, detail=f"El correo '{user_in.email}' ya está registrado.")

    _id_counter += 1
    new_user = {
        "id": _id_counter,
        "name": user_in.name,
        "email": user_in.email,
        "role": user_in.role.value,
        "is_active": user_in.is_active,
    }
    _users_db.append(new_user)
    return new_user