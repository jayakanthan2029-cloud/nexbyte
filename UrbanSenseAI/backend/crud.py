from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend import models, schemas

# ============================================================
# BUSES CRUD
# ============================================================
def get_buses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Bus]:
    return db.query(models.Bus).offset(skip).limit(limit).all()

def get_bus(db: Session, bus_id: str) -> Optional[models.Bus]:
    return db.query(models.Bus).filter(models.Bus.bus_id == bus_id).first()

def create_or_update_bus(db: Session, bus: schemas.BusCreate) -> models.Bus:
    db_bus = get_bus(db, bus.bus_id)
    if db_bus:
        for key, value in bus.model_dump(exclude_unset=True).items():
            setattr(db_bus, key, value)
        db_bus.last_seen = datetime.utcnow()
    else:
        db_bus = models.Bus(**bus.model_dump())
        db_bus.last_seen = datetime.utcnow()
        db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

def update_bus_telemetry(
    db: Session,
    bus_id: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    camera_status: Optional[str] = None,
    gps_status: Optional[str] = None
) -> Optional[models.Bus]:
    db_bus = get_bus(db, bus_id)
    if db_bus:
        if latitude is not None and longitude is not None:
            db_bus.latitude = latitude
            db_bus.longitude = longitude
        db_bus.last_seen = datetime.utcnow()
        if camera_status:
            db_bus.camera_status = camera_status
        if gps_status:
            db_bus.gps_status = gps_status
        db.commit()
        db.refresh(db_bus)
    return db_bus


# ============================================================
# EVENTS CRUD
# ============================================================
def get_events(
    db: Session,
    event_type: Optional[str] = None,
    bus_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Event]:
    query = db.query(models.Event)
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if bus_id:
        query = query.filter(models.Event.bus_id == bus_id)
    return query.order_by(desc(models.Event.timestamp)).offset(skip).limit(limit).all()

def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    event_data = event.model_dump(exclude={"media_files"})
    if not event_data.get("timestamp"):
        event_data["timestamp"] = datetime.utcnow()

    db_event = models.Event(**event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    if event.media_files:
        for m in event.media_files:
            db_media = models.Media(
                event_id=db_event.id,
                media_type=m.get("media_type", "IMAGE"),
                file_path=m.get("file_path", ""),
                file_name=m.get("file_name", "")
            )
            db.add(db_media)
        db.commit()
        db.refresh(db_event)

    return db_event


# ============================================================
# TRAFFIC ANALYSIS CRUD
# ============================================================
def get_traffic_records(
    db: Session,
    bus_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.TrafficAnalysis]:
    query = db.query(models.TrafficAnalysis)
    if bus_id:
        query = query.filter(models.TrafficAnalysis.bus_id == bus_id)
    return query.order_by(desc(models.TrafficAnalysis.timestamp)).offset(skip).limit(limit).all()

def create_traffic_record(
    db: Session,
    traffic: schemas.TrafficAnalysisCreate
) -> models.TrafficAnalysis:
    update_bus_telemetry(db, traffic.bus_id, traffic.latitude, traffic.longitude)

    traffic_data = traffic.model_dump()
    if not traffic_data.get("timestamp"):
        traffic_data["timestamp"] = datetime.utcnow()

    db_traffic = models.TrafficAnalysis(**traffic_data)
    db.add(db_traffic)
    db.commit()
    db.refresh(db_traffic)
    return db_traffic


# ============================================================
# INCIDENTS CRUD
# ============================================================
def get_incidents(
    db: Session,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Incident]:
    query = db.query(models.Incident)
    if status:
        query = query.filter(models.Incident.status == status)
    return query.order_by(desc(models.Incident.timestamp)).offset(skip).limit(limit).all()

def get_incident(db: Session, incident_id: str) -> Optional[models.Incident]:
    return db.query(models.Incident).filter(models.Incident.incident_id == incident_id).first()

def create_incident(db: Session, incident: schemas.IncidentCreate) -> models.Incident:
    inc_id = incident.incident_id or f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    incident_data = incident.model_dump(exclude={"media_files"})
    incident_data["incident_id"] = inc_id
    if not incident_data.get("timestamp"):
        incident_data["timestamp"] = datetime.utcnow()

    db_incident = models.Incident(**incident_data)
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    if incident.media_files:
        for m in incident.media_files:
            db_media = models.Media(
                incident_id=db_incident.id,
                media_type=m.get("media_type", "VIDEO"),
                file_path=m.get("file_path", ""),
                file_name=m.get("file_name", "")
            )
            db.add(db_media)
        db.commit()
        db.refresh(db_incident)

    return db_incident

def update_incident_status(db: Session, incident_id: str, status: str) -> Optional[models.Incident]:
    db_incident = get_incident(db, incident_id)
    if db_incident:
        db_incident.status = status
        db.commit()
        db.refresh(db_incident)
    return db_incident


# ============================================================
# LOCATIONS CRUD (With Provenance)
# ============================================================
def create_location(db: Session, loc: schemas.LocationCreate) -> models.Location:
    loc_data = loc.model_dump()
    if not loc_data.get("timestamp"):
        loc_data["timestamp"] = datetime.utcnow()

    db_loc = models.Location(**loc_data)
    db.add(db_loc)
    
    # Update bus coordinate & GPS status
    update_bus_telemetry(
        db, 
        bus_id=loc.bus_id, 
        latitude=loc.latitude, 
        longitude=loc.longitude,
        gps_status=loc.source_type
    )
    
    db.commit()
    db.refresh(db_loc)
    return db_loc

def get_latest_locations(db: Session) -> List[models.Location]:
    subquery = db.query(
        models.Location.bus_id,
        func.max(models.Location.timestamp).label("max_time")
    ).group_by(models.Location.bus_id).subquery()

    return db.query(models.Location).join(
        subquery,
        (models.Location.bus_id == subquery.c.bus_id) &
        (models.Location.timestamp == subquery.c.max_time)
    ).all()


# ============================================================
# DASHBOARD SUMMARY CRUD
# ============================================================
def get_dashboard_summary(db: Session) -> dict:
    active_buses = db.query(models.Bus).filter(models.Bus.status == "ACTIVE").count()
    events_count = db.query(models.Event).count()
    potholes_count = db.query(models.Event).filter(models.Event.event_type == "POTHOLE").count()
    waterlogging_count = db.query(models.Event).filter(models.Event.event_type == "WATERLOGGING").count()
    incidents_count = db.query(models.Incident).count()
    high_traffic_count = db.query(models.TrafficAnalysis).filter(
        models.TrafficAnalysis.traffic_level.in_(["HIGH", "CRITICAL"])
    ).count()

    return {
        "active_buses": active_buses,
        "live_events_count": events_count,
        "potholes_count": potholes_count,
        "critical_incidents_count": incidents_count,
        "high_traffic_zones_count": high_traffic_count,
        "waterlogging_count": waterlogging_count,
        "fleet_health": {
            "total": db.query(models.Bus).count(),
            "active": active_buses,
            "connected_cameras": db.query(models.Bus).filter(models.Bus.camera_status == "CONNECTED").count()
        },
        "system_status": {
            "backend": "online",
            "database": "connected"
        }
    }
