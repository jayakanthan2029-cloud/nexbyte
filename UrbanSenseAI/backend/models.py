from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, ARRAY
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String(50), unique=True, index=True, nullable=False)
    registration_number = Column(String(50))
    route_name = Column(String(100))
    status = Column(String(20), default="ACTIVE")
    camera_status = Column(String(20), default="DISCONNECTED")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    gps_status = Column(String(30), default="UNAVAILABLE") # 'LIVE_GPS', 'UNAVAILABLE', 'SIMULATED'
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    events = relationship("Event", back_populates="bus", cascade="all, delete-orphan")
    traffic_records = relationship("TrafficAnalysis", back_populates="bus", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="bus", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="bus", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String(50), ForeignKey("buses.bus_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True) # POTHOLE, WATERLOGGING, ROAD_HAZARD, etc.
    source_type = Column(String(30), default="LIVE_EDGE_AI") # 'LIVE_EDGE_AI', 'DEMO_DETECTION', 'SIMULATED_EVENT'
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, default=0.0)
    description = Column(Text)
    status = Column(String(20), default="NEW")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    bus = relationship("Bus", back_populates="events")
    media = relationship("Media", back_populates="event", cascade="all, delete-orphan")


class TrafficAnalysis(Base):
    __tablename__ = "traffic_analysis"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String(50), ForeignKey("buses.bus_id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(30), default="LIVE_EDGE_AI") # 'LIVE_EDGE_AI', 'SIMULATED_AI'
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    vehicle_count = Column(Integer, default=0)
    cars = Column(Integer, default=0)
    motorcycles = Column(Integer, default=0)
    buses = Column(Integer, default=0)
    trucks = Column(Integer, default=0)
    movement_score = Column(Float, default=0.0)
    traffic_level = Column(String(20), default="LOW")
    probable_reasons = Column(ARRAY(String))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    bus = relationship("Bus", back_populates="traffic_records")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True, nullable=False)
    bus_id = Column(String(50), ForeignKey("buses.bus_id", ondelete="CASCADE"), nullable=False, index=True)
    incident_type = Column(String(50), default="Potential Collision")
    source_type = Column(String(30), default="LIVE_EDGE_AI")
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default="PENDING_REVIEW")
    description = Column(Text)
    plate_number = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    bus = relationship("Bus", back_populates="incidents")
    media = relationship("Media", back_populates="incident", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    media_type = Column(String(20), nullable=False) # 'IMAGE', 'VIDEO', 'KEYFRAME_PRE', etc.
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    event = relationship("Event", back_populates="media")
    incident = relationship("Incident", back_populates="media")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String(50), ForeignKey("buses.bus_id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(30), default="LIVE_GPS") # 'LIVE_GPS', 'SIMULATED_GPS'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    speed = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    bus = relationship("Bus", back_populates="locations")
