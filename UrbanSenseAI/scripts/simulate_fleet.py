"""
UrbanSenseAI - Digital Fleet Simulator
Simulates BUS-002 through BUS-005 traversing authentic Chennai metropolitan routes,
emitting periodic GPS coordinates, traffic density metrics, and occasional civic events.
Clearly distinguishes SIMULATED fleet nodes from the physical prototype (BUS-001).
"""

import sys
import time
import random
from pathlib import Path
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai.simulator import FleetBusSimulator

# Chennai Transit Routes
ROUTES_CONFIG = [
    {
        "bus_id": "BUS-002",
        "reg_number": "TN-02-SIM-101",
        "route_name": "Route 19B (T.Nagar - Kelambakkam)",
        "waypoints": [
            (13.0418, 80.2341), # T.Nagar Panagal Park
            (13.0234, 80.2405), # Nandanam
            (12.9915, 80.2435), # Adyar Madhya Kailash
            (12.9654, 80.2490), # Thoraipakkam OMR
            (12.9372, 80.2290), # Sholinganallur
            (12.8710, 80.2220), # Navalur
            (12.7845, 80.2185)  # Kelambakkam
        ]
    },
    {
        "bus_id": "BUS-003",
        "reg_number": "TN-03-SIM-202",
        "route_name": "Route 23C (Ayanavaram - Besant Nagar)",
        "waypoints": [
            (13.0982, 80.2312), # Ayanavaram
            (13.0815, 80.2420), # Kilpauk
            (13.0580, 80.2505), # Thousand Lights
            (13.0350, 80.2580), # Alwarpet
            (13.0075, 80.2570), # Adyar Bridge
            (12.9985, 80.2665)  # Besant Nagar Beach
        ]
    },
    {
        "bus_id": "BUS-004",
        "reg_number": "TN-04-SIM-303",
        "route_name": "Route 570 (CMBT - Siruseri SIPCOT)",
        "waypoints": [
            (13.0694, 80.2055), # CMBT Koyambedu
            (13.0385, 80.2065), # Vadapalani
            (13.0080, 80.2120), # Ashok Nagar
            (12.9815, 80.2180), # Guindy Industrial Estate
            (12.9230, 80.2310), # Karapakkam
            (12.8285, 80.2215)  # Siruseri SIPCOT IT Park
        ]
    },
    {
        "bus_id": "BUS-005",
        "reg_number": "TN-05-SIM-404",
        "route_name": "Route 47A (ICF - Thiruvanmiyur)",
        "waypoints": [
            (13.1020, 80.2070), # ICF Villivakkam
            (13.0850, 80.2100), # Anna Nagar Roundtana
            (13.0520, 80.2110), # Kodambakkam
            (13.0180, 80.2250), # Little Mount
            (12.9830, 80.2585)  # Thiruvanmiyur Bus Stand
        ]
    }
]

def main():
    api_base = "http://localhost:8000/api"
    print("=" * 65)
    print("   UrbanSenseAI - Digital Fleet Simulator (BUS-002 to BUS-005)   ")
    print("=" * 65)
    print(f"Target API: {api_base}")
    print("Simulated fleet nodes running in background. Press Ctrl+C to stop.")

    simulators = [
        FleetBusSimulator(cfg["bus_id"], cfg["reg_number"], cfg["route_name"], cfg["waypoints"])
        for cfg in ROUTES_CONFIG
    ]

    cycle = 0
    try:
        while True:
            cycle += 1
            for sim in simulators:
                pos = sim.step(dt=2.5)

                # Send location update
                try:
                    requests.post(
                        f"{api_base}/locations",
                        json={
                            "bus_id": pos["bus_id"],
                            "latitude": pos["latitude"],
                            "longitude": pos["longitude"],
                            "speed": pos["speed"]
                        },
                        timeout=2.0
                    )
                except Exception:
                    pass

                # Send traffic update
                traffic = sim.generate_traffic(pos)
                try:
                    requests.post(
                        f"{api_base}/traffic",
                        json=traffic,
                        timeout=2.0
                    )
                except Exception:
                    pass

                # Occasional simulated civic event (Pothole / Waterlogging) every ~15 cycles
                if cycle % 15 == 0 and random.random() < 0.4:
                    event_type = random.choice(["POTHOLE", "WATERLOGGING", "ROAD_HAZARD"])
                    desc = f"DEMO DETECTION: Simulated {event_type.lower().replace('_', ' ')} detected by {pos['bus_id']}"
                    try:
                        requests.post(
                            f"{api_base}/events",
                            json={
                                "bus_id": pos["bus_id"],
                                "event_type": event_type,
                                "latitude": pos["latitude"],
                                "longitude": pos["longitude"],
                                "confidence": round(random.uniform(0.82, 0.94), 2),
                                "description": desc,
                                "status": "NEW"
                            },
                            timeout=2.0
                        )
                        print(f"[{time.strftime('%H:%M:%S')}] [{pos['bus_id']}] Emitted {event_type} event at ({pos['latitude']}, {pos['longitude']})")
                    except Exception:
                        pass

            if cycle % 5 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] Telemetry synced for 4 simulated fleet buses (BUS-002..BUS-005)")

            time.sleep(2.5)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    main()
