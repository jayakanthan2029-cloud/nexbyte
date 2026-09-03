from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/locations", tags=["Locations"])

ws_broadcast = None

def set_ws_broadcast(func):
    global ws_broadcast
    ws_broadcast = func

@router.get("", response_model=List[schemas.LocationResponse])
def read_latest_locations(db: Session = Depends(get_db)):
    """Retrieve the latest known GPS location for all active fleet buses."""
    return crud.get_latest_locations(db)

@router.post("", response_model=schemas.LocationResponse)
async def create_location(loc: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Record a real-time GPS coordinate update for a bus."""
    db_loc = crud.create_location(db, loc)

    if ws_broadcast:
        await ws_broadcast({
            "type": "BUS_LOCATION",
            "data": {
                "bus_id": db_loc.bus_id,
                "source_type": db_loc.source_type,
                "latitude": db_loc.latitude,
                "longitude": db_loc.longitude,
                "accuracy": db_loc.accuracy,
                "speed": db_loc.speed,
                "timestamp": db_loc.timestamp.isoformat()
            }
        })

    return db_loc
