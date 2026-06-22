from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoanCreate(BaseModel):
    user_id: int = Field(..., ge=1, examples=[1])
    device_id: int = Field(..., ge=1, examples=[1])


class LoanUpdate(BaseModel):
    status: str = Field(..., examples=["active", "returned", "overdue"])


class UserBrief(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class DeviceBrief(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    model_config = {"from_attributes": True}


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: str

    model_config = {"from_attributes": True}


class LoanDetailResponse(BaseModel):
    id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: str
    user: UserBrief
    device: DeviceBrief

    model_config = {"from_attributes": True}


class LoanListResponse(BaseModel):
    total: int
    loans: list[LoanDetailResponse]
