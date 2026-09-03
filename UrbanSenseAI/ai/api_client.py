import json
import threading
from queue import Queue
from typing import Dict, Any, Optional
import requests
from ai.config import ai_config
from ai.logger import logger

class APIClient:
    """
    Non-blocking HTTP client for edge-to-cloud communication.
    Queues messages and dispatches in background threads with robust error logging.
    """
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or ai_config.API_BASE_URL).rstrip("/")
        self.queue = Queue(maxsize=200)
        self.is_running = True

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        while self.is_running:
            try:
                endpoint, payload, method = self.queue.get(timeout=1.0)
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                try:
                    if method == "POST":
                        r = requests.post(url, json=payload, timeout=5.0)
                        if r.status_code >= 400:
                            logger.error(f"[API ERROR] POST {url} returned HTTP {r.status_code}: {r.text}")
                        else:
                            logger.info(f"[API CLIENT] POST {url} succeeded (HTTP {r.status_code})")
                    elif method == "GET":
                        r = requests.get(url, timeout=5.0)
                except requests.RequestException as e:
                    logger.warning(f"[API CLIENT] Connection error to {url}: {e}")
                finally:
                    self.queue.task_done()
            except Exception:
                continue

    def post_async(self, endpoint: str, payload: Dict[str, Any]):
        """Queue a POST request without blocking the camera loop."""
        if not self.queue.full():
            self.queue.put((endpoint, payload, "POST"))
        else:
            logger.warning(f"[API CLIENT] Queue full, dropping payload for {endpoint}")

    def send_heartbeat(self, ai_engine: str, camera: str, gps: str):
        payload = {
            "ai_engine": ai_engine,
            "camera": camera,
            "gps": gps
        }
        self.post_async("health/heartbeat", payload)

    def send_location(
        self,
        bus_id: str,
        latitude: float,
        longitude: float,
        speed: float = 0.0,
        source_type: str = "LIVE_GPS",
        accuracy: Optional[float] = None
    ):
        payload = {
            "bus_id": bus_id,
            "source_type": source_type,
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "accuracy": accuracy
        }
        self.post_async("locations", payload)

    def send_traffic(self, traffic_payload: Dict[str, Any]):
        self.post_async("traffic", traffic_payload)

    def send_event(self, event_payload: Dict[str, Any]):
        self.post_async("events", event_payload)

    def send_incident(self, incident_payload: Dict[str, Any]):
        self.post_async("incidents", incident_payload)
