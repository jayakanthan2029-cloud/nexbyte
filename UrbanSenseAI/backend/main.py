from pathlib import Path
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings, BASE_DIR
from backend.routes import (
    health, buses, events, traffic, incidents, locations, dashboard, media
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Mobile Urban Intelligence Platform Backend (SIH 2026)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# CORS MIDDLEWARE
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local Vite frontend (localhost:5173, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MOUNT STATIC MEDIA DIRECTORY
# ============================================================
MEDIA_ROOT = (BASE_DIR / settings.MEDIA_DIR).resolve()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")

# ============================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

ws_manager = ConnectionManager()

# Hook the broadcast function into all event routes
events.set_ws_broadcast(ws_manager.broadcast)
traffic.set_ws_broadcast(ws_manager.broadcast)
incidents.set_ws_broadcast(ws_manager.broadcast)
locations.set_ws_broadcast(ws_manager.broadcast)

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time live telemetry stream for the React GIS Dashboard."""
    await ws_manager.connect(websocket)
    try:
        # Send initial connected greeting
        await websocket.send_text(json.dumps({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to UrbanSenseAI Live Telemetry Stream"
        }))
        while True:
            # Keep connection alive and listen for optional client pings
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("type") == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Edge Heartbeat receiver
@app.post("/api/health/heartbeat")
def post_heartbeat(data: dict):
    """Receive heartbeat from physical edge bus AI engine."""
    health.update_edge_health(
        ai_engine=data.get("ai_engine"),
        camera=data.get("camera"),
        gps=data.get("gps")
    )
    return {"status": "ok"}

# ============================================================
# REGISTER API ROUTERS
# ============================================================
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(buses.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(traffic.router, prefix=settings.API_V1_STR)
app.include_router(incidents.router, prefix=settings.API_V1_STR)
app.include_router(locations.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(media.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "status": "operational",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": "/api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
