from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/traffic", tags=["Traffic"])

ws_broadcast = None

def set_ws_broadcast(func):
    global ws_broadcast
    ws_broadcast = func

@router.get("", response_model=List[schemas.TrafficAnalysisResponse])
def read_traffic_records(
    bus_id: Optional[str] = Query(None, description="Filter by bus ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve historical traffic analysis telemetry."""
    return crud.get_traffic_records(db, bus_id=bus_id, skip=skip, limit=limit)

@router.post("", response_model=schemas.TrafficAnalysisResponse)
async def create_traffic_record(
    traffic: schemas.TrafficAnalysisCreate,
    db: Session = Depends(get_db)
):
    """Receive periodic traffic analysis telemetry from edge node."""
    db_traffic = crud.create_traffic_record(db, traffic)

    if ws_broadcast:
        await ws_broadcast({
            "type": "TRAFFIC_UPDATE",
            "data": {
                "bus_id": db_traffic.bus_id,
                "source_type": db_traffic.source_type,
                "vehicle_count": db_traffic.vehicle_count,
                "cars": db_traffic.cars,
                "motorcycles": db_traffic.motorcycles,
                "buses": db_traffic.buses,
                "trucks": db_traffic.trucks,
                "movement_score": db_traffic.movement_score,
                "traffic_level": db_traffic.traffic_level,
                "probable_reasons": db_traffic.probable_reasons,
                "latitude": db_traffic.latitude,
                "longitude": db_traffic.longitude,
                "timestamp": db_traffic.timestamp.isoformat()
            }
        })

    return db_traffic
