import random
import time
from datetime import datetime
from typing import Dict, Any, List

class FleetBusSimulator:
    """
    Simulates a digital fleet bus (BUS-002 through BUS-005).
    Maintains authentic Chennai transit routes, speeds, and periodically emits
    simulated traffic and hazard events, clearly tagged as 'SIMULATED'.
    """
    def __init__(self, bus_id: str, reg_number: str, route_name: str, waypoints: List[tuple]):
        self.bus_id = bus_id
        self.reg_number = reg_number
        self.route_name = route_name
        self.waypoints = waypoints
        self.current_idx = random.randint(0, len(waypoints) - 2)
        self.progress = random.random()
        self.direction = 1
        self.speed = random.uniform(18.0, 35.0)

    def step(self, dt: float = 2.0) -> Dict[str, Any]:
        """Advance bus along its route."""
        step_dist = (self.speed / 3600.0) * dt * 0.12
        self.progress += step_dist

        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_idx += self.direction
            if self.current_idx >= len(self.waypoints) - 1:
                self.current_idx = len(self.waypoints) - 1
                self.direction = -1
            elif self.current_idx <= 0:
                self.current_idx = 0
                self.direction = 1

        next_idx = max(0, min(len(self.waypoints) - 1, self.current_idx + self.direction))
        lat1, lon1 = self.waypoints[self.current_idx]
        lat2, lon2 = self.waypoints[next_idx]

        curr_lat = round(lat1 + (lat2 - lat1) * self.progress, 6)
        curr_lon = round(lon1 + (lon2 - lon1) * self.progress, 6)

        # Dynamic speed fluctuation
        self.speed = max(10.0, min(45.0, self.speed + random.uniform(-2.0, 2.0)))

        return {
            "bus_id": self.bus_id,
            "registration_number": self.reg_number,
            "route_name": self.route_name,
            "latitude": curr_lat,
            "longitude": curr_lon,
            "speed": round(self.speed, 1),
            "status": "ACTIVE",
            "camera_status": "CONNECTED",
            "is_simulated": True
        }

    def generate_traffic(self, current_pos: dict) -> Dict[str, Any]:
        """Generate realistic simulated traffic telemetry."""
        cars = random.randint(4, 18)
        bikes = random.randint(2, 12)
        buses = random.randint(1, 3)
        trucks = random.randint(0, 3)
        total = cars + bikes + buses + trucks

        movement_score = round(random.uniform(0.10, 0.75), 2)
        if total >= 25:
            traffic_level = "HIGH"
            reasons = ["High vehicle density", "Slow vehicle movement"]
        elif total >= 12:
            traffic_level = "MEDIUM"
            reasons = ["Moderate vehicle density"]
        else:
            traffic_level = "LOW"
            reasons = ["Free flowing traffic"]

        return {
            "bus_id": self.bus_id,
            "vehicle_count": total,
            "cars": cars,
            "motorcycles": bikes,
            "buses": buses,
            "trucks": trucks,
            "movement_score": movement_score,
            "traffic_level": traffic_level,
            "probable_reasons": reasons,
            "latitude": current_pos["latitude"],
            "longitude": current_pos["longitude"],
            "timestamp": datetime.utcnow().isoformat()
        }
