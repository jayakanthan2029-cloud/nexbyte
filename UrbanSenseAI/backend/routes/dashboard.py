from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, schemas, models
from backend.routes.health import EDGE_HEALTH_STATE

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    """Executive summary KPI metrics for the UrbanSenseAI platform."""
    summary_data = crud.get_dashboard_summary(db)
    return schemas.DashboardSummary(**summary_data)

@router.get("/live")
def get_live_state(db: Session = Depends(get_db)):
    """Unified telemetry snapshot for real-time dashboard hydration."""
    buses = crud.get_buses(db)
    recent_events = crud.get_events(db, limit=10)
    recent_traffic = crud.get_traffic_records(db, limit=10)
    recent_incidents = crud.get_incidents(db, limit=10)
    summary = crud.get_dashboard_summary(db)

    # Check edge heartbeat
    ai_status = EDGE_HEALTH_STATE["ai_engine"]
    camera_status = EDGE_HEALTH_STATE["camera"]
    if EDGE_HEALTH_STATE["last_edge_heartbeat"]:
        diff = (datetime.utcnow() - EDGE_HEALTH_STATE["last_edge_heartbeat"]).total_seconds()
        if diff > 15:
            ai_status = "offline"
            camera_status = "disconnected"

    return {
        "summary": summary,
        "edge_status": {
            "ai_engine": ai_status,
            "camera": camera_status,
            "gps": EDGE_HEALTH_STATE["gps"],
            "last_heartbeat": EDGE_HEALTH_STATE["last_edge_heartbeat"]
        },
        "buses": [
            {
                "bus_id": b.bus_id,
                "registration_number": b.registration_number,
                "route_name": b.route_name,
                "status": b.status,
                "camera_status": b.camera_status,
                "latitude": b.latitude,
                "longitude": b.longitude,
                "gps_status": b.gps_status,
                "last_seen": b.last_seen,
                "is_simulated": (b.bus_id != "BUS-001")
            }
            for b in buses
        ],
        "recent_events": [
            {
                "id": e.id,
                "bus_id": e.bus_id,
                "event_type": e.event_type,
                "source_type": e.source_type,
                "latitude": e.latitude,
                "longitude": e.longitude,
                "confidence": e.confidence,
                "description": e.description,
                "status": e.status,
                "timestamp": e.timestamp,
                "media_count": len(e.media)
            }
            for e in recent_events
        ],
        "recent_traffic": [
            {
                "id": t.id,
                "bus_id": t.bus_id,
                "source_type": t.source_type,
                "vehicle_count": t.vehicle_count,
                "cars": t.cars,
                "motorcycles": t.motorcycles,
                "buses": t.buses,
                "trucks": t.trucks,
                "movement_score": t.movement_score,
                "traffic_level": t.traffic_level,
                "probable_reasons": t.probable_reasons,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "timestamp": t.timestamp
            }
            for t in recent_traffic
        ],
        "recent_incidents": [
            {
                "id": i.id,
                "incident_id": i.incident_id,
                "bus_id": i.bus_id,
                "incident_type": i.incident_type,
                "source_type": i.source_type,
                "latitude": i.latitude,
                "longitude": i.longitude,
                "confidence": i.confidence,
                "status": i.status,
                "description": i.description,
                "plate_number": i.plate_number,
                "timestamp": i.timestamp,
                "media": [
                    {
                        "media_type": m.media_type,
                        "file_path": m.file_path,
                        "file_name": m.file_name
                    }
                    for m in i.media
                ]
            }
            for i in recent_incidents
        ]
    }
