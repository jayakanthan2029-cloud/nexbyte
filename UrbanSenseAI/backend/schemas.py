from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

# ============================================================
# BUS SCHEMAS
# ============================================================
class BusBase(BaseModel):
    bus_id: str
    registration_number: Optional[str] = None
    route_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    camera_status: Optional[str] = "DISCONNECTED"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gps_status: Optional[str] = "UNAVAILABLE" # 'LIVE_GPS', 'UNAVAILABLE', 'SIMULATED'

class BusCreate(BusBase):
    pass

class BusUpdate(BaseModel):
    status: Optional[str] = None
    camera_status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gps_status: Optional[str] = None
    last_seen: Optional[datetime] = None

class BusResponse(BusBase):
    id: int
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_simulated: bool = False

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# MEDIA SCHEMAS
# ============================================================
class MediaBase(BaseModel):
    media_type: str
    file_path: str
    file_name: str

class MediaCreate(MediaBase):
    event_id: Optional[int] = None
    incident_id: Optional[int] = None

class MediaResponse(MediaBase):
    id: int
    event_id: Optional[int] = None
    incident_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# EVENT SCHEMAS (Potholes, Waterlogging, Hazards)
# ============================================================
class EventBase(BaseModel):
    bus_id: str
    event_type: str
    source_type: Optional[str] = "LIVE_EDGE_AI"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: Optional[float] = 0.0
    description: Optional[str] = None
    status: Optional[str] = "NEW"

class EventCreate(EventBase):
    timestamp: Optional[datetime] = None
    media_files: Optional[List[dict]] = None

class EventResponse(EventBase):
    id: int
    timestamp: datetime
    created_at: datetime
    media: List[MediaResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TRAFFIC SCHEMAS
# ============================================================
class TrafficAnalysisBase(BaseModel):
    bus_id: str
    source_type: Optional[str] = "LIVE_EDGE_AI"
    vehicle_count: int
    cars: int
    motorcycles: int
    buses: int
    trucks: int
    movement_score: float
    traffic_level: str
    probable_reasons: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class TrafficAnalysisCreate(TrafficAnalysisBase):
    timestamp: Optional[datetime] = None

class TrafficAnalysisResponse(TrafficAnalysisBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# INCIDENT SCHEMAS (Collisions)
# ============================================================
class IncidentBase(BaseModel):
    bus_id: str
    incident_type: Optional[str] = "Potential Collision"
    source_type: Optional[str] = "LIVE_EDGE_AI"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: Optional[float] = 0.0
    status: Optional[str] = "PENDING_REVIEW"
    description: Optional[str] = None
    plate_number: Optional[str] = None

class IncidentCreate(IncidentBase):
    incident_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    media_files: Optional[List[dict]] = None

class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    timestamp: datetime
    created_at: datetime
    media: List[MediaResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# LOCATION SCHEMAS
# ============================================================
class LocationCreate(BaseModel):
    bus_id: str
    source_type: Optional[str] = "LIVE_GPS" # 'LIVE_GPS', 'SIMULATED_GPS'
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = 0.0
    timestamp: Optional[datetime] = None

class LocationResponse(BaseModel):
    id: int
    bus_id: str
    source_type: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# DASHBOARD SUMMARY SCHEMAS
# ============================================================
class DashboardSummary(BaseModel):
    active_buses: int
    live_events_count: int
    potholes_count: int
    critical_incidents_count: int
    high_traffic_zones_count: int
    waterlogging_count: int
    fleet_health: dict
    system_status: dict

class SystemHealthResponse(BaseModel):
    backend: str
    database: str
    ai_engine: str
    camera: str
    gps: str
    timestamp: datetime
