from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TrafficTelemetrySchema(BaseModel):
    bus_id: str
    vehicle_count: int
    cars: int
    motorcycles: int
    buses: int
    trucks: int
    movement_score: float
    traffic_level: str
    probable_reasons: List[str]
    latitude: float
    longitude: float

class EventDispatchSchema(BaseModel):
    bus_id: str
    event_type: str
    latitude: float
    longitude: float
    confidence: float
    description: str
    status: str
