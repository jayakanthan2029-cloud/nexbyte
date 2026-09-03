from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/buses", tags=["Buses"])

@router.get("", response_model=List[schemas.BusResponse])
def read_buses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all buses with live vs simulated tagging."""
    buses = crud.get_buses(db, skip=skip, limit=limit)
    response = []
    for b in buses:
        bus_dict = {
            "id": b.id,
            "bus_id": b.bus_id,
            "registration_number": b.registration_number,
            "route_name": b.route_name,
            "status": b.status,
            "camera_status": b.camera_status,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "gps_status": b.gps_status,
            "last_seen": b.last_seen,
            "created_at": b.created_at,
            "is_simulated": (b.bus_id != "BUS-001") # BUS-001 is the only real prototype bus
        }
        response.append(schemas.BusResponse(**bus_dict))
    return response

@router.post("", response_model=schemas.BusResponse)
def create_or_update_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    """Register or update a bus in the fleet."""
    db_bus = crud.create_or_update_bus(db, bus)
    bus_dict = {
        "id": db_bus.id,
        "bus_id": db_bus.bus_id,
        "registration_number": db_bus.registration_number,
        "route_name": db_bus.route_name,
        "status": db_bus.status,
        "camera_status": db_bus.camera_status,
        "latitude": db_bus.latitude,
        "longitude": db_bus.longitude,
        "gps_status": db_bus.gps_status,
        "last_seen": db_bus.last_seen,
        "created_at": db_bus.created_at,
        "is_simulated": (db_bus.bus_id != "BUS-001")
    }
    return schemas.BusResponse(**bus_dict)

@router.get("/{bus_id}", response_model=schemas.BusResponse)
def read_bus(bus_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific bus by ID."""
    db_bus = crud.get_bus(db, bus_id)
    if not db_bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    bus_dict = {
        "id": db_bus.id,
        "bus_id": db_bus.bus_id,
        "registration_number": db_bus.registration_number,
        "route_name": db_bus.route_name,
        "status": db_bus.status,
        "camera_status": db_bus.camera_status,
        "latitude": db_bus.latitude,
        "longitude": db_bus.longitude,
        "gps_status": db_bus.gps_status,
        "last_seen": db_bus.last_seen,
        "created_at": db_bus.created_at,
        "is_simulated": (db_bus.bus_id != "BUS-001")
    }
    return schemas.BusResponse(**bus_dict)
