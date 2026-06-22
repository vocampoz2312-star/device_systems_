from fastapi import APIRouter, Query, Response, Depends, status
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.loan_schema import (
    LoanCreate, LoanDetailResponse,
    LoanListResponse, LoanResponse,
)
from app.services import loan_service
from app.dependencies.database_dependency import get_db

router = APIRouter(prefix="/loans", tags=["Loans"])

CUSTOM_HEADERS = {"X-App-Name": "device_systems", "X-API-Version": "3.0"}


def _headers(response: Response):
    for k, v in CUSTOM_HEADERS.items():
        response.headers[k] = v


@router.get(
    "/details",
    response_model=LoanListResponse,
    summary="Listar préstamos con detalle",
    description="Retorna todos los préstamos con información del usuario y del dispositivo. Permite múltiples filtros.",
    response_description="Lista de préstamos con detalle",
    status_code=status.HTTP_200_OK,
)
def get_loans_details(
    response: Response,
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filtrar por estado: active, returned, overdue"),
    user_email: Optional[str] = Query(default=None, description="Filtrar por correo del usuario"),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    loan_date_from: Optional[str] = Query(default=None, description="Fecha inicial (ISO 8601: 2024-01-01)"),
    loan_date_to: Optional[str] = Query(default=None, description="Fecha final (ISO 8601: 2024-12-31)"),
):
    _headers(response)
    loans = loan_service.list_loans(
        db, status_filter=status_filter, user_email=user_email,
        device_type=device_type, loan_date_from=loan_date_from,
        loan_date_to=loan_date_to,
    )
    return {"total": len(loans), "loans": loans}


@router.get(
    "",
    response_model=LoanListResponse,
    summary="Listar préstamos",
    description="Retorna todos los préstamos con información relacionada. Acepta filtros por estado, correo, tipo de dispositivo y fechas.",
    response_description="Lista de préstamos",
    status_code=status.HTTP_200_OK,
)
def get_loans(
    response: Response,
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filtrar por estado: active, returned, overdue"),
    user_email: Optional[str] = Query(default=None, description="Filtrar por correo del usuario"),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
):
    _headers(response)
    loans = loan_service.list_loans(
        db, status_filter=status_filter, user_email=user_email,
        device_type=device_type,
    )
    return {"total": len(loans), "loans": loans}


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Obtener préstamo por ID",
    description="Retorna un préstamo específico con información del usuario y del dispositivo.",
    response_description="Préstamo encontrado",
    status_code=status.HTTP_200_OK,
)
def get_loan(loan_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return loan_service.get_loan(db, loan_id)


@router.post(
    "",
    response_model=LoanDetailResponse,
    summary="Crear préstamo",
    description="Registra un nuevo préstamo. Valida que el usuario y el dispositivo existan, y que el dispositivo esté disponible. Cambia is_available a False.",
    response_description="Préstamo creado exitosamente",
    status_code=status.HTTP_201_CREATED,
)
def create_loan(loan_in: LoanCreate, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return loan_service.create_loan(db, loan_in)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanDetailResponse,
    summary="Devolver dispositivo",
    description="Marca un préstamo como devuelto, asigna fecha de devolución y cambia is_available del dispositivo a True.",
    response_description="Préstamo actualizado como devuelto",
    status_code=status.HTTP_200_OK,
)
def return_loan(loan_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return loan_service.return_loan(db, loan_id)
