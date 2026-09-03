from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db

router = APIRouter(tags=["Health"])

# Global state tracker for edge nodes
EDGE_HEALTH_STATE = {
    "ai_engine": "standby",
    "camera": "disconnected",
    "gps": "unavailable",
    "last_edge_heartbeat": None
}

def update_edge_health(ai_engine: str = None, camera: str = None, gps: str = None):
    if ai_engine:
        EDGE_HEALTH_STATE["ai_engine"] = ai_engine
    if camera:
        EDGE_HEALTH_STATE["camera"] = camera
    if gps:
        EDGE_HEALTH_STATE["gps"] = gps
    EDGE_HEALTH_STATE["last_edge_heartbeat"] = datetime.utcnow()

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    """System health check endpoint verifying DB and Edge status."""
    # Check Database connection
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Edge AI Engine status check
    ai_status = EDGE_HEALTH_STATE["ai_engine"]
    camera_status = EDGE_HEALTH_STATE["camera"]
    gps_status = EDGE_HEALTH_STATE["gps"]

    if EDGE_HEALTH_STATE["last_edge_heartbeat"]:
        diff = (datetime.utcnow() - EDGE_HEALTH_STATE["last_edge_heartbeat"]).total_seconds()
        if diff > 15: # Timeout after 15s of silence
            ai_status = "offline"
            camera_status = "disconnected"
            gps_status = "unavailable"

    return {
        "backend": "online",
        "database": db_status,
        "ai_engine": ai_status,
        "camera": camera_status,
        "gps": gps_status,
        "timestamp": datetime.utcnow().isoformat()
    }
