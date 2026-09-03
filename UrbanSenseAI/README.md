# UrbanSenseAI
### AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet
**SIH 2026 Problem Statement:** SIH26124  
**Target Hardware:** Windows 11 Laptop (Intel Core i7-13650HX, NVIDIA GeForce RTX 4060 Laptop GPU 8GB VRAM, 24GB RAM)

---

## 1. Project Overview
UrbanSenseAI transforms municipal public transport buses into mobile edge-sensing nodes. As buses navigate transit corridors, edge computers capture visual and spatial data to detect:
- Real-time traffic congestion, vehicle density, and modal breakdown (cars, bikes, buses, trucks).
- Road surface defects (potholes, damaged roads, waterlogging, hazards).
- Potential vehicle collisions using trajectory tracking, rolling video buffers (~25s MP4 evidence clips), and license plate OCR.
- Scalable digital fleet management distinguishing the **LIVE physical prototype bus (`BUS-001`)** from **SIMULATED fleet nodes (`BUS-002` to `BUS-005`)**.

---

## 2. System Architecture

```
                       PHYSICAL BUS-001
                              |
               Phone IP Camera (or Webcam/Video)
                              |
                OpenCV Capture (ai/camera.py)
                              |
               +--------------+--------------+
               |   EDGE AI ENGINE (ai/main)  |
               |  - YOLODetector (CUDA RTX)  |
               |  - ByteTracker (Persistent) |
               |  - TrafficAnalyzer (Score)  |
               |  - CrashDetector (Collision)|
               |  - RollingVideoBuffer (~25s)|
               |  - EventTriggeredOCR        |
               |  - UrbanDetectionModel      |
               +--------------+--------------+
                              |
                      Event Processor
                              |
                     REST / WebSocket
                              |
                     FASTAPI BACKEND
                     (Port 8000)
               +--------------+--------------+
               |                             |
        POSTGRESQL 18                 Local Filesystem
       (urbansense DB)               (media/ subfolders)
               |                             |
               +--------------+--------------+
                              |
                   WebSocket & REST APIs
                              |
                  REACT + VITE GIS DASHBOARD
                    (Port 5173 / Leaflet)
               +--------------+--------------+
               |       |      |       |      |
             Live     GIS  Traffic Incidents Fleet
             Bus      Map  Charts  Evidence  Sim
```

---

## 3. Hardware Requirements
- **Edge Computer:** Windows 11 Laptop
  - CPU: Intel Core i7-13650HX (or equivalent multi-core processor)
  - GPU: NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)
  - RAM: 24GB DDR5
  - Storage: 512GB SSD
- **Camera:** Android Phone used as an IP Camera (e.g. *IP Webcam* app on Android) or integrated 720p/1080p webcam.
- **Network:** Phone and laptop connected to the same local Wi-Fi network.

---

## 4. Requirements & Tech Stack
- **Edge AI:** Python 3.11, PyTorch 2.11.0+cu128, Ultralytics YOLO (YOLO11n), ByteTrack, OpenCV, NumPy.
- **Backend:** FastAPI, Uvicorn, SQLAlchemy 2.0, PostgreSQL 18, psycopg2-binary, Pydantic, WebSockets.
- **Frontend:** React 18, Vite 5, React-Leaflet, OpenStreetMap, Recharts, Lucide-React, Vanilla CSS design system.
- **Storage:** PostgreSQL 18 relational storage with local filesystem media storage under `media/`.

---

## 5. Python Virtual Environment Setup
Ensure Python 3.11 is installed. Open PowerShell in the project root:

```powershell
# Activate existing virtual environment
& "..\venv\Scripts\Activate.ps1"

# Verify PyTorch CUDA acceleration on RTX 4060
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0))"
```

---

## 6. Node.js & Frontend Environment
Verify Node.js (v20+ or v24+) and npm are available:

```powershell
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
node -v
npm -v
```

---

## 7. PostgreSQL Setup
- **PostgreSQL 18** runs as a Windows service (`postgresql-x64-18`) on port `5432`.
- Default superuser: `postgres`.

---

## 8. Database Creation & Schema Migration
Initialize the database following Requirement 3 (connects to maintenance DB `postgres`, creates `urbansense`, then applies the relational schema):

```powershell
# Create database and apply schema
python scripts/create_database.py

# Populate initial fleet and historical data
python scripts/seed_database.py
```

---

## 9. Environment Configuration (`.env`)
Configure your parameters in `.env`:

```ini
# Edge Bus Identification
BUS_ID=BUS-001
ROUTE_NAME=Route 21G (Broadway - Tambaram)

# Camera Source (IP Camera URL, Webcam '0', or sample video)
CAMERA_SOURCE=http://10.54.205.62:8080/video
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# AI Model
YOLO_MODEL_PATH=yolo11n.pt
URBAN_MODEL_PATH=models/urban_model.pt
CUDA_DEVICE=0

# Database
DATABASE_URL=postgresql://postgres:siharuvi@localhost:5432/urbansense
POSTGRES_USER=postgres
POSTGRES_PASSWORD=siharuvi
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=urbansense

# API & WebSocket
API_BASE_URL=http://localhost:8000/api
WS_URL=ws://localhost:8000/ws/live

# Media Storage
MEDIA_DIR=media
```

---

## 10. AI Model Setup
- Primary Vehicle Detector: `yolo11n.pt` is stored in the root and in `models/yolo11n.pt`.
- Custom Civic Infrastructure Model: `models/urban_model.pt`. If absent, the platform operates in graceful adapter mode and labels demo triggers as **`DEMO DETECTION`**.

---

## 11. Camera Setup (Android Phone IP Webcam)
1. Install **IP Webcam** (by Pavel Khlebovich) from Google Play Store on your Android phone.
2. Connect phone and laptop to the same Wi-Fi network.
3. In the app, scroll to the bottom and tap **Start server**.
4. Note the displayed IPv4 URL (e.g. `http://192.168.1.15:8080/video` or `http://10.54.205.62:8080/video`).
5. Update `CAMERA_SOURCE` in `.env`.
6. Run `python camera_test.py` to test connectivity.

---

## 12. Backend Startup
Start the FastAPI server:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/api/health`
- WebSocket: `ws://localhost:8000/ws/live`

---

## 13. Frontend Startup
In a second terminal:

```powershell
cd frontend
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 14. Edge AI Engine Startup (BUS-001)
In a third terminal:

```powershell
python -m ai.main
```
This opens the live OpenCV window **`UrbanSenseAI - Edge AI Intelligence (RTX 4060)`** showing:
- Real-time YOLO11n vehicle detection (`car`, `motorcycle`, `bus`, `truck`).
- Persistent ByteTrack IDs (`CAR #1`, `BIKE #2`).
- Bottom telemetry HUD panel with GPU name, vehicle counts, traffic level, and FPS.
- Live telemetry streaming to the dashboard.

---

## 15. Demo Mode & Keyboard Hotkeys
While the Edge AI window is focused:
- **`P`**: Trigger a **Demo Pothole Detection** (captures frame, saves to `media/potholes/`, dispatches event with GPS).
- **`W`**: Trigger a **Demo Waterlogging Detection** (captures frame, saves to `media/waterlogging/`, sends event).
- **`C`**: Trigger **Potential Collision Evidence Workflow** (locks ~10s rolling buffer, captures ~15s post-event frames, exports ~25s MP4 video and 3 keyframes `pre_event.jpg`, `event_frame.jpg`, `post_event.jpg` to `media/incidents/`, extracts plate number).
- **`Q`**: Clean shutdown.

To simulate the remaining fleet nodes (`BUS-002` through `BUS-005`):
```powershell
python scripts/simulate_fleet.py
```

---

## 16. Troubleshooting
1. **Camera connection fails**:
   - Ensure phone and laptop are on the same Wi-Fi subnet.
   - Test `CAMERA_SOURCE=0` in `.env` to test with your laptop's integrated webcam.
2. **PostgreSQL password error**:
   - Verify `POSTGRES_PASSWORD` in `.env` matches your PostgreSQL 18 password.
3. **Node/npm not recognized**:
   - Run `$env:PATH = "C:\Program Files\nodejs;$env:PATH"` before executing npm commands.
4. **CUDA out of memory**:
   - YOLO11n uses < 1.2GB VRAM on the RTX 4060 8GB GPU. Ensure no other heavy PyTorch processes are running.

---

## 17. REST & WebSocket API Documentation
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check (backend, DB, AI engine, camera, GPS). |
| `GET` | `/api/buses` | Fleet listing with `is_simulated` distinction. |
| `GET` | `/api/dashboard/summary` | Executive KPI counts. |
| `GET` | `/api/dashboard/live` | Real-time state for dashboard hydration. |
| `GET` | `/api/traffic` | Traffic analysis telemetry. |
| `POST`| `/api/traffic` | Submit periodic traffic records. |
| `GET` | `/api/events` | Civic road defects (potholes, hazards). |
| `POST`| `/api/events` | Log road defect with evidence photo. |
| `GET` | `/api/incidents` | Potential collision records. |
| `POST`| `/api/incidents` | Submit collision report with video buffer. |
| `PUT` | `/api/incidents/{id}/status` | Mark incident as `REVIEWED`. |
| `WS`  | `/ws/live` | Live WebSocket broadcast for real-time GIS map updates. |

---

## 18. Prototype Limitations & Future Roadmap
- **Custom Civic Models:** Pretrained YOLO11n handles COCO vehicles (`car`, `motorcycle`, `bus`, `truck`). Custom road hazard detections are labeled **`DEMO DETECTION`** until custom weights (`models/urban_model.pt`) trained on Indian road pothole datasets are mounted.
- **Accident Detection:** Implemented as a geometric and trajectory **Potential Collision** detector. Production deployments would utilize multi-camera optical flow and accelerometer IMU sensor fusion.
- **Hardware Scalability:** Validated for 1 physical bus node and 4 digital fleet nodes on a single laptop; designed to horizontally scale to 100+ buses via the same FastAPI and PostgreSQL backplane.
