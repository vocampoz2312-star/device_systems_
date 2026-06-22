from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.device_model import Device
from app.schemas.loan_schema import LoanCreate


def _get_loan_or_404(db: Session, loan_id: int) -> Loan:
    loan = (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.id == loan_id)
        .first()
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo con id={loan_id} no encontrado.",
        )
    return loan


def list_loans(
    db: Session,
    status_filter: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
    loan_date_from: Optional[str] = None,
    loan_date_to: Optional[str] = None,
) -> list[Loan]:
    query = (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .join(Loan.user)
        .join(Loan.device)
    )
    if status_filter:
        query = query.filter(Loan.status == status_filter)
    if user_email:
        query = query.filter(User.email.ilike(user_email))
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if loan_date_from:
        try:
            dt_from = datetime.fromisoformat(loan_date_from)
            query = query.filter(Loan.loan_date >= dt_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Formato de fecha inválido para loan_date_from. Use ISO 8601 (ej: 2024-01-01).",
            )
    if loan_date_to:
        try:
            dt_to = datetime.fromisoformat(loan_date_to)
            query = query.filter(Loan.loan_date <= dt_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Formato de fecha inválido para loan_date_to. Use ISO 8601 (ej: 2024-12-31).",
            )
    return query.order_by(Loan.id).all()


def get_loan(db: Session, loan_id: int) -> Loan:
    return _get_loan_or_404(db, loan_id)


def create_loan(db: Session, data: LoanCreate) -> Loan:
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={data.user_id} no encontrado.",
        )
    device = db.query(Device).filter(Device.id == data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con id={data.device_id} no encontrado.",
        )
    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El dispositivo '{device.name}' (id={device.id}) no está disponible.",
        )
    loan = Loan(
        user_id=data.user_id,
        device_id=data.device_id,
        status="active",
    )
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = _get_loan_or_404(db, loan_id)
    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El préstamo con id={loan_id} ya fue devuelto.",
        )
    loan.status = "returned"
    loan.return_date = datetime.utcnow()
    device = db.query(Device).filter(Device.id == loan.device_id).first()
    if device:
        device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan


def get_user_loans(db: Session, user_id: int) -> list[Loan]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={user_id} no encontrado.",
        )
    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.user_id == user_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )


def get_device_loans(db: Session, device_id: int) -> list[Loan]:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con id={device_id} no encontrado.",
        )
    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.device_id == device_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )
