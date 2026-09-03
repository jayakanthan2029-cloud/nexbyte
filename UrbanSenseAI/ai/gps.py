from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
import requests
from datetime import datetime
from ai.config import ai_config
from ai.logger import logger

class GPSProvider(ABC):
    @abstractmethod
    def get_location(self) -> Dict[str, Any]:
        pass

class PhoneGPSProvider(GPSProvider):
    """
    Physical Phone GPS Provider.
    Queries the Android phone running the IP Camera app via HTTP (/gps.json or /sensors.json).
    Strict Truthfulness Rule:
    If phone GPS cannot be obtained, reports status='UNAVAILABLE' and latitude=None, longitude=None.
    NEVER silently falls back to fake moving coordinates.
    """
    def __init__(self, camera_source: str = None, timeout: float = 2.0):
        self.camera_source = camera_source or ai_config.CAMERA_SOURCE
        self.timeout = timeout
        self.last_valid_location: Optional[Dict[str, Any]] = None
        self.last_attempt_time = 0.0
        self.query_interval = 2.0 # Query phone GPS every 2 seconds
        self.status = "UNAVAILABLE"
        self.gps_url = self._resolve_gps_url(self.camera_source)

    def _resolve_gps_url(self, source: str) -> Optional[str]:
        if isinstance(source, str) and source.startswith("http"):
            parts = source.split("/")
            # e.g., http://10.54.205.62:8080/video -> http://10.54.205.62:8080/gps.json
            base = "/".join(parts[:3])
            return f"{base}/gps.json"
        return None

    def get_location(self) -> Dict[str, Any]:
        now = time.time()
        
        # Throttle HTTP calls
        if now - self.last_attempt_time < self.query_interval and self.last_valid_location:
            return self.last_valid_location

        self.last_attempt_time = now

        if not self.gps_url:
            self.status = "UNAVAILABLE"
            return {
                "status": "UNAVAILABLE",
                "source_type": "LIVE_GPS",
                "latitude": None,
                "longitude": None,
                "accuracy": None,
                "speed": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Camera source is not an HTTP IP stream"
            }

        try:
            r = requests.get(self.gps_url, timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                
                # Check for IP Webcam GPS structure
                # Format 1: {"gps": {"latitude": ..., "longitude": ..., "accuracy": ...}}
                # Format 2: {"latitude": ..., "longitude": ...}
                gps_obj = data.get("gps", data)
                lat = gps_obj.get("latitude")
                lon = gps_obj.get("longitude")
                acc = gps_obj.get("accuracy")
                spd = gps_obj.get("speed", 0.0)

                if lat is not None and lon is not None and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    self.status = "LIVE_GPS"
                    loc = {
                        "status": "LIVE_GPS",
                        "source_type": "LIVE_GPS",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "accuracy": float(acc) if acc is not None else None,
                        "speed": float(spd) if spd is not None else 0.0,
                        "timestamp": datetime.utcnow().isoformat(),
                        "note": "Physical Phone GPS Locked"
                    }
                    self.last_valid_location = loc
                    return loc

        except Exception:
            pass

        # If phone returned {} (GPS logging disabled in app) or request timed out
        self.status = "UNAVAILABLE"
        if self.last_valid_location:
            cached = dict(self.last_valid_location)
            cached["status"] = "UNAVAILABLE"
            cached["note"] = "GPS signal lost; displaying last known real fix"
            return cached

        return {
            "status": "UNAVAILABLE",
            "source_type": "LIVE_GPS",
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "speed": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Phone GPS unavailable. (Enable 'Include GPS' in IP Webcam app)"
        }

class StaticGPSProvider(GPSProvider):
    """Fixed GPS coordinate for real static edge testing."""
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def get_location(self) -> Dict[str, Any]:
        return {
            "status": "STATIC_GPS",
            "source_type": "STATIC_GPS",
            "latitude": self.lat,
            "longitude": self.lon,
            "accuracy": 5.0,
            "speed": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Configured Static Real Coordinate"
        }

class DemoGPSProvider(GPSProvider):
    """
    Reserved exclusively for SIMULATED fleet buses (BUS-002 through BUS-005).
    NEVER used for physical prototype BUS-001 in LIVE mode.
    """
    WAYPOINTS = [
        (13.0878, 80.2871), (13.0827, 80.2707), (13.0674, 80.2608),
        (13.0512, 80.2490), (13.0381, 80.2378), (13.0210, 80.2225)
    ]

    def __init__(self, speed_kmh: float = 24.0):
        self.waypoints = self.WAYPOINTS
        self.current_idx = 0
        self.progress = 0.0
        self.speed_kmh = speed_kmh
        self.last_update_time = time.time()
        self.direction = 1

    def get_location(self) -> Dict[str, Any]:
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        step = (self.speed_kmh / 3600.0) * dt * 0.08
        self.progress += step

        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_idx = (self.current_idx + 1) % (len(self.waypoints) - 1)

        lat1, lon1 = self.waypoints[self.current_idx]
        lat2, lon2 = self.waypoints[self.current_idx + 1]

        curr_lat = lat1 + (lat2 - lat1) * self.progress
        curr_lon = lon1 + (lon2 - lon1) * self.progress

        return {
            "status": "SIMULATED",
            "source_type": "SIMULATED_GPS",
            "latitude": round(curr_lat, 6),
            "longitude": round(curr_lon, 6),
            "accuracy": None,
            "speed": round(self.speed_kmh, 1),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Simulated GPS Waypoints"
        }

def get_live_gps_provider() -> GPSProvider:
    """Factory for BUS-001 Live Node. Never returns DemoGPSProvider."""
    mode = ai_config.GPS_MODE.lower()
    if mode == "static":
        return StaticGPSProvider(ai_config.DEFAULT_LATITUDE, ai_config.DEFAULT_LONGITUDE)
    # Default to physical PhoneGPSProvider
    return PhoneGPSProvider(ai_config.CAMERA_SOURCE)
