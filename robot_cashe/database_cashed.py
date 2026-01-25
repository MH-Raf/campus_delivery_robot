from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import campus_delivery_robot as lr1


class TelemetryCache:
    def __init__(self, ttl_seconds: int = 1):
        self.ttl = timedelta(seconds=ttl_seconds)
        self.value: Optional[Dict[str, Any]] = None
        self.timestamp: Optional[datetime] = None

    def get(self):
        if self.value is None:
            return None
        if datetime.now() > self.timestamp + self.ttl:
    
            self.value = None
            return None
        return self.value

    def update(self, data: Dict[str, Any]):
        self.value = data
        self.timestamp = datetime.now()


class TelemetryServiceCached:
    def __init__(self, robot: lr1.CourierRobot, ttl_seconds: int = 1):
        self.robot = robot
        self.cache = TelemetryCache(ttl_seconds=ttl_seconds)

    def get_telemetry(self):
        cached = self.cache.get()
        if cached:
            return {**cached, "cached": True}

        x, y = self.robot.state.position
        data = {
            "x": x,
            "y": y,
            "busy": self.robot.state.busy,
            "speed": self.robot.state.speed,
            "units": self.robot.state.speed_units,
            "time": datetime.now().strftime("%H:%M:%S"),
        }

        self.cache.update(data)

        return {**data, "cached": False}
