from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/incidents", tags=["Incidents"])

ws_broadcast = None

def set_ws_broadcast(func):
    global ws_broadcast
    ws_broadcast = func

@router.get("", response_model=List[schemas.IncidentResponse])
def read_incidents(
    status: Optional[str] = Query(None, description="Filter by status (PENDING_REVIEW, REVIEWED)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve recorded potential collision and accident incidents."""
    return crud.get_incidents(db, status=status, skip=skip, limit=limit)

@router.post("", response_model=schemas.IncidentResponse)
async def create_incident(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db)
):
    """Record a potential collision with rolling buffer evidence and OCR."""
    db_incident = crud.create_incident(db, incident)

    if ws_broadcast:
        await ws_broadcast({
            "type": "INCIDENT_DETECTED",
            "data": {
                "id": db_incident.id,
                "incident_id": db_incident.incident_id,
                "bus_id": db_incident.bus_id,
                "incident_type": db_incident.incident_type,
                "source_type": db_incident.source_type,
                "latitude": db_incident.latitude,
                "longitude": db_incident.longitude,
                "confidence": db_incident.confidence,
                "status": db_incident.status,
                "description": db_incident.description,
                "plate_number": db_incident.plate_number,
                "timestamp": db_incident.timestamp.isoformat(),
                "media": [
                    {
                        "id": m.id,
                        "media_type": m.media_type,
                        "file_path": m.file_path,
                        "file_name": m.file_name
                    }
                    for m in db_incident.media
                ]
            }
        })

    return db_incident

@router.get("/{incident_id}", response_model=schemas.IncidentResponse)
def read_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve details and media evidence for a specific incident."""
    db_incident = crud.get_incident(db, incident_id)
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident

@router.put("/{incident_id}/status", response_model=schemas.IncidentResponse)
def update_status(
    incident_id: str,
    status: str = Query(..., description="New status, e.g. REVIEWED"),
    db: Session = Depends(get_db)
):
    """Mark an incident as reviewed or actioned."""
    db_incident = crud.update_incident_status(db, incident_id, status)
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db_incident
