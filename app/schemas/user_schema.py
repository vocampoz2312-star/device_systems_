from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
from typing import Optional


class RoleEnum(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


class UserCreate(BaseModel):
    """Datos requeridos para crear un usuario."""
    name: str = Field(..., min_length=3, max_length=100, examples=["Juan Pérez"])
    email: EmailStr = Field(..., examples=["juan@example.com"])
    role: RoleEnum = Field(..., examples=["user"])
    is_active: bool = Field(default=True)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return v.strip()


class UserUpdate(BaseModel):
    """Datos requeridos para actualización completa (PUT)."""
    name: str = Field(..., min_length=3, max_length=100, examples=["Juan Pérez"])
    email: EmailStr = Field(..., examples=["juan@example.com"])
    role: RoleEnum = Field(..., examples=["admin"])
    is_active: bool = Field(...)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return v.strip()


class UserPatch(BaseModel):
    """Datos opcionales para actualización parcial (PATCH)."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    email: Optional[EmailStr] = Field(default=None)
    role: Optional[RoleEnum] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class UserResponse(BaseModel):
    """Modelo de respuesta estandarizado."""
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


class MessageResponse(BaseModel):
    """Respuesta de mensaje simple."""
    message: str


class ErrorResponse(BaseModel):
    """Respuesta de error estructurada."""
    error: bool = True
    message: str
    status_code: int