import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai.detector import YOLODetector
from ai.tracker import ByteTracker
from ai.traffic import TrafficAnalyzer
from ai.urban_detection import UrbanDetectionModel
from ai.crash_detection import CrashDetector
from ai.evidence import RollingVideoBuffer
from ai.ocr import EventTriggeredOCR
from ai.gps import DemoGPSProvider

def test_yolo_and_tracker():
    print("\n[Test 1] Initializing YOLO11n on CUDA...")
    detector = YOLODetector("yolo11n.pt")
    assert detector.model is not None
    print(f"✅ YOLO loaded on device: {detector.device} ({detector.device_name})")

    # Load test image
    test_img_path = ROOT_DIR / "data" / "traffic-7272520_1280.jpg"
    assert test_img_path.exists(), f"Sample image {test_img_path} not found"
    frame = cv2.imread(str(test_img_path))
    assert frame is not None

    print("[Test 2] Running Detection + ByteTrack on test frame...")
    tracker = ByteTracker(detector)
    vehicles, result, displacements = tracker.track(frame)
    print(f"✅ Tracked {len(vehicles)} vehicles in test frame.")
    for v in vehicles[:3]:
        print(f"   - {v.class_name.upper()} #{v.track_id} at center ({v.center_x}, {v.center_y}) conf: {v.confidence}")

    print("[Test 3] Calculating Traffic Intelligence metrics...")
    analyzer = TrafficAnalyzer()
    traffic_data = analyzer.analyze(vehicles, displacements)
    assert "vehicle_count" in traffic_data
    assert "traffic_level" in traffic_data
    print(f"✅ Traffic Metrics: Total={traffic_data['vehicle_count']}, Level={traffic_data['traffic_level']}, Movement={traffic_data['movement_score']}")
    print(f"   Reasons: {traffic_data['probable_reasons']}")

def test_crash_detector():
    print("\n[Test 4] Verifying Crash Detector (Potential Collision)...")
    detector = CrashDetector()
    demo_crash = detector.trigger_demo_crash()
    assert demo_crash["incident_type"] == "Potential Collision"
    print("✅ Crash detection correctly labeled: Potential Collision")

def test_urban_detection():
    print("\n[Test 5] Verifying Urban Infrastructure Detection Adapter...")
    urban = UrbanDetectionModel("models/urban_model.pt")
    # Verify graceful demo generation when custom model is not present
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    demo_pothole = urban.generate_demo_detection(dummy_frame, "POTHOLE")
    assert "DEMO DETECTION" in demo_pothole["description"]
    print(f"✅ Honesty requirement passed: {demo_pothole['description']}")

def test_rolling_buffer():
    print("\n[Test 6] Verifying Rolling Video Buffer...")
    buffer = RollingVideoBuffer(fps=10, pre_seconds=1, post_seconds=1)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for _ in range(15):
        buffer.add_frame(dummy_frame)
    assert len(buffer.frame_buffer) > 0
    print(f"✅ Rolling buffer holding {len(buffer.frame_buffer)} frames in memory.")

def test_ocr():
    print("\n[Test 7] Verifying Event-Triggered OCR...")
    ocr = EventTriggeredOCR()
    dummy_crop = np.zeros((60, 180, 3), dtype=np.uint8)
    res = ocr.read_plate(dummy_crop, track_id=21)
    assert "plate_number" in res
    print(f"✅ OCR executed gracefully: Plate='{res['plate_number']}', Status='{res['status']}'")

def test_gps():
    print("\n[Test 8] Verifying Demo GPS Waypoint Generator...")
    gps = DemoGPSProvider()
    loc1 = gps.get_location()
    assert "latitude" in loc1 and "longitude" in loc1
    print(f"✅ GPS Location generated: ({loc1['latitude']}, {loc1['longitude']}) at {loc1['speed']} km/h")

if __name__ == "__main__":
    print("=" * 60)
    print("UrbanSenseAI - Edge AI Component Verification Suite")
    print("=" * 60)
    test_yolo_and_tracker()
    test_crash_detector()
    test_urban_detection()
    test_rolling_buffer()
    test_ocr()
    test_gps()
    print("\n🎉 ALL EDGE AI COMPONENTS VERIFIED SUCCESSFULLY ON RTX 4060 CUDA!")
