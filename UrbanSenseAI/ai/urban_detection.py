from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from ai.config import ai_config
from ai.logger import logger

class UrbanDetectionModel:
    """
    Adapter for Custom Urban Infrastructure Model.
    Supports classes: pothole, waterlogging, damaged_road, missing_divider, missing_signboard, road_hazard.
    Honesty requirement: If urban_model.pt is missing, gracefully disables or operates in demo mode,
    explicitly labeling outputs as 'DEMO DETECTION'.
    """
    def __init__(self, model_path: str = None):
        self.model_path = model_path or ai_config.URBAN_MODEL_PATH
        self.is_custom_model_available = False
        self.model = None

        resolved = Path(self.model_path)
        if resolved.exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(resolved))
                self.is_custom_model_available = True
                logger.success(f"Custom urban infrastructure model loaded from {resolved}")
            except Exception as e:
                logger.warning(f"Could not load custom urban model: {e}")
                self.is_custom_model_available = False
        else:
            logger.info(f"Custom model '{self.model_path}' not found. Operating in DEMO/TRIGGER mode (Labeled 'DEMO DETECTION').")

    def detect(self, frame) -> List[Dict[str, Any]]:
        """
        Run inference if custom model is available.
        """
        if not self.is_custom_model_available or self.model is None:
            return []

        results = self.model(frame, conf=0.40, verbose=False)
        detections = []
        result = results[0]

        if result.boxes is not None:
            for i in range(len(result.boxes)):
                cls_id = int(result.boxes.cls[i])
                class_name = self.model.names[cls_id]
                conf = float(result.boxes.conf[i])
                box = result.boxes.xyxy[i].cpu().numpy().astype(int)
                detections.append({
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": box.tolist(),
                    "source": "REAL_MODEL"
                })
        return detections

    def generate_demo_detection(self, frame: np.ndarray, event_type: str = "POTHOLE") -> Dict[str, Any]:
        """
        Generates an honest, clearly-labeled simulated event from the current frame for demo scenarios.
        """
        h, w = frame.shape[:2]

        if event_type == "POTHOLE":
            # Candidate lower road region
            x1, y1 = int(w * 0.35), int(h * 0.65)
            x2, y2 = int(w * 0.65), int(h * 0.85)
            label = "DEMO DETECTION: Road Surface Defect (Pothole)"
        elif event_type == "WATERLOGGING":
            x1, y1 = int(w * 0.20), int(h * 0.70)
            x2, y2 = int(w * 0.80), int(h * 0.95)
            label = "DEMO DETECTION: Waterlogging / Puddle Detected"
        else:
            x1, y1 = int(w * 0.40), int(h * 0.50)
            x2, y2 = int(w * 0.60), int(h * 0.75)
            label = f"DEMO DETECTION: {event_type}"

        # Draw demo bounding box on a copy
        annotated_frame = frame.copy()
        box_color = (0, 140, 255) if event_type == "POTHOLE" else (255, 100, 0)
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 3)
        cv2.putText(
            annotated_frame,
            label,
            (x1, max(30, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            box_color,
            2
        )

        return {
            "event_type": event_type,
            "confidence": 0.89,
            "bbox": [x1, y1, x2, y2],
            "description": label,
            "is_demo": True,
            "annotated_frame": annotated_frame
        }
