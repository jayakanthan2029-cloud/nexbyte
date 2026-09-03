import os
import sys
import time
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai.config import ai_config
from ai.logger import logger
from ai.camera import CameraManager
from ai.detector import YOLODetector
from ai.tracker import ByteTracker
from ai.traffic import TrafficAnalyzer
from ai.urban_detection import UrbanDetectionModel
from ai.crash_detection import CrashDetector
from ai.evidence import RollingVideoBuffer
from ai.ocr import EventTriggeredOCR
from ai.gps import get_live_gps_provider
from ai.api_client import APIClient
from ai.event_processor import EventProcessor

def main():
    # 1. Initialize API Client & Physical GPS Provider
    api_client = APIClient(ai_config.API_BASE_URL)
    gps_provider = get_live_gps_provider()
    event_processor = EventProcessor(gps_provider, api_client)

    # 2. Initialize Camera & AI Detector
    camera = CameraManager(
        source=ai_config.CAMERA_SOURCE,
        width=ai_config.CAMERA_WIDTH,
        height=ai_config.CAMERA_HEIGHT
    )
    yolo_detector = YOLODetector(ai_config.YOLO_MODEL_PATH)
    tracker = ByteTracker(yolo_detector)
    traffic_analyzer = TrafficAnalyzer()
    urban_detector = UrbanDetectionModel(ai_config.URBAN_MODEL_PATH)
    crash_detector = CrashDetector(iou_threshold=ai_config.IOU_THRESHOLD)
    rolling_buffer = RollingVideoBuffer(fps=15, pre_seconds=10, post_seconds=15)
    ocr_engine = EventTriggeredOCR()

    # Initial GPS check
    initial_loc = gps_provider.get_location()
    gps_display = "PHONE GPS" if initial_loc.get("status") == "LIVE_GPS" else "UNAVAILABLE"

    # Startup Truthfulness Banner
    print("========================================", flush=True)
    print("UrbanSenseAI Edge Node", flush=True)
    print(f"BUS ID: {ai_config.BUS_ID}", flush=True)
    print("MODE: LIVE", flush=True)
    print("CAMERA: IP CAMERA", flush=True)
    print("AI: YOLO11n", flush=True)
    print("TRACKER: ByteTrack", flush=True)
    print(f"GPU: {yolo_detector.device_name}", flush=True)
    print(f"GPS: {gps_display}", flush=True)
    print("========================================", flush=True)

    print("[HOTKEY INSTRUCTIONS]", flush=True)
    print("Focus the OpenCV window and press:", flush=True)
    print("  [Q] -> Clean Quit", flush=True)
    print("  [P] -> Trigger Demo Pothole Event", flush=True)
    print("  [W] -> Trigger Demo Waterlogging Event", flush=True)
    print("  [C] -> Trigger Potential Collision Evidence Workflow", flush=True)
    print("----------------------------------------", flush=True)

    last_telemetry_time = 0.0
    last_heartbeat_time = 0.0
    telemetry_interval = 2.0
    heartbeat_interval = 5.0

    # HUD notification banner state
    hud_message = None
    hud_message_color = (0, 255, 0)
    hud_message_expires = 0.0

    window_name = "UrbanSenseAI - Edge AI Intelligence (RTX 4060)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    try:
        while True:
            # 1. Capture Real Frame
            success, frame = camera.read_frame()

            # Check live GPS status
            current_loc = gps_provider.get_location()
            current_gps_status = current_loc.get("status", "UNAVAILABLE")

            # Standby frame if camera disconnected
            if not success:
                cv2.imshow(window_name, frame)
                now = time.time()
                if now - last_heartbeat_time > heartbeat_interval:
                    api_client.send_heartbeat(
                        ai_engine="running",
                        camera="disconnected",
                        gps=current_gps_status
                    )
                    last_heartbeat_time = now

                key = cv2.waitKey(50) & 0xFF
                if key in (ord("q"), ord("Q"), 27):
                    print("[HOTKEY] Q -> QUIT", flush=True)
                    break
                continue

            h, w = frame.shape[:2]

            # Feed frame to rolling video buffer
            incident_completed_evidence = rolling_buffer.add_frame(frame)
            if incident_completed_evidence:
                print(f"[HOTKEY] C -> Evidence complete! Dispatching incident {incident_completed_evidence['incident_id']}...", flush=True)
                event_processor.process_incident(
                    incident_data=incident_completed_evidence,
                    media_files=incident_completed_evidence["media_files"]
                )
                hud_message = "EVIDENCE SAVED - ~25 SEC VIDEO & KEYFRAMES"
                hud_message_color = (0, 255, 0)
                hud_message_expires = time.time() + 5.0

            # 2. Real Vehicle Detection & ByteTrack
            tracked_vehicles, yolo_result, displacements = tracker.track(frame)

            # 3. Real Traffic Analysis (Calculated directly from actual YOLO detections)
            traffic_data = traffic_analyzer.analyze(tracked_vehicles, displacements)

            # 4. Check Autonomous Collisions (Geometric IoU)
            potential_crash = crash_detector.check_collisions(tracked_vehicles)
            if potential_crash:
                logger.warning("Potential Collision detected by IoU algorithm!")
                rolling_buffer.trigger_incident(potential_crash, frame)
                if potential_crash.get("vehicles_involved"):
                    first_v = potential_crash["vehicles_involved"][0]
                    crop = ocr_engine.crop_candidate_plate(frame, first_v["bbox"])
                    plate_res = ocr_engine.read_plate(crop, first_v["track_id"])
                    potential_crash["plate_number"] = plate_res.get("plate_number")

            # 5. Check Custom Urban Infrastructure (if custom model exists)
            if urban_detector.is_custom_model_available:
                urban_detections = urban_detector.detect(frame)
                for ud in urban_detections:
                    event_processor.process_road_event(
                        event_type=ud["class_name"].upper(),
                        frame=frame,
                        confidence=ud["confidence"],
                        description=f"Road infrastructure alert: {ud['class_name']}",
                        source_type="LIVE_EDGE_AI"
                    )

            # 6. Annotate Visual Frame with Real Detections
            annotated_frame = yolo_result.plot()

            # Draw Persistent Track IDs on vehicles
            for v in tracked_vehicles:
                x1, y1, x2, y2 = v.bbox
                label = f"{v.class_name.upper()} #{v.track_id}"
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    2
                )

            # Draw Bottom Telemetry HUD panel
            annotated_frame = traffic_analyzer.draw_hud(
                annotated_frame,
                traffic_data,
                fps=camera.fps,
                gpu_name=yolo_detector.device_name
            )

            # GPS Status Badge in HUD top-left
            gps_color = (0, 255, 0) if current_gps_status == "LIVE_GPS" else (0, 165, 255)
            cv2.putText(
                annotated_frame,
                f"GPS: {current_gps_status}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                gps_color,
                2
            )

            # Prominent HUD Banners
            now = time.time()
            if rolling_buffer.is_recording_incident:
                rec_w = 560
                rec_x = max(10, (w - rec_w) // 2)
                remaining_sec = max(0, int((rolling_buffer.post_buffer_size - len(rolling_buffer.post_frames_collected)) / rolling_buffer.fps))
                cv2.rectangle(annotated_frame, (rec_x, 15), (rec_x + rec_w, 65), (0, 0, 0), -1)
                cv2.rectangle(annotated_frame, (rec_x, 15), (rec_x + rec_w, 65), (0, 0, 255), 2)
                cv2.circle(annotated_frame, (rec_x + 25, 40), 10, (0, 0, 255), -1)
                cv2.putText(
                    annotated_frame,
                    f"POTENTIAL COLLISION - EVIDENCE CAPTURE ACTIVE (REC {remaining_sec}s)",
                    (rec_x + 45, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2
                )
            elif hud_message and now < hud_message_expires:
                msg_w = 480
                msg_x = max(10, (w - msg_w) // 2)
                cv2.rectangle(annotated_frame, (msg_x, 15), (msg_x + msg_w, 65), (0, 0, 0), -1)
                cv2.rectangle(annotated_frame, (msg_x, 15), (msg_x + msg_w, 65), hud_message_color, 2)
                cv2.putText(
                    annotated_frame,
                    hud_message,
                    (msg_x + 20, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    hud_message_color,
                    2
                )

            # 7. Periodic Telemetry Dispatch (Strictly Real YOLO Data)
            if now - last_telemetry_time >= telemetry_interval:
                event_processor.process_traffic_update(traffic_data)
                last_telemetry_time = now

            if now - last_heartbeat_time >= heartbeat_interval:
                api_client.send_heartbeat(
                    ai_engine="running",
                    camera="connected",
                    gps=current_gps_status
                )
                last_heartbeat_time = now

            # 8. Display Edge Output Window
            cv2.imshow(window_name, annotated_frame)

            # 9. Keyboard Hotkeys (Supports both uppercase and lowercase)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q"), 27):
                print("[HOTKEY] Q -> QUIT", flush=True)
                break

            elif key in (ord("p"), ord("P")):
                print("[HOTKEY] P -> DEMO POTHOLE", flush=True)
                pothole_frame = frame.copy()
                # Visually annotate the captured frame
                x1, y1 = int(w * 0.35), int(h * 0.65)
                x2, y2 = int(w * 0.65), int(h * 0.85)
                cv2.rectangle(pothole_frame, (x1, y1), (x2, y2), (0, 140, 255), 3)
                cv2.putText(pothole_frame, "DEMO POTHOLE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)
                cv2.putText(pothole_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2)

                event_processor.process_road_event(
                    event_type="POTHOLE",
                    frame=pothole_frame,
                    confidence=0.92,
                    description=f"DEMO EVENT: Road surface pothole registered by {ai_config.BUS_ID}",
                    source_type="DEMO_EVENT"
                )

                hud_message = "DEMO POTHOLE EVENT SENT"
                hud_message_color = (0, 165, 255)
                hud_message_expires = time.time() + 4.0

            elif key in (ord("w"), ord("W")):
                print("[HOTKEY] W -> DEMO WATERLOGGING", flush=True)
                water_frame = frame.copy()
                # Visually annotate the captured frame
                x1, y1 = int(w * 0.20), int(h * 0.70)
                x2, y2 = int(w * 0.80), int(h * 0.95)
                cv2.rectangle(water_frame, (x1, y1), (x2, y2), (255, 120, 0), 3)
                cv2.putText(water_frame, "DEMO WATERLOGGING", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 120, 0), 2)
                cv2.putText(water_frame, "MANUAL DEMO EVENT", (x1, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 120, 0), 2)

                event_processor.process_road_event(
                    event_type="WATERLOGGING",
                    frame=water_frame,
                    confidence=0.88,
                    description=f"DEMO EVENT: Waterlogging alert registered by {ai_config.BUS_ID}",
                    source_type="DEMO_EVENT"
                )

                hud_message = "DEMO WATERLOGGING EVENT SENT"
                hud_message_color = (255, 120, 0)
                hud_message_expires = time.time() + 4.0

            elif key in (ord("c"), ord("C")):
                print("[HOTKEY] C -> POTENTIAL COLLISION", flush=True)
                demo_inc_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                demo_crash = {
                    "incident_id": demo_inc_id,
                    "bus_id": ai_config.BUS_ID,
                    "incident_type": "POTENTIAL_COLLISION",
                    "source_type": "DEMO_EVENT",
                    "description": f"DEMO EVENT: Potential collision workflow triggered on {ai_config.BUS_ID}",
                    "confidence": 0.85,
                    "plate_number": "TN09CC1234"
                }

                rolling_buffer.trigger_incident(demo_crash, frame)

                hud_message = "POTENTIAL COLLISION - EVIDENCE CAPTURE ACTIVE"
                hud_message_color = (0, 0, 255)
                hud_message_expires = time.time() + 3.0

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error in edge loop: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        logger.success("Edge AI Engine shut down cleanly.")

if __name__ == "__main__":
    main()
