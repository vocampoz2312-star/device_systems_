from typing import Optional
from fastapi import HTTPException, status
from app.data import users_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch


# ──────────────────────────────────────────────
# Servicio de usuarios — lógica de negocio
# ──────────────────────────────────────────────

def list_users(role: Optional[str] = None, is_active: Optional[bool] = None):
    users = users_db.get_all()
    if role:
        users = [u for u in users if u["role"] == role]
    if is_active is not None:
        users = [u for u in users if u["is_active"] == is_active]
    return users


def get_user(user_id: int):
    user = users_db.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={user_id} no encontrado.",
        )
    return user


def create_user(data: UserCreate):
    if users_db.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo '{data.email}' ya está registrado.",
        )
    new_user = {
        "id": 0,  # será asignado por users_db.insert
        "name": data.name,
        "email": data.email,
        "role": data.role.value,
        "is_active": data.is_active,
    }
    return users_db.insert(new_user)


def update_user(user_id: int, data: UserUpdate):
    # Verificar que el usuario existe
    get_user(user_id)

    # Verificar correo duplicado excluyendo al usuario actual
    if users_db.email_exists(data.email, exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo '{data.email}' ya está registrado por otro usuario.",
        )

    updated = users_db.update(user_id, {
        "name": data.name,
        "email": data.email,
        "role": data.role.value,
        "is_active": data.is_active,
    })
    return updated


def patch_user(user_id: int, data: UserPatch):
    # Verificar que el usuario existe
    get_user(user_id)

    # Obtener solo los campos que fueron enviados
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar.",
        )

    # Verificar correo duplicado si se envía email
    if "email" in changes and users_db.email_exists(changes["email"], exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo '{changes['email']}' ya está registrado por otro usuario.",
        )

    # Convertir role a string si viene como enum
    if "role" in changes and hasattr(changes["role"], "value"):
        changes["role"] = changes["role"].value

    return users_db.update(user_id, changes)


def delete_user(user_id: int):
    get_user(user_id)  # lanza 404 si no existe
    users_db.delete(user_id)