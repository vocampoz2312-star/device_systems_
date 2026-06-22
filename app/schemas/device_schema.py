from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, max_length=100, examples=["LEN-2024-001"])
    device_type: str = Field(..., examples=["laptop"])
    brand: Optional[str] = Field(default=None, max_length=100, examples=["Lenovo"])
    is_available: bool = Field(default=True)


class DeviceUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    serial_number: str = Field(..., min_length=3, max_length=100)
    device_type: str = Field(...)
    brand: Optional[str] = Field(default=None, max_length=100)
    is_available: bool = Field(...)


class DevicePatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    serial_number: Optional[str] = Field(default=None, min_length=3, max_length=100)
    device_type: Optional[str] = Field(default=None)
    brand: Optional[str] = Field(default=None, max_length=100)
    is_available: Optional[bool] = Field(default=None)


class DeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str] = None
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    total: int
    devices: list[DeviceResponse]
