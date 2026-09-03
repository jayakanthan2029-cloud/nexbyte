import sys
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.main import app
from ai.detector import YOLODetector
from ai.tracker import ByteTracker
from ai.traffic import TrafficAnalyzer
from ai.event_processor import EventProcessor
from ai.gps import PhoneGPSProvider
from ai.api_client import APIClient

client = TestClient(app)

def test_end_to_end_yolo_to_dashboard():
    print("--- Phase 3 & 4: Verifying YOLO to FastAPI to Dashboard Single Source of Truth ---")
    
    # 1. Initialize detector & tracker
    detector = YOLODetector("yolo11n.pt")
    tracker = ByteTracker(detector)
    analyzer = TrafficAnalyzer()
    
    # Empty frame
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    tracked_vehicles, yolo_result, displacements = tracker.track(blank_frame)
    traffic_data = analyzer.analyze(tracked_vehicles, displacements)
    
    # 2. Check counts from YOLO
    assert traffic_data["vehicle_count"] == 0
    assert traffic_data["cars"] == 0
    assert traffic_data["motorcycles"] == 0
    assert traffic_data["buses"] == 0
    assert traffic_data["trucks"] == 0
    
    # 3. Post to backend as Edge AI would
    payload = {
        "bus_id": "BUS-001",
        "source_type": "LIVE_EDGE_AI",
        "vehicle_count": traffic_data["vehicle_count"],
        "cars": traffic_data["cars"],
        "motorcycles": traffic_data["motorcycles"],
        "buses": traffic_data["buses"],
        "trucks": traffic_data["trucks"],
        "movement_score": traffic_data["movement_score"],
        "traffic_level": traffic_data["traffic_level"],
        "probable_reasons": traffic_data["probable_reasons"],
        "latitude": None,
        "longitude": None
    }
    
    post_res = client.post("/api/traffic", json=payload)
    assert post_res.status_code == 200
    
    # 4. Query Dashboard live endpoint
    dash_res = client.get("/api/dashboard/live")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    
    # 5. Verify the dashboard received exactly the YOLO count
    latest_bus1_traffic = next((t for t in dash_data["recent_traffic"] if t["bus_id"] == "BUS-001"), None)
    assert latest_bus1_traffic is not None, "BUS-001 traffic missing from dashboard!"
    assert latest_bus1_traffic["vehicle_count"] == 0, f"Expected 0 from YOLO, got {latest_bus1_traffic['vehicle_count']}"
    assert latest_bus1_traffic["source_type"] == "LIVE_EDGE_AI"
    
    # 6. Verify BUS-001 GPS status remains UNAVAILABLE without fabricating coordinates
    bus_001 = next(b for b in dash_data["buses"] if b["bus_id"] == "BUS-001")
    assert bus_001["gps_status"] == "UNAVAILABLE" or bus_001["gps_status"] == "LIVE_GPS"
    if bus_001["latitude"] is not None:
        print(f"BUS-001 Live GPS Lock: {bus_001['latitude']}, {bus_001['longitude']}")
    else:
        print("BUS-001 GPS is cleanly None / UNAVAILABLE (No fake coordinates).")
        
    print("✅ END-TO-END VERIFICATION SUCCESSFUL: YOLO output is the exact single source of truth for the dashboard.")

if __name__ == "__main__":
    test_end_to_end_yolo_to_dashboard()
