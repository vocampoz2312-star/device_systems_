from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc
from fastapi import HTTPException, status

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch


# ──────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────

def _get_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={user_id} no encontrado.",
        )
    return user


def _check_email_duplicate(db: Session, email: str, exclude_id: Optional[int] = None):
    query = db.query(User).filter(User.email == email.lower())
    if exclude_id:
        query = query.filter(User.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El correo '{email}' ya está registrado.",
        )


# ──────────────────────────────────────────────
# Operaciones CRUD
# ──────────────────────────────────────────────

def list_users(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    order_by: str = "id",
) -> list[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if order_by == "name":
        query = query.order_by(asc(User.name))
    elif order_by == "created_at":
        query = query.order_by(asc(User.created_at))
    else:
        query = query.order_by(asc(User.id))
    return query.all()


def get_user(db: Session, user_id: int) -> User:
    return _get_or_404(db, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def create_user(db: Session, data: UserCreate) -> User:
    _check_email_duplicate(db, data.email)
    user = User(
        name=data.name,
        email=data.email.lower(),
        role=data.role.value,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = _get_or_404(db, user_id)
    _check_email_duplicate(db, data.email, exclude_id=user_id)
    user.name = data.name
    user.email = data.email.lower()
    user.role = data.role.value
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user_id: int, data: UserPatch) -> User:
    user = _get_or_404(db, user_id)
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar.",
        )

    if "email" in changes:
        _check_email_duplicate(db, changes["email"], exclude_id=user_id)
        changes["email"] = changes["email"].lower()

    if "role" in changes and hasattr(changes["role"], "value"):
        changes["role"] = changes["role"].value

    for field, value in changes.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> User:
    user = _get_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return user