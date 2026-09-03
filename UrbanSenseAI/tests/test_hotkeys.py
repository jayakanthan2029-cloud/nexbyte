import os
import sys
import time
import cv2
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.main import app
from backend.database import SessionLocal
from backend import models
from ai.config import ai_config
from ai.gps import get_live_gps_provider
from ai.api_client import APIClient
from ai.event_processor import EventProcessor
from ai.evidence import RollingVideoBuffer

client = TestClient(app)

def test_hotkey_p_pothole():
    print("\n--- Testing Hotkey P (Demo Pothole Event) ---")
    gps = get_live_gps_provider()
    api = APIClient()
    processor = EventProcessor(gps, api)

    # 1. Create a test frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    h, w = frame.shape[:2]

    # 2. Annotate as P would
    pothole_frame = frame.copy()
    x1, y1 = int(w * 0.35), int(h * 0.65)
    x2, y2 = int(w * 0.65), int(h * 0.85)
    cv2.rectangle(pothole_frame, (x1, y1), (x2, y2), (0, 140, 255), 3)
    cv2.putText(pothole_frame, "DEMO POTHOLE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)
    cv2.putText(pothole_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2)

    # 3. Process road event
    evt_payload = processor.process_road_event(
        event_type="POTHOLE",
        frame=pothole_frame,
        confidence=0.92,
        description="DEMO EVENT: Road surface pothole registered by BUS-001",
        source_type="DEMO_EVENT"
    )

    # 4. Verify file saved on disk
    saved_file = Path(ROOT_DIR) / evt_payload["media_files"][0]["file_path"]
    assert saved_file.exists(), f"Image file not found at {saved_file}"
    assert saved_file.stat().st_size > 0, "Saved image file is empty!"
    print(f"✅ Verified image saved on disk: {saved_file.name} ({saved_file.stat().st_size} bytes)")

    # 5. Send directly to FastAPI endpoint
    resp = client.post("/api/events", json=evt_payload)
    assert resp.status_code == 200, f"Failed to post event: {resp.text}"
    created_id = resp.json()["id"]

    # 6. Verify PostgreSQL database row
    db = SessionLocal()
    try:
        db_evt = db.query(models.Event).filter(models.Event.id == created_id).first()
        assert db_evt is not None, "PostgreSQL Event row was not created!"
        assert db_evt.bus_id == "BUS-001"
        assert db_evt.source_type == "DEMO_EVENT"
        assert len(db_evt.media) > 0, "PostgreSQL Media entry was not linked!"
        print(f"✅ Verified PostgreSQL event ID {db_evt.id} created with media ID {db_evt.media[0].id}")
    finally:
        db.close()

def test_hotkey_w_waterlogging():
    print("\n--- Testing Hotkey W (Demo Waterlogging Event) ---")
    gps = get_live_gps_provider()
    api = APIClient()
    processor = EventProcessor(gps, api)

    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    h, w = frame.shape[:2]

    # Annotate as W would
    water_frame = frame.copy()
    x1, y1 = int(w * 0.20), int(h * 0.70)
    x2, y2 = int(w * 0.80), int(h * 0.95)
    cv2.rectangle(water_frame, (x1, y1), (x2, y2), (255, 120, 0), 3)
    cv2.putText(water_frame, "DEMO WATERLOGGING", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 120, 0), 2)
    cv2.putText(water_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 120, 0), 2)

    evt_payload = processor.process_road_event(
        event_type="WATERLOGGING",
        frame=water_frame,
        confidence=0.88,
        description="DEMO EVENT: Waterlogging alert registered by BUS-001",
        source_type="DEMO_EVENT"
    )

    saved_file = Path(ROOT_DIR) / evt_payload["media_files"][0]["file_path"]
    assert saved_file.exists(), f"Image file not found at {saved_file}"
    assert saved_file.stat().st_size > 0, "Saved image file is empty!"
    print(f"✅ Verified image saved on disk: {saved_file.name} ({saved_file.stat().st_size} bytes)")

    resp = client.post("/api/events", json=evt_payload)
    assert resp.status_code == 200, f"Failed to post event: {resp.text}"
    created_id = resp.json()["id"]

    db = SessionLocal()
    try:
        db_evt = db.query(models.Event).filter(models.Event.id == created_id).first()
        assert db_evt is not None, "PostgreSQL Event row was not created!"
        assert db_evt.bus_id == "BUS-001"
        assert db_evt.source_type == "DEMO_EVENT"
        assert len(db_evt.media) > 0, "PostgreSQL Media entry was not linked!"
        print(f"✅ Verified PostgreSQL event ID {db_evt.id} created with media ID {db_evt.media[0].id}")
    finally:
        db.close()

def test_hotkey_c_collision():
    print("\n--- Testing Hotkey C (Potential Collision Evidence Workflow) ---")
    gps = get_live_gps_provider()
    api = APIClient()
    processor = EventProcessor(gps, api)

    # Use 15 fps buffer with short cycle for testing (15 pre-frames, 15 post-frames)
    buffer = RollingVideoBuffer(fps=15, pre_seconds=1, post_seconds=1)

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Fill pre-event buffer
    for _ in range(15):
        buffer.add_frame(frame)

    # Trigger incident as C would
    demo_inc_id = f"INC-TEST-{int(time.time())}"
    demo_crash = {
        "incident_id": demo_inc_id,
        "bus_id": "BUS-001",
        "incident_type": "POTENTIAL_COLLISION",
        "source_type": "DEMO_EVENT",
        "description": "DEMO EVENT: Potential collision workflow triggered on BUS-001",
        "confidence": 0.85,
        "plate_number": "TN09CC1234"
    }

    buffer.trigger_incident(demo_crash, frame)
    assert buffer.is_recording_incident is True

    # Feed post-event frames
    completed_evidence = None
    for _ in range(15):
        completed_evidence = buffer.add_frame(frame)

    assert completed_evidence is not None, "Evidence collection did not complete!"
    assert completed_evidence["incident_id"] == demo_inc_id

    # Post to backend
    resp = client.post("/api/incidents", json=completed_evidence)
    assert resp.status_code == 200, f"Failed to post incident: {resp.text}"

    time.sleep(1.0)

    # Verify MP4 and keyframe files exist on disk
    video_path = Path(ROOT_DIR) / completed_evidence["video_path"]
    assert video_path.exists(), f"MP4 video not found at {video_path}"
    assert video_path.stat().st_size > 0, "MP4 video is empty!"
    print(f"✅ Verified MP4 video saved on disk: {video_path.name} ({video_path.stat().st_size} bytes)")

    for kf in completed_evidence["media_files"]:
        kf_path = Path(ROOT_DIR) / kf["file_path"]
        assert kf_path.exists(), f"Keyframe not found at {kf_path}"
        assert kf_path.stat().st_size > 0, f"Keyframe {kf_path.name} is empty!"
    print(f"✅ Verified all 3 keyframes saved on disk.")

    # Verify PostgreSQL database row
    db = SessionLocal()
    try:
        db_inc = db.query(models.Incident).filter(
            models.Incident.incident_id == demo_inc_id
        ).first()

        assert db_inc is not None, "PostgreSQL Incident row was not created!"
        assert db_inc.incident_type == "POTENTIAL_COLLISION"
        assert db_inc.source_type == "DEMO_EVENT"
        assert len(db_inc.media) == 4, f"Expected 4 media items (1 video + 3 keyframes), got {len(db_inc.media)}"
        print(f"✅ Verified PostgreSQL incident ID {db_inc.incident_id} created with 4 media records.")
    finally:
        db.close()

if __name__ == "__main__":
    print("============================================================")
    print("UrbanSenseAI - Hotkey Workflow End-to-End Test Suite")
    print("============================================================")
    test_hotkey_p_pothole()
    test_hotkey_w_waterlogging()
    test_hotkey_c_collision()
    print("\n============================================================")
    print("🎉 ALL HOTKEY WORKFLOW TESTS PASSED!")
    print("============================================================")
