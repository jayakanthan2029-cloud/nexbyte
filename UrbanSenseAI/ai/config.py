import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class AIConfig(BaseSettings):
    # Bus Metadata
    BUS_ID: str = "BUS-001"
    BUS_NAME: str = "Physical Prototype Bus"
    REGISTRATION_NUMBER: str = "TN-01-AL-2026"
    ROUTE_NAME: str = "Route 21G (Broadway - Tambaram)"

    # Camera Stream
    # Supports IP camera URL, webcam index ("0"), or test video file
    CAMERA_SOURCE: str = "http://10.54.205.62:8080/video"
    CAMERA_RECONNECT_DELAY: float = 3.0
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720

    # Models & Vision
    YOLO_MODEL_PATH: str = "yolo11n.pt"
    URBAN_MODEL_PATH: str = "models/urban_model.pt"
    DETECTION_CONFIDENCE: float = 0.35
    IOU_THRESHOLD: float = 0.45
    CUDA_DEVICE: int = 0

    # GPS
    # Options: phone (Physical Phone GPS), static (fixed real coordinate)
    GPS_MODE: str = "phone"
    DEFAULT_LATITUDE: float = 13.0827
    DEFAULT_LONGITUDE: float = 80.2707

    # API Backend
    API_BASE_URL: str = "http://localhost:8000/api"
    WS_URL: str = "ws://localhost:8000/ws/live"

    # Media Storage
    MEDIA_DIR: str = "media"

    # Demo & Simulation
    DEMO_MODE: bool = True

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

ai_config = AIConfig()
