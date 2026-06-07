from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from typing import List, Optional


class RoleEnum(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="Juan Pérez")
    email: str = Field(..., example="juan@example.com")
    role: RoleEnum = Field(..., example="user")
    is_active: bool = Field(default=True)

    @validator("name")
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return v.strip()

    @validator("email")
    def email_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Formato de correo inválido.")
        return v.lower().strip()


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]