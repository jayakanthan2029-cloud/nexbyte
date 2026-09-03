import logging
import sys
from datetime import datetime

class EdgeLogger:
    @staticmethod
    def info(msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] {msg}", flush=True)

    @staticmethod
    def success(msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] {msg}", flush=True)

    @staticmethod
    def warning(msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] {msg}", flush=True)

    @staticmethod
    def error(msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {msg}", flush=True)

    @staticmethod
    def event(event_type: str, msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [EVENT:{event_type}] {msg}", flush=True)

logger = EdgeLogger()
