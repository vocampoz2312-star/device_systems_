from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate, DevicePatch


def _get_or_404(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con id={device_id} no encontrado.",
        )
    return device


def _check_serial_duplicate(db: Session, serial: str, exclude_id: Optional[int] = None):
    query = db.query(Device).filter(Device.serial_number == serial)
    if exclude_id:
        query = query.filter(Device.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El número de serie '{serial}' ya está registrado.",
        )


def list_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
) -> list[Device]:
    query = db.query(Device)
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if is_available is not None:
        query = query.filter(Device.is_available == is_available)
    if brand:
        query = query.filter(Device.brand.ilike(f"%{brand}%"))
    if search:
        query = query.filter(
            or_(
                Device.name.ilike(f"%{search}%"),
                Device.serial_number.ilike(f"%{search}%"),
                Device.brand.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Device.id).all()


def get_device(db: Session, device_id: int) -> Device:
    return _get_or_404(db, device_id)


def create_device(db: Session, data: DeviceCreate) -> Device:
    _check_serial_duplicate(db, data.serial_number)
    device = Device(
        name=data.name,
        serial_number=data.serial_number,
        device_type=data.device_type,
        brand=data.brand,
        is_available=data.is_available,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device_id: int, data: DeviceUpdate) -> Device:
    device = _get_or_404(db, device_id)
    _check_serial_duplicate(db, data.serial_number, exclude_id=device_id)
    device.name = data.name
    device.serial_number = data.serial_number
    device.device_type = data.device_type
    device.brand = data.brand
    device.is_available = data.is_available
    db.commit()
    db.refresh(device)
    return device


def patch_device(db: Session, device_id: int, data: DevicePatch) -> Device:
    device = _get_or_404(db, device_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar.",
        )
    if "serial_number" in changes:
        _check_serial_duplicate(db, changes["serial_number"], exclude_id=device_id)
    for field, value in changes.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> Device:
    device = _get_or_404(db, device_id)
    db.delete(device)
    db.commit()
    return device
