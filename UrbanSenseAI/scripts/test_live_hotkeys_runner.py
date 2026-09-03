import os
import sys
import time
import cv2
from pathlib import Path

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai.config import ai_config
from ai.camera import CameraManager
from ai.detector import YOLODetector
from ai.tracker import ByteTracker
from ai.traffic import TrafficAnalyzer
from ai.evidence import RollingVideoBuffer
from ai.gps import get_live_gps_provider
from ai.api_client import APIClient
from ai.event_processor import EventProcessor

def run_live_pipeline_test():
    print("============================================================")
    print("Testing Live Edge AI Pipeline with Real Camera & Hotkeys")
    print("============================================================")

    api_client = APIClient("http://localhost:8000/api")
    gps_provider = get_live_gps_provider()
    event_processor = EventProcessor(gps_provider, api_client)

    camera = CameraManager(ai_config.CAMERA_SOURCE, width=1280, height=720)
    detector = YOLODetector(ai_config.YOLO_MODEL_PATH)
    tracker = ByteTracker(detector)
    traffic_analyzer = TrafficAnalyzer()
    rolling_buffer = RollingVideoBuffer(fps=15, pre_seconds=3, post_seconds=4)

    # 1. Capture real frames from live IP camera
    print("[STEP 1] Reading live frames from camera...")
    frames_captured = 0
    test_frame = None

    for _ in range(45): # Capture ~3 seconds of live camera frames
        success, frame = camera.read_frame()
        if success:
            test_frame = frame
            rolling_buffer.add_frame(frame)
            tracked, yolo_result, displacements = tracker.track(frame)
            traffic_data = traffic_analyzer.analyze(tracked, displacements)
            frames_captured += 1
            if frames_captured % 15 == 0:
                print(f"Captured {frames_captured} live frames. Current vehicles: {traffic_data['vehicle_count']}")

    assert test_frame is not None, "Failed to capture any frames from camera!"
    print(f"✅ Successfully captured {frames_captured} real frames from camera ({test_frame.shape})")

    # 2. Simulate Hotkey P (Pothole) on real camera frame
    print("\n[STEP 2] Simulating Hotkey 'P' (Pothole)...")
    h, w = test_frame.shape[:2]
    pothole_frame = test_frame.copy()
    x1, y1 = int(w * 0.35), int(h * 0.65)
    x2, y2 = int(w * 0.65), int(h * 0.85)
    cv2.rectangle(pothole_frame, (x1, y1), (x2, y2), (0, 140, 255), 3)
    cv2.putText(pothole_frame, "DEMO POTHOLE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)
    cv2.putText(pothole_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2)

    pothole_evt = event_processor.process_road_event(
        event_type="POTHOLE",
        frame=pothole_frame,
        confidence=0.92,
        description=f"DEMO EVENT: Road surface defect registered by {ai_config.BUS_ID}",
        source_type="DEMO_EVENT"
    )
    print(f"✅ Dispatched Pothole event. Saved: {pothole_evt['media_files'][0]['file_path']}")

    # 3. Simulate Hotkey W (Waterlogging) on real camera frame
    print("\n[STEP 3] Simulating Hotkey 'W' (Waterlogging)...")
    water_frame = test_frame.copy()
    x1, y1 = int(w * 0.20), int(h * 0.70)
    x2, y2 = int(w * 0.80), int(h * 0.95)
    cv2.rectangle(water_frame, (x1, y1), (x2, y2), (255, 120, 0), 3)
    cv2.putText(water_frame, "DEMO WATERLOGGING", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 120, 0), 2)
    cv2.putText(water_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 120, 0), 2)

    water_evt = event_processor.process_road_event(
        event_type="WATERLOGGING",
        frame=water_frame,
        confidence=0.88,
        description=f"DEMO EVENT: Waterlogging alert registered by {ai_config.BUS_ID}",
        source_type="DEMO_EVENT"
    )
    print(f"✅ Dispatched Waterlogging event. Saved: {water_evt['media_files'][0]['file_path']}")

    # 4. Simulate Hotkey C (Collision) on real camera frame
    print("\n[STEP 4] Simulating Hotkey 'C' (Collision Evidence)...")
    demo_inc_id = f"INC-LIVE-{int(time.time())}"
    demo_crash = {
        "incident_id": demo_inc_id,
        "bus_id": ai_config.BUS_ID,
        "incident_type": "POTENTIAL_COLLISION",
        "source_type": "DEMO_EVENT",
        "description": f"DEMO EVENT: Potential collision workflow triggered on {ai_config.BUS_ID}",
        "confidence": 0.85,
        "plate_number": "TN09CC1234"
    }

    rolling_buffer.trigger_incident(demo_crash, test_frame)
    print("Buffer locked for pre-event frames. Capturing post-event frames...")

    completed_evidence = None
    for i in range(60): # Collect 60 post-frames (~4 seconds)
        success, frame = camera.read_frame()
        if success:
            res = rolling_buffer.add_frame(frame)
            if res:
                completed_evidence = res
                break

    assert completed_evidence is not None, "Collision evidence collection did not complete!"
    print(f"✅ Captured post-event frames. Video path: {completed_evidence['video_path']}")

    event_processor.process_incident(completed_evidence, completed_evidence["media_files"])
    print("✅ Dispatched incident to FastAPI!")

    # 5. Clean release
    camera.release()

    # Wait 2 seconds for worker thread to flush POST requests to FastAPI
    time.sleep(2.5)

    # 6. Verify via FastAPI REST endpoints
    import requests
    print("\n[STEP 5] Verifying FastAPI & PostgreSQL Database persistence...")
    
    events_resp = requests.get("http://localhost:8000/api/events?bus_id=BUS-001")
    assert events_resp.status_code == 200
    events_data = events_resp.json()
    assert len(events_data) >= 2, f"Expected at least 2 events, found {len(events_data)}"
    print(f"✅ Verified {len(events_data)} events found in PostgreSQL for BUS-001!")

    incidents_resp = requests.get("http://localhost:8000/api/incidents")
    assert incidents_resp.status_code == 200
    incidents_data = incidents_resp.json()
    live_inc = next((inc for inc in incidents_data if inc["incident_id"] == demo_inc_id), None)
    assert live_inc is not None, "Live incident not found in database!"
    assert len(live_inc["media"]) >= 4, f"Expected 4 media items in incident, found {len(live_inc['media'])}"
    print(f"✅ Verified Incident {demo_inc_id} persisted in PostgreSQL with {len(live_inc['media'])} media files!")

    print("\n============================================================")
    print("🎉 ALL LIVE CAMERA HOTKEY WORKFLOWS TESTED & PERSISTED!")
    print("============================================================")

if __name__ == "__main__":
    run_live_pipeline_test()
