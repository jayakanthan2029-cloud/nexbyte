from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from ai.config import ai_config
from ai.detector import YOLODetector, VEHICLE_CLASSES

class TrackedVehicle:
    def __init__(
        self,
        track_id: int,
        class_name: str,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        timestamp: datetime
    ):
        self.track_id = track_id
        self.class_name = class_name
        self.bbox = bbox # (x1, y1, x2, y2)
        self.confidence = confidence
        self.timestamp = timestamp
        x1, y1, x2, y2 = bbox
        self.center_x = int((x1 + x2) / 2)
        self.center_y = int((y1 + y2) / 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "bounding_box": list(self.bbox),
            "center_x": self.center_x,
            "center_y": self.center_y,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp.isoformat()
        }

class ByteTracker:
    def __init__(self, detector: YOLODetector):
        self.detector = detector
        self.previous_positions: Dict[int, Tuple[int, int]] = {}

    def track(self, frame) -> Tuple[List[TrackedVehicle], Any, Dict[int, float]]:
        """
        Run tracking on frame using ByteTrack.
        Returns:
            - List of TrackedVehicle objects
            - Ultralytics result object (for plotting / annotation)
            - Movement distances per track ID (displacement from previous frame)
        """
        results = self.detector.model.track(
            frame,
            device=0 if self.detector.device == "cuda" else "cpu",
            conf=self.detector.conf,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]
        tracked_vehicles: List[TrackedVehicle] = []
        movement_displacements: Dict[int, float] = {}
        now = datetime.utcnow()

        current_positions: Dict[int, Tuple[int, int]] = {}

        if result.boxes is not None and result.boxes.id is not None:
            for i in range(len(result.boxes)):
                track_id = int(result.boxes.id[i])
                cls_id = int(result.boxes.cls[i])
                class_name = self.detector.model.names[cls_id]

                if class_name not in VEHICLE_CLASSES:
                    continue

                conf = float(result.boxes.conf[i])
                box = result.boxes.xyxy[i].cpu().numpy().astype(int)
                x1, y1, x2, y2 = box

                vehicle = TrackedVehicle(
                    track_id=track_id,
                    class_name=class_name,
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    confidence=conf,
                    timestamp=now
                )
                tracked_vehicles.append(vehicle)
                current_positions[track_id] = (vehicle.center_x, vehicle.center_y)

                # Compute Euclidean displacement if previously seen
                if track_id in self.previous_positions:
                    old_x, old_y = self.previous_positions[track_id]
                    dist = ((vehicle.center_x - old_x) ** 2 + (vehicle.center_y - old_y) ** 2) ** 0.5
                    movement_displacements[track_id] = dist

        self.previous_positions = current_positions
        return tracked_vehicles, result, movement_displacements
