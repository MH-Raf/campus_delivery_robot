from typing import Optional, Dict, Any
from Courier_Robot import robot, CourierRobot, Order
import asyncio
from enum import Enum


class RobotStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


class RobotService:
    def __init__(self):
        self.robot: Optional[CourierRobot] = None
        self.current_order: Optional[Order] = None
        self.status: RobotStatus = RobotStatus.IDLE
        self._scenario_task: Optional[asyncio.Task] = None

    def initialize(self):
        self.robot = robot
        self.status = RobotStatus.IDLE

    def create_order(self, address: str, window: str) -> Order:
        if not self.robot:
            raise RuntimeError("Robot not initialized")
        order = self.robot.create_order(address, window)
        self.robot.accept_order(order)
        self.current_order = order
        return order

    def deliver_order(self, code: str):
        if not self.robot:
            raise RuntimeError("Robot not initialized")
        return self.robot.deliver(code)

    def get_sensor_state(self) -> Dict[str, Any]:
        if not self.robot:
            raise RuntimeError("Robot not initialized")
        state = self.robot.state
        return {
            "position": state.position,
            "speed": state.speed,
            "speed_units": state.speed_units,
            "busy": state.busy
        }

    def get_actuator_state(self) -> Dict[str, Any]:
        if not self.robot:
            raise RuntimeError("Robot not initialized")
        drive_target = self.robot.drive.target
        return {
            "target": drive_target,
            "moving": self.robot.state.busy,
        }

    def stop(self):
        if self._scenario_task and not self._scenario_task.done():
            self._scenario_task.cancel()
        self.status = RobotStatus.IDLE

    def get_status(self) -> Dict[str, Any]:
        return {"status": self.status}

robot_service = RobotService()
