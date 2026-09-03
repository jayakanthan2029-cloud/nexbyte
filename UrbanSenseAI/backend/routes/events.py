from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/events", tags=["Events"])

# Reference to WebSocket broadcast function (will be set in main.py)
ws_broadcast = None

def set_ws_broadcast(func):
    global ws_broadcast
    ws_broadcast = func

@router.get("", response_model=List[schemas.EventResponse])
def read_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    bus_id: Optional[str] = Query(None, description="Filter by bus ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve road events (potholes, waterlogging, hazards)."""
    return crud.get_events(db, event_type=event_type, bus_id=bus_id, skip=skip, limit=limit)

@router.post("", response_model=schemas.EventResponse)
async def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """Create a new road hazard or infrastructure event."""
    db_event = crud.create_event(db, event)

    # Broadcast to WebSocket if active
    if ws_broadcast:
        await ws_broadcast({
            "type": f"{event.event_type}_DETECTED",
            "data": {
                "id": db_event.id,
                "bus_id": db_event.bus_id,
                "event_type": db_event.event_type,
                "source_type": db_event.source_type,
                "latitude": db_event.latitude,
                "longitude": db_event.longitude,
                "confidence": db_event.confidence,
                "description": db_event.description,
                "timestamp": db_event.timestamp.isoformat(),
                "media": [
                    {
                        "id": m.id,
                        "media_type": m.media_type,
                        "file_path": m.file_path,
                        "file_name": m.file_name
                    }
                    for m in db_event.media
                ]
            }
        })

    return db_event

@router.get("/{event_id}", response_model=schemas.EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db)):
    """Retrieve a single event by ID."""
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
