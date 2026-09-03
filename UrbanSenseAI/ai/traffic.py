import os
import cv2
from ultralytics import YOLO
from collections import Counter
from ai.traffic_reason import analyze_traffic

# ============================================================
# REUSABLE TRAFFIC ANALYZER CLASS (For ai/main.py and adapters)
# ============================================================

VEHICLES = {
    "car",
    "motorcycle",
    "bus",
    "truck"
}

class TrafficAnalyzer:
    """
    Core traffic intelligence processor.
    Calculates vehicle density, modal split, movement score, traffic level, and probable causes.
    """
    def __init__(self):
        self.movement_history = []

    def analyze(self, tracked_vehicles, movement_displacements=None) -> dict:
        counts = Counter()
        for v in tracked_vehicles:
            counts[v.class_name] += 1

        total = sum(counts.values())

        # Calculate movement score (normalized average movement)
        if movement_displacements and len(movement_displacements) > 0:
            avg_disp = sum(movement_displacements.values()) / len(movement_displacements)
            # Normalize displacement score (e.g. 0 to 1.0)
            norm_movement = min(1.0, round(avg_disp / 30.0, 2))
        else:
            norm_movement = 0.5 if total < 5 else 0.2

        # Traffic Level determination
        if total >= 20:
            traffic_level = "HIGH" if norm_movement < 0.35 else "MEDIUM"
        elif total >= 10:
            traffic_level = "MEDIUM"
        else:
            traffic_level = "LOW"

        if total >= 30 and norm_movement < 0.15:
            traffic_level = "CRITICAL"

        # Determine reasons using existing traffic_reason logic
        reasons_data = analyze_traffic(
            vehicle_count=total,
            average_movement=norm_movement
        )

        return {
            "vehicle_count": total,
            "cars": counts["car"],
            "motorcycles": counts["motorcycle"],
            "buses": counts["bus"],
            "trucks": counts["truck"],
            "movement_score": norm_movement,
            "traffic_level": traffic_level,
            "probable_reasons": reasons_data.get("reasons", ["No significant cause detected"])
        }

    def draw_hud(self, frame, traffic_data: dict, fps: float = 0.0, gpu_name: str = "RTX 4060"):
        """Draws the bottom telemetry HUD panel matching original styling."""
        h, w = frame.shape[:2]
        panel_height = 120

        # Semi-transparent bottom rectangle
        cv2.rectangle(
            frame,
            (0, h - panel_height),
            (w, h),
            (20, 20, 20),
            -1
        )

        traffic_level = traffic_data.get("traffic_level", "LOW")
        if traffic_level in ["HIGH", "CRITICAL"]:
            traffic_color = (0, 0, 255) # Red
        elif traffic_level == "MEDIUM":
            traffic_color = (0, 165, 255) # Amber
        else:
            traffic_color = (0, 255, 0) # Green

        # Line 1: Vehicle breakdown & Counts
        total = traffic_data.get("vehicle_count", 0)
        cars = traffic_data.get("cars", 0)
        bikes = traffic_data.get("motorcycles", 0)
        buses = traffic_data.get("buses", 0)
        trucks = traffic_data.get("trucks", 0)

        text1 = (
            f"TOTAL: {total}   "
            f"CARS: {cars}   "
            f"BIKES: {bikes}   "
            f"BUSES: {buses}   "
            f"TRUCKS: {trucks}"
        )
        cv2.putText(
            frame,
            text1,
            (20, h - 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        # Line 2: Traffic Level + GPU & FPS Badge
        text2 = f"TRAFFIC: {traffic_level}"
        cv2.putText(
            frame,
            text2,
            (20, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            traffic_color,
            3
        )

        text3 = f"GPU: {gpu_name} | FPS: {fps}"
        cv2.putText(
            frame,
            text3,
            (w - 480, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 200),
            2
        )
        return frame


# ============================================================
# STANDALONE EXECUTION (PRESERVES 100% EXISTING WORKING PIPELINE)
# ============================================================

if __name__ == "__main__":
    PHONE_URL = os.getenv("CAMERA_SOURCE", "http://10.54.205.62:8080/video")
    MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")

    previous_positions = {}
    movement_values = []

    print("Loading YOLO...")
    model = YOLO(MODEL_PATH)
    model.to("cuda")

    gpu_device = next(model.model.parameters()).device
    print("GPU:", gpu_device)

    cap = cv2.VideoCapture(PHONE_URL)
    if not cap.isOpened():
        print(f"❌ Could not connect to camera: {PHONE_URL}")
        exit()

    print("✅ Camera connected")
    print("Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame failed")
            break

        frame = cv2.resize(frame, (1280, 720))

        results = model.track(
            frame,
            device=0,
            conf=0.35,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )
        result = results[0]

        current_positions = {}
        if result.boxes is not None and result.boxes.id is not None:
            for i in range(len(result.boxes)):
                track_id = int(result.boxes.id[i])
                cls_id = int(result.boxes.cls[i])
                class_name = model.names[cls_id]

                if class_name not in VEHICLES:
                    continue

                box = result.boxes.xyxy[i].cpu().numpy()
                x1, y1, x2, y2 = box
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                current_positions[track_id] = (center_x, center_y)

                if track_id in previous_positions:
                    old_x, old_y = previous_positions[track_id]
                    distance = ((center_x - old_x) ** 2 + (center_y - old_y) ** 2) ** 0.5
                    movement_values.append(distance)

        previous_positions = current_positions
        annotated = result.plot()

        counts = Counter()
        if result.boxes is not None:
            for i in range(len(result.boxes)):
                cls_id = int(result.boxes.cls[i])
                class_name = model.names[cls_id]
                if class_name in VEHICLES:
                    counts[class_name] += 1

        total = sum(counts.values())

        if total >= 20:
            traffic_level = "HIGH"
            traffic_color = (0, 0, 255)
        elif total >= 10:
            traffic_level = "MEDIUM"
            traffic_color = (0, 165, 255)
        else:
            traffic_level = "LOW"
            traffic_color = (0, 255, 0)

        h, w = annotated.shape[:2]
        panel_height = 120
        cv2.rectangle(annotated, (0, h - panel_height), (w, h), (20, 20, 20), -1)

        text1 = (
            f"TOTAL: {total}   "
            f"CARS: {counts['car']}   "
            f"BIKES: {counts['motorcycle']}   "
            f"BUSES: {counts['bus']}   "
            f"TRUCKS: {counts['truck']}"
        )
        cv2.putText(annotated, text1, (20, h - 75), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(annotated, f"TRAFFIC: {traffic_level}", (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, traffic_color, 3)

        cv2.imshow("UrbanSenseAI - Live Traffic Intelligence", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()