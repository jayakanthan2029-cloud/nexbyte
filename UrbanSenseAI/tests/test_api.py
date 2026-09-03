import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "UrbanSenseAI"
    print("✅ Root endpoint passed")

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] == "online"
    assert data["database"] == "connected"
    print("✅ Healthcheck endpoint passed")

def test_buses():
    response = client.get("/api/buses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    # Verify BUS-001 is LIVE (is_simulated == False)
    bus_001 = next(b for b in data if b["bus_id"] == "BUS-001")
    assert bus_001["is_simulated"] is False
    # Verify BUS-002 is SIMULATED (is_simulated == True)
    bus_002 = next(b for b in data if b["bus_id"] == "BUS-002")
    assert bus_002["is_simulated"] is True
    print("✅ Buses endpoint and LIVE/SIMULATED distinction passed")

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["active_buses"] >= 5
    print("✅ Dashboard summary endpoint passed")

def test_post_and_get_traffic():
    payload = {
        "bus_id": "BUS-001",
        "vehicle_count": 18,
        "cars": 10,
        "motorcycles": 5,
        "buses": 2,
        "trucks": 1,
        "movement_score": 0.22,
        "traffic_level": "MEDIUM",
        "probable_reasons": ["Moderate vehicle density", "Slow speed"],
        "latitude": 13.0827,
        "longitude": 80.2707
    }
    response = client.post("/api/traffic", json=payload)
    assert response.status_code == 200
    print("✅ Traffic record creation passed")

    get_resp = client.get("/api/traffic?bus_id=BUS-001")
    assert get_resp.status_code == 200
    assert len(get_resp.json()) >= 1
    print("✅ Traffic records query passed")

def test_post_and_get_event():
    payload = {
        "bus_id": "BUS-001",
        "event_type": "POTHOLE",
        "latitude": 13.0830,
        "longitude": 80.2710,
        "confidence": 0.88,
        "description": "DEMO DETECTION: Simulated pothole on Anna Salai",
        "status": "NEW"
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "POTHOLE"
    print("✅ Event creation passed")

def test_post_and_get_incident():
    payload = {
        "bus_id": "BUS-001",
        "incident_type": "Potential Collision",
        "latitude": 13.0835,
        "longitude": 80.2715,
        "confidence": 0.75,
        "status": "PENDING_REVIEW",
        "description": "Potential Collision detected between Track #14 (car) and Track #19 (bike)",
        "plate_number": "TN09CC1234"
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["incident_type"] == "Potential Collision"
    print("✅ Incident creation passed")

if __name__ == "__main__":
    print("\n--- Running Backend API Verification Tests ---")
    test_api_root()
    test_health()
    test_buses()
    test_dashboard_summary()
    test_post_and_get_traffic()
    test_post_and_get_event()
    test_post_and_get_incident()
    print("\n🎉 ALL BACKEND API TESTS PASSED SUCCESSFULLY!")
