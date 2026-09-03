import time
import cv2
import numpy as np
from pathlib import Path
from ai.config import ai_config
from ai.logger import logger

class CameraManager:
    """
    Robust camera manager supporting:
    1. Phone IP camera URL (MJPEG / RTSP)
    2. Local webcam integer index (e.g. 0)
    3. Local video file path for testing
    Features automatic non-blocking reconnection, FPS measurement, and graceful fallback.
    """
    def __init__(self, source: str = None, width: int = None, height: int = None):
        self.source_str = source if source is not None else ai_config.CAMERA_SOURCE
        self.width = width or ai_config.CAMERA_WIDTH
        self.height = height or ai_config.CAMERA_HEIGHT
        self.reconnect_delay = ai_config.CAMERA_RECONNECT_DELAY

        self.cap = None
        self.is_connected = False
        self.last_reconnect_attempt = 0.0
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()
        self.consecutive_failures = 0

        # Parse source (integer for webcam, string for URL / file)
        self.source = self._parse_source(self.source_str)
        self.connect()

    def _parse_source(self, src: str):
        if isinstance(src, int):
            return src
        src_clean = str(src).strip()
        if src_clean.isdigit():
            return int(src_clean)
        return src_clean

    def connect(self) -> bool:
        """Attempt to open camera connection."""
        self.last_reconnect_attempt = time.time()
        logger.info(f"Connecting to camera source: {self.source}...")
        try:
            if self.cap is not None:
                self.cap.release()

            self.cap = cv2.VideoCapture(self.source)

            # Optimizations for IP cameras to prevent latency lag
            if isinstance(self.source, str) and self.source.startswith("http"):
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self.cap.isOpened():
                # Read a test frame to ensure stream is transmitting
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.is_connected = True
                    self.consecutive_failures = 0
                    logger.success(f"Camera connected successfully [{frame.shape[1]}x{frame.shape[0]}]")
                    return True

            self.is_connected = False
            logger.warning(f"Could not read initial frame from {self.source}")
            return False

        except Exception as e:
            self.is_connected = False
            logger.error(f"Error opening camera source {self.source}: {e}")
            return False

    def read_frame(self) -> tuple[bool, np.ndarray]:
        """
        Read the latest frame.
        If stream drops, attempts automatic reconnection without crashing.
        """
        now = time.time()

        # Handle disconnected state with throttled reconnection
        if not self.is_connected or self.cap is None or not self.cap.isOpened():
            if now - self.last_reconnect_attempt > self.reconnect_delay:
                self.connect()
            return False, self._get_placeholder_frame("RECONNECTING TO CAMERA...")

        ret, frame = self.cap.read()

        if not ret or frame is None:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 5:
                logger.warning("Multiple frame read failures. Marking camera disconnected.")
                self.is_connected = False
                self.last_reconnect_attempt = now
            return False, self._get_placeholder_frame("CAMERA STREAM INTERRUPTED")

        self.consecutive_failures = 0
        self.frame_count += 1

        # Calculate rolling FPS
        elapsed = now - self.start_time
        if elapsed >= 1.0:
            self.fps = round(self.frame_count / elapsed, 1)
            self.frame_count = 0
            self.start_time = now

        # Normalize resolution
        if (frame.shape[1], frame.shape[0]) != (self.width, self.height):
            frame = cv2.resize(frame, (self.width, self.height))

        return True, frame

    def _get_placeholder_frame(self, message: str) -> np.ndarray:
        """Generate a standby frame when camera is disconnected."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Gradient background
        frame[:] = (25, 25, 30)

        # Draw warning banner
        cv2.putText(
            frame,
            "UrbanSenseAI - Camera Feed Offline",
            (self.width // 2 - 260, self.height // 2 - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 165, 255),
            2
        )
        cv2.putText(
            frame,
            f"Status: {message} ({self.source})",
            (self.width // 2 - 320, self.height // 2 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            1
        )
        return frame

    def release(self):
        """Cleanly close camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        logger.info("Camera resources released")
