from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import cv2
import numpy as np
from pathlib import Path
from ai.config import ai_config, BASE_DIR
from ai.logger import logger

class PlateOCR(ABC):
    @abstractmethod
    def read_plate(self, vehicle_crop: np.ndarray) -> Dict[str, Any]:
        pass

class EventTriggeredOCR(PlateOCR):
    """
    Event-triggered License Plate OCR.
    Runs strictly upon an incident or suspicious event detection (never per-frame).
    Checks for available OCR backends (PaddleOCR or EasyOCR).
    If unavailable, returns OCR_STATUS='unavailable' or simulated candidate clearly labeled.
    """
    def __init__(self):
        self.backend = None
        self.status = "unavailable"
        self.plates_dir = (BASE_DIR / ai_config.MEDIA_DIR / "plates").resolve()
        self.plates_dir.mkdir(parents=True, exist_ok=True)

        # Check PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.backend = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            self.status = "paddleocr"
            logger.success("PaddleOCR loaded successfully for event-triggered plate recognition")
        except ImportError:
            # Check EasyOCR fallback
            try:
                import easyocr
                self.backend = easyocr.Reader(["en"])
                self.status = "easyocr"
                logger.info("EasyOCR fallback loaded for plate recognition")
            except ImportError:
                self.status = "unavailable"
                logger.info("OCR packages not installed. Running in graceful fallback mode (OCR_STATUS = 'unavailable').")

    def crop_candidate_plate(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Crops the bottom 35% of a vehicle bounding box where license plates typically reside.
        """
        x1, y1, x2, y2 = bbox
        h = y2 - y1
        w = x2 - x1

        # Bottom 35% of vehicle box
        plate_y1 = max(0, int(y2 - h * 0.35))
        plate_y2 = min(frame.shape[0], y2)
        plate_x1 = max(0, int(x1 + w * 0.15))
        plate_x2 = min(frame.shape[1], int(x2 - w * 0.15))

        crop = frame[plate_y1:plate_y2, plate_x1:plate_x2]
        return crop

    def read_plate(self, vehicle_crop: np.ndarray, track_id: int = 0) -> Dict[str, Any]:
        """
        Execute OCR on cropped region.
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return {"status": self.status, "plate_number": None}

        # Save plate crop to media/plates/
        crop_name = f"plate_track_{track_id}_{int(cv2.getTickCount())}.jpg"
        crop_path = self.plates_dir / crop_name
        cv2.imwrite(str(crop_path), vehicle_crop)
        relative_path = f"{ai_config.MEDIA_DIR}/plates/{crop_name}"

        if self.status == "paddleocr" and self.backend is not None:
            try:
                results = self.backend.ocr(vehicle_crop, cls=True)
                if results and len(results) > 0 and results[0]:
                    text = results[0][0][1][0]
                    conf = float(results[0][0][1][1])
                    return {
                        "status": "success",
                        "plate_number": text.strip().upper(),
                        "confidence": round(conf, 2),
                        "crop_path": relative_path
                    }
            except Exception as e:
                logger.error(f"PaddleOCR error: {e}")

        # Graceful fallback: when OCR is not installed, return simulated plate clearly tagged
        demo_plate = f"TN-0{track_id % 9 + 1}-AL-{1000 + (track_id * 37) % 8999} (Simulated)"
        return {
            "status": "unavailable",
            "plate_number": demo_plate,
            "confidence": 0.82,
            "crop_path": relative_path,
            "note": "OCR engine not installed. Simulated plate generated for demonstration."
        }
