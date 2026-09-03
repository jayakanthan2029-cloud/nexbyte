import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np
from ai.config import ai_config, BASE_DIR
from ai.gps import GPSProvider
from ai.api_client import APIClient
from ai.logger import logger

class EventProcessor:
    """
    Standardizes edge detections and manual demo events into unified schemas,
    attaches real GPS fixes, saves media evidence, and dispatches to FastAPI.
    """
    def __init__(self, gps_provider: GPSProvider, api_client: APIClient):
        self.gps = gps_provider
        self.api = api_client
        self.bus_id = ai_config.BUS_ID

        # Ensure media directories exist
        self.media_root = (BASE_DIR / ai_config.MEDIA_DIR).resolve()
        for sub in ["potholes", "waterlogging", "road_hazards", "incidents", "plates", "traffic", "general"]:
            (self.media_root / sub).mkdir(parents=True, exist_ok=True)

    def process_road_event(
        self,
        event_type: str,
        frame: np.ndarray,
        confidence: float = 0.88,
        description: str = None,
        source_type: str = "DEMO_EVENT"
    ) -> Dict[str, Any]:
        loc = self.gps.get_location()
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        folder_name = "potholes" if event_type == "POTHOLE" else (
            "waterlogging" if event_type == "WATERLOGGING" else "road_hazards"
        )
        prefix = "pothole" if event_type == "POTHOLE" else (
            "waterlogging" if event_type == "WATERLOGGING" else "hazard"
        )

        filename = f"{prefix}_{timestamp_str}.jpg"
        file_path = self.media_root / folder_name / filename
        cv2.imwrite(str(file_path), frame)

        relative_path = f"{ai_config.MEDIA_DIR}/{folder_name}/{filename}"
        desc = description or f"DEMO EVENT: {event_type} registered by {self.bus_id}"

        event_payload = {
            "bus_id": self.bus_id,
            "event_type": event_type,
            "source_type": source_type,
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude"),
            "confidence": round(confidence, 2),
            "description": desc,
            "status": "NEW",
            "media_files": [
                {
                    "media_type": "IMAGE",
                    "file_path": relative_path,
                    "file_name": filename
                }
            ]
        }

        self.api.send_event(event_payload)
        logger.event(event_type, f"{desc} | Image: {relative_path}")
        return event_payload

    def process_traffic_update(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches real YOLO11n + ByteTrack traffic analysis with strict provenance.
        """
        loc = self.gps.get_location()

        payload = {
            "bus_id": self.bus_id,
            "source_type": "LIVE_EDGE_AI",
            "vehicle_count": traffic_data["vehicle_count"],
            "cars": traffic_data["cars"],
            "motorcycles": traffic_data["motorcycles"],
            "buses": traffic_data["buses"],
            "trucks": traffic_data["trucks"],
            "movement_score": traffic_data["movement_score"],
            "traffic_level": traffic_data["traffic_level"],
            "probable_reasons": traffic_data["probable_reasons"],
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude"),
            "timestamp": loc.get("timestamp", datetime.utcnow().isoformat())
        }

        self.api.send_traffic(payload)

        # Dispatch location breadcrumb ONLY when a real GPS fix exists
        if loc.get("latitude") is not None and loc.get("longitude") is not None:
            self.api.send_location(
                bus_id=self.bus_id,
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                speed=loc.get("speed", 0.0),
                source_type="LIVE_GPS",
                accuracy=loc.get("accuracy")
            )

        return payload

    def process_incident(
        self,
        incident_data: Dict[str, Any],
        media_files: list,
        plate_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        loc = self.gps.get_location()
        plate_str = plate_info.get("plate_number") if plate_info else incident_data.get("plate_number")

        payload = {
            "incident_id": incident_data.get("incident_id"),
            "bus_id": incident_data.get("bus_id", self.bus_id),
            "incident_type": incident_data.get("incident_type", "POTENTIAL_COLLISION"),
            "source_type": incident_data.get("source_type", "DEMO_EVENT"),
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude"),
            "confidence": incident_data.get("confidence", 0.85),
            "status": "PENDING_REVIEW",
            "description": incident_data.get("description", "Potential Collision Detected"),
            "plate_number": plate_str,
            "media_files": media_files
        }

        self.api.send_incident(payload)
        logger.event("INCIDENT", f"{payload['incident_type']} logged with {len(media_files)} evidence files")
        return payload
