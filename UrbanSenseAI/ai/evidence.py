import os
import time
import cv2
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ai.config import ai_config, BASE_DIR
from ai.logger import logger

class RollingVideoBuffer:
    """
    Maintains a rolling ring-buffer of recent video frames (~10s pre-event).
    When an incident occurs:
    1. Locks pre-event frames
    2. Collects ~15s of post-event frames
    3. Asynchronously writes ~25s MP4 video to media/incidents/crash_<bus_id>_<timestamp>.mp4
    4. Saves 3 keyframe snapshots: pre_event.jpg, event_frame.jpg, post_event.jpg
    """
    def __init__(
        self,
        fps: int = 15,
        pre_seconds: int = 10,
        post_seconds: int = 15
    ):
        self.fps = fps
        self.pre_buffer_size = fps * pre_seconds
        self.post_buffer_size = fps * post_seconds
        self.frame_buffer = deque(maxlen=self.pre_buffer_size)

        self.is_recording_incident = False
        self.post_frames_collected = []
        self.current_incident_context = None
        self.locked_pre_frames = []
        self.event_frame = None

        self.incidents_dir = (BASE_DIR / ai_config.MEDIA_DIR / "incidents").resolve()
        self.incidents_dir.mkdir(parents=True, exist_ok=True)

    def add_frame(self, frame) -> Optional[Dict[str, Any]]:
        """
        Feed each new camera frame into the rolling buffer.
        Returns evidence payload dict when a recording cycle completes.
        """
        # Always maintain rolling pre-event buffer
        self.frame_buffer.append(frame.copy())

        # If currently capturing post-event frames
        if self.is_recording_incident:
            self.post_frames_collected.append(frame.copy())

            if len(self.post_frames_collected) >= self.post_buffer_size:
                # Recording cycle complete: write video and keyframes
                self.is_recording_incident = False
                completed_incident = self.current_incident_context or {}
                pre_frames = list(self.locked_pre_frames)
                post_frames = list(self.post_frames_collected)
                self.current_incident_context = None

                evidence_data = self._finalize_evidence(completed_incident, pre_frames, post_frames)
                return evidence_data

        return None

    def trigger_incident(self, incident_data: dict, current_frame):
        """
        Trigger collision evidence capture.
        Locks pre-event buffer (~10s) and starts post-event recording (~15s).
        """
        if self.is_recording_incident:
            logger.warning("Incident evidence capture already in progress.")
            return

        logger.info("[HOTKEY] C -> Locking rolling video buffer for incident evidence...")
        self.is_recording_incident = True
        self.locked_pre_frames = list(self.frame_buffer)
        self.post_frames_collected = []
        self.event_frame = current_frame.copy()
        self.current_incident_context = incident_data

    def _finalize_evidence(
        self,
        incident_data: dict,
        pre_frames: list,
        post_frames: list
    ) -> Dict[str, Any]:
        """
        Saves the complete MP4 video and 3 keyframe snapshots.
        """
        bus_id = incident_data.get("bus_id", ai_config.BUS_ID)
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        inc_id = incident_data.get("incident_id") or f"INC-{timestamp_str}"

        video_filename = f"crash_{bus_id}_{timestamp_str}.mp4"
        video_path = self.incidents_dir / video_filename

        pre_img_name = f"{inc_id}_pre.jpg"
        event_img_name = f"{inc_id}_event.jpg"
        post_img_name = f"{inc_id}_post.jpg"

        pre_img_path = self.incidents_dir / pre_img_name
        event_img_path = self.incidents_dir / event_img_name
        post_img_path = self.incidents_dir / post_img_name

        all_frames = pre_frames + post_frames

        # Synchronously write keyframes so they exist immediately
        if len(pre_frames) > 0:
            cv2.imwrite(str(pre_img_path), pre_frames[0])
            cv2.imwrite(str(self.incidents_dir / "pre_event.jpg"), pre_frames[0])
        elif self.event_frame is not None:
            cv2.imwrite(str(pre_img_path), self.event_frame)
            cv2.imwrite(str(self.incidents_dir / "pre_event.jpg"), self.event_frame)

        if self.event_frame is not None:
            cv2.imwrite(str(event_img_path), self.event_frame)
            cv2.imwrite(str(self.incidents_dir / "event_frame.jpg"), self.event_frame)

        if len(post_frames) > 0:
            cv2.imwrite(str(post_img_path), post_frames[-1])
            cv2.imwrite(str(self.incidents_dir / "post_event.jpg"), post_frames[-1])
        elif self.event_frame is not None:
            cv2.imwrite(str(post_img_path), self.event_frame)
            cv2.imwrite(str(self.incidents_dir / "post_event.jpg"), self.event_frame)

        # Write MP4 video in worker thread
        def _write_video():
            try:
                if len(all_frames) > 0:
                    h, w = all_frames[0].shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    out = cv2.VideoWriter(str(video_path), fourcc, self.fps, (w, h))
                    for f in all_frames:
                        out.write(f)
                    out.release()
                    logger.success(f"Evidence video saved: {video_path} ({len(all_frames)} frames, ~{round(len(all_frames)/self.fps, 1)}s)")
            except Exception as e:
                logger.error(f"Failed to write incident video: {e}")

        thread = threading.Thread(target=_write_video, daemon=True)
        thread.start()

        relative_dir = f"{ai_config.MEDIA_DIR}/incidents"
        return {
            **incident_data,
            "incident_id": inc_id,
            "incident_type": incident_data.get("incident_type", "POTENTIAL_COLLISION"),
            "source_type": incident_data.get("source_type", "DEMO_EVENT"),
            "bus_id": bus_id,
            "video_path": f"{relative_dir}/{video_filename}",
            "media_files": [
                {"media_type": "VIDEO", "file_path": f"{relative_dir}/{video_filename}", "file_name": video_filename},
                {"media_type": "KEYFRAME_PRE", "file_path": f"{relative_dir}/{pre_img_name}", "file_name": pre_img_name},
                {"media_type": "KEYFRAME_EVENT", "file_path": f"{relative_dir}/{event_img_name}", "file_name": event_img_name},
                {"media_type": "KEYFRAME_POST", "file_path": f"{relative_dir}/{post_img_name}", "file_name": post_img_name}
            ]
        }
