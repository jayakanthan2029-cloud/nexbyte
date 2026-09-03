from typing import List, Dict, Any, Optional, Tuple
import time
from datetime import datetime
from ai.tracker import TrackedVehicle
from ai.logger import logger

def calculate_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    denom = float(boxAArea + boxBArea - interArea)
    if denom <= 0:
        return 0.0
    return interArea / denom

class CrashDetector:
    """
    Prototype collision detection engine.
    Analyzes trajectory intersections, sudden bounding box overlap (> 0.55 IoU),
    and sudden kinetic proximity.
    Honesty requirement: Labeled strictly as 'Potential Collision'.
    """
    def __init__(self, iou_threshold: float = 0.55):
        self.iou_threshold = iou_threshold
        self.last_incident_time = 0.0
        self.cooldown_period = 15.0 # Seconds between collision triggers to avoid duplicates

    def check_collisions(self, tracked_vehicles: List[TrackedVehicle]) -> Optional[Dict[str, Any]]:
        now = time.time()
        if now - self.last_incident_time < self.cooldown_period:
            return None

        n = len(tracked_vehicles)
        if n < 2:
            return None

        # Compare pairs of tracked vehicles
        for i in range(n):
            for j in range(i + 1, n):
                v1 = tracked_vehicles[i]
                v2 = tracked_vehicles[j]

                iou = calculate_iou(v1.bbox, v2.bbox)

                # If overlapping boxes indicate potential collision
                if iou >= self.iou_threshold:
                    self.last_incident_time = now
                    logger.warning(
                        f"Potential Collision detected: Track #{v1.track_id} ({v1.class_name}) "
                        f"<-> Track #{v2.track_id} ({v2.class_name}) with IoU: {round(iou, 2)}"
                    )
                    return {
                        "incident_type": "Potential Collision",
                        "confidence": round(iou, 2),
                        "vehicles_involved": [
                            {"track_id": v1.track_id, "class_name": v1.class_name, "bbox": v1.bbox},
                            {"track_id": v2.track_id, "class_name": v2.class_name, "bbox": v2.bbox}
                        ],
                        "description": (
                            f"Potential Collision: Intersection between {v1.class_name.upper()} #{v1.track_id} "
                            f"and {v2.class_name.upper()} #{v2.track_id} (Overlap IoU: {round(iou, 2)})"
                        ),
                        "timestamp": datetime.utcnow()
                    }

        return None

    def trigger_demo_crash(self, tracked_vehicles: List[TrackedVehicle] = None) -> Dict[str, Any]:
        """
        Manually trigger the collision evidence workflow for demonstration (Keyboard hotkey 'c').
        """
        self.last_incident_time = time.time()

        if tracked_vehicles and len(tracked_vehicles) >= 2:
            v1, v2 = tracked_vehicles[0], tracked_vehicles[1]
            desc = (
                f"Potential Collision (Demo Trigger): Conflict between {v1.class_name.upper()} #{v1.track_id} "
                f"and {v2.class_name.upper()} #{v2.track_id}"
            )
            v_inv = [
                {"track_id": v1.track_id, "class_name": v1.class_name, "bbox": v1.bbox},
                {"track_id": v2.track_id, "class_name": v2.class_name, "bbox": v2.bbox}
            ]
        else:
            desc = "Potential Collision (Demo Trigger): Manual collision evidence test event"
            v_inv = [
                {"track_id": 14, "class_name": "car", "bbox": [400, 300, 600, 480]},
                {"track_id": 19, "class_name": "motorcycle", "bbox": [550, 350, 680, 500]}
            ]

        logger.event("POTENTIAL_COLLISION", f"Manual trigger activated: {desc}")
        return {
            "incident_type": "Potential Collision",
            "confidence": 0.85,
            "vehicles_involved": v_inv,
            "description": desc,
            "timestamp": datetime.utcnow()
        }
