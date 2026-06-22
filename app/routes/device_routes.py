from fastapi import APIRouter, Query, Response, Depends, status
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.device_schema import (
    DeviceCreate, DeviceUpdate, DevicePatch,
    DeviceResponse, DeviceListResponse,
)
from app.services import device_service, loan_service
from app.dependencies.database_dependency import get_db

router = APIRouter(prefix="/devices", tags=["Devices"])

CUSTOM_HEADERS = {"X-App-Name": "device_systems", "X-API-Version": "3.0"}


def _headers(response: Response):
    for k, v in CUSTOM_HEADERS.items():
        response.headers[k] = v


@router.get(
    "",
    response_model=DeviceListResponse,
    summary="Listar dispositivos",
    description="Retorna todos los dispositivos registrados. Permite filtrar por tipo, disponibilidad, marca y búsqueda textual.",
    response_description="Lista de dispositivos",
    status_code=status.HTTP_200_OK,
)
def get_devices(
    response: Response,
    db: Session = Depends(get_db),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo: laptop, tablet, proyector, etc."),
    is_available: Optional[bool] = Query(default=None, description="Filtrar por disponibilidad"),
    brand: Optional[str] = Query(default=None, description="Filtrar por marca (búsqueda parcial)"),
    search: Optional[str] = Query(default=None, description="Búsqueda textual en nombre, serie o marca"),
):
    _headers(response)
    devices = device_service.list_devices(
        db, device_type=device_type, is_available=is_available,
        brand=brand, search=search,
    )
    return {"total": len(devices), "devices": devices}


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Obtener dispositivo por ID",
    description="Retorna un dispositivo específico usando su ID.",
    response_description="Dispositivo encontrado",
    status_code=status.HTTP_200_OK,
)
def get_device(device_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return device_service.get_device(db, device_id)


@router.post(
    "",
    response_model=DeviceResponse,
    summary="Crear dispositivo",
    description="Registra un nuevo dispositivo. El número de serie debe ser único.",
    response_description="Dispositivo creado exitosamente",
    status_code=status.HTTP_201_CREATED,
)
def create_device(device_in: DeviceCreate, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return device_service.create_device(db, device_in)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo completo (PUT)",
    description="Reemplaza todos los campos de un dispositivo existente.",
    response_description="Dispositivo actualizado",
    status_code=status.HTTP_200_OK,
)
def update_device(device_id: int, device_in: DeviceUpdate, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return device_service.update_device(db, device_id, device_in)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcial (PATCH)",
    description="Modifica solo los campos enviados. Mínimo un campo requerido.",
    response_description="Dispositivo actualizado parcialmente",
    status_code=status.HTTP_200_OK,
)
def patch_device(device_id: int, device_in: DevicePatch, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    return device_service.patch_device(db, device_id, device_in)


@router.get(
    "/{device_id}/loans",
    response_model=dict,
    summary="Historial de préstamos de un dispositivo",
    description="Retorna todos los préstamos asociados a un dispositivo específico.",
    response_description="Lista de préstamos del dispositivo",
    status_code=status.HTTP_200_OK,
)
def get_device_loans(device_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    loans = loan_service.get_device_loans(db, device_id)
    return {"total": len(loans), "loans": loans}


@router.delete(
    "/{device_id}",
    summary="Eliminar dispositivo",
    description="Elimina permanentemente un dispositivo de la base de datos.",
    response_description="Confirmación de eliminación",
    status_code=status.HTTP_200_OK,
)
def delete_device(device_id: int, response: Response, db: Session = Depends(get_db)):
    _headers(response)
    device = device_service.delete_device(db, device_id)
    return {"message": f"Dispositivo '{device.name}' eliminado correctamente."}
