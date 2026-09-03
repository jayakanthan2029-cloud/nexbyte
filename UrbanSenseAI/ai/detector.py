from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import torch
from ultralytics import YOLO
from ai.config import ai_config
from ai.logger import logger

VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck"}

class BaseDetector(ABC):
    @abstractmethod
    def detect(self, frame):
        pass

class YOLODetector(BaseDetector):
    def __init__(self, model_path: str = None, conf: float = None):
        self.model_path = model_path or ai_config.YOLO_MODEL_PATH
        self.conf = conf if conf is not None else ai_config.DETECTION_CONFIDENCE

        # Check CUDA availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"

        logger.info(f"Initializing YOLO detector [{self.model_path}] on device: {self.device} ({self.device_name})")

        # Resolve model path (check local and models/ directory)
        resolved_path = Path(self.model_path)
        if not resolved_path.exists():
            candidate = Path("models") / resolved_path.name
            if candidate.exists():
                resolved_path = candidate

        self.model = YOLO(str(resolved_path))
        if self.device == "cuda":
            self.model.to("cuda")

        logger.success(f"YOLO11n loaded successfully. Accelerated by: {self.device_name}")

    def detect(self, frame):
        """Run YOLO inference on a single frame."""
        results = self.model(
            frame,
            device=0 if self.device == "cuda" else "cpu",
            conf=self.conf,
            verbose=False
        )
        return results[0]
